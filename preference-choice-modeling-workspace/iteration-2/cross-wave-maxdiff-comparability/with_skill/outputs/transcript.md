# Reasoning Transcript — Cross-Wave MaxDiff Comparability

## Task
User wants to compare MaxDiff utility scores across two waves:
- Wave 1: 25 items
- Wave 2: 27 items (5 new, 3 swapped out, retaining ~19 original items)

The question is whether utility scores can be compared across waves to detect which benefits have grown or declined.

---

## Reasoning Process

### Step 1: Identify the core problem

This is a cross-study comparison question. The skill's SKILL.md explicitly addresses this in the "Common requests" section:

> "Can we compare our MaxDiff results to last year's wave / a competitor study?" → Only if both studies were anchored. Raw utilities from different MaxDiff studies are not comparable — different item sets produce different normalizations. Anchored share-above-anchor is the only valid cross-wave metric. If the prior wave was unanchored, there is no reliable way to compare; re-fielding with anchoring is the correct answer.

The reference file (maxdiff.md section 9) reinforces this:

> "Cross-study comparisons: rescaled utilities from one MaxDiff study are not comparable to those from another (different item set → different normalization). Anchored shares are comparable across studies. If the stakeholder wants to track importance over time, anchor."

### Step 2: Diagnose why raw utility comparison fails

The normalization issue is fundamental to how MaxDiff utilities are computed:
- In standard MaxDiff, utilities are zero-centered or rescaled so they sum to a constant (e.g., 0–100 or sum-to-zero). This normalization is **relative to the specific item set** tested in that wave.
- When you add 5 items and remove 3, you have a different 27-item set. The normalization denominators change. An item that scored 72 in Wave 1 could score 65 in Wave 2 not because respondents care about it less, but simply because the pool contains new items that soak up some of the relative "importance budget."
- Even if item sets were identical, the rescaling would vary if the overall latent utility distribution changes (e.g., different year, different macro environment).

### Step 3: What does anchoring solve?

Anchored MaxDiff solves this by providing a fixed external reference point that is independent of the item set composition. The most common method — direct binary anchor — asks respondents to flag every item that meets a threshold (e.g., "Is this benefit actually important to you?"). The anchored score then represents the proportion of respondents who say the item clears the bar, which is a population-level absolute statement rather than a relative-within-set rank.

Because the anchor is grounded in respondent behavior (binary flagging) rather than item-set normalization math, it is comparable across waves even when the item sets differ. If Item X had 62% above-anchor in Wave 1 and 54% in Wave 2, that's a real decline — the same question was asked of the same threshold.

### Step 4: The user's specific situation — what makes this harder

The user is adding 5 items AND swapping 3. This creates two compounding problems:

1. **Different item pools → different normalization**: As above, the rescaled utilities from Wave 1 and Wave 2 are on different scales. Even items that appear in both waves are scored relative to different comparison sets.

2. **Carry-over anchor on new items is undefined**: If Wave 1 was anchored, the anchor exists for the 25 Wave 1 items. Wave 2 has 5 new items with no Wave 1 baseline. This is fine for the new items (they simply don't have a prior-wave comparison), but the anchor infrastructure must be carried forward properly in the Wave 2 design — the same anchor question wording, threshold framing, and response scale must be used.

3. **Items swapped out have no Wave 2 data**: The 3 items dropped from Wave 1 will not appear in Wave 2. They simply exit the tracker. This is expected and acceptable — the user needs to communicate to stakeholders that those items' trends end at Wave 1.

### Step 5: The answer if Wave 1 was unanchored

If last year's study was unanchored (which is the more common default in Qualtrics/Sawtooth studies), the user cannot compare raw utilities. The skill is explicit: "there is no reliable way to compare; re-fielding with anchoring is the correct answer." The best path forward is to add anchoring in Wave 2 and treat Wave 2 as the new baseline for future tracking. Trying to correct unanchored Wave 1 utilities post-hoc (e.g., by using item means or empirical percentiles as a pseudo-anchor) produces unreliable estimates that will mislead stakeholders.

### Step 6: Structural recommendation for Wave 2 design

To enable proper cross-wave tracking going forward:
- Add a direct binary anchor to Wave 2 (and keep it identical in all future waves)
- Include an anchor consistency question to validate anchor calibration doesn't shift across years
- Use the same anchor wording verbatim year-over-year
- Consider including a small anchor calibration item (e.g., one item expected to be universally high and one universally low) to detect if the threshold interpretation drifts

### Step 7: What CAN be compared across waves even without anchoring

One legitimate cross-wave comparison is available even without anchoring: **relative rank-order stability within a subset**. If Items A, B, C, D, E all appeared in both waves and their relative rank order is of interest (not their absolute utility scores), the analyst can run a correlation or rank-order agreement test on the utilities for the common-item subset. This is weak evidence, not a strong comparability claim, but it is methodologically defensible as a "has the relative ordering of these specific items changed?" question. The user needs to be clear with stakeholders that this is a rank comparison, not a magnitude comparison.

### Summary of Key Judgments
- Core problem is normalization: MaxDiff utilities are relative to the item set
- Cross-wave comparison of raw/rescaled utilities is not valid when item sets differ
- Anchored share-above-anchor IS valid across waves
- If Wave 1 was unanchored: establish anchor in Wave 2, treat as new baseline
- If Wave 1 was anchored: carry the same anchor forward; comparison is valid for the 19 retained items
- New items in Wave 2 have no prior-wave anchor comparison by definition — that's fine
- Dropped items simply exit the tracker
