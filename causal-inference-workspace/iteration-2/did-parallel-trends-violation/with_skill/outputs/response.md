# DiD Parallel Trends Violation: Should You Trust the +8% Estimate?

**Short answer: No — not without serious qualification. The scenario you've described is a near-textbook case of a parallel-trends violation, and the +8% estimate is likely biased, probably downward toward zero.**

---

## Step 1: Name the Rung

This is a **rung-2 question**: "Did the new pricing page cause higher conversion?" You want to know the effect of an intervention (rolling out the page) on an outcome (conversion rate). The tool chosen — differences-in-differences — is appropriate in principle for rung-2 inference from observational-style rollout data. The question is whether the identifying assumption holds.

---

## Step 2: Sketch the DAG

The DiD estimand operates under a specific causal structure:

```
   Time-invariant group differences (U_group)
              ↓
   Treatment assignment (T) → New pricing page (D) → Conversion (Y)
              ↑
   Pre-existing growth trend (G) → Y
```

The critical background variable here is **pre-existing conversion trajectory** (G). In your setup:
- G is higher in the 3 treatment markets before rollout (+25% faster growth)
- G → Y (pre-treatment trajectory predicts post-treatment outcomes)
- T is correlated with G (treatment assignment is non-random with respect to trajectory)

This creates a fork: **G ← [selection process] → T**, where G is a confounder between treatment assignment and the outcome trajectory. DiD's job is to cancel this out — but it only cancels it if the *trend*, not just the *level*, is the same in both groups absent treatment.

---

## Step 3: Identify the Core Problem — Parallel Trends Violation

DiD's single critical assumption is **parallel trends**: in the absence of treatment, the treated and control groups would have followed the same trajectory.

Your setup directly violates this assumption:

- **Treatment markets were growing 25% faster** than control markets in the pre-period
- This means the two groups were already on diverging trajectories before the rollout
- DiD implicitly assumes that the control group's post-rollout trajectory is a valid counterfactual for what the treatment group's trajectory would have been without treatment

When pre-trends are non-parallel, this assumption fails. The control group's post-period trend is **not** a valid counterfactual for the treatment group.

### The Direction of the Bias

Here's what makes this case particularly suspicious: after rollout, **all 8 markets converged to similar growth rates**. The treatment markets slowed down toward the control markets' pace.

Under parallel trends, if the new pricing page added +8%, you'd expect treatment markets to *still* be growing faster than controls in the post-period (at roughly the same differential as before, plus the added treatment effect). Instead they converged.

There are two competing explanations for this convergence, and they pull the true effect in opposite directions:

**Explanation A — Mean Reversion (bias inflates the estimate)**
The treatment markets were simply in a high-growth phase that was unsustainable. They would have converged back toward control-market growth rates with or without the new pricing page. DiD attributes some of that reversion to the pricing page and misreads mean reversion as treatment effect. In this scenario, the true effect is *less than* +8% — possibly zero or negative.

**Explanation B — Treated Markets Dragged Down by Regression to Mean, Understating a Real Effect**
The new pricing page genuinely helped, but the treatment markets' underlying growth was also mean-reverting simultaneously, creating a cancellation. In this scenario, the true effect is *greater than* +8% — the page helped but you can't see the full effect because underlying trajectories pulled in the opposite direction.

**Explanation C — The Page Caused the Convergence (the intended story)**
The treatment markets slowed down *because* the page homogenized the customer experience, eliminating their natural growth advantage. In this story, the rollout changed the underlying trajectory, not just the level — which itself would require a more nuanced model than standard DiD.

The data pattern you describe is consistent with all three. You cannot distinguish between them without additional information.

---

## Step 4: The Standard Diagnostic — Pre-Trend Plot

The primary diagnostic for DiD is a **pre-period trend plot**:

- Plot conversion growth rates for both treatment and control markets across multiple pre-rollout periods (not just one year collapsed to a single number)
- If the lines are parallel (same slope, possibly different levels), parallel trends is plausible
- If they're diverging or converging in the pre-period, parallel trends fails

You've already told me the answer: treatment markets grew 25% faster in the year before rollout. If this was a steady pre-existing differential — not a one-time anomaly — you have direct evidence against parallel trends. One year of pre-data is typically insufficient to establish trend; you want 2–4 pre-periods to see the shape of the trajectory, not just one data point on each side.

