# IV Exclusion Restriction: Distance to Gym as an Instrument

## The Short Answer

Your colleague is right, and importantly, they're right for reasons that go beyond theoretical pedantry. The exclusion restriction for distance-to-gym is almost certainly violated in ways that are both empirically plausible and analytically consequential. Here's the diagnostic.

---

## Step 1: Name the Rung

You're asking a **rung 2 (intervention)** question: what would happen to health outcomes if we intervened on gym membership? The self-selection problem means raw observational data answers a rung 1 question (what's the association between membership and health?) instead. You've correctly identified that IV is the right tool — the question is whether your instrument is valid.

---

## Step 2: Sketch the DAG

The intended IV structure is:

```
Distance → Membership → Health
                ↑
                U (unobserved: health consciousness, income, motivation)
                ↓
              Health
```

In this DAG, Distance has no arrow directly to Health. It only reaches Health through Membership. That's the exclusion restriction. The question is whether this DAG is correct.

A more realistic DAG looks like this:

```
Distance → Membership → Health
    ↓                    ↑
    [multiple direct paths to Health, listed below]
```

---

## Step 3: Why the Exclusion Restriction Is Almost Certainly Violated

The exclusion restriction requires that distance to the nearest gym affects health **only** through gym membership. Here are several plausible direct paths that violate it:

### (a) Neighborhood Socioeconomic Sorting

Gyms locate in wealthier, safer, better-served neighborhoods. Distance to the nearest gym is a proxy for neighborhood quality — and neighborhood quality affects health through dozens of channels that have nothing to do with gym membership: air quality, proximity to fresh food, walkability, noise, access to parks, crime stress, and quality of local healthcare. A person living far from a gym is not just living far from a gym; they are likely living in a neighborhood with systematically different health infrastructure.

This is arguably the strongest violation and the hardest to dismiss.

### (b) General Physical Activity Opportunities

If you live close to a gym, you probably also live near parks, bike paths, fitness studios, and other activity infrastructure. Distance to gym is partially an index of overall access to physical activity opportunities. The instrument would then pick up the effect of the entire activity environment, not just gym membership.

### (c) Walkability and Incidental Exercise

Living in a denser, more walkable area (which correlates with gym proximity) means more incidental physical activity — walking to transit, errands on foot, etc. This is a direct effect of the neighborhood type that the instrument captures, not an effect mediated through gym membership.

### (d) Access to Health-Promoting Retail and Services

Close proximity to a gym often co-occurs with proximity to grocery stores (including ones selling fresh produce), urgent care clinics, and health-oriented restaurants. Living farther from a gym may mean living farther from all of these.

---

## Step 4: The Failure Mode in IV Terms

When the exclusion restriction is violated, the IV estimand becomes:

```
IV estimate = (Effect of Z on Y) / (Effect of Z on X)
            = (Effect of Distance on Health, total) / (Effect of Distance on Membership)
```

The numerator conflates the gym membership channel with all the direct neighborhood channels. The denominator is just the first stage.

**Key points from the skill's failure-mode analysis:**

1. **This is a bias problem, not a power problem.** Collecting more data does not fix an exclusion violation. The IV estimate converges to the wrong thing.

2. **The bias direction is unknown.** The direct effects of distance on health (through neighborhood quality) could run in either direction and with varying magnitudes. The IV estimate could be wrong in sign — not merely inflated in magnitude. You might conclude gym membership *hurts* health when in fact it helps, or overshoot the true effect by a factor of several.

3. **No amount of statistical significance changes this.** A very tight confidence interval around a badly biased estimate is worse than a wide interval around an unbiased one, because it creates false confidence.

---

## Step 5: The Falsification Test

The most useful diagnostic available is this: **does distance to the nearest gym predict health outcomes in a sub-population where gym membership is essentially impossible?**

Concretely: look at individuals with severe mobility impairments, residents of long-term care facilities, or any group where gym membership is near-zero regardless of proximity. If distance still predicts health outcomes in that sub-population, you have direct evidence of a path from the instrument to the outcome that bypasses membership — the exclusion restriction is violated.

This test doesn't require you to assume anything about the mechanism. A positive result is falsifying; a null result is reassuring (though not conclusive, since the health-active sub-population may be the one where the direct effects are largest).

---

## Step 6: Is There a Path Forward?

Your colleague's critique does not mean the question is unanswerable. It means this instrument, as stated, is not credible. Some options:

**Option A: Tighten the instrument's scope.** If you can find variation in gym proximity that is *genuinely* isolated from neighborhood quality — such as the opening of a new gym in a neighborhood while controlling richly for baseline neighborhood characteristics, or lottery-based gym access programs — the exclusion restriction becomes more defensible. The key is isolating variation in gym access that doesn't co-move with the neighborhood's overall health infrastructure.

**Option B: Use a different design.** If gym chains periodically open new locations, a differences-in-differences design comparing neighborhoods that got a new gym to similar neighborhoods that didn't (with a parallel trends check) might be more credible than IV on proximity. The identification assumption is different and in this case may be easier to defend.

**Option C: Use back-door adjustment if rich enough neighborhood controls exist.** If you can measure and condition on neighborhood socioeconomic status, walkability index, food access scores, and healthcare access, the back-door path through neighborhood quality is blocked. This requires the strong assumption that you've measured all the relevant neighborhood channels — but at least the assumption is explicit and partially checkable.

**Option D: Be explicit about what the IV estimates, conditional on the violation.** If the direct effect of distance on health (through non-membership channels) is small relative to the membership channel, the bias may be modest. A sensitivity analysis quantifying how large the direct effect would need to be to overturn your conclusion is honest and useful, even if it doesn't fix the problem.

---

## Summary

| Claim | Assessment |
|-------|-----------|
| Distance affects membership (relevance) | Plausible; testable via first stage F-statistic |
| Distance affects health only through membership (exclusion) | Almost certainly violated via neighborhood quality, walkability, food access, and activity infrastructure |
| Distance is exogenous to health (no Z-Y confounder) | Uncertain; residential sorting on health status is a real concern |
| More data fixes the violation | No. This is a bias problem, not a variance problem |
| The bias direction is known | No. The estimate could be wrong in sign |

Your colleague is right. The exclusion restriction is the weak link, the violation is substantively plausible rather than merely hypothetical, and the bias from a violated exclusion restriction cannot be resolved by collecting more data or improving estimation methods. The DAG doesn't support this instrument without substantial additional assumptions or design changes.
