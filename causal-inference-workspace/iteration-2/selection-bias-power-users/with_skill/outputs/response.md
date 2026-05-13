# Causal Analysis: Does Onboarding Completion Drive Long-Term Retention?

## Short answer

No — not on the basis of this analysis. The correlation you found (r = 0.42, p < 0.001) is almost certainly an artifact of collider bias introduced by the sample restriction. The dataset was filtered to users still active at day 90, which conditions on a downstream outcome. That act of filtering creates spurious correlations between anything that predicts 90-day survival and any later outcome. The real causal question — does improving onboarding completion cause higher 6-month retention across all users? — is unanswerable from this sample.

---

## Step 1: Name the rung

The question being asked is rung 2 (intervention): "If we invest in improving onboarding completion, will 6-month retention go up?" That is a do-operator question: what is P(6-month retention | do(onboarding completed))?

The data answers a rung-1 question: within users still active at day 90, what is the correlation between onboarding completion and 6-month retention?

That is a very different question. No amount of within-sample association answers the intervention question without additional causal assumptions — and the sampling restriction has already poisoned those assumptions.

---

## Step 2: Sketch the DAG

Let the key variables be:

- **O** — onboarding checklist completed (the treatment of interest)
- **R6** — 6-month retention (the outcome of interest)
- **S** — surviving/active at day 90 (the selection filter)
- **U** — user quality / engagement propensity (an unmeasured common cause)

A plausible DAG:

```
U (user engagement / motivation / product fit)
├──→ O (onboarding completion)
├──→ S (active at day 90)
└──→ R6 (6-month retention)

O ──→ S (completing onboarding increases early retention)
O ──→ R6 (onboarding may also affect long-term retention directly — this is the effect we want)
S ──→ (not a cause of R6, but the analysis conditions on S = 1)
```

The critical structural fact: **S is a common effect of O and U**. Both completing onboarding and being an engaged user independently increase the probability of surviving to day 90.

This makes S a **collider** on the path O → S ← U.

---

## Step 3: Identify the structure — collider conditioning / selection bias

A collider is closed by default. Conditioning on it opens a spurious path.

The analysis team filtered to S = 1 — users active at day 90. This is precisely conditioning on the collider. As a result:

- Within the filtered sample, O and U become **negatively correlated** (or at least informationally dependent) because they are now competing explanations for why someone reached day 90.
- Users who completed onboarding but are otherwise low-engagement (low U) survived because of O. Users who are high-engagement but skipped onboarding (high U, low O) survived because of U.
- Since U also causes R6, this induced dependency between O and U inside the filtered sample **inflates the apparent association between O and R6**.

In plain terms: within the day-90 survivors, users who completed onboarding may look more retained at 6 months — not because onboarding caused that retention, but because both onboarding completion and later retention are proxies for the same underlying trait (U: genuine product-market fit, motivation, etc.) that was already present before the analysis began.

The structural diagram of the bias:

```
O → S ← U → R6
        ↑
        conditioning here (S = 1)
        opens the path O ← [S] → U → R6
```

The correlation r = 0.42 is estimated inside a sample defined by S = 1. It reflects a collider-opened path, not the causal effect of O on R6.

---

## Step 4: Why this is not a survivorship-by-accident problem

