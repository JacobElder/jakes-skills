# Is the regression sufficient to establish causation?

**Short answer:** No. The regression establishes a strong, robust association — rung 1 work done well. Your manager is asserting a rung-2 conclusion: that intervening with the new flow *caused* the retention improvement. That leap requires causal identification, not regression robustness. "Adding more controls and the coefficient stays stable" is not the same as "the back-door criterion is satisfied."

---

## Step 1: Name the rung

The real question is rung 2: **"Did the new onboarding flow cause the retention improvement?"**

This is an interventional question. You want to know P(retention | do(new flow)) versus P(retention | do(old flow)) — what would retention be if you intervened to assign the new vs. old flow, across the user population.

Your data is observational. The new flow shipped as a product change, not a randomized experiment. There was no concurrent control group on the old flow. You are trying to answer a rung-2 question with rung-1 tools (regression and correlation).

Pearl's critical rule applies here directly: **a rung-2 question cannot be answered with rung-1 data alone without additional causal assumptions** — typically encoded in a DAG. No amount of data volume, p-value magnitude, or robustness checks overcomes this gap. A p < 0.001 tells you the association is unlikely to be sampling noise. It says nothing about whether the association is causal.

---

## Step 2: Sketch the DAG

The minimal causal structure for this problem:

```
U (unmeasured: seasonality, macro trends, competitor changes,
   cohort composition shifts, other product changes, ...)
  ↙                                                      ↘
New Onboarding Flow (X) ─────────────────────────> Retention (Y)
        ↑
   [measured controls Z: user age, device type, acquisition channel]
   [also potentially caused by or correlated with the time of launch]
```

The question is whether every back-door path from X to Y — every path that begins with an arrow *into* X — has been blocked by the measured controls. Three conditions must all hold for back-door identification:

1. The controls are correctly classified as confounders (not mediators or colliders).
2. The controls collectively close every back-door path.
3. There are no unmeasured confounders on remaining open paths.

Condition 3 is where this analysis fails. "New flow" is perfectly collinear with calendar time — it was rolled out to everyone at once. Every unmeasured factor that also changed over that 3-month window is a potential confounder, and no regression on measured pre-treatment user characteristics can close those paths.

---

## Step 3: The core identification failure — temporal confounding

Because the flow shipped at a single moment and was deployed universally (not to a random subset), **the treatment is confounded with everything else that changed in the same period**:

- Seasonal patterns in user behavior and acquisition (cohorts who sign up in different quarters have different retention profiles)
- Changes in acquisition channel mix or marketing spend that altered the composition of new users
- Other product changes shipped during the same 3-month window
- External market shifts (competitor quality changes, platform algorithm changes, macro economic conditions)
- Regression to the mean if retention was in an unusual dip before the launch

The back-door path structure looks like this:

```
Time/Period + Unmeasured Co-occurring Factors (U)
  ↙                                                ↘
New Flow shipped (X)                          Retention (Y)
```

Your three controls (Z = age, device type, acquisition channel) may close paths *through those specific variables*. They do not and cannot close paths through U — the unmeasured temporal and cohort factors. The back-door criterion requires closing *every* path with an arrow into X. Paths through unmeasured factors remain open.

---

## Step 4: Why coefficient stability does not establish causation

Your manager's reasoning — "it's robust to adding more controls, so it's real" — is one of the most common conflations in applied work. Here is the precise failure:

**What stability actually tells you:** the coefficient on New Flow doesn't change much when additional measured covariates are added. This is consistent with two completely different underlying situations:

1. *The favorable story:* the additional controls happened to be the remaining confounders, they're now absorbed, and the residual coefficient reflects a genuine causal effect.
2. *The unfavorable story:* the additional controls are near-orthogonal to the main confound (the time trend / unmeasured factors), so they barely move the coefficient — not because confounding is removed, but because those variables weren't carrying the confounding to begin with.

