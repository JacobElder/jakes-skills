# Reasoning Transcript: method-selection-maxdiff (with_skill)

## Task
"I want to rank 30 product benefits by importance for our messaging team. What's the best approach and roughly how many respondents do I need?"

## Step 1: Method identification

The task is single-dimension prioritization of a list of items (benefits) on importance/appeal. This maps cleanly to the method-selection table in SKILL.md:

> "Prioritize a long list of features/messages/benefits on a single dimension (importance, appeal) → MaxDiff"

No trade-off structure is described (no price, no bundled attributes). CBC is explicitly called out in SKILL.md as wrong here: "running CBC when the real question is 'which of these 30 messages resonates' — Conjoint over messages is almost always a misuse — use MaxDiff."

Rating scales are the obvious naive alternative and SKILL.md addresses this directly: scale-use bias, ceiling effects, no forced trade-off. With 30 items rated on importance, the likely outcome is 25+ items rated "very important" with no discrimination.

## Step 2: Full vs. sparse design decision

k = 30 is in the "full design still feasible" range per SKILL.md: "16–30: full design still feasible; respondent burden becomes the constraint, not statistical." However, I need to verify the sets per respondent math to confirm feasibility.

With m = 4 items per set, target r = 4 showings/item:
- s = k × r / m = 30 × 4 / 4 = 30 sets — too long (maxdiff.md: "most respondents tolerate 12–15 sets without quality degradation")

With m = 5, 15 sets:
- r = 15 × 5 / 30 = 2.5 showings/item per respondent — acceptable but not generous

With m = 5, 18 sets:
- r = 18 × 5 / 30 = 3.0 — solid

Conclusion: full design is feasible at 15–18 sets with 5 items per set. Sparse is not needed at k = 30 but becomes sensible above k ~35.

## Step 3: Anchoring trigger

SKILL.md has an explicit trigger: "whenever the user mentions 'importance'..." — this question literally asks about "importance." The skill states:

> "Unanchored MaxDiff cannot support absolute claims, and most stakeholder requests for 'importance' are implicitly asking for something anchoring is required to answer."

The messaging team use case (deciding which benefits to lead with) is an absolute question, not a purely relative one. Anchoring is required and must be flagged prominently.

Anchoring method: Direct binary anchor is the recommended default per maxdiff.md. Dual-response anchor would also work but is more complex.

## Step 4: Sample size derivation

From maxdiff.md and sample-size.md:

SE formula:
```
SE_i ≈ C / sqrt(n × r)
```

With r = 2.5 and C ≈ 12:

- n = 200: SE ≈ 12 / sqrt(200 × 2.5) = 12 / sqrt(500) = 12 / 22.4 ≈ 0.54 logit ≈ 4.8 on 0–100
- n = 300: 12 / sqrt(750) = 12 / 27.4 ≈ 3.9 points
- n = 400: 12 / sqrt(1000) = 12 / 31.6 ≈ 3.4 points
- n = 600: 12 / sqrt(1500) = 12 / 38.7 ≈ 3.1... wait, let me recalculate: sqrt(600 × 2.5) = sqrt(1500) = 38.7, 12/38.7 ≈ 2.8 points (not 3.1)
- n = 800: 12 / sqrt(800 × 2.5) = 12 / sqrt(2000) = 12 / 44.7 ≈ 2.4 points

Smallest detectable gap ≈ 2.8 × SE (from sample-size.md worked examples):
- n = 200 → ~13.4 points
- n = 300 → ~10.9 points
- n = 400 → ~9.5 points
- n = 600 → ~7.8 points
- n = 800 → ~6.7 points

The sample-size.md quick reference table confirms: "Sparse MaxDiff, 30–80 items → 500–1000" but this is actually borderline full vs. sparse at k = 30. For full design at 30 items, the default in sample-size.md is "MaxDiff, ≤25 items → 250–400" extrapolated slightly upward given k = 30 is just above the breakpoint. I'll recommend 400–500 as the base case, 600–800 for subgroup needs.

## Step 5: Estimation method

maxdiff.md is unambiguous: "Aggregate-only logit on MaxDiff data is almost never the right answer. Even when reporting only aggregate utilities, run HB and average." This should be stated as a requirement, not a suggestion.

## Step 6: Output guidance

The response should address what the messaging team gets, not just the survey design. SKILL.md and maxdiff.md both emphasize:
- CIs / significance bands, not just point estimates
- Lead with anchored share-above-anchor, not raw utilities
- Explicitly group statistically tied items

## Skill utilization assessment

The skill triggered correctly on "rank," "30 product benefits," and "importance." Core guidance applied:
- Method selection table → MaxDiff
- Anti-pattern flagged → CBC would be wrong here
- Anchoring trigger fired → importance keyword
- Anchoring method → direct binary (default)
- Design math applied → 5 items/set, 15–18 sets, r = 2.5–3.0
- Sample size derived from precision formula, not rule-of-thumb
- Subgroup multiplier explained
- HB requirement stated
- Reporting guidance applied (CIs, anchor-first framing)
