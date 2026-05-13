# Causal Analysis: Executive Mentorship and Promotion Rates

## Step 1: Name the rung

This is a **Rung 2 (interventional)** question. You want to know: "What would happen to promotion rates if we intervened and assigned employees to receive executive mentorship?" The question is not about prediction — it is about the causal effect of the treatment (mentorship) on the outcome (promotion). The data is observational, which creates a gap that must be addressed through identification strategy, not just regression adjustment.

---

## Step 2: Sketch the DAG

Let's name the variables:
- **M** = receives executive mentorship (treatment)
- **P** = promoted (outcome)
- **Perf** = prior performance (the candidate control)
- **U** = unmeasured confounders (other factors that drive both who gets mentored and who gets promoted — e.g., being in a visible role, having a supportive manager, social capital, political savvy)

The question tells us:
1. Prior performance strongly predicts receiving mentorship (r ≈ 0.85).
2. Prior performance also directly predicts promotion.
3. Mentorship is "almost exclusively" given to high performers — the assignment mechanism is highly non-random.

A plausible DAG:

```
   Perf ---------> P (promotion)
     |
     v
     M (mentorship) --> P
     ^
     |
     U (unmeasured: visibility, manager support, political capital)
     |
     v
     P (promotion)
```

More precisely:

```
   Perf --> M --> P
   Perf ---------> P
   U -----> M
   U ---------> P
```

Where:
- **Perf** is a confounder (causes both M and P directly)
- **U** represents unmeasured confounders that also cause both M and P
- The back-door paths from M to P are:
  - M ← Perf → P
  - M ← U → P

---

## Step 3: Classify prior performance's structural role

Your colleague is correct that **Perf is a confounder in the classic sense** — it is a common cause of both treatment (M) and outcome (P). Under the fork structure `M ← Perf → P`, controlling for Perf closes that back-door path and removes the spurious correlation running through Perf. This is textbook back-door adjustment. So far, the colleague's advice is right.

**However**, there is a second structural problem your colleague may be ignoring.

---

## Step 4: The near-instrument trap — bias amplification

The critical issue is the correlation of 0.85 between prior performance and receiving mentorship. This is not just "a strong confounder." It means that **prior performance is functioning as a near-instrument for mentorship**.

Recall the bias-amplification structure from `controls.md`:

```
   Perf --> M --> P
             ^
             |
             U (unobserved)
             |
             v
             P
```

When a variable is a very strong predictor of treatment but the treatment still has substantial residual variation driven by unmeasured factors (U), conditioning on that strong predictor **concentrates the remaining variation in M onto the portion driven by U**. In other words:

- Before adjusting for Perf: M's variation comes partly from Perf and partly from U.
- After adjusting for Perf: M's variation comes almost entirely from U.

By removing the "clean" Perf-driven variation in M, you leave only the U-driven variation. The unmeasured confounder U is now a **stronger relative driver** of the residual variation in M than it was before adjustment. The bias from U, measured as a fraction of the remaining identifying variation, strictly increases.

This is not a theoretical curiosity. With a 0.85 correlation between Perf and M, conditioning on Perf is especially dangerous. The after-adjustment estimate of the mentorship effect could be more biased — in either direction — than the unadjusted estimate, because the U-to-M variation has been amplified relative to the total.

---

## Step 5: Is the full back-door criterion satisfied?

Your colleague's recommendation implicitly assumes that adjusting for Perf alone closes **all** back-door paths from M to P. That is only true if Perf is the **only** confounder — no U, no unmeasured common causes of mentorship and promotion.

Given the context, this assumption is almost certainly false. Factors like:
- Being in a high-visibility role
- Having an executive sponsor who informally advocates for both mentorship assignment and promotion
- Social capital and networking ability
- Organizational political positioning

...all plausibly affect both who receives mentorship and who gets promoted, independently of measurable prior performance. These are the U's in the DAG.

