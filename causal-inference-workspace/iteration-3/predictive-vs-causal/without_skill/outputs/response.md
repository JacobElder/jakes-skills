# Can Feature Importances Guide Intervention Decisions?

**Short answer: No — not directly, and using them that way could lead marketing to waste money or make churn worse.**

---

## The Core Problem: Prediction vs. Causation

Your model was trained to *predict* churn, not to explain *what causes* churn. Feature importance tells you which variables were most useful for making accurate predictions. That is a very different question from "which variables, if we change them, will reduce churn?"

This distinction matters enormously for intervention decisions. A variable can be highly predictive and completely unactionable — or even harmful to act on.

---

## Walking Through Your Four Features

### 1. `account_age` — High predictive power, low intervention value

Account age is almost certainly a proxy for many underlying things: loyalty, product-market fit for a particular cohort, historical pricing, etc. You cannot make a customer's account older. Any attempt to use this for intervention would require you to figure out *what account age is actually proxying for* — and then target that underlying thing instead.

**Risk:** Segmenting by account age and treating it causally tells you nothing useful about what to *do*.

---

### 2. `last_login_days` — Predictive, but direction of causality is ambiguous

This is where things get interesting. There are at least two plausible causal stories:

- **Story A:** Customers who are about to churn disengage first (stop logging in), so low login frequency *precedes* and *predicts* churn. In this story, re-engagement campaigns could work — but only if you can re-engage customers before they've already decided to leave.
- **Story B:** Customers don't log in because they don't need the product, and they also churn for the same underlying reason (low perceived value). In this story, a re-engagement email doesn't address the root cause and may not reduce churn at all.

Feature importance cannot distinguish between these two stories. You need to either run an experiment (A/B test a re-engagement campaign) or apply causal inference methods to observational data.

---

### 3. `support_tickets` — Classic confounding risk

High support ticket volume predicts churn. But why?

- Customers with product problems file tickets *and* churn — the underlying issue (product failure, poor fit) causes both. Filing fewer tickets doesn't reduce churn; fixing the product does.
- Alternatively, customers who file many tickets and get *bad support* churn, while customers who file tickets and get *good support* stay. In this case, intervention should target support quality, not ticket volume itself.

**Worst-case intervention mistake:** Marketing sees high support tickets as a churn risk signal and decides to *discourage* customers from filing tickets (e.g., making support harder to access). This would suppress the signal in future models but almost certainly increase churn.

---

### 4. `pricing_tier` — Confounded by selection

Pricing tier is predictive, but customers self-select into tiers. Lower-tier customers may churn more because they have lower commitment, lower switching costs, or fundamentally different use cases — not simply because of the price.

Offering lower-tier customers a discount to upgrade sounds logical from a feature importance perspective. But if pricing tier is a proxy for customer type rather than a lever on churn, you will spend retention budget on customers who were going to churn regardless, or customers who would have stayed anyway.

---

## Why Feature Importance Fails as a Causal Guide

Feature importance (whether from tree-based models, permutation importance, SHAP, etc.) answers the question: **"How much does knowing this feature help the model predict the outcome?"**

It does not answer:
- Does changing this feature change the outcome?
- Is this feature upstream or downstream of churn in a causal graph?
- Is this feature a cause, a consequence, or a correlated proxy for an unmeasured common cause?

The classic illustration: shoe size predicts reading ability in children. Shoe size is a great feature. Buying bigger shoes does nothing.

Your model is trained on observational data. Every feature's importance reflects the correlation structure in that data, including all the confounding, reverse causation, and mediation that exists in the real world.

---

## What You Should Actually Do

### Step 1: Separate "signals" from "levers"

Classify each feature by whether it is something you can actually change:

| Feature | Type | Rationale |
|---|---|---|
| `account_age` | Signal only | Cannot be manipulated |
| `last_login_days` | Possible lever | Needs causal validation |
| `support_tickets` | Signal (lever at the cause level) | Ambiguous; investigate upstream causes |
| `pricing_tier` | Possible lever | Heavily confounded; needs experimentation |

### Step 2: Run experiments for candidate levers

For `last_login_days` and `pricing_tier`, the cleanest path forward is a randomized experiment:

- Randomly assign at-risk customers (identified by your model) to a re-engagement campaign or a pricing intervention.
- Measure actual churn rates, not just engagement with the campaign.
- This gives you an unbiased estimate of the causal effect.

### Step 3: For observational analysis, use causal inference methods

If you cannot run experiments, consider:

- **Propensity score matching or weighting** to compare similar customers who received vs. did not receive an intervention
- **Instrumental variables** if you have a valid instrument
- **Difference-in-differences** if you have a natural experiment or policy change

These methods attempt to isolate the causal effect from confounding, which pure prediction models cannot do.

### Step 4: Investigate what `support_tickets` is really measuring

Pull a sample of high-ticket churners and look at ticket content. Are they complaining about a specific feature? A bug? Billing issues? The feature importance told you something is broken in the customer experience — your job now is to diagnose *what* and fix it at the source.

---

## The Bottom Line for Marketing

Your model is genuinely useful — 92% AUC is strong, and it can reliably identify *who* is at risk of churning. That is valuable for prioritizing who to target with retention efforts.

But the feature importances answer a different question than "what should we change?" To answer that question, you need either:

1. **Randomized experiments** on your candidate interventions, or
2. **Causal inference methods** applied to your observational data

Using feature importances directly to choose interventions is a common mistake that leads to wasted budget (acting on non-levers) or backfiring campaigns (intervening on the wrong side of a causal relationship).

The model tells you *who* to worry about. Figuring out *what to do about it* requires additional work.
