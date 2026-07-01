# Foundations of Representation Learning

What a representation *is*, why learned beats hand-engineered, and the cross-field connections.

## Contents
1. What is a representation
2. Feature learning vs hand-engineered features
3. Distributed vs local representations
4. The manifold hypothesis
5. The information-bottleneck / sufficiency view
6. Inductive biases: there is no representation without them
7. Relationships to neighboring fields

---

## 1. What is a representation

A representation is a function f: input → vector (or set of vectors) such that the geometry of the output space makes some downstream computation easy. "Easy" almost always means **linearly accessible**: a good representation is one where the thing you care about can be read off with a linear map (a probe, a logistic head, a dot product). This is the operational definition that matters — not "captures meaning," which is unfalsifiable.

Key consequence: **representation quality is task-relative and metric-relative.** The same vector can be excellent for retrieval (good angular structure) and poor for a linear classifier (the classes aren't linearly separable in it). Always pin down *good for what, measured how* before evaluating.

## 2. Feature learning vs hand-engineered features

For decades, ML meant hand-engineering features (SIFT/HOG for vision, TF-IDF and parse features for NLP, domain heuristics for tabular) and feeding them to a simple model. The deep-learning thesis is that **the features are the hard part and should be learned end-to-end** from the objective. AlexNet (2012) was the inflection: a learned hierarchy of features crushed hand-engineered pipelines on ImageNet.

Why learned wins when data is plentiful:
- **Composition.** Deep nets build features hierarchically (edges → textures → parts → objects), reusing lower features across many higher ones — exponentially more efficient than enumerating features by hand.
- **Objective alignment.** Learned features are optimized for *your* loss, not a human's guess at what matters.
- **Transfer.** Features learned on a large task transfer to many smaller ones (the entire pretraining paradigm).

When hand-engineering still wins: small data, strong domain priors, hard interpretability/regulatory constraints, or tabular problems where gradient-boosted trees on sensible features remain state of the art. "Learn everything" is not free — it needs data and compute proportional to the nuisance you're asking the model to discover.

## 3. Distributed vs local representations

- **Local (one-hot / symbolic):** each concept gets its own unit. Interpretable, but no generalization across concepts and exponential in the number of distinguishable states.
- **Distributed:** each concept is a *pattern* across many units, and each unit participates in many concepts. n binary units can represent up to 2^n regions; similar concepts get similar patterns, so generalization is automatic. This is the foundational idea (Hinton et al.) behind why neural representations generalize — and, taken to the limit (more features than dimensions), it's exactly **superposition**, which is why interpretability is hard.

## 4. The manifold hypothesis

Natural high-dimensional data does not fill its ambient space — it concentrates near a much-lower-dimensional manifold. A 256×256 RGB image lives in ~196k dimensions, but the set of *natural* images is a tiny, curved, low-dimensional subset. Representation learning = learning coordinates *on* that manifold: directions that move along real factors of variation (pose, lighting, identity) while collapsing the off-manifold nuisance directions. This reframes many methods: autoencoders learn a chart; contrastive methods learn an embedding where manifold-neighbors are close; the bottleneck dimensionality is an estimate of intrinsic dimension.

## 5. The information-bottleneck / sufficiency view

Frame the encoder as trading off two informations: maximize I(Z; Y) (keep what's relevant to the task/target) while minimizing I(Z; X) (forget the input otherwise). The ideal Z is a **minimal sufficient statistic** for Y. This explains *why discarding information is good*: a representation that memorizes X transfers and generalizes poorly; one that keeps only Y-relevant structure is robust. Caveats: in pure SSL there's no Y, so the relevant target is implicit (the augmentation-invariances or the masked content); and the *strong* IB claim that SGD has a distinct "compression phase" explaining generalization is **contested** (Tishby & Schwartz-Ziv 2017 vs Saxe et al. 2018 — likely a tanh-saturation artifact). Use IB as intuition, not as a proven mechanism.

## 6. Inductive biases: there is no representation without them

A model's representation is determined as much by its **inductive biases** as by its data: convolution (translation equivariance), attention (content-based routing, permutation equivariance modulo position), the augmentation set in contrastive learning (what you declare "the same"), the prior in a VAE, the sparsity penalty in an SAE. The Locatello impossibility result for disentanglement is the sharp version of this: with no bias and no supervision, infinitely many equally-good-fitting latent factorizations exist, so "the" disentangled representation is underdetermined. **Whenever you specify a representation method, you are specifying a bias about what should be invariant and what should vary.** Make that explicit.

## 7. Relationships to neighboring fields

The unifying object is *a learned latent code*; fields differ in their assumptions about it.

- **Dimensionality reduction & manifold learning.** Special cases / classical cousins. PCA = a linear autoencoder with orthogonality (the optimal linear code under MSE). Kernel PCA, Isomap, LLE, Laplacian eigenmaps, UMAP, t-SNE are nonlinear, mostly *unsupervised* and *visualization-grade*. Representation learning generalizes these to deep, supervised/self-supervised, transfer-oriented codes. (Boundary with the dimensionality-reduction skill: it owns "compress & visualize"; this skill owns "learn a code for downstream use." They hand off.)
- **Latent-variable & probabilistic modeling.** Factor analysis, pPCA, mixture models, HMMs, topic models (LDA), and VAEs all posit unobserved causes generating the data. The split: deterministic point-embeddings (no uncertainty, no generative story) vs distributional latents (priors, posteriors, likelihoods, sampling).
- **Information theory.** Supplies the objective language: mutual information, sufficiency, rate-distortion, the bottleneck. InfoNCE is literally a mutual-information lower bound.
- **Deep learning.** The substrate; representation learning is arguably *the* reason deep learning works.
- **Reinforcement learning.** State/observation representations (often the bottleneck in sample efficiency), world models (learned latent dynamics), successor representations, and reward modeling (a learned representation of preferences).
- **Psychometrics.** IRT and factor analysis are latent-trait *representation learning* from the 1900s–1950s: estimate a person's latent ability/trait vector and item parameters from responses — formally a logistic matrix factorization. The vocabulary differs ("loadings," "abilities," "discrimination"); the math overlaps with embeddings and 2PL-style models.
- **Behavioral science.** Preference and choice models (Bradley-Terry 1952, Thurstone 1927, random-utility/logit; McFadden 1974) are representation learning over preferences — the same family as RLHF reward models and MaxDiff/conjoint utilities.
- **Foundation models.** Their internal representations are the field's primary object of study now (probing, SAEs, steering).
- **AI agents.** Memory, retrieval (RAG), and grounding all run on embeddings; an agent's effective "knowledge" is mediated by representation quality.
