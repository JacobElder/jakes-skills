#!/usr/bin/env python3
"""
power_analysis.py — sample size, power, and MDE for two-arm experiments.

Pure standard library (no numpy/scipy needed) so it runs in any environment.
Uses the standard normal approximation, which is what practitioners use for
experiment planning and is accurate well within the precision the inputs justify.

Supports:
  - outcome types: proportion (rates) and mean (continuous)
  - solve for: n (sample size), power, or mde
  - cluster randomization via design effect (ICC + cluster size)
  - multiple-comparison correction (Bonferroni on alpha)
  - one- or two-sided tests

Assumes the metric is a simple proportion or mean with independent observations
at the analysis unit. For RATIO metrics with a random denominator
(revenue-per-session, clicks-per-pageview when randomizing by user), the naive
variance is wrong: compute the variance separately via the delta method or a
user-level bootstrap, then pass it in through the `--type mean --sd <value>`
path. See references/power-and-sample-size.md. This tool also assumes two arms
with equal allocation; for >2 arms, size each pairwise comparison and apply the
comparison correction with --comparisons.

Examples
--------
# How many users per arm to detect a lift from 10% -> 11% (1pp absolute MDE)?
python power_analysis.py --solve n --type proportion --baseline 0.10 --mde 0.01

# Same, but as a 10% RELATIVE lift, 90% power, and 3 metrics (Bonferroni):
python power_analysis.py --solve n --type proportion --baseline 0.10 \
    --mde 0.10 --relative --power 0.90 --comparisons 3

# Continuous metric: detect a 0.5-unit difference, sd=4, two arms:
python power_analysis.py --solve n --type mean --mde 0.5 --sd 4

# What power do I actually have with 5000 per arm?
python power_analysis.py --solve power --type proportion --baseline 0.10 \
    --mde 0.01 --n 5000

# What's the smallest effect I can detect with 20000 per arm?
python power_analysis.py --solve mde --type proportion --baseline 0.10 --n 20000

# Cluster-randomized by store (ICC 0.02, ~200 users/store):
python power_analysis.py --solve n --type proportion --baseline 0.10 --mde 0.01 \
    --icc 0.02 --cluster-size 200
"""

import argparse
import math
import sys


# --- normal distribution helpers (no scipy) ---------------------------------

def norm_cdf(z: float) -> float:
    """Standard normal CDF via the error function."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Inverse standard normal CDF (Acklam's algorithm + one Halley refinement)."""
    if not (0.0 < p < 1.0):
        raise ValueError("probability must be in (0, 1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
            ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    elif p <= phigh:
        q = p - 0.5
        r = q * q
        x = (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5])*q / \
            (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
            ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1)
    # one Halley step for full double precision
    e = norm_cdf(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    x = x - u / (1 + x * u / 2)
    return x


# --- core calculations -------------------------------------------------------

def z_alpha(alpha: float, sided: int) -> float:
    return norm_ppf(1 - alpha / 2) if sided == 2 else norm_ppf(1 - alpha)


def design_effect(icc: float, cluster_size: float) -> float:
    return 1.0 + (cluster_size - 1.0) * icc


def n_for_proportion(p1, p2, alpha, power, sided):
    za = z_alpha(alpha, sided)
    zb = norm_ppf(power)
    pbar = (p1 + p2) / 2.0
    term = za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1*(1-p1) + p2*(1-p2))
    return term ** 2 / (p2 - p1) ** 2


def n_for_mean(delta, sd, alpha, power, sided):
    za = z_alpha(alpha, sided)
    zb = norm_ppf(power)
    return (za + zb) ** 2 * (2 * sd ** 2) / delta ** 2


def power_for_proportion(p1, p2, n, alpha, sided):
    za = z_alpha(alpha, sided)
    pbar = (p1 + p2) / 2.0
    zpow = (abs(p2 - p1) * math.sqrt(n) - za * math.sqrt(2 * pbar * (1 - pbar))) \
        / math.sqrt(p1*(1-p1) + p2*(1-p2))
    return norm_cdf(zpow)


def power_for_mean(delta, sd, n, alpha, sided):
    za = z_alpha(alpha, sided)
    zpow = abs(delta) * math.sqrt(n / (2 * sd ** 2)) - za
    return norm_cdf(zpow)


def mde_for_mean(sd, n, alpha, power, sided):
    za = z_alpha(alpha, sided)
    zb = norm_ppf(power)
    return (za + zb) * math.sqrt(2 * sd ** 2 / n)


