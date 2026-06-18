#!/usr/bin/env python3
"""
irt_latent.py — Latent estimation for evals: precise estimates for BOTH eval items
and skill variants, on a common latent scale, with honest uncertainty.

This is the skill's measurement-model deliverable. It fits a HIERARCHICAL Bayesian
2PL: variant abilities (theta) on a fixed N(0,1) scale (NOT pooled — the goal is to
separate variants), and item difficulty (b) and discrimination (a) PARTIALLY POOLED
under priors whose spread is learned from the data. That learned spread is the
"adaptive shrinkage" knob: when data are sparse/uninformative the discriminations
shrink toward a common value (≈ Rasch, stable); as variants/observations accumulate
the pooling relaxes and 2PL structure is recovered. This is what makes precise
latent estimates obtainable even with only a handful of variants — where a free 2PL
would return confident noise.

Outputs (every run):
  * per-variant theta with 95% interval  (ability of each skill version/model)
  * per-item b (difficulty) and a (discrimination) with 95% intervals
  * the learned discrimination spread sigma_a (the shrinkage state)
  * a saturation read (test information across the ability range)

Backends:
  --backend auto     (default) MCMC 2PL if PyMC installed, else stable Rasch.
  --backend mcmc     full posterior via PyMC (pip install pymc). Use when you
                     want exact HDIs or per-item discrimination with adaptive
                     shrinkage. NumPy 2.x + Numba conflict: if you see a Numba
                     import error set PYTENSOR_FLAGS=linker=py before running,
                     or the script sets it automatically when invoked directly.
  --backend rasch    hierarchical 1PL, scipy-only, always available.

Modes:
  default            joint estimation of items + variants.
  --fixed-items P    anchor mode: freeze item params from a calibrated bank (CSV
                     item_id,b[,a]) and estimate ONLY theta per variant — the most
                     precise small-N path when a bank exists.

INPUT  : long-format CSV: taker_id,item_id,score  (score binarized at --thresh)
USAGE  : python irt_latent.py results.csv [--backend auto|rasch|mcmc] [--thresh 0.5]
                  [--fixed-items bank.csv] [--out estimates.json]
Dependencies: numpy, pandas, scipy. (PyMC only for --backend mcmc/auto with PyMC installed.)
"""
import os, argparse, json, sys
# Avoid NumPy 2.x / Numba compiled-against-1.x crash when pytensor uses the Numba linker.
os.environ.setdefault("PYTENSOR_FLAGS", "linker=py")
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

SCALE_B, SCALE_LA = 2.5, 0.5  # half-Cauchy hyperprior scales (Gelman weakly-informative)


def load(path, thresh):
    df = pd.read_csv(path)
    if not {"taker_id", "item_id", "score"}.issubset(df.columns):
        sys.exit("ERROR: need columns taker_id, item_id, score")
    df = df.groupby(["taker_id", "item_id"], as_index=False)["score"].mean()
    mat = df.pivot(index="taker_id", columns="item_id", values="score")
    Y = (mat.values >= thresh).astype(float)
    M = ~np.isnan(mat.values)  # observed mask
    return list(mat.index), list(mat.columns), np.nan_to_num(Y), M


# ---------- hierarchical models ----------
def _rasch_neglp(x, Y, M, P, I):
    theta = x[:P]; b = x[P:P + I]; mu_b, s_b = x[P + I:]
    z = theta[:, None] - b[None, :]
    p = np.clip(expit(z), 1e-9, 1 - 1e-9)
    ll = np.where(M, Y * np.log(p) + (1 - Y) * np.log(1 - p), 0.0).sum()
    ib = np.exp(-2 * s_b)
    lp = -0.5 * np.sum(theta ** 2) + np.sum(-s_b - 0.5 * (b - mu_b) ** 2 * ib) - 0.5 * mu_b ** 2 / 25
    ub = np.exp(s_b) / SCALE_B
    lp += -np.log1p(ub ** 2) + s_b
    return -(ll + lp)


