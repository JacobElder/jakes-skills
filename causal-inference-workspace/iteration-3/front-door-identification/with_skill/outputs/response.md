# Causal Analysis: Does Technical Skills Training Cause Higher Performance Ratings?

## 1. Name the Rung

This is a **Rung 2 (intervention)** question. You want to know P(Performance Rating | do(Training)) — what would happen to ratings if you intervened to send an employee to training, not merely what ratings look like among employees who happen to have been sent. Observational data plus the structure of the DAG determines whether this is answerable.

---

## 2. Sketch the DAG

The setup as described produces the following structure:

```
U (Ambition, unobserved)
↙                  ↘
Training (X)  →  Skills Applied (M)  →  Performance Rating (Y)
```

In words:
- **U (Ambition)** is an unobserved common cause. It affects who gets selected into training (ambitious employees push for it, or managers nominate high-ambition employees) and it independently drives performance ratings (ambitious employees perform better regardless of training).
- **Training (X)** causes employees to apply new skills on the job.
- **Skills Applied on the Job (M)** is an intermediate variable — it sits between training and the performance outcome and captures whether the training content actually changed behavior.
- **Performance Rating (Y)** is the outcome, caused both by skills applied and by ambition directly.

There is also a second arrow to account for: does ambition affect skills applied independently of training? Probably yes — ambitious employees may apply skills more diligently. This matters and is addressed below.

---

## 3. Identify the Structure

### The back-door problem

The path X ← U → Y is a **fork** — a classic confounding path. U (ambition) is a common cause of both training assignment (X) and performance ratings (Y). This is the "bad path" you want to block.

Back-door adjustment requires controlling for something that blocks X ← U → Y without opening new spurious paths. Since U is unobserved, **back-door adjustment fails**. You cannot close this path with the variables you have.

### Is the effect unidentifiable? Not necessarily — enter the front-door criterion.

Before concluding the effect is unidentifiable, the skill's framework directs you to ask: *Is there an observed mediator between X and Y whose own back-door paths to Y are all blockable?*

You have exactly that: **Skills Applied on the Job (M)**.

The **front-door criterion** requires three conditions:

1. **M blocks all directed paths from X to Y.** The entire causal effect of training on performance ratings must run through M. If training has a direct effect on ratings (e.g., the act of attending training signals effort to a manager who then rates you higher, independently of skill application), this condition fails.

2. **No unblocked back-door paths from X to M.** This means: no path of the form X ← [something] → M that isn't already closed. The only confounding variable described is U (ambition). Does U affect M? If ambition causes employees to apply skills on the job *regardless* of training, then there is a path X ← U → M, which is an unblocked back-door from X to M. This is the critical structural question.

3. **All back-door paths from M to Y are blocked by X.** The path M ← U → Y exists (ambition drives skill application and ratings). This back-door from M to Y is blocked by conditioning on X in the second stage, because U reaches M only through X in the stated DAG — holding X fixed severs U's influence on the M → Y association.

**The pivot point: does ambition directly cause skills applied, independent of training?**

This is the structural assumption you must interrogate. Two scenarios:

### Scenario A: Ambition affects skills applied only through training selection

```
U (Ambition)
↙              ↘
X (Training) → M (Skills Applied) → Y (Performance)
               U → Y (direct)
```

In this structure, U affects M only by increasing the probability that the employee received training (X), not by directly causing M. Once you know whether someone received training, ambition has no additional effect on whether skills show up in daily work. Under this DAG, the three front-door conditions are met:

1. Training's entire effect on ratings passes through skills applied. ✓
2. The only back-door into X is via U, but U does not reach M except through X — no unblocked back-door from X to M. ✓
3. The back-door from M to Y runs through U, which is blocked by conditioning on X in the second stage. ✓

**The effect is identifiable via front-door adjustment.**

### Scenario B: Ambition directly causes skills applied, independent of training

```
U (Ambition)
↙       ↓       ↘
X   →   M   →   Y
```

Here U → M creates an unblocked back-door path from X to M (X ← U → M). This violates front-door condition 2. Ambition pushes employees both into training and into applying skills on the job, regardless of whether training occurred. Skills applied is now not a clean mediator — it's partially driven by the same confounder that's driving ratings.

**Under this DAG, front-door adjustment also fails.** The effect is no longer identifiable from observational data without additional assumptions or data.

