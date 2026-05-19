# Causal Analysis: LATE vs. ATE in Feature Rollout Decisions

## The Question

> We used an encouragement design — we randomly sent a push notification to 30% of users inviting them to try our new premium feature. 18% of the notified group adopted the feature vs. 3% in the non-notified control group. Using the notification as an instrument, we estimate the LATE (Local Average Treatment Effect) for compliers at +$32 average 6-month revenue per user. Our CEO wants to force-enable the premium feature for all users who haven't adopted it, expecting roughly $32 revenue uplift per user. Is that the right expectation?

**Short answer: No. The $32 estimate almost certainly overstates the revenue effect of forced rollout, possibly substantially. The CEO's expectation is built on a category error about what LATE measures.**

---

## Step 1: Name the Rung

The CEO's question is **rung 2 (intervention)**: "What happens to revenue if we *do* force-enable the feature for everyone?" That requires the causal quantity P(Revenue | do(Feature = enabled)).

The $32 LATE estimate is also a rung-2 quantity — but it answers a different, narrower rung-2 question: "What is the effect of feature adoption on revenue *for the subpopulation of users who adopted because of the notification?*"

These are two different interventions on two different populations. Conflating them is the core error here.

---

## Step 2: Sketch the DAG

```
Notification (Z) ---> Feature Adoption (X) ---> Revenue (Y)
                              ^
                              |
                    User Type / Motivation (U)
                              |
                              v
                           Revenue (Y)
```

- **Z** = push notification (the instrument, randomly assigned)
- **X** = feature adoption (the treatment)
- **Y** = 6-month revenue
- **U** = unobserved user heterogeneity (intrinsic motivation, engagement level, willingness to pay, how well the feature fits their workflow)

