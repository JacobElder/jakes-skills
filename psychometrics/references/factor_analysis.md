# Factor analysis (EFA) — deep reference

EFA is for **discovering** latent structure when you don't have strong priors. CFA is for **testing** a hypothesized structure (see `cfa_sem.md`). Don't blur them. Running EFA, then running CFA on the same data and presenting both is double-dipping unless you split the sample.

## The model

Common factor model (orthogonal case):

xᵢ = Σⱼ λᵢⱼ · ξⱼ + δᵢ

where xᵢ is observed item i, ξⱼ are latent common factors, λᵢⱼ are factor loadings, and δᵢ is the unique factor (specific variance + measurement error).

Item variance decomposes into:

σᵢ² = h²ᵢ + uᵢ²

- **Communality (h²ᵢ)**: variance of item i explained by common factors. h²ᵢ = Σⱼ λ²ᵢⱼ (orthogonal case).
- **Uniqueness (uᵢ²)**: variance not explained by common factors.

This is the key distinction from PCA: PCA models *total* variance (no separation of h² and u²); FA models *common* variance only.

## PCA vs FA

- **PCA**: components are weighted sums of observed variables. Total variance modeled. Components are determinate (compute directly from data). Use for: dimension reduction, summarizing.
- **FA**: factors are *causes* of items. Common variance modeled. Factors are indeterminate (estimated). Use for: measuring latent constructs.

The distinction matters substantively: if you want to claim your factor *is* the construct of interest, the factor model commits you to a latent-variable interpretation. PCA does not.

Operationally, with many items and high communalities, PCA and FA give similar loading patterns. With few items or low communalities, they diverge — FA loadings are typically smaller in magnitude.

## Extraction methods

- **Principal axis factoring (PAF)**: iterates to estimate communalities. Robust, doesn't require multivariate normality. Default in many older treatments.
- **Maximum likelihood (ML)**: requires multivariate normality (or large N for asymptotic robustness). Provides chi-square test of fit, allows model comparison, gives standard errors.
- **Minimum residual (`minres` in `psych`)**: minimizes the off-diagonal residuals. Default in `psych::fa()` and often the safest general-purpose choice. Doesn't require normality, doesn't choke on Heywood cases as often as ML.
- **Weighted least squares (WLS), generalized least squares (GLS)**: various weighting schemes for the residual matrix.

Default in `psych::fa()` is `fm = "minres"`. Switch to `fm = "ml"` if you want chi-square fit and standard errors.

## How many factors?

The single most consequential decision in EFA. Methods, roughly in order of trustworthiness:

1. **Parallel analysis (Horn, 1965)** — gold standard. Compare observed eigenvalues to eigenvalues from random data of the same dimensions. Retain factors whose observed eigenvalue exceeds the random eigenvalue (or the 95th percentile of random eigenvalues). `psych::fa.parallel(data, fa = "fa")`.
2. **Velicer's MAP (Minimum Average Partial)** — finds the number of factors that minimizes the average squared partial correlation. `psych::nfactors(data)` reports this and several others.
3. **Scree plot** — visual inspection for the "elbow." Subjective; works best with strong factors. Use alongside parallel analysis, not instead.
4. **Kaiser's eigenvalue > 1 rule** — *overestimates* the number of factors, often badly. Don't use as primary criterion. It's defensible only as a soft upper bound.
5. **Theoretical and interpretability considerations** — if you can name the factor and it has substantively meaningful items loading on it, that's strong evidence. If a "factor" has 2 items both about the same narrow content, it may be a methods artifact (similar wording) rather than a substantive factor.

Don't pick one number mechanically. Fit models with k−1, k, k+1 factors and compare loading patterns, communalities, and interpretability.

## Rotation

After extraction, factors are rotated to maximize interpretability. Two families:

### Orthogonal (factors uncorrelated)

- **Varimax** — maximizes variance of squared loadings within each factor. Pushes loadings toward 0 or 1.
- **Quartimax** — pushes loadings toward 0 or 1 within each *item*.

Imposes uncorrelated factors as a structural assumption. Almost never substantively correct for psychological constructs.

### Oblique (factors allowed to correlate)

- **Promax** — starts with varimax, then relaxes. Fast, well-behaved.
- **Oblimin** (direct oblimin, gamma = 0) — minimizes loading cross-products.
- **Geomin** — used in CFA-style models and Mplus EFA; works well for moderately complex structures.

**Default to oblique.** Constructs are correlated; orthogonal rotation either imposes an unrealistic constraint or — if factors are actually orthogonal — gives the same answer as oblique. Oblique is strictly more general. Report the factor correlation matrix; if all interfactor correlations are near zero, your factors are de facto orthogonal anyway.

In oblique rotation, distinguish:

- **Pattern matrix**: standardized regression coefficients of items on factors. Use for *interpretation* of which factor "owns" which item.
- **Structure matrix**: simple correlations of items with factors. Always larger in magnitude when factors are correlated.

