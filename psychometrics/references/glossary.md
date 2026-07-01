# Psychometric glossary

Terms that recur in measurement work, including pairs that are easy to confuse. Use this as a quick reference when reading a paper or evaluating a claim.

## Foundational

- **Construct**: a theoretical attribute (depression, conscientiousness, math ability) that is not directly observable but is inferred from observable behavior.
- **Indicator / item / observed variable**: a single observation (item response, behavior count, physiological reading) used to infer construct level.
- **Latent variable**: the unobserved construct itself, modeled as the cause of observed indicators (reflective) or constituted by them (formative).
- **Reflective indicator**: caused by the latent variable (most psychological items: "I am sad" reflects depression).
- **Formative indicator**: constitutes the latent variable (income, education, occupation constitute SES, not the reverse).
- **Measurement model**: the relations between observed indicators and latent constructs.
- **Structural model**: the relations among latent constructs.
- **True score (T)**: the expected value of an observed score across infinite parallel administrations. T = X − E in CTT.
- **Error score (E)**: random measurement error. E[E] = 0, E ⊥ T in CTT.
- **Observed score (X)**: what you actually record. X = T + E.

## CTT terms

- **Reliability (ρ)**: proportion of observed-score variance attributable to true-score variance. σ²_T / σ²_X.
- **Reliability index**: correlation between T and X. √ρ.
- **Parallel measures**: equal true scores AND equal error variances. Strongest equivalence.
- **Tau-equivalent measures**: equal true scores; error variances may differ. The assumption alpha requires.
- **Essentially tau-equivalent**: true scores differ by a constant; covariances are equal.
- **Congeneric measures**: true scores are linearly related (different loadings allowed). The realistic case; omega assumes this.
- **Internal consistency**: how strongly items hang together. Indexed by alpha, omega.
- **Test-retest reliability**: correlation between scores at two occasions on same persons.
- **Alternate forms (equivalence)**: correlation between scores on parallel forms.
- **Standard error of measurement (SEM)**: σ_X × √(1 − ρ). CI around individual observed scores.
- **Spearman-Brown prophecy**: how reliability changes with test length.

## Reliability vs. validity

- **Reliability**: consistency of measurement. A scale can be reliable (consistent) without being valid (measuring the right thing).
- **Validity**: appropriateness of score interpretations and uses.
- **Validity-reliability ceiling**: r_xy ≤ √(ρ_x ρ_y). Low reliability bounds attainable validity coefficients.
- **Attenuation correction**: dis-attenuated r = r_obs / √(ρ_x ρ_y). Theoretical maximum; report with care.

## Factor analysis

- **Common variance**: shared across indicators; modeled by FA.
- **Unique variance**: not shared with other indicators. = specific variance + measurement error.
- **Communality (h²)**: proportion of an indicator's variance explained by the common factors. Σλ² in orthogonal case.
- **Uniqueness (u²)**: 1 − h² for standardized items.
- **Factor loading (λ)**: regression coefficient of indicator on factor. Standardized version is the correlation when factors are orthogonal.
- **Pattern loading**: standardized regression coefficient in oblique rotation.
- **Structure loading**: zero-order correlation between item and factor in oblique rotation. Pattern × factor correlation matrix.
- **Eigenvalue**: variance accounted for by a component or factor.
- **Rotation**: transformation of factor axes to enhance interpretability. Orthogonal keeps factors uncorrelated; oblique allows correlation.
- **Simple structure (Thurstone)**: each item loads strongly on one factor and weakly on others; the goal of rotation.
- **PCA vs. FA**: PCA models total variance with determinate components; FA models common variance with latent factors.

## CFA / SEM

