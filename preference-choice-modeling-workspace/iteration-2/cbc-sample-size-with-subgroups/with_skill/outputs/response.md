# CBC Sample Size for Pricing Tier Study with Enterprise vs. SMB Subgroups

## Study parameters as stated

- 6 attributes: brand, price, 4 features
- 2 subgroups: enterprise and SMB, roughly 50/50 in the population
- Goal: compare preferences and simulator outputs across segments

---

## The subgroup constraint drives this, not the aggregate floor

With a 50/50 split, you need n ≥ 200 per segment for clean HB-driven individual-level utility estimation and stable subgroup simulator output. That puts the **aggregate floor at n = 400** from subgroup requirements alone. But 400 is tight — read why below.

The right way to work through this is to ask three questions in order:

1. What needs to be precise? (Subgroup differences in part-worths, or shared-preference shares per segment?)
2. How precise? (What's the smallest meaningful share difference between segments?)
3. What design do I have? (Tasks × alternatives determines per-respondent information.)

---

## Step 1: Does the per-respondent design give HB enough information?

For stable individual-level utilities, you need `t × a ≥ 30` per respondent, where `t` = tasks and `a` = alternatives per task (excluding None).

**Typical design recommendations for 6 attributes:**
- Tasks: 12 (solid for HB; 10 is borderline)
- Alternatives per task: 3 + dual-response None
- t × a = 12 × 3 = **36** — this meets the ≥ 30 threshold comfortably

If you go to 10 tasks × 3 alts = 30, that's the floor — workable but not recommended when you're running subgroup analysis.

**Recommendation: 12 tasks, 3 alternatives + dual-response None.**

---

## Step 2: Check the Orme floor (aggregate logit lower bound)

```
(n × t × a) / c ≥ 500
```

Where c = largest number of levels on any single attribute. Price typically has 4–6 levels for a pricing-tier study; call it 5 as the constraining attribute.

```
(n × 12 × 3) / 5 ≥ 500
n ≥ 500 × 5 / 36 ≈ 70
```

The Orme floor is trivially met at any reasonable sample size. It is not the binding constraint here. Do not let it set your target.

---

## Step 3: Simulator precision — what can you distinguish?

The SE on a simulated share scales as approximately `1/sqrt(n)` for the full sample, and `1/sqrt(n_segment)` within a segment.

| Overall n | n per segment (50/50) | Approx SE on simulated share per segment |
|---|---|---|
| 300 | 150 | 4–6 pp |
| 400 | 200 | 3–5 pp |
| 600 | 300 | 2.5–4 pp |
| 800 | 400 | 2–3 pp |
| 1000 | 500 | 1.5–2.5 pp |

If you need to say "Enterprise segment prefers Plan A over Plan B by a meaningful margin" and expect shares around 30–40% for each plan, you need to distinguish differences of ~5–8 pp with confidence. **n = 400 per segment (overall n = 800) gives you SE ~2–3 pp per segment, which supports that claim reliably.** At n = 200 per segment (overall n = 400), you're at 3–5 pp SE — you can catch large differences (>10 pp) but not moderate ones.

---

## Step 4: Cross-segment comparison adds another consideration

If the primary deliverable is comparing enterprise vs. SMB preferences (e.g., "price sensitivity differs significantly between segments"), you need to test whether segment differences in part-worths or shares are real. The SE on a *difference* between two independent estimates is `sqrt(SE_1² + SE_2²)` — roughly 1.4× the per-segment SE.

At n = 400 per segment (SE ~2–3 pp per segment), the SE on the difference is ~3–4 pp. You can reliably distinguish segment differences of 6–8 pp or more.

---

## Recommendation

**Target n = 800, with explicit attention to segment balance.**

Reasoning:
- 400 per segment gives HB-stable individual utilities and simulator precision adequate for distinguishing meaningful differences (≥6 pp) between enterprise and SMB
- 12 tasks × 3 alternatives meets the per-respondent information threshold at each segment size
- The Orme aggregate floor is irrelevant at this sample size

**If segments are truly 50/50 in the population**, proportional sampling gets you 400 per segment at n = 800. But treat "roughly 50/50" as a fielding assumption to verify — if enterprise respondents are harder to recruit and you end up 35/65, the minority segment is n = 280 at n = 800, which tightens precision. Build in a monitoring rule: if the split drifts outside 40/60, either oversample the smaller segment or increase overall n toward 1,000.

**If you can field n = 1,000**, do it. The marginal cost of ~200 respondents buys a meaningful precision improvement on cross-segment comparisons, and this is a pricing study — pricing decisions often rest on exactly those differences.

---

## What n = 400 (total) can and cannot support

If budget caps you at n = 400:
- Aggregate readout: solid
- Per-segment utilities: very rough at n = 200/segment; HB will shrink aggressively toward the population mean, which may obscure genuine segment differences
- Simulator precision: 3–5 pp SE per segment; you can detect differences of ~10 pp but not smaller
- Cross-segment significance tests: underpowered for moderate differences

If you're capped at n = 400, widen the minimum detectable difference threshold in your reporting, or reframe the enterprise/SMB comparison as exploratory rather than confirmatory.

---

## Design checklist before fielding

1. 6 attributes is well within the full-profile CBC range (practical ceiling ~6–8). No need for partial-profile or ACBC.
2. Price: define 4–6 levels spanning the realistic pricing range for the new tier. Use categorical coding, not linear — it rarely fits for SaaS pricing.
3. None option: use dual-response None (pick best option, then confirm you'd actually buy). Especially important for enterprise, where "we'd need procurement approval" is real behavior that dual-response None captures.
4. Segment screener: identify enterprise vs. SMB at the start of the survey (company size, role, or segment self-ID), not just in analysis. HB can use segment membership as a covariate in the upper-level model to improve individual-level utility precision.
5. Check relative D-efficiency before fielding. Should be ≥ 90% with no prohibitions and 6 attributes.

---

## Bottom line

| Scenario | Total n | Notes |
|---|---|---|
| Adequate for confirmatory segment comparison | 800 | 400/segment; recommended |
| Comfortable, handles drift in segment split | 1,000 | Buffer for 40/60 drift |
| Floor for exploratory segment comparison | 600 | 300/segment; flag as exploratory |
| Not recommended for segment readout | < 400 | < 200/segment; HB unstable at subgroup level |
