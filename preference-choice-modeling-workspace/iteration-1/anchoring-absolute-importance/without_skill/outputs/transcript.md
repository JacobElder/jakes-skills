# Transcript — Baseline (No Skill)

**Condition:** without_skill  
**Date:** 2026-05-29  
**Model:** claude-sonnet-4-6  

---

## Task Prompt

"My stakeholder is asking 'which features are actually important' not just 'which are more important than others'. How do I get to that from a MaxDiff?"

---

## Summary of Response

The response correctly identified the core problem: standard MaxDiff produces ipsative (relative) scores and cannot answer absolute importance questions directly.

Five methods were described:

1. **Anchored MaxDiff** — identified as the gold standard; adds a post-task follow-up to establish an absolute zero point on the importance scale.
2. **Probability rescaling** — converting logit scores via softmax to share-of-preference scores for more communicable magnitude, while noting this still doesn't resolve the absolute question.
3. **External benchmarking** — including calibration items of known importance levels in the item set to provide informal anchors.
4. **Supplementary direct ratings** — pairing MaxDiff with a Likert importance battery post-survey to cross-validate, with caveats about acquiescence bias.
5. **"Never best" count analysis** — identifying features no respondent ever selects as best as a proxy for irrelevance.

A recommended path was given for both scenarios (data already collected vs. redesign possible), and a stakeholder-ready talking point was provided.

---

## Observed Strengths

- Correctly named "anchored MaxDiff" / "anchored best-worst scaling" as the primary solution.
- Correctly described the mechanism (post-task anchor question to establish absolute zero).
- Correctly described the ipsative nature of raw MaxDiff scores as the root cause of the problem.
- Identified acquiescence bias as the limitation of direct rating supplementation.

## Observed Weaknesses / Gaps

- Did not mention Sawtooth Software's specific implementation details for anchored MaxDiff.
- Did not discuss the statistical model underlying anchored estimation (e.g., the None/anchor parameter in HB estimation).
- Did not mention the "top 2 box" or "importance threshold" conventions sometimes used in practice.
- Did not distinguish between object-case and profile-case best-worst scaling, which affects how anchoring is implemented.
- Probability rescaling explanation was correct but somewhat surface-level on the math.
