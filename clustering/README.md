# Cluster Analysis Skill

A skill that applies practitioner-grade methodology to clustering problems: choosing the right method for the data's actual geometry, diagnosing bad clusters at their source (almost always preprocessing or assumption mismatch), and validating whether structure is real or an artifact before anyone presents it to a room.

The skill has a strong point of view. Preprocessing and the distance metric dominate your results — not the algorithm. Clustering always returns clusters, even on noise, so a result is a hypothesis until it survives stability testing and a null comparison. HDBSCAN dominates plain DBSCAN for density problems. The elbow method is weak. LPA, GMM, and LCA are one finite-mixture family; for continuous indicators, LPA and GMM are the same model. These positions are grounded in the clustering methodology literature and the skill holds them under pressure.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/clustering
```

Or manually:

```bash
cp -r jakes-skills/clustering ~/.claude/skills/clustering
```

Once installed, the skill applies automatically whenever you ask about grouping unlabeled data, choosing a clustering algorithm, validating cluster structure, diagnosing bad clusters, customer or patient segmentation, latent profile/class analysis, or interpreting results from k-means, GMM, DBSCAN, HDBSCAN, agglomerative, spectral, or mixture models.

---

## Example use cases

**"I have sensor data with weird shapes, variable density, and outliers. I was going to use k-means."**
> 50k points, 8 numeric features, unknown number of groups, definitely some junk readings I'd rather not force into a group.

The skill pushes back: k-means assumes spherical, equal-size clusters and forces every point into one — wrong on all three stated properties. It recommends HDBSCAN (handles variable density, labels noise, doesn't need k), explains why plain DBSCAN is worse (single global eps breaks under variable density), and flags scaling the 8 features first.

---

**"Silhouette is highest at k=6, so I'm going with 6."**
> "Just want a sanity check."

The skill refuses to bless a single index. It requires: multiple validation criteria (gap statistic, Davies-Bouldin alongside silhouette), a stability check (bootstrap resampling), and a null sanity check — does shuffled data produce silhouette scores nearly as good? Frames k as under-determined, not a single correct value, and interpretability as a legitimate tiebreaker.

---

**"My k-means clusters are dominated by one or two variables."**
> Features include annual_revenue (millions), employee_count (thousands), founding_year, and a 1–5 satisfaction score.

The skill diagnoses this immediately: unscaled features mean revenue and headcount dominate the Euclidean distance while satisfaction contributes almost nothing. Frames preprocessing as the dominant driver of clustering results — not the algorithm.

---

**"I want to segment users with both numeric and categorical fields. One-hot + k-means?"**
> age, total_spend, sessions_per_week, subscription_tier, acquisition_channel, country (30 values).

The skill flags the problem: Euclidean distance on one-hot encodings imposes arbitrary geometry, and a high-cardinality field like country inflates dimensionality and dominates distance. Recommends Gower distance + k-medoids (PAM) or k-prototypes, scaling the numeric features, and handling country separately.

---

## What it does

The base model knows clustering algorithms. The skill gives the agent the *precision to apply them correctly when the standard approach is wrong*. The hard cases require the agent to:

- **Reject k-means for non-convex or variable-density data** and name the right alternative (HDBSCAN, spectral) with the correct reasoning tied to the data's stated properties
- **Refuse to validate a single silhouette score** and require stability + null comparison before clusters can be called real
- **Diagnose "bad clusters" at their actual source** — almost always unscaled features or assumption mismatch, not the algorithm choice
- **Explain the LPA = GMM equivalence** for continuous indicators, and distinguish it from LCA (categorical indicators) rather than treating them as separate families
- **Warn explicitly against forcing HDBSCAN noise into clusters** — the -1 labels are a finding, not a bug; retuning purely to reduce the noise fraction manufactures false structure
- **Handle mixed-type data properly** — not one-hot + k-means, but Gower distance + k-medoids or k-prototypes

Without the skill, the model tends to name a popular algorithm, return boilerplate code, and endorse a single validation metric. It misses the null comparison, skips the stability check, and treats k-means as universally applicable.

## Benchmark: skill vs. base model

Evaluated on 22 scenarios covering method selection, validation, code correctness, pitfall detection, deployment, and edge cases. Each scenario is graded on 4–6 specific assertions about whether the model gave the correct, opinionated, assumption-first response.

```
Condition       Score       Pass rate
──────────────────────────────────────
Base model      78 / 95     82.1%
With skill      95 / 95     100.0%
Delta                       +17.9 pp
```

The largest gains come from scenarios where a specific methodology piece is easy to overlook:

| Eval | Topic | Base | Skill | Gap |
|------|-------|:----:|:-----:|:---:|
| k selection / validation | silhouette alone isn't enough | 40% | 100% | **+60pp** |
| Non-convex shapes | spectral/HDBSCAN for crescents | 50% | 100% | **+50pp** |
| Mixed-type code | Gower+PAM vs one-hot+k-means | 50% | 100% | **+50pp** |
| HDBSCAN transductive | no native predict; don't refit | 50% | 100% | **+50pp** |
| Clusterability gate | check for structure before clustering | 50% | 100% | **+50pp** |
| Mixed-type framing | high-cardinality categoricals | 75% | 100% | **+25pp** |
| HDBSCAN noise handling | -1 labels are data, not bugs | 75% | 100% | **+25pp** |
| BIRCH at scale | CF-tree compression + two-phase workflow | 75% | 100% | **+25pp** |
| Null comparison for silhouette | k-means clusters noise too | 80% | 100% | **+20pp** |
| LPA / GMM equivalence | same model, different culture | 80% | 100% | **+20pp** |

The base model already handles: scaling diagnosis, AP/Mean Shift scalability, high-dimensional dimensionality reduction, GMM vs k-means tradeoffs, k-means initialization, LPA fit statistics, agglomerative/Ward selection, and OPTICS vs DBSCAN. The skill's value concentrates on validation workflow, assumption-first method selection, mixed-type data, HDBSCAN deployment semantics, and clusterability-first framing.

## Eval suite

22 scenarios across 7 categories, graded by `claude-haiku-4-5` against explicit assertions (executor: `claude-sonnet-4-6`).

| # | Scenario | Category |
|---|----------|----------|
| 1 | HDBSCAN for variable-density sensor data vs. k-means | Method selection |
| 2 | k selection: silhouette peak alone isn't enough | Validation |
| 3 | LPA / GMM / LCA — same family, different indicators | Mixture models |
| 4 | Unscaled features dominate k-means distance | Preprocessing |
| 5 | Mixed-type data: one-hot + k-means vs. Gower + PAM | Preprocessing |
| 6 | Affinity Propagation / Mean Shift at 200k rows | Scalability |
| 7 | HDBSCAN on 250 genomic features: curse of dimensionality | High-dimensional |
| 8 | Silhouette 0.61 at k=4 — null comparison required | Validation |
| 9 | HDBSCAN 35% noise: informative, don't force | Pitfall detection |
| 10 | LPA: BIC says 4 classes, AveCAPP = 0.66 | Mixture models |
| 11 | Crescent shapes: k-means geometry failure | Method selection |
| 12 | Python code: mixed-type clustering with Gower/k-prototypes | Code correctness |
| 13 | User resists scaling: explicit weighting vs. implicit magnitude | Adversarial |
| 14 | k-means gives different results on every run | Implementation |
| 15 | GMM vs k-means: what's actually different | Mixture models |
| 16 | k-means and GMM disagree — which result to trust | Mixture models |
| 17 | Full-covariance GMM: 500 obs, 80 features, BIC looks great | Pitfall detection |
| 18 | HDBSCAN transductive: assigning new points after training | Deployment |
| 19 | Hierarchical / dendrogram structure: agglomerative vs. k-means | Method selection |
| 20 | Clusterability first: what to check before picking an algorithm | Validation |
| 21 | OPTICS vs. DBSCAN vs. HDBSCAN: when to use which | Method selection |
| 22 | BIRCH at 8M rows: CF-tree compression + two-phase clustering | Scalability |

See [`evals/`](evals/) for the full eval definitions and `evals/results/` for benchmark data.
