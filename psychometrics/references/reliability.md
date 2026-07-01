# Reliability — deep reference

Reliability is the proportion of observed-score variance attributable to true-score variance in the classical test theory (CTT) decomposition X = T + E, with E ⊥ T. Equivalently, it's the squared correlation between observed and true scores, or the correlation between observed scores on parallel forms.

Reliability is a **property of scores in a population**, not a property of an instrument. Always frame as "alpha was .85 in this sample" — never "the scale has alpha = .85."

## Coefficient alpha — what it actually is

Cronbach's alpha is:

α = (k / (k−1)) × (1 − Σσᵢ² / σₓ²)

where k is number of items, σᵢ² is item variance, σₓ² is total-score variance.

Alpha is a **lower bound on reliability** *only* under the assumption of **tau-equivalence** (all items have equal true-score loadings on the construct). Under congeneric measurement (the realistic case — loadings differ), alpha underestimates reliability and **omega** is preferred.

### Common misuses

1. **Alpha as evidence of unidimensionality** — wrong. Alpha is driven by `k × r̄` (number of items times mean inter-item correlation). A 30-item multidimensional scale can have α = .90.
2. **Comparing alphas across scales of different lengths** as if they're directly comparable — they aren't; use Spearman-Brown to project to a common length.
3. **Nunnally's 0.70 rule cited universally** — Nunnally (1978) said 0.70 for early-stage research, 0.80+ for applied use, 0.90+ for individual decisions. The 0.70 cutoff is often misapplied.
4. **Reporting alpha for a clearly multidimensional scale by computing on the total score** — meaningless. Compute per-subscale, or use a hierarchical model and report omega-hierarchical.

### When alpha is OK

When items are approximately tau-equivalent and unidimensional, alpha is fine and is well understood by readers. Report it alongside omega rather than instead of omega.

## McDonald's omega — the modern default

Omega is derived from a factor model. For a unidimensional congeneric model with factor loadings λᵢ and item residual variances θᵢ:

ω = (Σλᵢ)² / [(Σλᵢ)² + Σθᵢ]

This is **omega-total**: the proportion of total-score variance attributable to all common variance (general + group factors in a bifactor model).

For hierarchical (bifactor) structures, distinguish:

- **omega-hierarchical (ω_h)**: variance attributable to the general factor alone. Tells you how interpretable a total score is.
- **omega-total (ω_t)**: variance attributable to all common factors. The upper bound of ω_h.
- **omega-subscale (ω_s)**: reliability of a subscale score after partialling out the general factor.

If ω_h is much lower than ω_t (e.g., ω_h = .55, ω_t = .90), the total score is contaminated by group-factor variance and shouldn't be interpreted as "the construct."

### Computing omega in R

```r
# psych package — works on raw data or correlation matrix
library(psych)
om <- omega(data, nfactors = 3, fm = "ml", poly = TRUE)  # poly=TRUE for ordinal Likert
om$omega_h   # hierarchical
om$omega.tot # total
# also returns subscale omegas

# semTools — preferred when you already have a fitted CFA model
library(lavaan); library(semTools)
fit <- cfa(model, data = d, ordered = ord_items, estimator = "WLSMV")
compRelSEM(fit)  # current best-practice omega from lavaan models;
                 # handles ordinal and missing data correctly
```

`semTools::compRelSEM()` is the modern preferred call; the older `reliability()` function is deprecated. For ordinal items, computing omega from the polychoric-based CFA is correct; computing alpha on raw Likert sums underestimates reliability of the underlying continuous construct.

## Reliability of a composite — Spearman-Brown

If you have reliability ρ for a test of length k and you want reliability for a test of length nk (same item quality):

ρ_new = (n × ρ) / (1 + (n−1) × ρ)

So doubling test length (n = 2) takes ρ = .70 to .82, not .90. Quintupling takes .70 to .92. This is why short scales struggle for reliability and why "just add more items" has diminishing returns.

Common applied use: a pilot showed α = .65 with 6 items; how many items needed for .85? Solve SB for n: n = ρ_new × (1 − ρ) / (ρ × (1 − ρ_new)) = .85 × .35 / (.65 × .15) ≈ 3.05, so ≈ 18 items total.

## Standard error of measurement (SEM)

SEM = σ_x × √(1 − ρ)

The SEM gives confidence intervals around individual scores. For an observed score X, the 95% CI is approximately X ± 1.96 × SEM.

SEM is **on the score metric** (more useful than reliability for interpreting individual scores). A reliability of .90 on a scale with SD = 10 gives SEM = 3.16, so a 95% CI is ±6.2 points wide. Decisions based on small score differences are often within measurement error.

## Test-retest reliability

