# Cross-Wave MaxDiff Comparability

## Question

We ran a MaxDiff on 25 product benefits last year and want to run it again this year with 5 new items added and 3 old ones swapped out. Can we compare the utility scores across waves to see which benefits have grown or declined in importance?

---

## Response

The short answer is: **not directly, and with caution even indirectly.** Cross-wave MaxDiff comparability is a genuinely tricky psychometric problem, and the changes you describe — adding 5 items and swapping out 3 — create two distinct threats to comparability that you'll want to address before drawing any conclusions about change over time.

### Why Raw Utility Scores Are Not Directly Comparable Across Waves

MaxDiff utilities (whether raw counts, logit-scaled scores, or HB posterior means) are estimated relative to the item set. When you change the item set, you change the competitive context in which each item is evaluated. Adding 5 new items means there are now more alternatives competing for "most important" selections, and the new items may attract choices that previously went to existing items. Even if a benefit's true underlying importance to respondents has not changed at all, its estimated utility is likely to shift because it is now competing in a larger, different choice environment.

This is sometimes called the **scale indeterminacy problem** in discrete choice modeling: utilities are identified only up to an arbitrary normalization, and the normalization changes when the item set changes.

### The Specific Problems With Your Design Change

**1. Adding 5 new items**
New items dilute the competitive set. If the 5 new items are meaningful to respondents, they will draw "most important" choices away from existing items, depressing utilities for everything else — even if underlying preferences are unchanged. You cannot distinguish "this benefit declined in importance" from "this benefit now faces more competition."

**2. Swapping out 3 old items**
Removing items can have the opposite effect: it concentrates choices on the remaining items. The 3 removed items were absorbing some "most" and "least" selections; their absence means remaining items may score higher on average. Again, this has nothing to do with actual preference change.

**3. Scale re-anchoring**
If you use zero-centered scores or rescale to sum-to-100 (probability scores), the entire scale shifts when the item set changes. A score of 60 in Wave 1 and a score of 55 in Wave 2 for the same benefit could reflect actual decline, or simply the effect of a richer/different item set in Wave 2.

### What You Can Compare

**Items present in both waves (the overlap set):**
You have 25 − 3 = 22 items that appear in both waves. For these items, **relative rankings** within each wave are more interpretable than absolute utility differences. If benefit A ranked #3 in Wave 1 and #8 in Wave 2, that relative position change is a meaningful signal — though still influenced by the changed item set around it.

**Within-wave importance ordering:**
Each wave gives you a valid picture of what matters most within that wave's item set. You can tell stakeholders "benefit X is the top-ranked benefit in 2025 vs. 4th-ranked in 2024" and that is meaningful.

### Approaches That Can Help

**1. Anchored MaxDiff (if you can go back and re-run or plan ahead)**
Anchored MaxDiff adds a rating follow-up question (usually a Likert scale) after the best-worst task. This anchors the utilities to an absolute scale that is not purely relative to the item set. If both waves use anchored MaxDiff, inter-wave comparisons become much more defensible.

**2. Common-item equating / rescaling**
For the 22 items appearing in both waves, you can attempt to equate the scales using the common items as anchors. The logic: if the common items collectively represent the same "true" importance distribution, you can find a linear transformation (shift and stretch) that maps Wave 2 utilities onto the Wave 1 metric. This is analogous to test equating in psychometrics.

The simplest version: compute mean and SD of utilities for the 22 overlap items in each wave, then z-score them to a common metric. Differences in z-scored utilities across waves are then more comparable.

A more principled version: fit a regression of Wave 2 overlap utilities on Wave 1 overlap utilities, and use the regression to project Wave 2 utilities onto the Wave 1 scale. This works best when the overlap set is large and representative.

**Caveats on equating approaches:**
- These approaches assume the scale shift is uniform across all items. If some items are differentially affected by the new additions, equating will not fully correct for this.
- You need a reasonably large overlap set. With 22 of 25 items overlapping, you are in reasonable shape.
- The 3 removed items may have had specific substitution relationships with remaining items, introducing non-uniform distortion.

**3. Partial overlap / bridging study design (best practice going forward)**
If tracking over time is a priority, the best practice is to include a "bridge" condition in which a subset of respondents sees the original 25-item set, and a separate subset sees the new 27-item set (25 − 3 + 5). The bridge condition lets you directly estimate how much utility shifts due to item-set changes vs. true preference change. This design is feasible but requires larger total sample sizes.

**4. Separate-but-calibrated waves**
Another approach: run both waves with the new item set (27 items) but include a replication condition for Wave 1's item set in the same fielding period. This is retrospective bridging — you cannot do it now for your Wave 1 data, but it is useful for future waves.

### Practical Guidance for Your Situation

Given that you already have Wave 1 data and are about to field Wave 2, here is what I would suggest:

1. **Proceed with the planned Wave 2 design** (27 items), but acknowledge in reporting that direct utility comparisons are approximate.

2. **Use rank-order comparisons** for the 22 overlap items as your primary cross-wave comparison metric. Rank is less sensitive to scale shifts than absolute utilities.

3. **Apply z-score equating** on the 22 overlap items to put both waves on a common standardized scale before making any absolute comparisons. Flag results where equated differences exceed ~0.3–0.5 SD as potentially meaningful, and treat smaller differences as noise.

4. **Do not compare utilities for the 5 new items against Wave 1** — they have no Wave 1 baseline.

5. **Report with appropriate caveats**: "Comparisons between waves should be interpreted as directional signals rather than precise estimates, given changes to the item set between waves."

6. **For future tracking studies**, adopt a stable core item set policy (no removals, additions only in a secondary block) or use anchored MaxDiff to maintain an absolute reference point.

### Summary

| Comparison type | Feasibility | Method |
|---|---|---|
| Rank order change for overlap items | Feasible, recommended | Compare rank positions directly |
| Utility magnitude change for overlap items | Feasible with caveats | Apply z-score or regression equating on overlap set |
| Utility comparison for new items | Not feasible | No Wave 1 baseline |
| Direct raw utility comparison | Not recommended | Scale shift due to item set change |

The core issue is that MaxDiff is a comparative instrument: importance is always measured relative to what else is in the study. Changing the item set changes the ruler. Equating methods can help, but they are approximations — and it is important to communicate that limitation clearly to stakeholders who want to conclude that "benefit X is declining."
