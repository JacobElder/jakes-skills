# GLM: First-level, Second-level, Contrasts, Thresholding

This reference covers task fMRI analysis: estimating BOLD responses to stimuli via the General Linear Model, computing contrasts, and going from single-subject results to group-level inference.

## The full GLM pipeline at a glance

```
events.tsv ─┐
            ├──► design matrix ──► fit ──► compute_contrast ──► z-map ──► threshold ──► report
4D BOLD ────┤                        │
confounds ──┘                        └──► group: stack z-maps ──► SecondLevelModel ──► group z-map
```

## First-level model

The `FirstLevelModel` class fits a GLM at each voxel for one subject (one or more runs).

### Setup

```python
from nilearn.glm.first_level import FirstLevelModel

model = FirstLevelModel(
    t_r=2.0,                          # REQUIRED. Repetition time in seconds.
    hrf_model="glover + derivative",  # canonical HRF + time derivative
    drift_model="cosine",             # high-pass filter via cosine basis
    high_pass=1/128,                  # ~0.008 Hz; standard SPM default
    smoothing_fwhm=5.0,               # mm. Skip if already smoothed in preproc.
    noise_model="ar1",                # AR(1) prewhitening
    standardize=False,                # GLM does its own scaling
    signal_scaling=0,                 # per-voxel scaling for percent signal change
    minimize_memory=True,             # don't store residuals unless needed
    n_jobs=1,                         # parallelize across runs
)
```

Common `hrf_model` choices: `"glover"` (default, no derivatives), `"glover + derivative"` (HRF + temporal derivative — usually a good default), `"glover + derivative + dispersion"` (adds dispersion derivative — overkill in most cases), `"spm"`/`"spm + derivative"` (SPM-style HRF), `"fir"` (finite impulse response — no HRF assumption).

### Events DataFrame

The events DataFrame needs three columns:

```python
import pandas as pd
events = pd.DataFrame({
    "trial_type": ["face", "house", "face", "house", ...],
    "onset":      [10.0,   25.0,    40.0,   55.0,    ...],  # seconds from scan start
    "duration":   [5.0,    5.0,     5.0,    5.0,     ...],  # seconds
})
```

Duration of 0 = delta function (instantaneous event). Optional column: `modulation` for parametric modulators.

### Fit

```python
model.fit(
    "sub-01_task-faces_bold.nii.gz",
    events=events,
    confounds=confounds_df,   # optional; pandas DataFrame, one row per volume
)
```

For multi-run: pass lists of equal length.
```python
model.fit(
    [run1_img, run2_img, run3_img],
    events=[events1, events2, events3],
    confounds=[conf1, conf2, conf3],
)
```

After fit, the design matrix is available as `model.design_matrices_[0]` (one per run).

### Compute contrasts

```python
# By name — use the column name(s) from the design matrix
z_map = model.compute_contrast("face - house", output_type="z_score")

# By formula (multi-column)
z_map = model.compute_contrast("(face + scrambled_face) - (house + scrambled_house)",
                                output_type="z_score")

# By array (when you need explicit control)
import numpy as np
design_cols = model.design_matrices_[0].columns
contrast = np.zeros(len(design_cols))
contrast[design_cols.get_loc("face")] = 1
contrast[design_cols.get_loc("house")] = -1
z_map = model.compute_contrast(contrast, output_type="z_score")
```

`output_type` options:
- `"z_score"` — most common, normalized to z
- `"stat"` — raw t-statistic
- `"effect_size"` — beta estimate
- `"effect_variance"` — variance of the beta (need this for group-level fixed-effects)
- `"p_value"` — uncorrected p-value
- `"all"` — returns a dict with all of the above

Save the result:
```python
z_map.to_filename("face_vs_house_z.nii.gz")
```

### HTML report (highly recommended)

After fitting a first-level model, nilearn can generate an HTML report with the design matrix, contrast maps, glass-brain views, and tables of significant clusters. Use the model's `.generate_report()` method (since nilearn 0.13; the older standalone `make_glm_report` works but is deprecated for 0.15):

```python
report = model.generate_report(
    contrasts={"face - house": "face - house", "face": "face"},
    threshold=3.1,             # used only when height_control=None
    height_control=None,       # set to None if you want `threshold` to apply directly,
                               # OR set to "fpr"/"fdr"/"bonferroni" with alpha=
    alpha=0.001,
    cluster_threshold=15,
)
report.save_as_html("first_level_report.html")
```

**Important**: `threshold` and `height_control` interact. If `height_control` is `"fpr"` (default), `"fdr"`, or `"bonferroni"`, nilearn ignores your `threshold` and uses one derived from `alpha`. To use a manual threshold, set `height_control=None`.

