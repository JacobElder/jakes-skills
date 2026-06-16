#!/usr/bin/env python3
"""Validation tests for sdt.py — analytic ground truth, not just regression."""
import numpy as np
from scipy.stats import norm
import sdt

z, Phi = norm.ppf, norm.cdf
ok = True


def check(name, cond, *info):
    global ok
    status = "PASS" if cond else "FAIL"
    if not cond:
        ok = False
    print(f"[{status}] {name}" + (f"  {info}" if info else ""))


# 1. d' and c from a clean, known operating point.
# Simulate ground truth: noise N(0,1), signal N(2,1), criterion at 1.0.
d_true = 2.0
crit = 1.0
H = 1 - Phi(crit - d_true)   # P(X>crit | signal)
F = 1 - Phi(crit)            # P(X>crit | noise)
check("d' recovers true separation", np.isclose(sdt.dprime(H, F), d_true), sdt.dprime(H, F))
# criterion c should equal crit - d'/2 = 1.0 - 1.0 = 0.0 (unbiased midpoint here)
check("c equals crit - d'/2", np.isclose(sdt.criterion(H, F), crit - d_true / 2), sdt.criterion(H, F))

# 2. Sign convention of c: liberal observer (says yes a lot) -> c < 0.
Hl, Fl = 0.95, 0.40
check("liberal observer has c < 0", sdt.criterion(Hl, Fl) < 0, sdt.criterion(Hl, Fl))
Hc, Fc = 0.40, 0.05
check("conservative observer has c > 0", sdt.criterion(Hc, Fc) > 0, sdt.criterion(Hc, Fc))

# 3. ln(beta) == c * d' == -0.5*(z(H)^2 - z(F)^2)
H2, F2 = 0.84, 0.16
lhs = sdt.ln_beta(H2, F2)
rhs = -0.5 * (z(H2) ** 2 - z(F2) ** 2)
check("ln beta identity", np.isclose(lhs, rhs), lhs, rhs)

# 4. d_a reduces to d' when s = 1.
H3, F3 = 0.90, 0.20
check("d_a == d' when s=1", np.isclose(sdt.da(H3, F3, 1.0), sdt.dprime(H3, F3)))

# 5. A_z identities agree: Phi(d_a/sqrt2) == Phi(a/sqrt(1+s^2)).
# Build an unequal-variance world: noise N(0,1), signal N(2, (1/0.8)^2) so sigma_s=1.25, s=0.8.
sigma_s = 1.25
s = 1.0 / sigma_s   # = 0.8 = sigma_noise/sigma_signal = z-ROC slope
d_mean = 2.0
# pick a criterion, derive H,F, then da
xc = 1.3
Fuv = 1 - Phi(xc)
Huv = 1 - Phi((xc - d_mean) / sigma_s)
d_a = sdt.da(Huv, Fuv, s)
# analytic Az = P(signal > noise) = Phi(d_mean / sqrt(sigma_s^2 + 1))
Az_true = Phi(d_mean / np.sqrt(sigma_s ** 2 + 1))
check("A_z from d_a matches analytic", np.isclose(sdt.az_from_da(d_a), Az_true, atol=1e-6),
      sdt.az_from_da(d_a), Az_true)

# 6. Probit-GLM identity: equal-variance SDT == probit regression.
# Fit response ~ stimulus by probit; slope on stimulus should equal d', intercept = z(F)... = -criterion-ish.
rng = np.random.default_rng(0)
n = 200000
d_glm = 1.5
crit_glm = 0.6
# signal trials
xs = rng.normal(d_glm, 1, n); ys = (xs > crit_glm).astype(int)
# noise trials
xn = rng.normal(0, 1, n); yn = (xn > crit_glm).astype(int)
H_glm = ys.mean(); F_glm = yn.mean()
# probit: z(P(yes)) = -crit + d'*stim, with stim in {0,1}
# intercept = z(F) = -crit ; slope = z(H)-z(F) = d'
import numpy as np
intercept = z(F_glm)
slope = z(H_glm) - z(F_glm)
check("probit intercept = z(F) ~ -criterion-on-noise", np.isclose(intercept, -crit_glm, atol=0.02),
      intercept, -crit_glm)
check("probit slope = d'", np.isclose(slope, d_glm, atol=0.03), slope, d_glm)

# 7. 2AFC conversion: d'_2AFC = sqrt(2) z(Pc); round-trips.
d_yn = 1.2
pc = sdt.pc_from_dprime_2afc(d_yn)
check("2AFC d' round-trip", np.isclose(sdt.dprime_2afc(pc), d_yn))

# 8. log-linear correction handles a perfect (extreme) cell without inf.
H_e, F_e = sdt.rates(50, 0, 0, 50, correction="loglinear")
check("loglinear avoids 0/1", 0 < H_e < 1 and 0 < F_e < 1, H_e, F_e)
check("loglinear d' finite & large", np.isfinite(sdt.dprime(H_e, F_e)) and sdt.dprime(H_e, F_e) > 2)

