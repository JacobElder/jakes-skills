# Multimodal, Graph/KG Embeddings, and the Research Frontier

Cross-modal alignment, graph and knowledge-graph embeddings, and the active research directions. **This file dates fastest — refresh the frontier section against recent literature when currency matters (knowledge current to early 2026).**

## Contents
1. Multimodal representations and the modality gap
2. Graph embeddings
3. Knowledge-graph embeddings
4. Causal representation learning
5. The information bottleneck (status)
6. Representation collapse (research view)
7. Current directions

---

## 1. Multimodal representations and the modality gap

- **CLIP-style contrastive alignment:** train image and text encoders so matched pairs are close, mismatched far, in a *shared* space → zero-shot classification (compare an image to text class prompts), cross-modal retrieval. The positive pair is (image, caption); other captions are negatives.
- **The modality gap (Liang et al. 2022):** in the "shared" space, image embeddings and text embeddings actually occupy **two separate cones/regions** with a gap between them — they are *aligned in relative geometry* (a cat image is near "cat" text *relative to other texts*) but not interleaved. Caused by initialization + the contrastive temperature; partly closable, and the gap's size affects downstream transfer. So "CLIP puts images and text in the same space" is true only in the relative sense — don't assume metric uniformity across modalities.
- **Beyond dual-encoder:** fusion architectures (cross-attention: ViLBERT, Flamingo, and modern VLMs) interleave modalities for richer interaction (the cross-encoder analogue), vs CLIP's bi-encoder. Same retrieve-vs-rerank trade-off as text search.
- **Any-to-any / bind-style** (ImageBind): align many modalities to one anchor (usually image) so they share a space transitively.

## 2. Graph embeddings

Represent nodes (or edges/subgraphs) as vectors preserving graph structure:
- **Shallow / random-walk (DeepWalk, Perozzi et al. 2014; node2vec, Grover & Leskovec 2016):** run random walks, treat node sequences like sentences, apply skip-gram. node2vec's p,q biases walks between **homophily** (community) and **structural equivalence** (role). Transductive — no embedding for unseen nodes.
- **Matrix-factorization view:** many shallow methods implicitly factorize a (powered/normalized) adjacency or PMI matrix (NetMF) — the same MF↔embedding duality as word2vec.
- **GNNs (GCN, GraphSAGE, GAT):** learn node representations by **message passing** — aggregate neighbors' features iteratively. **Inductive** (GraphSAGE, GAT) → embed unseen nodes from features, fixing the cold-start/transductive limitation. Watch **oversmoothing** (too many layers → all node embeddings converge) — the GNN analogue of representation collapse.

**Practical design call:** whenever new nodes appear at serving time (new accounts, new users, new fraud entities), choose an **inductive GNN** (GraphSAGE, GAT) over a transductive one (GCN trained on a fixed graph) — transductive methods have no way to embed a node they weren't trained on. This applies directly to fraud detection, recommendation, and any dynamic graph. Depth budget: typically 2–3 layers is sufficient and avoids oversmoothing; deeper GNNs often *hurt* because all nodes converge to similar representations.

## 3. Knowledge-graph embeddings

Embed entities and relations so that scored triples (head, relation, tail) rank true facts above false ones — used for link prediction / KG completion:
- **TransE** (Bordes et al. 2013): relation = translation, h + r ≈ t. Simple, but can't model symmetric or 1-to-many relations.
- **DistMult** (Yang et al. 2015): bilinear diagonal; scores via a multiplicative interaction — but is inherently **symmetric** (can't distinguish (a,r,b) from (b,r,a)).
- **ComplEx** (Trouillon et al. 2016): complex-valued embeddings → models **asymmetric** relations (fixes DistMult's flaw).
- **RotatE** (Sun et al. 2019): relation = rotation in complex space → models symmetry, antisymmetry, inversion, composition.
- **GNN-based (R-GCN, CompGCN):** message passing over the relational graph.
The progression TransE → DistMult → ComplEx → RotatE is a clean story of **adding the inductive bias needed to express more relation types** — a good illustration of "representation capacity = which structures the geometry can encode."

## 4. Causal representation learning

The goal: recover latent variables that are not just predictive but **causal** — disentangled factors corresponding to real generative mechanisms, so the representation supports intervention and generalizes under distribution shift (Schölkopf et al. 2021). Motivated by the limits of statistical SSL (correlational, can't guarantee the right factors — cf. the disentanglement impossibility result). **Identifiability** is the core technical question: under what conditions can you provably recover the true factors? Pure i.i.d. unsupervised is non-identifiable; leverage helps — **interventions/multiple environments**, **temporal structure** (ICA-style, time-contrastive), **auxiliary labels** (iVAE), or known mechanism sparsity. Still mostly theory + synthetic benchmarks; the promise is OOD-robust, manipulable representations. Connect to: disentanglement (the supervised/biased version), domain generalization, and world models in RL.

## 5. The information bottleneck (status)

IB frames a representation as maximizing I(Z;Y) while minimizing I(Z;X) — minimal sufficiency. **Deep variational IB** (Alemi et al. 2017) makes it trainable and improves robustness/calibration. The **contested** part is the *explanatory* claim (Tishby & Schwartz-Ziv 2017) that SGD training has a distinct "compression phase" that causes generalization; Saxe et al. (2018) showed it's largely an artifact of **saturating nonlinearities** (tanh) and doesn't appear with ReLU, and MI in deterministic nets is ill-defined without care. Use IB as a *design objective and intuition* (it works), not as a settled *explanation* of why deep nets generalize.

## 6. Representation collapse (research view)

Beyond the SSL-training taxonomy (see `ssl-contrastive.md`), collapse recurs across the field as the same underlying pathology — *the representation stops using its available capacity*:
- **Complete / dimensional collapse** in SSL.
- **Neural collapse** (Papyan et al. 2020) in supervised terminal-phase training (class means → simplex ETF).
- **Oversmoothing** in deep GNNs.
- **Codebook collapse** in VQ-VAE.
- **Posterior collapse** in VAEs.
- **Mode collapse** in GANs (generator, but related representational degeneracy).
Recognizing these as one family — and naming the specific anti-collapse mechanism each method uses (negatives, variance floors, stop-gradient, decorrelation, KL annealing, EMA codebooks) — is a hallmark of depth.

## 7. Current directions (refresh me)

As of early 2026, active threads: **scaling SAEs / dictionary learning** to frontier models and stress-testing whether features are faithful (top-k/JumpReLU/gated SAEs, transcoders, crosscoders); **representation/activation engineering** for control and safety (steering, concept erasure — LEACE/R-LACE); **the Platonic Representation Hypothesis** and cross-model representational convergence; **causal representation learning** identifiability; **multimodal/any-to-any** representations and closing the modality gap; **embedding models** for RAG (long-context, instruction-tuned, Matryoshka, multi-vector/ColBERT-style late interaction); **representation-space SSL** (JEPA family) as an alternative to pixel/token reconstruction; and **mechanistic interpretability circuits** built on top of SAE features. Verify specifics against recent papers before stating them as current — this list is the part of the skill most likely to be stale.
