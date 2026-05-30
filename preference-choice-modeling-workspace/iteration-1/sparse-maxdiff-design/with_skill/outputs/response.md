# Designing a Sparse MaxDiff for 75 Items

75 items puts you firmly in sparse MaxDiff territory. A full design — every respondent sees every item — would require roughly 94 sets per respondent at 4 items per set with 5 showings each. Nobody finishes that. Here's how to structure it correctly.

---

## Step 1: Confirm the method is right

MaxDiff is the right call here assuming the goal is to rank-order or prioritize features on a single dimension (appeal, importance, likelihood to drive adoption). If the deliverable is "which features should we bundle in the product and at what price," that's CBC territory, not MaxDiff. Assuming it's a prioritization question, proceed.

---

## Step 2: Items per set — use 4

With 75 items, use **m = 4 items per set**.

The tradeoff: more items per set (5–6) increases information per task but raises cognitive load and degrades worst-pick quality — respondents start pattern-responding on the "worst" choice especially. With a large-k sparse design, you're already asking respondents to evaluate unfamiliar combinations of items. Keep the per-set cognitive load low. Four items per set is the standard for item pools in this range.

---

## Step 3: Per-respondent scope and set count

In a sparse design, each respondent sees a *subset* of the 75 items. The two constraints:

1. **Each respondent needs to see each of their assigned items at least 3–4 times** to provide information that can be distinguished from the population prior in HB estimation. Fewer than 3 showings per item per respondent means you're essentially extrapolating from the group mean for that individual — segmentation becomes unreliable.

2. **Respondent burden ceiling is roughly 15–18 sets** before quality degrades.

Working the math:

- Target **18 sets per respondent**, which is near the ceiling but feasible for a motivated B2B audience (scale back to 15 for a consumer panel).
- With m = 4 items per set and 18 sets: 72 item observations per respondent.
- Assign each respondent a **subset of 24 items** out of 75.
- Showings per item per respondent: 72 / 24 = **3 showings per item** — the minimum viable for individual-level estimation.

So the per-respondent design is: **24 items, 18 sets of 4, 3 showings per item**.

If your audience is lower-engagement (consumer panel, shorter attention), drop to 15 sets and 20 items per respondent (3 showings each). You'll need more respondents to compensate — see below.

---

## Step 4: Design structure — use a block design, not random sparse

Don't use random sparse (Sawtooth's default "Express MaxDiff" random assignment). For k = 75, construct a proper **block design**:

- Divide the 75 items into blocks. With 24 items per respondent from a pool of 75, you need at least ⌈75/24⌉ = ~4 block types (with overlap), but a well-constructed design will use more block varieties to ensure adequate co-occurrence across items.
- The key property: every pair of items should co-occur in at least **2–3 respondents' sets** across the population. If two items never appear together in any set for any respondent, their relative utility is identified only through chains — HB will pull them toward the mean and compress the real difference.

In Sawtooth, generate this as a balanced incomplete block design (BIBD) or use the built-in sparse design optimizer and check the co-occurrence matrix. Accept the design only if the minimum pairwise co-occurrence count is ≥ 2 at your target sample size.

---

## Step 5: Sample size

The key quantity is **population-level showings per item** — the total number of times each item is seen across all respondents combined. Precision scales as approximately:

```
SE_i ≈ C / sqrt(showings_per_item_in_population)
```

where C ≈ 12 for 0–100 rescaled utilities in a study with moderate utility spread.

**Population showings per item** = (n × 24 items per respondent × 3 showings per item) / 75 items = **0.96 × n**

So each additional respondent adds roughly 1 showing per item at the population level.

| n | Pop showings per item | Approx SE (0–100 scale) | Smallest detectable diff (95% CI) |
|---|---|---|---|
| 400 | 384 | ~6.1 | ~17 points |
| 600 | 576 | ~5.0 | ~14 points |
| 800 | 768 | ~4.3 | ~12 points |
| 1,000 | 960 | ~3.9 | ~11 points |
| 1,200 | 1,152 | ~3.5 | ~10 points |

**The right n depends on the decision:**

- If you need to separate clearly dominant features from clearly weak ones (gaps of 15–20+ points), **n = 500–600** is sufficient.
- If you need a reliable rank ordering through the middle of the list — distinguishing feature #30 from feature #35 — you probably can't, regardless of sample size, because those items are genuinely close. But if you need to detect 10-point gaps, **n = 800–1,000** is the range.
- If you need subgroup readouts (e.g., by user persona, company size, region), apply the subgroup multiplier. A segment at 25% prevalence that needs the same precision as the overall requires 4× the sample. Budget subgroup analysis explicitly — this is where studies silently fail.

**Default recommendation: n = 800**, assuming no subgroup readouts and a target of distinguishing items roughly 12 points apart on the rescaled scale. This gives ~768 population showings per item.

If you're doing subgroup analysis, tell me the smallest subgroup's expected prevalence and I'll recompute.

---

## Step 6: Anchoring decision

Do not report unanchored utilities to stakeholders. With 75 items, stakeholders will treat the rescaled scores as absolute importance measures and conclude the bottom-ranked features are "unimportant" — which is only valid if you have an anchor.

Use a **direct binary anchor**: after the MaxDiff sets, ask respondents to flag every item they would consider a meaningful benefit (or whatever the relevant threshold is). Rescale so the anchor is 0; items above are positive, below are negative. Report the share of items above the anchor per respondent, then the rescaled utilities.

---

## Summary

| Parameter | Value |
|---|---|
| Method | Sparse MaxDiff |
| Items (k) | 75 |
| Items per set (m) | 4 |
| Items per respondent | 24 |
| Sets per respondent | 18 |
| Showings per item per respondent | 3 |
| Design type | Block design (BIBD-derived), not random sparse |
| Recommended n (no subgroups) | 800 |
| Population showings per item at n=800 | ~768 |
| Approx SE at n=800 | ~4.3 points (0–100 scale) |
| Detectable gap at n=800, 95% CI | ~12 points |
| Anchoring | Direct binary anchor, required |
| Estimation | HB (aggregate logit is not acceptable here) |
| HB iterations | ≥100,000 after burn-in |

---

## What to watch for in execution

- **Check the co-occurrence matrix** before fielding. At n = 800, every item pair should co-occur at least 5–10 times. Pairs that co-occur fewer than 3 times will have compressed relative utilities.
- **Monitor response times**. With 18 sets, median completion should be 6–12 minutes depending on item complexity. Drop respondents completing in under 3 minutes.
- **Don't over-interpret middle ranks**. With 75 items and ~4-point SE, items ranked 30–50 are likely in a statistically indistinguishable band. Report by significance groupings, not strict rank order.
- **Run 100,000+ HB iterations**. The default 10,000 in some platforms is insufficient for sparse designs. Check the between-respondent covariance matrix convergence explicitly — platforms often only report log-likelihood.
