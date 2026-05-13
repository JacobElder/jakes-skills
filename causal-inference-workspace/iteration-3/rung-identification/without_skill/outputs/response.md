# Is the Regression Sufficient to Establish Causation?

**Short answer: No. The regression is suggestive and worth taking seriously, but it does not establish causation — and your manager is overreaching.**

---

## What the Regression Actually Tells You

A regression with controls (user age, device type, acquisition channel) can reduce *observed* confounding. If the coefficient on "new flow" is +0.07 with p < 0.001 and it's stable as you add more controls, that's a meaningful signal. It means:

- The association is not easily explained by those three observable factors
- The effect size is plausible and consistent

That's genuinely useful information. But "not explained by the controls we thought of" is a long way from "caused by the new flow."

---

## Why Regression Alone Doesn't Establish Causation

### 1. Unmeasured Confounding (Selection Bias)

The most important threat. Users who experienced the new flow are not randomly assigned — they were exposed to it because of *when* they signed up. What else changed in that three-month window?

- Did marketing targeting change (bringing in different-quality leads)?
- Did a seasonal pattern shift the acquisition mix?
- Did the product itself change beyond the onboarding flow?
- Did support quality, pricing, or competitors' products change?

No matter how many controls you add, you can only control for variables you *measured and included*. Any unmeasured variable that (a) correlates with receiving the new flow and (b) independently affects retention is a confounder that regression can't touch.

### 2. The Pre/Post Design Problem

This is fundamentally a before-after comparison (35% → 42%). Pre/post designs are among the weakest causal designs because time itself is a confounder. Users in the "before" period differ from users in the "after" period in every way that time captures — macro trends, product maturity, team learning, market conditions. Controlling for age, device, and channel doesn't fix this.

### 3. Statistical Significance is Not Causal Evidence

p < 0.001 tells you the association is unlikely to be zero. It tells you nothing about whether the association is causal. You can have a highly statistically significant spurious correlation. The regression is estimating a conditional association, not an effect.

### 4. Stability Across Controls is Encouraging but Not Definitive

Coefficient stability as you add controls is a sign that the estimate isn't driven by the particular covariates you tested. Some researchers treat this as mild evidence of causation (it's harder to explain away). But it only checks robustness to *observed* variables. The unobserved confounders remain unaddressed.

---

## What Would Actually Strengthen the Causal Claim?

**Stronger designs, roughly in order of credibility:**

1. **Randomized controlled experiment (A/B test)**: Random assignment to old vs. new flow. This is the cleanest design. If you have this data, it dominates everything else.

2. **Difference-in-differences**: If you have a control group that *didn't* receive the new flow (e.g., users in a different region, or a holdout group), compare the change in retention across groups. This controls for time trends.

3. **Regression discontinuity**: If the new flow launched on a specific date, users just before and just after the launch date are likely very similar. Comparing retention for users who signed up just before vs. just after can approximate a local experiment.

4. **Instrumental variables**: If there's a variable that predicts exposure to the new flow but has no direct effect on retention, you can use it to isolate exogenous variation.

**Supplementary evidence that builds the case:**

- Granular behavioral data: Do users who completed specific new flow steps (vs. dropped out mid-flow) show dose-response patterns in retention?
- Replication across cohorts: Does the effect appear consistently across different segments, or is it driven by one subgroup?
- Falsification tests: Are there outcomes that *shouldn't* have changed that also changed? If so, something else is going on.

---

## How to Frame This With Your Manager

Your manager's instinct is understandable — the evidence is meaningful and the effect size is practically significant. But "settled" is the wrong frame. Here's a more accurate framing:

- "We have strong observational evidence that the new flow is associated with improved retention, and the association holds up to the controls we've tested."
- "The most plausible alternative explanations are [list the ones you've investigated and can rule out]."
- "We can't rule out unmeasured confounders without a stronger design, so we should continue treating this as a high-confidence hypothesis rather than a proven causal claim."
- "The right next step to settle it is [RCT / holdout group / DiD], which we should run before scaling this further or using it as a template."

That framing is honest, actionable, and respects both the value of the evidence you have and its limits.

---

## Summary

| Claim | Warranted? |
|---|---|
| The new flow is associated with higher retention | Yes |
| The association is robust to observed covariates | Yes, based on your controls |
| The regression coefficient is statistically significant | Yes |
| The new flow *caused* the retention improvement | Not established |
| The analysis is "settled" | No |

The regression is a useful piece of evidence that should inform your decision-making. It is not sufficient to establish causation, and treating it as settled shuts down the kind of careful thinking that would protect you from acting on a spurious correlation at scale.
