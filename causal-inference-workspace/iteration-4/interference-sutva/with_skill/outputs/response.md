# Response: A/B Test Interference and the SUTVA Problem

Yes, your colleague is right to flag this — and the concern is serious enough that it should change how you interpret your +15% result before you commit to a rollout projection. Let me walk through why.

---

## Step 1: Name the rung

Your A/B test is a rung-2 question: "What would happen if we intervened and gave all users the online-presence feature?" You ran an RCT, which is great for identification. But the specific concern here isn't about confounding or identification in the usual sense — it's about whether the experiment's estimand (the effect you measured) matches the rollout's estimand (the effect you want to project).

---

## Step 2: Sketch the causal structure — and where it breaks down

Standard A/B test logic rests on a core assumption called **SUTVA: the Stable Unit Treatment Value Assumption**. SUTVA has two parts:

1. **No interference:** A user's outcome depends only on *their own* treatment assignment, not on other users' assignments.
2. **No hidden treatment versions:** "Treatment" means the same thing regardless of how or when it's applied.

Your feature — showing users when their *friends* are online — violates assumption #1 structurally. The value of seeing a friend as "online" depends on whether that friend is in the treatment or control group.

Here's what's happening in your experiment:

- **Treatment users** can see when their friends are online.
- **But only ~50% of those friends are also in treatment** — the other half are in control and aren't broadcasting their online status (or their status isn't being surfaced to them, depending on your implementation).

This means treatment users in the experiment are experiencing a *diluted* version of the feature: the social graph is half-lit, not fully lit. They can see online status for maybe half their friends, not all of them.

---

## Step 3: Identify the trap — spillover and the treatment-density problem

The specific structure of this interference is what economists sometimes call a **network effect** or **social spillover**. In potential-outcomes language:

- In the experiment: Y_i(1) means "user i's engagement when i is treated *and* ~50% of their social graph is treated"
- At full rollout: Y_i(1) means "user i's engagement when i is treated *and* 100% of their social graph is treated"

These are different potential outcomes. Your experiment measured the first; you want to predict the second.

The direction of bias is almost certainly **downward**: the feature should be *more* valuable at full rollout than in your experiment, because every friend a user has will be visible when online. The true +15% is probably a lower bound on the full-rollout effect — possibly substantially so.

But here's the other side of the coin: the +15% you measured might *also* be partially explained by **novelty** or **network externalities that create local clusters**. If users in dense friend-clusters both tend to be in treatment and tend to activate each other, the treatment effect in your experiment could be inflated by local-cluster dynamics that won't scale uniformly across all user types.

So in practice, the extrapolation error can go in *either direction* depending on the social graph structure:

| Mechanism | Direction of bias | Why |
|---|---|---|
| Feature is more valuable when all friends are online | Experiment *understates* rollout effect | Diluted treatment in experiment |
| Local cluster saturation / early adopter networks | Experiment *overstates* rollout effect | Dense treatment clusters drive early numbers |
| Control group deprivation (cross-group envy) | Experiment *overstates* rollout effect | Control users noticing they lack the feature |

The net direction is an empirical question about your specific social graph — you can't know without more analysis.

---

## Step 4: What should you do?

### Option A: Cluster-randomized experiment (the gold standard fix)

Instead of randomizing at the user level, randomize at the **friend-cluster or community level**: entire social circles go to treatment or control together. This way:

- Treatment users have 100% of their friends in treatment (within-cluster)
- Control users have 0% of their friends in treatment
- SUTVA is approximately restored

The catch: cluster randomization requires more clusters than you probably have if clusters are large, and you lose statistical power. But it gives you a clean estimate of the full-deployment effect.

### Option B: Varied-density treatment analysis (next best)

If you have social graph data, you can look at your current experiment through the lens of **local treatment density**: what fraction of each treatment user's friends are *also* in treatment? If the feature's value scales with local density, you'll see a dose-response curve. Extrapolating that curve to density=1.0 (full rollout) gives you a better projection than taking the global +15% at face value.

This is a form of using the experiment you have to estimate the counterfactual you want, but it requires modeling assumptions about how the social spillover scales.

### Option C: Staged rollout with monitoring (pragmatic fallback)

Roll out to progressively larger fractions (10%, 25%, 50%, 75%, 100%) and measure engagement at each stage. If SUTVA violation is the dominant concern, you'll see the measured effect *increase* as treatment density increases. If it decreases, novelty or cluster effects are dominating. Either way, you learn the shape of the curve before committing to the projection.

---

## Bottom line

Your +15% estimate is real — you ran a properly randomized experiment. But it is **not the right number to plug into a full-rollout projection**, because the experiment and the rollout expose users to fundamentally different social environments. Your colleague is correct: the extrapolation is invalid as-is.

The honest summary:
- The true rollout effect is probably *at least* +15%, because more friends will be visible at full saturation.
- But it could also be higher or lower depending on network structure, novelty, and whether control-group users were being affected by their treatment-group neighbors.
- To get a defensible projection, you need either cluster randomization, a density-stratified analysis of your current data, or a staged rollout with measurement at each density level.

The good news: this is a solvable problem, and the experiment you already ran gives you useful signal to work with. You're not starting from scratch — you're refining the estimate.
