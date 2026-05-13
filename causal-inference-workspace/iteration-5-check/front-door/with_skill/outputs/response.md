# Does the Unmeasured Confounder (Ambition) Make This Effect Unidentifiable?

**Short answer:** No — not necessarily. The unmeasured confounder blocks the back-door adjustment route, but the structure you've described is a strong candidate for **front-door identification**. However, you need to scrutinize three conditions carefully before concluding the effect is recoverable. One of them is the condition most often glossed over, and it may be the sticking point in your setting.

---

## Step 1: Name the Rung

Your question is **Rung 2 (Intervention)**: "Does receiving training *cause* higher performance ratings?" You want P(Performance | do(Training)), not the correlation you'd observe in your data. This is a genuine causal question, and observational data does not answer it without additional structure — which is exactly what a DAG provides.

---

## Step 2: Sketch the DAG

Here is the structure your description implies:

```
Ambition (U) ──────────────────────────────────────┐
     │                                              ↓
     ↓                                      Performance Rating (Y)
Training (X) ──→ Skills Applied on Job (M) ──────→ Performance Rating (Y)
```

More precisely:

- **U (Ambition)** is unobserved. It points into both **X (Training)** and **Y (Performance Rating)**.
- **X (Training)** points into **M (Skills Applied on Job)**.
- **M** points into **Y**.
- There is a **backdoor path**: X ← U → Y, which is open and confounded.
- The causal path runs: X → M → Y.

---

## Step 3: Why Back-Door Fails (and What That Means)

The standard fix for confounding is **back-door adjustment**: control for all variables that block the paths from X to Y that flow into X. In your case, the back-door path is X ← U → Y, and U is **unobservable**. You cannot block it by conditioning, because you do not have the data. This is the classic "unmeasured confounder" problem — back-door adjustment is not available.

But this is not the end of the road.

---

## Step 4: The Front-Door Criterion — Your Path Forward

Pearl's **front-door criterion** was designed precisely for situations where a back-door set is unavailable due to unobserved confounders, but an observed mediator sits between the treatment and the outcome. Your variable "skills applied on the job" (M) looks exactly like that mediator.

The front-door criterion says you can identify P(Y | do(X)) from observational data if you can find a variable M such that:

1. **M is completely interceptive:** All directed paths from X to Y run through M. There is **no direct path** from X to Y that bypasses M.
2. **No unblocked back-door path from X to M:** M is not confounded with X by any open path.
3. **All back-door paths from M to Y are blocked by X:** The back-door path from M to Y runs through U, but conditioning on X blocks it — because X is on the path X ← U → Y that also passes through X → M.

If all three hold, the front-door formula recovers the causal effect:

```
P(Y | do(X)) = Σ_m P(M=m | X) · Σ_x' P(Y | X=x', M=m) · P(X=x')
```

In plain terms: (1) estimate the effect of training on whether skills get applied, then (2) estimate the effect of skills applied on performance (averaging over the distribution of training), then (3) chain them together. The unmeasured U gets averaged out in step 2, because you condition on both M and X simultaneously, and X blocks U's backdoor influence on M→Y.

---

## Step 5: Interrogating Each Condition for Your Setting

### Condition 1 (Complete Mediation — the most important and most often violated)

**The question:** Can training affect performance ratings through *any* mechanism that does not pass through "skills applied on the job"?

This is the condition that is most often glossed over in front-door analyses, and it is the one most likely to be problematic in your setting. Think through these specific mechanisms:

- **Signaling / halo effect:** Being seen attending training, or having "completed training program" appear on an internal record, might directly influence how a manager rates the employee — independent of whether any skills were actually applied. The manager knows who went to training; that knowledge alone could shift the rating.
- **Confidence and motivation:** Training might boost an employee's self-confidence or motivation in ways that improve performance through routes other than the specific skills taught — presenting more assertively in meetings, volunteering for stretch assignments — none of which would be captured by "skills applied on the job" if that measure is specifically about training content.
- **Network effects:** Training sessions often bring employees into contact with peers or managers from other departments. These relationships could independently boost performance ratings.

If any of these are plausible, there is a direct X → Y path that M does not intercept, and Condition 1 is violated. The front-door formula would then give you a biased estimate — specifically, it would underestimate or misattribute the portion of the effect running through the direct path.

**Practical diagnostic:** Ask yourself whether your measure of "skills applied on the job" is comprehensive enough to capture *every* mechanism by which training could affect performance. If it is a narrow measure — say, whether the employee is using the specific technical skills taught — it probably does not capture all pathways, and a direct path likely exists.

### Condition 2 (No Unblocked Back-Door from X to M)

**The question:** Is training confounded with skills applied on the job, independent of ambition?

