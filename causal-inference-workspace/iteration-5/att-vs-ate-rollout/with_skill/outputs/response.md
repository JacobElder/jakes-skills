# LATE vs. ATE: Why the CEO's $32 Rollout Expectation Is Almost Certainly Wrong

**Short answer:** No. The $32 LATE estimate applies to a specific, self-selected subgroup — users who adopted the feature *because* they received the notification and wouldn't have otherwise. Force-enabling the feature for the remaining non-adopters is a fundamentally different population, and the effect on them is almost certainly lower, possibly zero or even negative. The CEO is conflating three different causal estimands.

---

## Step 1: Name the Rung

This is a **Rung 2 (intervention)** question: "What will happen if we *do* X to this population?" The CEO is trying to use an IV estimate to predict the outcome of a new intervention — a force-enablement rollout. That's exactly the right rung, but the IV estimate doesn't answer the right version of the question. The LATE is a Rung 2 answer to a *different* Rung 2 question.

---

## Step 2: Sketch the DAG and Population Structure

The encouragement design creates a clear population segmentation. With 30% notified and the adoption rates you describe, here is who's in the data:

```
Notification (Z) --> Feature Adoption (X) --> 6-month Revenue (Y)
                                   ^
                                   |
                         Unobserved heterogeneity
                         (willingness, need for
                          the feature, tech savvy)
                                   |
                                   v
                                   Y
```

- **Z (notification):** Randomly assigned. Valid instrument: it causally affects adoption (X), and its only path to revenue (Y) is through adoption (exclusion restriction). Random assignment ensures no common cause with Y.
- **X (adoption):** The treatment. Confounded by unobserved user preferences — users who want the feature are both more likely to adopt and more likely to generate revenue from it.
- **U (user preferences/motivation):** Unobserved. Creates the confounding that makes naive comparison of adopters vs. non-adopters biased, and is exactly why the IV design was needed.

The IV design uses Z to isolate exogenous variation in X, sidestepping the U confounder. That's valid. The problem is *which users* that variation identifies.

---

## Step 3: Who Are the Compliers? (And Why That's Everything)

Under the standard IV / encouragement-design monotonicity assumption, users partition into three latent types:

| Type | Behavior with notification | Behavior without notification | Estimated share |
|------|---------------------------|-------------------------------|-----------------|
| **Compliers** | Adopt | Don't adopt | ~15% of notified group |
| **Always-takers** | Adopt | Adopt | ~3% |
| **Never-takers** | Don't adopt | Don't adopt | ~82% |
| **Defiers** | Don't adopt | Adopt | ~0% (assumed away by monotonicity) |

**Working out the numbers from your data:**

- Non-notified adoption rate = 3%. This is the **always-taker rate** — they adopted without any nudge.
- Notified adoption rate = 18%. The extra 15 percentage points (18% − 3%) is the **complier share** among the notified group — the users whose adoption was *caused* by the notification.
- The ~82% who didn't adopt even with a notification are the **never-takers**.

**The LATE of +$32 is the average treatment effect for compliers only.** By the Wald estimator:

```
LATE = ITT_revenue / First-stage
     = (mean revenue difference: notified vs. control) / (18% − 3%)
     = $32
```

This $32 is entirely a statement about a 15% slice of your user base — people who were on the fence and could be nudged into adoption by a push notification. They are, by construction, the most persuadable users who still needed encouragement. They are not representative of the users who remain.

---

## Step 4: Why the Force-Enable Rollout Targets a Completely Different Population

The users the CEO wants to force-enable are overwhelmingly the **never-takers** — users who received (or, in expectation, would have received) a notification and still did not adopt. By the definition of their type, they actively chose not to use the feature even when directly invited.

Why don't never-takers adopt? Three plausible reasons:

1. **They don't want the feature.** It doesn't fit their use case, workflow, or preferences. Force-enabling produces $0 in incremental engagement — or a negative experience that increases churn.
2. **Friction beyond the notification.** Possible for some, but the notification was specifically designed to overcome awareness friction. If a direct push didn't move them, a forced enable will move only a small fraction.
3. **They're structurally lower-value users.** The unobserved U that correlates with adoption also correlates with revenue. Never-takers may simply generate less revenue in general. Even if force-enable raises feature usage, the revenue ceiling is lower.

