# Manifold & neural embedding methods

Nonlinear methods, mostly aimed at **visualization** (job 2). Their great strength is revealing
local neighbourhood structure that linear methods miss; their great danger is that the output is a
*picture*, and people read clustering, distances, and discoveries off it as if it were analysis.

Contents: t-SNE · UMAP · PaCMAP · TriMap · PHATE · Isomap · LLE · Spectral/Laplacian eigenmaps ·
Autoencoders/VAEs · Interpretation traps (read this last section every time).

---

## t-SNE — t-distributed Stochastic Neighbor Embedding

**What it does.** Converts pairwise similarities into probabilities (Gaussian in high-dim, Student-t
in low-dim), then moves points so the two distributions match (minimizes KL divergence). The
heavy-tailed t-distribution in the output space prevents the "crowding problem."

**Excels at.** Revealing local cluster structure; gorgeous separations on data with real clusters
(MNIST, single-cell).

**Hyperparameters that actually matter.**
- **perplexity** (~5–50): the effective neighbourhood size. Too low → spurious clumps; too high →
  clusters merge. There is no universally correct value; *scan a range*.
- **learning rate** and **iterations**: too-low LR or too-few iters → a "ball" of points.
- **init**: PCA initialization (not random) greatly improves global layout and reproducibility —
  use it. Modern openTSNE defaults to PCA init + better exaggeration schedules.

**Hard truths.** Stochastic (seed-dependent). Cluster **sizes mean nothing** (it equalizes density).
Distances **between** clusters mostly mean nothing. Does not scale gracefully past ~100k points
without approximations (Barnes-Hut, FFT/FIt-SNE). Always PCA→~50d first.

**sklearn / better.** `TSNE(init='pca', perplexity=..., random_state=...)`; prefer **openTSNE** for
speed, PCA-init defaults, and the ability to embed new points.

---

## UMAP — Uniform Manifold Approximation and Projection

**What it does.** Builds a fuzzy topological graph of the data (via local fuzzy simplicial sets) and
optimizes a low-dim layout to match it using a cross-entropy-style loss with attractive/repulsive
forces. Faster than vanilla t-SNE and supports transforming new points and supervised/metric variants.

**Excels at.** Fast, scalable visualization; reusable `transform`; flexible (supervised UMAP, custom
metrics, embedding to >2 dims for features).

**Hyperparameters that matter.**
- **n_neighbors** (~5–50): low = local detail, high = more global structure.
- **min_dist** (~0.0–0.99): how tightly points may pack; purely a cosmetic/clumping knob — *not* a
  structural truth.
- **metric**: choose to match the data (cosine for text embeddings, etc.).

**Hard truths.** The widely repeated claim that "UMAP preserves global structure (and t-SNE doesn't)"
is **overstated** — controlled benchmarks find UMAP only marginally better than t-SNE globally, and
both far behind PCA/PaCMAP/TriMap on global geometry. UMAP is stochastic; vary the seed. `min_dist`
changes how clustered it *looks* without changing the data. As with t-SNE: cluster size and
inter-cluster distance are not trustworthy. Theoretical "guarantees" rely on assumptions
(uniform density on a manifold) that rarely hold and ignore the PCA preprocessing.

**Library.** `umap-learn`: `UMAP(n_neighbors=..., min_dist=..., metric=..., random_state=...)`.
Setting `random_state` disables parallelism (reproducibility vs speed trade-off).

---

## PaCMAP — Pairwise Controlled Manifold Approximation

**What it does.** Optimizes the layout using three pair types — **neighbour**, **mid-near**, and
**further** pairs — with a schedule that captures global structure first, then refines local
structure. Designed explicitly to fix the local-vs-global trade-off that t-SNE/UMAP force.

**Why prefer it.** Independent benchmarks repeatedly rank PaCMAP at or near the top for preserving
*both* local and global structure, and it's less hyperparameter-fragile than t-SNE. When the user
cares about global layout *and* wants a 2D picture, PaCMAP (or TriMap) is a better recommendation
than reflexively reaching for UMAP. (`ParamRepulsor`/parametric PaCMAP add a reusable encoder + GPU.)

**Library.** `pacmap.PaCMAP(n_components=2, n_neighbors=..., MN_ratio=..., FP_ratio=...)`.

---

## TriMap

Triplet-based: enforces relative-distance constraints ("i is closer to j than to k"). Strong **global**
structure preservation — often the best at keeping large-scale geometry and line/trajectory shapes —
but can be weaker on fine local structure. Good when the macro-layout is the point.

---

## PHATE

Diffusion-based; built for **continuous trajectories / developmental progressions** (single-cell
biology) rather than discrete clusters. Captures branching/continuum structure well; tends to do
poorly when the truth is tight discrete clusters, and can underperform on pure local-structure
metrics. Recommend it for trajectory/continuum questions, not generic clustering visualization.

---

## Isomap