def mde_for_proportion(baseline, n, alpha, power, sided):
    # solve numerically for absolute lift d s.t. required n(d) == n
    def needed(d):
        p2 = baseline + d
        if not (0 < p2 < 1):
            return float("inf")
        return n_for_proportion(baseline, p2, alpha, power, sided)
    lo, hi = 1e-6, min(1 - baseline - 1e-6, baseline if baseline < 0.5 else 1 - baseline) 
    hi = max(hi, 1e-4)
    # expand hi until needed(hi) <= n (smaller effect needs more n; bigger effect needs less)
    for _ in range(60):
        if needed(hi) <= n:
            break
        hi *= 1.5
        if baseline + hi >= 1:
            hi = (1 - baseline) - 1e-6
            break
    # bisection: needed() is decreasing in d
    for _ in range(200):
        mid = (lo + hi) / 2
        if needed(mid) > n:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# --- CLI ---------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Two-arm experiment power / sample size / MDE.")
    ap.add_argument("--solve", choices=["n", "power", "mde"], required=True,
                    help="quantity to solve for")
    ap.add_argument("--type", choices=["proportion", "mean"], required=True,
                    dest="otype", help="outcome type")
    ap.add_argument("--baseline", type=float, help="control rate (proportion type)")
    ap.add_argument("--sd", type=float, help="outcome std dev (mean type)")
    ap.add_argument("--mde", type=float,
                    help="minimum detectable effect; absolute by default, "
                         "or relative fraction with --relative")
    ap.add_argument("--relative", action="store_true",
                    help="interpret --mde as a relative lift (e.g. 0.10 = +10%%)")
    ap.add_argument("--n", type=float, help="sample size per arm (for --solve power/mde)")
    ap.add_argument("--alpha", type=float, default=0.05, help="significance level (default 0.05)")
    ap.add_argument("--power", type=float, default=0.80, help="target power (default 0.80)")
    ap.add_argument("--sided", type=int, choices=[1, 2], default=2, help="test sidedness (default 2)")
    ap.add_argument("--comparisons", type=int, default=1,
                    help="number of comparisons; Bonferroni-adjusts alpha (default 1)")
    ap.add_argument("--icc", type=float, default=0.0, help="intracluster correlation (cluster design)")
    ap.add_argument("--cluster-size", type=float, default=1.0, help="avg units per cluster")
    args = ap.parse_args(argv)

    alpha = args.alpha / args.comparisons  # Bonferroni
    deff = design_effect(args.icc, args.cluster_size) if args.icc > 0 else 1.0

    # resolve absolute effect for proportion type
    abs_mde = None
    p1 = p2 = None
    if args.otype == "proportion":
        if args.baseline is None:
            ap.error("--baseline is required for --type proportion")
        if args.mde is not None:
            abs_mde = args.baseline * args.mde if args.relative else args.mde
            p1, p2 = args.baseline, args.baseline + abs_mde
    else:
        if args.sd is None:
            ap.error("--sd is required for --type mean")
        if args.mde is not None:
            abs_mde = args.baseline * args.mde if (args.relative and args.baseline) else args.mde

    print("=" * 60)
    print(f"  Two-arm {args.otype} test | {args.sided}-sided | alpha={args.alpha}"
          + (f" (adj {alpha:.5f} for {args.comparisons} comparisons)" if args.comparisons > 1 else ""))
    if deff != 1.0:
        print(f"  Cluster design: ICC={args.icc}, cluster size={args.cluster_size} -> DEFF={deff:.2f}")
    print("=" * 60)

    if args.solve == "n":
        if abs_mde is None:
            ap.error("--mde is required to solve for n")
        if args.otype == "proportion":
            n = n_for_proportion(p1, p2, alpha, args.power, args.sided)
            print(f"  Baseline:        {args.baseline:.4f}")
            print(f"  Treatment:       {p2:.4f}  (abs MDE {abs_mde:+.4f}"
                  + (f", rel {args.mde:+.1%}" if args.relative else "") + ")")
        else:
            n = n_for_mean(abs_mde, args.sd, alpha, args.power, args.sided)
            print(f"  MDE:             {abs_mde:.4f}   SD: {args.sd}")
        n_eff = math.ceil(n * deff)
        print(f"  Power:           {args.power}")
        print("-" * 60)
        print(f"  REQUIRED N PER ARM:   {n_eff:,}")
        print(f"  TOTAL (2 arms):       {2 * n_eff:,}")
        if deff != 1.0:
            print(f"  (pre-cluster N/arm:   {math.ceil(n):,}; clusters/arm: "
                  f"{math.ceil(n_eff / args.cluster_size):,})")

    elif args.solve == "power":
        if args.n is None or abs_mde is None:
            ap.error("--n and --mde are required to solve for power")
        n_per_cluster_adj = args.n / deff  # effective n after clustering
        if args.otype == "proportion":
            pw = power_for_proportion(p1, p2, n_per_cluster_adj, alpha, args.sided)
        else:
            pw = power_for_mean(abs_mde, args.sd, n_per_cluster_adj, alpha, args.sided)
        print(f"  N per arm:       {int(args.n):,}"
              + (f"  (effective {n_per_cluster_adj:,.0f} after DEFF)" if deff != 1.0 else ""))
        print(f"  MDE:             {abs_mde:.4f}")
        print("-" * 60)
        print(f"  ACHIEVED POWER:       {pw:.3f}")
        if pw < 0.795:
            print("  ** underpowered (<0.80) — expect inflated effect sizes on wins.")

    else:  # mde
        if args.n is None:
            ap.error("--n is required to solve for mde")
        n_eff = args.n / deff
        if args.otype == "proportion":
            d = mde_for_proportion(args.baseline, n_eff, alpha, args.power, args.sided)
            print(f"  N per arm:       {int(args.n):,}")
            print(f"  Baseline:        {args.baseline:.4f}")
            print("-" * 60)
            print(f"  SMALLEST DETECTABLE ABS LIFT:  {d:+.4f}  (to {args.baseline + d:.4f})")
            print(f"  AS RELATIVE LIFT:              {d / args.baseline:+.1%}")
        else:
            d = mde_for_mean(args.sd, n_eff, alpha, args.power, args.sided)
            print(f"  N per arm:       {int(args.n):,}   SD: {args.sd}")
            print("-" * 60)
            print(f"  SMALLEST DETECTABLE DIFFERENCE: {d:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
