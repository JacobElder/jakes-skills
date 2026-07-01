# Embeddings in Practice: Retrieval and Recommenders

From word2vec to vector databases to two-tower recsys — the practical embedding stack and its preference-modeling core.

## Contents
1. Static vs contextual vs sentence embeddings
2. Pooling, normalization, dimension
3. Semantic search and the bi-/cross-encoder split
4. ANN and vector databases
5. Dense vs sparse vs hybrid retrieval
6. Recommender systems: matrix factorization to two-tower
7. Cold start
8. Preference modeling (the bridge to reward models)

---

## 1. Static vs contextual vs sentence embeddings

- **Static (word2vec, GloVe, fastText):** one vector per word *type*, regardless of context. word2vec's skip-gram/CBOW are shallow nets trained to predict context (skip-gram + negative sampling is a contrastive objective; it factorizes a shifted PMI matrix — Levy & Goldberg 2014). Can't disambiguate "bank" (river vs money). Analogy arithmetic (king−man+woman≈queen) is real but **brittle and cherry-picked** (Linzen 2016; the standard eval even excludes the query words from candidates).
- **Contextual (BERT, ELMo, GPT):** one vector per *token in context* — "bank" gets different vectors in different sentences. Rich, but **anisotropic and not similarity-ready off the shelf** (see geometry file).
- **Sentence/document embeddings (SBERT, SimCSE, E5, GTE, the text-embedding API models):** purpose-built, contrastively trained to make whole-text cosine meaningful. **For retrieval/RAG/clustering, use one of these — not raw BERT pooling.** This single recommendation fixes most "my embeddings are bad" reports.

Static vs contextual is usually a **category error to "rank"**: ask whether the task needs sense/context (→ contextual) or wants a fast type-level lexicon (→ static is fine and cheap).

## 2. Pooling, normalization, dimension

- **Pooling** token vectors into one: mean-pooling is the robust default; [CLS] is only good if the model was trained to make it meaningful (SBERT trains it); last-token pooling for decoder-only embedders. Attention/weighted pooling can help.
- **Normalize** (L2) when you'll use cosine — and match it to training (§geometry).
- **Dimension** is a tuned hyperparameter; bigger is not better (anisotropy, cost). **Matryoshka Representation Learning** (Kusupati et al. 2022) trains nested embeddings so a single model lets you *truncate* to 64/128/256/… dims with graceful degradation — use it to trade accuracy for index size/speed without retraining.

## 3. Semantic search and the bi-/cross-encoder split

- **Bi-encoder (dual encoder):** encode query and document *independently* into the same space; score by dot/cosine. Documents are **precomputed and indexed** → scales to billions, but the query and doc never interact, capping accuracy.
- **Cross-encoder:** feed (query, doc) *together* through the model → rich interaction, much higher accuracy, but **O(N) forward passes per query** and **not indexable**.
- **The production pattern: bi-encoder retrieve top-k, cross-encoder rerank.** Don't ask one model to do both jobs. ColBERT's **late interaction** (token-level multi-vector; Khattab & Zaharia 2020) is the middle ground — more accurate than single-vector bi-encoders, more scalable than cross-encoders.

## 4. ANN and vector databases

Exact nearest-neighbor is O(N·d); at scale you need **approximate** NN:
- **HNSW** (graph-based; Malkov & Yashunin 2018): builds a navigable small-world graph; excellent recall/latency, higher memory; the default for most vector DBs. Key knobs: M (graph degree), ef_construction, ef_search (recall/latency trade-off).
- **IVF** (inverted file / coarse quantization): cluster vectors (k-means), search only the nearest few cells (nprobe controls recall/speed).
- **PQ (Product Quantization):** compress vectors into subspace codebooks for massive memory savings; usually IVF-PQ together. Trades recall for footprint.
- **ScaNN:** anisotropic quantization tuned for MIPS.
Vector DBs (FAISS as the library; Milvus, Qdrant, Weaviate, pgvector, Pinecone as systems) wrap these with filtering/persistence. **MIPS ≠ metric search** — if you score by raw dot product, you need a MIPS-aware index, not a cosine one. Always evaluate **recall@k vs the exact baseline** when tuning ANN; a fast index that silently drops recall is a common production bug.

