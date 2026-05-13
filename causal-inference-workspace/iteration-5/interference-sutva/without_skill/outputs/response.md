# Should You Be Worried About Interference?

Yes, your colleague is right to raise this concern. The extrapolation from your A/B test result to a full-launch expectation is problematic, and interference is exactly the right term for the issue. Let me walk through what's happening, why it matters, and what the consequences are for your +15% estimate.

---

## The Core Problem: SUTVA and Why Your Experiment Violates It

Classical causal inference — including the logic behind standard A/B tests — rests on an assumption called **SUTVA**: the Stable Unit Treatment Value Assumption. It has two components:

1. **No interference between units**: The potential outcome for any one user depends only on that user's own treatment assignment, not on whether other users are treated.
2. **No hidden versions of treatment**: There is only one version of the treatment, not multiple variants that happen to be labeled the same.

Your experiment almost certainly violates the first condition, and the violation is not incidental — it's structural to the product you're testing.

The feature is "users in the treatment group can see when their friends are online." Think carefully about what this means for the experiment:

- A treated user can only see online status indicators for **friends who are also in the treatment group**.
- Because you randomized at the user level with 50% probability, a treated user, on average, only has **about 50% of their friends** in the treatment group.
- This means treated users in your A/B test experienced a substantially **diluted** version of the feature compared to what they would experience if the feature were fully launched to everyone.

Under full launch, 100% of a treated user's friends would be visible in the online status feature. During your experiment, only ~50% were. The product experience — and therefore the behavioral response — is different in these two scenarios.

---

## The Direction and Magnitude of the Bias

Interference can bias experimental estimates in different directions depending on whether treatment effects are **complementary** or **substitutable** across the network. For a social presence feature, the effects are almost certainly complementary:

- The feature becomes more valuable as more of your friends are also using it.
- Seeing 5 friends online is useful. Seeing 50 friends online is much more useful.
- More visible friends means more opportunities for real-time interaction, which drives engagement.

This is a **positive network externality**: the value of the feature scales with adoption. Under this model:

> Your A/B test measured the effect at ~50% network saturation. Full launch represents 100% network saturation. The true effect at full launch is likely **larger** than +15%, not equal to it.

So the extrapolation problem isn't that you'll overpromise — it's that you may actually be underselling the feature.

---

## The Spillover Problem: Your Control Group Isn't Clean

There's a second form of interference operating simultaneously that further complicates your estimate.

In your experiment, treated users changed their behavior — they saw who was online and (presumably) engaged more, messaged more, posted more, or initiated more interactions. Some fraction of those interactions landed on **control-group users**, who are friends with treated users.

This means your control group wasn't experiencing a true "no feature" world. They were experiencing a world where some of their friends were actively engaging more due to the feature. Their engagement may have been lifted by this spillover — more messages received, more notifications, more reasons to open the app — even though they never saw the online status indicator themselves.

If control-group engagement is artificially elevated by spillover from treated users, then:

- The denominator of your treatment effect estimate (control group mean) is inflated.
- The measured lift (+15%) is **smaller** than the true causal effect of a world-with-feature vs. a world-without-feature.

Again, this pushes the observed estimate downward relative to the true full-launch effect.

---

## Putting It Together: What the +15% Actually Estimates

Let's be precise about the estimand. In a standard A/B test under SUTVA, you estimate:

**Average Treatment Effect (ATE)** = E[Y(1)] - E[Y(0)]

Where Y(1) is the potential outcome under treatment and Y(0) under control, for each user independently. This is the right quantity for extrapolating to a full launch — if SUTVA holds.

Under interference, potential outcomes are not just functions of each user's own assignment. They're functions of the entire assignment vector across the network. A user's outcome depends on what fraction of their neighbors are treated. So the true potential outcome is something like:

Y_i(z_i, z_{N(i)})

where z_{N(i)} captures the treatment exposure of user i's neighbors.

Your experiment estimated something like:

E[Y_i(1, ~0.5)] - E[Y_i(0, ~0.5)]

That is, the effect of being personally treated versus untreated, holding fixed the fact that approximately 50% of neighbors are treated. But a full-launch extrapolation requires:

E[Y_i(1, 1.0)] - E[Y_i(0, 0.0)]

These are different quantities. Your experiment cannot directly identify the full-launch effect without additional modeling assumptions about how outcomes scale with neighbor treatment saturation.

---

## Concrete Example to Build Intuition

Suppose the feature works as follows: a user's engagement increases by 5% for each friend whose online status they can see. In a 50% randomized experiment, a user with 10 friends can see ~5 friends' status on average, gaining ~25% engagement. Under full deployment, they see all 10 friends' status and gain ~50% engagement.

If you measured the A/B test effect and found +15% (some users have more friends, some less, some are more reactive), you might naively extrapolate to +15% at full launch. But the actual full-launch effect, under this nonlinear model, would be much higher — because everyone's neighbor saturation doubles.

The exact numbers are illustrative, not precise, but the direction is clear: linear extrapolation from 50% to 100% saturation almost certainly underestimates the true full-deployment effect for a feature with network externalities.

---

## What You Should Do

**For this launch:**

- Acknowledge that the +15% is a conservative estimate of full-launch lift, not an unbiased one.
- The interference here likely means the true effect is higher than +15%, not lower, because of complementary network externalities.
- You can note this as a risk in the positive direction: the feature may perform better than the experiment suggests.

**For future experiments on network features:**

1. **Cluster randomization**: Randomize by geographic region, city, or detected social community rather than at the individual user level. This contains interference within clusters and allows valid comparisons between clusters. The tradeoff is reduced statistical power because you have fewer independent units.

2. **Ego-network saturation designs**: Intentionally assign different users to receive treatment at varying levels of neighbor saturation (e.g., 0%, 25%, 50%, 75%, 100% of friends treated). This lets you directly estimate the dose-response relationship and extrapolate to full saturation.

3. **Graph-cluster randomization**: Use community detection (Louvain, spectral clustering, etc.) on your social graph to find densely connected subgraphs. Randomize entire communities to treatment or control. This minimizes the cross-arm links that create interference while respecting the network's natural clustering structure.

4. **Exposure modeling post-hoc**: Even with your current data, you can construct a "network exposure" variable for each user — what fraction of their friends were treated — and model outcomes as a function of both own assignment and neighbor saturation. This lets you estimate the saturation-response curve from your existing experiment, with caveats about the modeling assumptions required.

---

## Summary

| Question | Answer |
|---|---|
| Is interference a real concern here? | Yes — the feature is inherently relational and its value scales with how many friends are treated. |
| Does your experiment violate SUTVA? | Almost certainly yes, on the no-interference condition. |
| Is the +15% estimate biased? | Yes — it estimates the effect at ~50% network saturation, not 100%. |
| In which direction is the bias? | Downward — the true full-launch effect is likely larger than +15%. |
| Will you overpromise if you cite +15%? | Unlikely — you're more likely to understate the effect. |
| What should future experiments do differently? | Cluster or saturation-based randomization designs. |

Your colleague is right that the extrapolation is problematic, but the practical implication here is nuanced: for a feature with strong positive network externalities, interference usually means the experiment *understates* the full-launch effect. The +15% should be treated as a lower bound on expected impact, not a precise point estimate, and the uncertainty should be communicated honestly alongside the result.
