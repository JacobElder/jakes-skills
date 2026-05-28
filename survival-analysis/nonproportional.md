# Non-proportional hazards: weighted log-rank, MaxCombo, RMST

The standard log-rank test and Cox PH model both assume the hazard ratio is constant over time. When that fails — and it often does — you have two problems:

1. **Hypothesis testing**: standard log-rank loses power against specific alternatives (early differences, late differences, crossing curves).
2. **Effect estimation**: a Cox HR is hard to interpret as a single summary when the true HR is changing over time.

This file covers both: the weighted log-rank family for testing, and RMST for effect estimation under non-PH.

## The weighted log-rank family

All log-rank-like tests are weighted sums of "observed minus expected" at each event time. They differ only in the weight $w(t_j)$ applied at each event time $t_j$:

$Z = \sum_j w(t_j) (O_j - E_j) / \text{se}$

- **Standard log-rank** (Mantel-Haenszel): $w(t) = 1$ at every event time. Optimal under PH.
- **Gehan-Breslow (Wilcoxon)**: $w(t_j) = n_j$ (number at risk). Weights early events more (when more subjects are at risk). Good if you expect treatment effect to vanish over time.
- **Tarone-Ware**: $w(t_j) = \sqrt{n_j}$. Compromise between log-rank and Gehan.
- **Peto-Peto**: $w(t_j) = \hat S(t_j)$, where $\hat S$ is a modified KM survival estimate. Less sensitive to censoring patterns than Gehan.
- **Peto-Prentice**: similar to Peto-Peto but with slightly different KM modification. Often grouped together.
- **Fleming-Harrington G(ρ, γ)**: $w(t_j) = \hat S(t_j)^\rho (1 - \hat S(t_j))^\gamma$. A whole family parameterized by two numbers:
  - G(0, 0) = standard log-rank.
  - G(1, 0) = Peto-Peto (emphasizes early).
  - G(0, 1) = emphasizes late differences (delayed treatment effects).
  - G(1, 1) = emphasizes middle differences (peak around median survival).

### Pick the weight based on the alternative you expect

| Expected pattern | Best-powered test |
|---|---|
| Proportional hazards | Standard log-rank |
| Early difference that vanishes (e.g., surgical mortality) | Gehan-Breslow, Tarone-Ware, FH(1,0) / Peto-Peto |
| Delayed difference (e.g., immunotherapy takes time to work) | FH(0, 1) |
| Hump in middle | FH(1, 1) |
| Any of the above, don't know which | **MaxCombo** |
| Crossing curves | **MaxCombo** with FH(0,0) + FH(0,1) + FH(1,0) + FH(1,1) |

**Standard log-rank can fail to detect crossing curves entirely** — early and late differences cancel, giving a non-significant test even when the two populations are obviously different. This is one of the most important reasons to know about the weighted family.

### R
```r
library(survival)

# Standard log-rank (rho = 0)
survdiff(Surv(time, status) ~ group, data = df, rho = 0)

# Peto-Peto (rho = 1) — emphasizes early differences
survdiff(Surv(time, status) ~ group, data = df, rho = 1)

# survdiff only supports rho parameter (FH with gamma = 0). For full FH:
library(FHtest)
FHtestrcc(Surv(time, status) ~ group, data = df, rho = 0, lambda = 1)  # FH(0,1)
FHtestrcc(Surv(time, status) ~ group, data = df, rho = 1, lambda = 1)  # FH(1,1)

# Alternative: nph package, comprehensive
library(nph)
logrank.test(time = df$time, event = df$status, group = df$group,
             rho = c(0, 0, 1, 1), gamma = c(0, 1, 0, 1))  # multiple tests at once

# Or use the survRM2 / nphRCT packages
```

### Python

The weighted log-rank family is less mature in Python.

```python
from lifelines.statistics import logrank_test

# Standard log-rank
result = logrank_test(df_a['time'], df_b['time'],
                      event_observed_A=df_a['event'], event_observed_B=df_b['event'])
print(result.p_value, result.test_statistic)

# Weighted log-rank with FH weights:
result = logrank_test(df_a['time'], df_b['time'],
                      event_observed_A=df_a['event'], event_observed_B=df_b['event'],
                      weightings="fleming-harrington", p=0, q=1)  # FH(0,1) - late differences
# Other weightings: "wilcoxon" (Gehan), "tarone-ware", "peto", "fleming-harrington"
```

scikit-survival has `compare_survival` but only the standard log-rank.

## MaxCombo

The **MaxCombo** test combines several Fleming-Harrington tests and reports the maximum (most significant). The reference distribution accounts for the multiple testing via a multivariate normal correction. This gives you a single p-value with power against PH, early differences, late differences, and crossings — at a small efficiency cost when PH actually holds.

MaxCombo with the four-test set {G(0,0), G(0,1), G(1,0), G(1,1)} is the increasingly standard choice for trials where the form of the alternative is uncertain — for example, immuno-oncology trials with potential delayed effects, or any phase-3 trial where regulators want a "show me the difference however it manifests" test.

### R
```r
library(nph)
mc <- logrank.maxtest(time = df$time, event = df$status, group = df$group,
                      rho   = c(0, 0, 1, 1),
                      gamma = c(0, 1, 0, 1))
print(mc)
# Returns a single MaxCombo p-value plus the individual FH p-values.

# Alternative: nphRCT package
library(nphRCT)
maxcombo(Surv(time, status) ~ group, data = df)
```

