# Deep Eval Analysis Skill

A skill that treats an eval suite as a *psychometric instrument* and audits it — diagnosing which items carry signal, which are dead weight, how reliable the whole thing is, and how confidently you can act on a delta between versions.

**The one idea:** A pass rate is a measurement, not *the* measurement. The mean hides whether items discriminate between strong and weak runs, whether the suite is saturated, whether the grader is trustworthy, and whether a score moved because the system improved or because you reran the dice.

The skill has a strong point of view. It routes to the right method by regime — CTT item analysis for small iteration suites, generalizability theory for intermediate suites, IRT only at 40+ items with 50+ eval "takers" — and explicitly refuses to fit a free 2PL at small N. It defers single-method theory questions (IRT, SDT) to the dedicated skills for those domains, and focuses entirely on the eval-as-instrument workflow.

## What's inside

```
SKILL.md                              — skill hub; load this first
reference/
  01_diagnostic_workflow.md          — regime map: which method for which N(items) × N(versions)
  02_ctt_item_analysis.md            — item difficulty, discrimination, point-biserial, guard items
  03_generalizability_theory.md      — G-coefficient, D-study, variance decomposition
  04_irt_for_evals.md                — Rasch / 1PL for mature suites; when NOT to use 2PL/3PL
  05_sdt_for_triggering.md           — trigger evals as yes/no SDT problems; d', AUC, c
  06_judge_calibration.md            — grader reliability, agreement, calibration checks
  07_small_sample_playbook.md        — what you can and can't conclude from 3–15 items
  08_latent_estimation.md            — marginal MLE, EAP, WLE; when point estimates mislead
  09_joint_glmm.md                   — crossed random effects (items × versions × seeds)
  10_synthesis.md                    — putting it together: the full diagnostic report
  11_stan_backend.md                 — Stan/brms for the joint GLMM
  12_facets_and_confounding.md       — prompt/seed/judge facets; confound detection
  13_item_drift.md                   — detecting items that change difficulty across versions
scripts/
  eval_item_analysis.py              — CTT item analysis (difficulty, discrimination, point-biserial)
  gtheory_eval.py                    — G-coefficient, D-study, variance components
  irt_eval.py                        — Rasch / 1PL IRT for eval suites (with guard rails)
  irt_latent.py                      — latent trait estimation: EAP, WLE, MAP
  item_drift.py                      — between-version item difficulty drift
  joint_glmm.py                      — crossed random-effects GLMM (items × versions × seeds)
  judge_calibration.py               — grader agreement and calibration diagnostics
  sdt_trigger.py                     — SDT analysis of trigger evals (d', c, AUC)
  synthesize.py                      — full diagnostic report generation
stan/
  joint_glmm.stan                    — Stan model for the joint GLMM
  brms_alternative.R                 — brms wrapper for the same model
  run_cmdstanpy.py                   — Python runner for the Stan model
  run_rstan.R                        — R runner
evals/
  evals.json                         — 3 capability evals across the diagnostic workflow
  fixtures/                          — synthetic eval data for testing
```

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/deep-eval-analysis
```

Or manually:

```bash
cp -r jakes-skills/deep-eval-analysis ~/.claude/skills/deep-eval-analysis
```

Once installed, the skill applies automatically whenever you ask about evaluating an eval suite, trimming cases, diagnosing why a benchmark won't move, checking grader reliability, determining how many seeds or cases you need, or whether a delta between skill versions is real.

## Example use cases

**"I want to shrink my eval suite without losing signal — which cases should I cut?"**

The skill runs CTT item analysis: computes per-item difficulty and discrimination, flags negative-discrimination items as broken (fix them, don't trim), identifies truly dead-weight items (saturated or non-discriminating), and raises the guard-item exception (don't auto-cut a saturated item that serves as a regression check). Attaches confidence intervals given small N rather than acting on point estimates.

---

**"My two newest versions score 78% vs 80% — is the newer one actually better or is that noise?"**

The skill identifies the regime (small N iteration), reaches for generalizability theory rather than IRT, and runs a D-study to answer the cases/seeds sizing question — reporting a dependability coefficient so the delta can be judged against reliability rather than read directly. Does not fit a free 2PL.

---

**"My skill over-fires — it triggers on things it shouldn't. How do I measure that?"**

The skill treats trigger evals as a binary SDT problem: computes d' and c from the trigger/no-trigger confusion matrix, distinguishes liberal criterion from poor discriminability, and interprets the CS-coefficient from a bootstrapped trigger ROC. Routes to `scripts/sdt_trigger.py`.

## Eval suite

3 scenarios covering the core diagnostic regimes, graded by `claude-haiku-4-5` against explicit assertions (executor: `claude-sonnet-4-6`). Benchmarks forthcoming.

| # | Scenario | What it tests |
|---|----------|---------------|
| 1 | trim_decision_ctt | CTT item analysis on a synthetic 22-case suite: flag broken items, identify trim candidates, raise the guard-item exception |
| 2 | is_the_delta_real_gtheory | G-theory for a 6-version × 15-case × 3-seed suite: dependability coefficient, D-study, cases-vs-seeds tradeoff |
| 3 | trigger_sdt | SDT analysis of a trigger eval: d'/c decomposition, criterion vs. discrimination distinction |

## License

MIT
