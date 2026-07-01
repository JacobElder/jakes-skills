# Item response theory (IRT) — deep reference

IRT models the probability of an item response as a function of (1) a respondent's latent trait level θ and (2) item parameters. Unlike CTT, where reliability is a single number for the whole test, IRT gives **conditional measurement precision** — how well the test measures at each point on the trait continuum.

## Core idea

The **item response function (IRF)** maps θ → P(response). For dichotomous items, it's a sigmoid going from near 0 at low θ to near 1 at high θ. The shape of that sigmoid depends on item parameters.

Two assumptions underlie unidimensional IRT:

1. **Unidimensionality**: a single latent trait explains item responses.
2. **Local independence**: conditional on θ, item responses are independent. (If the items are passages with shared reading comprehension demands, this is violated and needs a multidimensional or testlet model.)

Check both before adopting IRT. Lack of unidimensionality biases item parameters and θ estimates.

## Dichotomous IRT models

### 1PL / Rasch model

P(Xᵢ = 1 | θ) = exp(θ − bᵢ) / [1 + exp(θ − bᵢ)]

One parameter per item: **difficulty bᵢ** (where on the θ scale the item has 50% probability of correct response).

All items share the same **discrimination** (slope). This is a *substantive commitment*, not a statistical convenience — Rasch's argument was that equal discrimination gives **specific objectivity**: item parameters are independent of the sample of persons and person parameters are independent of the sample of items. The Rasch tradition (Andrich, Wright) treats Rasch as the model items should *conform to*, with misfitting items revised or dropped.

### 2PL (Birnbaum)

P(Xᵢ = 1 | θ) = exp(aᵢ(θ − bᵢ)) / [1 + exp(aᵢ(θ − bᵢ))]

Adds **discrimination aᵢ** — the slope of the IRF at b. Higher a = steeper curve = item differentiates better between adjacent θ levels.

The 2PL tradition (Birnbaum, Lord) lets data dictate the model — items vary in discrimination empirically and we should model that.

**Rasch vs. 2PL is a substantive choice, not just "which fits better."** Don't switch based on AIC alone if you've committed to Rasch properties for measurement reasons (e.g., specific objectivity for cross-test linking).

### 3PL

P(Xᵢ = 1 | θ) = cᵢ + (1 − cᵢ) × exp(aᵢ(θ − bᵢ)) / [1 + exp(aᵢ(θ − bᵢ))]

Adds **guessing cᵢ** — the lower asymptote (probability of correct response for very low θ).

Use only for multiple-choice ability/achievement tests where guessing is plausible. **Don't use for personality or attitude items** — there's no "right answer" to guess. The c parameter is hard to estimate (requires many low-ability respondents at each item) and is often constrained or given priors in practice.

### 4PL

Adds an upper asymptote < 1 (slips). Rarely used; needs even larger N.

## Polytomous IRT models (for Likert)

### Graded Response Model (Samejima, 1969)

For items with K ordered categories, models cumulative response probability. For category k (with k = 0...K−1):

P(Xᵢ ≥ k | θ) = exp(aᵢ(θ − bᵢ,k)) / [1 + exp(aᵢ(θ − bᵢ,k))]

with K−1 ordered thresholds bᵢ,1 < bᵢ,2 < ... < bᵢ,K−1. The probability of a specific category is the difference: P(Xᵢ = k) = P(Xᵢ ≥ k) − P(Xᵢ ≥ k+1).

**Default choice for Likert items with strong N.**

### Generalized Partial Credit Model (Muraki, 1992)