The LATE explicitly excludes never-takers by construction. It identifies the effect for the complier stratum only. There is **no statistical or structural reason** to expect never-takers to respond like compliers — they are defined by the fact that they don't respond to nudges.

This is an **ATE vs. LATE confusion**. The CEO is implicitly treating the LATE as if it were the ATE (average over all non-adopters) or the ATT for the target population. It is neither.

---

## Step 5: The Structural Problem With "Force-Enable"

Beyond the population mismatch, the force-enable rollout changes the causal mechanism. The LATE was estimated from a design where:

- A user received an invitation.
- The user made an active choice to adopt.
- Adoption was voluntary and intentional.

Force-enable removes the choice entirely. Users who didn't want the feature now have it on anyway. This is a structurally different intervention with a structurally different causal graph — the pathway from "feature enabled" to "revenue" for a user who chose it vs. a user who had it imposed is not the same. Voluntary adoption predicts engagement; imposed enablement predicts resistance, ignore behavior, or friction.

This is not a minor caveat. The $32 LATE estimate does not speak to this new intervention at all.

---

## Step 6: The Direction and Magnitude of the Error

| Scenario | Expected per-user uplift from force-enable |
|----------|--------------------------------------------|
| Never-takers respond like compliers | ~$32 — CEO's assumption, almost certainly wrong |
| Never-takers mildly positive | $2–$8 — optimistic upper bound |
| Never-takers neutral | ~$0 |
| Never-takers net negative (friction, churn) | Negative |

The most defensible prior, absent further data, is close to $0, with material downside risk. The $32 figure is a ceiling estimate for a different population, not a floor estimate for this one.

---

## Step 7: What You Should Do Instead

**Run a direct A/B test on force-enable.** The encouragement design answered a different question. A direct experiment — randomly force-enable the feature for a subset of non-adopters and hold out a control group — would directly measure what the CEO wants to know. This is the clean Rung 2 answer, and it's feasible given you already have the infrastructure for randomized experiments.

**Before that test, segment the never-takers.** Not all never-takers are the same. Users who opened the notification but didn't convert are different from users who never opened it. Users who explored the feature page vs. users who showed zero engagement are different. Some never-taker segments may respond positively to a more aggressive enablement nudge; others will not. Targeting the more responsive segments reduces risk.

**Separate awareness from preference.** If users genuinely didn't know the feature existed (the notification was lost in noise), force-enable or a higher-visibility prompt may recover value. If users knew and actively declined, force-enable is overriding a preference signal. These are different situations requiring different interventions.

**Check the exclusion restriction on your LATE.** The IV estimate assumes the notification's only path to revenue is through adoption. If the notification itself re-engaged users (opened the app, browsed the product) independently of whether they adopted the feature, the exclusion restriction is violated, and the $32 is itself biased — potentially in either direction. This is a secondary concern but worth verifying.

---

## Summary Diagnosis

| Question | Answer |
|----------|--------|
| What does the $32 LATE represent? | The causal effect of feature adoption on 6-month revenue, identified for the complier subpopulation — users on the fence who were nudged to adopt by the notification. |
| Does it apply to never-takers? | No. Never-takers are defined as users who don't respond to nudges. Their response to force-enable is a separate, unmeasured quantity. |
| Is the CEO's expectation well-founded? | No. It conflates LATE with ATE for a different population and ignores that force-enable is a structurally different intervention from voluntary adoption. |
| What's the right expectation? | Unknown without a direct experiment. The defensible prior is substantially below $32, with meaningful probability of near-zero or negative effects. |
| What should happen next? | Run a randomized force-enable experiment on a subset of non-adopters before any broad rollout. |

The encouragement design gave you a valid, internally sound causal estimate. It just answered a different question than the one the CEO is now asking. That gap — LATE for compliers vs. ATE for non-adopting never-takers under a forced intervention — is the entire problem. Treat the $32 as a signal about your most persuadable users, not as a forecast for everyone else.
