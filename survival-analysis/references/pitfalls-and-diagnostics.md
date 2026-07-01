# Pitfalls and diagnostics

A field guide to the errors that quietly corrupt survival analyses, with how to detect them and what to do instead. If you're reviewing someone else's survival analysis (your own past self included), run down this list.

## Top errors in applied survival analysis

### 1. Using linear regression or logistic regression on time-to-event data

**The error**: regressing duration on covariates with OLS, or "did the event happen by time T" with logistic.

**Why it's wrong**:
- OLS on durations treats censored observations as if they had short event times. Bias is downward and systematic.
- Logistic on "event by T" throws away the timing information and forces an arbitrary T. Subjects censored before T are usually dropped or miscoded.

**Fix**: use survival methods. If you only have an indicator outcome (event by some natural fixed horizon, no censoring before that horizon for anyone), logistic is fine. Otherwise, use Cox or a parametric survival model.

### 2. Naive 1 − KM for cumulative incidence with competing risks

**The error**: treating competing events as censoring, then plotting 1 − KM and calling it the cumulative incidence of the event of interest. **Overestimates** the cumulative incidence.

**Fix**: Aalen-Johansen CIFs. See `competing-risks.md`.

### 3. Immortal time bias

**The error**: defining a covariate based on something that happens during follow-up (e.g., "ever received treatment") and treating it as baseline. Subjects in the "received treatment" group were guaranteed to survive until they received it — they couldn't have died first. Artificially inflates survival in the treated group.

**Symptoms**: implausibly strong protective effect of a treatment that "happened to be given" to some subjects. Especially suspicious for therapies given non-randomly during follow-up.

**Fix**: model treatment as a time-varying covariate using counting-process data structure. See `cox-and-extensions.md`.

### 4. Confusing left truncation with left censoring

**The error**: treating "subject entered the study at age 65" as left censoring (or ignoring it entirely) instead of as left truncation. Biases survival estimates because you incorrectly assume the subject was at risk from age 0.

**Symptoms**: when using age as the time scale (or any scale where subjects enter at varying times), KM curves that don't start at S = 1, or implausible early survival.

**Fix**: `Surv(entry, exit, event)`. See `special-censoring.md`.

### 5. Ignoring the proportional hazards assumption

**The error**: fitting a Cox model and reporting HRs without checking PH. If PH is violated, the "HR" is a time-averaged summary that doesn't describe the data well, and can be misleading (e.g., reporting HR ≈ 1 for two groups whose curves cross).

**Fix**: always run `cox.zph()` / `check_assumptions()` and inspect Schoenfeld residual plots. Escalate to stratified Cox, time-varying coefficients, AFT, RMST, or MaxCombo when needed. See `nonproportional.md`.

### 6. No `cluster()` / `robust=True` in recurrent events

**The error**: fitting Andersen-Gill (or any model with multiple rows per subject) without robust SEs. Standard errors are too small because they pretend rows from the same subject are independent.

**Fix**: include `+ cluster(id)` in R or `robust=True` (with appropriate id_col) in Python. Point estimates are unbiased without it; SEs are not.

### 7. Treating interval-censored data as exact

**The error**: using the right endpoint (or midpoint) of an observation interval as if it were the exact event time. Biases estimates, more severely with wider intervals.

**Fix**: use interval-censored methods (`icenReg` in R, `fit_interval_censoring` in lifelines). See `special-censoring.md`.

### 8. Using log-rank when comparing groups with competing risks

**The error**: log-rank compares cause-specific hazards; it can declare two groups equal even when their CIFs differ substantially (because competing-event rates differ between groups).

**Fix**: Gray's test on CIFs.

### 9. Choosing τ for RMST after seeing the data

**The error**: trying several τ values and picking the one that gives the most impressive RMST difference. Inflates Type I error.

**Fix**: pre-specify τ based on clinical/operational meaning before looking at curves. A reasonable default is "the smallest of the maximum observed times in each group" if you must choose after seeing data, but pre-specification is better.

