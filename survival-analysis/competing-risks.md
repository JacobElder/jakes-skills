# Competing risks

A competing risk is an event that **precludes** the event of interest. The canonical biomedical example: if you're studying time to cardiovascular death, death from cancer is a competing risk — once a subject dies of cancer, they can no longer die of cardiovascular causes. In product contexts: if you're modeling time to paid conversion of a free trial, churning out of the trial is a competing risk for converting.

Naively treating competing events as censoring is one of the most consistently made errors in applied survival analysis. It produces **biased** estimates of both the cumulative incidence and (usually) the covariate effects.

## The fundamental issue

Standard Kaplan-Meier treats censored subjects as "still at risk but unobserved." For random censoring (lost to follow-up), that's fine — those subjects might still have the event later, we just can't see it. For competing events, it's not fine — those subjects **cannot** have the event of interest anymore. Treating them as still at risk overestimates how many will eventually have your event of interest.

Concretely: $1 - \text{KM}(t)$ with the competing event coded as censoring **overestimates** the cumulative incidence of the event of interest. The correct estimator is the **cumulative incidence function (CIF)** from Aalen-Johansen.

## Two questions, two model families

The choice depends on what you're trying to learn:

| Question | Model | What it estimates |
|---|---|---|
| "What causes the event?" (etiology) | **Cause-specific Cox** | Effect of covariates on the rate of the event among those still at risk for it |
| "Who will have the event?" (absolute risk prediction) | **Fine-Gray subdistribution** | Effect of covariates on the cumulative incidence over time |

You can — and often should — fit **both** and report side by side. They answer different questions and a covariate can have opposite effects on the two scales. Classic example: a treatment that strongly reduces cancer mortality but has no effect on other-cause mortality can show:
- **Cause-specific HR for cancer death**: 0.5 (treatment cuts the cancer mortality rate in half).
- **Fine-Gray subdistribution HR for cancer death**: 0.7 (treatment cuts cancer cumulative incidence, but less dramatically because more treated patients live long enough to die of other causes — which then *count against* the cumulative incidence of cancer death in the subdistribution framework).

Both numbers are correct; they describe different things.

## Cause-specific hazards approach

For each cause k, the cause-specific hazard is:

$h_k(t) = \lim_{\Delta t \to 0} P(t \le T < t + \Delta t, D = k \mid T \ge t) / \Delta t$

This is the rate of cause-k events among subjects who haven't yet had **any** event. You can fit a separate Cox model for each cause, treating events from other causes as censoring **for the purpose of estimating cause-specific hazards** (this is correct here — we're estimating a rate, not a cumulative risk).

### R
```r
library(survival)

# Cause-specific Cox for cause 1
df$event_cause1 <- as.integer(df$status == 1)
fit_cs1 <- coxph(Surv(time, event_cause1) ~ age + sex + treatment, data = df)
summary(fit_cs1)

# Cause-specific Cox for cause 2
df$event_cause2 <- as.integer(df$status == 2)
fit_cs2 <- coxph(Surv(time, event_cause2) ~ age + sex + treatment, data = df)

# More elegant: multi-state Surv() in survival >= 3.0
df$status_f <- factor(df$status, levels = c(0, 1, 2),
                      labels = c("censored", "cause1", "cause2"))
fit_ms <- coxph(Surv(time, status_f) ~ age + sex + treatment, data = df, id = id)
# This fits both cause-specific transitions in one call; print() shows both.
```

### Python
```python
# lifelines: fit a CoxPHFitter per cause
from lifelines import CoxPHFitter

df['cause1_event'] = (df['status'] == 1).astype(int)
cph1 = CoxPHFitter().fit(df, duration_col='time', event_col='cause1_event',
                          formula='age + sex + treatment')

df['cause2_event'] = (df['status'] == 2).astype(int)
cph2 = CoxPHFitter().fit(df, duration_col='time', event_col='cause2_event',
                          formula='age + sex + treatment')

# scikit-survival: same idea, fit separately per cause
```