Classical-MDS on **geodesic** distances (shortest paths along a k-NN graph) → "unrolls" curved
manifolds like the swiss roll that defeat PCA. **Fragile**: the neighbour count `n_neighbors` is
critical, and a single noisy "short-circuit" edge between manifold folds collapses the geometry.
Best on clean, densely-sampled, genuinely-manifold data.

## LLE — Locally Linear Embedding

Reconstructs each point from its neighbours with linear weights, then finds the low-dim layout that
preserves those weights. Preserves local structure, no geodesic graph needed, but sensitive to
`n_neighbors` and prone to collapsing/distorting global structure. Variants: Modified LLE, Hessian
LLE, LTSA. Niche today — usually outperformed by UMAP/PaCMAP for visualization.

## Spectral embedding / Laplacian Eigenmaps

Eigenvectors of the graph Laplacian of a k-NN graph; the foundation under spectral clustering and
related to diffusion maps. Good for connected manifold structure; the conceptual ancestor of much
of the above.

---

## Autoencoders & VAEs

**Autoencoder.** A neural net trained to reconstruct its input through a narrow bottleneck; the
bottleneck activations are the embedding. A linear-activation undercomplete AE **recovers the same
subspace as PCA** (though not necessarily orthogonal or variance-ordered components unless you
constrain it); nonlinear activations give a nonlinear, *parametric* (reusable) encoder.

**When justified.** Large datasets; images/audio/sequences where convolutional/recurrent/transformer
encoders exploit structure; when you need to encode *new* points cheaply at inference; when DR is one
stage of a larger trained pipeline.

**When NOT.** Small/medium tabular data — PCA + UMAP/PaCMAP is faster, needs no architecture/epoch
tuning, won't overfit, and is far easier to validate. Don't reach for a deep net to look serious.

**VAE.** Adds a probabilistic latent prior and a sampling layer → a *generative* latent space you can
sample/interpolate, with a smoother, more disentangled latent geometry. Use when you want generation
or a principled probabilistic latent space, not merely a 2D picture. (β-VAE trades reconstruction for
disentanglement.)

**Validation.** Same neighbour-preservation diagnostics apply; also watch reconstruction error and,
for VAEs, the KL/reconstruction balance (posterior collapse).

---

## Interpretation traps — re-read before interpreting ANY t-SNE/UMAP plot

These come straight from the well-known failure catalogue (Wattenberg et al.'s "How to Use t-SNE
Effectively"; the Chari & Pachter "specious art" critique and its rebuttals) and apply to UMAP too:

1. **Cluster sizes are meaningless.** The algorithms equalize density, expanding sparse clusters and
   shrinking dense ones. A big blob is not a more variable group.
2. **Distances between clusters are mostly meaningless.** Two clusters far apart are not "more
   different" than two close ones. If distance matters, measure it in the original/PCA space.
3. **Clumps at low perplexity / n_neighbors can be pure noise.** Random data produces apparent
   structure. Always scan multiple settings.
4. **Shape can be an artifact.** The same data yields different shapes under different seeds and
   parameters. `min_dist` in particular changes appearance, not data.
5. **One run is not evidence.** Reproduce across seeds and parameters; report what's stable.
6. **Topology is not always preserved.** Connectedness and relative positions can be wrong; don't
   infer lineage/ordering from a 2D embedding without trajectory-aware methods and validation.
7. **Don't cluster on the 2D embedding.** Run clustering (k-means, HDBSCAN, Leiden) in the
   original or PCA-reduced space; use the embedding only to *display* those labels.

The honest framing to give users: a t-SNE/UMAP plot is a *hypothesis-generating picture*, not a
result. Confirm anything you see with metrics (see `validation-and-diagnostics.md`) and with analysis
in the original space.

---

## Sources / further reading

- Interpretation traps: Wattenberg, Viégas & Johnson, "How to Use t-SNE Effectively," *Distill*
  (2016) — the canonical demonstration that cluster sizes/distances are not trustworthy.
- t-SNE: van der Maaten & Hinton, "Visualizing Data using t-SNE," *JMLR* (2008); openTSNE (Poličar
  et al.) for PCA-init defaults and approximate out-of-sample transform.
- UMAP: McInnes, Healy & Melville, "UMAP: Uniform Manifold Approximation and Projection," (2018).
- PaCMAP / the local-vs-global analysis: Wang, Huang, Rudin & Shaposhnik, "Understanding How
  Dimension Reduction Tools Work," *JMLR* (2021).
- TriMap: Amid & Warmuth (2019). PHATE: Moon et al., *Nature Biotechnology* (2019).
- The distortion debate: Chari & Pachter, "The specious art of single-cell genomics," *PLOS
  Computational Biology* (2023), and the rebuttal "The art of seeing the elephant in the room: 2D
  embeddings of single-cell data do make sense," *bioRxiv* (2024).
- Global-structure benchmarks: comparative DR evaluations in *Communications Biology* (2022) and
  related benchmarking work consistently rank PCA/PaCMAP/TriMap above t-SNE/UMAP on global structure.
