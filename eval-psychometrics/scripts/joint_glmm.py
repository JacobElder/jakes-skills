#!/usr/bin/env python3
"""
joint_glmm.py — One hierarchical model, many theories' parameters from a single fit.

The unification is real because IRT, SDT, calibration, and G-theory are all readings of a
generalized linear mixed model. This engine fits ONE probit GLMM over up to three response
channels and emits the parameters of each framework from the same posterior:

  * IRT          per-item difficulty b, discrimination a (hierarchical, adaptive shrinkage),
                 optional 4PL upper asymptote (slip) for label-noisy/saturated items.
  * SDT          the probit reading of the accuracy channel: discrimination a_i IS detection
                 sensitivity per unit ability; b_i is the criterion location. (For trigger-style
                 signal/noise SDT, see sdt_trigger.py — that's a different response process and
                 should be a separate channel, not merged into task ability.)
  * Calibration  per-variant confidence-vs-correctness slope from the optional confidence channel.
  * G-theory     the measurement-model bridge: IRT empirical (marginal) reliability
                 rho = Var(theta_hat) / (Var(theta_hat) + mean posterior var) — the latent
                 analogue of E-rho^2. Full crossed-facet G-theory (judge/seed) is gtheory_eval.py;
                 add those as random effects here to reproduce it.

The headline identifiability move (van der Linden, 2007): add the LATENCY/CoT-length channel and
the variant speed trait tau is estimated jointly with ability theta under a shared correlation.
That correlation lets latency data inform theta — which is the single best lever for squeezing
precision out of a few variants. Run with --channels acc then acc,latency to see theta's
intervals tighten.

HONEST LIMIT (the thing the Gemini-style "just put it all in one Stan model" pitch skips): with a
handful of variants you cannot ESTIMATE a rich trait covariance — you assert it via priors, and
the precision is then manufactured, not measured. This engine estimates only a single theta-tau
correlation (cheap, 2 traits) and warns when the variant count is too small to trust even that.
For >2 correlated traits at small N, prefer --decouple and report traits independently.

INPUT  : long CSV taker_id,item_id,score[,cot_len][,confidence]
USAGE  : python joint_glmm.py results.csv --channels acc,latency,confidence
              [--effort-col output_tokens] [--slip] [--decouple] [--draws 1000] [--out joint.json]
         The latency channel accepts any effort/length column (CoT length, OUTPUT tokens, latency);
         output tokens buy identifiability, input tokens mostly do not. See reference/09.
Dependencies: numpy, pandas, pymc (this engine is MCMC-only by design — see the σ_a lesson in
reference/07; the variance/correlation components need full Bayes, not a MAP optimizer).
"""
import os, argparse, json, sys
os.environ.setdefault("PYTENSOR_FLAGS", "linker=cvm")
import numpy as np
import pandas as pd


def load(path, thresh):
    df = pd.read_csv(path)
    if not {"taker_id", "item_id", "score"}.issubset(df.columns):
        sys.exit("ERROR: need columns taker_id, item_id, score")
    takers = sorted(df.taker_id.unique()); items = sorted(df.item_id.unique())
    ti = {t: k for k, t in enumerate(takers)}; ii = {it: k for k, it in enumerate(items)}
    df = df.copy()
    df["tv"] = df.taker_id.map(ti); df["iv"] = df.item_id.map(ii)
    df["y"] = (df.score >= thresh).astype(int)
    return df, takers, items


