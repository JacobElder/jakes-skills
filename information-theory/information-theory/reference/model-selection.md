# Information-Criterion Model Selection

Contents: [The unifying idea](#the-unifying-idea-everything-estimates-out-of-sample-deviance) · [AIC](#aic) · [AICc](#aicc) · [BIC](#bic) · [The AIC-vs-BIC question](#the-aic-vs-bic-question-answer-it-correctly) · [Cross-validation](#cross-validation-the-reference-standard) · [Bayesian: WAIC and PSIS-LOO](#bayesian-models-waic-and-psis-loo) · [DIC](#dic-and-why-to-avoid-it) · [Recipes & pitfalls](#recipes-and-pitfalls)

## The unifying idea: everything estimates out-of-sample deviance

Every criterion here is trying to estimate the same thing — **expected predictive accuracy on
new data from the same process**, measured as expected log loss = cross-entropy = (up to a
constant that doesn't depend on the model) the **KL divergence from the truth to your fitted
model**. In-sample log-likelihood is an optimistically biased estimate of this (you fit to the
noise), so each criterion is `−2·(in-sample log-lik)` plus a *penalty that corrects the
optimism*. They differ in how they derive the penalty and, crucially, in **what target they're
optimizing** (see the AIC-vs-BIC section). `−2 log L` is "deviance"; lower is better throughout.

## AIC

```
AIC = 2k − 2 log L̂        (k = number of free parameters, L̂ = maximized likelihood)
```

Akaike's derivation: `2k` is (asymptotically) the expected optimism — the bias between
in-sample and out-of-sample deviance — so **AIC is an approximately unbiased estimate of
out-of-sample deviance / expected KL.** It targets *predictive accuracy*. It is **efficient**
(asymptotically selects the model minimizing prediction error) but **not consistent** (as
`N→∞` it keeps a nonzero chance of choosing an over-large model — it isn't trying to find a
"true" model, it's trying to predict well). Differences are what matter: `ΔAIC`; convert to
**Akaike weights** `w_i ∝ exp(−½ΔAIC_i)` for relative support / model averaging. Rough reading:
`ΔAIC < 2` ≈ comparable, `> 10` ≈ decisively worse.

## AICc

`AICc = AIC + 2k(k+1)/(N−k−1)`. The small-sample correction; the extra term blows up as `k`
approaches `N`. **Use AICc by default whenever `N/k` is small (≲ 40).** It converges to AIC for
large `N`, so there's little downside to always using it for Gaussian models. Forgetting AICc
on small data is a common way to over-select complexity.

## BIC

```
BIC = k ln N − 2 log L̂
```

Schwarz's derivation is **Bayesian**: `−½ BIC` is a Laplace approximation to the log **marginal
likelihood** `log p(data | model)`, so comparing BICs approximates comparing models by
posterior probability (with equal priors). Its penalty `k ln N` grows with `N`, so BIC punishes
complexity harder than AIC for any `N>7`. BIC is **consistent**: *if the true model is in the
candidate set*, BIC selects it with probability → 1. That "if" is the whole story — it's an
assumption you rarely get to make. Differences map to Bayes factors: `ΔBIC` of 2–6 is positive
evidence, 6–10 strong, >10 very strong (Kass–Raftery).

## The AIC-vs-BIC question (answer it correctly)

The framing "which is better?" is a **category error**, and saying so is part of the skill's job.
They estimate **different quantities** and are each optimal for *their own* target:

| | **AIC** | **BIC** |
|---|---|---|
| Estimates | out-of-sample predictive deviance (KL) | marginal likelihood / posterior model prob |
| Optimal property | **efficient** (best prediction) | **consistent** (finds true model if present) |
| Assumes a "true model" in the set? | No | Yes |
| Penalty | `2k` | `k ln N` (harsher for `N>7`) |
| Picks, as `N→∞` | possibly slightly over-complex, but best-predicting | the true model (under its assumption) |

Choose by the **question**, not by habit:
- "Which model will **predict** best on new data?" → AIC/AICc (or just do CV).
- "Which variables are **really** in the data-generating model / which is the parsimonious
  truth?" → BIC, while owning the true-model-exists assumption.
- **Do not average AIC and BIC**, and don't report whichever agrees with your prior. If they
  disagree, that disagreement *is* information: it usually means "the best-predicting model is
  richer than the most-defensibly-true one," which is a substantive thing to tell the user.

Both also assume the **same data and same likelihood** across compared models (you cannot
compare an AIC on raw `y` to one on `log y` — the Jacobian of the transform changes the
likelihood; adjust or refit on a common scale). And neither is valid when models are fit to
different subsets after listwise deletion of missing data.

## Cross-validation (the reference standard)

When you can afford it, **out-of-sample prediction error via CV is the most direct and
assumption-light answer** — it estimates the same expected log loss without leaning on
asymptotics. The key theoretical tie-in: **AIC is asymptotically equivalent to leave-one-out
cross-validation** (Stone), and BIC is asymptotically equivalent to a specific form of
*K*-fold-with-`K` growing / Bayes. So AIC isn't an alternative to CV — it's a cheap analytic
approximation to LOO. If AIC and CV disagree materially, trust CV and suspect the asymptotic
assumptions. For dependent data (time series, grouped, spatial) ordinary CV leaks; use
blocked / `h`-step-ahead / leave-one-group-out CV, and note that vanilla AIC/BIC also assume
independence.

## Bayesian models: WAIC and PSIS-LOO

For Bayesian models, use criteria built from the **posterior predictive**, not point estimates:
- **WAIC** (Watanabe) `= −2(lppd − p_waic)`, where `lppd = Σ_i log E_post[p(y_i|θ)]` (log
  pointwise predictive density) and `p_waic = Σ_i Var_post[log p(y_i|θ)]` is the effective
  number of parameters *estimated from the posterior* (handles hierarchical/regularized models
  where "counting parameters" is ill-defined). Computed from the pointwise log-likelihood matrix;
  `scripts/info_criteria.py` implements it.
- **PSIS-LOO** (Vehtari–Gelman–Gabry) — importance-sampling LOO with Pareto-smoothed weights;
  generally **preferred over WAIC** because it comes with a **diagnostic** (the Pareto `k̂`): when
  `k̂ > 0.7` for some points, the estimate is unreliable *and tells you so*. Use `arviz.loo` /
  `arviz.compare`. This self-diagnosis is why PSIS-LOO is the modern default in the Bayesian
  workflow.

## DIC (and why to avoid it)

DIC was the older Bayesian default but is **not recommended** for new work: it uses a point
estimate (posterior mean) so it's not invariant to reparameterization, its effective-parameter
count `p_D` can go negative, and it behaves badly for non-normal / singular models. If you see
DIC in legacy code, suggest WAIC or PSIS-LOO instead.

## Recipes and pitfalls

- **Report a table, not a winner.** Show `ΔAIC`/`ΔBIC` (or `ΔLOO ± SE`) across the candidate
  set and the weights, so the user sees how decisive the choice is. A model "winning" by
  `ΔAIC = 0.4` is a tie; present it as one.
- **Compute everything from one fitting routine.** Don't mix a hand-typed `k` with a library's
  log-lik; off-by-one on parameter count (forgetting the variance parameter in a Gaussian
  model!) is a frequent, silent error. Let the script count `k` and pull `log L̂`. (`info_criteria.py`)
- **These criteria are for comparing models on the *same data*.** They are not goodness-of-fit
  tests and a low AIC doesn't mean the model is *good*, only *less bad than the alternatives*.
  Pair selection with an absolute check (posterior predictive checks, residuals, calibration).
- **Don't select on AIC then report p-values as if the model were pre-specified.** Post-selection
  inference is biased; if you searched over models, say so and use selective-inference or
  held-out data for the final claims.
- **When prediction is the actual goal, prefer CV/LOO and consider averaging** (Akaike weights or
  Bayesian model averaging) over hard selection — committing to one model discards real
  uncertainty about which is right.
