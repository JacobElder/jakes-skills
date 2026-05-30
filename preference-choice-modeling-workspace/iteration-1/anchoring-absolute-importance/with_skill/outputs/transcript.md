# Transcript

## Prompt

"My stakeholder is asking 'which features are actually important' not just 'which are more important than others'. How do I get to that from a MaxDiff?"

## Skill Used

`preference-choice-modeling` — read SKILL.md and references/maxdiff.md (anchoring section, section 5).

## Response

See `response.md`.

## Key Points Covered

1. **Root cause of the problem**: plain MaxDiff utilities are relative by construction — normalization removes any absolute zero, so utilities only support ordinal comparisons, not absolute importance claims.

2. **Direct binary anchor**: post-task checklist asking whether each item crosses a meaningful threshold; proportion flagging "yes" is the absolute importance estimate. Recommended default. Wording of the threshold question is critical.

3. **Dual-response anchor**: embed the anchor question after each MaxDiff set rather than as a separate task; lower scale-use bias but noisier per-item estimates, more complex estimation. Use when a standalone binary question would feel unnatural.

4. **Reporting format**: lead with share-above-anchor per item, then utilities for within-threshold rank-ordering. Anchored shares are also cross-study comparable; raw utilities are not.

5. **If the study already ran without anchoring**: options are refield, use a proxy anchor question with explicit caveats, or flag the limitation explicitly and refuse to claim any item is "unimportant."

6. **What to avoid**: labeling utility magnitudes as "moderately important" or "low importance" without an anchor; treating utility rank as a proxy for absolute importance.
