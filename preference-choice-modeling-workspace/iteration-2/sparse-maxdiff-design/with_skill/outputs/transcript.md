# Reasoning Transcript

## Task
Design a sparse MaxDiff for 75 items: recommend items per set, showings per item, and sample size.

---

## Step 1: Method confirmation

The task is to prioritize 75 items on a single dimension (importance/appeal). This is a clear MaxDiff use case — the skill flags this explicitly: "Prioritize a long list of features/messages/benefits on a single dimension → MaxDiff (sparse if k > ~20–25)."

At k = 75, this is deep into sparse territory. The skill's item-count guidance specifies: "31–60: sparse MaxDiff territory" and "61–150: sparse MaxDiff or Bandit MaxDiff." At 75 items, sparse MaxDiff is the correct design. Bandit MaxDiff is only appropriate if the goal is top-K identification; the task asks for a general prioritization, so a standard sparse design is preferred.

---

## Step 2: Items per set (m)

The skill/reference does not mandate a specific m, but the standard in the field and the examples used throughout the reference are m = 4 or m = 5. The reference notes the respondent burden ceiling in terms of sets, not items per set, but consistently uses m = 4 in worked examples for feature lists.

Decision: m = 4 for a 75-item feature list. This is the default most appropriate for lists with any descriptive context per feature. m = 5 is only sensible for very short labels. Going below m = 4 loses precision; going above m = 6 increases cognitive noise on the worst-pick.

---

## Step 3: Per-respondent block size and sets

The reference states:
- Respondent burden ceiling: ~12–15 sets, degradation at 18+
- Individual-level estimation floor: 3 showings per item per respondent
- Formula: `sets = (items_per_respondent × r) / m`

Working out options:
- 20 items/respondent × 3 showings / 4 items per set = 15 sets → at the ceiling, feasible
- 16 items/respondent × 3 showings / 4 items per set = 12 sets → comfortable
- 24 items/respondent × 3 showings / 4 items per set = 18 sets → too long, risk of quality degradation

The reference explicitly recommends that per-respondent blocks of 20 items × 15 sets is feasible (same worked example for k=60 is cited at 15 sets), and notes that 4–5 showings per item can be achieved by expanding to 24 items at 18 sets — but recommends against 18 sets because of respondent fatigue.

Primary recommendation: 20 items per respondent, 15 sets. Fallback if burden is a concern: 16 items, 12 sets, compensate with larger n.

---

## Step 4: Population-level showings and precision

Using the formula `r_pop = (n × s × m) / k`:
- With k=75, m=4, s=15: r_pop = n × 60 / 75 = 0.8n
- At n=500: r_pop = 400 per item

The reference gives SE formula: `SE_i ≈ C / sqrt(r_pop)` where C ≈ 8–15 for 0–100 rescaled scores (mid-range C = 12 used for illustration).

Computing SE at different n levels to build the table in the response, then back-calculating the distinguishable gap as approximately 2×SE (to distinguish items at p ≈ 0.05 two-sided, need a gap of roughly 2× the SE).

This is consistent with the reference's worked examples: "n = 200: SE ≈ 4–5 points on 0–100" and "n = 500: SE ≈ 2.5–3 points on 0–100" — though those are for k=20 with r=3, which gives r_pop = 600 at n=200. Adjusting for r_pop = 160 at n=200 for k=75 gives a slightly larger SE, which is reflected in the table.

---

## Step 5: Sample size guidance

The skill explicitly says: "whenever the user asks 'how many respondents do I need,' resist quoting a single number. Ask: (1) smallest gap between items to detect, (2) subgroup readout, (3) aggregate vs. individual-level."

The response addresses all three in the "answer these questions first" framing before giving a range. The final recommendation (n = 500 solid default, 600–750 if middle-of-list rank order matters) is grounded in the SE table, not a platform floor.

The Sawtooth n ≥ 300 floor is intentionally not cited as a target — consistent with skill instruction: "Do not cite Sawtooth's n ≥ 300 floor — it is a floor of the industry, not a target for your study."

---

## Step 6: Design construction

The reference distinguishes random sparse from block designs: "For k up to ~80, a well-constructed block design beats random sparse by a meaningful margin." At k = 75, this is directly applicable — recommend structured block design. Co-occurrence coverage check (every item co-occurs with every other at least 2–3 times) is lifted directly from the reference.

---

## Step 7: Anchoring

The skill contains a specific trigger: "whenever the user mentions 'importance'... confirm anchoring is in the plan before going further. Unanchored MaxDiff cannot support absolute claims."

The task says "prioritize" and "feature ideas" — this is an importance judgment. Anchoring is flagged as required. The reference recommends direct binary anchor as the default for most studies (dual-response anchor is for evaluative/attitude statements). A feature prioritization study uses the direct binary anchor.

---

## Summary of key design choices and their grounding

| Choice | Value | Grounded in |
|---|---|---|
| Sparse not full | Yes | k=75 >> 30-item threshold for sparse |
| m = 4 | 4 items/set | Standard for feature lists; reference worked examples |
| Per-respondent block | 20 items | Balances 15-set ceiling and 3 showings/item floor |
| Sets per respondent | 15 | Derived from block × showings / m |
| Fallback design | 16 items, 12 sets | For burden-sensitive fielding contexts |
| n = 500 default | 500 | SE ≈ 2 pts on 0–100, grounded in r_pop calculation |
| Structured block design | Yes | Reference: outperforms random sparse for k ≤ ~80 |
| Anchoring | Direct binary | Required for any absolute importance claim |
| Estimation | HB | Reference: aggregate logit almost never correct |