In your setup, U (ambition) is a common cause of X and Y. Does U also directly cause M? If ambitious employees are both more likely to attend training *and* more likely to apply skills on the job *regardless of whether they attended training* — then U → M directly, which creates an unblocked back-door path X ← U → M. Condition 2 would be violated.

This is a real concern. An ambitious employee might proactively apply skills they picked up from books, peers, or self-study, and this would appear in the "skills applied" measure even if training caused none of it. In that case, the observed correlation between M and X is partly driven by U, not just by training.

**Practical diagnostic:** Does the "skills applied" measure distinguish between skills specifically acquired through training versus skills the employee would have developed independently? If it is a general measure of on-the-job skill application, U → M is likely, and Condition 2 may be violated.

### Condition 3 (Back-Door from M to Y Blocked by X)

This condition is usually the easiest to satisfy in a front-door setup. The back-door path from M to Y runs through U: M ← X ← U → Y. Once you condition on X in the second step of the front-door formula, this path is blocked. As long as U does not have a *direct* path into M that bypasses X — which is what Condition 2 is about — Condition 3 holds automatically from your DAG structure.

---

## Step 6: What Happens If Conditions Are Violated?

| Condition Violated | Consequence |
|--------------------|-------------|
| 1 (Direct X→Y path) | Front-door underestimates total effect; direct path contribution is not captured. You get only the mediated effect, not the total causal effect. |
| 2 (U→M directly) | M is confounded; the first step of the formula (X→M) is biased. The whole estimate is contaminated. |
| 3 (Back-door M→Y not blocked) | Typically follows from Condition 2 violation. If Condition 2 holds, Condition 3 usually holds. |

---

## Step 7: What Should You Do?

**If you believe Condition 1 holds (no direct X→Y path)** and **Condition 2 holds (U does not directly cause M):** You can apply the front-door formula. The effect is identifiable without observing ambition at all. This is one of the more remarkable results in the causal inference literature — unobserved confounding is fully neutralized by the two-step chain through M.

**If Condition 1 is in doubt (plausible direct effects from training on ratings):** The front-door formula recovers only the path-through-M portion of the effect. You have a partial identification problem. Consider whether you can redefine or broaden the M measure to capture more of the mechanisms, or whether you can use a different design.

**If Condition 2 is in doubt (ambition drives skill application independently):** The front-door approach breaks down. You would need to either: (a) find a sub-measure of M that is only reachable through training and not through ambition, (b) find an instrument for training (a variable that assigns training more or less randomly, with no direct effect on performance), or (c) run a randomized experiment — assign some employees to training and some to a control condition.

---

## Step 8: Alternative Strategies Worth Naming

- **Instrumental variable:** Is there something that determines *who gets sent to training* that is essentially random, and that has no direct effect on performance ratings? For example, an alphabetical enrollment lottery, a mandatory rotation by team, or a budget constraint that caused some teams to receive training in Q1 and others in Q3. If so, you may be able to use assignment as an instrument for training receipt, and bypass the ambition confounder entirely. The exclusion restriction — that the instrument has no direct effect on ratings — is the usual weak link.
- **Differences-in-differences:** If you observe employees before and after training, and you have a control group that did not receive training, DiD can difference out time-invariant confounders like stable individual traits. Ambition, if it is a relatively fixed trait, would be absorbed in the individual fixed effect. The key assumption is parallel trends: in the absence of training, treated and untreated employees would have had similar trajectories in performance ratings.
- **Randomized experiment:** If you can randomize who gets access to training, the ambition confounder is balanced by design. This is the cleanest solution if feasible.

---

## Summary

| Question | Answer |
|----------|--------|
| Does the unmeasured confounder (ambition) make the effect unidentifiable? | Not automatically — the front-door criterion may rescue identification. |
| What is the key variable enabling this? | "Skills applied on the job" (M) as a fully interceptive observed mediator. |
| What is the most dangerous assumption? | No direct training → performance path that bypasses M (Condition 1). |
| What is the second most dangerous assumption? | Ambition does not directly cause skill application independently of training (Condition 2). |
| If both conditions hold, can you identify the effect? | Yes, using the front-door formula, without ever observing ambition. |
| If either condition fails, what next? | IV, DiD, or a randomized experiment are the remaining options. |

The unmeasured confounder is not a dead end. It closes the back-door route, but your mediator variable opens the front-door route — provided the structural assumptions hold. Your immediate job is to scrutinize whether training can affect performance ratings through any channel that bypasses "skills applied on the job," and whether ambitious employees would score high on "skills applied" even without the training. Those two questions determine whether you have a clean identification strategy or a more difficult problem requiring a different design.
