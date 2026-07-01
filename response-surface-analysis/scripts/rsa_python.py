#!/usr/bin/env python3
"""
rsa_python.py — Congruence Response Surface Analysis in Python.

There is no mature, maintained Python package for the Edwards/Schoenbrodt
congruence-RSA tradition (the R `RSA` package is the reference implementation).
This module fills that gap with a transparent, dependency-light implementation:

  * second-order polynomial regression  Z ~ X + Y + X^2 + X*Y + Y^2
  * the surface parameters a1..a5 and the first-principal-axis parameters p10, p11
  * the incremental block test for the three higher-order terms (gate)
  * percentile bootstrap CIs for every surface parameter (the a's and p's are
    NONLINEAR functions of the b's, so delta-method SEs are unreliable in
    typical N; bootstrap is the default for a reason)
  * an automated evaluation of the Humberg, Nestler & Back (2019) checklist for
    a *broad* and a *strict* congruence effect
  * a 3D surface plot with the LOC and LOIC drawn on it

Design stances baked in (see the skill's references/ for the why):
  - predictors are centered on a SINGLE COMMON constant (pooled scale midpoint
    by default), never on their separate means — separate-mean centering
    silently destroys commensurability and moves the line of congruence off X=Y.
  - no single parameter proves congruence. The checklist is evaluated as a
    conjunction; `a4 < 0` alone is reported as INSUFFICIENT.

Usage (CLI):
    python rsa_python.py data.csv --x self --y other --z outcome --midpoint 4
    python rsa_python.py data.csv --x self --y other --z outcome   # auto midpoint

Usage (import):
    from rsa_python import fit_rsa
    res = fit_rsa(df, "self", "other", "outcome", center=4.0)
    res.summary()
    res.plot("surface.png")

References: Edwards & Parry (1993); Edwards (2002); Shanock et al. (2010);
Humberg, Nestler & Back (2019). Parameter formulas follow Edwards (2002).
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------
# Core estimation
# ----------------------------------------------------------------------------
def _design(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Design matrix for [intercept, X, Y, X^2, XY, Y^2]."""
    return np.column_stack([np.ones_like(x), x, y, x * x, x * y, y * y])


