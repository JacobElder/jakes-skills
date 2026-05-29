# Post-Estimation: Contrasts, Simple Slopes, and Marginal Effects

Fitting the model is half the job. Communicating what it means is the other half. This reference covers the tools for extracting interpretable quantities — specific contrasts, simple slopes, adjusted predictions, marginal effects — from a fitted MLM.

The two dominant frameworks are `emmeans` (Lenth) and `marginaleffects` (Arel-Bundock). Both work with `lme4`, `glmmTMB`, `brms`, `rstanarm`, and others. They overlap heavily but emphasize different things.

## When you reach for post-estimation tools

- The coefficient table answers "is the effect different from zero," but you want "what's the predicted value in condition X" → `emmeans` or `marginaleffects::predictions`
- You have an interaction and want to test the effect of A at each level of B → `emmeans` with simple slopes, or `marginaleffects::slopes`
- You need pairwise comparisons among 4+ factor levels with multiple-comparison adjustment → `emmeans` pairs()
- You want the average treatment effect on the probability scale from a logistic GLMM → `marginaleffects::avg_slopes`
- You need to communicate findings to a non-statistical audience and the log-odds coefficient won't do → either, on the response scale

## emmeans (R)

The estimated marginal means framework. Conceptually: compute predictions at a reference grid of predictor values, then average or contrast those predictions.

```r
library(emmeans)

# Fit a model
fit <- lmer(rt ~ condition * distractor + (1 + condition * distractor | subject), data = d)

# Estimated marginal means by condition (averaging over distractor)
emm <- emmeans(fit, ~ condition)
emm
# condition emmean   SE    df lower.CL upper.CL
# control     612.3 18.4  58.4    575.5    649.1
# treatment   635.9 17.9  58.4    600.0    671.8

# Pairwise comparison with Tukey adjustment
pairs(emm)

# Both factors and the interaction
emmeans(fit, ~ condition * distractor)

# Simple slopes: effect of condition AT each level of distractor
emmeans(fit, pairwise ~ condition | distractor)
```

For continuous moderators (Johnson-Neyman intervals, simple slopes at specific values):

```r
# Effect of x at specific values of moderator z
emtrends(fit, ~ z, var = "x", at = list(z = c(-1, 0, 1)))

# Johnson-Neyman: range of z where x effect is significant
emtrends(fit, ~ z, var = "x", at = list(z = seq(-3, 3, 0.1)))
```

For GLMMs, you can request the response scale:

```r
fit_glmm <- glmer(correct ~ condition + (1|subject), data = d, family = binomial())

# Log-odds scale (default)
emmeans(fit_glmm, ~ condition)

# Probability scale
emmeans(fit_glmm, ~ condition, type = "response")

# Odds ratio for the contrast
pairs(emmeans(fit_glmm, ~ condition), type = "response")
```

For Bayesian fits (`brms`), emmeans works the same way but returns posterior summaries:

```r
emm_b <- emmeans(brm_fit, ~ condition)
summary(emm_b, point.est = median)
# Includes posterior median and 95% HPD interval

# Get the full posterior draws for a contrast
contrast_draws <- as.mcmc(pairs(emm_b))
mean(contrast_draws > 0)  # posterior probability of direction
```

## marginaleffects (R and Python)

A newer framework that consolidates predictions, contrasts, and marginal effects (derivatives/slopes) under one API. Works in R and Python; same syntax as much as possible.

```r
library(marginaleffects)

# Predictions at every combination in the data
predictions(fit)

# Predictions at a specified grid
predictions(fit, newdata = datagrid(condition = unique, distractor = unique))

# Average predicted value by condition
avg_predictions(fit, by = "condition")

# Slope of x with respect to y, averaged over the sample
avg_slopes(fit, variables = "x")

# Comparison: difference between conditions, averaged
avg_comparisons(fit, variables = "condition")

# Hypothesis tests on arbitrary linear combinations
predictions(fit, hypothesis = "b1 = b2")
```

The Python interface is identical for the most part:

```python
from marginaleffects import predictions, avg_slopes, avg_comparisons

predictions(fit)
avg_comparisons(fit, variables="condition")
avg_slopes(fit, variables="x")
```

A useful distinction `marginaleffects` makes precise: **conditional vs. marginal effects** in GLMMs. For a logistic GLMM, the coefficient is the cluster-conditional effect (the effect for a typical cluster). The marginal (population-averaged) effect is different because of the nonlinearity. `marginaleffects` computes both:

```r
# Population-averaged predicted probabilities — integrating over the random effects
avg_predictions(fit_glmm, re.form = NA)

# Cluster-conditional (random effects at their means)
avg_predictions(fit_glmm)
```

This matters because reviewers and applied audiences often want population-average effects but the MLM coefficient gives cluster-conditional effects. Being able to report both — and explain the difference — improves the analysis.

