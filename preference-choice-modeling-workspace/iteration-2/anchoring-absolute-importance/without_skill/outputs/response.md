# Response: Getting to Absolute Importance from MaxDiff

## The Core Problem

Standard MaxDiff gives you **relative** importance scores — you know Feature A is more important than Feature B, but you don't know if A is genuinely important, somewhat important, or that the respondent cares little about any of them. The ranking is real, but the floor is unknown.

Your stakeholder's question — "which features are *actually* important" — requires anchoring the scale to something absolute.

---

## Option 1: Anchored MaxDiff (Best-Worst Scaling Type 2 / Profile Case)

The cleanest solution is to redesign the survey to include an **anchor item** — typically a "None of these" or "Not at all important" option alongside the standard best/worst choices.

### How It Works
- In each task, respondents choose the most AND least important item, plus indicate whether the least important item still matters at all (above/below an anchor threshold).
- This creates a true zero-point on the latent importance scale.
- Items can be scored as genuinely important (above anchor) vs. unimportant (at or below anchor).

### Limitation
- Requires redesigning the instrument — not applicable to already-collected data.

---

## Option 2: Dual-Response / Follow-Up Rating

After a standard MaxDiff, add a follow-up question for each item (or a subset):

> "How important is [Feature X] to you, regardless of how you ranked it?"  
> Scale: Not at all / Slightly / Moderately / Very / Extremely important

This anchors the MaxDiff-derived rank ordering to an absolute rating scale. You can then:
- Flag items rated "Not at all" or "Slightly" as **genuinely unimportant** regardless of their relative rank.
- Create a threshold (e.g., only items rated ≥ "Moderately" by ≥ X% of respondents are "important").

---

## Option 3: Normalization Against a Known Anchor Item

If you have a feature that all stakeholders agree is important (a "gold standard" item), you can:
1. Include it in the MaxDiff as a reference item.
2. Compare all other items' scores against it.
3. Items scoring substantially below it are likely unimportant in an absolute sense.

This is informal but practical for stakeholder communication.

---

## Option 4: Top-Box Analysis of MaxDiff Scores

For already-collected data without anchoring:

1. Compute individual-level MaxDiff scores (HB or MNL) normalized to sum to 100.
2. Look at the **distribution** of scores across respondents for each item.
3. Flag items where:
   - The mean score is very low (e.g., < 5 on a 0–100 scale).
   - A high percentage of respondents assigned it a near-zero score.

This is interpretive, not principled anchoring, but can support the stakeholder narrative.

---

## Option 5: Conversion Using a Threshold / Rule of Thumb

A common practitioner heuristic:

- Rescale so scores sum to 100 across all items.
- Items with scores **below 1/N × 100** (where N = number of items) are performing below chance — they're being chosen least more than most, indicating genuine unimportance.
- Items 1–2× the chance level are "on the margin."
- Items well above chance are "genuinely important."

Example: 20 items → chance = 5. Items scoring < 5 are genuinely unimportant; items > 10 are clearly important.

---

## What to Tell Your Stakeholder

MaxDiff alone can't definitively answer "actually important" without anchoring. Your honest answer is:

1. **If data is already collected:** Use the distribution-based approach (Option 4) or the chance-threshold heuristic (Option 5) as a practical proxy. Pair it with a rating scale if you have one.
2. **If survey design is flexible:** Implement anchored MaxDiff or a dual-response follow-up.
3. **Frame it clearly:** "These are the features that consistently rose to the top when people were forced to choose — but we can't say from this data alone whether even the top features hit a meaningful absolute threshold of importance without additional anchoring."

---

## Summary Table

| Approach | Data Needed | Principled Anchoring | Practical |
|---|---|---|---|
| Anchored MaxDiff (Type 2) | Redesign survey | Yes | Medium |
| Dual-response follow-up | Add post-hoc rating | Yes | High |
| Reference item comparison | Gold-standard item in survey | Partial | High |
| Distribution / top-box analysis | Existing MaxDiff data | No (interpretive) | High |
| Chance-level threshold heuristic | Existing MaxDiff data | Partial | High |
