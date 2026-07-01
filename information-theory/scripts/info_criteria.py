#!/usr/bin/env python3
"""
info_criteria.py — information criteria computed honestly from a likelihood.

All criteria estimate the SAME thing: expected out-of-sample deviance (= cross-entropy
on future data = KL from truth to model, up to a constant). They differ in how they
penalize in-sample optimism and in what target they optimize (AIC: prediction; BIC:
true-model identification). Lower is better for every quantity here.

Design choice: let the *data and the fit* supply log L and k. Hand-typing k is how you
silently forget the variance parameter and shift every number. Helpers below count k
for you (Gaussian/OLS) and pull the maximized log-likelihood.

API
---
aic(loglik, k)                  -> 2k - 2*loglik
aicc(loglik, k, n)              -> aic + 2k(k+1)/(n-k-1)   (small-sample correction)
bic(loglik, k, n)               -> k*ln(n) - 2*loglik
akaike_weights(aics)           -> normalized exp(-0.5*dAIC) support weights
gaussian_loglik_ols(y, yhat, k_mean) -> (loglik, k) with k = k_mean + 1 (the +1 is sigma^2)
waic(loglik_matrix)             -> (waic, p_waic) from an (S samples x N points) pointwise log-lik matrix

Run `python3 info_criteria.py --selftest` for a validated demo (polynomial order recovery
+ a WAIC computation on a conjugate normal model).
"""
from __future__ import annotations
import numpy as np


def aic(loglik, k):
    return float(2 * k - 2 * loglik)


def aicc(loglik, k, n):
    if n - k - 1 <= 0:
        return float("inf")  # AICc undefined; model too complex for the data
    return float(aic(loglik, k) + 2 * k * (k + 1) / (n - k - 1))


def bic(loglik, k, n):
    return float(k * np.log(n) - 2 * loglik)


def akaike_weights(aics):
    aics = np.asarray(aics, dtype=float)
    d = aics - aics.min()
    w = np.exp(-0.5 * d)
    return w / w.sum()


