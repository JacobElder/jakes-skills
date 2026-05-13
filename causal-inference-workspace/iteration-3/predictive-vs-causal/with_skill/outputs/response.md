# Can Feature Importances Tell You What to Intervene On?

**Short answer: No. Feature importances answer a rung-1 question; your marketing team is asking a rung-2 question. They are not interchangeable.**

---

## Step 1: Name the Rung

Your 92% AUC model lives entirely on **Rung 1 — Association**. It answers: "Given that a customer has these feature values, what is the probability they churn?" That is a seeing question.

Marketing's question is: "If we act on feature X, will churn go down?" That is a **Rung 2 — Intervention** question. It requires the do-operator: P(churn | do(X = x)), not P(churn | X = x).

These quantities can be dramatically different — and the gap is not a matter of sample size or model sophistication. No amount of additional data or a better ML model closes it. Closing it requires causal assumptions, typically encoded in a DAG.

---

## Step 2: Sketch the DAG

Here is the most plausible causal structure for your four features:

```
Customer Disengagement (U, unobserved)
        |
        |-----> last_login_days (symptom)
        |-----> support_tickets (ambiguous)
        |-----> Churn (Y)

account_age --------> Churn (Y)   [lifecycle effect; not actionable]
pricing_tier -------> Churn (Y)   [structural — can be directly set]
```

The key variable is unobserved: **underlying disengagement** — the latent state in which a customer has mentally decided to leave, or has simply stopped finding the product valuable. This state causes both the measurable symptoms and the eventual cancellation event.

---

## Step 3: Classify Each Feature Structurally

### `last_login_days` — Downstream Indicator. Do not intervene directly.

This is the downstream indicator trap. Disengaged customers stop logging in *before* they cancel. The causal arrow runs:

```
Disengagement -> infrequent logins -> (eventually) Churn
```

The login gap is a symptom, not a cause. The difference is precise:

- P(churn | last_login_days = 30): The churn rate among customers who *happen to have* a 30-day login gap. High — because disengaged users have long gaps.
- P(churn | **do**(last_login_days = 30)): The churn rate if you *forced* someone to log in every 30 days. Likely far lower and possibly close to zero change — because the intervention addresses the symptom, not the underlying disengagement.

Re-engagement campaigns that increase login frequency without addressing the underlying reason for disengagement will not reduce churn. They treat the symptom. The model correctly identifies this feature as predictive; it is wrong to treat it as an intervention target.

**Verdict: Valid targeting signal (who is at risk). Invalid intervention target (what to change).**

### `account_age` — Not an Actionable Lever.

You cannot make a customer older. Account age cannot be directly manipulated.

