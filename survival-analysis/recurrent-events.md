# Recurrent events

When the event can happen more than once per subject — hospital readmissions, equipment breakdowns, repeat purchases, app crashes, asthma attacks — the standard "time to first event" analysis throws away most of the information. Recurrent event models use all events per subject.

There are several competing frameworks. They give different answers to different questions, and they're not interchangeable. Pick deliberately.

## The four main approaches

| Model | Time scale | Risk set | Best for |
|---|---|---|---|
| **Andersen-Gill (AG)** | Total time from origin | All subjects at risk at time t (subject re-enters after each event) | Effect on overall event rate; events that are exchangeable |
| **PWP Total Time (PWP-TT)** | Total time from origin | Subjects who have had ≥ (k-1) events, in risk set for k-th event | Effect can differ by event order; total elapsed time matters |
| **PWP Gap Time (PWP-GT)** | Time since previous event | Subjects who have had ≥ (k-1) events, with clock reset | Effect depends on time since last event (renewal process flavor) |
| **WLW (Wei-Lin-Weissfeld)** | Total time from origin | All subjects at risk for the k-th event, including those who haven't had (k-1) events | Marginal effect on each event separately; events not necessarily ordered |

A summary of the differences:

- **AG** treats the event sequence as a single counting process: events are exchangeable, the hazard depends only on the current covariate values and the at-risk indicator. Easiest to fit and interpret. Use when you can plausibly assume events are exchangeable (e.g., asthma attacks: a second attack isn't fundamentally different from a first).
- **PWP-TT** stratifies by event number. The first event uses one baseline hazard, the second another, and so on. Captures the idea that "having already had two events" changes your hazard for the third in a way not captured by covariates. Uses total time from origin as the time scale.
- **PWP-GT** is PWP-TT but with the clock reset after each event. Models the **gap** time between events. Use when the relevant question is "after an event, how long until the next?" rather than "from origin, how long until the k-th?"
- **WLW** fits a separate marginal model per event number (one for "time to first," one for "time to second," etc.) using the entire sample for each, and combines via robust variance. Originally intended for unordered failure types but sometimes used for ordered events. Often criticized for the "at risk for the k-th event even before having (k-1) events" structure.

If unsure, start with **AG** and check whether event-number-specific effects matter using PWP-TT. WLW is less commonly recommended now.

## Data structure

All four methods use **counting-process** format: one row per (subject, interval), with `(tstart, tstop, event)`. After each event, a new row starts.

For a subject with events at days 30 and 90, censored at day 120:

```
id | tstart | tstop | event | enum  (event number)
 1 |   0    |  30   |   1   |  1
 1 |  30    |  90   |   1   |  2
 1 |  90    | 120   |   0   |  3
```

For PWP-TT/GT, you also need the event-number stratifier (`enum`). For PWP-GT, `tstart` resets to 0 after each event (so the second row has `tstart=0, tstop=60` instead of `tstart=30, tstop=90`).

For WLW, the data is restructured differently: one row per (subject × event number) with all subjects represented for every event number, regardless of whether they reached that event.

## Andersen-Gill (AG)

The natural extension of Cox to recurrent events. The intensity (hazard) at time $t$ for subject $i$ is:

$\lambda_i(t) = Y_i(t) \cdot \lambda_0(t) \cdot \exp(x_i(t)^\top \beta)$

where $Y_i(t) = 1$ when subject $i$ is under observation (with subjects re-entering the risk set immediately after each event). One baseline hazard, one set of coefficients.

### R
```r
library(survival)

# Data in counting-process format
fit_ag <- coxph(Surv(tstart, tstop, event) ~ treatment + age + cluster(id),
                data = recurrent_df)
summary(fit_ag)
# cluster(id) gives robust variance to handle within-subject correlation.
```

The `cluster(id)` (or, equivalently, `+ cluster(id)` and using robust = TRUE) is **essential**. Without it, standard errors assume independence between rows from the same subject and are too small. The point estimate is unaffected.

### Python

Two options. Use lifelines for point estimates; use `statsmodels PHReg` when you need cluster-robust SEs.

**Point estimates (lifelines):**
```python
from lifelines import CoxTimeVaryingFitter

ctv = CoxTimeVaryingFitter()
ctv.fit(recurrent_df, id_col='id', event_col='event',
        start_col='tstart', stop_col='tstop',
        formula='treatment + age')
ctv.print_summary()
# robust=True raises NotImplementedError in lifelines 0.30.x — use PHReg below for robust SEs.
```

**Cluster-robust SEs (statsmodels PHReg):**
```python
import statsmodels.duration.hazard_regression as smh

mod = smh.PHReg(
    endog  = recurrent_df['tstop'].values,
    exog   = recurrent_df[['treatment', 'age']].values,
    status = recurrent_df['event'].values,
    entry  = recurrent_df['tstart'].values,   # counting-process start time
)
res_naive  = mod.fit(disp=False)                              # information-based SEs
res_robust = mod.fit(groups=recurrent_df['id'].values, disp=False)  # sandwich-robust SEs

# Point estimates identical; robust SEs are typically larger
print(res_naive.params, res_naive.bse)
print(res_robust.params, res_robust.bse)
```

`groups=id` applies the Lin-Wei sandwich correction for within-subject correlation, the Python equivalent of `cluster(id)` in R. Point estimates are unaffected; SEs increase to reflect that rows from the same subject carry correlated information.

### Interpretation

The AG HR is interpreted as a ratio of **event rates** (events per unit time at risk), not a ratio of "time to first event" hazards. An AG HR of 0.7 for treatment means treated subjects have 30% lower event rate over follow-up.

## PWP — Prentice, Williams, Peterson

Two flavors, both stratifying on event number.

### PWP-TT (Total Time)

```r
fit_pwp_tt <- coxph(Surv(tstart, tstop, event) ~ treatment + age +
                    strata(enum) + cluster(id),
                    data = recurrent_df)
summary(fit_pwp_tt)
```

Each event number has its own baseline hazard (via `strata(enum)`). Time scale is total time from origin.

### PWP-GT (Gap Time)

```r
# Restructure so tstart and tstop are gap times since previous event:
recurrent_df$gap_start <- 0
recurrent_df$gap_stop  <- recurrent_df$tstop - recurrent_df$tstart

fit_pwp_gt <- coxph(Surv(gap_start, gap_stop, event) ~ treatment + age +
                    strata(enum) + cluster(id),
                    data = recurrent_df)
summary(fit_pwp_gt)
```

PWP-GT is appropriate when the gap between events is the right time scale — e.g., recovery between attacks, time between equipment maintenance cycles.

### Letting effects differ by event number

If you suspect a covariate's effect varies by event number (treatment works for first event but not later ones), interact:

```r
fit <- coxph(Surv(tstart, tstop, event) ~ treatment * strata(enum) + age +
             cluster(id), data = recurrent_df)
```

Or fit per-stratum models.

### Python

`CoxTimeVaryingFitter` doesn't have first-class strata-by-event-number support; you can approximate by fitting separate models per event number, or restructure with interaction terms. For PWP work, R is much cleaner.

## WLW — Wei, Lin, Weissfeld

A marginal model: for each event number k, fit a Cox model on the time to the k-th event using all subjects (those who didn't reach event k are censored at their last observation). Combine via robust variance.

```r
# Requires restructuring: one row per subject per event number considered
# (subject 1 has rows for events 1, 2, 3 even if they only experienced 2 events)
fit_wlw <- coxph(Surv(time_to_event_k, status_k) ~ treatment + age +
                 strata(enum) + cluster(id),
                 data = wlw_df)
```

WLW is mostly of historical interest now. It's been critiqued because the risk set for the k-th event includes subjects who haven't had the (k-1)-th event, which is conceptually awkward. Prefer AG or PWP for most applications.

## Choosing among AG, PWP-TT, PWP-GT, WLW

A practical decision tree:

1. **Are events exchangeable?** (Is the k-th event fundamentally the same as the first?)
   - Yes → AG.
   - No, depends on event number → PWP-TT or PWP-GT.
2. **If non-exchangeable: what's the natural time scale?**
   - Time from study origin (e.g., "from diagnosis to k-th flare") → PWP-TT.
   - Time since previous event (e.g., "time between flares") → PWP-GT.
3. **Marginal effects per event without event-number ordering?** → WLW (uncommon).

Reporting both AG and PWP-TT side by side is a defensible approach when you're unsure — AG gives the overall rate effect, PWP-TT shows whether the effect changes across event numbers. If they agree, the AG summary is clean. If they disagree, the PWP results are more informative.

## Mean cumulative function (MCF)

For description (without regression), plot the **mean cumulative function**: the expected number of events per subject by time $t$. This is the recurrent-events analog of $1 - S(t)$ from KM.

### R
```r
library(survival)
mcf <- survfit(Surv(tstart, tstop, event) ~ treatment, data = recurrent_df,
               id = id)
plot(mcf, cumhaz = TRUE, xlab = "Time", ylab = "Mean cumulative events",
     col = c("blue", "red"))
```

```r
# Alternative: reReg package
library(reReg)
mcf_fit <- reReg(Recur(tstop, id, event) ~ treatment, data = recurrent_df,
                 model = "cox.LWYY")
plot(mcf_fit)
```

The LWYY (Lin-Wei-Yang-Ying) model is a robust version of AG that's often recommended when the proportional rates assumption is shaky.

## Recurrent events with a terminal event

A subject can have recurring non-terminal events (e.g., readmissions) until a terminal event (death) ends the process. Treating death as just another type of censoring is wrong — it's informative censoring (sicker subjects die and stop generating readmissions, biasing the readmission rate downward).

This is properly handled by **joint frailty models** (recurrent events and the terminal event share a frailty random effect; see `multistate-frailty.md`) or by switching to a multi-state framework.

## Common errors

1. **Forgetting `cluster(id)`** in AG/PWP models. Standard errors are wildly underestimated without it.
2. **Using AG when events aren't exchangeable.** The "10th asthma attack" really might not be the same as the "1st." Check by fitting PWP-TT and seeing if baseline hazards differ noticeably by event number.
3. **Mixing time scales.** AG and PWP-TT use total time; PWP-GT uses gap time. Don't restructure data for one and fit the other.
4. **Treating a terminal event as ordinary censoring** when modeling recurrent events. Use joint frailty or a multi-state model instead.
5. **Reporting "time to first event" Cox** when more events exist. You're throwing away the recurrent information.

## Reporting checklist

- Choice of model (AG, PWP-TT, PWP-GT) and why.
- Number of subjects, total number of events, distribution of events per subject.
- Whether `cluster(id)` or robust variance was used.
- For PWP: results per event number (or that effects didn't vary, with supporting analysis).
- MCF plot for description.
- Whether a terminal event was present, and how it was handled.
