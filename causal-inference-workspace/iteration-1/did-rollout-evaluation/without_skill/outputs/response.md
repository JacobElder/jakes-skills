# Estimating the Impact of a New Pricing Page Rollout

## Overview

Your situation is nearly ideal for causal inference: you have a natural experiment with treated and control groups, longitudinal data, and a clean pre/post period. The go-to framework here is **Difference-in-Differences (DiD)**, potentially enhanced with **Synthetic Control** methods given the small number of treatment units.

---

## 1. Difference-in-Differences (DiD)

### Core Idea

DiD compares the *change* in conversion rates in the treated markets (before vs. after rollout) to the *change* in conversion rates in the control markets over the same period. By using the control markets' trend as a counterfactual, you remove confounders that affect all markets similarly (e.g., seasonality, global economic conditions).

**The estimator:**

```
ATT = (Treated_Post - Treated_Pre) - (Control_Post - Control_Pre)
```

### Implementation Steps

**Step 1: Define the time window**
- Pre-period: all months before the rollout quarter
- Post-period: the rollout quarter and any months after
- Be precise about which month the rollout occurred in each treated market (if they staggered)

**Step 2: Run the regression**

The standard panel regression:

```
Conversion_it = α + β₁(Treated_i) + β₂(Post_t) + β₃(Treated_i × Post_t) + ε_it
```

Where:
- `Treated_i` = 1 if market i received the new pricing page
- `Post_t` = 1 if the time period is after rollout
- `β₃` = the DiD estimate — the causal effect you care about

Add market fixed effects (replaces `Treated_i`) and time fixed effects (replaces `Post_t`) to absorb time-invariant market characteristics and common time trends:

```
Conversion_it = α_i + γ_t + β(Treated_i × Post_t) + X_it + ε_it
```

**Step 3: Cluster standard errors**
- Cluster at the market level to account for serial correlation within markets
- With only 8 markets, clustering gives you few clusters — consider wild cluster bootstrap for more reliable inference

---

## 2. Validating the Parallel Trends Assumption

DiD only works if, absent the treatment, treated and control markets would have followed similar trends. This is the **parallel trends assumption** — it cannot be proven, only assessed.

**How to check it:**

1. **Visual inspection**: Plot monthly conversion rates for all 8 markets from the 2-year pre-period. Do the treated and control markets trend together before the rollout? Large divergences suggest a problem.

2. **Placebo/event study test**: Run an event study specification that estimates separate treatment effects for each pre-period month:

   ```
   Conversion_it = α_i + γ_t + Σ_k β_k (Treated_i × Month_k) + ε_it
   ```
   
   Where k indexes months relative to the rollout (k = -24, -23, ..., -1, 0, 1, ...). If the pre-period βs (k < 0) are statistically indistinguishable from zero, parallel trends is supported.

3. **Covariate balance check**: Compare treated and control markets on pre-period baseline characteristics (market size, pre-trend slope, volatility). Very different markets are a warning sign.

---

## 3. Synthetic Control (Recommended Addition)

With only 3 treated markets and 5 controls, your sample is small. The **Synthetic Control Method** (Abadie et al.) is designed for exactly this setting.

### Idea

For each treated market, construct a weighted combination of control markets that best matches the treated market's *pre-period* conversion trajectory. This synthetic twin serves as the counterfactual. The treatment effect is the gap between the treated market's actual post-period performance and its synthetic twin's performance.

### Why it's valuable here

- More transparent: you can see *which* control markets make up the synthetic control and how well the pre-period match is
- Inference via permutation: run the same procedure on each control market (placebo tests) and compare the gaps — if your treated markets have unusually large post-period gaps, that's evidence of a real effect
- Works well with small N (few treated units)

### Practical note

In Python, use the `pysynth` or `SyntheticControlMethods` libraries. In R, use the `Synth` package.

---

## 4. Handling Staggered Rollout

If the 3 treated markets didn't all receive the new pricing page at the same time within the quarter, you have a **staggered DiD** setting. Standard two-way fixed effects (TWFE) DiD can give biased estimates in this case due to "forbidden comparisons" (already-treated units acting as controls for later-treated units).

**What to do:**

- Use the **Callaway & Sant'Anna (2021)** estimator or the **Sun & Abraham (2021)** estimator, which compute clean group-time average treatment effects and aggregate them
- In R: `did` package (Callaway & Sant'Anna), `fixest` package with `sunab()` (Sun & Abraham)
- In Python: `pyfixest` with staggered DiD support, or `doubleml`

If all 3 treated markets went live in the same month, standard TWFE is fine.

---

## 5. Accounting for Market Heterogeneity

Your 8 markets likely differ in size, growth rate, and baseline conversion. A few adjustments:

- **Log-transform or normalize conversion rates** if markets differ vastly in scale, to avoid larger markets dominating the estimates
- **Include market-level covariates** (e.g., GDP per capita, mobile vs. desktop traffic share, language) if you suspect these correlate with both treatment selection and outcomes
- **Check for spillovers**: if markets share customer segments or if brand perception in one market affects others, SUTVA (stable unit treatment value assumption) may be violated — assess this qualitatively

---

## 6. Checking for Selection Bias in Treatment Assignment

A critical question: **Why were these 3 markets chosen for the rollout?**

- If they were selected randomly, you're in great shape
- If they were selected because they were high-performing, low-performing, or "easy wins," there may be regression to the mean or other selection effects that bias your estimate
- If selection was based on observable characteristics (e.g., market size), control for those in the regression
- If selection was based on unobservable factors correlated with conversion trends, DiD may still be biased — be transparent about this limitation

---

## 7. Practical Checklist

| Step | Action |
|------|--------|
| Data prep | Panel format: one row per (market, month) |
| Define treatment | Binary indicator + exact rollout date per market |
| Visual check | Plot all 8 markets' pre-period trends |
| Run event study | Estimate pre-period coefficients; check they're near zero |
| Run TWFE DiD | Get point estimate + clustered SEs |
| Run Synthetic Control | Validate with permutation inference |
| If staggered | Use Callaway-Sant'Anna or Sun-Abraham |
| Report | Effect size, confidence interval, pre-trend plot, placebo tests |

---

## 8. Interpreting and Reporting Results

- Report the ATT (Average Treatment Effect on the Treated) in absolute percentage points and relative lift (e.g., "conversion increased by 1.2 pp, or +15% relative to pre-period baseline")
- Report the event study plot — it's the most compelling visual evidence
- Be explicit about assumptions and their plausibility given your context
- Consider power: with only 8 markets and monthly data, you may have limited statistical power to detect small effects — a power analysis is worthwhile

---

## Summary

The best approach is a **two-way fixed effects DiD regression** with an **event study specification** to validate parallel trends, combined with **Synthetic Control** as a robustness check. If the rollout was staggered across the quarter, use a heterogeneity-robust estimator like Callaway & Sant'Anna. With 2 years of pre-period data across 8 markets, you have a solid foundation for credible causal inference.
