# Survival Analysis Skill

A skill that applies practitioner-grade methodology to time-to-event modeling in R and Python. It gives the agent the conviction to catch the structural errors that standard tools paper over — immortal time bias, naive 1−KM with competing risks, left truncation on age scales, complete separation in Cox PH, standard log-rank failing against crossing or delayed effects — and to give the technically precise, opinionated answer that an applied biostatistician would give instead of validating whatever plan the user already has.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/survival-analysis
```

Or manually:

```bash
cp -r jakes-skills/survival-analysis ~/.claude/skills/survival-analysis
```

Once installed, the skill applies automatically whenever the user asks about time-to-event outcomes, censoring, Kaplan-Meier, Cox regression, hazard ratios, churn modeling, competing risks, recurrent events, or packages `lifelines`, `survival`, `scikit-survival`, `flexsurv`, `cmprsk`, or `mstate`. It also triggers when a user reaches for linear or logistic regression on duration data — a common and silent source of bias.

---

## Example use cases

### "I made a binary covariate for whether patients ever got immunotherapy — HR 0.4, p < 0.001"

> I ran a Cox model on cancer patient survival. My covariate is `received_immuno = 1` if the patient ever received immunotherapy during follow-up. HR = 0.4, p < 0.001. Treatment works!

Without the skill, the response validates the finding and moves to interpretation:

> An HR of 0.4 is a strong protective effect. At any point during follow-up, treated patients had 60% lower instantaneous risk of the event. Make sure you've checked the proportional hazards assumption with `cox.zph()`, but this looks like a meaningful treatment benefit. You might also report the absolute survival difference at 1 and 2 years...

With the skill, the response stops before interpreting the HR:

> There is a serious problem with how this covariate is defined before you can interpret that HR.
>
> **Immortal time bias.** Subjects coded as `received_immuno = 1` had to survive long enough to actually receive the treatment. They couldn't have died during the window between enrollment and therapy delivery. That survival period — before treatment — is being credited to the "treated" group, artificially inflating its survival. The HR of 0.4 is almost certainly not the true treatment effect; it's partly or entirely encoding the selection induced by requiring subjects to survive until treatment.
>
> **Fix: time-varying covariate.** Restructure the data in counting-process format. Each subject contributes rows as `received_immuno = 0` from enrollment up to the treatment date, then as `received_immuno = 1` afterward. Subjects who never received treatment contribute only the `0` rows.
>
> ```r
> # Wrong — baseline covariate
> coxph(Surv(time, status) ~ received_immuno, data = df)
>
> # Right — time-varying covariate via counting process
> # tv_df has columns: id, tstart, tstop, event, received_immuno
> coxph(Surv(tstart, tstop, event) ~ received_immuno + cluster(id), data = tv_df)
> ```
>
> The corrected HR will usually be substantially closer to 1 — sometimes null — depending on how the treatment was allocated. Report this correction before any clinical conclusions.

---

### "Some users uninstall before purchasing — can I treat that as censoring?"

> I'm modeling time from app install to first purchase. Some users churn (uninstall) before ever purchasing — about half. Going to treat uninstall as right-censoring on the time-to-purchase analysis. That's fine, right?

Without the skill, the response accepts the framing with a minor caution:

> Treating uninstall as censoring is the standard approach for this kind of analysis. The main assumption is that uninstallers have the same future purchase probability as still-active users at the same time point — the independent censoring assumption. If that's approximately true (random churn), the KM estimate gives you the purchase probability in a "world without uninstalls." If churn is strongly correlated with low purchase intent, you'll overestimate purchase probability slightly. For a first-cut analysis this is reasonable...

With the skill, the response flags the structural error first:

> Uninstall and purchase are mutually exclusive outcomes — a user who uninstalls can't purchase later. That's a competing risks problem, not a censoring problem, and the distinction matters quantitatively.
>
> When you treat uninstall as censoring, you assume uninstallers have the same latent purchase rate as still-active users at the same point in time. That assumption is almost certainly wrong: users who uninstall are disproportionately low-intent. The 1−KM curve will overestimate the probability that any given install eventually leads to purchase.
>
> **The correct approach depends on your question:**
>
> - *"What drives the rate of purchase among users who haven't uninstalled yet?"* → Cause-specific Cox, treating uninstall as censoring on the purchase hazard. This is etiology — modeling the within-risk-set dynamics.
> - *"What drives the absolute probability a given install will ever purchase?"* → Fine-Gray subdistribution model. This is the question you're probably asking.
>
> Both start with the Aalen-Johansen estimator for cause-specific CIFs — not 1−KM — to describe the cumulative incidence of purchase and uninstall separately. They sum to ≤ 1 plus the probability of still-active; if you use 1−KM for purchase, it can exceed the actual purchase probability substantially.
>
> ```r
> library(cmprsk)
> # status: 0 = censored (still active), 1 = purchase, 2 = uninstall
> cif <- cuminc(ftime = df$time, fstatus = df$status, group = df$arm)
> plot(cif)  # Aalen-Johansen CIFs for both events
>
> # Fine-Gray for "purchase" treating uninstall as a competing event
> crr(df$time, df$status, df[, covariates], failcode = 1)
> ```

---

### "KM curves cross around month 6, log-rank p = 0.62 — no significant difference"

> Our A/B test has 6-month follow-up. The KM curves for treatment vs control look identical for the first 3 months, then the treatment arm starts doing better. But the log-rank p = 0.62. I'm reporting no significant difference.

Without the skill, the response confirms the conclusion:

> Log-rank p = 0.62 is well above any standard significance threshold. With crossing curves this shape it's possible you're underpowered — a sample size calculation might tell you how many more subjects you'd need to detect an effect of this size. But based on current data, there's no significant difference to report...

With the skill, the response identifies why log-rank fails here:

> The log-rank test can't see this pattern. Standard log-rank weights all event times equally: a difference at month 1 counts the same as a difference at month 5. When curves are parallel for the first half of follow-up and then diverge, the early "no difference" contributions partially cancel the late signal, and the test loses power — sometimes completely. A p = 0.62 from log-rank against a delayed-effect pattern is not evidence of no difference; it's evidence that log-rank is the wrong test.
>
> **What to run instead:**
>
> 1. **Fleming-Harrington G(0,1)**: weights later event times more heavily. Directly targets the pattern you're describing.
>
>    ```r
>    library(nph)
>    logrank.test(time = df$time, event = df$status, group = df$group,
>                 rho = 0, gamma = 1)  # FH(0,1) — emphasizes late differences
>    ```
>
> 2. **MaxCombo**: combines G(0,0), G(0,1), G(1,0), G(1,1) with a multivariate normal correction. Power against any pattern without pre-specifying the shape.
>
>    ```r
>    mc <- logrank.maxtest(time = df$time, event = df$status, group = df$group,
>                          rho = c(0,0,1,1), gamma = c(0,1,0,1))
>    print(mc)
>    ```
>
> 3. **RMST difference at 6 months**: the cleanest single-number summary for a business audience. "Treatment added X days of average event-free time over 6 months" — no distributional assumptions, interpretable to anyone.
>
> Report the log-rank p-value as context, but lead with FH(0,1) or MaxCombo and RMST.

---

## What the skill does

The base model knows survival analysis methods. The skill gives the agent the *conviction to apply them correctly*. Its most important moves are:

- **Catch immortal time bias before it contaminates a result.** Time-varying treatment coded as a baseline covariate is one of the most common and consequential errors in observational survival analysis. The skill names it by name and provides the counting-process fix.
- **Block 1−KM and naïve censoring when competing events are present.** Treating one event as censoring on another's time-to-event overestimates cumulative incidence. The skill routes to Aalen-Johansen CIFs and names cause-specific Cox vs Fine-Gray as answering different questions (etiology vs absolute risk).
- **Flag left truncation when age is the time scale.** Subjects entered the study at varying ages; `Surv(age_at_exit, event)` assumes they were at risk since birth. The skill always checks for delayed entry and corrects to `Surv(age_at_entry, age_at_exit, event)`.
- **Redirect from standard log-rank against crossing or delayed effects.** Log-rank cancels out when early and late differences are opposite. The skill names FH(0,1) for delayed effects, MaxCombo when shape is unknown, and RMST as the effect summary that's interpretable under any hazard pattern.
- **Name complete separation before it produces fake output.** `coxph` reports "convergence achieved" with HR near 0 or ∞ and enormous SE. The skill recognizes this symptom, describes why partial likelihood fails, and redirects to Firth-penalized Cox or descriptive reporting.
- **Require PH checking — and enforce the right escalation.** Significant `cox.zph` is not optional. The skill holds the line when users want to "just report the HR anyway," while correctly updating when the residual plot shows a mild deviation in a large sample.
- **Maintain Python-honest claims.** Several methods have clean R implementations but no Python equivalent (joint frailty, Royston-Parmar splines, cluster-robust SEs in Andersen-Gill). The skill flags these as ecosystem gaps rather than offering a broken workaround.

---

## Eval suite

26 prompts across 7 categories, analytically graded. Shipping criteria: ≥ 4/5 on method selection and pitfall detection; all code prompts run; all communication prompts pass; ≥ 5/6 on adversarial cases.

| # | Category | Eval | Trap |
|---|---|---|---|
| A1 | Method selection | Subscription cancellation → logistic regression at 1 year | Pushes back: throws away timing, handles right-censored-before-1-year awkwardly |
| A2 | Method selection | Install-to-purchase with uninstall competing | Flags competing risks; refuses naive censoring treatment |
| A3 | Method selection | Equipment failure, multiple per machine, Cox on time-to-first | Identifies recurrent events; pushes for Andersen-Gill or PWP |
| A4 | Method selection | Using age as time scale in a cohort study | Names left truncation; corrects `Surv(exit, event)` to `Surv(entry, exit, event)` |
| A5 | Method selection | Seroconversion detected at 6-month visits; midpoint used | Identifies interval censoring; redirects to `icenReg::ic_par` |
| B1 | Pitfall detection | Immunotherapy ever-received as baseline covariate; HR 0.4 | Catches immortal time bias; provides time-varying covariate fix |
| B2 | Pitfall detection | Competing event treated as censoring; "same HR as Fine-Gray?" | Explains cause-specific vs subdistribution: different estimands |
| B3 | Pitfall detection | Crossing KM curves; log-rank p = 0.62; "no difference" | Explains log-rank failure; names MaxCombo and FH(0,1) |
| B4 | Pitfall detection | `cox.zph` global p = 0.04 on age; user wants to ignore it | Holds position on PH check; names escalation options |
| B5 | Pitfall detection | RSF SHAP says "plan tier" strongest; team should upgrade everyone | Distinguishes predictive importance from causal effect |
| C1 | Code | R: full Cox script on `survival::lung` with PH check and plot | Script runs; `cox.zph` produced; survival curve plotted |
| C2 | Code | Python: Weibull AFT on rossi; print summary; predict median | `WeibullAFTFitter` used; `print_summary()` and `predict_median()` correct |
| C3 | Code | R: competing risks simulation; cause-specific vs Fine-Gray HRs | Both estimators run; HRs visibly differ |
| C4 | Code | Python: recurrent events; show robust vs non-robust SEs differ | `statsmodels PHReg` with `groups=id` for cluster-robust SEs; point estimates identical, SEs larger |
| D1 | Communication | HR 0.52 (0.37–0.74) — explain to clinical and regulatory audience | Absolute effects supplemented; HR described as instantaneous; PH check cited |
| D2 | Communication | Treatment median survival not reached | "Median not reached"; reports longest follow-up; suggests fixed-time survival + RMST |
| D3 | Communication | C-index 0.78 — is this a good model? | Adds calibration requirement; notes discrimination ≠ calibration |
| E1 | R/Python consistency | Cox on `lung`; HR for age | Both yield ~1.02 (1.00–1.04) |
| E2 | R/Python consistency | Log-rank test for sex in `lung` | p-values agree to numerical tolerance |
| E3 | R/Python consistency | Weibull AFT null simulation; Cox non-significant | Both languages find non-significant result |
| F1 | Adversarial | 14 subjects, 5 events, 4 predictors | Flags EPV 1.25 << 10; refuses before fitting or flags as exploratory only |
| F2 | Adversarial | All treated alive, all untreated dead; fit Cox | Names complete separation; warns fake convergence; redirects to Firth or descriptive |
| F3 | Adversarial | "What's my personal 1-year survival probability?" (patient) | Declines to give personalized clinical prognosis |
| F4 | Adversarial | Tried τ = 365 (p=0.08), 540 (p=0.04), 730 (p=0.09) — report 540? | Identifies p-hacking; mandates pre-specification |
| F5 | Adversarial | Silent-for-30-days users coded as still-active | Flags informative censoring; explains bias direction |
| F6 | Adversarial | Everyone finished a test; model test duration with survival? | Recognizes no censoring; redirects to linear regression |
| G1 | Multi-turn | Free trial: convert / expire / delete — "what makes users convert?" | Identifies competing risks turn 2; in turn 3, correctly notes 14-day fixed window may support logistic regression if censoring is minimal |
| G2 | Multi-turn | User wants to ignore `cox.zph` p = 0.02 on treatment | Holds line through pushback; updates recommendation when residual plot shown to be mild |
| G3 | Multi-turn | Median comparison → individual prediction → "does tenure matter?" | Evolves from descriptive to predictive; handles tenure-heterogeneity without restarting |

**Automated benchmark result (haiku, iter-1)**: 29/29 with skill (100%), 21/29 baseline (72%), **+28pp delta**. Evals run via `survival-analysis/evals/run_evals.py` (baseline vs `--append-system-prompt SKILL.md`). C4 (Python cluster-robust SEs for Andersen-Gill) uses `statsmodels.duration.hazard_regression.PHReg` with `groups=id` in `.fit()` for the sandwich correction — the Python equivalent of R's `cluster(id)`.

---

## Sources

The skill's positions are drawn from:

- **Cox, D. R. (1972).** "Regression models and life-tables." *Journal of the Royal Statistical Society B* 34: 187–220. — The PH model.
- **Kaplan, E. L. & Meier, P. (1958).** "Nonparametric estimation from incomplete observations." *JASA* 53: 457–481. — KM estimator.
- **Nelson, W. (1972).** "Theory and applications of hazard plotting for censored failure data." *Technometrics* 14: 945–966. — Nelson-Aalen cumulative hazard.
- **Fine, J. P. & Gray, R. J. (1999).** "A proportional hazards model for the subdistribution of a competing risk." *JASA* 94: 496–509. — Fine-Gray subdistribution regression.
- **Grambsch, P. M. & Therneau, T. M. (1994).** "Proportional hazards tests and diagnostics based on weighted residuals." *Biometrika* 81: 515–526. — Scaled Schoenfeld residuals, `cox.zph`.
- **Prentice, R. L., Williams, B. J., & Peterson, A. V. (1981).** "On the regression analysis of multivariate failure time data." *Biometrika* 68: 373–379. — PWP models for recurrent events.
- **Andersen, P. K. & Gill, R. D. (1982).** "Cox's regression model for counting processes: a large sample study." *Annals of Statistics* 10: 1100–1120. — Counting-process formulation, AG model.
- **Turnbull, B. W. (1976).** "The empirical distribution function with arbitrarily grouped, censored and truncated data." *JRSS-B* 38: 290–295. — NPMLE for interval-censored data.
- **Royston, P. & Parmar, M. K. B. (2002).** "Flexible parametric proportional-hazards and proportional-odds models for censored survival data, with application to prognostic modelling and estimation of treatment effects." *Statistics in Medicine* 21: 2175–2197. — Flexible parametric survival models, `flexsurv`.
- **Uno, H., Claggett, B., Tian, L., et al. (2014).** "Moving beyond the hazard ratio in quantifying the between-group difference in survival analysis." *JCO* 32: 2380–2385. — RMST as primary endpoint.
- **Therneau, T. M. & Grambsch, P. M. (2000). *Modeling Survival Data: Extending the Cox Model*.** Springer. — Comprehensive reference for the `survival` package.
- **Klein, J. P. & Moeschberger, M. L. (2003). *Survival Analysis: Techniques for Censored and Truncated Data* (2nd ed.).** Springer. — Estimators, diagnostics, competing risks.
- **Beyersmann, J., Allignol, A., & Schumacher, M. (2011). *Competing Risks and Multistate Models with R*.** Springer. — `cmprsk`, `mstate`, multi-state methods.
- **Therneau, T. M. (2024). *A Package for Survival Analysis in R*.** CRAN vignette. — Reference for the `survival` package; `Surv()`, `coxph()`, `cox.zph()`.
- **Davidson-Pilon, C. (2019). *lifelines: survival analysis in Python*.** JOSS 4: 1686. — lifelines package API and limitations.
