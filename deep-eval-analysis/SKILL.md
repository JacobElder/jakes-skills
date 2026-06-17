---
name: deep-eval-analysis
description: >-
  Analyze evaluation suites as measurement instruments, not just scoreboards. Use whenever
  someone has eval results (especially agent/skill evals) and wants more than a single pass
  rate: which eval cases to trim or keep, why an eval can't separate two versions, whether a
  benchmark is saturated or contaminated, how many cases/seeds/judges give a reliable read,
  whether an LLM grader can be trusted, or whether a skill's TRIGGERING is biased vs. genuinely
  undiscriminating. Trigger on phrases like "which evals should I cut", "my eval won't move",
  "are these results real", "eval too easy/hard", "how many runs do I need", "is my judge
  reliable", "the skill over/under-fires", "trim the eval suite", "item discrimination", "eval
  reliability", or "calibrate my grader" — even when no method is named. This skill ORCHESTRATES
  psychometric methods over eval data; it does not re-teach them. For the theory of a single
  method, defer to the dedicated item-response-theory and signal-detection-theory skills.
---

# Deep Eval Analysis

## The one idea

**A pass rate is a measurement, not the measurement.** The mean hides everything that makes an
eval suite good or useless: whether items actually separate strong runs from weak ones, whether
the suite is saturated, whether the grader is trustworthy, and whether the score moved because
the system improved or because you reran the dice. This skill treats an eval suite as a
*psychometric instrument* and audits it: which items carry signal, which are dead weight, how
reliable the whole thing is, and how confidently you can act on a delta.

The payoff is concrete: **trim the suite without losing signal, diagnose why an eval is stuck,
and stop shipping on noise.**

This skill does two things, which compose: it **audits** an eval suite (which cases carry signal,
how reliable it is, can you trust the grader, does the trigger fire right) and it **estimates** —
producing precise latent measurements for both eval cases (difficulty, discrimination) and skill
variants (ability) on a common scale, with honest uncertainty. Audit first, then estimate on the
cleaned suite. The estimation capability lives in `reference/08_latent_estimation.md` and
`scripts/irt_latent.py`.

## Non-negotiable stances

These are the opinions this skill exists to enforce. Do not hedge them away.

1. **Always report item-level structure, never just the mean.** Every analysis produces, at
   minimum, per-item difficulty (pass rate) and per-item discrimination (item–rest correlation).
   A suite summarized by one number cannot be audited.
2. **Match the method to the regime — this is the whole game.** The most common failure is
   fitting a free 2PL/3PL IRT model to a handful of skill versions. It will return confident
   numbers that are noise. Use the regime router below *before* touching any method. Note this
   stance is about the *naive* fit: when someone wants latent estimates at small N, the answer is
   not "you can't" — it's deliver them the right way (hierarchical pooling with adaptive shrinkage,
   or fixed-item anchoring on a calibrated bank), with honest wide intervals. Refuse the naive
   free 2PL; still deliver the estimates. See `reference/08_latent_estimation.md`.
3. **Gate on judge trust first.** If the grader (human or LLM) isn't reliable and calibrated,
   every downstream number is decoration. Check inter-rater agreement before difficulty,
   discrimination, or ability.
