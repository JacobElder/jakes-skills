---
name: dimensionality-reduction
description: >-
  Expert guidance for choosing, applying, validating, and interpreting dimensionality
  reduction methods — PCA, ICA, NMF, MDS, LDA/GDA, EFA/CFA, t-SNE, UMAP, PaCMAP, TriMap,
  PHATE, Isomap, LLE, and autoencoders/VAEs. Use this whenever the user wants to reduce
  dimensions, embed high-dimensional data, visualize a dataset in 2D/3D, "find structure"
  or latent factors, compress features for a downstream model, separate sources, or
  interpret a t-SNE/UMAP/PCA plot they already made. ALSO trigger when the user mentions
  any of these acronyms, says things like "reduce my features", "embed", "project to 2D",
  "latent factors/constructs", "factor analysis", "manifold", "low-dimensional
  representation", or asks whether clusters/distances in an embedding are real — even if
  they don't name a specific method. The single most valuable thing this skill does is
  stop people from misreading embeddings and from picking a method that answers the wrong
  question.
---

# Dimensionality Reduction

## The one idea that prevents most mistakes

"Dimensionality reduction" names three genuinely different jobs that get fatally conflated.
**Before recommending any method, force the question: which job is this?**

1. **Compression / feature extraction** — squeeze many features into fewer that retain
   signal for a *downstream model*. The new axes need not be human-interpretable. Success =
   downstream performance and variance/information retained. (PCA, ICA, NMF, autoencoders,
   random projection.)
2. **Visualization** — make a 2D/3D *picture for a human*. Success = the picture is honest
   about neighbourhood structure. This is the job where people lie to themselves the most.
   (t-SNE, UMAP, PaCMAP, TriMap, PHATE, MDS, plus PCA as the honest baseline.)
3. **Latent-variable measurement** — recover the *unobserved constructs that generated* the
   observed variables (a measurement model). Success = the model fits and the constructs are
   theoretically coherent. (EFA, then CFA to test it. **Not PCA.**)

A method that is excellent at one job can be actively misleading at another. The most common
real-world error is using a visualization method (t-SNE/UMAP) as if it were doing job 1 or 3 —
reading clustering, distances, and "discoveries" off a picture that was only ever meant to be
a picture.

When the user hasn't said which job they're in, ask, or state the assumption you're making
and why. Don't silently pick.

## Method selection

| You want to… | Reach for | Not | Why |
|---|---|---|---|
| Compress numeric features, keep it interpretable & fast | **PCA** | t-SNE/UMAP | Linear, deterministic, orthogonal axes ranked by variance; the default and a strong baseline. |
| Visualize cluster/neighbourhood structure in 2D | **UMAP or t-SNE** (after PCA→~30–50d) | PCA alone if it looks blobby | Nonlinear local structure; but treat output as a *picture*, validate quantitatively. |
| Visualize AND keep global layout trustworthy | **PaCMAP / TriMap**; or PCA | t-SNE | Benchmarks show t-SNE/UMAP global structure is weak; PaCMAP/TriMap do better; PCA best for global. |
| Genuinely preserve distances | **metric MDS** (or just PCA for Euclidean) | t-SNE/UMAP | Distances in t-SNE/UMAP are not meaningful; classical MDS on Euclidean = PCA anyway. |
| Find latent constructs behind survey/test items | **EFA** | PCA | Common-factor model separates shared from unique variance; PCA does not. |
| Test a hypothesized factor structure | **CFA** (SEM) | EFA on the same data | CFA is confirmatory hypothesis testing, not structure discovery. |
| Reduce dims using known class labels | **LDA** (linear) / **GDA** (kernel) | PCA | Supervised; maximizes class separation. Capped at (k−1) dims for k classes. |
| Separate mixed independent sources (EEG, audio) | **ICA** | PCA | ICA targets statistical independence/non-Gaussianity, not variance. |
| Decompose nonnegative parts (counts, spectra, topics) | **NMF** | PCA | Parts-based, additive, interpretable — but only valid for nonnegative data. |
| Learn a reusable nonlinear encoder / generative latent space | **autoencoder / VAE** | plain AE for small tabular data | Powerful for images/sequences; overkill and hard to validate on small tabular data. |
| Unfold a known curved manifold (swiss roll) | **Isomap / LLE** | PCA | Geodesic/local-linear manifold learning; fragile to noise and neighbour count. |
| Reduce **categorical / nominal / mixed-type** data | **MCA** (categorical), **FAMD / PCAmix** (mixed) | PCA on one-hot | PCA on dummy-coded categories distorts geometry; correspondence-analysis family is the right tool. |

