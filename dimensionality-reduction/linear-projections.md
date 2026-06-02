# Linear projection methods

Methods that produce the embedding as a (possibly supervised) linear map of the inputs, or via
an eigen/SVD decomposition. Deterministic, fast, and far more interpretable than manifold
methods — which is exactly why they should usually be tried first.

Contents: PCA · Kernel PCA · ICA · NMF · LDA · GDA · MDS · Random projection.

---

## PCA — Principal Component Analysis

**What it does.** Finds orthogonal directions of maximum variance via the eigendecomposition of
the covariance matrix (equivalently the SVD of the centered data). Components are ordered by
explained variance; keep the top *d*.

**Assumes.** Variance = signal; linear structure; (for interpretation) roughly elliptical data.
Sensitive to feature scale → **standardize** unless features share units.

**Strengths.** Deterministic, unique (up to sign), fast, invertible/reconstructable, ranked axes,
honest about global structure and distances. A strong baseline and the correct preprocessing step
before t-SNE/UMAP.

**Failure modes.** Misses nonlinear manifolds (a swiss roll defeats it). High-variance noise can
masquerade as a top component. Components are linear combinations of *all* features, so "loadings"
are not factors (see EFA). Outliers tilt the axes — consider robust PCA.

**Choosing d.** Cumulative explained variance (e.g. 90–95%), the scree "elbow," or parallel
analysis. For downstream compression, pick by downstream CV performance, not a variance rule.

**sklearn.** `PCA(n_components=...)`, `.explained_variance_ratio_`. For sparse/large data,
`TruncatedSVD` (also the right tool for LSA on text).

**Kernel PCA.** PCA in a feature space induced by a kernel (RBF, poly) → captures nonlinear
structure. Cost: no easy inverse, kernel/bandwidth tuning, O(n²) memory. Useful but often
superseded by UMAP for visualization.

---

## ICA — Independent Component Analysis

**What it does.** Decomposes a signal into components that are *statistically independent* and
maximally non-Gaussian (FastICA maximizes negentropy). The classic use is blind source separation:
the cocktail-party problem, separating EEG/MEG sources, removing artifacts.

**vs PCA.** PCA decorrelates (second-order, orthogonal, variance-ranked). ICA targets full
statistical independence (higher-order) and the components are **not ordered** and have
**sign/scale ambiguity**. PCA whitening is typically a preprocessing step inside ICA.

**Assumes.** Sources are independent and at most one is Gaussian (it cannot separate Gaussian
sources — independence is unidentifiable there). Linear mixing.

**Use it when.** You believe the observed data is a linear mixture of independent generators and
you want the generators — not when you just want generic compression. Off-label use as a
variance-reduction step is usually a mistake; use PCA.

**sklearn.** `FastICA(n_components=...)`. Standardize/whiten first; expect to fix component
order/sign manually.

---

## NMF — Non-negative Matrix Factorization

**What it does.** Factorizes a **non-negative** matrix X ≈ W·H with W, H ≥ 0. The non-negativity
forces an *additive, parts-based* representation (Lee & Seung): facial parts, document topics,
spectral signatures, audio sources.

**Strengths.** Interpretable, parts-based components; natural for counts, intensities, term-document
matrices (topic modeling), spectra, gene expression.

**Constraints / cautions.** Requires non-negative input — never standardize into negatives first.
**Not unique** and **initialization-dependent**: different seeds give different factorizations, so
fix and report the seed and consider multiple restarts. Choosing the rank (number of components) is
its own problem — use reconstruction error elbow, stability/consensus across restarts, or downstream
task performance.

**sklearn.** `NMF(n_components=..., init='nndsvda', random_state=...)`. `init` matters; `nndsvd*`
gives more deterministic, sparser starts than random.

---

## LDA — Linear Discriminant Analysis (Fisher)

**What it does.** **Supervised** projection that maximizes between-class scatter relative to
within-class scatter — pulls classes apart and squeezes each class together. Solves a generalized
eigenproblem on the scatter matrices.

**Hard ceiling.** At most **(k − 1)** components for k classes. Two classes → a single LDA axis.
This surprises people who expect a PCA-like menu of components. If you need more axes, LDA is the
wrong tool.

**Assumes.** Each class roughly Gaussian with a *shared* covariance (QDA relaxes the shared-covariance
assumption at the cost of more parameters). Linear class boundaries.

**Small-sample-size (SSS) problem.** When #features ≥ #samples, the within-class scatter matrix is
singular and plain LDA fails. Fixes: regularized/shrinkage LDA, PCA-then-LDA, or pseudo-inverse
variants. This is *the* classic LDA gotcha in high-dim domains (genomics, face recognition).

**Not for unlabeled data.** LDA needs labels. If someone asks to "use LDA to reduce my unlabeled
data," that's a category error — redirect to PCA (unsupervised) and clarify the goal. (Also beware:
"LDA" can mean *Latent Dirichlet Allocation*, a topic model — disambiguate.)

**sklearn.** `LinearDiscriminantAnalysis(n_components=..., solver='eigen', shrinkage='auto')` for
the regularized version.

---

## GDA — Generalized / Kernel Discriminant Analysis

