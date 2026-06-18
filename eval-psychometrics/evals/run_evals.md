# Running the eval-psychometrics evals

This skill's outputs are **judgment + correct-method-selection**, so the evals are graded
qualitatively against assertions rather than by exact match. The point of each case is to check a
*stance*, not a string. The most important cases are #3 (refuse free IRT at small N) and #6
(defer method-theory to the IRT/SDT skills) — those guard the skill's reason for existing.

## What you're comparing

For each eval, run two configurations on the same prompt:

- **with_skill** — Claude has `eval-psychometrics` available.
- **baseline (no_skill)** — Claude has none of these skills available.

The signal is the *delta*: does the skill change Claude from "fits a 2PL to 4 versions and reports
discrimination numbers" (a real, common failure) to "refuses, explains the regime, offers
anchoring/shrinkage/G-theory"? If with_skill and baseline are identical, the skill isn't earning
its place on that case — either the case is too easy or the skill needs sharpening.

## Procedure (Claude Code / subagents available)

1. For each eval in `evals.json`, spawn two subagents in the same turn (with-skill, baseline),
   passing the prompt and any `files`. Save outputs under
   `eval-psychometrics-workspace/iteration-N/<eval-name>/{with_skill,no_skill}/`.
2. Grade each output against its `assertions` using `evals/grader_prompt.md`. Write
   `grading.json` per run with fields `text`, `passed`, `evidence` (exact field names the
   skill-creator viewer expects).
3. Aggregate (`python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name eval-psychometrics`)
   and open the eval viewer for human review before editing the skill.
4. Iterate: read failures, sharpen the relevant reference file or the SKILL.md routing, re-run.

## Procedure (claude.ai / no subagents)

No parallel subagents and no baseline comparison. Instead, for each case: read `SKILL.md`, follow
it to produce the answer yourself, and check it against the assertions inline. This is a sanity
check, not a benchmark (you wrote the skill and you're running it, so you have full context).
Treat divergences as candidates for sharpening, and defer the real with-skill-vs-baseline
benchmark to Claude Code (see `HANDOFF.md`).

## Fixtures

All cases that need data point at `evals/fixtures/`:

- `results_5versions.csv` — 10 takers x 22 items (incl. a saturated, a non-discriminating, an
  inverted/negative-discrimination, and a duplicate item) — for CTT/G-theory/trim cases.
- `trigger_eval.csv` — 3 skills with distinct d'/criterion profiles (good / trigger-shy /
  vague-overlap) — for the SDT case.
- `two_judge_labels.csv` — 3 judges, moderate agreement — for the judge-gate case.
- `model_bank_40.csv` + `calibrated_items.csv` — a 40-model bank and its item params — for IRT
  and fixed-item anchoring demos.

These double as smoke tests for the scripts: each script's `--help` shows the call, and running it
on the matching fixture should reproduce the behavior described in the reference files.

## Pass bar

A case "passes" if the majority of its assertions are met AND the headline stance is correct
(e.g., for #3, refusing the free 2PL is necessary regardless of how good the rest of the answer
is). Track per-assertion pass rates across iterations; a stance that regresses during a polish
pass is a release blocker — see the protect-the-claims note in `HANDOFF.md`.
