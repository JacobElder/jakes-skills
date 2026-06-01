# CBC Sample Size for Pricing Study with Enterprise vs. SMB Segments

## Quick Answer

For a CBC with 6 attributes comparing two roughly equal segments, a total sample of **300–400 respondents** (150–200 per segment) is a reasonable starting point. Depending on the precision you need and the estimation method, you may want to push toward 400–600 total.

---

## Thinking Through the Problem

### 1. The Standard "Rule of 500" and Its Variants

The most widely cited heuristic for CBC sample sizes comes from Sawtooth Software and related work:

> **n ≥ 500 / (tasks × alternatives)**

For a typical CBC design with, say, 12 choice tasks and 3 alternatives per task, this yields:
- 500 / (12 × 3) = ~14 respondents minimum — clearly a floor, not a target.

A more practical and commonly used version is:

> **n × t × a ≥ 1,000 × c**

Where:
- n = sample size
- t = number of tasks
- a = alternatives per task (excluding "none")
- c = maximum number of levels for any one attribute

This ensures each level appears a minimum number of times across all respondents and tasks. With brand (say 4 levels), price (4–5 levels), and 4 features (2–3 levels each), the binding constraint is the attribute with the most levels — likely price or brand at ~4–5 levels.

### 2. Accounting for Segment Comparisons

The key complication here is that you want to **compare enterprise vs. SMB**. This shifts the sample size logic from overall precision to subgroup comparison precision.

When comparing two equal-sized groups:
- Effect sizes in preference/utility space tend to be moderate (Cohen's d ~0.3–0.5 is common in B2B segmentation).
- For a two-sample comparison at 80% power and α = 0.05 for a moderate effect (d ≈ 0.3), you need roughly **175–200 per group**.
- For d ≈ 0.5, you can get by with ~65–80 per group, but utilities from CBC are estimated with noise, so the effective effect size is smaller than the true underlying difference.

**Practical recommendation for subgroup comparison: 200 per segment = 400 total.**

### 3. Estimation Method Matters

#### Aggregate Logit (OLS on share of preference)
- Lower data requirements, but ignores individual heterogeneity.
- Suitable with 150–200 per segment if the goal is group-level estimates.

#### Hierarchical Bayes (HB)
- The current industry standard for CBC.
- HB borrows strength across respondents, so it performs well even with fewer tasks per person.
- Minimum practical sample is often cited as 150–200 total for a single group; for two-group comparisons, 150–200 per group is reasonable.
- HB also allows individual-level utilities, enabling post-hoc segmentation if your a priori segmentation turns out to be wrong.

#### Latent Class
- Requires at least 100 per latent class you want to recover; less relevant here since you have defined segments.

### 4. Design Parameters That Interact with Sample Size

The sample size is not independent of your design choices:

| Design Parameter | Effect on Required n |
|---|---|
| More choice tasks per respondent | Reduces required n (more data per person) |
| More alternatives per task | Reduces required n but increases cognitive burden |
| More attribute levels | Increases required n (more parameters to estimate) |
| Prohibitions / restrictions | Effectively reduces efficient observations; increases required n |

**Recommended design given your 6 attributes:**
- 12–15 choice tasks per respondent
- 3–4 alternatives per task (plus optional "none")
- Ensure a balanced, orthogonal or near-orthogonal design

With 12 tasks × 3 alternatives = 36 choices per respondent. At 200 per segment × 2 segments = 400 respondents × 36 choices = 14,400 total choice observations. With ~20 parameters to estimate (sum of levels minus attributes), this gives you a comfortable information ratio.

### 5. Summary Recommendation

| Scenario | n per Segment | Total n | Notes |
|---|---|---|---|
| Minimum viable (HB, 12 tasks, 3 alts) | 150 | 300 | Risk: low power for segment comparisons on secondary attributes |
| Recommended (HB, 12–15 tasks, 3 alts) | 200 | 400 | Good balance of cost and precision |
| Conservative / high-stakes pricing decisions | 300 | 600 | Supports finer subgroup cuts or post-hoc analysis |

**For a pricing study feeding product and go-to-market decisions, 400 total (200 per segment) is the pragmatic target.** If you plan to run market simulations and need tight confidence intervals on willingness to pay, lean toward 500–600.

---

## Caveats

- These figures assume clean, complete responses. Budget for 10–15% attrition/screener removal.
- If enterprise and SMB have meaningfully different base rates in your recruiting pool, ensure the segment split is enforced during fielding, not corrected post-hoc via weighting alone.
- Price attribute design (absolute dollar amounts vs. relative discounts) can significantly affect the variance of price utility estimates and thus required n. Using too many price levels or a wide range increases variance and may require a larger sample to pin down price sensitivity reliably.
