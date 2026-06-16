# SDT Estimation — corrections, models, and tooling

How you *estimate* SDT parameters matters as much as the formulas. The plug-in formulas in `formulas.md` are fine for a single observer with plenty of trials, but they quietly mishandle extreme cells, ignore estimation uncertainty, and fall apart for multi-subject designs. This file covers doing it right.

## Contents
1. Extreme-cell corrections (and why uniform application matters)
2. SDT *is* a probit GLM
3. Why the "two-step" plug-in approach is weak for groups
4. The GLMM (mixed-effects) approach
5. Bayesian SDT
6. Tooling: Python and R

---

## 1. Extreme-cell corrections

A hit or false-alarm rate of exactly 0 or 1 maps to z = ±∞, breaking d' and c. Two corrections dominate:

- **Log-linear (Hautus 1995) — DEFAULT.** Add 0.5 to all four cell counts, then compute rates:
  `HR = (Hits + 0.5)/(N_signal + 1)`, `FAR = (FA + 0.5)/(N_noise + 1)`.
  Apply it to **every** observer/condition uniformly, whether or not their cells are extreme. Monte-Carlo results show it gives the least biased d' (it slightly *under*estimates, predictably). Applying a correction only to the subjects with extreme cells introduces a systematic difference between "extreme" and "non-extreme" subjects that contaminates group comparisons — so correct everyone or no one.

- **1/(2N) rule.** Replace only the extreme proportions: 0 → 1/(2N), 1 → 1 − 1/(2N). More biased than log-linear and can err in either direction. Offered for compatibility; not recommended as a default.

The deeper fix is to **not plug in rates at all** — fit a model (below) that handles zero cells natively via the likelihood. Hierarchical Bayesian estimation in particular sidesteps edge corrections entirely, which is one of its main selling points.

## 2. SDT is a probit GLM (DeCarlo 1998)

Equal-variance yes/no SDT is *identical* to a binomial regression with a probit link. Code the response as 1 = "yes", and code the stimulus as a 0/1 (or effect-coded) predictor `signal`:

`probit(P(yes)) = β₀ + β₁ · signal`

Then:
- `β₀ = z(FAR)` (the intercept is the noise operating point), so **criterion** `c = −(β₀ + β₁/2)` and the noise-referenced criterion `k = −β₀`.
- `β₁ = z(HR) − z(FAR) = d'` (the stimulus coefficient *is* sensitivity).

This identity (verified in `scripts/test_sdt.py`) is the bridge to everything modern:
- **Unequal variance** = heteroscedastic probit (let the residual SD depend on stimulus). The variance ratio becomes the z-ROC slope.
- **Confidence ratings** = ordinal probit (cumulative-link model) with K−1 thresholds = the K−1 criteria.
- **Logistic link** instead of probit = Luce's choice-theory / "logistic detection" variant; d' is then on a logit scale (`sensR::SDT(..., "logit")`).

### "If SDT is just a probit GLM, is the SDT framework redundant?"
No — they answer different questions and you want both. The GLM is the **estimation engine**; SDT is the **measurement theory** that tells you what to estimate and how to read it.
- The GLM hands you coefficients; **SDT tells you those coefficients are sensitivity and bias** — the substantive decomposition (discriminability vs. threshold) is an interpretation the bare regression doesn't supply. `β₁` is just "the stimulus effect" until SDT names it d'.
- **Most SDT models are not a vanilla probit GLM.** Unequal-variance, rating/ROC, 2AFC and same-different/triangle, and meta-d' are extensions (heteroscedastic probit, ordinal probit, protocol-specific Thurstonian likelihoods, a type-2 generative model) — the plain probit identity is the *equal-variance yes/no special case*.
- The GLM view earns its keep precisely when you need its machinery: **covariates, hierarchical/mixed effects, proper uncertainty, and partial pooling.** For a single observer with plenty of trials, the closed-form plug-in (`sdt.py`) is faster and equivalent — you don't need to fit a model at all.
- SDT also carries the **theory the GLM doesn't**: the optimal-criterion / decision-theory layer (base rates, payoffs; `formulas.md` §10), the ROC geometry, and the conceptual apparatus (β as likelihood ratio, the latent evidence axis).

So: reach for the GLM/GLMM when you have a multi-subject/multi-condition design or need covariates and uncertainty; keep the SDT framework always, because it's what makes the numbers mean something.

## 3. Why the two-step plug-in is weak for groups

The common workflow — compute one d' per subject with the formula, then run a t-test/ANOVA/regression on those d' values — is the "two-step" approach. It is convenient but statistically lossy:

- **Ignores trial counts.** A d' from 20 trials and a d' from 2000 trials are treated as equally precise. They are not.
- **Ignores estimation uncertainty.** The second-stage test sees point estimates as if they were known exactly, understating uncertainty and inflating false positives in some regimes.
- **Forces ad-hoc edge corrections** on every subject before the second stage.
- **Throws away item structure.** If stimuli vary in difficulty (they always do), treating items as fixed inflates Type-I error the same way it does in any by-subjects-only analysis.

