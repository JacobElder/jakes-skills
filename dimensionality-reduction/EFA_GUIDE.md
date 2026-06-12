# EFA with Parallel Analysis: Complete Guide

## Quick Start

```python
from efa_with_parallel_analysis import fit_efa, summary_efa

# Load your survey data (pandas DataFrame)
df = pd.read_csv('survey.csv')

# Fit EFA with parallel analysis (auto-determine n_factors)
fa, diagnostics = fit_efa(
    df,
    method="ml",           # "ml" or "pa" (principal-axis)
    rotation="oblimin",    # "oblimin" (default) or "varimax"
)

# Print formatted summary with interpretation
summary = summary_efa(fa, df, verbose=True)
```

---

## The Three Critical Choices

### 1. **How many factors?** → Use parallel analysis

**Parallel analysis** compares your data's eigenvalues to those from random noise.
- Keep factors where observed eigenvalue > 95th percentile of random eigenvalues
- More defensible than Kaiser (eigenvalue > 1) or the scree elbow
- Implementation: `fit_efa()` with `n_factors=None` and `parallel_analysis=True`

**Alternative (less rigorous):**
- Scree plot: look for the "elbow" where variance drops
- Theory: specify from prior research or hypotheses
- Kaiser rule (eigenvalue > 1): outdated, tends to over-extract

### 2. **Extraction method?** → Use ML or PA

**Maximum Likelihood (ML)**
- Assumes data ~normally distributed
- Produces likelihood-ratio fit statistics (χ², CFI, RMSEA)
- Better if you want hypothesis tests
- Implementation: `method="ml"`

**Principal-Axis Factoring (PA)**
- More robust to non-normality
- No distributional assumptions
- Slower to compute
- Implementation: `method="pa"`

**Default recommendation:** ML for most social science work (surveys, psychology)

### 3. **Rotation type?** → Use oblique by default

#### **Oblique (oblimin, promax)** ← USE BY DEFAULT

**Assumption:** Factors MAY correlate (realistic for psychology/business/education)

**What you get:**
- Factor loadings λ (item × factor matrix)
- Factor correlation matrix φ (shows which factors covary)

**Why oblique:**
- Depression and anxiety correlate; intelligence and motivation correlate
- Simple structure usually emerges (items load strongly on one factor)
- Cleaner interpretation
- You learn whether factors are related (φ > |0.5| suggests shared construct)

**Implementation:**
```python
fa, diag = fit_efa(df, rotation='oblimin')
# Inspect diag → summary correlations in φ matrix
```

#### **Orthogonal (varimax, equamax)** ← Special case only

**Assumption:** Factors are completely independent (often unrealistic)

**When to use:**
- Theory explicitly requires independent factors
- Downstream machine learning wants uncorrelated features
- Historical/conventional expectation in your field

**Drawbacks:**
- Forces zero correlations (often false)
- Messier loadings (items spread across factors)
- Loses information about factor relationships

**Implementation:**
```python
fa, diag = fit_efa(df, rotation='varimax')
# φ matrix is identity; factor correlations reported as r = 0
```

---

## Interpretation Checklist

### Step 1: Factorability
Before fitting, check:

```
✓ KMO (Kaiser-Meyer-Olkin) ≥ 0.60
  • < 0.5: data not suitable for FA
  • 0.6–0.7: adequate
  • > 0.8: excellent

✓ Bartlett's Test p < 0.05
  • Tests if correlation matrix ≠ identity
  • Want significant (correlations present)
```

### Step 2: Number of Factors
From parallel analysis output:

```
Num  Observed  Random (95%)  Keep?
─────────────────────────────────
 1    4.532      1.823      ✓  (observed > random)
 2    2.187      1.654      ✓
 3    1.456      1.521      ✓
 4    0.932      1.398         (observed < random → stop)
```

→ Retain 3 factors

### Step 3: Factor Loadings
Interpret λ (factor loadings):

```
Item_1: Factor_1 = 0.85, Factor_2 = 0.12, Factor_3 = -0.08
                    ↑ primary         ↑ negligible
```

**Thresholds (field-dependent):**
- |λ| ≥ 0.40: substantive loading (primary interpretation)
- 0.30 ≤ |λ| < 0.40: weak-moderate (secondary)
- |λ| < 0.30: negligible (ignore)

### Step 4: Communalities (h²)
Variance in each item explained by the factors:

```
Item_1: h² = 0.73  ✓ Good (73% of variance explained)
Item_6: h² = 0.18  ⚠ Low (only 18%; item may measure unique variance)
Item_8: h² = 0.99  ⚠ Heywood (impossible; model misfit)
```

**Red flags:**
- h² < 0.30: Item doesn't belong (remove or revise)
- h² > 0.98: Heywood case (misspecification, consider fewer factors)

### Step 5: Cross-loadings
Items loading on multiple factors:

```
Item_4: Factor_1 = 0.42, Factor_2 = 0.38  ⚠ Ambiguous
        Both above 0.30 threshold; factor assignment unclear
```

**Solutions:**
- Revise item wording to be more specific
- Remove item if redundant
- Accept if theoretically justified (method variance)

### Step 6: Factor Correlations (if oblique)
The φ (phi) matrix shows inter-factor relationships:

```
        Factor_1  Factor_2  Factor_3
Factor_1    1.00      0.32      0.15
Factor_2    0.32      1.00      0.05
Factor_3    0.15      0.05      1.00
```

**Interpretation:**
- r ≈ 0.00–0.30: factors are independent
- r ≈ 0.30–0.50: moderate relationship (typical)
- r ≥ 0.70: factors may be measuring the same thing
  → Consider whether to merge or reconsider model

