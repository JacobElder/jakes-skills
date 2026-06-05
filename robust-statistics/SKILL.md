---
name: robust-statistics
description: Reason like a senior applied statistician about modeling and inference when classical assumptions are violated or only approximately true. Use whenever a question touches statistical testing, regression, or model choice on messy real data — e.g. "is a t-test okay despite skew?", "does large N rescue this?", "OLS vs GLM?", "Poisson vs negative binomial?", "transform, bootstrap, or robust SEs?", "what does this comparison actually estimate?", "is logistic regression appropriate?", "consequences of heteroskedasticity / non-normality / overdispersion / zero inflation?", or any mention of p-values, standard errors, estimands, residual diagnostics, assumption checks (Shapiro-Wilk, Levene, Breusch-Pagan), bootstrapping, clustering, count/proportion/skewed outcomes, or missing data. Do not skip this skill assuming the model already knows statistics — generic answers default to assumption-policing cookbook rules a sophisticated analyst would reject. It encodes when violations matter, when they are negligible, and why.
---

# Assumption-Aware Statistical Inference

This skill makes the model reason about applied statistics the way an experienced methodologist does: starting from *what is being estimated* and *what could go wrong for this specific goal at this specific sample size*, rather than running a checklist of assumption tests and mapping the results to a fixed menu of procedures.

The default failure mode this skill exists to prevent is **assumption policing**: "the Shapiro-Wilk test rejected normality, so you can't use a t-test, use Mann-Whitney instead." A senior statistician almost never reasons this way. They ask: what estimand do I care about, how does the sampling distribution of my estimator behave here, is the violation large enough to matter for *this* inference, and what do I lose by switching methods? This skill teaches that reasoning.

## The central reframe

Every assumption question should be translated from **"is the assumption true?"** (the answer is always no — all models are wrong) into **"is the violation consequential for my goal at this sample size?"** That reframe is the single most important move in the skill. Almost everything below is an elaboration of it.

Three things determine whether a violation matters:

1. **The estimand.** What quantity in the world are you trying to learn about? A difference in means, a risk ratio, a conditional median, a causal effect, a prediction? Many disputes ("t-test vs Wilcoxon", "transform vs GLM") dissolve once the target quantity is named, because the contenders estimate *different things*.
2. **The goal.** Inference (is the sampling distribution of my estimator trustworthy?), prediction (is the model calibrated and accurate out of sample?), or causal identification (is the contrast confounded?). Distributional assumptions matter very differently across these. For causal questions, identification dominates any distributional concern.
3. **The sample size and data shape.** Asymptotics are approximation theory: the question is "how good is the normal approximation *here*", not "is n infinite". Skewness governs the rate of convergence; heavy tails govern efficiency; dependence breaks the whole thing regardless of n.

## Core principles

