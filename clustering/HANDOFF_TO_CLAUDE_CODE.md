# Handoff: iterate and harden the `cluster-analysis` skill

You're picking up a drafted Claude Agent Skill called **`cluster-analysis`**. It's
built and internally sanity-checked; your job is to run the full skill-creator
evaluation loop, harden the technical content and the diagnostic script, optimize the
description for triggering, and package it. Use the skill-creator skill
(`/mnt/skills/examples/skill-creator/SKILL.md` or your installed copy) as your process
guide — you have subagents and the `claude` CLI, so the full workflow (parallel
with-skill vs. baseline runs, the eval viewer, benchmarking, description optimization)
is all available to you, unlike the environment this was drafted in.

## What this skill is and the point of view it takes

`cluster-analysis` is an **opinionated** decision guide for choosing, running,
validating, and interpreting clustering methods (k-means, k-medoids, fuzzy c-means,
agglomerative/Ward, divisive/DIANA, DBSCAN, HDBSCAN, OPTICS, Mean Shift, BIRCH,
spectral, Affinity Propagation, GMM/LCA/LPA/mixture models). Its value is the point of
view, not neutral coverage. The core theses, which must survive your edits:

1. **Clustering always returns clusters** — so a result is a hypothesis, not a
   discovery. Stability and null comparison are mandatory.
2. **Preprocessing and the distance metric dominate the outcome** more than the
   algorithm choice. This reordering of priorities is the skill's spine.
3. **Assumptions over algorithms** — pick a method by whether its shape/density/size
   priors match the data, using the decision framework.
4. **Honest, specific verdicts**: HDBSCAN is the density default over plain DBSCAN;
   GMM is "soft k-means done honestly"; LPA/LCA/GMM are one finite-mixture family
   differing by indicator type and research culture; the elbow method is weak; Affinity
   Propagation / Mean Shift / DIANA are over-recommended relative to their niches; BIRCH
   is a scalability tool not a philosophy; internal validity indices assume convex
   clusters and frequently disagree with experts.

### CRITICAL: do not dilute the strong claims

When you polish, keep the opinions sharp. Do **not** sand the verdicts down into
"it depends, every method has trade-offs, consider your use case" mush. The whole point
is that it commits to defensible recommendations and says what's over-recommended. If
you think a specific claim is wrong or overstated, *fix it to be more precise*, don't
neutralize it. Tighten language and improve accuracy; preserve the spine and the verdicts.

## Structure

```
cluster-analysis/
├── SKILL.md                      # decision framework, taxonomy, opinionated defaults, workflow
├── references/
│   ├── algorithms.md             # per-method deep reference + geometry cheat sheet (has TOC)
│   ├── mixture-models.md         # GMM/LCA/LPA, EM, model selection (BIC/ICL/BLRT), naming map
│   ├── validation.md             # choosing k, internal/external indices, stability, clusterability
│   └── preprocessing.md          # scaling, distance, mixed/categorical data, dimensionality
├── scripts/
│   └── cluster_diagnostics.py    # clusterability + k-sweep + method comparison + bootstrap stability
└── evals/
    ├── evals.json                # 6 task evals with expectations
    └── trigger_evals.json        # 20 should/should-not queries for description optimization
```

## Your tasks, in order

### 1. Run the task-eval loop (skill-creator §"Running and evaluating test cases")
- For each of the 6 evals in `evals/evals.json`, spawn **two** subagents in the same
  turn: one with the skill, one baseline (no skill). Save to
  `cluster-analysis-workspace/iteration-1/eval-<id>/{with_skill,without_skill}/`.
