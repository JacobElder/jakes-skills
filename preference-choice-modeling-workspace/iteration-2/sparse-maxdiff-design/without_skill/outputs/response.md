# MaxDiff Design for 75 Feature Ideas

## Overview

With 75 potential feature ideas, MaxDiff (Maximum Difference Scaling) is a strong choice. It forces respondents to make explicit best-worst tradeoffs, producing ratio-scale preference scores that rank all items. Here's how to design the study.

---

## Step 1: Items Per Set

**Recommendation: 5 items per set.**

MaxDiff sets typically range from 4 to 7 items. The tradeoff:

- **Too few (3–4):** Easy for respondents but fewer comparisons per task; less statistical information per choice.
- **Too many (6–7):** Cognitively taxing, especially with abstract feature descriptions. Quality degrades.

**5 items per set is the standard sweet spot** for product/feature prioritization work. Each task asks the respondent to pick the most and least important item from the 5, producing `(k − 1)` implicit rankings per set where k = set size.

With 5 items, each task yields effectively 4 ordered pieces of information.

---

## Step 2: Showings Per Item

**Recommendation: 3–5 showings per item across the full design.**

Each of your 75 items needs to appear enough times across the full design (across all respondents and sets) to be reliably estimated. The conventional target is **3 to 5 appearances per item per respondent** in a balanced design — but with 75 items this is infeasible within a single respondent session.

### For a large item pool like 75 items:

You have two practical design approaches:

**Option A: Sparse/Incomplete Block Design (Recommended)**
Not every respondent sees every item. Use a balanced incomplete block design (BIBD) or near-balanced design where:
- Each item appears a target number of times *in aggregate* across respondents
- Each respondent only sees a manageable subset of items (e.g., 15–20 sets × 5 items = 75–100 item-exposures per respondent, covering roughly 15–20 unique items with repetition, or up to ~75 with no repeats)

**Option B: Augmented Design**
Each respondent sees all 75 items exactly once across 15 sets of 5. This is feasible but borderline in terms of respondent burden (15 tasks is acceptable; 20+ is pushing it).

**Recommended approach for 75 items:**
- Use a **sparse design** where each respondent sees a random subset of items (e.g., 25–30 items across 5–6 sets)
- Target **3–5 showings per item in aggregate** (summed across all respondents), not per respondent
- This is estimated with hierarchical Bayes (HB) modeling, which pools information across respondents

---

## Step 3: Sets Per Respondent

**Recommendation: 12–18 sets per respondent** (targeting ~15).

At 5 items per set:
- 15 sets × 5 items = 75 item-exposures per respondent
- If each item appears once per respondent: 75 items ÷ 5 per set = **15 sets** — this is a complete coverage design
- If you want 2 showings per item: 30 sets — too many (respondent fatigue)

**15 sets is the practical ceiling for most online respondents.** For 75 items, a once-through complete design (15 sets, 5 items each) is feasible per respondent, giving you:
- Each item seen once per respondent
- Aggregate item-level data pooled across the sample

If you use a sparse design (respondents see only a subset), you can keep tasks at 10–12 per respondent, which improves data quality.

---

## Step 4: Sample Size

### Rule of thumb (aggregate-level estimation)
The standard heuristic for aggregate-level MaxDiff: **each item should appear at least 500 total times** across all completed surveys.

With 15 sets per respondent and 5 items per set:
- Each respondent generates 15 best picks + 15 worst picks = 30 choice observations
- Each of 75 items appears once per respondent in a complete design

To get **500 exposures per item:**
- 500 exposures ÷ 1 showing per respondent = **500 respondents** for aggregate analysis

### Rule of thumb (individual-level / HB estimation)
For hierarchical Bayes, the target is typically **150–300 respondents** when each respondent sees a reasonable subset of items (10–15 sets). HB borrows strength across respondents, so individual-level estimates stabilize with smaller samples than aggregate methods require.

**Practical recommendation:**
| Analysis type | Recommended n |
|---|---|
| Aggregate counts / logit | 400–600 |
| Hierarchical Bayes (HB) | 150–300 |
| Segmentation (2–3 groups) | 300–500 |

For most product prioritization use cases, **n = 200–300 with HB estimation** gives reliable item-level rank ordering with adequate precision.

---

## Summary Design Recommendation

| Parameter | Recommendation |
|---|---|
| Items per set | 5 |
| Sets per respondent | 15 (complete) or 10–12 (sparse) |
| Showings per item (per respondent) | 1 (complete) or fractional (sparse) |
| Aggregate showings per item (target) | 200–500 |
| Sample size (HB) | 200–300 |
| Sample size (aggregate logit) | 400–600 |
| Design type | Complete block (all 75 per respondent) or sparse BIBD |

---

## Design Construction Notes

- Use software like **Lighthouse Studio (Sawtooth)**, **Qualtrics MaxDiff**, or **ideally construct a BIBD** using combinatorial design tools (R packages: `AlgDesign`, `crossdes`)
- Verify **balance**: each item appears approximately equally often, and each pair of items co-appears approximately equally often (co-occurrence balance matters for HB)
- **Anchoring**: consider adding a "none/unimportant" anchor task after main MaxDiff to convert relative scores to absolute importance
- **Randomize** set order and item order within sets per respondent to control order effects

---

## Estimation

Analyze with:
1. **Counting analysis** (quick sanity check): proportion of times item chosen as "best" minus "worst"
2. **Aggregate logit** (fast, interpretable)
3. **Hierarchical Bayes** (gold standard for individual-level scores and reliable item ranking with moderate n)

HB utilities can be rescaled to **probability scores** (sum to 100 across items) or **zero-centered diffs** for easy interpretation and sharing with stakeholders.
