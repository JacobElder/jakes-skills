# TWFE with Staggered Rollout: Is Your +6% Estimate Reliable?

Your reviewer is correct, and yes, you should be worried. This is one of the most important methodological insights in applied econometrics from the last several years. Let me break down what's happening and what you should do.

---

## The Core Problem: TWFE is a Weighted Average of Many 2x2 DiDs

Standard two-way fixed effects (TWFE) with a single "treated" indicator implicitly decomposes into a weighted average of pairwise difference-in-differences comparisons. In a staggered rollout, the estimator uses **three types of comparisons**:

1. **Early-treated vs. never-treated** (clean comparison)
2. **Late-treated vs. never-treated** (clean comparison)
3. **Early-treated vs. late-treated** — and here's the problem: it uses early-treated units *as a control group* for the late-treated units, even though those early-treated units are already treated

The third type of comparison is the dangerous one. When treatment effects are **heterogeneous across cohorts** (different adoption timing groups) or **dynamic** (effects grow or change over time), the early-treated units serve as "bad controls." Their already-accumulating treatment effect gets differenced away in a way that can produce severe bias — including estimates with the **wrong sign** even when parallel trends holds perfectly.

**Your specific setup makes this likely:**
- Q1 adopters (15 regions) have 18 months of treatment by end of period
- Q3 adopters (20 regions) have ~12 months
- Q4 adopters (10 regions) have ~6 months

When TWFE estimates the Q3 effect, it compares Q3 adopters against both never-treated *and* Q1 adopters. The Q1 regions in that comparison are already experiencing treatment effect dynamics (perhaps a ramp-up or saturation), which introduces negative weights on some comparisons. If treatment effects are heterogeneous or dynamic, these negative weights can flip or bias your estimate.

---

## Why Parallel Trends Is Not Sufficient

Parallel trends is about the *untreated potential outcomes* — it says that in the absence of treatment, all groups would have trended the same way. Parallel trends says nothing about:

- Whether treatment effects are the same across cohorts
- Whether treatment effects are stable or dynamic over time

TWFE can be biased even when parallel trends holds *exactly* if there is any cohort-level or time-varying heterogeneity in treatment effects. This is the key insight from Goodman-Bacon (2021), Callaway & Sant'Anna (2021), Sun & Abraham (2021), and de Chaisemartin & D'Haultfoeuille (2020).

---

## How to Diagnose Whether You Have a Problem

**Step 1: Goodman-Bacon Decomposition**
Decompose your TWFE estimate into its constituent 2x2 DiD components and their weights. Look for:
- Negative weights (a red flag)
- Whether the components with negative weights have large absolute effect magnitudes
- How much of your overall estimate is driven by comparisons using treated-vs-treated

In Stata: `bacon treated outcome, ddetail`
In R: `bacon()` from the `bacondecomp` package

**Step 2: Event Study Plot**
Plot pre-treatment trends and post-treatment effects by time-relative-to-treatment. Look for:
- Pre-trend violations (the standard check)
- Diverging post-treatment trajectories across cohorts (suggesting effect heterogeneity)

**Step 3: Check Effect Heterogeneity Across Cohorts**
Do Q1, Q3, and Q4 adopters show similar renewal rate improvements? If the Q1 regions show dramatically larger or smaller effects than Q3/Q4, heterogeneity is present and TWFE is suspect.

---

## Better Estimators to Use Instead

### 1. Callaway & Sant'Anna (2021) — Recommended Starting Point
Estimates cohort-average treatment effects (CATT) for each (cohort, time) combination, using only clean control groups (never-treated or not-yet-treated units). Then aggregates as desired.

- **Pros:** Transparent, flexible, handles parallel trends conditional on covariates
- **Cons:** Requires a never-treated or not-yet-treated group as a clean control

In R: `did` package — `att_gt()` then `aggte()`
In Stata: `csdid`

### 2. Sun & Abraham (2021)
An interaction-weighted estimator that estimates cohort-specific effects within the TWFE framework by saturating the model with cohort x event-time interactions.

- **Pros:** Easy to implement as a modified TWFE regression, integrates naturally into existing workflows
- **Cons:** Slightly less flexible than Callaway & Sant'Anna

In R: `fixest` package — `sunab()` function
In Stata: `eventstudyinteract`

### 3. de Chaisemartin & D'Haultfoeuille (2020)
Estimates a weighted average of instantaneous switching effects, robust to heterogeneous treatment effects.

- **Pros:** Handles more general treatment patterns, well-suited for panel data
- **Cons:** Conceptually estimates a different (more local) parameter

In Stata/R: `did_multiplegt` package

---

## Interpreting Your +6% Result

Your +6% estimate could be:
- **Approximately correct** if treatment effects are homogeneous across cohorts and stable over time (the TWFE assumptions happen to hold)
- **Attenuated** if early adopters' effect is being used negatively in the comparison for later adopters
- **Inflated** if the weighting happens to overweight high-effect comparisons
- **Correct in sign but wrong in magnitude**, which in practice is the most common outcome

The fact that you have three distinct adoption cohorts with different sample sizes (15, 20, 10) and meaningful differences in treatment duration means effect heterogeneity is very plausible.

---

## Recommended Action Plan

1. **Run the Goodman-Bacon decomposition** to understand what comparisons are driving your +6%
2. **Plot an event study** with cohort-stratified event-time indicators to visually inspect pre-trends and post-treatment dynamics across cohorts
3. **Re-estimate with Callaway & Sant'Anna or Sun & Abraham** and compare results to your TWFE estimate
4. **Report both estimates** — if they're close (+5-7%), your TWFE result is probably robust. If they diverge substantially, the heterogeneity-robust estimate should be preferred and the discrepancy should be explained

---

## Bottom Line for Your Reviewer

Your reviewer is raising a legitimate and well-documented concern. The critique is not about parallel trends being violated — it's that **TWFE is not the right estimator for staggered rollouts even when parallel trends holds**, because it implicitly makes assumptions about treatment effect homogeneity that are rarely justified in practice.

The fix is straightforward: use a heterogeneity-robust DiD estimator (Callaway & Sant'Anna is the most widely used and cited). If your +6% estimate survives that robustness check, you can report it with confidence. If it doesn't, you've learned something important about your program's effects across different adoption cohorts.

---

*Key references:*
- *Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. Journal of Econometrics.*
- *Callaway, B. & Sant'Anna, P. (2021). Difference-in-differences with multiple time periods. Journal of Econometrics.*
- *Sun, L. & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. Journal of Econometrics.*
- *de Chaisemartin, C. & D'Haultfoeuille, X. (2020). Two-way fixed effects estimators with heterogeneous treatment effects. American Economic Review.*
