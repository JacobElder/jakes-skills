# Should You Worry About Interference?

Yes. Your colleague is right, and the concern is serious. The +15% estimate from your A/B test is internally valid — but it is measuring something different from what a full launch would produce. The gap between those two quantities is exactly what interference (and the assumption it violates, called SUTVA) is about.

---

## Step 1: Name the Rung

Your question is **Rung 2 — intervention**: "What will happen to engagement if we roll this feature out to everyone?" That is a do-operator question: P(engagement | do(feature = on for all users)).

The A/B test gives you a clean Rung 2 estimate — but the estimand it identifies is not the same as your rollout estimand. That is the core problem.

---

## Step 2: Sketch the DAG and the Violation

The standard A/B test logic assumes **SUTVA** — the Stable Unit Treatment Value Assumption. SUTVA has two components:

1. **No interference**: my potential outcome depends only on my own treatment assignment, not on anyone else's.
2. **No hidden versions of treatment**: "treatment" means the same thing for everyone.

Your feature — seeing when friends are online — breaks assumption 1 by design. Whether I benefit from seeing my friends' online status depends on how many of my friends are *also* in the treatment group. If only 50% of users are treated, most people's friend networks are half-dark: I can see when treatment friends are online, but not control friends. Under full launch, everyone is visible to everyone.

Structurally, the potential outcomes framework collapses. In the standard setup, each user i has two potential outcomes: Y_i(1) (engaged, treated) and Y_i(0) (engaged, control). SUTVA lets us write the treatment effect as Y_i(1) − Y_i(0). But with interference, the correct notation is Y_i(z_1, z_2, ..., z_n) — my outcome depends on the full vector of everyone else's assignments, not just my own. The "treatment effect" is not a single number; it is a function over the entire assignment vector.

What your A/B test measured: the effect of being treated **when 50% of the network is treated**. Call this the partial-equilibrium effect.

What full launch produces: the effect of everyone being treated **when 100% of the network is treated**. This is the full-equilibrium effect — and it is a different quantity.

---

## Step 3: Which Direction Does This Bias Go?

This is the critical question, and the answer depends on the social mechanism.

**The +15% is likely an underestimate.**

Here is why. In the A/B test, treated users can see which of their friends are online — but only the treatment half. Control users' status is invisible. Under full launch, treated users would see the full friend network's online status, which is a richer, more useful signal. The spillover from having more visible friends goes in the positive direction: the feature becomes more valuable as network penetration increases. This is a positive network externality.

If the feature's value scales with the fraction of friends who are also in treatment, then:
- At 50% penetration, you see half your network → +15% lift
- At 100% penetration, you see the full network → lift > 15%

The extrapolation of "+15% at full launch" is not just imprecise — it is directionally conservative in this case. You may be underselling the feature.

**But the opposite direction is also possible**, and you should not dismiss it:

- If the feature primarily drives *coordination* (e.g., users reach out to online friends), and treated users in the experiment were reaching out to *both* treated and control friends (creating asymmetric notification behavior), then the mechanism in the experiment differs from the full-launch mechanism in complicated ways.
- If the feature creates **information overload or social pressure** at scale (many friends online at once feels overwhelming), the effect could flatten or reverse at high penetration.
- If the main effect was novelty-driven, the experiment may have captured a novelty spike that won't persist at scale regardless of network penetration.

The point is not that the sign is certainly wrong — it is that the experiment's estimand and the rollout's estimand are different quantities, and the direction of the gap requires a mechanistic argument, not a statistical one.

---

## Step 4: Why the Standard Extrapolation Fails Formally

Under SUTVA, the A/B test identifies the ATE: E[Y_i(1) − Y_i(0)]. This equals the expected engagement gain under full rollout because Y_i(1) is stable — it does not depend on others' assignments.

With interference, Y_i(1) is not stable. What you actually estimated is something closer to:

> E[Y_i(1, z_{−i} ~ Bernoulli(0.5)) − Y_i(0, z_{−i} ~ Bernoulli(0.5))]

This is the direct effect of treatment on user i when the rest of the network is independently 50% treated. Full rollout produces:

> E[Y_i(1, z_{−i} = 1 for all j)]

These two quantities differ whenever Y_i depends on z_{−i} — which it does here by construction, because the feature is a function of what other users' statuses are visible.

---

## Step 5: What Should You Do?

**Short-term:** Flag the SUTVA violation explicitly. Do not present "+15% at full launch" as a confident point estimate. Present it as the lower bound under positive network externalities, or as an uncertain baseline that requires mechanistic modeling to extrapolate.

**Better experimental designs for network effects:**

1. **Cluster randomization (ego-network or geographic clustering).** Randomize at the level of clusters — friend groups, geographic regions, or communities — so that within each cluster, treatment is either all-on or all-off. This eliminates interference within clusters and lets you estimate the full-equilibrium effect rather than the partial-equilibrium effect. The tradeoff is power: cluster-level randomization has far fewer independent units.

2. **Bernoulli graph experiments with saturation design.** Assign different clusters to different saturation levels (e.g., 0%, 25%, 50%, 75%, 100% of cluster members treated). This lets you directly estimate the dose-response relationship between network penetration and individual lift — and extrapolate to 100% saturation empirically rather than theoretically.

3. **Staggered geographic rollout.** Roll out to one region at a time, with clean geographic separation, and use DiD to compare regions before and after rollout. This approximates the full-equilibrium effect if geographic networks don't spill across boundaries.

**Mechanistic analysis:** Model the feature's value as a function of the fraction of a user's friends who are also treated. Even a simple regression of individual lift on "fraction of friends in treatment" gives you a slope that lets you extrapolate to 100% penetration. If this slope is positive, the full-launch effect is larger than +15%.

---

## Summary Verdict

| Question | Answer |
|---|---|
| Is the A/B test internally valid? | Yes. The within-experiment comparison is clean. |
| Does +15% estimate the full-launch effect? | No. SUTVA is violated by design. |
| What did the experiment actually measure? | Direct effect at 50% network saturation. |
| Which direction is the bias? | Likely upward at full launch (positive externality), but mechanism-dependent. |
| What is the right fix? | Cluster randomization or saturation design to identify the full-equilibrium effect. |

Your colleague is right to flag this. The interference concern is not a nitpick — for a social feature whose value is intrinsically a function of others' behavior, SUTVA is the wrong assumption, and any extrapolation from a user-level randomization requires a mechanistic argument about how the effect scales with network penetration.
