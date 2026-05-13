# Causal Analysis: Onboarding Completion and Long-Term Retention

## The Core Problem: You're on the Wrong Rung

The question being asked is Rung 2 — **intervention**: "If we invest in improving onboarding completion, will we improve 6-month retention?"

The data answers a Rung 1 question — **association**: "Among users still active at 90 days, what correlates with 6-month retention?"

These are not the same question. The correlation (r = 0.42) cannot answer the intervention question directly — and in this case, the gap between the two is especially severe because of a structural problem in how the sample was constructed.

---

## Step 1: Name the Rung

The business question is squarely Rung 2: P(6-month retention | do(improve onboarding completion)). That requires knowing what happens when you intervene on onboarding — not what correlates with retention among the users you happened to keep.

The analysis answers a Rung 1 question: within the cohort still active at 90 days, is onboarding completion associated with 6-month retention? No amount of statistical significance (p < 0.001 included) bridges this gap. A highly significant association in a badly conditioned sample is still a badly conditioned sample.

---

## Step 2: Sketch the DAG

Key variables:

- **O**: Onboarding checklist completion (the proposed lever)
- **A90**: Still active at 90 days (the selection filter applied by the analysis team)
- **R6**: Active at 6 months (the outcome of interest)
- **Q**: User motivation / product-market fit (unmeasured latent trait)

Plausible causal structure:

```
Q → O          (motivated users complete onboarding)
Q → A90        (motivated users survive to day 90)
Q → R6         (motivated users stay long-term)
O → A90        (completing onboarding supports early engagement)
O → R6         (onboarding may support long-term retention — the effect we want to estimate)
```

This gives us the critical structure: **A90 is a collider**. It is caused by both O and Q. The analysis team then conditions on A90 = 1 by filtering to users still active at day 90.

---

## Step 3: Identify the Structure — Collider Conditioning

Conditioning on a collider opens a spurious path. By filtering to A90 = 1, the analysis opens:

```
O → A90 ← Q → R6
```

Within the 90-day-active sample, O and Q are no longer independent — even if they were independent in the full population. Consider the intuition: a user who made it to day 90 *without* completing onboarding got there despite a rough start, which is evidence of very high Q. A user who made it to day 90 *with* onboarding completion needed that onboarding to get there, so Q is less extreme on average. Inside the conditioned sample, onboarding completion and user quality are negatively correlated. When you then predict 6-month retention from onboarding completion in this sample, the signal is inflated by this induced relationship.

This is collider stratification — also called Berkson's bias when the collider is a study-entry condition. The label "highest-quality users" is part of the confusion: these users aren't a neutral random sample of engaged users. They are a sample defined by a collider, which makes relationships within them structurally distorted.

---

## Step 4: Two Additional Problems

Even setting the collider aside, the correlation faces two more problems.

**Confounding by Q (fork structure)**

Q → O and Q → R6. Users who complete onboarding self-select: they are more motivated, have clearer use cases, and fit the product better. This is a standard fork: Q is a common cause of both O and R6, inducing a spurious O–R6 correlation. The analysis does not control for Q (which is largely unobserved).

**The downstream indicator trap**

Onboarding completion may be a symptom of user quality rather than a cause of retention. The mechanism that matters could be:

```
Q → O    and    Q → R6
```

...with O having little or no independent causal effect on R6. If that's the structure, then intervening on O — nudging users to complete onboarding steps they would have skipped — adds completions from users with lower Q, who were going to churn regardless. The metric goes up; retention does not.

The do-operator makes the distinction precise:
- P(R6 | O = 1): retention rate among users who naturally completed onboarding — high, because they are high-Q.
- P(R6 | do(O = 1)): retention rate if you force completion for everyone — potentially much lower, because you're now including low-Q users who were pushed through.

---

## Step 5: What the Correlation Actually Reflects

The r = 0.42 is a mixture of at least three components:

| Component | Structural source | Contribution to observed r |
|---|---|---|
| Genuine causal effect of O on R6 | O → R6 direct path | Some (unknown) fraction |
| Confounding by user quality Q | Q → O and Q → R6 fork | Inflates r |
| Collider conditioning on A90 | O → A90 ← Q → R6, conditioned | Further inflates r |