### Interpretation

A cause-specific HR of 1.5 for treatment on cause 1 means: "among subjects still at risk for any event, the rate of cause-1 events is 1.5x higher in the treated group." It does **not** mean "cause-1 cumulative incidence is 1.5x higher" — that's a Fine-Gray question.

## Fine-Gray subdistribution hazards

Fine-Gray works on a different quantity: the **subdistribution hazard**, which keeps subjects who have had a competing event in the risk set forever (with weights). This makes the model directly map onto the CIF: regression coefficients describe effects on the cumulative incidence of the event of interest.

$h^{sub}_k(t) = \lim_{\Delta t \to 0} P(t \le T < t + \Delta t, D = k \mid T \ge t \text{ or } (T \le t \text{ and } D \ne k)) / \Delta t$

The interpretation isn't as clean as cause-specific hazards (the risk set includes "people who already had the competing event," which is conceptually weird), but the practical value is that a Fine-Gray HR > 1 implies a higher cumulative incidence of the event of interest — directly answering the question "is the absolute risk of cause k higher in this group?"

### R — cmprsk
```r
library(cmprsk)

# Fine-Gray for cause 1
cov <- model.matrix(~ age + sex + treatment, data = df)[, -1]  # drop intercept
fg1 <- crr(ftime = df$time, fstatus = df$status, cov1 = cov,
           failcode = 1, cencode = 0)
summary(fg1)
# Reports subdistribution HRs with 95% CIs.

# For cause 2
fg2 <- crr(ftime = df$time, fstatus = df$status, cov1 = cov,
           failcode = 2, cencode = 0)
```

### R — survival package (cleaner syntax)
```r
library(survival)

# Construct weights and fit via coxph
fg_data <- finegray(Surv(time, status_f) ~ ., data = df, etype = "cause1")
fit_fg <- coxph(Surv(fgstart, fgstop, fgstatus) ~ age + sex + treatment,
                weights = fgwt, data = fg_data)
summary(fit_fg)  # subdistribution HRs
```

### Python — lifelines doesn't have native Fine-Gray

