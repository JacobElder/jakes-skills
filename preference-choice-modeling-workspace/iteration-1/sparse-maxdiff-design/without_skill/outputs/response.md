# Designing a MaxDiff Survey for 75 Feature Ideas

MaxDiff (Maximum Difference Scaling, also called Best-Worst Scaling) is the right tool for prioritizing a large list of items. Here's how to design it for your 75 features.

---

## The Core Design Challenge

With 75 items, you cannot show all of them at once. MaxDiff works by presenting small subsets (called "choice sets" or "tasks") repeatedly, where respondents pick the best and worst option in each set. The design must ensure:

1. Every item appears enough times for reliable estimation
2. Items are efficiently balanced across respondents
3. Respondents don't get fatigued

---

## Items per Set

**Recommended: 5 items per set** (range: 4–6)

- **4 items** is safe but yields less information per task (only 1 best + 1 worst signal)
- **5 items** is the industry standard — maximizes signal without cognitive overload
- **6 items** is feasible but starts to stress respondents
- Avoid 3 (too little discrimination) or 7+ (too hard to evaluate simultaneously)

For 75 items with 5 per set, stick with k = 5.

---

## Showings per Item (Frequency)

**Target: 3–4 appearances per item per respondent**

Why this range?
- Fewer than 3 showings per item produces unreliable individual-level estimates
- More than 5 is usually unnecessary and bloats survey length
- The standard for aggregate-level (group) analysis is ≥ 3; for individual-level (HB) analysis, aim for ≥ 4

### Calculating Number of Tasks

With 75 items, 5 per set, and a target of ~3 showings per item:

```
Total exposures needed = 75 items × 3 showings = 225
Tasks per respondent = 225 ÷ 5 items per task = 45 tasks
```

45 tasks is far too many for a single respondent. This is the **sparse design problem** with large item sets.

---

## The Sparse Design Solution

Because 75 items is large, you use a **sparse (incomplete block) design**: each respondent only sees a subset of items, and coverage is achieved across respondents.

### How it works:
- Each respondent sees a manageable number of tasks (typically 15–20)
- The full item set is covered by aggregating across the respondent pool
- You need enough respondents so that every item gets ≥ 3–4 showings in total (or per segment)

### Recommended per-respondent task count: **15–20 tasks**

At 18 tasks × 5 items = 90 item exposures per respondent. With 75 items, each respondent covers 90/75 = 1.2× the item set — meaning most items appear about once per respondent, some twice.

This is fine for **aggregate analysis**. For **individual HB (hierarchical Bayes)** estimates, you'd need more tasks or accept borrowing heavily from the group prior.

---

## Sample Size

### For aggregate-level analysis (utilities at the group level):

**Minimum: 200 respondents**
**Recommended: 300–400 respondents**

At 300 respondents × 18 tasks × 5 items = 27,000 total item-level observations. Spread across 75 items, that's ~360 observations per item — well above the minimum for stable aggregate estimates.

### For hierarchical Bayes (individual-level utilities):

**Minimum: 300 respondents**, but the more sparse the design, the more HB relies on the group prior rather than individual data. With 75 items and only ~18 tasks per respondent, individual estimates will be relatively imprecise.

**Practical recommendation for HB with 75 items: 400–500 respondents**

### For subgroup analysis:

If you want to compare segments (e.g., enterprise vs. SMB customers), ensure each subgroup has at least 150–200 respondents. Plan your total N accordingly.

---

## Design Summary (Recommended Configuration)

| Parameter | Value |
|---|---|
| Total items | 75 |
| Items per set | 5 |
| Tasks per respondent | 18 |
| Item coverage per respondent | ~60 of 75 items (each appears ~1.2×) |
| Design type | Sparse incomplete block (balanced) |
| Sample size (aggregate analysis) | 300–400 |
| Sample size (HB / segmentation) | 400–500 |
| Total item observations | ~27,000–45,000 |

---

## Practical Design Steps

1. **Generate a balanced incomplete block design (BIBD)** or use near-BIBD for 75 items, 5 per set, 18 tasks per respondent. Software options:
   - Sawtooth Software (industry standard for MaxDiff)
   - R packages: `support.BWS`, `idefix`
   - Python: manual combinatorial design or Sawtooth-exported designs

2. **Check orthogonality**: Items should co-appear with each other approximately equally often. Avoid items always appearing together (confounded pairs).

3. **Randomize set order** across respondents to prevent order effects.

4. **Pilot test**: Run 20–30 respondents first. Check:
   - Survey completion time (target: 10–15 minutes)
   - Item non-response rates
   - Variance in choices (if respondents always pick the same item type as best, check for bias)

5. **Analysis approach**:
   - Aggregate: multinomial logit (MNL) on pooled data
   - Individual: hierarchical Bayes (HB) multinomial logit
   - Output: scaled utility scores (often zero-centered, or converted to probability shares)

---

## Common Pitfalls to Avoid

- **Showing all 75 items in a single blocked design to one respondent**: Fatigue destroys data quality after ~25 tasks
- **Too few items per set (k=3)**: Reduces statistical efficiency; you get fewer paired comparisons per task
- **Skipping balance checks**: If some items appear far more than others, their utilities will have different standard errors
- **Under-sampling for HB**: With sparse designs, HB estimates regress heavily to the mean — a feature-level artifact, not a real finding
- **Ignoring item grouping**: If your 75 features cluster into categories (e.g., performance, UX, integrations), consider a stratified design where sets are drawn proportionally from categories to avoid all-performance or all-UX sets
