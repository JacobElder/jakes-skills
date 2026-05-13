# Causal Analysis: Technical Skills Training and Performance Ratings

## 1. Name the Rung

This is a **Rung 2 (Intervention)** question: "Does sending employees to technical skills training cause higher performance ratings?" You're not asking what training attendance predicts — you're asking what would happen if you intervened on training participation. The gap between your data (observational) and the question (interventional) is the core identification challenge. Observational data alone, however large, cannot bridge this gap without additional causal assumptions — but those assumptions may be available to you.

---

## 2. Sketch the DAG

Here is the structure you've described:

```
Ambition (U) ───────────────────────────────────────┐
     │                                               ↓
     ↓                                        Performance (Y)
Training (X) ──→ Skills Applied on Job (M) ──→ Performance (Y)
```

More precisely:

- **U (Ambition)** is an unmeasured common cause: it causes both **X** (selection into training) and **Y** (performance ratings) independently.
- **X (Training)** is the treatment.
- **M (Skills Applied on Job)** is a measured mediator: it sits on the causal path from X to Y, capturing whether training content actually shows up in daily work.
- **Y (Performance Ratings)** is the outcome.

The unobserved fork `U → X` and `U → Y` creates an open back-door path: `X ← U → Y`. This is the confounding you're worried about.

---

## 3. Identify the Structure

**Back-door paths from X to Y:**

The path `X ← U → Y` is a back-door path — it runs from X backward through the confounder U to Y. Because U is unobserved, you cannot block this path by conditioning on U directly. Back-door adjustment fails.

**But ask the front-door question before concluding "not identifiable."**

The skill's identification strategy explicitly instructs: *before concluding "not identifiable," ask — is there an observed mediator between X and Y whose own back-door paths to Y are all blockable?*

Check the three conditions for front-door identification:

1. **M is on the causal path from X to Y.** Yes — "Skills Applied on Job" is causally downstream of training and upstream of performance.
2. **There is no unblocked back-door path from X to M.** The question here is: does Ambition also directly cause M, independent of Training? If ambitious employees apply skills whether or not they attend training, then `U → M` exists, and M has its own open back-door path that runs through U. **This is the critical assumption to interrogate.** If you believe that Ambition drives skills application *only through* causing people to attend training — and not directly — then there is no direct `U → M` arrow, and condition 2 holds.
3. **All back-door paths from M to Y are blocked after conditioning on X.** The path `M ← X ← U → Y` is a back-door path from M to Y. You can block it by conditioning on X — which is observed. So condition 3 holds.

**If conditions 1–3 hold**, the front-door criterion is satisfied and the effect of Training on Performance is **identifiable from observational data**, despite the unmeasured confounder.

---

## 4. The Front-Door Estimator

Under the front-door criterion, the causal effect P(Y | do(X)) is identified by the following two-stage procedure:

**Stage 1:** Estimate the effect of Training (X) on Skills Applied on Job (M).

Because X has no unblocked back-door paths to M (by assumption 2), this is identified directly from the observational distribution:

```
P(M | do(X)) = P(M | X)
```

**Stage 2:** Estimate the effect of Skills Applied on Job (M) on Performance (Y), controlling for X.

The back-door path from M to Y via U runs through X (specifically `M ← X ← U → Y`), so conditioning on X blocks it:

```
P(Y | do(M)) = Σ_x P(Y | M, X=x) · P(X=x)
```

**Composing the two stages:**

```
P(Y | do(X)) = Σ_m P(M=m | X) · Σ_x' P(Y | M=m, X=x') · P(X=x')
```

In plain English: for each value of training, compute the predicted distribution of skills application; then for each level of skills application, compute the performance outcome after averaging over the marginal distribution of training status. The double averaging is what cancels out the confounding by U.

---

## 5. The Critical Assumption and How to Stress-Test It

