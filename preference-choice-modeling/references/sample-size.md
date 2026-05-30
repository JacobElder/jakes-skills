# Sample Size Derivation for Preference & Choice Studies

The point of this reference: derive sample size from the precision you need on the *decision*, not from a rule of thumb. Quote actual numbers to stakeholders so they can see the trade-off between cost and information.

## The general framework

Three inputs drive sample size:

1. **What needs to be precise?** A single item's utility? The difference between two items? A simulated share for a hypothetical product? Subgroup differences?
2. **How precise?** What gap between estimates is the smallest you want to be able to detect with confidence?
3. **Will you read out for subgroups?** If yes, design for the smallest subgroup's precision needs, then divide by prevalence.

Sample size scales as `1/precision²` and `1/subgroup_prevalence`. Doubling precision = 4× sample. Halving subgroup size = 2× sample.

---

## MaxDiff sample size

### Single-item precision

For a balanced design with `r` showings per item per respondent, the SE on the rescaled (0–100) utility for any one item is approximately:

```
SE_i ≈ C / sqrt(n × r)
```

where C is study-dependent (typically 10–15 for rescaled scores; higher when utilities are widely spread, lower when compressed). For sparse designs, replace `r` with the per-item population showings divided by n.

### Worked examples

**Study A**: 20 items, m = 4 per set, 12 sets per respondent → r = 12 × 4 / 20 = 2.4 showings/item per respondent. Use C ≈ 12.

| n | SE on 0–100 scale | Smallest detectable difference (95% CI, two items) |
|---|---|---|
| 150 | ~6.3 | ~17 points |
| 300 | ~4.5 | ~12 points |
| 500 | ~3.5 | ~10 points |
| 1000 | ~2.5 | ~7 points |

The "smallest detectable difference" is roughly 2.8 × SE (the 95% CI half-width for a difference, accounting for correlated estimates within a study, which is somewhat less than 2 × sqrt(2) × SE).

**Study B**: 50 items, sparse design, each respondent sees 20 items with 3 showings each (so 15 sets of 4). Population r per item = (n × 20 × 3) / 50 = 1.2n. Use C ≈ 12.

| n | Pop showings per item | Approximate SE | Smallest detectable diff |
|---|---|---|---|
| 300 | 360 | ~5.8 | ~16 points |
| 600 | 720 | ~4.0 | ~11 points |
| 1000 | 1200 | ~3.0 | ~8 points |
| 1500 | 1800 | ~2.5 | ~7 points |

### Subgroup precision

If the stakeholder wants segment-level utilities, the relevant `n` is the segment's size. A segment that's 20% of the sample with overall n = 1000 has segment n = 200 → SE roughly 2× the overall.

**Decision rule**: if you need 5-point precision overall but also need it within a 25% segment, you need 4× the overall sample. That's the trade-off to put in front of the stakeholder.

---

## CBC sample size

### Orme's rule (with caveats)

For aggregate logit estimation:

```
(n × t × a) / c ≥ 500
```

where:
- n = respondents
- t = tasks per respondent
- a = alternatives per task (excluding None)
- c = largest number of analytical cells, which roughly equals the largest number of levels on any one attribute

This is a *floor*. It says "you have enough information to estimate the model" but says nothing about the precision needed for your specific decision.

### HB CBC sample size

For HB, focus on two things:

1. **Per-respondent information**: t × a ≥ 30 for stable individual-level utilities. With t = 12 and a = 3, that's 36. Good.
2. **Total observations vs. parameters**: total choices (n × t) divided by number of estimated parameters should be at least 30. For a study with 30 part-worth parameters and t = 12, that's n ≥ 75 just for stability — but precision will be poor at that level.

### Simulator precision

The thing stakeholders actually care about: how precise is the simulator's share-of-preference for a hypothetical product?

The SE on a simulated share scales as approximately `1 / sqrt(n)`. Rough magnitudes (these vary widely with the specific simulation):

| n | Approx SE on simulated share (mid-range) |
|---|---|
| 200 | 3–5 percentage points |
| 400 | 2–3 pp |
| 800 | 1.5–2 pp |
| 1600 | 1.0–1.5 pp |

So for a stakeholder wanting to distinguish "Product A gets 22% share" from "Product B gets 28% share" with confidence, n = 400 is borderline; n = 800 is comfortable.

### Subgroup CBC

For each subgroup the stakeholder wants to read out, you need enough respondents within it for HB to produce stable individual-level utilities. A practical minimum is n = 200 per subgroup for clean readout. With 3 subgroups at 30/40/30, you need overall n of ~670 minimum.

### Worked example: pricing study

Stakeholder wants to know optimal price for a new product, expects competitors at $20, $30, $40, $50. Wants to read out for two segments (enterprise vs. SMB, roughly 60/40).

- Attributes: 5 (brand, price, feature_A, feature_B, support_level). Levels: 4, 6, 3, 3, 3.
- t = 12, a = 3 + None.
- Orme floor: n × 12 × 3 / 6 ≥ 500 → n ≥ 84. Easily met.
- Per-respondent: t × a = 36 ≥ 30. Fine.
- Subgroup floor: 200 per segment → 200/0.4 = 500 minimum for SMB.
- Simulator precision target: distinguish 2 pp shares → n ≈ 800.
- Recommendation: **n = 800–1000**, with explicit SMB oversampling if their share of the sample drops below 35%.

---

## When the stakeholder won't budge on sample size

If budget caps the sample below what precision requires:

1. Quantify what you'll be able to say. "At n = 200, we can distinguish items more than 12 points apart, but ranks within 12 points will not be statistically reliable."
2. Identify the decision and check if it survives the lower precision. If the stakeholder is choosing between two items that differ by 25 points in pilot, n = 200 may be enough; if they want to rank-order 30 items in a tight distribution, it's not.
3. Push for either: bigger sample, narrower scope (fewer items / fewer subgroups), or explicit acceptance that the result will be exploratory rather than confirmatory.

Don't run an underpowered study without surfacing this. The stakeholder will read the point estimates as if they were precise regardless of what you write in the appendix.

---

## Quick reference: defaults by study type

| Study type | Default n | Notes |
|---|---|---|
| Standard CBC, 5–7 attributes, no subgroups | 400–600 | Per-respondent stability + simulator precision |
| CBC with 2–3 subgroup readouts | 800–1200 | Driven by smallest subgroup |
| ACBC | 300–500 | Adaptive design squeezes more from each respondent |
| MaxDiff, ≤25 items, no subgroups | 250–400 | Decision-dependent on required gap detection |
| Sparse MaxDiff, 30–80 items | 500–1000 | Larger to compensate for per-item exposure |
| Sparse MaxDiff, 80+ items | 800–1500 | Plan for aggregate-only readout |
| Pricing-focused CBC | 600–1000 | Price precision needs strong sample |
| Volumetric CBC | 800–1500 | Volume is noisier than share |

These are starting points, not prescriptions. Derive from precision needs whenever the stakes warrant.