- **Identification**: enough constraints to uniquely solve for parameters.
- **Just-identified**: zero df; fits perfectly by construction.
- **Over-identified**: positive df; model can be tested against the data.
- **Under-identified**: not enough info; can't be estimated uniquely.
- **Fit index**: a number summarizing model-data agreement (CFI, TLI, RMSEA, SRMR).
- **Modification index (MI)**: estimated chi-square decrease if a fixed parameter were freed.
- **Standardized residual**: covariance not reproduced by the model, in standardized units.
- **Heywood case**: improper estimate (communality > 1, negative variance). Indicates problem.
- **FIML**: full information maximum likelihood for missing data.
- **WLSMV**: mean- and variance-adjusted weighted least squares for ordinal data.
- **MLR**: maximum likelihood with robust standard errors (Huber-White) for non-normal continuous data.

## IRT

- **θ (theta)**: latent trait level for a person.
- **Item response function (IRF) / item characteristic curve (ICC)**: P(response | θ) as a function of θ. (Careful: "ICC" overloaded with intraclass correlation.)
- **Difficulty (b)**: θ value where P(correct) = .5 for 1PL/2PL.
- **Discrimination (a)**: slope of IRF at θ = b. Higher = item differentiates better.
- **Guessing (c)**: lower asymptote in 3PL.
- **Local independence**: items independent given θ.
- **Specific objectivity**: Rasch property; comparisons of persons independent of items used, and vice versa.
- **Item information function (IIF)**: precision contributed by an item at each θ.
- **Test information function (TIF)**: sum of IIFs.
- **EAP, MAP, ML scoring**: methods for estimating individual θ.
- **Plausible values**: multiple draws from each person's θ posterior, used in large-scale assessment.

## Polytomous IRT

- **Graded Response Model (GRM, Samejima)**: cumulative-category logits.
- **Generalized Partial Credit Model (GPCM, Muraki)**: adjacent-category logits.
- **Partial Credit Model (PCM, Masters)**: Rasch family GPCM.
- **Rating Scale Model (Andrich)**: PCM with shared step structure.
- **Threshold**: the θ at which a respondent has 50% probability of crossing into the next category.

## Measurement invariance

- **Configural invariance**: same factor structure (loadings nonzero in same positions).
- **Metric (weak) invariance**: equal loadings.
- **Scalar (strong) invariance**: equal loadings and intercepts.
- **Strict (residual) invariance**: equal loadings, intercepts, and residual variances.
- **Partial invariance**: invariance with some parameters released.
- **DIF (Differential Item Functioning)**: item-level invariance failure.
- **Uniform DIF**: item consistently easier/harder for one group across θ.
- **Non-uniform DIF**: DIF varies with θ (loading or discrimination differs).
- **Bias**: DIF that's attributable to construct-irrelevant features.
- **Anchor items**: items assumed invariant to put groups on common scale.

## Validity sources (modern unified framework)

- **Content evidence**: items represent the domain.
- **Response process evidence**: respondents engage with items as theorized.
- **Internal structure evidence**: factor structure, reliability, DIF.
- **Relations-to-other-variables evidence**: convergent, discriminant, predictive, incremental.
- **Consequences evidence**: intended and unintended consequences of test use.
- **Multitrait-multimethod (MTMM)**: design for separating trait variance from method variance.
- **Nomological network**: the theoretical web of expected relations the construct sits in.
- **Construct underrepresentation**: failure to capture important aspects of the construct.
- **Construct-irrelevant variance**: variance in scores due to things other than the construct.

## Reliability indices

- **Alpha (α)**: Cronbach's coefficient. Lower bound on reliability under tau-equivalence.
- **Omega-total (ω_t)**: total common variance / total variance. From factor model.
- **Omega-hierarchical (ω_h)**: general factor variance / total. For bifactor / hierarchical scales.
- **Omega-subscale (ω_s)**: subscale variance after removing general factor.
- **Glb (greatest lower bound)**: highest possible lower bound on reliability for a given covariance matrix; tighter than alpha but biased upward with small samples.
- **Test-retest correlation (r_tt)**: stability over time.
- **Cohen's kappa (κ)**: chance-corrected agreement for two raters on categorical data.
- **Weighted kappa**: ordinal categories with disagreement weights.
- **ICC**: intraclass correlation; multiple variants (Shrout & Fleiss labels 1, 2, 3 × single, average; McGraw-Wong labels A, C × 1, k).

