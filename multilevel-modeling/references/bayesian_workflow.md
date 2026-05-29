# Bayesian MLM Workflow

This document covers Bayesian multilevel modeling end-to-end: priors, fitting, diagnostics, summarizing, comparing models, and the practical reasons to prefer Bayesian fits in many MLM contexts.

The main reference is Gelman & Hill (2007), supplemented by Gelman et al. (*Regression and Other Stories*, 2020) and McElreath (*Statistical Rethinking*, 2nd ed.). Workflow advice draws on Gelman, Vehtari, Simpson, et al. (2020) "Bayesian workflow."

## When to prefer Bayesian MLM

There are several situations where a Bayesian fit is meaningfully better, not just a different flavor:

1. **Few clusters at any level.** REML/ML variance components can collapse to zero with sparse data. Weakly informative priors regularize them sensibly. Gelman's advice: when you have fewer than ~5 groups, even a frequentist analyst should consider partial pooling with priors.

2. **Maximal random-effects structures that lme4 can't fit.** The number-one reason to switch to brms or bambi. Priors keep variance estimates off the boundary; LKJ priors on correlation matrices keep correlations away from ±1.

3. **You want uncertainty in variance components and ICC.** Frequentist CIs for variance components are awkward (Wald is bad; profile and bootstrap are slow and often unstable). Posterior intervals are straightforward.

4. **You want to make probabilistic statements about cluster-specific predictions.** Posterior predictive distributions for new clusters or new observations within clusters are clean to obtain.

5. **You have prior information.** Pilot data, previous studies, mechanistic constraints. Don't waste it.

6. **Complex non-standard models.** Measurement error in predictors, missing data jointly modeled, IRT-MLM hybrids, mixture models with random effects.

## Choosing priors

The Gelman/Stan-team recommendation for default priors in MLM:

| Parameter | Recommended prior | Notes |
|---|---|---|
| Fixed effects (after centering/scaling) | `Normal(0, 2.5)` to `Normal(0, 10)` | Weakly informative; lets data dominate. Wider if scale of outcome is large. |
| Intercept | `Normal(mean(y), 2*sd(y))` or similar | Centered on a reasonable value. |
| Random-effect SDs | `HalfNormal(0, sd(y))` or `HalfStudent_t(3, 0, sd(y))` | Half-Student-t is more robust to outlying variance components. Avoid uniform on (0, large); avoid inverse-gamma. |
| Random-effect correlation matrix | `LKJ(eta=2)` | eta=1 is uniform over correlation matrices; eta=2 puts mild mass near zero correlation (mild regularization). |
| Residual SD (Gaussian) | `HalfStudent_t(3, 0, sd(y))` | Similar logic to RE SDs. |

`brms` and `bambi` use these defaults reasonably well out of the box. **Always inspect the default priors before fitting** — print the model object in brms or bambi to see what priors were chosen, and ask whether they make sense for your data scale.

### A worked prior decision

Suppose `y` is reaction time in ms, mean ≈ 600, SD ≈ 150. After centering, effect sizes on the order of tens of ms are plausible.

- `Normal(0, 100)` on a treatment coefficient is weakly informative (effects of ±200 ms within prior 2σ; ±500 ms within 5σ — wide).
- `Normal(0, 10)` would be informative (effectively claims you'd be surprised by anything larger than 20–30 ms).
- `HalfNormal(0, 100)` on random-intercept SD is weakly informative.

The honest move is to write down what you expect a priori, what would be surprising, and check whether the prior reflects that. A prior predictive check (simulate `y` from the prior alone) catches most calibration errors.

```r
# brms prior predictive check
fit_prior <- brm(formula, data = d, prior = priors, sample_prior = "only")
pp_check(fit_prior)
```

If the prior-predictive distribution puts mass on physically impossible values (e.g., RTs of 50,000 ms), tighten the priors.

## Fitting with brms

```r
library(brms)

priors <- c(
  prior(normal(0, 100), class = "b"),
  prior(normal(600, 300), class = "Intercept"),
  prior(student_t(3, 0, 150), class = "sd"),
  prior(student_t(3, 0, 150), class = "sigma"),
  prior(lkj(2), class = "cor")
)

fit <- brm(
  rt ~ condition * distractor +
    (1 + condition * distractor | subject) +
    (1 + condition | item),
  data = d,
  prior = priors,
  chains = 4,
  cores = 4,
  iter = 4000,
  warmup = 2000,
  control = list(adapt_delta = 0.95, max_treedepth = 12),
  seed = 42
)
```

`adapt_delta` higher (up to 0.99) and `max_treedepth` higher (up to 15) when you see divergent transitions or maximum treedepth warnings. These cost time but improve sampling.

### Diagnostics in brms

```r
summary(fit)              # R-hat, ESS, posterior summaries
plot(fit)                 # trace + density
pp_check(fit)             # posterior predictive
pp_check(fit, type = "stat", stat = "mean")
loo(fit)                  # leave-one-out cross-validation
bayes_R2(fit)             # Bayesian R²
```

R-hat target: < 1.01 (strict) or < 1.05 (lenient). ESS (bulk and tail) should be at least a few hundred per chain.

### Fitting with bambi (Python)

Equivalent workflow in Python via bambi:

```python
import bambi as bmb
import arviz as az

priors = {
    "Intercept": bmb.Prior("Normal", mu=600, sigma=300),
    "condition": bmb.Prior("Normal", mu=0, sigma=100),
    "distractor": bmb.Prior("Normal", mu=0, sigma=100),
    "condition:distractor": bmb.Prior("Normal", mu=0, sigma=100),
    "1|subject": bmb.Prior("HalfStudentT", nu=3, sigma=150),
    "sigma": bmb.Prior("HalfStudentT", nu=3, sigma=150),
}

model = bmb.Model(
    "rt ~ condition * distractor + "
    "(1 + condition * distractor | subject) + (1 + condition | item)",
    data=d,
    priors=priors,
    family="gaussian",
)

idata = model.fit(
    draws=2000, tune=2000, chains=4,
    target_accept=0.95,
    random_seed=42,
)
```

`target_accept` in bambi/PyMC is the analogue of `adapt_delta` in brms.

## Convergence problems and what to do

### Divergent transitions

Sampler can't navigate the posterior geometry. First-line remedies:

1. **Increase `adapt_delta` / `target_accept`** to 0.95, 0.99.
2. **Reparameterize**. Most commonly, switch from centered to non-centered parameterization for random effects. brms and bambi handle this automatically in most cases.
3. **Tighten priors**. Diffuse priors create geometric problems for HMC.
4. **Scale predictors**. Same as frequentist — predictors on very different scales hurt the sampler.

### Maximum treedepth warnings

Sampler is hitting the tree-depth limit. Often correlated with divergences. Bump `max_treedepth` to 12, 13, 15 (each step doubles compute per iteration).

### Low ESS

The chains aren't mixing well. Run longer (more iterations after warmup), thin less (don't), or improve the parameterization. Low tail ESS especially matters if you care about credible intervals.