Similar but parameterizes adjacent-category logits rather than cumulative. Allows for non-ordered thresholds (which GRM doesn't). Sometimes better fit for items where middle categories are rarely chosen.

### Partial Credit Model (Masters, 1982)

Rasch-family equivalent — equal discrimination across items.

### Rating Scale Model (Andrich, 1978)

PCM with the constraint that thresholds have the same spacing across items (different overall difficulty, same step structure). Useful when items share a common response scale.

```r
library(mirt)
fit_grm <- mirt(data, 1, itemtype = "graded")     # GRM
fit_gpcm <- mirt(data, 1, itemtype = "gpcm")      # GPCM
fit_rsm <- mirt(data, 1, itemtype = "Rasch")      # equivalent to PCM/RSM family
coef(fit_grm, simplify = TRUE, IRTpars = TRUE)
itemplot(fit_grm, item = 1)
```

## Parameter invariance

A property of IRT that CTT doesn't have: **item parameters don't depend on the sample of persons** (up to a linear transformation), and **person parameters don't depend on the sample of items**. This is what enables equating, computerized adaptive testing (CAT), and matrix-sampled measurement (different respondents see different items, all on a common θ scale).

Invariance holds only when the model fits. Check via:

- Plot item parameters from two subsamples; should fall on the identity line.
- DIF tests (do parameters differ across groups beyond what θ predicts? — see `invariance_dif.md`).

## Estimation

### For item parameters

- **Marginal Maximum Likelihood (MML)** with EM algorithm — the standard. Integrates over the θ distribution (typically assumed N(0,1)). Implemented in `mirt`, `ltm`, IRTPRO, flexMIRT.
- **Joint Maximum Likelihood (JML)** — historic; biased, especially for short tests. Avoid.
- **Conditional Maximum Likelihood (CML)** — Rasch-specific; conditions on total score, eliminating θ. Implemented in `eRm` package.
- **Bayesian MCMC** — `MCMCpack`, Stan via `edstan` or `rstanarm`. Useful for small N or complex models.

### For person parameters

After item parameters are estimated, estimate θ for each person:

- **Maximum Likelihood (ML)** — efficient asymptotically; undefined for all-correct or all-incorrect response patterns.
- **Maximum A Posteriori (MAP)** — adds a prior on θ; always defined; biased toward the prior mean.
- **Expected A Posteriori (EAP)** — Bayesian mean; the modern default. Has known SE per person.
- **Plausible values** — multiple draws from each person's posterior. Used in large-scale assessment (PISA, NAEP).

```r
theta_eap <- fscores(fit, method = "EAP", full.scores.SE = TRUE)
```

## Sample size requirements

Approximate minimums (lower → biased; higher → more stable):

- Rasch (1PL): ~250 respondents per test, fewer with stable θ distribution.
- 2PL: ~500.
- 3PL: ~1000, ideally larger; c is hard to estimate.
- GRM: 500+ depending on number of categories.

Below these, parameter estimates have wide CIs and θ estimation may be inconsistent across subsamples. CAT applications with item banks need much more — often 1000+ per item with calibration designs.

## Information and reliability in IRT

**Item information function (IIF)**:

For 2PL: Iᵢ(θ) = aᵢ² × Pᵢ(θ) × (1 − Pᵢ(θ))

Peaks at θ = b (for 2PL) and is taller for higher a. **An item provides the most information about respondents whose θ is near its difficulty.**

**Test information function (TIF)** = sum of IIFs across items. The TIF is the test's measurement precision at each θ:

SE(θ) = 1 / √I(θ)

Reliability at a given θ: ρ(θ) = I(θ) / (I(θ) + 1) for standard N(0,1) prior.

**This is more informative than a single reliability coefficient.** A test can have great precision at moderate θ but be useless at the extremes (or vice versa). For screening (clinical cutoff at low θ), you want a TIF peak at the cutoff, not at the mean.

```r
plot(fit, type = "info")               # test information function
plot(fit, type = "infoSE")             # info and conditional SE
plot(fit, type = "infotrace")          # per-item information
```

## Model fit

### Item-level fit

- **S−χ² (Orlando & Thissen, 2000)** — compares observed and expected frequencies in score groups. The standard fit statistic; in `mirt::itemfit(fit)`.
- **Infit/Outfit (Rasch tradition)** — weighted (infit) and unweighted (outfit) mean-square residuals. Values near 1 indicate fit; > 1.3 underfit, < 0.7 overfit. Standard in Rasch analysis.

### Model-level fit

- **M2 statistic (Maydeu-Olivares & Joe, 2006)** — limited information goodness-of-fit; `mirt::M2(fit)`. Reports an RMSEA, CFI, TLI for IRT (analogous to SEM fit indices).
- **AIC, BIC** — for non-nested model comparison.
- **Likelihood ratio test** for nested models (1PL vs. 2PL, etc.).

### Assumption checks

- **Dimensionality**: parallel analysis, MAP, or formal tests (DETECT, NOHARM). For multidimensional items: bifactor IRT or multidimensional IRT (MIRT, also implemented in `mirt`).
- **Local independence**: Q3 statistic (Yen, 1984) — correlations of standardized residuals. Large positive Q3s indicate local dependence (item pair shares more than θ explains).
- **Monotonicity**: nonparametric checks (Mokken scaling, `mokken` package). Item characteristic curves should be monotonically increasing in θ.

## IRT applications

### Computerized adaptive testing (CAT)

Each item is selected to maximize information at the respondent's current θ estimate. Dramatically shorter tests for the same precision. Requires a calibrated item bank.

### Test equating

Putting scores from different test forms on a common scale. IRT-based equating uses anchor items (common across forms) to link θ scales. Procedures: mean/mean, mean/sigma, Stocking-Lord, Haebara. Implemented in `equate`, `plink`, `equateIRT` packages.

### Differential item functioning (DIF)

Items that function differently across groups (e.g., gender, language) beyond what θ predicts. See `invariance_dif.md`.

### Item banking and matrix sampling

Different respondents see different items, all on a common θ scale. Enables large-scale assessment (NAEP gives different students different ~10-item booklets), longitudinal designs where you change items but track the same construct, and content-balanced CAT.

## What IRT buys you (vs. CTT)

- Conditional precision (SE varies with θ).
- Item parameters that don't depend on the sample.
- A principled way to link tests across forms and over time.
- Adaptive testing.
- Detection of DIF beyond confounding with mean differences.
- Information about *where* on the trait your test works well.

## What IRT requires

- Larger N than CTT.
- Unidimensionality (or commitment to multidimensional models).
- Local independence.
- Substantively defensible model choice (Rasch vs. 2PL).
- Software literacy beyond reading mean correlations.

## R workflow

```r
library(mirt)

# Fit unidimensional 2PL
fit <- mirt(data, 1, itemtype = "2PL", SE = TRUE)
coef(fit, IRTpars = TRUE, simplify = TRUE)   # IRT parameterization (a, b)

# Fit the same data with Rasch and compare
fit_rasch <- mirt(data, 1, itemtype = "Rasch")
anova(fit_rasch, fit)   # LRT, AIC, BIC

# Item and model fit
itemfit(fit, fit_stats = "S_X2")
M2(fit)

# Plots
plot(fit, type = "trace")          # IRFs
plot(fit, type = "info")           # TIF
itemplot(fit, item = 3)            # one item

# Person scores
theta <- fscores(fit, method = "EAP", full.scores.SE = TRUE)

# For polytomous
fit_grm <- mirt(likert_data, 1, itemtype = "graded")
```

For DIF: `mirt::DIF(fit, which.par = c("a1","d"), Focal.name = "group2")`.

For multidimensional: `mirt(data, 2, itemtype = "2PL")` fits 2-factor 2PL; specify a confirmatory pattern via `mirt.model()`.

## Common mistakes

- **Adopting IRT for N < 200** — estimates will be too unstable to be useful.
- **Using 3PL when guessing isn't substantively relevant** — overfit.
- **Ignoring local independence** for testlet data (passage-based items) — biases everything downstream.
- **Reporting θ as if it has the same SE for every respondent** — it doesn't; that's the whole point. Report conditional SEs.
- **Equating without checking parameter invariance across forms** — bad linkings propagate.
- **Treating the choice of Rasch vs. 2PL as a model selection problem** — it's a measurement-philosophy problem first.
