# Eval Transcript — Baseline (No Skill)

## Metadata

- **Eval:** sparse-maxdiff-design
- **Condition:** without_skill
- **Model:** claude-sonnet-4-6
- **Date:** 2026-05-29
- **Skill loaded:** None

## Task Prompt

> I have a list of 75 potential feature ideas and need to prioritize them. Walk me through how to design this — items per set, showings per item, sample size.

## Response Summary

The model answered with a structured MaxDiff design walkthrough covering:

1. **Items per set:** Recommended 5 (standard sweet spot, balancing information yield vs. cognitive load). Noted range of 4–7 and reasons to avoid extremes.

2. **Showings per item:** Distinguished between per-respondent and aggregate showings. Recommended targeting 3–5 showings per item in aggregate. Introduced sparse/incomplete block design as the practical approach for 75 items. Did NOT clearly specify a concrete target showings-per-item figure for the sparse case (e.g., did not anchor on the standard "each item shown ~3× per respondent" guidance for HB).

3. **Sets per respondent:** Recommended 12–18 sets (targeting 15 for complete coverage of 75 items at 5 per set). Noted 15 is a practical ceiling and sparse designs allow fewer sets with better data quality.

4. **Sample size:** Provided dual guidance — aggregate logit (400–600), HB (150–300), with segmentation bumping to 300–500. Used a "500 exposures per item" heuristic for aggregate but did not tie this cleanly to the sparse design case.

5. **Design construction:** Mentioned Sawtooth/Qualtrics, BIBD construction, balance checking, anchoring, and randomization.

6. **Estimation:** Covered counting, aggregate logit, and HB.

## Key Gaps / Accuracy Notes

- The response correctly identifies the sparse/incomplete block design as appropriate for 75 items but is **vague on the concrete mechanics**: did not specify the standard formula `n_respondents × showings_per_respondent / N_items` to determine aggregate coverage.
- The **500-exposures-per-item rule** is a reasonable heuristic for aggregate logit but not standard industry guidance — more typical is ~200–300 aggregate exposures per item.
- The model **did not mention the concept of "versions"** (i.e., multiple survey versions with different item rotation schemes) — a key operational detail for sparse MaxDiff at scale.
- HB sample size guidance (150–300) is reasonable but on the low end; many practitioners target 300+ for 75-item pools.
- No mention of **d-efficiency** or algorithmic design construction as the preferred method over pure BIBD for unequal item counts or practical constraints.
- Response is generally correct in direction but lacks precision on the sparse design case, which is the core challenge with 75 items.