### Different chains finding different modes

Real multimodality is rare in well-specified MLMs but can happen with weak data and weak priors. Inspect with `mcmc_trace()` per parameter and `mcmc_pairs()` on suspicious pairs.

## Posterior summarization

For each fixed effect:

- Posterior median (or mean) — your point estimate
- 95% credible interval (default) or 89% (McElreath's choice — less likely to be confused with α=0.05)
- Probability of direction (P(β > 0 | data)) when sign matters

For variance components and ICC: same approach but on the posterior of the SD and the derived ICC.

**Don't report posterior probabilities as if they were *p*-values.** "P(β > 0 | data) = .97" is not the same kind of claim as a frequentist *p*-value, and conflating them invites methodological criticism.

### Reporting template (Bayesian)

> We fit a Bayesian multilevel model with brms 2.20 (Stan backend), using 4 chains of 4000 iterations (2000 warmup). Priors were weakly informative: Normal(0, 100) on fixed-effect coefficients, Student-t(3, 0, 150) on random-effect SDs and residual SD, and LKJ(2) on the random-effect correlation matrices. All R-hat values were below 1.01 and bulk ESS exceeded 1000 for all parameters. The posterior median effect of condition was 23.4 ms (95% CrI [8.1, 38.7]), with 99.7% of the posterior mass above zero.

## Model comparison

Use leave-one-out cross-validation (LOO) via the `loo` package (or `arviz.loo` in Python). Don't use BIC for MLMs. AIC is OK but loo is better.

```r
loo1 <- loo(fit_simple)
loo2 <- loo(fit_full)
loo_compare(loo1, loo2)
```

`elpd_diff` more than ~4 SE in favor of one model is a meaningful preference.

Watch for high Pareto-k diagnostics (> 0.7) — observations that disproportionately influence the result. Refit with `reloo = TRUE` or investigate those observations.

## Posterior predictive checks

Always do them. They catch model misspecification that R-hat won't.

```r
pp_check(fit, type = "dens_overlay")           # density overlay
pp_check(fit, type = "stat_grouped", stat = "mean", group = "condition")  # condition means
pp_check(fit, type = "intervals", x = "trial")  # per-trial intervals
```

If the posterior predictive systematically misses features of the data (e.g., wrong skewness, wrong cluster-level variance), the model is wrong somewhere — likely the likelihood family, or omitted heteroscedasticity.

## When Bayesian fits regularize variance components — and when they don't

Priors regularize **toward** the prior mean. With `HalfNormal(0, σ)`, you're regularizing small variance components toward zero, but not as hard as ML/REML can crush them to exactly zero. With LKJ(2), correlations are regularized mildly toward zero.

This means: a Bayesian fit of a maximal model that lme4 fails on will usually succeed and give sensible answers, but if there's genuinely no information about a variance component, the posterior will be close to the prior. That's the correct behavior — but it means you should still inspect, and report whether posteriors are prior-dominated or data-dominated. `posterior_summary()` and prior/posterior overlay plots (`mcmc_plot(fit, type = "areas")`) make this easy.

## Key references

- Gelman, A., & Hill, J. (2007). *Data Analysis Using Regression and Multilevel/Hierarchical Models.* Cambridge UP.
- Gelman, A., Hill, J., & Vehtari, A. (2020). *Regression and Other Stories.* Cambridge UP.
- Gelman, A., Vehtari, A., Simpson, D., et al. (2020). Bayesian workflow. arXiv:2011.01808.
- McElreath, R. (2020). *Statistical Rethinking* (2nd ed.). CRC Press.
- Bürkner, P.-C. (2017). brms: An R package for Bayesian multilevel models using Stan. *Journal of Statistical Software*, 80(1).
- Vehtari, A., Gelman, A., & Gabry, J. (2017). Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC. *Statistics and Computing*, 27(5), 1413–1432.
