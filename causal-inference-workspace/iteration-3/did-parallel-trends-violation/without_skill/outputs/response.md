# Should You Trust Your DiD Estimate of +8%?

**Short answer: No, not without significant scrutiny. The setup you've described contains a textbook parallel trends violation, which is the foundational assumption of Difference-in-Differences. Your +8% estimate is likely biased.**

---

## What the Data Is Telling You

You've described a situation where:

- Treatment markets were growing **25% faster** in conversions than control markets in the pre-period
- After rollout, **all 8 markets converged** to similar growth rates
- Your DiD estimate shows **+8% lift** from the new pricing page

The problem is the order of these facts. DiD assumes that, absent treatment, both groups would have continued along **parallel trajectories**. Your pre-period data shows they were not on parallel trajectories — treatment markets were on a steeper upward curve.

---

## The Core Problem: Regression to the Mean

The most likely explanation for your results is **regression to the mean**, not a causal effect of the pricing page.

Markets that are growing unusually fast — 25% faster than peers — are often experiencing a temporary spike driven by noise, seasonality, competitive dynamics, or some local factor that temporarily inflated their numbers. When that temporary boost fades, they naturally slow down and converge toward the group average. This convergence would have happened **with or without the new pricing page**.

Your DiD model is interpreting this natural convergence as evidence that the pricing page flattened growth. But wait — it estimates a **positive** +8% effect. Here's how the math still produces a spurious positive: if treatment markets were already on a decelerating trajectory (regressing back to mean), the control markets may have also slowed but slightly more. The DiD estimator picks up the *relative difference* in changes. The +8% could easily reflect:

- Treatment markets decelerating less than expected (because the pricing page partially offset a natural slowdown)
- Or simply noise in the convergence pattern

Without true parallel trends, you cannot distinguish genuine treatment effect from artifact.

---

## Why the Parallel Trends Violation Is Serious Here

Parallel trends is not just a statistical nicety — it is the entire identifying assumption of DiD. It states:

> In the absence of treatment, the average outcome for the treatment group would have followed the same trend as the average outcome for the control group.

You have direct evidence this assumption fails. The pre-treatment divergence (treatment growing 25% faster) tells you the groups were on different trajectories. The post-treatment convergence is consistent with several stories, only one of which is "the pricing page caused this."

Alternative stories:
1. **Regression to the mean** — treatment markets were randomly high and naturally reverted
2. **Selection into treatment** — if markets were chosen for rollout *because* they were high-growth, you have selection bias baked in from the start
3. **Mean reversion + real effect** — the pricing page had a real positive effect, but it was masked by a concurrent mean reversion; your +8% could be an underestimate
4. **No real effect** — the +8% is entirely explained by the convergence dynamic

---

## What You Should Do Instead

**1. Pre-treatment trend test**
Formally test whether pre-period trends are parallel using a placebo-in-time approach or by including interaction terms for each pre-period unit of time. A statistically significant pre-trend is a red flag you already have strong informal evidence for.

**2. Investigate why those 3 markets were growing faster**
Was it a specific product launch? A local competitor exiting? Seasonality? If you can explain the pre-period divergence with observable covariates, you may be able to control for it.

**3. Consider a synthetic control approach**
Instead of using all 5 control markets equally, build a weighted synthetic counterfactual that matched the treatment markets' pre-period trajectory. This can handle pre-existing trend differences more gracefully.

**4. Use an augmented DiD or matching**
Methods like Callaway-Sant'Anna or doubly-robust DiD estimators can help when parallel trends is suspect, especially if you have covariates that explain group differences.

**5. Look at the event study**
Plot the DiD coefficients for each time period, not just the post-treatment average. If you see pre-trend coefficients that are already drifting before treatment, that confirms the violation. If the post-period coefficients spike only after rollout and the pre-period coefficients are flat, you have more credibility — but given what you described, expect to see pre-period drift.

**6. Ask about treatment assignment**
Why were those 3 markets chosen? If they were selected because of their high growth (to "test on the best"), you have a non-random assignment problem that DiD alone cannot fix. You need to understand the assignment mechanism.

---

## The Bottom Line

The convergence of growth rates after rollout — when treatment markets were *already* growing faster than control — is a classic confound. Your +8% estimate reflects the change in *relative* growth rates between groups, but since those relative growth rates were already changing (converging) for reasons unrelated to the pricing page, you cannot causally attribute the +8% to the intervention.

This does not mean the pricing page had zero effect. It may well have had a real positive effect. But your current estimate is not credible because the identifying assumption is violated. Before making business decisions on this number, invest in at least one of the diagnostic steps above — particularly the event study and the synthetic control — to bound what the true effect might be.

The uncomfortable truth is: the most likely story here is **regression to the mean**, and any measured effect is confounded with that dynamic. You need a method that accounts for non-parallel pre-trends before this estimate should inform a rollout decision.
