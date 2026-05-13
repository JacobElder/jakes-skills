# TWFE with Staggered Rollout: Is Your +6% Estimate Trustworthy?

Your reviewer is correct, and this is one of the most important — and until recently, most underappreciated — problems in applied causal inference. Let me walk through exactly what's happening and what you should do.

---

## 1. Name the Rung

This is a **Rung 2 (intervention)** question: does the customer success program *cause* renewal rates to increase? You're not asking who will churn (prediction) — you're asking what would happen if the program were deployed. That requires a causal estimator, not just a regression.

The question is whether TWFE with staggered timing gives you a reliable answer to that Rung 2 question.

---

## 2. Sketch the DAG

The structure here is a standard panel DiD setup:

```
Time (Quarter FE) ──────────────────────────────────────┐
                                                         ↓
Region (Region FE) ──> Treatment Status ──> Renewal Rate
                                 ↑
                  Rollout Timing (Q1 / Q3 / Q4)
```

The hope with TWFE is that region fixed effects absorb time-invariant regional differences, and time (quarter) fixed effects absorb common shocks affecting all regions. The identifying variation is regions switching from untreated to treated at different times.

The problem: with **staggered treatment timing**, the "control group" for each cohort isn't just clean never-treated units — it includes **already-treated regions from earlier cohorts**. And that's where the bias enters.

---

## 3. The Core Problem: TWFE Uses Treated Units as Controls

With a single treatment date, TWFE is clean: you compare treated units to untreated units before and after. The parallel trends assumption is straightforward.

With **staggered rollout**, what TWFE actually does is more complicated. The Callaway-Sant'Anna decomposition (2021) and the Goodman-Bacon (2021) decomposition show that the TWFE coefficient is a **weighted average of all pairwise 2x2 DiD comparisons** that can be constructed from the data. There are three types:

1. **Early vs. Never-treated**: Clean — this is what you want.
2. **Late vs. Never-treated**: Clean — this is what you want.
3. **Late vs. Early** (using already-treated early units as the "control"): This comparison is contaminated.

The third type is the problem. When Q3 and Q4 regions are compared against Q1 regions in later periods, the Q1 "control" regions are already treated and have already had their renewal rates shift. If the treatment effect is **dynamic** — meaning it builds over time rather than being a fixed step change — then using already-treated units as a control group negatively biases the estimates from those comparisons, because you're measuring the incremental gain against a baseline that's already been elevated by the treatment. This can cause the overall TWFE coefficient to be **attenuated, sign-flipped, or otherwise misleading** relative to the true average treatment effect.

Critically: **this happens even when parallel trends holds perfectly for every cohort**. It's not a parallel trends violation — it's a mechanical artifact of how TWFE constructs weights under staggered timing.

---

## 4. How Badly Should You Worry?

The severity depends on two things:

**A. How dynamic is the treatment effect?**

If the program has a constant, immediate effect that doesn't change with exposure duration, TWFE is unbiased. If renewal rates improve gradually over the quarters following program adoption (which is plausible — customer success programs often have ramp-up periods, relationship-building takes time), the "late vs. early" comparisons will systematically underestimate the effect of the program by comparing late-adopter gains against early-adopter gains rather than against a clean baseline.

In your setup: a customer success program's effect is almost certainly **dynamic**. Relationships between CSMs and customers deepen over time. You'd expect larger effects at 3 quarters post-treatment than at 1 quarter post-treatment. This is the scenario most dangerous for TWFE.

**B. What share of the identifying variation comes from the "bad" comparisons?**

With 15 Q1 regions, 20 Q3 regions, and 10 Q4 regions, over 18 months:
- Q1 regions are treated earliest and spend the most time as "already treated" — they're actively used as controls for Q3 and Q4 cohorts in those later periods.
- The Goodman-Bacon decomposition would tell you the exact weights, but directionally: you have a large early cohort (15 regions) acting as a contaminated control for two later cohorts (30 regions total). This is not a small slice of the variation — it's likely a substantial share of your identifying variation.

**Bottom line:** You have staggered timing, a plausibly dynamic effect, and a large early cohort. These are the conditions under which TWFE bias is most severe. The +6% could be attenuated, or in extreme cases, could be the wrong sign.

---

## 5. The Right Estimators for This Setting

Several estimators have been developed to handle staggered DiD without these problems. The key insight they share: **only use clean controls** (never-treated or not-yet-treated units) for each cohort-period comparison, then aggregate the cohort-specific effects appropriately.

