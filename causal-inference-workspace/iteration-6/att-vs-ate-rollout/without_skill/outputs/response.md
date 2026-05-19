# Is $32 Revenue Uplift Per User the Right Expectation for a Force-Enable Rollout?

**Short answer: No. The CEO's expectation is almost certainly too high, and may be wrong in direction for some users.**

---

## What Your IV Estimate Actually Measures

Your encouragement design (push notification as instrument) estimates the **Local Average Treatment Effect (LATE)** — also called the Complier Average Causal Effect (CACE). This is the average treatment effect *for compliers only*: users who adopted the feature **because** they received the notification and would not have adopted it otherwise.

### Identifying the Complier Population

In your setup:
- 30% of users received a notification (treated group)
- 18% of notified users adopted the feature
- 3% of non-notified users adopted the feature

The **first-stage compliance rate** (share of notified users who were induced to adopt) is:

```
Compliance rate = Adoption rate (notified) - Adoption rate (control)
               = 18% - 3%
               = 15 percentage points
```

So roughly **15% of notified users** are compliers — the marginal, nudgeable users who adopted *because* of the notification. The remaining 3% who adopted in the control group are "always-takers" (they would have adopted regardless).

The $32 LATE applies **only to this 15% slice of the notified group** — users who were on the fence and needed a nudge.

---

## Why the Force-Enable Rollout Is Different

A force-enable rollout targets a fundamentally different population: **never-takers** — users who, when sent a notification, still did not adopt (and presumably had even lower intent or interest). These are the users who:

- Saw (or ignored) the notification and didn't engage, OR
- Were in the non-notified control group and didn't self-adopt

### The Three User Types (Imbens-Rubin Framework)

| Type | Description | Share (approx.) | Included in LATE? |
|------|-------------|-----------------|-------------------|
| Always-takers | Adopt regardless of notification | ~3% of all users | No |
| Compliers | Adopt only when nudged by notification | ~4.5% of all users* | YES — this is who $32 applies to |
| Never-takers | Don't adopt even when notified | ~92.5% of all users* | No |

*Approximate: 15% compliance rate × 30% notified = ~4.5% of total user base are observed compliers.

The force-enable rollout will be applied almost entirely to **never-takers** — the group most resistant to the feature. The LATE of $32 tells you nothing about them.

---

## Why the $32 Expectation Is Wrong for Force-Enable

### 1. Selection bias in the complier group

Compliers self-selected into adoption when given a gentle push. They had *some* underlying interest or fit with the feature. Never-takers actively or passively resisted adoption even after being informed. Forcing a feature on users who don't want it is unlikely to produce the same engagement and revenue as for users who chose it.

### 2. The LATE is a lower-population, higher-interest estimate

The $32 estimate is for the most nudge-responsive users — the "low-hanging fruit." Force-enabling targets the hardest-to-convert population. The true effect for never-takers could be:
- **Zero**: They ignore the feature even when it's enabled
- **Negative**: Friction, confusion, or annoyance from forced changes leads to churn or downgrades
- **Positive but much smaller**: Some benefit, but far less than $32

### 3. Behavioral vs. passive exposure

The compliers *actively chose* to use the feature after a nudge — that active choice correlates with engagement. Force-enabling does not replicate the decision to engage; a feature being "on" is not the same as a user actually using it.

### 4. No monotonicity violation concern, but external validity concern

IV assumptions require monotonicity (no defiers), which is plausible here. But the **external validity** of LATE to the never-taker population is not guaranteed by IV — IV gives you a local estimate, not a global one.

---

## What Would Be a Better Framework?

To estimate the effect of force-enabling on never-takers, you would need:

1. **A separate experiment**: Randomly force-enable the feature for a subset of non-adopters and measure revenue vs. control.
2. **Heterogeneous treatment effect analysis**: Estimate treatment effect heterogeneity by user characteristics to assess how the effect varies across user types.
3. **Bounds analysis**: Use Manski-style partial identification to bound what the force-enable effect could plausibly be, given what you know about always-takers and compliers.

---

## Summary for the CEO

| Claim | Correct? | Explanation |
|-------|----------|-------------|
| "The LATE is $32" | Yes | Valid IV estimate for compliers |
| "Force-enable will yield $32/user" | No | LATE applies to compliers; force-enable targets never-takers |
| "Revenue will go up" | Maybe | Direction is unknown without additional evidence |
| "Effect will be close to $32" | Unlikely | Never-takers are systematically less interested in the feature |

**The right expectation**: The force-enable effect on non-adopters is unknown from this study and is very likely substantially less than $32 per user. It could be near zero or even negative if forced adoption creates negative user experience. A new randomized experiment targeting non-adopters is needed to estimate this effect credibly before a full rollout.

---

## Key Concepts Referenced

- **LATE / CACE**: Effect of treatment on compliers only (Imbens & Angrist, 1994)
- **Encouragement design**: Using a randomly assigned nudge as an instrument for take-up
- **Always-takers / Compliers / Never-takers**: The three principal strata under monotonicity
- **External validity of IV**: IV estimates are local — they don't automatically generalize to other subpopulations
- **First-stage**: The causal effect of the instrument on treatment take-up (15pp here)
