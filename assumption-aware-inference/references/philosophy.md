# Statistical Philosophy and Pragmatism

The stance that ties the rest of the skill together. These are not abstractions; they change what answer you give.

## Contents
- "All models are wrong, some are useful"
- Robustness vs exact correctness
- Estimands before procedures
- Asymptotics as approximation theory
- Predictive vs inferential vs causal goals
- Why assumption tests are misused
- Practical vs statistical significance
- Interpretability vs fidelity

## "All models are wrong, some are useful"

Box's line is the operating premise, not a disclaimer. No assumption is ever exactly true — errors are never exactly normal, variances are never exactly constant, links are never exactly right. If "is the assumption true?" were the question, every analysis would fail. The useful question is always **"is this model good enough for the decision I'm making, and where would its wrongness bite?"** Usefulness is judged against a purpose, so you cannot evaluate a model without first knowing what it is for. This reframing dissolves most assumption anxiety: the goal is adequacy for a purpose, not fidelity to an unattainable ideal.

## Robustness vs exact correctness

There is a genuine tradeoff between procedures that are *exactly* optimal under narrow ideal conditions and procedures that are *approximately* valid across a wide range. Classical methods (Student's t, model-based GLM SEs) are exact under their ideal conditions and can degrade when those fail. Robust methods (Welch, sandwich SEs, the bootstrap) sacrifice a sliver of efficiency under the ideal in exchange for far better behavior when the world is messier — which it always is. For applied work the wider basin of validity is almost always worth the small efficiency cost, which is why "robust by design" beats "test the assumption, then choose." Robustness is not a synonym for "ignore assumptions"; it is a deliberate purchase of insurance against the assumptions you cannot verify.

## Estimands before procedures

Many apparent statistical disputes are estimand confusions wearing procedural clothing:
- "t-test vs Mann–Whitney" → difference in means vs stochastic ordering.
- "log-OLS vs gamma GLM" → effect on the geometric mean vs the arithmetic mean.
- "ANCOVA vs change score" → outcome-at-follow-up-given-baseline vs amount-of-change.
- "OR vs RR vs risk difference" → three different contrasts, none more "correct" absent a decision context.

Define the target quantity in words first, and the procedure debate often resolves itself. A procedure is a way to estimate an estimand; arguing about procedures without naming the estimand is arguing about means to an unspecified end. The modern causal-inference framing — estimand, then identification, then estimation — is the right order of operations for inferential and causal work alike.

## Asymptotics as approximation theory

"Asymptotically normal/valid" is not a promise that holds only at n = ∞; it is the claim that the finite-sample distribution is *approximated* by the limit, with an error that shrinks at a known rate. The applied question is therefore quantitative — "how good is the approximation at *my* n, given *my* skew?" — answerable via Berry–Esseen intuition (error ∝ skewness/√n), simulation, or the bootstrap. Reading asymptotic results as binary ("only valid for large n") misses their actual content, which is a statement about *how fast* and *how well*. Equally, asymptotics can be invoked too freely: the relevant n for clustered data is the number of clusters, and dependence or infinite variance can prevent convergence at any n.

## Predictive vs inferential vs causal goals

The same assumption violation has different consequences depending on the goal, and the goal should set the diagnostics:
- **Prediction:** what matters is out-of-sample accuracy and calibration. Collinearity is irrelevant, "statistical significance" of coefficients is beside the point, and the test is held-out performance.
- **Inference (about a parameter):** what matters is the sampling distribution of the estimator — so the error/variance structure and the SEs are central, while the raw data's normality is mostly not.
- **Causal:** identification dominates everything. No distributional fix rescues a confounded contrast; the assumptions about *which variables to adjust for* (confounders, not colliders or mediators) matter more than any error-structure assumption.

Stating the goal first prevents importing prediction-world worries (or significance rituals) into a causal question, and vice versa.

## Why assumption tests are misused

Formal tests of assumptions (Shapiro–Wilk, Levene, Breusch–Pagan) as gatekeepers fail on three counts:
1. **Wrong question.** They test "is the assumption *exactly* true," whose answer is essentially always no. They don't measure whether the violation is *consequential*.
2. **Sample-size pathology.** At small n they are underpowered — they miss the violations large enough to matter. At large n they are overpowered — they reject trivial, harmless deviations. So they are least informative exactly when you most need a decision.
3. **Pretesting distorts the final inference.** "Test, then choose a procedure based on the result" makes the *final* test's level and coverage depend on a random first stage, with operating characteristics worse than just committing to the robust method. The cleaner path is to reason about robustness directly and/or adopt robust-by-design methods, looking at graphical diagnostics for magnitude rather than treating an assumption-test p-value as a switch.

## Practical vs statistical significance

With enough data, every effect is "statistically significant" and every assumption test rejects, because significance conflates effect size with sample size. Lead with **effect sizes and interval estimates** on an interpretable scale; treat the p-value as one limited summary of evidence against a specific null, not as the result. Conversely, a non-significant result is **not** evidence of no effect — absence of evidence is not evidence of absence — and "p > .05 so the assumption holds" is the same error applied to a diagnostic. Frame conclusions in terms of magnitude, direction, and uncertainty.

## Interpretability vs fidelity

There is a real frontier between models that mirror the data-generating process faithfully and models a stakeholder can understand and act on. A linear probability model is less faithful than logistic but yields directly interpretable marginal effects; a flexible machine-learned model may predict better but resist explanation. The right point on the frontier depends on the goal: for a high-stakes causal claim, interpretability and defensible identification usually win; for a pure prediction pipeline, fidelity/accuracy wins. Name the tradeoff explicitly rather than pretending one model dominates on every axis — and remember that a more complex model is not automatically more correct, only more flexible.

## The throughline

Good applied statistics is judgment about consequences, organized around a clearly stated estimand and goal, using methods whose remaining assumptions you can defend — not a ritual of checking assumptions and looking up the corresponding test. Confidence to say "that violation doesn't matter here, and here's why" is as much a part of the craft as flagging the violations that do.
