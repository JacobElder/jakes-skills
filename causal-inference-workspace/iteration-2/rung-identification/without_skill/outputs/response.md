## How to Be Confident Your New Onboarding Flow Is Driving 30-Day Retention

The core challenge you're facing is distinguishing correlation from causation. Retention going up after you shipped the new flow could mean the flow caused it — or it could mean something else changed at the same time (seasonality, a marketing push, a product update, the kind of users you were acquiring that month). Here's how to think through it rigorously.

---

### The Fundamental Problem: Confounding

When you ship a new onboarding flow to all users, everyone who signed up after the launch gets the new experience. That means you're comparing users from two different time periods, and time is a massive confounder. Users in different cohorts differ in:

- When they heard about your product (different channels, campaigns)
- What stage of the market you're in
- What other product changes landed in the same release
- Seasonal effects (e.g., January signups vs. summer signups behave differently)

A raw before/after comparison ("retention was 20%, now it's 28%") doesn't tell you the flow caused the improvement. It tells you something changed.

---

### The Gold Standard: A Randomized Experiment (A/B Test)

If you haven't already run an A/B test, that's the clearest path to causal confidence:

- Randomly assign new users to old flow (control) vs. new flow (treatment)
- Measure 30-day retention for both groups
- Because assignment is random, the two groups are identical in expectation on every confound — so any difference in retention is attributable to the flow

If you're still in the process of rolling out, you can still run this. Hold back ~20-50% of new signups on the old flow, measure both groups for 30 days, then compare. The longer you wait to run the experiment, the harder it gets to isolate the effect cleanly.

**What "statistically significant" means here:** Run a two-proportion z-test or chi-squared test. You need enough users in each group that the difference is unlikely to be noise. A rough rule: if your baseline retention is ~20% and you want to detect a 5 percentage point lift, you need roughly 1,500–2,000 users per group.

---

### If You Shipped to Everyone (No A/B Test): Quasi-Experimental Options

If the new flow already went to all users with no holdout, you have a few options, each with tradeoffs:

**1. Interrupted Time Series (ITS)**
Plot your 30-day retention cohort by cohort (weekly or monthly) going back 6-12 months before the launch, then continue through post-launch cohorts. Look for:
- A level change at the launch date (retention jumps)
- A slope change (retention trend accelerates)

The strength here is that you're using the historical trend as your counterfactual. The weakness is that if anything else changed around launch, you can't separate it out.

**2. Difference-in-Differences (DiD)**
This requires a comparison group that didn't receive the new flow but is otherwise similar — for example:
- Users in a market or country where you hadn't yet rolled out the flow
- A different user segment (e.g., mobile vs. web, if one got it first)

Compare the change in retention for the treated group vs. the change for the untreated group over the same period. If the treated group improved more, and you believe the two groups would have moved in parallel absent the intervention (the "parallel trends" assumption), you have a causal estimate.

**3. Regression Discontinuity (RD)**
If there was a sharp cutoff date when the new flow launched, you can compare users who signed up just before the cutoff to users who signed up just after. Users on either side of the cutoff are essentially random (no one chose which flow they'd see based on their sign-up date). This is a strong design if you have enough users near the cutoff.

---

### What to Watch Out For

**Novelty effects:** Users often engage more with anything new. If the "new flow" effect fades over 2-3 cohorts, it may be novelty, not a durable retention driver.

**Cohort size differences:** If you scaled up acquisition around the same time you launched the flow, your cohorts may be larger and potentially composed of different user types (e.g., broader targeting).

**Incomplete 30-day windows:** Make sure you're only measuring cohorts that have had a full 30 days to convert. Measuring a cohort that's only 15 days old will artificially suppress retention.

**Multiple simultaneous changes:** Did pricing change? Did you ship a major feature? Did a competitor do something? Any of these could explain the lift independently.

---

### Practical Recommendation

If you still have time to act:
1. Run an A/B test immediately, even with a 10-20% holdout on the old flow, for at least 30 days.
2. This will give you a clean causal estimate and let you shut down the test confidently.

If the ship has sailed:
1. Run an interrupted time series on your historical retention cohorts.
2. Look hard for any comparison group to run a DiD.
3. Build the case by ruling out alternative explanations one by one (document what else changed, check if those changes would predict the magnitude of lift you saw).

The goal isn't to prove the flow works — it's to test whether alternative explanations can account for the improvement. If you can rule out the major confounds, your confidence in the flow as the cause grows substantially.

---

### Summary

| Situation | Best Approach | Confidence Level |
|---|---|---|
| Still rolling out | A/B test with holdout | High (causal) |
| Already shipped, good historical data | Interrupted time series | Medium |
| Already shipped, comparison group available | Difference-in-differences | Medium-High |
| Sharp cutoff date, enough users | Regression discontinuity | High |
| Only before/after averages | Raw comparison | Low (correlational) |

The numbers looking better is a promising signal. But "promising signal" and "the flow is doing it" are different claims, and they warrant different levels of confidence in your roadmap decisions. Use one of the above designs to close that gap.
