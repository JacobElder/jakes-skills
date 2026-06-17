# 12 — Facets, Confounding & Where Else to Buy Identifiability

Two things you raised that the rest of the skill only half-covered: (1) judge model, responder base
model, and run-to-run resource non-determinism are all *sources of variance* you have to model, not
ignore; and (2) the recurring question — where else does identifiability come from. This file is the
opinionated map for both.

## Part A — Judge, base model, and run are facets (not nuisances to average blindly)

Every score is produced by a *combination*: this skill version × this eval case × **this judge
model** × **this responder base model** × **this run** (with whatever resources/non-determinism that
run had). In generalizability-theory terms these are **facets**, and each contributes variance that
is *not* the skill-version signal you want. The move is to model them as crossed/nested random
effects so their variance is separated rather than smeared into your estimate.

- **Judge model (Flash-1.5 vs a larger grader, etc.).** Two effects: a judge *main effect* (one
  grader is systematically harsher — shifts everything, mostly harmless for ranking) and the
  dangerous **judge × version interaction** (a grader that happens to like what version 5 does).
  Defend with: multiple judges (estimate the judge variance and the interaction), or one fixed judge
  held constant across the whole comparison. Calibrate judges against each other / humans first with
  `judge_calibration.py`. **Switching judges mid-stream is drift on the judge axis** — the same
  invariance problem as item drift (`reference/13`); link through overlap or don't compare across the
  switch.
- **Responder base model.** If "skill version" and "base model" move together, they're **confounded**
  (see Part B). If you run several base models, treat base model as a facet (or a covariate, Part C)
  so "the skill improved" is separable from "the model improved."
- **Run / resources / non-determinism.** The same model on the same case can score differently across
  runs (sampling temperature, load, truncation, tool flakiness). That's **within-cell residual
  variance** — estimate it with replicate **seeds**. `gtheory_eval.py --seed-facet` reports it
  separately, and the D-study tells you how many seeds you need to average it down. If seed variance
  exceeds the residual, *adding seeds beats adding cases* — the synthesis and G-theory output both
  flag this.

### Confounding is the silent killer — check the design before the model

No amount of modeling rescues a confounded design. If version 5 was only ever run on the new base
model with the new judge, then "v5 is better" is **inseparable** from "new model is better" and "new
judge scores higher." Before estimating anything, ask: is each skill version observed across more
than one level of each facet (judge, base model)? If not, the comparison is confounded and the
honest output is "can't separate these," not a number. The fix is a **connected design**: cross the
facets (every version under every judge/model) or at least overlap them enough to link
(common-condition equating, same logic as anchor items). A cheap partial fix: hold judge and base
model *fixed* across the versions you're comparing, so they can't vary and therefore can't confound —
at the cost of generalizability to other judges/models.

## Part B — The consolidated identifiability menu

Ordered roughly by leverage for the small-N (few-variant) regime. "Built" = a script does it today;
"handoff" = scoped in `HANDOFF.md`.

1. **Expand the taker dimension** — model tiers + ablations + seeds + prior iterations turn 5
   variants into 30. Biggest, cheapest lever; spreads variants across a real ability range, which is
   what makes items estimable at all. *(built/documented — `reference/07`)*
2. **Pairwise / comparative judgments (Bradley–Terry / Thurstone)** — "which version did better on
   this case" separates few variants far more efficiently than absolute scores. The single biggest
   *unbuilt* lever for your regime. *(handoff)*
3. **Latency / effort channel** — output tokens or CoT length as a second response correlated with
   ability (van der Linden). *(built — `joint_glmm.py`)*
4. **Fixed-item anchoring** — freeze item params from a bank, estimate only θ; precise at any N.
   *(built — `irt_latent.py --fixed-items`)*
5. **Hierarchical pooling / adaptive shrinkage** — partial-pool item params; regularization that
   relaxes as N grows. *(built — `irt_latent.py --backend mcmc`, `joint_glmm.py`)*
6. **Latent regression on variant covariates (MIMIC)** — regress θ on what you *know* about each
   variant (base model, temperature, prompt length, # tools). This both tightens θ (explained
   variance) and **directly answers "performance differs by model type"** — model type becomes a
   predictor of ability instead of unexplained noise. *(handoff — high value)*
7. **Explanatory IRT / item covariates (LLTM)** — model difficulty as a function of case features
   (length, domain, tool-use required). Borrows strength across items, so item params are estimable
   with fewer variants, and it predicts difficulty of unseen cases. *(handoff)*
8. **Empirical-Bayes priors from prior iterations** — use last iteration's posterior as this
   iteration's prior. Across 4–6 versions shipped over time, this carries real information forward
   instead of starting cold each run. *(handoff — cheap, strong for longitudinal tracking)*
9. **Anchor-linking across content drift** — keep stable anchor cases to put runs on a common scale.
   *(built — `item_drift.py` + `--fixed-items`; `reference/13`)*
10. **Ordinal / polytomous scoring** — stop binarizing rubric levels; a graded-response model keeps
    the middle-level information. More information per cell. *(handoff)*
11. **Replicate seeds** — separate true ability from run-to-run noise (Part A). *(built —
    `gtheory_eval.py --seed-facet`)*

## The standing caveat (it applies to every item above)

Each lever helps *only to the extent it carries real, independent information.* A covariate that
doesn't predict ability, a prior that's asserted rather than learned, a channel entangled with the
grader (output tokens + a length-biased judge, `reference/09`) — these *manufacture* precision
rather than add it. The honest test for any addition: does the estimate's interval tighten *because
the data spoke*, or because you narrowed the prior? Prefer levers that bring new data (more takers,
a real second channel, pairwise judgments, anchors) over levers that bring new assumptions.
