# Special censoring: left, interval, and left-truncation

Right censoring (subject still event-free at last observation) is what standard methods handle by default. Three other patterns require different handling, and conflating them produces silent errors.

## Quick definitions

- **Right censoring**: we know T > c. "Subject was still event-free at time c." Default in `Surv()`.
- **Left censoring**: we know T < c. "Event happened before c, we don't know exactly when."
- **Interval censoring**: we know c₁ < T < c₂. "Event happened sometime between two observation times."
- **Left truncation (delayed entry)**: subject was not in the risk set until time τ. "We couldn't have observed them earlier even if the event had occurred."

The crucial conceptual distinction: **censoring** is about not observing the exact event time despite the subject being in the risk set; **truncation** is about the subject not being in the risk set at all until some later time. These need different methods.

## Left censoring

You observe the subject at time c, and they have already had the event. You don't know when between time 0 and c it happened.

**Examples**:
- HIV infection: at first test, subject is already positive. We know seroconversion happened before the test.
- Age at first menstruation, asked retrospectively in a survey, where many participants don't remember exactly.
- A defect is detected at first inspection — could have occurred any time before.

### Likelihood

For a left-censored observation, the contribution to the likelihood is F(c) = P(T ≤ c), instead of f(t) for an exact observation or S(c) for a right censoring.

### R — Surv with type = "left"

```r
library(survival)

# event = 1 if exactly observed, event = 0 if left censored
# (NOTE: type = "left" reverses the usual interpretation)
sv <- Surv(time, event, type = "left")
fit <- survfit(sv ~ 1, data = df)
plot(fit)
```

For more complex situations, use the interval-censoring framework below and represent left-censored points as having L = 0.

### Python (lifelines)

```python
from lifelines import KaplanMeierFitter, WeibullFitter

kmf = KaplanMeierFitter()
kmf.fit_left_censoring(df['time'], event_observed=df['event'])

# Parametric:
wf = WeibullFitter()
wf.fit_left_censoring(df['time'], df['event'])
```

`lifelines` parametric fitters support `fit_left_censoring`, `fit_interval_censoring`, and the standard `fit` (right censoring). Use the right one for your data structure.

## Interval censoring

You only know the event happened between two observation times. This is the natural form of data from any study with periodic check-ups: doctor visits, equipment inspections, app analytics windows.

**Examples**:
- HIV seroconversion: tested negative at visit k, positive at visit k+1. We know T ∈ (t_k, t_{k+1}).
- Time to a tumor reaching detectable size: imaging at scheduled intervals.
- Time to a user clicking a particular feature: log aggregated daily, so time is in [day, day+1).

The naive approach — using the midpoint or right endpoint as if it were the exact event time — is **biased**, sometimes badly. The size of the bias depends on interval width relative to typical event times. Wide intervals = big bias. Use proper interval-censored methods.

### R — icenReg

```r
library(icenReg)

# Data format: L = lower bound, R = upper bound of the interval containing the event.
# Right-censored: R = Inf
# Left-censored: L = 0
# Exact: L = R (or use a tiny interval around the exact time)

# Non-parametric NPMLE (Turnbull-style)
fit_np <- ic_np(cbind(L, R) ~ group, data = df)
plot(fit_np)

# Parametric (Weibull, log-normal, log-logistic, gamma, exponential, generalized gamma)
fit_par <- ic_par(cbind(L, R) ~ age + sex, data = df, model = "ph", dist = "weibull")
summary(fit_par)
# model: "ph" = proportional hazards, "po" = proportional odds, "aft" = accelerated failure time

# Semi-parametric (preferred for inference under interval censoring)
fit_sp <- ic_sp(cbind(L, R) ~ age + sex, data = df, model = "ph", bs_samples = 100)
summary(fit_sp)
# bs_samples = bootstrap iterations for SE; can take a while.
```

### R — interval package (group comparison)

```r
library(interval)

# Generalized log-rank for interval-censored data (Sun's test)
ictest(L, R, group, data = df, rho = 0)              # log-rank style
ictest(L, R, group, data = df, scores = "wmw")        # Wilcoxon-Mann-Whitney style

# Turnbull's NPMLE
fit <- icfit(L, R, data = df)
plot(fit)
```

### Python (lifelines)

```python
from lifelines import WeibullFitter, LogNormalFitter, ExponentialFitter

# Data: lower_bound and upper_bound columns
wf = WeibullFitter()
wf.fit_interval_censoring(lower_bound=df['L'], upper_bound=df['R'])
wf.print_summary()

# Regression: parametric fitters support interval censoring via fit_interval_censoring
from lifelines import WeibullAFTFitter
waft = WeibullAFTFitter()
waft.fit_interval_censoring(df, lower_bound_col='L', upper_bound_col='R',
                            formula='age + sex')
```

For **non-parametric** or **semi-parametric** interval-censored regression, R (`icenReg`) is significantly better than Python.

### Practical handling