`psych::fa(...)` reports both; use the pattern matrix for naming factors.

## Polychoric correlations for Likert items

Pearson correlations on Likert items (≤ ~5 categories, especially with skewed distributions) underestimate the true correlation between the underlying continuous traits. This biases loadings downward and inflates factor count (an artifactual "difficulty factor" can appear, where items separate by their endorsement frequency rather than content).

Use polychoric correlations: model item responses as discretizations of underlying continuous bivariate normal variables; estimate the correlation between those latent variables.

```r
# psych
fa(data, nfactors = 3, fm = "minres", rotate = "oblimin", cor = "poly")

# or compute the matrix first
pc <- psych::polychoric(data)$rho
fa(pc, nfactors = 3, n.obs = nrow(data), fm = "minres", rotate = "oblimin")
```

When in doubt with ordinal data: use polychoric. The downside is computational cost and occasional numerical issues with sparse cells.

## Sample size

The old "N ≥ 200" or "N ≥ 5 per item" rules are too crude. MacCallum, Widaman, Zhang & Hong (1999) showed that what matters is:

- **Communality magnitude**: with high communalities (h² > .6 on average), N = 100 can give stable solutions.
- **Overdetermination**: ≥ 4 items per factor improves stability.
- **Number of factors**: more factors require larger N.

With low communalities (h² ≈ .3) and few items per factor, even N = 500 may give unstable rotations. Run bootstrap or split-half stability checks for borderline cases. See `psych::fa.bootstrap()`.

## Factor scores

Three main estimation methods:

- **Regression scores** (Thurstone, ML): predict factor scores from regression of factors on items. Most common. Slightly biased toward the mean.
- **Bartlett scores**: unbiased ML estimate. Variance of estimates equals factor variance.
- **Anderson-Rubin**: orthogonal scores even from oblique factors. Useful when you need uncorrelated regressors downstream.

**Factor score indeterminacy** is a real conceptual issue: for a given factor model and observed data, there are infinitely many sets of factor scores consistent with the model. The estimated scores are *one* of these. This indeterminacy is small when factor loadings are strong; large when they're weak. Grice (2001) is the modern reference.

Practical upshot: if you want a "score" for use in downstream regression, sum scores (with reverse-coding) are often nearly as good as factor scores and much simpler. Use factor scores when (1) items are very unequal in loading and you want a more efficient composite, or (2) you're using SEM and need the latent variable directly.

## Heywood cases

Communality estimates > 1 (impossible — variance can't exceed 1) or negative residual variances. Signals:

- Sample size too small relative to factor complexity.
- Misspecification (wrong number of factors).
- Empirical underidentification (some items don't have enough variance separable from one factor).

Don't just constrain to 1 and proceed. Investigate.

## Bifactor and hierarchical models

For scales with a general factor plus group factors (e.g., depression with general factor + somatic, cognitive, affective group factors):

- **Bifactor model**: each item loads on the general factor *and* one group factor; group factors are orthogonal to general and to each other.
- **Hierarchical (second-order) model**: items load on group factors; group factors load on a second-order general factor.

Bifactor is mathematically more general (a hierarchical model is a constrained bifactor). Use bifactor when group factors are theoretically meaningful as separable from the general factor. Use hierarchical when the general factor is conceptualized as a cause of the group factors.

For both, report `omega_h` (hierarchical) to know how much variance the general factor actually explains — bifactor models often have a strong general factor but group factors that add little after accounting for it (or vice versa).

`psych::omega()` fits a Schmid-Leiman transformation of an oblique EFA, giving an approximate bifactor solution and omega coefficients.

## Reporting an EFA — minimum

- Sample size, missing data handling.
- Suitability checks: Kaiser-Meyer-Olkin (KMO) ≥ .6 (preferably ≥ .8), Bartlett's test of sphericity significant.
- Correlation type used (Pearson, polychoric).
- Extraction method.
- Number of factors and how determined (parallel analysis, MAP, scree, theory).
- Rotation method.
- Pattern matrix with all loadings (don't suppress small ones in the table; suppression is fine in narrative discussion).
- Factor correlations (for oblique rotation).
- Communalities.
- Variance explained per factor and cumulatively.

## Common mistakes

- **Reporting PCA results and calling them EFA** — very common in applied papers.
- **Varimax by default** — usually wrong substantively.
- **Eigenvalue > 1 to pick factor count** — overextracts.
- **Pearson on Likert without checking** — biases loadings down, can spawn artifactual difficulty factors.
- **Dropping items with low loadings without inspecting cross-loadings or communalities** — purely statistical pruning produces over-fit short scales.
- **Reporting EFA "fit" indices from ML extraction as if they were CFA fit indices** — they exist, but EFA isn't a constrained model; chi-square and RMSEA from EFA test very weak models.
- **Treating factor labels as if they validate the factor** — a factor is whatever the loaded items have in common, which may not be what you named it. Validate labels through external relations.
