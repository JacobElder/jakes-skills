# Should You Control for Manager Motivation Level?

**Short answer: No. Controlling for "manager motivation level" — measured 1 month after the training ended — is a structural mistake. It is a mediator on the causal path from training to performance. Conditioning on it produces overcontrol bias: you block the very mechanism through which training improves outcomes and systematically underestimate (or entirely destroy) your estimate of the training effect.**

---

## Step 1: Name the rung

Your question is Rung 2 (intervention): "Does completing the 3-day management training program *cause* higher team performance scores 6 months later?" You want to know the effect of *doing* something — assigning managers to training — not merely what correlates with performance. That's a causal question, requiring causal identification tools, not just regression precision.

---

## Step 2: Sketch the DAG

The most plausible causal structure, given the problem description:

```
                    U (unmeasured confounders)
                   / \
                  ↓   ↓
Training (X) ───────────────────────────→ Team Performance (Y)
     |                                            ↑
     └──→ Manager Motivation, t+1 month (M) ─────┘
```

Variables:
- **X** = completion of the 3-day management training (treatment)
- **M** = manager motivation level, measured 1 month after training ends
- **Y** = team performance scores, measured 6 months after training
- **U** = unmeasured pre-training factors (e.g., baseline motivation, organizational culture, manager tenure)

The critical structural fact: M is measured **after** the treatment. The first question to ask about any post-treatment variable is: *could treatment have caused this variable?* The answer here is almost certainly yes — that is the explicit logic of the training program. Management training is designed to raise managers' sense of efficacy, give them tools and frameworks, and increase their motivation to apply them. The motivational boost is the mechanism.

This means M sits **on the causal path** from X to Y. Structural role: **mediator**.

The DAG has two paths from X to Y:
1. **X → M → Y** (the indirect/motivational pathway)
2. **X → Y directly** (any residual direct pathway not mediated by motivation)

---

## Step 3: Classify the structural role of M

Applying the per-variable classification:

| Candidate Control | Timing | Structural Role | Verdict |
|---|---|---|---|
| Manager motivation level | Post-treatment (t + 1 month) | Mediator (X → M → Y) | **Do not control** |

**Why conditioning on a mediator is harmful — not neutral:**

When you include M in a regression of Y on X, you are asking: "Among managers with the *same* motivation level 1 month after training, what is the effect of training on performance?" You have held constant the very mechanism through which training was supposed to work. What remains is only the direct effect of training that bypasses motivation entirely — a smaller, residual quantity that is almost certainly not what you care about.

This is **overcontrol bias**. The result:
- The coefficient on X (training) will be attenuated toward zero
- In the extreme case where motivation is the *only* mechanism, the training coefficient goes to zero — meaning you'd conclude the training had no effect, even if it worked perfectly through motivation
- The bias is systematic and structural, not sampling error; larger samples make it worse, not better

---

## Step 4: Why "strong predictor of performance" is exactly the wrong reason to include M

The reasoning "it strongly predicts Y, so I should control for it" is the most common route into overcontrol bias. Here's the precise failure:

A strong correlation between M and Y is *expected if M is a mediator*. The better the training works through the motivational mechanism, the stronger the M–Y association will be. The predictive strength of M is not evidence that M is a confounder — it is evidence that M is doing exactly what a mediator should do.

Statistical association patterns are structurally ambiguous. The same (X correlates with M, M correlates with Y) pattern is produced by:
- A confounder (M → X, M → Y)
- A mediator (X → M → Y)
- A collider (X → M ← Y) — less likely here but possible
- A proxy for any of the above

Predictive strength does not discriminate between these. The DAG determines which structural role M occupies. Whether to control depends entirely on that structural role — not on R², variable importance scores, or theoretical salience as a predictor.

From the skill's control taxonomy: *"Statistical-only justification is a trap. 'Z correlates with X and Y, so I controlled for it.' The same correlation pattern is produced by every DAG type — confounder, mediator, collider, proxy. Choosing whether to control requires causal reasoning."*

---

## Step 5: Enumerate alternative structural roles and what they imply

**Alternative A: M is a mediator (most plausible)**

```
X → M → Y   (and possibly X → Y directly)
```

Training causes motivation change; motivation causes performance improvement. If true, controlling for M blocks the indirect path, produces overcontrol bias, and underestimates the total training effect. **Do not control for M.**

