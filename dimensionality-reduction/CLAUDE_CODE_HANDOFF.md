# Claude Code handoff — dimensionality-reduction skill

Paste the block below into Claude Code (run from the directory that contains the
`dimensionality-reduction/` folder). It assumes the skill-creator skill is installed; if not,
point Claude Code at its `SKILL.md` first.

---

You're picking up a draft Claude Agent Skill at `./dimensionality-reduction/`. It teaches an agent
to choose, apply, validate, and interpret dimensionality-reduction methods (PCA, ICA, NMF, MDS,
LDA/GDA, EFA/CFA, t-SNE, UMAP, PaCMAP, TriMap, PHATE, Isomap, LLE, autoencoders/VAEs). Your job is
to test it rigorously, run the eval loop, harden the bundled script, and package it. Use the
**skill-creator** skill's workflow (subagent runs, grader, eval viewer, description optimizer)
throughout — read its SKILL.md first and follow it.

PRESERVE THE POINT OF VIEW. This skill's value is its opinionated stance, not neutrality. During any
revision, do NOT soften or hedge the core claims (t-SNE/UMAP distances/sizes are not trustworthy;
"UMAP preserves global structure" is overstated; PCA ≠ EFA; CFA is not exploratory DR; LDA is
supervised and (k−1)-capped; validate quantitatively, never by how the plot looks). If a revision
makes the skill more wishy-washy, you've regressed it. You may sharpen, add nuance, or add evidence
— not dilute.

Do the following, in order:

1. **Verify and harden the bundled diagnostics script on REAL embeddings.** `pip install umap-learn
   pacmap openTSNE scikit-learn` and run `scripts/dr_diagnostics.py` on
   `sklearn.datasets.load_digits()` comparing PCA(2), t-SNE, UMAP, and PaCMAP embeddings. Confirm
   the metrics behave as the skill claims: PCA should score high Shepard correlation; t-SNE/UMAP
   should score *low* Shepard but reasonable trustworthiness; the LD-beats-HD label-accuracy warning
   should fire where expected. Then fix these known limitations (left for you deliberately):
   - **`continuity` is currently computed as `trustworthiness(Y, X)` — a common shortcut, NOT the
     canonical co-ranking-matrix definition.** Validate it against a proper co-ranking / Q_NX
     implementation and either confirm equivalence at the k used or replace it. Don't let it ship
     labeled as exact if it isn't.
   - **Metric is hard-coded Euclidean in both spaces.** Add a `metric` parameter (per space) so
     cosine-metric embeddings (text/sentence vectors) are handled correctly.
   - **No large-n guard on trustworthiness/continuity** (only Shepard subsamples). Add subsampling
     or a clear warning above some n, since `sklearn.trustworthiness` materializes a full distance
     matrix.
   - **Label path assumes classification** (`KNeighborsClassifier` + `cross_val_score`). Either
     detect continuous targets and switch to a regression-appropriate check, or document that labels
     must be categorical.
   Add a couple of unit tests under `scripts/` covering these.

2. **Run the output evals** in `evals/evals.json` (**9 cases** — note IDs 7 and 8 are an
   over-correction guard and a categorical-data trap added after a self-review). For each, spawn a
   with-skill subagent and a no-skill baseline subagent in the same turn, save outputs to a
   `dimensionality-reduction-workspace/iteration-1/` tree, then grade each response against its
   `assertions` with a grader subagent. These assertions are largely binary/objective, so grade
   precisely. Capture timing/token data from the task notifications.
   - **Focus on baseline LIFT, not raw pass rate.** Modern Claude already knows several of these
     unaided (e.g. "LDA is supervised," generic t-SNE caveats), so the baseline will pass those.
     The evals that justify the skill are the *differentiators* where baseline plausibly fails:
     the UMAP-global-structure overclaim (id 4), volunteering **PaCMAP/TriMap** (ids 3/4), the
     silhouette/kNN-in-embedding circularity, the EFA→CFA double-dip (id 6), the categorical trap
     (id 8), and NOT over-lecturing on the easy PCA case (id 7). Report per-eval with-skill vs
     baseline deltas and call out where the skill actually moved the needle.
   - **Check the script is actually used:** for the full-pipeline eval (id 3), verify the with-skill
     subagent found and invoked `scripts/dr_diagnostics.py` rather than hand-rolling metrics; if it
     didn't, tighten the SKILL.md pointer to the script.

3. **Generate the eval viewer** with `eval-viewer/generate_review.py` BEFORE you start editing the
   skill yourself, so a human can review the with-skill vs baseline outputs. The interesting question
   is not just "does with-skill pass" but "how much does the skill move the baseline" — the baseline
   may already avoid some traps, and evals where it doesn't are where the skill earns its keep.

4. **Iterate.** Where with-skill fails an assertion or doesn't clearly beat baseline, improve the
   skill (generalize the fix, explain the why, keep it lean — per skill-creator). Re-run into
   `iteration-2/`, etc. Watch the transcripts, not just final outputs: if subagents keep
   re-deriving the same diagnostic code, make sure they're actually finding and using
   `scripts/dr_diagnostics.py`, and tighten the SKILL.md pointer if not.

5. **Optimize the description for triggering** using the 18 `trigger_evals` (10 should-trigger, 8
   should-not). The should-not cases are deliberate near-misses — Latent Dirichlet Allocation (also
   "LDA"), discriminant *validity* / HTMT (psychometrics but not DR), eigenvalue homework, PDF file
   "reduction". Make sure the optimized description still fires on casual phrasings ("squish my
   features", "project to 2d", "is the distance in my plot real") without grabbing the near-misses.

6. **Resolve two ambiguities with me before finalizing:**
   - **MVR** in the original request is non-standard. Confirm whether I meant PLS / reduced-rank
     regression (supervised projection toward a continuous target) or something else, and add a
     short section if so.
   - **GDA**: confirm Generalized (kernel) Discriminant Analysis is the intended meaning (the skill
     assumes so) vs Gaussian Discriminant Analysis.
   Also consider whether to add genuinely distinct methods the request gestured at with "or whatever
   else" — candidates: kernel PCA (already mentioned), diffusion maps, SOM, spectral embedding, UMAP
   for features (>2d). Add only if they're not near-duplicates of what's there.
   - **One content nuance to weave in** (deferred from review): principle #1 says "measure distances
     in the original space," but the sharpest version of the critique is that high-dimensional
     Euclidean distances are *themselves* fragile (curse of dimensionality) — which is part of why
     preserving them is undesirable. Add a sentence acknowledging this so the stance is "embedding
     distances are artifacts AND raw HD distances are fragile; rely on neighbour structure,
     appropriate metrics, or PCA-space distances," rather than implying HD distances are ground
     truth. Keep it tight; don't let it dilute the core claim.

7. **Package** with `package_skill.py` and give me the `.skill` file plus a short changelog of what
   you changed and the final eval pass rates (with-skill vs baseline).

Constraints: keep SKILL.md under ~500 lines (currently ~180); keep reference files focused; the
script must stay dependency-light (numpy/scikit-learn/scipy only — embedding libraries are the
caller's responsibility). Ask me before any large structural reorganization.
