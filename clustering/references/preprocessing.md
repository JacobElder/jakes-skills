# Preprocessing and Distance

The thesis of this skill: **preprocessing and the distance metric change your clustering
results more than the choice of algorithm.** This file is where most of the leverage
actually is. If clusters look wrong, the cause is here far more often than in the
algorithm.

## Contents

- [Scaling — almost always required](#scaling)
- [Distance metrics — match the data and the geometry](#distance)
- [Categorical and mixed data](#categorical-mixed)
- [Dimensionality and the curse](#dimensionality)
- [Outliers](#outliers)
- [A preprocessing checklist](#checklist)

---

## Scaling

Distance-based clustering (which is almost all of it) treats features as commensurable.
If one feature is income in dollars (range 0–500,000) and another is age in years (0–100),
Euclidean distance is **dominated entirely by income** — you're clustering on income and
pretending age matters. This single oversight produces more "bad clusters" than any
algorithm flaw.

- **Standardize (z-score)** — subtract mean, divide by SD. The default. Use when features
  are roughly bell-ish and you want each to contribute comparably.
- **Min–max scale** to [0,1] — when you want bounded ranges or features aren't
  Gaussian-ish. More outlier-sensitive than z-scoring.
- **Robust scale** (median / IQR) — when outliers are present; resists their influence.
- **Don't scale** when units are already meaningful and comparable (e.g., all features
  are the same physical quantity, or spatial x/y coordinates where the geometry *is* the
  point). Scaling lat/long or pixel coordinates can destroy the structure you want.

**Subtle but important:** standardizing equalizes *variance*, which implicitly equalizes
how much each feature can influence clusters. That's usually right, but if a feature is
high-variance *because it carries the real signal*, scaling it down can suppress the
structure. Scaling is a modeling choice, not a mechanical preprocessing step — decide it,
don't default through it unthinkingly. Also: **fit the scaler on training data only** if
you'll assign new points, to avoid leakage.

## Distance

The metric defines what "similar" means; it is as consequential as the algorithm.

- **Euclidean (L2)** — straight-line. The default; assumed by k-means, Ward, GMM. Good
  for continuous, scaled, low-to-moderate-dimensional data. Degrades in high d.
- **Manhattan (L1)** — sum of absolute differences. More robust to outliers; sometimes
  better-behaved in higher dimensions. Use with k-medoids/PAM.
- **Cosine** — angle between vectors, ignores magnitude. The right choice for text
  embeddings, TF-IDF, and any setting where *direction/proportion* matters more than
  length. (k-means on L2-normalized vectors approximates spherical k-means / cosine.)
- **Mahalanobis** — accounts for feature covariance and scale; equivalent to Euclidean
  after whitening. GMM with full covariance effectively learns a per-cluster Mahalanobis
  distance.
- **Correlation distance** — groups by *shape* of profiles rather than level; common in
  gene expression and time-series shape clustering.
- **Gower** — for mixed-type data (see below).
- **DTW (dynamic time warping)** — for time series that should match despite shifts/warps
  in time; pair with k-medoids or hierarchical, not k-means (means of warped series are
  ill-defined; use DBA if you must).

Centroid methods (k-means) are wedded to (squared) Euclidean by construction. If you need
a different metric, use k-medoids, hierarchical, DBSCAN/HDBSCAN (which accept arbitrary
metrics or precomputed distance matrices), or spectral with a matching affinity.

## Categorical and mixed

Euclidean distance on one-hot-encoded categories is usually a mistake — it imposes
arbitrary geometry (all categories equidistant, and high-cardinality variables dominate).
Handle types honestly:

- **All categorical:** **k-modes** (modes instead of means, a matching/Hamming
  dissimilarity), or **LCA** (model-based — see `mixture-models.md`, often the better
  choice because it gives uncertainty and model selection).
- **Mixed continuous + categorical:** **Gower distance** (per-feature normalized
  dissimilarity, averaged across types) fed to **k-medoids (PAM)** or hierarchical; or
  **k-prototypes** (k-means/k-modes hybrid with a weight balancing the two parts). The
  k-prototypes `gamma` weight (how much categorical mismatch counts vs. numeric distance)
  is a real tuning decision, not a detail.
- **Ordinal:** don't one-hot (loses order) and don't treat as plain numeric
  unthinkingly. Map to ranks/scores if spacing is defensible, or use Gower's ordinal
  handling.
- **High-cardinality categoricals** (e.g., ZIP code, product ID): one-hot explodes
  dimensionality and dominates distance. Consider target/frequency encoding, embeddings,
  or grouping before clustering.

## Dimensionality

**The curse of dimensionality is the quiet killer of clustering.** As dimensions grow,
distances between all pairs of points concentrate toward the same value — the contrast
between "near" and "far" collapses, and density becomes meaningless. Every distance- and
density-based method degrades. Symptoms: everything looks equidistant; DBSCAN/HDBSCAN
mark almost everything noise or lump everything together; k-means clusters look
arbitrary.

What to do:

- **Reduce dimensions before clustering**, especially before density methods. **PCA**
  for linear structure (cluster on enough components to retain the variance you care
  about). **UMAP** for non-linear structure, with a sharp caveat: UMAP/t-SNE can
  *create* apparent clusters and distort densities, so (a) prefer UMAP over t-SNE for
  preserving global structure, (b) never validate clusters with the same embedding that
  produced them, and (c) be wary of over-interpreting inter-cluster distances in the
  embedding.
- **Feature selection.** Often better than projection — drop features irrelevant to the
  distinction you care about. Irrelevant features add pure noise to every distance.
- **Use cosine** in very high-dimensional sparse spaces (text), where it behaves better
  than Euclidean.
- **Prefer GMM with constrained covariance or model-based methods** over density methods
  when d is high and you can't reduce it — they degrade more gracefully.

## Outliers

- **Centroid and model-based methods assign everything**, so outliers distort centers
  (k-means especially; the mean chases them). Robust-scale, cap/winsorize, or remove
  egregious outliers first — or use k-medoids (robust) or **density methods, which label
  outliers as noise instead of forcing them in.** "I have outliers I want set aside" is
  itself a strong argument for HDBSCAN.
- Don't reflexively delete outliers, though — sometimes the outliers *are* the
  interesting cluster (fraud, rare disease subtype). Decide based on the goal.

## Checklist

Before clustering anything, confirm you've consciously decided each of these (and
recorded the decision — they drive the result and reviewers/stakeholders will ask):

1. **Types handled?** Continuous vs categorical vs mixed → metric/method matches.
2. **Scaled?** Which scaler, and why — or a defensible reason not to.
3. **Distance metric** chosen to match the data and the geometry you care about.
4. **Dimensionality** assessed; reduced or features selected if high (mandatory before
   density methods).
5. **Outliers** considered: remove, robust-scale, or use a noise-labeling method —
   matched to whether outliers are nuisance or signal.
6. **Leakage** avoided: scalers/reducers fit on training data only if you'll assign new
   points.

Every one of these moves clusters around. Algorithm choice comes *after* they're settled.
