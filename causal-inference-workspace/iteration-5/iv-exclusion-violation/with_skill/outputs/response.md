# IV Exclusion Restriction: Distance to Gym as an Instrument for Gym Membership

## Short answer

Your colleague is right, and they are right in a way that matters more than you might think. The exclusion restriction for distance-to-gym is almost certainly violated, and the violation is not a minor technical quibble — it means your IV estimate may be biased in an unknown direction, possibly wrong even in sign.

---

## Step 1: Name the rung

You are asking a Rung 2 question: "What would happen to health outcomes if we *intervened* to give someone a gym membership?" You want P(health | do(membership)), not merely the correlation between membership and health. That is the right framing, and IV is a legitimate identification strategy in principle. The question is whether distance to gym satisfies the three conditions for a valid instrument.

---

## Step 2: Sketch the DAG

Here is what the DAG looks like under your assumptions (the version where IV would work):

```
Distance (Z) → Membership (X) → Health (Y)
                    ↑
                    U (unobserved: health-consciousness, income, etc.)
                    ↓
                    Y
```

For Z to be a valid instrument, three conditions must hold:

1. **Relevance:** Z affects X. Living closer to a gym increases the probability of membership. This is the most defensible condition and is testable — just regress membership on distance.

2. **Exclusion restriction:** Z affects Y *only* through X. Distance to gym has no direct effect on health except by changing gym membership status.

3. **Exogeneity (independence):** Z shares no common cause with Y. Distance to gym is not confounded with health.

Condition 1 is likely satisfied. Conditions 2 and 3 are the problem.

---

## Step 3: Why the exclusion restriction almost certainly fails

The exclusion restriction requires that distance to the nearest gym has *zero* direct effect on health outcomes through any channel other than gym membership. Here are the concrete violation pathways:

### Violation pathway 1: Neighborhood selection (the big one)

Distance to the nearest gym is not random — it is a characteristic of where you live. Neighborhoods with nearby gyms are systematically different from neighborhoods without them:

- Gyms cluster in wealthier, more walkable, more commercially developed areas.
- Those same neighborhoods have better grocery stores, safer streets, lower pollution, better access to parks, and higher-quality healthcare.
- They also attract residents who are already health-conscious, higher-income, and better-educated.

The correct DAG includes a fork:

```
Neighborhood quality (W) → Distance (Z) → Membership (X) → Health (Y)
Neighborhood quality (W) ────────────────────────────────→ Health (Y)
```

W is a common cause of Z and Y. This is an exogeneity violation (condition 3), not merely an exclusion violation — but it produces the same problem: Z is not exogenous with respect to Y.

### Violation pathway 2: Physical activity through proximity itself

Living near a gym may increase physical activity even among non-members. People who walk or cycle past the gym may use adjacent parks, bike lanes, or sidewalks more. The gym may be in a mixed-use area that encourages active transportation. Distance to the gym is partly a proxy for "distance to a dense, walkable, active area" — which has direct health effects that do not run through membership.

```
Distance (Z) → Active transportation / walkability → Health (Y)
Distance (Z) → Membership (X) ──────────────────── → Health (Y)
```

The first arrow is a direct path from Z to Y that bypasses X. The exclusion restriction is violated.

### Violation pathway 3: Social environment and chronic stress

Neighborhoods with gyms also tend to have lower crime, stronger social cohesion, and lower chronic stress exposure. Chronic stress is a major driver of cardiovascular disease, immune function, and mental health. Distance to gym conflates proximity to gyms with proximity to low-stress social environments.

### Violation pathway 4: Health-consciousness of neighbors

Your neighbors' health behaviors affect yours through social norms, peer effects, and shared infrastructure. If health-conscious people disproportionately live near gyms (because they selected into those neighborhoods), living near a gym exposes you to social contagion of healthy behavior independent of your own membership status.

---

## Step 4: What the violation means for your estimate

This is the part that is easy to underestimate. An exclusion violation is not a power problem — **more data will not fix it.** It is a structural bias problem. The IV estimator conflates the effect of membership on health with the direct effect of distance on health. The bias is in the probability limit of the estimator, not in its variance.

Formally, the IV estimator converges to:

```
plim(β_IV) = β_true + (direct effect of Z on Y) / (effect of Z on X)
```

**The direction of the bias is unknown.** Whether the IV estimate is too high, too low, or even wrong in sign depends on the sign and magnitude of the direct Z → Y effect relative to the Z → X → Y effect. In this case, all the direct pathways — neighborhood quality, walkability, social environment — plausibly have positive effects on health, the same direction as gym membership's hypothesized effect. This means the IV estimate is likely *upward biased*, potentially substantially. You would be attributing to gym membership some of the benefit of simply living in a health-supporting neighborhood.

