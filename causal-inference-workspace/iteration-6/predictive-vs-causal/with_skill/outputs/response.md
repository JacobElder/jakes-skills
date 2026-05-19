# No — feature importance does not tell you what to intervene on

## The core problem: you are asking a rung-2 question with rung-1 tools

Your model answers a **rung-1 (association) question**: "Given what I observe about a customer, what is the probability they churn?" A 92% AUC is a genuine achievement at this task.

But marketing's question — *which variables should we intervene on?* — is a **rung-2 (intervention) question**: "If we do X to a customer, what happens to their churn probability?" These are categorically different questions. No amount of predictive accuracy at rung 1 answers rung 2. Feature importance tells you what variables carry information about the outcome *in the world as it is*. It says nothing about what happens when you reach in and change those variables.

The do-operator makes this precise:

- `P(churn | last_login_days = 30)` — the churn rate among customers who *happen* to have 30-day login gaps
- `P(churn | do(last_login_days = 30))` — the churn rate if you *force* a customer to log in every 30 days

These are different quantities. Feature importance estimates the first. You need the second.

---

## A DAG for each feature: who is upstream and who is downstream?

Let me sketch the structural role of each feature in a plausible DAG, then apply the intervention test.

### account_age

**Structural role: upstream cause of churn (plausibly)**

Account age is largely fixed — customers accumulate it passively, and you cannot meaningfully intervene on it. But it is causally prior to churn (older accounts have had more time to experience events that drive churn or loyalty). It is a valid *targeting signal*: customers at certain tenure points may have different risk profiles. You can use it to identify who to contact, but there is nothing to intervene on. Age-based segmentation is rung 1 applied usefully; it does not become a lever just because it predicts.

### last_login_days

**Structural role: downstream indicator — a symptom, not a cause**

This is the clearest trap in your feature set. Days since last login predicts churn well precisely because disengaged customers stop logging in *before* they cancel. The causal direction runs:

```
Underlying disengagement → infrequent logins → churn
                        ↘                    ↗
```

The login gap is an effect of the disengagement state that also causes churn. It is a **downstream indicator** — a symptom with a common cause, not the cause itself.

The intervention implication is direct: a re-engagement campaign that gets someone to log in more often (say, email nudges or in-app notifications) will move `last_login_days` without necessarily touching the underlying disengagement. The predictive model says "low logins → high churn." The causal truth is "disengagement → low logins AND churn." Treating the symptom does not fix the disease.

`P(churn | do(last_login_days = 7))` — forcing weekly logins via nudges — is likely much smaller than the feature importance implies, possibly near zero if the underlying disengagement is unchanged.

**Verdict: valid targeting signal (who to act on); not a valid intervention target (what to change).**

### support_tickets

**Structural role: ambiguous — requires structural investigation**

Support tickets could be a **cause** of churn or a **downstream indicator**, depending on what drives them:

- If customers file tickets because the product is broken or confusing, the tickets signal a problem that the company can fix. Here the causal chain is: `product friction → tickets → churn`, and intervening on product friction (upstream) is the lever. Tickets are still a symptom, but they point at a fixable cause.
- Alternatively, `underlying dissatisfaction → tickets AND churn` — tickets are again a downstream indicator of a latent state.
- A third possibility: tickets could be part of a **protective path** (customers who file tickets are more engaged, or they get support that resolves their issue, reducing churn). In this case the correlation might be positive (more tickets predicts more churn) even though the intervention effect is negative or zero.

The predictive model cannot distinguish these structures. To determine whether reducing ticket volume (by fixing product issues) would reduce churn, you need a causal model of what generates tickets in the first place.

**Verdict: ambiguous. Tickets are a potential causal pathway indicator — worth investigating structurally. Do not assume intervention on tickets directly reduces churn without additional evidence.**

### pricing_tier

**Structural role: upstream cause — potentially a real lever**

Pricing tier is typically set *before* churn and is not caused by churn (the reverse is implausible unless tier assignment is endogenous to engagement signals). This makes it the most plausible upstream causal variable in your set.

The structural story: `pricing_tier → value perception → retention probability`. If customers on higher-cost tiers are churning more because the price-to-value ratio is unfavorable, changing pricing (discounts, tier migration, feature bundling) could directly affect churn.

**Caveats:**
- Selection into pricing tiers is not random. High-tier customers may differ from low-tier customers in ways that explain churn independent of the price. The correlation in the model is a mix of the causal price effect and selection differences. You need to adjust for (or design around) those confounders to estimate the actual treatment effect.
- If you could run a pricing experiment — randomly offer some high-tier customers a discount or tier migration — you would get a clean rung-2 answer. Observational data alone requires back-door adjustment on whatever drove tier assignment in the first place.

**Verdict: most promising intervention candidate, but requires causal identification work (ideally an experiment) before concluding the effect is large.**

---

## What you should actually do

**Step 1: Separate targeting from intervention.**

Use the model for what it is good at: identifying which customers are at risk. High-probability-of-churn customers are valid targets for intervention. That is a legitimate rung-1 use. Do not conflate "this feature predicts churn" with "this feature is a lever."

**Step 2: Build a causal model of churn.**

Sketch a DAG with your domain knowledge:
- What are the underlying states that drive churn? (Pricing dissatisfaction, product friction, lifecycle stage, competitive alternatives, disengagement.)
- Which of your measured variables are upstream causes of those states vs. downstream symptoms?
- What are the unobserved confounders (e.g., customer need-fit, company size, alternatives available)?

**Step 3: Test the most promising upstream lever — pricing_tier — causally.**

Design an experiment: randomly offer at-risk customers (identified by your predictive model) a tier migration or discount. Compare churn over 90 days. This gives you `P(churn | do(pricing_tier = lower))` directly.

**Step 4: Investigate what drives support tickets.**

If ticket volume reflects product-specific friction points, fixing those upstream problems is the real lever. Analyze ticket content to find the proximate causes. Then intervene on those (product fixes, onboarding improvements), not on ticket counts.

**Step 5: Do not build a re-engagement campaign based on login frequency as the lever.**

If you invest in forcing logins (in-app nudges, email re-engagement with no substantive content), you will move the feature without moving churn. The metric will look better; the business outcome will not follow. Identify what the login gap is a symptom of and intervene there.

---

## Summary

| Feature | Causal role | Intervention target? |
|---|---|---|
| account_age | Causally prior, not manipulable | No — use as targeting signal |
| last_login_days | Downstream indicator (symptom of disengagement) | No — targeting signal only; treating this directly is a trap |
| support_tickets | Ambiguous — symptom or upstream signal | Investigate structurally; do not intervene on ticket count |
| pricing_tier | Upstream causal candidate | Yes — but requires causal identification (experiment preferred) |

The 92% AUC is valuable for *who to target*. To know *what to do*, you need a causal model. Feature importance from a predictive model is not a causal model, and substituting one for the other is one of the most common and consequential analytic errors in applied machine learning for business decisions.
