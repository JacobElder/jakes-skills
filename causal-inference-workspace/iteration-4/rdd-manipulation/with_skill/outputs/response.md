# Causal Inference Response: RDD Density Spike at the Health Score Threshold

## The short answer

Yes, the density spike matters a great deal — and your data science lead's reasoning, while intuitive, does not actually protect you. The spike is the canonical signal that the RDD identifying assumption has been violated, regardless of who knew the threshold.

---

## Step 1: Name the rung

Your question is **Rung 2 (Intervention)**. You want to know: *does proactive outreach cause better retention?* That is a do-operator question — P(retention | do(outreach = 1)) — not a prediction question. RDD is a design-based strategy for climbing from observational data to rung 2, but it only works when its key assumption holds.

---

## Step 2: Sketch the DAG and name the RDD assumption

In a clean RDD, the DAG looks like this:

```
Health Score → Treatment (outreach) → Retention
Health Score → Retention  (direct path — confounding)
```

The running variable (health score) is a confounder: it affects both who gets treated and retention outcomes. The threshold creates quasi-random variation *only if* units cannot sort themselves to one side or the other. The identifying assumption is called **no manipulation**: the health score just below vs. just above the cutoff is effectively as-if-random, because nobody can finely control their score to land on a preferred side.

When that assumption holds, the DAG near the threshold becomes:

```
[Threshold position ≈ random] → Treatment → Retention
```

The confounder (health score level) is balanced across the threshold by continuity, so you can attribute the discontinuous jump in outcomes to treatment.

---

## Step 3: What the density spike tells you structurally

A spike in the density of units **just above** the treatment cutoff — specifically on the *untreated* side — is the direct empirical signature of **sorting or manipulation**. The McCrary density test (or the more recent Cattaneo-Jansson-Ma test) formalizes this: it tests whether the density of the running variable is continuous at the cutoff. A statistically significant density discontinuity is strong evidence that the no-manipulation assumption is violated.

The structural story here: some entity — users, the support team, or some other actor — caused units to end up with scores of 41–45 rather than 36–40. There are several mechanisms, and the mechanism matters for how seriously your estimate is compromised:

### Mechanism A: Users gamed the threshold (self-selection)

If users somehow learned that a score below 40 triggered outreach (which they may have inferred from being contacted, from product interfaces, from word of mouth, etc.), users who valued not being contacted may have taken actions to push their score above 40. These are systematically *different users* — more engaged, more privacy-conscious, or otherwise distinct. The comparison just below vs. just above 40 is now comparing a selected group of engaged users (who chose to stay above 40) to unselected users (who could not or did not manage their score). Any measured difference in retention is confounded by this selection.

### Mechanism B: The support team manipulated scores

Your data science lead says the threshold was only communicated internally. That is exactly the scenario in which **the support team** is the most plausible manipulator. If support agents knew that a score of 40+ meant no outreach was required, they had implicit or explicit incentives to record or adjust scores just above the threshold for some users — perhaps to reduce their own workload. This is a particularly dangerous form of manipulation because the agents likely had *non-random* reasons for doing it: they may have cherry-picked users they already knew were healthier, or users they wanted to deprioritize. The units that got pushed above 40 are now systematically different from those who stayed below, even among users who were originally near the boundary.

Both mechanisms produce the same observable signature (a density spike just above the cutoff) and both destroy the no-manipulation assumption. The lead's reasoning — "users didn't know, so they couldn't have gamed it" — eliminates Mechanism A but leaves Mechanism B entirely open, and in fact makes Mechanism B the *more likely* explanation. Internal knowledge of the threshold is a prerequisite for internal manipulation.

---

## Step 4: Why this is not a minor correction

When RDD identification fails, you are not left with a slightly biased estimate — you are left with a comparison between two self-selected groups. The units just above 40 are no longer a valid counterfactual for the units just below 40. Any effect you estimate is a mix of the treatment effect and the selection effect, and there is no way to separate them from the data alone without additional assumptions.

To be concrete: suppose users (or agents) pushed scores from 38 to 42 specifically for users who were already on a positive trajectory. The "untreated" group just above 40 would have better retention than the "treated" group just below 40 *even if outreach had zero effect* — or even if outreach hurt retention. The sign and magnitude of your estimate are not trustworthy.

---

## Step 5: Diagnostics and what to do next

**Run the formal density test first.** Compute the McCrary or Cattaneo-Jansson-Ma test statistic. If the density discontinuity is statistically significant, you have formal evidence of manipulation. If it is not, the visual spike may be noise — though you should still characterize its magnitude and consider whether the power of the test is adequate for your sample size.

**Look for covariate discontinuities at the threshold.** If manipulation occurred, pre-treatment covariates (tenure, plan type, historical usage) should also be discontinuous at the cutoff. Plot these. A clean RDD produces smooth covariate distributions through the cutoff; manipulation almost always leaves fingerprints in covariates.

**Investigate whether support agents recorded scores.** If the health score is computed automatically from product usage data, agents likely could not have manipulated it directly. But if agents had any ability to flag, adjust, or override scores, that is the first place to look.

**Check whether users received feedback on their scores.** Product UI showing a user their health score, or any in-app notification linking low scores to outreach, would support Mechanism A.

---

## Step 6: Alternative identification strategies if RDD is compromised

If manipulation is confirmed, RDD at this threshold cannot be salvaged without additional design work. Consider:

1. **Donut RDD**: Exclude observations very close to the cutoff (e.g., scores 38–42) and estimate the effect using users further away. This removes the potentially manipulated mass. The cost is reduced precision and the implicit assumption that the effect is homogeneous enough to extrapolate from the tails — usually fragile.

2. **Instrumental variables**: Find a variable that predicts whether a user received outreach but has no direct effect on retention and is unrelated to the score-manipulation process. This is hard but worth asking whether any natural variation in support team capacity or assignment created variation in outreach independent of the score.

3. **Differences-in-differences**: If you have pre-treatment retention data and a period when outreach did not exist (or used a different threshold), DiD with parallel-trends testing is an alternative. The manipulation concern does not apply to DiD in the same way, though parallel trends is its own assumption.

4. **Randomized experiment**: If the business can tolerate a trial, randomizing outreach among users in a band around the threshold (e.g., 30–50) would cleanly identify the effect. The RDD exercise has already given you a hypothesis and a target population; that makes the experiment design straightforward.

---

## Summary verdict

The density spike is a serious problem, not a cosmetic one. The internal-communication argument rules out one manipulation mechanism but is itself evidence for another. Before relying on any estimate from this RDD:

- Run formal density and covariate continuity tests.
- Determine whether support agents had any ability to influence the score or the assignment process.
- If manipulation is confirmed, treat all current RDD estimates as unreliable and move to one of the alternative identification strategies above.

The right question to take back to your data science lead is not "could users have gamed the threshold?" but rather "could *anyone* — user or internal actor — have caused systematic sorting at the cutoff, and do we have evidence that they did not?" The density spike is that evidence, and the burden of proof has shifted.