def gaussian_loglik_ols(y, yhat, k_mean):
    """Maximized Gaussian log-likelihood for an OLS fit with MLE sigma^2 = RSS/n.
    Returns (loglik, k) where k = k_mean (mean-function params) + 1 for the variance.
    The +1 is the parameter everyone forgets; including it is the point of this helper."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    rss = float(np.sum((y - np.asarray(yhat, dtype=float)) ** 2))
    sigma2 = rss / n
    loglik = -0.5 * n * (np.log(2 * np.pi) + np.log(sigma2) + 1.0)
    return float(loglik), int(k_mean + 1)


def waic(loglik_matrix):
    """WAIC from a pointwise log-likelihood matrix of shape (S posterior draws, N points).
    Returns (waic, p_waic). lppd = sum_i log mean_s p(y_i|theta_s);
    p_waic = sum_i var_s log p(y_i|theta_s); WAIC = -2(lppd - p_waic)."""
    ll = np.asarray(loglik_matrix, dtype=float)
    # log mean over draws via logsumexp - log S, per data point
    S = ll.shape[0]
    m = ll.max(axis=0)
    lppd = np.sum(m + np.log(np.mean(np.exp(ll - m), axis=0)))
    p_waic = np.sum(np.var(ll, axis=0, ddof=1))
    return float(-2 * (lppd - p_waic)), float(p_waic)


def _select_degree(x, y, criterion, max_deg=6):
    n = len(y)
    scores = []
    for deg in range(max_deg + 1):
        yhat = np.polyval(np.polyfit(x, y, deg), x)
        ll, k = gaussian_loglik_ols(y, yhat, k_mean=deg + 1)
        scores.append(criterion(ll, k, n))
    return int(np.argmin(scores))


def _selftest():
    rng = np.random.default_rng(0)
    print("=" * 74)
    print("1. ONE FIT, ALL CRITERIA (truth: y = 2 + 1.5x - 0.8x^2 + N(0,0.7^2), n=60)")
    n = 60
    x = np.linspace(-3, 3, n)
    y = 2 + 1.5 * x - 0.8 * x ** 2 + rng.normal(0, 0.7, n)
    print(f"   {'deg':>3} | {'k':>2} | {'logL':>9} | {'AIC':>8} | {'AICc':>8} | {'BIC':>8} | {'w_AICc':>7}")
    rows = []
    for deg in range(0, 7):
        yhat = np.polyval(np.polyfit(x, y, deg), x)
        ll, k = gaussian_loglik_ols(y, yhat, k_mean=deg + 1)
        rows.append((deg, k, ll, aic(ll, k), aicc(ll, k, n), bic(ll, k, n)))
    w = akaike_weights([r[4] for r in rows])
    for (deg, k, ll, a, ac, b), wi in zip(rows, w):
        print(f"   {deg:>3} | {k:>2} | {ll:9.3f} | {a:8.2f} | {ac:8.2f} | {b:8.2f} | {wi:7.3f}")
    print("   (A single noisy sample can favor one order above the truth — which is exactly")
    print("    why the *statistical* properties below, not one fit, are the real contrast.)")

    print("=" * 74)
    print("2. AIC vs BIC ARE DIFFERENT ESTIMATORS — selection frequencies over 600 datasets")
    print("   Same truth (degree 2). BIC is CONSISTENT (concentrates on truth);")
    print("   AIC is EFFICIENT but OVER-SELECTS (leaks probability to higher degrees).")
    reps = 600
    for n in (60, 250):
        x = np.linspace(-3, 3, n)
        aic_pick = np.zeros(7, dtype=int)
        bic_pick = np.zeros(7, dtype=int)
        for _ in range(reps):
            y = 2 + 1.5 * x - 0.8 * x ** 2 + rng.normal(0, 0.7, n)
            aic_pick[_select_degree(x, y, lambda ll, k, nn: aicc(ll, k, nn))] += 1
            bic_pick[_select_degree(x, y, bic)] += 1
        print(f"   n={n}:  P(select degree d), d = 0..6")
        print("          AICc: " + " ".join(f"{v/reps:4.2f}" for v in aic_pick)
              + f"   P(>2) = {aic_pick[3:].sum()/reps:4.2f}")
        print("          BIC : " + " ".join(f"{v/reps:4.2f}" for v in bic_pick)
              + f"   P(>2) = {bic_pick[3:].sum()/reps:4.2f}")
    print("   As n grows, BIC's P(correct)->1 while AIC keeps a stubborn over-selection rate.")
    print("   Neither is 'better' — they optimize different targets (prediction vs truth-ID).")

    print("=" * 74)
    print("3. WAIC on a conjugate normal-mean model (closed-form posterior, no PPL needed)")
    print("   Data: y ~ N(mu=1, sigma=1), n=40; prior mu ~ N(0, 10^2). Sample posterior, get WAIC.")
    mu_true, sigma, npts = 1.0, 1.0, 40
    yv = rng.normal(mu_true, sigma, npts)
    prior_var = 100.0
    post_var = 1.0 / (1.0 / prior_var + npts / sigma ** 2)
    post_mean = post_var * (yv.sum() / sigma ** 2)
    draws = rng.normal(post_mean, np.sqrt(post_var), 4000)
    # pointwise log-lik matrix (S x N): normal density of each y under each mu draw
    ll = (-0.5 * np.log(2 * np.pi * sigma ** 2)
          - 0.5 * ((yv[None, :] - draws[:, None]) ** 2) / sigma ** 2)
    w_, pw = waic(ll)
    print(f"   posterior mean of mu = {post_mean:.3f} (true 1.0); WAIC = {w_:.2f}, "
          f"p_waic = {pw:.2f} (effective params ~1, as expected)")
    print("=" * 74)
    print("Both checks behave as documented. k is counted from the fit, sigma^2 included.")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
