# Functional Connectivity

Extracting timeseries from brain regions and computing how they relate. Works for resting-state (no task) and task-based fMRI alike.

## The pipeline

```
4D BOLD ──┐
          ├─► masker (atlas or seed) ──► n_volumes × n_regions timeseries
confounds ┘                                   │
                                              ▼
                            ConnectivityMeasure ──► n_regions × n_regions matrix
                                              │
                                              ▼
                                    plot_matrix / plot_connectome
```

## Step 1: Choose a masker

Maskers extract timeseries from regions. Three kinds based on the atlas/region type:

### NiftiLabelsMasker — for deterministic atlases (Harvard-Oxford, Schaefer, AAL)

```python
from nilearn.maskers import NiftiLabelsMasker
from nilearn import datasets

atlas = datasets.fetch_atlas_schaefer_2018(n_rois=400, yeo_networks=7)

masker = NiftiLabelsMasker(
    labels_img=atlas.maps,
    labels=atlas.labels,
    standardize="zscore_sample",   # IMPORTANT: use the string, not True (deprecated)
    detrend=True,
    low_pass=0.1,                  # Hz; standard for resting-state
    high_pass=0.01,                # Hz
    t_r=2.0,                       # REQUIRED if filtering
    memory="nilearn_cache",        # speeds up repeated fits
    verbose=1,
)
```

### NiftiMapsMasker — for probabilistic atlases (MSDL, DiFuMo, Smith)

```python
from nilearn.maskers import NiftiMapsMasker

atlas = datasets.fetch_atlas_msdl()

masker = NiftiMapsMasker(
    maps_img=atlas.maps,
    standardize="zscore_sample",
    detrend=True,
    low_pass=0.1,
    high_pass=0.01,
    t_r=2.0,
    verbose=1,
)
```

### NiftiSpheresMasker — for seed-based (custom ROI coordinates)

```python
from nilearn.maskers import NiftiSpheresMasker

# E.g., DMN seeds (MNI coords)
seeds = [(0, -52, 18), (-46, -68, 32), (46, -68, 32), (1, 50, -5)]

masker = NiftiSpheresMasker(
    seeds=seeds,
    radius=8,                       # mm
    standardize="zscore_sample",
    detrend=True,
    low_pass=0.1,
    high_pass=0.01,
    t_r=2.0,
)
```

### NiftiMasker — for whole-brain or arbitrary mask (voxel-level)

```python
from nilearn.maskers import NiftiMasker

masker = NiftiMasker(
    mask_img="brain_mask.nii.gz",  # or mask_strategy="background" / "epi"
    standardize="zscore_sample",
    detrend=True,
    smoothing_fwhm=6,
    t_r=2.0,
)
```

## Step 2: Extract timeseries

```python
timeseries = masker.fit_transform(
    "sub-01_task-rest_bold.nii.gz",
    confounds=confounds_df,   # pandas DataFrame, one row per volume
    sample_mask=sample_mask,  # optional: indices of volumes to keep
)
# Shape: (n_volumes, n_regions)
```

For fMRIPrep data, get confounds via `load_confounds_strategy`:
```python
from nilearn.interfaces.fmriprep import load_confounds_strategy
confounds, sample_mask = load_confounds_strategy(
    "sub-01_task-rest_desc-preproc_bold.nii.gz",
    denoise_strategy="simple",
)
timeseries = masker.fit_transform(img, confounds=confounds, sample_mask=sample_mask)
```

For multi-subject use the `Multi*` variants (`MultiNiftiLabelsMasker`, `MultiNiftiMapsMasker`) which parallelize:
```python
from nilearn.maskers import MultiNiftiLabelsMasker
multi = MultiNiftiLabelsMasker(labels_img=atlas.maps, standardize="zscore_sample",
                                t_r=2.0, n_jobs=4)
all_timeseries = multi.fit_transform(list_of_imgs, confounds=list_of_confounds_dfs)
# Returns a list of (n_volumes, n_regions) arrays
```

## Step 3: Compute connectivity

```python
from nilearn.connectome import ConnectivityMeasure

measure = ConnectivityMeasure(
    kind="correlation",         # see options below
    standardize="zscore_sample",
)

# For a single subject
matrix = measure.fit_transform([timeseries])[0]  # note the list wrapping; fit_transform expects multi-subject

# For many subjects
matrices = measure.fit_transform(all_timeseries)
# Shape: (n_subjects, n_regions, n_regions)
```

`kind` options:
- `"correlation"` — Pearson correlation (most common, easy to interpret)
- `"partial correlation"` — controls for all other regions (more conservative)
- `"covariance"` — raw covariance
- `"precision"` — inverse covariance (sparse inverse covariance estimation; identifies direct connections)
- `"tangent"` — projects covariance matrices to the tangent space at the group geometric mean. **Diagonal elements are approximately zero** (unlike correlation/covariance where diagonal=1 or variance). Recommended for downstream ML on connectivity matrices because it removes the mean structure and is better-conditioned. Only meaningful when computed across many subjects (needs a group to define the reference point). The returned matrices look very different from correlation matrices — off-diagonal values are typically small and the sign has a different interpretation.