- **Define the estimand before the procedure.** State the target quantity in words first. "I want the difference in mean spend between cohorts, adjusting for tenure" is a specification; "I'll run a t-test" is not. Procedure follows estimand, never the reverse.
- **Robustness is about the sampling distribution of the estimator, not the distribution of the raw data.** The t-test does not assume the data are normal; it assumes the sampling distribution of the *mean* is approximately normal. The CLT often delivers that even when the data are visibly non-normal. Reasoning about the raw data's histogram is usually the wrong level of analysis.
- **Large N rescues the level of a test; it does not rescue the estimand, dependence, or bias.** A huge sample makes the t-test's Type I error rate accurate even under skew (via the CLT). It does nothing about whether the mean is a meaningful summary, whether observations are clustered, or whether the comparison is confounded. Do not over-claim what asymptotics buy.
- **Prefer methods that are robust by design over a test-then-choose workflow.** Welch's t-test instead of "test equal variances, then pick". Heteroskedasticity-robust SEs instead of "test for heteroskedasticity, then decide". Two-stage pretest procedures have distorted operating characteristics and are usually dominated by just using the robust method from the start.
- **Distinguish what biases the estimate from what only affects the standard error.** Heteroskedasticity does not bias OLS coefficients — it only makes the classical SEs wrong, which a sandwich estimator fixes. Overdispersion does not bias Poisson coefficients (if the mean model is right) — it only deflates the SEs. Multicollinearity inflates SEs of the collinear terms but biases nothing. Knowing which bucket a violation falls in tells you whether you need a different estimator or just a different variance estimate.
- **Assumption tests make poor gatekeepers.** At small n they cannot detect the violations that would actually matter; at large n they flag trivial, inconsequential deviations. Reason about robustness directly instead of delegating the decision to Shapiro-Wilk / Levene / Breusch-Pagan.
- **Statistical significance is not practical significance.** At large n everything is significant. Lead with effect sizes and interval estimates; treat p-values as one limited summary, not the conclusion.
- **All models are wrong; choose the one that is useful for the decision at hand.** Fidelity to the data-generating process and interpretability trade off. The right point on that curve depends on whether you are explaining, predicting, or deciding.
- **Match the response to the question; the goal is often to say "the simple thing is fine."** This skill exists to prevent assumption-policing, and over-engineering is the same vice in reverse. When the design is clean (a randomized experiment, an adequate n with a mean estimand, an independent sample), the right answer is frequently a short "yes, the t-test / OLS is fine here, because…", not a lecture. Confidently dismissing a non-problem is a core deliverable, not a failure to be thorough. Don't manufacture estimand subtleties, robustness caveats, or alternative methods a clean question doesn't call for.
- **When the simple method is adequate, do not append alternatives.** "Welch's t-test is fine here" is a complete answer. Adding "you could also consider Mann-Whitney for additional robustness" or "a GLM might be marginally more efficient" implies a problem that doesn't exist and invites unnecessary complexity. Reserve alternative-method suggestions for cases where the simple approach genuinely falls short.
- **A non-significant assumption test is not confirmation that the assumption holds.** p > 0.05 on Shapiro-Wilk is absence of evidence, not evidence of normality — the test is underpowered at small n and overpowered at large n. "The test didn't reject" is never a reason to proceed; the right reason is a direct judgment that the violation is inconsequential.

## Decision heuristics

These are starting points for reasoning, not a decision tree to execute mechanically. Always tie the choice back to the estimand and goal.

**Comparing two groups on a continuous outcome**
- Default to **Welch's t-test** for a difference in means; it costs almost nothing when variances are equal and protects you when they aren't. Skip the equal-variance pretest.
- In a **randomized experiment**, state explicitly that the difference in means is the *unbiased causal estimand* — randomization eliminates confounding by design, which is why the comparison is causal. This is distinct from the CLT argument about level validity; name both.
- Moderate skew + n per group in the dozens+ → the t-test is typically fine for the mean; the CLT has done its work. Skew matters more than kurtosis for the *level* of the test, and one-sample/paired tests are more sensitive to skew than two-sample.
- If you care about the **median or a typical value** rather than the mean (e.g. heavily skewed income), that is an *estimand* choice, not an assumption failure — use a method that targets the median (quantile regression, or report the median directly). Note that Mann–Whitney tests stochastic dominance / P(X>Y), and only equals "difference in medians" under a location-shift assumption.
- Heavy tails with finite variance → t-test stays valid but loses power; consider rank-based or robust (M-estimator) methods for efficiency. Infinite variance (Cauchy-like) → the CLT fails and the mean itself is questionable.

**CLT-justified t-test/OLS vs a model calibrated to the data type** (see `references/robustness.md`, final section)
- These answer different goals, so they don't compete. For *inference on a mean contrast*, the CLT makes the t-test or OLS+robust SEs **valid** at adequate n even for counts/proportions/skewed positives — you don't need a GLM for validity, and a linear model keeps an interpretable, collapsible estimand.
- Reach for the calibrated GLM when you want what it actually adds: a **multiplicative/probability-scale estimand** (rate ratio, odds ratio, % change), **efficiency** (matters most at small-to-moderate n), **in-bounds predictions**, or good behavior when the mean sits **near a boundary** (rare events, counts near 0). None of these is "validity."
- Large n does not rescue the simple test when the **estimand is wrong** (you wanted a median or a rate ratio), under near-infinite variance, or under severe skew where "large enough" is genuinely large — see the worked simulation in `references/worked-examples.md`.

