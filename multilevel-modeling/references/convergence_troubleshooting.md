# Convergence Troubleshooting: A Decision Tree

The dispersed advice across `random_effects_specification.md`, `fitting_r.md`, and `bayesian_workflow.md` brought together as a single procedure. When a model fails to fit cleanly, work down this list. **Do not drop random-effects structure until you've exhausted the upstream fixes.** The most common mistake in applied MLM is to skip the cheap fixes and reflexively simplify the model.

## Step 1: Identify what kind of problem you have

Different warnings point to different remedies. First, classify:

### Frequentist (lme4, glmmTMB)

| Symptom | Likely cause |
|---|---|
| `Model failed to converge with max\|grad\|` warning | Optimizer hit iteration limit or precision threshold |
| `boundary (singular) fit` | Variance component(s) estimated at 0 or correlation(s) at ±1 — overspecified random structure |
| `Hessian is numerically singular` | Identifiability problem; often paired with singular fit |
| `Some predictor variables are on very different scales` | Numerical conditioning — fix scaling |
| `Model is nearly unidentifiable` | Fixed-effects collinearity or near-collinearity |
| Output looks fine but `isSingular()` returns TRUE | Same as singular fit — don't ignore just because no warning printed |

### Bayesian (brms, bambi, PyMC, Stan)

| Symptom | Likely cause |
|---|---|
| Divergent transitions after warmup | Posterior geometry problem — usually solvable |
| Maximum treedepth exceeded | Sampler hitting iteration cap per draw |
| Low effective sample size (ESS < ~400 per chain) | Poor mixing — autocorrelated chains |
| R-hat > 1.01 | Chains disagree — not converged |
| BFMI low | Energy distribution problem (often paired with divergences) |

## Step 2: Cheap fixes first (try all of these before touching the model)

These are essentially free and resolve a large fraction of convergence issues.

### 2a. Scale and center continuous predictors

```r
d$x_scaled <- as.numeric(scale(d$x))          # mean=0, SD=1
# Or Gelman's rescaling: divide by 2 SDs
d$x_scaled <- d$x / (2 * sd(d$x, na.rm = TRUE))
```

If predictors live on wildly different scales (one in the thousands, another between 0 and 1), the optimizer struggles. lme4 will warn about this explicitly; even when it doesn't, scaling helps.

### 2b. Switch from treatment to sum or contrast coding

Treatment coding creates correlations in interaction models that show up in the random-effects covariance. Sum coding decorrelates these. See `references/contrast_coding.md` for details.

```r
contrasts(d$condition) <- contr.sum(2)
# Or for 2-level: (-0.5, +0.5)
contrasts(d$condition) <- matrix(c(-0.5, 0.5), ncol = 1)
```

This alone resolves many singular fits in maximal models without dropping any structure.

### 2c. Try a different optimizer (lme4 specifically)

```r
# Try them all and compare
library(lme4)
all_fits <- allFit(fit)
summary(all_fits)
```

If one optimizer converges cleanly and others fail or warn, the converged one is likely fine. If they disagree on parameter estimates substantially, that's a sign of a genuine identifiability problem and you can't optimizer-your-way out.

Common optimizers to try: `bobyqa`, `Nelder_Mead`, `nlminbwrap`, `nloptwrap`. `bobyqa` is often best for lme4.

```r
fit <- lmer(formula, data = d,
            control = lmerControl(optimizer = "bobyqa",
                                  optCtrl = list(maxfun = 1e5)))
```

For `glmmTMB`, options are more limited but worth checking:

```r
fit <- glmmTMB(formula, data = d,
               control = glmmTMBControl(optimizer = optim,
                                        optArgs = list(method = "BFGS")))
```

### 2d. Increase iterations

If the optimizer is converging in direction but running out of iterations:

```r
control = lmerControl(optCtrl = list(maxfun = 1e6))  # default is 1e4 for some optimizers
```

For Bayesian: longer warmup and more iterations.

```r
brm(..., chains = 4, warmup = 4000, iter = 8000)
```

### 2e. (Bayesian) Increase `adapt_delta` / `target_accept`

For divergent transitions in brms/Stan or bambi/PyMC:

```r
# brms
brm(..., control = list(adapt_delta = 0.95, max_treedepth = 12))
# Push to 0.99 and 15 if still problematic
```

```python
# bambi
model.fit(target_accept=0.95)
# Push to 0.99
```

This costs time per draw but resolves many divergences without changing the model.

## Step 3: Diagnose what's actually unsupported

Only after the cheap fixes haven't resolved things should you look at simplifying the model. The goal here is to identify *which specific* random-effects parameter the data doesn't support, not to drop structure wholesale.

### 3a. Inspect the random-effects covariance

```r
VarCorr(fit)
summary(fit)$varcor
```

Look for:
- Variance components estimated at exactly 0
- Correlation parameters estimated at exactly ±1

These are the parts the data can't pin down. If a variance is exactly 0, the data doesn't support that random effect. If a correlation is exactly ±1, the data doesn't support estimating the correlation (but the variances themselves might be fine).

### 3b. Run rePCA

```r
library(lme4)
summary(rePCA(fit))
```

This decomposes the random-effects covariance matrix into principal components. Components near zero indicate dimensions the data doesn't support. If `rePCA` shows that a 5-parameter random-effects structure only supports 3 effective dimensions, the model is overspecified — but you still need to figure out *which* dimensions to drop.

