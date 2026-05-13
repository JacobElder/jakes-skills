# Causal Effect of Gym Membership on Health: IV Analysis with Distance as Instrument

## Short Answer

Your colleague is almost certainly right. The exclusion restriction is highly likely to be violated when using distance to the nearest gym as an instrument for gym membership. Here's a thorough breakdown of why.

---

## The IV Setup

You want to estimate:

**Health Outcome = α + β × Gym Membership + ε**

where β is the causal effect of gym membership. The endogeneity problem is selection bias: people who are already healthier (or more health-conscious) are more likely to join gyms, so OLS will overestimate β.

Your instrument Z = Distance to nearest gym. For this to be valid, it must satisfy:

1. **Relevance**: Distance → Gym Membership (closer gyms → more likely to join)
2. **Exclusion Restriction**: Distance affects Health *only through* Gym Membership
3. **Independence (Exogeneity)**: Distance is as-good-as-randomly assigned (not correlated with unobserved confounders)

---

## The Relevance Condition

This is plausible and likely holds. There is solid empirical evidence that proximity to recreational facilities increases their use. Greater distance raises the cost (time, money, effort) of gym attendance, reducing membership likelihood. The first stage F-statistic would likely be respectable, though not enormous. This condition is the strongest part of your design.

---

## Why the Exclusion Restriction Is Almost Certainly Violated

The exclusion restriction requires that distance to a gym affects your health **only** through whether you join that gym. But distance to a gym is fundamentally a measure of **where you live** — and where people live is correlated with a huge number of health-relevant factors.

### 1. Neighborhood Socioeconomic Status

Gyms cluster in wealthier, more commercially developed neighborhoods. People who live close to a gym are more likely to live in areas with:
- Higher income and wealth
- Better access to healthy food (grocery stores, farmers markets, fewer food deserts)
- Lower exposure to environmental hazards (pollution, noise)
- Better healthcare access (clinics, hospitals, pharmacies nearby)
- Greater perceived safety enabling outdoor physical activity

All of these independently affect health outcomes, violating exclusion.

### 2. Urban Density and Walkability

Gyms are more common in dense urban areas. Urban residents who live near gyms also tend to:
- Walk more in daily life (commuting, errands)
- Have access to parks, bike lanes, and other recreational infrastructure
- Use public transit (which involves more walking than car commuting)

If walkability increases health independent of gym membership, your instrument is contaminated.

### 3. Other Physical Activity Infrastructure

Distance to a gym correlates with distance to other health-promoting facilities: swimming pools, yoga studios, sports courts, parks, and trails. Someone who lives 0.2 miles from a gym likely also lives near a park. If they exercise outdoors rather than joining the gym, the instrument affects health through a pathway that bypasses gym membership entirely.

### 4. Sorting and Neighborhood Selection

People choose where to live, and health-conscious people may actively sort into neighborhoods with amenities — including gyms. This creates a correlation between proximity and the unobserved health consciousness variable (ε), violating the independence/exogeneity condition as well. Even if you believe the exclusion restriction, the instrument may not be exogenous.

### 5. Stress and Mental Health Pathways

Urban areas with more gyms may also have more cafes, restaurants, cultural amenities, and social infrastructure. These affect mental health and stress, which in turn affect physical health — entirely independent of gym membership.

---

## The Formal Problem

Let the true model be:

**Health = α + β × Membership + γ × Neighborhood_Quality + ε**

where Neighborhood_Quality is unobserved and correlated with Distance. Your instrument Distance correlates with Neighborhood_Quality, so the IV estimator picks up the effect of Neighborhood_Quality on health, not just the effect of Membership. The IV estimate is:

**β̂_IV → β + (γ × Cov(Distance, Neighborhood_Quality)) / Cov(Distance, Membership)**

This is biased. The direction is ambiguous depending on the sign of γ and the correlation structure, but the contamination is real.

---

## How Serious Is This?

The exclusion violation is not just a theoretical concern — it is likely large in magnitude. Neighborhood quality effects on health are well-documented in the literature (see Chetty et al. on neighborhood effects, or the Moving to Opportunity experiment). These effects are large enough that they could substantially distort your IV estimate, potentially even reversing its sign or magnitude relative to the true causal effect.

---

## What Could You Do Instead?

If you're committed to an IV approach, here are refinements:

1. **Control for neighborhood characteristics**: Include income, density, walkability scores, food access measures, and other observable neighborhood variables as controls. This doesn't fully solve the problem (unobservables remain) but reduces the magnitude of the violation.

2. **Use variation in gym openings/closures**: If a gym opens in a neighborhood, people nearby experience a sudden change in distance. A difference-in-differences or event study using gym openings could isolate more plausibly exogenous variation — though sorting into neighborhoods in anticipation of gym openings is still a concern.

3. **Restrict sample geographically**: Comparing people within the same neighborhood or census tract who differ slightly in distance (e.g., living on different sides of a block) reduces the neighborhood confounding problem. This is essentially a regression discontinuity logic.

4. **Randomized trials or natural experiments**: Employer-sponsored gym subsidies that were randomly assigned, or lottery-based gym membership programs, would provide cleaner identification.

5. **Sensitivity analysis**: Use bounds methods (e.g., Conley et al. 2012 "plausibly exogenous" approach) to assess how large the exclusion violation would need to be to overturn your conclusions.

---

## Bottom Line

Your colleague is right. Distance to the nearest gym fails the exclusion restriction because it proxies for where you live, and where you live affects health through many channels beyond gym membership: neighborhood SES, walkability, food access, environmental quality, and proximity to other health-promoting infrastructure. The instrument is also likely to violate exogeneity due to residential sorting by health-conscious individuals.

This doesn't mean the project is hopeless — it means you need a more carefully designed identification strategy, richer controls, or a different instrument. Using gym openings with narrow geographic comparison groups is probably your best available option without running a randomized experiment.
