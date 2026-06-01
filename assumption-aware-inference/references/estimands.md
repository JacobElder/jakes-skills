# Interpreting Group Comparisons and Estimands

The question "what does this analysis actually estimate?" is more important than "which test should I run." This file covers what bivariate and adjusted comparisons target, and when a contrast supports a causal reading.

## Contents
- What a raw group comparison estimates
- Descriptive vs causal: the identification gap
- Omitted-variable bias and adjustment
- Post-treatment variables, mediators, and colliders
- ANCOVA vs change scores (Lord's paradox)
- Matching vs regression adjustment
- ATE vs ATT and other estimands
- When simple comparisons are exactly right

## What a raw group comparison estimates

A difference in means between two observed groups estimates exactly that: the difference in the conditional mean of the outcome given group membership, *as the groups exist in the data*. It is a **descriptive** contrast. It is confounded by everything that differs between the groups. Calling it "the effect of X" requires an additional, untestable identification assumption — not a distributional one.

This is the most important separation in applied inference: **distributional assumptions** (normality, equal variance, the error structure) govern whether your standard errors and p-values are trustworthy; **identification assumptions** (exchangeability/ignorability, no unmeasured confounding, correct adjustment set) govern whether the number means what you want it to mean. The second class dominates. A beautifully specified GLM with perfect residual diagnostics still answers the wrong question if the contrast is confounded.

## Descriptive vs causal: the identification gap

A contrast is causal only under conditions like:
- **Randomization** (an experiment): the simple difference in means *is* the average causal effect, with no adjustment needed for unbiasedness. This is the cleanest case and the reason RCTs are valued — not because the t-test's assumptions are met, but because exchangeability holds by design.
- **Conditional ignorability** (observational): treatment is as-good-as-random *given* a sufficient set of measured confounders. This is an assumption about the world, never verifiable from the data, and adjustment can only address *measured* confounders.

When a user asks for a causal interpretation of an observational comparison, the right move is to make the identification assumptions explicit (what would have to be true, ideally via a DAG) and consider a sensitivity analysis — not to reach for a fancier estimator.

## Omitted-variable bias and adjustment

Regression adjustment removes confounding from a covariate only if (a) the covariate is measured, (b) it is a genuine confounder (a common cause of treatment and outcome), and (c) its functional form is modeled correctly. The classic OVB formula — bias ≈ (effect of omitted variable on outcome) × (association of omitted variable with treatment) — gives the sign and rough magnitude intuition: an omitted confounder positively related to both inflates the estimate.

Adjustment is not free or always-helpful. Adjusting for the wrong things actively introduces bias (next section). "Control for as much as possible" is not rigor; it is a recipe for collider and post-treatment bias.

## Post-treatment variables, mediators, and colliders

Three ways adjustment backfires:

- **Post-treatment / mediator control.** Conditioning on a variable that is itself affected by the treatment removes part of the causal pathway you are trying to measure, biasing the total effect toward zero (or in unpredictable directions). Example: estimating the effect of a job-training program on income while controlling for whether the person got a job — the job is a mechanism, not a confounder.
- **Collider bias.** Conditioning on a common *effect* of two variables induces a spurious association between them. Selecting the sample on a collider does the same thing (selection bias). This is why "controlling for everything in the dataset" is dangerous: some of those variables are colliders.
- **Bad controls generally.** The adjustment set should be chosen by the causal structure (a confounder is a common cause of treatment and outcome), not by what improves fit or what is available. Variables that lie on the causal path, or that are descendants of the outcome or treatment, should typically be left out.

The practical heuristic: more covariates is not more credible. Each control must be justified as a confounder, not a collider or mediator.

## ANCOVA vs change scores (Lord's paradox)

For pre/post designs, two analyses target different estimands and can disagree:
- **Change score:** regress (post − pre) on group. Asks whether the groups changed by different amounts.
- **ANCOVA:** regress post on group *adjusting for* pre. Asks whether the groups differ at follow-up among units with the same baseline.

Lord's paradox is the observation that these can give opposite signs in observational pre/post data. Which is correct depends on the causal question and the assignment mechanism:
- Under **randomization**, ANCOVA and change-score are both unbiased for the causal effect, but **ANCOVA is more efficient** (it uses the baseline as a covariate to soak up variance) and is generally preferred.
- In **observational** settings where baseline differs systematically by group, the two answer genuinely different questions, and the choice must be driven by the causal model (does conditioning on baseline block a confounding path or open a collider/regression-to-the-mean artifact?). There is no purely statistical resolution; it is an identification question.

## Matching vs regression adjustment

Both are strategies to approximate conditional exchangeability; they differ in where they put their assumptions:
- **Regression** imposes a functional form for how covariates relate to the outcome and extrapolates across regions of poor overlap (which can hide a lack of common support).
- **Matching / weighting** is nonparametric on the design side — it balances covariate distributions before any outcome model — and makes a lack of overlap visible (unmatched units). It is often paired with a regression on the matched sample ("doubly robust").

Neither solves unmeasured confounding; both rely on the same ignorability assumption. The advantage of matching is transparency about overlap and reduced dependence on functional form; the advantage of regression is efficiency and the ability to adjust continuously.

## ATE vs ATT and other estimands

Different methods, and different weightings, target different populations:
- **ATE** — average treatment effect over the whole population.
- **ATT** — average effect among the treated (what matching on the treated, or a difference-in-differences, typically estimates).
- **ATC, LATE/CACE** (complier average causal effect, what IV estimates), **conditional/CATE** effects, marginal vs conditional ORs in nonlinear models.

These can differ substantially under effect heterogeneity. When a user compares estimates from two methods that "should agree," a different target population is a common and underappreciated reason they don't. Always name which population the estimand refers to.

## The Table 2 fallacy

In a multivariable regression with one main exposure and several covariates, it is tempting to report *all* coefficients as the causal effects of each variable. Westreich & Greenland (2013) named this the **Table 2 fallacy**: only the main exposure was designed to have its confounders controlled; the other coefficients don't have that property.

Specifically:
- Each coefficient is a *partial* effect — the association with the outcome holding all other variables constant. This is **not** the total causal effect of that variable on the outcome.
- The model was designed to estimate one causal contrast (the main exposure). The adjustment set was chosen to block confounders of *that* exposure, not of the covariates themselves.
- Some covariates may be mediators or colliders for each other, making their coefficients further uninterpretable as causal effects.
- The non-collapsibility of odds and hazard ratios (conditional vs marginal) makes this worse: the covariate coefficients in a logistic or Cox model have no marginal causal interpretation even under ideal conditions.

The correct language: "adjusting for X in the model for exposure-outcome" vs "the effect of X on the outcome." Only the exposure was designed to support a causal claim; the covariate coefficients are at best descriptive partial associations.

## When simple comparisons are exactly right

Don't over-correct into the belief that raw comparisons are always naive:
- In a **randomized experiment**, the unadjusted difference in means is the unbiased causal effect; covariate adjustment is for precision, not bias.
- As a **transparent description** of the data as it is ("buyers spend more than non-buyers, unadjusted"), a bivariate contrast is honest and useful, provided it is not dressed up as causal.
- As a **baseline / sanity check** before modeling, to see whether adjustment is moving the estimate and to detect overlap problems.

The error is not running a simple comparison; it is mislabeling a descriptive contrast as a causal effect.
