# Does the Density Spike Near the RDD Threshold Matter?

**Short answer: Yes, it matters a great deal — and your data science lead is wrong to dismiss it.**

The density spike you've observed is called "sorting" or "manipulation" of the running variable, and it is one of the most serious threats to the validity of a regression discontinuity design. Here is a thorough explanation of why it matters, why your lead's reasoning is flawed, and what you should do next.

---

## What Regression Discontinuity Requires

The entire logic of RDD rests on a single identifying assumption: **units cannot precisely sort themselves to one side of the threshold**. More formally, the density of the running variable (the health score) must be smooth and continuous at the cutoff. When this holds, units just below and just above the threshold are comparable in expectation — they are as-good-as-randomly assigned to treatment status, even though assignment is technically deterministic. The only reason a unit ended up at 39 rather than 41 is effectively random noise, so the two groups serve as valid counterfactuals for each other.

The moment there is a meaningful discontinuity in the *density* of the running variable at the threshold — more units than expected piling up on one side — that assumption is violated.

---

## Why the Spike Is a Red Flag

A density spike just above 40 means that more users have health scores of 41–45 than a smooth distribution would predict. The question is: how did they get there?

There are two broad classes of explanation:

### 1. Legitimate statistical noise
Random variation can produce local clustering. But you describe this as a notable spike — enough that you and presumably others have flagged it as unusual. True random noise should not produce a systematic excess on one specific side of a policy-relevant cutoff. The fact that the excess is just *above* 40 (i.e., the untreated side) rather than randomly distributed is itself suspicious.

### 2. Manipulation
Someone or something moved users across the threshold — either:
- **Support agents proactively inflated health scores** for users near the boundary, pushing them above 40 to avoid triggering outreach (e.g., logging spurious positive interactions, rounding scores up).
- **Users themselves gamed the system**, perhaps learning about the threshold despite it being "internal," and taking actions to push their score above 40 to avoid being flagged.
- **The health score algorithm** may have a discontinuity baked in — for example, a floor or rounding rule that makes 40 function differently than adjacent values.
- **Support agents preferentially reached out to some users near 41–45** even though the rule said not to, blurring the treatment boundary.

Any of these mechanisms invalidates RDD.

---

## Why Your Data Science Lead's Argument Is Wrong

The lead's reasoning is: *"The threshold was only communicated internally to the support team, so users couldn't have manipulated their scores."*

This argument is too narrow. Manipulation in RDD does not require users to be aware of and game the threshold. There are multiple ways manipulation can occur without user knowledge:

**1. Agent-side manipulation is still manipulation.**
If support agents knew the threshold and — even with good intentions — subtly adjusted health scores for near-threshold users, the RDD is broken. For example:
- An agent might log an extra positive touchpoint for a user at 38 to "help" them avoid being flagged.
- A team lead might adjust score weights for borderline cases.
- A data pipeline could have a bug that produces score values biased away from exactly 40.

The key point: **manipulation does not have to come from the units being assigned**. It just has to cause non-random selection around the threshold.

**2. The threshold may have been revealed indirectly.**
Users don't need to know the explicit rule. If users with scores below 40 received outreach and users above 40 didn't, users could have *inferred* the threshold from the pattern of who got contacted. Over time, even a soft signal could produce sorting behavior — users engaging slightly more with the product after receiving outreach, which moves their score above 40, while others who narrowly avoided outreach cluster just above.

**3. The health score itself may have a discontinuity unrelated to manipulation.**
If the scoring algorithm behaves differently near 40 — due to rounding, a composite score with a hard rule, or any non-linearity — that alone can cause density clustering that is not about outreach but still corrupts the RDD.

**The bottom line:** The lead's argument only rules out *one specific mechanism* of manipulation. There are many others. The density test does not care why clustering occurs — it only cares whether the density is smooth at the threshold.

---

## The McCrary Density Test

The standard formal test for this is the **McCrary (2008) density test** (or its updated version by Cattaneo, Jansson, and Ma, 2020). The test:

1. Estimates the density of the running variable just below and just above the cutoff using local polynomial methods.
2. Tests whether there is a statistically significant discontinuity in the density at the threshold.
3. A significant discontinuity is evidence of manipulation.

Given that you're already observing a visual spike, it would be worth running this test formally. But even a visual spike that passes a formal test at p=0.06 should make you cautious — the formal test has limited power in small samples, and economic reasoning matters too.

