# Workplace Burnout Scale: Psychometric Analysis

Great — you have everything you need to run these analyses. Here's a complete walkthrough covering Cronbach's alpha, CFA, and measurement invariance testing. I'll use R with the `psych` and `lavaan` packages, which are the standard tools for this kind of work.

---

## Setup and Data Preparation

```r
library(psych)
library(lavaan)
library(semTools)  # for measurementInvariance()
library(dplyr)

# Assume your data is in a data frame called `burnout_data`
# with 20 item columns (item1–item20) and a grouping variable `office`
# office = "LocationA" or "LocationB"

# Separate subscale item sets — adjust these to match your actual structure
# Example: 3 subscales with 7, 7, and 6 items
subscale1_items <- paste0("item", 1:7)    # e.g., Exhaustion
subscale2_items <- paste0("item", 8:14)   # e.g., Cynicism/Depersonalization
subscale3_items <- paste0("item", 15:20)  # e.g., Inefficacy/Reduced accomplishment
```

---

## Step 1: Cronbach's Alpha for Each Subscale

```r
alpha_sub1 <- alpha(burnout_data[, subscale1_items])
alpha_sub2 <- alpha(burnout_data[, subscale2_items])
alpha_sub3 <- alpha(burnout_data[, subscale3_items])

cat("Subscale 1 alpha:", round(alpha_sub1$total$raw_alpha, 3), "\n")
cat("Subscale 2 alpha:", round(alpha_sub2$total$raw_alpha, 3), "\n")
cat("Subscale 3 alpha:", round(alpha_sub3$total$raw_alpha, 3), "\n")
```

**What to look for:**
- Alpha ≥ 0.70 is typically acceptable for research scales.
- Alpha ≥ 0.80 is preferred for applied/clinical use.
- Check `alpha_sub1$item.stats` for item-total correlations — any item with r < 0.30 is worth examining.
- Also inspect `alpha_sub1$alpha.drop` to see whether removing any item would substantially raise alpha.

**Important caveat:** Alpha is sensitive to scale length. With 5-point Likert items and decent inter-item correlations, 6–7 items per subscale should yield alpha ≥ 0.80 if the items are well-written. If you get alpha in the 0.60s, check for reverse-scored items you may have forgotten to flip.

---

## Step 2: Confirmatory Factor Analysis

### Define the Three-Factor Model

```r
burnout_model <- '
  Exhaustion     =~ item1 + item2 + item3 + item4 + item5 + item6 + item7
  Cynicism       =~ item8 + item9 + item10 + item11 + item12 + item13 + item14
  Inefficacy     =~ item15 + item16 + item17 + item18 + item19 + item20
'
```

### Fit the Model

```r
cfa_fit <- cfa(
  burnout_model,
  data      = burnout_data,
  estimator = "MLR",       # robust ML — handles mild non-normality in Likert data
  std.lv    = TRUE         # standardize latent variances for cleaner output
)

summary(cfa_fit, fit.measures = TRUE, standardized = TRUE)
```

### Key Fit Indices to Evaluate

| Index | Acceptable | Good |
|---|---|---|
| CFI | > 0.90 | > 0.95 |
| TLI | > 0.90 | > 0.95 |
| RMSEA | < 0.08 | < 0.06 |
| SRMR | < 0.10 | < 0.08 |

```r
fitMeasures(cfa_fit, c("cfi", "tli", "rmsea", "rmsea.ci.lower",
                        "rmsea.ci.upper", "srmr", "aic", "bic"))
```

**If fit is poor:**
- Inspect modification indices: `modindices(cfa_fit, sort. = TRUE, maximum.number = 10)`
- Common culprits: items that cross-load, or item pairs with correlated residuals (especially adjacent items on the survey).
- Only free parameters suggested by theory or face content — don't chase every MI blindly.

**Standardized loadings** (from `summary(..., standardized = TRUE)`, look at the `Std.all` column) should generally be ≥ 0.40, ideally ≥ 0.60. Loadings below 0.40 suggest an item isn't measuring its intended factor well.

---