Detailed treatment of each lives in the reference files (see end). Read the relevant one
before giving method-specific advice — don't wing the math.

### Can it embed new points? (out-of-sample transform)

A decision axis people forget until it bites them in production. Ask early whether the user needs
to apply the reduction to *future / held-out* data.

- **Has a reusable `transform` (fit once, apply forever):** PCA, ICA, NMF, LDA/GDA, UMAP,
  parametric autoencoders/VAEs, random projection, kernel PCA (via the learned mapping).
- **Must be refit on the combined data (no honest out-of-sample map):** classical/metric MDS,
  Isomap, LLE, spectral embedding, and **vanilla t-SNE**. (openTSNE adds an approximate
  `transform`; treat it as approximate, and never refit-per-batch and compare embeddings as if
  they shared a coordinate system.)

If the workflow is "train a model on reduced features and score new rows later," that alone rules
out half the manifold methods regardless of how pretty their plots are.

## Core principles (the opinionated part — this is where the value is)

These are strong claims on purpose. State them plainly; soften only when the user's specific
situation genuinely warrants it.

1. **t-SNE and UMAP are visualization tools, not analysis tools.** In their output, *cluster
   sizes are meaningless, distances between clusters are largely meaningless, and apparent
   density is an artifact* of the algorithm equalizing neighbourhoods. Do clustering, neighbour
   analysis, and distance comparisons in the *original* (or PCA-reduced) space — never on the
   2D embedding. The 2D plot is for the eyes, not for inference.

2. **"UMAP preserves global structure" is oversold.** Head-to-head benchmarks put UMAP only
   marginally ahead of t-SNE on global structure; PaCMAP and TriMap do better; PCA remains the
   gold standard for global geometry. If global layout matters, don't lean on UMAP to provide it.

3. **A single t-SNE/UMAP run is not a result.** These methods are stochastic and
   hyperparameter-sensitive (perplexity / n_neighbors, seed, init). Vary them. If your
   conclusion flips when you change the seed or perplexity, the conclusion was an artifact.
   Random data can look clustered at low perplexity.

4. **Never select a method or tune hyperparameters by how "nice" the plot looks.** That is
   circular: you will reliably find the settings that show you the structure you hoped for.
   Tune and compare with *quantitative neighbour-preservation metrics* instead
   (see Validation below).

5. **Always PCA-reduce to ~30–50 dimensions before running t-SNE/UMAP** on
   high-dimensional data. It denoises, speeds things up by an order of magnitude, and is
   standard practice — even critics of these methods do it.

6. **PCA is not EFA, and they are not interchangeable** — despite the fact that SPSS's "factor
   analysis" menu defaults to PCA. PCA has no error term and no common-factor model: it
   repackages *all* variance (shared + unique + noise) into components. EFA models only the
   *shared* variance as coming from latent factors. If the question is "what underlying
   constructs explain the correlations among my items?", that is EFA. If it's "give me fewer
   axes that retain variance," that is PCA.

7. **CFA is not exploratory dimensionality reduction at all.** It is hypothesis testing inside
   structural equation modeling: you specify which items load on which factors *first*, then
   test fit (CFI, TLI, RMSEA, SRMR). Don't reach for CFA to "discover" structure, and don't run
   EFA and CFA on the *same* sample — that's double-dipping. Explore on one split, confirm on another.

8. **LDA is supervised and capped at (k−1) components** for k classes (a 3-class problem gives
   you at most 2 LDA dimensions). It is *not* a drop-in for PCA on unlabeled data. It also breaks
   under the small-sample-size problem (when features ≥ samples the within-class scatter matrix
   is singular) — use regularized LDA or PCA-then-LDA. **GDA** = kernel/generalized LDA for
   nonlinear class boundaries, and it inherits and amplifies the same small-sample issues.

