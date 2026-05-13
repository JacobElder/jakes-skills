# Can Feature Importances Tell You What to Intervene On?

**Short answer: No. Feature importance tells you what predicts churn, not what causes it. These are fundamentally different questions.**

## The Core Problem: Prediction vs. Causation

Your model answers: "Given what we observe about a customer, how likely are they to churn?" That's a prediction task.

Marketing's question is: "If we change something about a customer's experience, will it reduce their churn?" That's a causal question.

Feature importance answers the first. It cannot answer the second without additional assumptions and analysis.

## Walking Through Your Features

### account_age
This is almost certainly not actionable. Account age is a proxy for many things — loyalty, product fit, switching costs. You cannot make a new customer "older." Intervening on account age is nonsensical. Its high importance likely reflects that older accounts have different churn dynamics, not that aging your customers reduces churn.

### last_login_days (days since last login)
This is tempting — "let's email inactive users!" But high last_login_days may be a *symptom* of already-decided churn, not a cause. Customers who have mentally checked out stop logging in before they cancel. Sending re-engagement emails to people who have already decided to leave may have zero or even negative effect. Correlation here does not imply that forcing logins reduces churn.

### support_tickets
This is ambiguous. High support ticket volume could mean:
- The product has bugs that frustrate users (causal — fixing the product would reduce churn)
- The customer is confused and under-utilizing the product (causal — better onboarding might help)
- The customer is already frustrated and escalating before churning (symptom — intervening on tickets alone may not help)

You need to understand the mechanism before acting. Running an A/B test on support quality or resolution speed would help establish causality here.

### pricing_tier
This is the most promising candidate for intervention, but it still requires caution. If customers on certain pricing tiers churn more, it could mean:
- That tier is a poor product-market fit (causal — restructuring the tier or pricing could help)
- Those customers are self-selected to be price-sensitive (selection effect — discounts may just cannibalize revenue without retaining customers who would have churned anyway)

## Why Feature Importance Fails as Causal Evidence

Feature importance algorithms (SHAP, permutation importance, etc.) measure association — how much knowing a feature reduces prediction error. They do not establish:

1. **Direction of causality**: Does low login frequency cause churn, or does intent to churn cause low login frequency?
2. **Confounding**: Account age correlates with cohort, pricing, and product version. Importance scores don't disentangle these.
3. **Intervention effects**: The statistical relationship in observational data may not hold when you actively change the variable. This is Judea Pearl's fundamental point — the distribution under intervention (do-calculus) is not the same as the observational conditional distribution.

This is sometimes called the difference between P(churn | last_login_days = 30) and P(churn | do(last_login_days = 30)). Your model estimates the former; marketing needs the latter.

## What You Should Actually Do

**1. Apply domain reasoning first**
Separate your features into:
- *Immutable proxies*: account_age, customer demographic features — don't intervene
- *Symptoms*: last_login_days (likely a lagging indicator) — treat as a targeting signal, not an intervention target
- *Potential levers*: pricing_tier, support quality, feature adoption — these are candidates for causal investigation

**2. Run randomized experiments**
The gold standard. Randomly assign customers to:
- Proactive support outreach vs. control
- Pricing tier changes vs. control
- Re-engagement campaigns vs. control

Measure actual churn differences. This is the only way to establish that an intervention works.

**3. Use causal inference methods on observational data**
If experiments aren't feasible, consider:
- **Propensity score matching**: Compare churners and non-churners who look similar on all other features except the variable of interest
- **Difference-in-differences**: Exploit natural variation or policy changes over time
- **Instrumental variables**: Find a variable that affects your feature of interest but has no direct effect on churn
- **Causal discovery algorithms**: Use tools like DoWhy, CausalNex, or EconML to estimate causal effects rather than predictive associations

**4. Use the model for targeting, not intervention design**
Your 92% AUC model is genuinely valuable — use it to identify *who* is at risk. But determine *what to do* for those at-risk customers through separate causal analysis or domain expertise, not by reading the feature importances.

## The Practical Summary

| Feature | Actionable? | Why |
|---|---|---|
| account_age | No | Immutable; intervening is impossible |
| last_login_days | Use as signal, not intervention target | Likely a symptom; re-engagement campaigns need A/B testing |
| support_tickets | Maybe — but test it | Mechanism is ambiguous; resolution quality is a testable lever |
| pricing_tier | Maybe — but test it | Possible lever, but selection effects may dominate |

Your model is excellent at identifying who will churn. To know what to do about it, you need causal analysis — which requires either running experiments or applying causal inference methods to your observational data. Feature importances alone cannot bridge that gap.
