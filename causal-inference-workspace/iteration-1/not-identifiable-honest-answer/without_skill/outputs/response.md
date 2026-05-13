# Can You Estimate the Causal Effect of Mentorship on Career Success from Observational Data?

## Short Answer

Possibly — but not without strong assumptions that your data alone cannot verify. The honest answer is that causal identification is not guaranteed here, and the credibility of any causal claim depends entirely on how well you can defend those assumptions.

---

## Why This Is Hard: The Fundamental Problem of Causal Inference

The core challenge is the **fundamental problem of causal inference**: you can never simultaneously observe the same person both with and without a mentor. What you observe is a correlation between mentorship status and salary. Whether that correlation reflects a causal effect, a selection effect, or both is the central question.

In your data, people who sought out mentors are almost certainly not a random draw from the population. They likely differ from non-mentored professionals in ways that also predict career success:

- Higher ambition or motivation
- Better social capital or access to networks
- Being employed at firms that offer formal mentorship programs (often large, well-paying firms)
- Higher baseline ability or credentials
- More proactive career management in general

This is **confounding** — the mentored group and unmentored group differ on variables that independently affect salary, making a raw comparison misleading. The "effect" you measure is a mixture of the true causal effect and selection into mentorship.

---

## What You Would Need to Assume

To estimate a causal effect from observational data, you need to invoke one of several identification strategies. Each requires assumptions that go beyond the data itself.

### 1. Selection on Observables (Regression / Matching / IPW)

**The assumption:** Conditional on the variables you observe (demographics, etc.), mentorship assignment is as good as random — i.e., there are no unobserved confounders. This is called **conditional ignorability** or the **no unmeasured confounders** assumption.

**What this means in practice:** You run a regression of salary on mentorship status plus controls, or you match mentored and unmentored individuals on observable characteristics, or you use inverse probability weighting (IPW). If the assumption holds, the estimated coefficient on mentorship is causal.

**The problem:** This assumption is almost certainly violated in your setting. Motivation, ambition, network quality, and personality traits are major confounders that you almost certainly do not observe. A regression controlling only for demographics will not close these backdoor paths. No amount of statistical sophistication fixes an omitted variable that is correlated with both mentorship and salary.

**Bottom line:** You can run these models, and they may be informative about associations, but claiming the result is causal requires arguing that your covariate set captures all relevant confounding — a difficult case to make here.

---

### 2. Instrumental Variables (IV)

**The idea:** Find a variable (an "instrument") that:
1. Causally affects whether someone had a mentor
2. Has no direct effect on salary (except through mentorship)
3. Is independent of unobserved confounders

**Example instruments in principle:** Exogenous variation in access to mentorship programs — e.g., whether someone's employer happened to run a formal mentorship program, or random assignment to a cohort that had a mentor available. Geographic or firm-level variation in mentorship culture that the individual did not self-select into.

**The problem:** Good instruments are rare and hard to argue for convincingly. The exclusion restriction (assumption 2) is untestable, and weak instruments cause serious bias. If you don't have an instrument in your data, IV is unavailable.

**Bottom line:** Unless you have a plausible instrument, this strategy is not available to you.

---

### 3. Regression Discontinuity (RD)

**The idea:** If there is some threshold rule that determined mentorship assignment — e.g., people at firms with more than 100 employees got assigned to a program — you can compare outcomes just above and just below the cutoff.

**The problem:** Mentorship in your data is self-reported and voluntary. There is no natural threshold rule. RD almost certainly does not apply here.

---

### 4. Difference-in-Differences (DiD)

**The idea:** Compare changes in outcomes over time for those who gained a mentor versus those who did not, controlling for time trends.

**The problem:** Your data appears to be a single cross-section (no panel structure, no pre/post measurement). DiD is not available without longitudinal data.

---

### 5. Propensity Score Methods

**The idea:** Estimate the probability of having a mentor given observed covariates (the propensity score), then match or weight on this score to create a pseudo-experimental comparison.

**The problem:** Propensity score methods are a form of "selection on observables." They do not address unobserved confounding — they only balance the distribution of observed covariates. In your setting, the most important confounders are likely unobserved (motivation, personality, etc.), so propensity score methods do not solve the identification problem.

---

## What You Can Honestly Do

Given your data — cross-sectional, self-reported, with demographics only — here is what you can credibly claim:

### What is credible:
- **Descriptive association:** "Professionals who had mentors earn on average $X more than those who did not, after controlling for age, gender, education, and industry."
- **Conditional correlations:** Regression coefficients that describe the relationship between mentorship and salary within subgroups.
- **Bounding analysis:** You can use techniques like sensitivity analysis (Rosenbaum bounds) or partial identification methods (Manski bounds) to characterize how large unobserved confounding would need to be to explain away your estimated association.

### What is not credible without additional assumptions or data:
- A clean causal claim that "having a mentor causes higher salary"
- Policy recommendations based on the causal interpretation

---

## Practical Recommendations

If you want to strengthen causal identification, here are paths forward:

1. **Collect better data:** If you can get longitudinal data (salary before and after mentorship), DiD becomes possible. If you can identify firms that randomly assigned mentors, you have quasi-experimental variation.

2. **Sensitivity analysis:** Report your association estimate but also show how sensitive it is to unobserved confounding. The `sensemakr` package in R or `rbounds` formalizes this. If a confounder would need to be implausibly strong to explain away your result, that strengthens the claim.

3. **Mechanistic reasoning:** Strengthen the causal interpretation by examining mechanisms (does mentored salary advantage appear in specific industries? Does it grow with career stage?). This doesn't prove causality but makes the story more coherent.

4. **Treat it as a lower/upper bound problem:** Use partial identification — ask not "what is the effect?" but "what range of effects is consistent with the data and plausible assumptions?"

5. **Be honest in your framing:** Present results as "the association between mentorship and earnings" rather than "the effect of mentorship on earnings" unless you can defend a specific identification strategy.

---

## Summary Table

| Strategy | Available? | Key Assumption | Likely Holds? |
|---|---|---|---|
| OLS with controls | Yes | No unobserved confounders | Probably not |
| Propensity score matching | Yes | No unobserved confounders | Probably not |
| Instrumental variables | Only with a valid instrument | Exclusion restriction | Unknown / hard to find |
| Regression discontinuity | No | Threshold-based assignment | Not applicable |
| Difference-in-differences | No | Panel data needed | Not applicable |

---

## Conclusion

You can estimate an **association** between mentorship and career success from your observational data, and that association is worth reporting. However, claiming a **causal effect** requires invoking the no-unmeasured-confounders assumption, which is almost certainly violated in this setting given that people self-select into mentorship based on unobserved traits (motivation, ambition, network access) that independently predict salary.

The most intellectually honest approach is to:
1. Report the conditional association with appropriate controls
2. Conduct a sensitivity analysis showing how robust the estimate is to unobserved confounding
3. Clearly state the assumptions required for a causal interpretation and assess their plausibility
4. Seek additional data or natural experiments if a clean causal claim is important

The data you have is useful and worth analyzing. It just cannot, on its own, definitively answer the causal question without strong auxiliary assumptions.
