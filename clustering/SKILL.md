---
name: cluster-analysis
description: >-
  Opinionated guide to choosing, running, validating, and interpreting clustering
  methods. Use this whenever a task involves grouping unlabeled data into clusters,
  segments, profiles, latent classes, communities, or "natural groupings" — even when
  the user names a specific algorithm (k-means, GMM, DBSCAN, HDBSCAN, OPTICS, BIRCH,
  agglomerative/Ward, divisive, spectral, mean shift, affinity propagation, fuzzy
  c-means, LCA, LPA, mixture models) or asks adjacent questions like "how many clusters
  should I use," "which clustering algorithm is best for X," "why are my clusters bad,"
  customer/market segmentation, unsupervised exploratory analysis, or choosing a
  distance metric for grouping. Trigger it for the method-selection decision itself,
  not only for code. Do NOT use it for supervised classification, nearest-neighbor
  retrieval, dimensionality reduction on its own (PCA/UMAP/t-SNE), or topic modeling
  unless those feed a clustering decision.
---

# Cluster Analysis

Clustering finds groups in unlabeled data. The hard part is almost never running the
algorithm — every library does that in one line. The hard part is (1) deciding whether
groups exist at all, (2) choosing a method whose *assumptions* match your data, (3)
preprocessing so the geometry is meaningful, and (4) telling a real, stable cluster
from a confident artifact. This skill is built around those four problems, with strong
defaults so you don't relitigate them every time.

## The single most important idea

**Clustering always returns clusters.** Feed k-means uniform random noise and ask for
4 groups; you get 4 tidy groups with a respectable silhouette score. The output of a
clustering run is therefore not evidence that structure exists. Clustering is
*hypothesis generation*, not discovery of ground truth. Every result must survive two
questions before you trust it: **Is it stable?** (does it reproduce under resampling,
reinitialization, and small perturbations?) and **Is it real?** (does a structureless
null version of your data produce "clusters" that look just as good?). If you skip
these, you are pattern-matching on noise with extra steps.

## What dominates your results (in order)

1. **Preprocessing and the distance metric.** Scaling, feature selection, and the
   choice of distance change the answer far more than swapping k-means for spectral.
   An unscaled feature with a large range silently becomes the only thing you cluster
   on. Spend your effort here first. See `references/preprocessing.md`.
2. **Whether your assumptions match the cluster geometry.** Every algorithm encodes a
   shape prior (spherical, convex, density-connected, manifold, distributional).
   Mismatch is the usual cause of "bad clusters."
3. **k (or the parameter that implies k).** Important, but downstream of the above and
   never has a single correct value. See `references/validation.md`.
4. **The specific algorithm.** Genuinely matters least once 1–3 are handled. This is
   the opposite of how most people allocate their attention.

## Decision framework — start here

Answer these about your problem, then read the recommendation below. Don't reach for
a reference file until you've narrowed the family.

- **Data type?** Continuous → most methods. Categorical → LCA, k-modes. Mixed → Gower
  distance + PAM, or k-prototypes. (`references/preprocessing.md`)
- **Do you know k?** Yes, or willing to pick it → centroid/model-based. No, and you'd
  rather the data decide → density methods or affinity propagation.
- **Cluster shape?** Roughly convex/blobby → centroid or model-based. Arbitrary,
  elongated, nested, or manifold (moons, rings) → density or spectral.
- **Variable density across clusters?** Yes → HDBSCAN (not plain DBSCAN).
- **Noise/outliers you want *excluded* rather than forced into a cluster?** → density
  methods (they label noise; centroid/model-based methods assign everything).
- **Do you need soft / probabilistic membership?** → GMM (preferred) or fuzzy c-means.
- **Do you need a generative model / uncertainty / model selection by BIC?** → mixture
  models (GMM, LCA, LPA). (`references/mixture-models.md`)
- **Will you assign *new* points later (inductive)?** → k-means, GMM, BIRCH assign
  cleanly. DBSCAN/HDBSCAN/spectral/affinity propagation are transductive; new points
  need an approximate-predict step or a trained classifier on top.
