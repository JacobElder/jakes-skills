# Robust and Alternative Inference

These methods relax a classical assumption — but each solves a *specific* problem and leaves others untouched. The discipline is naming which problem you have and what assumption still remains after you apply the fix.

## Contents
- The sandwich estimator and HC standard errors
- Clustered standard errors
- The bootstrap
- Permutation / randomization tests
- Rank-based tests
- Quantile regression
- M-estimation and robust regression
- Bayesian alternatives
- What each fixes — and what it doesn't

## The sandwich estimator and HC standard errors

OLS coefficients are **unbiased under heteroskedasticity** — non-constant error variance costs you efficiency, not consistency. What breaks is the classical variance formula σ²(X'X)⁻¹, which assumes homoskedasticity. The **sandwich (Huber–White) estimator** replaces it with (X'X)⁻¹ X'ΩX (X'X)⁻¹, estimating Ω from the squared residuals, giving **heteroskedasticity-consistent (HC) standard errors**. Practical notes:
- HC0 is the original; it is biased downward in small samples. HC1 applies a simple df correction; HC2 and HC3 correct using the leverage (hat) values. **Use HC3 by default for small/moderate n** — it is the most reliable, slightly conservative.
- These fix only the SEs; the point estimates are the same OLS numbers.
- The crucial residual assumption: robust SEs assume the **mean model (the conditional expectation) is correctly specified**. They protect against the wrong *variance* structure, not the wrong *functional form*. A misspecified mean with robust SEs is still misspecified.
- As with Welch, prefer using robust SEs by default over a Breusch–Pagan pretest-then-switch.

## Clustered standard errors

When observations are correlated within groups (students in schools, repeated measures on subjects, firms over time, individuals in villages), the effective sample size is smaller than n and naive SEs are too small. **Cluster-robust SEs** generalize the sandwich to allow arbitrary within-cluster correlation, clustering at the level at which treatment is assigned or sampling occurs (cluster broadly enough; clustering too finely understates correlation).
- They rely on having **enough clusters**. The asymptotics are in the number of clusters, not observations; with few clusters (rule of thumb < ~40) cluster-robust SEs are biased downward and over-reject.
- **Few-cluster fix:** the **wild cluster bootstrap** (Cameron–Gelbach–Miller) gives far better inference, or use cluster-count corrections / degrees-of-freedom adjustments.
- This is a case where no sample size of *observations* rescues you — it is the number of independent *clusters* that governs the inference.

## The bootstrap

Resample the data (with replacement) to approximate the sampling distribution of an estimator empirically, instead of relying on an analytic asymptotic formula. Strengths: works for complicated statistics with no clean variance formula (ratios, indirect effects, nonparametric curves), and can be more accurate than first-order asymptotics in moderate samples (especially bias-corrected/accelerated, BCa). Caveats — the bootstrap is not assumption-free:
- The basic nonparametric bootstrap assumes **iid** observations. Under dependence you must resample the dependent unit — **block bootstrap** for time series, **cluster bootstrap** for clustered data.
- It can fail for **non-smooth functionals** (the maximum, parameters on a boundary, the number of distinct values) and for **heavy-tailed** distributions where the variance is infinite.
- For hypothesis testing, bootstrap *under the null* (impose the null when resampling) rather than just inverting a CI, when the two differ.

The bootstrap approximates the sampling distribution; it does not manufacture information the data don't contain, and it inherits any bias in the estimator being bootstrapped.

## Permutation / randomization tests

Permute the treatment labels to build the exact null distribution of the test statistic under the **sharp null of no effect for any unit**. In a randomized experiment this is the inference that most directly mirrors the design: the randomization itself justifies the test, with no distributional assumption. Strengths: exact level in finite samples, no normality needed, applies to arbitrary test statistics. Things to keep straight:
- The null tested is **sharp** (no effect for *anyone*), which is stronger than the t-test's null of equal means. Under heterogeneity the two nulls differ, and a permutation test can be sensitive to variance differences when used for a difference in means.
- Outside a randomized/exchangeable design, the exchangeability that justifies permutation has to be argued for, not assumed.

