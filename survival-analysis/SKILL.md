---
name: survival-analysis
description: Apply survival analysis (time-to-event modeling) correctly in R and Python. Use whenever the user asks about modeling the time until something happens — churn, conversion, retention, time-to-purchase, time-to-failure, readmission, default, promotion — or any "how long until" question, especially with censoring (subjects who haven't had the event by end of observation). Trigger on Kaplan-Meier, Cox proportional hazards, hazard ratios, log-rank, RMST, Fine-Gray, competing risks, recurrent events, frailty, multi-state, Royston-Parmar, AFT, Weibull, time-varying covariates, left truncation, interval censoring, concordance index, Brier score, or packages `lifelines`, `survival`, `survminer`, `flexsurv`, `cmprsk`, `mstate`, `scikit-survival`. Also trigger when a user reaches for linear or logistic regression on time-to-event data — usually the wrong tool. Do not skip this skill assuming the base model already knows the field; specific conventions around censoring, assumption checks, and choice between similar-looking estimators are where generic advice silently produces wrong answers.
---

# Survival Analysis (Time-to-Event Modeling)

This skill is for analyses where the outcome is **how long until an event happens** — and where some observations are censored (the event hasn't happened yet, or the subject was lost to follow-up). Survival analysis is the right tool whenever both of these are true:

1. The outcome variable is a duration (time to an event).
2. Some subjects are observed without yet having the event.

If you have time-to-event data and reach for linear regression on the durations, you'll bias your estimates downward (censored subjects look like they had short times when really we just stopped watching). If you reach for logistic regression on "did the event happen by time T," you throw away the timing information and have to arbitrarily pick T. Survival analysis handles both problems correctly.

The classic application is biomedical (time until death/relapse/recovery), but the same machinery applies to:

- **Product/UX**: time until user churn, time until a feature is adopted, time until first purchase, time until session abandonment, time until a free trial converts.
- **Engineering**: time until component failure (called "reliability analysis").
- **Economics/finance**: time until loan default, time until unemployment ends, time until a customer upgrades.
- **HR**: time until an employee quits, time until a job posting is filled.

The vocabulary differs by field but the math is the same.

## How to use this skill

The SKILL.md is the map. It covers the core concepts you must keep straight, the decision tree for picking a method, and pointers to reference files for code. **Always read the relevant reference file before writing code** — the references encode specific function names, argument quirks, and traps that aren't memorizable from training data alone.

```
survival-analysis/
├── SKILL.md (this file — concepts + decision tree)
└── references/
    ├── r-recipes.md           — R code for all methods (survival, survminer, flexsurv, cmprsk, mstate, frailtypack, nph)
    ├── python-recipes.md      — Python code (lifelines, scikit-survival, pycox)
    ├── estimators.md          — Non-parametric estimators in depth: KM, NA, AJ, Turnbull, kernel hazard smoothing
    ├── cox-and-extensions.md  — Cox PH, stratified Cox, time-varying covariates, time-varying coefficients
    ├── parametric-and-aft.md  — AFT models, parametric distributions, Royston-Parmar flexible splines
    ├── nonproportional.md     — Weighted log-rank family, MaxCombo, RMST, when PH fails
    ├── competing-risks.md     — Cause-specific hazards, Fine-Gray subdistribution, Gray's test, CIFs
    ├── recurrent-events.md    — Andersen-Gill, PWP-TT, PWP-GT, WLW, gap-time vs total-time
    ├── multistate-frailty.md  — Multi-state models, illness-death, frailty (shared, joint, nested)
    ├── special-censoring.md   — Left censoring, interval censoring, left truncation (delayed entry)
    ├── pitfalls-and-diagnostics.md — Assumption checks, common errors, interpretation traps
    └── synthetic-data.md      — Generate realistic time-to-event data for demos, testing, examples
```

## Diagnosing what the user is actually asking

Users almost never say "I need Fine-Gray subdistribution regression." They describe a data situation in their own vocabulary, and the first job is translating that into a method. The decision tree later in this file is the destination; this section is how to get there from messy natural language.

### Listen for signals in the user's framing

**Signals of competing risks** (more than one type of event, mutually exclusive):
- "Users either convert or churn" / "either get hired or give up" / "either get promoted or leave."
- Two outcomes that can't both happen to the same subject in the relevant window.
- Any "cause-specific mortality" or "primary endpoint vs secondary endpoint that ends follow-up" framing.
- → Reach for cause-specific Cox and/or Fine-Gray; never naive KM treating one event as censoring.
- **Exception — fixed finite horizon with near-zero censoring**: if the observation window is hard-capped at a known time T (e.g., a 14-day free trial) and virtually everyone is observed through T, the competing events may not generate meaningful censoring. In that case, standard logistic regression on "event A by day T, yes/no" can be defensible and simpler. Ask whether there is substantial censoring *before* T; if not, survival methods add complexity without benefit. If there is, use Aalen-Johansen CIFs and Fine-Gray.

**Signals of recurrent events** (event can repeat for same subject):
- "Crashes," "readmissions," "purchases," "logins," "failures," "attacks," "incidents."
- "How often does X happen" rather than "how long until X."
- Plural framing of the event.
- → Andersen-Gill, PWP, or LWYY. If "time to first" is what's being asked, push back: that throws away information.

**Signals of left truncation** (subject not at risk from time origin):
- Using **age** as the time scale.
- Prevalent-cohort designs ("we recruited people who already have diabetes").
- Insurance/policy data captured from issue date.
- Any "we started observing them when..." that isn't "from time zero."
- → `Surv(entry, exit, event)`. If the user hasn't thought about this, raise it explicitly.

**Signals of interval censoring** (event known only within a window):
- Periodic check-ups, scheduled visits, batch processing of logs.
- "We check daily / weekly / monthly whether the event happened."
- → Don't use the midpoint or right endpoint as if it were the event time. Use `icenReg` (R) or `fit_interval_censoring` (lifelines).

**Signals of non-proportional hazards**:
- "The treatment effect kicks in after a few months" (delayed effect).
- "The surgery has high early mortality then patients do well" (early effect).
- "Curves cross" or "the benefit reverses over time."
- → Don't default to Cox + single HR. Consider RMST, weighted log-rank (with FH weights matching the shape), MaxCombo, or time-varying coefficients.

**Signals the user is reaching for the wrong tool entirely**:
- "I'm running a linear regression on survival time" — censored observations are biasing your estimates downward.
- "I'm using logistic regression on whether they churned by day 30" — you've thrown away timing info and arbitrary T.
- "I'm computing average time to event" — biased if censoring is present. Use RMST or median survival from KM.
- → Walk them back to survival methods, briefly explain why.

**Signals of clustering / correlation**:
- "Patients within hospitals," "students within schools," "users within accounts."
- "Some subjects have multiple events" (also recurrent).
- → `cluster()` / `robust=True` for SEs; consider frailty if heterogeneity is itself of interest.

### When the user hasn't thought about censoring at all

A common situation: the user has time-to-event data, didn't realize censoring matters, and is about to do something biased. They usually phrase it as "predict how long until X happens." Two questions surface what's going on:

1. "Do you have subjects who haven't had the event yet at the end of your observation window?" (Tests for right censoring.)
2. "Could the event have happened before you started observing some subjects?" (Tests for left censoring or truncation.)

If yes to (1), survival analysis is needed. If yes to (2), it's needed *and* you have non-standard censoring to handle.

### When in doubt, ask one clarifying question

The most useful clarifying questions, in order of how often they unlock the right method:

1. "Is the event of interest something that can happen more than once per subject, or just once?" (Recurrent vs single-event.)
2. "Are there other events that would stop you from observing the event of interest?" (Competing risks.)
3. "When does the clock start, and is it the same for every subject?" (Time origin, possible left truncation.)
4. "How is the event recorded — exact time, or only within some window?" (Exact vs interval censored.)
5. "Do you want to compare groups, estimate effects of covariates, or predict for individuals?" (Determines whether to use a test, regression, or prediction model.)

Don't ask all of these. Pick the one most likely to disambiguate based on the framing.

## Core concepts you must keep straight

Most beginner mistakes come from confusing four related but distinct functions. Always be clear which one you're talking about.

- **Survival function S(t)**: probability that a subject's event time T is greater than t. This is what the Kaplan-Meier curve plots. Starts at 1, decreases monotonically.
- **Hazard function h(t)**: the instantaneous rate of the event at time t, given the subject has survived until t. "If you've made it to time t, what's the risk in the next instant?" The hazard is NOT a probability — it can exceed 1.
- **Cumulative hazard H(t)** = integral of h(t). Related to survival by S(t) = exp(-H(t)). The Nelson-Aalen estimator estimates this directly.
- **Hazard ratio**: ratio of hazards between two groups. What Cox regression reports. HR = 2 means "at any given moment, group A has twice the instantaneous risk of group B."

Hazard ratios are **not** risk ratios or odds ratios. They are instantaneous and time-local. The "constant hazard ratio over time" assumption is the proportional hazards assumption — the single most important thing to check in any Cox analysis.

### Censoring types

- **Right censoring** (by far the most common): we know T > c for some known c. Handled natively by all standard methods.
- **Left censoring**: we know T < c. The event happened before observation began but we don't know exactly when. Use Turnbull's estimator or specialized parametric models. See `references/special-censoring.md`.
- **Interval censoring**: we know c1 < T < c2. Common in studies with periodic check-ups (HIV seroconversion, dental events, equipment inspections). Naively treating midpoint as event time is *biased*. See `references/special-censoring.md`.
- **Left truncation / delayed entry**: subjects enter the risk set only after some time. Different from left censoring. Most common when using **age as the time scale** rather than time-on-study, or in any prevalent-cohort design. See `references/special-censoring.md`.

Confusing left truncation with left censoring is a common error. Truncation = subject wasn't observable until later; censoring = subject was observable but we didn't see the exact event time.

### The "independent censoring" assumption

Every standard survival method assumes censoring is independent of the event process — censored subjects at time t have the same future hazard as uncensored subjects at time t. Often violated in practice: if sicker patients drop out, or if churned users are more likely to also stop being trackable, your estimates are biased. Always think about *why* subjects are censored before trusting any output.

## The decision tree

Use this to pick the right method. Each row points to where to find the code and details.

### "I want to describe survival in my data"

| Situation | Method | Reference |
|---|---|---|
| Right-censored only | **Kaplan-Meier** for S(t), **Nelson-Aalen** for H(t) | `estimators.md` |
| Interval-censored | **Turnbull NPMLE** | `estimators.md`, `special-censoring.md` |
| Competing events | **Aalen-Johansen** for cause-specific CIFs (NOT 1 - KM) | `estimators.md`, `competing-risks.md` |
| Smooth hazard estimate | **Kernel hazard smoothing** (`muhaz` in R, `bshazard`) | `estimators.md` |
| Multi-state | **Aalen-Johansen** generalized (transition probabilities) | `multistate-frailty.md` |

### "I want to compare survival between groups"

| Situation | Method | Reference |
|---|---|---|
| Standard, expect proportional hazards | **Log-rank test** | `r-recipes.md`, `python-recipes.md` |
| Differences expected early (vanishing treatment effect) | **Gehan-Breslow** or **Tarone-Ware** | `nonproportional.md` |
| Differences expected late (delayed treatment effect) | **Fleming-Harrington G(0,1)** or **Peto-Peto** | `nonproportional.md` |
| Don't know shape of effect; curves may cross | **MaxCombo** (combines G(0,0), G(0,1), G(1,0), G(1,1)) | `nonproportional.md` |
| Stratified comparison | **Stratified log-rank** | `r-recipes.md`, `python-recipes.md` |
| Competing risks comparison | **Gray's test** (on CIFs, NOT log-rank) | `competing-risks.md` |
| Want a single interpretable summary | **RMST difference** | `nonproportional.md` |

### "I want to model the effect of covariates"

| Situation | Method | Reference |
|---|---|---|
| Standard, PH plausible | **Cox PH regression** | `cox-and-extensions.md` |
| PH violated for some variable | **Stratified Cox** OR **time-varying coefficient** | `cox-and-extensions.md`, `nonproportional.md` |
| Want absolute survival predictions / extrapolation | **Parametric AFT** (Weibull, log-normal, log-logistic, generalized gamma) | `parametric-and-aft.md` |
| Need flexible baseline hazard, want full distribution | **Royston-Parmar flexible parametric** (`flexsurvspline`, `rstpm2`) | `parametric-and-aft.md` |
| Many covariates, prediction-focused | **Penalized Cox** (lasso/elastic-net), **Random Survival Forest**, **GB survival** | `cox-and-extensions.md`, `python-recipes.md` |
| Time-varying covariate (changes during follow-up) | **Cox with counting-process data** (start, stop, event) | `cox-and-extensions.md` |
| Time-varying coefficient (effect changes over time) | **Cox with tt() / time interaction** | `cox-and-extensions.md`, `nonproportional.md` |
| Continuous covariate with non-linear effect | **Cox with splines** (`pspline`, `rcs`) | `cox-and-extensions.md` |
| Highly non-linear, lots of data | **Random Survival Forest**, **Gradient Boosting**, **DeepSurv / DeepHit** | `python-recipes.md` |

### "I have something more complex than one event per subject"

| Situation | Method | Reference |
|---|---|---|
| Two+ competing causes of event | **Cause-specific Cox** (for etiology) and/or **Fine-Gray subdistribution** (for risk prediction) | `competing-risks.md` |
| Recurrent events, common baseline hazard, total time | **Andersen-Gill** | `recurrent-events.md` |
| Recurrent events, stratified by event number, total time | **PWP-TT** (Prentice-Williams-Peterson Total Time) | `recurrent-events.md` |
| Recurrent events, gap-time clock resets after each event | **PWP-GT** (PWP Gap Time) | `recurrent-events.md` |
| Recurrent events, marginal approach (event-specific risk sets) | **WLW** (Wei-Lin-Weissfeld) | `recurrent-events.md` |
| Subject-level heterogeneity (clustering) | **Shared frailty** (Gamma or log-normal) | `multistate-frailty.md` |
| Recurrent events + terminal event (e.g., readmissions + death) | **Joint frailty** | `multistate-frailty.md` |
| Subjects move through multiple states | **Multi-state models** (`mstate`, `msm`) | `multistate-frailty.md` |

### "Standard censoring assumptions are violated"

| Situation | Method | Reference |
|---|---|---|
| Some events known only as "before time c" | **Left censoring** via Turnbull or parametric likelihood | `special-censoring.md` |
| Events known only within intervals | **Interval-censored** Cox (`icenReg::ic_sp`, `ic_par`) | `special-censoring.md` |
| Subjects observable only after some entry time | **Left truncation**: `Surv(entry, exit, event)` | `special-censoring.md` |
| Using **age** as time scale | **Left truncation by definition** — always specify entry age | `special-censoring.md` |
| Informative censoring suspected | Sensitivity analysis with **IPCW** or **joint models** | `pitfalls-and-diagnostics.md` |

## The workflow (apply to every analysis)

### 1. Set up the data correctly

Standard format: one row per subject with at least a **time** column (duration from origin to event or censoring) and an **event indicator** (1 if event observed, 0 if censored). For competing risks, the indicator takes values 0/1/2/... for censored/cause1/cause2/.... For time-varying covariates or recurrent events, restructure into **counting process** format: one row per interval with `(tstart, tstop, event)`.

Make sure the time origin is meaningful and consistent (date of enrollment? date of diagnosis? date of feature launch?). If using **age as the time scale**, you must handle left truncation: subjects are not at risk from age 0, only from the age at which they entered the study. Specify with `Surv(age_at_entry, age_at_exit, event)`.

### 2. Always start with Kaplan-Meier (or Aalen-Johansen for competing risks)

Before any modeling, plot the survival curve(s). For each major covariate of interest, plot KM curves stratified by that covariate and run a log-rank test. This:

- Shows you whether the event rate is high or low (if S(t) barely decreases, you might be underpowered).
- Reveals whether curves cross — a strong sign that proportional hazards will be violated.
- Tells you the median survival time, if reached.
- Surfaces obvious group differences before you confound yourself with regression.

**Always show the "number at risk" table** beneath KM plots — survival estimates in the tail become unreliable as the at-risk population shrinks. With competing risks, **plot CIFs from Aalen-Johansen, not 1 − KM**.

### 3. Pick a model from the decision tree above

Don't default to Cox without thinking. If you need absolute predictions, want to extrapolate, or have lots of late censoring, parametric models (or Royston-Parmar splines) often win. If you have competing risks, you need to commit to whether you care about etiology (cause-specific Cox) or absolute risk prediction (Fine-Gray) — they answer different questions.

### 4. Check assumptions — non-negotiable for Cox

For a Cox model, check the proportional hazards assumption with **scaled Schoenfeld residuals** (Grambsch-Therneau test):

- R: `cox.zph(fit)` — p-value per covariate and globally.
- Python (lifelines): `cph.check_assumptions(df, p_value_threshold=0.05)`.

**Don't just look at the p-value.** Plot scaled Schoenfeld residuals against time. A flat line means PH holds; a clear trend means it doesn't. P-values are oversensitive in large samples and undersensitive in small ones.

If PH is violated, options in order of escalation:
1. **Stratify** by the violating variable (controls for it but no HR estimate for it).
2. **Add a time-varying coefficient** (interaction with a function of time).
3. **Switch to AFT** or **Royston-Parmar** model with time-dependent effects.
4. **Report RMST differences** (assumption-free, clean "extra expected survival time" interpretation).
5. **Use MaxCombo** for the hypothesis test if you're comparing groups.

Also check influential observations (`dfbeta` residuals) and nonlinearity in continuous covariates (martingale residuals, splines).

### 5. Evaluate predictive performance honestly

For prediction-style models:

- **Concordance index (C-index)**: probability the model ranks a random pair in the right order by risk. 0.5 = random; 1.0 = perfect. Survival analog of AUC. Available everywhere.
- **Brier score**: time-specific squared error between predicted survival probability and actual outcome at time t. Must be **IPCW-weighted** to be unbiased under censoring. Integrate over a time range to get the Integrated Brier Score (IBS).
- **Calibration plots**: predicted vs observed survival probability bucketed at chosen times. A model can have great discrimination (C-index) but be miscalibrated. Both matter.
- **Time-dependent AUC**: AUC for "event by time t" prediction at varying t. Useful when discrimination at specific horizons matters more than overall ranking.

Always split into train/test or use cross-validation.

## Choosing R vs Python

Both are capable; they have different strengths:

- **R is more mature** for classical survival. `survival` (Therneau) is the reference implementation. `survminer` produces publication-ready plots. `flexsurv`/`rstpm2` for Royston-Parmar. `cmprsk` for Fine-Gray. `mstate` for multi-state. `frailtypack` for advanced frailty/joint models. `nph` for MaxCombo and weighted log-rank. Use R for competing risks, multi-state, parametric AFT with unusual distributions, regulatory/clinical reports.
- **Python is better integrated with ML pipelines**. `scikit-survival` follows the scikit-learn API. `lifelines` has clean ergonomics for basics. `pycox` opens neural survival models (DeepSurv, DeepHit). Use Python when survival is one piece of a larger ML system or for production.

Match the user's existing stack rather than switching them. Some methods are only well-supported in one ecosystem — flag that explicitly when it comes up (e.g., Royston-Parmar in `flexsurv` has no clean Python equivalent; joint frailty models really only exist in R's `frailtypack`).

## Communicating results

Rules that consistently produce clearer survival writeups:

- **Report hazard ratios with 95% CIs**, not just point estimates or p-values. "HR = 1.45 (95% CI 1.12–1.88)" is a complete summary.
- **Interpret HRs as instantaneous, not cumulative.** "Patients on treatment had ~45% higher hazard of the event at any given time" — not "45% more likely to die." If a non-technical audience wants the cumulative version, supplement with survival probabilities or RMST differences at clinically meaningful timepoints.
- **Always show median survival time with CI when available.** "Median not reached" is informative — say so explicitly.
- **Mark censoring on KM curves** (the little ticks) and include the at-risk table.
- **Distinguish absolute and relative effects.** A 2x hazard ratio sounds huge but if the absolute event rate is 1%, the absolute risk goes from 1% to ~2%. Both numbers matter.
- **Disclose assumption check results.** If PH was violated, say what you did. If naive KM was used in the presence of competing risks, flag the limitation.
- **Specify the time origin and time scale.** "Time since randomization in days" or "age in years (left-truncated)" — readers can't interpret durations without this.
- **For competing risks: report CIFs, not "1 − KM"**, and report cause-specific hazards separately from subdistribution hazards. They mean different things.

When asked for a specific number (median survival, 1-year survival probability, HR for a specific contrast), give it with a CI. When asked "is X significant," give the effect size and CI first, p-value as supporting detail.

## Worked examples

These show the end-to-end pattern of applying this skill — from user prompt to method selection to reference consultation to response.

### Example 1: SaaS churn analysis with competing exit reasons

**User prompt**: "I have SaaS subscription data — for each customer, when they signed up, when they cancelled (if they did), and whether they cancelled or upgraded to enterprise. About 30% upgraded, 25% cancelled, and the rest are still active. I want to know what predicts cancellation."

**What's happening here**:
- Right-censored: subjects still active have unknown future event times.
- **Two competing events**: cancel and upgrade. They're mutually exclusive (once upgraded, a customer can't "cancel from free tier"). This is a competing risks problem.
- The user said "predicts cancellation" — could mean either the *rate* among still-at-risk customers (cause-specific Cox) or the *cumulative probability* a given customer will eventually cancel (Fine-Gray). These give different answers.

