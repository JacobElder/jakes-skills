# Worked Examples (with real simulation output)

Two short simulations that make the skill's central claims concrete. The numbers below are actual output from the code shown; rerun it to reproduce (results vary trivially with the seed). Use these when an explanation lands better with a number than with prose, and adapt the code to a questioner's specific n / skew / dispersion when it helps.

## Contents
- Example 1 — how fast does the CLT actually rescue the t-test?
- Example 2 — overdispersion biases the SE, not the coefficient
- How to use these in an answer

## Example 1 — how fast does the CLT actually rescue the t-test?

**Claim being illustrated:** skew distorts the *level* of the t-test at small n, large n rescues it, and the speed of rescue depends on skew (Berry–Esseen: error ∝ skewness/√n). The mechanism is visible in the tail asymmetry.

Setup: one-sample t-test (the case most sensitive to skew) of the true mean of strongly right-skewed lognormal(0,1) data, nominal two-sided α = 0.05, 60,000 replications per n.

```python
import numpy as np
from scipy import stats
rng = np.random.default_rng(7)
true_mean = np.exp(0.5)            # mean of lognormal(0,1)
for n in [10, 30, 100, 1000]:
    d = rng.lognormal(0, 1, size=(60000, n))
    t = (d.mean(1) - true_mean) / (d.std(1, ddof=1) / np.sqrt(n))
    crit = stats.t.ppf(0.975, n - 1)
    print(n, np.mean(np.abs(t) > crit), np.mean(t < -crit), np.mean(t > crit))
```

| n | actual Type I error (nominal 0.05) | left-tail rejections | right-tail rejections |
|---|---|---|---|
| 10 | **0.160** | 0.159 | 0.001 |
| 30 | **0.117** | 0.114 | 0.003 |
| 100 | **0.083** | 0.078 | 0.005 |
| 1000 | **0.056** | 0.043 | 0.013 |

What to read off this:
- At n = 10 the test rejects **three times too often** (16% vs 5%) — and almost entirely in one tail. Right skew pulls the sample SD up when the sample mean is high and makes the studentized statistic systematically negative, so the rejections pile into the left tail. This asymmetry, not just the inflated total, is the signature of skew.
- The error decays roughly like 1/√n (0.160 → 0.117 → 0.083 → 0.056), exactly the Berry–Esseen rate. It is *not* gone by n = 100; lognormal(0,1) is severely skewed.
- By n = 1000 the level is close to nominal — the CLT has done its work — though a faint tail asymmetry lingers.

The lesson for advice: "the CLT makes it fine" is true but quantitative. For *severe* skew you may need n in the hundreds-to-thousands before the nominal level is trustworthy; for mild skew, dozens suffice. And note this is the worst case (one-sample); a two-sample test with comparable group sizes is far more robust because the skew partially cancels across groups.

## Example 2 — overdispersion biases the SE, not the coefficient

**Claim being illustrated:** fitting overdispersed counts with plain Poisson leaves the point estimate essentially unbiased but makes the model-based SE far too small, so confidence intervals badly undercover and p-values are too optimistic.

Setup: two groups of 200, true mean counts 5 and 10 (true log rate ratio = log 2 ≈ 0.693). Data are negative-binomial with dispersion θ = 1.5 (variance = μ + μ²/1.5, i.e. heavily overdispersed), but analyzed with the Poisson model-based SE. 20,000 replications.

```python
mu0, mu1, n_per, theta, reps = 5.0, 10.0, 200, 1.5, 20000
b1_true = np.log(mu1/mu0)
est = np.empty(reps); se_pois = np.empty(reps)
for r in range(reps):
    y0 = rng.negative_binomial(theta, theta/(theta+mu0), n_per)
    y1 = rng.negative_binomial(theta, theta/(theta+mu1), n_per)
    est[r]     = np.log(y1.mean()) - np.log(y0.mean())
    se_pois[r] = np.sqrt(1/y1.sum() + 1/y0.sum())   # Poisson model-based SE
```

| quantity | value |
|---|---|
| true log rate ratio | 0.693 |
| mean Poisson estimate | **0.694** (essentially unbiased) |
| true sampling SD of the estimate | **0.091** |
| mean Poisson model-based SE | **0.039** (≈ 2.3× too small) |
| coverage of nominal 95% Poisson CI | **0.595** |

What to read off this:
- The coefficient is fine — Poisson is consistent for the mean model even under overdispersion.
- The reported SE is less than half the true sampling variability, so a "95%" CI covers the truth only ~60% of the time and p-values are wildly optimistic. This is the concrete cost of ignoring overdispersion, and exactly why the fix is about the variance (NB, quasi-Poisson, or robust SEs), not the coefficient.
- The √θ-ish inflation factor is not cosmetic: a result reported at p = 0.001 from plain Poisson could be nowhere near significant once dispersion is handled.

## How to use these in an answer

Don't dump a simulation into every reply. Reach for one of these when (a) a questioner doubts that the CLT "really" rescues a test and a number settles it, (b) someone is about to report plain-Poisson SEs on obviously overdispersed data, or (c) you want to show *how large* n must be for their specific skew rather than asserting "large enough." When it helps, adapt the code to their actual n, skew, or dispersion and report the number — that is the senior-statistician move: quantify the consequence instead of invoking a rule.
