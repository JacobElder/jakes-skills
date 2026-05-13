# Feature Importances vs. Causal Inference: What You Can and Cannot Do

## Short Answer

No — feature importances alone cannot tell you which features to intervene on. A 92% AUC model is impressive for prediction, but prediction and causation are fundamentally different problems. Using feature importances to guide interventions is a common and costly mistake. Here is why, and what to do instead.

---

## The Core Problem: Prediction vs. Causation

Your model has learned to answer the question: *"Given what we know about a customer, how likely are they to churn?"*

Marketing's question is different: *"If we change something about a customer's experience, will they be less likely to churn?"*

These are different questions. The first is observational. The second is interventional. A predictive model — no matter how accurate — is trained to detect correlation, not to identify causes. Feature importance tells you which variables are most useful for *distinguishing* churners from non-churners in your historical data. It does not tell you which variables, if changed, would *cause* someone to stay.

---

## Walking Through Your Four Features

### 1. `account_age`
Account age is almost certainly a **marker, not a lever**. Older accounts may churn less simply because customers who were going to churn already did so — a classic survivorship effect. You cannot intervene on account age. It accrues passively. High importance here reflects a useful predictive signal, but there is nothing marketing can do with it directly.

### 2. `last_login_days`
This one looks actionable — you could send a re-engagement email to customers who haven't logged in recently. But the causal question is: *does low engagement cause churn, or does dissatisfaction cause both low engagement and churn?* If customers disengage because they're already unhappy, then pushing them to log in won't reduce churn — it will just temporarily mask the signal. The feature is predictive of churn, but re-engagement campaigns may or may not work, and you cannot know from feature importance alone.

### 3. `support_tickets`
Similar ambiguity. High support ticket volume predicts churn. But is that because unresolved issues cause customers to leave (causal), or because customers who were already unhappy both file more tickets and churn (confounded)? If you try to suppress tickets — for instance by making it harder to file one — you would reduce the feature value without reducing churn, and likely make things worse.

### 4. `pricing_tier`
This is the most potentially actionable — pricing is something you can change. But feature importance doesn't tell you the direction of the effect or the magnitude. Customers on certain pricing tiers might churn more because the price is wrong for them, or because that tier attracts a different customer segment with different needs. Without causal analysis, you don't know if changing pricing would help, and for whom.

---

## Why This Matters: The Intervention vs. Correlation Gap

Here is an illustrative example of the failure mode:

Imagine a hospital predicts mortality risk. One of the top features is "received oxygen supplementation." High importance. But this doesn't mean you should withhold oxygen to reduce mortality — sicker patients receive oxygen *because* they are sicker. Oxygen correlates with mortality because illness causes both. Intervening on the feature in the wrong direction would be fatal.

The same logic applies to churn. You can accidentally intervene in the wrong direction, waste budget on features that are correlates rather than causes, or miss the real levers entirely.

---

## What You Actually Need: Causal Inference Methods

To answer marketing's question, you need methods designed to estimate causal effects. Here are the main options, ordered roughly by feasibility:

### A/B Testing (Randomized Experiments) — Gold Standard
If you can randomize customers into treatment and control groups, you can directly measure the causal effect of an intervention. For example: randomly offer a discount to some customers on lower pricing tiers, and measure whether it reduces churn compared to the control group. This is the most reliable method.

**Limitation:** You can't A/B test everything (e.g., you can't randomly assign account age), and experiments take time.

### Uplift Modeling (Heterogeneous Treatment Effects)
Rather than predicting who will churn, uplift models predict *who will respond to a treatment*. You train a model to estimate the individual treatment effect — the difference in churn probability with vs. without intervention. This is often built on top of experimental data.

**Tools:** T-learner, S-learner, X-learner, causal forests (e.g., via the `grf` R package or `econml` in Python).

### Causal Graph / DAG Analysis
If you have domain knowledge about the relationships between variables, you can encode this as a Directed Acyclic Graph (DAG) and use it to identify which variables are causally upstream of churn. This helps you rule out confounders and mediators before designing experiments.

**Tools:** `dagitty`, `DoWhy` (Python), `bnlearn`.

### Instrumental Variables or Difference-in-Differences
If you have natural experiments in your data (e.g., a pricing change that affected some customers but not others, or a regional policy change), you can use these quasi-experimental methods to estimate causal effects without running a new A/B test.

### Observational Causal Inference (with caveats)
Methods like propensity score matching, inverse probability weighting, or doubly-robust estimators can help adjust for confounders in observational data. These are weaker than experiments because they rely on the *no unmeasured confounders* assumption, which is untestable. Use with caution and strong domain knowledge.

---

## Practical Recommendations for Marketing

Given your four features, here is how to think about next steps:

| Feature | Actionable? | Recommended Approach |
|---|---|---|
| `account_age` | No | Use as a stratification variable in experiments; don't intervene directly |
| `last_login_days` | Potentially | Run A/B test: send re-engagement emails to inactive users, measure churn delta |
| `support_tickets` | Potentially | Investigate ticket resolution rates; test proactive outreach after ticket filing |
| `pricing_tier` | Potentially | Run pricing experiment; use uplift model to find segments where price sensitivity is highest |

The key framing shift: instead of asking "which features are most important for predicting churn?" ask "if we intervene on X, how much does churn probability change, and for which customers?"

---

## Summary

- Feature importance = predictive signal, not causal signal
- High importance means the variable is useful for distinguishing churners; it does not mean changing that variable will reduce churn
- Some important features are completely non-actionable (e.g., account age)
- Others may be actionable but the direction and magnitude of effect are unknown without causal analysis
- The right tools for marketing decisions are: A/B tests, uplift models, causal graphs, and quasi-experimental methods
- Your 92% AUC model is valuable for *targeting* — finding the right customers to intervene on — but it must be paired with causal evidence about *what to do*

The combination of a strong predictive model for identifying at-risk customers, plus causal inference to determine which interventions work, is the right framework for building an effective churn reduction program.
