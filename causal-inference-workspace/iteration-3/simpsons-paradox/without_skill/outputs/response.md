# A/B Test Analysis: Simpson's Paradox in Checkout Feature

## Short Answer

Your analyst is wrong. The overall +2.1% conversion result is likely the correct signal. What you're describing is a textbook case of **Simpson's Paradox**, and killing the feature based on the platform-level splits would be a mistake.

---

## What's Happening: Simpson's Paradox

Simpson's Paradox occurs when a trend appears in aggregate data but disappears or reverses when the data is split into subgroups. It's not a data error or a bug — it's a mathematical consequence of how subgroups are weighted.

Here's why it's happening in your case:

Your treatment (the "Continue on App" prompt) is **changing the composition of who ends up on each platform.** The feature actively redirects web users toward the app. This means:

- **Control group:** Some mix of web vs. app users (e.g., 80% web, 20% app)
- **Treatment group:** A different mix — fewer web users, more app users (e.g., 60% web, 40% app)

Since app users convert at a much higher rate than web users, the treatment group naturally has a higher-converting composition. When you split by platform *after* this redirection has occurred, you're comparing:

- **Web/Treatment** vs. **Web/Control** — Treatment web users are now the *hardest to redirect* (those who ignored or declined the app prompt), so they may convert worse.
- **App/Treatment** vs. **App/Control** — Treatment app users include people who came from web (who may not have been planning to buy), diluting the app conversion rate.

The platform split is comparing **different populations within each platform**, not equivalent groups.

---

## A Concrete Numerical Example

Suppose in the **control** group:
- 800 web users → 8% convert → 64 conversions
- 200 app users → 40% convert → 80 conversions
- **Total: 144/1000 = 14.4% overall conversion**

In the **treatment** group (the prompt moved 200 web users to app):
- 600 web users → 7.5% convert → 45 conversions (web holdouts convert slightly worse)
- 400 app users → 37% convert → 148 conversions (includes redirected web users who convert less than native app users)
- **Total: 193/1000 = 19.3% overall conversion**

Now look at the platform split:
- Web: 7.5% (treatment) vs. 8.0% (control) → **negative**
- App: 37% (treatment) vs. 40% (control) → **negative**

Yet overall: 19.3% vs. 14.4% → **strongly positive**

Both platform-level results are negative. The aggregate result is massively positive. The feature works — it's just working by moving people between platforms, not by improving within-platform conversion.

---

## Why the Aggregate Is the Right Metric Here

The purpose of your A/B test is to measure **the causal effect of showing the prompt on total checkout conversion.** Users were randomly assigned to treatment or control, so the two groups are comparable in expectation. The overall conversion rate is the correct estimand.

The platform-level splits are **post-treatment variables** — they were influenced by the treatment itself. Conditioning on a post-treatment variable introduces collider bias and breaks the randomization. This is why the platform-level results are misleading.

In causal inference terms: platform is a **mediator** (or at minimum a variable downstream of treatment), not a baseline covariate. You should never condition on mediators when estimating a total treatment effect unless you specifically want to decompose direct vs. indirect effects.

---

## What Your Analyst Got Wrong

The analyst is implicitly reasoning: "it doesn't work for web users, and it doesn't work for app users, so it can't work overall." This logic is only valid when the subgroup splits are **independent of treatment assignment.** Here they are not — the feature *defines* which platform users end up on.

This is the classic Simpson's Paradox error. The subgroups look like natural splits, but they're actually endogenous to the experiment.

---

## What You Should Do

1. **Trust the aggregate result.** The +2.1% overall lift is valid because randomization was done at the user level before platform assignment.

2. **Verify the mechanism is real.** Confirm that the treatment group does indeed show higher app checkout rates — this validates that the feature is doing what you think it's doing (redirecting users to app).

3. **Check for other confounds.** Make sure there's no sample ratio mismatch (i.e., the treatment and control groups are the same size they should be), which would indicate a different problem.

4. **Decompose effects if needed.** If you want to understand the within-platform effects more rigorously, you'd need to use mediation analysis or instrument the platform variable — but this is supplementary analysis, not the basis for a kill decision.

5. **Consider practical significance.** +2.1% conversion is meaningful. Before shipping, validate that the app redirect experience is high-quality and doesn't create friction that erodes trust — but the statistical evidence supports keeping the feature.

---

## Bottom Line

Do not kill the feature. The negative platform-level splits are a predictable artifact of Simpson's Paradox caused by the feature itself changing platform composition. The aggregate A/B result — which preserves the integrity of randomization — is the correct measure of the feature's causal effect on conversion. Your analyst is conditioning on a post-treatment variable and drawing the wrong conclusion.
