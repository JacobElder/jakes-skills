# Diagnostics and Model Checking

Diagnostics exist to answer one question: **is the model adequate for the goal?** Not "does it pass a test." This file separates the diagnostics that earn their keep from the ones that are routinely overemphasized.

## Contents
- The triage: what could be wrong and does it matter
- Residual diagnostics
- Leverage and influence
- Overdispersion (count models)
- Calibration (probability models)
- Separation (logistic)
- Multicollinearity — the most overrated diagnostic
- Misspecification checks
- Posterior predictive checks
- What matters most vs what is overemphasized

## The triage: what could be wrong and does it matter

Before running any diagnostic, locate the candidate problem in one of three buckets, because the bucket determines whether you need a different model, a different SE, or nothing:
1. **Mean structure wrong** (nonlinearity, omitted terms, wrong link) → biases the estimates. This is the one that most deserves attention.
2. **Variance/error structure wrong** (heteroskedasticity, overdispersion, correlation) → biases the SEs, not the estimates; fix with robust/clustered SEs or a richer variance model.
3. **A few influential observations** → may drive the whole result; check stability.

Normality of residuals is conspicuously *not* at the top of this list, because for inference about coefficients it matters least (the CLT handles it at adequate n) and only really bites for small-sample exact inference and prediction intervals.

## Residual diagnostics

- **Residuals vs fitted** is the workhorse plot: curvature signals a misspecified mean (the important bucket); a fan/funnel signals heteroskedasticity (the SE bucket). For GLMs use deviance or Pearson residuals, and consider randomized quantile (DHARMa-style) residuals, which are interpretable even for discrete outcomes where raw residual plots are hard to read.
- **QQ plot of residuals** checks normality — relevant mainly for small-n exact inference and for prediction intervals, much less for large-n coefficient inference.
- **Residuals vs each predictor / partial-residual (component+residual) plots** localize where the mean structure is wrong and suggest transformations or added terms.
- **Scale-location** plots make heteroskedasticity easier to see than the raw residual plot.

## Leverage and influence

These are distinct and both matter:
- **Leverage** (the hat value hᵢ) measures how unusual a point's *predictors* are — its potential to pull the fit. High leverage alone is not a problem.
- **Influence** = leverage × discrepancy: how much the fit actually *changes* if the point is removed. **Cook's distance** summarizes influence on all coefficients; **DFBETAs** show influence on a specific coefficient.
The operative question is never "is this an outlier?" but "does any single observation change my conclusion?" Refit without suspect points and see whether the substantive answer moves. If conclusions hinge on one or two points, report that fragility; do not delete points for being inconvenient — deletion needs a substantive, not statistical, justification.

## Overdispersion (count models)

For Poisson models, compare the **Pearson (or deviance) statistic to its degrees of freedom**; a ratio meaningfully above 1 signals overdispersion (variance exceeds the mean). Confirm by binning fitted values and plotting empirical variance against mean to see whether it grows linearly (quasi-Poisson) or quadratically (NB). Consequence of ignoring it: SEs too small, p-values too optimistic. (See `references/glm-families.md`.) Underdispersion (ratio < 1) makes Poisson SEs conservative and is usually less urgent.

## Calibration (probability models)

For a model whose output is a probability or a prediction used in a decision, **calibration is often more important than discrimination** (AUC). A model can have high AUC and still output probabilities that are systematically too extreme or too timid. Check with a **calibration/reliability plot** (predicted probability vs observed frequency across bins) and consider recalibration (Platt scaling, isotonic) if decisions depend on the probability magnitude. Discrimination answers "does it rank cases correctly?"; calibration answers "are the probabilities trustworthy as probabilities?" — and most decisions need the latter.

## Separation (logistic)

**Complete or quasi-complete separation** occurs when a predictor (or combination) perfectly or nearly perfectly predicts the outcome. The likelihood has no finite maximum, so the MLE for that coefficient diverges to ±∞, with absurd estimates and enormous SEs. Signs: a coefficient and its SE both blow up, or convergence warnings. Fix with **penalization (Firth's bias-reduced logistic)** or **weakly-informative Bayesian priors**, both of which yield finite, sensible estimates. Tiny cell counts in categorical predictors are a common cause.

## Multicollinearity — the most overrated diagnostic

High correlation among predictors **inflates the standard errors of the collinear coefficients** and makes them unstable — but it **biases nothing**, does not affect predictions, and does not affect coefficients for variables that aren't part of the collinear set. The reflexive **VIF** screen-and-drop ritual is mostly misguided:
- If the goal is **prediction**, collinearity is essentially irrelevant.
- If the goal is the coefficient on a variable *not* tangled in the collinearity, it is irrelevant to that estimate.
- If the goal is a coefficient that *is* in the collinear set, the honest message is "the data can't separate these effects," which dropping a variable hides rather than solves (and can introduce omitted-variable bias).
Treat collinearity as information about what the data can and cannot identify, not as an assumption to be tested and "fixed."

## Misspecification checks

- **Link / functional-form tests** (RESET, the GLM link test) check whether the chosen mean/link form is adequate.
- **Comparing nested or non-nested models** (likelihood-ratio, AIC/BIC) helps, but fit indices are not estimands — a better AIC does not validate a causal interpretation.
- For dependence, **plot residuals against the suspected grouping/time index**; structure there says the independence assumption (and thus the SEs) is wrong.

## Posterior predictive checks

The Bayesian (and broadly useful) diagnostic: simulate new datasets from the fitted model and ask whether they reproduce features of the observed data that you care about (the proportion of zeros, the tail, the max, group-wise means). A model that cannot generate data resembling the observed data is inadequate regardless of how its parameters look. This generalizes naturally to frequentist simulation-based checks.

## What matters most vs what is overemphasized

**Earns its keep:**
- Influence/stability — does one point or one cluster drive the result?
- Mean-structure adequacy — nonlinearity, omitted terms, wrong link (the bias bucket).
- Overdispersion for counts; calibration for probability models.
- Dependence structure — the thing that silently invalidates SEs and that no n fixes.
- Posterior predictive / simulation checks against features you actually care about.

**Routinely overemphasized:**
- Formal **normality tests** (Shapiro–Wilk) as gatekeepers — underpowered at small n where it might matter, hypersensitive at large n where it doesn't. Look at a QQ plot if you care; don't pretest-and-switch.
- Formal **homoskedasticity tests** (Breusch–Pagan, Levene) as gatekeepers — just use robust SEs.
- **VIF/multicollinearity** screening, for the reasons above.
- p-values of assumption tests in general — they answer "is the assumption *exactly* true" (always no) instead of "is the violation consequential here" (the real question).

The throughline: diagnostics are for judging adequacy against a goal and for finding the violations that change conclusions — not for running a gauntlet of significance tests whose outcomes mechanically dictate the next method.
