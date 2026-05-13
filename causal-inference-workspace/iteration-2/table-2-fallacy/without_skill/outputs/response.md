# Does a Large, Significant Country Coefficient Mean Country Has a Big Causal Effect?

## Short answer: No — not necessarily.

This is a classic instance of what methodologists sometimes call the **"Table 2 fallacy"**: the mistake of reading causal interpretations off every coefficient in a regression table, when only the coefficient you designed the study to estimate has that interpretation.

---

## What your regression is actually doing

You ran something like:

```
Conversion = β₀ + β_treatment * Treatment + β_age * Age + β_country * Country + β_browser * Browser + β_tod * Time-of-Day + ε
```

Your causal target is β_treatment. To isolate that effect cleanly, you included country (and the other variables) as **controls** — variables you adjust for because they affect conversion and may be correlated with treatment assignment.

---

## Why β_country does not have a clean causal interpretation

### 1. Controls serve a different statistical role than the treatment variable

The treatment variable was (presumably) randomized or designed to have exogenous variation. The control variables were not. They are included to reduce omitted variable bias on the treatment coefficient, not to estimate their own causal effects.

### 2. Controls are not "controlled experiments"

To estimate the causal effect of country, you would need an experiment or natural experiment where country assignment is as-good-as-random — or a very careful observational design (instrumental variables, difference-in-differences, etc.) specifically aimed at country. You have none of that here. Country is almost certainly correlated with dozens of unmeasured confounders: income, language, culture, marketing spend by region, device ecosystem, local competition, and so on.

### 3. The coefficient absorbs confounding

When you control for country, the country coefficient picks up all the stable between-country variation in conversion — which is a mixture of the true causal effect of country plus every omitted country-level factor. There is no way to separate these from a single cross-sectional regression.

### 4. Multicollinearity and specification sensitivity

Control variable coefficients tend to be much more sensitive to model specification than the coefficient of interest. Add or remove one other control, and β_country may change substantially. That is a sign you are not in a regime where that coefficient is identified.

---

## A concrete intuition

Imagine users from Country A convert at 60% and users from Country B convert at 20%. The country coefficient will be large and significant. But this could be entirely explained by:
- Country A having higher average incomes (real purchasing power effect)
- Country A receiving better-targeted ads before they arrive on the site
- Country A being a market you entered later, when the product was more mature
- Any combination of the above

The regression has no way to disentangle these. It just fits a number.

---

## What this means for your analysis

| Coefficient | Your design supports a causal claim? | Why |
|---|---|---|
| β_treatment | Yes (if randomization was valid) | Treatment was exogenously assigned |
| β_country | No | Country was not randomized; confounders abound |
| β_age, β_browser, β_tod | No | Same reason as country |

**The controls are doing their job** — they are helping β_treatment be unbiased — but they are not themselves unbiased estimates of causal effects. This is not a bug; it is how regression adjustment is supposed to work.

---

## If you genuinely want the causal effect of country

You would need a separate identification strategy:
- **Randomized experiment**: randomly show users content as if they were in a different country (hard/impractical)
- **Instrumental variables**: find something that shifts country-level conversion rates but has no direct effect on individual conversion
- **Difference-in-differences**: exploit a country-level policy change over time
- **Regression discontinuity**: exploit a sharp geographic or regulatory boundary

Without one of these, the country coefficient is a descriptive association, not a causal effect.

---

## Summary

A large, significant country coefficient means country is **predictive** of conversion after conditioning on your other controls. It does not mean country **causes** that difference. The Table 2 fallacy is the error of treating every coefficient in a well-specified regression as if it carries the same causal weight as the coefficient you designed the study to identify. Only your treatment coefficient has a defensible causal story here.
