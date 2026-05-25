# Model Comparison

Read this when the user is comparing two or more cognitive models on the same data — picking among RL variants, deciding between PT and EU, choosing between hyperbolic and exponential discounting, etc. Or when they ask "which fits better?", "is my model significantly better?", or how to interpret AIC/BIC/WAIC/LOO numbers.

Canonical references: Vehtari, Gelman & Gabry (2017) for PSIS-LOO and WAIC — the modern standard for Bayesian model comparison; Gelman et al. (2014) for the conceptual unification; Burnham & Anderson (2002) for AIC/BIC; Wagenmakers & Farrell (2004) for AIC weights; Spiegelhalter et al. (2002) for DIC. For cognitive modeling specifically: Daw (2011), Lewandowsky & Farrell (2010), Lee & Wagenmakers (2014).

## The big distinction: prediction vs. evidence

There are two philosophically different goals you might want from model comparison:

**Predictive accuracy.** Which model would best predict new data drawn from the same data-generating process? AIC, DIC, WAIC, LOO-CV, k-fold CV are all answering this. They estimate *expected log predictive density* (elpd) on unseen data and penalize complexity to avoid in-sample over-fitting.

**Marginal evidence / Bayes factors.** Which model has higher posterior probability given the data and a prior over models? Bayes factors, BIC (as an asymptotic approximation), bridge sampling. These answer "given equal prior credence in the models, how should the data shift my belief?"

These can give different answers. Bayes factors are sensitive to the prior on parameters; predictive criteria are not. WAIC/LOO favor flexible models that predict well; BIC tends to favor parsimony. For cognitive modeling, the field has converged on PSIS-LOO and WAIC for Bayesian fits and AIC for MLE fits. Use Bayes factors only when the prior is genuinely meaningful and well-specified.

## The criteria, in plain English

**AIC** (Akaike Information Criterion): `AIC = -2 · log L̂ + 2k`. Penalty `2k` for k free parameters. Easy to compute from any MLE fit. Estimates relative out-of-sample predictive accuracy under standard regularity assumptions. Lower is better.

**AICc** (small-sample correction): `AICc = AIC + 2k(k+1)/(n-k-1)`. Use when `n/k < ~40`. Always at least as appropriate as AIC.

**BIC** (Bayesian/Schwarz Information Criterion): `BIC = -2 · log L̂ + k · log(n)`. Heavier penalty than AIC at typical n. Asymptotically selects the "true" model if one exists in the candidate set; AIC selects the best predictor (a different thing). Often disagrees with AIC; both are defensible but answer different questions. Lower is better.

**DIC** (Deviance Information Criterion): a Bayesian generalization of AIC using posterior mean parameters and a complexity penalty derived from the posterior. Was the standard for hierarchical Bayesian fits in BUGS/JAGS-era work. Now considered superseded by WAIC and LOO — DIC can be unstable for non-Gaussian posteriors and is no longer recommended for new work. If you see it in older papers, fine; don't introduce it in new ones.

**WAIC** (Widely Applicable Information Criterion, Watanabe 2010): a fully Bayesian elpd estimator that uses the full posterior. Works for singular models (those without unique MLEs) where AIC fails. Computed from posterior draws as: `WAIC = -2 · (lppd - p_WAIC)` where lppd is the log pointwise predictive density and p_WAIC is the effective parameter count from posterior variance. Lower is better when scaled the usual way; some packages report it on the elpd scale where higher is better.

**PSIS-LOO** (Pareto-smoothed importance-sampling leave-one-out cross-validation, Vehtari et al. 2017): the gold standard for Bayesian model comparison. Approximates leave-one-out cross-validation from a single MCMC fit using importance sampling, with Pareto smoothing for numerical stability. Implemented in `loo` (R) and `arviz` (Python). The diagnostics (Pareto k values) tell you whether the approximation is trustworthy — if k > 0.7 for some observations, those observations need exact LOO refit, and if many observations have k > 0.7 the approximation is shaky.

