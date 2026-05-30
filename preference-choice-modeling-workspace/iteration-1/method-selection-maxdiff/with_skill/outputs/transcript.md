# Reasoning Transcript

## What I read

1. `/Users/jacobelder/Documents/GitHub/jakes-skills/preference-choice-modeling/SKILL.md` — The top-level skill file. Key guidance extracted:
   - The method-selection table explicitly maps "Prioritize a long list of features/messages/benefits on a single dimension (importance, appeal)" → **MaxDiff**.
   - 30 items is in the 16–30 range: "full design still feasible; respondent burden becomes the constraint, not statistical."
   - The skill flags the second most common mistake as "running CBC when the real question is 'which of these 30 messages resonates' — use MaxDiff."
   - For sample size, the skill instructs: resist quoting a single number; derive from precision needed on the decision.
   - The skill points to `references/maxdiff.md` and `references/sample-size.md` for the math.

2. `/Users/jacobelder/Documents/GitHub/jakes-skills/preference-choice-modeling/references/maxdiff.md` — Advanced MaxDiff reference. Key content used:
   - Design math: r = s × m / k. With k = 30, m = 4, target s ≈ 15–18 sets gives r ≈ 2–2.4 per respondent.
   - Respondent burden ceiling: "most respondents tolerate 12–15 MaxDiff sets without quality degradation. Beyond ~18, response times collapse." This constrained the set count recommendation.
   - Sample size formula: SE_i ≈ C / sqrt(n × r), C typically 8–15 for 0–100 rescaled scores. Used C = 12 as midpoint.
   - Anchoring: unanchored utilities are relative-only; direct binary anchor is the recommended default for messaging/benefits studies.
   - HB estimation: always prefer HB to aggregate logit; run ≥30,000 post-burn-in iterations.
   - Reporting traps: rank-order trap (adjacent items may be statistically tied), absolute importance trap (requires anchor), always show CIs.

3. `/Users/jacobelder/Documents/GitHub/jakes-skills/preference-choice-modeling/references/sample-size.md` — Sample size derivation reference. Key content used:
   - Worked formula and table for SE vs n at different r values.
   - Quick reference table: "MaxDiff, ≤25 items, no subgroups: 250–400." The question is 30 items, so one step above — pushed to 400–500 as the base recommendation.
   - Subgroup rule: need 1/p × base n for segment precision parity.
   - "Smallest detectable difference ≈ 2.8 × SE" — used to construct the detection gap table in the response.

## Method decision

**MaxDiff, full design (not sparse).** 30 items is at the top of the comfortable full-design range. Sparse MaxDiff is for k > ~30–60 where per-respondent burden becomes infeasible even at low r. At 30 items with 15–18 sets of 4, every respondent sees every item at least twice, which is sufficient for HB to produce stable individual-level utilities.

Rejected alternatives:
- Rating scale: ruled out by scale-use bias and ceiling effects (per skill guidance on stakeholder pushback section).
- CBC: explicitly flagged in the skill as the wrong tool for "which of 30 messages resonates."
- Sparse MaxDiff: unnecessary at k = 30 and would reduce per-item precision without meaningful reduction in respondent burden.

## Sample size decision

Base case (no subgroups): **n = 400–500**.

Reasoning: With r ≈ 2 and C = 12, SE at n = 400 ≈ 12/sqrt(800) ≈ 4.2 pts on 0–100 scale, implying ~12 pt detection gap. This supports clear tier separation (top/middle/bottom) which is what a messaging team typically needs from a 30-item ranking study. If a tighter rank order is needed in the middle, push to n = 500–750.

Subgroup caveat surfaced explicitly in the response rather than buried — per skill instruction to "resist quoting a single number" and surface the subgroup question.

## Anchoring

Added direct binary anchor as default (per `references/maxdiff.md` section 5). The task is messaging benefit ranking, which is exactly the use case where stakeholders will misread unanchored utilities as absolute importance. The direct binary is cleaner for this context than dual-response (which is better suited to evaluative/attitudinal statements).

## Reporting guidance

Included the CIs / significance-tier framing from the reporting section of `references/maxdiff.md` because the rank-order trap is near-universal in messaging research deliverables.