Scenario 2 is the expected result when the dominant confounder is temporal and your controls are all individual-level user characteristics measured at signup. Signup-level variables are largely orthogonal to the time of launch because they characterize the person, not the period. Adding more of them changes the coefficient very little — which looks like robustness but is actually evidence that the controls aren't addressing the dominant threat.

Additionally, if any control variable added in the robustness checks is *downstream* of the new flow — something the onboarding experience could itself affect — then you have partially conditioned on a mediator. Coefficient stability under a mediator control is actively misleading: it means the estimate has been attenuated, and "stable" just means it was attenuated before too.

---

## Step 5: Classify each control's structural role

Applying the per-variable classification from Pearl's framework:

**User age.**
Plausibly a confounder. Age at signup predates treatment assignment and may predict both who signs up (acquisition mix varies by age) and retention (older users may be stickier or more churnable depending on the product). The structural role is likely fork (Age → X; Age → Y), making it a valid control. However, age proxies only weakly for cohort-level differences driven by *when* someone signed up — a 28-year-old signing up in October and a 28-year-old signing up in January are the same age but belong to different cohorts with potentially different retention behavior. The control absorbs individual-level age variation but not period-level cohort effects.

**Device type.**
Requires scrutiny. Two possible structural roles:

- *Confounder (fork):* Device type → X and Device type → Y, if mobile users disproportionately received the flow or the flow was built for mobile, AND mobile/desktop users have inherently different retention rates. If measured before flow exposure and not affected by the flow, this is a valid control.
- *Mediator:* If the new onboarding flow changed which device users chose to engage with going forward, device type post-onboarding is a descendant of X — controlling for it blocks part of the causal effect. Ask: was device type measured at the point of onboarding assignment, or afterward? Could the onboarding experience itself steer users toward a different device or platform?

If device type is a mediator and you've controlled for it, the coefficient is measuring only the portion of the effect that does not operate through device shift — not the total effect.

**Acquisition channel.**
Similar ambiguity. Acquisition channel likely predates the onboarding flow and correlates with both treatment exposure (if certain channels drove more traffic around the launch) and retention (organic users typically retain better than paid). This is the strongest candidate for a genuine confounder. The concern is whether channel mix also shifted in the same 3-month window for reasons other than the flow — if the company ran a new paid campaign at launch, channel is now also a proxy for the period effect, which it will absorb some of but not completely.

**Overall verdict on controls:** These three variables address a narrow slice of the identification problem. They're worth including. They do not constitute a closed back-door because the dominant threat — unmeasured temporal confounders — passes through variables entirely absent from the model.

---

## Step 6: Enumerate alternative structural interpretations

The structural question your manager is treating as settled actually has multiple live interpretations:

| Structural interpretation | What the data would look like | Verdict |
|---|---|---|
| New flow causally improved retention by 7pp | Regression coefficient +0.07, robust to measured controls | Consistent with the data |
| Seasonal cohort effect: Q1 cohorts always retain better, and the flow launched at Q1 | Same regression result | Also consistent |
| Acquisition channel shifted toward organic at launch (new SEO campaign) | Same regression result if channel control is imperfect | Also consistent |
| Concurrent product change (feature, bug fix, server reliability) drove retention | Same regression result | Also consistent |
| Combination of causal effect + confounding inflating it | Same regression result | Also consistent |

The data you have cannot discriminate between these stories. This is what "not identified" means in practice — not that the estimate is wrong, but that the estimate is consistent with too many causal structures to support a definitive conclusion.

---

## Step 7: What would actually establish causation

In order of strength for this specific problem:

**1. Concurrent A/B test (randomization).** The correct retrospective response to "we shipped it and retention went up" is: now run a holdout. Randomly assign a small percentage of new users to the old flow. The difference in retention between groups, measured over 30-90 days, gives an unbiased causal estimate under ITT (intent-to-treat). This closes the temporal confound entirely because treated and control groups are contemporaneous.

