# Evaluating Representation Quality

There is no single "quality" number. Match the measurement to the use, and avoid the leakage and probe-expressivity traps.

## Contents
1. The intrinsic vs extrinsic split
2. The linear-probing protocol (done right)
3. kNN and clustering evaluation
4. Retrieval metrics
5. Geometry diagnostics (anisotropy, collapse, alignment/uniformity)
6. Disentanglement metrics and their critiques
7. Cross-representation comparison
8. The leakage and confound checklist

---

**Runnable versions of these diagnostics live in `scripts/`** — don't reimplement them by hand (the math has subtle traps: CKA centering, control-task selectivity, effective rank). Use `anisotropy_effective_rank.py`, `collapse_spectrum.py`, `alignment_uniformity.py`, `linear_probe_with_controls.py`, and `cka_rsa.py`; each self-tests against fixtures via `--selftest`.

## 1. The intrinsic vs extrinsic split

- **Extrinsic (preferred when you have a real task):** plug the representation into the actual downstream system and measure the task metric (retrieval recall@k, classification accuracy, recommender nDCG, RAG answer quality). This is ground truth — but task-specific.
- **Intrinsic (cheap, task-agnostic, diagnostic):** measure properties of the space itself (anisotropy, alignment/uniformity, kNN consistency, probe accuracy). Useful for fast iteration and debugging, but a good intrinsic number does not guarantee downstream gains. Use intrinsic to *diagnose*, extrinsic to *decide*.

Default to a small panel, not one number: one extrinsic metric matching the real use + two or three intrinsic diagnostics.

## 2. The linear-probing protocol (done right)

The standard transfer evaluation for pretrained representations: **freeze** the encoder, train only a **linear** classifier on top, report accuracy.
- Freeze the backbone (no fine-tuning) — you're measuring the *representation*, not the model's capacity to learn the task.
- Linear on purpose (a deep probe measures the probe; see `interpretability.md`).
- For *interpretability* claims (does this encode property F), add **control tasks** and report **selectivity**, not raw accuracy.
- Report the probing **layer** — middle layers often beat the last layer (see `transformers-llms.md`); sweep them.
- Linear probe vs fine-tuning measure different things: probe = "are good features already linearly present"; fine-tune = "can this initialization reach a good solution." A representation can probe poorly yet fine-tune well (MAE) and vice versa. Report which you ran.

## 3. kNN and clustering evaluation

- **kNN accuracy** on frozen features (no training at all) is the most assumption-light transfer metric — purely a property of the geometry. Great companion to linear probing.
- **Clustering metrics** when labels exist: cluster the embeddings and score with NMI / ARI vs ground-truth labels. Silhouette etc. are unsupervised but can be gamed by anisotropy. Don't read cluster *shapes* off t-SNE/UMAP (artifacts).

## 4. Retrieval metrics

For embeddings used in search/RAG/recsys, rank-aware metrics on held-out relevance judgments:
- **Recall@k / Hit@k** — is the right item in the top k (candidate generation).
- **MRR** — reciprocal rank of the first relevant (one-right-answer tasks).
- **nDCG@k** — graded relevance, position-discounted (the general-purpose ranking metric).
- **MAP** — multiple relevant items.
Two separate things to measure: **embedding quality** (recall vs an *exact* NN baseline) and **index quality** (ANN recall vs exact). A drop can come from either — isolate them. Standard benchmark: **MTEB** (Muennighoff et al. 2022) for text embedding models, **BEIR** (Thakur et al. 2021) for zero-shot retrieval (and remember dense ≠ dominant OOD).

## 5. Geometry diagnostics

- **Anisotropy:** average cosine between random pairs (should be near 0 for isotropic; high = degenerate cone). Or the ratio of the top singular value to the rest.
- **Dimensional collapse:** singular-value spectrum of the embedding matrix — a cliff to near-zero means effective dimensionality ≪ nominal.
- **Alignment & uniformity** (Wang & Isola): two scalars — positive-pair closeness and sphere coverage — that localize *why* a contrastive embedding is good or bad.
- **Effective rank / participation ratio:** a continuous "how many dimensions are really used" number.

## 6. Disentanglement metrics and their critiques

If someone claims a disentangled representation, ask which metric — and remember all of them require **ground-truth factors** (so they're only computable on synthetic/controlled data like dSprites):
- **MIG (Mutual Information Gap):** for each factor, gap in MI between its top-2 latent dimensions — rewards one-dimension-per-factor.
- **DCI (Disentanglement, Completeness, Informativeness):** three numbers from a feature-importance matrix.
- **SAP (Separated Attribute Predictability).**
- **FactorVAE / β-VAE metric:** classifier-based.
Critiques to deliver: metrics **disagree** with each other; they need ground-truth factors you rarely have; and — per Locatello et al. 2019 — scores are dominated by **seed/hyperparameters**, and unsupervised model selection can't reliably pick disentangled models. So "we got MIG 0.4" from one run is weak evidence; report variance across seeds and which metric.

## 7. Cross-representation comparison

To ask "did model A and model B learn similar representations" (not "is A better"): **CKA** (orthogonal- and scale-invariant) or **RSA** (compare distance matrices). For aligning two embedding sets of the same items: **orthogonal Procrustes**. Never raw cosine across two independently-trained spaces.

## 8. The leakage and confound checklist

Most "amazing representation" results that don't replicate die here:
- **Augmentation leakage:** in SSL kNN/linear eval, ensure eval augmentations don't leak the label or duplicate train views.
- **Near-duplicate train/test split:** large image/text corpora have near-dupes across the split → inflated retrieval/probe numbers. De-dupe by similarity, not exact match.
- **Probing on pretraining data:** if the probe's eval set overlaps pretraining, you measure memorization.
- **Anisotropy confound:** apparent "high similarity" may be the cone, not real signal — check anisotropy before trusting cosine numbers.
- **Metric mismatch:** evaluating with cosine a model trained for dot product (or vice versa) understates it.
- **Probe expressivity:** a strong probe inflates "decodability" — use linear + control.
- **Single-seed reporting:** representations are seed-sensitive (especially disentanglement, small-data SSL) — report variance.
- **Train/test contamination in benchmarks:** public benchmark text may be in the pretraining set — a live concern for MTEB-style leaderboards.
- **Near-duplicate contamination:** if a new model aces a retrieval benchmark but underperforms on fresh queries, compute embedding similarity between train and eval items; high-similarity pairs indicate contamination. The fix is not re-running — it's building a **de-duplicated, distribution-shifted eval set** that doesn't overlap the training distribution on near-duplicates.
- **Cross-version eval comparability:** when the model architecture, pretraining data, or tokenizer changes between versions, the same eval can measure different things. Always include anchor evals (frozen test sets evaluated with a fixed pipeline) so improvements are comparable across model generations.

## 9. Temporal evaluation splits for graph and transactional representations

For fraud detection, financial graph representations, and other settings with **temporal dynamics**, random splits are nearly always invalid: a random split allows future transaction patterns to leak into training, artificially inflating detection scores.

**Always use temporal splits:** train on data before a cutoff date, evaluate on data after it. This mirrors real deployment where the model is trained today and must detect fraud on future transactions it has never seen. Random splits can overstate performance by 20-50% in adversarial settings where fraudsters adapt over time.
