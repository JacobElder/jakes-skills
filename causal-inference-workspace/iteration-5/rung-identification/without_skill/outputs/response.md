# Causal Analysis: Sequential User ID Assignment as A/B Test Randomization

## The Short Answer

The senior engineer is right, and the junior analyst is wrong. The +4.2% conversion difference cannot be treated as a valid causal estimate of the checkout redesign's effect.

---

## Breaking Down the Disagreement

### The Junior Analyst's Claim

The analyst argues that because user IDs are "arbitrary" labels, extracting the last digit is effectively random. The logic: last digits (0–9) are uniformly distributed, so there's no pattern to exploit — users should be balanced across groups.

This reasoning conflates **distributional uniformity** with **independence from confounders**. Even if last digits are uniformly distributed in aggregate, that does not mean the assignment mechanism is independent of characteristics that predict conversion.

### The Senior Engineer's Claim

Sequential ID assignment means user ID approximates account creation timestamp. Lower IDs were created earlier; higher IDs were created later. The last digit of a sequential ID encodes the **position in the sequence modulo 10**, not a random signal.

- IDs ending in 0–4: captures users at positions 0, 10, 20, ... and 4, 14, 24, ...
- IDs ending in 5–9: captures users at positions 5, 15, 25, ... and 9, 19, 29, ...

These interleave — they are not "early users" vs. "late users" in the most naive sense. But critically, they are still drawn from the same sequential stream, and if that stream has any **temporal drift** (user characteristics changing over time), then the two groups may differ systematically in ways that affect conversion.

---

## Why Sequential IDs Violate the Randomization Assumption

For a treatment assignment to support causal inference, it must be **independent of potential outcomes** conditional on observed covariates — the ignorability or exchangeability assumption. In an ideal RCT, treatment is assigned by a coin flip unrelated to any user characteristic.

Sequential user IDs carry real information:

**1. Account Tenure**
Earlier users have been on the platform longer. Older accounts may have higher purchase intent, more stored payment information, established trust in the platform, or may represent power users.

**2. Cohort Effects**
The product, marketing, and user base were different when early users signed up. Early adopters often differ in demographics, tech-savviness, and loyalty compared to users who joined years later. Users acquired via word-of-mouth in year one behave differently than users acquired via paid ads in year five.

**3. Survivorship Bias**
If the analysis is run on currently active users, older cohorts have already survived a longer attrition filter. The "older" users in the treatment group are the survivors of a long retention funnel, while newer users include many who may still churn — this operates asymmetrically across the groups.

**4. Temporal Confounds**
The economy, seasonality, competitor landscape, and the company's own product changes are different across cohorts. A user who signed up in 2018 vs. 2024 experienced different onboarding flows, different marketing, and different product quality.

---

## Formalizing the Problem with the Backdoor Criterion

For the observed difference in conversion rates to be a valid causal estimate, treatment assignment (last digit 0–4 vs. 5–9) must be independent of all confounders:

```
T ⊥⊥ Y(0), Y(1)  |  X
```

Where T is treatment, Y(t) are potential outcomes, and X are observed covariates.

With sequential IDs, **user tenure** — a strong predictor of conversion behavior — is correlated with treatment assignment. There is an open backdoor path:

```
User Tenure / Cohort → Conversion Rate (Y)
         ↓
      User ID → Last Digit → Treatment (T)
```

Without blocking this backdoor path (by conditioning on tenure or cohort), the observed difference in conversion rates is a biased estimate of the causal effect. The bias is not small and abstract — tenure and cohort effects are among the largest sources of heterogeneity in user behavior on any consumer platform.

---

## A Nuance: The Engineer's Framing Is Slightly Imprecise, But the Concern Is Valid

The senior engineer's description of "newer vs. older users" is not quite right in the most literal sense. Because the last digit interleaves groups, both the 0–4 group and the 5–9 group contain users from every period — they alternate positions in the sequence. So it's not a clean temporal split.

However, this doesn't save the analyst's argument. The real danger is:

- **Prior product changes**: If the product team made any feature changes that affected conversion rates and those changes differentially impacted users based on their signup cohort (e.g., a new onboarding flow experienced only by users who joined after a certain date), then last-digit assignment correlates with exposure to those prior changes.
- **Active-user composition**: If the analysis is restricted to active users, early cohorts may be underrepresented due to churn, distorting the effective cohort composition of each group.
- **ID-range correlations**: In practice, large blocks of IDs are often issued at once (e.g., batch account creation via enterprise signup, social network invitation waves, viral growth spikes). These create non-uniform density across the ID space that the simple interleaving model does not account for.

The mechanism the senior engineer names is real even if the precise framing of "newer vs. older" is too simple. The key point stands: sequential IDs are not random.

---

## Pearl's Ladder of Causation

