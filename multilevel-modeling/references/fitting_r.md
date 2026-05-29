# Fitting MLMs in R

The R ecosystem for MLM is more mature than Python's. Default to it when the user is flexible.

## Package selection

| Need | Use | Notes |
|---|---|---|
| LMM (continuous outcome) | `lme4::lmer` + `lmerTest` | Standard. `lmerTest` adds Satterthwaite *p*-values. |
| GLMM (binary, count) | `lme4::glmer` or `glmmTMB::glmmTMB` | `glmmTMB` is faster and more flexible (zero-inflation, dispersion modeling, AR(1) residuals, heterogeneous variances). |
| Ordinal | `ordinal::clmm` | Cumulative link mixed models. |
| Survival / time-to-event | `coxme::coxme`, `survival::coxph` with `frailty` | |
| Bayesian (Stan-backed) | `brms` | Use this whenever maximal models won't converge frequentist-style, with few clusters, or when you want proper uncertainty in variance components. See `bayesian_workflow.md`. |
| Bayesian (faster but less flexible) | `rstanarm` | Pre-compiled; faster startup. Less flexible than brms. |
| Multiple imputation + MLM | `mice` + `lme4` via `with()` and `pool()` | |
| Older but still useful | `nlme::lme` | Better for some variance structures (AR(1) within-subject, heteroscedasticity via `weights = varIdent`). |

## lme4 / lmerTest workflow

```r
library(lme4)
library(lmerTest)  # loads on top of lme4 to add p-values

# Maximal model for a 2x2 within-subjects, with crossed random effects of subject and item
fit <- lmer(
  rt ~ condition * distractor + 
    (1 + condition * distractor | subject) + 
    (1 + condition | item),  # distractor was between-items
  data = d,
  control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 1e5))
)

summary(fit)

# Always check for singular fits
isSingular(fit)
VarCorr(fit)

# rePCA tells you how many random-effects dimensions are actually supported
summary(rePCA(fit))
```

If `isSingular()` is TRUE or `rePCA` shows components near zero, follow the simplification procedure in `random_effects_specification.md` (drop correlations first via `||`, then highest-order interaction slopes, etc.).

### Inference

`lmerTest` provides Satterthwaite (default) and Kenward-Roger *p*-values:

```r
anova(fit)  # F-tests with Satterthwaite df
anova(fit, ddf = "Kenward-Roger")  # more conservative, slower, often preferred
summary(fit)$coefficients  # t-tests on fixed effects
```

For confidence intervals on fixed effects and variance components:

```r
confint(fit, method = "profile")     # likelihood profile - usually best
confint(fit, method = "boot", nsim = 1000)  # parametric bootstrap - most reliable for variance components
confint(fit, method = "Wald")        # fastest, but Wald CIs for variance components are bad
```

For likelihood-ratio tests of fixed effects, refit with ML (not REML):

```r
fit_ml <- update(fit, REML = FALSE)
fit_reduced <- update(fit_ml, . ~ . - condition:distractor)
anova(fit_reduced, fit_ml)
```

For LRTs on random effects, the χ² null distribution is wrong (variance components are bounded at 0). The correct null is a mixture of χ²s; in practice, halve the *p*-value for testing one variance component on the boundary, or use parametric bootstrap via `pbkrtest::PBmodcomp`.

### Common warnings and what they mean

| Warning | Meaning | First thing to try |
|---|---|---|
| `Model failed to converge` | Optimizer didn't find a good optimum | Center/scale predictors; try `bobyqa` or `nloptwrap`; check `?convergence` |
| `singular fit` | Variance component(s) at zero or correlation(s) at ±1 | Inspect `VarCorr()`; drop correlations or unsupported slopes |
| `Some predictor variables are on very different scales` | Numerical instability | Scale them: `scale(x)` or divide by a meaningful unit |
| `boundary (singular) fit` | Same as singular fit | Same |
| `Hessian is numerically singular` | Variance-covariance of estimates can't be inverted | Often fixed by the same things as singular fits; sometimes indicates an identifiability problem |

## glmmTMB

Faster than `lme4::glmer` for GLMMs, especially with crossed random effects. Same formula syntax. Adds: zero-inflation (`ziformula`), dispersion modeling (`dispformula`), heterogeneous residual variance.