## Step 4: Visualize

### Matrix plot

```python
import numpy as np
from nilearn import plotting

# Zero out the diagonal for visibility
np.fill_diagonal(matrix, 0)
plotting.plot_matrix(
    matrix,
    labels=atlas.labels,
    vmax=0.8, vmin=-0.8,
    reorder=True,            # cluster-reorder rows/columns
    figure=(10, 10),
)
```

### Connectome on a glass brain

```python
# Need ROI coordinates
from nilearn.plotting import find_parcellation_cut_coords, plot_connectome

coords = find_parcellation_cut_coords(atlas.maps)   # for label atlases
# OR for probabilistic atlases:
# from nilearn.plotting import find_probabilistic_atlas_cut_coords
# coords = find_probabilistic_atlas_cut_coords(atlas.maps)

plot_connectome(
    matrix,
    coords,
    edge_threshold="95%",    # show top 5% of edges by absolute value
    title="Functional connectome",
    output_file="connectome.png",
)
```

### Interactive connectome (HTML)

```python
view = plotting.view_connectome(matrix, coords, edge_threshold="95%")
view.save_as_html("connectome_interactive.html")
```

## Seed-based connectivity maps

To make a whole-brain map showing voxels correlated with a seed timeseries:

```python
from nilearn.maskers import NiftiSpheresMasker, NiftiMasker
import numpy as np

# Extract seed timeseries
seed_masker = NiftiSpheresMasker(
    seeds=[(0, -52, 18)],  # posterior cingulate (DMN hub)
    radius=8,
    standardize="zscore_sample",
    t_r=2.0, low_pass=0.1, high_pass=0.01,
)
seed_ts = seed_masker.fit_transform(img, confounds=confounds_df)  # (n_vols, 1)

# Extract whole-brain timeseries
brain_masker = NiftiMasker(
    standardize="zscore_sample", smoothing_fwhm=6,
    t_r=2.0, low_pass=0.1, high_pass=0.01,
)
brain_ts = brain_masker.fit_transform(img, confounds=confounds_df)  # (n_vols, n_voxels)

# Correlate
seed_to_brain = (np.dot(brain_ts.T, seed_ts) / seed_ts.shape[0]).squeeze()

# Inverse transform to NIfTI
seed_map = brain_masker.inverse_transform(seed_to_brain.T)
seed_map.to_filename("dmn_seed_map.nii.gz")

# Plot
plotting.plot_stat_map(seed_map, threshold=0.3, title="DMN seed connectivity")
```

## Common pitfalls

**Forgot to filter**: resting-state needs bandpass filtering (~0.01–0.1 Hz). Either do it in the masker (`low_pass`, `high_pass`, `t_r` together) or beforehand. If you set `low_pass`/`high_pass`, you MUST set `t_r` or you get a meaningless filter.

**Confounds order matters**: `confounds` must be a DataFrame with one row per BOLD volume, in the same order. If you got confounds from `load_confounds`, they're already aligned. If you read them by hand, double-check `len(confounds) == img.shape[3]`.

**Sparse inverse covariance with too few subjects**: `kind="precision"` is sensitive to small n. With <30 subjects, prefer `"partial correlation"` or use `tangent` then move to a downstream model.

**Tangent space requires multiple subjects**: it fits a reference point on the manifold from the group. Running it on a single subject is meaningless — use `"correlation"` or `"partial correlation"` instead.

**Diagonal dominates matrix plots**: always zero or NaN the diagonal before `plot_matrix`, or the colormap gets crushed by the 1.0s on the diagonal.

**Coordinates for connectome plots**: `plot_connectome` needs (x, y, z) MNI coordinates for each ROI. `find_parcellation_cut_coords` is for deterministic atlases, `find_probabilistic_atlas_cut_coords` for probabilistic. Both return arrays of shape (n_regions, 3).

**Atlas resampling — required when affines differ**: if the atlas is at a different resolution than the BOLD (e.g., atlas at 2mm, BOLD at 4mm), you must resample before masking:

```python
from nilearn.image import resample_to_img

atlas_resampled = resample_to_img(
    atlas_img, bold_img,
    interpolation="nearest",   # REQUIRED for label atlases — nearest-neighbor preserves integer labels
)
masker = NiftiLabelsMasker(labels_img=atlas_resampled, ...)
```

Use `interpolation="nearest"` for discrete label atlases. Using `"continuous"` or `"linear"` will corrupt the integer labels into fractional values and yield garbage region assignments. For probabilistic atlases use `"continuous"`.

While `NiftiLabelsMasker` will attempt auto-resampling, it can silently fail or produce wrong results when the affine difference is large. Explicit pre-resampling is safer and faster for multi-subject loops.
