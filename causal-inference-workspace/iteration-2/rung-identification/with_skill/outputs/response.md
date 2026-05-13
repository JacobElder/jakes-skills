# Does the new onboarding flow actually improve 30-day retention?

## Step 1: Name the rung

Your question — "is the new onboarding flow *actually causing* better retention?" — is a **Rung 2 (intervention) question**. You want to know the effect of *doing* something (shipping the flow) on an outcome, not merely what correlates with retention.

The data you currently have — "the numbers look better since we shipped it" — are **Rung 1 (association) data**. Retention went up around the time the flow shipped. That is a correlation. Without additional causal reasoning, you cannot conclude the flow is responsible.

This gap — using Rung 1 data to answer a Rung 2 question — is the core of your uncertainty, and it is the right instinct to feel uncertain about it.

---

## Step 2: Sketch the DAG

Here is the minimal causal structure to reason about:

```
   Confounders (C)
    ↙         ↘
Onboarding    30-day
Flow (X)  →  Retention (Y)
```

C represents any variables that independently affect both who received the new flow *and* retention rates. These create back-door paths — spurious associations between X and Y that have nothing to do with the flow's causal effect.

What might C include in your situation?

- **Time / seasonality.** If you launched during a period when users are naturally more engaged (a major marketing push, a seasonal high, a new product announcement), both the new flow and improved retention are downstream of the same timing.
- **User cohort quality.** If the mix of users acquiring your product changed around launch — you ran a different ad campaign, changed pricing, attracted a higher-intent segment — those users would have had better retention regardless of the flow.
- **Co-shipped product changes.** Did other teams ship features, fix bugs, or change the experience in the same release window? Any simultaneous change is a confounder.
- **Novelty / attention effects.** Your team may have been more attentive to new users around launch (closer monitoring, faster support responses), improving retention independently of the flow content.

There are also two structural variants worth flagging explicitly:

**Mediator trap.** Suppose you collected an intermediate metric — say, "completed first key action" — and want to control for it. If "completed first key action" is *caused by* the new onboarding flow, it is a mediator (`Flow → Key Action → Retention`). Controlling for it would block the very effect you are trying to measure. Do not include it as a control variable.

**Selection / collider trap.** If your retention analysis is scoped to users who reached a certain onboarding step, you may have conditioned on a collider. Users who complete step 3 of onboarding are selected by both engagement (which predicts retention) and flow quality — conditioning on them creates spurious correlations.

---

## Step 3: Identify the structure and threats

Every confounder above creates an open back-door path:

```
Onboarding Flow ← [Time / Cohort / Co-shipped change] → Retention
```

These paths carry spurious association. The retention improvement could be entirely explained by the confounder rather than the flow.

Per-variable classification for common candidates:

| Variable | Structural role | Verdict |
|---|---|---|
| Acquisition channel / cohort mix | Fork (confounder) | Control for it |
| Signup date / time period | Fork (confounder) | Control for it or use DiD |
| Feature adoption rate | Mediator | Do NOT control |
| "Completed onboarding" | Mediator / descendant | Do NOT condition the analysis on it |
| User device / platform | Confounder if rolled out differentially | Control or use as comparison group |

---

## Step 4: Pick an identification strategy

In order of preference:

### Option A: Randomized A/B test (cleanest)

Randomly assign new users to old flow (control) versus new flow (treatment). Hold everything else constant. Measure 30-day retention. The difference in means is an unbiased estimate of the average treatment effect (ATE).

Randomization closes all back-door paths by construction — every confounder above is balanced across arms.

One nuance: if users self-select deeper engagement with the new flow (e.g., optional steps), your estimate drifts toward the **ATT** (effect among those who engaged), not the **ATE** across all users. For a rollout decision, you want the ATE.

If you have already fully shipped and cannot randomize, this option is closed for the current cohort — but it is the right design for future launches.

### Option B: Differences-in-differences (DiD)

If any group of users did NOT receive the new flow at the same time as the main cohort — a different geography, platform, user segment, or a holdback group — you have a natural control group and DiD is available.

```
DiD estimate = (retention_treated_post − retention_treated_pre)
             − (retention_control_post − retention_control_pre)
```

The key assumption is **parallel trends**: absent the new flow, the treated and control groups would have followed the same retention trajectory. This neutralizes time-based confounders and cohort effects shared by both groups.