Bates et al. (2015) directly recommend this as the diagnostic for principled simplification.

### 3c. For Bayesian fits, inspect prior-vs-posterior

```r
# brms
library(bayesplot)
mcmc_areas(fit, regex_pars = "sd_")  # density of SD parameters
posterior_summary(fit, pars = "sd_")
```

If a variance-component posterior overlaps heavily with the prior, the data is uninformative about it. That's not a fatal problem — Bayesian fits handle this gracefully — but it tells you what's actually being estimated vs. prior-dominated.

## Step 4: Principled simplification (only after Steps 1–3)

If diagnostics confirm overspecification, simplify in this order:

### 4a. Drop correlation parameters first

Replace `(1 + x | subject)` with `(1 + x || subject)`. Same variances; correlations forced to zero. This is the smallest change that resolves singular correlations.

Caveat in lme4: `||` only works cleanly for numeric predictors. For factors with multiple levels (or interactions of factors), you need to expand explicitly:

```r
# This doesn't reliably suppress all correlations for a factor:
(1 + condition || subject)

# Safer for factors: expand manually
(1 | subject) + (0 + condition | subject)

# For multiple terms:
(1 | subject) + (0 + condition | subject) + (0 + distractor | subject) + 
  (0 + condition:distractor | subject)
```

If correlations were the problem, this fix is sufficient.

### 4b. Drop highest-order interaction slopes

If you have `(1 + A * B | subject)` and the A:B interaction slope variance is near zero, drop it:

```r
(1 + A + B | subject)
```

Document this: "The by-subject random slope for the A×B interaction had variance estimated at 0, so we dropped it following Matuschek et al. (2017)."

### 4c. Drop main-effect slopes only as a last resort

And only on the grouping factor where the variance is at zero. If by-item random slope for condition has variance 0 but by-subject random slope is fine, drop only the by-item version.

### 4d. Never drop the random intercept

Unless you have a very strong design-based reason. The intercept variance is almost always nonzero in practice (people differ from each other in their means), and dropping it forces a wrong assumption.

### 4e. Order summary

The principled simplification order:

1. Correlations
2. Highest-order interaction slopes (on the grouping factor where the variance is at zero)
3. Lower-order interaction slopes
4. Main-effect slopes
5. The random intercept (essentially never)

Document every step and the diagnostic that motivated it. In the write-up, explain the order of removals.

## Step 5: Consider going Bayesian instead

For models where the maximal structure is design-justified but lme4 keeps singular-fitting, a Bayesian fit with weakly informative priors often fits cleanly without dropping anything. The prior keeps variance components off the boundary; the LKJ prior keeps correlations away from ±1.

This is not a hack. It's that REML/ML at the boundary is genuinely ill-conditioned, while Bayesian estimation with regularizing priors is well-defined. The maximal model is what the design requires; Bayesian estimation just lets you fit it.

```r
library(brms)
fit_b <- brm(
  formula = formula_maximal,
  data = d,
  prior = c(
    prior(normal(0, 10), class = "b"),
    prior(student_t(3, 0, sd_y), class = "sd"),
    prior(lkj(2), class = "cor")
  ),
  chains = 4, cores = 4, iter = 4000,
  control = list(adapt_delta = 0.95)
)
```

If the Bayesian fit converges and the posteriors for variance components look reasonable (not prior-dominated, R-hat < 1.01, ESS > 400 per chain), this is your model. Report it as such.

## Step 6: Genuinely intractable cases

A small fraction of designs are genuinely too complex for the data. Signs:

- Even the simplest reasonable random-effects structure fails
- Bayesian fit shows posteriors completely prior-dominated for variance components
- Different optimizers / different priors give wildly different estimates

In these cases, the honest moves are:
- Collect more data (especially more clusters)
- Simplify the design or hypothesis to one the data can address
- Acknowledge limitations explicitly in the write-up

Don't fit a model that the data doesn't support and report it as if it does.

## Quick-reference flowchart

```
Convergence warning / singular fit
         │
         ▼
Are predictors on similar scales? ───No──► Scale them
         │ Yes
         ▼
Using sum/contrast coding for factors? ──No──► Switch coding
         │ Yes
         ▼
Tried alternative optimizers (allFit)? ──No──► Try them
         │ Yes
         ▼
Increased max iterations / adapt_delta? ──No──► Increase
         │ Yes
         ▼
Inspect VarCorr() and rePCA()
         │
         ▼
Is the problem just correlations? ────Yes──► Drop correlations (||)
         │ No (variance(s) at 0)
         ▼
Drop highest-order interaction slope on the affected grouping factor
         │
         ▼
Still problematic?
         │
         ▼
Try Bayesian fit with weakly informative priors
         │
         ▼
Still problematic? ──► Honestly: the design is too complex for the data
```

## Documenting your troubleshooting

In the methods section, briefly state what you tried:

> The maximal random-effects structure (Barr et al., 2013) produced a singular fit with the by-subject random-effect correlations estimated at ±1. We first verified that predictors were centered and that factors used sum coding, then tried alternative optimizers via `allFit()`; the singular fit persisted. Following Bates et al. (2015), we removed the correlation parameters using `||` syntax. The reduced model converged without warnings, with no singular variance components (smallest rePCA component = 0.04). We report this model below.

That paragraph turns a "we simplified" hand-wave into a defensible methodological choice.
