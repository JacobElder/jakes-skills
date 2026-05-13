# Estimating the Impact of the New Pricing Page

## Rung

This is a **Rung 2 (intervention)** question. You want to know what the new pricing page *does* to conversion rates — not just whether treated markets and control markets differ. The answer requires causal reasoning, not pure association.

---

## Design

You have the classic setup for **Differences-in-Differences (DiD)**:

- 8 markets total: 3 treated, 5 controls
- Monthly conversion data for 2 years pre-rollout (pre-period) and 1 quarter post-rollout (post-period)
- Treatment is a one-time, market-level change (the new pricing page)

This is a panel DiD with multiple treated units and multiple control units, which is the best-case scenario for this design. Two years of pre-period data is more than enough to evaluate the core assumption.

---

## DAG (in prose)

```
    Market characteristics (U)
         ↙              ↘
  New Pricing Page  →  Conversion Rate
  (Treatment D)            (Y)
         ↑
  Rollout decision (W)
```

The main worry is that W — why *these* 3 markets got the new page — is correlated with market-level characteristics U that also affect conversion trends. DiD handles **time-invariant** versions of U automatically (they cancel in the double difference). The residual threat is that U creates **differential trends** — markets that were going to grow faster regardless got selected for rollout. That's the parallel-trends threat.

---

## Estimator

**Two-way fixed effects (TWFE) OLS regression:**

```
Y_{mt} = α_m + γ_t + β · D_{mt} + ε_{mt}
```

Where:
- `Y_{mt}` = conversion rate for market `m` in month `t`
- `α_m` = market fixed effects (absorb all time-invariant market differences — market size, baseline propensity to convert, regional effects)
- `γ_t` = time fixed effects (absorb all shocks common to all markets — seasonal trends, global macro, platform-wide changes)
- `D_{mt}` = indicator for whether market `m` has the new pricing page active in month `t`
- `β` = the DiD estimate; the average treatment effect on the treated (ATT)

Use **clustered standard errors at the market level** — observations within a market are serially correlated, and ignoring that will give artificially narrow confidence intervals. With only 8 markets, note that you have a small number of clusters (see failure modes below).

---

## Key Assumption: Parallel Trends

**In the absence of the new pricing page, the 3 treated markets would have followed the same conversion trend as the 5 control markets.**

DiD does NOT require that the groups start at the same conversion level. It only requires that their *trajectories* would have been the same without treatment. Time-invariant differences between markets are fully absorbed by the market fixed effects.

---

## Diagnostics

### 1. Pre-trends plot (mandatory)

Plot the monthly conversion rates for treated vs. control markets from month 1 through the last pre-treatment month. If parallel trends holds, the two series should track each other closely over the 2-year pre-period. Any systematic divergence before rollout is direct evidence of violation.

For a cleaner view, demean each market around its own mean so you're comparing trend shapes, not levels.

### 2. Event-study specification

Replace the single post-treatment indicator with leads and lags relative to rollout:

```
Y_{mt} = α_m + γ_t + Σ_{k=-K}^{K} β_k · D_{m,t-k} + ε_{mt}
```

- **Pre-treatment coefficients (k < 0):** Should be near zero and statistically insignificant. Non-zero pre-coefficients ("pre-trends") are the formal test of the parallel-trends assumption.
- **Post-treatment coefficients (k ≥ 0):** Show how the effect builds over time. Is the effect immediate? Does it grow? Does it fade? This is substantively informative.

### 3. Placebo tests

Run the same DiD specification on outcomes that the new pricing page should *not* affect — for example, time-on-site for users who never visit the pricing page, or conversion rates on a different product line. If you detect a "treatment effect" there, it likely reflects pre-existing market differences, not a causal effect of the page.

### 4. Covariate balance check

Compare pre-treatment trends in market-level covariates (traffic volume, marketing spend, seasonality patterns) across treated and control markets. Large imbalances don't disqualify DiD, but they raise the prior probability that trends differ too.

---

## Optional Enhancements

### Synthetic control as a robustness check

With 3 treated markets and 5 controls and 2 years of pre-period data, you have enough to construct a synthetic control for each treated market — a weighted combination of untreated markets that matches its pre-treatment conversion trajectory. This can sharpen the counterfactual and provides an additional robustness check that doesn't rely solely on parametric TWFE.

### Covariate-adjusted DiD

If you have market-level covariates (size, region, device mix, marketing spend), you can add them to the TWFE regression. This doesn't change the identification strategy but can improve precision and is especially helpful if you suspect the parallel trends assumption is borderline.

### Heterogeneous treatment effects

If the 3 treated markets differ substantially in characteristics (e.g., one is much larger, one is a different language), consider estimating market-specific effects or interacting D with market-level features. The aggregate ATT may mask meaningful heterogeneity.

---

## Failure Modes to Watch

| Failure mode | What it looks like | Response |
|---|---|---|
| **Parallel trends violation** | Pre-period trends diverge before rollout | Reframe: synthetic control; add market-specific time trends; question identification |
| **Selection into treatment** | The 3 rollout markets were chosen because they were already improving | Pre-trends plot will show this; reframe or use synthetic control |
| **Anticipation effects** | Treated markets started optimizing pricing-related strategy before nominal rollout | Check if conversion movement began before rollout date |
| **Differential shocks** | A market-specific event (competitor exit, local promotion) hits only treated or only control markets during post-period | Investigate any known market events; placebo tests help diagnose |
| **Small cluster count** | 8 markets total means few clusters for clustered SEs | Wild cluster bootstrap for inference; consider permutation inference |
| **Staggered rollout complications** | If the 3 markets got the page at different points in the quarter | Use a staggered DiD estimator (Callaway-Sant'Anna or Sun-Abraham) rather than vanilla TWFE, which can produce biased estimates under heterogeneous timing |

---

## Summary

**Design:** Differences-in-differences (panel DiD)
**Estimator:** Two-way fixed effects OLS with market and time fixed effects; clustered SEs at the market level
**Key assumption:** Parallel trends — treated markets would have trended like control markets absent the new pricing page
**Primary diagnostic:** Pre-trends plot and event-study specification over the 2-year pre-period
**Most likely trap:** Selection bias in which markets were rolled out first; inspect pre-trends before trusting the estimate
