# Does the Density Spike Invalidate Your RDD?

**Short answer: Yes, the spike matters — a lot. Your data science lead's reasoning, while intuitive, is wrong. The internal/external communication of the threshold is a red herring. What matters is whether *users or anyone acting on their behalf* could have manipulated scores across the cutoff. The density spike is direct evidence that something like that happened.**

---

## Step 1: Name the Rung

This is a Rung 2 (intervention) question: does proactive outreach *cause* better retention? You want to estimate P(retention | do(outreach)) — the effect of intervening on someone's support status, not just observing who happened to receive it.

You chose regression discontinuity (RDD) to answer this, which is a design-based identification strategy. RDD's entire causal logic rests on one key assumption. The density spike you found is direct evidence against that assumption.

---

## Step 2: What RDD Requires and Why Density Is Load-Bearing

Regression discontinuity works by treating the threshold as producing locally-as-good-as-random assignment. Just below 40, users are treated. Just above 40, they are not. The identifying assumption is that — absent the threshold rule — the potential outcomes Y(0) and Y(1) would vary smoothly through the cutoff. Users at 39 and users at 41 are assumed to be otherwise identical in expectation, so the jump in outcomes at 40 is attributable entirely to the treatment.

This assumption is **violated if any user or user-adjacent actor can sort across the threshold** — that is, if anyone with knowledge of or incentives tied to the threshold has the ability to move users' health scores relative to 40.

A smooth density of the running variable (health score) near the threshold is the standard empirical test for this. The intuition: if assignment is locally as-good-as-random, you would not expect to see more mass on one side of the threshold than the other. A spike above 40 — excess density just above the cutoff — is the hallmark signature of manipulation in favor of non-treatment.

The formal test is the McCrary density test (or the more recent Cattaneo-Jansson-Ma test), which fits the density on each side and tests whether there is a statistically significant jump at the cutoff. You should run this if you haven't.

---

## Step 3: The DAG

Here is the structural picture:

```
Team Behavior / Score Process → Health Score
                                      |
                              [threshold at 40]
                                      |
                              Outreach (T=1 if <40)
                                      |
                                  Retention (Y)
```

RDD works when "Team Behavior / Score Process" is smooth through the cutoff — so that conditioning on being near 40 makes assignment as-good-as-random. The density spike is evidence that this node has a discontinuity at 40, meaning there is now a fork between score-generating factors and both treatment assignment and potential outcomes. That is a confound.

Put differently: the variable you're using as your running variable is not clean. Health score is supposed to be a pre-treatment summary of user state, but if the support team's awareness of the threshold influences how scores are recorded or updated, then the score is partially a post-threshold-awareness variable. RDD requires the running variable to be unmanipulated.

---

## Step 4: Why "Only Communicated Internally" Is Not Exculpatory

Your data science lead's argument is: "users don't know about the threshold, so they can't game it." This is partially correct but misses two critical failure modes.

**Failure mode 1: The support team itself is the manipulator.**

The threshold was communicated to the support team. Support agents are now aware that users at score 40+ do not receive outreach. If any support agent — or any automated workflow triggered by the support team's tooling — can influence health scores (through activity crediting, data entry, engagement nudges, or score corrections), they have an inadvertent or deliberate incentive structure to push borderline users above 40.

Why would they? Several plausible mechanisms:

- **Workload management.** If outreach requires effort, a team under capacity pressure might resolve borderline cases by pushing marginal users to the "no outreach needed" side.
- **Optimism bias.** Agents reviewing accounts and entering qualitative signals might round up for users who seem "probably fine," inflating scores just above 40.
- **Automated triggers.** If any process runs when a support interaction is logged (e.g., logging a contact as a positive engagement signal that increments the health score), then the act of initiating outreach for a user near 40 might mechanically raise their score above the threshold, causing them to exit the treatment-eligible pool — concentrating density just above 40.

Any of these produce exactly the spike you observed: excess mass just above 40.

**Failure mode 2: The spike is non-random even without intentional gaming.**

Even if no one is actively gaming the threshold, a density spike above the cutoff tells you something structurally important: whatever process generates health scores has a discontinuity near 40. Maybe the scoring algorithm has a non-linearity there. Maybe 40 was chosen because it aligned with a natural cluster in underlying user behavior. In either case, users just above 40 differ from users just below 40 in some systematic way that produced the clustering — and if that underlying characteristic is correlated with retention potential, you have confounding at the threshold. The smoothness assumption is violated regardless of intent.