**Approach**:
1. Open `references/competing-risks.md` and `references/r-recipes.md` (or python-recipes.md depending on user stack).
2. Plot Aalen-Johansen CIFs for cancel and upgrade, stratified by candidate predictors. Do NOT use 1 − KM on "cancel" treating upgrade as censoring (overestimates cancel probability).
3. Fit both cause-specific Cox (for cancel) and Fine-Gray subdistribution (for cancel), report both with clear labels.
4. Run Gray's test (not log-rank) when comparing groups on cumulative incidence.
5. Check PH assumption on the cause-specific model.

**Response framing**: "Because some customers upgrade rather than cancel, this is a competing risks problem and the choice of model depends on what you actually mean by 'predicts cancellation'..."

### Example 2: A/B test where treatment effect kicks in late

**User prompt**: "We A/B tested a new onboarding flow. Looking at the Kaplan-Meier curves for 90-day retention, they look almost identical for the first 30 days, then the new flow starts pulling ahead. Log-rank p-value is 0.14. Are we underpowered, or is the treatment not working?"

**What's happening here**:
- A delayed treatment effect is a textbook PH violation.
- Standard log-rank weights all event times equally and loses power against delayed effects — exactly this scenario.
- The conclusion "not working" from log-rank alone could be wrong.

**Approach**:
1. Open `references/nonproportional.md`.
2. Re-test with a weighting that emphasizes late differences: Fleming-Harrington G(0, 1), or MaxCombo if you want to stay agnostic to the pattern.
3. Compute RMST difference at 90 days — gives a clean "extra days retained on average" summary that's interpretable to a non-technical audience.
4. If wanting a regression-style summary, fit Cox with a time-varying coefficient or stratified by time period to characterize how the HR changes.

