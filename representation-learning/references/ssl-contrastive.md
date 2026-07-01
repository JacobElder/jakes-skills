# Self-Supervised and Contrastive Learning

The taxonomy, the methods, and the single organizing question: **how does this method avoid collapse?**

## Contents
1. The SSL taxonomy
2. Contrastive methods (InfoNCE family)
3. Non-contrastive methods (no negatives)
4. Masked / reconstruction modeling
5. The collapse taxonomy
6. Contrastive vs masked: which geometry you get
7. JEPA and predict-in-representation-space

---

## 1. The SSL taxonomy

Self-supervised learning = create a supervised signal from unlabeled data via a pretext task. Three broad families:
- **Contrastive** — learn invariances by pulling augmented views together and pushing other samples apart (SimCLR, MoCo, CLIP).
- **Non-contrastive / self-distillation** — pull views together with an architectural trick that prevents collapse *without* negatives (BYOL, Grill et al. 2020; SimSiam, Chen & He 2021; DINO, Caron et al. 2021) or a redundancy-reduction loss (Barlow Twins, Zbontar et al. 2021; VICReg, Bardes et al. 2022).
- **Generative / reconstruction** — predict masked or corrupted parts of the input (BERT, GPT, MAE (He et al. 2022), denoising autoencoders).

The deepest way to organize them is not by family but by **collapse-prevention mechanism** (§5).

## 2. Contrastive methods (InfoNCE family)

**InfoNCE / NT-Xent loss.** For a positive pair (i, j) among a batch with other samples as negatives:
L = −log[ exp(sim(z_i,z_j)/τ) / Σ_k exp(sim(z_i,z_k)/τ) ]
It's a softmax classification: "which of these is my positive?" — i.e. **cross-entropy** over a (1 positive + N negatives) set, which is why the loss reads like categorical cross-entropy with the positive as the target class. It is a **lower bound on mutual information** between views: I(z_i; z_j) ≥ log(N) − L_InfoNCE, so more negatives N raise the achievable bound (Oord et al. 2018, CPC).
- **Temperature τ** matters a lot: low τ sharpens focus on hard negatives (good separation, can be unstable); high τ smooths. Tuning τ is not optional.
- **SimCLR (2020):** two augmentations of each image, in-batch negatives, NT-Xent. Showed strong augmentations (crop + color jitter especially) and **large batch sizes** (more negatives) drive performance.
- **MoCo (2019):** decouples #negatives from batch size via a **momentum encoder** + a queue/memory bank of past embeddings, so you get many negatives on modest hardware. The momentum (EMA) encoder gives a slowly-moving, consistent target.
- **CLIP (2021):** contrastive across *modalities* — image and its caption are the positive pair, other captions are negatives. Yields a shared image-text space enabling zero-shot classification. (Modality gap caveat in `frontier-and-relationships.md`.)

Negatives are the repulsion that prevents collapse. **False negatives** (a true semantic match sampled as a negative) are a real failure source in large in-batch schemes.

**The projection head — keep the backbone, not the head.** SimCLR and its descendants apply the contrastive loss not to the encoder output *f(x)* directly but to *g(f(x))*, where *g* is a small MLP projection head. The representation you keep for downstream use is *f(x)* (pre-projection); *g* is **discarded after pretraining**. SimCLR's ablation (Chen et al. 2020) found the pre-projection features transfer markedly better — the head is trained to throw away information (e.g. augmentation-specific nuisance) that helps the contrastive task but hurts transfer. Practical consequence: if you serve, probe, or evaluate the projection output, you are using the wrong tensor, and a contrastively-trained encoder that "underperforms" is often hitting exactly this. Non-contrastive methods (BYOL, SimSiam, DINO, VICReg) also use projector (and sometimes predictor) heads with the same keep-the-backbone rule.

## 3. Non-contrastive methods (no negatives)

