# Estimating the Causal Effect of a Discount Given at an Engagement Score Threshold

## 1. Name the Rung

This is a **Rung 2 (intervention) question**: "Does giving the discount *do* something to return behavior?" You want P(return | do(discount)), not just the correlation between discount receipt and returns. Since the discount is assigned by company policy rather than a randomized experiment, you need a design-based identification strategy.

## 2. Sketch the DAG

```
engagement_score (S) → discount (D) → return (Y)
          ↑                              ↑
          U (unobserved user traits: motivation, platform fit, life circumstances)
```

The core problem: low-engagement users who receive the discount are *systematically different* from high-engagement users who don't. User motivation (U) drives both engagement score and return probability independently of the discount. A naive comparison — "do discounted users come back more than non-discounted users?" — confounds the discount effect with selection effects. Low-engagement users are harder to re-activate regardless of any discount.

## 3. Identify the Structure: This Is a Sharp RDD

Your engagement score is a **continuous running variable**, and your company applies a **hard threshold at 50** that deterministically assigns treatment (discount). This is the textbook setup for a **Regression Discontinuity Design (RDD)** — specifically a *sharp* RDD, because the cutoff fully determines who gets treated.

The insight: users with a score of 48 and users with a score of 52 are very similar in their underlying engagement characteristics. The only reason one gets a discount and the other doesn't is which side of 50 they happen to fall on. That near-randomness at the boundary is the identification lever.

**Formal estimand:** the local average treatment effect (LATE) at the cutoff — the average causal effect of the discount for users whose engagement score is approximately 50.

## 4. The Estimation Procedure

### Step 1: Verify the Running Variable

Plot the distribution of engagement scores. Check for **bunching just below 50** — if users or the system can manipulate the score to get below 50 and receive the discount, the "as-if-random" assumption fails. A histogram and a formal McCrary density test will tell you whether manipulation is occurring.

### Step 2: Estimate the Discontinuity

Fit separate smooth functions of engagement score on each side of the threshold, and compare the predicted outcome values at S = 50 from the left and right:

```
Y = f_left(S - 50) + D * τ + ε    for S near 50
```

where D = 1 if S < 50 (discount received), and τ is the estimated jump at the threshold.

In practice: use local linear regression with a data-driven bandwidth (e.g., the Calonico-Cattaneo-Titiunik optimal bandwidth selector, available in the `rdrobust` package in R or Python). Don't just run a global polynomial — high-degree global polynomials behave poorly near the boundary.

### Step 3: Plot the Discontinuity

A raw binned scatter plot — average return rate within small score bins, with the threshold marked — is the most intuitive check. If the discount causes returns, you should see a visible jump in return rate at S = 50. A smooth curve with no jump is evidence the discount is not working.

### Step 4: Robustness Checks

- **Bandwidth sensitivity:** Does the estimated effect hold under narrower and wider windows around the threshold?
- **Placebo thresholds:** Test for jumps at fake thresholds (e.g., S = 40, S = 60). There should be none.
- **Covariate balance:** At the threshold, pre-treatment covariates (user tenure, device type, historical purchase count) should show no discontinuity. A jump in covariates at 50 suggests manipulation or that something else also changes at 50.
- **Donut RDD:** Exclude observations very close to the threshold and re-estimate. If results are sensitive to this, it may indicate heaping or rounding in the score.

## 5. Assumptions to State Explicitly

| Assumption | Content | How to Check |
|---|---|---|
| No manipulation | Users cannot precisely sort themselves to be just below 50 | Density test, histogram inspection |
| Continuity | In the absence of the discount, expected return rate would be smooth through S = 50 | Covariate balance at threshold; placebo tests |
| SUTVA | One user's discount doesn't affect another user's return behavior | Domain judgment (usually plausible for individual discounts) |

## 6. Scope Limitation: This is a Local Effect

The RDD recovers the treatment effect **only at the threshold**. This is the causal effect of the discount for users with an engagement score near 50 — not for users with scores of 20 or 30. If you want to know whether the discount drives returns for deeply disengaged users, RDD at this threshold cannot tell you that. You'd need either a separate threshold at a lower score, or a different design.

## 7. The Trap to Avoid

Do not simply compare return rates between discounted users (S < 50) and non-discounted users (S ≥ 50) across the full population. Users below 50 are less engaged by definition, so they will likely show lower return rates than users above 50 regardless of what the discount does. This naive comparison answers the wrong question — it's a Rung 1 (association) answer dressed up as a Rung 2 (intervention) answer.

Similarly, don't "control for engagement score" in a regression covering the full score range without the discontinuity design — the functional form assumption will drive your result.

## 8. Summary: Recommended Approach

**Use a sharp RDD at S = 50.** It is the cleanest available design for this question because the threshold was set by your company's policy, not by users' choices, and the score is a continuous running variable that creates near-random assignment near the boundary.

Concretely:
1. Collect the post-discount return outcome for all users in a window around S = 50.
2. Run a density test to verify no score manipulation.
3. Fit local linear regression on each side using optimal bandwidth selection (`rdrobust`).
4. Report the discontinuity estimate τ with confidence intervals.
5. Show the binned scatter plot as a visual summary.
6. Report that the finding is local to users near the threshold and may not generalize to deeply disengaged users.

If you later want to estimate effects across the full distribution of low-engagement users, a randomized holdout (randomly withhold the discount from some fraction of users below 50) would extend the scope and remain the cleanest long-term infrastructure for measuring the discount's ROI.
