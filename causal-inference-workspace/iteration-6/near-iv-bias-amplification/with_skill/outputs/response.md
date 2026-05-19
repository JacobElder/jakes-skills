# Should You Control for Prior Performance?

Your colleague's instinct is understandable but structurally wrong for the specific variable in question. Controlling for prior performance in this case is a textbook instance of **bias amplification via a near-instrument**, and it will make your estimate worse, not better.

Here is the diagnostic.

---

## 1. Name the rung

This is a **rung 2 (intervention) question**: what is the causal effect of *doing* mentorship — receiving it — on promotion rates? You want P(Promoted | do(Mentorship)), not the observed correlation. Observational data can't answer this directly without structural assumptions, so the DAG is the working object.

---

## 2. Sketch the DAG

The key variables:

- **M** = receives executive mentorship (treatment)
- **P** = promotion (outcome)
- **PP** = prior performance (candidate control)
- **U** = unmeasured confounders (e.g., ambition, social capital, visibility, manager advocacy)

The structure your scenario describes:

```
   PP → M → Promotion
        ↑
        U (unobserved)
        ↓
        Promotion
   PP → Promotion (direct path)
```

More precisely:

```
   PP ──────────────────→ Promotion
    ↘                        ↑
     M ────────────────────→ ┘
     ↑
     U (unobserved: ambition, social networks, etc.)
     ↓
     Promotion
```

Prior performance (PP) causes both mentorship receipt (M) and promotion directly. That looks like a classic confounder fork: PP → M → Promotion, with PP → Promotion as the back-door path. Your colleague sees this fork and concludes: control for PP to close the back-door path PP → M.

That reasoning would be correct **if PP were the only confounder and U did not exist.** The problem is that U is almost certainly present — and the correlation of 0.85 between PP and M tells you something important about what PP is doing structurally.

---

## 3. Identify the structure — and where it goes wrong

### Prior performance as a partial confounder

PP is a genuine confounder on one path: PP → Promotion directly. Controlling for PP blocks that path. So far, so good.

### But PP is also a near-instrument — and that changes everything

PP also drives mentorship assignment (r = 0.85). Now consider what happens to the residual variation in M after you condition on PP:

- Most of M's variation is explained by PP (0.85 correlation means ~72% of variance in M is shared with PP).
- The remaining ~28% of variation in M — the part that is *not* explained by PP — is disproportionately driven by the unmeasured confounders U (ambition, social capital, who the employee knows, manager favoritism, etc.).

When you condition on PP, you strip away the "clean" PP-driven variation in M and leave behind almost exclusively the U-driven variation. U is now a *stronger* relative confounder of the M → Promotion relationship than it was before conditioning. You have effectively concentrated the confounding bias into the remaining variation.

This is exactly the **bias amplification** mechanism documented in the controls literature: a variable that is a strong predictor of treatment but leaves unmeasured confounding in place does not reduce bias when controlled for — it amplifies it.

The structural signature is:

```
   PP → M → Promotion
        ↑
        U (unobserved)
        ↓
        Promotion
```

PP is upstream of M with a direct path to M but not a direct path to Promotion *solely through U* — PP is a genuine cause of Promotion, but the problem is not PP's causal role, it is what conditioning on PP does to the remaining variation in M.

### The intuition in plain language

Imagine two employees who both received mentorship. One received it because PP predicted it (the "high-performance" mechanism). The other received it despite lower PP — perhaps because of informal networks, because a senior executive took a special interest, or because of some other unmeasured factor U.

After conditioning on PP, the only remaining variation in mentorship is the second type. Now your "treatment effect" estimate is comparing promoted vs. not promoted *within the U-driven slice of mentorship assignment*. The U-driven slice is exactly where your unmeasured confounders are at full strength. The bias is worse than it was unconditionally.

---

## 4. What the three possible structural roles of PP imply

To be rigorous, enumerate the alternatives:

| Role of PP | What conditioning does | Verdict |
|---|---|---|
| Classic confounder only (no U) | Blocks the only back-door path PP → Promotion. Correct. | Control. |
| Near-instrument with unmeasured U present | Strips PP-driven clean variation from M; amplifies U's confounding. | Do not control. Bias worsens. |
| Mediator (if PP changes *because* of mentorship — unlikely here since PP is prior) | Would block part of the M → Promotion path. | Do not control for total effect. |

In your setting, the near-instrument + unmeasured U structure is the most plausible. A correlation of 0.85 between PP and M is a red flag precisely because it signals how little variation in M is left after accounting for PP — and that residual variation is the unmeasured-confounder-heavy portion.

---

## 5. The right strategy

### Don't use PP as a regression covariate

Putting PP in the regression alongside M is the biasing move. Don't do it.

### Consider PP as a potential instrument instead

If PP predicts mentorship strongly (r = 0.85) and its direct effect on promotion can be plausibly argued to run *only* through mentorship (exclusion restriction), PP could function as an instrument. This is a strong assumption — PP almost certainly has direct effects on promotion independent of mentorship — so this path requires careful arguability. But structurally, a strong predictor of treatment that is only weakly related to the outcome *after accounting for the treatment* is an IV candidate, not a covariate.

### Look for design-based alternatives

Given the selection mechanism (mentorship is assigned to high performers), a natural quasi-experimental approach would be a **regression discontinuity** if mentorship eligibility is determined by a threshold (e.g., performance score above X). Employees just above and just below the threshold are comparable on PP and U; the jump at the threshold identifies the mentorship effect locally.

If mentorship programs were rolled out at different times across departments, **differences-in-differences** becomes available.

If you have rich enough data on what determines mentorship assignment, a **back-door adjustment** is valid — but the adjustment set must close *all* back-door paths, which requires measuring all the U components (ambition, social capital, manager relationships). Given that these are typically unobservable in HR data, full identification via back-door is likely unavailable.

### Sensitivity analysis

If none of the above designs are available, run a sensitivity analysis: how strong would U need to be (in terms of its correlation with both M and Promotion) to overturn your estimate? If the answer is "very strong — stronger than any known confounder in similar studies," the estimate is robust despite the confounding. If the answer is "moderately strong," it isn't.

---

## 6. The most likely trap you'd fall into

Controlling for PP because "it's pre-treatment and predicts both treatment and outcome" is the **statistical-only justification** fallacy. The same correlation pattern (Z predicts both X and Y) is produced by confounders, mediators, colliders, and near-instruments alike. Choosing whether to control requires structural reasoning — the DAG — not just correlation patterns. Your colleague's heuristic "control for confounders" is only valid when you've confirmed the variable is *structurally* a confounder and not a near-instrument with unmeasured confounding present.

---

## Summary

| Question | Answer |
|---|---|
| Is the colleague right to control for PP? | No — not as a regression covariate. |
| Why? | PP is a near-instrument (r = 0.85 with M). Conditioning amplifies U's bias rather than reducing it. |
| What should you do instead? | Look for a design-based strategy (RDD at a performance cutoff, DiD across cohorts). Evaluate PP as a potential IV (exclusion restriction required). Run sensitivity analysis if identification is partial. |
| What's the diagnostic to run? | How much variation remains in M after conditioning on PP? Very little (high R²) confirms the near-IV structure. What proportion of that residual variation is plausibly U-driven? If most of it, controlling makes things worse. |