The surprising result: you can drop negatives entirely if you prevent collapse another way.
- **BYOL (2020):** online network predicts the target network's representation of another view; target is an **EMA** of the online net; a **predictor head + stop-gradient** on the target breaks the symmetry that would otherwise collapse everything to a constant. No negatives, yet no collapse.
- **SimSiam (2021):** strips even the momentum encoder — just **stop-gradient + predictor**. Demonstrated that stop-gradient is the load-bearing trick. (Mechanistically it behaves like an EM / alternating optimization.)
- **Barlow Twins (2021):** make the cross-correlation matrix between two views' embeddings close to the identity — diagonal = 1 (invariance), off-diagonal = 0 (**redundancy reduction**). Collapse is prevented by the decorrelation term, not by negatives.
- **VICReg (2022):** explicit three-term loss — **V**ariance (keep each dimension's variance above a floor → anti-collapse), **I**nvariance (views agree), **C**ovariance (decorrelate dimensions). The most legible "here are the three things you must enforce" formulation.
- **DINO (2021):** self-distillation with a momentum teacher + **centering and sharpening** of the teacher output to prevent collapse; famously yields attention maps that segment objects.

## 4. Masked / reconstruction modeling

- **Masked language modeling (BERT):** mask ~15% of tokens, predict them from bidirectional context. Learns rich contextual features; *not* directly metric-meaningful (see §6).
- **Autoregressive (GPT):** predict next token. Also representation learning as a side effect of a generative objective.
- **Masked autoencoders (MAE, 2021):** mask ~75% of image patches, reconstruct pixels with an asymmetric encoder-decoder (encoder sees only visible patches). High masking ratio is the key — images are redundant, so easy masking is too easy. Reconstruction objective → great fine-tuning features, weaker linear-probe / off-the-shelf-similarity features than contrastive.

## 5. The collapse taxonomy

"Collapse" is not one thing — name which:
- **Complete (constant) collapse:** encoder maps everything to the same point. Loss looks "solved." Prevented by negatives / variance terms / stop-gradient tricks.
- **Dimensional collapse:** embeddings span only a low-dimensional subspace of the available dimensions (some singular values → 0); you "have" 768 dims but effectively use 30. Diagnose via the singular-value spectrum of the embedding matrix. Contrastive learning can still suffer this; VICReg's covariance term and whitening directly fight it.
- **Cluster / neural collapse:** in *supervised* late training, class features collapse to their class means arranged as a simplex (Papyan et al. 2020) — a different, often-benign phenomenon.
Reporting "my SSL model's loss went to zero and downstream accuracy is chance" → almost always complete collapse; "downstream is mediocre and singular values are lopsided" → dimensional collapse.

**Fixing dimensional collapse:** if the singular-value spectrum is top-heavy (a few large values, many near zero), the encoder is not using the full embedding space. Mitigations: (1) add a **decorrelation / covariance loss** — VICReg and Barlow Twins regularize the off-diagonal covariance to near zero, directly fighting dimensional collapse; (2) **whitening** the embeddings (ZCA or iterative normalization); (3) stronger augmentations or lower temperature to increase the effective pull across views.

## 6. Contrastive vs masked: which geometry you get

This is a high-value distinction (a classic comparison eval):
- **Contrastive** explicitly optimizes the *embedding geometry* (alignment + uniformity on a hypersphere) → embeddings are **directly usable for cosine retrieval / kNN / clustering** and strong at **linear probing**.
- **Masked/reconstruction** optimizes *predicting content* → embeddings encode rich information but the **geometry isn't shaped for similarity**; they shine after **fine-tuning**, and underperform contrastive on frozen linear-probe and off-the-shelf retrieval.
Practical upshot: for retrieval you either use a contrastive model or contrastively fine-tune a masked one (SBERT/SimCSE). For "pretrain then fine-tune on each task," masked modeling is excellent. Neither is "better" unconditionally — they target different uses.

## 7. JEPA and predict-in-representation-space

Joint-Embedding Predictive Architectures (LeCun; I-JEPA 2023, V-JEPA) predict the *representation* of masked regions rather than reconstructing pixels/tokens. The argument: pixel reconstruction wastes capacity on unpredictable low-level detail; predicting in latent space focuses on semantic structure and avoids the representational cost of modeling noise. Collapse is prevented architecturally (stop-gradient/EMA target, like BYOL). Conceptually it sits between masked modeling (predictive) and non-contrastive (latent-space targets, no negatives).

## 8. Domain-valid augmentations

The quality of contrastive representations depends critically on **which augmentations define a positive pair** — they encode what the model learns to be invariant to. Domain knowledge should drive this:

- **Images:** random crop + color jitter is the SimCLR default. Works because color and exact crop position are usually irrelevant for semantic category.
- **Text:** paraphrase, back-translation, or dropout-based augmentation (SimCSE). *Not* random word deletion — it corrupts syntax and isn't a valid semantic invariance.
- **DNA / genomic sequences:** **reverse-complement** is the canonical augmentation — the same double-stranded DNA can be read from either strand, so reverse-complement pairs are true semantic equivalents. k-mer masking, species-matched sequences.
- **Molecular graphs:** 3D rotation and reflection; atom-type masking; valid bond/stereochemistry perturbations.
- **Audio:** time-stretch, pitch-shift, frequency masking (SpecAugment); *not* random noise injection beyond realistic levels.
- **Point clouds:** 3D rotation, jitter, subsampling.

When someone applies SSL to a new domain, the first question is: **what invariances should the model learn?** The augmentation choice is where that answer lives. Using SimCLR's image augmentations on a new modality is the number-one error.
