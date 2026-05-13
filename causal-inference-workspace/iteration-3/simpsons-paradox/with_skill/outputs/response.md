# Causal Diagnosis: Simpson's Paradox at Checkout

## The short answer

Your analyst is probably wrong. Killing the feature based on the platform-level splits is likely the wrong call — and the reason is a classic structural error: treating a post-treatment mediator as if it were a pre-treatment confounder.

---

## Step 1: Name the rung

This is a **Rung 2 (Intervention)** question: "Does deploying this checkout feature cause an improvement in overall conversion?" You have an A/B test, which is the right tool for Rung 2. The question is not whether there is confounding — randomization handles that — but whether the platform breakdown should govern the decision.

---

## Step 2: Sketch the DAG

Two structural stories compete here.

**Story A — Platform is a confounder (your analyst's implicit assumption):**

```
Platform (web / app)
      |            \
      v             v
  Feature ------> Conversion
  Exposure
```

Under this DAG, platform is a pre-existing characteristic that causes both which users end up in which checkout channel and how likely they are to convert. If randomization failed to balance platform across arms, the overall +2.1% would be confounded, and the platform-stratified results would be the honest ones.

**Story B — Platform is a mediator (the more plausible story given how the feature works):**

```
Feature Exposure  -->  Platform (web vs. app)  -->  Conversion
        |                                                 ^
        |_________________________________________________|
                    (direct effect, if any)
```

Under this DAG, the feature *itself* causes some users who would otherwise complete a web checkout to instead complete an app checkout. Platform is not a stable pre-treatment characteristic — it is an outcome of the treatment. The feature shifts the mix of users between platforms, and that shift is part of how it produces higher conversion.

---

## Step 3: Identify which structure is correct

The diagnostic is mechanical: **could the treatment itself cause a user's platform to change?**

Your feature description answers this directly. The feature "prominently shows a 'Continue on App' prompt at checkout." By construction, its mechanism is to redirect users from web checkout to app checkout. Users who would have been web converters (or web non-converters) are pushed toward app checkout. Platform is not fixed before treatment exposure — the treatment actively moves people across platforms.

This means platform is a **mediator**, not a confounder. Part of the causal effect of your feature operates *through* the channel: Feature → user switches to app → higher conversion. That channel is real. Stratifying by platform and computing effects within each platform blocks that exact channel.

The skill's explicit guidance applies here: *"The critical diagnostic before concluding 'segment is a confounder' is: could the treatment itself have caused users to change segments? A feature that redirects users to a mobile app could cause web users to become app users; 'platform' would then be a mediator on the treatment path, and the aggregate result is the correct one."*

---

## Step 4: Why the platform-stratified results go negative

When you condition on a mediator, you induce overcontrol bias. Here is the mechanics in your specific case.

Suppose the feature's effect consists of two components:

1. **Switching effect**: The prompt moves some fraction of web users (who convert at a lower rate) to app checkout (which converts at a higher rate). This is a positive effect operating through platform composition.

2. **Within-platform selection distortion**: Among users who remain on web in the treatment arm (those who saw the prompt and did not switch), they are a negatively selected residual — the ones with lower intent or stronger web preference. The web-checkout population in the treatment arm is now adversely selected compared to the web-checkout population in the control arm. Meanwhile, the app population in the treatment arm is diluted with switchers who had lower intent than the app-native users in the control arm.

Both within-platform comparisons go negative because the feature re-sorted users across platforms in a way that corrupts within-stratum intent comparability. The aggregate result — which does not condition on which platform someone ended up on — correctly captures the total effect including the switching benefit.

This is Simpson's Paradox, but the resolution is not "trust the stratified results." The DAG decides the resolution, and the DAG here points to the aggregate.

---

## Step 5: The structural rule for Simpson's Paradox

**Confounder → disaggregate. Mediator → aggregate.**

- If platform were a pre-existing characteristic that independently causes conversion (mobile-first vs. desktop-first users already assigned before hitting your checkout page), and if randomization somehow failed to balance it, then platform-stratified results would be right.
- If platform is a downstream consequence of the feature — as it is here, because the feature literally redirects people to the app — then platform is a mediator, and the aggregate result is the correct one.

Your feature's mechanism is the routing. You cannot evaluate the routing effect by conditioning on where people ended up. That is like evaluating whether a drug lowers blood pressure by controlling for whether the patient's blood pressure went down.

---

## Step 6: What a valid analysis looks like

Since you have a true A/B test, the overall ITT (intent-to-treat) estimate — the +2.1% in aggregate — is the correctly identified causal effect of offering the feature. It requires no adjustment.

If you want to decompose the effect, the right question is not "what's the effect within each platform?" but rather:

- **What fraction of the lift comes from the switching channel vs. direct within-platform effects?** This is a mediation analysis question, not a stratification question. You would model the switching rate as an intermediate outcome and decompose the total effect into direct and indirect components.
- **Are there user segments where the feature hurts even accounting for the switching?** This is a CATE (conditional average treatment effect) question. The relevant segmentation variables are *pre-treatment* characteristics — user tenure, device type at the start of the session, prior conversion history — not platform, which is post-treatment.

---

## Step 7: The key diagnostic check

Before accepting either interpretation, run this:

**Compare platform composition across arms.** If the feature caused switching, the treatment arm should have a meaningfully higher share of app checkouts than the control arm. If the platform mix is identical across arms, the switching story collapses and the stratified results gain credibility. If the treatment arm shows significantly more app checkouts, that is direct evidence that platform is a mediator and the aggregate estimate is the right one.

A single cross-tab answers this. It is the falsification test that resolves the structural ambiguity.

---

## Step 8: Alternative structural roles — robustness check

For completeness, here is what the recommendation becomes under each possible DAG:

| Platform role | Structural story | Correct estimate | Decision |
|---|---|---|---|
| Pre-treatment confounder | Platform determines which checkout type users prefer, and randomization failed to balance it | Platform-stratified results | Kill the feature |
| Post-treatment mediator | Feature causes users to switch platforms; switching drives the conversion lift | Aggregate result (+2.1%) | Ship the feature |
| Collider | Platform is caused by both the feature and some third variable that also affects conversion | Neither estimate is clean | Investigate further |

The confounder interpretation requires that randomization failed — possible but unlikely with a proper A/B test, and checkable by looking at pre-treatment platform preference. The mediator interpretation is directly implied by the feature mechanism and is the prior you should start with.

---

## Summary verdict

| Question | Answer |
|---|---|
| Is the +2.1% overall estimate real? | Yes — assuming clean randomization, it is the ITT causal effect. |
| Should you trust the platform-split negatives? | No — platform is almost certainly a mediator, not a confounder. |
| Is this Simpson's Paradox? | Yes — but the resolution favors the aggregate, not the disaggregate. |
| Should you kill the feature? | Not on this evidence. The platform-level results are artifacts of conditioning on a downstream outcome of the treatment. |
| What should you do first? | Compare platform composition across arms. If treatment has more app checkouts, the mediator story is confirmed and the aggregate result stands. |

Your analyst's error is a common one: Simpson's Paradox creates an intuition that the "more granular" result is always the more honest one. That intuition is wrong. The DAG decides which level of aggregation is correct, and in this case the mechanism of the feature itself makes platform a consequence of treatment, not a background control variable.