**Alternative B: M is a pre-existing confounder**

This would require M to be causally prior to training participation — highly motivated managers both seek out training and independently produce better team outcomes. But M is measured 1 month *after* training ends. A measurement taken after treatment cannot be a pre-treatment confounder unless you make the strong and implausible assumption that training had zero effect on motivation. That assumption directly contradicts the program's theory of change. Even if pre-training motivation *is* a confounder (a real concern — see below), post-training motivation is the wrong variable to control for it.

**Alternative C: M is a collider**

If there were a common unmeasured cause of both post-training motivation and performance (e.g., a simultaneous organizational intervention that made managers both more motivated and led to performance gains independently of training), M would be a collider. Conditioning on a collider opens a spurious path between X and Y, creating bias where none existed. This provides another structural reason not to control for M.

**The discriminating question:** Did training affect M? If there is *any* plausible mechanism by which the training influenced manager motivation — even partially — then M is at least partly a mediator, and conditioning on it blocks causal signal. Given the explicit theory of change for management training programs, this answer is almost certainly yes.

---

## Step 6: The real confounding concern and what to do about it

There *is* a legitimate confounding concern in this study, but it is not addressed by controlling for post-training motivation. The concern is:

**Pre-training manager motivation** may be a confounder. Managers who are already highly motivated may be more likely to attend (or be selected for) the training *and* independently produce better team performance. This would create a spurious positive association between training and outcomes that does not reflect the program's effect.

The correct response to this confound:
- Measure and control for **pre-training** motivation (or other pre-treatment proxies)
- Control for other pre-treatment confounders: manager tenure, baseline team performance scores, team size, organizational unit, manager experience level
- Use design-based methods if feasible: randomization of training slots, regression discontinuity on selection criteria, or a difference-in-differences approach using pre/post performance data for trained and untrained managers

Post-training motivation does not fix this confound. It makes things worse by additionally blocking the mechanism.

---

## Step 7: What to do instead

**For estimating the total effect of training (what you almost certainly want):**

Regress team performance (Y, at 6 months) on training participation (X), controlling only for pre-treatment variables that causally precede both X and Y. Reasonable candidates:
- Pre-training team performance scores
- Manager tenure and experience
- Team size
- Organizational unit fixed effects
- Manager baseline skill assessments (if available)
- Pre-training motivation (if measured before training)

Leave post-training motivation out of the main outcome model entirely.

**If you want to understand the motivational mechanism:**

This is a **mediation analysis** question: "How much of training's effect on performance runs through the motivational pathway versus other routes?" That requires a proper mediation framework — estimating natural direct and indirect effects — not covariate adjustment. Mediation analysis has its own identification requirements (particularly, that the mediator–outcome relationship is itself unconfounded after conditioning on treatment). This is a separate, well-posed analysis you could run alongside the main total-effect estimate.

**If you want to use motivation as an outcome:**

Run a separate model: does training affect manager motivation? Regress M on X with appropriate pre-treatment controls. This is a legitimate causal question with M as the dependent variable — it tells you whether training works through the motivational pathway. Do not use this variable as a control in the performance model.

---

## Summary

| Question | Answer |
|---|---|
| Is post-training manager motivation a good control variable? | No |
| Why not? | It is a mediator — on the causal path X → M → Y |
| What happens if you include it? | Overcontrol bias: the indirect training effect is blocked, the training coefficient is attenuated or zeroed out |
| Does its strong predictive power justify including it? | No. Predictive strength does not distinguish confounders from mediators. Statistical association patterns are structurally ambiguous. |
| What should you control for? | Pre-treatment confounders only: pre-training performance, manager tenure, team size, org unit, pre-training motivation if measured |
| What if you want to study the motivational mechanism? | Use mediation analysis (natural direct/indirect effects), not covariate adjustment |
| Is there a real confounding concern? | Yes — pre-training motivation may confound the X–Y relationship. Fix it with pre-treatment measurement, not post-treatment control. |

The timing of measurement is not sufficient to determine whether a variable is a valid control. What matters is the causal structure: does M causally precede X, or could X have caused M? When the answer is "X caused M" — as it almost certainly is here — M is a mediator (or partly a mediator), and conditioning on it destroys the causal signal you are trying to estimate. This is one of the most common and consequential errors in program evaluation research.
