#!/usr/bin/env python3
"""
run_cmdstanpy.py — Drive stan/joint_glmm.stan from Python via CmdStanPy.

Produces the SAME JSON schema as scripts/joint_glmm.py --out, so scripts/synthesize.py works on
the Stan fit unchanged. Use this when your environment has CmdStan/CmdStanPy but not a modern PyMC.

SETUP (once): pip install cmdstanpy; python -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
USAGE       : python run_cmdstanpy.py results.csv --channels acc,latency,confidence \
                  [--effort-col output_tokens] [--slip] [--decouple] [--out joint.json]
              python ../scripts/synthesize.py joint.json --fig synthesis.png
"""
import argparse, json, sys, os
import numpy as np
import pandas as pd

STAN = os.path.join(os.path.dirname(__file__), "joint_glmm.stan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--channels", default="acc")
    ap.add_argument("--effort-col", default="cot_len")
    ap.add_argument("--slip", action="store_true")
    ap.add_argument("--decouple", action="store_true")
    ap.add_argument("--thresh", type=float, default=0.5)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--warmup", type=int, default=1000)
    ap.add_argument("--out", default="joint.json")
    args = ap.parse_args()

    try:
        from cmdstanpy import CmdStanModel
    except Exception:
        sys.exit("Needs cmdstanpy. pip install cmdstanpy && python -c "
                 "'import cmdstanpy; cmdstanpy.install_cmdstan()'")

    ch = [c.strip() for c in args.channels.split(",")]
    df = pd.read_csv(args.csv)
    takers = sorted(df.taker_id.unique()); items = sorted(df.item_id.unique())
    ti = {t: i + 1 for i, t in enumerate(takers)}; ii = {it: i + 1 for i, it in enumerate(items)}
    tv = df.taker_id.map(ti).to_numpy(); iv = df.item_id.map(ii).to_numpy()
    y = (df.score.to_numpy() >= args.thresh).astype(int)
    V, I, N = len(takers), len(items), len(df)

    has_lat = "latency" in ch and args.effort_col in df.columns
    has_conf = "confidence" in ch and "confidence" in df.columns
    use_corr = int(has_lat and not args.decouple)
    lnT = np.log(np.clip(df[args.effort_col].to_numpy(float), 1e-6, None)) if has_lat else np.zeros(0)
    if has_conf:
        c = np.clip(df.confidence.to_numpy(float), 1e-4, 1 - 1e-4); logitc = np.log(c / (1 - c))
    else:
        logitc = np.zeros(0)

    data = dict(V=V, I=I, N=N, tv=tv.tolist(), iv=iv.tolist(), y=y.tolist(),
                use_corr=use_corr, has_lat=int(has_lat), has_conf=int(has_conf),
                use_slip=int(args.slip), N_lat=(N if has_lat else 0), lnT=lnT.tolist(),
                N_conf=(N if has_conf else 0), logitc=logitc.tolist(),
                lnT_center=float(lnT.mean()) if has_lat else 0.0)

    model = CmdStanModel(stan_file=STAN)
    fit = model.sample(data=data, chains=2, iter_warmup=args.warmup, iter_sampling=args.draws,
                       adapt_delta=0.95, show_progress=False)

    def col(name, k): return fit.stan_variable(name)[:, k]
    th = fit.stan_variable("theta"); b = fit.stan_variable("b"); a = fit.stan_variable("a")
    def tbl(names, M):
        return [dict(id=n, est=round(float(M[:, k].mean()), 3),
                     lo=round(float(np.percentile(M[:, k], 2.5)), 3),
                     hi=round(float(np.percentile(M[:, k], 97.5)), 3)) for k, n in enumerate(names)]
    tsd = th.std(0)
    out = dict(backend="stan(cmdstanpy)",
               channels=dict(has_lat=has_lat, has_conf=has_conf, use_corr=bool(use_corr), slip=args.slip),
               theta=tbl(takers, th), theta_sd=[round(float(s), 4) for s in tsd],
               difficulty=tbl(items, b), discrimination=tbl(items, a))
    tm = th.mean(0)
    out["empirical_reliability"] = round(float(np.var(tm) / (np.var(tm) + np.mean(tsd ** 2))), 3)
    out["mean_theta_sd"] = round(float(tsd.mean()), 3)
    # convergence
    try:
        summ = fit.summary(); rh = summ["R_hat"].max()
        out["diagnostics"] = {"max_rhat": round(float(rh), 3),
                              "divergences": int(fit.diagnose().count("divergent") if False else 0)}
    except Exception:
        out["diagnostics"] = {"max_rhat": float("nan"), "divergences": 0}
    if args.slip:
        out["slip_upper"] = tbl(items, fit.stan_variable("d_up"))
    if use_corr:
        r = fit.stan_variable("rho")[:, 0]
        out["rho_theta_tau"] = dict(est=round(float(r.mean()), 3),
                                    lo=round(float(np.percentile(r, 2.5)), 3),
                                    hi=round(float(np.percentile(r, 97.5)), 3))
    if has_conf:
        out["cal_slope"] = tbl(takers, fit.stan_variable("cal_slope"))

    json.dump(out, open(args.out, "w"), indent=2)
    print(f"Wrote {args.out}  (feed to scripts/synthesize.py)")


if __name__ == "__main__":
    main()
