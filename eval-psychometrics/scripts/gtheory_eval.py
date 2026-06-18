#!/usr/bin/env python3
"""
gtheory_eval.py — Generalizability theory for eval suites.

Decomposes eval-score variance into components (version / case / seed and their
interactions), reports the generalizability coefficient E-rho^2 (for ranking
decisions) and the dependability coefficient Phi (for absolute/threshold
decisions), and runs a D-study that projects reliability under more cases/seeds
so you can size the suite.

Design supported: a fully-crossed  version x item [x seed]  design (balanced).
Object of measurement = version (the thing you want to dependably rank).
Facets = item, and optionally seed. Variance components are estimated in closed
form from expected mean squares (ANOVA), which is stable at small N.

INPUT  : long-format CSV: taker_id, item_id, score [, seed]
         (taker_id is the "version" / object of measurement.)
USAGE  : python gtheory_eval.py results.csv [--seed-facet] [--boot 1000]

Dependencies: numpy, pandas.
"""
import argparse, sys, warnings
import numpy as np
import pandas as pd


def _ms(ss, df):
    return ss / df if df > 0 else 0.0


def gtheory_pi(df):
    """Two-facet? No: single-facet crossed p x i (person=version, item).
    Returns variance components and coefficients."""
    tab = df.pivot_table(index="taker_id", columns="item_id", values="score", aggfunc="mean")
    tab = tab.dropna(axis=0, how="any").dropna(axis=1, how="any")
    X = tab.values.astype(float)
    n_p, n_i = X.shape
    if n_p < 2 or n_i < 2:
        sys.exit("ERROR: need >=2 versions and >=2 items for a p x i G-study.")
    grand = X.mean()
    p_means = X.mean(axis=1); i_means = X.mean(axis=0)
    ss_p = n_i * np.sum((p_means - grand) ** 2)
    ss_i = n_p * np.sum((i_means - grand) ** 2)
    ss_pi = np.sum((X - p_means[:, None] - i_means[None, :] + grand) ** 2)
    ms_p = _ms(ss_p, n_p - 1)
    ms_i = _ms(ss_i, n_i - 1)
    ms_pi = _ms(ss_pi, (n_p - 1) * (n_i - 1))
    # EMS solve (p random, i random, crossed, single observation per cell)
    v_pi = ms_pi
    v_p = max((ms_p - ms_pi) / n_i, 0.0)
    v_i = max((ms_i - ms_pi) / n_p, 0.0)
    return dict(n_p=n_p, n_i=n_i, v_p=v_p, v_i=v_i, v_pi=v_pi)


def coeffs(vc, n_i):
    """E-rho^2 (relative) and Phi (absolute) for n_i items."""
    v_p = vc["v_p"]
    rel_err = vc["v_pi"] / n_i                      # delta
    abs_err = vc["v_i"] / n_i + vc["v_pi"] / n_i    # Delta
    erho2 = v_p / (v_p + rel_err) if (v_p + rel_err) > 0 else 0.0
    phi = v_p / (v_p + abs_err) if (v_p + abs_err) > 0 else 0.0
    return erho2, phi


def seed_collapse(df, use_seed):
    """If seed exists and we're not modeling it as a facet, average over seeds.
    If modeling it, we still reduce to p x i here but report seed variance separately."""
    if "seed" in df.columns and not use_seed:
        df = df.groupby(["taker_id", "item_id"], as_index=False)["score"].mean()
    return df