This is a textbook case of **collider stratification bias** (also called Berkson's bias or selection bias). It is not merely that the sample is "unrepresentative" in a vague sense. The specific structure is:

1. S has two causes: O and U.
2. The analysis conditions on S.
3. U also causes the outcome R6.
4. Therefore, conditioning on S opens a back-door path from O to R6 that runs through U.

Filtering to "highest-quality users" is precisely the operation that creates this bias. The users who survive to day 90 *without* completing onboarding disproportionately have very high U; users who survive *because of* onboarding may have lower baseline U. Within the survivor pool, O and U are anti-correlated in a way they are not in the full population. Because U drives R6, this makes O appear more predictive of R6 than it actually is causally.

---

## Step 5: What the data cannot tell us

The r = 0.42 correlation is a rung-1 finding inside a biased sample. It cannot be converted into a causal effect size for an intervention by any amount of regression, matching, or covariate adjustment performed *within this sample*. The selection was already made; the collider was already conditioned upon. This is not a fixable omitted-variable problem — it is a structural problem with which sample was chosen.

Concretely: if the product team invests in nudging low-engagement users to complete onboarding, those users are not in this sample. The correlation within day-90 survivors tells us nothing about what happens when we intervene on the broader population. The effect for non-survivors is structurally absent from the data.

---

## Step 6: Alternative structural interpretations and their implications

Being explicit about alternative DAGs is the discipline that separates a diagnostic from a description.

**Alternative A (the claimed story):** Onboarding completion causally builds habits and product familiarity, which directly cause long-term retention. Under this DAG, O → R6 is a real causal path, and the correlation is partly capturing it. The problem: even under this DAG, the selection on S inflates the estimate because the collider-opened path is still present. You cannot know how much of r = 0.42 is the causal effect and how much is the bias.

**Alternative B (pure selection artifact):** O has no causal effect on R6 beyond what it contributes to early retention. All of r = 0.42 is the collider path. Under this DAG, investing in onboarding completion would produce zero improvement in 6-month retention for the broader user base.

**Alternative C (mediation through early retention):** Onboarding completion causes early retention (O → S), which in turn might improve 6-month retention (S → R6), but the direct path O → R6 is small or zero. Under this DAG, you'd want to improve onboarding for early retention benefits — but the magnitude inferred from this sample is still inflated by collider bias.

The data as structured cannot discriminate among these alternatives. They are all consistent with r = 0.42 in the survivor sample.

---

## Step 7: How to actually answer the question

To identify whether improving onboarding completion causally increases 6-month retention, you need one of the following:

**1. Randomized experiment (preferred).** A/B test where a randomly selected subset of users receives onboarding nudges or a redesigned checklist. Measure 6-month retention for the full intention-to-treat population — not filtered to early survivors. This directly estimates P(R6 | do(O)).

**2. Redo the analysis in the full user population** (rung-1, at minimum). Compute the correlation between onboarding completion and 6-month retention without pre-filtering to day-90 survivors. This won't be causal, but it avoids the collider bias and gives an uncontaminated association to reason from. Then control for observable proxies of U (e.g., acquisition channel, session depth in first week, device type) to close the U → O and U → R6 back-door paths.

**3. Instrumental variable.** Find a variable that exogenously shifts onboarding completion rates (e.g., an onboarding reminder email going out due to a technical glitch, an A/B test on onboarding design from a prior period, day-of-week at signup affecting checklist completion) but has no direct path to long-term retention. Use that as an instrument for O in the full population.

**4. Differences-in-differences.** If onboarding was redesigned or a campaign launched at a known point in time, compare cohorts before and after the change — looking at 6-month retention for users who had improved-onboarding exposure vs. those who did not — and use the control cohort's trend as the counterfactual.

---

## Step 8: The most likely trap being committed here

The analysis team has committed **collider conditioning / selection-on-the-outcome**. This is listed as a canonical structural mistake in the controls taxonomy. The framing "these are our most engaged, highest-quality users" treats the selection as a feature (we're studying the right people) when it is actually a bug (we've conditioned on a collider and induced spurious correlations throughout the dataset).

The statistical significance (p < 0.001) and the magnitude (r = 0.42) make this harder to dismiss intuitively, which is exactly why structural thinking is necessary. A collider-opened path can produce arbitrarily strong and statistically significant associations. p-values and correlation magnitudes do not diagnose structural bias.

---

## Summary recommendation

Do not interpret r = 0.42 as evidence that improving onboarding completion will improve 6-month retention. The finding is a selection artifact. The correct response is:

1. **Do not invest based on this analysis alone.** The sample restriction has made the estimate uninterpretable for the intervention question.
2. **Run an A/B test** where users are randomly assigned to a high-quality onboarding experience vs. the status quo, and measure 6-month retention in the full randomized sample.
3. **As a faster diagnostic,** recompute the onboarding-retention correlation in the full user population (not filtered to day-90 actives) and control for observable proxies of baseline engagement to get a less-biased observational estimate while the experiment is being designed.
4. **Articulate the DAG** with the product and data teams before any next analysis. Specifically: what are the common causes of both onboarding completion and long-term retention? Those variables need to be measured and adjusted for, or the experiment is the only clean path.
