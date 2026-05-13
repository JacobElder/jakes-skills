# ATE vs. ATT: Definitions, Differences, and When It Matters

## The Potential Outcomes Setup

The foundation for both estimands is the **Neyman-Rubin potential outcomes framework**. Every unit *i* has two potential outcomes:

- **Y_i(1)**: the outcome unit *i* would have if treated
- **Y_i(0)**: the outcome unit *i* would have if not treated

The individual treatment effect for unit *i* is the difference Y_i(1) − Y_i(0). This quantity is never directly observable — for any given unit, we only ever see *one* of the two potential outcomes (the "fundamental problem of causal inference"). All population-level estimands are averages over this unobservable quantity.

---

## Precise Definitions

### Average Treatment Effect (ATE)

ATE = E[Y_i(1) − Y_i(0)]

The expectation is taken over **the full population** — everyone, treated and untreated alike. ATE answers: "If we assigned this treatment to a randomly chosen member of the population, what would the expected gain be?"

### Average Treatment Effect on the Treated (ATT)

ATT = E[Y_i(1) − Y_i(0) | T_i = 1]

The expectation is taken only over the **subpopulation that actually received treatment**. ATT answers: "For the people who were actually treated, what was the expected gain from being treated?"

There is also a symmetric estimand, the **Average Treatment Effect on the Untreated (ATU)** (also called ATC — average treatment effect on the controls):

ATU = E[Y_i(1) − Y_i(0) | T_i = 0]

And the **Conditional Average Treatment Effect (CATE)**:

CATE(x) = E[Y_i(1) − Y_i(0) | X_i = x]

which asks how the effect varies across subgroups defined by covariates X.

---

## When ATE and ATT Are the Same

In a **perfectly randomized experiment**, treatment assignment is independent of potential outcomes by construction:

(Y_i(1), Y_i(0)) ⊥ T_i

Under this independence, the people who happen to be treated are a random draw from the full population. Their average potential outcomes mirror the population's. So:

E[Y_i(1) − Y_i(0) | T_i = 1] = E[Y_i(1) − Y_i(0)]

**ATE = ATT in a well-executed RCT.** A simple difference in group means is an unbiased estimate of both simultaneously.

---

## When ATE and ATT Diverge

They diverge whenever **treatment selection is correlated with treatment effect** — that is, when the people who choose (or are assigned) to be treated are systematically different from the overall population in how much they benefit.

This is the norm in observational settings and in any study involving self-selection.

### Example: Job Training Programs

Suppose a voluntary job training program is offered. Workers who expect to benefit most — those who are motivated, have strong baseline skills, or work in industries where training pays off — are more likely to enroll. Their expected gain from training (Y(1) − Y(0)) is above average.

- **ATT** captures the average gain for the people who enrolled. It may be high because enrollees self-selected based on anticipated benefit.
- **ATE** captures the average gain if training were assigned to a random worker from the whole labor pool — including workers who would not normally participate and who might benefit less.

ATT > ATE in this setting. Estimating ATE and reporting it as the program effect would *understate* the benefit for the people the program actually serves. Estimating ATT and applying it to a universal mandate would *overstate* what expanding the program to unwilling participants would achieve.

### Example: Medical Treatment Adoption

Doctors prescribe a drug most heavily to patients whose characteristics suggest they will respond well. Those patients are the treated group. Their expected gain from treatment, E[Y(1) − Y(0) | T = 1], may be larger than the population average. ATT > ATE.

If a policymaker wants to know the effect of mandating the drug for *all* patients — including those currently not prescribed it — ATE is the right estimand. If the question is "was the doctor's prescription decision beneficial for the patients who received it?", ATT is correct.

---

## Why It Matters: Connecting to Policy Questions

The choice between ATE and ATT is not a technical nicety — it reflects a substantive decision about the **policy question being asked**.

### Policy Question 1: Expanding a Program to Everyone

"Should we mandate this treatment / roll this feature out to all users?"

This is an **ATE question**. The relevant comparison is between treating the whole population and treating no one. If the program was previously voluntary or targeted, the untreated population has unknown or lower expected benefit. ATE answers: what happens on average if we apply this to everyone?

Estimating ATE from an observational study is harder because it requires extrapolating potential outcomes to units that were never treated. Methods like doubly robust estimators or causal forests try to do this carefully.