In R:
```r
library(rdd)
DCdensity(health_scores, cutpoint = 40, plot = TRUE)
```

In Python (using `rddensity`):
```python
from rddensity import rddensity, rdplotdensity
result = rddensity(health_scores, c=40)
print(result.summary())
```

---

## What the Spike Does to Your Estimates

If manipulation is occurring, here is what goes wrong with your RDD estimates:

**Selection bias re-enters.** The whole point of RDD is to create local random assignment. If users near 41–45 are systematically different from users near 35–39 — not just because of the outreach, but because *who ends up on each side* is non-random — then your estimated treatment effect is confounded. Users who "made it" above 40 may be more engaged, more responsive to any intervention, or just fundamentally different in their retention trajectory. You would be comparing the wrong groups.

**The estimate is no longer interpretable as a causal effect.** At best, you'd be estimating some mix of the true outreach effect and the selection effect of who ended up above vs. below the threshold. The control group (41–45) is contaminated — it likely includes users who received some form of intervention (the very action that moved their score above 40), even though they are nominally "untreated."

---

## What You Should Do

**Step 1: Run the formal density test.**
Use the McCrary test or the `rddensity` package (Cattaneo et al.). Report the test statistic and p-value. If it is significant — or borderline significant — take it seriously.

**Step 2: Investigate the mechanism.**
This is critical. Try to understand *how* the spike got there:
- Pull the raw health score audit log. Do you see unusual score updates near the threshold?
- Check whether scores were edited or rounded near 40.
- Ask the support team whether they were aware of users near the boundary and whether they ever "helped" users over the threshold.
- Check whether there is a rounding rule or a scoring formula discontinuity at exactly 40.

**Step 3: Consider the direction and magnitude.**
The spike is above 40 (the untreated side). This means there are *more untreated units* than expected near the threshold. If those users were pushed above 40 because they were higher-engagement users who "naturally" recovered, you would be comparing truly sick users (just below 40) to recovering users (just above 40), which would *inflate* the apparent treatment effect. If agents pushed borderline users above 40 to avoid outreach, you might be *understating* how many users needed support.

**Step 4: Explore robustness checks.**
- **Bandwidth sensitivity:** Does your RDD estimate change substantially as you vary the bandwidth? Instability is a warning sign.
- **Covariate balance test:** Check whether observable pre-treatment covariates (e.g., account age, product tier, historical engagement) are smooth at the threshold. If you see jumps in covariates at the cutoff, that's further evidence of sorting.
- **Donut RDD:** Estimate the RDD excluding observations very close to the threshold (e.g., 38–42). If the estimate changes dramatically, the near-threshold observations are driving results and the spike matters.

**Step 5: Consider alternative identification strategies.**
If manipulation is confirmed, RDD is not valid for this data. Options include:
- **Donut RDD**: Exclude the potentially contaminated band and estimate using users slightly further from the cutoff (e.g., 30–37 vs. 43–50). Introduces more uncertainty but removes the most compromised data.
- **Reconstruct the pre-manipulation running variable**: If you have a score history, use the health score from before the outreach program launched as your running variable instead of the post-launch score. This is the cleanest solution if the data exists.
- **Difference-in-differences**: If you have pre/post data and a clean control group assumption.
- **Matching or propensity score methods**: Lower identification power, but may be more defensible if selection on observables is credible.
- **Bound the estimates**: Use partial identification methods (Manski bounds, Lee bounds) to establish a range of plausible treatment effects even under manipulation.

---

## Summary

| Claim | Assessment |
|---|---|
| "The threshold was only internal, so users couldn't game it" | Partially true, but irrelevant — agent-side and algorithmic manipulation are still possible |
| "The density spike doesn't matter" | Incorrect — density continuity is a core RDD assumption |
| "We can still use RDD" | Only if you can explain and rule out manipulation; otherwise estimates are biased |
| "The spike should be investigated" | Yes — identify the mechanism before proceeding |

The density spike is telling you that something non-random is happening near your threshold. That is precisely the thing RDD cannot tolerate. Your data science lead is conflating "users didn't game the score" with "the running variable is clean," and those are not the same thing. Until you can explain the spike and rule out selection, your RDD estimates cannot be trusted as causal.
