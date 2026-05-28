# R recipes for survival analysis

A consolidated quick-reference of R packages and patterns. For deep coverage of any method, see the topic-specific reference files (`estimators.md`, `cox-and-extensions.md`, etc.). This file is the "what package, what function, what argument" lookup.

## Package landscape

| Package | What it's for | Notes |
|---|---|---|
| **survival** | The foundation: `Surv`, `survfit`, `coxph`, `survdiff`, `cox.zph`, `survreg` | Always loaded. Terry Therneau's package. |
| **survminer** | `ggsurvplot`, `ggcoxdiagnostics`, publication-ready plots | The standard for figures. |
| **flexsurv** | Parametric AFT, Royston-Parmar splines, hazard/survival predictions | More distributions and easier API than `survreg`. |
| **rstpm2** | Royston-Parmar alternative; also for relative survival | Used heavily in epidemiology. |
| **cmprsk** | Fine-Gray subdistribution, Gray's test, CIFs | Original implementation. |
| **mstate** | Multi-state modeling, transition probabilities | Standard for multi-state. |
| **msm** | Markov multi-state for panel data | When observations are at discrete time points. |
| **coxme** | Mixed-effects Cox (random intercepts/slopes) | Successor to `survival::frailty()`. |
| **frailtypack** | Frailty, nested frailty, joint frailty (recurrent + terminal) | The advanced frailty toolbox. |
| **icenReg** | Interval-censored regression (parametric, semi-parametric, NP) | Best-in-class. |
| **interval** | Generalized log-rank for interval-censored data | Sun's test, etc. |
| **survRM2** | RMST estimation and comparison | Clean implementation. |
| **nph**, **nphRCT** | Weighted log-rank, MaxCombo for non-PH | Becoming standard for non-PH trials. |
| **reReg** | Recurrent events incl. terminal events, LWYY model | |
| **randomForestSRC** | Random survival forests | |
| **glmnet** | Penalized Cox (lasso, ridge, elastic net) | `family = "cox"`. |
| **rms** | Frank Harrell's regression modeling strategies | `cph()`, `rcs()`, calibration plots. |
| **broom** | `tidy()`, `glance()`, `augment()` for survival models | Tidyverse-friendly output. |
| **finalfit** | Quick descriptive + Cox tables for clinical reports | Convenient for publication. |
| **tidymodels / censored** | Tidy-style survival modeling | Newer; growing capability. |

## Data setup patterns

### Basic Surv object

```r
library(survival)

# Right-censored
sv <- Surv(time = df$time, event = df$status)

# Left-censored (event = 0 means left censored, 1 means exact)
sv <- Surv(time = df$time, event = df$status, type = "left")

# Interval-censored
sv <- Surv(time = df$lower, time2 = df$upper, type = "interval2")
# type = "interval2": Inf in time2 means right-censored, NA in time means left-censored

# Counting process (time-varying covariates, recurrent events, left truncation)
sv <- Surv(time = df$tstart, time2 = df$tstop, event = df$event)

# Competing risks (multi-state)
sv <- Surv(time = df$time, event = factor(df$status, levels = c(0, 1, 2),
                                          labels = c("censored", "cause1", "cause2")))
```

### Counting process restructuring (tmerge)

```r
# Start with baseline data
base <- df[, c("id", "age", "sex")]
base$tstart <- 0
base$tstop  <- df$followup_time

# Initialize with endpoint
new <- tmerge(base, df, id = id, endpoint = event(followup_time, status))

# Add a time-varying covariate from a separate change-table
# change_table has columns: id, change_time, new_value
new <- tmerge(new, change_table, id = id, treatment = tdc(change_time, new_value))

# Add a count of prior events (e.g., for PWP)
new <- tmerge(new, event_table, id = id, n_prior = cumevent(event_time))
```

## Descriptive

```r
library(survival)
library(survminer)

# KM curves with risk table
fit <- survfit(Surv(time, status) ~ group, data = df)
ggsurvplot(fit, data = df,
           risk.table = TRUE,
           pval = TRUE,
           conf.int = TRUE,
           censor = TRUE,
           surv.median.line = "hv",
           palette = "lancet",
           ggtheme = theme_minimal())

# Summary of survival at fixed times
summary(fit, times = c(180, 365, 730))

# Median survival
print(fit)  # last column is median with CI; "NA" if not reached

# Aalen-Johansen CIF for competing risks
df$status_f <- factor(df$status, levels = c(0, 1, 2),
                      labels = c("cens", "cause1", "cause2"))
aj <- survfit(Surv(time, status_f) ~ group, data = df)
plot(aj, col = 1:4)
```

## Group comparisons