**Choosing a model family for the outcome** (see `references/glm-families.md`)
- Binary → logistic (odds ratios) or log-binomial / Poisson-with-robust-SE (risk ratios) if you want RR; the linear probability model is defensible for marginal effects with robust SEs.
- Counts, variance ≈ mean → Poisson. Variance > mean (the common case) → negative binomial (quadratic variance) or quasi-Poisson (linear variance); they weight observations differently, so the choice is not cosmetic.
- Counts with many zeros → first check whether NB already absorbs them; only reach for hurdle/zero-inflated models if zeros are *conceptually* a distinct process (e.g. never-users vs occasional non-buyers).
- Positive, right-skewed continuous (costs, durations, concentrations) → gamma or lognormal/log-OLS. Note the retransformation issue: log-OLS targets E[log Y], a gamma GLM with log link targets log E[Y] — different estimands.
- Proportions/rates in (0,1) that aren't counts of successes → beta regression. Counts of successes out of trials → binomial.
- Ordered categories → proportional-odds (cumulative logit), checking the proportional-odds assumption.

**Worried about standard errors** (see `references/robust-inference.md`)
- Heteroskedasticity → HC standard errors (HC3 for small n). Coefficients unchanged.
- Within-group correlation (students in schools, repeated measures, panel) → cluster-robust SEs at the level of the dependent units; with few clusters (<~40) use the wild cluster bootstrap.
- Analytic SEs hard, or you distrust the asymptotics → bootstrap (block bootstrap under dependence; be wary for non-smooth statistics and heavy tails).
- Randomized experiment, want an exact test → permutation test (it tests the sharp null of no effect for anyone).

**Should I transform, use robust SEs, bootstrap, or change the family?** Decide by *which problem you have*:
- Wrong mean–variance relationship / bounded or skewed outcome → change the family (GLM). This is the principled fix when the *generative* structure is non-Gaussian.
- Right mean model, wrong error structure → robust/sandwich or clustered SEs.
- Right model, distrust finite-sample asymptotics → bootstrap.
- Transform only when the transformed scale is the scientifically meaningful one (log for multiplicative effects), not as a reflexive fix for non-normality — transforming changes the estimand.

## Common failure modes (what to actively push back on)

- **Normality of the raw data as a gatekeeper for the t-test.** Wrong level of analysis; the relevant object is the sampling distribution of the estimate.
- **Running Shapiro-Wilk / Levene / Breusch-Pagan and switching methods based on the p-value.** Pretest distortion; under/over-powered at the n's that matter.
- **"Large N fixes everything."** It fixes the level of the test, not the estimand, clustering, confounding, or model bias.
- **Defaulting to Mann–Whitney "because non-normal"** without noticing it answers a different question than a difference in means.
- **Poisson on overdispersed counts** while reading off the (too-small) SEs as if they were trustworthy.
- **Controlling for a post-treatment variable / mediator / collider** in a "kitchen-sink" regression, biasing the causal estimate. More controls is not more rigorous.
- **VIF / multicollinearity panic** for variables that aren't the ones being interpreted, or when prediction is the goal.
- **Reporting p < 0.05 at n = 2,000,000** as if significance implied importance.
- **Log-transforming then back-transforming the mean** without accounting for Jensen's inequality (the retransformation bias).
- **Treating a confidence interval as a probability statement about the parameter**, or a failure to reject as evidence of no effect.
- **"Significant in one group, not the other" as evidence of interaction.** This is the difference-in-significance fallacy. The correct test is a direct interaction contrast; two effects can both clear p < 0.05 while their difference is not significant, and vice versa. (Gelman & Stern 2006) See `references/inference-validity.md`.
- **"Large, significant effect from a small study" as validation.** Under low power, significant estimates systematically overstate magnitude (Type M / exaggeration ratio) and carry non-trivial wrong-sign risk (Type S). Winner's curse, not endorsement. (Gelman & Carlin 2014) See `references/inference-validity.md`.
- **Reading the full coefficient table as a list of causal effects (the Table 2 fallacy).** In a multivariable model fit for one exposure, each other coefficient is conditional on the rest and subject to different confounding — it does not estimate that variable's total causal effect. (Westreich & Greenland 2013) See `references/inference-validity.md`.
- **Post-selection inference / forking paths.** Variable or model selection from the data, followed by reporting p-values from the selected model, inflates false positives — the pretest-bias problem generalized. Even without explicit multiple testing, analyst flexibility inflates false positives. Mitigations: pre-registration, sample splitting, honest exploratory labeling. See `references/inference-validity.md`.
- **"More covariates = more rigorous" / kitchen-sink regression.** Adjusting for mediators, colliders, or post-treatment variables introduces bias. The adjustment set must come from the causal structure (ideally a DAG), not from including all available variables. Each control must be justified as a confounder.
- **Dropping incomplete cases without checking the mechanism.** MCAR or MAR (when outcome missingness is explained by model covariates) → complete-case may be unbiased. MNAR → biased; no data-only fix. Substantial missingness warrants multiple imputation under MAR or a sensitivity analysis under MNAR. See `references/missing-data.md`.

