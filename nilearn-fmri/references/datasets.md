# Datasets, BIDS, and Atlases

This reference covers how to get fMRI data into a nilearn analysis: built-in demo fetchers, BIDS directories, fMRIPrep derivatives, raw NIfTI inputs, and atlases.

## Built-in dataset fetchers

These download a small public dataset and cache to `~/nilearn_data/`. First call downloads, subsequent calls reuse the cache. Use these whenever the user wants a demo or doesn't have their own data.

### Task fMRI (GLM-ready)

```python
from nilearn import datasets

# SPM auditory — single subject, single run, simple block design (audio vs rest)
# ~30MB; perfect for fast GLM examples
data = datasets.fetch_spm_auditory()
# data.func[0], data.anat[0] are NIfTI paths; events are not in BIDS form, see below
# This dataset's events need to be constructed manually:
import pandas as pd
events = pd.DataFrame({
    "trial_type": ["active"] * 8,
    "onset": list(range(6, 102, 12)),   # blocks every 12 scans of TR=7s
    "duration": [42] * 8,
})

# Language localizer demo — BIDS-formatted! Use first_level_from_bids
data = datasets.fetch_language_localizer_demo_dataset()
# data.data_dir is the BIDS root; has bold.nii, events.tsv, derivatives/

# Localizer first level — single subject button-pressing localizer
data = datasets.fetch_localizer_first_level()
# data.epi_img is the 4D BOLD; data.events is the events DataFrame
```

### Resting-state (connectivity-ready)

```python
# ADHD — 40 subjects, ~500MB if you take all; use n_subjects to limit
data = datasets.fetch_adhd(n_subjects=5)
# data.func: list of NIfTI paths
# data.confounds: list of confound TSVs (not fMRIPrep — has CompCor, motion, etc. precomputed)
# data.phenotypic: pandas DataFrame with diagnostic group, age, sex, etc.

# Development fMRI — children + adults watching a movie, downsampled to 4mm
# 155 subjects available; fast to load a few
data = datasets.fetch_development_fmri(n_subjects=10)
# data.func, data.confounds, data.phenotypic
```

### Decoding-ready

```python
# Haxby — single subject, 8 object categories shown across 12 runs
# ~310MB; the canonical MVPA dataset
data = datasets.fetch_haxby()
# data.func[0]: 4D BOLD path
# data.mask: brain mask
# data.mask_vt[0]: ventral temporal ROI mask
# data.session_target[0]: TSV with 'labels' (category) and 'chunks' (run number) per volume
```

### When to use which

| Need              | Dataset                              | Why                                |
|-------------------|--------------------------------------|------------------------------------|
| Quick GLM demo    | `fetch_spm_auditory`                 | Single run, simple block design    |
| BIDS GLM demo     | `fetch_language_localizer_demo_dataset` | Full BIDS structure incl. derivatives |
| Group GLM         | `fetch_localizer_contrasts` (16 subj)| Already-computed contrast maps     |
| Resting-state     | `fetch_adhd` or `fetch_development_fmri` | Multi-subject, with confounds  |
| Decoding          | `fetch_haxby`                        | Labeled, multi-class, multi-run    |

## BIDS datasets

If the user has a real BIDS directory (with or without fMRIPrep derivatives), use `first_level_from_bids`. It returns ready-to-fit models, the imgs, the events, and the confounds — all sliced per subject.

```python
from nilearn.glm.first_level import first_level_from_bids

models, imgs, events, confounds = first_level_from_bids(
    dataset_path="/path/to/bids/root",
    task_label="languagelocalizer",       # required, must match BIDS
    space_label="MNI152NLin2009cAsym",    # required if using fMRIPrep derivatives
    img_filters=[("desc", "preproc")],    # filter fMRIPrep outputs to preproc images
    derivatives_folder="derivatives/fmriprep",
    n_jobs=1,
    verbose=1,
)
# models[i] is a FirstLevelModel with t_r, slice_time_ref etc. populated from sidecar JSON
# imgs[i], events[i], confounds[i] are the matched inputs for subject i
```

Then fit per subject:
```python
for model, img, event_df, conf_df in zip(models, imgs, events, confounds):
    model.fit(img, events=event_df, confounds=conf_df)
```

## fMRIPrep confounds

Never read the fMRIPrep confounds TSV by hand. Column names change across fMRIPrep versions, and selecting the right ones is fiddly. Use the official loader:

