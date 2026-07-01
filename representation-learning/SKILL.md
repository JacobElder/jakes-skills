---
name: representation-learning
description: Reason about learned representations — embeddings, latent spaces, self-supervised and contrastive learning (SimCLR/BYOL/DINO/MAE), autoencoders and VAEs, transformer/LLM internal representations, multimodal/graph/knowledge-graph embeddings, retrieval and recommender systems, reward/preference modeling, and interpretability (probing, superposition, sparse autoencoders). Use it whenever someone asks which similarity metric to use (cosine vs Euclidean vs dot product), bi-encoder vs cross-encoder, fine-tune vs frozen encoder, why embedding/retrieval/RAG quality is bad, how to evaluate or compare representations across models, why a VAE collapsed, what contrastive learning does, or how to design a representation pipeline — even if they never say the words. Also fires for word2vec/BERT/CLIP/SBERT, vector-DB/ANN search, two-tower or matrix-factorization recsys, bi-encoder/cross-encoder retrieval architectures, metric learning, and disentanglement. Settled positions diverge from intuitive defaults (just-use-cosine, more-dimensions-is-better, high-probe-accuracy-means-use), so getting them wrong yields confidently wrong answers.
---

# Representation Learning

This skill makes Claude reason about **learned representations** the way a strong ML researcher or engineer does — someone who has trained embedding models, debugged retrieval systems, read the contrastive-learning and interpretability literature, and developed *opinionated, defensible* positions on the questions where intuition fails.

The job is not to summarize the field. Generic "AI explains embeddings" answers are evenhanded, vague, and wrong in characteristic ways. This skill encodes (a) the **mental models** that make representation questions tractable, (b) the **settled positions** to state with confidence, (c) the **genuinely contested questions** where you surface the spectrum instead of faking consensus, and (d) the **failure modes** that separate deep understanding from pattern-matching.

## The one idea everything hangs on

**A representation is a learned coordinate system, and its quality is defined only relative to a downstream use.** There is no "the" embedding of a sentence or an image — there is the embedding *this encoder trained with this objective on this data* produces, which is good *for some tasks measured some way* and bad for others. The first move on almost any representation question is to refuse the un-asked version and ask: **good for what, measured how?** A vector that's excellent for nearest-neighbor retrieval can be useless for linear classification, and vice versa, because those need different geometric properties.

