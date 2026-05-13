# Causal Analysis: Opt-In Experiment and the ATT vs. ATE Problem

## Short answer

No. An 18% retention improvement across all users is not a reasonable expectation from this experiment. The estimate your team has is the effect of the redesign on users who actively chose to try it — a fundamentally different population from users who were never offered a choice. Making the redesign the default for everyone is a different intervention measured on a different group, and the two estimates can diverge substantially. The gap is not a statistical artifact; it is a structural feature of how opt-in studies work.

---

## Step 1: Name the rung

Your team is asking a **Rung 2 (intervention) question**: "What will happen to retention if we do X (make the redesign the default for all users)?"

The data you have answers a different question. Even calling this an "experiment" overstates the comparison. The 18% figure comes from users who opted in versus users who were invited but declined. That comparison is already contaminated by self-selection: the opt-in and opt-out groups differ on dimensions related to how they respond to new UI. The 18% is not a cleanly identified average treatment effect — it is closer to a **Rung 1 (associational)** estimate dressed in experimental language.

---

## Step 2: Sketch the DAG

Let U = unobserved user traits (tech curiosity, engagement level, openness to change, prior satisfaction with the product).

```
U ──────────────────────────────────► Retention (Y)
│
└──► Opt-In Decision (D) ──► Redesign Exposure (X) ──► Retention (Y)
```

Key features:
- U is a common cause of both D (who opts in) and Y (retention outcomes). This is a **fork** — a classic confounder on the D → Y path.
- The matched control group (invited but declined) does not remove U's influence. Users who decline are systematically different from users who accept — they are less exploratory, less engaged, or less tolerant of interface change. These same traits predict retention independently of which dashboard they use.
- Even with matching, if U is not directly measured, the match only balances on observed proxies of U, not U itself.

---

## Step 3: Identify the key structural distinction — ATT vs. ATE

The skill's framework names this precisely in potential-outcomes terms.

**ATT (Average Treatment Effect on the Treated):**
The effect of the redesign among users who chose to opt in.

> ATT = E[Y(1) − Y(0) | D = 1]

This is approximately what your 18% estimates — the retention gain *for the people who wanted the redesign.*

**ATE (Average Treatment Effect):**
The effect of the redesign if applied to the full user population.

> ATE = E[Y(1) − Y(0)]

This is what you need to forecast if you make the redesign the default for everyone.

**Why ATT ≠ ATE here:**

Only 12% of invited users opted in. That 12% is not a random sample of all users. They are disproportionately:
- Engaged and curious (more likely to explore new features)
- Satisfied enough with the product to invest time in a redesign
- Flexible in their UI preferences

These same traits make them more likely to benefit from a new interface. Users who declined may find the redesign disorienting, prefer the familiar layout, or be less engaged to begin with — making a retention benefit less likely or even negative for them.

Formally: if Cov(Y(1) − Y(0), D) > 0 — i.e., users who benefit more from the redesign are more likely to opt in — then ATT > ATE. Given the mechanism described, this covariance is almost certainly positive and potentially large.

---

## Step 4: Quantify the gap (conceptually)

The relationship between ATT, ATE, and the ATU (Average Treatment Effect on the Untreated) is:

> ATE = p · ATT + (1 − p) · ATU

where p = 0.12 (opt-in rate).

Your 18% estimates ATT. You do not have ATU — the effect on the 88% who declined. If ATU is near zero or even negative (the redesign disrupts workflows for less engaged users), then:

| Assumption about ATU | Implied ATE |
|---|---|
| ATU = 0% | ATE ≈ 2.2% |
| ATU = −2% | ATE ≈ −1.4% (rollout slightly harmful on average) |
| ATU = 5% | ATE ≈ 6.6% |
| ATU = 18% | ATE ≈ 18% (requires opt-in to carry zero information about benefit) |

The only scenario where ATE ≈ 18% is if ATU ≈ 18% as well — i.e., users who actively chose not to try the redesign would benefit just as much as those who chose to try it. That would mean opt-in behavior carries zero information about likely benefit, which directly contradicts the plausible mechanisms above.

---

## Step 5: Additional structural problems in this study

**Selection into comparison group.** The "matched control" (invited but declined) creates its own selection issue. Conditioning on "was invited and responded in some way" restricts the sample to users who engaged with the invitation at all. Users who ignored the invitation entirely are excluded. If engagement with the invitation itself predicts retention, the comparison group is already selected upward on unobservable engagement traits, making even the ATT estimate optimistic.

**Novelty and Hawthorne effects.** Users who opt into an experiment may behave differently simply because they know they are trying something new. For the opted-in group, some portion of the +18% may reflect novelty rather than the sustained causal effect of the redesign. When the redesign becomes the default, there is no novelty for existing users who are switched, and the novelty effect for new users will differ in magnitude and direction.

**Duration of measurement.** 30-day retention for a group that actively chose a new interface is a favorable measurement window. Users who did not choose the change and are forced into it may take longer to adapt, meaning short-run retention could look worse under a forced rollout even if long-run retention eventually recovers or improves.

---

## Step 6: What would credibly estimate the ATE?

**Option A: True randomized rollout (RCT)**
Randomly assign a subset of users — with no opt-in step — to the new dashboard vs. the old one. This estimates ATE directly. The opt-in mechanism is bypassed entirely, so selection bias is eliminated. This is the gold standard and the most important next step before full rollout.

**Option B: Intent-to-treat analysis with an IV**
If a forced RCT is not feasible, randomize *invitation to opt in* vs. *no invitation*, then compare outcomes between these two groups regardless of who actually opted in. This estimates the intent-to-treat effect (ITT). Using invitation assignment as an instrument for actual exposure recovers a local average treatment effect (LATE) — the effect for users who would switch if invited. This is still not the full ATE, but it avoids selection-into-treatment bias and is much more honest than the current estimate.

**Option C: Staged randomized rollout with holdback**
Roll the redesign out to 20–30% of users selected at random with no opt-in step. Compare retention against a randomly selected holdback group. This is effectively Option A at smaller scale and is the most practical path given you are already moving toward rollout.

**What not to do:** use the 18% estimate directly as the planning number for a forced full rollout. It will almost certainly overstate the benefit and potentially by a large margin.

---

## Step 7: Recommended framing for your team

| Scenario | What the number measures | Valid for rollout planning? |
|---|---|---|
| +18% from opt-in study | ATT: effect on self-selected enthusiasts | No |
| +X% from randomized holdback | ATE: effect on representative users | Yes |
| +Y% from ITT / IV analysis | LATE: effect on users who respond to nudges | Partially — depends on nudge mechanism |

The team's excitement about +18% is understandable — this is a real signal that the redesign has value for at least some users. The problem is the leap from "enthusiasts love it" to "everyone will respond at the same rate." That leap requires assuming opt-in behavior is uninformative about benefit, which is almost certainly false.

---

## Bottom line

The 18% figure is an estimate of the ATT, not the ATE. Because only 12% of users opted in, and opt-in behavior is almost certainly correlated with who benefits from a redesign, the ATT substantially overstates the expected effect of a forced full rollout. A reasonable planning range for ATE — without further data — is probably somewhere between 2% and 8%, with large uncertainty in both directions.

The most important next step is to run a small randomized holdback alongside the rollout to get an unbiased ATE estimate before committing to the full deployment and anchoring stakeholder expectations on 18%.
