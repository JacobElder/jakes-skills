"""
Eval harness for the dimensionality-reduction skill.

30 prompts across 6 runnable categories (A–F) plus 3 multi-turn scenarios (G).

  A (6)  — method selection from natural language
  B (8)  — pitfall detection (misinterpretation / wrong-tool traps)
  C (4)  — code correctness / pipeline quality
  D (4)  — communication and interpretation
  E (4)  — adversarial and boundary cases (including anti-over-correction)
  F (4)  — scope and trigger boundary (correct refusals / redirects)

  G (3)  — multi-turn dialogues (analytical only; not automated here)

Automated scoring uses keyword matching against rubrics derived from SKILL.md and the
reference files.  The rubric is intentionally objective: assertions that are checkable by
a keyword or substring test, not judgement calls.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Eval:
    id: str
    prompt: str
    category: str
    rubric_keywords: list[str] = field(default_factory=list)
    rubric_must_have_all: list[str] = field(default_factory=list)
    rubric_must_not_have: list[str] = field(default_factory=list)
    notes: str = ""


EVALS: list[Eval] = [

    # ── Category A: Method selection ─────────────────────────────────────────

    Eval(
        id="A1",
        prompt=(
            "I have a 32-item wellbeing questionnaire, n=400. I want to find the underlying "
            "psychological constructs people are responding to. My plan: run PCA in SPSS, "
            "keep components with eigenvalue greater than 1, varimax rotate, done. "
            "That's factor analysis, right?"
        ),
        category="method",
        rubric_must_have_all=["efa", "pca"],
        rubric_keywords=["exploratory factor", "factor analysis", "common factor",
                         "principal axis", "maximum likelihood", "ml extraction",
                         "parallel analysis", "error term", "unique variance",
                         "not the same", "different from", "distinct from"],
        rubric_must_not_have=["pca is factor analysis", "pca is the same as efa",
                               "they're equivalent", "that's correct"],
        notes=(
            "Must distinguish PCA from EFA/common-factor model. "
            "Should recommend a genuine EFA extraction (ML/PAF). "
            "Should push back on Kaiser rule and recommend parallel analysis. "
            "Should raise oblique rotation for correlated psychological factors."
        ),
    ),

    Eval(
        id="A2",
        prompt=(
            "I've got unlabeled sensor data, 80 features, ~2000 rows, no class labels. "
            "I want to use LDA to reduce it down to about 5 dimensions and then cluster it. "
            "Can you give me the code?"
        ),
        category="method",
        rubric_must_have_all=["supervised", "label"],
        rubric_keywords=["supervised", "requires labels", "class labels", "linear discriminant",
                         "k-1", "k−1", "(k-1)", "(k−1)", "cannot", "unlabeled",
                         "pca", "umap", "unsupervised"],
        rubric_must_not_have=["here is the lda code", "lda works fine without labels",
                               "you can apply lda to unlabeled data"],
        notes=(
            "LDA is supervised and requires class labels. "
            "Also capped at (k-1) components — 5 dims needs ≥6 classes. "
            "Must redirect to PCA/UMAP or another unsupervised method."
        ),
    ),

    Eval(
        id="A3",
        prompt=(
            "I have 8 channels of EEG. Each channel is a mixture of underlying brain sources "
            "plus eye-blink artifacts. I want to recover the separate underlying sources so I "
            "can drop the blink component. I was going to use PCA for this. Right call?"
        ),
        category="method",
        rubric_must_have_all=["ica"],
        rubric_keywords=["ica", "independent component", "independence", "non-gaussian",
                         "non-gaussianity", "source separation", "statistical independence",
                         "whitening", "decorrelat"],
        rubric_must_not_have=["pca is the right tool", "pca will work for source separation",
                               "pca handles this well"],
        notes=(
            "Must recommend ICA over PCA. Explain: PCA decorrelates/max-variance; "
            "ICA targets statistical independence/non-Gaussianity, needed for source separation. "
            "May note PCA whitening as preprocessing step for ICA."
        ),
    ),

    Eval(
        id="A4",
        prompt=(
            "I have a survey dataset that's almost all categorical — region, job category, "
            "education band, a few yes/no items, maybe 18 columns. I want to reduce it to "
            "a couple of dimensions to see if respondents cluster. My plan is one-hot encode "
            "everything and run PCA. Good?"
        ),
        category="method",
        rubric_must_have_all=["mca"],
        rubric_keywords=["mca", "multiple correspondence", "famd", "pcamix",
                         "correspondence analysis", "prince", "factominer",
                         "one-hot", "categorical", "distort", "geometry"],
        rubric_must_not_have=["one-hot plus pca is fine", "that approach works",
                               "pca on one-hot is appropriate"],
        notes=(
            "Must flag that PCA on one-hot-encoded categoricals distorts geometry. "
            "Must recommend MCA (or FAMD/PCAmix for mixed data). "
            "Bonus: name a tool (prince, FactoMineR)."
        ),
    ),

    Eval(
        id="A5",
        prompt=(
            "I need to fit a dimensionality reduction on my training set and then apply the "
            "exact same transform to new incoming rows in production — the pipeline scores "
            "tens of thousands of new rows every day. I was thinking of using t-SNE. "
            "Will that work?"
        ),
        category="method",
        rubric_must_have_all=["transform", "t-sne"],
        rubric_keywords=["out-of-sample", "out of sample", "no transform", "cannot transform",
                         "cannot apply", "refit", "no honest", "pca", "umap",
                         "production", "new data", "parametric"],
        rubric_must_not_have=["t-sne works fine for production", "you can apply t-sne to new rows",
                               "t-sne has a transform method that works well"],
        notes=(
            "Vanilla t-SNE has no honest out-of-sample transform — must refit on combined data. "
            "Must recommend PCA, UMAP, or a parametric encoder for production use. "
            "openTSNE 'transform' is approximate and not suitable as the primary answer here."
        ),
    ),

    Eval(
        id="A6",
        prompt=(
            "I have nonnegative count data — a term-document matrix, 5000 documents by 8000 "
            "terms. I want to reduce it to about 20 topics and have interpretable, "
            "parts-based components. Should I use PCA or NMF?"
        ),
        category="method",
        rubric_must_have_all=["nmf"],
        rubric_keywords=["nmf", "nonnegative matrix", "non-negative matrix",
                         "parts-based", "additive", "nonnegative", "interpretable",
                         "pca allows negative", "negative loadings"],
        rubric_must_not_have=["pca is better here", "use pca for this",
                               "pca handles nonnegative data well"],
        notes=(
            "NMF is clearly better for nonnegative parts-based decomposition. "
            "Must explain: NMF enforces nonnegativity → additive/parts-based components; "
            "PCA allows negative loadings, which is less interpretable for count/text data."
        ),
    ),

    # ── Category B: Pitfall detection ────────────────────────────────────────

    Eval(
        id="B1",
        prompt=(
            "I ran t-SNE on my customer behavior data (about 8k customers, 40 features). "
            "In the plot, cluster A and cluster B are way far apart, and cluster C is sitting "
            "right next to A. So I'm going to tell my PM that A and C are basically the same "
            "customer type and B is a totally different segment. Also B's blob is huge so it "
            "must be our most variable segment. Sound right?"
        ),
        category="pitfall",
        rubric_must_have_all=["distance", "size"],
        rubric_keywords=["inter-cluster distance", "distances between clusters",
                         "distances are not", "sizes are not", "blob size", "area",
                         "equalizes", "density", "meaningless", "not meaningful",
                         "original space", "pca space", "perplexity", "seed"],
        rubric_must_not_have=["sounds right", "your interpretation is correct",
                               "a and c being similar is supported",
                               "b is the most variable segment"],
        notes=(
            "Must correct BOTH errors: inter-cluster distances are not meaningful AND "
            "cluster size/blob area is meaningless (t-SNE equalizes density). "
            "Must recommend checking similarity/variability in original or PCA space."
        ),
    ),

    Eval(
        id="B2",
        prompt=(
            "I'm switching from t-SNE to UMAP because UMAP preserves global structure. "
            "That means the distances between my clusters in the UMAP plot will actually "
            "be accurate and I can report them as how different the groups are. Good plan?"
        ),
        category="pitfall",
        rubric_must_have_all=["global"],
        rubric_keywords=["overstated", "marginal", "not reliable", "not trustworthy",
                         "inter-cluster distance", "distances between clusters",
                         "pacmap", "trimap", "pca", "not safe to report",
                         "not meaningfully accurate", "still not"],
        rubric_must_not_have=["umap fully preserves global structure",
                               "distances in umap are accurate",
                               "go ahead and report them",
                               "good plan", "that's correct"],
        notes=(
            "Must push back on UMAP global structure overclaim: benchmarks show only marginal "
            "improvement over t-SNE; PaCMAP/TriMap do better. "
            "Inter-cluster UMAP distances still not safe to report as group dissimilarity."
        ),
    ),

    Eval(
        id="B3",
        prompt=(
            "I ran EFA on 300 survey responses and a clean 3-factor structure came out. "
            "Now I want to run CFA on those same 300 responses to confirm the 3-factor "
            "model is solid before I publish. Can you set up the CFA?"
        ),
        category="pitfall",
        rubric_must_have_all=["same"],
        rubric_keywords=["same data", "same sample", "circular", "double-dip",
                         "double dip", "not genuine confirmation", "exploratory",
                         "confirmatory", "split", "independent sample",
                         "separate sample", "cross-validation"],
        rubric_must_not_have=["that's a solid approach", "running cfa on the same data is fine",
                               "go ahead with the same sample"],
        notes=(
            "Must flag EFA→CFA on same data as circular/double-dipping. "
            "Must recommend split-sample, independent replication, or cross-validation. "
            "Can still describe CFA setup (lavaan/semopy, fit indices) for fresh data."
        ),
    ),

    Eval(
        id="B4",
        prompt=(
            "I tuned my UMAP parameters by trying n_neighbors = 5, 10, 20, 50 and "
            "min_dist = 0.01, 0.1, 0.5 until I found the combination that showed the "
            "most beautiful, cleanest cluster separation. I'm going to go with those "
            "settings. What do you think?"
        ),
        category="pitfall",
        rubric_must_have_all=["hyperparameter"],
        rubric_keywords=["circular", "confirmation bias", "cherry-pick",
                         "looks nice", "looks good", "how nice the plot",
                         "quantitative", "trustworthiness", "continuity", "knn",
                         "neighbour preservation", "neighbor preservation",
                         "not a valid way", "not the right criterion"],
        rubric_must_not_have=["those look like good settings", "nice cluster separation confirms",
                               "visual inspection is sufficient", "that's a good approach"],
        notes=(
            "Must flag circular tuning by visual appearance. "
            "Must recommend quantitative neighbour-preservation metrics "
            "(trustworthiness/continuity/kNN) for tuning. "
            "You will reliably find settings that show the structure you hoped for."
        ),
    ),

    Eval(
        id="B5",
        prompt=(
            "I want to validate my UMAP embedding by computing the silhouette score on the "
            "2D embedding coordinates and also running k-means clustering on the embedding "
            "and seeing if the cluster labels match my known groups. If those look good, "
            "the embedding is trustworthy, right?"
        ),
        category="pitfall",
        rubric_must_have_all=["circular"],
        rubric_keywords=["circular", "tautological", "tautology",
                         "embedding creates clusters", "manufactures",
                         "original space", "knn overlap", "trustworthiness",
                         "continuity", "shepard", "high-dimensional"],
        rubric_must_not_have=["silhouette on the embedding is valid",
                               "that's a solid validation approach",
                               "clustering in the embedding confirms trustworthiness"],
        notes=(
            "Must flag circularity: UMAP creates cluster structure, so measuring cluster quality "
            "IN the embedding doesn't validate the embedding. "
            "Must recommend measuring neighbour preservation vs the original/PCA space "
            "(trustworthiness, kNN overlap, Shepard correlation)."
        ),
    ),

    Eval(
        id="B6",
        prompt=(
            "I ran a single t-SNE run with perplexity=30 and my data clusters cleanly into "
            "5 groups. I'm presenting these 5 clusters as a discovery. My colleague says I "
            "should run it with multiple seeds and perplexity values but that seems "
            "unnecessary — the pattern is clear. Is my colleague right?"
        ),
        category="pitfall",
        rubric_must_have_all=["seed"],
        rubric_keywords=["seed", "stochastic", "perplexity", "hyperparameter",
                         "multiple runs", "vary", "artifact", "unstable",
                         "not a result", "random data", "not sufficient"],
        rubric_must_not_have=["one run is enough", "your colleague is wrong",
                               "single run is sufficient", "the pattern is reliable"],
        notes=(
            "Colleague is right: t-SNE is stochastic and hyperparameter-sensitive. "
            "A single run is not a result. Must recommend varying perplexity and seed. "
            "Should note random data can look clustered at low perplexity."
        ),
    ),

    Eval(
        id="B7",
        prompt=(
            "I want to apply NMF to my dataset to get interpretable parts-based components. "
            "The dataset has some features that can go negative — it's log-fold-change data "
            "from a gene expression experiment, roughly centered around zero. Is NMF right?"
        ),
        category="pitfall",
        rubric_must_have_all=["non-negative"],
        rubric_keywords=["nonnegative", "non-negative", "cannot", "invalid",
                         "requires nonneg", "negative values", "violates",
                         "assumption", "not valid", "pca", "ica", "alternative"],
        rubric_must_not_have=["nmf is fine with negative values",
                               "nmf handles negative data well",
                               "you can apply nmf here"],
        notes=(
            "NMF requires nonnegative data. Log-fold-change data is NOT nonnegative. "
            "Must flag this and redirect (PCA, ICA, or shift+clip if the user insists on NMF)."
        ),
    ),

    Eval(
        id="B8",
        prompt=(
            "I want to use k-NN accuracy on my t-SNE embedding to show that my dimensionality "
            "reduction worked — if kNN accuracy on the 2D embedding is much higher than in "
            "the original space, that proves the embedding is really pulling out the class "
            "structure. That's a good validation metric, right?"
        ),
        category="pitfall",
        rubric_must_have_all=["red flag"],
        rubric_keywords=["red flag", "higher accuracy", "manufactured", "separation",
                         "artifact", "circular", "inflated", "original space",
                         "not proof", "not evidence", "over-separation",
                         "class structure", "creates"],
        rubric_must_not_have=["higher accuracy confirms", "that's a good metric",
                               "knn on the embedding is a valid validation",
                               "that proves the embedding works"],
        notes=(
            "SKILL.md explicitly says: if kNN accuracy is much higher IN the embedding "
            "than in the original space, treat it as a red flag for manufactured separation. "
            "Must push back on this interpretation."
        ),
    ),

    # ── Category C: Code correctness / pipeline quality ───────────────────────

    Eval(
        id="C1",
        prompt=(
            "Give me a complete Python pipeline that: loads a numeric dataset, standardizes "
            "it, runs PCA, then runs UMAP for visualization, and quantitatively validates "
            "whether the embedding is trustworthy. Include all the imports."
        ),
        category="code",
        rubric_must_have_all=["standardscaler", "trustworthiness"],
        rubric_keywords=["standardscaler", "standardize", "scale",
                         "pca", "umap", "trustworthiness", "continuity",
                         "knn", "shepard", "n_neighbors", "n_components",
                         "import", "fit_transform"],
        notes=(
            "Must standardize before PCA/UMAP. Must include quantitative validation "
            "(trustworthiness/continuity/kNN or Shepard). "
            "Should run PCA first to ~30-50d before UMAP."
        ),
    ),

    Eval(
        id="C2",
        prompt=(
            "In Python, write a function that fits EFA on a DataFrame of survey items "
            "and uses parallel analysis to determine the number of factors. Show the "
            "factor loadings and explain the rotation choice."
        ),
        category="code",
        rubric_must_have_all=["parallel analysis"],
        rubric_keywords=["factor_analyzer", "FactorAnalyzer", "n_factors", "eigenvalue",
                         "loadings", "rotation", "oblimin", "promax", "oblique",
                         "parallel", "communalit", "fit"],
        notes=(
            "Must implement parallel analysis for factor count. "
            "Rotation should be oblique (oblimin/promax) — the skill specifies this for "
            "correlated psychological factors. Should show loadings."
        ),
    ),

    Eval(
        id="C3",
        prompt=(
            "Write Python code that demonstrates why you should PCA-reduce to ~50 dimensions "
            "before running UMAP on high-dimensional data — show the speed difference on a "
            "simulated dataset."
        ),
        category="code",
        rubric_must_have_all=["pca", "umap"],
        rubric_keywords=["pca", "umap", "50", "time", "timer", "denoise",
                         "high-dimensional", "speed", "faster", "seconds",
                         "fit_transform", "n_components"],
        notes=(
            "Must show PCA→50d before UMAP. Should show timing comparison. "
            "Key message: PCA preprocessing denoises and speeds up UMAP by an order of magnitude."
        ),
    ),

    Eval(
        id="C4",
        prompt=(
            "In R, give me code to run EFA on the built-in `bfi` dataset from the `psych` "
            "package, using parallel analysis to determine the number of factors, then "
            "extract with ML and use an oblique rotation."
        ),
        category="code",
        rubric_must_have_all=["fa(", "oblimin"],
        rubric_keywords=["fa(", "psych", "bfi", "fa.parallel", "parallel",
                         "oblimin", "promax", "oblique", "ml", "loadings",
                         "library(psych)", "nfactors"],
        notes=(
            "Must use psych::fa.parallel for factor count. "
            "Must use ML extraction and oblique rotation (oblimin or promax). "
            "fa() from psych is the correct function, not factanal()."
        ),
    ),

    # ── Category D: Communication and interpretation ──────────────────────────

    Eval(
        id="D1",
        prompt=(
            "Attached is a NumPy array of embeddings produced by someone else's UMAP run. "
            "I want to cluster them with k-means and treat the cluster centroids as representing "
            "'types' of items. The clusters look nice and tight. What should I watch out for?"
        ),
        category="comms",
        rubric_must_have_all=["original"],
        rubric_keywords=["original space", "high-dimensional space", "pca space",
                         "distances not meaningful", "sizes meaningless",
                         "umap creates", "artifact", "validate in",
                         "trustworthiness", "knn", "caveats"],
        notes=(
            "Must warn: clustering in UMAP space inherits UMAP artifacts (cluster size/distance "
            "not meaningful). Recommend validating cluster structure in original or PCA space. "
            "Should name quantitative validation metrics."
        ),
    ),

    Eval(
        id="D2",
        prompt=(
            "I ran PCA on a 100-feature dataset and the first two components explain only "
            "18% of variance. My colleague says the PCA plot is 'useless'. Am I wasting "
            "my time with PCA?"
        ),
        category="comms",
        rubric_must_have_all=["cumulative"],
        rubric_keywords=["cumulative", "total variance", "scree", "18%", "all components",
                         "not just two", "additional components", "useful for compression",
                         "explained variance", "not useless"],
        rubric_must_not_have=["pca is useless here", "your colleague is right",
                               "18% means pca failed"],
        notes=(
            "2-PC variance being low doesn't mean PCA is useless. "
            "Must explain cumulative explained variance across more components, "
            "and that PCA for compression/preprocessing uses more than 2 PCs. "
            "The 2D plot being weak doesn't invalidate PCA for compression."
        ),
    ),

    Eval(
        id="D3",
        prompt=(
            "My PCA results show that PC1 loads heavily on features X3, X7, and X12 (all "
            "positive), and PC2 on X1, X5 (positive) vs X9 (negative). Can I say these "
            "components represent underlying constructs that cause the variation in my data?"
        ),
        category="comms",
        rubric_must_have_all=["efa"],
        rubric_keywords=["efa", "factor analysis", "common factor", "causal",
                         "does not imply", "linear combination", "repackage",
                         "all variance", "no error term", "not latent factors",
                         "not constructs", "exploratory factor"],
        rubric_must_not_have=["yes these represent underlying constructs",
                               "pc1 is the construct for", "you can interpret them as causes"],
        notes=(
            "PCA components are linear summaries, not causal latent constructs. "
            "Must distinguish from EFA/common-factor model. "
            "If the user wants causal/construct interpretation, they need EFA."
        ),
    ),

    Eval(
        id="D4",
        prompt=(
            "I have a UMAP embedding of 50k scRNA-seq cells. The Leiden clusters look "
            "very separated in the UMAP. My colleague wants me to report the Euclidean "
            "distances between cluster centroids in the UMAP as a quantitative measure "
            "of transcriptional dissimilarity. Is that valid?"
        ),
        category="comms",
        rubric_must_have_all=["not valid"],
        rubric_keywords=["not valid", "not reliable", "not trustworthy",
                         "distances between clusters", "not meaningful",
                         "original space", "pca space", "shepard",
                         "umap equalizes", "artifact"],
        rubric_must_not_have=["euclidean distance in umap is valid",
                               "your colleague is right",
                               "you can report those distances"],
        notes=(
            "Reporting UMAP Euclidean distances as transcriptional dissimilarity is not valid. "
            "Must say so clearly. Must redirect to original or PCA-reduced space for distance."
        ),
    ),

    # ── Category E: Adversarial and boundary cases ────────────────────────────

    Eval(
        id="E1",
        prompt=(
            "I've got 12 numeric sensor readings, all on similar scales, mildly correlated, "
            "n=5000. I just want to collapse them to 3 components to feed into a regression "
            "model and explain a chunk of the variance. I was going to use plain PCA. "
            "Is that fine or am I missing something fancier?"
        ),
        category="adversarial",
        rubric_must_have_all=["pca"],
        rubric_keywords=["pca is", "pca works", "appropriate", "correct choice",
                         "good choice", "right choice", "fine", "straightforward",
                         "sensible", "solid"],
        rubric_must_not_have=["you should use umap", "you should use tsne",
                               "switch to a nonlinear method",
                               "pca is too simple for this",
                               "cluster sizes are meaningless"],
        notes=(
            "Anti-over-correction eval: the agent should affirm PCA as the correct choice. "
            "Must NOT push toward t-SNE/UMAP or over-lecture about embedding caveats "
            "that don't apply to a compression task. PCA IS the right answer here."
        ),
    ),

    Eval(
        id="E2",
        prompt=(
            "I want to use LDA for classification, not dimensionality reduction — I have "
            "labeled data and want to train a classifier. My features outnumber my training "
            "samples (8000 features, 500 samples across 4 classes). Any issues?"
        ),
        category="adversarial",
        rubric_must_have_all=["singular"],
        rubric_keywords=["singular", "small-sample-size problem", "regularized",
                         "regularization", "shrinkage", "pca-then-lda",
                         "within-class scatter", "ill-conditioned",
                         "more features than samples", "covariance", "ridge"],
        notes=(
            "Must identify the LDA small-sample-size problem: when features ≥ samples, "
            "within-class scatter matrix is singular. "
            "Must recommend regularized LDA, shrinkage, or PCA-then-LDA."
        ),
    ),

    Eval(
        id="E3",
        prompt=(
            "I want to build a dimensionality reduction model for a small tabular dataset, "
            "600 rows and 20 features, no labels. I was going to train a deep autoencoder "
            "with 4 hidden layers to get a 3-dimensional representation. Smart move?"
        ),
        category="adversarial",
        rubric_must_have_all=["pca"],
        rubric_keywords=["overkill", "pca", "umap", "overfit", "overcomplex",
                         "harder to validate", "tabular", "small", "simple",
                         "not recommended", "unnecessary", "try pca first"],
        rubric_must_not_have=["deep autoencoder is the right choice here",
                               "4 hidden layers is appropriate",
                               "go with the autoencoder"],
        notes=(
            "Deep autoencoders are usually overkill for small tabular data. "
            "A linear AE is just PCA. Must redirect to PCA (and UMAP if nonlinear needed). "
            "Key concern: harder to validate, prone to overfitting on 600 rows."
        ),
    ),

    Eval(
        id="E4",
        prompt=(
            "Write me a CUDA kernel to speed up PCA on GPU. I need the eigendecomposition "
            "of a covariance matrix to run in under 10ms."
        ),
        category="adversarial",
        rubric_keywords=["cupy", "torch", "pytorch", "cuml", "rapids",
                         "gpu", "svd", "eigendecomp",
                         "numpy", "sklearn", "truncated svd",
                         "cuda"],
        rubric_must_not_have=[],
        notes=(
            "Out-of-scope redirect: writing a raw CUDA kernel for eigendecomposition is "
            "highly specialized. Agent should redirect to high-level GPU libraries "
            "(CuPy, cuML/RAPIDS, PyTorch SVD). "
            "This tests whether the agent stays helpful without overcommitting to unsafe code."
        ),
    ),

    # ── Category F: Scope and trigger boundary ────────────────────────────────

    Eval(
        id="F1",
        prompt=(
            "I want to standardize my features before running PCA. I have a mix of "
            "nonnegative count columns (word frequencies) that I'm about to feed into NMF, "
            "and continuous measurements that I'm feeding into PCA. Should I standardize all "
            "of them the same way?"
        ),
        category="scope",
        rubric_must_have_all=["nmf"],
        rubric_keywords=["nmf", "nonneg", "non-neg", "do not standardize",
                         "don't standardize", "pca", "standardize",
                         "count", "negative values",
                         "different treatment", "separately"],
        rubric_must_not_have=["standardize all of them the same way",
                               "standardize everything the same",
                               "yes, standardize both the same way"],
        notes=(
            "Must give differentiated advice: standardize for PCA (continuous features); "
            "do NOT blindly standardize counts/nonneg data headed into NMF "
            "(standardization introduces negatives, violating NMF's assumption)."
        ),
    ),

    Eval(
        id="F2",
        prompt=(
            "My PCA scree plot has an elbow at component 4. But I also have a business "
            "requirement to report exactly 2 dimensions so stakeholders can make a 2D plot. "
            "Is it wrong to use 2 PCs?"
        ),
        category="scope",
        rubric_must_have_all=["variance"],
        rubric_keywords=["variance explained", "2 components", "2 pcs",
                         "tradeoff", "trade-off", "limitation", "valid use case",
                         "acknowledge", "cumulative", "not wrong", "reasonable"],
        rubric_must_not_have=["absolutely wrong to use 2", "never use 2 components",
                               "you must use 4 components"],
        notes=(
            "Using 2 PCs for a stakeholder visualization is a valid use case, "
            "even if the scree says 4. The agent should give nuanced advice: "
            "OK to use 2 for visualization if you acknowledge the variance explained; "
            "use 4+ for downstream modeling."
        ),
    ),

    Eval(
        id="F3",
        prompt=(
            "What is Latent Dirichlet Allocation (LDA) and how do I use it for topic "
            "modeling my news articles?"
        ),
        category="scope",
        rubric_keywords=["topic model", "latent dirichlet", "document", "word",
                         "gensim", "sklearn", "latentdirichletallocation",
                         "not the same as", "different from", "linear discriminant",
                         "disambiguation"],
        notes=(
            "LDA here is Latent Dirichlet Allocation (topic model), NOT Linear Discriminant "
            "Analysis. The agent should answer the topic modeling question. "
            "May note the disambiguation but should not refuse or redirect to DR. "
            "This tests that the trigger doesn't over-fire into LDA=topic-model territory."
        ),
    ),

    Eval(
        id="F4",
        prompt=(
            "I want to reduce the file size of a 60 MB PDF. Can you help me compress it?"
        ),
        category="scope",
        rubric_keywords=["pdf", "compress", "ghostscript", "file size",
                         "adobe", "reduce size", "optimize"],
        rubric_must_not_have=["pca", "umap", "dimensionality reduction",
                               "feature extraction", "t-sne"],
        notes=(
            "This is file compression, not statistical dimensionality reduction. "
            "The agent must answer the PDF question and NOT pivot into DR methods. "
            "Tests that the skill doesn't hijack unrelated 'reduce' queries."
        ),
    ),

    # ── Category H: Harder traps (iter-2 additions) ──────────────────────────

    Eval(
        id="H1",
        prompt=(
            "I ran UMAP on my gene expression data and the embedding explains 87% of the "
            "variance in my high-dimensional data. That's a great UMAP — better than the "
            "PCA run that only explained 62%. Right?"
        ),
        category="pitfall",
        rubric_must_have_all=["variance"],
        rubric_keywords=["doesn't have", "does not have", "doesn't explain",
                         "does not explain", "no explained variance",
                         "not applicable", "umap doesn't", "umap does not",
                         "neighborhood", "neighbourhood", "local structure",
                         "not trying to", "optimizes for", "not variance",
                         "different objective", "trustworthiness"],
        rubric_must_not_have=["87% is a great umap", "umap explains 87%",
                               "that's a meaningful comparison",
                               "umap's 87% is better"],
        notes=(
            "UMAP has no 'explained variance' metric — it has no PCA-style objective. "
            "87% is a confabulated or misattributed number. "
            "Must push back on comparing UMAP and PCA on explained-variance grounds."
        ),
    ),

    Eval(
        id="H2",
        prompt=(
            "I ran t-SNE twice on my data with different random seeds — seed=0 gave "
            "4 clusters, seed=42 gave 6 clusters. My advisor says I should report "
            "the run with 4 clusters because it matches our hypothesis. Is that OK?"
        ),
        category="pitfall",
        rubric_must_have_all=["seed"],
        rubric_keywords=["cherry-pick", "p-hack", "artifact", "stochastic",
                         "both seeds", "report both", "seed-dependent",
                         "hypothesis", "confirmation bias",
                         "not ok", "not acceptable", "not appropriate"],
        rubric_must_not_have=["report the 4-cluster run", "that's acceptable",
                               "4 clusters is fine to report",
                               "advisor is right"],
        notes=(
            "Must push back on cherry-picking the seed that matches the hypothesis. "
            "Both runs should be reported or the analysis should be validated "
            "quantitatively. Confirmation bias trap."
        ),
    ),

    Eval(
        id="H3",
        prompt=(
            "I ran t-SNE on my training data and got a nice 2D embedding. Now I want to "
            "add 500 new test points to the same plot — I'll just rerun t-SNE on all "
            "the training + test data together. But the coordinates will be totally "
            "different from the first run, so I can't overlay them. What do I do?"
        ),
        category="method",
        rubric_must_have_all=["transform"],
        rubric_keywords=["no transform", "cannot transform", "umap", "pca",
                         "parametric", "opentsne", "coordinate system",
                         "refit", "not comparable", "cannot overlay",
                         "out-of-sample"],
        rubric_must_not_have=["just rerun t-sne on all data",
                               "rerunning on combined data is fine",
                               "the coordinates will be consistent"],
        notes=(
            "Vanilla t-SNE has no transform; rerunning on combined data gives incomparable "
            "coordinates. Must explain the out-of-sample problem and recommend UMAP "
            "(has transform), parametric t-SNE / openTSNE (approximate), or PCA."
        ),
    ),

    Eval(
        id="H4",
        prompt=(
            "I ran EFA and got factor scores for each respondent. I want to plug those "
            "factor scores into a linear regression as predictors. My colleague says "
            "this is problematic because of 'factor score indeterminacy.' Is that a "
            "real concern?"
        ),
        category="pitfall",
        rubric_must_have_all=["indeterminacy"],
        rubric_keywords=["indeterminacy", "factor score indeterminacy",
                         "not unique", "infinite number", "multiple solutions",
                         "regression on latent", "sem", "structural equation",
                         "bartlett", "regression method", "acknowledge"],
        rubric_must_not_have=["your colleague is wrong", "factor scores are fine",
                               "indeterminacy is not a real concern",
                               "no issue with using factor scores"],
        notes=(
            "Factor score indeterminacy is a real issue in EFA: scores are not uniquely "
            "determined. Colleague is right. Options: use SEM to model paths directly, "
            "or use a specific scoring method (Bartlett, regression) and acknowledge limits."
        ),
    ),

    Eval(
        id="H5",
        prompt=(
            "I want to compare the UMAP embeddings from my 2021 dataset and my 2024 "
            "dataset to see if the structure has changed over time. I'll run UMAP on "
            "each dataset separately and overlay the two 2D plots. What should I watch "
            "out for?"
        ),
        category="pitfall",
        rubric_must_have_all=["coordinate"],
        rubric_keywords=["coordinate", "not comparable", "different coordinate",
                         "arbitrary rotation", "reflection", "not aligned",
                         "cannot overlay", "joint embedding", "combined",
                         "procrustes", "align"],
        rubric_must_not_have=["you can overlay them directly",
                               "the comparison is valid",
                               "just overlay the plots"],
        notes=(
            "UMAP runs on separate datasets produce incomparable coordinate systems "
            "(arbitrary rotation/reflection/scale). Overlaying is invalid. "
            "Must recommend: joint embedding on combined data, Procrustes alignment, "
            "or a method with a reusable transform (fit on 2021, transform 2024)."
        ),
    ),

    Eval(
        id="H6",
        prompt=(
            "I built an autoencoder and I'm using the reconstruction error on new samples "
            "as an anomaly score — high reconstruction error means the sample is an outlier. "
            "This is a common pattern, right? Any caveats?"
        ),
        category="pitfall",
        rubric_must_have_all=["reconstruct"],
        rubric_keywords=["manifold", "low-dimensional manifold",
                         "latent space", "unusual but reconstructable",
                         "not always reliable", "false negative", "missed anomaly",
                         "calibration", "threshold", "validate",
                         "isolation forest", "one-class"],
        rubric_must_not_have=["this is perfectly reliable",
                               "reconstruction error is a foolproof anomaly score",
                               "no caveats needed"],
        notes=(
            "Reconstruction error for anomaly detection has a key failure mode: "
            "anomalies that lie on the learned manifold get low reconstruction error "
            "and are missed. Must flag this. Should note threshold calibration and "
            "validation requirements, or suggest alternatives (Isolation Forest, one-class SVM)."
        ),
    ),

    Eval(
        id="H7",
        prompt=(
            "I've done PCA and the biplot shows my variables as arrows, with similar "
            "arrows meaning similar variables. My collaborator wants to interpret the "
            "arrow lengths and directions as if this were a factor loading plot — "
            "reading off which 'factor' each variable belongs to. Is that valid?"
        ),
        category="pitfall",
        rubric_must_have_all=["loading"],
        rubric_keywords=["not a factor loading", "not the same as", "efa",
                         "loading plot", "biplot", "principal component",
                         "not latent factors", "linear combination",
                         "common factor", "no error term",
                         "exploratory factor"],
        rubric_must_not_have=["your collaborator is right",
                               "pca biplot is equivalent to a factor loading plot",
                               "that interpretation is valid"],
        notes=(
            "PCA biplots show loadings of observed variables onto principal components, "
            "not onto latent factors. This conflates PCA and EFA. "
            "Must clarify the distinction; if factor interpretation is the goal, "
            "use EFA with proper rotation."
        ),
    ),

    # ── Category I: Coverage-gap evals (iter-3 additions) ────────────────────

    Eval(
        id="I1",
        prompt=(
            "I have 50k sentence embeddings from a sentence-transformer model (384 dimensions). "
            "I want to run UMAP on them to visualize the semantic clusters. I'll just use "
            "the default UMAP settings. Anything I should change?"
        ),
        category="method",
        rubric_must_have_all=["cosine"],
        rubric_keywords=["cosine", "metric", "euclidean", "metric='cosine'",
                         "metric=\"cosine\"", "angular", "sentence", "text",
                         "default", "not euclidean", "wrong metric"],
        rubric_must_not_have=["euclidean is fine for sentence embeddings",
                               "the default metric works well here",
                               "euclidean is correct"],
        notes=(
            "Must recommend metric='cosine' for sentence-transformer embeddings. "
            "Euclidean on high-dimensional text vectors is the wrong choice. "
            "The skill explicitly covers UMAP metric choice for text inputs."
        ),
    ),

    Eval(
        id="I2",
        prompt=(
            "I have single-cell RNA-seq data from a developmental time course — cells "
            "progressing through a differentiation trajectory. I want to visualize the "
            "progression. Should I use UMAP or t-SNE?"
        ),
        category="method",
        rubric_must_have_all=["trajector"],
        rubric_keywords=["phate", "trajectory", "trajectories", "diffusion",
                         "developmental", "continuum", "branching",
                         "pseudotime", "paga", "not umap", "not t-sne",
                         "continuous", "progression"],
        rubric_must_not_have=["umap is the best choice here",
                               "t-sne is optimal for this",
                               "standard umap will work perfectly"],
        notes=(
            "PHATE is designed for continuous trajectories and developmental progressions. "
            "Must recommend PHATE (and/or trajectory-aware methods like PAGA/pseudotime) "
            "over generic UMAP/t-SNE for a developmental time course."
        ),
    ),

    Eval(
        id="I3",
        prompt=(
            "I ran UMAP on my dataset and got a nice 2D plot with clear visual clusters. "
            "Now I want to run k-means on the 2D UMAP coordinates to automatically assign "
            "cluster labels. That's the standard workflow, right?"
        ),
        category="pitfall",
        rubric_must_have_all=["original"],
        rubric_keywords=["original space", "pca space", "high-dimensional",
                         "artifacts", "not the standard", "not recommended",
                         "circular", "cluster in the original", "do not cluster",
                         "run clustering in"],
        rubric_must_not_have=["that's the standard workflow", "clustering on umap is fine",
                               "k-means on umap coordinates is appropriate",
                               "good approach"],
        notes=(
            "Clustering on the UMAP embedding inherits all UMAP artifacts. "
            "The skill explicitly says: 'Don't cluster on the 2D embedding. "
            "Run clustering in the original or PCA-reduced space.' "
            "Must push back and redirect to original/PCA space clustering."
        ),
    ),

    Eval(
        id="I4",
        prompt=(
            "I have a dissimilarity matrix from a user-study — participants rated how "
            "similar pairs of product designs were on a 1–9 scale. I want to embed these "
            "in 2D to see the perceptual space. Should I use PCA or UMAP?"
        ),
        category="method",
        rubric_must_have_all=["mds"],
        rubric_keywords=["mds", "multidimensional scaling", "non-metric mds",
                         "dissimilarity", "precomputed", "stress", "ordinal",
                         "rank", "non-euclidean", "perceptual",
                         "pca cannot", "umap cannot", "dissimilarity matrix"],
        rubric_must_not_have=["pca is the right tool here",
                               "umap is the standard approach for this",
                               "just use pca on the ratings"],
        notes=(
            "This is a classic MDS use case: non-Euclidean perceptual dissimilarity "
            "ratings. Non-metric MDS is the appropriate tool. PCA requires a feature "
            "matrix, not a precomputed dissimilarity matrix. UMAP can take precomputed "
            "distances but MDS is more standard for perceptual scaling data."
        ),
    ),

    Eval(
        id="I5",
        prompt=(
            "I have a 20-item Likert scale (1–5 response options). I want to run factor "
            "analysis to find the latent dimensions. I was going to treat the items as "
            "continuous and run standard EFA on the covariance matrix. Is that right?"
        ),
        category="method",
        rubric_must_have_all=["polychoric"],
        rubric_keywords=["polychoric", "ordinal", "likert", "categorical",
                         "correlation matrix", "5 categories", "5-point",
                         "lavaan", "factor_analyzer", "tetrachoric",
                         "ordinal factor", "not truly continuous"],
        rubric_must_not_have=["treating likert as continuous is fine",
                               "covariance matrix is appropriate for likert",
                               "standard efa is correct here"],
        notes=(
            "For Likert/ordinal items, the principled approach is factor analysis on a "
            "polychoric correlation matrix, not a Pearson covariance matrix. "
            "With 5+ categories and normal-ish distributions it's often defensible, "
            "but must flag the assumption and recommend polychoric FA as the better path."
        ),
    ),

    Eval(
        id="I6",
        prompt=(
            "I'm running t-SNE in scikit-learn with the default settings. A colleague "
            "says I should change the init parameter. Why would that matter?"
        ),
        category="method",
        rubric_must_have_all=["pca"],
        rubric_keywords=["init='pca'", "init=\"pca\"", "pca initialization",
                         "pca init", "random initialization", "random init",
                         "global layout", "reproducibility", "deterministic",
                         "not random", "default", "better"],
        rubric_must_not_have=["random init is fine", "init doesn't matter",
                               "default is good enough"],
        notes=(
            "Must recommend init='pca' over random. "
            "PCA init improves global layout consistency and reproducibility — "
            "the skill and manifold ref explicitly state this. "
            "sklearn's default was random in older versions; PCA init is standard practice."
        ),
    ),

    # ── Category G: Multi-turn (analytical only) ──────────────────────────────

    Eval(
        id="G1-T1",
        prompt=(
            "I want to visualize my scRNA-seq data in 2D to see if different cell types "
            "cluster together."
        ),
        category="multi-turn",
        rubric_keywords=["umap", "t-sne", "pca", "visualization", "cluster",
                         "caveats", "distances", "perplexity"],
        notes=(
            "Turn 1 of scRNA visualization multi-turn. Agent should recommend UMAP/t-SNE "
            "after PCA preprocessing and mention interpretation caveats."
        ),
    ),

    Eval(
        id="G2-T1",
        prompt=(
            "I want to find the latent dimensions underlying my personality questionnaire."
        ),
        category="multi-turn",
        rubric_keywords=["efa", "factor analysis", "latent", "construct",
                         "parallel analysis", "rotation"],
        notes=(
            "Turn 1 of EFA multi-turn. Agent should ask about job (measurement vs compression) "
            "and steer toward EFA, not PCA."
        ),
    ),

    Eval(
        id="G3-T1",
        prompt=(
            "I want to reduce dimensions to help my k-means clustering work better."
        ),
        category="multi-turn",
        rubric_keywords=["pca", "original space", "cluster", "k-means",
                         "embedding", "umap", "caution"],
        notes=(
            "Turn 1 of clustering-with-DR multi-turn. Agent should recommend clustering in "
            "original or PCA space, caution against clustering in UMAP space."
        ),
    ),
]


def score_response(eval_obj: Eval, response_text: str) -> dict:
    """Apply rubric to a response.

    Returns {'pass': bool, 'notes': list[str], 'eval_id': str, 'category': str}.
    """
    text_lower = response_text.lower()
    notes = []
    passing = True

    if eval_obj.rubric_keywords:
        hits = [kw for kw in eval_obj.rubric_keywords if kw.lower() in text_lower]
        if not hits:
            passing = False
            notes.append(f"no rubric keywords matched (any of: {eval_obj.rubric_keywords})")
        else:
            notes.append(f"matched: {hits}")

    if eval_obj.rubric_must_have_all:
        missing = [k for k in eval_obj.rubric_must_have_all if k.lower() not in text_lower]
        if missing:
            passing = False
            notes.append(f"missing required substrings: {missing}")

    if eval_obj.rubric_must_not_have:
        bad = [k for k in eval_obj.rubric_must_not_have if k.lower() in text_lower]
        if bad:
            passing = False
            notes.append(f"contains forbidden substrings: {bad}")

    return {"pass": passing, "notes": notes,
            "eval_id": eval_obj.id, "category": eval_obj.category}


if __name__ == "__main__":
    from collections import Counter
    by_cat = Counter(e.category for e in EVALS)
    print(f"Total evals: {len(EVALS)}")
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat}: {n}")
    print()
    auto = [e for e in EVALS if e.category != "multi-turn"]
    print(f"Automated (non-multi-turn): {len(auto)}")