Using Judea Pearl's three rungs of causation:

| Rung | Question | Method |
|---|---|---|
| 1. Association | What is the correlation? | Observational data |
| 2. Intervention | What happens if we intervene? | True experiments (do-calculus) |
| 3. Counterfactual | What would have happened? | Structural models |

The analyst wants to claim this is **Rung 2 (intervention)** — that because last-digit assignment resembles randomization, we can read off the causal effect of changing the checkout. But this only holds if the assignment satisfies exchangeability.

With sequential IDs, the assignment is effectively **Rung 1 (association)** dressed up as randomization. We observe that users with IDs ending in 0–4 have higher conversion, but this is confounded by all the cohort-related variables that correlate with account age. Reading a Rung 2 answer off Rung 1 data requires strong additional assumptions — assumptions the analyst has not stated, let alone tested.

---

## What the Junior Analyst Gets Partly Right

Within a very narrow window — say, users who all signed up on the same day — the last digit may do a reasonable job of randomizing assignment. Same-day cohorts are approximately balanced on tenure and acquisition channel, so within-cohort the last digit is uninformative. 

But:
- The analysis almost certainly pools across all users, not just same-day cohorts.
- Even within a day, the order of ID assignment within that day may correlate with behavioral patterns (e.g., users who sign up in the morning vs. evening differ on time zone, engagement level, etc.).
- The analyst's blanket claim applies to the full dataset, where the senior engineer's concern clearly applies.

The analyst has identified a real property of the last digit (uniform marginal distribution) and incorrectly inferred from it a causal property (independence from confounders). This is a common and important error.

---

## Can We Recover a Valid Causal Estimate?

Possibly, with the right steps:

**Option 1: Condition on Cohort / Join Date**
Stratify the analysis by signup cohort (e.g., week or month of signup). Within each cohort, last-digit assignment may be approximately balanced. Combine estimates across cohorts using direct standardization or regression adjustment. This requires verifying that within-cohort, last digit is truly uninformative.

**Option 2: Pre-Period Placebo Test**
If pre-experiment behavioral data exists, test whether the two groups had different conversion rates *before* the new checkout launched. A non-zero pre-period difference reveals baseline imbalance and directly falsifies the randomization claim.

**Option 3: Regression Control**
Regress conversion on treatment assignment while controlling for all relevant confounders (tenure, acquisition channel, cohort, geography, device type, etc.). This is only valid if the controls fully account for all confounding pathways — a strong and often untestable assumption.

**Option 4: Difference-in-Differences**
If pre-period data is available, use DiD to remove time-invariant cohort-level confounding. Requires the parallel trends assumption to hold.

**Option 5: Run a Proper Experiment Going Forward**
Given the severity of the confounding concern, the cleanest path is to acknowledge the design flaw and re-run a properly randomized experiment. True random assignment (e.g., a cryptographic hash of user ID with a random salt) eliminates systematic correlation with user tenure.

---

## Verdict

| Claim | Assessment |
|---|---|
| Junior analyst: "User IDs are arbitrary, so last-digit assignment is random" | **Wrong.** The assignment mechanism is deterministic and encodes user tenure via sequential ID structure. |
| Senior engineer: "This just compares newer users to older users" | **Directionally correct, slightly imprecise.** Both groups span all cohorts via interleaving, but cohort confounding remains a real and serious threat. |
| "+4.2% is our causal estimate of the checkout effect" | **Not valid as stated.** The raw comparison is confounded by cohort effects, tenure, and acquisition channel differences. |

The observed +4.2% difference is a mixture of the true checkout effect (which could be positive, negative, or even zero) and the systematic behavioral differences between user cohorts. Without controlling for cohort and tenure and passing a pre-period balance check, these cannot be disentangled. The estimate should not be used to make product decisions.

---

## Key Takeaways

1. **"Arbitrary" labels are not the same as random assignment.** Randomness is a property of the assignment mechanism, not the labels themselves. An arbitrary number that was assigned sequentially is not random.

2. **Sequential assignment encodes time.** Any variable derived from a sequential ID is implicitly a function of when the user joined the platform — one of the most powerful confounders in user behavior research.

3. **Uniform marginal distribution does not imply independence from confounders.** The last digit being uniformly distributed (0–9) does not mean it is uncorrelated with user tenure, cohort, or any other variable that predicts conversion.

4. **The Ladder of Causation matters.** This question is at Rung 2 (intervention): what would happen if we changed the checkout for everyone? Observational data with confounding cannot directly answer interventional questions without strong additional assumptions.

5. **Always examine the assignment mechanism from first principles.** A valid causal estimate requires that treatment assignment is independent of potential outcomes. That independence must be established from how units were assigned — not assumed from the superficial appearance of the treatment variable.