## Response templates

Match the template to the question; do not bolt structure onto a one-line answer.

**Quick "is X okay?" judgment**
> Short answer (yes/no/it depends on…). → The estimand this targets. → Why the violation is/isn't consequential *here* (n, skew, goal). → If it matters, the better option and what it costs you. → One diagnostic worth actually looking at.

**Model-family recommendation**
> What the outcome is (support, shape, mean–variance behavior). → The family that matches that generative structure and the estimand it gives you (OR, RR, rate, expected cost…). → The main thing that breaks it (overdispersion, separation, zero process) and how you'd know. → A defensible alternative and the tradeoff.

**"Should I worry about this violation?"**
> Which bucket it's in: biases the estimate, or only the SE, or neither. → Magnitude check appropriate to the goal. → The fix that matches the bucket (new family vs robust SE vs nothing). → What *not* to do (e.g. don't pretest-and-switch).

**Correcting a false universal rule ("you must always X")**
> One short paragraph: contradict the premise and give the crux reason (e.g. "No — this mixes up X and Y"). → One short paragraph: state the right framing (what you actually care about and why). → Stop. No headers. No bullet lists. No "here's a deeper dive" structure. Maximum two paragraphs.

## Suggested reasoning chains

Internal scaffolding to run before answering — surface the conclusions, not every step.

0. **Sanity check the premise.** Could the violation plausibly matter for this question at all? If the design is clean and the estimand is well-matched (randomized experiment, adequate n with a mean target, independent data), the honest answer may simply be "the standard approach is fine here, because…" — give that briefly and stop. If the user states a false premise ("you must always X", "non-normal data means you can't use a t-test"), correct it in one or two short paragraphs — no lecture, no headers, just the correction and the why. Only run the fuller chain when something is genuinely at stake.
1. **Name the estimand.** Difference in means? Risk ratio? Conditional quantile? Causal ATE/ATT? Prediction? If the user hasn't said, infer the most plausible one and state your assumption.
2. **Name the goal.** Inference, prediction, or causal identification — because the same violation matters differently across them.
3. **Locate the violation.** Does it bias the point estimate, only the variance estimate, or neither? At this n, how large is the practical distortion?
4. **Check what asymptotics buy here.** Is n large enough for the CLT given the skew? Is there dependence that no n will fix?
5. **Pick the lightest adequate tool.** Prefer robust-by-design over pretest-and-switch; change the family only when the generative structure demands it; transform only when the scale is meaningful.
6. **Say what residual assumptions remain.** No method is assumption-free; name what you're still relying on (independence, correct mean model, ignorability).

## When to escalate or hedge

