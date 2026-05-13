# Is $32 Revenue Uplift the Right Expectation for a Force-Enable Rollout?

**Short answer: No.** The $32 LATE almost certainly overstates what you should expect from force-enabling the feature for all non-adopters — possibly by a wide margin. Here is why, and what to do about it.

---

## What the LATE Actually Measures

Your encouragement design (the push notification) is a valid instrumental variable. The IV estimate recovers the **Local Average Treatment Effect** — the average treatment effect *specifically for compliers*: users who adopted the premium feature *because* they received the notification, and who would *not* have adopted it otherwise.

Compliers are a self-selected subgroup. They are the users who were on the fence — interested enough that a nudge pushed them over the threshold. By definition:

- **Always-takers** (would have adopted regardless of notification) are not in the complier population.
- **Never-takers** (would not adopt even with a notification) are also not in the complier population.
- **Defiers** (would do the opposite of the nudge) are assumed away by monotonicity, which is standard and reasonable here.

The $32 LATE is the average causal effect for compliers only. It says nothing directly about the never-takers, who are the exact population your CEO wants to force-enable.

---

## The Core Problem: Never-Takers Are Different

The users who did *not* adopt even after receiving the notification — and the users in the control group who did not self-select into adoption — are disproportionately **never-takers**. These users ignored the push notification. They had an explicit prompt to try the feature and chose not to.

There are strong reasons to expect the treatment effect for never-takers is lower than $32, possibly much lower, possibly even negative:

### 1. Selection Into Adoption Signals Value Fit
Users who adopt a premium feature — whether organically or after a nudge — are those for whom the feature is a good fit. Compliers received a push, considered it, and said yes. Never-takers received a push and said no. The feature may genuinely not serve their use case, workflow, or preferences.

### 2. Forced Adoption Can Generate Backlash
Force-enabling a feature for users who actively declined it or never expressed interest is not the same as helping a willing user adopt. Research on autonomy and reactance (Brehm's psychological reactance theory) consistently finds that users who feel their choices are overridden respond negatively — higher churn, lower engagement, more support tickets, more negative reviews. The revenue effect could be zero or negative for this population.

### 3. The ATE Requires Extrapolation Beyond the Experiment
The $32 is not an Average Treatment Effect (ATE) for the full user base. Getting from LATE to ATE requires assuming the complier effect generalizes to never-takers. There is no empirical basis for that assumption in this experiment. In many product contexts, the complier effect is substantially higher than the population-average effect.

### 4. You Have Direct Evidence: The Notification Response Rate
You have a useful signal right in the data. Among notified users, 18% adopted and **82% did not**. That 82% is largely the never-taker population. They saw your best pitch for the feature and said no. Force-enabling is a more coercive intervention, but the underlying preference signal is clear.

---

## Quantifying the Uncertainty

Let's make the math concrete. Define:

- pi_c = share of users who are compliers
- pi_n = share who are never-takers
- LATE = $32 (effect for compliers)
- LATE_n = unknown effect for never-takers

The ATE (what a full rollout affects on average) is a weighted average:

```
ATE = pi_c x LATE + pi_n x LATE_n + pi_a x 0
```

(Always-takers already have the feature; their incremental effect from force-enable is zero.)

Your compliance rate gives you a lower bound on pi_c: it's at most 15 percentage points (18% minus 3% = 15pp of users were induced to adopt by the notification). But compliers are likely a small fraction of the full user base. If the never-taker effect is anywhere near $0 or negative, and never-takers are the majority of your target population for force-enable, the expected ATE is substantially below $32.

**Example scenario:**
- Compliers: 15% of non-adopters (generous estimate)
- Never-takers: 85% of non-adopters
- LATE for compliers: $32
- LATE for never-takers: $5 (modest positive effect assumed)

Expected effect on non-adopters: 0.15 x $32 + 0.85 x $5 = $4.80 + $4.25 = **$9.05**

That is less than 30% of the $32 figure. And $5 for never-takers may itself be generous.

---

## What the CEO Should Expect Instead

The CEO should expect:

1. **The revenue uplift will likely be well below $32 per user** for the force-enabled population. A reasonable range might be $5-$15, but this is speculative without additional data.

2. **The effect will be heterogeneous.** Some non-adopters may benefit substantially; others may churn or generate support costs that offset revenue gains.

3. **There is a real risk of net negative effects** for a subset of users, particularly those who actively noticed the notification and chose not to act on it.

---

## What You Should Do Before a Full Rollout

### Option 1: Run a Direct Experiment on Force-Enable
The cleanest answer is to run a small A/B test where you actually force-enable the feature for a random subset of non-adopters and measure the revenue outcome directly. This gives you an unbiased estimate of the ATE for that population, rather than extrapolating from the LATE.

### Option 2: Bound the ATE Using Existing Data
Apply Lee (2009) bounds or Manski bounds to estimate the range of plausible ATE values given the data you have. This will not give you a point estimate but will tell you the worst-case and best-case scenarios.

### Option 3: Segment Never-Takers
Use your behavioral data to segment non-adopters into those who saw the notification (and ignored it) vs. those who may not have seen it, and further segment by engagement level, feature usage patterns, and revenue tier. The force-enable effect likely varies dramatically across these groups. Target force-enable only at segments where the signal suggests positive value fit.

### Option 4: Consider Softer Interventions First
Instead of force-enable, consider a prominent in-app prompt, an opt-out (rather than opt-in) framing, or a time-limited free trial. These interventions reach never-takers with less coercion and generate their own experimental data about the population's responsiveness.

---

## Summary

| Concept | Value | Interpretation |
|---|---|---|
| Compliance rate | 15pp (18% minus 3%) | Share of users nudgeable by notification |
| LATE | $32 | Effect for compliers only — the nudgeable users |
| Force-enable target | Non-adopters | Predominantly never-takers, not compliers |
| Expected ATE for force-enable | Unknown, likely < $32 | Requires separate experiment to estimate |
| Risk | Real | Backlash, churn, negative revenue for some users |

The $32 LATE is a real and valuable estimate — it tells you that your notification strategy works well for the users it reaches. But it is the wrong number to use for projecting the revenue impact of a force-enable rollout. The CEO's reasoning conflates the effect on compliers with the effect on a fundamentally different population: users who have already expressed, through their behavior, that they do not want this feature. Running a direct experiment on a small forced-enable cohort before a full rollout is the right call.
