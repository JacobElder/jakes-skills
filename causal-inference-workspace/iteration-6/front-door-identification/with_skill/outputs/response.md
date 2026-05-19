# Causal Analysis: Does Technical Skills Training Cause Higher Performance Ratings?

## 1. Name the Rung

This is a **Rung 2 (Intervention)** question. You want to know what would happen to performance ratings *if you intervened* to send employees to training — not merely what ratings look like among employees who happen to have been trained. That's `P(Rating | do(Training))`, not `P(Rating | Training)`. Observational data alone can't answer this without causal structure. The good news is that your mediator observation creates real leverage.

---

## 2. Sketch the DAG

The causal structure you've described looks like this:

```
   U (Ambition, unobserved)
   ↙                    ↘
Training  →  Skills Applied  →  Performance Rating
```

In notation:
- **U** = Employee ambition (unobserved confounder)
- **X** = Technical skills training (treatment)
- **M** = Skills applied on the job (observed mediator)
- **Y** = Performance ratings (outcome)

Paths:
- **Causal:** X → M → Y (the mediated effect you want to measure)
- **Confounded back-door:** X ← U → Y (the spurious association driven by ambition)

---

## 3. Does the Unobserved Confounder Make This Unidentifiable?

**No — not necessarily.** This is precisely the structure the **front-door adjustment** was designed for. Before concluding the effect is unidentifiable, you need to check all three front-door conditions against your specific setting.

---

## 4. Front-Door Identification: The Three Conditions

### Condition 1: Complete Mediation — No Direct X → Y Path Bypassing M

**This is the condition most likely to fail in your setting, and it deserves the most scrutiny.**

Ask yourself: can attending training affect performance ratings through *any* mechanism that doesn't go through "skills applied on the job"?

Several plausible direct paths exist in a real workplace:

- **Signaling / halo effect.** Managers may know which employees attended training. Being visibly sent to training could signal investment and commitment, causing the manager to view the employee more favorably in ratings — independent of whether any skills showed up in actual work.
- **Credential effect.** If training completion appears on an employee's internal profile and rating forms reference development activity, training can influence ratings directly.
- **Self-efficacy.** Training may increase employee confidence, which changes their work behavior in ways your "skills applied" measure doesn't capture.
- **Social capital.** Attending training connects employees with peers and leadership, which can affect ratings through relationship channels.

If *any* of these direct paths exist, the front-door formula is **biased** even if "skills applied" is the dominant channel. This is the most commonly overlooked front-door assumption, and in organizational settings, the signaling path is almost always present at some level.

**Diagnostic question:** Do employees who attend training but show zero change in "skills applied on the job" still get higher performance ratings than matched non-trainees? If yes, there is a direct X → Y path and Condition 1 fails.

---

### Condition 2: No Unblocked Back-Door from X to M

There must be no unobserved confounder that independently causes both training assignment and skills applied on the job, bypassing training itself.

In your case, the concern is whether ambition (U) directly causes employees to apply skills on the job *regardless* of whether they attended training. This would open a U → M path, which combined with U → X creates a back-door from X to M.

The plausible story: ambitious employees may proactively self-study, seek feedback, and apply skills they learned elsewhere. In that case, ambition affects M directly, and Condition 2 fails.

**Diagnostic question:** Do employees who were *not sent to training* still show variation in "skills applied on the job" that correlates with other proxies for ambition (e.g., voluntary development activity, self-initiated feedback requests)? If yes, U → M is likely open.

---

### Condition 3: Back-Door from M to Y Is Blocked by X

The path M ← X ← U → Y can be blocked by conditioning on X. This condition typically follows from Condition 2 holding. If Condition 2 is satisfied (no U → M path), then conditioning on X blocks the back-door from M to Y, and Condition 3 holds.

---

## 5. The Front-Door Formula (When Conditions Are Met)

If all three conditions hold, the causal effect is identified by:

```
P(Y | do(X)) = Σ_M P(M | X) · Σ_{X'} P(Y | M, X') · P(X')
```

The intuition behind the two steps:
1. **Step 1:** Estimate the effect of training on skills applied — this is clean because any confounder affecting X also passes through X before reaching M (no unblocked back-door on X → M).
2. **Step 2:** Estimate the effect of skills applied on performance ratings — this is done by conditioning on X, which blocks the ambition confounder's back-door path through M.

Combined, these two steps identify the total causal effect of training on ratings through the mediator, without ever needing to observe ambition.

---

## 6. Verdict and Strategy

| Condition | Status in Your Setting | Diagnosis |
|-----------|----------------------|-----------|
| 1. Complete mediation (no direct X→Y) | **At risk** | Signaling, halo, credential effects are common in training contexts. Test empirically. |
| 2. No back-door from X to M | **At risk** | Ambitious employees may apply skills regardless of training. Check with proxies for ambition. |
| 3. Back-door from M to Y blocked by X | Likely holds if Condition 2 holds | Follows from Condition 2. |

**If both Conditions 1 and 2 hold:** Front-door adjustment identifies the causal effect. Run the two-step estimator.

**If Condition 1 fails (direct X→Y path exists):** The front-door formula is biased. The effect is partially identified at best. Consider: (a) an IV approach if there's a variable that affected training assignment but not performance directly; (b) a DiD design if you have pre/post rating data and a comparison group; (c) sensitivity analysis quantifying how large the direct effect would need to be to meaningfully change your conclusion.

**If Condition 2 fails (U→M path exists):** The mediator is itself confounded. The front-door formula breaks down. The same IV or DiD alternatives apply.

---

## 7. What This Changes Practically

The unmeasured confounder (ambition) does *not* automatically make this unidentifiable. The front-door criterion offers a path to identification precisely for situations like yours — unobserved confounding of the treatment, but an observed mediator that carries the full effect.

The real question is whether your "skills applied on the job" variable is clean enough to satisfy the two critical conditions above. In most organizational settings, Condition 1 (no direct training → rating path) is the harder sell. If managers who assign ratings also know who attended training, a signaling channel is almost guaranteed to exist at some level.

Before relying on the front-door estimate, run the diagnostic: look at employees who attended training but whose "skills applied" scores show no change. If their ratings still improved, you have evidence of a direct path, and the front-door formula will overstate the skills-mediated effect.

---

## 8. Most Likely Trap

**The signaling / halo path.** The front-door approach is elegant and the instinct to use it here is correct. The trap is assuming complete mediation without testing for it. In practice, performance ratings are influenced by managerial perception, and managerial perception is influenced by knowing someone attended training — independent of whether that training changed their work behavior. This is a substantive domain claim, not a statistical one, and it needs to be argued or tested directly.

---

## Summary

The unmeasured confounder does not make this effect unidentifiable. Front-door adjustment through "skills applied on the job" can identify the causal effect of training on performance ratings *if*: (1) there is no direct training-to-ratings path that bypasses skills applied, and (2) ambition does not directly cause skills applied independently of training. Test Condition 1 by looking at trainees with no measured change in skills applied — any rating improvement in that subgroup is evidence of a direct path. Test Condition 2 by looking at non-trainees' variation in skills applied and correlating it with ambition proxies. If both conditions hold, use the two-step front-door estimator. If either fails, shift to IV or DiD.
