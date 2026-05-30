# Robustness of Classical Tests

The recurring question — "is a t-test okay despite non-normality?" — is almost always asked at the wrong level. This file gives the intuition for answering it correctly.

## Contents
- The object that has to be normal
- CLT and Berry-Esseen: the rate is what matters
- Skewness vs heavy tails
- Means vs medians: an estimand question in disguise
- Unequal variances and why Welch is the default
- Outliers and influence
- When classical methods genuinely fail
- CLT-justified mean inference vs a calibrated model (the t-test/OLS vs GLM question)

## The object that has to be normal

A t-test does not assume the raw data are normal. It assumes the **sampling distribution of the sample mean** (more precisely, the t-statistic) is approximately normal/t under the null. The data's marginal distribution is relevant only insofar as it controls how fast that sampling distribution converges to normal. So the histogram of the raw data is the wrong thing to stare at; the relevant object is the distribution of the *estimate*, which is far more Gaussian than the data because averaging is a smoothing operation.

This is why "the data are skewed, so the t-test is invalid" is a category error. Skewed data can still produce an essentially normal sampling distribution for the mean at modest n.

## CLT and Berry-Esseen: the rate is what matters

The Central Limit Theorem says that for iid data with finite variance, the standardized sample mean converges to a standard normal as n → ∞. For applied work the asymptotic statement is useless on its own; what matters is *how close* the approximation is at your finite n. The Berry–Esseen theorem makes this concrete: the maximum error of the normal approximation to the CDF of the standardized mean is bounded by roughly

    C · γ / √n

where γ is the population skewness (standardized third moment) and C is a small constant. Two consequences:

1. **Convergence is governed primarily by skewness, not by "non-normality" in general.** A symmetric but heavy-tailed distribution (finite variance) converges quickly in terms of level; a skewed one converges slowly.
2. **The error shrinks like 1/√n.** Doubling the sample does not halve the approximation error. This is why heavily skewed data can need n in the hundreds before the t-test's nominal level is trustworthy, while mildly skewed data are fine in the dozens.

Rules of thumb that fall out of this (use as intuition, not law): for roughly symmetric data, n ≈ 15–30 per group is usually plenty; for moderate skew, dozens to ~100; for severe skew (e.g. lognormal with high variance, or near-zero-inflated), several hundred or reconsider the estimand.

## Skewness vs heavy tails

These break different things and call for different responses:

- **Skewness** primarily threatens the **level** (Type I error rate) of the test, because it makes the sampling distribution of the mean asymmetric at finite n. This is the CLT-rate issue above.
- **Heavy tails (with finite variance)** primarily threaten **efficiency/power**, not level. The sample mean is an inefficient estimator under heavy tails — a few extreme observations dominate it — so the t-test loses power relative to robust or rank-based alternatives, even though its level is approximately right.
- **Infinite variance** (e.g. Cauchy, or a power-law with tail index < 2) breaks the CLT entirely. The sample mean does not concentrate, the t-statistic has no limiting normal distribution, and the mean may not even be a sensible estimand. Here you must change the target (median, trimmed mean) or the model.

So "heavy-tailed" is not automatically a problem for validity; it is a problem for power and a signal that the mean may be an inefficient or unstable summary.

## Means vs medians: an estimand question in disguise

When someone says "the data are too skewed for a t-test, use a rank test," they are usually conflating two separate decisions:

1. *Do I still want to estimate the mean?* For skewed but finite-variance data, the mean is well-defined and the t-test estimates the difference in means with approximately correct level at adequate n.
2. *Is the mean the quantity I care about?* For something like income or healthcare cost, the **median** or another quantile may be the more meaningful target. That is a substantive choice about the estimand, not a consequence of an assumption failing.

Critically, the Wilcoxon–Mann–Whitney test does **not** test "equality of medians" in general. It tests stochastic ordering — essentially P(X > Y) = ½. It coincides with a statement about medians only under a pure location-shift model (identical shapes, shifted). If the two groups have different shapes/spreads, Mann–Whitney can reject even when medians are equal, and a "significant" result does not translate into "the median differs by X." If the median difference is the estimand, target it directly (e.g. median/quantile regression, or a Hodges–Lehmann estimate with its location-shift caveat).

## Unequal variances and why Welch is the default

Student's t-test assumes equal variances (homoscedasticity) to pool the variance estimate. When variances differ — especially combined with unequal group sizes — the pooled test's level is distorted, sometimes badly (the direction depends on whether the larger group has the larger or smaller variance).

**Welch's t-test** drops the equal-variance assumption, using a Satterthwaite approximation for the degrees of freedom. Its key practical property: it is barely less powerful than Student's when variances *are* equal, and substantially more reliable when they aren't. Therefore the sound default is to **use Welch unconditionally** and skip the variance pretest. The common "run Levene's test, then choose Student or Welch" workflow is a pretest procedure that distorts the level of the final test and buys nothing — you would have been better off using Welch from the start. This is a concrete instance of the general "robust by design beats test-then-choose" principle.

## Outliers and influence

