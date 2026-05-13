# Analysis: Onboarding Completion as a Lever for Long-Term Retention

## Short Answer

No — not yet. The correlation is real, but the study design makes it impossible to conclude that improving onboarding completion will *cause* better long-term retention. The analysis has a critical methodological flaw that must be resolved before investing based on this finding.

---

## The Core Problem: Survivorship Bias (a form of Selection Bias)

The analysis filtered to "users who were still active at the 90-day mark." This is the key problem. By restricting the sample to 90-day survivors before measuring the outcome (6-month retention), the team has conditioned on a variable that sits in the middle of the causal pathway — or, more precisely, has selected a non-representative subpopulation that systematically differs from all users in ways that distort the observed relationship.

This is a classic case of **survivorship bias** (a specific form of collider bias / selection bias). Here is why it matters:

### What the sample actually is

Users who reach 90 days are not a random subset of all users. They have already demonstrated higher-than-average engagement, motivation, product-market fit, and likely onboarding completion. The very users most likely to have completed onboarding are over-represented in this filtered group — not because onboarding causes retention, but because motivated users both complete onboarding *and* stay active.

### Why the correlation is misleading

Within a pre-filtered group of highly engaged users, any early behavior (including onboarding completion) will appear to correlate with later retention — not necessarily because it is causal, but because:

1. **The low-engagers are already excluded.** Users who would have churned before 90 days (and who also did not complete onboarding) are not in the sample. This artificially inflates the apparent correlation between onboarding completion and 6-month retention within the remaining group.

2. **A latent variable ("engagement propensity") drives both.** Users with high intrinsic motivation complete onboarding *and* stay retained. Onboarding completion is a *symptom* of this disposition, not necessarily a *cause* of retention. Improving the onboarding flow might not change the underlying disposition.

3. **Conditioning on a collider can induce spurious associations.** If "active at 90 days" is itself influenced by both onboarding completion and other engagement factors, conditioning on it can create or amplify correlations between onboarding and later retention that would not exist (or would be weaker) in the full population.

---

## What the Analysis Should Have Done

To properly estimate whether onboarding completion drives long-term retention, the analysis should be conducted on the **full user cohort**, not a filtered survivor group. Specifically:

| Better Approach | Why |
|---|---|
| Analyze all users from the cohort start | Avoids survivorship bias; reflects real causal population |
| Use a randomized experiment (A/B test) on onboarding | Gold standard for establishing causality |
| Apply propensity score matching or regression on the full sample | Controls for confounders without selection distortion |
| Examine onboarding completion's effect on *reaching* 90 days first | Separates the two outcomes to understand the full causal chain |

---

## What This Finding Does (and Does Not) Tell You

| Claim | Validity |
|---|---|
| Among 90-day survivors, onboarding completers are more likely to stay at 6 months | Likely true as a descriptive fact within this sample |
| Completing onboarding causes users to be retained longer | Unsupported — causality cannot be inferred from this design |
| Improving onboarding completion will improve long-term retention | Unknown — this is the causal claim that requires a better study |

---

## Practical Recommendation

Before investing in onboarding improvements as a retention lever, take these steps:

1. **Re-run the correlation on the full user cohort** (not filtered to 90-day survivors). If the effect weakens substantially or disappears, it is largely a survivorship artifact.

2. **Run an A/B test.** Randomly assign some new users to an improved/prompted onboarding experience. Measure both onboarding completion rates *and* 6-month retention. This directly tests the causal hypothesis.

3. **Instrument the causal chain.** Does onboarding completion predict *reaching* 90 days (early retention)? Does it predict 6-month retention *conditional on* reaching 90 days? Distinguishing these tells you where in the user journey onboarding actually matters.

4. **Check if onboarding completion is truly actionable.** If users who complete onboarding are simply more motivated by nature, then making onboarding easier might increase completion rates without increasing actual product engagement — a metric win with no real-world impact.

---

## Summary

The r = 0.42 correlation is statistically significant but methodologically compromised. Filtering to 90-day survivors before measuring the predictor-outcome relationship selects on engagement, inflates the correlation, and makes it impossible to establish whether onboarding completion causes retention or merely reflects the same underlying user quality. Investing based on this finding alone would risk optimizing a metric (onboarding completion) without moving the underlying driver (retention). The correct next step is a properly designed experiment or, at minimum, a re-analysis on the unfiltered cohort.
