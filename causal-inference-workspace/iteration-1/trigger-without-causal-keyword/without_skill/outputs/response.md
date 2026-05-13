# Is Your New Onboarding Flow Actually Driving 30-Day Retention?

You've shipped a new onboarding flow and retention numbers look better. That's exciting — but you're right to be cautious. Correlation in time does not equal causation. Here's how to think through this rigorously and build real confidence in whether the onboarding flow is the cause.

---

## The Core Problem: Confounding

When you observe that retention improved after shipping a new feature, several things could explain it:

- **The new onboarding flow** (what you want to credit)
- **Seasonal effects** — maybe this cohort signed up during a period of higher intent
- **Marketing channel mix** — maybe paid/organic mix shifted and you're now acquiring higher-quality users
- **Other simultaneous product changes** — did anything else ship around the same time?
- **Regression to the mean** — if retention was unusually low before, it may have naturally rebounded
- **Macroeconomic or market trends** — external factors unrelated to your product

Any of these could produce the pattern you're seeing. The goal is to isolate the effect of the onboarding flow specifically.

---

## The Gold Standard: A/B Test (Randomized Controlled Experiment)

If you haven't run one yet, **the cleanest path forward is to run a proper A/B test**:

1. Randomly assign new users to either the old onboarding flow (control) or the new one (treatment)
2. Track 30-day retention for both groups
3. Compare outcomes after a sufficient sample size is reached

Why randomization matters: by randomly assigning users, you ensure that both groups are statistically equivalent on everything *except* the onboarding flow. This eliminates confounding.

**Key implementation details:**
- Use stable user-level randomization (e.g., hash of user ID mod 100), not session-level
- Don't peek at results too early — use a pre-specified sample size calculation based on your expected effect size and desired statistical power (typically 80%)
- Use a two-sided test unless you have strong prior reason to expect improvement only
- Report confidence intervals, not just p-values

If you've already fully rolled out the new flow, a prospective A/B test would require partially rolling it back, which may not be acceptable. In that case, you'll need quasi-experimental methods.

---

## If You Already Fully Shipped: Quasi-Experimental Methods

### 1. Difference-in-Differences (DiD)

Compare the *change* in retention from before to after the launch, for your affected users, against the *change* for a comparable group that wasn't affected.

**Example:** If you only launched the new onboarding to mobile users and desktop users got the old flow, you can compare:
- Mobile retention before vs. after (the "treatment" change)
- Desktop retention before vs. after (the "control" change)

The difference of these two differences isolates the treatment effect, under the assumption that both groups would have had parallel trends absent the intervention.

**What to watch out for:** The "parallel trends" assumption is key and often violated. Validate it by checking that pre-launch trends were similar for both groups.

### 2. Regression Discontinuity Design (RDD)

If there was a sharp cutoff date when the new flow launched, you can compare users who signed up just before the launch vs. just after. Users right around the cutoff are likely very similar in characteristics, so any sharp jump in retention at the cutoff is attributable to the new flow.

**This works well when:**
- The launch was a clean, instantaneous rollout (not gradual)
- You have enough users in a narrow window around the launch date
- There were no other major changes happening simultaneously

**What to watch out for:** Other confounding events that happened simultaneously, and whether user sign-up patterns changed around the launch date.

### 3. Interrupted Time Series (ITS)

Model the trend in retention over time before your launch, project what retention would have looked like if the trend continued, and compare that projection to what actually happened after launch.

- Fit a regression model to pre-launch data: `retention = f(time) + error`
- Project this forward past the launch date
- The gap between projected and actual post-launch retention is your estimated treatment effect

**This works well when:**
- You have a long pre-launch time series (ideally 6+ months of weekly/monthly cohort data)
- There are no other simultaneous changes that could explain a break in trend

---

## Checklist: Questions to Ask Before Drawing Conclusions

- [ ] Did anything else change at the same time? Other feature launches, pricing changes, marketing campaigns?
- [ ] Did your user acquisition mix change? New channel, different geographic focus, different ad targeting?
- [ ] Is there seasonality? Compare to the same period last year if possible
- [ ] Is the improvement durable? Check whether retention is still improved 2-3 months post-launch
- [ ] Is it consistent across segments? If the new flow helps, you'd expect to see the effect in most user segments
- [ ] Is the effect size plausible? Extremely large effects (>10-15% relative lift) are rare and warrant more scrutiny
- [ ] How many users are in the post-launch cohort? Small samples produce misleading results

---

## Practical Recommendation: What to Do Right Now

1. **Segment and sanity check.** Pull 30-day retention by signup week for the past 12 months. Plot it. Look for whether the improvement coincides cleanly with your launch date and whether it persists.

2. **Control for acquisition channel.** Compare pre/post retention *within* each acquisition channel. If all channels improved, that's stronger evidence for the product change.

3. **Run a holdout if you can.** Even now, you can create a small holdout group (5-10% of new users) who receive the old onboarding. Let it run for 6-8 weeks. This is the fastest path to causal evidence if a full rollback isn't feasible.

4. **Document your assumptions.** Whatever method you use, write down the assumptions required for the estimate to be valid — then actively look for evidence those assumptions are violated.

5. **Communicate uncertainty.** "Retention improved 8-12 percentage points, and our best evidence suggests the new onboarding explains most of this, though we can't fully rule out [X]" is more credible than false precision.

---

## Summary

| Method | When to use | Key assumption |
|---|---|---|
| A/B test | Best option; use prospectively | Random assignment achieves balance |
| Difference-in-Differences | When you have an unaffected comparison group | Parallel trends pre-launch |
| Regression Discontinuity | When launch was sharp, users right around cutoff are similar | No other changes at exact cutoff |
| Interrupted Time Series | Long pre-launch time series, no comparison group needed | Pre-trend projection is valid |

The numbers looking better is a promising signal. The goal isn't to dismiss the result — it's to build confidence that your team is making the right call when deciding whether to invest further in this direction. Rigorous analysis protects you from doubling down on something that isn't working, and gives you justified confidence when it is.
