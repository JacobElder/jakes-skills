# Multiverse analysis — methodology reference

Read this when you need the conceptual grounding: what a multiverse is, how to elicit the
decision set, how to do inference, and how to interpret and report results without
overclaiming. Quick map:

- [Core idea and vocabulary](#core-idea-and-vocabulary)
- [The workflow](#the-workflow)
- [Eliciting the decision set (the hard part)](#eliciting-the-decision-set-the-hard-part)
- [Nonsensical cells and conditions](#nonsensical-cells-and-conditions)
- [Specification curve analysis and inference](#specification-curve-analysis-and-inference)
- [Interpreting results](#interpreting-results)
- [Pitfalls and honest framing](#pitfalls-and-honest-framing)
- [Reporting template](#reporting-template)

## Core idea and vocabulary

Most empirical results depend on data-analytic decisions that are *simultaneously
defensible, arbitrary, and consequential* — how to exclude outliers, how to operationalize
a construct, which covariates to include, which model to fit. A single paper reports one
path and hides the rest. A multiverse analysis (Steegen, Tuerlinckx, Gelman & Vanpaemel,
2016) makes those choices explicit, runs the analysis under *every reasonable combination*,
and reports the whole distribution of results. The goal is transparency and robustness, not
finding a better single estimate.

Use the "tree of analysis" vocabulary (Sarma & Kay):

- **Decision / parameter** — a point in the analysis with more than one defensible option
  (e.g. "outlier rule").
- **Option** — one choice at a decision (e.g. "exclude > 3 SD").
- **Universe / specification** — one complete path: a single option chosen at every
  decision. One universe = one end-to-end analysis = one result.
- **Multiverse** — the set of all universes, i.e. the cross-product of options across
  decisions (minus invalid combinations).

Two flavors that combine: the **data multiverse** (different ways of *processing raw data
into a dataset* — exclusions, coding, transformations; Steegen's emphasis) and the
**modelling multiverse** (different models/estimators/covariates on a given dataset). A full
multiverse crosses both. Related lineage worth knowing: the "garden of forking paths"
(Gelman & Loken), "researcher degrees of freedom" (Simmons, Nelson & Simonsohn), and
"vibration of effects" (Patel, Burford & Ioannidis) all name the same underlying problem.

## The workflow

1. **State the focal question precisely** — the one estimand whose robustness you are
   probing (e.g. "the coefficient on `group`", "the A−B mean difference"). The multiverse
   varies *nuisance* decisions while holding the question fixed.
2. **Enumerate the decisions and their reasonable options** (see next section). Write them
   as a structured list before any code.
3. **Flag invalid / nonsensical combinations** as constraints so they never run.
4. **Implement the analysis once, parameterized by the choices**, then execute every
   universe. Use the bundled `scripts/multiverse.py` engine, or `multiverse`/`specr` in R,
   or `boba`/`specification_curve` in Python (see `tooling.md`).
5. **Summarize the distribution**: specification curve, share of specifications significant
   and in which direction, median effect, and which decisions drive the variance.
6. **Do joint inference** if you want an inferential (not just descriptive) claim.
7. **Report** the full picture, including the decisions you considered and rejected.

## Eliciting the decision set (the hard part)

The engine is trivial; the judgment is in choosing a decision set that is *complete* (no
obvious defensible choice omitted) and *defensible* (no choices a critic would call
unreasonable). When helping someone build a multiverse, actively probe these common
decision families — most analyses have 4–8 live decisions hiding in them:

- **Exclusions**: outlier rules (none / 2.5 SD / 3 SD / IQR / winsorize), attention-check or
  data-quality filters, eligibility windows, missing-data handling (listwise / pairwise /
  imputation).
- **Operationalization of the IV and DV**: which measured variable stands for the construct,
  composite vs single item, raw vs standardized, binary vs continuous coding. *This family
  usually matters most* — Schweinsberg et al. (2021) found that once analysts fixed how they
  operationalized the key variables, the choice of statistical technique and covariates
  mattered far less. Probe operationalization hardest.
- **Transformations**: log / sqrt / none on skewed positives; centering; scaling.
- **Covariates / controls**: which to include, and whether to include interactions.
- **Model / estimator**: OLS vs GLM family, linear vs logistic vs count, fixed vs random
  effects, robust SEs, Bayesian vs frequentist.
- **Sample / subgroup**: full sample vs theoretically motivated subsets.

Two tests for each candidate option, from Simonsohn et al.'s definition of "reasonable":
it should be (1) **consistent with the underlying theory**, (2) **statistically valid**, and
(3) **non-redundant** with options already included. Drop options that fail any of these.
Distinguish **principled** decisions (theory gives a defensible range — include the range)
from **arbitrary** ones (no principled basis — include the common conventions). Do not pad
the multiverse with options nobody would actually defend; a bloated multiverse dilutes the
signal and invites the criticism that you averaged good analyses with bad ones.

## Nonsensical cells and conditions

A pure cross-product will generate combinations that are incoherent — e.g. a linear model
applied to a binary outcome, or an interaction term whose component is absent. Identify
these *before* running and encode them as constraints. In the bundled engine, pass
`constraints=[lambda c: not (c["dv"]=="binary" and c["model"]=="linear")]`. In R's
`multiverse` use the `%when%` operator; in Boba use `@constraint`. Some downstream decisions
are only meaningful conditional on an upstream one (e.g. "which interaction" only applies
when "include interaction" is yes) — encode those as conditions too.

## Specification curve analysis and inference

Specification curve analysis (Simonsohn, Simmons & Nelson, 2020) is the most common way to
present and test a multiverse. Three steps:

1. **Identify** the set of reasonable specifications (the decision elicitation above).
2. **Describe** — the *descriptive specification curve*: plot every specification's point
   estimate sorted from smallest to largest (top panel), with a linked panel below showing
   which option was active in each decision for the specification above it. This reveals
   *which choices* move the estimate. The bundled `specification_curve()` draws exactly this.
3. **Test (joint inference)** — the key question is not "is any single specification
   significant" (with hundreds of specs, some will be by chance) but "is the curve *as a
   whole* inconsistent with the null?" Build a null by breaking the link between the focal
   predictor and the outcome — **shuffle the focal predictor** (permutation under H0) — then
   re-run the entire multiverse on each shuffled dataset. Compare the *observed* test
   statistic to its null distribution. Useful statistics: the **median effect** across
   specifications, and the **share of specifications that are significant in the predicted
   direction**. The p-value is the share of shuffled multiverses at least as extreme as the
   observed. `permutation_test()` in the engine implements this; use ≥500 permutations for a
   reportable result.

If the focal predictor is not orthogonal to the controls, simple shuffling can be too
strong; residualize or shuffle within strata. Note this limitation if it applies.

## Interpreting results

- **Robust effect**: estimates cluster tightly, mostly same sign, large share significant in
  one direction, and joint inference rejects the null. The conclusion does not hinge on
  arbitrary choices.
- **Fragile effect**: estimates straddle zero, sign flips across specifications, only a
  minority significant, joint test non-significant. Honest read: the headline result is
  contingent on specific analytic choices.
- **Which decisions matter**: use `decision_importance()` (η² and median spread per
  decision) to say *which* forks drive the dispersion. "The effect is significant only when
  outliers are not excluded" is the kind of contingency a multiverse exists to surface.

Report the distribution, not a cherry-picked universe — including your own original
analysis's location within the curve.

**Make estimates comparable first.** When decisions change the scale of the estimate — DV
operationalizations with different ranges, raw vs standardized variables, log vs linear — the
raw coefficients are not comparable across universes, and a "scale" decision will swamp the
specification curve and the variance decomposition for reasons that have nothing to do with
robustness. Put every universe's estimate on a common footing (e.g. a standardized
mean-difference or fully standardized coefficient) before plotting or computing
`decision_importance`. A scale-only fork that survives as the dominant decision is usually a
red flag that you compared apples to oranges, not a substantive finding.

## Pitfalls and honest framing

- **Not a p-hacking laundromat.** A multiverse is for assessing robustness and being
  transparent, *not* for selecting the specification you like best. The `specr` authors
  explicitly caution against using it to "arrive at a better estimate." If you only report
  the curve to justify a single chosen path, you have missed the point.
- **Garbage options dilute signal.** Including indefensible specifications and then noting
  "most specs are null" is misleading; so is padding with redundant near-duplicates that
  inflate the apparent robustness. Curate.
- **Combinatorial explosion.** Decisions multiply fast (5 decisions × 3 options ≈ 243
  universes; it balloons). If exhaustive estimation is infeasible, randomly sample
  specifications (`max_universes` in the engine) — Simonsohn et al. endorse drawing a random
  subset for the curve while noting inference should use the full set where possible.
- **Specifications are not independent or equally likely**, so the curve is a sensitivity
  display, not a posterior. Do not treat "% significant" as a probability the effect is real.
- **Non-convergence / errors** in some cells are informative, not noise to hide — report how
  many universes failed and why.

## Reporting template

When writing up, include: the focal estimand; a table of decisions × options with a one-line
justification for each (and notable options you *rejected* and why); the number of universes
(and any sampling); the descriptive specification curve; the share significant and median
effect; the decision-importance summary; the joint-inference result if claimed; and where
the original/preferred analysis sits in the distribution. Share code and the decision spec so
others can re-run or extend the multiverse.
