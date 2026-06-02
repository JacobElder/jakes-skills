# Iteration 1 — grading summary

Self-run on Claude.ai (no subagents): the skill was executed by the same model
that wrote it, so this is the optimistic ceiling — a check that the workflow
produces correctly-shaped, complete outputs and that the script integrates, NOT
an independent benchmark. Read it that way.

| Eval | Focus | Expectations passed |
|---|---|---|
| 1 | Full checkout A/B brief | 8 / 8 |
| 2 | Scoped sample-size ask (scale-down) | 6 / 6 * |
| 3 | Critique: no control / before-after | 5 / 5 |
| 4 | n=30 within-subjects UXR | 5 / 5 |
| 5 | Quasi-experiment (fee-cap law) | 5 / 5 |
| 6 | Interference → cluster (social) | 5 / 5 |
| 7 | File-based power/runtime from CSV | 5 / 5 |

All formal expectations pass, but one real defect surfaced:

## Defect (eval 2): hand-waved a wrong secondary number
The main answer (6,950/arm) is correct and scoped well. But in a clarifying
aside about the *relative*-lift interpretation, the output asserted "roughly
1.7M per arm" — the correct value is ~140,000/arm (verified via the script).
Off by ~12x.

Root cause: the skill insists on using the calculator for *the* calculation, but
didn't stop the model from tossing out an illustrative N from mental math. Mental
math on sample sizes is unreliable (N scales with 1/MDE², which intuition gets
wrong fast).

Proposed fix (small, generalizable): add a line to step 5 / the script section
telling the model that *any* sample size it states — including hypotheticals,
ranges, and asides — must come from the script, never mental math; if it's worth
mentioning a number, it's worth one more script call.

## Observations
- The new content surfaced naturally: eval 7 proactively raised the
  ratio-metric / delta-method caveat; eval 1 handled ethics in one line without
  over-moralizing (the calibration held).
- Scale-down worked: eval 2 stayed short instead of emitting a full brief.
- Eval 6 correctly framed interference as bias, not noise — the distinction the
  expectation was probing.