- The expectations are already written and are objective (presence of specific
  reasoning, e.g., "recommends HDBSCAN," "identifies unscaled features dominate
  distance"). Grade with a grader subagent against those expectations.
- Capture timing/token data from task notifications into `timing.json` as you go.
- Aggregate (`python -m scripts.aggregate_benchmark ...`) and **generate the eval viewer
  with `generate_review.py`** so Jake can review qualitative outputs before you revise.
  Do this BEFORE you start editing anything yourself.
- Expected signal: the baseline tends to name a popular algorithm and dump boilerplate;
  the with-skill runs should interrogate assumptions/preprocessing/validation and give a
  recommendation *with its catch*. If the skill isn't beating baseline on the
  assumption-first reasoning, that's the thing to fix.

### 2. Improve based on results + the review
Generalize from failures rather than overfitting to these 6 prompts. Watch specifically
for: the model citing a reference file's verdict without the *reasoning* (tighten the
"why"); the diagnostic script being ignored when it would help; or any eval where
with-skill ≈ baseline (means that part of the skill isn't pulling weight).

### 3. Technical accuracy pass (subagent or careful read)
Spot-check the claims against current sources — the draft was research-grounded but
verify rather than trust. High-value checks:
- HDBSCAN parameter semantics (`min_cluster_size`, `min_samples` default = mcs,
  `cluster_selection_epsilon`) against scikit-learn ≥1.3 and the `hdbscan` docs.
- OPTICS reachability/`xi` vs. DBSCAN-cut extraction.
- The Nylund et al. (2007) claim that BIC and BLRT are the strongest class-enumeration
  criteria; the ICL = BIC + entropy-penalty framing.
- mclust covariance-family naming (EEE/VVV/...) and the tidyLPA model numbers.
- The geometry cheat-sheet table rows (especially "handles varying density," "labels
  noise," "needs k," "assigns new points") — these are the most load-bearing and the
  easiest to get subtly wrong.

### 4. Harden `scripts/cluster_diagnostics.py`
It runs clean today (tested on synthetic blobs; clusterability, k-sweep, multi-method
comparison incl. sklearn HDBSCAN, and bootstrap stability all work). Consider adding:
- Optional matplotlib output (`--plots DIR`): silhouette plot, k-sweep curves,
  reachability/dendrogram, 2D PCA scatter colored by labels. (Header mentions `--plots`
  conceptually; wire it up.)
- A `--dbscan-eps-knee` helper (k-distance plot) since DBSCAN's default eps is a
  footgun, and the script currently warns about it but doesn't help tune it.
- Graceful behavior when GMM BIC fails on singular covariance (it currently NaNs — fine,
  but a one-line note in output would help).
Keep it an editable harness, not a black box — that framing is intentional.

### 5. Description optimization (skill-creator §"Description Optimization")
Run `scripts/run_loop.py` with `evals/trigger_evals.json` (20 queries, already split-able
into should/should-not). The tricky negatives are deliberate near-misses: PCA/UMAP alone,
KNN retrieval, LDA topic modeling, record-linkage dedup, supervised classification,
semantic image segmentation. Use the session model id. Apply `best_description` (chosen
by held-out test score) to the frontmatter, show Jake before/after + scores. Consider
adding a few more negative near-misses (e.g., "vector search," "anomaly detection with an
autoencoder") if coverage looks thin.

### 6. Optional expansions if evals reveal gaps
- A worked code example or two in references (e.g., k-prototypes on mixed data; spectral
  on two-moons showing silhouette would mislead) — only if the eval loop shows the model
  struggling to operationalize the advice.
- More task evals targeting under-covered methods (BIRCH/streaming; spectral/manifold;
  time-series + DTW; categorical-only LCA).

### 7. Package
`python -m scripts.package_skill <path-to-cluster-analysis>` and hand back the `.skill`
file path.

## Definition of done
- With-skill clearly beats baseline on the task evals (assumption-first reasoning, honest
  caveats, correct method verdicts), reviewed by Jake in the viewer.
- Technical claims verified; geometry cheat sheet correct.
- Diagnostic script runs clean with plots and the eps-knee helper.
- Description optimized against the trigger set and applied.
- The opinionated spine and verdicts are intact — sharper, not softer.
- Packaged `.skill` produced.

Jake prefers direct, opinionated content and terse communication. Keep updates concise
and surface disagreements rather than burying them.