**2. Differences-in-differences (DiD).** If there exists a comparable segment that did *not* receive the new flow (a platform, geography, or product tier where it wasn't deployed), and you have pre-period retention data for both groups, DiD differences out shared time trends. The identifying assumption is parallel trends — that the two groups would have trended the same absent the flow. This must be validated with a pre-period plot. If trends diverged before launch, parallel trends is implausible.

**3. Regression discontinuity (RDD).** If the flow was deployed based on signup date (users who signed up before date T got old flow; after T got new flow), users immediately on either side of T are comparable. The identifying assumption is no other discontinuity at T and no manipulation of assignment. This is feasible if the rollout was sharp and precisely dated.

**4. Instrumental variable.** If a technical deployment variable caused some users to get the new flow while others (randomly or quasi-randomly) did not — a server-side rollout percentage, a bug that delayed exposure for a subset — that could serve as an instrument. The instrument must affect flow assignment but have no direct effect on retention other than through the flow. This requires careful validation.

**5. Sensitivity analysis (minimum viable step if nothing else).** Using Cinelli & Hazlett (2020) / `sensemakr`, compute how strong an unmeasured confounder would need to be (in terms of its partial R² with the treatment and outcome) to reduce the coefficient to zero. If it would require a confounder as strong as the strongest measured predictor, the conclusion may be robust. If a modest confounder suffices, it isn't. This doesn't establish causation but it quantifies the threat.

---

## Step 8: Evidence summary

| Claim | Status |
|---|---|
| Retention improved ~7pp around the launch window | Supported — descriptive fact |
| The association between new-flow exposure and retention is not sampling noise | Supported — p < 0.001 addresses this |
| The association persists after controlling for age, device type, acquisition channel | Supported — the regression addresses this |
| All back-door paths from new flow to retention are blocked | Not established — temporal/unmeasured confounders remain |
| The new flow causally produced the retention improvement | Not established |
| 7pp is a reliable estimate of the causal effect magnitude | Not established |
| Investment decisions should treat this as a 7pp causal effect | Not supported without identification |

---

## What to tell your manager

The regression tells you the association is not due to chance and is not explained by the three measured covariates you controlled for. Those are meaningful facts. What the regression cannot tell you is whether something else that also changed in the same 3-month window — something your measured variables don't capture — is partly or wholly responsible for the improvement.

"Robust to adding controls" means the result isn't driven by age, device, or channel differences. It does not mean all confounders have been addressed. It means the confounders you measured weren't the main story — which is consistent with either good identification or with an unmeasured temporal confounder dominating.

The 35% → 42% improvement is meaningful evidence. The right action is not to declare it settled — it's to run a concurrent holdout A/B test. The cost of that test is low (a small percentage of new users on the old flow for 60-90 days). The cost of incorrectly attributing a cohort trend to the feature — and then making downstream roadmap and resource decisions on a falsely attributed 7pp effect — is high.

Statistically significant in a well-controlled regression is one standard of evidence. Causally identified is a different, stricter standard. Applied work conflates these routinely. Your manager's conclusion is common; it is also incorrect.

---

## Diagnostic summary

- **Rung mismatch:** rung-2 question ("did this cause retention to improve?") answered with rung-1 tools (regression/correlation).
- **Core identification threat:** temporal confounding — new flow is perfectly collinear with calendar time; everything else that changed in those 3 months is a potential unmeasured confounder.
- **What the controls do:** close back-door paths through user age, device type, and acquisition channel specifically. Do not close paths through unmeasured time-varying factors.
- **Why stability doesn't help:** coefficient stability under controls that are orthogonal to the dominant confound is not evidence of identification. It's evidence that those specific controls weren't carrying the confounding.
- **Most likely trap triggered:** confounding ignored — temporal/period effects mistaken for treatment effects.
- **Path forward:** concurrent A/B test is the cleanest resolution; DiD with a comparable untreated segment is the observational alternative.
- **Appropriate posture:** strong suggestive evidence, not settled proof. Run the identification strategy before locking in causal conclusions or scaling investments based on a 7pp causal estimate.
