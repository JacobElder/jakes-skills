# 02 — CTT Item Analysis on Eval Data

Classical test theory item statistics are the robust first look in **every** regime. No model
fitting, no distributional assumptions about latent ability, and the two core statistics map
directly onto the questions "is this item too easy/hard?" and "does this item separate good runs
from bad ones?" Script: `scripts/eval_item_analysis.py`.

## The response matrix

Rows = **takers** (versions, model tiers, ablations, seeds — see `07_small_sample_playbook.md`
for inflating this). Columns = **eval cases (items)**. Cell = 1 if the taker passed that case,
else 0 (or a partial-credit score in [0,1]). Long-format input expected by the script:

```
taker_id,item_id,score
v3,case_routing_01,1
v3,case_routing_02,0
haiku,case_routing_01,0
...
```

## Item difficulty (p)

Per-item pass rate: `p_i = mean(score over takers)`. **Higher p = easier item** (psychometric
convention; don't flip it). Interpretation for eval suites:

| p range | Meaning | Action |
|---|---|---|
| p ≥ 0.95 | **Saturated** — nearly everyone passes | Carries ~no information about differences. Cut *unless it guards a known regression/safety case* (then label and keep as insurance). |
| 0.70–0.95 | Easy | Keep a few as sanity checks; low discriminating power. |
| **0.30–0.70** | **Mid-range — maximum information** | The core of a discriminating suite. Keep. |
| 0.05–0.30 | Hard | Useful for separating strong takers; keep if discriminating. |
| p ≤ 0.05 | **Floored** — almost nobody passes | Either too hard to be informative yet, or *broken/mis-specified*. Inspect: is it measuring something real or is the grader wrong? |

**The mid-range difficulty filter:** an item near p≈0.5 carries the most discriminative
information about latent ability (this is an IRT result — Fisher information for a Rasch item
peaks where pass probability is 0.5). A validated, optimization-free suite-reduction rule is to
**retain items with pass rates in 0.30–0.70**; on agent benchmarks this cuts task count by
~44–70% while preserving model *ranking* fidelity. Use it as a default trimming heuristic, not a
law — temper it with the discrimination statistic and the guard-item exception below.

## Item discrimination (item–rest correlation)

The key statistic. For each item, correlate each taker's score on that item with that taker's
score on **all other items** (the "rest score" — exclude the item itself to avoid spurious
self-correlation). This is the point-biserial correlation with rest-score correction:

```
r_rest(i) = corr( score[:, i] , sum(score[:, j != i], axis=1) )
```

Interpretation:

| r_rest | Meaning | Action |
|---|---|---|
| **≥ 0.30** | Strong discrimination — good runs pass it, weak runs fail it | Keep; this is your signal. |
| 0.15–0.30 | Acceptable | Keep, especially if difficulty is mid-range. |
| 0–0.15 | **Non-discriminating** — passing it is ~unrelated to overall quality | Trim candidate. It adds runtime, not signal. |
| **< 0** | **Negative discrimination — broken item** | **Urgent fix, not trim.** Worse runs pass it more than better runs. Means the item rewards the wrong behavior, the gold label is wrong, or the grader is inverted. Investigate before trusting *any* suite-level number. |

Negative-discrimination items are the highest-value finding CTT produces: they are actively
poisoning your aggregate. A single inverted-label item can flip a version comparison.

A quick non-correlational proxy (robust at tiny N) is the **discrimination index / Mokken proxy**:
mean pass rate of the top-third takers minus the bottom-third (`D = p_top − p_bottom`). Same sign
convention; flag `D < 0.15` as weak, `D < 0` as broken.

## Saturation and contamination heuristics

- **Suite saturation:** if the median item difficulty is very high (most items p>0.9), the suite
  has aged out — top takers have hit the ceiling and it can no longer rank them. Symptom: versions
  you believe differ all score ~the same. Remedy: add harder cases; don't keep polishing a
  saturated suite.
- **Contamination smell (multiple-choice / known-answer items):** in IRT terms, contamination
  shows up as a high "guessing" floor — items everyone gets right *regardless of ability*, i.e.
  high difficulty-pass combined with **near-zero discrimination**. A cluster of easy +
  non-discriminating items, especially items whose answers are likely in training data, is a
  contamination smell. CTT can flag the pattern (easy ∧ r_rest≈0); confirming contamination needs
  the IRT 3PL guessing parameter (`04_irt_for_evals.md`) or provenance checks.
- **Redundant items:** if two items' pass/fail patterns across takers are nearly identical
  (high inter-item correlation), they're measuring the same thing — keep one. The script reports
  an item–item correlation matrix to spot clusters.

## Output the script produces

A per-item table (difficulty, r_rest, discrimination index, flags), a ranked trim list, a ranked
fix list (negative discrimination first), the mid-range-filtered suite, and — at small N —
bootstrap CIs on difficulty and r_rest so you don't act on a noisy point estimate. See
`01_diagnostic_workflow.md` for how the trim/keep/fix decisions compose with the guard-item
exception and the reliability check.