But notice: this is a conditional judgment about direction. If any direct pathway ran in the opposite direction (e.g., gyms locate near industrial zones with poor air quality), the bias could flip. You cannot sign the error without reasoning carefully about each direct pathway — which itself requires the DAG you were trying to avoid specifying.

---

## Step 5: A concrete falsification test

The skill's framework offers a useful diagnostic: **check whether the instrument predicts the outcome in a sub-population where the treatment cannot vary.**

Here, that means: does distance to gym predict health outcomes among people who are definitively unable to use a gym regardless of proximity — people with severe mobility impairments, residents of long-term care facilities, or people who are incarcerated?

If distance to gym still predicts health outcomes in that group, you have direct evidence of an exclusion violation: Z is affecting Y through a channel that bypasses X entirely.

This won't fully exonerate the instrument if no effect is found (the violation pathways may only operate among ambulatory, community-dwelling people), but a positive finding is essentially a proof of violation. It is a concrete, relatively cheap test to run before committing to the IV design.

Additional falsification approaches:

- Regress the instrument on a rich vector of neighborhood characteristics (median income, Walk Score, park access, grocery store proximity, crime rates, healthcare provider density). If distance to gym loads heavily onto all of them — which it will — you have direct evidence that Z encodes much more than "access to a gym."
- If historical data exist, test whether distance predicts health outcomes *before* any gyms operated in the area. Pre-gym predictive power reflects the neighborhood quality channel that was always there.

---

## Step 6: What to do instead

Given that the exclusion restriction is plausibly violated, here are the structural alternatives in order of preference:

**Option A: RCT or encouragement design**

Randomly assign discounts, free memberships, or free trials to some people. Lottery assignment is a clean instrument because it is genuinely independent of neighborhood quality and walkability — it has no plausible direct effect on health except through the membership it encourages. An encouragement design is the fastest path to a credible IV.

**Option B: Better natural instrument**

Look for variation in gym availability that is more plausibly exogenous:

- A new gym opening or closing in a neighborhood: the timing of commercial real estate decisions is less correlated with pre-existing health trajectories than static proximity is. Use the opening date and control for pre-trends.
- Employer gym benefit: if employment at a firm with a gym benefit is as-if-random conditional on occupation, industry, and baseline health, this could work.
- Insurer subsidy lotteries: some plans have run randomized "Silver Sneakers" or gym-reimbursement lotteries; lottery assignment is clean.

**Option C: Differences-in-differences around gym openings or closings**

If a gym opened or closed in a neighborhood, DiD compares the change in health outcomes for nearby residents to the change for residents in comparable neighborhoods without the event. This design controls for all time-stable neighborhood characteristics — including the SES, walkability, and social environment factors that violate the exclusion restriction in the IV design — under a parallel trends assumption. Parallel trends is testable in pre-event data. This is probably the most feasible observational design if you cannot run an experiment.

**Option D: Back-door adjustment with rich controls**

If you believe the confounders are measurable (neighborhood income, walkability, food access, healthcare proximity, baseline health), conditioning on them directly is legitimate. The challenge is that health-consciousness is not fully observed, and some proxies for it (recent doctor visits, supplement use) are plausibly post-treatment or themselves endogenous. A rich set of neighborhood-level administrative covariates combined with individual-level health history may make back-door adjustment defensible, but you need to argue for each confounder in the DAG rather than just "controlling for everything."

**Option E: Partial identification**

If you are committed to using distance as an instrument but acknowledge the exclusion restriction may be violated, Nevo and Rosen's (2012) bounds approach allows you to derive informative bounds on the true effect under weaker conditions — for instance, the assumption that the direct effect of Z on Y is no larger than the direct effect of X on Y, or that the violation runs in a known direction. This gives you a range rather than a point estimate, which may still support policy conclusions if the bounds are tight enough.

---

## Bottom line

Your colleague is right. The exclusion restriction for distance to gym is almost certainly violated because distance to a gym is not just a shifter of gym membership — it is a proxy for neighborhood quality, walkability, social environment, and access to health-supporting infrastructure. All of these have direct effects on health that do not run through gym membership.

The violation is structural, not statistical. More data does not cure it. The IV estimate is likely upward biased — it partially credits gym membership for the general health advantages of living in a resource-rich neighborhood — but the direction cannot be known for certain without mapping all direct pathways.

Before proceeding, the recommended sequence is:

1. Run the falsification test on a sub-population that cannot use gyms.
2. Regress the instrument on neighborhood characteristics to quantify how much of the Z variation reflects neighborhood quality versus something more specific to gym access.
3. Consider alternative instruments (gym openings, employer subsidies, randomized trials) where the exogeneity case is stronger.
4. If none of those are available, acknowledge that the causal effect of gym membership is not credibly identified with this instrument and report a sensitivity analysis showing how large the direct Z → Y effect would need to be to overturn any conclusion.