9. **Match the method to the data's structure AND type, not its popularity.** ICA needs
   non-Gaussian independent sources; NMF needs nonnegativity; Isomap/LLE need a genuine smooth
   manifold and are noise-fragile. And check the *data type* before anything: PCA/t-SNE/UMAP assume
   meaningful numeric distances, so running them on one-hot-encoded **categorical** data (or on
   Likert items treated as continuous without thought) produces confident nonsense — use the
   correspondence-analysis family instead (MCA for categorical, FAMD/PCAmix for mixed). Using any
   of these off-label is a silent correctness bug, not a style choice.

10. **Autoencoders are usually overkill for tabular DR.** A plain undercomplete autoencoder with
    linear activations *is* PCA; with nonlinear ones it's a harder-to-validate nonlinear PCA.
    Reach for them when you need a reusable parametric encoder, or for images/sequences, or a
    VAE when you specifically want a probabilistic/generative latent space. Don't deploy a deep
    net where PCA + UMAP already answers the question.

11. **Standardize before any variance- or distance-based method** (PCA, MDS, t-SNE, UMAP, k-NN
    metrics) unless the features are already on a common scale — otherwise the highest-variance
    *unit* dominates, not the highest-variance *signal*. (Exception: don't blindly standardize
    count/nonnegative data headed into NMF.)

## Validation is mandatory, not optional

Every embedding you produce or interpret should be checked quantitatively. The skill bundles a
tested script for exactly this so you don't reinvent it each time:

```bash
python scripts/dr_diagnostics.py --hd X.npy --ld embedding.npy [--labels y.npy] --k 15
```

It reports **trustworthiness** (does the embedding invent false neighbours?), **continuity**
(does it tear true neighbours apart?), **kNN overlap**, and the **Shepard correlation** between
high-dim and low-dim pairwise distances — the quantitative form of "you can't read distances off
this plot." With labels it also reports k-NN accuracy in *both* spaces; if accuracy is much higher
in the embedding than in the original space, treat that as a red flag for manufactured separation,
not a success. See `references/validation-and-diagnostics.md` for what good values look like and
the circularity traps to avoid.

Use `from dr_diagnostics import diagnose` to call it in-process. Prefer running this script over
hand-rolling metrics — it's faster and consistent across analyses.

## Default workflow

When asked to "reduce dimensions" or "embed/visualize this data" without further constraints:

1. Clarify the job (compression vs visualization vs latent measurement). State your assumption
   if the user is silent.
2. Inspect & preprocess: handle missing values; standardize (or not, per principle 11).
3. **Always run PCA first** — as the answer (compression), as preprocessing (→30–50d before
   nonlinear methods), and as a sanity check. Report the scree / cumulative explained variance.
4. If visualizing and PCA looks uninformative, run a nonlinear method — and run it across
   ≥2 seeds and ≥2 perplexity/n_neighbors values.
5. **Validate** with `dr_diagnostics.py`. Report the numbers, not just the picture.
6. Interpret with the caveats above stated explicitly. Do downstream clustering/stats in the
   original or PCA space.

## Reference files — read the relevant one before method-specific advice

- `references/linear-projections.md` — PCA, ICA, NMF, LDA, GDA, MDS, random projection: math,
  assumptions, failure modes, sklearn usage.
- `references/manifold-embeddings.md` — t-SNE, UMAP, PaCMAP, TriMap, PHATE, Isomap, LLE,
  autoencoders/VAEs: how they work, hyperparameters that matter, interpretation traps.
- `references/latent-variable-models.md` — EFA, CFA, the common-factor model, rotation, factor
  retention, fit indices, and the PCA-vs-EFA distinction in depth.
- `references/validation-and-diagnostics.md` — trustworthiness/continuity, kNN preservation,
  Shepard diagrams, co-ranking matrix, label-based checks, and the circularity pitfalls.

## A note on ambiguous acronyms in requests

- **GDA** almost always means **Generalized Discriminant Analysis** (kernel LDA; Baudat &
  Anouar, 2000). It can occasionally mean *Gaussian* Discriminant Analysis (the generative
  classifier, LDA/QDA family). If context is unclear, ask.
- **MVR** is not standard DR shorthand. The most charitable DR-relevant readings are
  *reduced-rank regression* or *PLS (Partial Least Squares)* — supervised projection toward a
  continuous target, i.e. the regression analog of LDA. Confirm with the user rather than guessing.
- Treat "or whatever else" requests as license to add genuinely appropriate methods
  (e.g. spectral embedding, kernel PCA, diffusion maps, SOM) — not to pad the list with
  near-duplicates.