If U is present:
- Controlling for Perf removes one back-door path (Perf's fork) but leaves the U-driven back-door open.
- Worse, the near-IV property of Perf means adjusting for it amplifies the bias from U.

The result: your colleague's adjustment does not satisfy the back-door criterion, and actively worsens identification relative to not adjusting, or to using a different strategy.

---

## Step 6: What should you do instead?

### Option A: Acknowledge the identification limits

If U is present and unobserved, the back-door criterion cannot be satisfied by observable covariates alone. The honest conclusion is partial: "we can control for measured prior performance to remove that source of confounding, but unobserved confounders likely remain, and controlling for a near-IV amplifies their bias." A **sensitivity analysis** (e.g., Cinelli & Hazlett's sensemakr framework) can quantify how strong U would need to be to overturn the estimated effect.

### Option B: Treat Perf as an instrument rather than a control

If prior performance affects promotion **only through mentorship** (i.e., Perf → M → P, with no direct Perf → P path), then Perf satisfies the exclusion restriction and could serve as an instrument. However, the problem statement says "prior performance also predicts promotions directly" — this means Perf → P exists, **violating the exclusion restriction**. Perf cannot be a valid IV here.

This also confirms: do not put Perf in the regression as a covariate if you are concerned about near-IV bias amplification. And do not use it as an instrument, because the exclusion restriction fails.

### Option C: Design-based identification

If there is any variation in mentorship assignment that is not purely performance-driven — for example, if a specific cohort year had an unusually large or small number of mentor slots due to organizational changes, or if different business units had different mentorship norms independent of employee performance — these could be exploited as natural experiments or quasi-IVs.

A regression discontinuity design could work if mentorship is assigned through a scoring or rating system with a hard cutoff: employees just below and just above the cutoff would be comparable on performance but differ in mentorship receipt.

### Option D: Front-door adjustment (if applicable)

If there is an observable variable that fully mediates the mentorship → promotion effect (e.g., "received a specific project stretch assignment" that is caused by mentorship and fully explains how mentorship leads to promotion), front-door adjustment could identify the effect even with unmeasured U. This is a high bar — the mediator must fully carry the effect and have no unblocked back-doors to promotion — but it is worth examining.

---

## Summary of verdicts on prior performance as a control

| Role of Perf | DAG Structure | Verdict |
|---|---|---|
| Classic confounder (Perf → M, Perf → P) | Fork | Control — closes the Perf-driven back-door |
| Near-instrument (r = 0.85 with M) | Strong Perf → M, weak residual | Danger: adjusting amplifies bias from U if U exists |
| Combined: confounder + near-IV with unmeasured U | Both structures present | Net effect: adjusting for Perf removes one back-door but amplifies the remaining one; likely worsens total bias |
| Instrument (if Perf → P path absent) | Perf → M → P only | Could use as IV, but this path exists — exclusion violated |

---

## Direct answer to your colleague's recommendation

Your colleague is **partially right but importantly wrong in this context**.

Controlling for prior performance is the correct move *if* (a) Perf is the only confounder, and (b) you are not worried about unmeasured confounders. In that narrow world, Perf is a textbook confounder and should be controlled for.

But given:
1. The 0.85 correlation between Perf and M (near-IV property)
2. The near-certain existence of unmeasured confounders in a real organizational context

...controlling for Perf is likely to **amplify** the bias from unmeasured confounders rather than reduce total bias. The "great covariate" intuition — "it's highly correlated with treatment, so controlling must help" — is precisely backwards when the variable is functioning as a near-instrument and unmeasured confounding is present.

The right response to your colleague is: "Yes, prior performance is a confounder for the Perf-driven back-door, but its extremely high correlation with mentorship receipt means it also behaves like an instrument. Adjusting for it concentrates the residual variation in mentorship onto the part driven by unmeasured confounders, making those confounders relatively more influential. Unless we can argue that Perf is the only confounder, we should not expect controlling for it to fix — and may expect it to worsen — the bias in our estimate."

The appropriate next step is to (a) conduct sensitivity analysis to quantify the robustness of any estimate to unmeasured confounding, and (b) look seriously for a design-based identification strategy (RDD, natural experiment) that exploits as-if-random variation in mentorship assignment.