### Option A: Callaway & Sant'Anna (2021) — Recommended Starting Point

Defines **Group-Time Average Treatment Effects (ATT(g,t))**: the average effect for regions first treated in group *g* at time period *t*. Aggregates these using researcher-specified weights (e.g., equal weight per cohort, weight by cohort size, weight by time since treatment for dynamic effects).

- Never uses already-treated units as controls.
- Lets you see whether the effect is growing, constant, or fading.
- Available in R (`did` package) and Python (`csdid`).

### Option B: Sun & Abraham (2021)

Also fully interacts treatment cohort indicators with time indicators. Produces a clean, cohort-robust estimate. Slightly different aggregation; performs comparably to Callaway-Sant'Anna.

Available in R as `sunab()` in the `fixest` package — easy to implement if you're already using `fixest` for TWFE.

### Option C: Stacked DiD

Manually constructs a "clean" dataset for each cohort: for each treatment cohort, take a window around their treatment date and include only that cohort + clean controls (never-treated or not-yet-treated as of the end of the window). Stack these datasets and run standard TWFE with cohort-specific treatment indicators.

More transparent, easier to explain to non-specialists, but requires careful construction.

---

## 6. What the Analysis Should Look Like

Run the following and compare:

1. **Your original TWFE estimate**: +6% — this is your baseline, potentially biased.

2. **Goodman-Bacon decomposition**: Decomposes your TWFE estimate into its component 2x2 DiDs and their weights. Shows you which comparisons are driving the result and how much weight the "bad" (already-treated) comparisons receive. If those comparisons have negative weights or are a major share of the total, you have a problem.

3. **Callaway-Sant'Anna ATT(g,t) estimates**: Run these and examine:
   - Are cohort-specific effects broadly similar across Q1, Q3, Q4 cohorts?
   - Do effects appear to grow with time since treatment (dynamic effects)?
   - What is the aggregated estimate? How does it compare to +6%?

4. **Pre-trends test**: For each cohort, plot the parallel trends in pre-treatment periods (relative to the cohort's treatment date). Each cohort should be compared against not-yet-treated units at that point in time. A classic TWFE pre-trends test is also biased under staggered timing — use the cohort-robust version.

---

## 7. What to Report to Your Reviewer

**Tell them:** Yes, the reviewer is correct. The standard TWFE estimate with staggered rollout is a weighted average that can include negative weights on valid treatment effects when the effect is dynamic, because already-treated units are used as implicit controls for later-adopting cohorts. This is not a parallel trends violation — it's a weighting problem that occurs even when parallel trends holds for every cohort. Given the plausibility of dynamic effects in a customer success program and the large Q1 cohort serving as a control group for Q3/Q4 regions, the +6% TWFE estimate is suspect and should not be reported as the headline finding.

**Commit to:** Running Callaway-Sant'Anna or Sun-Abraham estimates before presenting conclusions. The Goodman-Bacon decomposition (a quick diagnostic) will tell you how much of the original TWFE estimate comes from contaminated comparisons.

---

## 8. The Most Likely Trap Here

The most likely failure mode in your setting is **effect heterogeneity masked by contaminated controls**: the true per-cohort effects may be larger than +6% (maybe Q1 regions, with 3 extra quarters of program exposure, have 10%+ gains), but the TWFE estimate is being pulled down because Q3/Q4 regions are being measured against Q1 "control" periods where the renewal rate is already elevated. The treatment effect estimate would then be attenuated — possibly substantially — even though the program is genuinely working.

The fix is clean cohort-time comparisons. If the true ATT is larger than +6%, that's a much better story for your customer success program — one that the standard TWFE estimate was obscuring.

---

## Quick Reference: What to Run

| Step | Tool | What it tells you |
|------|------|-------------------|
| Goodman-Bacon decomposition | `bacondecomp` (Stata/R) | Share of variation from bad comparisons, direction of contamination |
| Callaway-Sant'Anna ATT(g,t) | `did` package (R) or `csdid` (Python/Stata) | Cohort-specific effects, clean aggregation |
| Sun-Abraham | `sunab()` in `fixest` (R) | Clean heterogeneity-robust TWFE alternative |
| Dynamic effects plot | From C&S output | Whether effects grow with exposure duration |
| Cohort-robust pre-trends | From C&S output | Whether parallel trends holds per-cohort |

If all three estimators (TWFE-clean, C&S, S&A) agree on ~6%, you can report +6% with confidence. If they diverge, report the C&S or S&A estimate as primary and disclose the TWFE sensitivity.
