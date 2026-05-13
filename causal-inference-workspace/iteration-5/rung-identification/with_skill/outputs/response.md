# Causal Analysis: Sequential User ID Assignment as an A/B Test

## The Verdict

The senior engineer is right, and the junior analyst is wrong — though the analyst is making an understandable error. The +4.2% estimate is not a valid causal estimate of the checkout effect without further scrutiny and adjustment. Here is why, and what you would need to recover one.

---

## Step 1: Name the Rung

The question is a **Rung 2 (Intervention) question**: "Does the new checkout flow cause higher conversion rates?" The team wants to know P(conversion | do(checkout = new)) minus P(conversion | do(checkout = old)) — the effect of *forcing* a user onto the new checkout, not the effect observed among users who *happened* to get it.

The junior analyst is implicitly treating the association as the causal effect. That inference requires an explicit identification argument — specifically, that the assignment mechanism is independent of potential outcomes. Asserting that user IDs are "arbitrary" is not that argument.

---

## Step 2: Sketch the DAG

The key structural question is whether the last digit of a sequential user ID is independent of the factors that cause conversion. Let's make the causal structure explicit:

```
Time-of-registration --> UserID (sequential) --> last_digit --> Treatment
Time-of-registration --> User_cohort_characteristics --> Conversion
Treatment --> Conversion  (the effect we want to estimate)
```

Because user IDs are assigned sequentially, a user's ID encodes *when they registered*. Registration timing is a fork:

- `Registration_timing --> UserID --> last_digit --> Treatment`
- `Registration_timing --> Cohort_characteristics --> Conversion`

This is the open back-door path. The path `Treatment <- last_digit <- UserID <- Registration_timing -> Cohort_characteristics -> Conversion` is not blocked by anything in the naive comparison. The naive difference in conversion rates conflates the checkout effect with any systematic difference in conversion propensity between older and newer user cohorts.

---

## Step 3: Where the Analyst's Reasoning Breaks Down

The analyst says: "User IDs are arbitrary, so the last digit is essentially random."

There are two separate claims embedded here, and they need to be evaluated independently:

**Claim 1: The last digit is uniformly distributed across the population.** This is likely true. For a large sequential integer range, every last digit (0–9) appears in exactly 10% of users. The last digit does not predict account age in a simple correlation sense, because by construction, every cohort of 10 consecutive IDs contains all 10 digits equally.

**Claim 2: The last digit is independent of potential conversion outcomes.** This is the claim that matters causally, and it is much harder to defend. "Uniform distribution" and "independence of outcomes" are not the same thing. The last digit being uniformly distributed across registration cohorts is entirely consistent with the two treatment groups having systematically different conversion propensities — because those propensities track registration cohort, not last digit per se.

The engineer is pointing at the right concern: the assignment rule is deterministic and encodes account age information through the sequential ID structure. Any factor that predicts whether a user converts and is correlated with registration timing is a potential confounder. In most real products, this list is long:

- Older users have higher trust, product familiarity, and brand affinity.
- User acquisition channel mix shifts over time — early users often come from founder-led referrals and investor networks; later users from paid acquisition with different intent profiles.
- Product quality improves over time; users who registered after major product improvements may have experienced a better onboarding and have higher baseline engagement.
- Seasonal effects: conversion rates for users who registered in Q4 (holiday buying patterns) differ from those who registered in Q1.

Each of these opens a back-door path from Treatment to Conversion through Registration_timing.

---

## Step 4: The Engineer's Framing Is Slightly Imprecise But Directionally Correct

The engineer says "this just compares newer users to older users." Technically, that is not quite right either — as noted above, last digit is balanced across cohorts if IDs are assigned in a perfectly uninterrupted sequence. Every cohort has last digits 0–9 in equal proportion.

But the engineer's deeper concern is valid: the assignment is **deterministic given the user's ID**, and anything that correlates with user ID (beyond the last digit itself) correlates with treatment. The engineer is correct that this is not a valid randomization. The framing "newer vs. older users" is a shorthand for "users with systematically different cohort characteristics," which is the real concern.

There is also a practical concern the engineer may be gesturing at: **ID gaps and batching**. If IDs were not assigned in a perfectly uninterrupted sequence — e.g., blocks of IDs were reserved for enterprise accounts, test users, or imported accounts — then certain last-digit ranges may be over-represented in specific cohorts or user types. This would create direct confounding even in the marginal distribution of last digits.

---

## Step 5: Structural Classification of the Key Variable

Applying the per-variable classification from Pearl's framework to `last_digit(UserID)` as the assignment mechanism:

