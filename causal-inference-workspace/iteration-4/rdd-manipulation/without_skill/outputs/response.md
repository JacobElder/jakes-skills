# Does the Density Spike Matter for Your RDD?

**Short answer: Yes, it matters — and your data science lead is likely wrong.**

---

## What the Density Spike Tells You

A spike in density just *above* the threshold (41–45) in a regression discontinuity design is a classic warning sign of **manipulation of the running variable**. The formal test for this is the **McCrary density test** (or the more modern Cattaneo-Jansson-Ma test), which checks whether the density of the running variable (here, health score) is smooth through the cutoff. A statistically significant discontinuity in density is evidence that sorting has occurred.

The key question is: **How did users end up in the 41–45 range at higher rates than expected?**

There are two broad possibilities:

1. **Random statistical noise** — sometimes you get clusters by chance. (Unlikely to be the explanation if the spike is notable enough that you're asking about it.)
2. **Systematic sorting** — something caused users who would have scored below 40 to instead appear above 40 in your data.

---

## Why "Internally Communicated" Doesn't Eliminate the Problem

Your data science lead's argument is: *"The threshold was only told to the support team, so users couldn't have manipulated their health scores."* This sounds reasonable but conflates two very different manipulation mechanisms.

### Type 1: User Self-Sorting (Not the concern here)
This would be users *knowing* the threshold and strategically changing their behavior to avoid or receive treatment. Example: a student who knows the scholarship cutoff is a GPA of 3.0 and studies extra hard to hit 3.1. Your lead is correct that users likely couldn't do this — they probably don't know their health score or the cutoff.

### Type 2: Administrator/System Sorting (The real concern)
This is where the internal communication to the support team becomes *the problem, not the defense*. If support team members knew the cutoff was 40, they may have — consciously or unconsciously — influenced the health scores of borderline users. For example:

- **Score nudging:** A support rep reviews a user at 38 and, knowing outreach is triggered below 40, logs an extra interaction or updates a field that bumps the score to 41.
- **Data entry bias:** Health scores that have any manual input component get rounded up when the scorer knows the stakes.
- **Proactive informal outreach:** Reps already informally reach out to users at 38–39 outside the formal protocol, those users engage more, and their health scores rise above 40 organically — but this means *treated* users are appearing in your *control* group.
- **Model artifacts:** If the health score itself is computed by a system the team has any influence over, knowing the threshold can shift how inputs are weighted or logged.

Any of these mechanisms — all plausible precisely *because* the threshold was communicated internally — would produce exactly the spike you observe: a bunching of users just above 40.

---

## Why This Breaks the RDD

RDD's identifying assumption is that **units just below and just above the threshold are comparable in all ways except treatment assignment**. This is credible when assignment near the cutoff is "as good as random" — users can't precisely control which side of the threshold they land on.

If manipulation has occurred, that assumption fails:

- Users who "should" have been at 38–39 (and received outreach) are instead appearing at 41–43 (appearing untreated).
- Your "just above" control group is contaminated with users who are fundamentally different — they either received informal support, had their scores adjusted by a motivated team member, or are systematically selected in some other way.
- The comparison group is no longer a valid counterfactual.
- Any estimate of the treatment effect is **biased**, and you cannot determine the direction of the bias without understanding the specific mechanism.

---

## What You Should Do

### 1. Run the Formal Density Test
Use the McCrary (2008) test or the Cattaneo-Jansson-Ma (2020) manipulation test. A statistically significant discontinuity in density at the cutoff is grounds to question the design's validity.

```r
# In R, using the rddensity package
library(rddensity)
rdd <- rddensity(X = health_score, c = 40)
summary(rdd)
rdplotdensity(rdd, health_score)
```

```python
# In Python, you can use the rddensity package
# pip install rddensity
from rddensity import rddensity, rdplotdensity
result = rddensity(health_score, c=40)
```

### 2. Investigate the Source of the Spike
Before writing off the design, understand *why* the spike exists:

- Is the health score computed algorithmically with no human input? If so, manipulation by the support team is less plausible, and you should look for other explanations (e.g., a discrete jump in an input variable at that range, rounding in the score calculation).
- Does the health score have any manual components, or can support team actions feed back into the score? If yes, manipulation is very plausible.
- Check timestamps: did the bunching at 41–45 emerge *after* the threshold was communicated to the support team, or was it present beforehand?

### 3. Check Baseline Covariate Balance at the Cutoff
Even if density looks problematic, check whether pre-treatment covariates (tenure, plan type, industry, etc.) are smooth through the cutoff. Sharp discontinuities in covariates at the threshold further confirm sorting.

### 4. Consider Alternative Identification Strategies
If the density test fails or investigation reveals manipulation:

- **Instrumental variables:** Is there something that caused some users to receive outreach that is independent of the health score near the threshold?
- **Difference-in-differences:** If you have pre-outreach retention data and a comparable control group elsewhere, DiD may be feasible.
- **Fuzzy RDD:** If treatment assignment is probabilistic near the threshold (not perfectly determined by the score), fuzzy RDD may still be salvageable — but only if the density issue is mild.
- **Expand the bandwidth and use control variables:** A partial mitigation, but not a solution if selection is occurring.

---

## Summary

| Claim | Assessment |
|---|---|
| "Users couldn't manipulate their own scores" | Likely true, but irrelevant |
| "The threshold was only communicated internally" | This is actually *evidence for* manipulation risk, not against it |
| "The density spike doesn't matter" | Incorrect — it is a direct threat to RDD validity |
| "We can proceed with the RDD as planned" | Not without further investigation and formal testing |

The density spike absolutely matters. The internal communication of the threshold to the support team means you have exactly the *people* who could cause manipulation (support reps) knowing exactly the *number* that triggers different treatment. The pattern you're seeing in the data is consistent with that mechanism. You need to run the density test, investigate the data generating process, and likely reconsider your identification strategy before drawing any causal conclusions.
