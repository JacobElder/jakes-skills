# Does the Exclusion Restriction Hold for Distance-to-Gym as an Instrument?

**Short answer: Your colleague is right, and this is a serious problem — not a minor technicality.**

---

## Step 1: Name the Rung

Your goal is a **rung-2 (intervention) question**: what happens to health outcomes if we *cause* someone to join a gym? You have observational data, so you're relying on an instrument (distance to nearest gym) to recover a causal effect from non-experimental variation.

---

## Step 2: Sketch the DAG

Here is what you're assuming the DAG looks like for IV to work:

```
Distance (Z) → Gym Membership (X) → Health Outcome (Y)
                      ↑
               Unobserved Health
               Predisposition (U) → Y
```

For this instrument to be valid, there must be **no arrow from Z directly to Y**, and **no path from Z to Y that doesn't go through X**. That is the exclusion restriction.

Here is what the DAG almost certainly actually looks like:

```
Distance (Z) → Gym Membership (X) → Health Outcome (Y)
     |                ↑                      ↑
     |         Unobserved Health             |
     |         Predisposition (U) ──────────→|
     |                                       |
     └──────── Neighborhood Quality ─────────┘
     |                                       |
     └──────── Walkability / Active Transit ─┘
     |                                       |
     └──────── Socioeconomic Status ─────────┘
     |                                       |
     └──────── Access to Other Health        |
               Infrastructure ───────────────┘
```

Each of those arrows from Distance to Y, bypassing Gym Membership, is a direct violation of the exclusion restriction.

---

## Step 3: Why the Exclusion Restriction Is Almost Certainly Violated

The exclusion restriction requires that distance to the nearest gym affects health outcomes **only through gym membership**. Let's go through the specific mechanisms that make this implausible:

### Violation 1: Neighborhood Quality (the biggest one)

Distance to a gym is not random — gyms locate in neighborhoods with higher income, better infrastructure, and more health-conscious residents. People who live close to a gym also tend to live near:

- Better grocery stores and access to fresh food
- Better-maintained parks and green space
- Lower rates of environmental hazards (air pollution, noise, crime stress)
- Better healthcare facilities

All of these directly affect health outcomes independent of gym membership. This is a confounded instrument: Z is correlated with unobserved determinants of Y that have nothing to do with X.

### Violation 2: Walkability and General Physical Activity

Proximity to a gym is almost always correlated with neighborhood walkability. Walkable neighborhoods cause people to accumulate more incidental physical activity — walking to transit, walking to shops, cycling. This is a direct Z → Y path that does not pass through gym membership.

Put differently: two people at identical distances from the nearest gym may have very different health outcomes based on whether their neighborhood is walkable. And the instrument (distance) has soaked up some of that variation.

### Violation 3: Socioeconomic Status (SES)

Gyms cluster in wealthier areas. Distance to a gym is therefore a proxy for SES. SES has massive, well-documented direct effects on health through stress, healthcare access, diet, sleep, and housing quality — none of which have anything to do with gym membership. If you don't perfectly control for SES (and you can't — it has many dimensions), the exclusion restriction is violated.

### Violation 4: Access to Complementary Health Infrastructure

Close proximity to a gym also tends to mean close proximity to health clinics, mental health services, healthy restaurants, and other health-promoting establishments. These independently cause better health outcomes.

### Violation 5: Direct Psychological Effects of Neighborhood

There is reasonable evidence that perceived neighborhood safety, green space, and social cohesion affect health outcomes (through stress pathways, mental health, and social support) independent of any specific health behavior like gym attendance.

---

## Step 4: The Nature of the Problem

It is critical to understand what a violated exclusion restriction does to your estimate:

1. **This is a bias problem, not a power problem.** More data does not fix it. If the exclusion restriction is violated, your IV estimate is inconsistent — it does not converge to the true causal effect of gym membership even with a sample of a million people.

2. **The bias direction is unknown.** You cannot tell from theory alone whether your IV estimate will be upward- or downward-biased. The direction depends on the sign and magnitude of the direct Z → Y effect (which goes through neighborhood quality, walkability, SES, etc.), and on the sign of the correlation between Z and X. This means your IV estimate could have the wrong sign — not just the wrong magnitude.

3. **IV does not solve the confounding problem here; it relocates it.** The back-door problem was: healthier people self-select into gyms (U → X). The IV strategy was supposed to remove that. But because Z is also correlated with U (wealthier, healthier neighborhoods have more gyms), and because Z directly causes Y through non-gym pathways, you've introduced new violations in exchange for the ones you tried to remove.

---

## Step 5: A Falsification Check

One practical diagnostic for exclusion restriction violations: **check whether distance to gym predicts health outcomes among people who will never join a gym regardless of distance.**

If your instrument were valid, it should have no predictive power on health in a subpopulation where gym membership can't vary (e.g., elderly individuals with severe mobility limitations who are definitively not going to join a gym no matter how close one is). If distance still predicts health outcomes in that subpopulation, the exclusion restriction is violated — the instrument is picking up the effects of neighborhood quality, walkability, and SES, not gym membership.

This is not easy to execute cleanly, but it's the right direction for a falsification exercise.

---

## Step 6: What Would You Need for a Valid Instrument?

A valid instrument for gym membership would need to:

1. **Cause variation in gym membership** — it needs to be relevant.
2. **Be as-good-as-random with respect to unobserved health determinants** — ideally exogenous.
3. **Affect health only through gym membership** — the exclusion restriction.

Some candidates that have been used (with varying success) in the literature:

- **Random assignment to a gym subsidy or voucher.** This is the cleanest but requires an experiment.
- **Discontinuities in gym pricing** (e.g., employer wellness programs that kick in at a specific income or tenure threshold) — leverages an RDD-style design.
- **Supply shocks** (a new gym opened in area X due to a local zoning change unrelated to neighborhood health trends) — this is closer but still requires ruling out that the zoning change was driven by neighborhood characteristics correlated with health.

Distance to gym is attractive because it's easy to measure, but its face validity for the exclusion restriction is low. It is almost certainly confounded by all the pathways described above.

---

## Summary

Your colleague is correct. The exclusion restriction for distance-to-nearest-gym is almost certainly violated because:

- Distance is a proxy for neighborhood quality, walkability, SES, and access to health infrastructure — all of which directly cause health outcomes independent of gym membership.
- These are not minor, correctable nuisances. They are structural features of how gyms locate in space, and they cannot be fully controlled away.
- The consequence is not imprecision but bias of unknown sign and magnitude — your IV estimate may be wrong in direction, not just magnitude, and more data won't help.

The right response is either (a) find a better instrument with a more credible exclusion restriction, (b) use a design-based approach if there's a plausible natural experiment (e.g., a new gym opened due to a shock unrelated to neighborhood health trends), or (c) be explicit that your estimate is an upper or lower bound under specific assumptions about the direction of the exclusion restriction violation, and characterize the sensitivity.

What you should not do is proceed as if the exclusion restriction holds when the theoretical case against it is this strong.
