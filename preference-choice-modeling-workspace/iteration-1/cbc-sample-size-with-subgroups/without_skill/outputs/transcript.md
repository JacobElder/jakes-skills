# Transcript — CBC Sample Size with Subgroups (Without Skill)

## Task
Planning a CBC for a new pricing tier. 6 attributes (brand, price, 4 features). Need to compare enterprise vs. SMB segments (roughly 50/50 in population). What's the right sample size?

## Condition
Baseline — no skill file consulted.

## Model Response Summary

**Core recommendation:** 500 total respondents (250 per segment).

**Reasoning provided:**
- Applied the standard "minimum cells" heuristic: n ≥ (500 × c) / (t × a), where c = max levels on any attribute, t = tasks, a = alternatives per task
- Noted this gives a floor per segment, not a total
- Recommended 200–250 per segment as a standard commercial target for stable HB part-worth estimation
- Flagged 150/segment as a defensible minimum and 300+/segment for high-confidence pricing decisions
- Provided a table: 300 (min viable), 400–500 (standard), 600+ (high confidence)
- Discussed power analysis angle: ~200/segment to detect medium effect size differences between segments
- Discussed how attribute levels, number of tasks, and analysis method (HB vs. latent class vs. aggregate logit) affect required N
- Provided a practical checklist for finalizing design

**Key numbers cited:**
- 250 per segment / 500 total = primary recommendation
- 200 per segment / 400 total = budget-constrained defensible threshold
- 150 per segment = floor below which segment comparisons become unreliable

## Notable Gaps vs. Ideal Answer
- Did not reference specific academic citations or Sawtooth Software documentation
- Did not discuss Johnson-Orme rule by name (though applied the underlying formula)
- Did not address design efficiency (D-efficiency) optimization explicitly
- Did not discuss overlap or balance in the experimental design
- Segment comparison power was discussed qualitatively but not with a formal formula
- No mention of simulation-based power estimation approaches