**Response framing**: "The log-rank p-value is misleading here. Standard log-rank can't see a delayed effect like the one you're describing — positive and negative contributions through follow-up partially cancel. With FH(0,1) weights or MaxCombo, you can test for the pattern you actually see. And the cleanest single-number summary for a non-technical audience is the RMST difference at 90 days..."

### Example 3: Hospital readmissions with death as a competing event

**User prompt**: "I'm modeling 30-day hospital readmission rates. Some patients have multiple readmissions, some die before any readmission. I have a covariate I want to test: whether the patient was discharged on a weekend."

**What's happening here**:
- **Recurrent events**: multiple readmissions per patient.
- **Terminal event (death) that ends the recurrent process**, and is **informative censoring** — sicker patients die and stop generating readmissions, biasing naive readmission-rate estimates.
- "Time to first readmission" Cox would discard most of the information.

**Approach**:
1. Open `references/recurrent-events.md` and `references/multistate-frailty.md`.
2. The right model is a **joint frailty model** (`frailtypack::frailtyPenal` in R) where readmissions and death share a frailty. This handles both the recurrence and the informative censoring by death.
3. If sticking with simpler tools: Andersen-Gill with `cluster(id)` for the readmissions, separately model death, and discuss the informative-censoring caveat explicitly.
4. Plot the mean cumulative function for readmissions by weekend-vs-weekday discharge.

