# Does a Big Country Coefficient Mean Country Has a Causal Effect on Conversion?

No — and the confusion here is a textbook instance of the **Table 2 Fallacy**. Your treatment coefficient and the country coefficient are doing entirely different things in that regression, even though they share the same table.

---

## Step 1: Name the rung

Your question has two parts, even though you may not have framed it that way:

- **Part A:** What is the causal effect of the treatment on conversion? (Rung 2 — intervention)
- **Part B:** What is the causal effect of country on conversion? (Also rung 2 — intervention)

Both are rung-2 questions. The regression is a rung-1 tool (association). To get causal answers from it, you need an identification argument — and crucially, that argument is **different** for the treatment than for country. Having one does not give you the other.

---

## Step 2: What your regression was built to do

You included age, country, browser, and time-of-day as controls for a specific purpose: to identify the **treatment → conversion** effect. The logic is that some of these variables might confound the treatment assignment (e.g., if treatment probability varied by country or time-of-day). You chose an adjustment set designed to close back-door paths for **treatment**.

The back-door criterion for your focal effect requires:
- The adjustment set Z blocks every path from treatment to conversion that enters treatment with an incoming arrow.
- Z contains no descendants of treatment.

If your controls satisfy this for the treatment variable, then the **treatment coefficient** is identified. Good.

---

## Step 3: Why the country coefficient does not get the same free ride

Here is the core issue. Identifying the treatment → conversion effect requires blocking back-doors for **treatment**. Identifying the country → conversion effect would require blocking back-doors for **country**. Those are different sets of requirements, and your regression was not designed to satisfy the second one.

To estimate the causal effect of country on conversion, you would need to:
1. Draw a DAG with country as the focal exposure.
2. Identify all back-door paths from country to conversion.
3. Find a valid adjustment set that blocks all of those paths without opening colliders.

That adjustment set would almost certainly include variables you did not include — and would exclude some variables you did include that might be mediators on the country → conversion path.

### What is likely wrong with the country coefficient specifically

**Mediators are in the model.** Browser and time-of-day are plausibly *caused by* country — people in different countries use different browsers and have different peak-usage hours. If browser or time-of-day are on the causal path from country to conversion (country → browser → conversion, for instance), then conditioning on them in your regression **blocks part of the causal effect of country**, biasing its coefficient. This is overcontrol bias — conditioning on a mediator.

```
country → browser → conversion
country → time-of-day → conversion
country ──────────────→ conversion  (direct path)
```

If these mediated paths exist, then your regression's country coefficient estimates only the **direct effect** of country, not the total effect. Depending on how large the mediated paths are, the coefficient could be dramatically attenuated — or, if the direct and indirect effects have opposite signs, the coefficient could even flip sign.

**The adjustment set was optimized for a different focal variable.** The variables you chose close back-doors for treatment. There is no reason to believe they constitute a valid adjustment set for the country → conversion question. Some of them may be confounders for that question (age likely is), some may be mediators (browser, time-of-day plausibly are), and there may be confounders for the country question that you did not include at all — e.g., purchasing power, language, product-market fit, payment infrastructure availability.

**Multiple valid adjustment sets for treatment give unstable control coefficients.** Even when your treatment coefficient is robust across different valid adjustment sets, the country coefficient can vary wildly. Hünermund and Louw (2024) showed this explicitly: a control variable's coefficient is not stable across different valid adjustment sets for the focal treatment, even when the focal coefficient is. The number you see is an artifact of *this particular* set of covariates, not a stable structural quantity.

---

## Step 4: The Table 2 Fallacy, named

When researchers run a regression with a focal treatment and several controls, they often report all the coefficients in the same table and interpret each as that variable's causal effect. Westreich and Greenland (2013) called this the **Table 2 Fallacy**.

The logic is simple:

- Identifying treatment → conversion requires an adjustment set satisfying the back-door criterion **for treatment**.
- Identifying country → conversion requires an adjustment set satisfying the back-door criterion **for country**.
- These are generally different sets.
- A regression fit with the set appropriate for treatment will generally produce a **biased estimate** of country's causal effect.

Even when country is a perfectly valid control for estimating the treatment → conversion effect, country's own coefficient is typically biased for country's causal effect on conversion.

The practical implication: **in a causal regression, only the targeted coefficient deserves a causal interpretation. The rest describe model fit.**

A large, significant country coefficient means: country explains residual variance in conversion after conditioning on the other covariates in this particular model. That is all it means.

---

## Step 5: What the country coefficient actually reflects

Several mundane explanations are consistent with a large, significant country coefficient that have nothing to do with country's causal effect:

1. **Omitted confounders for country.** Variables correlated with country that independently affect conversion — purchasing power, cultural trust in online commerce, product-market fit — are not in the model. Their effects are absorbed into the country coefficient.

2. **Mediator overcontrol.** Browser and time-of-day mediate part of the country → conversion path. Conditioning on them shunts their contribution out of the country coefficient, making it a partial (direct-only) effect estimate of unknown reliability.

3. **Scaling and base-rate differences.** Countries differ enormously in their baseline conversion rates for reasons unrelated to any causal process you would want to intervene on. The coefficient captures these differences in ways that are definitionally associational.

4. **Model fit artifact.** The coefficient absorbs any systematic difference across countries not already captured by the other covariates — including measurement artifacts, data-collection differences, and population composition differences — none of which are causal effects.

---

## Step 6: What you would need to actually estimate country's causal effect

To answer "does country causally affect conversion?" you would need:

1. **A clear causal question.** What intervention are you imagining? You cannot change what country someone is in without changing many other things. This is the "no causation without manipulation" principle — it constrains what causal questions about fixed attributes like country even mean. A high causal estimate for "country" might actually be an effect of payment infrastructure, language, or product localization — each of which has a different intervention and a different policy implication.

2. **A DAG for the country → conversion question.** Draw the full set of plausible paths, including mediators (browser, time-of-day, language, device) and confounders (user acquisition channel, product availability, purchasing power).

3. **An adjustment set valid for that DAG.** This will almost certainly exclude browser and time-of-day if they are mediators, and include variables currently absent from the model.

4. **A separate regression** structured around country as the focal variable, with its own appropriate adjustment set. You cannot reuse the treatment regression.

---

## Summary

| Question | What the regression gives you | What you would need |
|----------|-------------------------------|---------------------|
| Effect of treatment on conversion | Identified, if controls satisfy back-door criterion for treatment | Done (assuming valid controls) |
| Effect of country on conversion | Not identified — likely biased due to mediators in model, missing confounders, back-door criterion not satisfied for country | Separate DAG for country, separate adjustment set, possibly a more specific causal question about what aspect of country you would intervene on |

The treatment coefficient is what you designed the regression to estimate — interpret that one. The country coefficient is a control variable doing its job: soaking up country-related variance so the treatment estimate is cleaner. That is all it is.

Reporting "country has a big causal effect on conversion" based on this coefficient is the Table 2 Fallacy. The right statement is: "conversion rates differ significantly by country in this model, but this regression was not designed to identify country's causal effect and the coefficient should not be interpreted as one."