## emmeans vs marginaleffects: when to use which

Honest practitioner take:

- **emmeans** is older, more mature for designs with multiple factors and complex contrast specifications, and integrates cleanly with planned-comparisons workflows. Its `pairs()` and `contrast()` interfaces are unmatched for "I have a 3×2×2 design and need specific contrasts with Holm correction."
- **marginaleffects** is unified, better-documented for non-statisticians, and handles the conditional-vs-marginal distinction in GLMMs more transparently. It's also actively developed and works in Python.

For frequentist work with rich factorial structure, lean emmeans. For Bayesian work, mixed model + GLMM marginal effects, or anything where you want one tool across R and Python, lean marginaleffects. You can use both in the same analysis.

## Common patterns

### Simple slopes for a continuous × continuous interaction

You fit `y ~ x * z + (1 + x | subject)`. You want the effect of x at low, mean, and high z.

```r
# emmeans approach
emtrends(fit, ~ z, var = "x", at = list(z = c(mean(d$z) - sd(d$z),
                                                mean(d$z),
                                                mean(d$z) + sd(d$z))))

# marginaleffects approach
slopes(fit, variables = "x", 
       newdata = datagrid(z = c(-1, 0, 1) * sd(d$z) + mean(d$z)))
```

### Pairwise comparisons among many levels

You have a 5-level factor and want all 10 pairwise comparisons with FDR adjustment.

```r
emm <- emmeans(fit, ~ group)
pairs(emm, adjust = "fdr")
```

### Probability scale predictions from a logistic GLMM

You fit a logistic GLMM and want predicted probabilities by condition, with CIs, for the response-scale outcome.

```r
# emmeans
emmeans(fit, ~ condition, type = "response")

# marginaleffects
avg_predictions(fit, by = "condition")
```

### Effect of a treatment averaged over a covariate

You fit `y ~ treatment + age + (1|subject)` and want the treatment effect, marginalized over the empirical age distribution (population-average rather than at mean age).

```r
# emmeans
emmeans(fit, ~ treatment, at = list(age = unique(d$age)), weights = "proportional")

# marginaleffects (this is the default — averages over observed data)
avg_comparisons(fit, variables = "treatment")
```

### Reporting from Bayesian MLM

```r
library(brms); library(emmeans); library(tidybayes)

# emmeans on brms fit returns a brmsmargins-style object
emm <- emmeans(brm_fit, ~ condition)

# Get full posterior draws for the contrast
draws <- gather_emmeans_draws(pairs(emm))

# Posterior probability of effect direction
mean(draws$.value > 0)

# Credible interval
quantile(draws$.value, c(0.025, 0.975))
```

## Multiple-comparison adjustments

Both packages handle adjustments. The defaults differ; be explicit:

```r
pairs(emm, adjust = "tukey")  # default for emmeans pairs
pairs(emm, adjust = "bonferroni")
pairs(emm, adjust = "fdr")
pairs(emm, adjust = "none")
```

For pre-registered planned contrasts, "none" is often appropriate (you specified the contrasts in advance). For exploratory pairwise comparisons, use FDR or Tukey.

## A note on degrees of freedom

For LMMs from `lme4`, both emmeans and marginaleffects use Satterthwaite or Kenward-Roger degrees of freedom (configurable). For GLMMs, they use asymptotic z-tests by default — fine with many clusters, anti-conservative with few. With few clusters in a GLMM, consider:

```r
emmeans(fit, ~ condition, lmer.df = "kenward-roger")  # KR df via pbkrtest
```

Or, more honestly with small samples, use a Bayesian fit and report posterior intervals.

## What to put in the write-up

For each focal effect you discuss, give:

- The estimate on the scale you're reporting on (raw outcome, log-odds, probability, etc.)
- A confidence/credible interval
- The contrast or comparison specification (so a reader could reproduce it)
- The multiple-comparison adjustment, if any

> The effect of treatment, averaged over the four levels of stimulus type, was 24.1 ms (95% CI [11.8, 36.4], computed via `emmeans` with Kenward-Roger degrees of freedom). Pairwise comparisons among stimulus types with FDR adjustment showed reliable differences between types 1 and 4 (Δ = 18.2 ms, *p*_FDR = .003) and types 2 and 4 (Δ = 12.5 ms, *p*_FDR = .04).

That's much more informative than a coefficient table alone.

## Key references

- Lenth, R. V. (2024). emmeans: Estimated Marginal Means, aka Least-Squares Means. R package. https://CRAN.R-project.org/package=emmeans
- Arel-Bundock, V. (2024). marginaleffects: Predictions, Comparisons, Slopes, Marginal Means, and Hypothesis Tests. R/Python package. https://marginaleffects.com
- Searle, S. R., Speed, F. M., & Milliken, G. A. (1980). Population marginal means in the linear model: An alternative to least squares means. *The American Statistician*, 34(4), 216–221.