**Bayes factors** (BF): ratio of marginal likelihoods. Compute via bridge sampling (`bridgesampling` R package), thermodynamic integration, or stepping-stone sampling. Hard to do well for high-dim hierarchical models because the marginal likelihood depends on the prior in non-obvious ways. Use only when priors are well-justified.

**Cross-validation** (k-fold, leave-one-block-out): always defensible but expensive. For cognitive models with structured data (subjects × trials), the right unit of cross-validation is usually leave-one-subject-out or leave-one-block-out, not random folds. Random folds across trials within a subject can leak information through learned values.

## The practical recommendation

For modern hierarchical Bayesian cognitive modeling:

- **First choice: PSIS-LOO via the `loo` package.** Report ELPD differences with their standard errors. Use `loo_compare()` in R; `az.compare()` in Python ArviZ. Check the Pareto k diagnostics.
- **Second choice: WAIC.** Faster than LOO; usually agrees. Good cross-check.
- **For point-estimate MLE: AIC or BIC.** AIC if you care about prediction; BIC if you care about identifying the data-generating model. Report both if results matter; if they disagree, think about why.
- **For cross-task/cross-design generalization: cross-validation explicitly.** Hold out subjects, blocks, or conditions, refit, evaluate on held-out portion. The relevant unit depends on the scientific claim.

## Interpreting the differences

A criterion difference (ΔELPD or ΔAIC) is meaningful only relative to its uncertainty.

For PSIS-LOO, `loo_compare` reports `elpd_diff` and `se_diff`. Rough rules of thumb that get cited (e.g., Sivula et al. 2022):
- `|elpd_diff|` < 4 SE: the comparison is uninformative; either model could be preferred on a different sample.
- `|elpd_diff|` > 4 SE: the difference is reliable in a statistical sense.

Even a reliable elpd difference doesn't mean the worse model is wrong — it just means the better one predicts new data more accurately. Always do PPC before declaring a model "right."

For AIC/BIC, the older "rules of thumb":
- ΔAIC < 2: models essentially equivalent
- 4 < ΔAIC < 7: considerable support for the better model
- ΔAIC > 10: essentially no support for the worse model

These are softer than they look — they don't account for sampling variance. Reported AIC weights `wᵢ = exp(-Δᵢ/2) / Σ exp(-Δⱼ/2)` give a relative-evidence interpretation but inherit the same uncertainty issue.

For BIC, the equivalent (Kass & Raftery 1995) Bayes-factor-style language:
- ΔBIC 0–2: weak
- 2–6: positive
- 6–10: strong
- > 10: very strong

These should be reported with humility — BIC is an asymptotic approximation to the log Bayes factor under specific assumptions that rarely hold exactly.

## Common pitfalls

