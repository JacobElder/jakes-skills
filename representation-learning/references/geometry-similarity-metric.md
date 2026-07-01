# Representation Geometry, Similarity, and Metric Learning

The geometry of embedding spaces, how to measure similarity correctly, and how to *train* a space to have the geometry you want.

## Contents
1. The cosine / Euclidean / dot-product relationship (with math)
2. Anisotropy and how to fix it
3. Alignment and uniformity
4. Metric learning objectives
5. Cross-space comparison (you cannot just use cosine)
6. The Platonic Representation Hypothesis

---

## 1. Cosine vs Euclidean vs dot product — settle it with algebra

For vectors a, b:
- dot product: a·b = ‖a‖‖b‖cos θ
- cosine: cos θ = a·b / (‖a‖‖b‖)
- squared Euclidean: ‖a−b‖² = ‖a‖² + ‖b‖² − 2a·b

**If a and b are L2-normalized** (‖a‖=‖b‖=1): ‖a−b‖² = 2 − 2cos θ. Euclidean distance and cosine similarity are then *monotonically related* — they induce **identical nearest-neighbor rankings**. So on normalized vectors, "cosine vs Euclidean" is a non-question; they agree.

The real decision is **whether to normalize**, which is the decision of **whether vector magnitude carries signal**:
- **Normalize → cosine** when only *direction* should matter (semantic similarity where you don't want frequent/long items to dominate). Most sentence/image retrieval.
- **Don't normalize → dot product (MIPS)** when magnitude is signal: models trained with a dot-product softmax (word2vec, two-tower retrieval, many recommenders) put confidence/frequency/popularity into the norm. Cosine throws that away. Maximum-inner-product search is its own ANN problem (not a metric — triangle inequality fails).
- **Euclidean** when the space is genuinely metric by construction (metric-learning embeddings trained with Euclidean triplet loss; some VAE latents).

**Decisive rule: match the inference metric to the training objective's metric.** If you don't know how the encoder was trained, that's the first thing to find out, not "default to cosine."

## 2. Anisotropy and how to fix it

Contextual LM token/sentence embeddings are **anisotropic**: they occupy a narrow cone, so even random pairs have high cosine (Ethayarajh 2019; "representation degeneration problem," Gao et al. 2019, driven by the softmax over a fixed vocabulary pushing embeddings in a shared direction). Effects: cosine similarities are compressed into a small high range and barely discriminate; raw mean-pooled BERT is poor at STS.

Fixes, roughly in increasing order of effectiveness:
- **Mean-centering / standardization** of the embedding set.
- **Whitening** (BERT-whitening): linearly transform so the covariance is identity → isotropic. Cheap, training-free, big STS gains.
- **Contrastive fine-tuning** — the real fix. SBERT (supervised NLI pairs) or **SimCSE** (unsupervised: same sentence twice through dropout = a positive pair) directly optimize alignment + uniformity and produce embeddings that are good under cosine without post-hoc surgery. Prefer a purpose-built sentence-embedding model over patching a raw LM.

If someone reports "all my BERT cosine similarities are ~0.9 and nothing separates," this is the diagnosis.

## 3. Alignment and uniformity

Wang & Isola (2020) decompose what a good contrastive embedding on the unit hypersphere optimizes:
- **Alignment:** positive pairs map close together (E‖f(x)−f(x⁺)‖² small).
- **Uniformity:** embeddings spread out to use the whole sphere (features preserved, no collapse).
These two are a clean, *measurable* lens for embedding quality: compute both on held-out data. Collapse = uniformity tanks; a model that memorizes augmentations but doesn't transfer = alignment good, uniformity bad. Better than a single opaque "quality" number.

## 4. Metric learning objectives

When you want the *geometry itself* to encode similarity (faces, retrieval, signature/verification), train the metric directly:
- **Contrastive (pairs):** pull positives together, push negatives apart beyond a margin.
- **Triplet loss:** anchor, positive, negative; enforce d(a,p) + margin < d(a,n). Sensitive to **triplet mining** — random triplets are mostly easy and uninformative; semi-hard mining (FaceNet) is the practical key.
- **N-pair / NT-Xent (InfoNCE):** use all other in-batch items as negatives; far more efficient than single triplets and the workhorse of modern contrastive learning. Large batches → more negatives → better.
- **Angular-margin softmax (SphereFace 2017 → CosFace 2018 → ArcFace, Deng et al. 2019):** instead of mining pairs, add an angular margin to a classification softmax so classes are separated by a fixed angular gap on the hypersphere. ArcFace's additive angular margin is the standard for face recognition — it gives metric-meaningful, normalized embeddings from a classification objective. A good answer to "how do I get a clean cosine space for verification" mentions ArcFace, not just triplet loss.

## 5. Cross-space comparison — you cannot just use cosine

Two models produce embeddings in **different, unaligned coordinate systems**. Raw cosine between a vector from model A and one from model B is meaningless (no shared basis; rotation/scale/permutation are unconstrained). To compare *representations* across models/layers/seeds:
- **CKA (Centered Kernel Alignment)** — similarity of two representation *matrices*, invariant to orthogonal transform and isotropic scaling. The standard tool.
- **Representational Similarity Analysis (RSA)** — compare the *distance matrices* (compare relationships, not coordinates). Borrowed from neuroscience.
- **Procrustes / linear CKA / SVCCA** — find an alignment first, then compare.
To compare two *embedding sets of the same items* for downstream use, align with **orthogonal Procrustes** before nearest-neighbor transfer. This is also how cross-lingual word embeddings are aligned (a learned orthogonal map).

## 6. The Platonic Representation Hypothesis

Huh et al. (2024): as models get larger and more capable across modalities, their representations *converge* toward a shared statistical model of reality — vision and language models come to embed concepts with increasingly similar relational geometry (measurable via mutual-nearest-neighbor / RSA-style metrics). Status: a striking empirical regularity and an organizing hypothesis, **not** a proven law. Useful when discussing why cross-modal alignment (CLIP) is even possible and why transfer works, but don't overclaim it.
