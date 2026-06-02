# Assumption-Aware Inference Skill

A skill that makes the agent reason about statistical assumptions the way an experienced methodologist does: starting from *what is being estimated* and *what could go wrong for this specific goal at this specific sample size*, rather than running a checklist of tests and mapping the results to a fixed menu of procedures.

The default failure mode this skill prevents is **assumption policing** — "Shapiro-Wilk rejected, so use Mann-Whitney." A senior statistician almost never reasons that way. They ask: what estimand matters, how does the sampling distribution behave at this n, is the violation large enough to matter, and what do you lose by switching methods? This skill encodes that reasoning.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/assumption-aware-inference
```

Or manually:

```bash
cp -r jakes-skills/assumption-aware-inference ~/.claude/skills/assumption-aware-inference
```

Once installed, the skill applies automatically whenever a question touches statistical testing, regression, or model choice on messy real data — e.g. "is a t-test okay despite skew?", "does large N rescue this?", "OLS vs GLM?", "Poisson vs negative binomial?", "transform, bootstrap, or robust SEs?", "what does this comparison actually estimate?", or any mention of p-values, standard errors, residuals, assumption checks, bootstrapping, clustering, or count/proportion/skewed outcomes.

---

## Example use cases

### "I ran Shapiro-Wilk — the data aren't normal, so I need Mann-Whitney, right?"

> I have two groups, about 80 people each, and I want to compare their average monthly spend. The data are right-skewed (Shapiro-Wilk p < 0.001 for both groups). My team says I must use Mann-Whitney because the data aren't normal. Is that right?

Without the skill, the response validates the team's reasoning and endorses the switch:

> Given that your data are right-skewed and the Shapiro-Wilk test has rejected normality in both groups, switching to the Mann-Whitney U test is indeed the appropriate choice. The Shapiro-Wilk test was significant, indicating that your data don't follow a normal distribution, which is an assumption of the t-test.
>
> The Mann-Whitney test is a non-parametric alternative that doesn't require normality. It tests whether one distribution tends to have larger values than the other... For your business context, you can report the median monthly spend for each group...

With the skill, the response corrects the misconception at the reasoning level:

> Your team has the logic backwards. The t-test does not assume the *data* are normal — it assumes the *sampling distribution of the mean* is approximately normal. At n ≈ 80 per group, the CLT has done that work for you regardless of what Shapiro-Wilk says.
>
> The Shapiro-Wilk test on n = 80 is sensitive enough to detect trivial departures from normality that have no bearing on inference about the mean. A rejection tells you the data aren't perfectly Gaussian — which was never in doubt — not that the t-test is invalid here.
>
> Use Welch's t-test (not Student's, to handle potentially unequal variances without a pretest). Mann-Whitney is fine too, but it estimates a different thing: P(X > Y), not the difference in means. If you care about average spend, Welch is the right tool.
>
> Shapiro-Wilk at n = 80 almost always rejects for real business data. Treating that as a veto on the t-test is the assumption-policing pattern this kind of question is designed to interrogate.

---

### "My n is 2.3 million — do I still have to worry about assumptions?"

> My sample is huge (2.3 million rows). Does that mean I don't have to worry about my regression assumptions anymore?

Without the skill, the response is broadly affirming:

> With 2.3 million rows, your large sample size does provide significant advantages when it comes to certain statistical assumptions. Here's how it helps: The Central Limit Theorem kicks in strongly... normality of residuals becomes less of a concern... estimates become more precise...
>
> That said, there are some assumptions that remain important regardless of sample size: independence of observations... outliers still matter... the linearity assumption...

With the skill, the response draws a sharp line between what large n fixes and what it doesn't:

> Large n buys you one specific thing: the level of your tests is accurate even when the raw data are non-normal, via the CLT. Everything else is either unaffected or made worse.
>
> **What large n doesn't fix:** Dependence/clustering — if observations are correlated within groups, every n in that group is not a new independent observation; the effective sample size is the number of independent clusters, not rows. Confounding/identification — 2.3 million confounded observations give you a precisely estimated wrong number. Model misspecification — a misspecified mean structure just has smaller uncertainty around a biased estimate. Wrong estimand — if you're estimating a mean when you want a quantile, or an unadjusted difference when you want a causal effect, n doesn't help.
>
> **A specific hazard at this n:** Everything will be statistically significant — p < 0.001 for effects of any size. Statistical significance stops being informative and effect sizes, interval widths, and practical relevance become the only meaningful summary.

---

### "My Poisson model is significant — can I report it?"

> Here's my Poisson regression output for daily complaint counts. Coefficients look reasonable and several are highly significant (p < 0.001). Residual deviance = 3,847 on 960 df. Is this okay to report?

Without the skill, the response reviews the output and moves toward reporting guidance:

> Your Poisson regression results look promising overall. The highly significant p-values (p < 0.001) for several coefficients suggest strong relationships in your data. Let me walk you through how to assess and report these results properly...
>
> First, assess model fit: residual deviance of 3,847 on 960 df... the deviance ratio of approximately 4.0 is higher than ideal (we'd want it close to 1.0)... this *might* indicate overdispersion, but it could also indicate model misspecification...

With the skill, the response stops before any reporting guidance:

> Hold on — your model has a serious problem that needs to be fixed before reporting anything.
>
> Residual deviance / df = 3,847 / 960 ≈ **4.0**. In a correctly specified Poisson model, this ratio should be close to 1. A ratio of 4 signals substantial overdispersion: the variance of your counts is roughly 4 times what Poisson assumes (variance = mean). Under overdispersion, Poisson coefficients may be approximately right, but the standard errors are deflated by a factor of about √4 = 2. Every p-value you're reading is far too small — the "p < 0.001" results may not survive a correct standard error.
>
> Your highly significant results may not be significant at all once dispersion is accounted for.
>
> **Fix:** Switch to negative binomial (quadratic variance) or quasi-Poisson (linear variance, same coefficients with inflated SEs). In R: `glm.nb()` or `glm(..., family=quasipoisson)`. In Python: `statsmodels.discrete.discrete_model.NegativeBinomial`. Refit and check the new p-values before drawing any conclusions.

---

## Eval suite

30 analytically graded evaluations covering the core failure modes — assumption policing, estimand confusion, misplaced asymptotics, and procedures that sound rigorous but mislead.

| # | Topic | Key distinction tested |
|---|---|---|
| 1 | Shapiro-Wilk + t-test | Sampling distribution of mean vs raw data; Welch default |
| 2 | Large N | What CLT fixes vs what it doesn't (clustering, confounding, estimand) |
| 3 | Poisson vs NB | Overdispersion; variance vs mean; SE deflation |
| 4 | RCT covariate adjustment | Post-treatment variable bias; pre-specified vs reactive adjustment |
| 5 | Non-normal residuals + heteroskedasticity | HC robust SEs; OLS unbiasedness under heteroskedasticity |
| 6 | Median estimand | Estimand mismatch: t-test vs median; Mann-Whitney location-shift caveat |
| 7 | Complete separation | MLE divergence; Firth penalization |
| 8 | VIF / multicollinearity | SE inflation vs bias; omitted-variable risk of dropping controls |
| 9 | Few clusters (G = 6) | Cluster-level asymptotics; wild bootstrap for few clusters |
| 10 | Continuous proportions | Beta regression vs logistic; successes-out-of-trials distinction |
| 11 | Lord's paradox | ANCOVA vs change scores; causal model dependence |
| 12 | Log-OLS vs gamma GLM | Retransformation/Jensen bias; E[log Y] vs log E[Y] |
| 13 | Linear probability model | LPM vs logistic; estimand (RD vs OR) |
| 14 | Excess zeros | NB vs zero-inflated; structural vs incidental zeros |
| 15 | Pretest workflow | Pretest bias; underpowered/overpowered assumption tests |
| 16 | Clean RCT, large n | Resisting unnecessary complexity; CLT already sufficient |
| 17 | n=300, symmetric | Welch default; proportionate response without over-engineering |
| 18 | Count outcome, n=500k | OLS validity at large n; what GLM adds beyond validity |
| 19 | Bootstrap for max | Bootstrap inconsistency for extreme order statistics; EVT |
| 20 | AUC vs calibration | Discrimination vs calibration; decision relevance |
| 21 | Poisson overdispersion | Deviance/df ratio; SE deflation; NB/quasi-Poisson remedy |
| 22 | Subgroup p-value comparison | Interaction test vs comparing individual p-values |
| 23 | Underpowered significant result | Type M / exaggeration ratio; Type S / wrong-sign risk |
| 24 | Table 2 fallacy | Covariate coefficients ≠ causal effects; confounding set mismatch |
| 25 | Post-selection inference | Stepwise selection invalidates reported p-values |
| 26 | Missing outcome data | MCAR/MAR/MNAR; when complete-case is and isn't valid |
| 27 | Quantile regression | Heterogeneous effects; conditional quantile vs conditional mean |
| 28 | Permutation test assumptions | Sharp null; exchangeability; not assumption-free |
| 29 | Log-transform premise | Estimand change; CLT makes raw-scale OLS valid at adequate n |
| 30 | Non-normal histogram, n=150 | CLT; sampling distribution vs raw data distribution |

---

## Why this skill exists

The base model gives technically correct but practically misleading answers to applied statistics questions. The failure pattern is consistent: it reasons at the level of the raw data distribution rather than the sampling distribution of the estimator, it defaults to the conservative/"safe" choice (nonparametric, transform, GLM) without asking whether that choice is warranted by the data or the estimand, and it validates assumption-checking workflows (Shapiro-Wilk → Mann-Whitney) that statisticians have criticized for decades.

This skill corrects that by encoding the senior-statistician reasoning chain: name the estimand first, locate the violation in the right tier (biases the estimate / only affects the SE / neither), check what asymptotics actually buy at this n, and match the response to the scale of the problem. A clean design at adequate n should get a short "yes, the standard approach is fine, here's why" — confident negation of a non-problem is as valuable as flagging a real one.

## Sources

- Berry, A. C. (1941). The accuracy of the Gaussian approximation to the sum of independent variates. *Transactions of the AMS*, 49, 122–136.
- Box, G. E. P. (1979). Robustness in the strategy of scientific model building. In *Robustness in Statistics* (pp. 201–236).
- Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics*, 90(3), 414–427.
- Gelman, A., & Tuerlinckya, J. (2000). Type S error rates for classical and Bayesian single and multiple comparison procedures. *Computational Statistics*, 15(3), 373–390.
- Gelman, A., & Stern, H. (2006). The difference between "significant" and "not significant" is not itself statistically significant. *The American Statistician*, 60(4), 328–331.
- Grambsch, P., & Therneau, T. (1994). Proportional hazards tests and diagnostics based on weighted residuals. *Biometrika*, 81(3), 515–526.
- Ioannidis, J. P. A. (2008). Why most discovered true associations are inflated. *Epidemiology*, 19(5), 640–648.
- Lin, W. (2013). Agnostic notes on regression adjustments to experimental data. *Annals of Applied Statistics*, 7(1), 295–318.
- Lumley, T., Diehr, P., Emerson, S., & Chen, L. (2002). The importance of the normality assumption in large public health data sets. *Annual Review of Public Health*, 23, 151–169.
- Manning, W. G., & Mullahy, J. (2001). Estimating log models: to transform or not to transform? *Journal of Health Economics*, 20(4), 461–494.
- Westreich, D., & Greenland, S. (2013). The Table 2 fallacy: presenting and interpreting confounder and modifier coefficients. *American Journal of Epidemiology*, 177(4), 292–298.
- White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. *Econometrica*, 48(4), 817–838.
