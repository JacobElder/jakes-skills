# Transcript — Without Skill Baseline

**Date:** 2026-05-29
**Condition:** No skill loaded; response from built-in model knowledge only
**Task prompt:** "I want to rank 30 product benefits by importance for our messaging team. What's the best approach and roughly how many respondents do I need?"

---

## Summary of Response

The model recommended **MaxDiff (Best-Worst Scaling, Case 1)** as the appropriate method and provided the following key details:

**Method identification:** Correctly named MaxDiff and explained why direct ranking and rating scales are inferior for 30 items.

**Design parameters given:**
- Set size: 5 items per set
- Sets per respondent: 20–24
- Item appearances: 3–4 per item

**Sample size guidance:**
- 150–200 for aggregate ranking only
- 300–400 for 2–3 segment comparisons
- 400–600 for high-stakes or fine discrimination needs
- Practical recommendation: 200–300

**Analysis methods mentioned:** Aggregate logit, Hierarchical Bayes (HB); noted HB enables individual-level scores.

**Scoring:** Mentioned 0–100 rescaled probability scores.

**Pitfalls noted:** Rating scale bias, cognitive overload of direct ranking, over-segmentation with small N.

---

## Observations for Eval

- Correctly identified MaxDiff as the preferred method without being prompted.
- Provided a sensible design formula (sets = items × appearances / set size).
- Sample size ranges are in the right ballpark but given as wide ranges without specific anchoring to statistical precision criteria (e.g., standard error targets, confidence intervals on utility scores).
- Did not mention specific software (Sawtooth, Qualtrics, etc.) or formal design efficiency concepts (D-efficiency, balanced incomplete block designs).
- Did not mention the distinction between Case 1 (object scaling) vs. Case 2/3 Best-Worst Scaling — though it labeled the method correctly.
- No mention of test-retest reliability, holdout tasks, or fit statistics for validating the MaxDiff model.
