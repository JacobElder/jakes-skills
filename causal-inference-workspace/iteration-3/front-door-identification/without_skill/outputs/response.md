# Does the Unmeasured Confounder Make the Effect Unidentifiable?

**Short answer: No — but only if your mediator variable satisfies three strict conditions. If those hold, you can use the Front-Door Criterion to identify the causal effect of training on performance ratings despite never measuring ambition.**

---

## The Causal Structure You Are Describing

Let's name the variables:

- **T** = Technical skills training (treatment)
- **M** = Skills applied on the job (mediator)
- **Y** = Performance ratings (outcome)
- **U** = Ambition (unmeasured confounder)

The directed acyclic graph (DAG) looks like this:

```
U ──────────────────────────┐
│                            ▼
└──► T ──► M ──► Y ◄────── U
```

More precisely:
- U → T (ambitious employees are more likely to be selected for, or self-select into, training)
- U → Y (ambitious employees earn higher performance ratings regardless of training)
- T → M (training causes employees to apply new skills on the job)
- M → Y (applied skills cause higher performance ratings)
- There is NO direct path U → M (ambition does not independently determine whether training content shows up in daily work, beyond its effect through T)
- There is NO direct path T → Y that bypasses M (training only affects performance *through* the application of skills)

This is precisely the structure that Pearl's **Front-Door Criterion** was designed to handle.

---

## Why the Confounder Alone Does Not Make the Effect Unidentifiable

The standard omitted-variable/confounder problem blocks identification because the backdoor path T ← U → Y cannot be closed without conditioning on U (which you cannot observe). Naively regressing Y on T would conflate the causal effect of training with the selection effect of ambition.

However, identification does not always require blocking backdoor paths directly. The Front-Door Criterion exploits the mediator M to construct a two-step identification strategy that sidesteps U entirely:

**Step 1 — Identify the effect of T on M.**
The path T → M has no backdoor path that passes through U, *because U does not directly cause M*. The only path from U to M runs through T, and that path is blocked when you condition on T. Therefore, the causal effect of training on skill application is identified from observed data:

> P(M | do(T)) = P(M | T)

**Step 2 — Identify the effect of M on Y, controlling for T.**
The path M → Y does have a backdoor path: M ← T ← U → Y. But here, T is *observed*, so you can condition on T to block this backdoor. Within levels of T, the association between M and Y is causal:

> P(Y | do(M)) = Σ_t P(Y | M, T=t) · P(T=t)

**Step 3 — Chain the two steps together.**
The Front-Door formula combines these:

> P(Y | do(T)) = Σ_m P(M=m | T) · Σ_t' P(Y | M=m, T=t') · P(T=t')

This gives you the average causal effect of training on performance ratings without ever conditioning on U.

---

## The Three Conditions That Must Hold

The Front-Door Criterion is valid if and only if:

1. **M is on every causal path from T to Y.**
   Training must affect performance ratings *only* through skill application. If there are direct effects of training on performance that bypass skill application (e.g., training boosts confidence, which boosts ratings independently of applied skills), M is not a complete mediator and the criterion fails.

2. **There are no unblocked backdoor paths from T to M.**
   Ambition (U) must not directly cause M. If ambitious employees apply skills on the job more readily *regardless of whether they attended training* — not just because they went to training — then U → M exists and creates a backdoor path T ← U → M that cannot be blocked without observing U.

3. **All backdoor paths from M to Y are blocked by conditioning on T.**
   Since T is observed and sits on the only backdoor path into M from U, conditioning on T is sufficient. This condition is met by design in your setup, as long as there are no other unmeasured variables that directly cause M and Y simultaneously.

---

## The Critical Vulnerability in Your Setup

Condition 2 deserves careful scrutiny in your specific context. Ask yourself: does ambition independently influence whether employees apply skills on the job, *beyond its effect of getting them into training in the first place*?

If the answer is yes — if highly ambitious employees, regardless of training, simply work harder to demonstrate skill application in their day-to-day behavior — then U → M is a real path in your DAG. This would invalidate the Front-Door Criterion and you would be back to unidentifiable territory without an instrument or a way to measure ambition.

Similarly, Condition 1 requires scrutiny. Training may affect performance through channels other than skill application: peer networks formed during training, increased visibility to managers, credential signaling, or motivational effects. If any of these channels are real and M does not capture them, the direct path T → Y (not through M) would exist, and the total effect would again be unidentified.

---

## Practical Implications

If you believe the three conditions hold reasonably well, the Front-Door estimator can be implemented as a two-stage regression:

1. Regress M on T (and controls) to estimate T → M.
2. Regress Y on M and T (and controls) to estimate M → Y within training status.
3. Marginalize over the distribution of T to recover the population average treatment effect.

If the conditions are uncertain or partially violated, sensitivity analyses around the U → M and T → Y assumptions are important. Quantifying how large U → M or T → Y would need to be to materially bias your estimate gives you a sense of how much the unmeasured confounder actually threatens your conclusion.

---

## Summary

The presence of an unmeasured confounder (ambition) does *not* automatically make the causal effect of training on performance ratings unidentifiable. If "skills applied on the job" intercepts every causal path from training to performance, is not independently caused by ambition, and if its own backdoor paths can be blocked by conditioning on the observed training variable, then the Front-Door Criterion applies and provides a nonparametric identification formula for the average causal effect. The hard empirical work is defending those three assumptions in your specific organizational context.