## 5. Dense vs sparse vs hybrid retrieval

Dense (embedding) retrieval does **not** dominate sparse lexical retrieval (BM25) everywhere: BM25 wins on exact matches, rare entities/IDs, and out-of-domain queries; dense wins on paraphrase/semantic match. **Hybrid** (combine BM25 + dense via reciprocal-rank fusion or learned weights) is frequently best, and **learned sparse** (SPLADE, Formal et al. 2021) blends the two. "Switch to embeddings" is not automatically an upgrade — measure on your queries, especially OOD.

## 6. Recommender systems: matrix factorization to two-tower

- **Collaborative filtering** = learn user and item embeddings from the interaction matrix; similar users like similar items. Implicit-feedback (clicks) ≠ explicit (ratings) and needs different objectives.
- **Matrix factorization:** R ≈ U Vᵀ; predicted preference = uᵤ·vᵢ (a bilinear *representation* model). Train with **ALS** (explicit/weighted) or **BPR** (Bayesian Personalized Ranking — a pairwise *contrastive* objective for implicit feedback: rank observed items above unobserved). A tuned MF/iALS or item-kNN is the **baseline neural methods must beat** — and frequently don't (Dacrema et al. 2019).
- **Two-tower (dual encoder):** separate user and item towers (incorporating features) into a shared space; enables ANN retrieval of items for a user. The industrial standard for candidate generation; same bi-encoder geometry as search.
- **Sequence/graph models:** transformers over interaction sequences (SASRec, BERT4Rec) and GNNs (LightGCN) help with *sequential* and *graph* structure — that's where neural earns its keep, not by being neural per se.
- **Two-stage architecture:** cheap retrieval (two-tower + ANN) → expensive ranking (cross-features, gradient-boosted or deep ranker). Mirrors retrieve-then-rerank in search.

## 7. Cold start

Pure CF **cannot embed an entity with no interactions** — a brand-new item/user has no row in the matrix. Solutions: **content/side features** (embed item text/image, user profile) via two-tower so new entities get a representation from features; hybrid CF+content; exploration (bandits). "Just use collaborative filtering" fails on day-one items; flag this whenever cold-start is in play.

## 8. Preference modeling (the bridge to reward models)

Recommenders, RLHF reward models, MaxDiff/conjoint, and psychometric choice models share one core: **learn a latent utility/representation that explains observed preferences/choices.**
- **Bradley-Terry / logistic** (Bradley & Terry 1952): P(i ≻ j) = σ(s_i − s_j) where s is a learned score. RLHF reward models are exactly this over a learned scalar from pairwise human comparisons.
- **Thurstone / random-utility / multinomial logit:** the behavioral-science lineage; choices reflect latent utilities plus noise.
- **BPR** (above) is the implicit-feedback recsys instance.
Seeing these as one family — *latent representations of preference* — is the multi-step synthesis this skill is built to support (embeddings → retrieval → recsys → preference → reward modeling). Reward-model pathologies (miscalibration, Goodhart/overoptimization) are in `transformers-llms.md`.

## 9. In-batch softmax and the popularity bias problem

Two-tower models trained with **in-batch softmax** (the standard: treat other items in the batch as negatives, maximize the softmax score of the true item) have a subtle failure mode:

**Popular items appear disproportionately as negatives** (because they appear often in the data and therefore often in the batch). The model learns to penalize popular items just because they show up as negatives so often, which hurts their retrieval scores at serving. Result: popular items are systematically under-retrieved relative to their true relevance.

**Fix: logQ correction** (also called sampled-softmax correction). Subtract the log of the item's sampling probability from its logit before the softmax: `logit_corrected = logit - log(q_i)`. This debiases the training objective and makes in-batch sampling equivalent to uniform negative sampling. Implementation: track item frequency, compute log-frequency, subtract from dot products before loss.

Secondary fix: **mixed negatives** — supplement in-batch negatives with uniformly sampled hard negatives that aren't popularity-biased.

Diagnosing: if popular items (high interaction count) have lower retrieval scores than expected from their true relevance, and tail items are over-retrieved, suspect popularity bias from in-batch sampling.