**What it does.** The kernel extension of LDA (Baudat & Anouar, 2000; a.k.a. kernel Fisher
discriminant). Maps inputs into a kernel feature space where classes that aren't linearly separable
become separable, then does LDA there. Solves a kernelized generalized eigenproblem.

**Use it when.** Class structure is nonlinear and you have labels and want a discriminative
low-dim representation.

**Cautions.** Inherits LDA's (k−1) ceiling-in-spirit and **amplifies** the small-sample-size problem
(the kernel space is high/infinite-dimensional). Needs kernel + bandwidth tuning and regularization.
O(n²) in samples. Often a research/specialist choice rather than a default.

**Naming.** "GDA" usually = Generalized Discriminant Analysis (this). Occasionally "Gaussian
Discriminant Analysis," the generative classifier (the LDA/QDA modeling view). Confirm if unclear.

---

## MDS — Multidimensional Scaling

**What it does.** Places points in low-dim space so that pairwise *distances* match the original
dissimilarities as closely as possible (minimizes "stress").

- **Classical (metric) MDS** on Euclidean distances is **mathematically equivalent to PCA** — so if
  your dissimilarity is Euclidean, just run PCA. MDS earns its keep when you have a *non-Euclidean*
  or precomputed dissimilarity matrix (edit distance, travel time, perceptual dissimilarity ratings).
- **Non-metric MDS** preserves only the *rank order* of dissimilarities — for ordinal/judgment data.

**Why it matters here.** MDS is the honest method for "I genuinely care about distances." Single-cell
and many ML practitioners avoid it because it often fails to show crisp clusters — but that "failure"
is partly MDS being truthful that the clusters aren't as distance-separated as a t-SNE plot implies.

**Cautions.** O(n²)+ memory/time; sensitive to the chosen dissimilarity; local minima in the
non-metric/SMACOF optimization (use multiple inits). Isomap (see manifold reference) is MDS on
*geodesic* distances.

**sklearn.** `MDS(n_components=..., dissimilarity='precomputed' | 'euclidean', n_init=...)`.

---

## Random projection — the cheap baseline worth knowing

By the Johnson–Lindenstrauss lemma, projecting onto random directions approximately preserves
pairwise distances with high probability, in time independent of the data's structure. For very
high-dimensional data where you just need a fast distance-preserving compression (e.g. before
approximate nearest neighbours), `GaussianRandomProjection` / `SparseRandomProjection` can beat PCA
on speed with little quality loss. Mention it when the user's bottleneck is scale, not interpretability.

---

## Categorical & mixed data — CA, MCA, FAMD/PCAmix

The single most common silent error in applied DR: one-hot-encoding categorical variables and
running PCA on them. PCA assumes meaningful numeric variance/distance; on dummy variables the
"variance" is an artifact of category frequencies, and the geometry is meaningless. There is a
proper family for this.

- **Correspondence Analysis (CA).** For a two-way **contingency table** (counts of one categorical
  variable cross-tabulated against another). Decomposes the χ² departure from independence; rows and
  columns get coordinates in the same space (a biplot). The categorical analog of PCA for count tables.
- **Multiple Correspondence Analysis (MCA).** The generalization to **many categorical variables**
  (e.g. a survey of all-nominal items). This is what to use instead of "PCA on one-hot."
- **FAMD (Factor Analysis of Mixed Data) / PCAmix.** For datasets with **both** numeric and
  categorical columns. It balances the contributions of the two types (standardizing numerics,
  scaling categoricals appropriately) so neither dominates by accident — strictly better than
  hand-mixing standardized numerics with dummy variables into one PCA.

**Likert / ordinal caution.** Treating ordinal Likert responses as continuous and PCA-ing them is
common and sometimes defensible (with enough categories, ~5+), but the principled routes are
**polychoric-correlation-based factor analysis** (see latent-variable-models.md) or ordinal/optimal-
scaling methods. At minimum, flag the assumption rather than making it silently.

**Tools.** Python: `prince` (CA/MCA/FAMD), `light-famd`. R: `FactoMineR` (`CA`, `MCA`, `FAMD`) and
`factoextra` for visualization — the most mature implementations.

---

## Sources / further reading

- PCA: Jolliffe, *Principal Component Analysis* (2002); Jolliffe & Cadima, "PCA: a review and recent
  developments," *Phil. Trans. R. Soc. A* (2016).
- ICA: Hyvärinen & Oja, "Independent Component Analysis: Algorithms and Applications," *Neural
  Networks* (2000); FastICA.
- NMF: Lee & Seung, "Learning the parts of objects by non-negative matrix factorization," *Nature*
  (1999).
- LDA / SSS problem: Fisher (1936); Krzanowski et al. and the regularized/PCA-then-LDA literature on
  the small-sample-size singularity.
- GDA: Baudat & Anouar, "Generalized Discriminant Analysis Using a Kernel Approach," *Neural
  Computation* (2000).
- CA/MCA/FAMD: Greenacre, *Correspondence Analysis in Practice* (3rd ed., 2017); FactoMineR docs.
- Random projection: Johnson–Lindenstrauss lemma (1984); Achlioptas (2003).
