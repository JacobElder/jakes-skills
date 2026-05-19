# RDD and the Density Spike: Does It Matter?

## Short Answer

Yes, the density spike matters — and your data science lead's reasoning is incorrect. The fact that the threshold was only communicated internally to the support team does not protect your regression discontinuity design (RDD) from the threat posed by sorting around the cutoff. This is a serious validity concern that you cannot dismiss.

---

## What the Density Spike Tells You

In RDD, the core identifying assumption is that units (users, in your case) cannot precisely sort themselves to one side of the threshold. If this assumption holds, then users just below 40 and just above 40 are comparable on all other characteristics — they ended up near the threshold essentially by chance — and any discontinuity in the outcome (retention) at the cutoff can be attributed to the treatment (proactive outreach).

A density spike — specifically, an excess mass of observations just above the cutoff — is a signature pattern of **manipulation or sorting**. The standard diagnostic for this is the McCrary (2008) density test, which tests whether the density of the running variable (health score) is smooth through the threshold. A statistically significant discontinuity in density at the cutoff is strong evidence that something is causing observations to cluster on one side.

---

## Why Your Lead's Reasoning Fails

Your data science lead argues: "Users didn't know about the threshold, so they couldn't have sorted around it." This reasoning conflates two very different channels through which manipulation can occur:

### 1. User-Side Sorting
This is what your lead is (correctly) ruling out. If users knew that a score below 40 triggered outreach, some might deliberately let their health score drop to receive support. That seems implausible if the threshold was internal.

### 2. Administrator/Operator-Side Sorting
This is the real threat, and it does not require users to know anything. Consider who *did* know about the threshold: **the support team and whoever manages health scores**.

If health scores are:
- Calculated by a person or process with discretion (e.g., account managers rating customers)
- Subject to rounding, adjustment, or override
- Updated periodically and visible to the support team

...then the support team (or whoever calculates/approves scores) may have — consciously or unconsciously — bumped users with scores of 37, 38, or 39 up to 41 or 42 to avoid triggering the outreach protocol. This could happen for many reasons:
- A belief that the customer doesn't really need outreach
- Desire to avoid the workload of proactive calls
- Optimism bias in scoring customers they like
- Systematic rounding conventions

The result would be exactly what you observe: a density spike just above 40, because users who "should" have scored in the 37–39 range were nudged above the threshold.

### 3. Feedback Loops in Score Calculation
If health scores incorporate engagement data that is itself influenced by support activity, and if the support team was already informally triaging before the formal threshold, the scores themselves could be endogenous in complex ways.

---

## Why This Invalidates the RDD

If sorting occurred — regardless of who caused it — users just above 40 are **not a valid counterfactual** for users just below 40. The two groups differ not just in whether they received outreach, but also in whatever factor caused some users to end up above rather than below the threshold. That hidden factor (e.g., support team favoritism, scoring discretion for "promising" accounts) may itself predict retention, creating confounding bias.

Formally: RDD requires that the conditional expectation of potential outcomes is continuous through the cutoff. Sorting violates this. Users just above 40 may have systematically better prognosis (which is why their scores were nudged up), making the treatment group (below 40) look worse off not because outreach failed, but because the control group was selected to look good.

---

## What To Do

### Immediate Diagnostics
1. **Run the McCrary density test** (or the Cattaneo-Jansson-Ma 2018 local polynomial density test, which is more robust). If the discontinuity in density at 40 is statistically significant, you have formal evidence of a problem.
2. **Plot the density histogram** with narrow bins (e.g., width = 1) around the cutoff and look visually at whether the spike is at exactly 41–45 or spread more broadly.
3. **Test for covariate balance at the cutoff.** Run RDD-style local linear regressions for pre-treatment covariates (e.g., account age, plan tier, historical usage) as the outcome. If covariates jump discontinuously at 40, that confirms the treated and control groups are not comparable.
4. **Audit the score calculation process.** Who inputs or approves scores? Is there any manual override or adjustment step? When were scores calculated relative to the outreach intervention?

### If Sorting Is Confirmed
- **The RDD estimate is not credibly causal.** You should not report it as causal evidence.
- Consider **instrumental variables**, **difference-in-differences**, or **matching** designs if alternative identification strategies are feasible.
- If the score calculation process can be made algorithmic and automatic (no human discretion), a prospective RDD with that process could be valid going forward.
- Consider running a **randomized controlled trial** in the near-threshold region (e.g., randomly assign outreach to users scoring 35–44) to generate clean causal evidence.

### If Sorting Cannot Be Ruled Out But Seems Minor
- Be transparent about the threat in any write-up.
- Report sensitivity analyses using narrower bandwidths and donut-hole RDD (excluding users very close to the cutoff, where manipulation would be most concentrated).
- Treat the estimate as descriptive/associational rather than causal.

---

## Summary

| Claim | Assessment |
|---|---|
| "Users didn't know the threshold, so sorting couldn't happen" | Incorrect — users are not the only potential manipulators |
| "The density spike doesn't matter" | Incorrect — density spikes at the cutoff are the primary diagnostic of RDD violation |
| "We can use RDD as planned" | Not without further investigation; the spike is a red flag that must be addressed |
| "The estimate might still be valid" | Possibly, but requires ruling out operator-side sorting through audits and covariate balance tests |

The density spike is exactly the evidence that the RDD's core assumption may be violated. Dismissing it based on user-side reasoning alone misunderstands where the threat comes from. Before drawing any causal conclusions, you need to investigate the score generation process and run the standard diagnostic tests.
