# Is an 18% Retention Improvement a Reasonable Rollout Expectation?

**Short answer: No. The 18% is almost certainly an overestimate for a full rollout, and treating it as the expected effect for all users is a classic ATT-vs-ATE error.**

---

## Step 1: Name the Rung

Your team is asking a **Rung 2 (intervention)** question: "What will happen to retention if we *do* the rollout?" The number you have — +18% — comes from an opt-in experiment. That is an observational/self-selected design, not a randomized assignment. The gap between what you measured and what you need to know is structural, not statistical.

---

## Step 2: Sketch the DAG

```
User characteristics (U)
    ↙              ↘
Opt-in (D)  →  Retention (Y)
```

Where U represents things like: motivation to engage, tech-savviness, willingness to try new products, existing frustration with the old dashboard, etc.

- U → D: Users who are most likely to benefit from a redesign are also most likely to opt in. Power users, frustrated users, change-seekers all self-select into the treatment.
- U → Y: Those same characteristics independently predict higher retention.

This is a **fork** (confounder): U opens a back-door path D ← U → Y. Your matched control group partially addresses this, but matching can only close back-door paths through *observed* characteristics. If any component of U is unobserved, the path remains open.

---

## Step 3: Identify the Estimand Problem (ATT vs. ATE)

Your opt-in experiment estimates the **ATT — Average Treatment Effect on the Treated**:

> ATT = E[Y(1) − Y(0) | D = 1]

This is the average effect among the 12% who chose to opt in. It answers: "How much did the redesign help the people who actually tried it?"

The rollout decision requires the **ATE — Average Treatment Effect**:

> ATE = E[Y(1) − Y(0)]

This answers: "How much will the redesign help everyone, including the 88% who didn't opt in?"

These are the same number only if there are no **heterogeneous treatment effects** correlated with selection. In your case, that assumption is almost certainly violated:

- The 12% who opted in are likely the most motivated, most engaged, and most change-receptive users. They may also be the ones who were most frustrated with the old dashboard — and therefore had the most room to improve.
- The 88% who didn't opt in include users who are happy enough with the current dashboard, lower-engagement users who may not notice the change at all, and users who actively resist change.

**The ATT will typically be larger than the ATE when self-selection is driven by expected benefit.** This is textbook: people opt in when they expect to gain, so optees are drawn disproportionately from the high-effect end of the distribution.

---

## Step 4: What to Expect Instead

The realistic scenario for a full rollout is:

| Population | Likely Effect |
|------------|--------------|
| The 12% who opted in | ~+18% (what you measured) |
| The 88% who didn't | Substantially less — possibly near 0% for disengaged/resistant users |
| Full population (ATE) | Somewhere between 0% and 18%, likely much closer to the lower end |

The exact ATE depends on the distribution of effect heterogeneity, which you don't currently know. But it is almost always a mistake to assume ATE ≈ ATT from an opt-in design.

---

## Step 5: The Most Likely Traps Being Triggered

1. **Conflating ATT with ATE.** This is the core error. The 18% is a real effect — for those users. Extrapolating it to everyone assumes no heterogeneity correlated with selection.

2. **Residual selection bias in the matched control.** Matching on observed characteristics doesn't eliminate confounding through unobserved variables (engagement mindset, latent dissatisfaction, etc.). If matching is imperfect, the 18% itself is upwardly biased even as an ATT estimate.

3. **The opt-in itself as a signal.** Users who opted in may have increased retention partly *because they chose to try something new* (a novelty/motivation effect), not solely because the redesign is objectively better. This effect won't replicate when the redesign is the default for all users.

---

## Step 6: What Would Actually Justify an 18% Expectation?

To confidently project 18% onto the full population, you'd need one of:

- **A proper A/B test** with random assignment (not opt-in). Randomly force some users into the new dashboard, force others to stay on the old one. The difference in means is an unbiased ATE.
- **Evidence that the treatment effect is homogeneous** — that engaged power-users and passive low-engagement users respond equally to the redesign. This would need to be measured, not assumed.
- **Heterogeneous treatment effect (CATE) analysis** across user segments — understanding how the effect varies by engagement level, tenure, use-case type — and then weighting those CATEs by the population composition to compute an ATE directly.

---

## Practical Recommendation

**Do not project 18% onto the full rollout.** Here's what to do instead:

1. **Run a proper A/B test before full rollout.** Randomly assign some percentage of users (ideally users who never opted in) to the new dashboard. This measures the ATE directly. Even a small holdout — 5-10% — will give you a much more reliable population-level estimate.

2. **Segment the opt-in data.** Look at how the 18% effect breaks down by engagement tier, tenure, and product-usage patterns. If lower-engagement users (who are more representative of the 88%) show much weaker effects even within the opt-in group, that's direct evidence the ATE will be lower.

3. **Plan for a staged rollout with measurement.** Roll out to 20%, measure retention, compare against a held-out control. The DiD approach (comparing the change in retention in the rollout cohort vs. control, pre and post rollout) will give you a cleaner causal read than the opt-in study ever could.

4. **Set internal expectations honestly.** If you must give a forecast now, a range like "2–10% improvement for the full population, with the true effect likely in the lower half" is more defensible than 18%. The 18% is an upper bound driven by the most favorable users.

---

## Summary

The +18% is a real causal effect — for the 12% who chose to try the new dashboard. It is not a reliable forecast for the full population. The structural reason is that opt-in designs estimate the ATT (effect on triers) not the ATE (effect on everyone), and ATT > ATE whenever high-benefit users disproportionately self-select. The right path forward is a randomized A/B test or a properly measured staged rollout with a control group before committing the 18% as a planning assumption.