def _ols(Xmat: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Plain OLS coefficients via least squares (b0..b5)."""
    beta, *_ = np.linalg.lstsq(Xmat, z, rcond=None)
    return beta


def surface_params(b: np.ndarray) -> dict:
    """
    Compute surface parameters from polynomial coefficients
    b = [b0, b1, b2, b3, b4, b5].

      a1 = b1 + b2            slope of surface along Line Of Congruence (X=Y)
      a2 = b3 + b4 + b5       curvature along LOC
      a3 = b1 - b2            slope along Line Of INcongruence (X=-Y)
      a4 = b3 - b4 + b5       curvature along LOIC   (congruence => a4 < 0)
      a5 = b3 - b5            relates to rotation of the first principal axis

    First principal axis projected onto the X-Y plane:  Y = p10 + p11 * X.
    Computed from the stationary point and the eigenvectors of the Hessian of
    the quadratic form, which is sign-convention-safe (matches the RSA package).
    """
    b0, b1, b2, b3, b4, b5 = b
    a1 = b1 + b2
    a2 = b3 + b4 + b5
    a3 = b1 - b2
    a4 = b3 - b4 + b5
    a5 = b3 - b5

    # Stationary point (X0, Y0): solve gradient = 0 of the quadratic.
    # grad: [b1 + 2 b3 X + b4 Y, b2 + b4 X + 2 b5 Y] = 0
    denom = 4.0 * b3 * b5 - b4 * b4
    if abs(denom) < 1e-12:
        x0 = y0 = np.nan
    else:
        x0 = (b2 * b4 - 2.0 * b1 * b5) / denom
        y0 = (b1 * b4 - 2.0 * b2 * b3) / denom

    # Principal axes = eigenvectors of the quadratic-form matrix [[b3, b4/2],[b4/2, b5]].
    Q = np.array([[b3, b4 / 2.0], [b4 / 2.0, b5]])
    eigvals, eigvecs = np.linalg.eigh(Q)  # ascending eigenvalues
    # "First" principal axis: the one with the LARGER eigenvalue (max curvature),
    # which is the ridge convention used in RSA congruence work.
    v = eigvecs[:, np.argmax(eigvals)]
    if abs(v[0]) < 1e-12:
        p11 = np.inf
        p10 = np.nan
    else:
        p11 = v[1] / v[0]          # slope of the axis
        p10 = y0 - p11 * x0        # intercept (axis passes through stationary point)

    return dict(a1=a1, a2=a2, a3=a3, a4=a4, a5=a5,
                p10=p10, p11=p11, X0=x0, Y0=y0,
                eig_min=float(eigvals.min()), eig_max=float(eigvals.max()))


# ----------------------------------------------------------------------------
# Result container
# ----------------------------------------------------------------------------
@dataclass
class RSAResult:
    coef: dict                      # b0..b5
    params: dict                    # a1..a5, p10, p11, stationary point
    ci: dict                        # bootstrap percentile CIs for each param
    boot_p: dict                    # bootstrap two-sided p (share crossing 0 / ref)
    r2_full: float
    r2_linear: float
    block_F: float
    block_p: float
    block_df: tuple
    n: int
    center: float
    commensurate_warn: Optional[str]
    _data: tuple = field(repr=False, default=None)  # (xc, yc, z) centered

    # --- congruence checklist (Humberg, Nestler & Back, 2019) ----------------
    def checklist(self) -> dict:
        ci = self.ci
        a3_lo, a3_hi = ci["a3"]
        a4_lo, a4_hi = ci["a4"]
        p10_lo, p10_hi = ci["p10"]
        p11_lo, p11_hi = ci["p11"]
        a1_lo, a1_hi = ci["a1"]
        a2_lo, a2_hi = ci["a2"]

        c1 = a4_hi < 0                         # a4 significantly negative
        c2 = (a3_lo <= 0 <= a3_hi)             # a3 not different from 0
        c3 = (p10_lo <= 0 <= p10_hi)           # no lateral shift of FPA
        c4 = (p11_lo <= 1 <= p11_hi)           # no rotation of FPA
        broad = c1 and c2 and c3 and c4
        # strict additionally requires a flat ridge along the LOC:
        c5 = (a1_lo <= 0 <= a1_hi)
        c6 = (a2_lo <= 0 <= a2_hi)
        strict = broad and c5 and c6
        return {
            "C1 a4 < 0 (inverted-U over LOIC)": c1,
            "C2 a3 = 0 (symmetric; max at congruence)": c2,
            "C3 p10 = 0 (no lateral shift of ridge)": c3,
            "C4 p11 = 1 (no rotation of ridge)": c4,
            "BROAD congruence effect": broad,
            "C5 a1 = 0 (flat LOC slope)": c5,
            "C6 a2 = 0 (flat LOC curvature)": c6,
            "STRICT congruence effect": strict,
        }

    def summary(self) -> None:
        print(f"\nResponse Surface Analysis  (N = {self.n}, centered on {self.center:g})")
        if self.commensurate_warn:
            print(f"  ⚠ COMMENSURABILITY: {self.commensurate_warn}")
        print("\n  Polynomial coefficients (centered predictors):")
        for k in ["b0", "b1", "b2", "b3", "b4", "b5"]:
            print(f"    {k} = {self.coef[k]:+.4f}")
        print(f"\n  Model R² (full)   = {self.r2_full:.4f}")
        print(f"  Model R² (linear) = {self.r2_linear:.4f}")
        print(f"  BLOCK TEST (gate): higher-order terms add R² = "
              f"{self.r2_full - self.r2_linear:.4f}")
        print(f"    F({self.block_df[0]:.0f}, {self.block_df[1]:.0f}) = "
              f"{self.block_F:.3f}, p = {self.block_p:.4g}")
        if self.block_p >= 0.05:
            print("    → Surface is NOT justified. The quadratic/product terms do not")
            print("      jointly improve fit. Report a linear model; do not interpret a1..a5.")
        print("\n  Surface parameters  [95% bootstrap percentile CI]:")
        order = ["a1", "a2", "a3", "a4", "a5", "p10", "p11"]
        labels = {
            "a1": "LOC slope        ", "a2": "LOC curvature    ",
            "a3": "LOIC slope       ", "a4": "LOIC curvature   ",
            "a5": "rotation comp.   ", "p10": "ridge intercept  ",
            "p11": "ridge slope      ",
        }
        for k in order:
            lo, hi = self.ci[k]
            star = "*" if (lo > 0 or hi < 0) and k not in ("p11",) else " "
            print(f"    {k}  {labels[k]} = {self.params[k]:+.4f}  "
                  f"[{lo:+.4f}, {hi:+.4f}] {star}")
        print(f"    stationary point (X0, Y0) = "
              f"({self.params['X0']:+.3f}, {self.params['Y0']:+.3f})")
        a3_lo, a3_hi = self.ci["a3"]
        if a3_lo > 0 or a3_hi < 0:
            print("\n  ⚠  DIRECTIONALITY: a3 CI excludes 0 — the mismatch effect is")
            print("     ASYMMETRIC. A directional claim (e.g. 'overestimation is worse')")
            print("     is licensed by a3 ≠ 0, but note: asymmetry means the effect is")
            print("     NOT pure (symmetric) congruence. You cannot simultaneously claim")
            print("     pure congruence AND a directional advantage.")
        else:
            print("\n  NOTE (directionality): a3 CI includes 0 — the surface is")
            print("     symmetric. The data do NOT speak to which direction of mismatch")
            print("     (over- vs under-estimation) is worse (directionality fallacy).")
        print("\n  Congruence checklist (Humberg, Nestler & Back, 2019):")
        for cond, ok in self.checklist().items():
            print(f"    [{'PASS' if ok else 'fail'}] {cond}")
        print("\n  NOTE: a single parameter (e.g. a4<0) does NOT establish congruence.")
        print("  Congruence requires the full conjunction above.\n")

    def plot(self, path: str = "rsa_surface.png", n_grid: int = 40) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

        xc, yc, z = self._data
        b = np.array([self.coef[f"b{i}"] for i in range(6)])
        rng = max(np.abs(xc).max(), np.abs(yc).max())
        g = np.linspace(-rng, rng, n_grid)
        XX, YY = np.meshgrid(g, g)
        ZZ = (b[0] + b[1] * XX + b[2] * YY + b[3] * XX**2
              + b[4] * XX * YY + b[5] * YY**2)

        fig = plt.figure(figsize=(8, 6.5))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_surface(XX, YY, ZZ, cmap="viridis", alpha=0.85,
                        linewidth=0, antialiased=True)
        # LOC (X=Y) and LOIC (X=-Y)
        t = np.linspace(-rng, rng, n_grid)
        loc_z = b[0] + (b[1] + b[2]) * t + (b[3] + b[4] + b[5]) * t**2
        loic_z = b[0] + (b[1] - b[2]) * t + (b[3] - b[4] + b[5]) * t**2
        ax.plot(t, t, loc_z, color="white", lw=3, label="LOC (X=Y)")
        ax.plot(t, -t, loic_z, color="red", lw=3, label="LOIC (X=-Y)")
        ax.set_xlabel("X (centered)")
        ax.set_ylabel("Y (centered)")
        ax.set_zlabel("Outcome")
        ax.legend(loc="upper left")
        ax.set_title("Response surface  (white=LOC, red=LOIC)")
        fig.tight_layout()
        fig.savefig(path, dpi=130)
        plt.close(fig)
        return path


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------
def fit_rsa(df: pd.DataFrame, x: str, y: str, z: str,
            center: Optional[float] = None, n_boot: int = 2000,
            seed: int = 1, ci: float = 0.95) -> RSAResult:
    """
    Fit a congruence RSA.

    center : common constant subtracted from BOTH X and Y. If None, uses the
             pooled midpoint ((min+max)/2 across both predictors), which keeps
             the predictors commensurable and the LOC on X=Y. Pass the scale
             midpoint explicitly when you know it (e.g. 4 on a 1-7 scale).
    """
    d = df[[x, y, z]].dropna().to_numpy(dtype=float)
    xr, yr, zr = d[:, 0], d[:, 1], d[:, 2]
    n = len(zr)

    # Commensurability diagnostic (heuristic, not a substitute for judgment).
    warn = None
    rng_x = xr.max() - xr.min()
    rng_y = yr.max() - yr.min()
    if rng_x > 0 and rng_y > 0:
        ratio = max(rng_x, rng_y) / min(rng_x, rng_y)
        if ratio > 1.5 or abs(xr.mean() - yr.mean()) > 0.5 * (np.std(np.r_[xr, yr]) + 1e-9):
            warn = (f"X and Y differ noticeably in range/level "
                    f"(ranges {rng_x:.2g} vs {rng_y:.2g}). Confirm they are on the "
                    f"SAME metric before interpreting congruence.")

    if center is None:
        center = (min(xr.min(), yr.min()) + max(xr.max(), yr.max())) / 2.0

    xc, yc = xr - center, yr - center

    Xfull = _design(xc, yc)
    b = _ols(Xfull, zr)
    fitted = Xfull @ b
    ss_tot = float(np.sum((zr - zr.mean()) ** 2))
    r2_full = 1.0 - float(np.sum((zr - fitted) ** 2)) / ss_tot

    # linear-only model for the block test
    Xlin = Xfull[:, :3]
    blin = _ols(Xlin, zr)
    r2_lin = 1.0 - float(np.sum((zr - Xlin @ blin) ** 2)) / ss_tot

    # incremental F for the 3 higher-order terms
    q = 3
    df_res = n - 6
    block_F = ((r2_full - r2_lin) / q) / ((1 - r2_full) / df_res)
    from scipy import stats
    block_p = float(stats.f.sf(block_F, q, df_res))

    coef = {f"b{i}": float(b[i]) for i in range(6)}
    params = surface_params(b)

    # ---- bootstrap CIs for the surface parameters --------------------------
    rng = np.random.default_rng(seed)
    keys = ["a1", "a2", "a3", "a4", "a5", "p10", "p11"]
    boot = {k: np.empty(n_boot) for k in keys}
    idx_all = np.arange(n)
    for bI in range(n_boot):
        idx = rng.choice(idx_all, size=n, replace=True)
        bb = _ols(Xfull[idx], zr[idx])
        sp = surface_params(bb)
        for k in keys:
            boot[k][bI] = sp[k]
    lo_q, hi_q = (1 - ci) / 2 * 100, (1 + ci) / 2 * 100
    ci_out, bp = {}, {}
    for k in keys:
        vals = boot[k][np.isfinite(boot[k])]
        ci_out[k] = (float(np.percentile(vals, lo_q)), float(np.percentile(vals, hi_q)))
        ref = 1.0 if k == "p11" else 0.0
        frac = np.mean(vals > ref)
        bp[k] = float(2 * min(frac, 1 - frac))

    return RSAResult(coef=coef, params=params, ci=ci_out, boot_p=bp,
                     r2_full=r2_full, r2_linear=r2_lin,
                     block_F=float(block_F), block_p=block_p, block_df=(q, df_res),
                     n=n, center=float(center), commensurate_warn=warn,
                     _data=(xc, yc, zr))


def _main():
    ap = argparse.ArgumentParser(description="Congruence Response Surface Analysis")
    ap.add_argument("csv")
    ap.add_argument("--x", required=True)
    ap.add_argument("--y", required=True)
    ap.add_argument("--z", required=True)
    ap.add_argument("--midpoint", type=float, default=None,
                    help="Common centering constant (scale midpoint). "
                         "Default: pooled midpoint of the two predictors.")
    ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--plot", default=None, help="Path to save 3D surface PNG.")
    a = ap.parse_args()
    if a.midpoint is None:
        print(
            "\n⚠  WARNING: --midpoint not supplied.\n"
            "   Congruence RSA requires centering BOTH predictors on the SCALE midpoint\n"
            "   (e.g. 4 for a 1–7 scale), not on a data-derived value. The pooled data\n"
            "   midpoint shifts with sample composition and silently corrupts a1–a5 and\n"
            "   the line of congruence. Specify --midpoint <value> before trusting results.\n",
            file=sys.stderr,
        )
    df = pd.read_csv(a.csv)
    res = fit_rsa(df, a.x, a.y, a.z, center=a.midpoint, n_boot=a.nboot)
    res.summary()
    if a.plot:
        print(f"  surface plot -> {res.plot(a.plot)}")


if __name__ == "__main__":
    _main()
