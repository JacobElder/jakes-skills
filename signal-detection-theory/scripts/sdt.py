#!/usr/bin/env python3
"""
sdt.py — a small, *correct* Signal Detection Theory toolkit.

Why this exists: the SDT literature is full of formulas copied across papers
that use incompatible conventions (especially the unequal-variance d_a, where
sources disagree on whether s = sigma_noise/sigma_signal or its reciprocal).
Re-deriving from memory is where errors creep in. Use these functions instead.

Conventions used throughout (stated once, enforced everywhere):
  - z(p)            = Phi^{-1}(p)          (scipy.stats.norm.ppf)
  - Hit rate    H   = P("yes" | signal)
  - False-alarm F   = P("yes" | noise)
  - d'  = z(H) - z(F)                       sensitivity (equal-variance Gaussian)
  - c   = -0.5 * (z(H) + z(F))              criterion / bias
            c > 0  -> conservative (biased toward "no")
            c < 0  -> liberal      (biased toward "yes")
  - c'  = c / d'                            criterion relative to sensitivity
  - ln(beta) = c * d' = -0.5*(z(H)^2 - z(F)^2);  beta = exp(ln beta)
  - UNEQUAL VARIANCE: s := z-ROC slope := sigma_noise / sigma_signal.
        In recognition memory s < 1 (target SD > lure SD; ~0.8 is typical).
        d_a = sqrt(2/(1+s^2)) * (z(H) - s*z(F))      <-- note s multiplies z(F)
        A_z = Phi(d_a / sqrt(2)) = Phi(a / sqrt(1+s^2))   (a = z-ROC intercept)
        Reduces to d' and Phi(d'/sqrt(2)) when s = 1.
    If your source multiplies s by z(H) instead, it is using the reciprocal
    convention s = sigma_signal/sigma_noise. Pick one and be consistent; this
    module is internally consistent under s = sigma_noise/sigma_signal.

CLI:
  python sdt.py --hits 45 --misses 5 --fa 12 --cr 38
  python sdt.py --hr 0.9 --far 0.24 --n-signal 50 --n-noise 50
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass, asdict
import numpy as np
from scipy.stats import norm

z = norm.ppf
Phi = norm.cdf


# --------------------------------------------------------------------------- #
# Rates and extreme-cell corrections
# --------------------------------------------------------------------------- #
def rates(hits, misses, fas, crs, correction="loglinear"):
    """Return (H, F) hit and false-alarm rates with a 0/1 correction applied.

    correction:
      "loglinear" (DEFAULT, Hautus 1995): add 0.5 to ALL four cells, always,
          regardless of whether any rate is extreme. Apply uniformly across all
          participants/conditions -- correcting only the extreme ones distorts
          comparisons. Slightly conservative (underestimates d') but lowest bias.
      "2N": only fix exact 0 and 1 (0 -> 1/(2N), 1 -> 1 - 1/(2N)). More biased
          and can err in either direction; offered only for compatibility.
      "none": raw rates (will return +/-inf z for 0/1 -- usually a bug).
    """
    hits, misses, fas, crs = map(float, (hits, misses, fas, crs))
    n_signal = hits + misses
    n_noise = fas + crs
    if correction == "loglinear":
        H = (hits + 0.5) / (n_signal + 1.0)
        F = (fas + 0.5) / (n_noise + 1.0)
    elif correction == "2N":
        H = hits / n_signal
        F = fas / n_noise
        if H == 0:
            H = 1.0 / (2 * n_signal)
        elif H == 1:
            H = 1.0 - 1.0 / (2 * n_signal)
        if F == 0:
            F = 1.0 / (2 * n_noise)
        elif F == 1:
            F = 1.0 - 1.0 / (2 * n_noise)
    elif correction == "none":
        H = hits / n_signal
        F = fas / n_noise
    else:
        raise ValueError(f"unknown correction: {correction!r}")
    return H, F


def correct_rate(p, n, kind="hit"):
    """1/(2N) correction for a single extreme proportion (kept for convenience)."""
    if p == 0:
        return 1.0 / (2 * n)
    if p == 1:
        return 1.0 - 1.0 / (2 * n)
    return p


# --------------------------------------------------------------------------- #
# Equal-variance measures
# --------------------------------------------------------------------------- #
def dprime(H, F):
    return float(z(H) - z(F))


def criterion(H, F):
    return float(-0.5 * (z(H) + z(F)))


def c_prime(H, F):
    d = dprime(H, F)
    if d == 0:
        return float("nan")
    return criterion(H, F) / d


def ln_beta(H, F):
    return float(criterion(H, F) * dprime(H, F))


def beta(H, F):
    return float(np.exp(ln_beta(H, F)))


# --------------------------------------------------------------------------- #
# Unequal-variance measures (require the z-ROC slope s)
# --------------------------------------------------------------------------- #
def da(H, F, s):
    """Unequal-variance sensitivity. s = z-ROC slope = sigma_noise/sigma_signal."""
    return float(np.sqrt(2.0 / (1.0 + s ** 2)) * (z(H) - s * z(F)))


def az_from_slope(intercept_a, s):
    """Area under the unequal-variance ROC from z-ROC intercept a and slope s."""
    return float(Phi(intercept_a / np.sqrt(1.0 + s ** 2)))


def az_from_da(d_a):
    return float(Phi(d_a / np.sqrt(2.0)))


# --------------------------------------------------------------------------- #
# Rating / confidence ROC: fit the z-ROC, get slope, d_a, A_z, empirical AUC
# --------------------------------------------------------------------------- #
def fit_zroc(signal_counts, noise_counts):
    """Fit a z-ROC from confidence-rating counts.

    signal_counts, noise_counts: arrays of length K (number of confidence bins),
    ordered from "most confident SIGNAL" to "most confident NOISE" (i.e., the
    order in which you would sweep the criterion from strict to lax). Each entry
    is the number of signal (resp. noise) trials that landed in that bin.

    Returns a dict with the K-1 operating points, fitted slope/intercept,
    parametric d_a and A_z (unequal-variance), and the nonparametric trapezoidal
    AUC (the principled distribution-free alternative to A').
    """
    s_counts = np.asarray(signal_counts, float)
    n_counts = np.asarray(noise_counts, float)
    if s_counts.shape != n_counts.shape or s_counts.ndim != 1:
        raise ValueError("signal_counts and noise_counts must be 1-D, same length")
    # add 0.5 (log-linear style) so cumulative rates never hit exactly 0/1
    s_adj = s_counts + 0.5
    n_adj = n_counts + 0.5
    n_signal = s_adj.sum()
    n_noise = n_adj.sum()
    # cumulative from the "signal" end gives K-1 internal operating points
    cum_H = np.cumsum(s_adj)[:-1] / n_signal
    cum_F = np.cumsum(n_adj)[:-1] / n_noise
    zH = z(cum_H)
    zF = z(cum_F)
    # regress zH on zF: slope = s = sigma_noise/sigma_signal, intercept = a
    s_slope, a_int = np.polyfit(zF, zH, 1)
    d_a = float(np.sqrt(2.0 / (1.0 + s_slope ** 2)) * a_int)  # at zF=0, zH=a
    Az = az_from_slope(a_int, s_slope)
    # empirical trapezoidal AUC: operating points are already ascending in F
    far = np.concatenate(([0.0], cum_F, [1.0]))
    hr = np.concatenate(([0.0], cum_H, [1.0]))
    _trap = getattr(np, "trapezoid", getattr(np, "trapz", None))  # numpy 2.x rename
    auc = float(_trap(hr, far))
    return {
        "operating_points": [{"H": float(h), "F": float(f)}
                             for h, f in zip(cum_H, cum_F)],
        "zroc_slope_s": float(s_slope),
        "zroc_intercept_a": float(a_int),
        "da": d_a,
        "Az_parametric": Az,
        "auc_empirical": auc,
        "unequal_variance_flag": bool(abs(s_slope - 1.0) > 0.1),
    }


# --------------------------------------------------------------------------- #
# Uncertainty and inference on d'  (delta method)
# --------------------------------------------------------------------------- #
def var_dprime(H, F, n_signal, n_noise):
    """Delta-method variance of d' (Gourevitch & Galanter 1967; Miller 1996).

    HR and FAR are binomial proportions; propagate their variance through the
    z-transform. d(z)/dp = 1/phi(z(p)); signal and noise trials are independent,
    so the variances add. Pass the SAME (corrected) H, F you used for d'.
    """
    phiH = norm.pdf(z(H))
    phiF = norm.pdf(z(F))
    var = (H * (1 - H)) / (n_signal * phiH ** 2) + (F * (1 - F)) / (n_noise * phiF ** 2)
    return float(var)


def se_dprime(H, F, n_signal, n_noise):
    return float(np.sqrt(var_dprime(H, F, n_signal, n_noise)))


def dprime_ci(H, F, n_signal, n_noise, level=0.95):
    d = dprime(H, F)
    se = se_dprime(H, F, n_signal, n_noise)
    zc = norm.ppf(0.5 + level / 2)
    return float(d - zc * se), float(d + zc * se)


def dprime_test_zero(H, F, n_signal, n_noise):
    """Wald z-test that d' > 0. Returns (z_stat, two_sided_p)."""
    d = dprime(H, F)
    se = se_dprime(H, F, n_signal, n_noise)
    zstat = d / se
    p = 2 * (1 - norm.cdf(abs(zstat)))
    return float(zstat), float(p)


def compare_dprimes(H1, F1, ns1, nn1, H2, F2, ns2, nn2):
    """Independent-groups Wald test that d'_1 != d'_2. Returns dict.

    For WITHIN-subject comparisons prefer a GLMM (see references/estimation.md);
    this independent test assumes the two d's come from separate observers/groups.
    """
    d1, d2 = dprime(H1, F1), dprime(H2, F2)
    v1 = var_dprime(H1, F1, ns1, nn1)
    v2 = var_dprime(H2, F2, ns2, nn2)
    diff = d1 - d2
    se = np.sqrt(v1 + v2)
    zstat = diff / se
    p = 2 * (1 - norm.cdf(abs(zstat)))
    return {"d1": d1, "d2": d2, "diff": float(diff), "se_diff": float(se),
            "z": float(zstat), "p_two_sided": float(p)}


# --------------------------------------------------------------------------- #
# Optimal criterion under base rates and payoffs (decision theory)
# --------------------------------------------------------------------------- #
def optimal_criterion(p_signal, dprime_val, v_hit=1.0, v_cr=1.0, c_miss=1.0, c_fa=1.0):
    """Expected-value-maximizing criterion (Green & Swets 1966).

    beta_opt = [P(noise)/P(signal)] * [(v_cr + c_fa)/(v_hit + c_miss)]
    with all values/costs given as POSITIVE magnitudes (benefit of a correct
    response, cost of an error). c_opt = ln(beta_opt)/d'.

    Equal base rates and equal payoffs -> beta_opt = 1, c_opt = 0 (neutral).
    Rare signals -> beta_opt > 1 -> optimal observer is CONSERVATIVE.
    """
    p_noise = 1.0 - p_signal
    beta_opt = (p_noise / p_signal) * ((v_cr + c_fa) / (v_hit + c_miss))
    c_opt = float(np.log(beta_opt) / dprime_val) if dprime_val != 0 else float("nan")
    return {"beta_opt": float(beta_opt), "ln_beta_opt": float(np.log(beta_opt)),
            "c_opt": c_opt}


# --------------------------------------------------------------------------- #
# Unequal-variance bias index
# --------------------------------------------------------------------------- #
def criterion_uv(H, F, s):
    """Relative criterion in the unequal-variance model. Reduces to c at s=1.

    c_a = -(z(H) + z(F)) / (1 + s). Conventions for unequal-variance bias vary
    in the literature; this one is the natural generalization of
    c = -(z(H)+z(F))/2 (since 2 = 1+s when s=1). Report alongside the
    noise-referenced criterion k = -z(F), which is unambiguous.
    """
    return float(-(z(H) + z(F)) / (1.0 + s))


# --------------------------------------------------------------------------- #
# Maximum-likelihood unequal-variance rating ROC fit
# --------------------------------------------------------------------------- #
def fit_zroc_mle(signal_counts, noise_counts):
    """ML fit of the unequal-variance Gaussian rating model (rigorous version).

    fit_zroc() uses least squares on the z-ROC points, which is biased (the
    points are dependent and have unequal variance). This function maximizes the
    multinomial likelihood instead, which is the principled estimator. Inputs are
    ordered "most confident SIGNAL" -> "most confident NOISE" (same as fit_zroc).

    Model: noise ~ N(0,1), signal ~ N(mu, sigma^2), K-1 ordered thresholds.
      slope s = 1/sigma = sigma_noise/sigma_signal ;  d_a = mu*sqrt(2/(1+sigma^2))
      A_z = Phi(mu/sqrt(1+sigma^2)) = Phi(d_a/sqrt2)
    """
    from scipy.optimize import minimize
    s_counts = np.asarray(signal_counts, float)
    n_counts = np.asarray(noise_counts, float)
    K = s_counts.size
    # boundaries: K-1 thresholds. Higher category index = more "signal-like".
    # We placed most-confident-SIGNAL first, so reverse to ascending evidence.
    s_asc = s_counts[::-1]
    n_asc = n_counts[::-1]

    def neg_ll(theta):
        mu = theta[0]
        log_sigma = theta[1]
        sigma = np.exp(log_sigma)
        # ordered thresholds via first threshold + positive increments
        t0 = theta[2]
        incs = np.exp(theta[3:])
        thr = np.concatenate(([t0], t0 + np.cumsum(incs)))  # length K-1, ascending
        edges = np.concatenate(([-np.inf], thr, [np.inf]))
        ll = 0.0
        for k in range(K):
            lo, hi = edges[k], edges[k + 1]
            p_n = norm.cdf(hi) - norm.cdf(lo)
            p_s = norm.cdf((hi - mu) / sigma) - norm.cdf((lo - mu) / sigma)
            p_n = min(max(p_n, 1e-12), 1.0)
            p_s = min(max(p_s, 1e-12), 1.0)
            ll += n_asc[k] * np.log(p_n) + s_asc[k] * np.log(p_s)
        return -ll

    # init: mu from a rough d', sigma=1, thresholds spread over [-1,2]
    init_thr = np.linspace(-1.0, 2.0, K - 1)
    init = np.concatenate(([1.0, 0.0, init_thr[0]],
                           np.log(np.diff(init_thr) + 1e-3)))
    res = minimize(neg_ll, init, method="Nelder-Mead",
                   options={"maxiter": 20000, "xatol": 1e-6, "fatol": 1e-6})
    mu = res.x[0]
    sigma = np.exp(res.x[1])
    s_slope = 1.0 / sigma
    d_a = float(mu * np.sqrt(2.0 / (1.0 + sigma ** 2)))
    Az = float(Phi(mu / np.sqrt(1.0 + sigma ** 2)))
    return {"mu": float(mu), "sigma": float(sigma), "zroc_slope_s": float(s_slope),
            "da": d_a, "Az_parametric": Az, "neg_loglik": float(res.fun),
            "converged": bool(res.success),
            "unequal_variance_flag": bool(abs(s_slope - 1.0) > 0.1)}


# --------------------------------------------------------------------------- #
# Forced-choice conversions
# --------------------------------------------------------------------------- #
def dprime_2afc(pc):
    """Unbiased 2AFC: d' = sqrt(2) * z(Pc). Lets you put 2AFC on the same
    scale as a yes/no d' (they are NOT directly comparable without this)."""
    return float(np.sqrt(2.0) * z(pc))


def pc_from_dprime_2afc(d):
    return float(Phi(d / np.sqrt(2.0)))


# --------------------------------------------------------------------------- #
# Convenience: full report from raw counts
# --------------------------------------------------------------------------- #
@dataclass
class SDTReport:
    n_signal: float
    n_noise: float
    hit_rate: float
    fa_rate: float
    correction: str
    dprime: float
    criterion_c: float
    c_relative: float
    ln_beta: float
    beta: float


def report(hits, misses, fas, crs, correction="loglinear"):
    H, F = rates(hits, misses, fas, crs, correction=correction)
    return SDTReport(
        n_signal=float(hits + misses),
        n_noise=float(fas + crs),
        hit_rate=round(H, 4),
        fa_rate=round(F, 4),
        correction=correction,
        dprime=round(dprime(H, F), 4),
        criterion_c=round(criterion(H, F), 4),
        c_relative=round(c_prime(H, F), 4),
        ln_beta=round(ln_beta(H, F), 4),
        beta=round(beta(H, F), 4),
    )


def _main():
    p = argparse.ArgumentParser(description="Signal Detection Theory measures")
    p.add_argument("--hits", type=float)
    p.add_argument("--misses", type=float)
    p.add_argument("--fa", type=float)
    p.add_argument("--cr", type=float)
    p.add_argument("--hr", type=float, help="hit rate (alternative to counts)")
    p.add_argument("--far", type=float, help="false-alarm rate")
    p.add_argument("--n-signal", type=float, default=None)
    p.add_argument("--n-noise", type=float, default=None)
    p.add_argument("--correction", default="loglinear",
                   choices=["loglinear", "2N", "none"])
    p.add_argument("--slope", type=float, default=None,
                   help="z-ROC slope s for unequal-variance d_a")
    a = p.parse_args()

    if a.hits is not None:
        rep = report(a.hits, a.misses, a.fa, a.cr, correction=a.correction)
        out = asdict(rep)
        if a.slope is not None:
            H, F = rates(a.hits, a.misses, a.fa, a.cr, correction=a.correction)
            out["da_unequal_var"] = round(da(H, F, a.slope), 4)
    elif a.hr is not None and a.far is not None:
        out = {
            "hit_rate": a.hr, "fa_rate": a.far,
            "dprime": round(dprime(a.hr, a.far), 4),
            "criterion_c": round(criterion(a.hr, a.far), 4),
            "c_relative": round(c_prime(a.hr, a.far), 4),
            "beta": round(beta(a.hr, a.far), 4),
        }
        if a.slope is not None:
            out["da_unequal_var"] = round(da(a.hr, a.far, a.slope), 4)
    else:
        p.error("provide either --hits/--misses/--fa/--cr or --hr/--far")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    _main()
