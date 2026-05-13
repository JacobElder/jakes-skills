# Is an 18% Retention Improvement a Reasonable Expectation for a Full Rollout?

**Short answer: No. Expecting 18% is almost certainly too optimistic, and the real effect could be substantially smaller — or even negative for some users.**

---

## What the Experiment Actually Measured

The +18% retention figure is an estimate of the **Average Treatment Effect on the Treated (ATT)** — that is, the effect of the new dashboard specifically among users who *chose to opt in*. This is not the same as what you'd get from a full rollout.

When you roll the new design out to everyone, you need the **Average Treatment Effect (ATE)** — the effect averaged across *all* users, including those who would have never voluntarily tried the new dashboard.

---

## Why These Two Numbers Are Likely Different

### 1. Self-selection bias in who opted in

Only 12% of invited users chose to try the new design. That 12% is not a random sample. They are almost certainly:

- More curious or tech-forward
- More engaged with the product to begin with
- More tolerant of change and interface disruption
- Perhaps already dissatisfied with the old dashboard

Users with these characteristics are likely to benefit *more* from a redesign than the average user. The 88% who declined are telling you something: they either prefer the status quo, feel friction around change, or simply don't care enough to try. When you force the new design on them, you may see little benefit — or even harm (frustration, churn from disorientation, support burden).

### 2. The matched control group may not solve this problem

Using a "matched control group of users who were invited but chose not to opt in" is a good attempt at a fair comparison — but the matching can only control for observable characteristics. The unobservable characteristic — *willingness to try something new* — is precisely the trait that drives both the decision to opt in and the likelihood of benefiting. This is a classic case of **selection on unobservables**, and matching cannot fix it.

### 3. The effect direction is not guaranteed to generalize

For the opt-in group, the new dashboard may align well with how they naturally think about the product. For other users — different roles, different workflows, different mental models — the redesign might be neutral or actively disruptive.

### 4. Novelty effects

Users who actively chose to try something new may be in a more engaged, exploratory mindset during the measurement window. Some portion of the 18% lift may reflect enthusiasm for the change itself, not the enduring quality of the redesign. This effect won't replicate when the new dashboard is simply the forced default.

---

## How Much Should You Discount the 18%?

There is no precise formula, but as a rough framework:

| Scenario | Expected ATE |
|---|---|
| Optimistic (new design is universally better) | 10–15% |
| Moderate (benefit concentrated among engaged users) | 5–10% |
| Pessimistic (opt-outs actively harmed or indifferent) | 0–5%, possibly negative for some segments |

The more different the opt-in population is from the average user, the more you should discount.

---

## What to Do Instead

1. **Run a proper randomized experiment (RCT).** Randomly assign users — regardless of whether they would have opted in — to the new dashboard vs. the old one. This directly estimates the ATE and removes self-selection entirely.

2. **Analyze heterogeneous effects.** Even within the opt-in experiment, look at whether retention gains were larger for certain user segments (tenure, role, usage level). This helps predict how non-opt-in users might respond.

3. **Stage the rollout and measure carefully.** Rather than a full cutover, do a phased release with a holdout control group. Treat it as a new experiment with the broader population.

4. **Talk to users who declined.** Qualitative research on why 88% did not opt in can reveal whether their hesitation reflects preference, indifference, or risk of harm.

---

## Bottom Line

The 18% figure is real — but it belongs to a self-selected minority. It is closer to a ceiling than a forecast for the general population. Planning and communicating around an 18% improvement for a full rollout is likely to lead to disappointment and may mask real harm to users who never wanted the change.

A conservative, honest forecast to stakeholders: "We expect a meaningful improvement, likely in the range of 5–10%, with significant uncertainty. We recommend a randomized rollout to get a clean estimate before committing fully."
