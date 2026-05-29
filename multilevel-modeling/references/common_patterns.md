# Common Patterns and Pitfalls

A field guide to recurring MLM situations and the mistakes that go with them. Skim this when the user describes a design — there's a good chance one of these patterns applies.

## Pattern: Subjects × items psycholinguistic experiment

Setup: each subject sees each item, items are sampled from a population (words, sentences, faces, etc.). One or more within-subject manipulations.

The right model has **crossed random effects** for subjects and items, with random slopes for any within-cluster manipulation:

```r
rt ~ condition + (1 + condition | subject) + (1 + condition | item)
```

Common mistakes:

- **Aggregating to subject means and running by-subjects ANOVA.** Clark (1973) — items vary too; this ignores it and inflates Type I error for treating items as a fixed effect.
- **F1/F2 ANOVA** (separate by-subjects and by-items analyses then combining via min-F'). Old workaround; just fit the mixed model.
- **Only by-subject random effects, omitting items.** Same Type I inflation as F1-only ANOVA.
- **Only random intercepts, no slopes.** Barr et al. (2013) directly addresses this. Inflated Type I rates of 20–50% in their simulations.

## Pattern: Pre-post or simple repeated measures

Setup: each subject measured at two or more time points. Compare time points.

If time has only 2 levels, the most general specification:

```r
y ~ time + (1 + time | subject)
```

A paired *t*-test is equivalent to this in the balanced case with no missing data. The MLM gains: handles missing data sensibly, extends naturally to more time points and covariates.

Common mistakes:

- **Running independent-samples test ignoring the pairing.** Classic.
- **Computing differences and t-testing them but ignoring covariates that should be modeled.** Often fine but loses flexibility.
- **For ≥3 time points: treating time as categorical without thinking.** Sometimes correct (compare specific time points), but for trajectories use time as continuous and add random slopes.

## Pattern: Longitudinal growth curve

Setup: each subject measured at several time points; you care about the trajectory.

Baseline model — random intercept and slope for time:

```r
y ~ time + (1 + time | subject)
```

Extensions:

- Polynomial growth: `y ~ time + I(time^2) + (1 + time + I(time^2) | subject)` — and use orthogonal polynomials (`poly()`) to reduce collinearity
- Spline-based: `y ~ ns(time, df=4) + (1 + ns(time, df=4) | subject)` (random effects on splines get expensive quickly)
- Predictor of trajectory: `y ~ time * treatment + (1 + time | subject)` — `time:treatment` is the differential growth rate by group

Common mistakes:

- **Random intercept only** for growth curves. Almost never defensible — assumes everyone grows at the same rate.
- **Using `lme4` without thinking about time coding.** Coding `time` as 0, 1, 2, 3 vs. centering it at the mean changes what the intercept represents. Coding as 0 at first observation makes the intercept the baseline; centered coding makes it the average.
- **Forgetting to model serial autocorrelation when time points are dense.** `nlme::lme` with `correlation = corAR1()` or `glmmTMB` with `ar1()` random structure. lme4 doesn't do this natively.

## Pattern: Cluster-randomized trial / multi-site study

Setup: treatment assigned at the cluster level (school, clinic, village). Outcome measured at the individual level.

Standard model:

```r
y ~ treatment + (1 | cluster)
```

Treatment is between-cluster, so no random slope for treatment is possible. The big question is **how many clusters** you have. With < 30, frequentist variance estimation for the cluster random effect is unreliable — go Bayesian, or use small-sample-corrected methods (Kenward-Roger).

Common mistakes:

- **Ignoring the clustering** and running individual-level OLS. Massively anti-conservative; reviewers will catch this immediately.
- **Including cluster as a fixed effect with dummies** when there are many clusters. Wastes degrees of freedom; loses partial pooling.
- **Comparing cluster means with a t-test on ~10 clusters.** Loses individual-level variation; underpowered.

## Pattern: Diary / EMA / experience sampling

Setup: many observations per person across days/moments.

Within-person predictor (e.g., today's stress) needs careful centering decisions. The within-person effect of stress on mood is conceptually different from the between-person effect (stressed people are unhappier people). Use within/between decomposition:

```r
library(dplyr)
d <- d %>%
  group_by(person_id) %>%
  mutate(
    stress_within = stress - mean(stress, na.rm = TRUE),
    stress_between = mean(stress, na.rm = TRUE)
  ) %>%
  ungroup()

fit <- lmer(mood ~ stress_within + stress_between + 
            (1 + stress_within | person_id), data = d)
```

`stress_within` is the within-person effect; `stress_between` is the between-person effect. Reporting both is much more informative than reporting a grand-mean-centered single coefficient.

Common mistakes:

- **Treating EMA data as if observations were independent.** With 50+ observations per person, the standard errors will be wrong by an order of magnitude.
- **Grand-mean centering only** — conflates within and between effects.
- **No random slope for the within-person predictor.** People differ in how much their mood responds to stress. Omitting the slope inflates Type I for the within-person effect.

## Pattern: Cross-classified data

Setup: observations belong to multiple grouping factors that don't nest. E.g., students belong to both schools and neighborhoods; sentences belong to both texts and speakers.

```r
y ~ x + (1 | school) + (1 | neighborhood)
```

Specify both as crossed random effects. lme4 and brms handle this natively.

Common mistakes:

- **Ignoring one of the cross-classifying factors.** Loses information about that source of variation; sometimes inflates Type I if that factor correlates with the predictor.
- **Using nesting syntax (`(1 | school/neighborhood)`) for cross-classified data.** That's wrong — it implies a hierarchy where there isn't one.

## Pattern: Binary outcomes in MLM (GLMM)

Setup: outcome is yes/no, correct/incorrect, etc.

```r
glmer(correct ~ condition + (1 + condition | subject) + (1 + condition | item),
      data = d, family = binomial())
```

Or with `glmmTMB::glmmTMB(..., family = binomial())` for speed.

Things specific to GLMMs:

- **Coefficients are on the log-odds (logit) scale.** Exponentiate for odds ratios. For probabilities, use `predict(fit, type = "response")`.
- **The fixed-effect interpretation is cluster-specific (conditional)**, not population-averaged. If you want population-average effects, use GEE (`geepack` or `statsmodels.gee`) with a working correlation and robust SEs.
- **Convergence is harder than for LMMs.** Center predictors; scale them. Try `nAGQ > 1` for `glmer` (adaptive Gauss-Hermite quadrature with more nodes) for accuracy, though only with a single grouping factor.
- **Complete separation** can make estimates blow up. With a Bayesian prior, this is much better behaved.

## Pattern: Count outcomes (Poisson, negative binomial)

```r
glmer(count ~ condition + offset(log(exposure)) + 
      (1 + condition | subject), 
      data = d, family = poisson())
```

For overdispersion (variance > mean):

```r
glmmTMB(count ~ ..., family = nbinom2)  # negative binomial
```

Common mistakes:

- **Ignoring overdispersion in Poisson models.** Inflates significance. Check with `performance::check_overdispersion()`.
- **Forgetting the offset** when the exposure (time at risk, number of trials) varies.

## Pitfall: Convergence warnings ignored

The reflex in many tutorials is "convergence warning means simplify." Often the right response is to:

1. Check that predictors are sensibly scaled.
2. Try alternate optimizers (`allFit()` in lme4).
3. Use sum coding instead of treatment coding.
4. Go Bayesian.

Only after those should you start dropping random-effects structure — and even then, do it in the principled order.

## Pitfall: Reporting a single *p*-value as the result

A complete MLM analysis report includes variance components, ICC, the random-effects structure, convergence diagnostics, effect sizes, and CIs. *p*-values alone are 2010-era practice and increasingly flagged in review.

## Pitfall: Centering decisions made implicitly

The intercept's meaning depends on how predictors are coded. If `condition` is treatment-coded with control = reference, the intercept is the predicted value in the control condition. If sum-coded, it's the grand mean. Both are valid; they're different parameters. Be explicit about which you used.

Similarly, the meaning of a random slope depends on the coding of the predictor. With contrast-coding for a 2-level factor (-0.5, 0.5), the random slope represents between-cluster variation in the difference between conditions, which is usually what you want.

## Pitfall: Confusing nested with crossed

If student IDs are unique across schools, `(1 | school) + (1 | student)` and `(1 | school/student)` give the same fit. If student IDs are not unique (student 1 in school A is a different person from student 1 in school B), the first formula will treat them as the same student. Always recode IDs to be globally unique or use the nesting syntax.

## Pitfall: Forgetting to refit with ML for fixed-effect LRTs

lme4 fits with REML by default, which is correct for variance estimation but **not** appropriate for likelihood-ratio tests of fixed effects (different REML criteria correspond to different fixed-effects structures). Refit with `REML = FALSE` for LRTs of fixed effects.

For LRTs of random effects, REML is correct, and you need the boundary correction (mixture of χ²s) for accurate *p*-values.

## Pitfall: Using AIC/BIC to choose random-effects structure

AIC/BIC penalties for random effects are non-standard because variance components live at a boundary. Better:

- For random effects, use parametric bootstrap LRTs or just report what you fit and why.
- For nested model comparison, LRT (with boundary correction for variance components).
- For non-nested comparison, leave-one-out cross-validation (LOO) via `loo` package in Bayesian fits.

## Pattern: Choosing between MLM, GEE, and cluster-robust SEs

When a user has clustered data and asks which approach to use, this is the decision that matters. The three approaches answer different questions and make different assumptions.

### The core distinction

**MLM (mixed-effects models)** estimate cluster-specific (conditional) effects: "how does X affect Y within a given cluster, holding its random effect constant?" The random-effects structure also provides variance decomposition and ICC — information about how much of the outcome variation is between vs. within clusters.

**GEE (generalized estimating equations)** estimate population-average (marginal) effects: "how does X affect Y on average across the population of clusters?" GEE specifies a "working correlation structure" for within-cluster observations (exchangeable, AR(1), independent) but gets robust SEs regardless of whether that structure is correct (Liang & Zeger, 1986).

**Cluster-robust SEs** on OLS or GLM also estimate population-average effects, without explicitly modeling the within-cluster correlation. The sandwich estimator (White, 1980; Huber, 1967) corrects the SEs for clustering without treating it as a modeling problem.

### When they give the same answer

For **linear outcomes (LMM)**: all three give the same fixed-effect estimates (under correct specification of the mean model). The differences are in efficiency and what you can additionally recover (variance components, cluster-level predictions).

For **nonlinear outcomes (GLMM)**: they do NOT give the same answer. The conditional (MLM) coefficient is always larger in magnitude than the marginal (GEE) coefficient because the nonlinear transformation (logistic, log-linear) is averaged differently. This is not a bug — they're estimating different quantities. Neither is "correct" in the abstract; pick the one that matches your scientific question.

### Decision guide

```
Does your scientific question require cluster-level predictions 
or between-cluster variance decomposition (ICC)?
  YES → MLM

Is your outcome nonlinear (binary, count) AND do you want 
an effect interpretable at the population level?
  YES → GEE

Do you have <30 clusters?
  YES → Avoid cluster-robust SEs (sandwich unreliable); use MLM or GEE

Is your outcome continuous, dataset large, and clustering a nuisance?
  YES → Cluster-robust SEs on OLS are defensible
```

### Software

**R:**
```r
# GEE
library(geepack)
fit_gee <- geeglm(y ~ x, id = cluster_id, data = d,
                  family = binomial(), corstr = "exchangeable")

# Cluster-robust SEs
library(sandwich); library(lmtest)
fit_ols <- lm(y ~ x, data = d)
coeftest(fit_ols, vcov = vcovCL(fit_ols, cluster = ~cluster_id))

# Or tidier:
library(estimatr)
lm_robust(y ~ x, clusters = cluster_id, data = d)
```

**Python:**
```python
import statsmodels.formula.api as smf

# GEE
fit_gee = smf.gee("y ~ x", groups="cluster_id", data=d,
                   family=sm.families.Binomial(),
                   cov_struct=sm.cov_struct.Exchangeable()).fit()

# Cluster-robust SEs via statsmodels OLS
fit_ols = smf.ols("y ~ x", data=d).fit(cov_type="cluster",
                                        cov_kwds={"groups": d["cluster_id"]})
```

### Key references
- Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models. *Biometrika*, 73(1), 13–22.
- Zeger, S. L., Liang, K.-Y., & Albert, P. S. (1988). Models for longitudinal data: A generalized estimating equation approach. *Biometrics*, 44(4), 1049–1060.
- Hubbard, A. E., et al. (2010). To GEE or not to GEE. *Epidemiology*, 21(4), 467–474. [clear practical comparison]

## Pitfall: Believing the level-2 *n* is large

Many studies have hundreds or thousands of observations but only 15 clusters. Inference about cluster-level effects is constrained by the **cluster *n***, not the observation *n*. Power for cross-level interactions is especially sensitive to this.

With small cluster *n*: use Kenward-Roger degrees of freedom (`lmerTest`), or go Bayesian.