Test-retest correlation conflates two things you should separate:

- **Stability of the construct**: trait constructs should be stable over months; state constructs should not.
- **Reliability of measurement**: how much measurement error in the score.

Pick the retest interval to match construct theory. State anxiety should NOT have high test-retest at 4 weeks; if it does, you're not measuring state anxiety. Trait Big Five should have r > .70 at 6+ months.

Test-retest is also affected by **practice effects** (especially cognitive tests), **regression to the mean** when initial scores are extreme, and **systematic life events** between testings.

## Alternate forms reliability

Correlation between two parallel forms administered to the same people. Combines stability + equivalence if separated in time. Useful for educational tests (SAT, GRE) where forms must be interchangeable. Established via test equating (separate topic).

## Interrater reliability and agreement

Distinguish:

- **Agreement**: do raters give the same score? (% agreement, Cohen's kappa, weighted kappa, AC1).
- **Reliability**: do raters rank-order targets the same way? (ICC, Pearson r between raters).

You can have high reliability with low agreement (raters use different parts of the scale but rank consistently) and vice versa.

### Kappa for categorical agreement

Cohen's κ = (p_o − p_e) / (1 − p_e)

Adjusts observed agreement for chance. Weighted kappa for ordinal categories (linear or quadratic weights).

**Kappa paradoxes**: with very unbalanced category frequencies, kappa can be low even when agreement is high. Report observed agreement and prevalence-adjusted statistics (Byrt et al. 1993) alongside.

For >2 raters: Fleiss's kappa, Light's kappa (mean of pairwise kappas), or Krippendorff's alpha (handles missing data, multiple scales).

### ICC for continuous ratings

The Shrout & Fleiss (1979) framework:

- **ICC(1,1)**: one-way random; each target rated by a different random rater. Single-measure.
- **ICC(2,1)**: two-way random; same raters rate all targets, raters drawn from a population. Single-measure.
- **ICC(3,1)**: two-way mixed; same raters rate all targets, raters are the population (no generalization). Single-measure.
- **ICC(k)**: average of k raters. Always higher than single-rater ICC.

McGraw & Wong (1996) re-label these as ICC(A,1), ICC(C,1), etc., distinguishing **absolute agreement** vs. **consistency**. Modern packages report both naming conventions.

```r
psych::ICC(rating_matrix)  # prints all 6 ICCs with labels
```

**Choosing**: For generalizing to other raters (typical research use), ICC(2,1) absolute agreement is usually right. For describing this specific rater team's reliability, ICC(3,1) consistency. Report which you used and why.

Rules of thumb (Koo & Li 2016): < .50 poor, .50–.75 moderate, .75–.90 good, > .90 excellent. These are rough; context matters.

## Generalizability theory (G theory)

Cronbach et al.'s (1972) extension of CTT that treats measurement error as decomposable into **facets** (raters, items, occasions, forms) using ANOVA-style variance components.

A G study estimates variance components for each facet and their interactions. A D study (decision study) uses those components to compute reliability-like coefficients (**G coefficient** for relative decisions, **Phi coefficient** for absolute decisions) under different design choices (more raters? more items? more occasions?).

Example: essays rated by raters on occasions. Person × Rater × Occasion design. G study estimates σ²(p), σ²(r), σ²(o), σ²(pr), σ²(po), σ²(ro), σ²(pro,e). D study answers: if I want G > .80, do I add raters or occasions? G theory tells you which facet contributes most error variance per unit of cost.

R packages: `gtheory`, `lme4` (variance components from random-effects ANOVA), or hand calculation from ANOVA tables.

G theory is underused in applied work and is especially valuable for **performance assessments** (essays, OSCEs, observational coding) where the design has multiple sources of error.

## Reliability of difference scores

Notorious — difference scores X − Y are usually much less reliable than X or Y individually:

ρ_(X−Y) = (ρ_x × σ²_x + ρ_y × σ²_y − 2r_xy × σ_x σ_y) / (σ²_x + σ²_y − 2r_xy σ_x σ_y)

When X and Y are correlated (which they usually are for pre-post), the difference score reliability drops. This is the technical basis for the long-standing skepticism about gain-score analyses and why latent-change models (in SEM) or ANCOVA-on-post are usually preferred.

## Recommended cutoffs (with caveats)

| Use | Recommended ρ |
|---|---|
| Early research, group comparisons | ≥ .70 |
| Applied research, established scales | ≥ .80 |
| Individual high-stakes decisions | ≥ .90 (often .95) |

These are heuristics. A clinical screening instrument used to make a binary decision needs much higher reliability than a research scale used to estimate group means. Sample size mitigates measurement error for group means; nothing mitigates it for individual scores.
