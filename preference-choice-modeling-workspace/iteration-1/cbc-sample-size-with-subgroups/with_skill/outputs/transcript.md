# Transcript

## User

Planning a CBC for a new pricing tier. 6 attributes (brand, price, 4 features). Need to compare enterprise vs. SMB segments (roughly 50/50 in our population). What's the right sample size?

## Assistant

# CBC Sample Size for Enterprise vs. SMB Subgroup Comparison

## Design parameters

Six attributes is well within the comfortable range for full-profile CBC (the ceiling before non-attendance becomes a structural problem is around 8). With brand, price, and 4 feature attributes, no partial-profile or ACBC is needed — standard full-profile CBC is the right call.

Recommended design parameters:

- **Tasks per respondent (t):** 12
- **Alternatives per task (a):** 3 (plus a dual-response None)
- **Attributes:** 6
- **Largest number of levels on any one attribute (c):** assume 5 for price; verify once levels are finalized

## Deriving sample size from precision, not a rule

There are three constraints that need to drive the number. Work through each in turn.

### Constraint 1: Per-respondent stability for HB

For stable individual-level utilities under HB, you need:

```
t × a ≥ 30
```

At t = 12 and a = 3: 12 × 3 = 36. That threshold is met. If you drop to t = 10, you're at 30 — borderline. Keep t ≥ 12.

### Constraint 2: Orme floor (sanity check, not the binding constraint)

```
(n × t × a) / c ≥ 500
```

With t = 12, a = 3, c = 5:

```
(n × 12 × 3) / 5 ≥ 500
n ≥ 70
```

The Orme floor is trivially satisfied by any realistic sample. It is not the binding constraint. Do not cite it to stakeholders as a justification for n.

### Constraint 3: Simulator precision

The thing you actually care about: can the simulator distinguish enterprise preferences from SMB preferences, and can it detect meaningful share differences within each segment?

The SE on a simulated share scales as approximately `1 / sqrt(n_segment)`. At a 50/50 split:

| Overall n | n per segment | Approx SE on simulated share |
|---|---|---|
| 400 | 200 | 3–5 pp |
| 600 | 300 | 2.5–4 pp |
| 800 | 400 | 2–3 pp |
| 1,000 | 500 | 1.5–2.5 pp |
| 1,200 | 600 | ~1.5–2 pp |

Ask: what is the smallest share difference between enterprise and SMB that your stakeholder needs to act on? If the decision is "does enterprise price sensitivity differ materially from SMB," a 5 pp difference in share response to a price change is likely the minimum actionable signal. At n = 800 (400 per segment), you're at 2–3 pp SE — able to detect a 5–6 pp difference with reasonable confidence. At n = 600 (300 per segment), the 95% CI on a segment share is roughly ±5–8 pp, which means even a 10 pp segment gap is ambiguous.

### Constraint 4: Subgroup minimum for clean HB readout

A practical floor for clean segment-level HB utilities is n = 200 per segment. At 50/50, that's an overall n of 400. That's a hard floor, not a target — HB will run but the posterior draws will be noisy and segment comparisons will have wide CIs.

A comfortable floor for publishable or decision-grade segment analysis is n = 300–400 per segment.

## Recommendation

**Target n = 800–1,000 total (400–500 per segment).**

This is driven by simulator precision, not the Orme floor or any platform default.

- At n = 800: each segment has ~400 respondents. Simulated shares have SEs of roughly 2–3 pp. You can reliably distinguish segment differences of ~6 pp or larger. For a pricing tier study, this is usually adequate — if enterprise and SMB price thresholds differ by less than 6 pp in simulated share, that difference probably doesn't change the product decision anyway.
- At n = 1,000: each segment has ~500. SEs drop to ~1.5–2.5 pp. More comfortable if the stakeholder expects tight segment differences or wants to run multiple simulator scenarios with confidence.
- Below n = 600 (300 per segment): the analysis is exploratory. You can report directional segment differences but cannot support confident pricing decisions based on them.

If budget forces a number below 800, quantify the cost explicitly before fielding: "At n = 600, we can detect segment differences ≥ 8–10 pp with confidence. Smaller differences will be directional only."

## Design considerations that affect sample efficiency

A few things to confirm before fielding that will materially affect whether n = 800 is enough:

1. **Price levels and coding**: if price has 6+ levels, treat it as piecewise-linear, not categorical. Categorical price with 6 levels adds parameters and requires more observations per level to estimate cleanly. If you can constrain to 4–5 price points, do it.

2. **Prohibitions**: if brand × price combinations will be prohibited (e.g., a premium brand cannot appear at the lowest price), check the design's relative D-efficiency after applying them. Prohibitions that drop D-efficiency below 85% effectively require you to increase n to compensate.

3. **Balance on the covariates you care about**: if enterprise/SMB split is based on a screener question, verify it before analysis. A self-reported 50/50 that comes back 65/35 in the data needs to be treated as a 35% minority segment — and that changes the precision calculation.

4. **Dual-response None**: use it. It distinguishes "I'd choose A over B and C in the scenario" from "I'd actually purchase this." For a pricing tier study where the question is conversion, not just relative preference, this matters for the simulator's validity.

## Summary

| Parameter | Value | Rationale |
|---|---|---|
| Tasks per respondent | 12 | HB stability: t × a = 36 ≥ 30 |
| Alternatives per task | 3 + dual-response None | Standard; none adds realism |
| Attributes | 6 | Within full-profile range; no ACBC needed |
| **Recommended n** | **800–1,000** | Driven by segment-level simulator precision |
| Hard floor | 600 | Below this, segment analysis is exploratory only |
| Binding constraint | Simulator precision at segment level, not Orme floor |
