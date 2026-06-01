# Ranking 30 Product Benefits by Importance

## Recommended Approach: MaxDiff (Maximum Difference Scaling)

For ranking 30 items by importance, **MaxDiff (Best-Worst Scaling, Case 1)** is the gold-standard method. It is far superior to simple rating scales or direct ranking tasks for a list this long.

### Why MaxDiff?

- **Direct ranking of 30 items is cognitively overwhelming.** Respondents cannot reliably rank 30 options in a single pass. MaxDiff breaks the task into a series of small, manageable choice sets.
- **Rating scales suffer from scale-use bias.** Many respondents rate everything 4–5 out of 5, making it impossible to differentiate. MaxDiff forces trade-offs.
- **MaxDiff produces interval-level scores** (not just ordinal ranks), so you can say "Benefit A is twice as important as Benefit B."
- **The data supports individual-level analysis** via Hierarchical Bayes (HB), giving you robust scores even per-respondent segment.

### How MaxDiff Works

Respondents see a series of sets, each showing a small subset of items (typically 4–5 per set). For each set, they select the **most** and **least** important item. The task repeats across many sets until all items have been seen multiple times.

The resulting "best-worst" choice counts are converted into utility scores (importance weights) using either:
- **Aggregate logit** (simple, fast, good for overall ranking)
- **Hierarchical Bayes** (preferred; produces individual-level scores for segmentation)

Scores are typically rescaled to a 0–100 probability scale for easy interpretation.

### Design for 30 Items

A sound design for 30 items typically uses:
- **Set size:** 5 items per set
- **Appearances per item:** Each item should appear approximately 3–4 times across the survey
- **Number of sets:** 18–24 sets per respondent is common for 30 items at 5 per set with ~3 appearances each

A rough formula: `sets ≈ (items × appearances) / set_size` = (30 × 3) / 5 = **18 sets minimum**. Most practitioners use 20–24 sets to achieve 4 appearances per item for more reliable estimates.

---

## Sample Size Guidelines

### Rule of Thumb

For MaxDiff with 30 items and aggregate-level analysis:

| Goal | Approximate N |
|---|---|
| Stable aggregate ranking only | 150–200 |
| Segment comparisons (2–3 segments) | 300–400 total (100–150 per segment) |
| Individual-level HB scores for segmentation | 300–500 |
| High-stakes decisions / fine item discrimination | 400–600 |

**A practical starting point: 200–300 respondents** for overall priority ranking without heavy segmentation needs.

### Why These Numbers?

- Each respondent completes ~20 sets, each providing 2 observations (best + worst), yielding roughly 40 data points per person.
- At N=200, you have ~8,000 observations total—sufficient for stable aggregate logit estimates across 30 items.
- HB estimation borrows strength across respondents, so individual-level scores become reliable with as few as 200–300 completes, though 400+ is safer for heterogeneous populations.

### Common Pitfalls to Avoid

1. **Don't use a simple importance rating scale** (e.g., "Rate each of 30 items 1–10"). Response biases make discrimination near-impossible.
2. **Don't use a Q-sort or drag-and-drop rank of all 30** unless your platform is excellent—respondents drop out or rank carelessly.
3. **Don't over-segment with small N.** If you want to compare 4 customer personas, you need ~150 per segment, so ~600 total.
4. **Pilot the design.** Check average completion time (target: under 12 minutes) and attention-check pass rates before full launch.

---

## Summary Recommendation

| Parameter | Recommendation |
|---|---|
| Method | MaxDiff (Best-Worst Scaling, Case 1) |
| Set size | 5 items per set |
| Sets per respondent | 20–24 |
| Item appearances | ~3–4 per item |
| Analysis | Hierarchical Bayes or aggregate logit |
| Sample size (overall ranking) | 200–300 |
| Sample size (2–3 segment comparisons) | 400–600 |

This approach will give your messaging team a defensible, discriminating rank order of all 30 benefits with clear separation between the top, middle, and bottom tiers.