```python
from nilearn.interfaces.fmriprep import load_confounds, load_confounds_strategy

# High-level: pick a named strategy
confounds, sample_mask = load_confounds_strategy(
    "/path/to/sub-01_task-rest_desc-preproc_bold.nii.gz",
    denoise_strategy="simple",   # other options: "scrubbing", "compcor", "ica_aroma"
)

# Low-level: pick exactly what you want
confounds, sample_mask = load_confounds(
    "/path/to/sub-01_task-rest_desc-preproc_bold.nii.gz",
    strategy=["motion", "wm_csf", "global_signal"],
    motion="basic",       # "basic" = 6 params; "derivatives" = +6; "full" = +12 (24 total)
    wm_csf="basic",
    global_signal="basic",
)
```

`sample_mask` is None unless scrubbing is requested — if not None, pass it to the model's `.fit(..., sample_masks=sample_mask)` to drop high-motion volumes.

## Raw NIfTI + events workflow

If the user has just `.nii.gz` and a TSV (or pandas DataFrame) of events, no BIDS structure:

```python
import pandas as pd
from nilearn.glm.first_level import FirstLevelModel

events = pd.read_csv("events.tsv", sep="\t")
# Required columns: trial_type, onset, duration (all in seconds)

model = FirstLevelModel(
    t_r=2.0,                         # MUST be set; read from sidecar or scanner
    hrf_model="glover + derivative", # default "glover" is fine for most cases
    drift_model="cosine",            # high-pass via cosine basis
    high_pass=0.01,                  # Hz, ~100s period
    smoothing_fwhm=5,                # mm; skip if already smoothed
    standardize=False,               # let GLM handle scaling
    noise_model="ar1",
)
model.fit("bold.nii.gz", events=events)
```

If TR is unknown, read from the NIfTI header:
```python
import nibabel as nib
t_r = float(nib.load("bold.nii.gz").header.get_zooms()[3])
```

## Atlases

Atlases parcellate the brain into ROIs for connectivity, ROI-based decoding, or visualization. Two types:

**Deterministic (label) atlases** — each voxel belongs to one parcel. Use `NiftiLabelsMasker`.

```python
# Harvard-Oxford cortical, 48 regions
ho = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
# ho.maps: 3D NIfTI of integer labels; ho.labels: list of region names

# Schaefer 2018, 7 networks, 400 parcels (popular for connectivity)
schaefer = datasets.fetch_atlas_schaefer_2018(n_rois=400, yeo_networks=7, resolution_mm=2)
# schaefer.maps, schaefer.labels

# AAL
aal = datasets.fetch_atlas_aal()
# aal.maps, aal.labels, aal.indices

# Yeo 2011 networks (7 or 17)
yeo = datasets.fetch_atlas_yeo_2011()
# yeo.thick_7, yeo.thin_7, yeo.thick_17, yeo.thin_17 are the maps
```

**Probabilistic atlases** — each voxel has a weight per network. Use `NiftiMapsMasker`.

```python
# MSDL — 39 functional networks
msdl = datasets.fetch_atlas_msdl()
# msdl.maps: 4D NIfTI; msdl.labels; msdl.region_coords

# DiFuMo — fine-grained probabilistic, choose 64/128/256/512/1024 components
difumo = datasets.fetch_atlas_difumo(dimension=64, resolution_mm=2)
# difumo.maps (4D), difumo.labels (DataFrame)

# Smith 2009 ICA atlas — canonical resting-state networks
smith = datasets.fetch_atlas_smith_2009()
# smith.rsn10: 10 RSNs, 4D NIfTI
```

## When the fetchers can't reach the network

In sandboxed environments (e.g., some agentic execution sandboxes), the dataset fetchers fail with SSL or connection errors because nilearn's CDN hosts (e.g., `www.fil.ion.ucl.ac.uk`, `osf.io`, `www.nitrc.org`) aren't on the allowlist. If a `fetch_*` call fails with `host_not_allowed`, `SSLCertVerificationError`, or `MaxRetryError`:

1. Check whether the user already has data locally and was just naming a familiar dataset by reflex. Ask.
2. If they truly need demo data and there's no internet, generate small synthetic NIfTIs (a brain-shaped mask of Gaussian blobs, random + block-design signal) that exercise the same APIs. See `evals/files/make_fixtures.py` in the skill for a template.
3. Tell the user the fetcher failed and explain the workaround — don't silently substitute data.

## Common pitfalls

**Atlas in wrong space**: many atlases ship in 2mm MNI. If the user's data is in 3mm or a different template, resample:
```python
from nilearn.image import resample_to_img
atlas_resampled = resample_to_img(
    atlas.maps, fmri_img,
    interpolation="nearest",   # for label atlas; use "continuous" for probabilistic
    force_resample=True
)
```
A `NiftiLabelsMasker` will also try to resample automatically when fitted, so often this isn't needed explicitly. But if you see "shapes don't match" errors, this is the fix.

**First call is slow**: dataset fetchers download on first call. Mention this to the user if they look surprised by a long pause.

**Cache location**: default is `~/nilearn_data/`. Override with `data_dir=` arg if disk space is a concern.