- **Scale?** n in millions or streaming → MiniBatch k-means or BIRCH. n in low
  thousands and you want quality → anything, including the O(n²)–O(n³) methods.
- **Need a hierarchy / dendrogram / nested granularity?** → agglomerative (Ward) or
  HDBSCAN's condensed tree.

### Default recommendations (opinionated)

These are starting points, not laws. The reasoning matters more than the verdict —
read the per-method entries in `references/algorithms.md` before committing.

| Situation | Reach for | Why (and the catch) |
|---|---|---|
| "Just give me reasonable clusters," continuous, blobby, moderate size | **k-means(++ init)**, pick k via silhouette + gap, cross-check with GMM | Fast, scalable, understood. Catch: silently imposes spherical, equal-size, convex clusters and will split a single elongated blob. |
| Don't know k; shapes may be irregular; variable density; noise present | **HDBSCAN** | Best general-purpose density method. No global `eps`, handles variable density, returns membership probabilities and a hierarchy, labels noise. Catch: two parameters still matter; struggles in high dimensions. |
| Want a probabilistic/generative model, soft assignment, elliptical clusters | **GMM**, k via BIC | "Soft k-means done honestly." Catch: full covariance + high d overfits — constrain/regularize covariance. |
| Continuous indicators, behavioral/psych/social research, want fit statistics and theory-driven classes | **LPA** (= Gaussian mixture), select with BIC/ICL/BLRT | Same math as GMM, different research culture. `mclust`, `tidySEM`, Mplus. |
| Categorical indicators (survey items, yes/no) | **LCA** (poLCA/Mplus), or k-modes | Mixture model with categorical/binomial indicators. |
| Connectivity / manifold structure (concentric circles, two moons) | **Spectral clustering**, or HDBSCAN | Catch: O(n³) eigendecomposition; must specify k and build a good affinity graph. |
| Huge data or streaming | **MiniBatch k-means** or **BIRCH** (compress, then cluster summaries) | BIRCH's value is the CF-tree, not its clustering philosophy. |
| Need a dendrogram / nested structure / small n | **Agglomerative**, Ward linkage for compact clusters | Catch: O(n²) memory, greedy merges are irreversible. |
| Want actual data points as cluster representatives (exemplars) | **k-medoids (PAM)** usually; **Affinity Propagation** if you also don't want to pick k | AP is O(n²) and parameter-touchy — see warning below. |

### Methods that are over-recommended (spend your skepticism here)

- **Affinity Propagation** and **Mean Shift**: O(n²), slow, sensitive to `preference` /
  `bandwidth`, and rarely beat a well-tuned alternative. Real but narrow niches (AP for
  exemplars without picking k; Mean Shift for low-dimensional mode-finding / image
  segmentation). Tutorials over-feature them because they're conceptually cute.
- **The elbow method**: weak and subjective. Prefer silhouette, gap statistic, or BIC —
  and still treat them as advisory.
- **Plain DBSCAN over HDBSCAN**: choose DBSCAN only when you specifically want a single
  global density scale, need its speed, or want exact reproducibility of a known result.
  Otherwise HDBSCAN dominates it.
- **Divisive hierarchical (DIANA)**: conceptually clean (top-down), almost never worth
  it in practice — agglomerative Ward is the default hierarchical method. Know it exists.

## The taxonomy (a map, not rigid bins)

The standard "families" are a way to reason about *assumptions*, not a filing system.
The boundaries leak, and that's fine — it's often the most useful thing to notice.

- **Centroid / partitional** — represent each cluster by a center; assign by distance.
  *k-means, k-medoids (PAM), MiniBatch k-means, fuzzy c-means.* Assume convex, roughly
  spherical, comparable-size clusters. Need k.
- **Distribution / model-based** — assume data is generated by a mixture of
  distributions; fit by EM; assign by posterior probability. *GMM, LCA, LPA, finite
  mixture models.* Give uncertainty, generative models, and principled model selection.