The observed correlation is consistent with a large genuine effect, a moderate effect buried in confounding, or essentially zero genuine effect. The data cannot separate these.

---

## Step 6: Alternative Structural Roles and What Each Implies

Being explicit about structural alternatives is the most useful thing this analysis can do.

**Alternative A: O is a genuine cause of R6**
- The causal effect is real but smaller than r = 0.42 suggests — confounding and collider bias inflate it
- Investment in onboarding is justified, but the intervention should be sized based on an identified estimate (from an experiment), not the observed correlation
- Estimated true effect is likely r = 0.10–0.20 range, not 0.42

**Alternative B: O is primarily a downstream indicator of Q**
- Intervening on onboarding completion for users who wouldn't naturally complete it produces near-zero retention gain
- The right lever is upstream: better user targeting, acquisition channel mix, clearer value communication before signup
- Onboarding completion remains a valid targeting signal (identify high-Q users to nurture) but is not a valid intervention target

**Alternative C: Partial — some onboarding improvements work, others don't**
- Onboarding improvements that deliver genuine product value (activate the feature that creates the "aha moment," reduce friction for a specific workflow) will improve retention
- Onboarding improvements that inflate the completion metric without changing the experience (shorter checklist, auto-completing steps, reminder emails) will not
- The right investment is in the substance of onboarding, not in the completion rate metric

**Diagnostic to discriminate:** Run an A/B test in which treatment makes onboarding mechanically easier to complete — fewer steps, pre-filled fields, reminder nudges — without changing the substantive product experience. If 6-month retention improves, O has real effect at the mechanical level. If completion rises but retention doesn't, onboarding completion is a downstream indicator and the metric is not a lever.

---

## Step 7: What Would Actually Answer the Question

**Option 1 (cleanest): Experiment on the full user population.**
Randomize at the point of signup to an improved onboarding condition vs. control. Measure 6-month retention. Analyze intention-to-treat on the full randomized sample — do not filter to 90-day survivors. This estimates P(R6 | do(improved onboarding)) as a population-level policy effect (ATE). Include 90-day retention as a secondary metric to understand the mechanism, but do not use it as a sample filter.

**Option 2: Rerun the analysis without the selection filter.**
Compute the O–R6 correlation in the full user base (including those who churned before 90 days). If the correlation drops substantially from 0.42, that is direct evidence the current finding is driven by collider bias. If it remains strong and is robust to controlling for observable proxies of Q (signup channel, device, pre-signup behavior), the case for a genuine causal path strengthens — though unmeasured confounding remains.

**Option 3: Instrument for onboarding completion.**
Find a source of variation in onboarding completion that is plausibly unrelated to user quality — a UX change that made a specific step easier to complete, a technical outage that blocked onboarding for a random subset of users, or a marketing campaign that drove different user types into onboarding at different rates. Use this as an instrument for completion.

**Option 4: Mechanism tracing.**
If onboarding completion causes retention, there should be a traceable downstream mechanism — specific features adopted, specific workflows established in the first session. Check whether completing onboarding predicts the adoption of specific features, and whether those features independently predict retention. If onboarding completion predicts R6 but predicts none of the intermediate product behaviors that ought to mediate it, that is evidence it is a proxy signal rather than a causal lever.

---

## Summary Verdict

**No — you should not invest in improving onboarding completion as a retention lever based on this analysis.**

The r = 0.42 finding is structurally compromised in at least two ways simultaneously:

1. **Collider conditioning**: filtering to 90-day-active users conditions on a common effect of onboarding completion and user quality, inducing spurious correlation between the two within the restricted sample.
2. **Fork confounding**: self-selection into onboarding completion by higher-quality users inflates the association with long-term retention throughout.

These biases stack. The true causal effect of onboarding completion on 6-month retention could be modest, small, or near zero — the observed correlation provides no reliable guidance.

The correlation is not worthless: a signal this strong is a reasonable hypothesis about mechanism, and onboarding completion is a useful targeting signal for identifying already-high-quality users worth nurturing. But it is not investment-grade evidence for onboarding as a causal lever.

The right next step is an A/B test on the full user population — not the 90-day survivors — measuring 6-month retention as the primary endpoint, analyzed as intention-to-treat. If the effect holds up, size the investment to what the experiment shows.
