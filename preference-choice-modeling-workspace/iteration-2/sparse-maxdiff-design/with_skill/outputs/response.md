# Designing a Sparse MaxDiff for 75 Items

75 items is well into sparse MaxDiff territory (the boundary is roughly 30–35 items). A full design — where every respondent sees every item — would require an unreasonable number of sets per person. The right framework is sparse MaxDiff with a block design, where each respondent sees a balanced subset of items and population-level coverage is achieved across respondents.

---

## Step 1: Items per set (m)

**Use m = 4 or m = 5.** Four is the standard default for item lists; five is acceptable when items are short (single concepts or labels) and respondents can hold them all in working memory simultaneously. For 75 features described with any context, use **m = 4**.

Do not go to m = 3: precision per set drops sharply because each set yields fewer implied paired comparisons. Do not go to m = 6+: cognitive load increases, and worst-picking in particular becomes noisy when six options are visible.

---

## Step 2: Sets per respondent and showings per item (within-person)

The respondent burden ceiling for MaxDiff is roughly **12–15 sets** before response quality degrades. At 18+ sets, response time distributions collapse and worst-pick responses become patterned.

For individual-level estimation via HB, each respondent needs to see each of their assigned items at least **3 times** (3 showings per item). Fewer than 3 showings per item means that respondent's individual utilities are essentially the population prior — you cannot do meaningful segmentation from their data.

With m = 4 and a target of 3 showings per item per respondent:

```
Sets needed = (items_per_respondent × 3) / 4
```

If each respondent sees a subset of 20 items:

```
Sets = (20 × 3) / 4 = 15 sets
```

That is at the ceiling but feasible. If 15 sets is too long for your fielding context, reduce the per-respondent subset to 16 items:

```
Sets = (16 × 3) / 4 = 12 sets   ← comfortable
```

**Recommendation for 75 items:**
- Each respondent sees **20 items** (a random block assigned from the full 75)
- **15 sets** per respondent
- **3 showings per item** per respondent within their assigned block

If respondent burden is a concern, drop to 16 items / 12 sets per respondent and compensate with a slightly larger n (see Step 4).

---

## Step 3: Showings per item at the population level

Per-item precision at the population level is what determines whether you can reliably rank items and distinguish adjacent scores. The formula:

```
r_pop = (n × sets_per_respondent × m) / k
```

With k = 75, m = 4, 15 sets per respondent, and n respondents:

```
r_pop = (n × 15 × 4) / 75 = n × 0.8
```

So at n = 500, each item receives 400 population-level showings. At n = 300, each item receives 240 showings.

The approximate standard error on a rescaled (0–100) item utility:

```
SE_i ≈ C / sqrt(r_pop)
```

where C is typically 8–15 for 0–100 rescaled scores depending on the utility spread. Using C = 12 as a mid-range estimate:

| n    | r_pop per item | SE (0–100 scale) | Distinguishable gap |
|------|----------------|------------------|---------------------|
| 200  | 160            | ~0.95            | ~3–4 pts            |
| 300  | 240            | ~0.77            | ~2–3 pts            |
| 500  | 400            | ~0.60            | ~2 pts              |
| 750  | 600            | ~0.49            | ~1.5 pts            |

These are aggregate-level SEs. For reliable rank ordering of items in the middle of the distribution — where the gaps are smallest — you want items 2–3 points apart to be distinguishable, which points toward **n = 400–600**.

---

## Step 4: Recommended sample size

Before committing to a number, answer three questions:

1. **What's the smallest gap between features you would treat as a meaningful difference?** If you only care about identifying a top-10 and bottom-10, n = 300 may be enough. If you need to distinguish features that rank 25th vs. 30th, push to 600.

2. **Will you read out by subgroup?** If you need segment-level utilities (job function, user tier, whatever), multiply required n by 1/p where p is the smallest subgroup's prevalence. A 25% subgroup needs 4× the sample for the same per-item precision — meaning if n = 400 works for the aggregate, you need n = 1,600 for that subgroup to match.

3. **HB aggregate only, or individual-level segmentation?** For individual-level HB segmentation, each respondent needs at least 3 showings per item in their assigned block. The sample size floor for reliable individual utilities is largely met by the per-respondent design — but aggregate n still governs population-level precision.

**For a 75-item list with a purely aggregate or top-level segment readout:**

- Minimum viable: **n = 300** (items 5+ points apart are distinguishable)
- Solid default: **n = 500** (items ~2 points apart are distinguishable)
- Recommended if you care about rank order through the middle: **n = 600–750**

---

## Step 5: Design construction

Do not use random sparse assignment. For k = 75, a structured block design (BIBD-derived or optimized via Sawtooth's design optimization) will meaningfully outperform random assignment by reducing the maximum variance on any item pair's relative utility. Sawtooth's MaxDiff design module handles this automatically — just specify k, m, sets per respondent, and the per-respondent block size.

Key check: verify that **every item co-occurs with every other item at least 2–3 times across the population design**. If two items never appear in the same set, their relative utility is identified only through indirect chains of co-occurrence, which degrades rank-order precision on those pairs.

---

## Step 6: Anchoring — do not skip this

Unanchored MaxDiff utilities are relative: they tell you Feature A > Feature B, but not whether either feature is actually valuable in absolute terms. For a feature prioritization decision, stakeholders will almost certainly interpret the output as importance ranking (absolute), not preference ordering (relative). That interpretation requires anchoring.

**Recommended method**: direct binary anchor — after the MaxDiff sets, ask respondents to flag each item as "would be valuable to me" / "would not be valuable to me." This serves as the zero-point, so features above the anchor threshold are reported as positive and those below as negative. Lead the deliverable with share-above-anchor, not raw utilities.

---

## Summary: Recommended design parameters

| Parameter | Value | Notes |
|---|---|---|
| Items (k) | 75 | As given |
| Items per set (m) | 4 | Standard for feature lists |
| Items per respondent | 20 | Sparse block; adjust down to 16 if survey length is constrained |
| Sets per respondent | 15 | Yields 3 showings/item/respondent at block size 20 |
| Design type | Block (not random sparse) | Minimizes maximum pair-variance |
| Sample size — aggregate only | 500 | Distinguishes items ~2 pts apart on 0–100 scale |
| Sample size — with subgroups | 500 / (smallest subgroup proportion) | E.g., 2,000 for a 25% subgroup |
| Anchoring | Direct binary anchor | Required for absolute importance claims |
| Estimation | HB, not aggregate logit | Minimum 30,000 post-burn iterations |

---

## What changes if your fielding context is tighter

- **Survey must be ≤ 12 sets**: reduce per-respondent block to 16 items (12 sets × 4 items / 3 showings). Compensate with n ≥ 600 to maintain population-level precision.
- **Budget for only n = 200**: aggregate read only, no subgroup claims, and frame the output as directional — items clearly separated by 6+ points are reliable; tight middle-of-pack ranks are not.
- **Need individual-level utilities for segmentation**: 3 showings per item per respondent is the floor; do not reduce the per-respondent block below 12 items, and run HB with at least 100,000 iterations for a k = 75 sparse design.
