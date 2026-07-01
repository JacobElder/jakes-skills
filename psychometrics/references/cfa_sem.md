# Confirmatory factor analysis & SEM — deep reference

CFA is a special case of SEM with only measurement model (no structural paths between latent variables). SEM adds structural paths. In `lavaan`, use `cfa()` for CFA and `sem()` for full SEM; mechanically similar.

## When CFA over EFA

- You have a **hypothesized structure** (from theory or prior EFA on a different sample).
- You want to test **specific constraints** (loadings equal, residuals correlated, factors orthogonal).
- You're testing **measurement invariance** across groups.
- The structure includes **cross-loadings or correlated residuals** you want explicit.

If you're running CFA on the same sample you used for EFA, results are over-fit; treat them as descriptive, not confirmatory. Split the sample (50/50 random split) or pre-register the model.

## lavaan syntax cheat sheet

```r
model <- '
  # measurement model
  F1 =~ x1 + x2 + x3        # factor =~ indicators
  F2 =~ x4 + x5 + x6

  # structural paths (for SEM)
  F2 ~ F1                    # F2 regressed on F1

  # covariances
  x1 ~~ x2                   # correlated residuals (use sparingly!)
  F1 ~~ F2                   # factor covariance (default in cfa())

  # intercepts (for invariance testing)
  x1 ~ 1
  
  # constraints
  F1 =~ a*x1 + a*x2          # equal loadings (label-equality)
'

fit <- cfa(model, data = d, std.lv = TRUE)   # std.lv: factor variance = 1, frees all loadings
                                              # (alternative: first loading = 1, the default)
summary(fit, fit.measures = TRUE, standardized = TRUE)
```

For ordinal indicators: `cfa(model, data = d, ordered = c("x1","x2",...))` triggers WLSMV automatically. Don't treat 5-point Likert as continuous if you have an estimator that handles ordinal properly.

## Identification

A model is **identified** if every parameter has a unique solution given the data. Necessary conditions:

- **t-rule**: number of free parameters ≤ number of unique elements in covariance matrix, p(p+1)/2.
- **Scale-setting for latent variables**: either fix one loading per factor to 1 (`std.lv = FALSE`, lavaan default) OR fix factor variance to 1 (`std.lv = TRUE`). Latter is often more interpretable.
- **For mean structure / intercepts**: fix one intercept per factor or fix factor mean to 0.

Sufficient conditions for measurement models:
- **Two-indicator rule**: a factor with 2+ indicators is identified if it's correlated with another factor (or has the metric set).
- **Three-indicator rule**: a factor with 3+ indicators is identified standalone.

Empirical underidentification can occur even with formal identification — when loadings are near zero or factor correlations are extreme. Symptom: huge SEs, nonconvergence, negative variances.

## Estimators

Pick based on data:

| Data | Estimator | Notes |
|---|---|---|
| Continuous, multivariate normal | ML | Default; chi-square and SEs trustworthy |
| Continuous, non-normal | **MLR** | Robust SEs, Yuan-Bentler scaled chi-square. Modern default for continuous data when normality is suspect (which is most of the time). |
| Ordinal (≤ 6 categories) | **WLSMV** | Mean- and variance-adjusted weighted least squares with theta parameterization. Standard for ordinal. |
| Categorical with missing | WLSMV with pairwise present, or FIML with `estimator = "MLR"` after treating as continuous (compromise) |
| Bayesian | `blavaan` | Useful for small N, complex models, prior info |

```r
cfa(model, data = d, estimator = "MLR")                          # continuous, non-normal
cfa(model, data = d, ordered = ord_items, estimator = "WLSMV")   # ordinal
```

## Missing data

- **FIML** (full information maximum likelihood) is the default in lavaan for ML estimation: `missing = "fiml"`. Uses all available data, assumes MAR. Best general-purpose option for continuous indicators with missingness.
- WLSMV with `missing = "pairwise"` for ordinal data. (FIML for categorical is computationally hard; multiple imputation is the alternative.)
- **Listwise deletion** is what lavaan does by default for ML if you don't specify. Almost never the right choice; biases estimates and wastes data.

Always check missingness patterns first: `mice::md.pattern()` or `naniar::vis_miss()`.

## Fit indices

A model can fit globally and still misfit locally; conversely it can have bad global fit but the misfit is in a part you don't care about. Look at multiple indices AND residuals AND substantive interpretability.

### Chi-square

Tests exact fit (H₀: model is correct). Almost always rejects with large N because no model is exactly correct. Report it but don't lean on it. Chi-square difference tests for nested models (e.g., invariance levels) are useful, but use **scaled chi-square difference tests** for MLR/WLSMV (`lavaan::lavTestLRT(..., method = "satorra.bentler.2010")`).

