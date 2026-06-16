# Type-2 SDT and Metacognition (meta-d', M-ratio, HMeta-d)

Standard ("type-1") SDT asks how well an observer tells signal from noise. **Type-2 SDT** asks a different question: how well do an observer's *confidence ratings* track whether their own type-1 decision was right? That's metacognitive sensitivity — the ability to know when you're likely correct. It's central to consciousness research, confidence calibration, and any "do people know what they know" question.

## The key distinction

- **Type-1 sensitivity (d'):** discriminating signal from noise.
- **Type-2 sensitivity:** discriminating one's own *correct* responses from *incorrect* ones, using confidence.

These are not the same and don't have to move together: a person can be highly accurate (high d') yet poorly calibrated (confidence doesn't track accuracy), or vice versa.

## Why raw confidence–accuracy correlations are the wrong tool

The tempting move — correlate confidence with accuracy (Goodman–Kruskal gamma, phi, point-biserial) — is **confounded by type-1 performance and by response/confidence bias**. Two observers with identical metacognitive ability but different d' (or different overall confidence) will show different gamma. So a difference in confidence–accuracy correlation across groups can be entirely an artifact of type-1 differences. Don't report gamma as "metacognition."

## meta-d' (Maniscalco & Lau 2012)

The fix: express metacognitive sensitivity in the *same units* as type-1 d'. **meta-d'** is defined as the type-1 d' that a metacognitively *ideal* observer would need in order to produce the confidence-rating data you actually observed, given the observed type-1 criteria. It's estimated from the type-2 ROC (built by sweeping confidence thresholds), but reported on the type-1 d' scale.

Because meta-d' and d' share units, you can compare them directly:

- **M-ratio = meta-d' / d'** — *metacognitive efficiency*. M-ratio = 1 means metacognition is as good as the type-1 information allows (ideal). M-ratio < 1 means the observer is *not* using all the available evidence in their confidence (inefficient metacognition). M-ratio > 1 is possible but usually signals a model violation or noise.
- **meta-d' − d'** — the difference-score alternative to the ratio. Less scale-dependent in some regimes; the ratio is more common.

Crucially, meta-d' controls for both type-1 performance and response bias by construction, which is exactly what gamma fails to do.

## HMeta-d (Fleming 2017): hierarchical Bayesian estimation

Point-estimating meta-d' per subject needs a lot of trials and is unstable with sparse data (e.g., patient populations). **HMeta-d** estimates meta-d'/M-ratio in a hierarchical Bayesian framework, pooling information across subjects:

- More robust with limited per-subject data; returns full posteriors (credible intervals), not just points.
- Avoids the edge-correction confounds that plague the MLE version.
- Supports group comparisons and regressing M-ratio on covariates at the group level.

Tooling: the original MATLAB toolbox (`metacoglab/HMeta-d`, JAGS-based) is **now superseded by the R package `hmetad`**. In Python, **`metadpy`** implements both MLE meta-d' (`metadpy.mle.metad`) and hierarchical Bayesian meta-d' (`metadpy.bayesian.hmetad`, via PyMC/Numpyro).

## Caveats and model assumptions

- meta-d' assumes a **specific generative model** of confidence (equal-variance type-1 distributions by default; Maniscalco & Lau's `fit_meta_d_MLE` allows a free variance ratio). Like all SDT, the model can be wrong; report the assumption.
- The standard model needs a **2-choice task with a confidence scale** (an S1/S2 × confidence matrix). For **N-alternative** tasks where that structure doesn't hold, use the **area under the type-2 ROC (AUROC2)** as a bias-free metacognitive-sensitivity measure (Fleming & Lau 2014) instead of meta-d'.
- Need enough confidence levels actually used; if subjects only ever say "high confidence," the type-2 ROC is degenerate.
- M-ratio is noisy with few trials — prefer the hierarchical Bayesian estimate, and never over-interpret a single subject's point M-ratio.

## Minimal workflow

1. Collect type-1 responses + confidence ratings per trial.
2. Build the S1/S2 × confidence response-count matrix (per subject).
3. Fit meta-d' (MLE for a quick look; hierarchical Bayesian for inference, especially with sparse data).
4. Report d', meta-d', and M-ratio (with intervals), plus the assumption status.
5. Interpret: "type-1 sensitivity d' = 1.8; metacognitive efficiency M-ratio = 0.7 — confidence captured ~70% of the available evidence, indicating sub-ideal but typical metacognition."
