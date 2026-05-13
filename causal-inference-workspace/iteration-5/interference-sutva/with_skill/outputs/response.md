# Should You Be Worried About Interference? Yes — And Here's Why It's Serious

Your colleague is right to flag this. The interference problem for a social feature is not a minor technical concern — it's a fundamental threat to the validity of your extrapolation. Let me walk through this precisely.

---

## Step 1: Name the Rung

Your A/B test answered a **Rung 2 (intervention)** question: *what happens to engagement when we assign users to see friend-online-status?* That is genuinely causal.

But your extrapolation is asking a **different Rung 2 question**: *what happens to engagement when we deploy this feature to everyone?* These are not the same intervention, and that distinction is the entire problem.

---

## Step 2: What "Interference" Means — The SUTVA Violation

The standard causal inference framework (both Pearl's do-calculus and the Neyman-Rubin potential outcomes model) rests on an assumption called **SUTVA: the Stable Unit Treatment Value Assumption**. It has two parts:

1. **No interference:** A unit's potential outcome depends only on its own treatment assignment, not on others' assignments.
2. **No hidden versions of treatment:** There is only one version of "treated."

Your feature violates Part 1 spectacularly.

### Why the Violation Is Structural, Not Incidental

The feature is "see when your friends are online." Think about what that means:

- A **treatment user** can see online-status signals only for friends who are **also online** — which is more likely when those friends are in the treatment group and are themselves engaging more (or in the control group but happen to be online).
- A **control user's** behavior is affected by whether their friends are in treatment or control: if a friend is in treatment and is now more active and sending messages, the control user receives more messages and social stimuli, independent of their own assignment.
- A **treatment user's** experience depends heavily on how many of their friends are also in treatment: if most of your friends are in control and offline-invisible, the online-status feature gives you very little to act on.

In formal notation: let $Y_i(t_i, \mathbf{t}_{-i})$ be user $i$'s potential outcome, where $t_i$ is their own treatment and $\mathbf{t}_{-i}$ is the treatment vector of all other users. SUTVA requires $Y_i(t_i, \mathbf{t}_{-i}) = Y_i(t_i)$ for all $\mathbf{t}_{-i}$. For a social feature, this is almost certainly false.

---

## Step 3: The DAG

Here is a simplified causal diagram:

```
Friend's Treatment Assignment (T_j)
        |
        v
Friend's Online Visibility (V_j)  ←── Friend's Engagement (E_j) ←── T_j
        |
        v
User i's Engagement (E_i) ←────────── User i's Treatment (T_i)
```

The key structural point: **T_j (friend's treatment) is an arrow into E_i.** Your randomization gave each user an independent T_i, but it did not — and cannot — randomize the T_j vector. At 50/50 allocation, the average treatment user has roughly 50% of their friends in control. At full rollout, every user has 100% of their friends in treatment.

This is a **network spillover**: the causal effect of your own treatment status on your outcome is moderated by the treatment saturation of your social neighborhood.

---

## Step 4: Why the +15% Is the Wrong Number for Full Rollout

Your experiment estimated the **Average Treatment Effect (ATE)** under a specific network saturation condition: approximately 50% of each user's social graph is treated.

Call this $\tau(s)$ where $s$ is the saturation level. You measured $\tau(0.5)$.

When you do a full rollout, you are asking about $\tau(1.0)$. The two quantities can differ substantially and in either direction:

### Scenario A: Complementarity (the feature is more valuable at full saturation)

Online-status is only useful if your friends are also visible. At 50% saturation, many treatment users had invisible friends — they could see who was online, but half their graph wasn't. At 100% saturation, every friend is visible. The feature becomes dramatically more valuable. In this case, $\tau(1.0) > \tau(0.5)$, and your +15% estimate is a **lower bound**. Full rollout could be better than you think.

### Scenario B: Control-group contamination deflated the control baseline

Control users at 50% saturation were being nudged by their treated friends: more messages arriving, more activity in their feeds. This inflated the control-group engagement baseline. Your treatment effect is measured relative to a contaminated control. At full rollout, the counterfactual is "everyone without the feature" — a much lower engagement floor. In this case, $\tau(1.0) < \tau(0.5)$... wait, actually: if treated users look better because control users were also boosted, the *measured* effect understates the true effect at 100% treatment. Let me be precise:

Let $\bar{Y}_T$ = mean engagement, treatment group, $\bar{Y}_C$ = mean engagement, control group (which is contaminated upward by spillovers from treated friends). Your measured ATE = $\bar{Y}_T - \bar{Y}_C$. The true total-effect at full rollout is $\bar{Y}_T(\text{everyone treated}) - \bar{Y}_C(\text{everyone untreated})$. Because $\bar{Y}_C$ was inflated by spillovers, your measured +15% is likely a **conservative underestimate** of the total effect.

### Scenario C: Social dynamics and norms change at scale

At 50% saturation, online-status is novel and "only some people have it." At 100%, new social norms form around response-time expectations, always-on pressure, etc. These second-order effects are invisible in a 50/50 experiment.

**The key takeaway:** You don't know which scenario you're in. The sign of the bias is genuinely ambiguous without understanding the mechanism.

---

## Step 5: What Your Experiment Actually Estimated

Your experiment provides a valid estimate of the **direct effect** of being assigned online-status, holding the social environment at a specific saturation level (≈50%). This is a well-defined causal quantity — but it is **not** the total effect of universal deployment.

More precisely, what you measured is closest to the **individual treatment effect under partial equilibrium**, not the **total equilibrium effect under full deployment**.

There is a formal framework for this: **Exposure Mapping** (Aronow & Samii, 2017). Rather than a single treatment indicator, you define each user's "exposure" as a function of both their own assignment and their neighborhood's assignment. Under this model, you'd need to estimate effects under multiple saturation levels to extrapolate to full rollout.

---

## Step 6: The Most Likely Trap Here

The most likely failure mode in your case is not that the +15% is wildly wrong — it might be in the right ballpark. The failure mode is that **you don't know the direction of the error**, and for a social feature, the complementarity story (Scenario A) is plausible enough that the true effect at full rollout could be substantially larger than +15%. That seems like good news, but it also means your confidence interval for the post-launch effect is genuinely wide, not tight.

There is also a second trap: **engagement by whom?** If treatment users are engaging more partly because they are messaging control users more (who then respond), and you're measuring engagement across both groups, some of the +15% in treatment is net activity, not newly-created value. At full rollout, there is no control group to stimulate — net engagement gain could be different.

---

## Step 7: What You Should Do

### Diagnostic: Was there spillover in the experiment?

You can test for interference directly:
1. **Estimate the effect of friend-saturation on control-group engagement.** Among control users, regress engagement on the fraction of friends who were in treatment. If this coefficient is positive and significant, you have direct evidence of spillover.
2. **Estimate treatment effects as a function of friend-saturation among treatment users.** Did treatment users with more treated friends show higher engagement gains? This tells you about complementarity.

These are Rung 1 (association) analyses, but in this context they are diagnostics for the interference structure, not causal claims.

### Better Experimental Design for Future Tests

If the concern is important enough, run a **cluster-randomized experiment**: randomize at the level of social clusters (friend groups, communities) rather than individual users. Within a cluster, everyone is either all-treatment or all-control. This eliminates cross-cluster contamination and gives you clean estimates of $\tau(1.0)$ vs. $\tau(0.0)$. The downside is massive variance inflation (cluster-level variance >> user-level variance) and the need for many independent clusters.

An even better design for network features is a **saturation experiment** (also called a two-stage experiment): randomly assign clusters to different treatment *rates* (e.g., 0%, 25%, 50%, 75%, 100%), then randomize individuals within clusters at those rates. This lets you estimate $\tau(s)$ as a function of saturation — exactly the quantity you need to extrapolate to full launch.

### For Your Immediate Decision

Given what you have:
- The +15% is a real signal. User-level randomization did isolate the individual assignment effect, even if it doesn't isolate the full equilibrium effect.
- The interference structure suggests the feature has **social complements** — it is more valuable when more people have it. This tilts the expected direction of extrapolation error toward the positive.
- You should present the +15% as a conservative-to-moderate estimate of the total effect, with the caveat that the true effect at full rollout depends on network saturation dynamics that the experiment was not designed to measure.
- If you run the spillover diagnostic (step 1 above) and find no significant effect of friend-saturation on control-group engagement, you have empirical evidence that interference was weak in your specific population, which strengthens the extrapolation.

---

## Summary

Your colleague is correct that the SUTVA assumption is violated by this feature, and the +15% cannot be cleanly extrapolated without additional assumptions. The mechanism is structural: online-status creates network complementarities, so a user's potential outcome is a function of their entire social neighborhood's treatment status, not just their own.

The good news: for a feature with positive social complements, the experiment-measured effect under 50% saturation is plausibly a lower bound on the full-rollout effect, not an overestimate. The worry is less "we'll be disappointed" and more "we don't actually know the shape of the saturation curve." If the full-rollout effect is what's driving the business case, a cluster-randomized or saturation experiment would give you a defensible number.

The bottom line: don't abandon the +15% figure, but do present it correctly — as the individual treatment effect under partial saturation, not as the total equilibrium effect of a full launch.
