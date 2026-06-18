#!/usr/bin/env python3
"""
irt_eval.py — IRT applied to eval data (MODEL-BANK regime only).

Fits a Rasch (1PL) or 2PL model to a takers x items binary matrix to get latent
ability per taker and difficulty/discrimination per item, flags saturation and
low/negative discrimination, and supports FIXED-ITEM (anchor) calibration so you
can score a few versions against pre-calibrated items — the safe way to use IRT
at small N.

GUARD: refuses a free 2PL fit below ~30 takers unless --force, and applies a
ridge penalty on log-discrimination as a lightweight stand-in for the hierarchical
adaptive shrinkage described in reference/07. For a proper small-N latent scale,
use --fixed-items or hierarchical Bayes (PyMC/brms), not a forced fit.

INPUT  : long-format CSV: taker_id, item_id, score   (score binarized at --thresh)
USAGE  : python irt_eval.py results.csv [--model 2pl|rasch] [--ridge 0.3]
                  [--fixed-items params.csv] [--force] [--thresh 0.5] [--out items.csv]
   fixed-items CSV columns: item_id, b [, a]
Dependencies: numpy, pandas, scipy.
"""
import argparse, sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

MIN_TAKERS_2PL = 30


def load(path, thresh):
    df = pd.read_csv(path)
    if not {"taker_id", "item_id", "score"}.issubset(df.columns):
        sys.exit("ERROR: need columns taker_id, item_id, score")
    df = df.groupby(["taker_id", "item_id"], as_index=False)["score"].mean()
    mat = df.pivot(index="taker_id", columns="item_id", values="score")
    Y = (mat.values >= thresh).astype(float)
    return mat.index.to_numpy(), mat.columns.to_numpy(), Y, np.isnan(mat.values)


def nll_rasch(params, Y, miss, np_, ni_):
    theta = params[:np_]; b = params[np_:]
    z = theta[:, None] - b[None, :]
    p = np.clip(expit(z), 1e-9, 1 - 1e-9)
    ll = Y * np.log(p) + (1 - Y) * np.log(1 - p)
    ll = np.where(miss, 0.0, ll)
    return -ll.sum()


def nll_2pl(params, Y, miss, np_, ni_, ridge):
    theta = params[:np_]; b = params[np_:np_ + ni_]; loga = params[np_ + ni_:]
    a = np.exp(loga)
    z = a[None, :] * (theta[:, None] - b[None, :])
    p = np.clip(expit(z), 1e-9, 1 - 1e-9)
    ll = Y * np.log(p) + (1 - Y) * np.log(1 - p)
    ll = np.where(miss, 0.0, ll)
    return -ll.sum() + ridge * np.sum(loga ** 2)


def fit(Y, miss, model, ridge):
    np_, ni_ = Y.shape
    raw = np.nanmean(np.where(miss, np.nan, Y), axis=1)
    theta0 = np.log((raw + 0.05) / (1 - raw + 0.05))
    bm = np.nanmean(np.where(miss, np.nan, Y), axis=0)
    b0 = -np.log((bm + 0.05) / (1 - bm + 0.05))
    if model == "rasch":
        x0 = np.concatenate([theta0, b0])
        res = minimize(nll_rasch, x0, args=(Y, miss, np_, ni_), method="L-BFGS-B")
        theta = res.x[:np_]; b = res.x[np_:]; a = np.ones(ni_)
    else:
        x0 = np.concatenate([theta0, b0, np.zeros(ni_)])
        res = minimize(nll_2pl, x0, args=(Y, miss, np_, ni_, ridge), method="L-BFGS-B")
        theta = res.x[:np_]; b = res.x[np_:np_ + ni_]; a = np.exp(res.x[np_ + ni_:])
    # identify: center difficulty, shift ability
    shift = b.mean(); b = b - shift; theta = theta - shift
    return theta, a, b


