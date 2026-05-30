# Generalized Linear Models: Families, Links, and Selection

The skill of GLM choice is matching the **generative structure of the outcome** (its support, its skew, and especially its mean–variance relationship) to a family, then choosing a link that gives the estimand you want. This file builds that intuition and then walks the families.

## Contents
- Exponential family in one idea: the mean–variance relationship
- Link functions and the canonical link
- The families, with selection heuristics
- Overdispersion: the most common real problem
- Zero-inflated vs hurdle
- Retransformation and the log-link estimand
- Marginal vs conditional effects (and non-collapsibility)
- A compact selection guide

## Exponential family in one idea: the mean–variance relationship

A one-parameter exponential-family density can be written

    f(y; θ, φ) = exp{ (yθ − b(θ)) / φ + c(y, φ) }

and the two facts that matter for applied work fall straight out of it:

    E[Y]   = b'(θ) = μ
    Var[Y] = φ · b''(θ) = φ · V(μ)

The **variance function V(μ)** — how the variance changes with the mean — is the fingerprint of each family and the single most useful thing to reason about when choosing one. Normal: V(μ)=1 (variance constant, independent of mean). Poisson: V(μ)=μ (variance equals mean). Gamma: V(μ)=μ² (constant coefficient of variation). Binomial: V(μ)=μ(1−μ). Inverse Gaussian: V(μ)=μ³. φ is a dispersion parameter (fixed at 1 for Poisson and binomial; estimated for normal/gamma).

So "which GLM?" is largely "how does the spread of my outcome grow with its level?" Counts where big means come with big variances → Poisson-like. Positive outcomes where the *relative* spread is roughly constant (a $10 cost and a $10,000 cost both vary by ~20%) → gamma. Bounded 0/1 → binomial. Reasoning about V(μ) is more reliable than reasoning about marginal histograms.

## Link functions and the canonical link

The link g maps the mean to the linear predictor: g(μ) = Xβ. It serves two jobs: keeping μ in its valid range (probabilities in [0,1], counts/rates positive) and defining the **scale on which effects are additive**, which is the estimand.

The **canonical link** is the one for which θ = Xβ directly (logit for binomial, log for Poisson, inverse for gamma, identity for normal). Canonical links have mathematical conveniences (the observed and expected information coincide, sufficiency, clean IRLS) but you are not obligated to use them. The choice should follow the estimand:
- Logistic (logit) link → **odds ratios**. Log link on a binomial → **risk ratios** (log-binomial), often more interpretable for communication, at the cost of convergence difficulties.
- Log link on counts/positives → **multiplicative (rate/ratio) effects**, usually what you want.
- Identity link → additive effects on the natural scale (the linear probability model is exactly this for binary outcomes).

## The families, with selection heuristics

**Logistic regression** — Bernoulli/binomial outcome, logit link, V(μ)=μ(1−μ). Coefficients are log odds ratios. Use for binary or proportion-of-trials data. Watch for **separation** (a predictor perfectly predicts the outcome → MLE diverges to ±∞; fix with Firth penalization or weakly-informative priors). Remember the logistic coefficient is a *conditional* OR and is not collapsible — adding covariates changes it even absent confounding, so conditional and marginal ORs differ by construction.

**Poisson regression** — counts (or rates, with an offset for exposure), log link, V(μ)=μ. The defining assumption is equidispersion (variance = mean). If the mean model is correct, Poisson coefficients are consistent even under overdispersion — but the model-based SEs are then too small. Two robust responses: Poisson with sandwich (robust) SEs, or move to NB/quasi-Poisson.

**Negative binomial** — overdispersed counts, log link, V(μ)=μ + μ²/θ (variance grows **quadratically** in the mean). Arises as a Poisson-gamma mixture (unobserved heterogeneity in rates). The principled likelihood-based fix for overdispersion when you want a full model and AIC/BIC comparisons.

**Quasi-Poisson** — overdispersed counts, log link, V(μ)=φμ (variance grows **linearly**, scaled by an estimated φ). Not a full likelihood (quasi-likelihood); it just inflates Poisson SEs by √φ. NB vs quasi-Poisson is not cosmetic: because the variance functions differ (quadratic vs linear), they **weight observations differently** in estimation — NB downweights high-count observations more. Pick based on which mean–variance pattern the data actually show; check by plotting empirical variance against mean across bins.

**Gamma regression** — positive continuous, right-skewed, log or inverse link, V(μ)=μ² (constant coefficient of variation). Natural for costs, durations, concentrations, insurance claims — anywhere relative variability is stable. With a log link the estimand is log E[Y], avoiding the retransformation problem of log-OLS (below).

**Inverse Gaussian** — positive continuous with even heavier right skew than gamma, V(μ)=μ³. Reach for it when gamma still under-models the tail.

**Beta regression** — outcomes genuinely in the open interval (0,1): proportions, fractions, rates that are *not* counts of successes out of a known number of trials (those are binomial). Models both mean and precision. Needs a transformation for exact 0s/1s (or a zero/one-inflated beta).

**Zero-inflated and hurdle models** — counts with more zeros than the base family predicts; see the dedicated section below.

**Ordinal models** — ordered categories (Likert, severity grades). Proportional-odds (cumulative logit) is standard; its key assumption is that the effect of each predictor is constant across the cut-points (proportional odds). Test/inspect that assumption; if it fails, partial-proportional-odds or multinomial models relax it.

