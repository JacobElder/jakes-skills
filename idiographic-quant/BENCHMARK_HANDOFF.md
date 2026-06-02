# Handoff: benchmark & optimize the `idiographic-quant` skill (run in Claude Code)

This prompt is for **Claude Code**, where subagents and the `claude` CLI are available —
the things the Claude.ai chat environment lacked. The skill and its eval harness are
already built and sanity-checked (8 content evals passing on single author-run grading).
Your job is to do the *rigorous* validation that couldn't be done in chat: with-skill vs.
baseline comparison, independent grading, and description-triggering optimization.

Use the **skill-creator** skill's scripts and subagent instructions
(`/mnt/skills/examples/skill-creator/`, or wherever it's installed) as your machinery —
this prompt tells you what to run; that skill tells you how its scripts work.

## Inputs

- Skill: `idiographic-quant/` (SKILL.md + references/ + scripts/check_ergodicity.py)
- Content evals: `idiographic-quant/evals/evals.json` (8 evals, 40 assertions; 2 are
  type `objective` and can be checked programmatically)
- Eval 6 data dependency: `idiographic-quant/evals/sample_esm_nonergodic.csv` — this file
  MUST be passed to the subagent for eval id 6, and the with-skill subagent is expected to
  run `scripts/check_ergodicity.py` on it.
- Trigger evals: `idiographic-quant/evals/trigger_evals.json` (20 queries, 10 should-trigger
  / 10 should-not, weighted toward hard near-misses on the idiographic↔nomothetic boundary)

## Part A — With-skill vs. baseline benchmark

The single most important question: **does the skill change behavior vs. the base model?**
For a sophisticated topic the base model may already know a lot, so measure the lift, don't
assume it.

1. For each eval in `evals.json`, in the **same turn**, spawn two subagents:
   - **with_skill**: given `idiographic-quant/` as the skill path, the eval prompt, and (for
     eval 6) the CSV. Save to `idiographic-quant-workspace/iteration-1/eval-<id>/with_skill/outputs/`.
   - **without_skill** (baseline): same prompt and files, **no skill**. Save to
     `.../without_skill/outputs/`.
   Launch all of them together so they finish around the same time.
2. Capture `total_tokens` / `duration_ms` from each task notification into `timing.json`.
3. Grade every run with an **independent grader subagent** (read skill-creator's
   `agents/grader.md`). Evaluate each assertion; write `grading.json` with fields
   `text`, `passed`, `evidence`. For the two `objective` assertions in eval 6, check them
   with a script against the known verdict (non-ergodic; between-r positive, within-r
   negative, ~100% sign disagreement) rather than by eye.
4. Aggregate: `python -m scripts.aggregate_benchmark idiographic-quant-workspace/iteration-1 --skill-name idiographic-quant`.
5. Generate the eval viewer (`generate_review.py`) — static HTML if no display — and give me
   the link so I can read the with-skill vs. baseline outputs side by side **before** any
   rewrite. The interesting cases are where the skill's *judgment* shows up: does the baseline
   comply with the underpowered-network request (eval 0)? endorse the group-coefficient plan
   (eval 1)? over-apply idiographic methods to the A/B test (eval 3)? miss the centrality trap
   (eval 7)? skip the script (eval 6)? Those deltas are the skill's value.

What to look for in the deltas: the skill should mainly buy *pushback, correct level-of-claim,
and method selection* — not encyclopedic recall. If the baseline already matches with-skill on
several evals, that's a signal to either tighten those evals toward harder cases or trim skill
content that isn't pulling weight.

## Part B — Description / triggering optimization

The description is the only thing that decides whether the skill is consulted at all. It's
currently hand-written and near the 1024-char limit.

1. Review `trigger_evals.json` with me first (skill-creator's `assets/eval_review.html`),
   so I can sign off / edit the should-trigger labels — especially the hard negatives
   (fixed-effects panel, latent growth curve, server-load forecast, cross-sectional SEM).
2. Run the optimization loop with the **model id powering this session**:
   ```bash
   python -m scripts.run_loop \
     --eval-set idiographic-quant/evals/trigger_evals.json \
     --skill-path idiographic-quant \
     --model <this-session-model-id> \
     --max-iterations 5 --verbose
   ```
   It splits train/test, runs each query ~3× for a stable trigger rate, proposes
   description rewrites, and selects `best_description` by held-out test score.
3. Show me before/after descriptions and the per-iteration scores. Apply `best_description`
   to SKILL.md frontmatter **only if** it beats the current one on the held-out set — and
   re-check it stays under 1024 chars after editing.

## Part C — Iterate, then re-package

Based on the viewer review and the benchmark deltas, propose skill edits (generalize from
failures; cut anything not earning its place; explain the *why* rather than adding rigid
MUSTs). Rerun Part A into `iteration-2/` with the same baseline, launch the viewer with
`--previous-workspace` pointing at iteration-1, and repeat until the feedback is empty or
we agree it's done. Then re-package:
```bash
python -m scripts.package_skill idiographic-quant
```
(Note: packaging strips `evals/`, so keep that folder in the repo separately as the harness.)

## Guardrails specific to this skill

- The skill is intentionally **opinionated**; don't let optimization sand down its strong
  methodological stances into hedged neutrality — the point of view is the value. But it must
  not become *advocacy*: eval 3 (nomothetic is correct) and eval 7 (centrality trap) exist to
  keep it honest. If a rewrite starts passing the "push idiographic" evals while regressing
  those two, reject it.
- Don't add new method families just because the baseline knows them; add only what changes
  behavior on a real eval.