Three things a representation can be *for* (Bengio's framing, lightly adapted). Keep these separate — methods that are great at one are often bad at another:
1. **Compression / denoising** — throw away nuisance, keep signal (autoencoders, PCA, the information-bottleneck view).
2. **Similarity / retrieval** — geometry encodes "alike-ness" so distance is meaningful (contrastive methods, metric learning).
3. **Transfer / linear readout** — features where downstream tasks become *linearly* easy (most SSL pretraining, evaluated by linear probing).

## Mental models (use these to reason, not just to explain)

- **Change of basis into a space where the task is easy.** A good representation is a coordinate transform after which the hard thing (classification, similarity, generation) becomes simple — ideally linear. "Deep learning works" largely *because* it learns such bases instead of you hand-engineering them.
- **The manifold hypothesis.** Real high-dimensional data (images, text) concentrates near a low-dimensional manifold. Representation learning = learning a *chart* for that manifold — coordinates that vary smoothly along directions of real variation and ignore the ambient nuisance dimensions.
- **A good representation is an approximate sufficient statistic.** It keeps everything about the input that's relevant to the task and discards the rest (information-bottleneck intuition). "Discards the rest" is not optional — it's what makes representations *transfer* and *generalize*.
- **Geometry is the API.** Once data is embedded, downstream systems only see geometry — distances, angles, linear directions, clusters. So the question "is this a good embedding" reduces to "is the geometry the downstream consumer needs actually present and trustworthy."
- **Contrastive learning = pull together + push apart, and the push-apart is load-bearing.** Pulling positives together alone collapses everything to a point. The repulsion (negatives, or a redundancy-reduction / stop-gradient surrogate) is what prevents collapse. Almost every SSL design choice is a collapse-prevention mechanism.
- **Superposition = a crowded apartment.** Models represent more features than they have dimensions by giving each feature a near-orthogonal *direction* rather than its own neuron, so neurons end up polysemantic. This is *why* interpretability is hard and why sparse autoencoders exist.

## Settled positions — state these directly, with reasoning

These are not hot takes; they are the consensus of people who work on this. Don't hedge them into mush.

1. **Cosine similarity is just Euclidean distance on L2-normalized vectors.** For unit vectors, ‖a−b‖² = 2 − 2·cos(a,b) — same ranking. So the real decision is *whether to normalize*, and that should match how the encoder was trained. "Just use cosine" is cargo-culting. If the model was trained with a dot-product objective, the vector *norm* often encodes confidence/frequency/magnitude you may want to keep — raw dot product, not cosine. See `references/geometry-similarity-metric.md`.

2. **Raw mean-pooled BERT embeddings are anisotropic and near-useless for similarity.** Contextual LM embeddings occupy a narrow cone (Ethayarajh 2019; "representation degeneration," Gao et al. 2019), so cosine similarities are inflated and barely discriminate. You must whiten, or — much better — use a model contrastively fine-tuned for sentence similarity (SBERT, SimCSE). Anyone computing STS from `bert-base` mean-pooling and getting bad numbers is hitting this, not a bug in their code.

3. **The point of modern SSL is to avoid representation collapse, not to "learn features" by magic.** Negatives (SimCLR/MoCo), redundancy reduction (Barlow Twins, VICReg), and stop-gradient + predictor (BYOL, SimSiam) are all *different solutions to the same collapse problem*. BYOL/SimSiam prove you don't strictly need negatives. If you understand a method as "here's how it stops collapse," you understand it.

4. **Contrastive objectives and masked/reconstruction objectives produce different geometries.** Contrastive (CLIP, SimCSE) optimizes *alignment + uniformity* (Wang & Isola 2020) → embeddings usable for cosine retrieval out of the box. Masked modeling (BERT, MAE) learns rich features great for *fine-tuning* but not directly metric-meaningful. This is exactly why you contrastively fine-tune BERT before using it for search.

5. **Unsupervised disentanglement is impossible without inductive biases or supervision** (Locatello et al. 2019, ICML best paper). β-VAE and friends "work" only via implicit architectural/data biases, and their disentanglement is highly seed-dependent. Treat any disentanglement claim as suspect until you see a metric *and* a supervision/bias story.

6. **A linear probe measures *decodability*, not *use*.** High probe accuracy means the information is linearly present, not that the model relies on it. To claim "present beyond chance," use control tasks / selectivity (Hewitt & Liang 2019). To claim the model *causally uses* it, you need intervention — amnesic probing / INLP, or activation patching — not a probe. Conflating these is the single most common interpretability error.

7. **VAEs are latent-variable models; plain autoencoders are not.** An AE learns a deterministic code with no generative semantics — sampling its latent space is meaningless. The VAE's KL term is what regularizes the latent into a usable prior-matched manifold. The signature VAE failure is **posterior collapse** (decoder ignores z, especially with a powerful autoregressive decoder), which looks like "the VAE learned nothing."

8. **A well-tuned matrix-factorization / kNN recommender beats most "neural" recommenders.** The Dacrema et al. (2019) reproducibility audit found many neural recsys papers didn't beat properly tuned MF/item-kNN baselines. Neural methods earn their keep on side information, sequences, and cold-start — not by being neural. Start with MF (ALS/BPR) as the baseline you must beat.

9. **Embeddings are point estimates; latent-variable models give distributions with a generative story.** Reach for an LVM (factor analysis, IRT, topic models, VAE) when you need uncertainty, interpretable factors, or generation. Reach for an embedding when you need a fast, transferable feature vector for similarity/transfer. They are not interchangeable.

10. **Don't trust t-SNE/UMAP geometry for anything quantitative.** Cluster *sizes*, inter-cluster *distances*, and global layout are largely artifacts of perplexity/`n_neighbors`. They're hypothesis-generation tools for *local* neighborhood structure, not evidence. (This is the hand-off boundary with the dimensionality-reduction skill — see below.)

11. **More dimensions is not better.** Beyond what the data manifold needs, extra dimensions add noise, cost, and anisotropy. Matryoshka embeddings exist precisely so you can *truncate* to the dimensionality your task tolerates. Dimension is a tuned hyperparameter, not "bigger = smarter."

12. **A reward model is a learned representation of *what the preference data rewards* — which is not "what humans want."** RLHF reward models are a Bradley-Terry head over a learned scalar; they are routinely miscalibrated and reward-hackable, and optimizing hard against one produces Goodhart effects (reward overoptimization, Gao et al. 2023). Treat the RM's scalar as a proxy representation with known pathologies.

13. **In contrastive SSL, keep the *backbone*, not the projection head.** SimCLR-style methods train an encoder *f* plus a small projection head *g* and compute the loss on *g(f(x))* — but the representation you transfer, serve, and evaluate is *f(x)*, the **pre-projection** features. SimCLR's own ablation (Chen et al. 2020) showed the layer *before* the head transfers substantially better; the head is trained to discard exactly the information the contrastive task doesn't need. Serving or probing the projection output instead of the backbone is a silent, common own-goal — and it's the first thing to check when a contrastively-trained encoder underperforms on a downstream task.

## Genuinely contested — surface the spectrum, don't pick a winner

- **Is the Information Bottleneck "compression phase" real?** Tishby & Schwartz-Ziv (2017) claimed SGD has a compression phase that explains generalization; Saxe et al. (2018) argued it's an artifact of saturating (tanh) nonlinearities and doesn't appear with ReLU. Unresolved; present both.
- **Are sparse-autoencoder features "the model's real features" or a basis we impose?** SAEs give striking monosemantic directions, but reconstruction fidelity ≠ faithfulness, feature-splitting depends on width, and whether the features are "really there" is open. Promising, not settled.
- **Does scaling alone yield better representations, or do objective/data matter as much?** The Platonic Representation Hypothesis (Huh et al. 2024) — that big models converge to a shared representation — is suggestive, not proven.
- **VAE vs diffusion vs GAN vs autoregressive as the "right" latent/generative model** — depends entirely on whether you need a usable latent, sample quality, likelihoods, or speed.
- **Bi-encoder semantic search vs good old BM25** — dense retrieval doesn't dominate sparse lexical retrieval everywhere (out-of-domain, rare entities, exact-match); hybrid is often best. Don't assume "embeddings > keywords."

When a question lands on one of these, say "this is contested" and lay out the positions. Faking consensus here is the tell of shallow understanding.

## Compact decision frameworks

**Should I use embeddings at all?** Yes when you need similarity, retrieval, clustering, transfer, or a fixed-size feature for heterogeneous/unstructured input. No (or not yet) when you need exact match/lookup (use an index/DB), interpretable factors with uncertainty (use an LVM/factor model), or when a tuned lexical/tabular baseline already solves it. Don't reach for a 1B-param encoder when TF-IDF + logistic regression clears the bar.

**Contrastive vs masked vs supervised pretraining?** Want metric-meaningful embeddings for retrieval/similarity → contrastive. Want rich features to *fine-tune* for many downstream tasks → masked/reconstruction. Have abundant labels for the actual target → supervised (or supervised contrastive) usually wins; SSL's value is when labels are scarce.

**Latent-variable model vs embedding?** Need uncertainty / interpretable factors / a generative model / to handle missingness principledly → LVM. Need a fast transferable similarity vector → embedding. Need both interpretability *and* scale → that's the hard research zone (disentanglement, causal rep. learning); calibrate expectations.

**Cosine vs Euclidean vs dot product?** Normalize-then-cosine when only *direction* should matter and magnitude is nuisance (most sentence/image retrieval). Raw **dot product** when magnitude carries signal you want (some recsys, models trained with dot-product softmax, MIPS retrieval). **Euclidean** when the space is metric by construction (metric-learning embeddings, some VAE latents). Decisive rule: **match the inference-time metric to the training objective's metric.**

**Frozen vs fine-tune vs train-from-scratch?** Frozen + linear probe when the pretrained features already separate your task (test this first — it's cheap). Fine-tune when the domain shifts the geometry (medical, legal, code) or you need the last few points. Train from scratch almost never — only with truly novel modalities or massive in-domain data.

**How do I evaluate embedding quality?** There is no single number. Use *intrinsic* checks (alignment/uniformity, anisotropy, kNN consistency) plus the *extrinsic* metric that matches the real use (recall@k / nDCG / MRR for retrieval; linear-probe accuracy for transfer; downstream task metric for the actual job). Beware probe expressivity, train/test leakage through augmentations, and comparing vectors across two models without a shared frame (use CKA/Procrustes, never raw cosine across spaces). Full protocol in `references/evaluation.md`.

## Runnable diagnostics (`scripts/`)

Don't eyeball these — run them. Each script is self-contained (numpy/sklearn/scipy), importable as a library, and ships a `--selftest` that validates it against fixtures with known answers. They operationalize the stances above instead of leaving the reader to reimplement subtle math (CKA centering, control-task selectivity, effective rank).

- `scripts/anisotropy_effective_rank.py` — anisotropy (mean random-pair cosine, with an exact closed-form cross-check) plus effective rank / participation ratio. **Run before trusting any cosine numbers** (stance #2).
- `scripts/collapse_spectrum.py` — singular-value spectrum; distinguishes *complete* from *dimensional* collapse and locates the cliff (stance #3, #7).
- `scripts/alignment_uniformity.py` — Wang & Isola alignment & uniformity, to localize *why* a contrastive space is good or bad (stance #4).
- `scripts/linear_probe_with_controls.py` — linear probe with Hewitt–Liang control tasks and **selectivity**, including the memorization guard. Measures decodability, not use (stance #6).
- `scripts/cka_rsa.py` — linear/RBF CKA, RSA, and orthogonal Procrustes for comparing two representations of the same items — never raw cosine across independently-trained spaces.

## Failure modes and misconceptions to catch

When reviewing someone's reasoning or code, watch for these — each is a concrete, common mistake:
- Computing cosine on **un-normalized** or **anisotropic** embeddings and trusting the numbers.
- Reading a **probe's accuracy as "the model uses this feature."** (It's decodability, not use.)
- Believing **word2vec analogies (king−man+woman)** are robust — they're cherry-picked and brittle (Linzen 2016; the standard implementation even excludes the input words from the answer set).
- Assuming **more embedding dimensions help**; ignoring that they add anisotropy and cost.
- **Train/test leakage** in SSL eval (augmentation overlap; probing on pretraining data; duplicate near-images across split). When a model aces a benchmark but underperforms on fresh queries, suspect near-duplicate contamination — the fix is a de-duplicated, distribution-shifted eval set.
- **Cross-version eval drift:** when model architecture, training data, or tokenizer changes between versions, the same benchmark can measure different things. Always pair headline metrics with anchor evals (fixed test sets + fixed pipeline) so version comparisons are meaningful.
- Calling a VAE "broken" when it's **posterior collapse**; or not noticing **dimensional collapse** (representations live in a subspace) vs complete collapse. When recommending a VAE for generation or smooth interpolation (e.g., molecules), proactively flag posterior collapse risk — a powerful decoder can learn to ignore the latent entirely (KL → 0, traversals do nothing).
- Trusting **t-SNE/UMAP** cluster sizes and distances.
- Treating embeddings as **objective/neutral** — they inherit data bias and objective choices.
- Comparing embeddings **across models** with raw cosine (different, unaligned coordinate systems).
- Expecting **pure collaborative filtering to handle cold-start** (a brand-new item/user has no interactions to embed).
- Assuming a shared multimodal space (CLIP) is **metrically uniform across modalities** — there's a persistent **modality gap** (Liang et al. 2022); image and text embeddings occupy separate cones.
- **Reward-model overoptimization** — pushing RL hard against a fixed RM degrades true quality past a point (Goodhart).
- Serving or evaluating the **projection-head output** of a contrastive model instead of the **backbone** features — the head is discarded by design, and pre-projection features transfer better.
- Assuming that a **representation direction** (steering vector, concept probe) will transfer across models, layers, or contexts — the same direction can have different effects or none at all in a different setting; always caveat "this is the direction in this model under these conditions."

## How this skill relates to neighboring fields (for "how does X connect" questions)

Representation learning is the connective tissue between: **dimensionality reduction & manifold learning** (classical, often-linear or unsupervised special cases — PCA is a linear autoencoder; UMAP/t-SNE are visualization-grade nonlinear cousins); **latent-variable & probabilistic modeling** (VAEs, factor analysis, IRT, topic models all posit latent codes — the difference is deterministic point-embedding vs distributional latent); **information theory** (the bottleneck/sufficiency view of what a good code keeps); **deep learning** (the engine that makes learned features beat hand-engineered ones); **reinforcement learning** (state representations, world models, reward modeling); **psychometrics** (IRT and factor analysis are latent-trait representation learning predating ML by decades — same math, different vocabulary); **recommender systems** (embeddings of users/items are the core); **foundation models** (their internal representations *are* the product the field studies); and **AI agents** (memory, retrieval, and tool-grounding all run on representations). When asked "how does representation learning connect to [field]," name the shared object (a learned latent code) and the precise difference in assumptions. Depth in `references/foundations.md` and `references/frontier-and-relationships.md`.

## When to consult the reference files

Pull the file that matches the question; you don't need all of them.

- `references/foundations.md` — what a representation is, feature learning vs hand-engineering, manifold hypothesis, distributed representations, information bottleneck, inductive biases, cross-field relationships in depth.
- `references/geometry-similarity-metric.md` — latent-space geometry, anisotropy/whitening, cosine vs Euclidean vs dot product (with the math), metric learning (triplet, N-pair, ArcFace), alignment & uniformity, Platonic representation hypothesis.
- `references/ssl-contrastive.md` — SSL taxonomy, InfoNCE/SimCLR/MoCo, non-contrastive (BYOL/SimSiam/Barlow Twins/VICReg), masked modeling (BERT/MAE), collapse taxonomy, JEPA.
- `references/generative-latent.md` — autoencoders, VAE/ELBO/reparameterization, posterior collapse, β-VAE, VQ-VAE, disentanglement and its impossibility result, diffusion-as-representation.
- `references/embeddings-retrieval-recsys.md` — word2vec/GloVe vs contextual vs sentence embeddings, pooling/normalization/dimension, semantic search, ANN/vector DBs (HNSW/IVF/PQ), bi- vs cross-encoder + rerank, recsys (MF/ALS/BPR, two-tower, cold-start), preference modeling (Bradley-Terry).
- `references/transformers-llms.md` — how transformers build representations (residual stream, attention as routing), what layers encode, scaling laws for representations, reward models in RLHF as learned preference representations.
- `references/interpretability.md` — probing (linear, selectivity, amnesic/INLP), superposition, sparse autoencoders, representation engineering / steering vectors, activation patching, CKA/representational similarity.
- `references/evaluation.md` — intrinsic vs extrinsic, the linear-probing protocol done right, kNN eval, retrieval metrics, disentanglement metrics (MIG/DCI/SAP) and their critiques, leakage pitfalls.
- `references/frontier-and-relationships.md` — multimodal alignment & modality gap, graph & knowledge-graph embeddings (node2vec, GCN/GraphSAGE; TransE/DistMult/ComplEx/RotatE), causal representation learning, representation collapse research, current directions. **This is the file most likely to go stale — refresh it against recent literature when currency matters.**

## Tone and stance

Be **direct and confident** on the settled positions and **honest about genuine disagreement** on the contested ones — never blur the two. **Show the math** when it settles a question (the cosine/Euclidean identity, an ELBO decomposition, an InfoNCE gradient) — numbers end debates that hand-waving prolongs. Lead with the **load-bearing distinction** rather than a definitions dump. And when someone's premise is subtly wrong ("which is better, word2vec or BERT embeddings?"), fix the premise first — it's usually a category error, and naming that is more useful than answering the literal question.
