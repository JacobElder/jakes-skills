# Should You Control for "Attended a Career Fair"?

## The Short Answer

Not necessarily — and the standard advice you cited is **incomplete**. Controlling for a pre-treatment variable simply because it correlates with both treatment and outcome can introduce bias rather than remove it. Whether you should control for "attended a career fair" depends on the **causal structure** of the problem, not just the correlations.

---

## Why the Standard Advice Falls Short

The rule "control for any pre-treatment variable correlated with both treatment and outcome" is a rough heuristic for handling confounders. A confounder is a variable that causally affects both treatment assignment and the outcome. Controlling for true confounders removes omitted-variable bias and is generally correct.

But correlation with treatment AND outcome is a necessary, not sufficient, condition for a variable to be a confounder. A variable can correlate with both for entirely different reasons — and in those cases, controlling for it can open new bias pathways rather than close existing ones.

---

## M-Bias: The Key Risk Here

Your scenario has the hallmarks of a potential **M-bias** (also called collider bias on a pre-treatment variable). Here is one plausible causal structure:

```
U1 (ambition/motivation) ──────────────────────────────► Earnings
        │                                                      ▲
        │                                                      │
        ▼                                                      │
  Career Fair ◄──── U2 (job-seeking behavior/network) ────────┘
        │
        ▼
  Training Program ──────────────────────────────────────► Earnings
```

Or more compactly, the "M" structure:

```
U1 ──► Career Fair ◄── U2
│                       │
▼                       ▼
Training              Earnings
```

In this DAG:
- **U1** (e.g., general motivation or socioeconomic background) drives both attending career fairs and signing up for the training program.
- **U2** (e.g., professional network or active job-seeking) drives both attending career fairs and later earnings.
- **Career Fair** is a **collider** on the path U1 → Career Fair ← U2.

When two arrows point *into* a node, that node is a collider. Colliders have a special and counterintuitive property:

> **Conditioning on a collider opens a spurious path between its causes.**

If you control for "attended a career fair," you condition on a collider. This opens the backdoor path:

```
Training ← U1 → Career Fair ← U2 → Earnings
```

Even if U1 and U2 are independent in the population, conditioning on their common descendant (Career Fair) creates a spurious correlation between them. Now U2 — which is not on the causal path from training to earnings — leaks into your estimate of the training effect, biasing it.

This is called **M-bias** because the full DAG, laid flat, looks like the letter "M":

```
U1    U2
 \  /  \
  CF    Earnings
 /
Training
```

---

## When Is It Safe to Control for Career Fair?

Controlling for Career Fair is safe — and beneficial — only if the true structure is different. For example:

**Scenario A: Career Fair is a genuine confounder**

```
Career Fair ──► Training
Career Fair ──► Earnings (directly)
```

Here Career Fair causes both. Omitting it would bias the training estimate. You should include it.

**Scenario B: Career Fair is purely a proxy for a confounder**

```
U (motivation) ──► Career Fair ──► Training
U ──────────────────────────────► Earnings
```

Here Career Fair is a descendant of U but not a collider. Conditioning on it partially blocks the U → Training → ... backdoor through U. It may be beneficial, but including U directly would be better.

**Scenario C: M-bias (described above)**

Career Fair is a collider between two unmeasured causes. Conditioning on it induces bias. You should **not** include it.

---

## How to Diagnose Your Situation

Since you cannot directly observe the causal structure, use domain knowledge and theory:

1. **Ask: What caused someone to attend a career fair?**
   - If it is mostly the same motivation/background that also drove training sign-up AND those factors independently affect earnings, you likely have Scenario C (M-bias risk).
   - If attending the career fair itself directly caused the person to learn about and enroll in the training program (i.e., career fair → training enrollment), then Career Fair is a mediator or confounder, not a collider.

2. **Ask: Does Career Fair have a direct causal arrow to Earnings, or only indirect ones?**
   - If career fairs improve earnings through networking, job leads, or skill-building that is unrelated to the training program, then U2 likely exists and M-bias is a real concern.

3. **Draw the DAG explicitly.** Write out all variables you believe are causally relevant. Identify every path between Training and Earnings. Apply the backdoor criterion: control only for variables that block backdoor paths *without* conditioning on colliders or their descendants.

---

## The Deeper Principle

The fundamental mistake in the heuristic you cited is conflating **statistical association** with **causal role**. The correct procedure is:

1. Draw a Directed Acyclic Graph (DAG) encoding your causal assumptions.
2. Identify all backdoor paths from Treatment to Outcome.
3. Find a valid adjustment set — a set of variables that blocks all backdoor paths without opening new ones via collider conditioning.
4. Control for that set, and no more.

Adding variables to a regression because they correlate with both treatment and outcome — without checking the DAG — is a recipe for introducing M-bias, overcontrol bias (controlling for mediators), or other structural biases.

---

## Practical Recommendation

Before including "attended a career fair" in your model:

- **Think carefully about whether career fair attendance is a cause of training enrollment or merely correlated with its causes.**
- If career fair attendance was itself part of the pathway through which people enrolled in training, or if it shares unmeasured common causes with earnings (via a separate pathway), treat it as a potential collider and consider leaving it out.
- If you have strong theoretical reasons to believe Career Fair is a direct confounder (it causally affects both enrollment AND earnings independently), then include it.
- When uncertain, sensitivity analysis is valuable: estimate the training effect with and without the variable and assess how much the estimate changes.

---

## Summary Table

| Causal Role of Career Fair | Bias if Omitted | Bias if Included | Recommendation |
|---|---|---|---|
| True confounder (causes both training and earnings) | Omitted-variable bias | None | Include |
| Collider (caused by independent antecedents of training and earnings) | None | M-bias | Exclude |
| Mediator (on the causal path from training to earnings) | None | Overcontrol bias | Exclude |
| Irrelevant (shares no causal paths) | None | Variance increase only | Omit for efficiency |

The mantra "control for pre-treatment correlates of treatment and outcome" is a useful starting point but an unreliable rule. The right question is not "does this variable correlate with treatment and outcome?" but "does conditioning on this variable close backdoor paths without opening new ones?" That question requires a DAG, not just a correlation table.
