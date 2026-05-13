# Causal Analysis: Sequential User ID Assignment as A/B Test

## The Short Answer

The senior engineer is right, and the junior analyst is wrong — but the full picture is more nuanced than either framing suggests. Whether the +4.2% is a valid causal estimate depends entirely on whether user ID assignment is sequential in a way that confounds the treatment-outcome relationship. If IDs are assigned sequentially (older users have lower IDs), then the "treatment" and "control" groups differ systematically on user tenure, and the estimate is confounded.

---

## Step 1: Name the Rung

The question is rung 2 (Intervention): *What would happen to conversion if we deployed the new checkout to all users?* That's P(conversion | do(checkout = new)) vs. P(conversion | do(checkout = old)).

The analyst is treating the observed data as if it answers this question cleanly. To do that, the assignment mechanism needs to be as-good-as-random — i.e., a valid natural experiment. The debate is exactly about whether that condition holds.

---

## Step 2: Sketch the DAG

Here is the structural picture under the senior engineer's hypothesis:

```
User ID → User Tenure → [Usage patterns, familiarity, historical behavior] → Conversion
    ↓
Last digit (0–4 vs 5–9) → Checkout version → Conversion
```

More formally, let:

- **U** = User ID (a number, assigned sequentially over time)
- **T** = User tenure (how long the user has been on the platform) — this is a function of U, so U → T
- **X** = Checkout version (new vs. old) — a deterministic function of U's last digit, so U → X
- **Y** = Conversion

Because U is the common cause of both X (through its last digit) and T (through its magnitude), and T causally affects Y, the DAG is:

```
U → X → Y
U → T → Y
```

This is a **fork**: U is a common cause of both X and T, and T affects Y. That means there is a back-door path:

**X ← U → T → Y**

This is an open, non-causal path from checkout version to conversion. It is confounding. The observed difference in conversion rates is a mix of the checkout effect and the tenure effect.

---

## Step 3: Evaluate the Junior Analyst's Claim

The analyst's argument is: "Last digits are arbitrary, so the groups are as good as randomly assigned."

This argument would be valid if last digits were *independent* of everything else that affects conversion. But under sequential ID assignment:

- Users with IDs ending in 0–4 are, on average, **newer users** (their IDs include the most recently issued numbers, which cluster in the lower last-digit range relative to sequential blocks)
- Users with IDs ending in 5–9 are, on average, **older users**

Wait — let's be more precise. Sequential assignment means user 1 was registered first, user 2 second, and so on. The last digit cycles 1,2,3,4,5,6,7,8,9,0,1,2,... This means the distribution of last digits across all users is nearly uniform — *that part* is correct. But the key question is not whether last digits are uniformly distributed; it's whether **last digit is independent of tenure and other confounders conditional on being a user at all**.

Under simple sequential assignment (no gaps, no deletions), the last digit is essentially uniform across all users regardless of when they joined. The analyst is right that, marginally, last-digit assignment looks roughly random.

**However**, the senior engineer's concern holds in a more specific way: if user IDs are issued in blocks, recycled, or assigned with any pattern (common in real systems — auto-increment databases, cohort-based ID ranges, soft-deleted accounts leaving gaps), then last digit can correlate with cohort membership. Real-world examples:

- **Auto-increment with gaps**: Deleted or soft-deleted users leave gaps. If early cohorts have higher churn/deletion rates, surviving users with low-range IDs (low last digits in the low hundreds or thousands) may skew older *and* higher-value.
- **Batch or cohort-based ID assignment**: Some systems assign IDs in blocks per acquisition channel, campaign, or geography. A batch starting at 10,000 has last digits 0–9 in order but the *block itself* may correspond to a specific user cohort.
- **ID ranges per product region**: Users from different markets or products may have IDs in different numeric ranges, making last digit correlated with geography or product line.

The analyst's claim requires assuming none of these patterns exist. That's an empirical question, not a logical one — and it's the first diagnostic you should run.

---

## Step 4: The Identification Problem