## Overdispersion: the most common real problem

Real count data are overdispersed far more often than not (unobserved heterogeneity, clustering, contagion). Consequences of ignoring it with plain Poisson: **point estimates are usually fine, but SEs are too small and p-values too optimistic** — you over-reject. Detect it by comparing the residual deviance (or Pearson statistic) to its degrees of freedom (a ratio ≫ 1 signals overdispersion), or by binning and plotting empirical variance vs mean. Fixes, in rough order of preference depending on goal: NB (quadratic), quasi-Poisson (linear), or Poisson with cluster/robust SEs. Underdispersion is rarer (often from constrained/bounded processes) and Poisson SEs are then conservative.

## Zero-inflated vs hurdle

Both handle excess zeros, but they encode different stories and you should choose by the science, not the fit statistic:
- **Hurdle:** two stages with a clean split — a binary model for zero vs positive, then a **zero-truncated** count model for the positives. All zeros come from one process ("did the event happen at all?"). Good when zero is a qualitatively distinct state and there is exactly one route to zero.
- **Zero-inflated:** a mixture — a "structural zero" class that can only produce zeros, plus a count component (Poisson/NB) that can *also* produce zeros. Two routes to zero. Good when some units are *never at risk* (structural zeros) while others are at risk but happened to score zero.

Example: counts of cigarettes smoked. Hurdle says everyone either smokes or doesn't, and smokers' counts follow a truncated distribution. Zero-inflation says there are never-smokers (structural zeros) plus current smokers who could report zero on a given day. The substantive question — are there genuine never-users distinct from incidental zeros? — picks the model. And first check whether plain NB already absorbs the zeros; it frequently does, making the extra machinery unnecessary.

## Retransformation and the log-link estimand

A frequent trap: log-transforming Y and running OLS does **not** model the mean of Y. OLS on log Y estimates E[log Y], and exp(E[log Y]) is the **geometric mean**, not E[Y]. Because of Jensen's inequality, naively exponentiating the fitted values underestimates E[Y]; recovering E[Y] requires a smearing/retransformation correction, and that correction depends on the (possibly heteroskedastic) error variance. A gamma (or other) GLM with a log link sidesteps this by modeling log E[Y] directly. So "log-transform vs gamma GLM" is again an estimand distinction (geometric-mean/median-ish effects vs effects on the arithmetic mean), not a matter of taste.

## Marginal vs conditional effects (and non-collapsibility)

In a nonlinear GLM, the coefficient is a **conditional** effect — the effect holding the other covariates fixed, on the link scale — and that is generally **not** the same as the **marginal** (population-averaged) effect, even with no confounding and a correctly specified model. This trips up sophisticated analysts regularly, so it is worth stating cleanly.

- **Non-collapsibility.** The odds ratio (and the hazard ratio) is non-collapsible: adding a covariate that genuinely predicts the outcome will change the coefficient on your variable of interest *even if that covariate is not a confounder and is independent of your variable*. The conditional OR moves away from 1 relative to the marginal OR. So "my odds ratio changed when I added a control" is not, by itself, evidence of confounding — it can be pure non-collapsibility. Risk ratios and risk differences are collapsible; odds ratios and hazard ratios are not. (Linear models are collapsible, which is part of why a linear-probability or log-binomial specification can be easier to interpret across models.)
- **Conditional logistic coefficient ≠ average effect.** A logistic coefficient of 0.7 (OR ≈ 2) is "the effect for a unit at fixed covariate values," not "doubling the odds on average in the population." If the decision-relevant quantity is the average change in probability, compute an **average marginal effect** (average of per-unit predicted-probability differences) or average predicted probabilities under each scenario, with delta-method or bootstrap SEs. Tools: `margins`/`marginaleffects` (R), `margins` (Stata), `marginaleffects` (Python).
- **Which to report.** For mechanism/biology, the conditional effect on the natural scale may be the target. For policy, communication, or anything population-level, the marginal effect / average predicted probabilities are usually what people actually want, and they are collapsible and comparable across specifications. State which one you are reporting; silent ambiguity here causes real misinterpretation.

This is another instance of the skill's core move: "OR vs marginal probability difference" is an estimand choice, not a modeling-quality issue.

## A compact selection guide

| Outcome | Start with | Main thing that breaks it |
|---|---|---|
| Binary / proportion-of-trials | logistic (OR); log-binomial or Poisson+robust SE for RR | separation; non-collapsibility of OR |
| Counts, var ≈ mean | Poisson (log link, offset for exposure) | overdispersion |
| Counts, var > mean | negative binomial (quadratic) or quasi-Poisson (linear) | choosing the wrong variance shape |
| Counts, excess zeros | check NB first; else hurdle (one zero process) or zero-inflated (structural zeros) | misreading the zero mechanism |
| Positive, right-skewed (cost/time) | gamma (log link) or lognormal/log-OLS | retransformation bias for log-OLS |
| Very heavy right tail (positive) | inverse Gaussian | still under-modeling the tail |
| Proportion in (0,1), not counts | beta regression | exact 0s/1s |
| Ordered categories | proportional-odds logit | non-proportional odds |

Treat the table as a starting hypothesis. Confirm by reasoning about V(μ) (plot variance vs mean), checking dispersion, and asking which estimand (OR, RR, rate, arithmetic-mean cost) the analysis is supposed to deliver.
