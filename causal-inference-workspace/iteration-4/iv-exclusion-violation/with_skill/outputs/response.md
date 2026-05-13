# IV Analysis: Distance to Gym as an Instrument for Membership

Your colleague is right, and this is worth working through carefully because the exclusion restriction failure is not a technicality — it's a substantive mechanism you can reason about from first principles.

---

## 1. Name the rung

You're on **Rung 2 (Intervention)**: you want to know the effect of *doing* gym membership, not merely correlating it with health. The data is observational, and you've recognized the core identification problem (self-selection). Instrumental variables is a valid Rung 2 strategy — when the instrument is valid.

---

## 2. Sketch the DAG

Let's draw out what you're assuming and what might actually be true.

**Your assumed DAG:**

```
Distance → Membership → Health
              ↑
          Confounders (health-consciousness, income, etc.)
```

In this DAG, `Distance` is a valid instrument because:
- It causes `Membership` (relevance)
- All paths from `Distance` to `Health` run through `Membership` (exclusion)
- `Distance` shares no common cause with `Health` (independence)

**The DAG your colleague suspects:**

```
Distance → Membership → Health
    ↓                    ↑
    └────────────────────┘
       (direct path)
```

Where the direct path `Distance → Health` exists through mechanisms that bypass gym membership entirely. The question is whether those direct paths are real.

---

## 3. Identify the structure — where the exclusion restriction breaks

The exclusion restriction says: *distance to a gym affects health only by changing gym membership*. Here are the concrete mechanisms that violate it:

**Walking and incidental physical activity.** Living closer to a gym usually means living in a denser, more walkable neighborhood. Residents walk more to transit, to shops, and simply as part of daily life — regardless of whether they join the gym. This is a direct path: `Distance → Neighborhood walkability → Physical activity → Health`, with no gym membership on the path.

**Neighborhood confounding (independence assumption failure).** Distance to gym is not randomly assigned. Gyms locate in neighborhoods that are wealthier, denser, or more health-oriented. These neighborhood characteristics are themselves causes of health outcomes — through air quality, grocery access, stress, green space, and social norms. This isn't just an exclusion restriction violation; it's also a threat to the independence assumption. The instrument is correlated with unobserved determinants of health.

**Access to co-located amenities.** Gyms cluster with other health-promoting infrastructure — parks, health food stores, cycling infrastructure, lower crime rates. Living near a gym means access to all of these, not just the gym itself.

**Selection on neighborhood.** Healthier, wealthier people sort into neighborhoods with gyms. Even holding individual gym membership constant, proximity is a proxy for socioeconomic and health-related characteristics that causally affect outcomes.

Each of these is a *specific, named mechanism* — not a vague worry about "other stuff." That's what makes your colleague's concern credible rather than speculative.

---

## 4. Structural diagnosis

The exclusion restriction fails if there exists *any* path from the instrument to the outcome that does not pass through the treatment. The walkability and neighborhood amenity channels are both plausible and empirically documented. Your instrument has to explain 100% of its effect on health through gym membership — not 95%, not 99%. Even small direct effects bias IV estimates, and the bias is not attenuated by sample size.

One more problem: the **monotonicity assumption** underlying LATE. IV with a binary treatment identifies the Local Average Treatment Effect — the effect on compliers (people who join a gym because they live close, and wouldn't join if they lived far). If there are defiers (people who join specifically *because* distance is a challenge, or who avoid gyms in their neighborhood for social reasons), LATE is not identified. This is a secondary concern, but worth noting.

---

## 5. The most likely trap here

**Instrument-as-proxy for neighborhood quality.** Distance to the nearest gym is, in many real datasets, primarily a measure of whether you live in a dense, wealthy, health-conscious urban area. Once you condition on that latent variable — which you can't, because it's unmeasured — the variation in distance that remains may have very little relevance (weak instrument) and the direct path through neighborhood characteristics would dominate.

This is the worst-case combination: a weak instrument *and* an exclusion restriction violation. Weak IV amplifies any exclusion restriction bias. The formula for asymptotic IV bias is approximately:

```
Bias(IV) ≈ (direct effect of Z on Y) / (effect of Z on X)
```

If the instrument is weak (small denominator) and the direct effect is non-trivial (non-zero numerator), the bias can be large — potentially larger than OLS.

---

## 6. What would a better instrument look like?

To save the IV approach, you'd need variation in gym proximity that is:
- **Plausibly exogenous:** not correlated with neighborhood quality, income, or baseline health
- **Exclusive:** only plausibly affecting health through membership

Candidates that have been used or proposed in the literature:
- **Quasi-random gym openings or closures:** a gym chain opening a new location for reasons unrelated to local health demand (real estate availability, lease negotiation, franchise rollout schedules). The timing and location would ideally be documented as driven by supply-side factors.
- **Lottery-based gym access programs:** if gym access was allocated by lottery (some policy programs do this), the lottery ticket is a clean instrument.
- **Distance to a gym that *just* opened vs. one that has existed for years:** a recently opened gym may generate less neighborhood sorting than an established one.

None of these are easy to find. The difficulty of finding a clean instrument is itself information — it tells you that gym membership is deeply entangled with neighborhood and socioeconomic factors that affect health through many channels.

---

## 7. What to do

**Option A: Test the exclusion restriction indirectly.** You can't directly test the exclusion restriction (that would require observing the counterfactual), but you can look for fingerprints. Control for neighborhood walkability, income, and access to parks and food stores — variables that capture the direct pathways. If the IV estimate changes substantially when you add these controls, the instrument is not doing what you think. (Note: this is a diagnostic, not a fix — you'd need to argue those controls don't open new backdoors.)

**Option B: Use distance as an imperfect instrument with sensitivity analysis.** There is a literature on "plausibly exogenous" instruments (Conley, Hansen & Rossi) that allows the exclusion restriction to hold only approximately, and traces out how much the estimate changes as a function of how strong the direct effect can be. If your estimate is robust across a range of plausible direct effects, you have a stronger case.

**Option C: Consider alternative identification strategies.** If a gym opened or closed in your study area, a differences-in-differences design (comparing health trajectories of nearby vs. far residents, before and after the opening/closure) may be cleaner. This leverages the *change* in proximity, not the level, which is less correlated with time-invariant neighborhood quality.

**Option D: Be honest about what OLS gives you, bounded.** OLS gives you a biased estimate due to positive selection (healthier people join). IV would give you an upwardly biased estimate in the other direction if the exclusion restriction is violated in the direction of neighborhood quality → health. The truth likely lies between these two bounds. A partial-identification approach (Manski bounds) can characterize that range without pretending identification is clean.

---

## Summary verdict

Your colleague is right. The exclusion restriction is almost certainly violated because distance to a gym is a proxy for neighborhood characteristics (walkability, wealth, amenity access) that directly affect health independent of gym membership. The violation is not a subtle statistical issue — it reflects well-documented causal mechanisms. The instrument should be treated as suspect unless you can find quasi-random variation in gym proximity driven by supply-side factors unrelated to neighborhood health demand.

The immediate next step is the sensitivity diagnostic in Option A: add controls for the direct-path mechanisms and see how much your IV estimate moves. If it moves a lot, you have your answer.