def build_and_sample(df, takers, items, channels, slip, decouple, draws, tune, effort_col):
    import pymc as pm
    import pytensor.tensor as pt
    V, I = len(takers), len(items)
    tv = df.tv.values; iv = df.iv.values; y = df.y.values
    has_lat = "latency" in channels and effort_col in df.columns
    has_conf = "confidence" in channels and "confidence" in df.columns
    use_corr = has_lat and not decouple

    with pm.Model() as m:
        # ---- variant latent traits (unit-variance; scale-fixing) ----
        theta_raw = pm.Normal("theta", 0, 1, shape=V)               # task ability
        if has_lat:
            if use_corr:
                rho = pm.Uniform("rho_theta_tau", -0.95, 0.95)      # estimated, not asserted
                e = pm.Normal("tau_e", 0, 1, shape=V)
                tau = pm.Deterministic("tau", rho * theta_raw + pt.sqrt(1 - rho ** 2) * e)
            else:
                tau = pm.Normal("tau", 0, 1, shape=V)
        # ---- hierarchical item parameters (adaptive shrinkage on discrimination) ----
        mu_b = pm.Normal("mu_b", 0, 1); sig_b = pm.HalfNormal("sig_b", 1.0)
        b = pm.Normal("b", mu_b, sig_b, shape=I)
        mu_la = pm.Normal("mu_la", 0, 0.5); sig_la = pm.HalfNormal("sig_la", 0.5)
        loga_raw = pm.Normal("loga_raw", 0, 1, shape=I)
        loga = pm.Deterministic("loga", mu_la + sig_la * loga_raw)
        a = pm.Deterministic("a", pm.math.exp(loga))
        # ---- accuracy channel (probit; optional 4PL upper asymptote) ----
        eta = a[iv] * (theta_raw[tv] - b[iv])
        phi = pm.math.invprobit(eta)
        if slip:
            d_up = pm.Beta("slip_upper", 20, 1, shape=I)            # ~0.95 unless data say otherwise
            p = d_up[iv] * phi
            p = pt.clip(p, 1e-6, 1 - 1e-6)
            pm.Bernoulli("acc", p=p, observed=y)
        else:
            pm.Bernoulli("acc", p=pt.clip(phi, 1e-6, 1 - 1e-6), observed=y)
        # ---- latency channel (van der Linden) ----
        if has_lat:
            lnT = np.log(np.clip(df[effort_col].values.astype(float), 1e-6, None))
            mu_lam = pm.Normal("mu_lam", float(lnT.mean()), 1.0); sig_lam = pm.HalfNormal("sig_lam", 1.0)
            lam = pm.Normal("lam", mu_lam, sig_lam, shape=I)
            kappa = pm.HalfNormal("kappa_speed", 1.0)               # how much speed spreads latency
            sigT = pm.HalfNormal("sigT", 1.0)
            pm.Normal("lat", mu=lam[iv] - kappa * tau[tv], sigma=sigT, observed=lnT)
        # ---- confidence channel (per-variant calibration slope) ----
        if has_conf:
            c = np.clip(df.confidence.values.astype(float), 1e-4, 1 - 1e-4)
            logitc = np.log(c / (1 - c))
            g0 = pm.Normal("g0", 0, 1); g1 = pm.Normal("g1", 1, 1)
            sig_gc = pm.HalfNormal("sig_gc", 1.0); gc = pm.Normal("gc", 0, sig_gc, shape=V)
            sigC = pm.HalfNormal("sigC", 1.0)
            cal_pred = g0 + (g1 + gc[tv]) * (theta_raw[tv] - b[iv])
            pm.Normal("conf", mu=cal_pred, sigma=sigC, observed=logitc)
            pm.Deterministic("cal_slope", g1 + gc)

        idata = pm.sample(draws, tune=tune, chains=2, cores=1, target_accept=0.95,
                          progressbar=False, random_seed=0)
    return idata, dict(has_lat=has_lat, has_conf=has_conf, use_corr=use_corr, slip=slip)


def summarize(idata, takers, items, flags):
    import arviz as az
    post = idata.posterior
    q = lambda v: (post[v].mean(("chain", "draw")).values,
                   post[v].quantile(0.025, ("chain", "draw")).values,
                   post[v].quantile(0.975, ("chain", "draw")).values)
    tm, tl, th = q("theta")
    th_sd = post["theta"].std(("chain", "draw")).values
    bm, bl, bh = q("b"); am, al, ah = q("a")
    out = {"backend": "joint_glmm", "channels": flags,
           "theta": _tbl(takers, tm, tl, th),
           "theta_sd": [round(float(s), 4) for s in th_sd],
           "difficulty": _tbl(items, bm, bl, bh),
           "discrimination": _tbl(items, am, al, ah)}
    # convergence — surface it, don't hide it
    try:
        rh = az.rhat(idata)
        max_rhat = float(max(float(rh[v].max()) for v in rh.data_vars))
    except Exception:
        max_rhat = float("nan")
    ndiv = int(idata.sample_stats["diverging"].sum()) if "diverging" in idata.sample_stats else 0
    out["diagnostics"] = {"max_rhat": round(max_rhat, 3), "divergences": ndiv}
    # IRT empirical (marginal) reliability == G-theory E-rho^2 bridge
    rel = float(np.var(tm) / (np.var(tm) + np.mean(th_sd ** 2)))
    out["empirical_reliability"] = round(rel, 3)
    out["mean_theta_sd"] = round(float(th_sd.mean()), 3)
    if flags["slip"]:
        sm, sl, sh = q("slip_upper"); out["slip_upper"] = _tbl(items, sm, sl, sh)
    if flags["has_lat"] and flags["use_corr"]:
        rm = float(post["rho_theta_tau"].mean())
        rl = float(post["rho_theta_tau"].quantile(0.025))
        rh = float(post["rho_theta_tau"].quantile(0.975))
        out["rho_theta_tau"] = dict(est=round(rm, 3), lo=round(rl, 3), hi=round(rh, 3))
    if flags["has_conf"]:
        cm, cl, ch = q("cal_slope"); out["cal_slope"] = _tbl(takers, cm, cl, ch)
    return out


def _tbl(names, e, lo, hi):
    return [dict(id=n, est=round(float(x), 3), lo=round(float(l), 3), hi=round(float(h), 3))
            for n, x, l, h in zip(names, e, lo, hi)]


