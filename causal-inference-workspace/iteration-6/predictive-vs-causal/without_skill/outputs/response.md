# Can Feature Importances Tell You What to Intervene On?

**Short answer: No — not reliably. Feature importance tells you what predicts churn, not what causes it.**

---

## The Core Problem: Prediction vs. Causation

Your model was trained to *predict* churn as accurately as possible. Feature importance scores (whether SHAP values, permutation importance, or tree-based gain) tell you which variables are most useful for that prediction task. They do **not** tell you what would happen if you *intervened* on those variables.

This distinction matters enormously for your marketing team's question. They aren't asking "which features help us predict who will churn?" — they're asking "which levers can we pull to *prevent* churn?" That's a causal question, and predictive models don't answer causal questions.

---

## Why Each Feature Could Be Misleading

### `account_age`
High account age might be protective against churn — but you can't make an account older. More importantly, account age is likely a **proxy** for a cluster of other things: product-market fit for that customer segment, accumulated switching costs, relationship depth. Knowing it's predictive tells you nothing about what to do.

### `last_login_days` (days since last login)
This is a classic case of a **symptom vs. cause** problem. Customers who are about to churn stop logging in *because* they've mentally checked out — they don't churn *because* they stopped logging in. If marketing sends re-engagement emails to get disengaged users to log in once more, that login event won't address the underlying dissatisfaction. The feature is predictive precisely because it's a downstream signal of the real causes.

### `support_tickets`
High support ticket volume correlates with churn, but the relationship is ambiguous without further investigation:
- Are customers churning *because* they had bad support experiences? (Causal — improve support quality)
- Are customers who have unresolved product problems opening tickets *and also* churning? (The unresolved problem is the cause)
- Are customers who are already decided to leave opening tickets as a last step? (Tickets as symptom, not cause)

Each scenario implies a completely different intervention strategy. Feature importance can't distinguish between them.

### `pricing_tier`
This one might actually be causal — pricing tier is something you can change, and price is a real lever. But even here, importance score alone doesn't tell you the *direction* or *magnitude* of the effect. Customers on higher pricing tiers might churn more simply because they're larger companies with procurement processes that rotate vendors, not because the price itself is the problem.

---

## The Fundamental Issue: Confounding

Feature importance in a predictive model reflects statistical association, which is contaminated by confounding. For example:

- `account_age` and `last_login_days` are both correlated with customer segment, product usage patterns, and company size — all of which themselves drive churn
- A variable can have high importance purely because it's a **proxy** for an unmeasured causal factor

When you intervene on a proxy variable, you're not touching the underlying cause. The correlation breaks down under intervention.

---

## What You Actually Need

To answer the intervention question, you need **causal inference** methods:

1. **A/B testing (randomized controlled trials)**: If you can randomly assign customers to different conditions (e.g., proactive outreach, pricing changes, support tier upgrades), you can measure true causal effects.

2. **Causal graphs (DAGs)**: Map out the assumed causal relationships between your variables. This forces explicit reasoning about what causes what, and helps identify confounders you need to control for.

3. **Instrumental variables or difference-in-differences**: For observational data where experiments aren't possible, these methods can sometimes recover causal estimates under specific assumptions.

4. **Uplift modeling**: Instead of predicting who will churn, model who will *respond* to a specific intervention — i.e., the causal effect of your action for each customer.

---

## Practical Recommendations for Your Team

1. **Don't intervene on `account_age`** — it's not actionable and is likely a proxy.

2. **Treat `last_login_days` as a trigger, not a target.** Use it to identify at-risk customers, then investigate *why* they disengaged. The actionable lever is the root cause of disengagement, not the login metric itself.

3. **Dig into `support_tickets` qualitatively.** Look at ticket categories and resolution outcomes. Run an experiment: randomly assign a subset of ticket-openers to an escalated support experience and measure churn difference.

4. **`pricing_tier` is the most plausibly actionable**, but run a pricing experiment or use a quasi-experimental design before drawing conclusions.

5. **Build an uplift model** for any intervention you're seriously considering — it will tell you which customers are actually movable by that specific action, rather than which customers are predicted to churn.

---

## Summary

| Feature | Predictive? | Directly Actionable? | Risk of Spurious Intervention |
|---|---|---|---|
| `account_age` | Yes | No | High |
| `last_login_days` | Yes | Partly (as a trigger) | High — symptom of churn |
| `support_tickets` | Yes | Maybe | Medium — depends on causal pathway |
| `pricing_tier` | Yes | Yes | Lower, but still needs testing |

Your 92% AUC model is excellent for *identifying* who is likely to churn. It should be used to prioritize which customers to focus your intervention efforts on. But **which interventions to make** requires causal reasoning — either randomized experiments or carefully designed observational studies — not feature importances.