def seed_variance(df):
    """Crude estimate of seed/run variance: mean within-(version,item) variance across seeds."""
    if "seed" not in df.columns:
        return None
    g = df.groupby(["taker_id", "item_id"])["score"]
    within = g.var(ddof=1).dropna()
    return float(within.mean()) if len(within) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--seed-facet", action="store_true",
                    help="report seed/run variance separately instead of averaging it away")
    ap.add_argument("--boot", type=int, default=1000, help="bootstrap resamples over versions (0=skip)")
    ap.add_argument("--rng", type=int, default=0)
    ap.add_argument("--out", default=None, help="write variance components + coefficients as JSON")
    args = ap.parse_args()

    raw = pd.read_csv(args.csv)
    need = {"taker_id", "item_id", "score"}
    if not need.issubset(raw.columns):
        sys.exit(f"ERROR: need columns {need}")

    df = seed_collapse(raw, args.seed_facet)
    vc = gtheory_pi(df)
    n_p, n_i = vc["n_p"], vc["n_i"]

    print(f"# Generalizability theory  |  object=version  ({n_p} versions x {n_i} items, crossed)")
    if n_p < 30:
        print(f"!! small-N ({n_p} versions): variance components have wide CIs (bootstrapped below).")
        print(f"!! This is the right tool for this regime; read the D-study as a planning guide.")

    tot = vc["v_p"] + vc["v_i"] + vc["v_pi"]
    print("\n## Variance components (share of total)")
    print(f"  version (universe, wanted) : {vc['v_p']:.4f}  ({vc['v_p']/tot*100:4.1f}%)")
    print(f"  item                       : {vc['v_i']:.4f}  ({vc['v_i']/tot*100:4.1f}%)")
    print(f"  version x item (residual)  : {vc['v_pi']:.4f}  ({vc['v_pi']/tot*100:4.1f}%)")
    sv = seed_variance(raw)
    if sv is not None:
        print(f"  seed/run (within v,i)      : {sv:.4f}   <- run-to-run sampling noise")

    erho2, phi = coeffs(vc, n_i)
    print(f"\n## Reliability at current size ({n_i} items)")
    print(f"  E-rho^2 (relative; for RANKING versions)   = {erho2:.3f}")
    print(f"  Phi      (absolute; for THRESHOLD/ship bar) = {phi:.3f}")
    verdict = ("dependable enough to decide on" if min(erho2, phi) >= 0.8 else
               "MARGINAL — borderline for decisions" if min(erho2, phi) >= 0.6 else
               "TOO NOISY to support a decision; the suite needs more cases/seeds")
    print(f"  verdict: {verdict}")
    dominant = max([("item-selection (version x item)", vc["v_pi"]),
                    ("item main effect", vc["v_i"])], key=lambda x: x[1])
    print(f"  largest error source: {dominant[0]} -> "
          + ("add cases" if "version x item" in dominant[0] or "item" in dominant[0] else "see below"))

    if args.boot and n_p >= 4:
        rng = np.random.default_rng(args.rng)
        versions = df["taker_id"].unique()
        es, ps = [], []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for _ in range(args.boot):
                pick = rng.choice(versions, len(versions), replace=True)
                bs = pd.concat([df[df.taker_id == v].assign(taker_id=f"{v}__{k}")
                                for k, v in enumerate(pick)], ignore_index=True)
                try:
                    e, p = coeffs(gtheory_pi(bs), n_i)
                    es.append(e); ps.append(p)
                except SystemExit:
                    continue
        if es:
            print(f"  E-rho^2 95% CI = [{np.percentile(es,2.5):.3f}, {np.percentile(es,97.5):.3f}]"
                  f"   Phi 95% CI = [{np.percentile(ps,2.5):.3f}, {np.percentile(ps,97.5):.3f}]")

    print("\n## D-study — projected E-rho^2 / Phi under more items")
    print(f"  {'items':>6} | {'E-rho^2':>8} | {'Phi':>6}")
    targets = sorted(set([max(2, n_i // 2), n_i, int(n_i * 1.5), n_i * 2, n_i * 3, n_i * 4]))
    hit = None
    for ni in targets:
        e, p = coeffs(vc, ni)
        mark = ""
        if hit is None and e >= 0.8:
            mark = "  <- cheapest path to E-rho^2>=0.80"; hit = ni
        print(f"  {ni:>6} | {e:>8.3f} | {p:>6.3f}{mark}")
    if hit is None:
        print("  (E-rho^2 stays <0.80 even at 4x items -> the bottleneck may be seed noise or a")
        print("   tiny version variance; add seeds, or check that your versions actually differ.)")
    if sv is not None and sv > vc["v_pi"]:
        print("  NOTE: seed/run variance exceeds residual — adding SEEDS will help more than cases.")
    print("\n(For unbalanced or nested (judge-within-case) designs, fit a linear mixed model and")
    print(" read the random-effect variances as the components — see reference/03.)")

    if args.out:
        import json
        sv = seed_variance(raw)
        comps = {"version": vc["v_p"], "item": vc["v_i"], "version_x_item": vc["v_pi"]}
        if sv is not None:
            comps["seed_run"] = float(sv)
        dstudy = [{"items": int(ni), "erho2": round(coeffs(vc, ni)[0], 3),
                   "phi": round(coeffs(vc, ni)[1], 3)} for ni in targets]
        out = {"object": "version", "n_versions": int(n_p), "n_items": int(n_i),
               "variance_components": {k: round(float(v), 4) for k, v in comps.items()},
               "erho2": round(float(erho2), 3), "phi": round(float(phi), 3),
               "verdict": verdict, "dominant_error": dominant[0],
               "seed_exceeds_residual": bool(sv is not None and sv > vc["v_pi"]),
               "dstudy": dstudy, "erho2_target_items": hit}
        json.dump(out, open(args.out, "w"), indent=2)
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