### 10. Treating ML model rankings as causal effects

**The error**: fitting a Random Survival Forest or XGBoost, reading SHAP values or feature importances, and concluding "this variable causes higher risk."

**Why it's wrong**: ML models are not causal inference. They capture associations conditional on what's in the dataset. Treatments observed under selection bias get spurious "importance."

**Fix**: ML models are great for prediction and ranking. For causal claims about a treatment, you need either an RCT, a target-trial-emulation observational design, or explicit causal methods (g-methods, IPTW, etc.). State the claim clearly: "this variable is predictive" vs "this variable is causal."

### 11. Complete (or quasi-complete) separation

**The error**: one group has zero events, or all events come from only one group. `coxph` (and its Python counterparts) may report "convergence achieved" while the coefficient is actually diverging to ±∞ with an enormous standard error. The output looks like a real result; it isn't.

**Symptoms to watch for**:
- Coefficient magnitude > 5–6 on the log-HR scale (HR > 400 or < 0.002).
- Very large SE relative to the coefficient.
- In R: `coxph` warning about "infinite coefficient" or "Ran out of iterations and did not converge."
- In Python (lifelines): `ConvergenceWarning` or an implausibly extreme HR.

```r
# Example: treat 0% events vs control 100% events
# coxph gives HR ~ exp(-15) or similar nonsense
fit <- coxph(Surv(time, status) ~ treatment, data = df)
summary(fit)  # coefficient ~ -15, se ~ 5: the partial likelihood never converges

# Fix 1: report the descriptive finding directly
table(df$status, df$treatment)  # "0% events in treatment, 100% in control"

# Fix 2: Firth penalized Cox (penalization pulls extreme coefficients toward finite values)
# install.packages("coxphf")
library(coxphf)
fit_firth <- coxphf(Surv(time, status) ~ treatment, data = df)
print(fit_firth)  # finite HR with a CI via profile likelihood; note it is still very large

# Fix 3: exact conditional logistic regression or penalized regression
# (for n small enough that exact methods are tractable)
```

**When it comes up**: small studies with strong predictors, rare events with an imbalanced covariate, or early termination of a trial with no events in one arm. Also common in simulation code that accidentally creates separation by construction.

**Don't**: report the divergent Cox coefficient as a real HR. Do: describe the separation plainly and, if regression is needed, use Firth penalization and label the result explicitly as Firth-penalized.

## Diagnostics — what to run, always

### For any survival analysis

1. **Counts**: total subjects, total events, events per group/cause, distribution of follow-up time. Survival inference is event-limited; a "large n" study with few events is small.
2. **KM curves with at-risk table** for each main covariate. Check for crossings, late-tail instability, sufficient at-risk in each group at chosen τ.
3. **Censoring pattern**: is censoring concentrated at the end of follow-up (administrative) or spread throughout (informative-looking)? If the latter, think about why subjects drop out and whether that's correlated with event risk.

### For Cox models

1. **Schoenfeld residuals** (`cox.zph` / `check_assumptions`) — per-covariate and global PH tests, with residual plots.
2. **Martingale residuals vs continuous covariates** — checks linearity. If the smooth shows a clear non-linear shape, fit with splines.
3. **dfbeta residuals** — checks for influential observations. A few subjects shouldn't dominate the fit.
4. **Concordance index** with bootstrap CI (or cross-validated for prediction-focused models).
5. **Events per covariate** — rough rule of thumb ≥ 10. Otherwise, use penalization.

### For parametric models

1. **Compare AIC across distributions** — but don't optimize for AIC; pick the simplest distribution that fits well.
2. **Overlay fitted curve on KM** — visual sanity check that the parametric form matches the data.
3. **Inspect smoothed hazard vs model hazard** — verify the chosen distribution captures the shape.
4. **For extrapolation: fan plot across distributions** — show the range of predictions, not a single number.

### For competing risks

