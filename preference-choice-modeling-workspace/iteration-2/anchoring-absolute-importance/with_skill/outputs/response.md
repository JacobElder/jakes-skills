# Getting to Absolute Importance from a MaxDiff

Your stakeholder's question — "which features are *actually* important" — is a fundamentally different question than what unanchored MaxDiff answers by default. This distinction is not cosmetic; it determines which analysis is valid and which results you can honestly report.

---

## The core problem: unanchored MaxDiff has no zero

Unanchored MaxDiff utilities are relative. The model normalizes across whatever items are in the study — the resulting scores tell you that Item A is more preferred than Item B, nothing else. There is no zero that separates "things people actually value" from "things people merely value slightly more than even-worse things."

A deck showing "Feature 1: 82, Feature 8: 18" does not tell you Feature 8 is unimportant. Both features could be above the threshold for motivating behavior, or both could be below it. You simply cannot know from unanchored data.

**If your study ran without anchoring, you cannot answer your stakeholder's actual question.** The only valid statement is relative ordering. You can say "Feature 1 is more important than Feature 8" — that's it.

---

## What you need: anchoring

Anchoring adds a reference point that separates "above the bar" from "below the bar." Two methods are used in practice:

### Direct binary anchor (recommended default)

After the MaxDiff sets, every respondent answers a simple binary task for each item: "Would you consider this a meaningful benefit?" or "Is this important to you in [context]?" The items they flag become the anchor.

How it works analytically:
- You have each respondent's anchor threshold (the set of flagged items).
- Utilities are rescaled so that items above the anchor are positive and items below are negative in the rescaled space.
- Reporting leads with the **share-above-anchor**: the proportion of respondents who flagged Item X as genuinely important, not just relatively preferred.

What stakeholders can actually say:
- "68% of respondents flagged Feature 1 as genuinely important."
- "Feature 8 was above the threshold for only 22% of respondents."
- "The cutoff between 'actually matters' and 'relatively preferred but not critical' falls between Feature 4 and Feature 5."

This is the language your stakeholder is asking for. It requires the anchor.

### Dual-response anchor

After each MaxDiff set, a follow-up question is embedded: "Are any of the items you selected actually important to you?" This embeds the anchor in the task rather than adding a separate post-task module.

When to use it: when the items are evaluative statements or agreement items, where a separate flagging task would feel awkward or redundant. For feature importance research, the direct binary anchor is cleaner and more intuitive for respondents.

---

## If anchoring was not included in your study

This is the hard conversation to have. There is no post-hoc fix that recovers absolute importance from unanchored data. Re-fielding with anchoring is the correct answer if the absolute importance question is genuinely what your stakeholder needs.

What you can do in the meantime:
- Report relative rankings clearly, with confidence intervals showing which items are statistically distinguishable.
- Be explicit with stakeholders: "This data tells us which features are more important relative to each other, but not which are important in an absolute sense. To answer that, we need to re-run with anchoring."
- Do not attempt to impute a threshold from external benchmarks, prior waves, or other studies unless those were also run with anchoring and the item sets are comparable.

---

## If your study was anchored: how to report it

Lead with the share-above-anchor, not the rescaled utilities.

**Recommended reporting structure:**
1. A chart showing each item's share-above-anchor (proportion of respondents who flagged it as genuinely important). This is the primary answer to "which features are actually important."
2. Underneath that, the rescaled utilities for rank-ordering *among* the important features.
3. Confidence intervals on both. Stakeholders read point estimates as truth; the practitioner's job is to make uncertainty visible.

**What to avoid:**
- Leading with a sorted utility list without the anchor. This invites the relative-as-absolute misread.
- Summarizing with "Top 2 Box" logic from rating scales. The valid analog is share-above-anchor.
- Presenting a feature as unimportant because its utility is in the bottom quartile — if its share-above-anchor is 40%, it is important for a large segment of respondents.

---

## Cross-wave and cross-study comparisons

If your stakeholder asks "how does this compare to last year's study" — anchored share-above-anchor is the only valid cross-wave metric. Raw utilities from two different MaxDiff studies are not comparable because different item sets produce different normalizations. If prior waves were unanchored, there is no reliable way to compare; re-fielding with anchoring is the correct answer.

---

## Summary

| What your stakeholder asked | What answers it | What does not answer it |
|---|---|---|
| "Which features are actually important?" | Anchored MaxDiff — share-above-anchor | Unanchored MaxDiff utilities |
| "Which features are most important relative to others?" | Unanchored or anchored MaxDiff utilities | — |
| "How important is Feature X overall?" | Anchored share-above-anchor for Feature X | Rank position or rescaled utility alone |

If the study ran unanchored, you can answer the relative question but not the absolute one. The honest answer to your stakeholder is to explain that distinction and plan for a follow-up anchored wave if absolute importance is the decision-relevant output.
