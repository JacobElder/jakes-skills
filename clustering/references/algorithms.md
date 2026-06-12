# Algorithms Reference

Per-method reference. Each entry: how it works, key parameters, complexity,
assumptions, when to use, when to avoid, and the gotchas that actually bite. Read the
entries relevant to your decision — don't dump the whole file into context.

Mixture models (GMM, LCA, LPA) live in `mixture-models.md`. Validation and k-selection
live in `validation.md`. This file is the non-probabilistic methods plus the geometry
reasoning that ties them together.

## Contents

- [Centroid / partitional](#centroid--partitional)
  - [k-means](#k-means)
  - [k-means++ initialization](#k-means-initialization)
  - [MiniBatch k-means](#minibatch-k-means)
  - [k-medoids (PAM)](#k-medoids-pam)
  - [Fuzzy c-means](#fuzzy-c-means)
- [Hierarchical](#hierarchical)
  - [Agglomerative + linkage criteria](#agglomerative)
  - [Divisive (DIANA)](#divisive-diana)
- [Density-based](#density-based)
  - [DBSCAN](#dbscan)
  - [HDBSCAN](#hdbscan)
  - [OPTICS](#optics)
  - [Mean Shift](#mean-shift)
- [Scalability / summarization](#scalability)
  - [BIRCH](#birch)
- [Graph / message-passing](#graph--message-passing)
  - [Spectral clustering](#spectral-clustering)
  - [Affinity Propagation](#affinity-propagation)
- [Cross-method geometry cheat sheet](#geometry-cheat-sheet)

---

## Centroid / partitional

These represent each cluster by a prototype (a mean or a medoid) and assign points by
distance. They share a family resemblance: they want convex, roughly spherical,
comparable-size clusters, and they need k. They differ mostly in what the prototype is
and whether assignment is hard or soft.

### k-means

**Mechanism.** Pick k centers; alternate (a) assign each point to its nearest center,
(b) move each center to the mean of its points. Repeat until assignments stop changing.
This is coordinate descent on within-cluster sum of squares (inertia). It converges to
a *local* optimum, so the initialization matters.

**Key parameters.** `k` (required); `n_init` (number of restarts — keep ≥10, the
default in good libraries); `init` (use k-means++); `max_iter`.

**Complexity.** O(n·k·d·i) per run, i iterations. Effectively linear in n — this is why
it scales and why it's the default for large data.

**Assumptions (the ones that bite).** Clusters are convex, isotropic (spherical), of
similar variance, and similar size. It minimizes variance, so it carves space into a
Voronoi tessellation — boundaries are always straight. It cannot represent an elongated
cluster, a ring, or two clusters of very different spread without splitting/merging them
wrongly. Because it assigns *every* point, outliers drag centers around.

**Use when.** Data is roughly blobby, you can scale features sensibly, n is large, and
you want a fast, well-understood baseline. It is the right default more often than its
reputation suggests — and the right thing to *compare against* even when it's not the
final method.

**Avoid when.** Clusters are non-convex or wildly different in size/density; there's
meaningful noise you want excluded; features are on incomparable scales and you haven't
fixed that; the data is categorical (use k-modes) or mixed (k-prototypes / Gower+PAM).

**Gotchas.** (1) *Always scale first* unless features are already comparable — k-means
is pure Euclidean variance. (2) Inertia always decreases with k, so you cannot pick k by
minimizing it; that's why the elbow is eyeballed and weak. (3) It will confidently
cluster noise. (4) High dimensions make all distances similar (curse of dimensionality);
reduce dimensions first.

### k-means++ initialization

Not an algorithm — the standard *initialization* for k-means. Picks initial centers
spread out (each new center chosen with probability proportional to squared distance
from the nearest existing center). Dramatically reduces bad local optima versus random
init and gives a provable expected-quality bound. Treat it as mandatory; there is rarely
a reason to use plain random initialization.

### MiniBatch k-means

k-means that updates centers using small random batches rather than the full dataset
each iteration. Trades a small amount of cluster quality for a large speedup and bounded
memory. **Use when** n is very large or streaming and plain k-means is too slow.
Otherwise prefer full k-means for the marginally better solution.

### k-medoids (PAM)

**Mechanism.** Like k-means, but the prototype is an actual data point (a *medoid*), and
it minimizes total distance to the medoid using *any* distance metric, not just squared
Euclidean.

**Why it matters.** (1) Works with arbitrary distances (Manhattan, cosine, Gower for
mixed data, precomputed dissimilarities). (2) Medoids are real, interpretable
representatives. (3) More robust to outliers than k-means (a mean chases outliers; a
medoid doesn't).

**Complexity.** Classic PAM is O(n²) per iteration — much heavier than k-means.
FasterPAM and CLARA (sampling) make it tractable for larger n.

**Use when** you need a non-Euclidean distance, real exemplars, or outlier robustness,
and n is moderate. **Avoid when** n is huge and Euclidean is fine — just use k-means.

### Fuzzy c-means

**Mechanism.** Soft k-means: each point gets a *membership degree* in every cluster
(summing to 1) rather than a hard label. Centers are membership-weighted means. A
fuzzifier `m` (typically 2) controls softness — as m→1 it approaches hard k-means; large
m makes memberships uniform and meaningless.

**Use when** you genuinely want graded membership and points that legitimately sit
between clusters, and you don't need a probabilistic model.

**Avoid / prefer GMM when** you want soft assignment *with* a generative model and
uncertainty — GMM gives you posteriors with the same softness plus model selection by
BIC and non-spherical covariance. Fuzzy c-means inherits all of k-means' geometric
assumptions (spherical, convex) and adds sensitivity to noise (noise points get spread
across clusters). In most cases where someone reaches for fuzzy c-means, GMM is the
better tool. Its real home is specific engineering domains (image segmentation, control)
where it's entrenched.

---

## Hierarchical

Build a tree of nested clusters instead of a single flat partition. You get a
dendrogram and cut it (at a height or a target cluster count) to get labels. Value:
no need to commit to k upfront, and the nesting can itself be the insight.

### Agglomerative

**Mechanism.** Bottom-up. Start with every point as its own cluster; repeatedly merge
the two "closest" clusters until one remains. "Closest" is defined by the **linkage
criterion**, which is the decision that actually determines the shape of your clusters:

- **Ward** — merge the pair that least increases total within-cluster variance. Produces
  compact, roughly equal-size, spherical clusters. **The default** for Euclidean data;
  behaves most like k-means but gives you the tree. Requires Euclidean distance.
- **Complete (maximum)** — distance between clusters = farthest pair. Compact clusters,
  sensitive to outliers, avoids chaining.
- **Average (UPGMA)** — distance = mean of all cross-pairs. A middle ground; common in
  bioinformatics/phylogenetics.
- **Single (minimum)** — distance = closest pair. Can find non-elliptical, elongated
  shapes, but suffers **chaining**: a thread of points links two otherwise separate
  clusters into one. Usually a footgun; use deliberately.
- **Centroid/median** — distance between cluster centroids; can produce non-monotone
  dendrograms (inversions), which are confusing. Generally prefer Ward.

**Complexity.** O(n²) memory and ~O(n²–n³) time. Practical to a few tens of thousands of
points, not millions. (For huge data, summarize with BIRCH first, then cluster.)

**Use when** you want a hierarchy/dendrogram, n is small-to-moderate, you want nested
granularity, or you need a non-Euclidean distance (with non-Ward linkage). A
`connectivity` constraint (e.g., a k-NN graph) can enforce spatial contiguity — useful
for image/geographic data.

**Avoid when** n is large (memory), or you need to assign new points (it's transductive
— refitting changes the whole tree).

**Gotchas.** Merges are greedy and irreversible — an early mistake propagates. The
linkage choice matters more than people expect; default to Ward and only deviate with a
reason. Don't read too much into the exact dendrogram heights; cuts are interpretive.

### Divisive (DIANA)

**Mechanism.** Top-down. Start with all points in one cluster; recursively split the
cluster with the largest diameter (DIANA splinters off the most dissimilar point and
grows a "splinter group"). Conceptually the mirror image of agglomerative.

**Reality check.** Rarely worth it. A naive exhaustive divisive split is exponential;
DIANA is a heuristic that's still heavier than agglomerative, and high-quality
implementations are scarce (`cluster::diana` in R is the standard one; not in
scikit-learn). It can be better than agglomerative when you care most about the *top*
of the hierarchy (big-picture splits) rather than fine local structure, because it makes
global decisions first. But for almost all practical work, reach for Ward agglomerative
instead. Know DIANA exists; rarely deploy it.

---

## Density-based

Clusters are dense regions separated by sparse regions; points in sparse regions are
labeled **noise** rather than forced into a cluster. This is the family's superpower:
arbitrary shapes, no k required, and honest handling of outliers. The shared weakness:
all rely on distance density, so they degrade in high dimensions where density becomes
meaningless. Reduce dimensionality first.

### DBSCAN

**Mechanism.** Two parameters: `eps` (neighborhood radius) and `min_samples`. A *core
point* has ≥ `min_samples` points within `eps`. Core points within `eps` of each other
form a cluster; non-core points within `eps` of a core point are border points;
everything else is noise.

**Complexity.** O(n log n) with a spatial index (typical), O(n²) worst case.

**Use when** clusters are arbitrarily shaped, density is roughly uniform *across*
clusters, you want noise labeled, and you don't know k. Classic for spatial data.

**Avoid when** clusters have **varying density** — a single global `eps` cannot be right
for a dense cluster and a sparse one at the same time. This is its defining failure mode
and the reason HDBSCAN exists.

**Gotchas.** (1) Wildly `eps`-sensitive; the standard heuristic is the k-distance graph
(plot sorted distance to the `min_samples`-th neighbor; look for the "knee"). (2)
Border-point assignment is order-dependent. (3) Transductive — no native predict for new
points. (4) Struggles in high d. **Bottom line:** prefer HDBSCAN unless you specifically
want a single global density scale, need DBSCAN's speed, or must reproduce a known
DBSCAN result.

### HDBSCAN

**Mechanism.** "Hierarchical DBSCAN." Transforms space by *mutual reachability distance*
(which down-weights distances through sparse regions), builds a minimum spanning tree,
forms a cluster hierarchy, then **condenses** it and extracts the most *stable* clusters
across density levels. The effect: it runs DBSCAN at all `eps` simultaneously and keeps
what persists.

**Key parameters.** `min_cluster_size` — the smallest group you'll call a cluster
(intuitive: set it to the smallest meaningful cluster). `min_samples` — how conservative
/ how much gets labeled noise (defaults to `min_cluster_size`; lower → less noise).
`cluster_selection_epsilon` — merge micro-clusters below a distance scale, recovering a
DBSCAN-like floor when you want it.

**Why it's the density default.** No global `eps`; handles **variable density**; returns
**membership probabilities** and **outlier scores**; exposes a hierarchy; and the
parameters have clear, tunable meanings. It dominates plain DBSCAN in almost every
practical case. In scikit-learn (`sklearn.cluster.HDBSCAN`, ≥1.3) or the `hdbscan`
package (which adds `approximate_predict` for new points).

**Avoid / caveats.** High dimensions still hurt (it's density-based). Can be slower and
more memory-hungry than DBSCAN on very large data. If almost everything comes back as
noise, your data may be one diffuse blob with a few tight outliers — that's information,
not a bug; lower `min_samples` or reconsider whether clusters exist.

**Transductive — no native predict for new points.** Like DBSCAN and spectral clustering,
HDBSCAN is transductive: it labels the training set but has no `predict()` for unseen
observations. Two options: (1) `hdbscan.approximate_predict()` assigns new points to the
nearest cluster in the fitted condensed tree — flag those labels as "assigned" rather than
"confidently clustered"; (2) train an inductive classifier (k-NN, random forest, logistic
regression) on the cluster labels and use it for future assignment. **Do not refit HDBSCAN
on the combined old + new data** each time new points arrive — that changes cluster
assignments for the entire historical set and makes comparisons across time meaningless.
If you will need to assign new points routinely, prefer k-means or GMM (which have clean
`predict()` methods) or plan the approximate-predict / classifier wrapper from the start.

**On high noise fractions.** A large -1 count (e.g., 30–40% noise) is a finding, not a
failure. Do not retune parameters just to force noise points into clusters and reduce the
-1 count — that defeats the purpose of using a density method and manufactures artificial
groupings. The right response is to first ask: *are these genuinely sparse/outlier points?*
If yes, report the noise fraction as part of the result. If the noise is unexpectedly high,
*then* adjust `min_samples` downward (to be less conservative) or `min_cluster_size`
(to allow smaller clusters) — but only as far as the data supports. If you need cluster
labels for all points, use `approximate_predict()` from the `hdbscan` package to assign
noise points to their nearest cluster post-hoc, clearly flagging them as assigned rather
than confidently clustered.

### OPTICS

**Mechanism.** "Ordering Points To Identify the Clustering Structure." A generalization
of DBSCAN that relaxes `eps` from a single value to a *range*. It doesn't directly
assign clusters; it orders points and assigns each a **reachability distance**,
producing a **reachability plot** — a 1D landscape where valleys are clusters and their
depth reflects density. You then extract a flat clustering either by cutting at a chosen
`eps` (DBSCAN-equivalent) or by the **xi method** (detecting steep valley boundaries),
which recovers clusters of varying density.

**Use when** you want to *understand* the density structure across scales (the
reachability plot is genuinely informative), or you'll extract clusterings at several
density levels from one fit. For repeated runs at varying `eps`, one OPTICS fit can be
cheaper than many DBSCAN runs.

**Avoid / caveats.** For a single `eps`, DBSCAN is faster. In practice, **HDBSCAN
usually subsumes OPTICS' benefits** with less fuss (it also handles variable density and
gives a hierarchy), so OPTICS is most valuable as a diagnostic/visual tool. `min_samples`
mostly smooths the reachability plot rather than acting like DBSCAN's.

### Mean Shift

**Mechanism.** Mode-seeking. Treat the data as samples from a density; each point climbs
the kernel density gradient toward the nearest **mode** (peak); points converging to the
same mode form a cluster. The number of clusters falls out of the density — you don't
set k. Controlled by `bandwidth` (kernel width).

**Complexity.** ~O(n²) per iteration — slow. `estimate_bandwidth` exists but is itself
O(n²)-ish.

**Use when** dimensionality is low, you want automatic cluster count from density modes,
and n is modest. Genuine home: image segmentation and tracking in computer vision, and
low-D mode-finding.

**Avoid when** n is large or d is high. **Over-recommended** in general tutorials: it's
slow, intensely `bandwidth`-sensitive (bandwidth implicitly sets the cluster count), and
rarely beats HDBSCAN or GMM on tabular data. Reach for it only in its niche.

---

## Scalability

### BIRCH

**Mechanism.** "Balanced Iterative Reducing and Clustering using Hierarchies." Makes one
pass over the data building a **CF-tree** (Clustering Feature tree). Each node stores
sufficient statistics — count, linear sum, squared sum — for the points it summarizes, so
it never holds all points in memory. After building the tree, it runs a global clustering
(e.g., agglomerative) on the leaf sub-clusters.

**Key parameters.** `threshold` (max radius of a leaf sub-cluster — the key knob; smaller
→ more, finer sub-clusters), `branching_factor`, `n_clusters` (final global step;
`None` returns the sub-clusters directly).

**Use when** data is too large for memory or arrives as a stream, features are numeric,
and you need an online/incremental method. Its real value is **compression**: use BIRCH
to summarize millions of points into thousands of CF sub-clusters, then run a higher-
quality method (GMM, Ward, HDBSCAN) on those summaries.

**Avoid when** clusters are non-spherical (the CF radius assumes roughly spherical
sub-clusters), data is high-dimensional (CF statistics degrade), or data is categorical
(numeric only). **Gotcha:** results are **order-sensitive** — the same data in a
different order can yield a different tree. Treat BIRCH as a scalability tool, not a
clustering philosophy.

---

## Graph / message-passing

### Spectral clustering

**Mechanism.** Build an affinity graph between points (k-NN graph or an RBF/Gaussian
kernel), form the graph **Laplacian**, take its smallest few eigenvectors as a new
low-dimensional embedding, then run k-means in that embedding. The eigen-embedding
unfolds manifold/connectivity structure into something a centroid method can split.

**Key parameters.** `n_clusters` (k, required), `affinity` (how the graph is built —
`nearest_neighbors` is usually more robust than `rbf`), kernel width / `n_neighbors`.

**Complexity.** O(n³) for the dense eigendecomposition (approximations like Nyström or
sparse k-NN graphs help). Practical to thousands–tens of thousands.

**Use when** clusters are defined by *connectivity*, not compactness — concentric
circles, two interleaving moons, manifolds where Euclidean distance lies. This is the
canonical right answer for those textbook shapes.

**Avoid when** n is large (cubic cost), or clusters are simply blobby (k-means is far
cheaper and just as good). **Gotcha:** the affinity graph construction is the whole
ballgame — a bad kernel width or neighbor count destroys results. You still must pick k
(the eigengap heuristic can suggest it).

### Affinity Propagation

**Mechanism.** Points exchange two kinds of real-valued messages — **responsibility**
(how well-suited point k is to be point i's exemplar) and **availability** (how
appropriate it is for i to choose k) — iterating until a stable set of **exemplars**
(actual data points) and their followers emerges. It does **not** require k; instead a
`preference` parameter (each point's a-priori suitability as an exemplar) implicitly
controls how many clusters form, and `damping` stabilizes the iteration.

**Complexity.** O(n²) time and memory (it materializes a similarity matrix). This caps it
at small–moderate n, hard.

**Use when** you specifically want exemplars (real representative points) *and* don't want
to choose k, on a modest dataset.

**Avoid when** n is large (the O(n²) wall), or you can pick k (k-medoids gives exemplars
more cheaply). **Gotchas:** tends to produce **many** clusters; sensitive to `preference`
and prone to non-convergence without enough `damping`. Like Mean Shift, it's
over-featured in tutorials relative to how often it's the right call.

---

## Geometry cheat sheet

The fastest way to predict whether a method will work is to ask what it assumes about
shape, size, density, and noise. Mismatched assumptions are the usual cause of "bad
clusters."

| Method | Cluster shape | Handles varying density | Handles different sizes | Labels noise | Needs k | Scales to large n | Assigns new points |
|---|---|---|---|---|---|---|---|
| k-means | spherical/convex | no | poorly | no | yes | yes | yes |
| k-medoids (PAM) | convex (any metric) | no | poorly | no | yes | no (O(n²)) | yes |
| Fuzzy c-means | spherical/convex | no | poorly | no (spreads it) | yes | moderate | yes |
| GMM | elliptical | somewhat | yes | no | yes (BIC) | moderate | yes |
| Agglomerative (Ward) | compact/spherical | no | moderate | no | cut tree | no (O(n²)) | no |
| Agglomerative (single) | arbitrary/elongated | somewhat | yes | no | cut tree | no | no |
| DBSCAN | arbitrary | **no** | yes | **yes** | no | yes (indexed) | no |
| HDBSCAN | arbitrary | **yes** | yes | **yes** | no | moderate | approx |
| OPTICS | arbitrary | **yes** | yes | yes | no | moderate | no |
| Mean Shift | arbitrary (modes) | somewhat | yes | somewhat | no | no (O(n²)) | yes (nearest mode) |
| BIRCH | spherical | no | moderate | no | optional | **yes (streaming)** | yes |
| Spectral | arbitrary/manifold | somewhat | moderate | no | yes | no (O(n³)) | no |
| Affinity Propagation | convex | no | moderate | no | no | no (O(n²)) | no |

Read "needs k" loosely: density methods trade k for density parameters that *implicitly*
set the cluster count — you're always choosing *something*. There is no parameter-free
clustering.
