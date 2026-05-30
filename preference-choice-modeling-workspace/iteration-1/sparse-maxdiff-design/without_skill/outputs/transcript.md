# Eval Transcript — Sparse MaxDiff Design (Without Skill)

## Task
Design a MaxDiff survey for 75 potential feature ideas: items per set, showings per item, sample size.

## Condition
Baseline (no skill)

## Model
claude-sonnet-4-6

## Date
2026-05-29

---

## Summary of Response

The model correctly identified this as a MaxDiff (Best-Worst Scaling) problem and addressed all three design dimensions:

**Items per set:** Recommended 5 (range 4–6), correctly identified 5 as the industry standard.

**Showings per item:** Recommended 3–4 per item. Correctly identified the sparse design problem: 75 items × 3 showings ÷ 5 per set = 45 tasks/respondent, which is infeasible. Proposed a sparse incomplete block design with ~18 tasks per respondent covering ~60 of 75 items per person, with coverage achieved across the respondent pool.

**Sample size:** Recommended 300–400 for aggregate MNL analysis, 400–500 for hierarchical Bayes (HB) or subgroup analysis. Provided rough math: 300 respondents × 18 tasks × 5 items = ~360 observations per item.

**Additional content:** Discussed BIBD generation tools (Sawtooth, R, Python), orthogonality checks, pilot testing, analysis approaches (MNL vs. HB), and common pitfalls (fatigue, sparse HB bias, item clustering).

---

## Assessment Notes

- Correctly named the sparse design problem with large item pools
- Gave the standard industry recommendation of k=5 items per set
- Math for total observations and per-item coverage was reasonable and shown explicitly
- Mentioned HB vs. aggregate distinction, which is relevant to sample size
- Did not reference specific efficiency metrics (D-efficiency, overlap rates) or formal design optimization criteria
- Did not distinguish between "showings per item per respondent" vs. "total showings across all respondents" with full clarity — used the sparse framing but could have been more explicit
- Practical steps and pitfalls section was a reasonable addition
