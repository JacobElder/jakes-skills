# Predictive Feature Importance vs. Causal Intervention Targets

## Short answer: No. Feature importance from a predictive model cannot tell you what to intervene on.

Your 92% AUC model is a rung-1 tool answering a rung-1 question: "Given what I observe, how likely is this customer to churn?" Marketing's question — "which variables should we act on to reduce churn?" — is a rung-2 question: "What happens if we *do* something?" No amount of predictive accuracy bridges that gap without additional causal assumptions.

This is one of the most common and costly mistakes in applied ML: mistaking a variable that *predicts* an outcome for a variable that *causes* it. The feature importance ranking tells you what variables are statistically associated with churn, not which ones, if changed, would reduce churn. Intervening on a predictor that isn't a cause can be useless or actively counterproductive.

---

## Why each top feature needs causal scrutiny

The right move is to sketch a DAG for each feature and classify its structural role. Here is what that looks like for the four features you listed.

### 1. `account_age`

**Likely role: a proxy or a confounder — probably not an actionable lever.**

Account age is almost certainly a strong predictor of churn because older accounts have survived longer, implying a selection effect. The causal structure is probably:

```
   customer_quality → account_age
   customer_quality → churn (inversely)
```

Customers who weren't a good fit churned early; long-tenured accounts are survivors. Account age is high because they didn't churn, not a cause of why they don't churn. Intervening on account age is incoherent — you can't make a new account look old. Even if there is a genuine "loyalty effect," it likely runs through mediators like product familiarity or switching costs, not account age per se.

**Verdict: Do not intervene. Likely a proxy/symptom, not a cause.**

### 2. `last_login_days` (days since last login)

**Likely role: a mediator or a symptom — potentially actionable, but direction of causation is ambiguous.**

This variable could be either:
- **A mediator:** disengagement causes infrequent logins, which causes churn. `Dissatisfaction → last_login_days → churn`. In this case, you can intervene on logins (re-engagement campaigns, push notifications), but you're only addressing a downstream symptom. You'd also want to ask what caused disengagement.
- **A collider or spurious marker:** low login frequency and churn share a common cause (e.g., competitor pricing, life change, unresolved support issue). In that case, driving logins via notifications may not reduce churn — it changes the symptom without touching the cause.

The two structures predict very different outcomes from a re-engagement campaign. In the mediator world, login nudges reduce churn. In the common-cause world, you get more logins and the same churn rate.

**The diagnostic:** run an A/B test. Randomly send re-engagement notifications to a subset of low-login customers and measure churn — not logins. If you only measure logins, you've confirmed the intervention works on a proxy, not on the outcome you care about.

**Verdict: Potentially actionable, but requires a test to establish causation. Don't assume high importance = causal.**

### 3. `support_tickets`

**Likely role: a mediator or bidirectional indicator — interventions here are plausible but nuanced.**

More support tickets likely signals product pain or unresolved problems. The causal structure could be:

```
   Product issues → support_tickets → churn
```

If so, resolving support issues faster or more completely is a genuine lever on churn. But two complications arise:

- **Direction of causation matters.** Do support tickets cause churn by creating friction? Or do customers who are already planning to churn open tickets as part of their exit behavior (refund requests, cancellation inquiries)? If the latter, faster resolution may not help.
- **Type of ticket matters.** Technical problems vs. billing disputes vs. cancellation requests are structurally different paths to churn. Aggregating them under one feature hides this.

**Verdict: Likely actionable, but you need to disaggregate ticket type and test whether resolution quality changes churn — not just whether tickets correlate with it.**

### 4. `pricing_tier`

**Likely role: a potential confounder or a true lever — but confounded by selection.**

Pricing tier is strongly confounded by customer type. Customers on lower tiers may churn more because:
- They're smaller businesses with higher failure rates (a confounder: company_size → pricing_tier, company_size → churn).
- The lower tier is genuinely insufficient for their needs (a causal path: pricing_tier → unmet_needs → churn).

If it's the former, downgrading customers to save them money would be useless or harmful. If it's the latter, proactively moving customers to a better-fit tier or offering relevant features could reduce churn.

**Verdict: Plausibly actionable, but confounded by selection into tiers. The right analysis is an experiment — e.g., a targeted upgrade offer to a random subset of at-risk lower-tier customers — not observational modeling.**

---

## The structural trap: Predictive accuracy != causal validity

Your model's 92% AUC means it has found variables that are highly *associated* with churn. That's useful for *scoring* who to target (prediction). It's not evidence that changing those variables will *cause* churn to change.

The SKILL.md framework names this directly: "Predictive accuracy ≠ causal validity. A model that predicts well can give wildly wrong answers about what to do. ZIP code may predict default, but lending policy based on it doesn't intervene on the cause."

The feature importance ranking also does not map to causal effect size. A feature can be the single most important predictor and have zero causal effect — because it's downstream of the cause, or it's a proxy for something unmeasured, or both X and Y are effects of a common cause. Importance scores measure predictive contribution, not causal magnitude.

---

## What to do instead

### Step 1: Build a DAG before running experiments

For each of the four features, sketch the plausible causal structures. Be explicit about:
- What causes this variable to be high or low?
- Does this variable cause churn, or do they share a common cause?
- Could this variable be a symptom (downstream of churn intention) rather than a cause?

This exercise will reveal which variables have plausible causal pathways and which are likely non-starters.

### Step 2: Prioritize by actionability and causal plausibility

| Feature | Causal plausibility | Actionability | Priority |
|---|---|---|---|
| `account_age` | Low — likely proxy/selection artifact | None (can't manipulate) | Do not intervene |
| `last_login_days` | Medium — plausible mediator | Moderate (re-engagement) | Test, don't assume |
| `support_tickets` | Medium-high — plausible mediator | High (resolution quality) | Test with ticket disaggregation |
| `pricing_tier` | Medium — confounded by selection | Moderate (upgrade offers) | Test with targeted offer |

### Step 3: Run experiments, not regressions

For each plausible lever, design a randomized intervention:
- **`last_login_days`:** Randomly assign re-engagement notifications. Measure churn at 30/60/90 days. Do not measure logins as a success metric.
- **`support_tickets`:** Randomly assign enhanced resolution (faster response, dedicated handler) to a subset of high-ticket customers. Measure churn.
- **`pricing_tier`:** Randomly offer tier upgrades to at-risk lower-tier customers. Measure churn vs. a holdout.

The predictive model is still useful here: use it to identify the *population* to target for experiments (customers with elevated churn probability). Do not use it to decide *what to change*.

### Step 4: Use the predictive model for targeting, not for intervention design

The 92% AUC model is excellent for identifying *who* is at risk. That's a rung-1 question and you've answered it well. The rung-2 question — *what to do* — requires experiments. The model feeds the experiment funnel; it doesn't replace it.

---

## Summary

Feature importance from a churn model answers the question "what predicts churn?" not "what causes churn?" The gap between these is the entire discipline of causal inference. For the four features listed:

- `account_age`: almost certainly not a causal lever; likely a selection artifact
- `last_login_days`: possibly causal, but requires an experiment to confirm
- `support_tickets`: probably causal for a subset of ticket types; test disaggregated
- `pricing_tier`: plausible but confounded by customer type; test with upgrade offers

The correct workflow is: use the predictive model to score risk and identify intervention targets, then run randomized experiments to establish which interventions actually reduce churn. The model is an input to experiment design, not a substitute for it.
