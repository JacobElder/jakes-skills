# Decoding / MVPA

Multi-Voxel Pattern Analysis: predicting a label (or value) from a brain image. Nilearn's `Decoder` wraps masking, feature selection, cross-validation, and a sklearn classifier into one pipeline.

## When to use which

| Task                                 | Tool                           |
|--------------------------------------|--------------------------------|
| Classify discrete labels             | `nilearn.decoding.Decoder`     |
| Predict continuous value             | `nilearn.decoding.DecoderRegressor` |
| Sparse multivariate (graph-net, TV-L1) | `SpaceNetClassifier` / `SpaceNetRegressor` |
| Searchlight (mapping where info lives) | `nilearn.decoding.SearchLight` |
| Encoding model (predict brain from stimulus) | manual; nilearn provides the masker |

## Basic Decoder

The Decoder fits a sklearn-style classifier to brain images. Inputs are typically:
- a 4D NIfTI where each volume corresponds to one trial/sample, OR
- a list of 3D NIfTIs (e.g., beta maps from a per-trial GLM)
- a list of labels of equal length
- optionally, "groups" (e.g., run number) to enforce cross-validation across runs

### Classification example (Haxby — face vs house)

```python
from nilearn import datasets
from nilearn.decoding import Decoder
from nilearn.image import index_img
import pandas as pd

haxby = datasets.fetch_haxby()
fmri_img = haxby.func[0]
mask_img = haxby.mask_vt[0]   # ventral temporal cortex ROI

# Load labels
behavioral = pd.read_csv(haxby.session_target[0], sep=" ")
conditions = behavioral["labels"]
runs = behavioral["chunks"]

# Restrict to two conditions
mask_condition = conditions.isin(["face", "house"])
fmri_subset = index_img(fmri_img, mask_condition.values)
conditions_subset = conditions[mask_condition].values
runs_subset = runs[mask_condition].values

# Set up cross-validation: leave-one-run-out
from sklearn.model_selection import LeaveOneGroupOut
cv = LeaveOneGroupOut()

decoder = Decoder(
    estimator="svc",                  # 'svc', 'svc_l1', 'logistic', 'logistic_l1', 'ridge_classifier', 'dummy_classifier'
    mask=mask_img,
    cv=cv,
    scoring="accuracy",               # 'roc_auc' (binary only), 'accuracy', 'f1', etc.
    screening_percentile=5,           # ANOVA-based feature selection: top 5% of voxels
    standardize="zscore_sample",
    smoothing_fwhm=4,
    n_jobs=1,
)

decoder.fit(fmri_subset, conditions_subset, groups=runs_subset)

# Inspect per-fold scores
import numpy as np
for label, scores in decoder.cv_scores_.items():
    print(f"{label}: mean={np.mean(scores):.3f}, scores={[f'{s:.2f}' for s in scores]}")

# Predict on new data
preds = decoder.predict(some_fmri_img)
```

### Regression example

```python
from nilearn.decoding import DecoderRegressor

decoder = DecoderRegressor(
    estimator="ridge",      # 'ridge', 'svr', 'lasso', 'dummy_regressor'
    mask=mask_img,
    cv=5,                   # plain k-fold; pass a sklearn CV object for more control
    scoring="r2",           # or 'neg_mean_absolute_error', 'neg_mean_squared_error'
    screening_percentile=20,
    standardize="zscore_sample",
)
decoder.fit(fmri_imgs, continuous_target_values)
```

## Anatomy of what Decoder does under the hood

1. **Mask** — `NiftiMasker` (or `NiftiLabelsMasker`/etc. if you pass one) extracts voxel timeseries.
2. **Feature selection** — `SelectPercentile` with `f_classif`/`f_regression` keeps the top `screening_percentile`% by univariate ANOVA. Done within each CV fold to avoid leakage.
3. **Standardize** — z-score features per fold.
4. **Fit estimator** — your chosen sklearn estimator. For 'svc' / 'logistic' it does a grid search over C.
5. **Cross-validate** — fits across folds, stores per-fold scores in `decoder.cv_scores_`.
6. **Average weight map** — averages the model's coefs across folds and inverse-transforms to a NIfTI, available as `decoder.coef_img_`.

## Inspecting and visualizing results