### Policy Question 2: Evaluating an Existing Program for Its Participants

"Did this training program benefit the workers who took it?"
"Should we keep funding this drug program for its current patient population?"

This is an **ATT question**. The relevant counterfactual is: what would have happened to *these same people* if they had not received the treatment? We do not need to estimate what the effect would be on people who were never treated; we only need to understand the treated group.

Estimating ATT is generally **easier** in observational settings because we only need to find valid counterfactuals for the treated group (from among the control group), rather than building a complete model of the entire population's response.

### Policy Question 3: Targeting / Triage

"Who should receive this treatment?"
"Should we show this to high-value users or everyone?"

This is a **CATE question** — heterogeneous effects across subgroups. Neither ATE nor ATT is granular enough. Here you want to know how the effect varies by individual characteristics and use that to personalize the decision.

### Policy Question 4: Regression Discontinuity and IV

These designs typically recover **local** average treatment effects — effects for the subpopulation at the threshold (RDD) or the compliers whose treatment status is changed by the instrument (LATE / CACE for IV). These are neither ATE nor ATT; they are estimands defined by which units are affected by the identification strategy. The question of whether the local estimate generalizes to the population of interest (external validity) is separate from the identification question.

---

## Identification: How Each Estimand Is Recovered

Both ATE and ATT require assumptions to identify from observational data, but they require them over different populations.

**For ATE**, we need:
- **Unconfoundedness / conditional ignorability** for the full population: (Y(1), Y(0)) ⊥ T | X
- **Overlap / positivity** for the full population: 0 < P(T = 1 | X = x) < 1 for all x in the support

The overlap requirement is strict for ATE — we need to be able to estimate counterfactuals for everyone, including units in regions of covariate space where treatment was rarely assigned.

**For ATT**, we need:
- Unconfoundedness only for the treated group: Y(0) ⊥ T | X (we need the control units' potential outcomes to be informative about the treated units' counterfactual under no treatment)
- Overlap only in the treated group's covariate distribution: P(T = 1 | X = x) < 1 for the support of X among the treated

The overlap requirement is weaker for ATT — we only need valid counterfactuals for the people who were actually treated, not for the full population. This makes ATT estimation feasible in settings where there are regions of covariate space populated almost entirely by untreated units.

In **matching estimators**, this distinction maps directly to procedure:
- For ATT: match each treated unit to similar control units. Impute their Y(0) counterfactual and compute the average treated-minus-control gap.
- For ATE: additionally match each control unit to similar treated units and impute their Y(1) counterfactual.

---

## Common Errors

1. **Estimating ATT but claiming ATE.** This is the most common mistake in program evaluation. An observational study follows participants in a voluntary program. It estimates the gain for those who participated. But the report says "the program has a positive effect" as if it would work equally well for everyone.

2. **Confusing ATE in an RCT with the correct policy estimand.** An RCT of a drug in a specific patient population estimates ATE *within that population*. Applying it to a broader population (external validity) requires additional assumptions. The RCT gives internal validity for ATE in the enrolled sample, not unconditionally.

3. **Ignoring effect heterogeneity when it changes the ATE vs. ATT comparison.** If effects are homogeneous (every unit responds the same way), ATE = ATT = ATU. The distinction only becomes operationally important when there is heterogeneity — when who gets treated affects the average effect.

---

## Summary

| | ATE | ATT |
|---|---|---|
| **Definition** | E[Y(1) − Y(0)] over the full population | E[Y(1) − Y(0)] over treated units only |
| **Policy question** | "What if we gave this to everyone?" | "Did this work for the people who got it?" |
| **When equal** | When treatment assignment is independent of potential outcomes (randomized experiment) | Same |
| **When different** | When treatment selection correlates with treatment benefit (self-selection, targeting) | Same |
| **Identification difficulty** | Requires overlap/counterfactuals for full population | Requires overlap/counterfactuals for treated group only — usually easier |
| **Typical use** | Universal policy evaluation, rollout decisions | Program evaluation, retrospective analysis |

The key discipline is to **name the estimand before choosing a method**. The DAG identifies whether any causal effect is recoverable; the potential-outcomes notation specifies precisely which one you are computing. Confusing them leads to valid estimates of the wrong quantity, which is often worse than acknowledging uncertainty.
