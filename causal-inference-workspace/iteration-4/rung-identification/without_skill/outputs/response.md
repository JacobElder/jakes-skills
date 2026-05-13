# Causal Inference Analysis: Sequential User ID Assignment Bug

## The Scenario

A backend bug caused A/B test assignment based on the last digit of user IDs:
- **New checkout**: last digit 0–4
- **Old checkout**: last digit 5–9
- **Observed effect**: +4.2% conversion for new checkout users

**Junior analyst**: "User IDs are arbitrary, so this is essentially random — +4.2% is a valid causal estimate."

**Senior engineer**: "User IDs are assigned sequentially, so this compares newer users to older users."

---

## Who's Right?

**The senior engineer is correct**, and the junior analyst is wrong. Here's why:

### The Core Issue: Sequential Assignment Creates Systematic Confounding

If user IDs are assigned sequentially (which is extremely common in production systems — auto-incrementing database keys, monotonically increasing counters, etc.), then the last digit of the user ID is **not random with respect to user characteristics**. It is a deterministic function of registration order.

Consider what "last digit 0–4 vs. 5–9" means under sequential assignment:

- Users with IDs ending in 0, 1, 2, 3, 4 were assigned to new checkout
- Users with IDs ending in 5, 6, 7, 8, 9 were assigned to old checkout

In a sequential numbering scheme (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ...), **every consecutive block of 10 users gets 5 in each group**. At first glance, this sounds like it could approximate balance. However, the critical confound is **time**.

#### Why Time Matters

Users who registered earlier differ systematically from users who registered later:

1. **Cohort effects**: Early adopters of a product often have different engagement patterns, intent, and demographics than later users.
2. **Retention bias**: Older users have had more time to convert, churn, or change behavior — the user base composition shifts over time.
3. **Product maturity**: The product itself (UX, pricing, trust signals, marketing) likely changed between when early vs. late users signed up.
4. **Seasonality and external factors**: Users who signed up during different time periods were exposed to different market conditions.

Now here's the key problem with sequential IDs and last-digit assignment: the **distribution of last digits is not balanced across time within a given measurement window**.

For example, if you're measuring conversions in the past 30 days, recently registered users (high IDs) are overrepresented in your active user pool. And under sequential assignment, recently registered users will cluster in specific last-digit groups depending on the current ID counter modulo. More subtly, even if the last-digit distribution is roughly uniform over long periods, **the composition of "who is actively converting" right now** can be systematically skewed.

---

### Formalizing the Problem with Causal Reasoning

To claim +4.2% is a valid causal estimate, we need the assignment mechanism to satisfy **ignorability** (also called unconfoundedness or exchangeability):

> (Y⁰, Y¹) ⊥ T | X

where T is treatment (new vs. old checkout), Y⁰ and Y¹ are potential outcomes, and X are observed covariates.

For this to hold, the assignment — last digit of user ID — must be independent of potential outcomes after conditioning on measured covariates. But if user ID encodes **time of registration**, then it encodes:

- User cohort (newer vs. older customers)
- Behavioral maturity
- Exposure to different versions of the product
- Different external conditions at time of signup

These are **causes of conversion** that are also correlated with treatment assignment. This is a classic **confound**: the treatment (new checkout) is systematically correlated with user recency, which independently affects conversion.

**The DAG looks like:**

```
User Recency → Treatment Assignment (last digit)
User Recency → Conversion
```

This backdoor path (User Recency → Treatment, User Recency → Outcome) means the observed association between treatment and outcome is confounded.

---

### Is the Junior Analyst Completely Wrong?

The junior analyst's **intuition has a kernel of truth** but is applied incorrectly:

- It is true that within a *truly* random ID system (e.g., UUIDs, randomly salted hashes), the last digit would be essentially random and uncorrelated with any user characteristic. In that case, the assignment would approximate random and the estimate could be valid.
- However, the analyst's argument fails to verify the **assumption** — they assumed arbitrariness without establishing it.

The senior engineer's point is the empirically relevant one: **production systems overwhelmingly use sequential IDs**, and assuming otherwise without verification is dangerous.

---

### Can We Salvage This as a Causal Estimate?

Potentially, but with significant caveats:

**Option 1: Check for balance**
Run covariate balance checks between the two groups (age of account, historical purchase behavior, acquisition channel, demographics if available). If groups are well-balanced on pre-treatment covariates, the estimate may still be approximately valid.

**Option 2: Regression adjustment / matching**
Control for user registration date (or a proxy for user age/cohort) in a regression model or use matching to compare users of similar tenure. This can reduce confounding due to cohort effects.

**Option 3: Subgroup analysis by cohort**
Analyze the effect separately within narrow cohort windows (e.g., users registered in the same month). If the effect persists within cohorts, that's stronger evidence.

**Option 4: Falsification tests**
Test whether the last-digit assignment predicts pre-treatment outcomes (e.g., conversion rate before the new checkout was deployed). If it does, that's a clear sign of confounding.

---

## Bottom Line

| Claim | Verdict |
|---|---|
| "Last digit of sequential IDs is essentially random" | **False** — it encodes time of registration |
| "+4.2% is a valid causal estimate as-is" | **Not established** — confounding by user cohort/recency is plausible |
| "This compares newer users to older users" | **Approximately correct** — the concern is legitimate |
| "We can't use this data at all" | **Too strong** — with proper adjustment, it may be salvageable |

The senior engineer raises the correct concern. The junior analyst made the classic mistake of confusing "we didn't consciously control assignment" with "assignment is random." Randomness must be verified, not assumed. The +4.2% estimate, taken at face value, likely reflects some mixture of the true checkout effect and cohort differences — and cannot be cleanly interpreted as a causal estimate without further analysis.

**Recommendation**: Before drawing conclusions, verify the ID assignment mechanism, run balance checks on user tenure and pre-treatment behavior, and if imbalance exists, apply covariate adjustment or stratified analysis before reporting the causal effect.