Practical options:
- **scikit-survival** doesn't have Fine-Gray either.
- The `lifelines-fork` / community packages occasionally implement it; check current state before relying on them.
- For serious competing risks work, R is significantly better supported.
- Workaround: fit cause-specific Cox in Python (since that's well-supported), report those, and if you need Fine-Gray, call R from Python via `rpy2`.

## Cumulative incidence functions (CIFs)

The CIF for cause k is:

$F_k(t) = P(T \le t, D = k)$

Estimated non-parametrically by Aalen-Johansen, or model-predicted from either cause-specific Cox (combining all cause-specific hazards) or Fine-Gray (directly).

### R — non-parametric CIFs
```r
library(survival)
library(cmprsk)

# Aalen-Johansen via survfit with factor status
aj <- survfit(Surv(time, status_f) ~ 1, data = df)
plot(aj, col = c("blue", "red"), xlab = "Time", ylab = "Cumulative incidence")

# By group
aj_g <- survfit(Surv(time, status_f) ~ treatment, data = df)
plot(aj_g, col = 1:4)

# Via cmprsk (with Gray's test included)
ci <- cuminc(ftime = df$time, fstatus = df$status, group = df$treatment, cencode = 0)
plot(ci, col = 1:4, lty = 1:2)
ci$Tests   # Gray's test p-values per cause
```

### R — CIFs from model predictions
```r
# From cause-specific Cox: predict from each cause-specific model, then combine
# Done via survival::survfit on the multi-state coxph
sf_ms <- survfit(fit_ms, newdata = data.frame(age = 60, sex = 1, treatment = 1))
plot(sf_ms)  # Shows CIFs for each cause from cause-specific Cox

# From Fine-Gray
predict(fg1, cov1 = matrix(c(60, 1, 1), nrow = 1))  # CIF for cause 1
```

### Python — Aalen-Johansen
```python
from lifelines import AalenJohansenFitter

# CIF for cause 1
ajf1 = AalenJohansenFitter(calculate_variance=True)
ajf1.fit(df['time'], event_observed=df['status'], event_of_interest=1)
ajf1.cumulative_density_   # CIF for cause 1
ajf1.plot()

# CIF for cause 2
ajf2 = AalenJohansenFitter()
ajf2.fit(df['time'], event_observed=df['status'], event_of_interest=2)
```

## Gray's test

The log-rank test compares **hazards**. For competing risks, you want to compare **CIFs** — and that's not the same thing. Gray's test is to CIFs what log-rank is to KM curves: a non-parametric two-sample test for whether two cumulative incidence functions differ.

### R
```r
library(cmprsk)
ci <- cuminc(ftime = df$time, fstatus = df$status, group = df$treatment, cencode = 0)
print(ci$Tests)
# A matrix with one row per event type, columns: stat, pv (p-value), df
```

Use Gray's test, not log-rank, when comparing groups in the presence of competing risks. The log-rank test compares cause-specific hazards, which can be similar even when CIFs differ substantially (because subjects in one group might die of competing causes faster, leaving fewer at risk for the event of interest, which compresses the cumulative incidence even if rate-per-time-at-risk is identical).

### Python

Not natively in lifelines or scikit-survival. Most reliable option is R via rpy2, or implementing the test manually following Gray's 1988 paper. For applied work involving competing-risks group comparisons, do this in R.

## How to choose: cause-specific vs Fine-Gray

A decision rule that works in most cases:

- **Etiology / causal questions about the mechanism**: use **cause-specific Cox** for each cause. "Does this risk factor accelerate the disease process?" → cause-specific.
- **Risk prediction for the individual** ("what's this patient's 5-year probability of cause-1 event?"): use **Fine-Gray** or **predict CIFs from cause-specific models combined**.
- **Trial primary endpoint comparing groups**: typically **CIFs + Gray's test** for the test, and Fine-Gray for the effect estimate. Some guidelines now recommend reporting both cause-specific and subdistribution HRs to give a complete picture.

When in doubt, fit both and report side by side. Discrepancies between them are informative, not embarrassing — they reveal that the competing events are also affected by the covariate.

## Common errors

1. **Using 1 − KM for cumulative incidence with competing risks.** Overestimates. Use Aalen-Johansen CIF.
2. **Using log-rank to compare groups with competing risks.** Tests cause-specific hazards, not what's usually wanted. Use Gray's test for CIFs.
3. **Reporting only one of cause-specific or Fine-Gray.** They answer different questions; pick deliberately or report both.
4. **Interpreting Fine-Gray HR as a hazard ratio in the usual sense.** It's a subdistribution hazard ratio; the risk set is weird (includes people who already had a competing event). Stick to "Fine-Gray HR for cumulative incidence" language.
5. **Censoring competing events when fitting Fine-Gray.** Fine-Gray *needs* the competing events labeled correctly; you don't censor them, the method handles them via weights.
6. **Forgetting that "any event" composite endpoints sidestep but don't solve competing risks.** "Time to any of {cause 1, cause 2}" is a valid composite, but it's a different question than "time to cause 1." Pick what you actually mean.

## Reporting checklist

- Number of subjects, number of events per cause, number censored.
- CIFs plotted (Aalen-Johansen) — not 1 − KM.
- Cause-specific HRs and/or Fine-Gray subdistribution HRs, clearly labeled, with 95% CIs.
- Gray's test (not log-rank) p-values when comparing groups.
- Time at which any cumulative-incidence claim is made (e.g., "5-year CIF in treatment arm was 18% (95% CI 14%–22%)").
- Brief note on whether cause-specific and Fine-Gray results agree, and if not, what that implies about effects on competing events.