**Response framing**: "Two things make this trickier than a standard Cox on time-to-first-readmission. First, you have multiple events per patient, so a single-event model throws away ~half your data. Second, death is informative censoring for readmissions — patients who die stop generating readmissions for reasons tied to their underlying risk. A joint frailty model handles both..."

### Example 4: Mortality study using age as the time scale

**User prompt**: "I'm comparing mortality between two diet patterns in a cohort of adults. I want to use age as the time scale rather than years-since-enrollment. Just `Surv(age_at_death_or_censoring, dead) ~ diet`, right?"

**What's happening here**:
- Using age as the time scale is fine — often preferable for mortality analyses because age is the dominant time-dependent risk factor.
- But subjects entered the study at different ages. They were not at risk for events at younger ages within the study. This is **left truncation**, and the user's formula ignores it.
- The bias is real and well-known: ignoring left truncation overstates survival at younger ages because nobody who died before their entry age is in the dataset.

**Approach**:
1. Open `references/special-censoring.md` and `references/cox-and-extensions.md`.
2. Correct the formula: `Surv(age_at_entry, age_at_exit, dead) ~ diet`. The first two arguments specify the (entry, exit] interval on the age scale.
3. Sanity check: predicted survival at the youngest entry age in the data should be ~1; survival at older ages descends from there. If the fit gives `S(age 40) = 0.7` when no one in the data was at risk at age 40, something is still wrong.

