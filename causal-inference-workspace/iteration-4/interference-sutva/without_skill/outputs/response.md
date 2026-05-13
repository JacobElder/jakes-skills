# A/B Test Extrapolation and Interference

## Short Answer

Yes, your colleague is right to raise this concern. The +15% engagement figure from your A/B test may not hold when you launch to all users. The key issue is a violation of a core assumption in causal inference called **SUTVA** (Stable Unit Treatment Value Assumption), specifically the **no-interference** component.

---

## What Is Interference?

In a randomized experiment, we typically assume that one person's treatment assignment doesn't affect another person's outcomes. This assumption is called **no interference** (the "I" in SUTVA).

Formally: the potential outcome for user *i* should depend only on *i*'s own treatment assignment — not on anyone else's.

Your feature — showing users when their friends are online — violates this assumption almost by definition. Whether I'm in treatment or control, my *experience* depends heavily on whether my friends are in treatment or control:

- If I'm in **treatment** and my friends are in **control**, I can see when they're online, but they can't see when I'm online. The feature is asymmetric.
- If I'm in **treatment** and my friends are **also in treatment**, we can both signal presence to each other. The social feedback loop is fully activated.
- The engagement value of the feature is a function of **network density in treatment**, not just my own assignment.

---

## Why the A/B Test Estimate Is Biased

In your experiment, treatment users were embedded in a mixed network: roughly half their friends were in control. The treatment effect you measured (+15%) reflects a world where treatment users have partial network exposure — only ~50% of their social connections could potentially reciprocate online-status signals.

At full launch, **every user is in treatment**. Now:
- Treatment users' friends are all also in treatment
- The feedback loops are fully activated
- Network effects compound

This means the true effect at full launch could be **substantially larger than +15%**. But it could also be smaller in the other direction if:
- The novelty of seeing friend status drives early engagement that habituates
- The feature creates social pressure ("I can see you're online") that drives churn in some user segments
- Saturation effects reduce marginal value as everyone has the same information

---

## The Formal Problem: SUTVA Violation

SUTVA requires two things:
1. **No interference**: Your treatment doesn't affect my outcome
2. **No hidden treatment versions**: There's only one version of the treatment

Your experiment violates condition 1. The potential outcome framework assumes:

```
Y_i(t_1, t_2, ..., t_n) = Y_i(t_i)
```

But in your case, Y_i actually depends on the treatment assignments of user *i*'s friends, not just on *t_i* alone. The observed treatment effect is:

```
Observed ATE = E[Y_i(1) - Y_i(0) | ~50% of neighbors treated]
```

What you want for full launch is:

```
Target estimand = E[Y_i(1) - Y_i(0) | 100% of neighbors treated]
```

These are different estimands. There's no guarantee they're close in magnitude or even sign.

---

## How Serious Is This?

For a **social feature that is explicitly about social presence signaling**, this is a high-severity concern. The feature's value is almost entirely derived from network effects. This isn't a minor bias — the whole mechanism of action is the social feedback loop.

Compare this to a feature like changing button color: whether my friends see a red or blue button has essentially no effect on my behavior. Interference is negligible there. For your feature, interference is the core mechanism.

---

## What You Can Do

**1. Cluster Randomization**
Randomize at the level of social clusters (friend groups, communities) rather than individual users. Treatment clusters get the feature; control clusters don't. This reduces interference because within-cluster, most friends share the same treatment.

- Downside: Far fewer independent units, much lower statistical power

**2. Ego Network Analysis**
Look at how the treatment effect varies as a function of what fraction of a user's friends are also in treatment. If you see the effect growing as network exposure increases, that's direct evidence of interference and gives you a dose-response curve to extrapolate from.

**3. Two-Stage Randomization**
First randomize the probability of treatment (low-saturation vs. high-saturation communities), then randomize individual assignment within those. This lets you estimate effects at different levels of network saturation and interpolate to 100%.

**4. Causal Models with Spillovers**
Fit a model that explicitly parameterizes the spillover effect — e.g., include "fraction of friends in treatment" as a covariate and model its interaction with own treatment.

**5. Be Transparent About Uncertainty**
If you can't run a better experiment, present the +15% figure as a lower bound (assuming network effects are positive) with explicit caveats about the extrapolation assumption.

---

## Bottom Line

| Concern | Severity |
|---|---|
| Interference violates SUTVA | High — this is the core mechanism of your feature |
| A/B estimate ≠ full-launch effect | High — estimands are genuinely different |
| Direction of bias | Uncertain — likely underestimates positive effects, but habituation/social pressure could flip it |
| Colleague's concern is valid | Yes |

Your +15% estimate is a valid measure of the average treatment effect **under the experimental conditions** (50% saturation). It is not a valid estimate of the effect under full rollout (100% saturation). Your colleague is correct. The extrapolation requires either a better experimental design or a model of how the effect scales with network saturation.
