# ATE vs ATT: Key Differences and When They Matter

## Definitions

### Average Treatment Effect (ATE)

The ATE is the expected effect of treatment for a **randomly selected unit from the entire population**:

```
ATE = E[Y(1) - Y(0)]
```

where Y(1) is the potential outcome under treatment and Y(0) is the potential outcome under control, for a randomly drawn individual from the full population (both treated and untreated).

### Average Treatment Effect on the Treated (ATT)

The ATT is the expected effect of treatment **only among those who actually received treatment**:

```
ATT = E[Y(1) - Y(0) | D = 1]
```

where D = 1 indicates the unit was actually treated. This conditions on the subpopulation that self-selected (or was selected) into treatment.

---

## Why They Differ

ATE and ATT differ whenever **treatment assignment is not random with respect to potential outcomes** — that is, whenever the people who select into treatment are systematically different from those who don't.

**Example — Job Training Program:**

Suppose a job training program is offered, and only people with the lowest earnings potential voluntarily enroll. These individuals might benefit enormously from training (high ATT), but if the program were extended to everyone, high-earners with strong baseline skills might benefit very little. The ATE — averaging over the whole population — would be much smaller than the ATT.

**Example — Medical Treatment:**

Doctors prescribe a drug more often to patients they expect to respond well to it. The ATT captures the effect for those prescribed patients. The ATE would also include patients for whom the drug was never prescribed — possibly because it was contraindicated or expected to be ineffective — and would therefore be lower.

Formally, the gap is:

```
ATE - ATT = E[Y(0) | D=1] - E[Y(0) | D=0]
```

(weighted by treatment probability). If treated units have lower untreated potential outcomes (they would have done worse anyway), ATT > ATE. If treated units have higher baseline outcomes, ATT < ATE.

---

## When the Distinction Matters

### 1. Policy Questions About Targeting vs. Universalization

- **ATT** is the right estimand when you want to evaluate a **program as currently implemented** — you're asking "did it work for the people it actually served?"
- **ATE** is the right estimand when you're considering **extending the program to everyone**, or when you want to evaluate a policy change that would apply universally.

### 2. Selection into Treatment

When treatment is not randomly assigned and participants self-select, treated individuals are typically not representative of the full population. Estimating ATE requires extrapolating effects to untreated units, which is a stronger assumption. ATT only requires overlap and comparability within the treated group.

### 3. Instrumental Variables (IV)

IV estimation typically identifies a **Local Average Treatment Effect (LATE)** — the effect for "compliers" (those whose treatment status is changed by the instrument). This is neither ATE nor ATT but a third estimand. When you care about the effect of a specific policy instrument, LATE may be the most relevant quantity.

### 4. Propensity Score Methods

- **Inverse Probability Weighting (IPW)** can be tuned to estimate either ATE or ATT depending on the weights used:
  - ATE weights: 1/p(x) for treated, 1/(1-p(x)) for controls
  - ATT weights: 1 for treated, p(x)/(1-p(x)) for controls
- **Matching** typically estimates ATT — you find controls that look like treated units, then compare outcomes.

### 5. Overlap / Common Support

Estimating ATE requires that every unit — treated or not — has a nonzero probability of being treated (full common support). ATT only requires that treated units have comparable counterparts in the control group. When overlap is limited, ATT is often more credible to estimate.

### 6. External Validity

If your goal is to generalize findings to a target population that differs from the study sample:
- **ATT** generalizes only to people like those who were treated.
- **ATE** is more relevant if the target population is the general population.
- Neither may be perfectly right; you may need **ATE on the target population (ATO or PATE)**.

---

## Quick Reference

| Feature | ATE | ATT |
|---|---|---|
| Population | Everyone | Treated units only |
| Typical estimators | IPW (ATE weights), doubly-robust | Matching, IPW (ATT weights) |
| Common support required | Full (all units) | Partial (treated units) |
| Best for | Universal policy evaluation | Program evaluation for existing participants |
| Assumption burden | Higher (extrapolation to untreated) | Lower (comparison within treated group) |

---

## Practical Guidance

- If you're evaluating a **voluntary or targeted program** and want to know if it worked for participants, estimate ATT.
- If you're asking whether **expanding** a program to the full population is worthwhile, you need ATE (or careful extrapolation).
- Always state explicitly which estimand your study targets — methods, assumptions, and interpretation all flow from this choice.
- Check overlap: if treated and untreated groups barely overlap in covariate space, ATE estimates will be highly sensitive to model assumptions; ATT may be more robust.
