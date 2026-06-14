#!/usr/bin/env python3
"""
rsa_power_sim.py — Monte-Carlo power analysis for congruence RSA.

Why simulate instead of using a rule of thumb? RSA tests hinge on quadratic and
product terms whose power depends jointly on N, the predictor correlation, the
predictor variances, the residual variance, and the *shape* of the hypothesized
surface. No closed-form n-per-cell rule captures that. Humberg, Nestler & Back
(2019) and Nestler et al. (2015) recommend determining N by simulation; this
script does exactly that for the broad-congruence checklist.

It answers: "If the true surface is the congruence surface I hypothesize, what
sample size do I need so that my analysis declares a BROAD congruence effect
(all four checklist conditions) with probability >= target?"

The data-generating surface used here is the canonical squared-difference
congruence model:  Z = b0 + s*Lvl - k*(X - Y)^2 + e
  - k > 0 controls the strength of the congruence effect (curvature of LOIC)
  - s controls an optional main effect along the level/LOC (set s=0 for strict)
You can also pass a fully custom b-vector.

Usage:
    python rsa_power_sim.py --n 200 300 400 --k 0.3 --rxy 0.4 --reps 500
    python rsa_power_sim.py --n 250 --k 0.5 --s 0.2 --sd-resid 1.0 --reps 800
"""
from __future__ import annotations
import argparse
import numpy as np

# reuse the estimator so power reflects the EXACT analysis you will run
from rsa_python import _design, _ols, surface_params


def _simulate_once(n, k, s, rxy, sd_pred, sd_resid, midpoint, lo, hi, rng):
    """Generate one dataset from the hypothesized congruence surface."""
    # correlated, bounded predictors on the response scale
    cov = np.array([[1.0, rxy], [rxy, 1.0]]) * sd_pred**2
    L = np.linalg.cholesky(cov)
    g = rng.standard_normal((n, 2)) @ L.T
    X = np.clip(midpoint + g[:, 0], lo, hi)
    Y = np.clip(midpoint + g[:, 1], lo, hi)
    xc, yc = X - midpoint, Y - midpoint
    level = (xc + yc) / 2.0
    z = s * level - k * (xc - yc) ** 2 + rng.normal(0, sd_resid, n)
    return xc, yc, z


def _broad_congruence(xc, yc, z, n_boot, rng):
    """Return True if all 4 broad-congruence conditions hold (bootstrap CIs)."""
    Xf = _design(xc, yc)
    keys = ["a3", "a4", "p10", "p11"]
    n = len(z)
    bvals = {kk: np.empty(n_boot) for kk in keys}
    idx = np.arange(n)
    for j in range(n_boot):
        s = rng.choice(idx, n, replace=True)
        sp = surface_params(_ols(Xf[s], z[s]))
        for kk in keys:
            bvals[kk][j] = sp[kk]

    def ci(kk):
        v = bvals[kk][np.isfinite(bvals[kk])]
        return np.percentile(v, 2.5), np.percentile(v, 97.5)

    a3lo, a3hi = ci("a3")
    a4lo, a4hi = ci("a4")
    p10lo, p10hi = ci("p10")
    p11lo, p11hi = ci("p11")
    return (a4hi < 0) and (a3lo <= 0 <= a3hi) and \
           (p10lo <= 0 <= p10hi) and (p11lo <= 1 <= p11hi)


def power_at(n, k=0.3, s=0.0, rxy=0.3, sd_pred=1.0, sd_resid=1.0,
             midpoint=4.0, lo=1.0, hi=7.0, reps=500, n_boot=400, seed=0):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(reps):
        xc, yc, z = _simulate_once(n, k, s, rxy, sd_pred, sd_resid,
                                   midpoint, lo, hi, rng)
        if _broad_congruence(xc, yc, z, n_boot, rng):
            hits += 1
    p = hits / reps
    se = (p * (1 - p) / reps) ** 0.5
    return p, se


def main():
    ap = argparse.ArgumentParser(description="Monte-Carlo power for congruence RSA")
    ap.add_argument("--n", type=int, nargs="+", required=True,
                    help="sample size(s) to evaluate")
    ap.add_argument("--k", type=float, default=0.3, help="LOIC curvature strength (>0)")
    ap.add_argument("--s", type=float, default=0.0, help="LOC/level slope (0 = strict)")
    ap.add_argument("--rxy", type=float, default=0.3, help="predictor correlation")
    ap.add_argument("--sd-pred", type=float, default=1.0)
    ap.add_argument("--sd-resid", type=float, default=1.0)
    ap.add_argument("--midpoint", type=float, default=4.0)
    ap.add_argument("--lo", type=float, default=1.0)
    ap.add_argument("--hi", type=float, default=7.0)
    ap.add_argument("--reps", type=int, default=500)
    ap.add_argument("--nboot", type=int, default=400)
    ap.add_argument("--target", type=float, default=0.80)
    a = ap.parse_args()

    print(f"\nMonte-Carlo power for BROAD congruence detection")
    print(f"  surface: Z = {a.s:g}*level - {a.k:g}*(X-Y)^2 + N(0,{a.sd_resid:g}^2)")
    print(f"  r(X,Y)={a.rxy:g}, sd_pred={a.sd_pred:g}, reps={a.reps}, "
          f"boot={a.nboot}, target={a.target:g}\n")
    print(f"  {'N':>6}  {'power':>7}  {'± 2SE':>7}")
    for n in a.n:
        p, se = power_at(n, k=a.k, s=a.s, rxy=a.rxy, sd_pred=a.sd_pred,
                         sd_resid=a.sd_resid, midpoint=a.midpoint, lo=a.lo,
                         hi=a.hi, reps=a.reps, n_boot=a.nboot, seed=n)
        flag = " <= target reached" if p >= a.target else ""
        print(f"  {n:>6}  {p:>7.3f}  {2*se:>7.3f}{flag}")
    print("\n  Note: power here is the probability that ALL FOUR broad-congruence")
    print("  conditions are simultaneously satisfied — a stricter, more honest")
    print("  target than 'a4 is significant'. Re-run with your own k/s/rxy.\n")


if __name__ == "__main__":
    main()