---

## Step 5: What the Density Spike Means for Your Estimates

If manipulation is upward (toward non-treatment), the users bunched just above 40 are a selected group — they were maneuvered across the threshold specifically because the team (or some process) judged them as less needy, easier to move, or lower priority. These are systematically different users from those who naturally land at 41-45.

The consequence: your control group just above 40 is contaminated with users who should have been in the treatment group but were moved out. This makes your control group look artificially like healthier, more-retainable users. The result is a **downward bias on the estimated treatment effect** — you will underestimate the benefit of outreach, because your comparison group (just-above-40 users) is not a valid counterfactual for just-below-40 users.

Alternatively, if the score process naturally clusters users above 40 due to a non-linearity in the scoring model, the threat is that users at 41 are categorically different from users at 39 along the dimension that causes clustering — and retention differences between them may be driven by that dimension rather than by the outreach. Either way, the causal estimate is unreliable.

---

## Step 6: What to Do

**Immediate diagnostics:**

1. **Run the McCrary / Cattaneo-Jansson-Ma density test.** Quantify whether the density discontinuity at 40 is statistically significant. A significant result is strong evidence against the manipulation-free assumption.

2. **Check the timing.** When was the threshold communicated to the support team? If the density spike appears in health scores recorded *after* that communication date but not before, that is near-direct evidence that internal knowledge of the threshold influenced score recording. This is the most powerful falsification test available to you.

3. **Audit the health score calculation.** Determine whether any support team actions — logging a contact attempt, creating a ticket, recording outreach — feed back into the health score. If so, the running variable is contaminated by design.

4. **Check covariate smoothness at the cutoff.** For pre-treatment covariates (account age, plan tier, historical activity), check whether they jump at 40. In a valid RDD, pre-treatment covariates should be continuous at the threshold. Jumps in covariates indicate that the groups on either side are systematically different — this is a direct test of the "as-if random" assumption.

**If manipulation is confirmed:**

- RDD at the 40 threshold is not valid in its current form.
- Consider **donut RDD**: exclude observations very close to the threshold (e.g., scores 38–42) and estimate the effect using units farther from the cutoff. This sacrifices some precision but avoids the contaminated region. The logic is that the manipulation is concentrated near the threshold; units farther away are more likely to be clean.
- Consider whether an alternative identification strategy is available: a randomized experiment (the cleanest fix), a different threshold that was not communicated to the support team, or a difference-in-differences using the pre/post timing of when the outreach policy was introduced.
- If you have a longer time series, look for a pre/post discontinuity in the density itself — if the spike at 40 emerged after the threshold was set, the manipulation story is confirmed.

**If diagnostics are inconclusive:**

Run your RDD but report sensitivity analyses: how large would the manipulation have to be to explain away a significant treatment effect? If the estimated effect is large, a modest amount of manipulation might not overturn the qualitative conclusion. But be explicit about this uncertainty in any reporting of results.

---

## Step 7: The Core Issue with Your Lead's Reasoning

"The threshold was only communicated internally" would be a valid response if the concern were that *users* themselves were gaming their scores. But that is not the primary threat here. The threats are:

1. The support team (or internal processes) influencing scores at the margin, whether intentionally or as a mechanical byproduct of the outreach workflow.
2. The threshold being chosen at a point that coincides with a natural discontinuity in the score distribution, making the sides of the threshold non-comparable on unmeasured dimensions.

Neither of these requires users to know anything. In fact, the internal communication of the threshold is precisely what makes failure mode 1 *more* likely: the people who know about the threshold are the same people who interact with the scoring inputs. The density spike is observable evidence that at least one of these failure modes is occurring. Dismissing it because users weren't told is answering the wrong concern.

---

## Summary

| Question | Answer |
|---|---|
| Does the density spike matter? | Yes. It is the primary diagnostic for running-variable manipulation in RDD. |
| Is "only told to the support team" sufficient to dismiss it? | No. The support team itself is the most likely source of manipulation. |
| What is the direction of bias? | Likely downward — you underestimate the benefit of outreach, because the control group above 40 is selectively composed of users who were moved there. |
| What should you do? | Run formal density tests, audit the score pipeline for feedback loops, check covariate continuity at the cutoff, and use a pre/post timing test as your strongest falsification. Consider donut RDD or a randomized experiment if manipulation is confirmed. |

The spike is not a nuisance artifact. It is the data telling you that the assumptions underlying your causal estimate are violated. Take it seriously before publishing or acting on these results.
