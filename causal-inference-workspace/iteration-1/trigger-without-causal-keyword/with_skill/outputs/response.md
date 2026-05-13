# Does the new onboarding flow improve 30-day retention?

## Rung: This is a Rung 2 (Intervention) question

You're asking "did doing X (shipping the new onboarding flow) change Y (30-day retention)?" That's a rung-2 question — it requires intervention-level reasoning, not just association. The trap you're already sensing is exactly the right one: observing that retention went up *after* the launch doesn't answer whether the flow *caused* it. Post-launch data is rung-1 (association). You need a rung-2 strategy to answer a rung-2 question.

---

## Sketch the DAG

Here's the minimal causal diagram for your situation:

```
   U (time, seasonality, other product changes, macro)
   ↙                                     ↘
 Onboarding flow (X)  ──────────────────→  30-day retention (Y)
```

More completely:

```
   U1 (cohort quality: who signed up during rollout)
   ↙                      ↘
 Onboarding flow (X) ──→  30-day retention (Y)
                               ↑
   U2 (other product changes shipped at the same time)
```

**X** = which onboarding flow the user experienced (new vs. old)  
**Y** = 30-day retention  
**U1** = cohort characteristics (acquisition channel mix, marketing campaign quality, seasonality)  
**U2** = other simultaneous changes (other product improvements, support changes, pricing)

The back-door paths are X ← U1 → Y and X ← U2 → Y (or more precisely: U2 coincidentally correlates with the timing of X). These are the confounders. Without closing them, any observed improvement in Y could be entirely explained by U1 or U2, not by X itself.

---

## Identify the structure

The core problem is a **fork (confounder)**:

```
   U (cohort quality / other changes)
   ↙                ↘
  X                  Y
```

Users who got the new flow are different from users who got the old flow — they signed up *later*, during a different time period, possibly through different channels, into a product that may have changed in other ways. Even if the new flow has zero effect, retention could look better just because you're comparing better-quality cohorts from a more mature product.

This is the "better numbers after launch" trap. It's textbook **confounding by time and cohort**, and it will fool a naive before/after comparison every single time.

---

## Pick a strategy

**Best option: Run a proper A/B test (Rung-2 by design)**

If you haven't already shipped to 100% of users, split incoming users randomly between old and new flow. Compare 30-day retention for both groups from the same time period. Randomization eliminates the confounders by construction — both groups are drawn from the same cohort, same time window, same product state. The simple difference in retention rates is an unbiased estimate of the flow's causal effect.

**If the new flow is already at 100% and you can't run an A/B test:**

Use **Differences-in-Differences (DiD)**:

```
ATE = (retention_new_flow_post − retention_new_flow_pre) − (retention_control_post − retention_control_pre)
```

You need a control group that didn't receive the new flow but was observed over the same window. Options:
- Users in a geography or platform (e.g., Android vs. iOS) where the new flow hasn't rolled out yet
- A segment excluded from the rollout for operational reasons

The key assumption is **parallel trends**: the control group's retention trajectory would have matched the treated group's trajectory in the absence of the new flow. Check pre-period trends — if retention was already diverging before launch, DiD breaks down.

**If you have no control group at all:**

You're stuck with a **before/after comparison**, which is rung-1. You can still add rigor:
- Measure and control for observable cohort differences (acquisition channel, device, plan tier) — this is back-door adjustment for U1
- Isolate the rollout date and plot retention week-by-week to check for a visible discontinuity at the launch date (a rough regression discontinuity)
- Run a **sensitivity analysis**: how large would the unmeasured confounder (cohort quality improvement) need to be to fully explain the observed retention lift? If the answer is "implausibly large," the flow is the more credible explanation

---

## The most likely trap to flag

**Confounding by cohort and time.** Users who signed up after you launched the new flow are simply a different population than those who signed up before. If acquisition quality improved, if a better marketing campaign ran, if another product feature shipped at the same time, if it's a different season — all of these can produce a retention lift that has nothing to do with onboarding.

A secondary trap: **Collider conditioning if you segment on engaged users.** If you look only at "users who completed onboarding" to compare old vs. new flow performance, you've conditioned on a downstream variable affected by both the flow *and* user quality. That's collider stratification — it can make a harmful flow look beneficial (or vice versa). Compare groups based on *assignment* to the flow, not on completion.

---

## What would change the answer

- **If you ran a true A/B test with random assignment**: you can trust the result directly. Check that randomization was properly implemented (SRM test) and that the groups had similar pre-experiment characteristics.
- **If the parallel-trends assumption in DiD fails** (the two groups were already diverging before rollout): the DiD estimate is biased in the direction of the pre-existing divergence.
- **If another major change shipped on the same day as the new flow**: the effect is confounded and not attributable to the flow alone without further isolation.
- **If the retention lift is concentrated in a specific cohort or segment**: this suggests heterogeneous treatment effects, and the average lift may not generalize. Use segment-level analysis (CATE) to see where the flow works and where it doesn't.

---

## Bottom line

The numbers looking better after launch is rung-1 evidence for a rung-2 question. To be confident it's the flow, you need either (a) an A/B test with proper randomization — the cleanest answer — or (b) a DiD design with a credible control group and parallel pre-trends. Without one of these, you can make the observational evidence *more* credible through back-door adjustment and sensitivity analysis, but you can't rule out that a better incoming cohort or a simultaneous product change is doing the work.
