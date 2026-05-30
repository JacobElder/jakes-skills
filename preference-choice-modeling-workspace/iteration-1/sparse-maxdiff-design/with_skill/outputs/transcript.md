# Reasoning Transcript

## Task
Design a sparse MaxDiff for 75 feature items: determine items per set, showings per item, and sample size.

---

## Step 1: Method confirmation

75 items → sparse MaxDiff is the right method. The skill's item-count guidance says:
- ≤15: comfortable full design
- 16–30: full design feasible but burdensome
- 31–60: sparse MaxDiff territory
- 61–150: sparse MaxDiff or Bandit MaxDiff

75 falls in the 61–150 range. Full design is infeasible: at m=4 items per set, r=5 showings per item, a full design would need s = k × r / m = 75 × 5 / 4 = 93.75 sets per respondent. The practical ceiling from maxdiff.md is ~15–18 sets before quality degrades. So sparse is necessary.

Bandit MaxDiff was considered and rejected: Bandit is appropriate when the goal is "identify top-K" but biased for producing full importance rankings. The task asks for prioritization of all 75, so a full rank-order is the deliverable. Standard sparse with HB is the right design.

---

## Step 2: Items per set

Options considered: m=4 vs m=5.

Arguments for m=5: more information per set (more paired comparisons), slightly fewer sets needed for the same showings.

Arguments for m=4: lower cognitive load per set, better worst-pick quality (the "worst" pick is disproportionately noisy at larger set sizes), standard for large-k studies.

Decision: m=4. With k=75 and a sparse design where respondents are evaluating items they may be less familiar with (feature ideas), keeping set complexity low is worth the modest increase in sets needed.

---

## Step 3: Per-respondent scope

Key constraints from maxdiff.md:
1. Each respondent needs ≥3 showings per item for individual-level HB estimation to be meaningful. Below 3, HB shrinks the individual estimate toward the population prior — the person's data barely moves the needle.
2. Respondent burden ceiling: ~15–18 sets before quality degrades.

Working the math:
- Set sets per respondent = 18 (near ceiling; scalable to 15 for lower-engagement audiences).
- Total item-observations per respondent = 18 sets × 4 items/set = 72.
- Target showings per item per respondent = 3 (minimum viable).
- Items per respondent = 72 / 3 = 24.

Each respondent sees 24 of 75 items, 3 times each, across 18 sets.

Alternative considered: 15 sets / 20 items / 3 showings each. This is valid but requires proportionally more respondents to achieve the same population showings per item. The response notes this option for lower-engagement audiences.

---

## Step 4: Design structure

The skill explicitly distinguishes random sparse (Sawtooth "Express MaxDiff") from block/BIBD designs. For k up to ~80, a well-constructed block design beats random sparse by a meaningful margin.

Key requirement from maxdiff.md: every item pair should co-occur at least 2–3 times across the population. Pairs that never co-occur are identified only through chains; HB shrinkage will compress their relative utilities.

At n=800 with 24 items per respondent:
- Each respondent covers 24/75 = 32% of the item pool.
- Any two specific items are both in a respondent's set with probability (C(73,22)/C(75,24)) approximately — roughly (24×23)/(75×74) ≈ 0.099, so expected co-occurrences per respondent pair is ~0.10. At n=800, expected co-occurrences per pair ≈ 80. That's well above the minimum but this is at the respondent level — within a set, pairs co-occur less frequently. A proper block design ensures systematic coverage rather than relying on probabilistic coverage.

Recommendation: use Sawtooth's sparse design optimizer, generate and check the co-occurrence matrix, accept only if minimum pairwise co-occurrence ≥ 2 (preferably 5+) at the target n.

---

## Step 5: Sample size derivation

From maxdiff.md and sample-size.md:

```
SE_i ≈ C / sqrt(showings_per_item_in_population)
```

C ≈ 12 (typical for 0–100 rescaled utilities, moderate utility spread).

Population showings per item = (n × items_per_respondent × showings_per_item_per_respondent) / k
= (n × 24 × 3) / 75
= 72n / 75
≈ 0.96 × n

So each additional respondent adds ~0.96 showings per item at the population level. This is essentially 1:1.

Built the table:
- n=400: ~384 showings → SE ≈ 12/√384 ≈ 6.1 → detectable diff ≈ 17 pts
- n=600: ~576 showings → SE ≈ 12/√576 = 12/24 = 5.0 → ~14 pts
- n=800: ~768 showings → SE ≈ 12/√768 ≈ 4.3 → ~12 pts
- n=1000: ~960 showings → SE ≈ 12/√960 ≈ 3.9 → ~11 pts
- n=1200: ~1152 showings → SE ≈ 12/√1152 ≈ 3.5 → ~10 pts

The "detectable difference" formula from sample-size.md: roughly 2.8 × SE (95% CI for a difference between two items, accounting for within-study correlation being somewhat less than 2√2 × SE).

Default recommendation: n=800. Rationale: distinguishes items ~12 points apart at 95% CI, which is a meaningful threshold for prioritization. Items closer than 12 points should be treated as tied; this is reasonable for a 75-item list where the goal is to identify high-priority clusters, not strict rank-ordering.

The skill's quick reference table confirms: "Sparse MaxDiff, 30–80 items → 500–1,000." n=800 is comfortably within this range.

Subgroup note: the response asks the user to specify subgroup prevalence before computing subgroup-adjusted n. This follows the skill's explicit instruction to ask about subgroups before quoting a number.

---

## Step 6: Anchoring

The skill is explicit: unanchored MaxDiff misleads stakeholders. With 75 items, the stakeholder will interpret bottom-ranked features as "unimportant" — which is only valid with an anchor.

Direct binary anchor is the recommended default from maxdiff.md: ask respondents post-MaxDiff to flag items meeting a threshold. This produces a 0-point for rescaling.

Dual-response anchor was considered but rejected: it adds complexity to an already-long survey (18 sets), and the direct binary anchor is the recommended default when anchoring feels natural as a standalone question.

---

## Quality control notes

Added from maxdiff.md Section 8:
- Response time filtering (bottom 5–10% median set completion time)
- Straightlining / position bias detection
- Trap set with obvious dominant item
- HB fit statistic — drop bottom 5–10%, cross-check with response time before dropping

HB iterations: the default 10,000 in some platforms is explicitly flagged as too few for sparse designs. Recommended ≥100,000 after burn-in. Also flag checking the between-respondent covariance matrix convergence, which platforms often skip.

---

## Key numbers summary

| Parameter | Value | Source |
|---|---|---|
| m (items per set) | 4 | Cognitive load ceiling; worst-pick quality |
| Items per respondent | 24 | 18 sets × 4 / 3 showings per item |
| Sets per respondent | 18 | Respondent burden ceiling |
| Showings per item per respondent | 3 | HB minimum viable for individual-level estimation |
| Default n | 800 | ~12-pt detectable gap; within 500–1000 range for 30–80 items |
| Population showings per item at n=800 | ~768 | 0.96 × 800 |
| SE at n=800 (0–100 scale) | ~4.3 pts | 12/√768 |