```r
# Standard log-rank
survdiff(Surv(time, status) ~ group, data = df)

# Weighted log-rank (rho parameter for FH(rho, 0) family)
survdiff(Surv(time, status) ~ group, data = df, rho = 1)  # Peto-Peto

# Full Fleming-Harrington
library(FHtest)
FHtestrcc(Surv(time, status) ~ group, data = df, rho = 0, lambda = 1)

# MaxCombo
library(nph)
logrank.maxtest(time = df$time, event = df$status, group = df$group,
                rho = c(0, 0, 1, 1), gamma = c(0, 1, 0, 1))

# Stratified log-rank
survdiff(Surv(time, status) ~ group + strata(institution), data = df)

# Gray's test for competing risks
library(cmprsk)
ci <- cuminc(ftime = df$time, fstatus = df$status, group = df$group, cencode = 0)
ci$Tests

# Generalized log-rank for interval-censored
library(interval)
ictest(L = df$L, R = df$R, group = df$group)

# RMST difference
library(survRM2)
rmst2(time = df$time, status = df$status, arm = df$group, tau = 365)
```

## Cox and extensions

```r
# Basic Cox
fit <- coxph(Surv(time, status) ~ age + sex + factor(treatment), data = df,
             ties = "efron")
summary(fit)
broom::tidy(fit, exponentiate = TRUE, conf.int = TRUE)

# Stratified Cox
fit_s <- coxph(Surv(time, status) ~ age + sex + strata(institution), data = df)

# Time-varying covariate (data in counting-process form)
fit_tv <- coxph(Surv(tstart, tstop, event) ~ treatment + age, data = long_df)

# Time-varying coefficient via tt()
fit_tt <- coxph(Surv(time, status) ~ age + tt(age) + sex, data = df,
                tt = function(x, t, ...) x * log(t))

# Splines for non-linear continuous effects
fit_ps <- coxph(Surv(time, status) ~ pspline(age, df = 4) + sex, data = df)
termplot(fit_ps, se = TRUE)

# Or with rms package
library(rms)
dd <- datadist(df); options(datadist = "dd")
fit_rcs <- cph(Surv(time, status) ~ rcs(age, 4) + sex, data = df,
               x = TRUE, y = TRUE, surv = TRUE)

# Penalized Cox
library(glmnet)
X <- model.matrix(~ . - 1, data = df[predictors])
y <- Surv(df$time, df$status)
cv_fit <- cv.glmnet(X, y, family = "cox", alpha = 0.9)
coef(cv_fit, s = "lambda.1se")

# Random survival forest
library(randomForestSRC)
rsf <- rfsrc(Surv(time, status) ~ ., data = df, ntree = 500, importance = TRUE)
```

## Cox diagnostics

```r
# Proportional hazards test (Grambsch-Therneau)
zph <- cox.zph(fit)
print(zph)
plot(zph)  # one panel per covariate; flat line = PH

# Or via survminer for ggplot output
ggcoxzph(zph)

# Influence (dfbeta)
ggcoxdiagnostics(fit, type = "dfbeta", linear.predictions = FALSE)

# Functional form (martingale residuals)
ggcoxfunctional(Surv(time, status) ~ age + log(age) + sqrt(age), data = df)
```

## Parametric and flexible parametric

```r
library(flexsurv)

# AFT Weibull
fit_aft <- flexsurvreg(Surv(time, status) ~ age + sex, data = df, dist = "weibull")

# PH Weibull (same model, different parameterization)
fit_ph <- flexsurvreg(Surv(time, status) ~ age + sex, data = df, dist = "weibullPH")

# Other distributions
fit_ln <- flexsurvreg(Surv(time, status) ~ age + sex, data = df, dist = "lnorm")
fit_gg <- flexsurvreg(Surv(time, status) ~ age + sex, data = df, dist = "gengamma")

# Compare by AIC
AIC(fit_aft, fit_ln, fit_gg)

# Royston-Parmar flexible parametric splines (k internal knots)
fp <- flexsurvspline(Surv(time, status) ~ age + sex, data = df, k = 2, scale = "hazard")
plot(fp, type = "survival")
plot(fp, type = "hazard")

# Time-varying coefficient via gamma1()
fp_tv <- flexsurvspline(Surv(time, status) ~ age + sex + gamma1(age),
                        data = df, k = 2, scale = "hazard")

# Predictions
summary(fp, newdata = data.frame(age = 60, sex = 1), t = c(180, 365, 730))
```

## Competing risks

