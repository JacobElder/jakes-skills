# Causal Effect of Executive Mentorship on Promotion Rates

## Question

I'm estimating the causal effect of receiving executive mentorship on promotion rates. Mentorship is almost exclusively given to employees who have already demonstrated high performance — the correlation between prior performance and receiving mentorship is around 0.85. Prior performance also predicts promotions directly. A colleague says I should control for prior performance to remove its confounding effect. Is that the right approach?

---

## Answer

Your colleague is pointing at a real problem — prior performance is a confounder, and ignoring it entirely would bias your estimate upward. But the recommendation to simply control for it deserves more careful thought, because the specific structure of your data introduces a second, less obvious hazard: **bias amplification**.

### The Confounding Structure

The causal graph here looks roughly like this:

```
Prior Performance --> Mentorship --> Promotion
Prior Performance ----------------------^
```

Prior performance causes both treatment assignment (mentorship) and the outcome (promotion). That is a classic backdoor confound. Your colleague is right that you need to address it.

### Why Controlling for Prior Performance Is Complicated

Here is the problem. When a covariate is a very strong predictor of treatment but only a moderately strong predictor of the outcome, controlling for it does not cleanly remove confounding — it can actually **amplify bias from any remaining unmeasured confounders**.

This is the bias amplification phenomenon, formalized by Bhattacharya and Vogt (2007) and Pearl (2010). The intuition works like this:

1. You have an unmeasured confounder U (e.g., social capital, manager favoritism, networking skill) that affects both mentorship receipt and promotions.
2. Prior performance is very strongly tied to mentorship (r = 0.85), meaning it is nearly an instrument for treatment — it predicts treatment strongly but is only a partial predictor of the outcome through channels other than treatment.
3. When you condition on prior performance, you partial out a large chunk of the variance in mentorship. The residual variation in mentorship — the part your model is now using to estimate the effect — is disproportionately driven by U.
4. The ratio of bias-from-U to signal-from-mentorship grows after conditioning, not shrinks.

In formal terms: if X is a near-instrument (strong treatment predictor, weaker direct outcome predictor), conditioning on X increases the coefficient on U relative to the coefficient on treatment in an OLS framework, amplifying rather than reducing omitted variable bias.

### How Strong Is This Concern in Your Case?

With a treatment-covariate correlation of 0.85, this is a serious concern. The amplification factor scales with the R-squared of the treatment model. At r = 0.85 (R² ≈ 0.72), adjusting for prior performance explains about 72% of treatment variance, leaving the residual treatment variation heavily loaded on whatever else drives mentorship selection — which is precisely where unmeasured confounders live.

This does not mean prior performance is useless as a control — it is genuinely a confounder and some adjustment is better than none if it is the only confounder. But the near-instrument structure means you should be cautious about claiming that controlling for it "solves" the confounding problem.

### What You Should Do Instead

**1. Be honest about the identification challenge.** With r = 0.85 between prior performance and treatment, you are in a regime where standard regression adjustment is fragile. Prior performance is close to an instrument for mentorship, which means it is simultaneously useful for adjustment and dangerous if used naively.

**2. Consider a richer outcome model.** If the direct effect of prior performance on promotion is well-specified and the functional form is correct (e.g., both have nonlinear effects), a well-specified model that includes prior performance may still recover a consistent estimate. But this puts heavy weight on correct functional form.

**3. Pursue a quasi-experimental design if possible.** Given that mentorship is nearly deterministic above some performance threshold, a regression discontinuity design around that threshold would be far more credible than regression adjustment. Even an approximate threshold (e.g., a performance rating cutoff) could be exploited.

**4. Conduct sensitivity analyses.** Use tools like the E-value (VanderWeele & Ding, 2017) to quantify how strong unmeasured confounding would need to be to explain away your estimated effect. Given the bias amplification risk, a large E-value should be required before you trust the estimate.

**5. If you control for prior performance, do it thoughtfully.** Use flexible functional forms (splines, quantile bins), not a linear control. A linear control assumes a linear relationship between prior performance and both treatment and outcome, which is unlikely to hold exactly at the extremes where most of the mentorship-assignment action occurs.

### Bottom Line

Your colleague is right that prior performance is a confounder you must address. But controlling for it is not automatically the right solution — and in your case, the near-instrument structure (r = 0.85) means that conditioning on it may amplify bias from unmeasured confounders rather than reduce overall bias. The honest answer is that this is a hard identification problem, and regression adjustment alone is unlikely to give you a credible causal estimate. You need either a quasi-experimental design that exploits discontinuities or thresholds in mentorship assignment, or at minimum a serious sensitivity analysis about what your estimate is robust to.
