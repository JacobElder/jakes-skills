# Non-parametric estimators

Choose the right estimator for the right quantity. These look interchangeable but answer different questions, and mixing them up produces silent errors.

## Quick reference

| Estimator | Estimates | When to use | What it can't handle |
|---|---|---|---|
| **Kaplan-Meier (KM)** | S(t) | Right-censored, single event, independent censoring | Competing risks, interval censoring |
| **Nelson-Aalen (NA)** | H(t) (cumulative hazard) | Same conditions as KM; preferred for hazard-based inference | Same limits as KM |
| **Aalen-Johansen (AJ)** | CIF for each cause, transition probabilities | Competing risks, multi-state | Interval censoring |
| **Turnbull** | S(t) under interval/general censoring | Interval-censored, left-censored, or mixed | Slow on large data |
| **Kernel hazard smoothers** | h(t) (the actual hazard function) | When you want to see the hazard shape (not just cumulative) | Bandwidth choice is hard |

## Kaplan-Meier — S(t) for right-censored data

The product-limit estimator. At each event time t_j: $S(t_j) = S(t_{j-1}) \cdot (1 - d_j / n_j)$ where $d_j$ is events at $t_j$ and $n_j$ is the number at risk just before $t_j$. Censored observations stay in the risk set until their censoring time, then drop out without changing the curve.

### R
```r
library(survival)
library(survminer)

# Single curve
fit <- survfit(Surv(time, status) ~ 1, data = lung)
summary(fit, times = c(180, 365, 730))  # survival at specific times

# By group
fit_g <- survfit(Surv(time, status) ~ sex, data = lung)

# Publication-ready plot
ggsurvplot(fit_g, data = lung,
           risk.table = TRUE,           # ALWAYS include
           censor = TRUE,               # mark censoring ticks
           conf.int = TRUE,
           pval = TRUE,                 # log-rank p-value
           surv.median.line = "hv",     # median survival lines
           xlab = "Time (days)",
           legend.labs = c("Male", "Female"))

# Median survival with CI
print(fit_g)              # one line per group, with median + CI
# If "NA" appears in the median column, the curve never crossed 0.5.

# Survival at specific times with CI
summary(fit_g, times = c(180, 365))
```

### Python (lifelines)
```python
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts
import matplotlib.pyplot as plt

kmf = KaplanMeierFitter()
kmf.fit(df['time'], event_observed=df['event'], label='Overall')

# Survival at specific times
kmf.survival_function_at_times([180, 365, 730])
kmf.confidence_interval_survival_function_  # full CI band
kmf.median_survival_time_                   # may be inf if never crossed 0.5

# By group, with at-risk table
fig, ax = plt.subplots(figsize=(9, 6))
kmfs = []
for grp, sub in df.groupby('sex'):
    k = KaplanMeierFitter().fit(sub['time'], sub['event'], label=str(grp))
    k.plot_survival_function(ax=ax, ci_show=True)
    kmfs.append(k)
add_at_risk_counts(*kmfs, ax=ax)
plt.tight_layout()
```

### scikit-survival
```python
from sksurv.nonparametric import kaplan_meier_estimator

times, surv_prob, conf_int = kaplan_meier_estimator(
    df['event'].astype(bool), df['time'], conf_type="log-log"
)
```

### Median survival pitfall

When the curve never reaches 0.5, the median is **undefined**, not infinite. R returns `NA`; lifelines returns `inf`. Report "median not reached" along with the longest follow-up time so readers know the floor. Don't extrapolate the curve to estimate a median you didn't observe.

### Greenwood vs log-log CIs

`survfit` defaults to log-transformed Greenwood CIs (`conf.type = "log"`). These can give CIs that include values > 1 or < 0 near the boundaries. For curves that get close to 0 or 1, prefer `conf.type = "log-log"` (also called the complementary log-log transform), which gives CIs that stay in [0, 1].