Outliers matter through their **influence** on the estimate, which is leverage × discrepancy, not through their mere existence. A single extreme point can dominate a mean (and hence a t-test) far more than it dominates a median or a rank statistic. The right question is never "is there an outlier?" but "does any single observation change my conclusion?" — check by refitting without it (or via Cook's distance / DFBETAs in regression). If conclusions hinge on one or two points, that is a fragility to report, not necessarily an error to delete away; deletion needs a substantive justification, not a statistical one.

## When classical methods genuinely fail

Be willing to say a classical test is the wrong tool when:
- **Dependence.** Observations are clustered, repeated, autocorrelated, or otherwise non-independent. No sample size fixes this; the SEs are wrong in a way the CLT does not address. Use clustered/robust SEs, mixed models, or design-based inference.
- **Infinite or near-infinite variance.** The CLT premise fails; reconsider the estimand.
- **Tiny n with strong skew.** The CLT has not engaged; exact, permutation, or Bayesian methods (or honest acknowledgment of wide uncertainty) are warranted.
- **The mean is not the estimand.** If the decision depends on a quantile, a rate, a probability, or a bounded/structured outcome, a test about means is answering the wrong question regardless of how well-behaved it is.

In all other common cases — moderate skew, moderate heavy tails, adequate n, independent observations — the classical test is typically *approximately valid*, and the honest answer to "is it okay?" is usually "yes, here's why," not a reflexive switch to a nonparametric alternative.

## CLT-justified mean inference vs a calibrated model (the t-test/OLS vs GLM question)

A recurring and genuinely subtle question: if the CLT makes the t-test (or OLS with robust SEs) valid at large n even for counts, proportions, or skewed positives, why ever bother with a GLM "calibrated" to that data type? The confusion dissolves once you see that the two arguments answer to **different goals**. The CLT argument is about *validity of inference on a mean contrast*; the GLM argument is about *efficiency, estimand, and prediction*. They are not competing answers to the same question.

**What the CLT genuinely buys you.** For the estimand "difference (or linear combination) of means," the sampling distribution of the estimator is asymptotically normal whenever the variance is finite, regardless of the outcome's marginal shape. So a t-test, or OLS with heteroskedasticity-robust SEs, is a *consistent and asymptotically valid* estimator of a mean contrast even when the outcome is a count, a 0/1 indicator, or a right-skewed cost. You do **not** need a Poisson/gamma/logistic model for the *validity* of inference about the mean difference. This is the basis for the defensible (Lumley-style) position that on large datasets one can often just use linear models with robust SEs and keep an interpretable, collapsible estimand.

**What the calibrated GLM adds — and it is not validity:**
1. **Efficiency.** A correctly specified GLM uses the mean–variance relationship to weight observations, yielding smaller standard errors than OLS on the raw scale. At small-to-moderate n this can matter a lot; at very large n you often have precision to spare, which weakens the efficiency argument.
2. **A different, frequently more natural estimand.** A log-link GLM reports multiplicative effects (rate ratios, odds ratios, % changes); OLS reports additive effects on the raw scale. Neither is "more correct" — they target different contrasts. If the science is multiplicative, the GLM's estimand is the one you actually want, and that, not validity, is the reason to use it.
3. **In-bounds, sensible predictions.** OLS can predict negative counts or probabilities outside [0,1]. If the goal is *prediction* rather than a single average contrast, the link function keeps fitted values in the valid range. This is a prediction-goal concern, not a mean-inference concern.
4. **Better behavior near a boundary.** The CLT-for-the-mean argument is weakest exactly where the mean sits near a boundary — rare events (probabilities near 0/1), counts near zero — because the sampling distribution of the mean is most skewed there and needs larger n. The GLM's variance function is built for this regime.

**When large n does NOT rescue the simple test, even for the mean:**
- The estimand is wrong. If you actually care about a median, a quantile, a rate ratio, or a probability, no n makes a difference-in-means answer the right question. Large n gives you a precise answer to the wrong question.
- Near-infinite variance: the CLT premise fails and the mean may not be estimable.
- Severe skew at the boundary: as Example 1 in `references/worked-examples.md` shows, lognormal-level skew can need n in the hundreds-to-thousands before the nominal level holds; "large" must be judged against the skew, not assumed.

**Practical adjudication.** Ask, in order: (1) Which estimand do I want — additive mean contrast, or a multiplicative/probability-scale effect? That alone often decides it. (2) Is the goal inference on a contrast (CLT + robust SEs is enough and keeps things interpretable) or prediction / in-bounds fitted values (favor the GLM)? (3) Is n large relative to the skew and is the mean away from a boundary (the simple approach is safe) or not (lean on the calibrated model)? (4) Do I need the efficiency (smaller n, or the variance structure is strong)? The frequent answer for a *single average contrast on a large sample* is "OLS with robust SEs is valid, interpretable, and fine"; the frequent answer when you want a *rate/odds ratio, good predictions, or efficiency at modest n* is "use the calibrated GLM." See `references/glm-families.md` for matching the family to the generative structure once you've decided a GLM is the right tool.