## Building the design matrix manually

For finer control or to inspect what's happening:

```python
import numpy as np
from nilearn.glm.first_level import make_first_level_design_matrix

n_scans = 200
t_r = 2.0
frame_times = np.arange(n_scans) * t_r

design = make_first_level_design_matrix(
    frame_times,
    events=events,
    hrf_model="glover + derivative",
    drift_model="cosine",
    high_pass=1/128,
    add_regs=motion_confounds,           # numpy array of (n_scans, n_confounds)
    add_reg_names=["tx","ty","tz","rx","ry","rz"],
)
# design is a DataFrame: rows = volumes, columns = regressors

# Plot it
from nilearn.plotting import plot_design_matrix
plot_design_matrix(design, output_file="design_matrix.png")
```

Then pass directly:
```python
model.fit("bold.nii.gz", design_matrices=design)
```

## Thresholding for inference

Display threshold ≠ statistical threshold. For proper inference:

```python
from nilearn.glm import threshold_stats_img

# FDR correction
thresholded, threshold = threshold_stats_img(
    z_map,
    alpha=0.05,
    height_control="fdr",   # or "bonferroni" or "fpr"
    cluster_threshold=10,   # min voxels per cluster
    two_sided=True,
)
print(f"FDR-corrected threshold: z = {threshold:.2f}")
```

For non-parametric inference (recommended for small samples or non-normal data), see `non_parametric_inference` in `nilearn.glm.second_level`.

## Second-level (group) analysis

Group analysis takes per-subject contrast maps and tests them for consistency at the group level.

### One-sample t-test (group mean)

```python
from nilearn.glm.second_level import SecondLevelModel
import pandas as pd

# subject_z_maps is a list of paths or Nifti1Image objects, one per subject
# (use output_type="effect_size" at first level for the group analysis)
design = pd.DataFrame([1] * len(subject_z_maps), columns=["intercept"])

group_model = SecondLevelModel()
group_model.fit(subject_z_maps, design_matrix=design)

group_z = group_model.compute_contrast("intercept", output_type="z_score")
group_z.to_filename("group_face_vs_house_z.nii.gz")
```

### Two-sample t-test (e.g., patients vs controls)

```python
# 10 patients, 10 controls
design = pd.DataFrame({
    "patient": [1]*10 + [0]*10,
    "control": [0]*10 + [1]*10,
})
group_model = SecondLevelModel()
group_model.fit(all_subject_maps, design_matrix=design)
group_z = group_model.compute_contrast([1, -1], output_type="z_score")
```

### With covariates (age, sex, motion summary)

```python
design = pd.DataFrame({
    "intercept": [1]*n_subjects,
    "age": ages,            # demean before fitting
    "sex": sexes,           # coded 0/1 or -1/1
})
design["age"] -= design["age"].mean()
group_model = SecondLevelModel()
group_model.fit(all_subject_maps, design_matrix=design)
# Contrast for the group mean (intercept)
mean_z = group_model.compute_contrast([1, 0, 0], output_type="z_score")
# Contrast for the age effect
age_z = group_model.compute_contrast([0, 1, 0], output_type="z_score")
```

### Non-parametric inference

For small samples (n < ~20) or when distributional assumptions are dubious:
```python
from nilearn.glm.second_level import non_parametric_inference

neg_log_pvals = non_parametric_inference(
    subject_z_maps,
    design_matrix=design,
    second_level_contrast="intercept",
    n_perm=5000,
    two_sided_test=True,
    n_jobs=1,
)
# Threshold at -log10(0.05) ≈ 1.3
```

## Common pitfalls

**Contrast vector wrong length**: design matrices include drift terms and constants. If you build a contrast vector by hand, make sure its length matches `len(model.design_matrices_[0].columns)`, not just the number of conditions.

**Forgot t_r**: every fit will fail informatively, but if you guess wrong (e.g., 2.0 when actually 1.5), it'll silently fit a wrong model.

**Forgot confounds**: motion is the single biggest noise source. Always include at least 6 motion params for task data, and more (24 motion + WM/CSF + scrubbing) for resting-state.

**Smoothing twice**: if fMRIPrep was run with `--fwhm`, the data is already smoothed. Don't smooth again. Check by looking at one volume — heavily-smoothed data is visibly blurry.

**Mismatched events and runs**: when fitting multiple runs, `events[i]` must correspond to `imgs[i]`. Easy to misalign when iterating subjects.

**`first_level_from_bids` returns slice_time_ref**: it reads it from the BIDS sidecar. If the JSON has `SliceTimingCorrected: true`, set `slice_time_ref=0.5`; otherwise `0.0`. The helper does this automatically when sidecars are present.
