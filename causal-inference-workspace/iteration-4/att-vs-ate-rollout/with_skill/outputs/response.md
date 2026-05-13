# Causal Inference Analysis: LATE vs. ATE for Premium Feature Rollout

**Short answer: No, $32 per user is not the right expectation for a forced rollout. Your CEO is conflating the LATE — the effect for a very specific subgroup — with the ATE, which is what a universal rollout would actually produce. These can differ substantially, and in your setup, the LATE is almost certainly an overestimate of the ATE.**

---

## 1. Name the rung

The CEO's question is a **rung-2 (intervention) question**: "What happens if we *do* X to all remaining users?" But the $32 LATE is estimated from an experiment involving *voluntary adopters* — people who responded to a nudge. Rolling out to everyone is a different intervention on a different population. The rung is right, but the estimand is wrong.

---

## 2. Sketch the DAG and what the LATE actually captures

Your encouragement design (push notification as instrument Z) estimates the **Local Average Treatment Effect (LATE)** — also called the **Complier Average Causal Effect (CACE)**. Here is what that means structurally.

Your instrument Z (notification) partitions users into four latent types based on their adoption behavior:

| Type | Notified group | Not-notified group | Description |
|------|---------------|-------------------|-------------|
| **Compliers** | Adopt | Don't adopt | Adopt *because* of the nudge — the only type the LATE identifies |
| **Always-takers** | Adopt | Adopt | Would have adopted regardless; not affected by the instrument |
| **Never-takers** | Don't adopt | Don't adopt | Won't adopt no matter what |
| **Defiers** | Don't adopt | Adopt | (Typically assumed away by monotonicity) |

Your adoption rates:
- Notified group: 18% adoption
- Control group: 3% adoption
- Complier share: 18% − 3% = **15% of users**

The LATE is the average treatment effect *for compliers only* — the 15% of users who adopted because they received the notification and would not have adopted otherwise.

The 3% in the control group who adopted anyway are **always-takers**: they wanted the feature regardless of being nudged. The remaining ~82% of notified users who still did not adopt after receiving the notification are **never-takers** (at least with respect to this nudge).

---

## 3. Why the LATE cannot be directly applied to the forced rollout

When the CEO wants to "force-enable" the feature for all non-adopters, the target population changes dramatically. The people remaining who have *not* adopted are overwhelmingly **never-takers** — users who either did not respond to the notification or were not notified, but in either case have not voluntarily adopted.

The LATE of $32 was identified entirely from **compliers**: users who were on the margin, receptive enough to a nudge to adopt. By definition, compliers are the segment *most likely to benefit* from the feature — they opted in when given a low-friction opportunity. Never-takers are definitionally more resistant and quite plausibly derive less value from the feature.

Extrapolating the LATE to the never-taker population is only valid under the assumption of **treatment effect homogeneity** — that every user gets the same $32 benefit from the feature. That assumption is almost certainly wrong, and the direction of the bias is predictable:

- Users who resist a feature even after being invited tend to have weaker use cases for it, less alignment with the feature's value proposition, or active preference against it.
- Compliers who adopted after the nudge self-selected into a group with at least some underlying interest.
- The ATE for forced adoption across all non-adopters will very likely be **lower** than $32 — possibly substantially lower, and potentially negative for some segments (e.g., users who find the feature disruptive or intrusive).

---

## 4. The key structural issue: LATE vs. ATE

Formally, the quantities are:

- **LATE** = E[Y(1) − Y(0) | complier] = $32 (your estimate)
- **ATE** = E[Y(1) − Y(0)] = weighted average across compliers, always-takers, and never-takers
- **ATT** = E[Y(1) − Y(0) | adopted] = effect among those who actually adopted (already-done; not directly answerable from IV)

For the rollout decision, the CEO needs something close to:

**E[Y(1) − Y(0) | never-taker]** — the effect of forcing adoption on the people who have not adopted.

The IV estimator gives you the LATE; it says nothing directly about never-takers. Applying the LATE to never-takers is not an identification issue — it is a **population mismatch**.

---

## 5. What actually drives the bias — the DAG

A simplified DAG for this setup:

```
Z (notification) → D (adoption) → Y (revenue)
                    ↑
              U (latent affinity for feature)
              ↓
              Y (revenue)
```

U represents unobserved heterogeneity — how well the feature matches a user's needs, their usage patterns, their willingness to pay. U causes both adoption propensity and revenue impact. The notification instrument is valid precisely because it is independent of U (random assignment).

But U is exactly what predicts *who* is a complier vs. a never-taker. Compliers have higher U — enough to adopt when nudged, but not high enough to self-discover and adopt unprompted. Never-takers have lower U — the feature doesn't resonate enough to motivate adoption even when invited.

So the LATE is identified for the high-U segment of non-always-takers. Applying it to the low-U population of never-takers ignores this selection on U.

---

## 6. What to tell the CEO

The $32 LATE is a real and meaningful causal estimate — it's an unbiased estimate of the effect *for compliers*, and that's not nothing. But it is the effect for the most receptive non-adopters, not for the non-adopters who remain after the nudge.

**A more defensible expectation-setting:**

1. **The $32 figure is an upper bound for the forced rollout**, not the central estimate. The actual ATE on remaining non-adopters is likely lower. How much lower depends on how heterogeneous treatment effects are — and you have evidence suggesting they are heterogeneous (some people adopted spontaneously, some with nudging, most not at all).

2. **Forced adoption introduces behavioral risk** that the experiment doesn't capture. Users who didn't want the feature and have it force-enabled may experience friction, generate support tickets, or churn at higher rates. These costs don't appear in your IV estimate because compliers *chose* to adopt.

3. **To estimate the ATE more accurately**, you would need either:
   - A separate RCT where a random sample of remaining non-adopters is force-enrolled (your actual intervention), measuring 6-month revenue versus a held-out control group of non-adopters.
   - Heterogeneous treatment effect analysis — segmenting users by observable proxies for U (engagement level, plan type, usage patterns) and estimating whether revenue uplift varies by segment. If effect size correlates strongly with user engagement, that's evidence the LATE overestimates the ATE for the bulk of the population.

4. **The complier population is well-suited for further nudges**, not force-enablement. If the goal is revenue uplift without behavioral risk, a more intensive notification campaign (in-app prompts, onboarding flows, 1:1 outreach for high-value accounts) would operate on a population more similar to the complier pool than a blanket force-enrollment would.

---

## 7. Most likely trap being committed

This is a **LATE-to-ATE extrapolation error** — applying an IV estimate to a population the instrument was never designed to represent. It's easy to miss because the LATE sounds like "the effect of the feature," but it is specifically "the effect of the feature, for users who were on the margin of adoption and needed one nudge to cross over."

The forced rollout targets the *opposite* of that population.

---

## Summary

| Question | Answer |
|----------|--------|
| Is $32 an unbiased causal estimate? | Yes — for compliers (the 15% who adopted because of the nudge) |
| Does the LATE apply to the forced rollout population? | No — the rollout targets never-takers, who are structurally different |
| Is $32 the right central estimate for rollout revenue uplift? | No — it is likely an overestimate, possibly a significant one |
| What should the CEO expect? | Lower than $32 per forced-enrolled user; direction is correct but magnitude is uncertain |
| What would give a more reliable estimate? | A dedicated RCT of forced enrollment on a held-out sample of non-adopters |