- **In-sample log-likelihood is not model fit.** A 7-parameter model will always fit the training data at least as well as its 3-parameter nested version. The complexity penalty is the whole point.
- **WAIC and LOO are pointwise.** They evaluate per-observation log-likelihood. You need to define what an "observation" is — usually one trial. For hierarchical models, this gives within-subject predictive accuracy. For *subject-level* generalization (e.g., predicting new subjects' behavior), you need leave-one-*subject*-out, which requires more careful implementation.
- **Stan models need a `log_lik` block** with per-trial log-likelihoods stored as `generated quantities` for LOO/WAIC to work. Forgetting this means you can't compute it.
- **Bayes factors are extremely sensitive to priors.** A weakly informative prior that's fine for parameter estimation can give wildly different Bayes factors than a tighter prior. If you use BFs, justify the prior carefully and ideally report sensitivity.
- **Comparing across non-identical data.** Models fit on slightly different data (e.g., one excludes outliers, one doesn't) cannot be compared via these criteria. The data must be identical.
- **Reporting only the winning model number.** Always include the candidates and the ΔELPD or ΔAIC table with SEs, not just "model X won."
- **Confusing model selection with model averaging.** If multiple models have similar fit, you might want to *average* predictions across them (BMA, stacking) rather than pick one. Especially relevant when downstream use (fMRI regressors, group-level inferences) depends on parameter estimates.
- **AIC weights and stacking weights are different.** AIC weights are model probabilities under a frequentist information-theoretic view; stacking weights (Yao et al. 2018) optimize predictive performance directly and often produce more sensible model averages.
- **Comparing models with very different likelihoods.** Be careful comparing a DDM (joint over RT and choice) with a softmax choice model (just choice). The likelihood scales are different; the comparison can be meaningless without subsetting.

## Code patterns

### PSIS-LOO in R

```r
library(loo)

# Stan fit with log_lik in generated quantities
log_lik_1 <- extract_log_lik(fit1, merge_chains = FALSE)
loo_1 <- loo(log_lik_1, r_eff = relative_eff(exp(log_lik_1)))
print(loo_1)  # check Pareto k diagnostics; ideally all k < 0.7

log_lik_2 <- extract_log_lik(fit2, merge_chains = FALSE)
loo_2 <- loo(log_lik_2, r_eff = relative_eff(exp(log_lik_2)))

# Compare
loo_compare(loo_1, loo_2)
# Output: elpd_diff and se_diff for each pair
```

### PSIS-LOO in Python with ArviZ

```python
import arviz as az

idata1 = az.from_cmdstanpy(posterior=fit1, log_likelihood='log_lik')
loo1 = az.loo(idata1)
print(loo1)  # check pareto_k diagnostics

idata2 = az.from_cmdstanpy(posterior=fit2, log_likelihood='log_lik')
loo2 = az.loo(idata2)

comparison = az.compare({'model1': idata1, 'model2': idata2}, ic='loo')
print(comparison)
```

### AIC/BIC from a scipy MLE fit

```python
import numpy as np

# After fitting
nll = result.fun           # negative log likelihood at MLE
k = len(result.x)          # number of parameters
n = n_trials_total
aic = 2 * nll + 2 * k
bic = 2 * nll + k * np.log(n)
aicc = aic + 2 * k * (k + 1) / (n - k - 1)
```

## How model comparison interacts with model recovery

A model can win the comparison even when *it can't be recovered* from its own simulated data. This is a serious issue: the comparison tells you which model fits *these* data better, but the design might lack the structure to distinguish them on principled grounds.

The right workflow is: (1) confirm model recovery; (2) confirm parameter recovery for the focal model; (3) *then* do model comparison on real data. Without (1) and (2), the comparison result is conditional on a design assumption you haven't validated.

## When the user shows you a model comparison result

Engage with the actual numbers:

- What's the ELPD/AIC/BIC difference?
- What's its uncertainty?
- Are Pareto k diagnostics okay (for LOO)?
- Is the comparison consistent with PPC qualitative findings?
- What does model recovery say about whether this design can distinguish these models?
- Is the "winner" the model the user expected? If so, are they still doing PPC? If not, what changed?

A bare "ΔWAIC = 12, model A wins" doesn't tell us much. The follow-ups above are where the actual scientific judgment happens.

## What to report

For Bayesian fits:

- ELPD (LOO or WAIC) for each candidate.
- Pairwise differences with standard errors.
- Pareto k diagnostics (for LOO).
- A statement of which model "wins" and how reliable the win is.
- PPC results for the winning model.
- Recovery results (parameter and model) on simulated data of the same size.

For MLE fits:

- AIC and/or BIC for each candidate.
- ΔAIC/ΔBIC table.
- AIC weights if appropriate.
- Same PPC and recovery caveats apply.

A bare "we used AIC and model X won" is not a model comparison — it's a citation of having done one.

---

**See also:**
- `references/recovery.md` — model recovery (confusion matrix) is as important as the comparison criterion; always run it.
- `references/hierarchical_stan.md` — `log_lik` generated quantities in Stan for LOO/WAIC; `loo` R package and `arviz` Python patterns.
- Model-family references for PPC guidance: `reinforcement_learning.md`, `drift_diffusion.md`, etc.