4. **Triggering is a detection problem, not an accuracy problem.** Raw trigger accuracy
   conflates two different failures. Use signal detection theory to split *discriminability*
   (d′ — the description can't tell relevant from irrelevant; a content fix) from *bias*
   (criterion — the description fires too eagerly or too reluctantly; a wording fix).
5. **Trim on evidence, fix on evidence, but protect the guards.** Cut saturated and
   non-discriminating items; *fix* negative-discrimination items urgently. But a saturated item
   that guards against a known regression or safety failure is insurance, not dead weight —
   label it and keep it. "Everyone passes" is only a reason to cut when the item isn't guarding
   anything.
6. **Don't dilute uncertainty.** Report intervals, pre-commit decision thresholds, and treat a
   few-point pass-rate move across a small suite as noise until a reliability analysis says
   otherwise. A delta without a dependability coefficient is a vibe.
7. **Internal consistency: McDonald's ω, not Cronbach's α.** Alpha assumes tau-equivalence
   (equal factor loadings = equal item discriminations). Eval suites violate this routinely —
   items have widely variable discrimination. Alpha underestimates reliability when violated.
   McDonald's ω estimates reliability from a factor model; ωh tests unidimensionality. But
   G-theory's Eρ² is usually more relevant than either, because it models the crossed
   version × case design and directly answers whether version *rankings* are reproducible.

## Regime router — read this before choosing a method

Pick the row that matches **how many independently-varying "takers" you have** (versions,
models, ablations, seeds — the columns of your response matrix), because that dictates which
methods are valid. Getting this wrong is the #1 way to produce confident nonsense.

| Your situation | Primary tools | Avoid |
|---|---|---|
| **Small-N iteration** (the default): ~2–8 skill/prompt versions × ~10–40 eval cases, maybe a few seeds | **G-theory** (reliability + how-many-you-need) + **CTT item analysis** (trim/keep) + **SDT** (triggers). See `reference/07_small_sample_playbook.md` FIRST. | Free 2PL/3PL IRT. Reading point estimates without intervals. |
| **Model-bank regime**: responses from ~30+ models/checkpoints (your own runs across model tiers, or a public leaderboard) on shared items | **IRT** for item difficulty/discrimination/saturation/contamination and item selection (`reference/04_irt_for_evals.md`); CTT as a fast first pass | Over-trusting IRT below ~30 takers without hierarchical shrinkage |
| **Trigger / routing analysis**: did the skill fire when it should, and stay quiet when it shouldn't | **SDT** (d′, criterion) per skill (`reference/05_sdt_for_triggering.md`) | Reporting only trigger accuracy/F1 — it hides the bias-vs-signal split |
| **"Can I even trust these labels?"**: an LLM or human is grading | **Judge calibration** (κ, agreement, Brier/ECE) (`reference/06_judge_calibration.md`) — do this before the rows above | Treating grader output as ground truth |
| **"Give me latent estimates"**: ability per variant + difficulty/discrimination per item, on one scale, with intervals | **Latent estimation** (`reference/08_latent_estimation.md`, `scripts/irt_latent.py`): `--backend auto` defaults to hierarchical 2PL via MCMC if PyMC is installed, else stable hierarchical Rasch (scipy-only, always available). Fixed-item anchoring for precise small-N placement on a pre-calibrated scale. | A naive free 2PL/3PL at small N (unstable discrimination, collapsed variance); MAP/EM point estimation (σ_a collapses to 0 under joint mode) |
| **"Give me everything at once"** / I logged latency or confidence too / I want IRT+SDT+calibration+G-theory from one model | **Unified joint GLMM** (`reference/09_joint_glmm.md`, `scripts/joint_glmm.py`): one fit, channels switchable; latency channel buys identifiability | A full multi-trait covariance at small N — it's asserted by priors, not estimated. Stack channels you don't have. |
| **"Is this comparison even valid?"**: judge/model changed, runs are noisy, or my eval cases got reworded | **Facets & invariance** (`reference/12_facets_and_confounding.md`, `reference/13_item_drift.md`, `scripts/item_drift.py`): model judge/model/seed as facets, check confounding, hash cases for drift | Reading a θ trend off a suite whose ruler (judge, base model, or case content) silently changed |

When in doubt you are in the **small-N iteration** regime. Start there.

## Routing to the method skills (mutual exclusion)

This skill is the *application layer*. It deliberately does not derive the methods. Hand off:

- **How IRT works** — model forms (1PL/2PL/3PL), item characteristic curves, ability
  estimation, assumptions, fitting → **item-response-theory skill**. This skill only covers
  *IRT applied to eval data and its eval-specific pitfalls*.
- **How SDT works** — d′ derivation, ROC, isosensitivity, the equal-variance assumption →
  **signal-detection-theory skill**. This skill only covers *SDT applied to triggering/routing*.
- **General multilevel/Bayesian estimation machinery** (brms/PyMC, priors, partial pooling) →
  the multilevel-modeling skill, when implementing the hierarchical small-N remedies.

If a request is purely "explain IRT/SDT to me," that is the method skill's job, not this one.
If the request is "use IRT/SDT/G-theory to tell me something about my evals," you're in the
right place.

## Workflow

Follow this order. Each step has a reference file with the concrete recipe and thresholds.

1. **Frame the question and the regime.** What decision rides on this analysis (trim? ship?
   trust? diagnose a stuck eval?) and which router row are you in? → `reference/01_diagnostic_workflow.md`
2. **Gate on the grader.** If anything other than an exact programmatic check produced the
   pass/fail labels, verify the grader is reliable before continuing. → `reference/06_judge_calibration.md`
3. **Run the CTT item pass.** Per-item difficulty and discrimination; flag saturated, floored,
   non-discriminating, and (urgent) negative-discrimination items. This is the cheap, robust
   first look that works in every regime (the only item-level method when takers < ~30). →
   `reference/01_diagnostic_workflow.md` §Step 3, script `scripts/eval_item_analysis.py`
3. **Quantify reliability and right-size the suite.** How much of your score variance is real
   version differences vs. case-selection noise, judge inconsistency, or seed-to-seed sampling —
   and how many cases/seeds/judges you actually need. → `reference/03_generalizability_theory.md`,
   script `scripts/gtheory_eval.py`
4. **If (and only if) you have a model bank, fit IRT.** Difficulty/discrimination/saturation,
   contamination signals, and IRT-based item selection for a "tiny" suite. → `reference/04_irt_for_evals.md`,
   script `scripts/irt_eval.py`
5. **If the goal is latent estimates, run the measurement model.** Ability per variant +
   difficulty/discrimination per item on one scale, with intervals — hierarchical 2PL (MCMC) for a
   bank, hierarchical Rasch or fixed-item anchoring for small N. → `reference/08_latent_estimation.md`,
   script `scripts/irt_latent.py`
6. **For triggers, run the detection analysis.** Per-skill d′ and criterion; translate into
   "rewrite the description's content" vs. "tune its eagerness." → `reference/05_sdt_for_triggering.md`,
   script `scripts/sdt_trigger.py`
7. **Decide and document.** Apply the trim/keep/fix rules with intervals attached; write down
   the decision thresholds you used. → `reference/01_diagnostic_workflow.md` (Decision section)
8. **Synthesize and visualize.** If you ran the joint engine, turn it into one plain-language read
   of all four frameworks plus a single figure (item–person map, separation matrix, information,
   calibration). → `reference/10_synthesis.md`, script `scripts/synthesize.py`

## Reference files

- `reference/01_diagnostic_workflow.md` — the end-to-end audit, regime decision tree, trim/keep/fix
  decision rules with thresholds, and the CTT item statistics (difficulty, item–rest discrimination,
  discrimination index, saturation/contamination/redundancy heuristics). The robust default in every regime.
- `reference/03_generalizability_theory.md` — variance components for evals (version × case ×
  judge × seed), generalizability vs. dependability coefficients, and D-studies to size your
  suite. The primary reliability tool for small-N iteration.
- `reference/04_irt_for_evals.md` — IRT *applied to evals*: the response-matrix mapping, the
  model-bank requirement, difficulty/discrimination/saturation/contamination read-outs,
  fixed-item (anchor) calibration, and IRT-based suite shrinking (tinyBenchmarks-style).
- `reference/05_sdt_for_triggering.md` — skill triggering as signal detection: hit/false-alarm
  mapping, d′ vs. criterion, log-linear correction for extreme rates, and the actionability split.
- `reference/06_judge_calibration.md` — trusting your grader: agreement (Cohen's/Fleiss' κ),
  discrimination (ROC-AUC vs. reference), calibration (Brier, ECE), and what to do when the
  judge is unreliable.
- `reference/07_small_sample_playbook.md` — **read this whenever you're in the default regime.**
  Why standard IRT breaks at small N, and the full remedy menu: expand the taker dimension,
  drop to Rasch, fixed/anchor-item calibration, hierarchical adaptive shrinkage (regularization
  that relaxes as N grows), G-theory-first, and bootstrap/Bayesian uncertainty.
- `reference/08_latent_estimation.md` — the estimation deliverable: precise latent estimates for
  items (difficulty, discrimination) and variants (ability) on a common scale with honest
  intervals; backend choice (hierarchical 2PL via MCMC / stable Rasch / fixed-item anchoring) and
  how to read σ_a, intervals, and saturation.
- `reference/09_joint_glmm.md` — the unified model: getting IRT + SDT + calibration + a G-theory
  reliability bridge from one GLMM fit, the latency (van der Linden) and 4PL channels, and the
  honest feasibility verdict on "one mega-model" — what's earned vs. asserted at small N.
- `reference/10_synthesis.md` — the synthesis layer: plain-language interpretation of all four
  frameworks at once plus a single multi-panel figure (item–person map, pairwise separation,
  test information, calibration), and how to read each panel.
- `reference/11_stan_backend.md` — version-proof **Stan / RStan** alternative to PyMC: one
  `stan/joint_glmm.stan` model with Python (cmdstanpy) and R (cmdstanr/rstan) runners that emit the
  same JSON (so synthesis is unchanged), a brms low-risk path, and the PyMC↔Stan correspondence.
- `reference/12_facets_and_confounding.md` — judge model / responder base model / run non-determinism
  as **facets**; detecting confounded designs; and the consolidated **identifiability menu** (taker
  expansion, pairwise, latent regression on model-type covariates, explanatory IRT, EB priors,
  anchoring, seeds) with what's built vs. handoff.
- `reference/13_item_drift.md` — eval **content drift / measurement invariance / equating**: keeping
  estimates comparable when cases get reworded over time; anchor-linking and DIF.

## Scripts

Scripts are self-contained (numpy/pandas/scipy/scikit-learn), read a long-format CSV of eval
results, and print a report plus write a tidy CSV/JSON. Run any with `--help`. They degrade
gracefully (with explicit warnings) at small N rather than failing silently. One optional
dependency: `irt_latent.py`'s `--backend mcmc` uses PyMC if installed; without it that script
falls back to a stable scipy-only Rasch fit, so nothing breaks.

- `scripts/eval_item_analysis.py` — CTT difficulty + discrimination + flags + trim report.
- `scripts/gtheory_eval.py` — variance components, Eρ²/Φ, and a D-study projection.
- `scripts/sdt_trigger.py` — d′, criterion, A′, with log-linear correction, per skill.
- `scripts/irt_eval.py` — Rasch / 2PL audit with a small-N guard, fixed-item anchoring, saturation.
- `scripts/irt_latent.py` — **latent estimation**: hierarchical 2PL (MCMC, adaptive shrinkage) or
  stable Rasch or fixed-item anchoring → ability per variant + difficulty/discrimination per item,
  all with intervals.
- `scripts/joint_glmm.py` — **unified engine** (PyMC): one fit emitting IRT + the SDT probit reading
  + calibration + a G-theory reliability bridge, with optional latency (van der Linden, for
  identifiability) and 4PL slip channels. Use in the bank regime or when extra channels are logged;
  see `reference/09_joint_glmm.md` for the honest small-N limits.
- `scripts/synthesize.py` — **synthesis & visualization**: turns a `joint_glmm` JSON (plus optional
  `gtheory_eval` and `sdt_trigger` JSON via `--gtheory`/`--sdt`) into a plain-language read of all
  four frameworks and a single multi-panel figure — item–person map, variant forest, test
  information, pairwise separation, calibration, G-theory variance + D-study, and the SDT triggering
  quadrant. See `reference/10_synthesis.md`.
- `scripts/item_drift.py` — **content-drift / invariance check**: hashes eval-case content across
  runs to catch silent rewrites under a stable `item_id`, flags drifted items, and identifies the
  stable anchor set for linking. See `reference/13_item_drift.md`.
- `scripts/judge_calibration.py` — κ, agreement, Brier, ECE, reliability-diagram data.

Expected input schema is documented at the top of each script and in
`reference/01_diagnostic_workflow.md`.
