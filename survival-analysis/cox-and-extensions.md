# Cox proportional hazards and its extensions

The workhorse of survival regression. This file covers the standard model, stratification, time-varying covariates (the variable changes during follow-up), time-varying coefficients (the variable's effect changes during follow-up), splines, and penalized variants.

## The basic Cox model

Models the hazard as $h(t \mid x) = h_0(t) \exp(x^\top \beta)$. The baseline hazard $h_0(t)$ is left unspecified (semi-parametric). Coefficients are estimated via partial likelihood, which doesn't require $h_0(t)$.

### R
```r
library(survival)

fit <- coxph(Surv(time, status) ~ age + sex + ph.ecog + factor(treatment),
             data = lung, ties = "efron")  # efron > breslow when ties present
summary(fit)
# Output: coef, exp(coef) = HR, se, z, p, plus 95% CI on HR
# Also: concordance, likelihood ratio test, Wald test, score test

# Tidy output
broom::tidy(fit, exponentiate = TRUE, conf.int = TRUE)

# Baseline cumulative hazard
basehaz(fit, centered = FALSE)

# Predicted survival curves for specific covariate profiles
newd <- data.frame(age = c(50, 70), sex = c(1, 1), ph.ecog = c(0, 0), treatment = c(1, 1))
sf <- survfit(fit, newdata = newd)
ggsurvplot(sf, data = lung, conf.int = TRUE, legend.labs = c("age=50", "age=70"))
```

### Python (lifelines)
```python
from lifelines import CoxPHFitter

cph = CoxPHFitter(penalizer=0.0)  # add small penalizer if convergence issues
cph.fit(df, duration_col='time', event_col='event',
        formula="age + sex + ph_ecog + C(treatment)")
cph.print_summary()
# Access components
cph.params_           # log HR
cph.hazard_ratios_    # HR
cph.confidence_intervals_
cph.concordance_index_

# Predicted survival for specific profiles
profiles = df.iloc[:2].copy()
cph.predict_survival_function(profiles).plot()
cph.predict_median(profiles)
cph.predict_partial_hazard(profiles)  # exp(x'beta), the linear predictor on hazard scale
```

### scikit-survival
```python
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.util import Surv

y = Surv.from_dataframe('event', 'time', df)
X = df[['age', 'sex', 'ph_ecog', 'treatment']]
cph = CoxPHSurvivalAnalysis(alpha=0.001)  # small ridge for stability
cph.fit(X, y)
cph.score(X, y)  # concordance
risk = cph.predict(X)                  # linear predictor (higher = worse)
surv_fns = cph.predict_survival_function(X)  # list of step functions
```

### Ties: Breslow, Efron, exact

When several events happen at the same time, the partial likelihood becomes ambiguous about which event "came first." Three approximations:
- **Breslow**: simplest, biased toward 0 when many ties. Avoid unless you have a reason.
- **Efron**: default in R `coxph`. Better with ties. Use this by default.
- **Exact**: enumerates all orderings. Correct but slow on heavy ties.

If your data has many ties (e.g., events recorded by month rather than day), strongly consider **discrete-time survival models** instead (logistic regression with person-period data).

## Stratified Cox

When you have a categorical variable that violates PH but isn't of substantive interest, **stratify** on it. Each stratum gets its own baseline hazard, so the PH assumption only needs to hold *within* strata. Cost: you can't estimate the HR for the stratification variable itself.

### R
```r
fit_s <- coxph(Surv(time, status) ~ age + sex + strata(institution), data = df)
# Now each institution has its own baseline; we don't estimate an institution effect.
```

### Python (lifelines)
```python
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event',
        strata=['institution'], formula="age + sex")
```

Common stratification targets: study center, calendar period, sex (when PH fails), age group.

## Time-varying covariates

Different from time-varying coefficients! Here, the **covariate value changes during follow-up**: a user upgrades their plan partway through, a patient starts a new medication mid-study, a borrower's credit score changes.

Restructure to **counting process** format: one row per interval where covariates are constant. Use `Surv(tstart, tstop, event)`.

### Restructuring example (R, tmerge from survival)

```r
# Long-form patient data:
# patient | tstart | tstop | event | treatment
# 1       | 0      | 30    | 0     | 0
# 1       | 30     | 90    | 1     | 1   <- switched treatment at day 30, event at day 90
# 2       | 0      | 60    | 0     | 0   <- censored at 60

fit_tv <- coxph(Surv(tstart, tstop, event) ~ treatment + age, data = long_df)
summary(fit_tv)
```

Use `tmerge` (in `survival`) to build this safely from baseline + time-stamped event/exposure data — manual restructuring is error-prone.

```r
# Start from baseline:
df1 <- tmerge(baseline, baseline, id = id, endpoint = event(time, status))
# Add a time-varying covariate from a separate table of changes:
df1 <- tmerge(df1, treatment_changes, id = id, treatment = tdc(change_time, new_value))
fit <- coxph(Surv(tstart, tstop, endpoint) ~ treatment + age, data = df1)
```

### Python (lifelines): `CoxTimeVaryingFitter`

```python
from lifelines import CoxTimeVaryingFitter

# df_long must have columns: id, start, stop, event, plus covariates
# Each row is one interval per subject where covariates are constant.
ctv = CoxTimeVaryingFitter()
ctv.fit(df_long, id_col='id', event_col='event',
        start_col='start', stop_col='stop')
ctv.print_summary()
```

### The immortal time bias

If you define a covariate as "ever received treatment by end of follow-up" and treat it as baseline, subjects who received it later were guaranteed to survive long enough to receive it — they couldn't have died first. This artificially inflates survival in the "treated" group. **Always model treatment as time-varying** when timing of exposure varies across subjects. This bug is depressingly common in published research.

## Time-varying coefficients (effect changes over time)

When the effect of a covariate changes with time (PH violation), let the coefficient be a function of time: $h(t \mid x) = h_0(t) \exp(\beta(t) x)$.

### R — `tt()` interaction
```r
# Allow age's effect to change linearly with log(time)
fit_tt <- coxph(Surv(time, status) ~ age + tt(age) + sex, data = lung,
                tt = function(x, t, ...) x * log(t))
summary(fit_tt)
# "age" gives the effect at t=1; "tt(age)" gives the change per unit log(t).
```

Equivalent approach: split follow-up at chosen change points with `survSplit`, then fit a model with time-period interactions.

```r
lung2 <- survSplit(Surv(time, status) ~ ., data = lung, cut = c(180, 365), episode = "tgroup")
fit_split <- coxph(Surv(tstart, time, status) ~ age * strata(tgroup) + sex, data = lung2)
# Now age has a different effect in each time period.
```

### Python (lifelines)

lifelines doesn't natively fit Cox with smooth time-varying coefficients but supports the same time-split approach: restructure to long-form with a time-period indicator and include period × covariate interactions in `CoxTimeVaryingFitter`.

## Splines and non-linear covariate effects

A linear-in-covariate Cox assumes the log-hazard is linear in each predictor. Often wrong for continuous variables (especially age). Check with martingale residuals; fix with splines.

### R
```r
# Restricted cubic spline via rms package (Frank Harrell)
library(rms)
dd <- datadist(lung); options(datadist = "dd")
fit_rcs <- cph(Surv(time, status) ~ rcs(age, 4) + sex, data = lung, x = TRUE, y = TRUE)
print(fit_rcs)
anova(fit_rcs)             # tests for linearity, overall effect
plot(Predict(fit_rcs))     # partial effect plots

# Penalized splines via survival package
fit_ps <- coxph(Surv(time, status) ~ pspline(age, df = 4) + sex, data = lung)
termplot(fit_ps, se = TRUE)
```

### Python (lifelines)

Use `patsy`/`formulaic` formula syntax with `bs()` or `cr()` (natural cubic) splines:

```python
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event',
        formula="bs(age, df=4) + sex + ph_ecog")
cph.plot_partial_effects_on_outcome('age', values=[40, 50, 60, 70, 80])
```

## Penalized Cox (lasso, ridge, elastic net)

For high-dimensional data (genomics, marketing with many features) or to stabilize estimates.

### R — glmnet
```r
library(glmnet)
X <- model.matrix(~ . - 1, data = df[, predictor_cols])
y <- Surv(df$time, df$event)
cv_fit <- cv.glmnet(X, y, family = "cox", alpha = 1)  # alpha=1 lasso, 0 ridge, between=elastic net
plot(cv_fit)
coef(cv_fit, s = "lambda.1se")
```

### Python — scikit-survival
```python
from sksurv.linear_model import CoxnetSurvivalAnalysis

est = CoxnetSurvivalAnalysis(l1_ratio=0.9, alphas=None, n_alphas=100)
est.fit(X, y)
# Pick alpha by cross-validation:
from sklearn.model_selection import GridSearchCV
gs = GridSearchCV(est, {"alphas": [[a] for a in est.alphas_]}, cv=5)
gs.fit(X, y)
```

## Tree- and ensemble-based survival

For non-linear, high-interaction settings with sufficient data.

### Random Survival Forests
```r
# R
library(randomForestSRC)
rsf <- rfsrc(Surv(time, status) ~ ., data = lung, ntree = 500, importance = TRUE)
plot(rsf)
vimp <- vimp(rsf)$importance  # variable importance
```

```python
# Python (scikit-survival)
from sksurv.ensemble import RandomSurvivalForest

rsf = RandomSurvivalForest(n_estimators=500, min_samples_split=10,
                            min_samples_leaf=15, n_jobs=-1, random_state=0)
rsf.fit(X_train, y_train)
rsf.score(X_test, y_test)  # concordance
```

### Gradient Boosting Survival
```python
from sksurv.ensemble import GradientBoostingSurvivalAnalysis
gbs = GradientBoostingSurvivalAnalysis(n_estimators=300, max_depth=3, learning_rate=0.1)
gbs.fit(X_train, y_train)
```

These give better predictive performance than Cox in many applied settings but lose the clean "HR with CI" interpretation. Use SHAP or partial dependence for explanation.

## Neural network survival models

For very large or very high-dimensional data where deep models can help.

```python
# pycox provides DeepSurv (PH-style), DeepHit (multi-event), and PCHazard
from pycox.models import CoxPH
# Requires PyTorch; see pycox docs for full pipeline.
```

These are usually overkill unless you have tens of thousands of subjects and very rich features (images, text).

## Diagnostics — always run these for Cox

### 1. Proportional hazards (Schoenfeld residuals)

```r
zph <- cox.zph(fit)
print(zph)        # p-value per covariate + global
plot(zph)         # one panel per covariate; flat line = PH holds
```

```python
cph.check_assumptions(df, p_value_threshold=0.05, show_plots=True)
```

Don't just look at p-values — plot the residuals. P-values are oversensitive in large samples, undersensitive in small ones.

### 2. Influential observations (dfbeta residuals)

```r
ggcoxdiagnostics(fit, type = "dfbeta")  # via survminer
```

A few subjects shouldn't dominate the fit. If dfbeta plots show large outliers, investigate those rows.

### 3. Functional form for continuous covariates (martingale residuals)

```r
ggcoxfunctional(Surv(time, status) ~ age + log(age) + sqrt(age), data = lung)
# Whichever transformation gives the straightest line is the best functional form.
```

```python
# lifelines: plot martingale residuals against a covariate
from lifelines.plotting import plot_partial_effects_on_outcome
# Or compute residuals directly:
cph.compute_residuals(df, kind='martingale')
```

### 4. Concordance and AIC for model comparison

```r
fit1$concordance['concordance']
AIC(fit1, fit2)
anova(fit_nested, fit_full)  # likelihood ratio test for nested models
```

```python
cph.concordance_index_
cph.AIC_partial_
# Nested model LRT:
from scipy.stats import chi2
lr = 2 * (cph_full.log_likelihood_ - cph_nested.log_likelihood_)
df_diff = len(cph_full.params_) - len(cph_nested.params_)
1 - chi2.cdf(lr, df_diff)
```

## Reporting checklist for any Cox model

- HR + 95% CI + p-value for each covariate.
- Number of subjects and number of events. The effective sample size for a Cox model is closer to the number of events than the number of subjects. Rule of thumb: ≥ 10 events per covariate.
- Time origin and time scale.
- Whether ties were handled by Efron or another method.
- Result of PH check (and what was done if violated).
- C-index (with CI from bootstrap if possible).
- Stratification variables, if any.
- For time-varying covariates: how exposure timing was defined.