## Nelson-Aalen — cumulative hazard H(t)

Estimates H(t) directly by summing $d_j / n_j$ at each event time. Relationship to KM: $S(t) = \exp(-H(t))$ for the Fleming-Harrington version, but the standard KM and standard NA are NOT exact transforms of each other (they differ in how ties are handled). They're asymptotically equivalent.

Use NA when:
- You want to estimate the cumulative hazard (e.g., to plot $\log H(t)$ vs $\log t$ to check Weibull shape).
- You need a baseline cumulative hazard estimate (e.g., for a Cox model's `basehaz()`).
- You want a smoother variance estimator than KM (KM's variance breaks down when few subjects are at risk).

### R
```r
# Nelson-Aalen via survfit with type = "fh" (Fleming-Harrington)
na_fit <- survfit(Surv(time, status) ~ 1, data = lung, type = "fleming-harrington")

# Or compute cumulative hazard directly
ch <- basehaz(coxph(Surv(time, status) ~ 1, data = lung))
head(ch)  # columns: hazard, time

# Plot
plot(na_fit, fun = "cumhaz", xlab = "Time", ylab = "Cumulative hazard")
```

### Python (lifelines)
```python
from lifelines import NelsonAalenFitter

naf = NelsonAalenFitter()
naf.fit(df['time'], event_observed=df['event'])
naf.cumulative_hazard_                    # H(t)
naf.cumulative_hazard_at_times([180, 365])
naf.plot_cumulative_hazard()
```

## Aalen-Johansen — competing risks and multi-state

This is the **right** estimator when more than one event can happen. The naive "treat competing event as censoring, then plot 1 − KM" approach **overestimates** the cumulative incidence of your event of interest, because it implicitly assumes that subjects experiencing the competing event would have had the same future hazard for your event — which they can't, they're gone.

AJ estimates the **cumulative incidence function (CIF)** for each cause k: $F_k(t) = P(T \le t, \text{cause} = k)$. The CIFs sum across causes to give the overall probability of any event. AJ also handles general multi-state models (sequences of transitions).

### R
```r
library(survival)
library(cmprsk)

# Status: 0 = censored, 1 = cause of interest, 2 = competing
# survival >= 3.0 supports multi-state directly:
df$status_f <- factor(df$status, levels = c(0, 1, 2), labels = c("censored", "cause1", "cause2"))

aj <- survfit(Surv(time, status_f) ~ 1, data = df)
plot(aj, col = c("blue", "red"), xlab = "Time", ylab = "Cumulative incidence")
# Plots CIFs for each cause.

# By group:
aj_g <- survfit(Surv(time, status_f) ~ treatment, data = df)
summary(aj_g, times = c(365, 730))  # cause-specific CIFs at specific times

# Alternative via cmprsk
ci <- cuminc(ftime = df$time, fstatus = df$status, group = df$treatment, cencode = 0)
plot(ci, col = 1:4)
```

### Python (lifelines)
```python
from lifelines import AalenJohansenFitter

# event_of_interest=1, other non-zero values treated as competing
ajf = AalenJohansenFitter(calculate_variance=True)
ajf.fit(df['time'], event_observed=df['status'], event_of_interest=1)
ajf.cumulative_density_                # CIF for cause 1
ajf.plot()

# For each cause, fit separately
for cause in [1, 2]:
    AalenJohansenFitter().fit(df['time'], df['status'], event_of_interest=cause).plot()
```

### The naive-KM-on-competing-risks bug

```r
# WRONG when there are competing events:
wrong <- survfit(Surv(time, status == 1) ~ 1, data = df)
plot(wrong, fun = function(s) 1 - s)  # overestimates cause-1 incidence

# RIGHT:
aj <- survfit(Surv(time, status_f) ~ 1, data = df)
plot(aj)  # plots proper CIFs
```

This is one of the most consistently made errors in applied survival work. If your data has any meaningful "death from other causes" or "user disengaged via a different mechanism," use AJ.

## Turnbull — interval-censored data

When event times are only known to lie in an interval (left, right, interval-censored, or any mix), KM is not valid. Turnbull's NPMLE generalizes KM by iteratively reassigning probability mass within each interval until likelihood converges. The resulting estimate is a survival curve that's only updated within "innermost intervals" — flat between them, so it looks blockier than KM.

### R
```r
library(icenReg)
library(interval)  # has icfit / ictest

# Data needs left and right interval bounds (L, R)
# Right-censored: R = Inf; left-censored: L = 0; interval-censored: L < R both finite; exact: L = R.

fit <- ic_np(cbind(L, R) ~ group, data = df)
plot(fit)

# Log-rank-like test for interval-censored data
library(interval)
ictest(L, R, group, data = df, rho = 0)  # rho > 0 for Fleming-Harrington weights
```

### Python (lifelines)
```python
from lifelines import KaplanMeierFitter

# lifelines supports left-censoring via left_censorship in older versions,
# and interval-censoring via the WeibullFitter / parametric models or use ic_np in R.
# For non-parametric Turnbull, R is the better tool.

# Left-censored only:
kmf = KaplanMeierFitter()
kmf.fit_left_censoring(df['time'], event_observed=df['event'])
```

If you have genuinely interval-censored data, lean on R's `icenReg` or `interval`. Python options are thinner.

## Kernel hazard estimators — h(t) directly

KM gives you S(t). NA gives you H(t). Neither shows you the *shape* of the actual hazard function h(t) — whether it's rising, falling, U-shaped, bathtub-shaped, etc. To see the hazard, you either fit a parametric model and read off its hazard, or you kernel-smooth.

### R
```r
library(muhaz)

# Kernel-smoothed hazard
h_est <- muhaz(times = df$time, delta = df$event,
               min.time = 0, max.time = max(df$time))
plot(h_est, xlab = "Time", ylab = "Hazard")

# Alternative: bshazard for B-spline hazard estimation
library(bshazard)
bs <- bshazard(Surv(time, status) ~ 1, data = lung)
plot(bs)
```

### What the hazard shape tells you

- **Monotonically increasing**: classic "aging" / wear-out pattern. Suggests Weibull with shape > 1, or Gompertz.
- **Monotonically decreasing**: "infant mortality" — early failures dominate. Weibull with shape < 1.
- **Constant**: memoryless process. Exponential distribution. Often a sign your time-to-event is more like a Poisson process.
- **U-shaped / bathtub**: high early hazard, low middle, rising late. Common in human mortality and many engineering systems. Mixture or log-logistic.
- **Inverted-U (humped)**: hazard peaks then declines. Log-normal or log-logistic.

Looking at the hazard shape before committing to a parametric form is good practice. If the smoothed hazard is clearly bathtub-shaped, fitting an exponential model is going to be wrong in instructive ways.

### Bandwidth caveat

Kernel hazard estimates are sensitive to bandwidth choice. `muhaz` has a `bw.method` argument; the "local" option does data-driven local bandwidth selection. Always show a smoothed hazard alongside its sensitivity to bandwidth — a single plot at default bandwidth can mislead.

## Confidence bands vs pointwise CIs

The shaded region around a KM curve from `survfit` is a **pointwise** CI — it's valid at each time t individually but not as a band. If you want a CI that contains the entire true survival curve with 95% probability, you need a simultaneous confidence band (e.g., Hall-Wellner or equal-precision bands).

```r
# Hall-Wellner band
library(km.ci)
fit <- survfit(Surv(time, status) ~ 1, data = lung)
band <- km.ci(fit, conf.level = 0.95, method = "hall-wellner")
plot(band)
```

For most descriptive uses, the pointwise band is fine and is what readers expect. If you're making formal claims about the entire curve (e.g., "treatment is uniformly superior over [0, T]"), use a simultaneous band.
