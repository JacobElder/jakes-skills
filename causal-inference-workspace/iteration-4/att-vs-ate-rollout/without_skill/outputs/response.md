# Causal Inference Analysis: LATE vs. ATE and the Force-Rollout Decision

## Short Answer

No, $32 per user is not the right expectation for a force-rollout. The LATE estimated from the encouragement design applies only to *compliers* — the specific subset of users who adopted the feature *because* they received the notification. Force-enabling the feature for everyone reaches a much broader and different population, and there is no IV-based evidence that the $32 effect holds for them.

---

## What the Encouragement Design Actually Estimates

### The Setup

| Group | N (relative) | Adoption Rate |
|---|---|---|
| Notified (Z=1) | 30% of users | 18% |
| Not notified (Z=0) | 70% of users | 3% |

### The IV / LATE Calculation

The LATE (also called CACE — Complier Average Causal Effect) is:

```
LATE = ITT / First Stage
     = (Revenue_notified - Revenue_control) / (Adoption_notified - Adoption_control)
     = Revenue difference / (0.18 - 0.03)
     = Revenue difference / 0.15
```

This $32 estimate represents the average revenue uplift **only for the compliers** — the ~15% of notified users who adopted *because of the notification* and would not have adopted otherwise.

---

## Who Are the Compliers?

In an encouragement design with one-sided or partial non-compliance, users fall into latent subgroups:

| Subgroup | Behavior | Fraction (approx.) |
|---|---|---|
| **Always-takers** | Adopt regardless of notification | ~3% (the control group adoption rate) |
| **Compliers** | Adopt only when notified | ~15% (the marginal adopters) |
| **Never-takers** | Never adopt, notification or not | ~82% |

The LATE of $32 is the effect for **compliers only**. We learn nothing from this design about:
- Always-takers (they were already going to adopt)
- Never-takers (they didn't adopt even when nudged — the vast majority of users)

---

## Why the Force-Rollout Expectation Is Wrong

When the CEO force-enables the feature for all non-adopters, the target population is roughly:

- **Never-takers**: ~82% of users — people who received a push notification and still didn't adopt. These are the most resistant users.
- **Some always-takers who simply hadn't seen the notification yet**: a small fraction.

The $32 LATE is estimated from compliers — users who are *responsive to a gentle nudge*. Never-takers are, by revealed preference, unresponsive to the notification. There are strong reasons to expect they would generate *less* incremental revenue from forced adoption:

1. **Selection into non-adoption is informative.** Users who ignored a push notification had low willingness to try the feature. Forced usage often leads to low engagement, churn, or backlash.

2. **The mechanism differs.** Compliers chose to adopt after a soft nudge — they were relatively interested. Force-enabling bypasses choice entirely, targeting those least interested.

3. **LATE ≠ ATE.** The Average Treatment Effect (ATE) for the full population could be higher or lower than $32. Without additional assumptions, the IV design does not identify it.

4. **Possible negative effects.** Forced feature activation on unwilling users can cause frustration, support ticket volume, or increased churn — potentially negative revenue effects.

---

## What Estimate Would Be Appropriate?

| Quantity | What It Measures | Available? |
|---|---|---|
| **LATE / CACE** | Effect on compliers (nudge-responsive users) | Yes — $32 |
| **ATE** | Effect on the full user population | Not identified by this design |
| **ATT** | Effect on users who would voluntarily adopt | Partially — close to LATE + always-taker effect |
| **Effect on never-takers** | Effect on forced-adoption resisters | Not identified — this is exactly what we need |

To estimate the effect of a force-rollout on non-adopters, the company would need a separate experiment: **randomly force-enable the feature for a subset of non-adopters** and measure the revenue outcome. That would directly estimate the causal effect on the relevant population.

---

## Practical Recommendations

1. **Do not use $32 as the forecast for the force-rollout.** It is the wrong estimand for the wrong population.

2. **Run a holdout experiment before full rollout.** Force-enable the premium feature for a random 10–20% of non-adopters and measure 6-month revenue vs. a control group of non-adopters. This gives the direct causal estimate needed.

3. **Consider heterogeneous treatment effects.** Even within compliers, the $32 is an average. Some user segments (high-value, power users) may drive most of the effect. Targeting force-rollout to those segments would be more defensible.

4. **Weigh behavioral risks.** Track engagement quality, support volume, and churn for any forced cohort — revenue per user is not the only outcome that matters.

---

## Summary

The $32 LATE is a credible causal estimate, but it applies to a narrow, self-selected group of users who responded positively to a gentle nudge. A force-rollout to all non-adopters — predominantly never-takers — is a categorically different intervention on a different population. Projecting $32/user onto that population conflates the LATE with the ATE and ignores the behavioral signal that non-adopters have already revealed: they don't want the feature. The CEO's expectation should be revised downward, and ideally tested directly before committing to the policy.