**Response framing**: "Using age as the time scale is the right call for a mortality study, but the formula needs to handle left truncation — subjects entered the cohort at different ages and weren't at risk for the event at younger ages. The fix is `Surv(age_at_entry, age_at_exit, dead) ~ diet`. Without this, you'd be implicitly assuming everyone was at risk from age 0, which biases the estimates..."

## How to proceed when invoked

1. **Translate the user's framing into a method.** Apply the signals in "Diagnosing what the user is actually asking." The most common errors come from missing a competing risk, missing recurrence, missing left truncation, or accepting a user's framing that's reaching for the wrong tool entirely.
2. **Pick a method from the decision tree.** Don't default to Cox without thinking through whether there are competing risks, recurrent events, or non-PH patterns the user has described.
3. **Open the relevant reference file(s) before writing code.** Don't reconstruct package APIs from memory — function signatures, argument names, and especially the difference between similar-looking estimators (cause-specific Cox vs Fine-Gray; AG vs PWP-TT vs PWP-GT vs WLW; KM with naive censoring vs Aalen-Johansen CIF) are exactly where errors creep in.
4. **If the user has no data and wants a demo, use `synthetic-data.md`** rather than improvising simulation code. The recipes there are matched to the methods they demonstrate.
5. **Run the standard diagnostics.** For Cox, that means `cox.zph` or `check_assumptions` every single time. If diagnostics fail, escalate as described in step 4 of "The workflow."
6. **Report results with the conventions in "Communicating results."** HRs with CIs, absolute and relative effects, time origin specified, assumption-check results disclosed.
