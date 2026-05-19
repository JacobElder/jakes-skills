# Causal Effect of Executive Mentorship on Promotion Rates: Should You Control for Prior Performance?

## Short Answer

Your colleague's advice is directionally correct — prior performance is a confounder and you should account for it — but the situation is more nuanced than "just control for it." The extremely high correlation (r ≈ 0.85) between prior performance and mentorship receipt creates a specific statistical hazard called **bias amplification**, which can make naive covariate adjustment backfire.

---

## The Causal Structure

To reason carefully, let's lay out what we know:

- **Treatment (T):** Receiving executive mentorship
- **Outcome (Y):** Promotion
- **Confounder (C):** Prior performance

The causal graph looks like this:

```
Prior Performance (C) → Mentorship (T) → Promotion (Y)
Prior Performance (C) → Promotion (Y)
```

Prior performance causes both mentorship receipt and promotion directly. This is a classic **backdoor path**: `T ← C → Y`. Failing to block this path means any naive comparison of mentored vs. non-mentored employees will confound the treatment effect with the selection effect of who gets mentored in the first place.

So yes, you need to block this backdoor — your colleague is right about that much.

---

## The Problem: Near-Instrument Bias Amplification

Here is the critical subtlety your colleague is likely missing. When a variable is a very strong predictor of treatment assignment (r ≈ 0.85) but has only a moderate or weak effect on the outcome *independent of treatment*, controlling for it can actually **amplify bias** rather than reduce it.

### Why This Happens

The intuition comes from instrumental variable logic, run in reverse. Consider a spectrum:

- **Pure instrument:** A variable that affects treatment but has *zero* direct effect on the outcome. Controlling for an instrument removes useful variation in treatment without helping with confounding, biasing your estimate.
- **Pure confounder:** A variable that affects both treatment and outcome. Controlling for it is unambiguously helpful.
- **Near-instrument:** A variable that strongly predicts treatment but has only a weak direct effect on the outcome. Controlling for it amplifies any remaining unmeasured confounding.

With r ≈ 0.85 between prior performance and mentorship, you've described a situation where prior performance functions more like a near-instrument. When you condition on prior performance:

1. You substantially reduce the variance in the treatment variable (mentorship) — most of the "who gets mentored" signal is absorbed.
2. If there are *any* other unmeasured confounders (ambition, social capital, manager favoritism, etc.), the residual variation in mentorship is now more strongly correlated with those unmeasured factors.
3. Your estimate of the mentorship effect becomes more sensitive to — and potentially more biased by — those residual unmeasured confounders.

This is sometimes called **variance inflation of omitted variable bias**: the OLS formula for omitted variable bias scales with `1/(1 - R²)` in the first stage, meaning that when your confounder explains most of the treatment variance, any leftover omitted variable bias gets magnified.

### Formal Condition

Controlling for a variable reduces bias if and only if:

> The variable's direct effect on the outcome (relative to its effect on treatment) is large enough to offset the amplification of remaining omitted variable bias.

If prior performance's direct effect on promotion is strong — comparable to or larger than its indirect effect via mentorship — then controlling for it is clearly the right call. But if most of prior performance's association with promotion runs *through* mentorship (i.e., high performers get mentored and therefore get promoted), then controlling for prior performance might do more harm than good.

---

## What You Should Actually Do

### 1. Map the Causal Graph Carefully

Ask: Does prior performance predict promotion *independently* of whether someone receives mentorship? Or is mentorship the main mechanism through which high performers get promoted?

If prior performance has a strong *direct* effect on promotion (e.g., high performers get promoted even without mentorship, through raises, visibility, recognition), then controlling for it is appropriate.

If prior performance primarily predicts promotion *because* it selects people into mentorship, you may be conditioning on a near-instrument.

### 2. Consider What Else Is Unmeasured

Bias amplification is most dangerous when there are other unmeasured confounders. Think about what else predicts mentorship receipt beyond prior performance: networking behavior, demographic factors, manager discretion, team placement, self-promotion. If these are unmeasured and correlated with promotion, controlling for a strong predictor of treatment (prior performance) will amplify their confounding effect.

### 3. Think About Functional Form

Even if controlling for prior performance is the right direction, how you control matters. If the relationship is nonlinear or if performance interacts with mentorship, a simple linear control may leave substantial residual confounding.

### 4. Consider Alternative Strategies

Given the near-instrument structure, other approaches may be more robust:

- **Matching or weighting on prior performance:** Match mentored employees to non-mentored employees with similar prior performance scores, rather than parametrically controlling. This limits extrapolation.
- **Sensitivity analysis:** After controlling for prior performance, quantify how large an unmeasured confounder would need to be to nullify your estimated effect (e.g., using E-values or Rosenbaum bounds).
- **Regression discontinuity:** If there is a threshold in prior performance scores above which mentorship is systematically assigned, an RD design could recover a local causal effect without the amplification problem.
- **Difference-in-differences:** If you have pre/post data, you can difference out time-invariant employee-level confounders.

---

## Practical Recommendation

1. **Do control for prior performance** — it is a confounder and omitting it entirely is worse than including it, provided prior performance has a meaningful direct effect on promotions.

2. **Acknowledge the amplification risk** explicitly. With r ≈ 0.85, the effective sample of residual variation in mentorship after controlling for performance is small. Report sensitivity analyses alongside your main estimate.

3. **Enumerate other potential confounders** and assess whether your estimate is robust to their potential influence. An E-value analysis is a minimal standard here.

4. **Do not treat statistical adjustment as a complete solution.** The high selection rate into mentorship (driven by prior performance) means that even after adjustment, the counterfactual comparison — "what would have happened to this high performer without mentorship?" — is extrapolating into a region of the data with very few observations.

---

## Summary

| Situation | What to Do |
|---|---|
| Prior performance has strong direct effect on promotion | Control for it — it's a genuine confounder |
| Prior performance mainly predicts promotion through mentorship | Controlling may amplify bias — proceed cautiously |
| Other unmeasured confounders exist | Bias amplification risk is highest — use sensitivity analysis |
| r(performance, mentorship) ≈ 0.85 | The near-instrument problem is real; residual variation in treatment is small |

Your colleague is right that prior performance is a confounder that needs to be addressed. But the near-instrument structure created by r ≈ 0.85 means that simply "controlling for it" in an OLS regression is not a complete answer — and could, in the presence of other unmeasured confounders, produce an estimate that is more biased than no adjustment at all. Proceed with covariate adjustment but pair it with rigorous sensitivity analysis and, where possible, design-based alternatives.