**Diagnostic to run now:** Plot each market's conversion growth rate quarterly (or monthly) for 2 years before rollout and 1 year after. If the treatment markets were consistently above control in the pre-period, you cannot trust a vanilla DiD.

---

## Step 5: Alternative Structures to Rule Out

Before concluding the estimate is garbage, check whether any of these rescue the analysis:

### 5a. Selection on levels, not trends
DiD allows for level differences — it only requires parallel *trends*. If the treatment markets were at a higher level of conversion but growing at the same rate as control markets, and the +25% you cite reflects annualized levels rather than a trend differential, the assumption may still hold. Clarify: is the 25% a growth *rate* differential (slopes differ) or a conversion *level* differential (slopes parallel, levels offset)?

### 5b. Staggered or heterogeneous treatment timing
You have 3 markets treated simultaneously against 5 controls. If any markets received the treatment at different times, canonical two-way fixed-effects DiD has known problems (Callaway & Sant'Anna 2021; Goodman-Bacon 2021 decomposition). In your case this may be moot if the rollout was truly simultaneous, but worth confirming.

### 5c. Differential external shocks
Did the 3 treatment markets experience any economic, competitive, or seasonal shocks during the post-period that the 5 control markets didn't? If so, those shocks — not the pricing page — could explain convergence. This is a parallel-trends violation of a different kind.

---

## Step 6: What the Convergence Pattern Tells You

The convergence pattern is the real signal here. After rollout, treatment markets that were growing 25% faster than controls are now growing at the same rate. That means one of:

1. The pricing page harmed the treatment markets' growth enough to eliminate a 25% advantage (unlikely if the claim is +8% help)
2. The 25% pre-period advantage was transient (mean reversion) and the page had a smaller real effect than estimated
3. The page genuinely caused the underlying trajectory to shift, and the DiD estimand is the wrong object to compute

None of these support confidently accepting +8% at face value.

---

## Step 7: What Would Fix This

### Option 1: Covariate-adjusted DiD
If you have market-level covariates that predict the pre-treatment growth differential (market size, product-market fit, seasonality, competitive intensity), you can condition on them and estimate a conditional DiD. This works if the *residual* trend, controlling for those covariates, is parallel. It requires domain knowledge and a good set of controls.

### Option 2: Synthetic control
With 8 markets (3 treated, 5 untreated), you have enough untreated units to build a synthetic control — a weighted combination of the 5 control markets that matches the treatment markets' pre-period trajectory as closely as possible. Synthetic control explicitly matches on pre-trends, which is exactly what vanilla DiD doesn't do. Abadie's synthetic control method is well-suited to this setup.

### Option 3: Interrupted time series
If you have enough time periods, you can model each market's individual trend and estimate a break at the rollout date. This doesn't rely on a comparison group at all — it extrapolates each market's pre-period trajectory and tests for a level/slope change post-rollout. Weaker than a control group design, but doesn't require parallel trends between groups.

### Option 4: Pre-trend test and honest reporting
Run a formal test for pre-trends (e.g., regress outcomes on treatment × pre-period time dummies; test joint significance). If the test rejects parallel pre-trends at conventional significance levels, report that your estimate is unreliable and bound the plausible effect range rather than point-estimating.

---

## Bottom Line

The +8% estimate should not be trusted as stated. The scenario has a near-certain parallel-trends violation: treatment markets were growing significantly faster before rollout and converged to control-market rates afterward. Standard DiD's identifying assumption requires that this convergence be caused by the treatment — but mean reversion is an equally (and arguably more) plausible explanation.

The estimate is confounded by pre-existing trajectory differences. Depending on how much of the convergence reflects mean reversion vs. real treatment effect, the true impact of the new pricing page could be anywhere from negative (the page slowed natural growth leaders) to substantially positive (the page helped but you can't measure it cleanly against a noisy baseline).

**The three most actionable next steps:**
1. Plot quarterly pre-trends for all 8 markets — visualize whether the 25% differential was stable or a one-period anomaly
2. Run a synthetic control analysis using the 5 control markets to match treatment-market pre-period trajectories
3. Formally test pre-trend equality; if it fails, report bounds rather than a point estimate

Claiming +8% in a board deck or product review without addressing the pre-trend violation is a meaningful analytic error. The honest answer is: "preliminary signal, assumptions not yet validated."