def fit_fixed(Y, miss, a, b):
    """Estimate only theta for each taker against fixed item params (a,b)."""
    np_, ni_ = Y.shape
    theta = np.zeros(np_)
    for p in range(np_):
        yi = Y[p]; m = miss[p]
        def nll(t):
            z = a * (t[0] - b)
            pr = np.clip(expit(z), 1e-9, 1 - 1e-9)
            ll = yi * np.log(pr) + (1 - yi) * np.log(1 - pr)
            ll = np.where(m, 0.0, ll)
            return -ll.sum() + 0.5 * t[0] ** 2  # mild N(0,1) prior on theta (EAP-ish)
        theta[p] = minimize(nll, [0.0], method="Nelder-Mead").x[0]
    return theta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--model", choices=["rasch", "2pl"], default="2pl")
    ap.add_argument("--ridge", type=float, default=0.3, help="ridge penalty on log-discrimination (2pl)")
    ap.add_argument("--fixed-items", default=None, help="CSV of pre-calibrated item params (item_id,b[,a])")
    ap.add_argument("--thresh", type=float, default=0.5)
    ap.add_argument("--force", action="store_true", help="allow free 2pl below the taker threshold")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    takers, items, Y, miss = load(args.csv, args.thresh)
    np_, ni_ = Y.shape
    print(f"# IRT on evals  |  {np_} takers x {ni_} items  |  model={args.model}")

    if args.fixed_items:
        fp = pd.read_csv(args.fixed_items).set_index("item_id")
        common = [i for i in items if i in fp.index]
        if not common:
            sys.exit("ERROR: no overlap between results items and fixed-item params.")
        idx = [list(items).index(i) for i in common]
        b = fp.loc[common, "b"].values.astype(float)
        a = fp.loc[common, "a"].values.astype(float) if "a" in fp.columns else np.ones(len(common))
        theta = fit_fixed(Y[:, idx], miss[:, idx], a, b)
        print(f"## FIXED-ITEM anchoring on {len(common)} calibrated items "
              f"(safe at any N — estimating ability only)\n")
        rank = pd.DataFrame({"theta": theta}, index=takers).sort_values("theta", ascending=False)
        print(rank.round(3).to_string())
        return

    if args.model == "2pl" and np_ < MIN_TAKERS_2PL and not args.force:
        print(f"\n!! REFUSING free 2PL: {np_} takers < {MIN_TAKERS_2PL}. Item parameters (esp.")
        print(f"!! discrimination) will be noise. Options:")
        print(f"!!   1) --model rasch        (fewer params, stable; get discrimination from CTT)")
        print(f"!!   2) --fixed-items P.csv   (anchor on a calibrated bank — recommended)")
        print(f"!!   3) hierarchical Bayes    (PyMC/brms, adaptive shrinkage — see reference/07)")
        print(f"!!   4) --force               (only if you understand the estimates are unstable)")
        sys.exit(1)
    if np_ < MIN_TAKERS_2PL:
        print(f"!! small-N ({np_} takers): estimates are unstable; ridge={args.ridge} applied. "
              f"Prefer fixed-item anchoring (reference/07).")

    theta, a, b = fit(Y, miss, args.model, args.ridge)

    p_pass = np.nanmean(np.where(miss, np.nan, Y), axis=0)
    tbl = pd.DataFrame({"difficulty_b": b, "discrimination_a": a, "pass_rate": p_pass}, index=items)
    def flag(r):
        if r.discrimination_a < 0.0:
            return "FIX:neg_discrimination"
        if r.pass_rate >= 0.95:
            return "TRIM:saturated"
        if r.discrimination_a < 0.3:
            return "TRIM:low_info"
        return "KEEP"
    tbl["flag"] = tbl.apply(flag, axis=1)
    tbl = tbl.round(3).sort_values("discrimination_a")

    pd.set_option("display.width", 200, "display.max_rows", None)
    print("\n## Items (low discrimination / saturated first)\n")
    print(tbl.to_string())
    print("\n## Taker ability (theta, descending)\n")
    print(pd.DataFrame({"theta": theta}, index=takers).round(3).sort_values("theta", ascending=False).to_string())

    # test information at the top end = saturation check
    grid = np.linspace(theta.min(), theta.max() + 1.0, 50)
    info = np.zeros_like(grid)
    for ai, bi in zip(a, b):
        p = expit(ai * (grid - bi)); info += (ai ** 2) * p * (1 - p)
    top = info[grid >= np.percentile(theta, 75)].mean()
    overall = info.mean()
    print(f"\n## Saturation: test information at top-quartile ability is "
          f"{top/overall:.2f}x the mean.")
    if top < 0.6 * overall:
        print("   -> LOW info at the top: the suite can't separate your strongest takers (saturated).")
    if args.out:
        tbl.to_csv(args.out); print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
