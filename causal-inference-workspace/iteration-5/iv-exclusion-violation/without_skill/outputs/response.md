# IV Exclusion Restriction Violation: Distance to Gym as an Instrument

## Short Answer

Yes, your colleague is almost certainly right. The exclusion restriction — that distance to the nearest gym affects health *only through* gym membership — is implausible for a number of theoretically grounded and empirically well-documented reasons. This doesn't mean IV is useless here, but you should take seriously that your estimates are likely biased, and you should be transparent about those threats.

---

## Background: What the Exclusion Restriction Requires

In the instrumental variables (IV) framework, a valid instrument Z (distance to gym) for the treatment D (gym membership) in the outcome equation Y (health) must satisfy three conditions:

1. **Relevance:** Z affects D (distance affects membership likelihood). This is testable and almost certainly holds — people closer to gyms join at higher rates.
2. **Independence (exogeneity):** Z is as good as randomly assigned, conditional on covariates. This is contestable but partially addressable.
3. **Exclusion restriction:** Z affects Y *only through* D. This is the assumption your colleague is questioning, and it is untestable from data alone.

The exclusion restriction fails whenever distance to a gym has *any* direct or indirect path to health that bypasses gym membership. There are multiple such paths.

---

## Why the Exclusion Restriction Is Likely Violated

### 1. Neighborhood Selection and Socioeconomic Confounding

Gyms are not randomly located. They cluster in higher-income, more commercially developed, urban, and lower-crime neighborhoods. People who live near gyms are systematically different:

- **Higher income and wealth**, which independently improve health through better nutrition, lower chronic stress, better healthcare access, and safer housing.
- **Access to healthier food environments.** Gym-dense areas tend to co-locate with grocery stores, farmers' markets, and health-food retailers. The same ZIP code that has a gym is more likely to have a Whole Foods than a food desert.
- **Better walkability and active transport infrastructure.** Proximity to a gym often proxies for living in a walkable urban core with bike lanes, parks, and transit — all of which produce physical activity *outside* of gym membership.
- **Lower pollution and environmental health burdens.** Wealthier, more developed neighborhoods with gyms tend to have lower industrial pollutant exposure.

Each of these is a direct path from "lives near a gym" to "better health" that has nothing to do with actually joining or using the gym.

### 2. Physical Activity Through Non-Membership Channels

Even if a person never joins the gym, living near one may increase physical activity:

- People may **walk or bike past the gym** as part of general neighborhood exploration.
- Gyms in commercial areas often co-locate with **parks, trails, and recreational facilities** that non-members use freely.
- The presence of a gym signals a neighborhood culture that **normalizes exercise**, which can affect behavior through social norms rather than membership.

This is a subtle but real violation: distance changes exercise behavior for non-members, which means the exclusion restriction fails even among the "untreated."

### 3. Social Environment and Peer Effects

People who live near gyms tend to live near *other people who go to gyms*. This shapes:

- **Social norms around health behaviors** — diet, sleep, substance use — that are independent of whether you personally hold a membership.
- **Peer influence on activity levels** more broadly, not just gym-specific activity.

### 4. Stress and Mental Health Pathways

Living in a walkable, lower-crime, higher-amenity area (which correlates with gym proximity) independently reduces chronic stress and improves mental health, both of which have large causal effects on physical health outcomes (cardiovascular disease, immune function, metabolic health).

### 5. Healthcare Access

Gym proximity is correlated with proximity to other health infrastructure — clinics, hospitals, urgent care centers. Better preventive care access is a direct health pathway entirely unrelated to gym use.

---

## Evaluating the Magnitude of the Problem

Not all exclusion violations are catastrophic. The severity depends on:

- **How large the direct effect is relative to the indirect (membership) effect.** If the direct effect of neighborhood quality on health is large (plausible), even a modest violation biases IV estimates substantially.
- **The direction of the bias.** Typically, neighborhoods near gyms are healthier for multiple reasons, meaning the IV estimate will *overstate* the causal effect of gym membership. Your instrument captures a bundle of health-promoting neighborhood features, and you're attributing all of the variation in health to the gym membership channel.
- **The strength of the first stage.** Ironically, a weak instrument makes violations *more* damaging, not less. Even a modest violation of exclusion with a weak instrument can produce badly biased estimates. If the first-stage F-statistic is, say, 15–20 (common in these settings), violations of even modest magnitude are not washed out.

The formal expression clarifies the problem. If there is a direct effect of Z on Y of magnitude δ, the IV estimator converges to:

```
β_IV → β_true + δ / (first stage coefficient)
```

A small direct effect δ gets amplified by the inverse of the first-stage coefficient. Weak instruments make exclusion violations more damaging, not less.

---

## What Can Be Done

### Conditional on Rich Geographic Controls

You can attempt to partial out neighborhood-level confounders by including:
- Neighborhood median income, poverty rate, Gini coefficient
- Census-tract-level walkability scores (e.g., Walk Score)
- Food environment indices (e.g., USDA Food Access Research Atlas)
- Crime rates, pollution measures, park access

The argument becomes: conditional on these controls, residual variation in distance to gym is plausibly excludable. This is a stronger claim, but it trades one assumption for another (correct specification of the controls).

### Falsification Tests

Test whether distance to a gym predicts health outcomes *among people who definitely cannot use gyms* (e.g., those with severe mobility impairments, or those in a period before gyms were built in the area). If distance still predicts health in these groups, the exclusion restriction is violated.

You can also test whether distance predicts other health-irrelevant outcomes that should be unaffected by the instrument if exclusion holds. Unexpected correlations suggest a neighborhood-level confound.

### Sensitivity Analysis for Exclusion Violation

Use tools like Conley, Hansen, and Rossi's (2012) "plausibly exogenous" approach, which allows you to specify a prior or bound on the magnitude of the direct effect and trace out how much the IV estimate changes. This lets you report: "If the direct effect of distance on health (through non-membership channels) is no larger than X, the true membership effect is bounded between A and B."

### Alternative Instruments

Consider whether there are instruments less susceptible to neighborhood-level confounding. Examples from the literature:
- **Gym opening/closing events** (difference-in-differences combined with IV, comparing people who lived near a gym before and after it opened vs. matched controls).
- **Random price variation** from employer wellness programs or insurance-linked gym reimbursements.
- **Gym construction lotteries or zoning decisions** where timing or location has some quasi-random component.

---

## The Deeper Issue: What Is Your Estimand?

Even if you could address the exclusion restriction, your IV recovers a **Local Average Treatment Effect (LATE)** — the effect of gym membership on the compliers, i.e., people who would join a gym if one were nearby but wouldn't otherwise. This is a specific subpopulation (likely younger, more urban, more mobile) and the effect may not generalize to the average person or to policy-relevant populations.

---

## Bottom Line

Your colleague is correct. Distance to a gym is a plausible and commonly used instrument in health economics, but the exclusion restriction is almost certainly violated in practice. The violations are not exotic or hard to imagine — they follow directly from the well-documented fact that gyms cluster in healthy, high-amenity neighborhoods where residents are healthier for many reasons unrelated to gym use. Your IV estimate likely overestimates the true causal effect of gym membership on health.

This does not necessarily mean you should abandon the instrument, but it does mean:

1. You should include rich neighborhood-level controls to absorb the most obvious direct pathways.
2. You should conduct and report falsification tests.
3. You should present sensitivity analyses that bound the estimate under varying degrees of exclusion violation.
4. You should be candid in your write-up that the exclusion restriction is an assumption, not a verified fact, and that readers should interpret the estimate as an upper bound on the gym membership effect under the plausible direction of violation.

Treating IV as providing a "clean" causal estimate here, without engaging with these threats, would be methodologically indefensible. Your colleague is doing you a favor.
