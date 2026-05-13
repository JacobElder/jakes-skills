# Feature Importance Is Not a Guide for Intervention

## Short answer

No. Feature importances tell you which variables are the best predictors of churn. They cannot tell you which variables, if changed, would reduce churn. Those are two completely different questions sitting on different rungs of the causal ladder.

---

## The core problem: you are asking a rung-2 question with rung-1 tools

Pearl's Ladder of Causation has three rungs:

| Rung | Activity | Question | Tools |
|------|----------|----------|-------|
| 1. Association | Seeing | "What predicts churn?" | Correlation, ML, regression |
| 2. Intervention | Doing | "If we intervene on X, will churn drop?" | RCTs, do-calculus, back-door/IV |
| 3. Counterfactual | Imagining | "Would this customer have churned if we had acted differently?" | Structural causal models |

Marketing is asking a **rung-2 question**: "What should we intervene on?" Your 92% AUC model is a **rung-1 answer**: "What predicts churn?" A higher rung cannot be answered with rung-1 tools alone, regardless of how good the predictive performance is. The AUC tells you the model is well-calibrated for prediction; it says nothing about what will happen if you act on these variables.

---

## Feature-by-feature causal diagnosis

Here is how each of the four top features looks through a causal lens:

### 1. `last_login_days` — most likely an **effect** of impending churn, not a cause

This is the most dangerous one to act on. A customer who has already mentally decided to leave will stop logging in *before* they formally churn. The correct DAG is probably:

```
  Disengagement (latent) → last_login_days ↑
  Disengagement (latent) → Churn
```

`last_login_days` is a downstream symptom — a highly predictive **effect indicator** — not a lever. If marketing sends re-engagement emails triggered by high `last_login_days`, they are reacting to a signal that churn has already been decided. The intervention addresses the smoke, not the fire. This is the classic trap: **predictive accuracy does not equal causal validity**. A model can achieve 92% AUC by learning to detect the late-stage symptom pattern, even though those symptoms cannot be causally reversed once they appear.

### 2. `support_tickets` — ambiguous; could be a cause, an effect, or both

Two competing DAGs are plausible:

**Causal (bad experience drives churn):**
```
  Poor product quality → support_tickets → Churn
```

**Reverse causal (intending to leave, customers escalate issues):**
```
  Latent dissatisfaction → support_tickets
  Latent dissatisfaction → Churn
```

Feature importance cannot distinguish these. If it is the first structure, reducing ticket volume (by fixing the underlying product issues) would reduce churn. If it is the second, ticket volume is again a symptom. You need to know the mechanism before acting. The right move is to look at ticket *content* and *timing* relative to eventual churn, ideally with a DAG grounded in qualitative customer research.

### 3. `pricing_tier` — plausibly a genuine lever, but confounded

`pricing_tier` could have a direct causal effect on churn (higher price → higher churn), making it an actionable lever. But it is also a strong correlate of customer segment, customer expectations, product fit, and contract type — all of which independently drive churn. The association between `pricing_tier` and churn in the model almost certainly absorbs these confounds. Acting on price without accounting for them risks making a poorly targeted intervention.

If pricing is the candidate intervention, it needs to be evaluated with a proper experiment (A/B test on price changes) or a back-door adjustment that controls for the relevant confounders.

### 4. `account_age` — almost certainly not an actionable lever

Account age is a proxy for a customer's history with your product, trust level, and switching costs. You cannot directly intervene on account age. Its importance in the model reflects that newer customers churn more (or older customers have been filtered by the experience) — a correlation that doesn't help marketing decide what to do. It may be useful for **targeting** (knowing *who* to intervene on) but not for deciding *what intervention* to apply.

---

## The Table 2 Fallacy in your context

Feature importance in a trained model is the ML analogue of reading every coefficient in a regression as a causal effect. Each feature's importance reflects its contribution to prediction given all other features in the model. That contribution is shaped by confounding, mediation, reverse causation, and feature correlations — none of which the model cares about, because the model's job is prediction, not identification. Reading importance as "how much would intervening on this feature move churn?" is exactly the Table 2 Fallacy: using prediction coefficients as causal estimates.

---

## What to do instead

### Step 1: Draw a DAG before deciding what to measure or act on

Sketch, in prose or in a tool like dagitty.net, the plausible causal structure. For each top feature ask: Is this a cause of churn? A symptom? Both? A proxy for something else? Make the assumptions explicit. Even a rough qualitative DAG is more informative than 92% AUC for the intervention question.

A plausible starting DAG might look like:

```
  Product fit (latent)   → support_tickets → Churn
  Product fit (latent)   → last_login_days ↑
  Product fit (latent)   → Churn
  Pricing mismatch       → Churn
  Account age            → Switching costs → Churn (protective)
  Switching costs        ← Account age
```

### Step 2: Identify the genuine levers — variables where do(X) changes P(Churn)

Based on domain knowledge, the variables most likely to be genuine levers (upstream causes) are things like:

- **Onboarding quality** — does early product adoption prevent churn?
- **Product feature usage** — are customers getting value from the core features?
- **Pricing fit** — is the tier-to-value ratio misaligned for specific segments?
- **Support resolution quality** — does resolving support tickets quickly reduce churn, even if ticket volume stays constant?

These are upstream causes that have not been measured or modeled, and their absence from the feature importance list does not mean they are unimportant — it may simply mean they weren't included.

### Step 3: Run a causal analysis on the candidate levers

For each candidate lever:

**If an experiment is feasible (A/B test):** randomize the intervention and measure churn. This is the gold standard and the only thing that definitively answers the rung-2 question without relying on DAG assumptions.

**If observational data only:** use back-door adjustment. Identify confounders (variables that cause both the lever and churn), include them as covariates, and estimate the effect of the lever on churn. The coefficient on the lever is interpretable causally only if the back-door criterion is satisfied — that is, only if you have controlled for all the confounding paths.

**If experimentation isn't possible and key confounders are unobserved:** consider instrumental variables (a variable that affects the lever but has no direct effect on churn) or a differences-in-differences design if there is pre/post variation in the lever across customer cohorts.

### Step 4: Use the predictive model for targeting, not for deciding what to do

The 92% AUC model is genuinely valuable — but for a different task. It can be used to identify **which customers** are at risk so you can prioritize intervention resources. It should not determine **what intervention** to apply. Targeting (rung 1) and intervention design (rung 2) are separate problems requiring separate tools.

---

## Summary table

| Feature | Causal role (most likely) | Actionable as a lever? |
|---|---|---|
| `last_login_days` | Effect of churn / symptom | No — intervening on a symptom doesn't address cause |
| `support_tickets` | Ambiguous — cause or effect | Uncertain until DAG is drawn; investigate mechanism |
| `pricing_tier` | Plausible cause, but confounded | Requires proper experiment or back-door adjustment |
| `account_age` | Non-manipulable proxy | No — useful for targeting, not intervention |

---

## Bottom line

The 92% AUC tells you the model is excellent at prediction. It does not tell you what to do. Marketing's question — "which variables should we intervene on?" — requires identifying the upstream causes of churn, separating them from downstream symptoms (especially `last_login_days`), and estimating causal effects through designed experiments or valid observational methods with a credible DAG. Feature importance from a predictive model is not a substitute for this analysis, and acting on it directly risks investing heavily in interventions that address symptoms rather than causes.
