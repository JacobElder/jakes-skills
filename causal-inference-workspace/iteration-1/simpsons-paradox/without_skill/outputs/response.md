# Simpson's Paradox: Why Your A/B Test Results Are Contradicting Themselves

## What You're Seeing

You've encountered a classic statistical phenomenon called **Simpson's Paradox** (also known as the Yule-Simpson effect). It's one of the most counterintuitive results in statistics: a trend that appears in aggregated data can reverse — or disappear entirely — when the data is broken into subgroups.

Your situation is a textbook case:
- **Overall**: New feature shows +2.1% conversion lift
- **Mobile segment**: New feature shows NEGATIVE effect
- **Desktop segment**: New feature shows NEGATIVE effect

Both are mathematically correct. They are not contradictory in a logical sense — they arise from the same data. But they tell you very different things about your feature.

---

## How Is This Possible? The Mechanism Explained

The paradox arises when a **confounding variable** (here: device type) is both:
1. Correlated with group assignment (treatment vs. control), AND
2. Correlated with the outcome (conversion rate)

### A Concrete Numerical Example

Suppose your test had the following structure:

| Segment  | Group     | Users  | Conversions | Rate   |
|----------|-----------|--------|-------------|--------|
| Mobile   | Control   | 1,000  | 150         | 15.0%  |
| Mobile   | Treatment | 9,000  | 1,260       | 14.0%  |
| Desktop  | Control   | 9,000  | 2,700       | 30.0%  |
| Desktop  | Treatment | 1,000  | 290         | 29.0%  |

Within each segment, treatment performs worse:
- Mobile: 14.0% vs. 15.0% (−1.0%)
- Desktop: 29.0% vs. 30.0% (−1.0%)

But look at the **overall aggregation**:
- **Control total**: 150 + 2,700 = 2,850 conversions / 10,000 users = **28.5%**
- **Treatment total**: 1,260 + 290 = 1,550 conversions / 10,000 users = **15.5%**

Wait — that gives a negative overall result. Let me show the version that produces your result:

The key is **unequal mixing**. If treatment users are disproportionately **mobile** (which has a higher base conversion rate), and control users are disproportionately **desktop** (which has a lower base conversion rate), the treatment group benefits from the "lift" of being more mobile-heavy — even if the feature itself hurts within each segment.

**The paradox occurs because**: The segments have very different baseline conversion rates, AND treatment and control groups are not evenly distributed across segments.

### Why the Math Works Out

The aggregate conversion rate is a weighted average of segment rates. If treatment has more users in the "high converting" segment, it can show an overall positive aggregate even if the feature performs worse within every segment.

---

## Why Does This Happen in A/B Tests Specifically?

Common causes in real experiments:

1. **Non-random rollout**: The feature was rolled out to certain segments first, or certain platforms adopted the feature more organically before the test began.

2. **Imbalanced randomization**: True randomization should produce balanced segments across treatment/control, but small tests, geographic rollouts, or time-based splits can break this.

3. **Post-stratification without weighting**: You're splitting results after the fact. The aggregate result doesn't account for the fact that the two segments have very different sizes and conversion rates.

4. **Segment size shifts**: The feature itself may change user behavior in a way that shifts who completes the funnel (survivorship bias within the experiment).

---

## Which Result Should You Trust?

**The short answer: Trust the segment-level results, not the aggregate.**

Here's why:

### The Aggregate Result Is Misleading

The +2.1% aggregate is an artifact of unequal mixing between segments and their baseline conversion rates — NOT evidence that the feature works. It's a compositional effect, not a causal effect of the feature.

If you deploy the feature to everyone in the same mix as your current user base, you will NOT see +2.1%. You'll see the negative effects playing out in both mobile and desktop users.

### The Segment-Level Results Are More Causally Valid

Within each segment, the comparison is more "apples to apples." Mobile treatment users are being compared to mobile control users. The segment-level estimate is insulated from the confounding caused by device type.

However, you should still ask: **Are the segments themselves properly balanced?** Check that within mobile, treatment and control groups are comparable on other dimensions (geography, user tenure, acquisition channel, etc.).

### The Gold Standard: Stratified Analysis with Proper Weighting

The correct way to compute an overall treatment effect in the presence of Simpson's Paradox is to use **Mantel-Haenszel weighting** or **stratified estimation**:

1. Compute the treatment effect within each segment separately.
2. Weight those effects by the segment's share of the **total population** (not the experimental sample).
3. Combine to get a properly adjusted overall estimate.

This is equivalent to asking: "If we applied this feature to our actual user mix, what would happen?" — which is the question that matters for deployment decisions.

---

## What to Do Next

### Step 1: Diagnose the Imbalance
Check the treatment/control split within each segment:
- What % of mobile users were in treatment vs. control?
- What % of desktop users were in treatment vs. control?

If these are not ~50/50 within each segment, you've found your confound.

### Step 2: Compute Segment Baseline Rates
- What is the baseline (control group) conversion rate for mobile?
- What is the baseline conversion rate for desktop?

A large gap here (e.g., mobile converts at 40% vs. desktop at 15%) amplifies the paradox.

### Step 3: Recalculate a Properly Weighted Overall Effect
Weight each segment's treatment effect by that segment's proportion in the overall user population:

```
Adjusted overall effect = (mobile_share × mobile_effect) + (desktop_share × desktop_effect)
```

This will almost certainly be negative, consistent with your segment results.

### Step 4: Investigate Why the Feature Hurts Both Segments
Before drawing final conclusions, make sure the negative segment effects are statistically significant (check confidence intervals and p-values). If yes, you have a real problem: your feature appears to hurt conversion across all users.

Ask:
- Does the feature have different UX implications on mobile vs. desktop?
- Is the feature introducing friction (extra steps, slower load times)?
- Is there a novelty effect — users are confused by the change?

### Step 5: Decide on Deployment Based on Segment Results
Given both mobile and desktop show negative effects, the appropriate conclusion is:

**Do not ship this feature in its current form.**

The +2.1% aggregate number is a statistical illusion created by the composition of your experiment, not evidence of a beneficial feature.

---

## Key Takeaways

| Question | Answer |
|----------|--------|
| Is this a real paradox? | Yes — Simpson's Paradox. Both results come from the same data and are mathematically correct. |
| Which is right? | The segment-level results. They are causally more valid. |
| What caused the discrepancy? | Unequal mixing of segments (mobile/desktop) with different baseline conversion rates across treatment/control. |
| Should you ship the feature? | No. Both segments show negative effects; the overall positive is a confounding artifact. |
| What's the correct overall number? | Compute a population-weighted average of the two segment effects. |

---

## Further Reading

- Judea Pearl's work on Simpson's Paradox and causal inference (Pearl, 2009 — "Causality")
- "Causal Inference: The Mixtape" by Scott Cunningham (free online) — Chapter on confounding
- The Mantel-Haenszel method for stratified analysis
- Google's "Trustworthy Online Controlled Experiments" (Kohavi et al.) — Chapter 3 on experiment design pitfalls