The entire identification rests on **condition 2: Ambition has no direct effect on Skills Applied on Job that bypasses Training.** This means the only way ambition feeds into on-the-job skills application is by causing employees to attend training in the first place.

This assumption is substantively falsifiable. Ask:

- Would a highly ambitious employee who *did not* attend training still apply more advanced technical skills on the job than a low-ambition employee who also skipped training? If yes, there is a direct `U → M` path and the front-door criterion fails.
- Is "Skills Applied on Job" measured in a way that captures *training-specific* content, or does it pick up general industriousness and initiative? If the measure is broad, it likely reflects Ambition directly — a violation.
- Could ambition cause employees to seek *other* forms of skill development (self-study, peer learning) that feed into M independently of X? If so, the path `U → M` is open.

The more tightly M is defined as "application of the specific content from the training program," the more plausible the assumption becomes. A generic "employee applies skills" measure will almost certainly reflect Ambition directly and violate the criterion.

---

## 6. Structural Role of "Skills Applied on Job"

Explicitly: what structural role does M play, and what are the consequences of different classifications?

| Assumed structure | Consequence for M |
|---|---|
| M is a pure mediator with no direct U → M path | Front-door criterion satisfied; effect identifiable without experiment |
| M has a direct U → M path (ambitious employees apply more skills regardless of training) | Front-door fails; effect not identified by front-door alone |
| M is also a collider between X and some other variable | Conditioning on M opens spurious paths — don't condition naively |

**Do not control for M in a standard regression attempting to estimate the total effect of X on Y.** M is a mediator. Including it as a covariate blocks the very causal path you're trying to measure and would give you the *direct* effect of training that does not run through skills application — which is likely near zero or mechanically undefined.

---

## 7. What If the Front-Door Assumption Fails?

If Ambition does directly cause Skills Applied on Job — front-door identification fails. Your remaining options:

- **Instrumental Variable.** Find a variable Z that causes training participation (X) but has no direct effect on performance (Y) and doesn't share unmeasured causes with Y. Candidates: an employer-side policy that quasi-randomly assigns some employees to training slots (a lottery, a mandatory training rotation, a capacity constraint), geographic proximity to training facilities, or a manager's propensity to nominate employees.
- **Regression Discontinuity.** If training eligibility is determined by a performance score threshold, seniority cutoff, or role classification threshold, the sharp discontinuity can identify a local average treatment effect for employees near the boundary.
- **Differences-in-Differences.** If training rollouts happened at different times for different departments or cohorts, and if pre-trends are parallel, DiD can absorb stable confounding — though it won't absorb time-varying ambition.
- **Experiment.** Randomly assign employees to training. Ambition becomes irrelevant — it's balanced across conditions by design.
- **Acknowledge non-identification.** If none of these are available, the honest answer is that the effect cannot be identified under your current design. The direction of bias (positive, since ambitious employees both attend training and perform better) is predictable — your observed Training-Performance association overstates the true causal effect — but the magnitude of bias is not estimable from the data alone.

---

## 8. Most Likely Trap to Flag

**The collider conditioning trap on M.** Once you correctly recognize M as a mediator, there will be pressure to "control for it" to understand whether training works "beyond just changing behavior." Resist this. If you condition on M to estimate a direct effect of X on Y that bypasses M, you will also condition on a descendant of X, which can open spurious paths and bias the estimate unpredictably. If a direct effect is the scientific target, restructure the mediation analysis explicitly (using proper mediation analysis methods) rather than naively adding M as a covariate.

---

## Summary

No — the unmeasured confounder (Ambition) does not automatically make this effect unidentifiable. The front-door criterion offers a path to identification using your observed mediator M, *provided* that Ambition does not have a direct effect on Skills Applied on Job that bypasses Training. Whether that assumption holds is an empirical and substantive judgment, not a statistical one. The tighter and more training-content-specific your measure of M is, the more credible the identification. If the assumption is questionable, the next-best move is to search for an instrument or a design-based source of variation in training assignment.
