# Should You Trust the +8% DiD Estimate? No — Here's Why.

## The Short Answer

No. The +8% Difference-in-Differences (DiD) estimate is likely **unreliable and overstated** — possibly entirely an artifact of a pre-existing trend difference rather than a real effect of the new pricing page.

---

## What Went Wrong: Parallel Trends Violation

DiD is built on one core assumption: the **parallel trends assumption**. This requires that, in the absence of the intervention, the treatment and control groups would have followed the same trajectory over time. You don't need them to start at the same level — just the same *rate of change*.

Your setup directly violates this:

- **Pre-rollout:** Treatment markets were growing 25% faster in conversion than control markets.
- **Post-rollout:** All 8 markets converged to similar growth rates.

This pattern — treatment was faster before, then converges after — is the textbook signature of **regression to the mean**, not a treatment effect.

---

## The Core Misinterpretation

Here is what DiD is actually measuring in your case:

```
DiD = (Treatment Post - Treatment Pre) - (Control Post - Control Pre)
```

If treatment markets were on a high-growth trajectory that naturally slowed, and control markets were on a lower-growth trajectory that stayed flat (or slightly improved), the arithmetic will produce a positive DiD estimate even if the new pricing page did **nothing at all**.

Your description — treatment markets growing 25% faster before, then converging to control after rollout — means the *counterfactual* you're implicitly assuming (that treatment markets would have kept outpacing control had they not received the new page) is almost certainly wrong. The "excess" growth the model attributes to the pricing page may simply be the tail end of a pre-existing growth surge that was already decelerating.

---

## How Large is the Bias Risk?

Significant. Without the parallel trends assumption holding, DiD gives you a **biased estimate of unknown direction and magnitude**. In this specific scenario:

- If treatment markets were reverting toward the mean anyway, the true effect could be **less than +8%**, possibly near zero.
- The convergence in growth rates post-rollout is consistent with the rollout having *no effect* — markets simply normalized.
- The +8% may be entirely explained by the 25% pre-existing differential decaying over time.

---

## What You Should Do Instead

### 1. Pre-trend Test (Placebo Test)
Plot conversion growth for both groups across multiple pre-rollout periods. If the trends were non-parallel before rollout, the core DiD assumption is violated and the estimate is invalid.

### 2. Event Study / Dynamic DiD
Estimate period-by-period treatment effects (leads and lags around rollout). If you see significant "pre-treatment effects" (the model picking up differences before the rollout), the parallel trends assumption fails.

### 3. Synthetic Control
Construct a weighted synthetic version of the treatment markets using combinations of control markets that closely match the pre-rollout trajectory of treatment markets. This approach does not assume parallel trends in levels or growth rates.

### 4. Regression Discontinuity (if applicable)
If rollout timing had any threshold or cutoff logic (e.g., markets above a certain size got it first), RD can provide a cleaner local estimate.

### 5. Difference-in-Difference-in-Differences (Triple DiD)
If you have segment-level data within markets (e.g., different customer cohorts), a triple DiD can sometimes control for market-specific trends.

### 6. Control for Pre-Treatment Trends Explicitly
Include market-specific linear time trends in the DiD model to partial out divergent pre-existing trajectories. This is an imperfect but pragmatic adjustment.

---

## The Intuition in Plain English

Imagine two runners: Runner A has been accelerating for the past year; Runner B has been running at a steady pace. You give Runner A new shoes at the start of this year. By the end of the year, both are running at the same speed. You conclude: "The shoes slowed Runner A down by the gap between their old pace and current pace." But the correct interpretation may simply be: Runner A was always going to slow down — the shoes did nothing.

Your pricing page rollout has the same structure. Markets selected for early rollout may have been peaking. The "effect" your DiD captures is likely a combination of mean reversion and selection bias, not a clean causal signal.

---

## Summary

| Issue | Verdict |
|---|---|
| Parallel trends assumption | Violated — 25% pre-existing growth gap |
| Post-rollout convergence | Consistent with zero effect + mean reversion |
| DiD estimate of +8% | Likely upward-biased or entirely spurious |
| Safe to act on? | No — requires additional validation |

**Bottom line:** Do not ship this as evidence that the new pricing page works. Run a pre-trend test first. If divergence exists in the pre-period (which your description strongly implies), the +8% number cannot be trusted without further methodological work.