What account age captures is a combination of habit formation, switching costs, and survivorship (churned customers don't have old accounts). It is useful for segmentation — interventions may have heterogeneous treatment effects by account age — but it is not itself an intervention lever.

**Verdict: Not actionable directly. Use for subgroup analysis of where other interventions work best.**

### `support_tickets` — Ambiguous. Structural role determines validity.

Support tickets could sit in two very different positions in the DAG:

**DAG A (tickets as symptom):** Disengagement causes customers to stop filing tickets as they disengage, or to file more frustrated ones on the way out — then churn. `disengagement -> support_tickets AND -> churn`. Improving support response time would not reduce churn; you would be treating a symptom.

**DAG B (bad support as cause):** Poor product experiences generate tickets; unresolved friction directly causes churn. `poor_product_experience -> support_tickets -> Churn`. Here, reducing ticket volume by fixing underlying issues, or improving resolution quality, is a valid intervention.

These two DAGs have opposite policy implications. The predictive importance of `support_tickets` in your model cannot distinguish between them. One concrete diagnostic: do customers who get their tickets resolved quickly churn at lower rates than similar customers with equivalent ticket volume whose tickets were resolved slowly? If yes, consistent with DAG B. If resolution quality does not predict churn, the tickets are likely symptomatic of a decision already made — DAG A.

**Verdict: Possibly causal, but the mechanism matters. Requires structural investigation before acting.**

### `pricing_tier` — Most Promising Intervention Candidate.

Pricing tier is set by the company (or chosen by the customer at signup, prior to the churn decision). It is structurally upstream of churn in most plausible DAGs. A price change is a real, well-defined do-operator — you can literally change it — and there is a plausible mechanism (affordability, value perception, feature access) by which it affects churn.

Two cautions:

1. **Confounding by self-selection**: Customers chose their pricing tier based on usage needs and budget. Higher-tier customers may be more committed, or more price-sensitive. The observational relationship between tier and churn is confounded by the reasons customers selected that tier. An RCT (random tier assignment or a promotional discount experiment) is needed to estimate the causal effect cleanly.

2. **Reverse causality risk**: Customers planning to churn may have already downgraded. If so, `pricing_tier` is partially a downstream indicator of the churn decision rather than a pure upstream cause.

**Verdict: Most plausible genuine intervention target. Requires an experiment to quantify the causal effect — the observational importance score does not give you the effect size of a pricing intervention.**

---

## Step 4: What Would Actually Identify These Effects?

| Feature | Structural Role | Identification Strategy |
|---|---|---|
| `last_login_days` | Downstream indicator | Use as targeting signal; the intervention must address what's driving disengagement |
| `account_age` | Non-actionable structural property | Use for heterogeneous treatment effect analysis |
| `support_tickets` | Ambiguous — needs DAG discrimination | Compare resolution speed vs. churn controlling for ticket volume; or run an A/B test on support quality |
| `pricing_tier` | Plausible direct cause | RCT on pricing offers; randomized discounts or tier assignments |

If a randomized experiment is not feasible for pricing, look for a natural experiment: a pricing change rolled out in one region or cohort before another, enabling a differences-in-differences analysis. The identifying assumption is parallel pre-treatment trends.

---

## Step 5: The Core Trap Here

**Predictive accuracy does not equal causal validity.** A model with 92% AUC is doing its job excellently at identifying which customers are likely to churn. The mistake is using feature importances from that model to set intervention priorities.

The features that best *predict* churn are often the ones most tightly coupled to the latent churn state — precisely the downstream indicators. A model trained to maximize predictive accuracy will correctly weight these highly. That is not a flaw in the model; it is a flaw in using the model's output to answer the wrong question.

The analogy from the skill: ZIP code predicts creditworthiness. Lending policy based on ZIP code does not improve creditworthiness. `last_login_days` predicts churn. Campaigns that force logins do not address the underlying disengagement.

---

## Step 6: Alternative Structural Interpretations

For `support_tickets`, two DAGs lead to opposite recommendations. If DAG B is correct and you improve support quality, you should see churn decline among customers with recent tickets even holding disengagement constant. You can probe this by measuring whether churn rates differ for customers with identical ticket volumes but varying resolution speed — though this comparison is confounded by which customers generate slow-resolution tickets. A proper test randomizes support response time or quality at the customer level.

If DAG A is correct, the same experiment will show no effect of resolution speed on churn, which is itself informative: stop investing in support improvements as a churn-reduction lever, and focus on the upstream disengagement driver.

One plausible diagnostic that doesn't require an experiment: does ticket volume *increase* sharply in the months before churn, even among customers who were otherwise similar to non-churning customers? A spike in tickets shortly before cancellation, without a concurrent product quality change, points toward downstream indicator. A more distributed pattern tied to specific product areas or issue types points toward a causal driver.

---

## Summary for Marketing

| Feature | Predictive Importance | Intervention Target? | Reasoning |
|---|---|---|---|
| `last_login_days` | High | No | Downstream symptom of disengagement; re-engagement campaigns treat the symptom |
| `support_tickets` | High | Possibly | Depends on whether bad support causes churn or disengagement causes both low engagement and churn. Needs investigation. |
| `pricing_tier` | Moderate | Yes (test it) | Structurally upstream; pricing changes can be randomized. Observational importance score does not give you the effect size. |
| `account_age` | Moderate | No | Cannot be intervened on directly; useful for segmenting where other interventions work best |

The model is doing exactly what it was built to do. The question marketing is asking requires a different tool: causal identification, not predictive modeling. Use the model to decide *who* to act on; run experiments to decide *what* to do.

The real intervention leverage almost certainly lies upstream of what your feature set measures — in whatever causes customers to become disengaged in the first place. That latent state is not in your model, and it will not surface from a predictive model trained on behavioral features. Finding it requires qualitative research, mechanism-first thinking, and experiments on candidate causes: product gaps, onboarding failures, competitive displacement, pricing misalignment.