The IV design is valid because:
- Z affects X (relevance confirmed: 18% vs. 3% adoption, a 15 percentage point first stage — strong)
- Z has no direct effect on Y (exclusion restriction: receiving a push notification doesn't independently change revenue, only through adoption)
- Z is exogenous (random assignment — satisfied by design)

The IV estimate recovers LATE, not ATE.

---

## Step 3: What LATE Actually Measures

IV with an encouragement design identifies the effect on **compliers** — the subpopulation of users who:
- Adopted the feature *because* they received the notification, and
- Would NOT have adopted without it

There are three other latent types in the population:

| Type | Notified behavior | Not-notified behavior | Size (approx.) |
|------|------------------|-----------------------|----------------|
| **Compliers** | Adopt | Don't adopt | ~15% of users (the first stage) |
| **Always-takers** | Adopt | Adopt | ~3% (the baseline adoption rate) |
| **Never-takers** | Don't adopt | Don't adopt | ~82% |
| **Defiers** | Don't adopt | Adopt | Assumed ~0% (monotonicity) |

The $32 LATE is the average treatment effect *only for compliers* — roughly 15% of the user base. The CEO wants to force-enable for the remaining ~82% who are **never-takers by revealed preference**.

---

## Step 4: Why Never-Takers Are Different

The never-takers (the vast majority of non-adopters the CEO wants to force-enable) revealed through the experiment that they did not adopt even after an explicit, personalized invitation. This is meaningful signal about U:

**Plausible reasons someone is a never-taker:**
- The feature doesn't fit their use case or workflow
- They already have a workaround or competing solution
- Their revenue contribution is inherently low (they're light users who won't benefit)
- They have lower willingness to pay for premium features
- They tried the feature briefly and found no value (this would show up as churn from the forced-enable)

**Compliers**, by contrast, were users who needed a nudge — they were on the margin of adoption. The notification moved them over the threshold. These are likely users for whom the feature *was* a good fit, but who faced inertia, discoverability friction, or mild inattention.

Under heterogeneous treatment effects (which are nearly certain here given the behavioral heterogeneity above), the LATE for compliers will typically **exceed the ATE across all users** — particularly when:
1. Compliers are positively selected on feature-outcome fit
2. Never-takers have lower treatment effects by definition of their type

There is no reason to expect U-shaped heterogeneity where never-takers would benefit more than compliers. The structural default is: complier LATE > population ATE > never-taker treatment effect.

---

## Step 5: The Extrapolation Gap

The CEO's calculation implicitly assumes:

**LATE(compliers) ≈ ATE(population) ≈ Effect on never-takers**

All three equalities fail under realistic assumptions.

**Effect on never-takers in particular:** The experiment provides no direct estimate of what happens to never-takers when the feature is force-enabled. There are at least three scenarios:

1. **Neutral or small positive effect:** Force-enabling creates modest revenue uplift because some never-takers find latent value once the friction is removed. Revenue uplift is real but much less than $32.

2. **Near-zero effect:** Never-takers ignore or immediately disable the feature. Revenue is unchanged. The $32 extrapolation is wrong by construction.

3. **Negative effect:** Force-enabling creates product friction, reduces satisfaction, or triggers churn among users who disliked the imposition. Revenue per user falls. The $32 extrapolation is not only wrong in magnitude but wrong in sign.

Scenario 3 is not exotic — there is substantial evidence from product literature that forced feature activation without user intent can harm engagement, particularly for premium features where the "premium" framing creates expectation mismatch.

---

## Step 6: Quantitative Illustration

Let's bound the expected revenue effect of forced rollout with simple arithmetic.

Assumptions for a rough calculation:
- Population split: 82% never-takers, 15% compliers, 3% always-takers
- LATE for compliers: +$32
- Effect on never-takers: unknown (let's call it δ)
- Always-takers already adopted; force-enable has no marginal effect on them

**Expected population-level effect of forcing adoption on all non-adopters:**

```
E[Revenue uplift] = (fraction compliers among non-adopters) × $32 + (fraction never-takers among non-adopters) × δ
```

Among non-adopters (the target of force-enable):
- Compliers are ~15/85 ≈ 18% of non-adopters
- Never-takers are ~82/85 ≈ 96% of non-adopters

So even if never-takers get *half* the complier benefit (δ = $16):

```
E[uplift] = 0.18 × $32 + 0.82 × $16 = $5.76 + $13.12 = $18.88
```

Even in this optimistic scenario, population uplift is ~$19, not $32. If δ = $5:

```
E[uplift] = 0.18 × $32 + 0.82 × $5 = $5.76 + $4.10 = $9.86
```

If δ = 0 (never-takers get no value):

```
E[uplift] = 0.18 × $32 = $5.76
```

If δ = -$10 (net negative for never-takers due to friction/churn):

```
E[uplift] = 0.18 × $32 - 0.82 × $10 = $5.76 - $8.20 = -$2.44
```

**The $32 figure requires δ = $32, which would require never-takers to benefit as much as compliers — contradicted by the very behavioral data that defines their type.**

---

## Step 7: What the CEO Is Actually Asking and What the Right Estimand Is

| Decision | Right estimand | Available? |
|----------|---------------|------------|
| Should we send more notifications? | LATE for compliers | Yes — $32 is exactly this |
| What's the value of reducing adoption friction (UI changes)? | Approximate LATE (if friction removers look like notifications) | Probably yes, with caveats |
| What happens if we force-enable for everyone? | ATE across full population, or specifically effect on never-takers | Not identified from this experiment |

The experiment was designed to answer the notification question. Extrapolating to forced rollout requires an additional assumption — that the treatment effect is homogeneous across complier and never-taker types — which the design cannot validate and which the behavioral data contradicts.

---

## Step 8: What to Do Instead

**Option 1: Run a forced-enable A/B test directly.**
Randomly force-enable the feature for a holdout group of non-adopters and measure 6-month revenue. This directly estimates the effect of the intervention the CEO actually wants. This is the cleanest answer.

**Option 2: Instrument the never-taker subgroup.**
Within the never-taker group, check if any variation in notification intensity or timing created sub-variation in adoption. This is typically low-power but can bound δ.

**Option 3: Use the complier characteristics to predict heterogeneity.**
Profile compliers vs. never-takers on observable dimensions (engagement level, product tier, usage patterns). If compliers look like a specific segment of never-takers, the $32 effect may generalize to that segment — but not to all never-takers.

**Option 4: Run the forced-enable on a small cohort first.**
Before committing to a full rollout, force-enable for 5-10% of non-adopters and measure revenue, engagement, and churn signals at 30/60/90 days. The marginal cost of this information is low relative to the decision size.

---

## The Most Likely Trap Being Walked Into

The core trap here fits the skill's explicit warning about **LATE vs. ATE extrapolation from opt-in experiments**:

> "Opt-in / self-selected experiments estimate the ATT (effect among those who chose in), not the ATE (effect if rolled out to everyone). When heterogeneous effects and self-selection are plausible, these differ substantially — and rollout decisions usually require the ATE."

The IV estimate here is even narrower than the ATT — it's the LATE for compliers, which excludes the always-takers (who would have adopted regardless) and gives zero weight to never-takers (who are precisely the target of the force-enable).

There is also a **downstream indicator** framing risk: the adoption behavior of never-takers revealed by the experiment is meaningful signal about the quality of fit between those users and the feature. Forcing adoption doesn't change the underlying fit — it changes the surface behavior while potentially damaging the user experience for people who weren't ready for the product. This is analogous to the churn/login example: treating the symptom (non-adoption) without addressing the underlying cause (feature-user mismatch or low engagement).

---

## Summary

| Question | Answer |
|----------|--------|
| Is $32 the right expectation for forced rollout? | No. It almost certainly overstates the effect, possibly substantially. |
| What does $32 actually measure? | The revenue lift for the ~15% of users who are on the adoption margin (compliers). |
| Why doesn't it apply to never-takers? | Never-takers revealed through the experiment that they don't want the feature. Their effect is likely much smaller, possibly negative. |
| What would be needed? | A direct forced-enable experiment or CATE estimates broken down by behavioral segment. |
| What's the safe action? | Run a small forced-enable holdout, measure 30/60/90-day revenue and churn before scaling. |

The encouragement design was the right instrument for evaluating the notification strategy. It is not the right instrument for evaluating forced rollout — those are different interventions, targeting different populations, with potentially very different effects.
