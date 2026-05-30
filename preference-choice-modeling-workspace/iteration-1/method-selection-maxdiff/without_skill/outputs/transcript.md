# Transcript: Baseline (No Skill) Response

## Task
Evaluate the best approach and sample size for ranking 30 product benefits by importance for a messaging team.

## Approach Taken

Responded from general knowledge without consulting any skill files or external references.

**Method reasoning:**
- Identified the core problem: large item sets (30 items) are poorly handled by rating scales and direct ranking
- Recommended MaxDiff (Best-Worst Scaling) as the appropriate technique
- Explained why alternatives (Likert ratings, direct full ranking, top-box picking) are inferior for this use case

**Study design:**
- Covered key design parameters: items per set (4–5), tasks per respondent (~22–24), and the goal of ~3 exposures per item
- Derived sample size recommendation from first principles: N=200 as primary recommendation, with ranges for different precision levels and segment-level analysis needs

**Analysis guidance:**
- Mentioned both count-based scoring and HB (Hierarchical Bayes) logit scoring as analytical options
- Referenced common software platforms (Sawtooth, Qualtrics)

## Key Claims Made
- MaxDiff is the recommended method for 30 items
- 4–5 items per set, ~22 tasks per respondent
- N = 200 for reliable total-sample rankings
- N = 200–300 per segment if segment-level cuts are needed
- Count-based vs. HB analysis tradeoffs mentioned

## Notes on Potential Gaps (Without Skill)
- Did not reference specific academic literature or rules of thumb from MaxDiff methodology literature
- Sample size guidance was derived from general principles rather than validated formulas (e.g., Orme's rule of thumb: N × T ≥ 500 × a, where T = tasks and a = items per set)
- No mention of minimum-counts-per-cell diagnostics
- Did not cover alternative methods like TURF, conjoint, or direct Q-sort in depth