1. **CIFs** (Aalen-Johansen) — not 1 − KM.
2. **Cumulative incidences for all causes** summing to ≤ 1, with non-event probability filling the rest.
3. **Cause-specific and Fine-Gray side by side** when reporting effects.

### For recurrent events

1. **Distribution of event counts per subject** — heavily skewed? A few subjects driving most events?
2. **Mean cumulative function** plot.
3. **Compare AG to PWP-TT** — if results differ substantially, events aren't exchangeable and PWP is more appropriate.
4. **Robust / cluster-adjusted SEs** confirmed in output.

## Interpretation traps

### "Hazard ratio is just a relative risk"

No. HR is the ratio of instantaneous hazards. Relative risk is the ratio of cumulative probabilities. They can give very different numbers, especially for common outcomes. An HR of 2 in a rare-event setting is close to RR = 2; in a common-event setting, the RR is much closer to 1.

### "P > 0.05 means PH holds"

No. The test has limited power; in small samples, it often fails to detect meaningful violations. Always inspect residual plots, not just the p-value.

### "P < 0.05 from cox.zph means I have to abandon the Cox model"

Not necessarily. In large samples, the test detects trivial deviations. Check whether the residual plot shows a meaningful trend or just slight wobble. If meaningful, escalate; if trivial, document and move on.

### "Median survival not reached" means treatment is amazing

Often it just means follow-up was too short. Always report "median not reached, longest follow-up = X" so readers know the floor.

### "C-index of 0.7 is a good model"

Maybe. C-index ignores calibration entirely. A model can rank subjects well (high C-index) while systematically over- or underpredicting survival probabilities. Report C-index AND calibration plots for prediction-focused work.

### "Treatment HR for a continuous variable means a per-unit effect"

Yes, but only on the log-hazard scale. The exp(coef) is the per-unit HR. To get the effect of a 10-unit increase: HR^10. Don't add HRs across units.

### "Schoenfeld residuals look fine for stratification variable"

You won't get Schoenfeld residuals for a stratification variable in `cox.zph` because it's not in the model. That's by design — stratification absorbs whatever effect that variable has. If you want to test PH for that variable, fit it as a regular covariate first, test, then decide whether to stratify.

### "I should use the most flexible model possible"

Often wrong. A Royston-Parmar with k = 4 knots and time-varying coefficients on every covariate will overfit small datasets and give wider CIs than needed. Match model complexity to information content (events, signal strength).

## Sanity checks before reporting

Before sending or publishing a survival analysis, walk through:

1. **Does the time origin make sense?** "Time since randomization," "time since signup" — could it be more meaningful otherwise?
2. **Is the right censoring time correct?** End of follow-up, end of contract, end of data collection?
3. **Are competing events present?** If yes, are you using Aalen-Johansen CIFs and the right regression framework?
4. **Was the PH assumption checked?** What did you find? Document.
5. **Are SEs robust / clustered if needed?** Recurrent events, clustered designs.
6. **Does the median survival match the KM curve visually?** If reported median is at t = 200 but the curve clearly crosses 0.5 at t = 250, something's wrong.
7. **Does C-index match what the model can actually do?** A C-index near 0.5 means the model isn't useful for prediction even if some HRs are statistically significant.
8. **Are predictions in plausible units and ranges?** Predicted 1-year survival = 1.2 means a coding bug.
9. **Did you communicate absolute and relative effects?** "HR = 1.5" alone is incomplete. "1-year survival 88% (control) vs 82% (treatment), HR 1.5 (1.2–1.9)" is complete.
10. **Are you treating an ML model as causal evidence?** If yes, walk it back.

## When in doubt

- **Re-plot the KM curves and look at them.** Most errors become visible.
- **Compare two approaches that should agree.** If KM and a Cox baseline predict different survival at the population mean, debug.
- **Simulate.** If you're not sure whether a method is doing what you think, simulate data with known properties and check that estimates recover the truth.
- **Cross-check between R and Python** for important results, especially if using less common methods. They should agree to numerical tolerance.