### Approximate fit indices

- **CFI (Comparative Fit Index)** — compares model to null (independence) baseline. Range 0–1, higher better. Hu & Bentler suggested > .95.
- **TLI (Tucker-Lewis Index, NNFI)** — similar to CFI but penalizes complexity. Can be > 1 or < 0.
- **RMSEA (Root Mean Square Error of Approximation)** — population-level badness of fit per df. Lower better. Hu & Bentler suggested < .06. Report 90% CI.
- **SRMR (Standardized Root Mean Residual)** — average standardized residual. Lower better. < .08 is the rough guide.

### Hu & Bentler cutoffs — the caveat

Hu & Bentler (1999) ran simulations under specific conditions (continuous normal data, simple structures, moderate N). The cutoffs .95/.06/.08 were specific to those conditions and **not intended as universal benchmarks**. With:

- Ordinal data
- More items per factor (higher complexity)
- Smaller communalities
- Larger N (chi-square sensitivity)

... cutoffs can be too strict or too lax. Marsh, Hau & Wen (2004) made this point forcefully. Modern best practice: report indices, interpret in context, don't reject a model solely for missing .95 by .003.

For WLSMV with ordinal data, RMSEA tends to be over-optimistic in some conditions; weight CFI/TLI and residual inspection.

### Reading residuals

`residuals(fit, type = "standardized")` (continuous) or `lavInspect(fit, "residuals")` shows item-pair residual covariances. Large standardized residuals (|z| > 2 or so) indicate where the model misfits — specific item pairs that covary more or less than the model predicts. Often more informative than global fit.

## Modification indices — the trap

MIs (`modificationindices(fit, sort = TRUE)`) tell you the chi-square decrease if you freed a constrained parameter. Strong temptation: free the biggest ones and refit.

Problems:
- **Capitalization on chance**: post-hoc model improvements don't generalize.
- **Equivalence**: many MI-suggested modifications are statistically equivalent to alternatives the data can't distinguish.
- **The chase**: free one, the next-largest changes; iterative chasing produces a complicated model that fits this sample's noise.

If you do use MIs:
- **Only with a substantive rationale** — "these two items have nearly identical wording so a correlated residual is theoretically warranted" beats "the MI was big."
- **Cross-validate** on a holdout sample.
- **Report all changes made** and the path from initial to final model.
- Treat the final model as exploratory/respecification, not confirmatory.

## Correlated residuals

Common reasons they're substantively justified:

- Items with nearly identical wording (method effect).
- Items administered adjacently in time (carry-over).
- Reverse-worded items often correlate as a group (acquiescence/wording effect).
- For longitudinal CFA: same indicator at adjacent time points often needs a correlated residual.

Reasons they're not justified: "fits better." Decide a priori where you'd expect correlated residuals and include them in the original model.

## Reporting a CFA

- Model specification (path diagram or syntax).
- Sample size, missing data handling, estimator.
- Fit indices: chi-square (df, p), CFI, TLI, RMSEA (with 90% CI), SRMR.
- Standardized loadings (all, in a table or figure).
- Factor correlations.
- Any post-hoc modifications and rationale.
- Reliability (omega from the fitted model — `semTools::compRelSEM()`).
- Configuration of nested model comparisons if testing alternatives.

## Common SEM additions

Once you have a measurement model that works, you can:

- **Add structural paths**: `F2 ~ F1` regresses F2 on F1. Path coefficient is standardized regression weight when standardized output requested.
- **Mediation**: `F3 ~ a*F1; F2 ~ b*F3 + c*F1; ab := a*b; total := ab + c`. Use `:=` to define computed parameters; lavaan returns SEs for them via the delta method (or use `bootstrap = 1000`).
- **Latent interactions**: products of latent variables; use `modsem` package or `lavaan` with double-mean-centering (Lin et al., 2010).
- **Latent growth curves**: factors representing intercept and slope of repeated measures. See Bollen & Curran (2006).
- **Multi-group SEM**: `group = "sex"` argument; combine with invariance testing.

## Common pitfalls

- **Treating ordinal Likert as continuous without considering WLSMV** — defaults to ML which is fine if many categories (≥ 6) and roughly normal, problematic for fewer.
- **Ignoring negative variances (Heywood cases)** — indicates misspecification or estimation problems; don't constrain to zero and move on.
- **Reporting only standardized output** — unstandardized estimates are needed for cross-sample, cross-group, or substantive interpretation.
- **Comparing non-nested models with chi-square difference** — use AIC, BIC, or Vuong's test.
- **Assuming CFA "validates" the structure** — CFA can fit because items share method variance or share a non-content commonality. Internal structure is one source of validity evidence among several.
