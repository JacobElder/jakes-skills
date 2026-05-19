# IV Estimation: Is the Exclusion Restriction Violated for Gym Distance as an Instrument?

## Short Answer

Yes, your colleague is almost certainly right. The exclusion restriction — that distance to the nearest gym affects health *only* through gym membership — is highly implausible. There are multiple credible pathways through which physical proximity to a gym could affect health outcomes independently of whether someone actually joins.

---

## Background: What the Exclusion Restriction Requires

In an instrumental variables (IV) setup, you need three conditions:

1. **Relevance**: The instrument Z (distance) is correlated with the treatment D (gym membership). Plausible — people closer to gyms are more likely to join.
2. **Independence (Exogeneity)**: Z is as-good-as-randomly assigned (uncorrelated with unobserved confounders). Debatable — neighborhood location is not random — but let's set this aside for now.
3. **Exclusion Restriction**: Z affects the outcome Y (health) *only through* D. This is the condition your colleague is questioning.

The exclusion restriction cannot be tested from the data alone — it is a theoretical/design assumption. This makes it crucial to think through carefully.

---

## Why the Exclusion Restriction Is Almost Certainly Violated

### 1. Neighborhood Characteristics (The Big One)

Distance to the nearest gym is largely a function of what neighborhood you live in. Neighborhoods with nearby gyms tend to differ systematically from those without them:

- **Walkability**: Urban, walkable neighborhoods have gyms nearby. They also have more opportunities for incidental physical activity (walking to transit, running errands on foot) entirely unrelated to gym membership.
- **Access to healthy food**: Grocery stores, farmers markets, and restaurants with healthy options cluster in similar areas as gyms. Proximity to gyms may proxy for access to nutritious food, which directly affects health.
- **Safety**: Neighborhoods where people feel safe enough to have built gyms may also be places where people feel safe to exercise outdoors, walk dogs, bike, etc.
- **Socioeconomic status (SES)**: Wealthier neighborhoods have more gyms. SES independently predicts health through income, stress, healthcare access, air quality, and dozens of other channels.
- **Air quality and environmental health**: Urban density (which correlates with gym proximity) may also mean more or less pollution, green space, and other environmental determinants of health.

All of these are pathways from "distance to gym" to "health outcome" that bypass gym membership entirely.

### 2. Selection on Neighborhood — Not Just on Gym

Even if we accept that gym membership is endogenous (healthier people self-select), the same logic applies more forcefully to neighborhood choice. Healthy, health-conscious people tend to choose neighborhoods with amenities like gyms, parks, and healthy restaurants. This creates a direct channel: health-consciousness → live near a gym → better health outcomes, none of which runs through actually joining the gym.

This also threatens the independence/exogeneity assumption, but note that it simultaneously threatens the exclusion restriction: health-conscious behavior produces better health *and* produces proximity to gyms, without requiring gym membership as the mechanism.

### 3. Park and Recreational Infrastructure Proximity

Gyms tend to co-locate with other recreational infrastructure — parks, trails, sports facilities, community centers. Living near a gym likely means living near these alternatives to gym membership. Someone who lives close to a gym but doesn't join may still improve their health by using the adjacent running trail or public park.

### 4. Mental Health and Stress Pathways

Living in a neighborhood with amenities (including gyms) may reduce stress through psychological mechanisms — sense of neighborhood quality, social cohesion, perceived safety — all of which affect health independently of gym use.

---

## The Formal Problem

In potential outcomes notation, the exclusion restriction requires:

**Y_i(d, z) = Y_i(d, z') for all z, z' and all d**

That is, changing the instrument Z (distance) while holding the treatment D (membership) fixed should not change the outcome Y (health). But if proximity to a gym independently affects health via walkability, food access, SES, or outdoor exercise options, then Y_i(1, z_near) ≠ Y_i(1, z_far) — a clear violation.

---

## What Violation Does to Your IV Estimate

If the exclusion restriction is violated, your IV estimator does not recover the causal effect of gym membership. Instead, it recovers a contaminated quantity that mixes the effect of membership with the direct effects of proximity on health. Depending on the direction of those direct effects (likely positive — living near a gym is good for health through multiple channels), your IV estimate will be **upward biased** relative to the true effect of gym membership.

In the worst case, you could find a large, statistically significant "effect" of gym membership that is entirely driven by the health advantages of living in a neighborhood with a nearby gym, not by anything the gym itself is doing.

---

## Is There Any Way to Salvage the Design?

Possibly, but it requires strong auxiliary moves:

1. **Control for neighborhood characteristics**: If you can control for walkability scores, food environment indices, SES, park access, etc., you remove some of the direct pathways. But you can never be certain you've captured all of them, and over-controlling can introduce collider bias.

2. **Use within-neighborhood variation**: If a new gym opens in a neighborhood, you can compare residents who are now slightly closer vs. slightly farther within the same neighborhood (a regression discontinuity or difference-in-differences approach). This absorbs neighborhood-level confounders, though some violations (e.g., the nearest gym also being near a new park) remain.

3. **Argue the violations are small relative to the relevance**: If the first stage is very strong and the direct effects of proximity are small, the bias may be modest. But this requires auxiliary evidence and quantitative sensitivity analysis, not just verbal argument.

4. **Sensitivity analysis (Conley et al., 2012)**: Formally relax the exclusion restriction by allowing a direct effect of Z on Y of magnitude δ, and examine how your estimate changes as δ varies. If the estimate is robust to plausible violations, confidence increases.

---

## Bottom Line

Your colleague is right, and this is not a close call. Distance to the nearest gym is a classic example of an instrument that satisfies relevance but almost certainly fails the exclusion restriction due to neighborhood-level confounding. The instrument captures too much about where someone lives — and where someone lives affects health through many pathways that have nothing to do with gym membership.

This is a very common challenge in health economics IV designs, and the literature has grappled with it extensively. Before proceeding, you should either find a more credible instrument (e.g., a policy change that quasi-randomly affected gym availability in some areas but not others), or pair the geographic instrument with rich neighborhood-level controls and explicit sensitivity analysis to bound the potential bias.
