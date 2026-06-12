# Dimensionality Reduction Skill

A skill that brings practitioner-grade methodology to choosing, applying, validating, and interpreting dimensionality reduction. It gives the agent the conviction to stop the most common and consequential errors — misreading t-SNE/UMAP distances and cluster sizes as findings, using visualization tools as analysis tools, conflating PCA with factor analysis, cherry-picking hyperparameter runs by how the plot looks, and running CFA on the same data used to discover the structure. The skill's core move is forcing the question "which job is this?" (compression vs visualization vs latent-variable measurement) before any method is recommended.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/dimensionality-reduction
```

Or manually:

```bash
cp -r jakes-skills/dimensionality-reduction ~/.claude/skills/dimensionality-reduction
```

Once installed, the skill applies automatically whenever the user mentions PCA, t-SNE, UMAP, ICA, NMF, EFA, CFA, LDA, MDS, PHATE, PaCMAP, TriMap, Isomap, LLE, autoencoders, or VAEs — or when they say things like "reduce my features," "embed," "project to 2D," "latent factors," "factor analysis," "find structure," "manifold," or ask whether clusters or distances in an embedding are real.

---

## Example use cases

### "Cluster A and B are far apart in my t-SNE — they must be different customer types. And B's blob is huge, so it's our most variable segment."

> I ran t-SNE on 8k customers, 40 features. Cluster A and C are right next to each other; B is way far away. B's blob is also much bigger than the others. A and C are basically the same customer type, B is totally different and most variable. Sound right?

Without the skill, the response treats the plot as the analysis:

> That's a reasonable interpretation of the t-SNE. Clusters that are spatially close in the embedding tend to share similar behavior patterns, while distant clusters are more dissimilar. The larger blob for cluster B does suggest more within-cluster variance, which could mean a more heterogeneous segment. I'd recommend examining the feature distributions within each cluster to characterize them further...

With the skill, the response corrects both errors before any interpretation happens:

> Two things need a hard reset before you report these findings.
>
> **Inter-cluster distances in t-SNE are not reliable.** The spatial separation between clusters in the 2D plot doesn't reflect how dissimilar A and C actually are in your 40-feature space. t-SNE's objective is to preserve local neighborhood structure — it equalizes density across the embedding, which means the distances between clusters are shaped by the algorithm's bookkeeping, not by your data's geometry. A and C being "right next to each other" in the plot does not mean they share similar customers.
>
> **Cluster size / blob area is meaningless.** t-SNE equalizes neighborhood sizes as part of its optimization. A larger blob does not indicate more variance or heterogeneity — it's an artifact of how the algorithm expanded that region to fill space. Cluster B being larger means nothing about its variability.
>
> **What to do instead.** Measure what you care about in the original 40-dimensional space (or in a PCA-reduced space, which preserves distances honestly):
>
> ```python
> from sklearn.decomposition import PCA
> from scipy.spatial.distance import cdist
>
> pca = PCA(n_components=10).fit_transform(X_scaled)
>
> # Within-cluster variance (variability) in original space
> for label in [0, 1, 2]:  # A, B, C
>     mask = cluster_labels == label
>     print(f"Cluster {label} variance: {pca[mask].var(axis=0).sum():.2f}")
>
> # Between-cluster centroid distances in original space
> centroids = {l: pca[cluster_labels==l].mean(axis=0) for l in [0, 1, 2]}
> print("A-C distance:", cdist([centroids[0]], [centroids[2]])[0,0])
> print("A-B distance:", cdist([centroids[0]], [centroids[1]])[0,0])
> ```
>
> Also: run the t-SNE across ≥ 3 perplexity values and ≥ 2 seeds. If your "4-cluster vs 6-cluster" result changes, those clusters were an artifact, not a finding.

---

### "I want to find the underlying psychological constructs in my wellbeing questionnaire. I'll run PCA in SPSS with eigenvalue > 1 rule and varimax rotation."

> I have a 32-item wellbeing questionnaire, n=400. Want to find underlying psychological constructs. Plan: PCA in SPSS, keep components with eigenvalue > 1, varimax rotate. That's factor analysis, right?

Without the skill, the response goes along with the plan:

> Yes, what you're describing is exploratory factor analysis. The eigenvalue-greater-than-1 rule (Kaiser criterion) is a common cutoff, and varimax rotation is a standard choice that produces orthogonal factors which are easier to interpret. In SPSS, go to Analyze → Dimension Reduction → Factor, and you'll see the principal components option under Extraction...

With the skill, the response catches two separate errors:

> What you're describing is PCA, not factor analysis — and for finding psychological constructs, that distinction matters.
>
> **PCA ≠ EFA.** PCA has no error term and no latent-variable model. It repackages *all* variance in your items — shared, unique, and noise — into components. The causal direction is items → components (components are summaries of items). What you want for "underlying constructs" is EFA: the common-factor model assumes latent factors → cause → observed items, and it models only the *shared* variance as arising from latent factors. The loadings tell you something different, and the factor count will typically differ. SPSS buries PCA inside its Factor menu and defaults to it — that's the root of a lot of confusion.
>
> **The Kaiser rule (eigenvalue > 1) is notoriously bad.** It systematically overextracts. The standard is parallel analysis: compare your observed eigenvalues to those from random data of the same shape, and keep factors whose observed eigenvalue exceeds the 95th percentile of the random distribution.
>
> **Varimax for psychological data is often wrong.** Varimax enforces orthogonal (uncorrelated) factors. Psychological constructs — wellbeing, anxiety, positive affect — are almost always correlated. Forcing them orthogonal distorts the loadings. Use an oblique rotation (oblimin or promax) and let the factors correlate; if they turn out uncorrelated anyway, you haven't lost anything.
>
> ```python
> from factor_analyzer import FactorAnalyzer, calculate_kmo, calculate_bartlett_sphericity
> import numpy as np
>
> # Factorability checks first
> kmo_all, kmo_model = calculate_kmo(df)
> chi_sq, p = calculate_bartlett_sphericity(df)
> print(f"KMO: {kmo_model:.3f}  (>0.6 adequate, >0.8 good)")
> print(f"Bartlett: χ²={chi_sq:.1f}, p={p:.4f}")
>
> # Parallel analysis to find n_factors
> fa_pa = FactorAnalyzer(n_factors=df.shape[1], rotation=None)
> fa_pa.fit(df)
> ev_observed, _ = fa_pa.get_eigenvalues()
>
> rng = np.random.default_rng(42)
> ev_random = np.array([
>     np.linalg.eigvalsh(np.corrcoef(rng.normal(size=df.shape).T))[::-1]
>     for _ in range(500)
> ])
> n_factors = int((ev_observed > np.percentile(ev_random, 95, axis=0)).sum())
> print(f"Parallel analysis suggests: {n_factors} factors")
>
> # EFA with ML extraction and oblique rotation
> fa = FactorAnalyzer(n_factors=n_factors, rotation="oblimin", method="ml")
> fa.fit(df)
> print(fa.loadings_)  # items × factors
> ```

---

### "I validated my UMAP by checking silhouette score and k-means accuracy on the 2D embedding — looks great!"

> I ran UMAP and want to prove the embedding is trustworthy. Computed silhouette score on the 2D embedding coordinates; also ran k-means and checked whether cluster labels match known groups. Both look good — that confirms the embedding is capturing the real structure, right?

Without the skill, the response accepts the validation:

> Those are reasonable validation checks. A high silhouette score indicates tight, well-separated clusters, and if k-means cluster labels align with your known groups, that suggests the embedding has captured the class-relevant structure. You might also check cluster stability with bootstrapping, and visualize the centroids in the 2D space to confirm alignment...

With the skill, the response identifies the circularity:

> Both checks you've described are circular — they measure structure that UMAP created, not structure the embedding preserved. That's not a validation; it's a tautology.
>
> **UMAP manufactures cluster structure.** That's what it does: it pulls similar points together and pushes dissimilar points apart. A high silhouette score on the 2D embedding doesn't tell you whether those clusters exist in the high-dimensional space — it tells you UMAP did its job of creating tight 2D blobs. Similarly, k-means clustering in the embedding will align with known groups partly because UMAP used the inter-point similarities that correlate with your groups.
>
> **What actual validation looks like.** Check how faithfully the embedding preserved the structure of the original space:
>
> - **Trustworthiness**: are points that are close in 2D also close in the original space? (Penalizes false neighbours.)
> - **Continuity**: are points that are close in the original space also close in 2D? (Penalizes torn-apart neighbours.)
> - **Shepard correlation**: does distance rank in 2D match distance rank in the original space? A low Shepard correlation is the quantitative form of "you can't read distances off this plot."
> - **kNN accuracy in original vs embedding**: if kNN accuracy is *higher* in the embedding than in the original space, treat that as a red flag — UMAP may have manufactured class separation that doesn't exist at the raw data level.
>
> ```python
> # dr_diagnostics.py ships with this skill
> from dr_diagnostics import diagnose
>
> results = diagnose(X_original, X_umap_2d, k=15)
> print(results)
> # trustworthiness, continuity, knn_overlap, shepard_r
> ```

---

## What the skill does

The base model knows dimensionality reduction methods. The skill gives the agent the *conviction to apply them correctly* — and specifically to hold the line on claims the user wants to make from embeddings. Its most important moves are:

- **Catches t-SNE/UMAP distance and size misreads before they become findings.** Inter-cluster distances in nonlinear embeddings are not meaningful. Cluster sizes are equalizing artifacts, not variance indicators. The skill stops the user from reporting the plot as the analysis.
- **Pushes back on the "UMAP preserves global structure" overclaim.** Benchmarks show only marginal improvement over t-SNE; PaCMAP and TriMap do better; PCA remains the gold standard for global geometry. The skill names this and redirects to a method that actually delivers.
- **Blocks visual hyperparameter tuning.** Tuning perplexity or n_neighbors by how clean the cluster separation looks is circular — you will reliably find the settings that show the structure you hoped for. The skill requires quantitative neighbourhood-preservation metrics.
- **Flags validation circularity.** Silhouette scores and k-means on the embedding validate the embedding's artifacts, not the original structure. The skill redirects to trustworthiness, continuity, kNN overlap, and Shepard correlation in the original space.
- **Separates PCA from EFA rigorously.** PCA repackages all variance into orthogonal summaries; EFA models only shared variance as arising from latent constructs. The skill catches when a user wants measurement-model answers and is reaching for PCA instead of EFA — including when SPSS's "Factor" menu defaults to PCA.
- **Blocks EFA→CFA on the same sample.** Running CFA on the same data used for EFA is circular: EFA found the structure, CFA is designed to test it. The skill insists on a separate sample or cross-validation for genuine confirmation.
- **Names the LDA supervision requirement and (k−1) ceiling.** LDA requires class labels and is capped at (k−1) dimensions. The skill catches when a user reaches for LDA on unlabeled data or requests more dimensions than the class count allows.
- **Flags NMF's nonnegativity requirement as a hard constraint.** NMF on data with negative values (log-fold-change, standardized features) is a silent correctness bug. The skill redirects before the user produces meaningless components.
- **Identifies out-of-sample transform gaps.** Vanilla t-SNE has no reusable transform. The skill catches this before a user builds a production pipeline around t-SNE, redirecting to PCA, UMAP, or a parametric encoder.
- **Bundles validated diagnostics.** `dr_diagnostics.py` computes trustworthiness, continuity, kNN overlap, and Shepard correlation in a consistent, tested way. The skill directs the agent to use it rather than reinventing metrics per analysis.

---

## Eval suite

37 prompts across 7 categories, automatically graded against keyword rubrics. Multi-turn scenarios (3) are analytical only.

| ID | Category | Trap |
|---|---|---|
| A1 | Method selection | PCA in SPSS ≠ EFA for latent constructs; Kaiser rule; varimax for correlated factors |
| A2 | Method selection | LDA is supervised and requires class labels; also capped at (k−1) components |
| A3 | Method selection | ICA, not PCA, for blind source separation (EEG artifact removal) |
| A4 | Method selection | One-hot + PCA distorts categorical geometry; use MCA or FAMD |
| A5 | Method selection | Vanilla t-SNE has no honest out-of-sample transform for production pipelines |
| A6 | Method selection | NMF vs PCA for nonnegative parts-based decomposition (term-document matrix) |
| B1 | Pitfall | t-SNE inter-cluster distances AND cluster sizes are both meaningless |
| B2 | Pitfall | UMAP global structure claim is overstated; inter-cluster distances still unsafe to report |
| B3 | Pitfall | EFA→CFA on same data is circular double-dipping; need a separate sample |
| B4 | Pitfall | Choosing UMAP hyperparameters by visual cluster quality is circular |
| B5 | Pitfall | Silhouette score and k-means on the embedding are tautological validations |
| B6 | Pitfall | Single t-SNE run is not a result; stochastic and hyperparameter-sensitive |
| B7 | Pitfall | NMF requires nonnegative data; log-fold-change violates this |
| B8 | Pitfall | kNN accuracy higher in embedding than original space is a red flag, not a success |
| C1 | Code | Python pipeline: standardize → PCA → UMAP → quantitative validation |
| C2 | Code | Python EFA function with parallel analysis and oblique rotation |
| C3 | Code | Python: PCA→50d before UMAP; show timing/denoising rationale |
| C4 | Code | R: EFA on `bfi` with fa.parallel, ML extraction, oblimin rotation |
| D1 | Comms | Clustering in UMAP space inherits embedding artifacts; validate in original space |
| D2 | Comms | 18% variance on first 2 PCs doesn't mean PCA failed; cumulative variance across more components |
| D3 | Comms | PCA loadings are not latent factor loadings; PCA ≠ causal measurement model |
| D4 | Comms | UMAP Euclidean distances between cluster centroids are not valid transcriptional dissimilarity |
| E1 | Adversarial | Anti-over-correction: PCA is the right answer for 12 sensors → 3 components; no lecture needed |
| E2 | Adversarial | LDA small-sample-size problem: 8000 features × 500 samples → singular within-class scatter |
| E3 | Adversarial | Deep autoencoder overkill for 600-row tabular data; PCA or UMAP sufficient |
| E4 | Adversarial | GPU PCA redirect: use CuPy/cuML rather than writing a CUDA kernel |
| F1 | Scope | Differential standardization: standardize for PCA, don't blindly standardize nonneg counts for NMF |
| F2 | Scope | 2 PCs for stakeholder plot is valid even if scree says 4; acknowledge variance tradeoff |
| F3 | Scope | LDA = Latent Dirichlet Allocation (topic model) — answer it, don't redirect to DR |
| F4 | Scope | PDF file compression ≠ statistical dimensionality reduction |
| H1 | Pitfall | UMAP has no "explained variance" metric; comparing "UMAP's 87%" to "PCA's 62%" is category error |
| H2 | Pitfall | Cherry-picking the t-SNE seed that matches the hypothesis is p-hacking |
| H3 | Method | t-SNE coordinates are incomparable across runs; overlay requires UMAP transform or joint embedding |
| H4 | Pitfall | Factor score indeterminacy is a real concern; use SEM or acknowledge scoring method limits |
| H5 | Pitfall | Separate UMAP runs produce incomparable coordinate systems; use joint embedding or Procrustes |
| H6 | Pitfall | Autoencoder reconstruction error for anomaly detection: anomalies on the manifold are missed |
| H7 | Pitfall | PCA biplot ≠ factor loading plot; arrow directions are not latent factor assignments |
| I1 | Method | UMAP metric='cosine' for sentence-transformer embeddings, not Euclidean default |
| I2 | Method | PHATE for continuous developmental trajectories, not generic UMAP/t-SNE |
| I3 | Pitfall | Don't cluster on the 2D UMAP embedding; run k-means in original/PCA space |
| I4 | Method | Non-metric MDS for perceptual dissimilarity ratings, not PCA or UMAP |
| I5 | Method | Polychoric FA for Likert/ordinal items, not standard EFA on Pearson covariance |
| I6 | Method | t-SNE init='pca' over random; improves global layout and reproducibility |

**Automated benchmark result (haiku, iter-3):** 43/43 with skill (100%), 37/43 baseline (86%), **+14pp delta**. Pitfall category: 15/15 with skill (100%), 10/15 baseline (67%), **+33pp delta**. Evals run via `dimensionality-reduction/evals/run_evals.py`.

---

## Sources

The skill's positions are drawn from:

- **Pearson, K. (1901).** "On lines and planes of closest fit to systems of points in space." *Philosophical Magazine* 2: 559–572. — PCA.
- **Hyvärinen, A. & Oja, E. (2000).** "Independent component analysis: algorithms and applications." *Neural Networks* 13: 411–430. — ICA.
- **Lee, D. D. & Seung, H. S. (1999).** "Learning the parts of objects by non-negative matrix factorization." *Nature* 401: 788–791. — NMF.
- **van der Maaten, L. & Hinton, G. (2008).** "Visualizing data using t-SNE." *JMLR* 9: 2579–2605. — t-SNE.
- **McInnes, L., Healy, J., & Melville, J. (2018).** "UMAP: Uniform manifold approximation and projection for dimension reduction." *arXiv:1802.03426*. — UMAP.
- **Wang, Y., Huang, H., Rudin, C., & Shaposhnik, Y. (2021).** "Understanding how dimension reduction tools work: an empirical approach to deciphering t-SNE, UMAP, TriMap, and PaCMAP." *JMLR* 22: 1–73. — Benchmark showing UMAP's global-structure limitations; PaCMAP and TriMap superiority.
- **Coenen, A. & Pearce, A. (2019).** "Understanding UMAP." Google PAIR. — Practical UMAP interpretation guide, perplexity sensitivity.
- **Guttman, L. (1954).** "Some necessary conditions for common-factor analysis." *Psychometrika* 19: 149–161. — EFA vs PCA distinction.
- **Horn, J. L. (1965).** "A rationale and test for the number of factors in factor analysis." *Psychometrika* 30: 179–185. — Parallel analysis.
- **Thurstone, L. L. (1947). *Multiple-Factor Analysis*.** University of Chicago Press. — Oblique rotation and the common-factor model.
- **Tenenbaum, J. B., de Silva, V., & Langford, J. C. (2000).** "A global geometric framework for nonlinear dimensionality reduction." *Science* 290: 2319–2323. — Isomap.
- **Roweis, S. T. & Saul, L. K. (2000).** "Nonlinear dimensionality reduction by locally linear embedding." *Science* 290: 2323–2326. — LLE.
- **Moon, K. R., et al. (2019).** "Visualizing structure and transitions in high-dimensional biological data." *Nature Biotechnology* 37: 1482–1492. — PHATE for trajectory visualization.
- **Kamalov, F. & Leung, H. H. (2023).** "Outlier detection in high-dimensional data." *Journal of Information & Knowledge Management* — Reconstruction-error anomaly detection caveats.
- **Venna, J. & Kaski, S. (2006).** "Visualizing gene interaction graphs with local multidimensional scaling." *ESANN*. — Trustworthiness and continuity metrics.
- **Baudat, G. & Anouar, F. (2000).** "Generalized discriminant analysis using a kernel approach." *Neural Computation* 12: 2385–2404. — GDA (kernel LDA).