- **Is `Registration_timing` a confounder (fork)?** Yes. It causes both the treatment assignment (via sequential ID) and conversion outcomes (via cohort characteristics). Under the DAG, conditioning on it is necessary for identification.
- **Is `last_digit` independent of `Registration_timing`?** At the margin, approximately yes — but conditioning on `Registration_timing` (account age), within each cohort window, `last_digit` should be uncorrelated with conversion. This is the kernel of truth in the analyst's argument, and it points toward a path to recovery.

---

## Step 6: Can You Recover a Valid Causal Estimate?

Possibly, but under assumptions that need to be stated and checked — not assumed.

### Option A: Back-Door Adjustment on Account Age / Registration Cohort

If `Registration_timing` (or a proxy like account age, registration date, or ID range) is the primary confounder, then conditioning on it blocks the back-door path.

- Stratify users by cohort (e.g., weekly or monthly registration windows).
- Within each cohort stratum, compare conversion rates for last-digit groups 0–4 vs. 5–9.
- Aggregate via the back-door formula: ATE = sum over cohorts of [E[Y|T=1, Cohort=c] - E[Y|T=0, Cohort=c]] * P(Cohort=c).

**Validity condition:** Within each cohort stratum, `last_digit` must be independent of unobserved factors that cause conversion. This is plausible — within a narrow registration window, ID assignment is approximately arbitrary. Whether it holds depends on how narrow your cohort strata are and whether there are sub-cohort patterns (e.g., time-of-day effects on who registers).

**Balance check:** Within each stratum, compare the two treatment groups on pre-treatment observables (number of sessions before reaching checkout, acquisition source, device type). If balanced, the within-stratum comparison is defensible.

### Option B: Difference-in-Differences (If Pre-Period Data Exists)

If the bug was introduced at a specific date, and you have pre-bug conversion data for both groups (old checkout for everyone), you can run DiD:
- Compare the change in conversion from pre-bug to post-bug between the two last-digit groups.
- This controls for any stable, time-invariant differences between the groups.
- **Requires parallel trends:** absent the new checkout, the two groups would have evolved similarly post-bug. This is plausible but should be checked using pre-period placebo tests.

### Option C: Local Randomization Interpretation

Within any 10-consecutive-ID window, the assignment of last digits 0–9 is completely balanced. If you treat each window of 10 users as a micro-RCT, the within-window comparison is valid by construction. Aggregating these micro-estimates across all windows avoids the cross-cohort confounding problem.

In practice this is equivalent to Option A with very fine cohort strata, and the power concern is the same: you need enough users per window to detect the effect.

### Option D: Run a Proper Experiment

The cleanest answer: do not use the buggy assignment data as the primary causal estimate. Run a properly randomized experiment where treatment is assigned by a cryptographic random hash of a random salt (not any function of user ID), with pre-stratification by account age if desired. This gives unambiguous causal identification and eliminates the need for back-door adjustment entirely.

---

## Step 7: The Core Trap

The trap here is **mistaking "no intentional selection" for "as-if random."**

"Arbitrary" in the colloquial sense means the rule was not designed to select users based on quality. But valid natural experiments require more: the assignment variable must be genuinely uncorrelated with potential outcomes, not merely unintentional. A coin flip that happens to land heads for all users who signed up in December is not a valid experiment, even if the coin was fair.

Sequential ID assignment is not intention-neutral with respect to causal identification: it encodes registration order, registration order encodes time, time encodes cohort, cohort encodes user characteristics that predict conversion. The question is not whether this encoding is *intended* but whether it *exists*.

---

## Summary

| Claim | Assessment |
|---|---|
| "Last digit is arbitrary, so it's essentially random" (analyst) | Partially true in a statistical sense (last digit is uniform), but false for the causal purpose. Uniformity of assignment is not the same as independence of potential outcomes. |
| "This compares newer users to older users" (engineer) | Directionally correct. The precise mechanism is that sequential IDs encode registration cohort, which is a confounder via the fork `Registration_timing --> Treatment` and `Registration_timing --> Conversion`. |
| "+4.2% is our causal estimate" (analyst) | Not valid as stated. This is a confounded association. The checkout effect and cohort effects are mixed. |
| "We can never recover a valid estimate from this data" | Too strong. Back-door adjustment on account age / cohort, or DiD if pre-period data exists, may allow identification under defensible assumptions. |

**Practical recommendations:**

1. Do not act on the +4.2% as a confirmed causal effect.
2. Run a balance check immediately: compare account age, acquisition source, pre-checkout session counts, and device type between the two groups. If they are well-balanced, the confounding threat is reduced.
3. If cohort imbalance exists, run cohort-stratified analysis with back-door adjustment on registration date.
4. If pre-bug conversion data exists for both groups, run a DiD analysis.
5. In parallel, fix the bug and run a properly randomized A/B test.

The senior engineer's instinct is correct. Sequential assignment is not equivalent to random assignment, and "arbitrary" is not the same as "independent of all potential confounders." The +4.2% requires adjustment before it can be interpreted causally.