## Generalizability theory

- **Facet**: a source of measurement variation (raters, items, occasions).
- **Object of measurement**: the entity being measured (usually persons).
- **Universe score**: expected score over the universe of admissible observations.
- **Crossed facet**: every level of facet A appears with every level of facet B.
- **Nested facet**: levels of A are unique to each level of B.
- **G study**: estimates variance components for facets.
- **D study**: applies G results to plan optimal designs.
- **G coefficient**: reliability for relative decisions (norm-referenced).
- **Phi coefficient**: reliability for absolute decisions (criterion-referenced).

## Item analysis

- **Item difficulty (p-value)**: proportion correct (cognitive) or mean (Likert, often standardized).
- **Item discrimination**: how well an item differentiates high vs. low scorers. Point-biserial (cognitive), corrected item-total correlation (general).
- **Distractor analysis**: examination of how often each wrong option is chosen, and by whom.
- **Item-total correlation (corrected)**: correlation of item with total of remaining items.

## Scoring

- **Sum score / raw score**: sum of item responses. Simple, robust.
- **Mean score**: average of item responses. Like sum, but rescaled.
- **Standardized score (z)**: (X − M) / SD. Mean 0, SD 1.
- **T-score**: 50 + 10z. Mean 50, SD 10.
- **Percentile rank**: percent of population at or below this score.
- **Stanine**: 1–9 scale, mean 5, SD ~2.
- **Normal curve equivalent (NCE)**: similar to percentile but on equal-interval scale.
- **Grade equivalent / age equivalent**: developmental scores; widely misinterpreted, use with care.
- **Factor score**: estimate of latent factor value. Regression, Bartlett, or Anderson-Rubin methods.
- **IRT theta**: latent trait estimate from IRT model.

## Often-confused pairs

- **Reliability vs. validity**: how consistent vs. how appropriate.
- **PCA vs. FA**: total variance vs. common variance.
- **EFA vs. CFA**: discovery vs. testing.
- **Alpha vs. omega**: tau-equivalence assumed vs. congeneric.
- **Cohen's kappa vs. ICC**: categorical agreement vs. continuous reliability.
- **Difficulty (CTT) vs. difficulty (IRT)**: proportion correct vs. theta-metric threshold; CTT difficulty is sample-dependent, IRT difficulty is not (under invariance).
- **Discrimination (CTT) vs. discrimination (IRT)**: item-total correlation vs. slope parameter.
- **Pattern loading vs. structure loading**: regression vs. correlation in oblique rotation.
- **DIF vs. bias**: statistical finding vs. substantively unfair.
- **Test of fit (chi-square) vs. fit index (CFI/RMSEA)**: exact-fit test (almost always rejects with large N) vs. approximate fit (more useful with large N).
- **Configural / metric / scalar invariance**: structure / loadings / intercepts.
- **State vs. trait**: momentary vs. enduring; affects test-retest interpretation.
- **Norm-referenced vs. criterion-referenced**: ranked against peers vs. against a fixed standard.

## Easily misused terms

- **"Significant" loading** — a misnomer; loadings are usually evaluated by magnitude (often ≥ .30 or .40), not by statistical significance.
- **"The scale was validated"** — validity isn't done once; it's an ongoing accumulation of evidence.
- **"Cronbach's alpha measures unidimensionality"** — no. It doesn't.
- **"High reliability proves validity"** — no. Reliable measures of the wrong thing exist.
- **"Modification indices improved the model"** — they improved fit *to this sample*; replication is the test.
- **"ICC" without specifying variant** — six different ICCs exist; specify.