---

## 4. The Front-Door Estimator (When Applicable)

Under Scenario A — where front-door conditions are satisfied — the causal effect is computed in two stages:

**Stage 1:** Estimate the effect of Training on Skills Applied.
- Because the only path from X to M is the direct causal path (no unblocked back-doors from X to M), the association P(M | X) directly identifies P(M | do(X)).
- Practically: compare rates of skill application between trained and untrained employees.

**Stage 2:** Estimate the effect of Skills Applied on Performance Rating, conditioning on Training.
- Conditioning on X blocks the back-door path from M to Y that runs through U. Since U reaches M only through X in this DAG, holding X fixed removes U's confounding influence on the M → Y relationship.
- Practically: within each training-status group, compare performance ratings between those who applied skills and those who did not.

**Combined estimator (Pearl's front-door formula):**

```
P(Y | do(X)) = Σ_M P(M | X) · Σ_{X'} P(Y | M, X') P(X')
```

In regression terms, this is a two-stage procedure: (1) regress M on X to get predicted values of M; (2) regress Y on M and X (using X to block the confounder path), then marginalize over X's distribution. This is structurally similar to a mediation analysis but with a distinct causal purpose — identifying the total effect despite an unmeasured confounder, not decomposing it into direct and indirect parts.

---

## 5. Key Structural Question You Must Answer

**The entire identification argument hinges on whether ambition (U) affects skills applied on the job (M) directly, or only through its effect on training selection (X).**

Ask yourself:
- Would a highly ambitious employee who was *not* sent to training still be more likely to apply skills on the job than a low-ambition employee who also wasn't sent? (If yes → Scenario B → front-door fails.)
- Or is the difference in skill application entirely explained by the fact that ambitious employees were trained? (If yes → Scenario A → front-door works.)

This is not a statistical question. It is a domain-knowledge question. No regression can answer it. You need substantive knowledge about how ambition operates in your organization.

---

## 6. Also Check: Does Training Have a Direct Effect on Ratings?

Front-door condition 1 requires that the entire training effect on performance flows through skills applied. This could be violated if:
- Managers rate trained employees higher simply because training signals initiative or company investment, independent of whether skills show up in work.
- Completing training appears on visible employee profiles and influences rating calibration.

If training has a direct effect on ratings not mediated by skills applied, the front-door adjustment recovers only the mediated portion, not the total effect. Decide whether the mediated effect is the estimand you care about.

---

## 7. What to Do Under Each Structural Diagnosis

| Scenario | Identification verdict | What to do |
|---|---|---|
| Ambition affects M only through X; training effect fully mediated by M | **Identifiable via front-door** | Apply the two-stage front-door estimator |
| Ambition directly affects M independent of training | **Not identifiable by front-door** | Consider IV, sensitivity analysis, or an experiment |
| Training has a direct effect on ratings not through M | **Front-door identifies partial effect only** | Decide if the mediated effect is the right estimand; acknowledge the gap |

---

## 8. Most Likely Trap Here

**Treating skills applied as a covariate in a regression of performance on training.** If you put M into a regression of Y on X as a control variable, you block the very causal pathway through which training operates — giving you approximately zero effect of training on performance, not because training has no effect, but because you conditioned on the mediator (overcontrol bias). Skills Applied is a mediator, not a confounder, and the structural taxonomy is clear: mediators on the X → Y path should not be controlled when estimating the total effect.

The front-door formula uses M in a specific, structured way across two stages — not as a generic regression covariate.

---

## 9. Summary Answer

No, the unmeasured confounder (ambition) does not automatically make this effect unidentifiable. The key insight is that "skills applied on the job" — the variable sitting between training and performance ratings — is a candidate for front-door identification. If the three front-door conditions hold (most critically: ambition does not directly cause skill application independently of training, and training's effect on performance is entirely mediated through skill application), then the causal effect of training on performance ratings is identifiable from observational data using Pearl's front-door formula.

The identification work has shifted from "find something that blocks the confounder" (impossible here, since ambition is unobserved) to "find a mediator whose own confounding structure is tractable" (possible here, conditionally). Whether you are in the identifiable scenario depends on a domain judgment about whether ambition operates on skill application only through training selection, or also through independent motivation present regardless of training. That judgment cannot be delegated to the data — it is the assumption on which identification rests, and it should be stated explicitly in any analysis you report.