---

## Common Mistakes

### ❌ Using PCA instead of EFA
**Wrong:** "I'll use PCA to find the latent factors"
- PCA has no latent factors; it's a linear combination of observed variables
- EFA models latent constructs that cause the observed correlations
- Results differ! (different loadings, different number of dimensions)

**Right:** "I'll use EFA to find latent constructs behind these items"

---

### ❌ Using orthogonal (varimax) by default
**Wrong:** "I'll use varimax because it's simpler"
- Violates reality (most constructs correlate)
- Produces messier results (less simple structure)
- Hides important information (factor relationships)

**Right:** "I'll use oblique (oblimin) unless theory says factors must be independent"

---

### ❌ Determining factors by "appearance"
**Wrong:** "The scree plot flattens after 4 factors"
- Visual judgment is unreliable
- Different people see different elbows
- Prone to confirmation bias

**Right:** "Parallel analysis suggests 4 factors; scree flattens there too"
- Use multiple criteria (PA, scree, theory, interpretability)
- Consensus > any single criterion

---

### ❌ Ignoring communalities and cross-loadings
**Wrong:** "The loadings look good, so the model is fine"
- Missed low-h² items (aren't being explained)
- Missed cross-loaders (ambiguous items)
- Missed Heywood cases (model misfit)

**Right:** "I reviewed communalities, cross-loadings, and checked for issues before accepting the model"

---

### ❌ Running EFA and CFA on the same sample
**Wrong:** "I'll run EFA to find structure, then CFA to confirm on the same data"
- Circular (confirming a structure you built from that data)
- Inflates apparent fit

**Right:** "I'll run EFA on Sample A, then CFA on Sample B"
- Or use cross-validation within the sample
- Or use SEM's model comparison

---

## Output Interpretation Example

```
================================================================================
EXPLORATORY FACTOR ANALYSIS SUMMARY
================================================================================

FACTOR LOADINGS (λ)
────────────────────────────────────────────────────────────────────────────────
        Factor_1  Factor_2  Factor_3
Item_1     0.878     0.026     0.005      ← Item_1 loads on Factor_1
Item_2     0.887    -0.056     0.000      ← Item_2 loads on Factor_1
Item_3     0.764     0.052    -0.001      ← Item_3 loads on Factor_1
Item_4    -0.005     0.825     0.062      ← Item_4 loads on Factor_2
Item_5     0.038     0.831    -0.050
Item_6    -0.030     0.840    -0.010
Item_7    -0.028     0.022     0.867      ← Item_7 loads on Factor_3
Item_8     0.014    -0.012     0.779
Item_9     0.066    -0.036     0.614

COMMUNALITIES (h²)
────────────────────────────────────────────────────────────────────────────────
           h²
Item_1  0.771   ✓ Good
Item_2  0.790   ✓ Good
Item_3  0.586   ✓ Good
Item_4  0.684   ✓ Good
Item_5  0.694   ✓ Good
Item_6  0.707   ✓ Good
Item_7  0.752   ✓ Good
Item_8  0.608   ✓ Good
Item_9  0.382   ⚠ Low (consider removing)

FACTOR CORRELATIONS (φ matrix, oblique rotation)
────────────────────────────────────────────────────────────────────────────────
          Factor_1  Factor_2  Factor_3
Factor_1     1.000     0.011     0.267   ← Factor_1 and Factor_3 correlate (r=0.27)
Factor_2     0.011     1.000     0.019   ← Factor_2 is independent
Factor_3     0.267     0.019     1.000

✓ No major interpretability issues detected
```

**Summary:**
- 3 factors clearly emerged (parallel analysis confirmed this)
- Items 1–3 → Factor 1; Items 4–6 → Factor 2; Items 7–9 → Factor 3
- All communalities > 0.38 (acceptable)
- Factor_1 and Factor_3 have moderate correlation (r = 0.27; not problematic)
- Recommend: Keep all 3 factors; consider revising Item_9 (low h²)

---

## API Reference

### `fit_efa(df, n_factors=None, method="ml", rotation="oblimin", ...)`

**Core function: fit EFA model**

```python
fa, diagnostics = fit_efa(
    data=df,
    n_factors=None,          # None = use parallel analysis
    method="ml",             # "ml" or "pa"
    rotation="oblimin",      # "oblimin" or "varimax"
    check_factorability=True,
    parallel_analysis=True
)
```

**Returns:**
- `fa`: FactorAnalyzer object with `.loadings_`, `.phi_`, `.get_communalities()`, etc.
- `diagnostics`: Dict with KMO, Bartlett, n_factors, variance_explained, etc.

---

### `summary_efa(fa, df, loading_threshold=0.30, verbose=True)`

**Format and display EFA results**

```python
summary = summary_efa(fa, df, loading_threshold=0.30, verbose=True)
# Prints formatted loadings, communalities, correlations, flags
# Returns dict with 'loadings', 'communalities', 'factor_correlations', 'flags'
```

---

## References

- **PCA vs EFA distinction:** Alavi et al., "EFA and PCA in clinical studies," *J. Advanced Nursing* (2020)
- **Parallel analysis:** Horn, "A rationale and test for the number of factors," *Psychometrika* (1965)
- **Rotation:** Fabrigar et al., "Evaluating the use of EFA in psychological research," *Psychol. Methods* (1999)
- **Fit indices:** Hu & Bentler, "Cutoff criteria for fit indices," *Structural Equation Modeling* (1999)
- **Communalities & Heywood:** Heywood, "On finite sequences of real numbers," *Proc. Royal Society* (1931)