def _rasch_re_obj(re, hyper, Y, M, P, I):
    return _rasch_neglp(np.concatenate([re, hyper]), Y, M, P, I)


def fit_rasch(Y, M, takers, items):
    """Stable hierarchical Rasch (1PL): discrimination fixed at 1, difficulties
    partially pooled, abilities on N(0,1). No per-item discrimination to run away,
    so this is the dependable portable backend. For per-item discrimination with
    adaptive shrinkage, use --backend mcmc."""
    P, I = Y.shape
    raw = np.clip((Y * M).sum(1) / np.maximum(M.sum(1), 1), .02, .98)
    rawi = np.clip((Y * M).sum(0) / np.maximum(M.sum(0), 1), .02, .98)
    re = np.concatenate([np.log(raw / (1 - raw)), -np.log(rawi / (1 - rawi))])
    mu_b, sig_b = 0.0, 1.0
    cov = None
    for _ in range(30):
        hyper = np.array([mu_b, np.log(sig_b)])
        res = minimize(_rasch_re_obj, re, args=(hyper, Y, M, P, I), method="L-BFGS-B",
                       options=dict(maxiter=500, ftol=1e-10))
        re = res.x
        n = P + I; H = np.zeros((n, n)); eps = 1e-4 * (1 + np.abs(re))
        gbase = _num_grad(_rasch_re_obj, re, hyper, Y, M, P, I)
        for j in range(n):
            rp = re.copy(); rp[j] += eps[j]
            H[:, j] = (_num_grad(_rasch_re_obj, rp, hyper, Y, M, P, I) - gbase) / eps[j]
        H = 0.5 * (H + H.T) + 1e-6 * np.eye(n)
        try:
            cov = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            cov = np.linalg.pinv(H)
        v = np.clip(np.diag(cov), 0, None)
        b = re[P:P + I]; vb = v[P:P + I]
        nmu_b = float(b.mean()); nsig_b = float(np.sqrt(max(np.mean((b - nmu_b) ** 2) + vb.mean(), 0.0025)))
        done = abs(nsig_b - sig_b) < 1e-3
        mu_b, sig_b = nmu_b, nsig_b
        if done:
            break
    theta = re[:P]; b = re[P:P + I]
    sd = np.sqrt(np.clip(np.diag(cov), 0, None))
    out = dict(backend="rasch (1PL, portable)",
               theta=_tbl(takers, theta, sd[:P]),
               difficulty=_tbl(items, b, sd[P:P + I]),
               discrimination=[dict(id=i, est=1.0, lo=1.0, hi=1.0) for i in items],
               sigma_b=float(sig_b), sigma_a=None, converged=bool(res.success))
    return out, theta, b, np.ones(I)


def _num_grad(f, x, *args, eps=1e-5):
    g = np.zeros_like(x)
    for j in range(len(x)):
        xp = x.copy(); xm = x.copy(); xp[j] += eps; xm[j] -= eps
        g[j] = (f(xp, *args) - f(xm, *args)) / (2 * eps)
    return g


def _tbl(names, est, sd, lo=None, hi=None):
    if lo is None:
        lo = est - 1.96 * sd; hi = est + 1.96 * sd
    return [dict(id=n, est=round(float(e), 3), lo=round(float(l), 3), hi=round(float(h), 3))
            for n, e, l, h in zip(names, est, lo, hi)]


