# Who's Right? Causal Validity of Last-Digit User ID Assignment

## Short Answer

The senior engineer is substantially more correct. The +4.2% conversion difference is **not** a valid causal estimate of the checkout effect. The assignment mechanism introduced a systematic confound — user tenure — that violates the core requirement for causal identification.

---

## Why the Junior Analyst Is Wrong

The junior analyst's argument rests on the assumption that "user IDs are arbitrary," meaning the last digit is essentially a coin flip. If that were true, the last digit would be independent of any user characteristic (experience, loyalty, purchase intent, etc.), and the comparison would be as clean as a randomized experiment.

But the senior engineer identifies the fatal flaw: **user IDs are assigned sequentially**. This means:

- Lower-numbered user IDs belong to earlier/older users
- Higher-numbered user IDs belong to more recent users
- The last digit of a sequential ID is NOT random — it is a deterministic function of the ID itself

Digits 0–4 vs. 5–9 in a sequential scheme will alternate in a fixed pattern (e.g., user IDs ...0, ...1, ...2, ...3, ...4 always precede ...5, ...6, ...7, ...8, ...9 in each block of 10). Across the full user base, half of every 10-user cohort goes to each group — but critically, **the groups are not balanced on tenure**. Within any given acquisition cohort (e.g., users 1000–1009), both digits 0–4 and 5–9 are represented. So at a cohort level, the randomization might look balanced... but it depends heavily on the distribution.

More importantly, even if the digit-based split happened to be approximately 50/50 in count, what matters for causal inference is **exchangeability**: would users in one group have the same potential outcomes as users in the other group, absent the treatment? Sequential ID assignment means the groups may systematically differ on:

- **Account age / tenure**: Long-tenured users have had more time to develop purchase habits, loyalty, and familiarity with the platform
- **Cohort effects**: Earlier users may have joined during a different product era, marketing campaign, or user acquisition strategy
- **Selection effects**: Early adopters are often more engaged, tech-savvy, or brand-loyal than later users
- **Survivorship bias**: Older accounts that are still active have already survived churn; they may convert at higher rates simply due to higher baseline engagement

---

## Pearl's Causal Hierarchy Applied

Using Judea Pearl's three-rung ladder:

**Rung 1 — Association**: We can observe that new_checkout users convert at +4.2% higher rates. This is just a correlation.

**Rung 2 — Intervention** (what we want): What would happen to conversion if we *intervened* and assigned a user to new_checkout vs. old_checkout, holding everything else equal?

**Rung 3 — Counterfactual**: What *would* this user have converted at under the other checkout?

To move from Rung 1 to Rung 2, we need the assignment mechanism to satisfy **ignorability** (also called "no unmeasured confounding" or the "backdoor criterion"): assignment to treatment must be independent of potential outcomes, conditional on observed covariates.

Here, the assignment (last digit of a sequential ID) is correlated with user tenure, which is correlated with conversion propensity. This creates an **open backdoor path**:

```
User Tenure → Conversion Rate
User Tenure → User ID Last Digit (via sequential assignment) → Treatment Group
```

The last-digit assignment does NOT block this path. It IS the path. Therefore, the observed +4.2% conflates the true checkout effect with the effect of user tenure on conversion.

---

## Is There Any Scenario Where the Junior Analyst Could Be Salvaged?

Only under very specific conditions:

1. **If user IDs are truly random** (e.g., UUIDs assigned at random): then the last digit IS random and the analyst would be right. But the problem states IDs are sequential, so this does not apply.

2. **If you condition on tenure / account age**: If you have data on when each user account was created, you could attempt to control for tenure using regression adjustment, matching, or stratification. However, you'd need to assume no other sequential confounds exist, and you'd lose the simplicity of a clean experimental design.

3. **If the effect is enormous and tenure effects are tiny**: As a practical matter, if you know from prior data that tenure has negligible effect on conversion, the bias may be small relative to the effect size. But this requires external validation, not assumption.

---

## Formal Diagnosis: What Kind of Bias Is This?

This is a **selection bias** problem caused by a non-random assignment mechanism. More specifically, it is a form of **confounding by indication** (the "indication" here being user tenure/seniority). The treatment assignment is correlated with a pre-treatment variable (account age) that also affects the outcome (conversion).

This is NOT randomization. It is a **quasi-experiment** with a systematic flaw in the instrument. It would be valid as a natural experiment only if sequential ID assignment were truly unrelated to any user characteristic — which it is not, by construction.

---

## What Should Be Done

1. **Do not report +4.2% as the causal effect.** It is a biased estimate.

2. **Measure the confound**: Pull account creation dates for both groups. If older accounts disproportionately land in one group (even slightly), this confirms the bias.

3. **Attempt adjustment**: Use regression with account age (and other observable covariates like historical purchase count, days since last visit) as controls. This may partially recover a less-biased estimate.

4. **Run a proper A/B test**: Assign users to checkout variant using a true random mechanism (e.g., a cryptographic hash of user ID with a salt, or explicit random assignment at the time of the experiment launch).

5. **Consider a difference-in-differences or cohort-matched analysis**: If you can identify matched cohorts of users with similar tenure across both groups, you can construct a more credible estimate.

---

## Summary Verdict

| Claim | Verdict |
|---|---|
| "Last digit is essentially random" | **Wrong** — sequential IDs make the last digit deterministic, not random |
| "This compares newer to older users" | **Correct in spirit** — the groups differ systematically on tenure |
| "+4.2% is a valid causal estimate" | **No** — confounding by tenure (and potentially other cohort effects) invalidates causal interpretation |
| "We can use this as a natural experiment" | **Only with strong controls and caveats** — not as-is |

The causal identification fails. The +4.2% is a biased, observational association, not an experimentally-identified treatment effect.
