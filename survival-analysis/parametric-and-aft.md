# Parametric and flexible parametric models

Cox is semi-parametric: it leaves the baseline hazard unspecified. That's a strength (no distributional assumption) and a weakness (no smooth survival prediction, hard to extrapolate). Parametric models commit to a distributional form for the survival times; flexible parametric (Royston-Parmar) splines split the difference — they specify the baseline hazard via splines on the log cumulative hazard scale, giving you Cox-like flexibility plus everything Cox lacks.

## When to use parametric or flexible parametric instead of Cox

- **Extrapolation beyond observed follow-up** (health economic models, lifetime value calculations). Cox can't extrapolate past the last event time.
- **Smooth survival/hazard predictions** at any time, not just step functions.
- **Absolute survival predictions** (not just hazard ratios).
- **Interval censoring** (parametric likelihoods handle this naturally; Cox doesn't).
- **Small samples** with stable distributional assumptions.
- **You want to interpret accelerated time** rather than hazard ratios. An AFT coefficient of 1.5 means subjects in that group live ~1.5x longer on average — a more intuitive scale for some audiences than HRs.
- **Non-proportional hazards** where you don't want to escalate to time-varying coefficients.

When in doubt and you have moderate-to-large samples, **Royston-Parmar flexible parametric** is often the best of both worlds — it specifies enough structure to predict and extrapolate, but the splines absorb arbitrary baseline shapes that fixed parametric forms (Weibull, log-normal) can't match.

## Parametric distributions and what they imply

| Distribution | Hazard shape | When it fits |
|---|---|---|
| **Exponential** | Constant | Memoryless processes. Often too restrictive. |
| **Weibull** | Monotonic (increasing if shape > 1, decreasing if < 1) | Classic aging or "infant mortality." Equivalent to Cox with PH if you reparameterize. |
| **Gompertz** | Exponentially increasing | Human mortality at adult ages. Common in demography. |
| **Log-normal** | Inverted-U (humped) | Times-to-event with peak risk somewhere in the middle. |
| **Log-logistic** | Inverted-U (humped) | Like log-normal but heavier tails. PH does NOT hold; PO (proportional odds) does. |
| **Generalized gamma** | Very flexible (nests Weibull, log-normal, gamma) | Default flexible parametric choice when you're unsure. |
| **Generalized F** | Even more flexible (nests gen gamma) | When gen gamma still doesn't fit. |

Plot a kernel-smoothed hazard first (`muhaz` in R) to see the shape, then choose the family that matches. Or just fit several and compare AIC / inspect residuals.

## AFT (accelerated failure time) parameterization

AFT models work on log-time: $\log T = x^\top \beta + \sigma W$ where $W$ has a specified distribution (e.g., Gumbel gives Weibull, normal gives log-normal). Equivalent to: $S(t \mid x) = S_0(t / \exp(x^\top \beta))$. A coefficient of $\beta = 0.4$ means $\exp(0.4) \approx 1.5$, i.e., this group's "clock runs 50% slower" — they reach any survival probability at 1.5x the time.

**AFT vs PH interpretation**:
- PH (Cox): "Group A's instantaneous risk is 2x group B's at every moment."
- AFT (Weibull, log-normal, etc.): "Group A reaches any survival milestone in half the time of group B."

For audiences who think in terms of "median survival doubled," AFT is more direct. For "risk reduction," PH is more direct. **Weibull is the only common distribution that admits both PH and AFT parameterizations** — `flexsurvreg` with `dist = "weibull"` and `dist = "weibullPH"` give the same fit but different coefficients.

## R — flexsurv (recommended, supports both AFT and PH)

```r
library(flexsurv)

# AFT Weibull
fit_aft <- flexsurvreg(Surv(time, status) ~ age + sex, data = lung, dist = "weibull")
print(fit_aft)
# Coefficients on AFT scale: exp(coef) = time ratio.

# PH Weibull (different parameterization, same model)
fit_ph <- flexsurvreg(Surv(time, status) ~ age + sex, data = lung, dist = "weibullPH")
# Coefficients on PH scale: exp(coef) = HR.

# Other distributions
fit_ln  <- flexsurvreg(Surv(time, status) ~ age + sex, data = lung, dist = "lnorm")
fit_ll  <- flexsurvreg(Surv(time, status) ~ age + sex, data = lung, dist = "llogis")
fit_gg  <- flexsurvreg(Surv(time, status) ~ age + sex, data = lung, dist = "gengamma")
fit_gf  <- flexsurvreg(Surv(time, status) ~ age + sex, data = lung, dist = "genf")

# Compare by AIC
AIC(fit_aft, fit_ln, fit_ll, fit_gg, fit_gf)

# Predictions
summary(fit_gg, newdata = data.frame(age = 60, sex = 1), t = c(180, 365, 730))
# Plot fitted survival
plot(fit_gg, type = "survival")
plot(fit_gg, type = "hazard")  # smooth hazard from the model
```

### survreg (in survival package) — AFT only

```r
fit <- survreg(Surv(time, status) ~ age + sex, data = lung, dist = "weibull")
# Coefficients are AFT log-time-ratios. Convert to HR for Weibull:
# beta_PH = -beta_AFT / scale
```

Most people prefer `flexsurv` because it handles more distributions, gives cleaner output, and supports flexible parametric splines (next section).

## Python — lifelines parametric fitters

```python
from lifelines import (WeibullFitter, WeibullAFTFitter,
                      LogNormalFitter, LogNormalAFTFitter,
                      LogLogisticFitter, LogLogisticAFTFitter,
                      GeneralizedGammaFitter, GeneralizedGammaRegressionFitter)

# Single-population fit (just estimating the distribution, no covariates)
wf = WeibullFitter().fit(df['time'], df['event'])
wf.print_summary()
wf.median_survival_time_
wf.survival_function_at_times([180, 365])

# Regression: AFT
waft = WeibullAFTFitter()
waft.fit(df, duration_col='time', event_col='event',
         formula="age + sex + ph_ecog")
waft.print_summary()
# coefficients on AFT log-time-ratio scale; exp(coef) = time ratio

# Survival predictions
waft.predict_survival_function(df.iloc[:5])
waft.predict_median(df.iloc[:5])

# Generalized gamma regression (most flexible parametric)
ggreg = GeneralizedGammaRegressionFitter()
ggreg.fit(df, duration_col='time', event_col='event', formula="age + sex")
```

### lifelines covariates on multiple parameters

Useful trick: lifelines AFT fitters let you put covariates not just on the location parameter but on the scale/shape too, via the `ancillary` argument:

```python
waft = WeibullAFTFitter()
waft.fit(df, duration_col='time', event_col='event',
         formula="age + sex",
         ancillary="age")   # let Weibull shape depend on age too
```

This lets you fit non-PH effects within a parametric framework.

## Royston-Parmar flexible parametric models

Instead of specifying a parametric distribution, model the **log cumulative hazard** (or log cumulative odds, or normal-equivalent deviate) as a natural cubic spline of log time:

$\log H(t \mid x) = s(\log t; \gamma) + x^\top \beta$

The spline $s$ has user-chosen knots (typically 1–4 internal knots, plus boundary knots at the extremes of event times). This recovers:
- Cox-like flexibility for the baseline hazard.
- Smooth survival, hazard, and cumulative hazard estimates.
- Easy extrapolation (the spline can extend, though carefully).
- Easy handling of time-varying coefficients (replace $\beta$ with $\beta(t)$ as another spline).

### R — flexsurvspline

```r
library(flexsurv)

# 2 internal knots, log cumulative hazard scale (proportional hazards-ish)
fp_ph <- flexsurvspline(Surv(time, status) ~ age + sex, data = lung,
                        k = 2, scale = "hazard")
print(fp_ph)
# k = number of internal knots; scale = "hazard" (log H), "odds" (log H/(1-H)), or "normal"

# Compare different knot numbers by AIC
AIC(flexsurvspline(Surv(time, status) ~ age + sex, data = lung, k = 0, scale = "hazard"),
    flexsurvspline(Surv(time, status) ~ age + sex, data = lung, k = 1, scale = "hazard"),
    flexsurvspline(Surv(time, status) ~ age + sex, data = lung, k = 2, scale = "hazard"),
    flexsurvspline(Surv(time, status) ~ age + sex, data = lung, k = 3, scale = "hazard"))

# Time-varying coefficient for age:
fp_tv <- flexsurvspline(Surv(time, status) ~ age + sex + gamma1(age), data = lung,
                        k = 2, scale = "hazard")
# gamma1(age) means: let age's effect vary as a function of (the first spline basis of) log time.

# Plot
plot(fp_ph, type = "survival")
plot(fp_ph, type = "hazard")
plot(fp_ph, type = "cumhaz")

# Predictions
summary(fp_ph, newdata = data.frame(age = 60, sex = 1), t = c(180, 365, 730))
```

### R — rstpm2 (alternative implementation, often used in epidemiology)

```r
library(rstpm2)
fp <- stpm2(Surv(time, status) ~ age + sex, data = lung, df = 4)  # df = spline degrees of freedom
summary(fp)
predict(fp, newdata = data.frame(age = 60, sex = 1), type = "surv",
        grid = TRUE, full = TRUE, se.fit = TRUE)
```

`rstpm2` is more flexible for relative survival modeling, time-dependent effects, and Bayesian extensions. `flexsurv` is more consistent with `flexsurvreg`'s API.

### Python — no first-class equivalent

This is one of the genuine gaps: there's no clean Python implementation of Royston-Parmar splines as featured as `flexsurv` or `rstpm2`. Closest is:
- `lifelines` generalized gamma + custom spline features in `formula`. Doesn't give the same nicely separated baseline-spline + linear-effects structure.
- Fitting in R via `rpy2` or doing the analysis in R and reading results in.

If a user needs Royston-Parmar in Python, tell them this honestly and offer R or a parametric AFT as alternatives.

## Choosing knots for Royston-Parmar

- **k = 0** is equivalent to a Weibull (log H is linear in log t).
- **k = 1** allows one bend; often enough.
- **k = 2 or 3** is the typical applied choice.
- **k > 3** rarely needed; risks overfitting at the boundaries.

Place internal knots at evenly spaced quantiles of **uncensored event times** (this is the default in `flexsurv`). Manual knot placement is rarely worth the bother.

Royston and Parmar's original paper recommended choosing knots by AIC. In practice, sensitivity analysis with k = 1, 2, 3 and checking that conclusions don't change is more useful than optimizing AIC.

## Extrapolation caveat

Parametric and Royston-Parmar models *can* extrapolate beyond observed follow-up, but they don't *know* what's there — they're extending the assumed shape. Always:

1. Plot the fit overlaid on KM up to the end of observation, to verify good fit in-sample.
2. Extrapolate to multiple distributions (Weibull, log-normal, gen gamma) and show the range. If they diverge wildly past the end of follow-up, that's the actual uncertainty.
3. Sanity-check with external data (life tables for human mortality; engineering specs for reliability).

Health economic models routinely report a "fan plot" of extrapolations from several distributions. Don't trust a single parametric extrapolation as if it were ground truth.

## Reporting checklist for parametric models

- Distribution chosen and why (AIC table, hazard shape inspection, prior reasoning).
- Coefficients in AFT or PH form (state which) with 95% CI.
- For Royston-Parmar: number of knots, knot locations, scale (hazard/odds/normal).
- Predicted survival at clinically meaningful timepoints with CI.
- Fitted curve overlaid on KM as a sanity check.
- If extrapolating: range of extrapolations across distributions.
