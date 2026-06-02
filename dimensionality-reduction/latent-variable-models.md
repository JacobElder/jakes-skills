# Latent-variable models: EFA & CFA

This is **job 3**: recover the unobserved constructs that *generated* the observed variables. This
is a different intellectual activity from PCA/UMAP, and conflating it with them is one of the most
common and consequential errors in applied stats. Read this before advising on "factor analysis,"
"latent constructs," "survey/scale structure," or "validating a questionnaire."

---

## The common-factor model (why EFA ≠ PCA)

EFA and CFA both assume the **common-factor model**:

> observed variable = (loading × common factor) + unique factor

The total variance of each observed item is split into **common variance** (shared with other items,
attributed to latent factors) and **unique variance** (item-specific + measurement error). EFA/CFA
model *only the shared variance* as arising from latent factors.

**PCA does not do this.** PCA has no error term and no latent factors; principal components are just
linear combinations of the observed variables that repackage **all** variance — common, unique, and
noise alike. The causal direction is also reversed:

- **EFA/CFA:** latent factor → causes → observed items (reflective measurement model).
- **PCA:** observed items → define → components (a weighted summary).

**Consequence.** If the question is "what underlying constructs explain the *correlations* among my
items?" → factor analysis. If it's "give me fewer composite axes that retain variance for prediction
or plotting" → PCA. They give numerically different loadings and can suggest different numbers of
dimensions. The fact that SPSS buries PCA *inside* its "Factor" menu (and makes it the default
extraction) has propagated this confusion for decades — call it out when you see it.

---

## EFA — Exploratory Factor Analysis

Use when you do **not** have a firm a-priori structure and want to *discover* how many latent factors
underlie a set of items and which items load where. The standard pipeline:

1. **Check factorability.** Kaiser–Meyer–Olkin (KMO) sampling adequacy (want > ~0.6, ideally > 0.8)
   and **Bartlett's test of sphericity** (want significant). If the correlation matrix is near-identity,
   there's nothing to factor.

2. **Choose an extraction method.** **Principal-axis factoring (PAF)** or **maximum likelihood (ML)** —
   *not* PCA. Use ML if you want fit statistics / significance tests and the data are ~normal; PAF is
   more robust to non-normality. (Defaulting to PCA "because it's the default" is the error above.)

3. **Decide the number of factors.** Don't use the old "eigenvalue > 1" (Kaiser) rule alone — it
   systematically over-extracts. Prefer **parallel analysis** (compare observed eigenvalues to those
   from random data; keep factors above the random curve), the scree elbow, and — critically —
   **interpretability and theory**. Map and report several criteria.

4. **Rotate** to interpretable simple structure.
   - **Oblique** (oblimin, promax) when factors are expected to **correlate** — usually the realistic
     default in social science. It also *reports* the inter-factor correlations, which is information.
   - **Orthogonal** (varimax) only when you have reason to believe factors are uncorrelated.
   Rotation doesn't change fit; it repackages the loadings for interpretation.

5. **Interpret loadings.** Common thresholds: |loading| > 0.30–0.40 to "count"; flag
   **cross-loadings** (an item loading on multiple factors) and **Heywood cases** (impossible
   communalities > 1). Name factors from their high-loading items — and stay honest about weak factors.

**Tools.** R: `psych::fa()` (set `fm="ml"` or `"pa"`, `rotate="oblimin"`), `psych::fa.parallel()`.
Python: `factor_analyzer` (`FactorAnalyzer(rotation='oblimin', method='ml')`, plus KMO/Bartlett
helpers). Note: sklearn's `FactorAnalysis` does ML extraction but offers **no rotation** and limited
diagnostics — fine for a quick latent-variance model, inadequate for real psychometric EFA.

---

## CFA — Confirmatory Factor Analysis

Use when you **already have** a hypothesized structure (from theory or a prior EFA) and want to
**test** it. CFA is **not** a structure-discovery / dimensionality-reduction tool — it is hypothesis
testing within **structural equation modeling (SEM)**. You specify, in advance, exactly which items
load on which factors (and which loadings are fixed to zero), fit the model, and judge fit.

**Fit indices to report (and rough conventional cutoffs — treat as guidelines, not laws):**
- **χ²** (almost always significant in large N, so don't rely on it alone)
- **CFI / TLI** ≥ ~0.95 (good), ≥ 0.90 (acceptable)
- **RMSEA** ≤ ~0.06 (good), ≤ 0.08 (acceptable); report its CI
- **SRMR** ≤ ~0.08

**Crucial discipline — don't double-dip.** Do **not** run EFA and then CFA on the **same** sample and
call the CFA "confirmation." That's circular: you'd be confirming a model you built from that exact
data. Split the sample, or use a fresh dataset, or cross-validate. Also resist piling on
modification indices until fit "passes" — each post-hoc freed parameter turns confirmation back into
exploration and inflates the appearance of fit.

**Tools.** R `lavaan` is the standard (`cfa(model, data)`); Python `semopy`. Commercial: Mplus, AMOS,
LISREL.

---

## Quick decision guide

| Situation | Method |
|---|---|
| "I have 40 survey items; how many constructs are there and what loads where?" | **EFA** (ML/PAF + parallel analysis + oblique rotation) |
| "Theory says my scale has 3 factors; does it hold in this new sample?" | **CFA** |
| "I just want fewer numeric features for a model / a quick 2D plot" | **PCA** (this is not factor analysis) |
| "Are my latent factors themselves correlated?" | EFA with **oblique** rotation (reports factor correlations), or a CFA with correlated factors |
| "I want to model factors *and* relationships among them / with outcomes" | **SEM** (CFA is the measurement part) |

The recurring advice to give: name the goal first. "Factor analysis" is not one thing, and it is not
PCA. The cost of getting this wrong is publishing construct claims that the method never actually
supported.

---

## Sources / further reading

- The PCA-vs-EFA distinction: Alavi et al., "EFA and PCA in clinical studies: which one should you
  use?" *J. Advanced Nursing* (2020); Widaman on common vs total variance; the long-standing
  "components are not factors" literature.
- Factor retention: Horn, "A rationale and test for the number of factors in factor analysis,"
  *Psychometrika* (1965) — parallel analysis; critiques of the Kaiser eigenvalue>1 rule.
- Polychoric/ordinal FA: for Likert data, factor analysis on a polychoric correlation matrix.
- CFA / SEM: Rosseel, "lavaan: An R Package for Structural Equation Modeling," *J. Statistical
  Software* (2012); Hu & Bentler (1999) for fit-index cutoffs (treat as guidelines, not laws).