- For each subject, determine L and R based on the observation schedule.
- For events observed in the first interval: L = 0 (left-censored).
- For subjects still event-free at end of follow-up: R = Inf (right-censored).
- For events with exact times: set L = R (or L = t, R = t + ε for numerical stability).

## Left truncation (delayed entry)

The subject was not under observation — couldn't have been observed even if they had the event — until time τ. They entered the risk set at τ and must therefore be conditioned on having survived to τ.

**Examples**:
- **Age as the time scale**: a subject enters a cohort at age 50. They were not observable for events at ages 0-49. Specify entry age explicitly.
- **Prevalent cohorts**: a study recruits subjects who already have a disease. They've survived from disease onset to recruitment — they couldn't have been recruited if they had died earlier.
- **Insurance / financial**: data captured starting at policy issue date; subjects with prior events never enter the dataset.

If you ignore left truncation and treat entry time as the origin, you bias your hazard estimates because you're attributing all the early-life "survival" to a population that was already selected for having survived that period.

### The fix: specify both entry and exit times

```r
# R
fit <- coxph(Surv(entry, exit, event) ~ age + sex, data = df)
# entry = time subject enters risk set; exit = time of event or censoring.
```

The `Surv(start, stop, event)` form uses **time intervals**, with the subject contributing to the risk set only during (entry, exit].

### Age-as-time-scale example

A common situation: you want to model mortality with age as the time scale rather than time-on-study. Each subject enters the study at some calendar date, when they have a specific age. They exit at death or end of follow-up.

```r
# Right way: time scale is age, entry = age at study start, exit = age at death/censoring
fit_age <- coxph(Surv(age_entry, age_exit, death) ~ sex + smoking + bmi, data = df)
# Subjects at age 65 are "at risk" only if their age_entry ≤ 65 ≤ age_exit.

# Wrong way: ignoring truncation
fit_wrong <- coxph(Surv(age_exit, death) ~ sex + smoking + bmi, data = df)
# Implicitly assumes everyone is at risk from age 0, which is false.
```

When in doubt: if you're using age (or calendar time) as the time scale and subjects enter the study at varying ages, you need `Surv(entry, exit, event)`.

### Python (lifelines)

```python
# Cox with left truncation (entry/exit form)
from lifelines import CoxTimeVaryingFitter

# Reshape to start/stop format
ctv = CoxTimeVaryingFitter()
ctv.fit(df, id_col='id', event_col='event',
        start_col='age_entry', stop_col='age_exit',
        formula='sex + smoking + bmi')
```

For KM with left truncation:

```python
from lifelines import KaplanMeierFitter
kmf = KaplanMeierFitter()
kmf.fit(durations=df['age_exit'], event_observed=df['event'],
        entry=df['age_entry'])  # 'entry' specifies left truncation times
```

### Verifying truncation handling

After fitting, a quick sanity check: predicted survival at the youngest entry age should be 1, and the curve should descend from there. If your fit gives "S(age 50) = 0.6" when nobody in your data was at risk at age 50, something is wrong.

## Mixing censoring and truncation

You can have all of these at once. A clinical trial might have:
- Subjects entering at varying ages (left truncation on age scale).
- Some events known exactly (death certificates with date).
- Some events known only by interval (last clinic visit was event-free, next one had the event).
- Some subjects right-censored at end of follow-up.

For complex mixes, parametric likelihood-based methods are cleanest because the likelihood factorizes naturally: each observation contributes $f(t)$ (exact), $S(c)$ (right-censored), $F(c)$ (left-censored), or $F(c_2) - F(c_1)$ (interval-censored), divided by $S(\tau)$ if left-truncated at $\tau$.

`flexsurv` (R), `icenReg` (R), and lifelines parametric fitters all handle these mixes when set up correctly. Non-parametric handling of complex mixes (left + interval + truncation) is mostly an R world (`interval`, `icenReg`).

## Common errors

1. **Treating interval-censored data as exact**: using the midpoint or right endpoint as if it were the event time. Biases estimates, especially with wide intervals.
2. **Confusing left truncation with left censoring**: very different problems. Truncation = subject wasn't in the data at all until later; left censoring = subject was observable but we only know they had the event "before time c."
3. **Using time-on-study as the scale when age is the more natural scale**: not wrong per se, but interpretation differs and ignoring age effects via covariates can leave residual confounding. Using age scale with proper truncation is often cleaner.
4. **Prevalent cohort without truncation handling**: recruiting subjects who already have the condition without specifying the time of onset as the entry into the risk set produces severely biased survival estimates.
5. **Length-biased sampling**: a special case of left truncation where subjects with longer event times are over-represented (because they're more likely to be alive at recruitment time). Requires specialized methods if not corrected via the entry-time approach.

## Reporting checklist

- The exact censoring pattern present in the data (counts of each type).
- For interval censoring: typical and maximum interval widths.
- For left truncation: the proportion of follow-up time vs total subject-time-at-risk that's actually used in the analysis.
- The time scale chosen (study time vs age vs calendar time) and why.
- For age scale: confirmation that left truncation was modeled.
