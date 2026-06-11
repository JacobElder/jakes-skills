# Validation: Choosing k and Trusting the Result

Two questions, constantly conflated, that this file keeps separate:

1. **How many clusters?** (model selection / k-selection)
2. **Should I believe these clusters at all?** (validity, stability, clusterability)

The second is more important and more often skipped. A clustering can have the "optimal"
k by every index and still be an artifact of noise. Resist letting a single number — an
elbow, a silhouette peak, a BIC minimum — stand in for the judgment that clustering
actually requires.

## Contents

- [First, is there structure at all? (clusterability)](#clusterability)
- [Choosing k](#choosing-k)
- [Internal indices (no labels)](#internal-indices)
- [External indices (you have ground truth)](#external-indices)
- [Stability — the validation that matters most](#stability)
- [The honest critique of all of this](#honest-critique)
- [A defensible validation protocol](#protocol)

---

## Clusterability

Before asking "how many clusters," ask "are there clusters." Clustering uniform noise
yields confident clusters, so this step prevents the most embarrassing failure mode.

- **Look at the data.** A 2D projection (PCA for linear structure; UMAP/t-SNE for
  non-linear, with the caveat that those can *manufacture* visual clusters — never
  validate clusters using the same embedding that created them). Often the eye settles
  the question instantly.
- **Hopkins statistic.** Compares distances among real points to distances among
  uniformly-sampled points in the same space. ≈0.5 → indistinguishable from uniform (no
  cluster tendency); →1 → strong clustering tendency. Crude and dimensionality-sensitive,
  but a cheap sanity check.
- **VAT (Visual Assessment of cluster Tendency).** Reorders the dissimilarity matrix and
  displays it as an image; dark blocks on the diagonal suggest clusters. Useful, scales
  poorly.

If there's no structure, the correct deliverable is "no robust clusters were found,"
not k clusters anyway. That is a real, reportable result.

## Choosing k

No method is an oracle; use several and expect disagreement.

- **Elbow method.** Plot within-cluster sum of squares (inertia) vs. k; look for the
  bend. **Weak and subjective** — inertia always decreases with k, the "elbow" is often
  ambiguous, and different viewers pick different k. Use it as a rough orientation, never
  as the justification.
- **Silhouette analysis.** For each point, (b−a)/max(a,b) where a = mean intra-cluster
  distance, b = mean distance to the nearest other cluster. Average silhouette across
  points, swept over k; higher is better. Far better than the elbow. Also inspect the
  per-cluster silhouette *plot* — a high average can hide one terrible cluster.
- **Gap statistic.** Compares within-cluster dispersion to its expectation under a
  null reference (uniform data over the data's bounding box / PCA-aligned box). Choose
  the smallest k where the gap is within one standard error of the next — built-in null
  comparison is its strength. More principled than the elbow, more expensive.
- **BIC / ICL / BLRT** — for model-based clustering (GMM/LCA/LPA), the *right* tools for
  k. See `mixture-models.md`. If you're using a mixture model, prefer these over the
  geometric indices below.
- **Density methods don't take k.** For DBSCAN/HDBSCAN/OPTICS you tune density
  parameters instead (`eps`, `min_cluster_size`, `min_samples`); the cluster count
  emerges. That's a feature, but you're still choosing *something* — there is no
  parameter-free clustering.

## Internal indices

Computed from the data and the labels alone (no ground truth). Use them *relatively*
(compare solutions) rather than absolutely.

- **Silhouette coefficient** — cohesion vs. separation, ∈[−1,1], higher better.
  Among the most reliable for convex clusters.
- **Davies–Bouldin index** — average ratio of within-cluster scatter to between-cluster
  separation; **lower** better. Reliable, cheap, pairs well with silhouette.
- **Calinski–Harabasz index (variance ratio)** — between-cluster vs. within-cluster
  dispersion; **higher** better. Fast; tends to favor more clusters.
- **Dunn index** — min inter-cluster distance / max intra-cluster diameter; higher
  better. Intuitive but outlier-sensitive and expensive.

**All of these encode a convex/compact prior.** They reward spherical, well-separated
blobs, so they will rate a (correct) DBSCAN clustering of two interleaving moons *worse*
than a (wrong) k-means split of it. Never use silhouette/CH/DB to judge a density or
manifold clustering against a centroid one — you'll pick the wrong method because the
metric shares k-means' assumptions.

## External indices

When you *do* have ground-truth labels (benchmarking, or a labeled subset):

- **Adjusted Rand Index (ARI)** — agreement of two partitions, corrected for chance;
  1 = identical, 0 = chance, can go negative. **The standard**; report it.
- **Normalized / Adjusted Mutual Information (NMI/AMI)** — information shared between
  partitions, normalized; AMI is chance-corrected. Use AMI over NMI for the same reason
  you use ARI over Rand.
- **Fowlkes–Mallows, homogeneity/completeness/V-measure** — situational supplements.

Use these to compare clusterings to a reference, or to compare two clusterings to each
other (the basis of the stability methods below).

## Stability

**The most trustworthy signal that a clustering is real.** A genuine structure
reproduces; an artifact doesn't.

- **Bootstrap / resampling.** Recluster many resamples (or subsamples) of the data;
  measure agreement (mean pairwise ARI/AMI, or per-cluster Jaccard). Stable clusters
  recur; unstable ones dissolve. `fpc::clusterboot` in R formalizes this (Jaccard ≥ ~0.75
  = stable, < ~0.6 = dissolved).
- **Reinitialization.** For stochastic methods (k-means, GMM, spectral), rerun with
  different seeds. If the partition lurches between runs, it's not robust — increase
  `n_init`, reconsider k, or reconsider the method.
- **Perturbation.** Add small noise or drop a few features; a real structure tolerates
  it. The bundled `scripts/cluster_diagnostics.py` does bootstrap-ARI stability.
- **Hold-out / inductive check.** Cluster a training split, assign a test split, and ask
  whether the test assignment is sensible. Only works for inductive methods (k-means,
  GMM, BIRCH).

## Honest critique

Internal validity indices are not ground truth, and the literature is increasingly blunt
about it: studies treating them as objective functions find that the "optimal" clustering
by a popular index frequently matches expert/domain judgment poorly, and indices
routinely disagree with each other on the same data. There is no purely data-driven
"correct" number of clusters, and there cannot be — clustering is under-determined; the
right answer depends on what distinction you care about, which the data alone doesn't
encode.

Practical consequences:

- **Never report a single index as the justification.** Triangulate (silhouette + DB +
  gap + stability), and weight stability and interpretability heavily.
- **Match the index to the method's geometry.** Don't judge non-convex clusterings with
  convex-assuming indices.
- **Substantive interpretability is a legitimate tiebreaker.** If k=3 is marginally worse
  on BIC but the three groups mean something actionable and k=4 splits one into noise,
  choose 3 and say why. This is standard practice in good LPA/LCA work and should be
  standard everywhere.

## Protocol

A defensible, reusable sequence:

1. **Clusterability** — visualize; Hopkins/VAT if in doubt. If no structure, stop and
   report that.
2. **Preprocess** deliberately (`preprocessing.md`); record every choice.
3. **Pick method by assumptions** (`SKILL.md` framework); when torn, run two and compare.
4. **Sweep k / parameters** with *multiple* criteria appropriate to the method (BIC for
   model-based; silhouette + gap + DB for geometric; density params for density methods).
5. **Stability** — bootstrap ARI and reinitialization. Demote any solution that won't
   reproduce, regardless of its index scores.
6. **Null comparison** — confirm a structureless version of your data doesn't score
   comparably (the gap statistic bakes this in; otherwise do it explicitly).
7. **Interpret and report honestly** — profile clusters on original features; disclose
   sizes, overlap, marginal members, and the choices that drove the result. State what
   you're uncertain about.