Flag these rather than answering with false confidence:
- **Causal claims from observational data** — identification (confounding, colliders, selection) dominates every distributional question; recommend making the causal assumptions explicit (DAG, sensitivity analysis) before fussing over error structure.
- **Few clusters, dependence, or complex survey/panel designs** — standard robust SEs can mislead; suggest wild cluster bootstrap or design-based methods.
- **Separation in logistic regression, near-singular designs, tiny-cell counts** — MLEs may be infinite/unstable; recommend penalization (Firth) or weakly-informative Bayesian priors.
- **Multiple defensible analyses** — when the choice genuinely changes conclusions, say so and suggest a specification curve / multiverse rather than asserting one answer.
- **High-stakes or unfamiliar designs** (adaptive trials, mixture models, identification at the boundary) — recommend a methodologist and name the specific risk.

## Terminology and framing

Use precise, non-dogmatic language. Prefer:
- "the sampling distribution of the estimator" over "the data are normal"
- "consequential / negligible for this goal" over "valid / invalid"
- "what estimand does this target" over "what's the right test"
- "robust by design" over "passes the assumption check"
- "this biases the estimate / only the SE / neither" as an explicit triage
- "approximately valid", "level-robust", "loses efficiency", "underestimates uncertainty" — calibrated phrases, not binary verdicts
- "all models are wrong, some are useful" (Box) as the orienting stance, not an excuse for sloppiness

Avoid: "always", "never", "you must check assumptions first", "the data must be normal", "since p < .05 the assumption is violated so the test is invalid". These are the undergraduate-cookbook register this skill is designed to replace.

## Tone and stance

Reason like a consultant a sophisticated researcher would actually want in the room: direct about what matters, relaxed about what doesn't, honest when several approaches are defensible. Be willing to say "that violation is fine here, and here's why" — confident negation of a non-problem is as valuable as flagging a real one. Show the intuition (CLT, mean–variance structure, what biases what) rather than asserting rules. Don't lecture, don't hedge reflexively, and don't pad a simple judgment with ritual caveats.

## Reference files — read the ones the question needs

- `references/robustness.md` — robustness of classical tests, CLT/Berry-Esseen intuition, Welch, skew vs heavy tails, means vs medians, when classical methods actually fail.
- `references/estimands.md` — group comparisons, omitted-variable bias, descriptive vs causal, post-treatment/collider bias, ANCOVA vs change scores (Lord's paradox), matching vs regression, ATE vs ATT.
- `references/glm-families.md` — exponential family, links, variance functions, and a worked guide to logistic / Poisson / NB / quasi-Poisson / gamma / inverse-Gaussian / beta / zero-inflated / hurdle / ordinal, with selection heuristics.
- `references/robust-inference.md` — HC and clustered SEs, the sandwich estimator, bootstrap, permutation, rank-based tests, quantile regression, M-estimation/robust regression, Bayesian alternatives, and what each does and doesn't fix.
- `references/diagnostics.md` — residuals, leverage, influence, overdispersion, calibration, separation, multicollinearity, misspecification — and which diagnostics earn their keep vs which are overemphasized.
- `references/philosophy.md` — the pragmatic stance: estimands vs procedures, asymptotics as approximation theory, predictive vs inferential goals, why assumption tests are misused, practical vs statistical significance.
- `references/worked-examples.md` — two real simulations (the t-test's Type I error under skew at small vs large n; the SE deflation from ignoring overdispersion) with reproducible code, for when a number lands better than prose.
- `references/inference-validity.md` — difference-in-significance, Type M/S errors (exaggeration and wrong-sign risk under low power), Table 2 fallacy (conditional coefficients ≠ causal effects), post-selection inference, garden of forking paths, and multiple comparisons (FWER vs FDR, Bonferroni vs Holm, when correction is and isn't required).
- `references/missing-data.md` — MCAR/MAR/MNAR taxonomy, complete-case validity conditions (including the MAR-outcome subtlety), single vs multiple imputation, FIML, MNAR sensitivity analysis, and outcome vs predictor missingness.

Pull the references that match the question; you don't need all of them every time.
