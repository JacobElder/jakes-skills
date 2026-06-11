#!/usr/bin/env python3
"""
check_ergodicity.py — within-person vs between-person association diagnostic.

Implements the core comparison from Fisher, Medaglia & Jeronimus (2018, PNAS):
for intensive longitudinal data (many occasions per unit), contrast the structure
of variation BETWEEN units against the structure WITHIN units over time. A large
gap is direct evidence that a group-level (nomothetic) model does not describe the
individuals — i.e., the process is non-ergodic and idiographic analysis is warranted.

It reports, for each pair of numeric variables:
  - between-person correlation (correlation of person means across units)
  - the DISTRIBUTION of within-person correlations (one per unit): mean, SD, range
  - sign disagreement: fraction of units whose within-person correlation has the
    OPPOSITE sign to the between-person correlation (the Simpson's-paradox signal)
And per variable, the variance-partition signal:
  - ratio of pooled within-person variance to between-person (person-mean) variance.
Fisher et al. found within-person variance ~2-4x larger than between; large ratios
and frequent sign disagreement both argue against pooling.

Usage:
  python check_ergodicity.py data.csv --id id --vars anx sad fatigue [--time t]
  python check_ergodicity.py data.csv --id id            # auto-uses all numeric cols
Data must be LONG format: one row per (unit, occasion).
"""
import argparse
import sys
import numpy as np
import pandas as pd
from itertools import combinations


def safe_corr(x, y):
    """Pearson r with guards for zero variance / too few points."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return np.nan, len(x)
    return float(np.corrcoef(x, y)[0, 1]), len(x)


def analyze(df, idcol, varcols, min_obs=3):
    units = df[idcol].unique()
    out = {"n_units": len(units), "vars": varcols, "pairs": [], "variance": []}

    # --- variance partition per variable ---
    for v in varcols:
        person_means = df.groupby(idcol)[v].mean()
        between_var = float(np.nanvar(person_means.values, ddof=1)) if len(person_means) > 1 else np.nan
        # pooled within variance: average of each person's variance
        within_vars = df.groupby(idcol)[v].var(ddof=1)
        within_var = float(np.nanmean(within_vars.values))
        ratio = within_var / between_var if (between_var and between_var > 0) else np.nan
        out["variance"].append({
            "var": v, "within_var": within_var, "between_var": between_var,
            "within_over_between": ratio,
        })

    # --- pairwise between vs within correlations ---
    for a, b in combinations(varcols, 2):
        # between-person: correlate person means
        pm = df.groupby(idcol)[[a, b]].mean()
        r_between, n_between = safe_corr(pm[a].values, pm[b].values)

        # within-person: one correlation per unit
        within_rs = []
        for u in units:
            sub = df[df[idcol] == u]
            r, n = safe_corr(sub[a].values, sub[b].values)
            if not np.isnan(r) and n >= min_obs:
                within_rs.append(r)
        within_rs = np.array(within_rs, float)

        if len(within_rs) == 0:
            continue
        sign_disagree = (
            float(np.mean(np.sign(within_rs) != np.sign(r_between)))
            if not np.isnan(r_between) else np.nan
        )
        out["pairs"].append({
            "pair": f"{a}~{b}",
            "r_between": r_between,
            "within_mean": float(np.nanmean(within_rs)),
            "within_sd": float(np.nanstd(within_rs, ddof=1)) if len(within_rs) > 1 else np.nan,
            "within_min": float(np.nanmin(within_rs)),
            "within_max": float(np.nanmax(within_rs)),
            "n_units_used": int(len(within_rs)),
            "frac_sign_disagree": sign_disagree,
        })
    return out


def fmt(x, p=3):
    return "  NA" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{p}f}"


def report(res):
    print(f"\n=== Ergodicity / heterogeneity diagnostic ===")
    print(f"Units: {res['n_units']}   Variables: {', '.join(res['vars'])}\n")

    print("Variance partition (within-person var / between-person var):")
    print(f"  {'variable':<16}{'within':>10}{'between':>10}{'ratio':>10}")
    for row in res["variance"]:
        flag = "  <-- within >> between" if (isinstance(row['within_over_between'], float)
                                             and row['within_over_between'] > 2) else ""
        print(f"  {row['var']:<16}{fmt(row['within_var']):>10}{fmt(row['between_var']):>10}"
              f"{fmt(row['within_over_between']):>10}{flag}")

    print("\nBetween- vs within-person correlations:")
    print(f"  {'pair':<18}{'r_betw':>9}{'win_mean':>10}{'win_sd':>9}"
          f"{'win_rng':>16}{'sign_disagree':>15}")
    for row in res["pairs"]:
        rng = f"[{fmt(row['within_min'],2)},{fmt(row['within_max'],2)}]"
        print(f"  {row['pair']:<18}{fmt(row['r_between']):>9}{fmt(row['within_mean']):>10}"
              f"{fmt(row['within_sd']):>9}{rng:>16}{fmt(row['frac_sign_disagree']):>15}")

    # verdict
    ratios = [r['within_over_between'] for r in res['variance']
              if isinstance(r['within_over_between'], float) and not np.isnan(r['within_over_between'])]
    disagrees = [p['frac_sign_disagree'] for p in res['pairs']
                 if isinstance(p['frac_sign_disagree'], float) and not np.isnan(p['frac_sign_disagree'])]
    print("\n--- Reading ---")
    if ratios and np.mean(ratios) > 2:
        print(f"* Within-person variance averages {np.mean(ratios):.1f}x between-person variance."
              " Consistent with Fisher et al.; group means poorly describe individuals.")
    if disagrees and np.mean(disagrees) > 0.15:
        print(f"* On average {100*np.mean(disagrees):.0f}% of units show a within-person association"
              " of OPPOSITE sign to the between-person one (Simpson's-paradox signal).")
    if (ratios and np.mean(ratios) > 2) or (disagrees and np.mean(disagrees) > 0.15):
        print("=> Evidence AGAINST ergodicity: prefer idiographic / pooled person-specific models.")
    else:
        print("=> No strong evidence against ergodicity in THIS diagnostic. Still report it;"
              " absence of a signal here is not proof the group model describes individuals.")
    print("\nNote: this is a descriptive screen, not a formal test. Wide within-person\n"
          "spread itself argues for person-level modeling regardless of the averages.")


def main():
    ap = argparse.ArgumentParser(description="Within- vs between-person association diagnostic.")
    ap.add_argument("csv", help="Long-format CSV: one row per (unit, occasion).")
    ap.add_argument("--id", required=True, help="Column identifying the unit/person.")
    ap.add_argument("--vars", nargs="+", help="Numeric variables (default: all numeric except id/time).")
    ap.add_argument("--time", default=None, help="Optional time column (excluded from vars).")
    ap.add_argument("--min-obs", type=int, default=3, help="Min occasions per unit to use it.")
    a = ap.parse_args()

    df = pd.read_csv(a.csv)
    if a.id not in df.columns:
        sys.exit(f"id column '{a.id}' not found. Columns: {list(df.columns)}")
    if a.vars:
        varcols = a.vars
    else:
        drop = {a.id} | ({a.time} if a.time else set())
        varcols = [c for c in df.columns if c not in drop and pd.api.types.is_numeric_dtype(df[c])]
    if len(varcols) < 1:
        sys.exit("Need at least one numeric variable.")
    res = analyze(df, a.id, varcols, min_obs=a.min_obs)
    report(res)


if __name__ == "__main__":
    main()
