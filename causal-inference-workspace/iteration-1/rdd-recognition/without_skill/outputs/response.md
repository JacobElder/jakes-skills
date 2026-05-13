# Estimating the Causal Effect of Your Discount on User Return Behavior

## The Core Problem

You want to know whether the 20% discount **causes** users to come back — not merely whether discounted users happen to return at higher rates. This is a causal inference question, and the setup you've described is actually ideal for one of the cleanest natural experiment designs available: a **Regression Discontinuity Design (RDD)**.

---

## Why RDD Is the Right Tool Here

Your discount policy creates a sharp threshold: users with an engagement score **below 50** get the discount; users **at or above 50** do not. This is exactly the structure RDD exploits.

The key insight: users with a score of 49 and users with a score of 51 are nearly identical in every observable and unobservable way — the only meaningful difference between them is that one group received the discount and the other did not. By comparing outcomes just around the threshold, you can isolate the causal effect of the discount without needing a randomized experiment.

---

## How to Implement It

### 1. Define Your Running Variable and Outcome

- **Running variable**: the engagement score (continuous, centered at 50 for convenience)
- **Treatment**: receiving the 20% discount (score < 50)
- **Outcome**: a measure of "coming back" — e.g., 30-day return rate, sessions in the following 30 days, revenue in the next quarter, or time-to-next-visit

### 2. Visualize the Data First

Plot the **mean outcome** against binned engagement scores. You should see a smooth relationship on either side of the threshold, with a visible jump (or lack thereof) right at 50. This is both a diagnostic and a communication tool.

```
Mean return rate
    |
    |       . . . . .
    |   . .             ← left side (discount group)
    | .   [JUMP?]
    |         . . . . . ← right side (no discount)
    |
    +---+---+---+---+---+---
       45  48  50  52  55   Engagement Score
```

### 3. Fit the RDD Model

The basic estimating equation:

```
Outcome_i = α + β·Treated_i + f(Score_i) + ε_i
```

Where:
- `Treated_i = 1` if score < 50, else 0
- `f(Score_i)` is a flexible function (polynomial or local linear) of the running variable, estimated separately on each side of the threshold
- `β` is your causal estimate — the local average treatment effect (LATE) at the threshold

**Practical recommendation**: Use a **local linear regression** with a data-driven bandwidth selector (e.g., the Imbens-Kalyanaraman or Calonico-Cattaneo-Titiunik optimal bandwidth). Avoid high-degree polynomials — they can produce spurious results near boundaries.

In Python, the `rdrobust` package handles this cleanly:

```python
from rdrobust import rdrobust, rdplot

# score_centered = engagement_score - 50
result = rdrobust(y=outcome, x=score_centered, c=0)
print(result.summary())

# Visual
rdplot(y=outcome, x=score_centered, c=0)
```

In R:
```r
library(rdrobust)
rdr <- rdrobust(y = outcome, x = score_centered, c = 0)
summary(rdr)
rdplot(y = outcome, x = score_centered, c = 0)
```

### 4. Check the Key Assumptions

RDD has two critical assumptions to validate:

**a) No manipulation of the running variable (McCrary density test)**
Users shouldn't be able to game their engagement score to get just below 50. Test this by checking whether the density of the running variable is smooth at the threshold — a spike just below 50 would indicate bunching/manipulation.

```python
from rdrobust import rddensity
rdd_test = rddensity(X=score_centered, c=0)
print(rdd_test.summary())
```

**b) No discontinuities in pre-treatment covariates (covariate balance)**
Run the same RDD model but replace the outcome with baseline covariates (e.g., prior-period engagement, account age, plan type). If there are jumps in these at the threshold, something is wrong with the design.

---

## Interpreting the Result

The `β` coefficient gives you the **Local Average Treatment Effect (LATE)** — the causal effect of the discount for users whose score is near 50. This is not the average effect for all users with score < 50; it is the effect specifically for the marginal users near the threshold.

This is usually the most policy-relevant estimate anyway: if you're deciding whether to keep or change the threshold, it's the users near that boundary whose behavior determines whether the cutoff is well-calibrated.

---

## Common Pitfalls to Avoid

| Pitfall | Why It Matters | Fix |
|---|---|---|
| Using too wide a bandwidth | Includes users far from threshold who aren't comparable | Use optimal bandwidth selection |
| High-degree global polynomials | Sensitive to data far from cutoff, can be misleading | Use local linear regression |
| Ignoring score manipulation | Invalidates the quasi-random assignment | Run the density test |
| Conflating LATE with ATE | Overgeneralizing findings | Be explicit that the estimate is local to the threshold |
| Not checking covariate balance | Threshold may coincide with a policy change or data artifact | Run placebo covariate tests |

---

## Alternative Designs (If RDD Doesn't Work)

RDD requires that the score is **not manipulated** and that the threshold was **not chosen in response to outcomes**. If either is violated, consider:

- **Difference-in-Differences (DiD)**: if the policy was rolled out at a specific date, compare score-below users before and after rollout vs. score-above users across the same period
- **Matched observational study**: match each discounted user to a similar non-discounted user on observable covariates and compare outcomes — weaker than RDD but sometimes the only option
- **Randomized holdout**: going forward, randomly withhold the discount from a small fraction of below-50 users — this is the gold standard and eliminates all assumption-checking

---

## Summary

Your setup is a textbook case for **Regression Discontinuity Design**. The engagement score cutoff at 50 creates a natural experiment: users just below and just above the threshold are essentially identical except for discount receipt. Fit a local linear RDD, validate the no-manipulation and covariate-balance assumptions, and the resulting estimate will be a credible causal effect of the discount on return behavior — no randomization required.
