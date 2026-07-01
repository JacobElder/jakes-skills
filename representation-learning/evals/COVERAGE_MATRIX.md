# Coverage Matrix — representation-learning eval suite

54 evals across 13 capability categories and 9 topic areas (reference files), plus a 22-query trigger set (`trigger_evals.json`) and 5 tested diagnostic scripts (`scripts/`). Generated from `evals/evals.json`.

## A. Capability category × eval IDs

| Category | # | Eval IDs |
|---|---|---|
| knowledge | 7 | 1, 2, 3, 4, 48, 51, 52 |
| conceptual | 5 | 5, 6, 7, 8, 47 |
| comparison | 6 | 9, 10, 11, 12, 13, 49 |
| reasoning | 4 | 14, 15, 16, 46 |
| application | 7 | 17, 18, 19, 20, 21, 50, 53 |
| design | 3 | 22, 23, 24 |
| debugging | 5 | 25, 26, 27, 28, 29 |
| adversarial | 5 | 30, 31, 32, 33, 34 |
| triggering | 2 | 35, 36 |
| multi-step | 2 | 37, 38 |
| generalization | 2 | 39, 40 |
| advanced-research | 5 | 41, 42, 43, 44, 45 |
| calibration | 1 | 54 |

## B. Topic area (reference file) × eval IDs

Each eval may test several topic areas; it appears under every area it touches.

| Topic area / reference | # evals | Eval IDs |
|---|---|---|
| foundations | 17 | 1, 5, 12, 18, 21, 31, 34, 35, 36, 37, 38, 39, 41, 43, 47, 50, 54 |
| geometry-similarity-metric | 10 | 10, 14, 22, 27, 29, 30, 40, 45, 46, 52 |
| ssl-contrastive | 9 | 6, 9, 15, 22, 28, 39, 44, 51, 52 |
| generative-latent | 6 | 2, 12, 19, 25, 33, 38 |
| embeddings-retrieval-recsys | 15 | 3, 11, 13, 16, 17, 18, 23, 24, 26, 31, 35, 37, 46, 48, 53 |
| transformers-llms | 6 | 7, 9, 16, 20, 24, 37 |
| interpretability | 5 | 4, 7, 8, 20, 32 |
| evaluation | 17 | 8, 14, 15, 17, 19, 21, 22, 26, 27, 28, 32, 33, 34, 40, 42, 47, 50 |
| frontier-and-relationships | 9 | 23, 29, 38, 41, 42, 43, 44, 45, 49 |
| embeddings (practical, folded into embeddings-retrieval-recsys) | 1 | 1 |

## C. Difficulty distribution

| Difficulty | # |
|---|---|
| Easy | 3 |
| Medium | 17 |
| Hard | 20 |
| Expert | 14 |

## D. Verification and negative assertions

- **Verified quantitative ground truth** (closed-form/numeric): evals 2, 10, 30, 48, 51, 52, 53.
- **`must_not` negative assertions** (a response FAILS if it commits the trap; also folded into `expectations`): evals 5, 8, 11, 14, 15, 16, 18, 21, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 50.

## E. Gap analysis (updated)

**Closed since the first pass.** (1) **Runnable diagnostics** — the five `scripts/` (anisotropy/effective-rank, collapse spectrum, alignment/uniformity, linear-probe-with-controls, CKA/RSA/Procrustes) now operationalize the stances instead of leaving the reader to reimplement subtle math; each self-tests against fixtures with known answers. (2) **Negative assertions** — 21 evals carry `must_not` items that fail a response committing the documented trap (defaulting to cosine, reading probe accuracy as use, calling a VAE broken, endorsing neural-recsys-by-default, treating word2vec analogies as proof, accepting a single quality number). These are folded into `expectations` so the grader checks them. (3) **Over-engineering guard** — eval 54 (category `calibration`) fails a verbose/reference-dumping answer to a one-sentence question. (4) **More verified ground truth** — added InfoNCE↔cross-entropy↔MI (51), alignment/uniformity definitions (52), and PQ memory arithmetic (53); seven evals now have closed-form ground truth. (5) **Inter-skill boundary negatives** — the trigger set now includes a dimensionality-reduction-methodology query and a difference-in-differences causal query that must route to those dedicated skills, not this one. (6) **Projection-head lesson** — added as settled stance #13, a failure mode, and a paragraph in `ssl-contrastive.md`.

**Remaining (deliberate) gaps.**
1. **Triggering / multi-step / generalization stay light in the main suite (2 each).** Triggering is covered by the 22-query `trigger_evals.json` (the real "does the skill fire" test); evals 35–36 cover in-conversation "you don't need representation learning here." If you scale the suite, 2–3 more multi-step and generalization items are the highest-value adds.
2. **Metric learning (triplet/ArcFace) and MF objectives (ALS/BPR)** are still tested mostly inside application/design evals (22, 24, 11, 18), not as isolated comparison items. ArcFace now has ground-truth-adjacent coverage only via the geometry reference, not a dedicated eval.
3. **Scaling laws (Chinchilla) and the emergence debate** remain in the `transformers-llms` reference without a dedicated eval.
4. **All evals are single-turn**, matching the harness design — no multi-turn/clarification eval.

**Grading note (unchanged).** `expectations` (including the folded-in `must_not` items) are necessary-but-not-sufficient proxies for the richer `scoring_rubric`. Pair assertion pass-rate with judge review of the `excellent_answer` characteristics — the adversarial, advanced-research, and calibration items reward judgment that binary assertions under-measure. The `must_not` items raise the floor by catching confidently-wrong answers that hit every positive assertion while still giving bad advice.