For the +4.2% to be a valid causal estimate of the checkout effect (the ATE), the assignment mechanism must satisfy:

1. **Relevance**: Last digit determines checkout version. Check — it does by construction.
2. **Independence (as-if-random)**: Last digit is independent of potential outcomes Y(0) and Y(1), conditional on observed covariates. This is the disputed assumption.
3. **Exclusion restriction**: Last digit affects conversion *only through* checkout version, not through any other pathway.

The independence assumption fails if last digit correlates with tenure, acquisition cohort, geography, or any other driver of conversion. The senior engineer's concern is precisely about this assumption.

Even if the last digit is marginally uniform, the *question* is whether it's associated with pre-treatment covariates that drive conversion. This is testable.

---

## Step 5: How to Diagnose Whether This Is Valid

Run a **balance check** (covariate balance test) — the equivalent of checking randomization integrity in an RCT:

| Covariate | New Checkout (digits 0–4) | Old Checkout (digits 5–9) | p-value |
|-----------|--------------------------|--------------------------|---------|
| Account age (days) | ? | ? | ? |
| Historical conversion rate (pre-experiment) | ? | ? | ? |
| Number of prior purchases | ? | ? | ? |
| Acquisition channel | ? | ? | ? |
| Geography / market | ? | ? | ? |

If these are balanced, the analyst's claim gains empirical support. If they're imbalanced — especially on account age or historical conversion rate — the engineer is right and the estimate is confounded.

**The single most diagnostic check**: compare the *pre-experiment* conversion rates of the two groups. If users with IDs ending in 0–4 had higher (or lower) conversion rates *before* the new checkout was deployed, last-digit assignment is not as-if-random, and the +4.2% is not a clean causal estimate.

---

## Step 6: What Can Be Salvaged

If confounding is detected, you have a few options:

1. **Back-door adjustment**: Control for account age, historical conversion rate, acquisition cohort, and other confounders in a regression. This recovers the causal effect *if you can measure all the confounders* — a strong assumption in practice.

2. **Differences-in-differences (DiD)**: If you have pre-period conversion data for both groups, DiD removes time-invariant user-level confounders under the parallel trends assumption. This is likely your best option here — compare the *change* in conversion for each group from pre to post the checkout deployment.

3. **Abandon the natural experiment, run a proper RCT**: Assign users to checkout versions using a cryptographic hash of their user ID (not the last digit), or a purpose-built experiment layer with true randomization. This eliminates the structural confound entirely.

---

## Step 7: Flag the Most Likely Trap

The trap here is **mistaking a deterministic function of a non-random variable for randomization**. User IDs are not random draws from a uniform distribution — they're sequential records of when users joined. Last digits of sequential integers are nearly uniform in distribution, which *looks* like randomization but isn't the same as causal independence from outcomes. Uniform distribution of the treatment variable is a necessary but not sufficient condition for unconfoundedness.

The junior analyst is reasoning about the marginal distribution of last digits. The senior engineer is reasoning about the joint distribution of last digit, tenure, and conversion — which is the right question.

---

## Summary Verdict

| Claim | Verdict | Reasoning |
|-------|---------|-----------|
| Junior analyst: "Essentially random, +4.2% is the causal effect" | Likely wrong | Requires last digit to be independent of all conversion drivers; sequential ID assignment creates tenure confounding that needs to be empirically ruled out, not assumed away |
| Senior engineer: "Just compares newer to older users" | Directionally right, but overstated | Under pure sequential assignment, last digit is uniform, so it's not *purely* a tenure comparison — but the confounding risk is real and must be tested |
| +4.2% is a valid causal estimate | Unknown until balance checks are run | If groups are balanced on pre-treatment covariates, the estimate may be defensible; if imbalanced, it's confounded and needs adjustment or a proper experiment |

**The right next step is not to argue about whether IDs are "random enough" — it's to run the balance checks and the pre-period conversion comparison.** Those are empirical questions with empirical answers. The causal framework tells you what to check; it doesn't tell you what you'll find.
