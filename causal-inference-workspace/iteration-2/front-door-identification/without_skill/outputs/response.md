# Does an Unmeasured Confounder Make the Training-Performance Effect Unidentifiable?

## Short Answer

No — the effect is not necessarily unidentifiable. Your setup describes precisely the conditions under which the **Front-Door Criterion** (Judea Pearl, 1995) applies. If those conditions hold, you can identify the causal effect of training on performance ratings even though the confounder "ambition" is never measured.

---

## The Causal Structure You Are Describing

Your problem maps onto a specific directed acyclic graph (DAG):

```
Ambition (U) -------> Training (X) --> Skills Applied (M) --> Performance Rating (Y)
     |                                                                ^
     +----------------------------------------------------------------+
```

More precisely:

- **U** (Ambition): unmeasured common cause. It causes who gets sent to training (X) and also directly affects performance ratings (Y) through a back-door path that cannot be blocked by conditioning.
- **X** (Training): the treatment of interest.
- **M** (Skills Applied on the Job): a mediator — it sits on the causal path from X to Y.
- **Y** (Performance Rating): the outcome.

The key structural features are:
1. X → M → Y is the causal pathway from training to performance.
2. U → X and U → Y create a confounded back-door path between X and Y.
3. There is **no direct arrow from U to M** — ambition affects whether someone gets trained, but ambition itself does not directly determine whether the training content shows up in daily work (that is caused by whether training occurred).
4. There is **no back-door path between M and Y that is unblocked** — once you hold X fixed, conditioning on X blocks the path M ← X ← U → Y.

---

## Why the Front-Door Criterion Saves You

The front-door criterion states that you can identify the causal effect P(Y | do(X)) if you can find a mediator M such that three conditions hold:

**Condition 1 — X affects Y only through M:**
All causal paths from X to Y pass through M. In your case this means training has no direct effect on performance ratings except by causing employees to apply skills on the job. If training changes performance through some other channel not captured in M (for example, managers rewarding training completion as a signal independent of behavioral change), this condition is violated.

**Condition 2 — No unblocked back-door path from X to M:**
There is no unmeasured confounder that simultaneously causes X and M. Ambition causes who gets trained, but does it independently cause skill application? If ambitious employees would apply new skills regardless of whether they were trained — meaning ambition directly affects M — this condition fails and the front-door criterion cannot be applied.

**Condition 3 — All back-door paths from M to Y are blocked by conditioning on X:**
Once you control for training status, the remaining variation in skills applied is not confounded with performance. This is satisfied because the only path from U to M runs through X (U → X → M), so conditioning on X closes that path.

When all three conditions hold, the front-door formula identifies the causal effect from observational data alone:

```
P(Y | do(X)) = Σ_m P(M=m | X) · Σ_x' P(Y | X=x', M=m) · P(X=x')
```

In plain language: first estimate how training affects skill application (X → M, which is unconfounded by construction); then estimate how skill application affects performance holding training constant (M → Y | X, which is unconfounded after conditioning on X); finally combine these two estimable relationships using the observed distribution of training.

---

## The Key Intuition

Why does this work? The unmeasured confounder creates a problem because it confounds the total X → Y relationship. But you never need to estimate X → Y directly. Instead, you route identification through two clean pieces:

- X → M is unconfounded because ambition has no direct path to M.
- M → Y is unconfounded after conditioning on X, because conditioning on X closes the back-door path through U.

You are using the mediator as a bridge that lets you walk around the confounded link entirely.

---

## The Critical Assumption to Scrutinize

The most likely place this breaks down in your setting is **Condition 2**: does ambition directly cause "skills applied on the job," independent of whether the person received training?

- If ambitious employees are more likely to seek out and apply new skills *regardless* of formal training, then U → M exists. The front-door formula no longer holds, because there is now a back-door path X ← U → M that is unblocked.
- In that case, you would need an alternative identification strategy — for example, an instrument for training assignment that breaks the U → X link, or a natural experiment.

If, however, "skills applied" is a relatively direct mechanical outcome of the training content being delivered and absorbed — meaning without training, employees would not have had access to those specific skills to apply — then the U → M arrow is absent and the front-door criterion holds.

---

## When the Approach Fails

The front-door identification strategy breaks down if any of the following are true:

- Training improves performance through a channel that bypasses skill application (e.g., credentialing effects, manager favoritism toward trained employees) — violates Condition 1.
- Ambitious employees apply new skills more diligently even absent training, creating a direct Ambition → Skills Applied path — violates Condition 2.
- There are additional unmeasured variables that confound the M → Y relationship after conditioning on X — violates Condition 3.
- The "skills applied" measure is a noisy proxy for actual behavioral change rather than a genuine mediator.

---

## Practical Estimation

If the conditions hold, you can estimate the front-door formula in several ways:

1. **Two-stage regression (linear case):** Regress M on X in the first stage. Regress Y on M and X in the second stage. The product of the two coefficients gives the identified causal effect of training through skill application. This is the product-of-coefficients mediation estimator, but here it carries a full nonparametric causal justification.
2. **Structural equation modeling (SEM):** Specify the two-equation system explicitly and estimate simultaneously.
3. **Nonparametric plug-in:** Use the full front-door formula above with empirical conditional probabilities — appropriate for discrete variables or with kernel/regression methods for continuous ones.

---

## Summary

| Question | Answer |
|---|---|
| Does the unmeasured confounder make the effect unidentifiable in principle? | Not necessarily — the front-door criterion may apply. |
| What is required? | M must fully mediate X → Y; M must not be directly caused by U; M → Y must be unconfounded after conditioning on X. |
| What is the key substantive assumption to check? | Does ambition independently cause skill application, or only through training? |
| If the criterion holds, can you estimate the effect from observational data? | Yes, using the front-door formula without ever measuring ambition. |

The unmeasured confounder is a serious threat, but your mediator variable gives you a viable identification path that does not require measuring ambition at all — provided the structural assumptions about how ambition relates to skill application hold in your empirical context.