```r
library(glmmTMB)

fit <- glmmTMB(
  count ~ condition + offset(log_exposure) + 
    (1 + condition | subject) + (1 | item),
  family = nbinom2,
  ziformula = ~ 1,  # constant zero-inflation probability
  data = d
)

summary(fit)
```

For Wald *p*-values, `summary()` gives them directly. For LRTs, use `anova()` to compare nested models. For confidence intervals, `confint(fit)`.

## Effect sizes and ICC

```r
library(performance)
icc(fit)              # variance partition coefficients
r2(fit)               # Nakagawa's marginal and conditional R²
check_model(fit)      # diagnostic plots all at once
check_singularity(fit)
check_convergence(fit)
```

`performance` is the most useful diagnostics package for MLMs. Use it.

## EBLUPs / random effects extraction

```r
ranef(fit)               # conditional modes (BLUPs/EBLUPs)
coef(fit)                # fixed + random combined (per-cluster coefficients)
as.data.frame(ranef(fit))  # tidy frame with conditional SDs for caterpillar plots

# Plot
library(lattice)
dotplot(ranef(fit, condVar = TRUE))
```

## Predictions

```r
# Population-level (random effects set to 0)
predict(fit, newdata = nd, re.form = NA)

# Including specific clusters' random effects
predict(fit, newdata = nd, re.form = ~ (1 | subject))

# Including all (default)
predict(fit)
```

For uncertainty in predictions including random-effects uncertainty, use parametric bootstrap (`bootMer`) or a Bayesian fit.

## Centering helpers

Within-cluster (group-mean) centering with the between-cluster mean as a separate predictor:

```r
library(dplyr)
d <- d %>%
  group_by(subject) %>%
  mutate(
    x_within = x - mean(x, na.rm = TRUE),
    x_between = mean(x, na.rm = TRUE)
  ) %>%
  ungroup()

fit <- lmer(y ~ x_within + x_between + (1 + x_within | subject), data = d)
```

The `x_within` coefficient is the within-subject effect, `x_between` is the between-subject (contextual) effect. Their difference tests whether the two effects are equal — Hox calls this the "contextual model" approach.

## Convergence troubleshooting recipe

When a model won't converge cleanly:

1. **Scale continuous predictors**: `scale()` or divide by 2 SDs (Gelman).
2. **Sum-code factors** (`contrasts = contr.sum`) so the intercept is a grand mean.
3. **Try alternate optimizers**:
   ```r
   library(lme4)
   allFit(fit)  # tries all available optimizers
   ```
4. **Increase iterations**:
   ```r
   control = lmerControl(optCtrl = list(maxfun = 1e6))
   ```
5. **Inspect with `rePCA`** — if dimensions are degenerate, simplify per the principled order in `random_effects_specification.md`.
6. **Go Bayesian**: `brms::brm()` with weakly informative priors will fit models lme4 can't.

## A complete example (psycholinguistic 2×2)

```r
library(lme4); library(lmerTest); library(performance)

# Sum coding so the intercept is the grand mean
contrasts(d$condition)  <- contr.sum(2)
contrasts(d$distractor) <- contr.sum(2)

# Maximal model
fit_max <- lmer(
  rt ~ condition * distractor +
    (1 + condition * distractor | subject) +
    (1 + condition | item),                      # distractor between-items
  data = d,
  REML = TRUE,
  control = lmerControl(optimizer = "bobyqa")
)

# Diagnose
isSingular(fit_max)
summary(rePCA(fit_max))
VarCorr(fit_max)

# If singular and the interaction slope variance is ~0 by-subject:
fit_red <- lmer(
  rt ~ condition * distractor +
    (1 + condition + distractor | subject) +     # dropped interaction slope
    (1 + condition | item),
  data = d,
  control = lmerControl(optimizer = "bobyqa")
)

# Report
summary(fit_red)
anova(fit_red, ddf = "Kenward-Roger")
icc(fit_red)
r2(fit_red)
confint(fit_red, method = "profile")
```

Document every step: the maximal structure you specified, what diagnostic motivated each simplification, and the final structure you report.