### Python

No first-class MaxCombo implementation. Best options:
- Run multiple `logrank_test` with different FH weights and combine manually with the multivariate-normal correction (some applied papers walk through the math).
- Call R via `rpy2`.
- Pre-register the most plausible FH alternative based on expected effect shape and use just that one (no multiple-testing penalty needed if pre-specified).

## RMST — restricted mean survival time

RMST is **the recommended summary measure when PH fails**, and it's increasingly recommended as a primary or co-primary endpoint even when PH holds. It has a clean interpretation any audience can understand.

### Definition

RMST up to time $\tau$ is the area under the survival curve from 0 to $\tau$:

$\text{RMST}(\tau) = \int_0^\tau S(t) \, dt$

In words: "the average event-free time over the next $\tau$ units of time." If $\tau$ = 5 years and RMST = 3.7 years, the average subject is event-free for 3.7 of the next 5 years.

### Why it's good

- **Always defined**, even when the median survival isn't reached.
- **Interpretation matches intuition** — "average extra survival time" not "instantaneous risk ratio."
- **Doesn't require PH**. Valid under any hazard pattern.
- **Has a meaningful unit** (time), so differences are interpretable directly. RMST difference of 3 months = "treatment adds 3 months of average event-free time over the chosen horizon."
- **Robust to late tail estimates** because you choose $\tau$ at or before the end of reliable follow-up.

### Why it's not perfect

- **Sensitive to choice of $\tau$**. Pre-specify $\tau$ based on clinical relevance (and the end of well-supported follow-up — typically the smaller of the maximum follow-up in each group). Don't shop for the $\tau$ that maximizes effect.
- **Loses some power vs Cox under PH**. Cost is small if you have enough events.

### R — survRM2

```r
library(survRM2)

# Set tau just inside the smaller of the maximum observed times per group
out <- rmst2(time = df$time, status = df$status, arm = df$group, tau = 365)
print(out)
# Reports: RMST per group, RMST difference, RMST ratio, with 95% CIs and p-values.

# Adjusted RMST (with covariates)
out_adj <- rmst2(time = df$time, status = df$status, arm = df$group,
                 tau = 365, covariates = df[, c("age", "sex")])
```

### R — direct from survfit

```r
fit <- survfit(Surv(time, status) ~ group, data = df)
print(fit, rmean = 365)  # restricted mean (over 0 to 365) for each group
# Or
summary(fit, rmean = 365)
```

### Python (lifelines)

```python
from lifelines.utils import restricted_mean_survival_time
from lifelines import KaplanMeierFitter

kmf = KaplanMeierFitter().fit(df['time'], df['event'])
rmst = restricted_mean_survival_time(kmf, t=365)
# Group comparison requires fitting two KMs and computing the difference + CI manually,
# or using the survRM2 R package via rpy2 for proper CIs.
```

The R implementation is much more complete. For applied work involving RMST, R is the cleaner path.

### How to pick τ

- **Pre-specified clinical horizon**: "5-year RMST" is a defensible choice for many oncology contexts.
- **Operational horizon**: a year, a quarter, the contract length.
- **End of well-supported follow-up**: $\tau$ should be at or just before the time when both arms still have substantial subjects at risk (e.g., where the smaller arm still has ~15% at risk).

Never pick $\tau$ after looking at the curves to maximize the effect. Pre-specify, ideally in the protocol or analysis plan.

## When PH fails: a workflow

1. **Confirm non-PH** via `cox.zph` and visual inspection of scaled Schoenfeld residuals and stratified KM curves.
2. **Identify the pattern**: do curves cross? Does treatment effect appear early then fade, or kick in late? Plot $\log[-\log S(t)]$ vs $\log t$ — parallel lines mean PH; non-parallel patterns hint at the form of the violation.
3. **For hypothesis testing**: use MaxCombo if the alternative shape is uncertain, or the specific FH(ρ, γ) matching your expected pattern.
4. **For effect estimation**:
   - **RMST difference at clinically meaningful τ** — usually the best choice.
   - **Time-varying coefficient Cox model** — if you want to characterize how the HR changes.
   - **Stratified Cox** — if the offending variable isn't of substantive interest.
   - **Royston-Parmar with time-dependent effects** — if you want a smooth parametric description of how effects change.
   - **Reporting HRs at specific time intervals** (from `survSplit`) — can be communicated as "HR was 1.8 in the first 6 months and 0.9 after."

Don't ignore PH violations and report a single HR anyway. Even if the test isn't significant, if the residuals show a clear pattern, the single-number HR misrepresents what's happening.

## Crossing curves specifically

When KM curves cross, the standard log-rank can have near-zero power even with very different survival distributions, because positive and negative contributions cancel. Always plot the curves before relying on log-rank. If they cross:

- Use MaxCombo (will detect the difference).
- Report RMST difference (will likely be near zero if the crossing is symmetric — which is fine, that's the truth: average survival over τ is similar even though the trajectories differ).
- Consider whether a single comparison makes sense. Sometimes the right answer is: "treatment helps early subjects but harms late ones" — report stratified results, not a single combined test.
