# Is an 18% Retention Improvement a Reasonable Expectation for a Full Rollout?

**Short answer: No. The 18% figure almost certainly overstates what you should expect from a full rollout, and the gap could be substantial.**

---

## What Your Experiment Actually Measured

The effect you observed — +18% retention among users who opted in, relative to a matched control of users who were invited but declined — is technically called the **Average Treatment Effect on the Treated (ATT)**.

It answers the question: *"Among the specific users who chose to try the new dashboard, how much did it help them?"*

This is a valid and meaningful number. But it is not the same as the **Average Treatment Effect (ATE)**, which answers: *"If we gave the new dashboard to everyone, what retention improvement would we see on average across all users?"*

When you roll out to all users, you're estimating the ATE — not the ATT. Planning as though ATT = ATE is one of the most common errors in product experimentation.

---

## Why the ATT Likely Overstates the ATE Here

### 1. Self-Selection Bias (The Core Problem)

Only 12% of invited users opted in. That 12% is not a random sample of your user base — they are almost certainly your **most engaged, most curious, or most change-tolerant users**. These are exactly the users most likely to benefit from a redesigned dashboard, because:

- They were willing to change their workflow voluntarily.
- They likely explored the new features more thoroughly.
- They may have been experiencing friction with the old design and were actively seeking improvement.
- Their higher intrinsic motivation means they would benefit more from any improvement, not just this one.

The 88% who declined to opt in represent a very different population: users who are more habit-bound, less engaged, or more skeptical of change. When you force the new dashboard on them, you should expect:

- Lower adoption and exploration of new features.
- Higher confusion and friction during the transition.
- Potentially negative short-term effects for some segments (e.g., power users with deeply ingrained workflows).

### 2. The Matched Control Group Has Limits

Matching on observable characteristics (demographics, activity level, tenure, etc.) helps, but it cannot fully correct for the *unobservable* differences between people who opted in and those who didn't. The very act of opting in is a signal of something about the user that your matching variables don't capture. This residual self-selection means the ATT is still a biased estimate of the ATE even after matching.

### 3. Demand Effects and Novelty

Users who voluntarily try something new often show elevated engagement simply because the experience is novel and they feel invested in it. This "novelty effect" inflates measured retention in opt-in experiments. In a full rollout, the novelty is diluted across the whole population and may disappear entirely for users who didn't choose to participate.

---

## A More Realistic Framework for Projection

Rather than assuming ATE = ATT, your team should think about the user population in layers:

| Segment | Share | Expected Effect |
|---|---|---|
| Opted-in users (enthusiasts) | ~12% | ~+18% (your observed ATT) |
| Curious but hesitant users | ~20-30%? | Positive, but smaller — maybe +5% to +12% |
| Neutral/indifferent users | ~40-50%? | Near zero or slightly positive |
| Change-resistant / power users | ~10-20%? | Potentially negative short-term |

A rough weighted average across these segments would likely produce an ATE materially below 18% — possibly in the range of **+3% to +8%**, though the true number depends heavily on your user base composition.

---

## What You Should Do Before Rolling Out

### Run a Proper Randomized Experiment
The most reliable path is a standard A/B test: randomly assign users (not opt-in) to the new dashboard vs. the old one. This directly estimates the ATE without self-selection confounds. Even a 2-4 week holdout test on a random 20% of users would give you a far more trustworthy number.

### Segment Your Opt-In Data
Look at how the treatment effect varies across user segments in your existing data. If the effect is much larger for high-engagement users than low-engagement users, that's a direct signal that the population-wide effect will be smaller.

### Consider a Phased Rollout with Monitoring
If business pressure requires moving forward, roll out to a random subset first (e.g., 20%), measure the effect on that random sample, and compare it to your ATT of 18%. The gap between those two numbers will tell you how much the self-selection was inflating your estimate.

### Plan for Change Management
For the 88% who didn't opt in, the transition itself is a treatment cost. Invest in onboarding, tooltips, and easy revert options to minimize friction and avoid negative effects in the resistant segment.

---

## Summary

Your experiment produced a valid and useful estimate of the treatment effect for users who wanted the new dashboard. Extrapolating that directly to all users assumes those users are representative of everyone — and a 12% opt-in rate is strong evidence they are not. The self-selection almost certainly inflates the observed effect. Planning for 18% retention improvement across the full user base is optimistic at best and could lead to significant disappointment or harm for segments that weren't represented in the opt-in group.

The right move is to validate with a randomized experiment before committing to a full rollout.
