# Reasoning Transcript: CBC Sample Size with Enterprise/SMB Subgroups

## Task

User is planning a CBC for a new pricing tier. Study parameters:
- 6 attributes: brand, price, 4 features
- Subgroup comparison: enterprise vs. SMB, ~50/50 in population
- Question: what's the right sample size?

---

## Step 1: Identify the binding constraint

First question from the skill: what drives sample size — the aggregate or the subgroup?

With a 50/50 split, both segments are equal in size, which is the favorable case for subgroup work. But subgroup analysis always drives sample size more than aggregate, because precision needs to be met *within* each segment, not just overall.

From `sample-size.md`:
> "For each subgroup the stakeholder wants to read out, you need enough respondents within it for HB to produce stable individual-level utilities. A practical minimum is n = 200 per subgroup for clean readout."

With 50/50 split: to get n = 200 per segment, need overall n = 400 at minimum. But the reference notes this is a *minimum*, not a target for a pricing decision.

---

## Step 2: Evaluate per-respondent information

From `conjoint.md` section 3:
> "For HB stability, total observations per respondent matters: t × (alternatives - 1) should be ≥ 30 for solid individual-level estimation."

And from `sample-size.md`:
> "Per-respondent information: t × a ≥ 30 for stable individual-level utilities."

With standard CBC design (12 tasks, 3 alternatives + None):
- t × a = 12 × 3 = 36 ✓

This meets the threshold. Design recommendation: 12 tasks, 3 alternatives, dual-response None.

6 attributes is within the full-profile CBC comfortable range (4–6, up to 8 before non-attendance risk increases). No need for ACBC or partial-profile.

---

## Step 3: Apply the Orme floor check

From `sample-size.md`:
```
(n × t × a) / c ≥ 500
```

Where c = largest number of levels on a single attribute. Price typically 4–6 levels for a pricing study. Use c = 5 as a reasonable assumption.

```
(n × 12 × 3) / 5 ≥ 500
36n / 5 ≥ 500
n ≥ 69
```

Orme floor is ~70 respondents. Trivially met. This confirms Orme is not the binding constraint — it almost never is in a properly designed study. Not cited as the target.

---

## Step 4: Simulator precision — the decision-relevant constraint

From `sample-size.md`:
> "The SE on a simulated share scales as approximately `1 / sqrt(n)`."

For subgroup-specific simulator readout (the actual deliverable), SE scales on segment n, not overall n.

At 50/50 split and overall n:
- n = 400 → 200/segment → SE ~3–5 pp per segment
- n = 600 → 300/segment → SE ~2.5–4 pp per segment
- n = 800 → 400/segment → SE ~2–3 pp per segment
- n = 1000 → 500/segment → SE ~1.5–2.5 pp per segment

A pricing-tier CBC will likely show shares in the 20–40% range. Distinguishing "enterprise prefers Tier A" from "SMB prefers Tier B" typically requires detecting differences of 5–10 pp. At n = 200/segment, the SE is too wide to support that with confidence. At n = 400/segment, it's viable.

---

## Step 5: Cross-segment difference testing

Stakeholder's primary question is comparing enterprise vs. SMB. SE on the difference between two independent segment estimates = sqrt(SE_1² + SE_2²) ≈ 1.4 × SE_per_segment.

At n = 400/segment: SE_diff ≈ 1.4 × 2.5 ≈ 3.5 pp → minimum detectable difference (95% CI) ≈ 7 pp.
At n = 200/segment: SE_diff ≈ 1.4 × 4 ≈ 5.5 pp → minimum detectable difference ≈ 11 pp.

For a pricing study where segment differences in price sensitivity are often 5–15 pp, n = 400/segment (overall 800) is the threshold for a confirmatory claim. n = 200/segment (overall 400) limits you to detecting large differences only.

---

## Step 6: Fielding risk — segment split drift

User says "roughly 50/50." This is a fielding assumption, not a guarantee. If actual split is 40/60 and overall n = 800:
- Minority segment (40%) = 320 respondents — tighter but still viable
- SE per segment for minority ≈ 2.5–3.5 pp → still workable

If overall n = 600 and split drifts to 35/65:
- Minority segment (35%) = 210 respondents — borderline
- Flagged as risk in response

Recommendation: build in a monitoring/oversampling rule if segments drift outside 40/60.

---

## Step 7: Final recommendation

Primary recommendation: n = 800 (400/segment)

Rationale:
1. Meets HB stability minimum (≥200/segment) with meaningful margin
2. Provides simulator SE of 2–3 pp per segment — adequate for pricing decision
3. Cross-segment difference testing viable at ~7 pp minimum detectable difference
4. Buffer for segment drift

Strong secondary recommendation: n = 1,000 for a pricing study where the decision is high-stakes. The cost of 200 additional respondents is low relative to the risk of underpowered pricing conclusions.

Floor if budget-constrained: n = 600 (300/segment). Flag as exploratory for cross-segment comparison.

Hard floor: n < 400 not recommended for this study design — produces <200/segment, which is too few for clean HB-driven subgroup readout.

---

## Design notes flagged

- Dual-response None recommended for enterprise context (procurement behavior, delayed decisions)
- Segment screener at start of survey enables HB covariate on segment membership — improves individual-level utility precision
- Categorical price coding preferred over linear for SaaS pricing
- Relative D-efficiency check before fielding (target ≥90%)
- No prohibitions needed for 6 attributes unless there's a specific structural constraint (alternative-specific design preferred if brand-price combinations need to differ)
