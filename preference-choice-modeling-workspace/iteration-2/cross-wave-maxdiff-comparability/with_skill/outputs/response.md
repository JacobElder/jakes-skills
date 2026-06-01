# Cross-Wave MaxDiff Comparability

## Short answer

No — not directly, and whether you can at all depends on one thing: **was Wave 1 anchored?**

Raw or rescaled utilities from MaxDiff studies are not comparable across waves when the item sets differ. Adding 5 items and swapping 3 changes the normalization denominator, so a utility score of 72 in Wave 1 and 65 in Wave 2 for the same benefit doesn't tell you the benefit declined — it could simply reflect a different pool of comparison items. The only valid cross-wave metric is **anchored share-above-anchor**, and only if you use the same anchor in both waves.

---

## Why raw utilities don't travel

MaxDiff utilities are rescaled relative to the specific item set tested. In practice, most platforms normalize so that utilities sum to zero (or to a constant like 100) across the k items in the study. When you change the item set — adding 5, swapping 3 — the normalization shifts. An item that rated high in a 25-item pool will have a different utility score in a 27-item pool, even if respondents' underlying preferences haven't changed at all. This is not a bug; it is inherent to relative scaling. The consequence is that you cannot interpret a year-over-year change in rescaled utilities as evidence of change in actual importance.

---

## What anchoring fixes

Anchored MaxDiff adds a direct binary question after the MaxDiff sets: for each item, respondents flag whether it clears a threshold ("Is this benefit genuinely important to you?" or similar). The resulting **share-above-anchor** is grounded in respondents' threshold judgments, not in the relative normalization of the item pool. Because you're asking the same binary question about the same threshold, that share is comparable across waves — even when the item sets differ.

If Item X had a 62% above-anchor share in Wave 1 and 54% in Wave 2, that is evidence of a real decline. The item-pool composition doesn't contaminate that comparison.

---

## Your situation, specifically

**If Wave 1 was anchored:**

You can compare Wave 1 and Wave 2 for the ~19 items that appear in both waves, provided you use the same anchor question wording verbatim in Wave 2. The 5 new items won't have a prior-wave baseline — that's expected, Wave 2 becomes their starting point. The 3 dropped items simply exit the tracker at Wave 1.

A few things to lock down before fielding Wave 2:
- Use the **exact same anchor question wording** as Wave 1. Even minor wording changes can shift the threshold interpretation across respondents.
- If feasible, include one "anchor calibration" item — a benefit expected to be universally high and one universally low — in both waves. If those items' above-anchor shares shift dramatically, you have a measurement consistency problem, not a real preference shift.
- Report trend lines only for items in both waves. Be explicit in the deliverable that the 3 dropped items are discontinued and the 5 new items start fresh.

**If Wave 1 was unanchored:**

There is no reliable method to recover comparability post-hoc. Attempts to use item means, percentile thresholds, or empirical anchors from Wave 1 to create a pseudo-comparison produce estimates too unstable to defend to stakeholders. The correct path is:

1. Add a direct binary anchor to Wave 2 now.
2. Treat Wave 2 as the new tracking baseline.
3. Communicate to stakeholders that Wave 1 established rank order among 25 benefits, but cross-wave magnitude comparisons require the anchor that starts with Wave 2.

This is a straightforward message. It's a better outcome than shipping a Wave 1-to-Wave 2 comparison that is technically invalid.

---

## What you can still say from unanchored data (limited)

If Wave 1 was unanchored and stakeholders want some signal from it, one methodologically defensible comparison is **relative rank-order stability** for the common items. You can run a rank correlation between the Wave 1 and Wave 2 utilities for the ~19 shared items and report whether their relative ordering held. This answers "did the rank structure change?" — not "did absolute importance grow or fall." Make that boundary explicit. Items that jumped in rank or dropped significantly warrant qualitative investigation into what changed, but you cannot quantify the magnitude of change.

---

## Recommended anchor for Wave 2

Use a **direct binary anchor**: after all MaxDiff sets, show respondents the full list of 27 items and ask them to check every one that meets a defined threshold (e.g., "Check all of the following that are genuinely important to you when choosing [product category]"). This:

- Cleanly separates relative preference (MaxDiff sets) from absolute threshold (binary check)
- Produces a simple, interpretable metric (% above threshold) for trend reporting
- Is easy to carry forward identically in Wave 3 and beyond

Dual-response anchoring (embedding the anchor judgment within each MaxDiff set) is an alternative but adds survey length and complexity without a material advantage for tracking studies where absolute share comparisons are the deliverable.

---

## Summary checklist before fielding Wave 2

- [ ] Confirm whether Wave 1 included a binary anchor question
- [ ] If yes: use identical wording in Wave 2; comparison is valid for the 19 retained items
- [ ] If no: add anchoring in Wave 2; treat as new baseline; do not attempt direct magnitude comparison to Wave 1
- [ ] Document which items are retained, added, and dropped; clearly label in deliverable
- [ ] Do not present year-over-year utility score changes to stakeholders without confirming the anchor question was identical — even a small wording change invalidates the comparison