## Rank-based tests

Wilcoxon signed-rank (paired), Wilcoxon–Mann–Whitney (two-sample), Kruskal–Wallis (k groups). They replace values with ranks, gaining robustness to outliers and not requiring normality. The interpretive subtlety (see `references/robustness.md`): Mann–Whitney tests **stochastic ordering** (P(X>Y)=½), not equality of medians, unless a pure location-shift model holds. They are excellent when the estimand is "does one group tend to exceed the other?" and risky when silently treated as a test about means or medians. They also lose power relative to parametric methods when the parametric model is approximately right, and "distribution-free under the null" does not make the *estimand* assumption-free.

## Quantile regression

Models a conditional **quantile** (e.g. the median, the 10th or 90th percentile) of Y given X, rather than the conditional mean. Reasons to use it:
- The estimand is a quantile (median spend, the 90th-percentile latency for an SLA). This is a substantive choice, often more decision-relevant than the mean for skewed outcomes.
- Robustness: median regression is far less sensitive to outliers in Y than mean regression.
- **Heterogeneous effects across the distribution:** a covariate can shift the upper tail without moving the median; quantile regression reveals this where OLS averages it away. No distributional assumption on the errors is needed; inference is typically via the bootstrap or kernel methods.

## M-estimation and robust regression

**M-estimators** generalize maximum likelihood by minimizing a chosen loss ρ; the sandwich variance applies generally to them. **Robust regression** uses a loss that grows sub-quadratically for large residuals — **Huber** (quadratic near zero, linear in the tails) or **Tukey biweight** (redescending: extreme points get zero weight) — so a handful of contaminated observations cannot dominate the fit. The tradeoff: a small efficiency loss under exact normality (Huber's ~95% efficiency is the usual benchmark) in exchange for large robustness to contamination. Use when you suspect a minority of corrupted/extreme observations but still want to estimate the conditional mean trend, rather than deleting points by hand. (Note this is about robustness to *outliers in the response*; high-leverage points in X may need bounded-influence or MM-estimators.)

## Bayesian alternatives

A Bayesian model places a prior on parameters and reports the full posterior, which changes what is on offer rather than escaping assumptions:
- **Makes assumptions explicit** as the likelihood + prior, instead of hiding them in a procedure.
- **Hierarchical / partial pooling** handles clustering and small-group estimation gracefully (shrinkage toward group means), often outperforming both no-pooling and complete-pooling under few clusters.
- **Robust likelihoods**: a Student-t likelihood downweights outliers automatically (a model-based analogue of robust regression); explicit mixture/heavy-tail components handle contamination.
- **Regularizing priors** resolve separation in logistic regression and stabilize near-singular designs.
- It does **not** dodge the model: a misspecified likelihood is still misspecified, and an informative prior can dominate weak data. Posterior predictive checks are the Bayesian diagnostic for whether the model can reproduce features of the observed data.

## What each fixes — and what it doesn't

| Method | Problem it solves | Assumption that remains |
|---|---|---|
| HC (sandwich) SEs | heteroskedasticity | correct mean model; large-n |
| Clustered SEs | within-cluster correlation | enough clusters; correct cluster level |
| Wild cluster bootstrap | few clusters | correct cluster level |
| Bootstrap | no clean variance formula; weak asymptotics | iid (or right resampling unit); smooth functional; finite variance |
| Permutation test | exact test, no normality | exchangeability (sharp null) |
| Rank tests | outliers, non-normality | location-shift if interpreting as medians; power loss |
| Quantile regression | quantile estimand, outliers, heterogeneity | the quantile is the right target |
| Robust regression / M-est. | outliers in Y | mean trend is the estimand; X-leverage may need more |
| Bayesian | explicit uncertainty, pooling, regularization | likelihood + prior are reasonable |

The meta-point: there is no assumption-free inference. Each tool trades one assumption for a weaker or more defensible one. Choose the tool whose *remaining* assumption you are most willing to defend for the problem at hand.
