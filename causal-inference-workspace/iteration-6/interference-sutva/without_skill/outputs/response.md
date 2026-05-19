# A/B Testing and Interference: Should You Be Worried?

**Yes, your colleague is right to flag this. You should be worried.**

The extrapolation from your A/B test result to a full-launch prediction is likely flawed due to a phenomenon called **interference** (also called **spillover**), which violates a core assumption underlying causal inference in experiments.

---

## The Core Assumption You're Violating: SUTVA

Most causal inference frameworks — including the potential outcomes framework underlying A/B tests — rely on an assumption called **SUTVA**: the **Stable Unit Treatment Value Assumption**. SUTVA has two parts:

1. **No interference**: A user's outcome depends only on their own treatment assignment, not on the treatment assignment of other users.
2. **No hidden versions of treatment**: The treatment is well-defined and consistent across units.

Your experiment almost certainly violates the **no-interference** condition.

---

## Why "Online Status Visibility" Creates Interference

The feature you tested — showing users when their friends are online — is **inherently social and network-dependent**. Here's the problem:

- In your A/B test, treatment users (50% of the population) could see when their friends were online.
- But many of those friends were in the **control group** and therefore *could not* see the online status of others.
- A treatment user's experience depended not just on their own assignment, but on **how many of their friends were also in treatment**.

This means the treatment effect you measured is **not the treatment effect you'll get at full launch**. At full launch, 100% of users will have the feature — a fundamentally different social environment than what you tested.

---

## The Direction of the Bias (and Why It Could Go Either Way)

The key question is: does the spillover inflate or deflate your measured effect?

**Likely scenario — your +15% is an underestimate:**

In your experiment, a treatment user sees their friends online and can initiate interactions. But if those friends are in control and don't have the feature, the friends may be less responsive, less aware they're being seen, or less likely to reciprocate. The social feedback loop is incomplete. At full launch, both sides of the interaction have the feature, so the engagement bump from mutual visibility could be *larger* than +15%.

**Alternative scenario — your +15% is an overestimate:**

If treatment users were engaging more *because* they were a novelty minority — e.g., they were reaching out to friends who weren't expecting it, creating a surprise effect — then at full launch, when everyone has it, the novelty wears off and the equilibrium engagement lift could be smaller.

**Network equilibrium effects:**

At full launch, you may reach a new social equilibrium. People may become accustomed to being "seen" and adjust behavior (e.g., appearing offline to avoid unwanted contact). These equilibrium effects are invisible in a short-term A/B test with partial rollout.

---

## A Concrete Illustration

Suppose your social network is a simple graph of friend pairs. Consider a pair (Alice, Bob):

| Scenario | Alice | Bob | What Alice Sees |
|---|---|---|---|
| A/B Test (both in treatment) | Treatment | Treatment | Bob online — engages |
| A/B Test (Alice treatment, Bob control) | Treatment | Control | Bob online — engages, but Bob doesn't see Alice back |
| Full Launch | Treatment | Treatment | Bob online — both aware, richer interaction |

In your A/B test, half of Alice's friend pairs fall into the "Alice treatment, Bob control" cell. At full launch, *all* pairs are in the "both treatment" cell. The measured effect in the experiment is a weighted average of these mixed conditions — not the pure, fully-deployed effect.

---

## What You Should Do

1. **Do not assume +15% extrapolates directly.** The true effect at full launch could be higher or lower, and you need a better estimate.

2. **Cluster-randomized experiment**: Instead of randomizing at the user level, randomize at the *community* or *friend-group* level. Assign whole clusters to treatment or control so that within a cluster, all users share the same condition. This eliminates within-cluster interference.

3. **Ego-network or graph cluster designs**: More sophisticated designs (e.g., Bernoulli graph cluster randomization) can explicitly model the fraction of treated neighbors and let you estimate both direct and spillover effects.

4. **Measure spillover directly**: With your existing data, compare treatment users who have many treated friends vs. few treated friends. If engagement scales with "treated friend fraction," that's direct evidence of interference — and gives you a way to extrapolate to 100% treated.

5. **Staged rollout with monitoring**: Roll out gradually (e.g., 50% → 75% → 100%) and measure whether the effect per-user changes as the treated fraction increases. If it does, interference is real and you can model it.

---

## Bottom Line

Your colleague is correct. The "+15% will extrapolate to all users" claim assumes that users' outcomes are independent of each other's treatment status — an assumption that is clearly violated when the feature itself is about social visibility and interaction. The true full-launch effect could be anywhere from less than +15% (if the test inflated novelty effects) to more than +15% (if the mutual-visibility network effect compounds at scale). You need a design that accounts for network interference before committing to a launch prediction.