The literature ("The Statistical Costs of Two-Step Signal Detection Analyses"; Rabe 2018 GLMM-SDT power simulations) shows the one-step mixed model recovers effects more powerfully and with better-calibrated error rates.

## 4. The GLMM (mixed-effects) approach — modern default for multi-subject SDT

Fit a single probit mixed model to trial-level data with random effects for subjects **and** items:

`probit(P(yes_ijk)) = (β₀ + u₀ⱼ + w₀ₖ) + (β₁ + u₁ⱼ + w₁ₖ)·signal + covariates·signal + ...`

- Fixed `β₁` = group-average d'; fixed `β₀` relates to group bias.
- By-subject random slopes `u₁ⱼ` = individual differences in sensitivity; by-subject random intercepts = individual bias.
- Interact `signal` with a condition factor to get **condition differences in d'** directly, with proper uncertainty; interact non-`signal` terms for bias effects.
- Use the **maximal random-effects structure justified by the design** (random slopes for any within-subject/within-item manipulation), consistent with best practice for mixed models generally.

This handles extreme cells (via the likelihood), trial-count weighting, and subject+item generalization in one shot.

## 5. Bayesian SDT

A Bayesian probit/ordinal model (e.g., in `brms` or PyMC/`bambi`) gives full posteriors over d', c, the z-ROC slope, and any contrast — naturally propagating uncertainty and avoiding edge corrections. This is especially valuable when:
- per-subject data are sparse (clinical/patient populations),
- you want credible intervals on M-ratio or on a condition difference in d_a,
- you want to compare equal- vs. unequal-variance models via information criteria / cross-validation.

For metacognition specifically, the hierarchical Bayesian **HMeta-d** model is the field standard (see `metacognition.md`).

## 6. Tooling

### Python
- **`sdt.py` (bundled here):** rates + corrections, d'/c/c'/β, **SE/CI/significance of d'** (delta method), d_a/A_z and the **unequal-variance bias `c_a`**, **optimal criterion** (base rates + payoffs), least-squares z-ROC fitting **and a maximum-likelihood unequal-variance rating fit** (`fit_zroc_mle` — prefer it over the LS `fit_zroc` for real ROC work, since least squares on z-ROC points is biased), empirical AUC, and 2AFC conversion. Tested against analytic ground truth. Start here for point estimates and single-observer inference.
- **`sdt.R` (bundled here):** an R mirror of the same core (rates/corrections, d'/c/β, d_a, SE/CI/test of d', optimal criterion, z-ROC fit), producing **identical numbers** to `sdt.py`. Use whichever language your pipeline is in; for model-based work in R, graduate to `brms`/`sensR` below.
- **`scipy.stats.norm`:** `ppf` = z, `cdf` = Φ, `pdf` = φ (needed for the SE of d'). All you need for hand calculations.
- **`metadpy`** (Legrand; formerly `metadPy`): trial-level dataframe → SDT indices, plus meta-d' by MLE and hierarchical Bayesian meta-d' via PyMC/Numpyro. The standard Python metacognition package. `from metadpy.sdt import dprime, criterion, rates, roc_auc, scores`.
- **`statsmodels`** (`Probit`, `GEE`) or **`bambi`/`PyMC`** for probit GLM/GLMM and Bayesian SDT. `pingouin` has basic SDT helpers.
- **`scikit-learn`** `roc_auc_score`/`roc_curve` for empirical ROC/AUC (useful, but remember AUC alone is the sensitivity half only).

### R
- **`sensR`:** `SDT()` computes d' for any 2×J table via the empirical-probit transform, with `"probit"`/`"logit"` options; built for sensory-discrimination/Thurstonian tasks (2AFC, A-not-A, triangle, duo-trio).
- **`psycho`** (and the `report` ecosystem): `dprime()` with log-linear correction.
- **`brms`:** Bayesian probit/ordinal SDT as a GLMM (`bf(sayold ~ isold + (isold | subject) + (isold | item))`, `family = bernoulli("probit")`). The reference path for unequal-variance and hierarchical models.
- **`lme4`:** `glmer(..., family = binomial("probit"))` for frequentist GLMM-SDT.
- **`hmetad`** (R) / **HMeta-d** (MATLAB, now superseded by the R package): hierarchical Bayesian meta-d'.
- **`pROC`, `ROCR`:** empirical ROC/AUC and DeLong tests for AUC differences.

### Choosing
- One observer, lots of trials → plug-in (`sdt.py`).
- Rating data, want the variance assumption tested → fit the z-ROC (`fit_zroc`) or an ordinal-probit model.
- Multiple subjects/conditions/covariates → probit **GLMM** (frequentist) or Bayesian (`brms`/PyMC).
- Sparse per-subject data, metacognition → hierarchical Bayesian (HMeta-d / `metadpy`).