def fit_anchor(Y, M, takers, items, bank):
    """Freeze item params from bank; estimate only theta per variant (+ SE)."""
    common = [i for i in items if i in bank.index]
    if not common:
        sys.exit("ERROR: no overlap between results items and the calibrated bank.")
    idx = [items.index(i) for i in common]
    b = bank.loc[common, "b"].values.astype(float)
    a = bank.loc[common, "a"].values.astype(float) if "a" in bank.columns else np.ones(len(common))
    Yc, Mc = Y[:, idx], M[:, idx]
    rows = []
    for p in range(len(takers)):
        y, m = Yc[p], Mc[p]
        def nll(t):
            pr = np.clip(expit(a * (t[0] - b)), 1e-9, 1 - 1e-9)
            return -(np.where(m, y * np.log(pr) + (1 - y) * np.log(1 - pr), 0).sum()) + 0.5 * t[0] ** 2
        r = minimize(nll, [0.0], method="L-BFGS-B")
        th = r.x[0]
        pr = expit(a * (th - b))
        info = np.sum((a ** 2) * pr * (1 - pr) * m) + 1.0  # +prior precision
        se = 1 / np.sqrt(info)
        rows.append(dict(id=takers[p], est=round(float(th), 3),
                         lo=round(float(th - 1.96 * se), 3), hi=round(float(th + 1.96 * se), 3)))
    return dict(backend="anchor", n_anchor_items=len(common), theta=rows)


def fit_mcmc(Y, M, takers, items):
    import pymc as pm
    P, I = Y.shape
    ii, pp = np.meshgrid(np.arange(I), np.arange(P))
    obs = M.ravel(); yv = Y.ravel()[obs]; pv = pp.ravel()[obs]; iv = ii.ravel()[obs]
    with pm.Model():
        theta = pm.Normal("theta", 0, 1, shape=P)
        mu_b = pm.Normal("mu_b", 0, 5); sig_b = pm.HalfCauchy("sig_b", SCALE_B)
        b = pm.Normal("b", mu_b, sig_b, shape=I)
        mu_la = pm.Normal("mu_la", 0, 1); sig_la = pm.HalfCauchy("sig_la", SCALE_LA)
        loga = pm.Normal("loga", mu_la, sig_la, shape=I); a = pm.math.exp(loga)
        eta = a[iv] * (theta[pv] - b[iv])
        pm.Bernoulli("y", logit_p=eta, observed=yv)
        idata = pm.sample(1000, tune=1000, chains=2, cores=1, target_accept=0.95,
                          progressbar=False, random_seed=0)
    post = idata.posterior
    qa = lambda v: (post[v].mean(("chain", "draw")).values,
                    post[v].quantile(0.025, ("chain", "draw")).values,
                    post[v].quantile(0.975, ("chain", "draw")).values)
    tm, tl, th = qa("theta"); bm, bl, bh = qa("b")
    am = np.exp(post["loga"]).mean(("chain", "draw")).values
    al = np.exp(post["loga"]).quantile(0.025, ("chain", "draw")).values
    ah = np.exp(post["loga"]).quantile(0.975, ("chain", "draw")).values
    return dict(backend="mcmc",
                theta=_tbl(takers, tm, None, tl, th),
                difficulty=_tbl(items, bm, None, bl, bh),
                discrimination=_tbl(items, am, None, al, ah),
                sigma_a=float(post["sig_la"].mean()), sigma_b=float(post["sig_b"].mean())), tm, bm, am


