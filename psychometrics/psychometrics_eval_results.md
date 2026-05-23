# Manual eval review — iteration 1

Method: For each behavior eval, I read the SKILL.md and references, generated a response to the prompt, then graded against the listed expectations. This is the Claude.ai-mode lightweight version of the eval workflow — no subagents, no automated grading, but a structured pass/fail per expectation.

## Summary

| # | Name | Pass rate | Notes |
|---|---|---|---|
| 1 | alpha-misinterpretation | 7/7 | Clean. Response hit every key point. |
| 2 | survey-design-workflow | 9/9 | Strong; the workflow ordering and mistake list track the SKILL.md closely. |
| 3 | cross-group-mean-comparison | 8/8 | Correctly emphasized WLSMV + threshold invariance for ordinal. Mentioned PHQ-9 invariance specifically. |
| 4 | rasch-vs-2pl-choice | 7/7 | Framed as substantive measurement-philosophy choice, not just AIC. |
| 5 | thin-validity-claim | 7/7 | Clear refusal to endorse; named MTMM and method variance. |
| 6 | modification-index-trap | 7/7 | Warned against MI-chasing, recommended substantive justification + replication. |
| 7 | icc-vs-kappa | 7/7 | Identified ICC over kappa, named multiple ICC variants, mentioned absolute vs. consistency. |
| 8 | efa-on-likert-defaults | 7/7 | Recommended polychoric, oblique, parallel analysis; did not default to varimax or Pearson. |

**Total: 59/59 expectations met (100%).**

## Caveats

This is a self-administered eval: I wrote the skill AND graded the responses, so the test isn't independent. The pass rates would be lower with adversarial prompts or a separate grader. For higher confidence, run the trigger_evals.json on Claude Code with `run_eval.py`, which uses an independent invocation.

## What might fail in the wild

A few weak spots to watch for, based on areas where the skill is opinionated and a different invocation of Claude might soften:

1. **Hedging on alpha vs. omega.** A different Claude run might "see both sides" rather than landing on omega as the modern default. The SKILL.md is pushy on this; hopefully it holds.
2. **Hu & Bentler cutoffs.** The skill warns against fetishizing them but applied reviewers want a cutoff. Claude might split the difference rather than picking a stance.
3. **Reverse-coded items.** The skill takes a stronger position against reflexive reverse-coding than many textbooks. A Claude run might fall back to "include them for acquiescence detection" without the empirical caveat.
4. **EFA + CFA on same sample.** The skill labels this double-dipping; some practitioners do it routinely. Claude might endorse the practice in a friendly response.
5. **Construct definition step.** Easy to skip in a fast response. Pre-flight check: did the response mention construct definition / boundaries / dimensionality theory before diving into analysis?

## Suggested next steps

1. **Get Jake's eyes on the responses** — does the tone work for him? Is it too pushy, just right, or not pushy enough?
2. **Test on Claude Code** if available, where independent invocation is possible — this would catch cases where the skill doesn't trigger or where another instance of Claude doesn't adopt the stances.
3. **Add adversarial prompts**: cases where the user pushes back ("but my reviewer said use varimax") to test whether the skill holds the line.
4. **Add Quant-UXR-specific prompts**: industry-flavored cases that don't sound academic. E.g., "should I A/B test on Likert means?" or "I have 5 brand attributes — can I just average them into a brand health score?"
