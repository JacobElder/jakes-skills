---
name: nilearn-fmri
description: Run fMRI analyses with nilearn — GLM (first-level and group-level task fMRI), functional connectivity (resting-state, connectomes, ROI-to-ROI), decoding/MVPA, and brain visualization & reporting. Use this skill whenever the user mentions fMRI, BOLD, NIfTI files, BIDS datasets, fMRIPrep outputs, brain imaging analysis, GLM, contrasts, design matrices, HRF, functional connectivity, connectomes, parcellations, resting-state, MVPA, decoding, or asks to plot brain maps or generate neuroimaging reports — even if they don't name nilearn explicitly. Also use when the user wants to learn nilearn workflows on demo data (Haxby, ADHD, development_fmri, SPM auditory, language localizer, etc.) without bringing their own.
---

# nilearn fMRI Analysis

Help users run reproducible fMRI analyses with [nilearn](https://nilearn.github.io). nilearn covers four core workflows that this skill orchestrates:

1. **GLM** — task fMRI: design matrices, first-level models, contrasts, group (second-level) analysis, thresholding, HTML reports
2. **Functional connectivity** — resting-state and task: timeseries extraction with maskers, atlas-based connectomes, seed-based maps, ROI-to-ROI matrices
3. **Decoding / MVPA** — classify or regress on brain images with the `Decoder` family; searchlight; cross-validation
4. **Visualization & reporting** — `plot_stat_map`, `plot_glass_brain`, `plot_connectome`, interactive views, and full HTML GLM reports

nilearn does **not** preprocess raw scanner data. It assumes preprocessing is done (typically by fMRIPrep). The skill explicitly checks input data state before proceeding.

## Workflow

Follow this order on every task. Don't skip the "Identify inputs" step — silently guessing what data the user has is the #1 source of wrong analyses.

### 1. Identify what the user actually has

Ask or infer from the message which of these the user is starting from:

- **A built-in nilearn dataset** — the user is learning, demoing, or doesn't have their own data. They'll say "show me how to…", "use the Haxby dataset", "I want to try…". → see `references/datasets.md` for fetcher signatures.
- **A BIDS dataset** (often with fMRIPrep derivatives) — a directory with `sub-XX/func/...nii.gz` and `events.tsv` files, possibly a `derivatives/fmriprep/` subfolder. → use `first_level_from_bids` and `load_confounds`. See `references/datasets.md` and `references/glm.md`.
- **Raw NIfTI paths + events** — the user hands you `.nii.gz` paths and possibly a TSV of events. → build a design matrix manually with `make_first_level_design_matrix`. See `references/glm.md`.
- **Already-extracted timeseries or beta maps** — the user has done the GLM elsewhere and wants connectivity, decoding, or plotting. → skip to the relevant reference.

If the user is vague, ask ONE clarifying question. Don't ask three.

### 2. Choose the workflow

Map the request to one of the four workflows above. If the request spans two (e.g., "first-level GLM then group analysis", or "extract DMN timeseries and decode"), do them in sequence — first-level before group, connectivity extraction before decoding, etc.

### 3. Read the relevant reference file(s)

Each reference is a focused, currently-accurate API guide with runnable code patterns. Read the ones for the workflow at hand before writing code:

- `references/datasets.md` — built-in fetchers, BIDS handling, fMRIPrep confounds, atlases
- `references/glm.md` — first-level, second-level, design matrices, contrasts, thresholding
- `references/connectivity.md` — maskers, ConnectivityMeasure, seed-based, ROI-to-ROI
- `references/decoding.md` — Decoder, DecoderRegressor, cross-validation, searchlight
- `references/visualization.md` — static plots, interactive views, HTML reports

### 4. Use the bundled scripts when applicable

For common end-to-end tasks, `scripts/` contains parameterized helpers that have been tested. Prefer these over writing from scratch — they handle edge cases (e.g., `standardize="zscore_sample"` for the new API, resampling atlases to data space, sensible defaults for `t_r`/`high_pass`):

- `scripts/run_first_level_glm.py` — fit a first-level GLM, compute contrasts, save z-maps + report
- `scripts/run_second_level_glm.py` — group-level analysis from a list of first-level contrast maps
- `scripts/extract_connectome.py` — atlas → timeseries → connectivity matrix → plot
- `scripts/run_decoder.py` — `Decoder` with cross-validation and weight-map output
- `scripts/make_report.py` — HTML GLM report from a fitted model

Each script has `--help`. They're meant to be edited; copy and adapt rather than treating them as black boxes.

### 5. Produce a reproducible deliverable

Every analysis should produce: (a) the result files (NIfTI maps, matrices as `.npy` or `.csv`, plots as `.png` or `.html`), (b) a short text summary of what was done with the key parameters (TR, smoothing, threshold, atlas, classifier, CV scheme), and (c) the analysis script if not using a bundled one. This is non-negotiable — fMRI results without documented parameters are not interpretable.

## Important conventions and gotchas

These come up constantly and are worth holding in mind.

**Standardize argument**: in nilearn ≥0.13, pass `standardize="zscore_sample"` (string) to maskers and the `Decoder`, not `standardize=True` (which is deprecated and removed in 0.15). Old examples on the web use `True` — update them.

**TR (repetition time)**: every GLM and many maskers need `t_r`. If the user doesn't know it, look in the NIfTI header (`nibabel.load(img).header.get_zooms()[3]`) or the BIDS sidecar JSON. Don't make one up.

**Affine and shape mismatches**: if you see "Images have different affines" or "shapes don't match", the atlas and the functional data are in different spaces. Use `nilearn.image.resample_to_img(atlas, fmri, interpolation='nearest')` for label atlases, `'continuous'` for probabilistic ones.

**Confounds for fMRIPrep**: use `nilearn.interfaces.fmriprep.load_confounds` or `load_confounds_strategy("simple")`. Don't try to read the confounds TSV by hand — the columns are inconsistent across fMRIPrep versions and `load_confounds` handles that.

**Memory**: nilearn caches via `joblib.Memory`. For repeated analyses, pass `memory="nilearn_cache"` to maskers and decoders. For one-off scripts, skip it.

**Thresholding**: `plot_stat_map` takes a `threshold` argument but doesn't do statistical correction. For proper inference, use `nilearn.glm.threshold_stats_img(z_map, alpha=0.05, height_control="fdr")` or `"bonferroni"` or cluster-level control.

**Don't fabricate file paths**: if the user hasn't given you a path, don't invent one. Use the built-in fetchers (which write to `~/nilearn_data/`) or ask.

## Output style

Default to producing both code and a brief written explanation. fMRI users span newcomers to experts; the written explanation lets newcomers understand what's happening without slowing experts down. Keep it short — a few sentences per analytic step, not a lecture.

When a workflow produces images (z-maps, connectivity matrices, glass brains), save them and call `present_files` so the user can actually see them. A nilearn analysis without visible output is not done.

When in doubt about whether to surface technical details (e.g., the exact contrast vector, the cross-validation splits, the FDR threshold value), include them. Reproducibility wins over brevity.