- **Density-based** — clusters are dense regions separated by sparse ones; points in
  sparse regions are noise. *DBSCAN, HDBSCAN, OPTICS, Mean Shift.* Find arbitrary
  shapes, don't need k, handle noise. Struggle in high dimensions.
- **Hierarchical** — build a tree of nested clusters. *Agglomerative (bottom-up,
  Ward/complete/average/single linkage), divisive/DIANA (top-down).* Give a dendrogram;
  you cut it to get a flat clustering.
- **Graph / spectral** — embed via the graph Laplacian's eigenvectors, then cluster the
  embedding. *Spectral clustering, affinity propagation (message passing).* Capture
  connectivity and manifold structure.

**Where the bins leak (and why it's instructive):** HDBSCAN is density *and*
hierarchical. GMM is distribution-based but reduces to "soft k-means" with spherical
equal covariance — so k-means is a degenerate GMM. Spectral is graph-based but the last
step is usually plain k-means on the embedding. Fuzzy c-means is centroid-based but
soft, like a non-probabilistic GMM. Use families to ask "what does this method assume
about cluster shape, density, and size?" — not to pick a winner by category.

## Workflow for an actual clustering task

1. **Frame it.** What decision will the clusters inform? "Customer segments for a
   campaign" and "are there subtypes in this disorder" demand different rigor and
   different methods. Interpretability and stability matter more for the former's
   stakeholders than a marginal silhouette gain.
2. **Preprocess deliberately.** Scale (almost always), choose a distance that matches
   the data type, handle mixed/categorical data properly, and reduce dimensionality
   *before* density methods if d is large. Document every choice — they drive the
   result. (`references/preprocessing.md`)
3. **Check for clusterability first.** Look at the data (2D projection via PCA/UMAP),
   and consider the Hopkins statistic or a VAT plot. If there's no structure, say so
   and stop. This is the step everyone skips and the one that prevents the most
   embarrassing conclusions.
4. **Pick a method by assumptions**, using the framework above. When unsure between two,
   run both — disagreement is informative.
5. **Choose k / parameters** with multiple indices, not one, and not the elbow alone.
   For model-based methods, use BIC. (`references/validation.md`)
6. **Validate.** Stability (bootstrap, reinitialize, perturb) and a null comparison.
   Internal indices are advisory and frequently disagree with domain experts — never
   let one number be the whole justification.
7. **Interpret honestly.** Profile clusters on the original features, name them
   tentatively, and report what's uncertain — sizes, overlap, points that barely belong.
   Resist the urge to tell a clean story the data doesn't support.

## When to load each reference

- `references/algorithms.md` — per-method deep reference (mechanism, parameters,
  complexity, assumptions, when to use / avoid, gotchas). Read the relevant entries
  before recommending or coding a specific algorithm. Has a table of contents.
- `references/mixture-models.md` — GMM, LCA, LPA, the finite-mixture family, EM, model
  selection (BIC/AIC/ICL/BLRT), identifiability, and the social-science↔ML naming map.
  Read it for anything involving latent classes/profiles or probabilistic clusters.
- `references/validation.md` — choosing k, internal/external/relative indices, the gap
  statistic, stability, clusterability tests, and the honest critique of all of them.
- `references/preprocessing.md` — scaling, distance metrics, categorical/mixed data,
  dimensionality and the high-d curse, what to do before density methods.

## Reusable diagnostic harness

`scripts/cluster_diagnostics.py` runs a standard battery on a numeric dataset:
clusterability check, a k-selection sweep across multiple internal indices, fits of
several algorithm families for comparison, and stability via bootstrap ARI. Prefer it
over hand-rolling the same sweep every time.

```bash
python scripts/cluster_diagnostics.py data.csv --max-k 10 --scale standard
python scripts/cluster_diagnostics.py data.csv --methods kmeans,gmm,hdbscan --k 4
```

Read its `--help` and the header docstring before use; it is meant to be edited for the
specific dataset, not treated as a black box.
