# Does the Density Spike Matter? Yes — It Invalidates the RDD

## Rung and estimand

The question is **rung 2 (intervention)**: does proactive support outreach *cause* better retention? You planned to use RDD at health score = 40 to estimate the local average treatment effect (LATE) at the threshold — the effect of outreach for users at the margin.

---

## The core RDD assumption your data is violating

RDD produces a valid causal estimate under one non-negotiable condition: **units cannot precisely manipulate which side of the cutoff they fall on.** The technical term is *no manipulation of the running variable at the threshold.*

Why does this matter? The entire logic of RDD rests on the idea that users just below 40 and just above 40 are effectively identical on all characteristics — observed and unobserved — except for treatment assignment. This near-randomness is what makes the comparison causal rather than merely associational. If units can sort themselves to one side of the threshold, that near-randomness is gone. The two groups are no longer exchangeable, and the jump in outcomes at the cutoff may reflect the selection rather than the treatment.

---

## What the density spike tells you

The spike in scores at 41–45 — more users clustering just above the threshold than a smooth distribution would predict — is the canonical signature of manipulation. This is precisely what the **McCrary density test** (and its variants) is designed to detect: a discontinuous jump in the density of the running variable at the threshold. A smooth underlying process produces a smooth density; a discontinuous pile-up at one side signals that someone or something is sorting units there.

The question is *who* is doing the sorting and *how*. The relevant possibilities:

1. **Users are gaming the health score.** If users have any visibility into their score and understand the 40 threshold (or can infer it from experiencing outreach), they may take small actions — logging in, completing a profile step, opening an email — that push their score from 38 to 41. This is self-selection into the control group.

2. **Support staff are gaming the assignment.** Even if users don't know the rule, the support team does. Customer-facing teams with discretion over inputs to the health score (e.g., manually marking a contact attempt as completed, logging a note that bumps an activity metric) can inadvertently or deliberately move borderline users just above 40 to reduce their own workload or to "help" users they expect to churn. This is staff selection into a favorable assignment.

3. **The health score calculation itself is threshold-aware.** Some scoring systems floor or cap values at round numbers, or aggregate components in ways that mechanically produce spikes at thresholds. If the score formula has a component that discretizes at 40, the spike could be a data artifact — but it still breaks the continuity assumption because the underlying latent score (the thing that matters causally) no longer maps smoothly to the observed score.

---

## Why your data science lead is wrong

The claim is: "the threshold was only communicated internally to the support team, so users couldn't game it." This argument rules out possibility (1) above — user manipulation — but it does not rule out possibilities (2) or (3), and it misidentifies what manipulation means in the RDD context.

**Manipulation does not require user awareness.** If the support team has any influence over health score inputs and knows the rule, they can sort users across the threshold. This is staff manipulation, and it is observationally indistinguishable from user manipulation in the density test. The spike you're seeing is equally consistent with a support rep deciding to log an extra interaction for a user at 39 — bumping them to 41 and clearing them from the outreach queue.

Moreover, even if human sorting is completely ruled out, the density spike still breaks the RDD's core claim. The comparison group (just above 40) is now systematically different from the treated group (just below 40). The users who ended up at 41–45 may be those who are marginally more engaged, more responsive to small nudges, more supervised by attentive reps, or simply those for whom the score algorithm happened to round favorably. Any of these differences could independently predict retention. The density spike is evidence that the threshold-adjacent groups are not exchangeable, regardless of the mechanism.

---

## The DAG, made explicit

```
U (engagement level, unobserved)
     ↙             ↘
Health score    Retention
     ↓
Treatment (outreach)
     ↓
Retention
```

RDD's validity requires that, conditional on being near the threshold, assignment to treatment is as-if-random — the only systematic difference between the two groups is whether their score fell just below or just above 40. The density spike breaks this. It is evidence that a confounder (something that moves the score and also predicts retention) is sorting users to the control side of the threshold. The fork U → Health score and U → Retention is now open in a way that is not blocked by the design.

---

## Concrete consequences for your estimate

If users (or staff, or the algorithm) with higher latent engagement are disproportionately ending up just above 40:

- The control group (just above 40) will have better retention than they would if assignment were clean.
- The treatment group (just below 40) will have worse retention than a clean control group.
- The estimated effect of outreach will be **biased downward** — you will underestimate how much outreach helps, or you may spuriously find no effect at all.

Note that if the direction of sorting is the opposite (systematically higher-risk users sorted above 40), the bias could go the other way. The density spike tells you there is a problem; it doesn't automatically fix the sign of the bias.

---

## What to do

**First, confirm the severity.** Run the McCrary (2008) density test or Cattaneo-Jansson-Ma (2018) local polynomial density test. If the p-value for the discontinuity in density at 40 is small, you have formal evidence of sorting. Also plot the density — the shape of the spike (sharp cliff vs. gradual accumulation) can suggest the mechanism.

**Second, investigate the mechanism.**
- Audit whether support reps have write access to any health score inputs and whether there is a pattern of users being scored up from sub-40 to above-40 shortly before or after the cutoff policy was implemented.
- Check whether the score formula has any component that discretizes or thresholds at 40.
- Look at covariate balance across the threshold for pre-treatment variables that should be smooth (account age, industry, plan tier, prior support contacts). If these are also discontinuous at 40, the sorting is into a biased comparison.

**Third, consider remedies or alternatives.**

- *If the spike is small and balance holds on pre-treatment covariates*: some researchers proceed with a bandwidth-narrowed RDD and argue the manipulation is minor. This is a judgment call and should be disclosed explicitly.
- *Exclude the manipulated region*: remove users in the 40–45 band from the analysis and use a donut RDD comparing users clearly below the threshold (e.g., 30–39) to users clearly above the manipulated region (e.g., 46–55). This gives a less precise but less contaminated estimate. The tradeoff: the LATE is now further from the threshold and less interpretable as "the effect at the margin."
- *Instrument the actual score with a version cleaned of rep influence*: if you can reconstruct what the score would have been absent rep intervention (e.g., from automated system logs), use the "pure" score as the running variable. Rare in practice.
- *Switch identification strategy*: if clean RDD is infeasible, consider DiD (comparing health-score-near-40 users over time, before and after the outreach policy launched), or a propensity score approach with rich covariate adjustment — accepting that this relies on the no-unmeasured-confounders assumption rather than the design-based clean variation.

---

## Summary verdict

Yes, the density spike matters, and it matters fundamentally. A spike in the density of the running variable just above the threshold is the primary diagnostic for manipulation in RDD, and manipulation directly violates the identifying assumption that makes RDD causal. Your data science lead's argument — that internal communication rules out user gaming — addresses only one mechanism and leaves staff manipulation and algorithmic artifacts unaddressed. The comparison you planned will not recover the causal effect of outreach. You need to diagnose the source of the spike, then either fix the running variable or switch to a design whose identifying assumption is not violated by the sorting you're observing.
