# Evaluations for the `comp-modeling` skill

This directory contains evaluations to verify that the skill produces the right behavior across the workflows it claims to cover. Each eval is one prompt plus a list of `must_include` and `must_not_include` criteria that an evaluator can check (manually or with an LLM judge). Hand these to Claude Code or a separate eval harness.

The eval suite is organized in three layers:

1. **Triggering evals** (`triggering.json`) — does the skill activate on prompts that should match it and stay quiet on prompts that shouldn't?
2. **Routing evals** (`routing.json`) — given a prompt that activates the skill, does it pull in the right reference file(s) for the model family in question?
3. **Workflow evals** (`workflow.json`) — given a multi-turn task, does the skill produce the recommended workflow (simulate → recover → fit → compare → PPC) and flag the right pitfalls?

There's also a `golden_responses.md` with hand-crafted ideal answers to a few high-stakes prompts, useful as anchors when judging skill output.

## How to run

These are prompt-level evals; they don't run themselves. The expected workflow is:

1. Pick an eval JSON.
2. For each item, run the prompt through the model (with the skill loaded).
3. Score the response against the `must_include` and `must_not_include` criteria.
4. Aggregate per-category and per-criterion pass rates.

An eval is **passing** if all `must_include` criteria are satisfied and no `must_not_include` criteria are violated. Partial credit is fine to track but the threshold for "skill works" should be a strict majority of full passes per category.

## What the evals collectively check

- **Triggering precision**: the skill fires on cognitive modeling prompts and doesn't fire on generic ML prompts.
- **Family selection**: when a specific model family is named, the skill loads the right reference file.
- **Workflow completeness**: when asked to "fit a model," the skill recommends the simulate → recover → fit → compare → PPC workflow rather than just jumping to a fit.
- **Pitfall awareness**: when the user is about to make a common mistake (skipping recovery, using MLE with few trials, fitting `k` on linear scale, etc.), the skill names the pitfall.
- **Tool recommendations**: when a standard task is described, the skill points to the appropriate toolbox (hBayesDM, HDDM, catlearn, TAPAS, etc.) rather than inventing a from-scratch solution.
- **Refusal patterns**: when asked to do something cognitive-modeling-shaped but actually wrong (compare models on different data, claim significance from in-sample fit, etc.), the skill pushes back.

## Scope of the evals

These are **behavioral evals on the skill content**, not unit tests of the scripts. The Python scripts in `scripts/` have their own smoke tests at the bottom of each file. If you want to evaluate the scripts specifically, run them directly:

```bash
python scripts/parameter_recovery.py
python scripts/model_recovery.py
```

Both print self-test output on a Rescorla-Wagner reference task.
