# Simpson's Paradox in Your A/B Test

## What's happening: Simpson's Paradox

You've encountered **Simpson's Paradox** — one of the most important traps in applied causal inference. A trend (positive effect overall) reverses when you slice the data by a third variable (negative effect in both mobile and desktop segments). This is not a measurement error or a bug in your analysis pipeline. It is a structural phenomenon, and the DAG tells you exactly how to resolve it.

## Why this is mathematically possible

The key is **unequal segment representation across treatment arms**. Here is a concrete illustration:

Suppose mobile users convert at 5% base rate and desktop users convert at 25% base rate. Now suppose the new feature was shown more heavily to desktop users in the treatment group than in the control group (a common occurrence when randomization is stratified imperfectly, or when one segment adopted the new feature disproportionately during rollout).

| Group | Segment | N control | Conv% control | N treatment | Conv% treatment | Effect |
|-------|---------|-----------|---------------|-------------|-----------------|--------|
| Control | Mobile | 900 | 5% | 100 | 4% | -1% |
| Control | Desktop | 100 | 25% | 900 | 24% | -1% |
| **Aggregate** | All | 1000 | ~7.5% | 1000 | ~22.0% | **+14.5%** |

In this illustration, the treatment group is dominated by high-converting desktop users even though the feature hurt both segments individually. The aggregate estimate mixes two populations with radically different base rates, weighted differently across arms. The overall number is a composition artifact.

In your real numbers, the magnitude is smaller (+2.1% overall vs. negative within both segments), but the mechanism is the same: **the mobile/desktop mix differs between your control and treatment groups**, and mobile and desktop users have meaningfully different baseline conversion rates.

## Step 1: Name the rung

Your question is on **Rung 2 (Intervention)**: "What does the new feature do to conversion if we deploy it?" This is not a correlation question. You have an A/B test, so randomization is your identification strategy — but Simpson's Paradox reveals that your randomization may not be clean with respect to user segment.

## Step 2: Sketch the DAG

```
Segment (mobile vs desktop)
     |           |
     v           v
  Treatment --> Conversion
  Assignment
```

More precisely:

```
   Segment
   /      \
  v        v
Treatment --> Conversion
```

If **Segment** affects both which arm a user lands in (treatment vs. control) and conversion rate, Segment is a **confounder** — it sits in a fork position relative to Treatment and Conversion:

```
Segment --> Treatment Assignment
Segment --> Conversion
Treatment --> Conversion  (the causal effect you want)
```

A confounder in a fork structure creates a spurious correlation between Treatment and Conversion in the aggregate data. The DAG prescribes exactly one remedy: **condition on Segment** (i.e., look within each segment), which closes the back-door path through Segment.

## Step 3: Identify the structure — confounder, not mediator

This is the critical structural question, and it determines which result to trust.

**Case A: Segment is a confounder (fork)**
- Segment → Treatment Assignment and Segment → Conversion
- The mobile/desktop split is unequal across your treatment and control arms
- The aggregate +2.1% is inflated (or the overall direction is wrong) because it conflates the treatment effect with the segment composition difference
- **The segment-level estimates (negative in both) are correct. The aggregate is misleading.**
- Action: report the segment-level effects. Run a randomization check immediately (see below).

**Case B: Segment is not confounding the randomization (assignment is truly balanced)**
- If your randomization was perfect — equal proportions of mobile/desktop in treatment and control — then Segment cannot be creating Simpson's Paradox through unequal assignment
- In this case the paradox would require an unusual composition of segment sizes, and you would want to verify your data pipeline (are you measuring conversion correctly across both segments and aggregates?)
- This case is much less common when the paradox is this stark

**The near-certain diagnosis for a real A/B test showing this pattern: Case A.** Check it immediately.

## Step 4: The diagnostic — randomization check

Run this now:

```
% Mobile users in CONTROL group
% Mobile users in TREATMENT group
```

If these numbers differ meaningfully (even a few percentage points), you have confirmed confounding. Mobile and desktop users have different base conversion rates, so unequal segment allocation across arms creates exactly the artifact you're seeing.

Also check:

- Absolute N of mobile vs. desktop users in each arm
- Baseline (pre-experiment) conversion rates by segment — if desktop converts at, say, 4x the rate of mobile, even a small imbalance in segment allocation is enough to produce a large aggregate distortion

## Step 5: Which result should you trust?

**The segment-level results.** Here is why.

Under back-door adjustment, the correct causal estimate of the treatment effect is obtained by conditioning on the confounder (Segment) and then averaging over the population distribution of Segment. The formula is:

```
P(Conversion | do(Treatment)) = 
  P(Conv | Treatment, Mobile) * P(Mobile) + 
  P(Conv | Treatment, Desktop) * P(Desktop)
```

where P(Mobile) and P(Desktop) are the **true population proportions**, not the distorted proportions in your experiment arms.

The aggregate A/B test number implicitly uses the weighted average of segment proportions *as they appeared in your experiment*, which — if treatment and control had different segment mixes — is not the population distribution. It is the confounded distribution.

The segment-level numbers are the inputs you need. The aggregate number from this experiment is not trustworthy.

**However**: "the segment-level effect is negative" is your answer only for the effect *within each segment*. The overall treatment effect you would expect at rollout depends on your actual user base's segment composition. If your real users are 70% desktop, the rollout effect would be a weighted average of the two segment effects — still negative in both, so still negative overall. The positive aggregate number from the experiment was a mirage.

## Step 6: What to do

**Immediate steps:**

1. **Run the randomization check.** Confirm the mobile/desktop split differs across arms. This is table stakes before interpreting any A/B test, and it's especially critical when the overall and segment results disagree.

2. **Compute the correct aggregate effect** using back-door adjustment:
   - Take the segment-specific effects (mobile effect, desktop effect)
   - Weight them by your real-world population's segment mix (not the experiment's mix)
   - This is the valid estimate of the average treatment effect (ATE) at rollout

3. **Investigate why randomization was imbalanced.** Common causes:
   - Treatment was rolled out on a platform that skewed toward one device type
   - Experiment assignment used a key that correlated with device (e.g., device ID vs. user ID)
   - A/B traffic routing was misconfigured

4. **Do not ship based on the +2.1% aggregate number.** If the feature is negative for both mobile and desktop users, it is harmful. The positive aggregate is a statistical artifact of who ended up in which arm.

**For the future:**

Stratified randomization (ensuring equal proportions of mobile and desktop users in each arm) prevents this class of problem. If the experiment is already running, post-stratification weighting during analysis can correct for the imbalance.

## Summary

| Result | Interpretation | Trust? |
|--------|---------------|--------|
| +2.1% overall | Confounded by unequal segment allocation across arms — likely a mirage | No |
| Negative in mobile | Within-segment effect, not contaminated by composition | Yes |
| Negative in desktop | Within-segment effect, not contaminated by composition | Yes |

The feature appears to hurt conversion. The DAG is unambiguous: Segment is a confounder, segment-level results close the back-door path, and the aggregate result does not. Trust the disaggregated numbers, validate with a randomization check, and compute the population-weighted effect before any rollout decision.