def report(out):
    f = out["channels"]
    chans = "accuracy" + (" + latency" if f["has_lat"] else "") + (" + confidence" if f["has_conf"] else "")
    print(f"# Joint GLMM  |  one fit, channels: {chans}\n")
    print("## IRT — item difficulty (b) and discrimination (a)"
          + (" and 4PL slip (upper)" if f["slip"] else "") + "\n")
    di = {d['id']: d for d in out['difficulty']}; ai = {d['id']: d for d in out['discrimination']}
    sl = {d['id']: d for d in out.get('slip_upper', [])}
    hdr = f"   {'item':<10}{'b':>16}{'a':>16}" + (f"{'slip':>16}" if f['slip'] else "")
    print(hdr)
    for it in di:
        d, av = di[it], ai[it]; line = (f"   {it:<10}{d['est']:>7.2f}[{d['lo']:>5.2f},{d['hi']:>5.2f}]"
                                        f"{av['est']:>7.2f}[{av['lo']:>5.2f},{av['hi']:>5.2f}]")
        if f['slip']:
            s = sl[it]; line += f"{s['est']:>7.2f}[{s['lo']:>5.2f},{s['hi']:>5.2f}]"
        print(line)
    print("\n   SDT (probit reading): each a_i is detection sensitivity per unit ability; b_i is the")
    print("   criterion location. d' between two variants on item i = a_i * (theta_1 - theta_2).")
    print("\n## Variant ability (theta), descending\n")
    for r in sorted(out['theta'], key=lambda r: -r['est']):
        wide = "  (wide)" if r['hi'] - r['lo'] > 2 else ""
        print(f"   {r['id']:<10}{r['est']:>7.2f}  [{r['lo']:>6.2f},{r['hi']:>6.2f}]{wide}")
    if "rho_theta_tau" in out:
        r = out["rho_theta_tau"]
        print(f"\n## Effort/length coupling — corr(ability, speed/terseness) = {r['est']:+.2f} "
              f"[{r['lo']:+.2f},{r['hi']:+.2f}]")
        print("   van der Linden channel (latency, CoT length, or OUTPUT tokens): shares info with ability.")
        if r['hi'] - r['lo'] > 1.0:
            print("   (interval is wide — the correlation itself is weakly identified at this N;")
            print("    it still helps theta, but don't over-read the number.)")
    if "cal_slope" in out:
        print("\n## Calibration — per-variant confidence-vs-correctness slope (1.0 = well-tracked)\n")
        for r in out["cal_slope"]:
            print(f"   {r['id']:<10}{r['est']:>7.2f}  [{r['lo']:>6.2f},{r['hi']:>6.2f}]")
    print(f"\n## G-theory bridge — IRT empirical reliability (≈ E-rho^2) = {out['empirical_reliability']:.3f}")
    print(f"   mean posterior SD of theta = {out['mean_theta_sd']:.3f}. "
          f"For full crossed-facet G-theory (judge/seed), use gtheory_eval.py or add those as")
    print("   random effects here.")
    d = out["diagnostics"]
    flag = "" if (d["max_rhat"] <= 1.01 and d["divergences"] == 0) else "  <-- CHECK: fit may be unreliable"
    print(f"\n## Convergence: max R-hat = {d['max_rhat']}, divergences = {d['divergences']}{flag}")
    if flag:
        print("   Increase --tune/--draws or simplify channels; treat the numbers above with caution.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--channels", default="acc", help="comma list of: acc,latency,confidence")
    ap.add_argument("--slip", action="store_true", help="4PL upper asymptote (bank regime only)")
    ap.add_argument("--decouple", action="store_true", help="don't estimate trait correlation")
    ap.add_argument("--effort-col", default="cot_len",
                    help="column for the effort/length channel: cot_len, output_tokens, latency_ms, ...")
    ap.add_argument("--thresh", type=float, default=0.5)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--tune", type=int, default=1000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    try:
        import pymc  # noqa
    except Exception:
        sys.exit("joint_glmm.py requires PyMC (pip install pymc). For a portable single-theory\n"
                 "estimator use irt_latent.py --backend rasch.")

    channels = [c.strip() for c in args.channels.split(",")]
    df, takers, items = load(args.csv, args.thresh)
    V = len(takers)
    print(f"# {V} variants x {len(items)} items | channels requested: {channels}\n", file=sys.stderr)
    if V < 10:
        print(f"NOTE: {V} variants. The trait correlation is weakly identified here and is "
              f"prior-influenced;\n      it still improves theta via the latency channel, but read "
              f"the correlation's interval, not\n      just its point estimate. The accuracy+latency "
              f"channels are where the small-N gain is real.\n")
    if args.slip and V < 25:
        print(f"WARNING: 4PL slip with {V} variants is a robustness device, not a measurement — the\n"
              f"         upper asymptote will sit near its Beta(20,1) prior unless an item is "
              f"strongly\n         saturated. Interpret slip<~0.85 items as 'flagged for label "
              f"noise', not as an estimated rate.\n")

    idata, flags = build_and_sample(df, takers, items, channels, args.slip, args.decouple,
                                    args.draws, args.tune, args.effort_col)
    out = summarize(idata, takers, items, flags)
    report(out)
    if args.out:
        json.dump(out, open(args.out, "w"), indent=2)
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