```python
# Per-class weight map (one per class for multiclass)
weight_img = decoder.coef_img_["face"]  # for multiclass; for binary use first class
weight_img.to_filename("face_weights.nii.gz")

# Plot it
from nilearn.plotting import plot_stat_map
plot_stat_map(weight_img, title="Face weights", threshold=1e-4,
              output_file="face_weights.png")
```

```python
# Score against chance
chance_level = 1.0 / len(np.unique(conditions_subset))
mean_acc = np.mean(list(decoder.cv_scores_.values())[0])
print(f"Accuracy: {mean_acc:.3f} (chance: {chance_level:.3f})")

# Permutation test for significance
from sklearn.model_selection import permutation_test_score
# (use a plain sklearn pipeline for permutation, since Decoder doesn't expose this directly)
```

## ROI vs whole-brain

**ROI-based** — pass a specific mask:
```python
decoder = Decoder(estimator="svc", mask=ventral_temporal_mask, ...)
```

**Whole-brain** — pass the brain mask (or omit and let it auto-compute):
```python
decoder = Decoder(estimator="svc", mask=brain_mask,
                  screening_percentile=5,   # crucial: don't try to fit ~200k voxels
                  ...)
```

For whole-brain decoding, `screening_percentile` is essential to keep computation tractable and to avoid overfitting. 5–20% is typical.

## Searchlight: where does the information live?

Searchlight slides a small sphere across the brain, fitting a classifier in each, mapping decoding accuracy as a brain map.

```python
from nilearn.decoding import SearchLight
from sklearn.model_selection import KFold

searchlight = SearchLight(
    mask_img=mask_img,
    radius=5.6,                    # mm
    estimator="svc",
    cv=KFold(n_splits=4),
    scoring="accuracy",
    n_jobs=4,                      # parallelize — searchlight is slow
    verbose=1,
)
searchlight.fit(fmri_imgs, labels)
# searchlight.scores_ is a 3D array of accuracies; wrap into NIfTI:
from nilearn.image import new_img_like
score_img = new_img_like(mask_img, searchlight.scores_)
score_img.to_filename("searchlight_accuracy.nii.gz")
```

**Searchlight is slow** — easily 30+ minutes on a single subject for whole-brain. Restrict to an ROI mask or downsample. Always check `n_jobs` is set high if you have cores.

## Best practices for decoding

**Cross-validate across runs**, not within. Within-run CV inflates accuracy because consecutive volumes are temporally correlated. Use `LeaveOneGroupOut` with `groups=runs`.

**Always report chance level** alongside accuracy. 60% sounds great until you mention it's a 4-class problem (chance = 25%) vs a binary problem (chance = 50%).

**Use beta maps, not raw BOLD volumes**, when possible. Beta maps from a least-squares-separate (LSS) per-trial GLM are cleaner than picking a single BOLD volume per trial. This requires fitting many small GLMs (one per trial) — see nilearn's "Beta-Series Modeling" examples.

**Don't interpret weight maps as activation maps**. The Decoder's `coef_img_` shows which voxels the classifier relies on, not which voxels are "active". A voxel can have a large weight because it's noisy and the classifier uses it to subtract noise from a different voxel (Haufe et al. 2014). For interpretable maps, transform the weights: `cov(X) @ weights` (the "activation pattern" formulation).

**Mind class imbalance**. If you have 80% class A and 20% class B, accuracy is a misleading metric — use `scoring="roc_auc"` (binary) or `"f1_macro"` (multiclass).

**Standardize the right way**: `standardize="zscore_sample"` (current) vs `standardize=True` (deprecated, removed in 0.15).

## Common pitfalls

**Group leakage**: passing `groups=` to `Decoder.fit` is necessary if your CV scheme is group-based. Without it, the LeaveOneGroupOut just won't work correctly.

**Mask too small / too big**: if the mask is one ROI but you ask for `screening_percentile=5` on a tiny mask, you might get just a handful of voxels. If it's whole-brain without screening, fitting takes forever and overfits.

**Trial-vs-volume confusion**: if your input is a 4D BOLD, each TR is a sample, and you need TR-by-TR labels (which is usually wrong — BOLD lags 4–6s after stimulus). Better: use per-trial beta maps so one sample = one trial.

**Wrong scoring metric**: `roc_auc` only works for binary; multiclass needs `"roc_auc_ovr"` or `"accuracy"` or `"f1_macro"`. Mismatched metric throws cryptic errors.