**How to test it:** plot the pre-launch retention trend for both groups. If they were tracking together before launch, the parallel-trends assumption is plausible. If they were already diverging, DiD will mislead you.

DiD cannot handle factors that differentially affected *only* the treated group at exactly the time of launch — for example, if a co-shipped feature was also only seen by the treated segment.

### Option C: Regression adjustment on measured confounders

If you have no clean comparison group, you can attempt to statistically adjust for measurable confounders:

```
Retention ~ NewFlow + AcquisitionChannel + UserSegment + SignupWeek + ...
```

The coefficient on `NewFlow` estimates the causal effect conditional on those confounders being a valid adjustment set.

**The honest limitation:** this only works if you have measured *all* the important confounders. Any unmeasured confounder that affects both exposure and retention biases the estimate. Since the main confounders here are largely time-based (cohort quality, seasonality), and time is hard to fully adjust for parametrically, treat a regression-only estimate as suggestive rather than definitive.

Also: do not interpret the coefficients on the control variables as causal effects of those variables. Only the focal coefficient (the `NewFlow` term) is identified by this design. This is the Table 2 Fallacy — the other coefficients describe model fit, not causal effects of those variables.

### Option D: Not identifiable — honest acknowledgment

If you have a simple before/after number, no comparison group, and limited confounder data, the causal effect is **not identifiable** from your current data. The right answer is to say: "We see a lift. We do not know how much of it is the flow versus other factors. Here is what we need to be confident." Then design a confirmatory experiment.

---

## Step 5: The most likely trap

Given the framing — "numbers look better since we shipped it" — you are almost certainly looking at a **simple before/after comparison with no control group**. This is a back-door path problem. The same moment that brought the new flow also brought different users, a different season, different co-shipped features, or different operational attention.

A quick diagnostic: pull the acquisition source breakdown and user segment mix for the cohort that got the new flow versus the prior cohort. If the mix is meaningfully different, you have direct evidence of a confounder — and the retention lift could be entirely explained by getting better users, not giving them a better flow.

The other high-probability trap: **regression to the mean**. If you shipped the new onboarding because retention was looking bad, natural mean-reversion will look like an improvement in the post-period regardless of what the flow does.

---

## Step 6: Alternative DAG interpretations and what they imply

Being explicit about structural alternatives is the most useful thing here:

| If this is the DAG | The correct estimate | What to do |
|---|---|---|
| Flow is the only thing that changed; cohorts are comparable | Causal effect of the flow | Before/after comparison is valid — verify by auditing the release and checking cohort similarity |
| User cohort quality also changed at launch | Biased (upward if better users) | Adjust for acquisition source and segment mix |
| Seasonality or marketing campaign also changed | Time-confounded | Use DiD with a comparison group; if no group, regression adjust for time |
| Multiple things changed simultaneously | Likely not identifiable from pre/post alone | Need an A/B test or natural control group |
| Users who engaged more with new flow had higher pre-existing intent | Mediator / selection conflation | Estimate ATE from a randomized design rather than ATT from engagement |

If pulling your release log shows that nothing else shipped in that window and your acquisition mix is stable across cohorts, the DAG simplifies considerably and a regression adjustment becomes much more credible. If those things changed, adjustment alone will not save you.

---

## Bottom line

You are asking a Rung 2 question with Rung 1 data. The right moves:

1. **Immediately: audit the release.** What else shipped in the same window? Did user acquisition mix change? Did you run any campaigns? This tells you how bad the confounder problem is.

2. **Check for a natural control group.** Did any segment — a platform, geography, user type — receive the new flow later or not yet? If yes, run a DiD analysis with the pre-period trend as your validity check.

3. **If a control group exists:** plot pre-launch trends for both groups. If they were tracking together, run DiD. That is the fastest path to a defensible causal estimate from existing data.

4. **If no control group exists:** run a regression adjusting for acquisition channel, user segment, and signup week. Treat the result as suggestive, not confirmed. Report the limitation.

5. **Going forward:** instrument every significant flow change with an A/B test before full rollout. A 30-day holdback of 5–10% of users gives you the control group DiD needs for future launches and avoids this uncertainty entirely.

The numbers looking better is real information — it is evidence *consistent with* the flow helping. It is not conclusive evidence that the flow *caused* the improvement. The gap between "consistent with" and "caused by" is exactly what the strategies above close.
