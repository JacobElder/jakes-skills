# Simpson's Paradox in Your A/B Test

## What You're Seeing is Real — and Has a Name

This is a classic instance of **Simpson's Paradox**: a statistical phenomenon where a trend appears in combined data but reverses (or disappears) when the data is broken into subgroups. Your data is not corrupted or mistaken — this is a genuine mathematical possibility.

---

## How Is This Possible?

The key is a **confounding variable**: the mix of mobile vs. desktop users is different between your control and treatment groups.

Here's a concrete numerical example that mirrors your situation:

### Control Group
| Segment  | Users | Conversions | Rate  |
|----------|-------|-------------|-------|
| Mobile   | 900   | 90          | 10.0% |
| Desktop  | 100   | 50          | 50.0% |
| **Total**| **1,000** | **140** | **14.0%** |

### Treatment Group
| Segment  | Users | Conversions | Rate  |
|----------|-------|-------------|-------|
| Mobile   | 100   | 9           | 9.0%  |
| Desktop  | 900   | 432         | 48.0% |
| **Total**| **1,000** | **441** | **44.1%** |

In both segments, treatment is **worse** than control (9% < 10% for mobile; 48% < 50% for desktop). Yet the aggregate treatment rate (44.1%) is far higher than control (14.0%) — because the treatment arm happened to get far more high-converting desktop users.

Your situation is the same pattern at a smaller scale: the treatment arm had a more favorable segment composition (more desktop users), which inflated the aggregate positive result despite the feature being harmful within each segment.

### Why This Happens in Practice

The most common causes in A/B tests:
1. **Non-stratified randomization**: Assignment wasn't balanced across device type, so one arm got disproportionately more desktop (high-converting) users.
2. **Timing effects**: Mobile and desktop users visit at different times. If one arm saw more weekend traffic and desktop users skew weekend, the composition shifts.
3. **Segment-level traffic changes**: If desktop traffic grew during the test period and treatment launched slightly later, treatment would see more desktop users.

---

## Which Result Should You Trust?

**Trust the segment-level results. The aggregate result is misleading.**

### The Aggregate is Confounded

The overall +2.1% figure is not a clean measure of the feature's causal effect. It is inflated by the imbalance in segment composition across your test arms. This is not a true treatment effect — it's a composition artifact.

### The Segment-Level Results are the Causal Signal

When you hold segment constant (comparing mobile control vs. mobile treatment, and desktop control vs. desktop treatment), you're doing a fair apples-to-apples comparison. If the effect is **negative in both segments**, that is your real answer: **the feature hurts conversion for both mobile and desktop users.**

### Decision Rule
- If the aggregate is positive but **all subgroups are negative**, the feature is almost certainly harmful — not beneficial.
- You should **not ship this feature** based on the aggregate number alone.
- The aggregate trend is a statistical illusion caused by unequal group composition.

---

## What To Do Next

### 1. Audit Your Randomization
Check whether mobile/desktop split was equal between control and treatment. A simple crosstab:

```python
df.groupby(['arm', 'segment']).size().unstack(fill_value=0).apply(lambda x: x / x.sum(), axis=1)
```

If the percentages differ meaningfully between arms, you have a compositional imbalance.

### 2. Run a Corrected (Stratified) Analysis
Use a weighted average of segment-level effects, weighted by the **real population proportions** — not the test arm proportions. This is the Mantel-Haenszel approach:

```
Adjusted effect = (mobile_share × mobile_effect) + (desktop_share × desktop_effect)
```

Or with regression:

```python
import statsmodels.formula.api as smf

# Logistic regression controlling for segment
model = smf.logit('converted ~ treatment + C(segment)', data=df).fit()
print(model.summary())
# The coefficient on 'treatment' is now adjusted for segment composition
```

### 3. Fix Randomization for Future Tests
Use **stratified randomization** (block on device type) so mobile/desktop ratios are guaranteed to be equal across arms:

```python
# Assign treatment within each segment
df['treatment'] = df.groupby('segment')['user_id'].transform(
    lambda x: np.random.binomial(1, 0.5, len(x))
)
```

### 4. Report Segment-Level Results as Primary
In your test readout, lead with segment effects. Flag the aggregate number as confounded. This protects the team from making the wrong ship decision.

---

## Summary

| What You Have | What It Means |
|---|---|
| +2.1% overall | Artifact of segment composition imbalance — not the true causal effect |
| Negative in mobile | Actual causal harm to mobile users |
| Negative in desktop | Actual causal harm to desktop users |
| Which to trust | **Segment-level results**, or a population-weighted average of them |

**Bottom line:** The feature likely **hurts conversion** for both mobile and desktop users. Do not ship it. The positive aggregate number is Simpson's Paradox — a real statistical phenomenon, not a data error. Investigate why segment distributions differed across arms and use stratified randomization in future tests.
