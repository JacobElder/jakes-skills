# Causal Analysis: Should You Control for Manager Motivation Level?

**Short answer: No. "Manager motivation level" measured 1 month after the training ended is almost certainly a mediator, and controlling for it would give you the wrong answer to your actual question.**

---

## Step 1: Name the Rung

Your question is a Rung 2 (intervention) question: "What is the causal effect of the training program on team performance?" You want P(Performance | do(Training)), not a prediction of who performs well. That framing matters for everything that follows.

---

## Step 2: Sketch the DAG

Here is the most plausible causal structure:

```
Training (X) → Manager Motivation (M) → Team Performance (Y)
      ↓__________________________________↑
              (direct path also plausible)

Confounders (U): pre-existing manager quality, team composition,
                 organizational support → X and Y
```

The training program ran for 3 days. Manager motivation was measured 1 month *after* training ended. Team performance was measured 6 months after training ended.

The temporal ordering tells the structural story: training happened first, then motivation was measured, then performance was measured. The most natural reading of this is:

- Training causes (in part) higher motivation — managers who complete the program come away more energized, with new tools and frameworks.
- Higher motivation causes (in part) better team performance — motivated managers apply what they learned.

That makes manager motivation a **mediator** on the Training → Performance path, not a confounder.

---

## Step 3: Structural Classification

Using the per-variable taxonomy from the controls framework:

| Role | Description | Verdict |
|------|-------------|---------|
| Mediator | Variable on the causal path X → M → Y | **Do not control** if you want the total effect |
| Confounder | Common cause of X and Y, measured before X | Control |
| Collider | Common effect of X and Y | Do not control |

**Manager motivation, measured post-training, is a mediator candidate, not a confounder.**

The "strong predictor of performance outcomes" observation is statistical — it says M and Y are correlated. That same correlation pattern is produced by every structural type: confounders correlate with X and Y, mediators correlate with X and Y, and even colliders correlate with X and Y after conditioning. Correlation cannot distinguish between them. The DAG distinguishes them.

---

## Step 4: What Goes Wrong If You Control for It

If you include manager motivation as a covariate in your regression of performance on training, you commit **overcontrol bias** (also called the mediator bias):

```
Training (X) → Motivation (M) → Performance (Y)
                     ↑
           You condition here, blocking this path
```

Conditioning on M blocks the Training → Motivation → Performance pathway. Your regression coefficient on training will estimate only the **direct effect** of training on performance (effects that do not pass through motivation), not the **total effect** you actually want.

In practical terms: if the training works *precisely because* it boosts manager motivation, controlling for motivation will make the training look ineffective. You've statistically removed the mechanism by which training works, then concluded the training didn't work. That is the wrong conclusion for your question.

---

## Step 5: What You Actually Want

Your stated goal is the total effect of the training program on team performance 6 months later. That is the sum of:

1. **Direct path**: Training → Performance (skills, frameworks, peer accountability effects that operate independently of motivation change)
2. **Mediated path**: Training → Motivation → Performance

Both are part of "does the training program improve outcomes?" Controlling for motivation discards path (2).

Only control for motivation if your research question changes to: *"Is there an effect of training on performance beyond what operates through motivation?"* That is a different and narrower question — the direct effect — and it requires a deliberate choice, not an accidental one.

---

## Step 6: What Should You Control For Instead?

To estimate the total effect cleanly, you need to block **back-door paths** — non-causal paths from training to performance that create spurious correlation. These run through confounders that affect both who received training and how teams performed. Candidates measured *before* the training are appropriate:

- Pre-training manager performance or experience level
- Team size, composition, or baseline performance scores
- Organizational unit / department (if training uptake varied systematically by unit)
- Time in role, tenure

The rule: measure confounders **before treatment** and ask whether they could plausibly affect both participation in the training and subsequent performance. If yes, control. If the variable was measured after treatment started, ask whether training could have caused it — if so, it's a mediator and should stay out of the model.

---

## Step 7: Alternative Structural Readings (and Why They Don't Change the Conclusion Much)

To be honest about uncertainty: there is one alternative DAG worth naming.

**Alternative: Motivation is a confounder, not a mediator.** This would be true if motivation level is stable and pre-existing — managers who were already highly motivated before training both (a) chose to engage more seriously with the training and (b) have better-performing teams. In that case, motivation is a common cause.

But this reading is harder to defend given:
1. Motivation was measured *after* the training ended. If it reflects a stable pre-existing trait, you should have measured it before — or used a pre-training measure.
2. Management training programs are specifically designed to affect motivation. It would be unusual (and would need domain-specific justification) to claim training had no effect on motivation.
3. If you believe motivation is a stable pre-existing trait, the right move is to obtain a *pre-training* measure of motivation and control for that — not the post-training measure.

**If you have access to pre-training motivation scores**, control for those. That variable would be a legitimate confounder. The post-training measure is not a substitute for it — the two variables have different structural roles.

**Diagnostic to discriminate**: Do you have any pre-training motivation data? If pre- and post-training motivation are highly correlated and training had no plausible effect on motivation (unlikely here, but possible in some settings), the mediator concern is reduced. If training is expected to affect motivation (the standard assumption in management training literature), the mediator reading dominates.

---

## Summary

| Question | Answer |
|----------|--------|
| Is post-training motivation a good control? | No |
| Why not? | It is most plausibly a mediator — on the causal path from training to performance |
| What bias does controlling for it introduce? | Overcontrol bias: you estimate only the direct effect, excluding the motivation-mediated path |
| When would controlling for motivation be valid? | If you have a *pre-training* motivation measure and believe it is a stable trait affecting both training engagement and performance |
| What should you control for? | Pre-training manager characteristics and team-level confounders measured before the intervention |
| What is the right estimand? | Total effect of training on performance — which includes both direct and mediated paths |

The instinct to include a "strong predictor" as a control is understandable but structurally incorrect here. Strong prediction is a statistical property; whether to control is a causal-structural question. Manager motivation is doing work *because* of the training, and that work is exactly what you are trying to measure.