## Step 3: Measurement Invariance Between Office Locations

This tests whether the scale "means the same thing" to employees at both locations. The standard sequence moves from least to most constrained:

1. **Configural invariance** — same factor structure, all parameters free
2. **Metric invariance** — factor loadings constrained equal across groups
3. **Scalar invariance** — loadings + item intercepts constrained equal (required for comparing latent means)

### Run the Invariance Sequence

```r
invariance_results <- measurementInvariance(
  model  = burnout_model,
  data   = burnout_data,
  group  = "office",
  estimator = "MLR"
)
```

This runs all four models automatically and prints a comparison table.

### Alternatively, Fit Each Level Manually

```r
# Configural (baseline)
fit_configural <- cfa(burnout_model, data = burnout_data,
                      group = "office", estimator = "MLR")

# Metric (equal loadings)
fit_metric <- cfa(burnout_model, data = burnout_data,
                  group = "office", group.equal = "loadings",
                  estimator = "MLR")

# Scalar (equal loadings + intercepts)
fit_scalar <- cfa(burnout_model, data = burnout_data,
                  group = "office",
                  group.equal = c("loadings", "intercepts"),
                  estimator = "MLR")

# Strict (equal residual variances — usually not required)
fit_strict <- cfa(burnout_model, data = burnout_data,
                  group = "office",
                  group.equal = c("loadings", "intercepts", "residuals"),
                  estimator = "MLR")

# Compare models
compareFit(fit_configural, fit_metric, fit_scalar, fit_strict)
```

### How to Interpret the Results

Because you're using MLR, compare models using the **Satorra-Bentler scaled chi-square difference test** (not the naive Δχ²). `semTools` handles this automatically.

The practical criteria most researchers use:

| Comparison | Decision rule |
|---|---|
| Configural → Metric | ΔCFI ≤ −0.010, ΔRMSEA ≤ 0.015 → metric holds |
| Metric → Scalar | Same thresholds |
| If scalar fails | Test **partial scalar** invariance (free 1–2 intercepts) |

```r
# If scalar fails, identify non-invariant intercepts
lavTestScore(fit_scalar)  # shows which constraints are responsible
```

**Partial scalar invariance** (≥ 2 intercepts invariant per factor) still allows meaningful, if qualified, group comparisons.

---

## Step 4: Reporting Your Results

A typical write-up might read:

> "Internal consistency was high for all three subscales (Exhaustion: α = .XX; Cynicism: α = .XX; Inefficacy: α = .XX). CFA of the three-factor structure fit the data well (CFI = .XX, TLI = .XX, RMSEA = .XX [90% CI: .XX–.XX], SRMR = .XX). All factor loadings were statistically significant and exceeded .50 in standardized form. Measurement invariance testing indicated [configural / metric / scalar] invariance across the two office locations (ΔCFI = .XXX, ΔRMSEA = .XXX), supporting [valid / qualified] comparison of subscale scores between sites."

---

## A Few Practical Notes

**Sample size:** 1,100 respondents is excellent for CFA. You have enough power to detect even small model misfit, so don't panic if CFI is 0.94 rather than 0.96 — look at the substantive size of modification indices, not just significance.

**Likert-scale estimator:** Some researchers prefer WLSMV (weighted least squares mean and variance adjusted) for ordered categorical data. With 5-point items and n = 1,100, MLR typically performs well, but if you have strong floor/ceiling effects or markedly skewed items, switch to WLSMV:

```r
cfa_fit_wlsmv <- cfa(burnout_model, data = burnout_data,
                     estimator = "WLSMV", ordered = TRUE)
```

Note: if you use WLSMV, the invariance testing syntax changes slightly — use `group.equal = c("thresholds", "loadings")` for metric invariance rather than `"intercepts"`.

**Between-group sample sizes:** Make sure both office locations have sufficient n (≥ 200 each) for stable parameter estimates in the multi-group models. If one location is much smaller, the standard errors will be asymmetric.

Let me know if you'd like help interpreting output once you've run these, or if you need to adapt the model syntax to your actual subscale structure.