```r
# CIFs (Aalen-Johansen)
df$status_f <- factor(df$status, levels = c(0, 1, 2),
                      labels = c("cens", "cause1", "cause2"))
aj <- survfit(Surv(time, status_f) ~ group, data = df)
plot(aj)

# Cause-specific Cox (single call, multi-state form)
fit_cs <- coxph(Surv(time, status_f) ~ age + sex + treatment, data = df, id = id)
print(fit_cs)

# Fine-Gray subdistribution
library(cmprsk)
cov <- model.matrix(~ age + sex + treatment, data = df)[, -1]
fg1 <- crr(ftime = df$time, fstatus = df$status, cov1 = cov, failcode = 1, cencode = 0)
summary(fg1)

# Fine-Gray via survival package
fg_data <- finegray(Surv(time, status_f) ~ ., data = df, etype = "cause1")
fit_fg <- coxph(Surv(fgstart, fgstop, fgstatus) ~ age + sex + treatment,
                weights = fgwt, data = fg_data)

# Gray's test
library(cmprsk)
ci <- cuminc(ftime = df$time, fstatus = df$status, group = df$treatment, cencode = 0)
ci$Tests
```

## Recurrent events

```r
# Andersen-Gill
fit_ag <- coxph(Surv(tstart, tstop, event) ~ treatment + age + cluster(id),
                data = recurrent_df)

# PWP Total Time (stratified by event number)
fit_pwp_tt <- coxph(Surv(tstart, tstop, event) ~ treatment + age +
                    strata(enum) + cluster(id), data = recurrent_df)

# PWP Gap Time
recurrent_df$gap <- recurrent_df$tstop - recurrent_df$tstart
fit_pwp_gt <- coxph(Surv(rep(0, nrow(recurrent_df)), gap, event) ~ treatment + age +
                    strata(enum) + cluster(id), data = recurrent_df)

# Mean cumulative function for description
mcf <- survfit(Surv(tstart, tstop, event) ~ treatment, data = recurrent_df, id = id)
plot(mcf, cumhaz = TRUE)

# LWYY robust version
library(reReg)
fit_lwyy <- reReg(Recur(tstop, id, event) ~ treatment + age, data = recurrent_df,
                  model = "cox.LWYY")
```

## Multi-state

```r
library(mstate)

# Define transition matrix (e.g., illness-death)
tmat <- transMat(x = list(c(2, 3), c(3), c()),
                 names = c("Healthy", "Ill", "Dead"))

# Reshape
df_long <- msprep(time = c(NA, "t_ill", "t_death"),
                  status = c(NA, "ill", "death"),
                  data = df, trans = tmat, keep = c("age", "sex"))

# Fit transition-specific Cox
df_long <- expand.covs(df_long, c("age", "sex"))
fit_ms <- coxph(Surv(Tstart, Tstop, status) ~ age.1 + age.2 + age.3 +
                strata(trans), data = df_long)

# Predict transition probabilities
msf <- msfit(fit_ms, newdata = newdata_long, trans = tmat)
pt  <- probtrans(msf, predt = 0)
plot(pt)
```

## Frailty and joint models

```r
# Shared frailty via coxme (preferred over survival::frailty())
library(coxme)
fit_me <- coxme(Surv(time, status) ~ age + sex + (1 | hospital), data = df)

# Joint frailty (recurrent + terminal)
library(frailtypack)
fit_jf <- frailtyPenal(Surv(tstart, tstop, recurrent_event) ~ cluster(id) +
                       treatment + terminal(death),
                       formula.terminalEvent = ~ treatment + age,
                       data = df, recurrentAG = TRUE,
                       n.knots = 8, kappa = c(1e7, 1e7))
summary(fit_jf)
```

## Interval and left censoring

```r
library(icenReg)

# Non-parametric (Turnbull-like) NPMLE
fit_np <- ic_np(cbind(L, R) ~ group, data = df)

# Parametric with model = "ph", "po", "aft"
fit_par <- ic_par(cbind(L, R) ~ age + sex, data = df, model = "ph", dist = "weibull")

# Semi-parametric Cox-like
fit_sp <- ic_sp(cbind(L, R) ~ age + sex, data = df, model = "ph", bs_samples = 100)
```

## Tidymodels approach (newer)

```r
library(tidymodels)
library(censored)

spec <- proportional_hazards() %>%
  set_engine("survival") %>%
  set_mode("censored regression")

fit <- spec %>% fit(Surv(time, status) ~ age + sex, data = df_train)

# Predictions
predict(fit, new_data = df_test, type = "time")           # predicted event time
predict(fit, new_data = df_test, type = "survival",       # survival probability at times
        eval_time = c(180, 365, 730))

# Cross-validation
folds <- vfold_cv(df_train, v = 5, strata = status)
# ... fit_resamples + survival metrics from yardstick
```

## Useful broom / finalfit helpers

```r
library(broom)
tidy(fit, exponentiate = TRUE, conf.int = TRUE)
glance(fit)

library(finalfit)
df %>% finalfit("Surv(time, status)", c("age", "sex", "treatment"))
# Produces a publication-style table with HR, CI, p-value.
```