# 9. fit_zroc recovers slope ~ s on simulated rating data.
# 6-point confidence scale; simulate from the unequal-variance world above.
K = 6
# criteria spread across the evidence axis
crits = np.linspace(-1.0, 3.0, K - 1)
def bin_counts(mu, sigma, ntot):
    draws = rng.normal(mu, sigma, ntot)
    # bin by criteria into K ordered bins, "most confident signal" first
    edges = np.concatenate(([np.inf], crits[::-1], [-np.inf]))
    counts = np.zeros(K)
    for i in range(K):
        hi, lo = edges[i], edges[i + 1]
        counts[i] = np.sum((draws <= hi) & (draws > lo))
    return counts
sig = bin_counts(d_mean, sigma_s, 50000)
noi = bin_counts(0.0, 1.0, 50000)
fit = sdt.fit_zroc(sig, noi)
check("fit_zroc slope ~ s", np.isclose(fit["zroc_slope_s"], s, atol=0.05), fit["zroc_slope_s"], s)
check("fit_zroc flags unequal variance", fit["unequal_variance_flag"])
check("fit_zroc empirical AUC ~ analytic Az", np.isclose(fit["auc_empirical"], Az_true, atol=0.02),
      fit["auc_empirical"], Az_true)

print("\nALL PASS" if ok else "\nSOME FAILURES")

# --------------------------------------------------------------------------- #
# Extended tests: SE/inference, optimal criterion, UV bias, MLE ROC
# --------------------------------------------------------------------------- #
print("\n--- extended ---")

# 10. SE of d' via delta method matches a Monte-Carlo SE.
rng2 = np.random.default_rng(7)
d_se_true = 1.5
crit_se = 0.5
ns_se = nn_se = 200
Hs = 1 - Phi(crit_se - d_se_true)
Fs = 1 - Phi(crit_se)
ds = []
for _ in range(4000):
    h = rng2.binomial(ns_se, Hs); f = rng2.binomial(nn_se, Fs)
    Hh, Ff = sdt.rates(h, ns_se - h, f, nn_se - f, correction="loglinear")
    ds.append(sdt.dprime(Hh, Ff))
mc_se = np.std(ds, ddof=1)
delta_se = sdt.se_dprime(Hs, Fs, ns_se, nn_se)
check("delta-method SE(d') ~ Monte-Carlo SE", np.isclose(delta_se, mc_se, rtol=0.15),
      round(delta_se, 4), round(mc_se, 4))

# 11. dprime_test_zero: a clearly-above-chance observer is significant; chance is not.
_, p_sig = sdt.dprime_test_zero(0.9, 0.2, 100, 100)
check("d'>0 test significant for strong observer", p_sig < 0.001, p_sig)
Hc0, Fc0 = sdt.rates(52, 48, 50, 50, correction="loglinear")  # ~chance
_, p_chance = sdt.dprime_test_zero(Hc0, Fc0, 100, 100)
check("d'>0 test non-significant near chance", p_chance > 0.05, round(p_chance, 3))

# 12. optimal_criterion: symmetric -> beta=1,c=0; rare signal -> conservative.
o_sym = sdt.optimal_criterion(0.5, 2.0)
check("optimal beta=1, c=0 for symmetric case",
      np.isclose(o_sym["beta_opt"], 1.0) and np.isclose(o_sym["c_opt"], 0.0))
o_rare = sdt.optimal_criterion(0.2, 2.0)
check("rare signals -> beta_opt>1 and c_opt>0 (conservative)",
      o_rare["beta_opt"] > 1 and o_rare["c_opt"] > 0, round(o_rare["beta_opt"], 2))

# 13. criterion_uv reduces to c at s=1.
Huv2, Fuv2 = 0.8, 0.25
check("criterion_uv == c at s=1", np.isclose(sdt.criterion_uv(Huv2, Fuv2, 1.0),
                                             sdt.criterion(Huv2, Fuv2)))

# 14. MLE ROC fit recovers slope and Az on simulated unequal-variance data.
fit_mle = sdt.fit_zroc_mle(sig, noi)  # reuse sim from test 9
check("fit_zroc_mle slope ~ s", np.isclose(fit_mle["zroc_slope_s"], s, atol=0.06),
      round(fit_mle["zroc_slope_s"], 3), s)
check("fit_zroc_mle Az ~ analytic", np.isclose(fit_mle["Az_parametric"], Az_true, atol=0.02),
      round(fit_mle["Az_parametric"], 3), round(Az_true, 3))

print("\nEXTENDED ALL PASS" if ok else "\nEXTENDED SOME FAILURES")