def report(out, theta=None, b=None, a=None):
    print(f"# Latent estimation  |  backend={out['backend']}")
    if out["backend"] == "anchor":
        print(f"## Variant ability (theta) anchored on {out['n_anchor_items']} calibrated items\n")
        _print_tbl(out["theta"], "variant")
        print("\n(Item params were frozen from the bank, so theta is precise even at tiny N.)")
        return
    if out.get("sigma_a") is not None:
        print(f"## Learned discrimination spread sigma_a = {out['sigma_a']:.3f}  ->",
              "near 0: discriminations pooled toward a common value (~Rasch; data can't yet resolve them)"
              if out["sigma_a"] < 0.25 else
              "moderate: partial pooling, some 2PL structure resolved" if out["sigma_a"] < 0.6 else
              "large: data strongly resolve discriminations (full 2PL behavior)")
        print(f"   (this is the adaptive-shrinkage state; it relaxes as variants/observations grow)\n")
    else:
        print(f"## Discrimination fixed at 1.0 (Rasch). sigma_b={out['sigma_b']:.2f}. "
              f"For per-item discrimination with\n   adaptive shrinkage, re-run with --backend mcmc.\n")
    print("## Variant ability (theta), descending — your skill-variant latent estimates\n")
    _print_tbl(sorted(out["theta"], key=lambda r: -r["est"]), "variant")
    show_disc = out.get("sigma_a") is not None
    print("\n## Item difficulty (b)" + (" and discrimination (a)" if show_disc else "")
          + " with 95% intervals\n")
    di = {d["id"]: d for d in out["difficulty"]}; ai = {d["id"]: d for d in out["discrimination"]}
    if show_disc:
        print(f"   {'item':<22}{'b (diff)':>20}{'a (disc)':>20}")
        for it in di:
            d, av = di[it], ai[it]
            print(f"   {it:<22}{d['est']:>8.2f} [{d['lo']:>5.2f},{d['hi']:>5.2f}]"
                  f"{av['est']:>8.2f} [{av['lo']:>5.2f},{av['hi']:>5.2f}]")
    else:
        print(f"   {'item':<22}{'b (difficulty)':>22}")
        for it in di:
            d = di[it]
            print(f"   {it:<22}{d['est']:>8.2f} [{d['lo']:>6.2f},{d['hi']:>6.2f}]")
    if theta is not None and b is not None and a is not None:
        grid = np.linspace(min(theta) - .5, max(theta) + 1.0, 60)
        info = sum((ai ** 2) * expit(ai * (grid - bi)) * (1 - expit(ai * (grid - bi)))
                   for ai, bi in zip(a, b))
        top = info[grid >= np.percentile(theta, 75)].mean(); mean = info.mean()
        print(f"\n## Saturation: test information at top-quartile ability = {top/mean:.2f}x mean", end="")
        print("  -> LOW; suite can't separate your strongest variants (add harder items)."
              if top < 0.6 * mean else "  -> adequate across your variant range.")


def _print_tbl(rows, label):
    print(f"   {label:<22}{'theta':>9}{'95% interval':>20}")
    for r in rows:
        width = r["hi"] - r["lo"]
        flag = "  (wide — low precision)" if width > 2.0 else ""
        print(f"   {r['id']:<22}{r['est']:>9.2f}   [{r['lo']:>6.2f},{r['hi']:>6.2f}]{flag}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--backend", choices=["auto", "rasch", "mcmc"], default="auto",
                    help="auto: MCMC 2PL if PyMC installed, else stable Rasch (1PL)")
    ap.add_argument("--fixed-items", default=None)
    ap.add_argument("--thresh", type=float, default=0.5)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    takers, items, Y, M = load(args.csv, args.thresh)
    P, I = Y.shape
    print(f"# {P} variants x {I} items\n", file=sys.stderr)

    backend = args.backend
    if backend == "auto":
        try:
            import pymc  # noqa
            backend = "mcmc"
        except Exception:
            backend = "rasch"
            print("NOTE: PyMC not installed -> using the stable hierarchical Rasch backend "
                  "(difficulty + ability,\n      discrimination fixed at 1). For per-item "
                  "discrimination with adaptive shrinkage, install PyMC\n      (pip install pymc) "
                  "and re-run, or use --fixed-items to anchor on a calibrated bank.\n")

    if args.fixed_items:
        bank = pd.read_csv(args.fixed_items).set_index("item_id")
        out = fit_anchor(Y, M, takers, items, bank); report(out)
    elif backend == "mcmc":
        if P < 8:
            print(f"NOTE: {P} variants is very small. Hierarchical pooling keeps the 2PL estimable,")
            print(f"      but expect wide intervals — that's honest. --fixed-items is tighter if you")
            print(f"      have a calibrated bank.\n")
        out, th, b, a = fit_mcmc(Y, M, takers, items); report(out, th, b, a)
    else:
        out, th, b, a = fit_rasch(Y, M, takers, items); report(out, th, b, a)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
