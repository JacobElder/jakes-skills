# Does a Large, Significant Country Coefficient Mean Country Has a Big Causal Effect on Conversion?

**Short answer: Not necessarily — and conflating statistical significance in a control variable with causal interpretation is a very common mistake.**

---

## What Your Regression Is Actually Doing

You ran something like:

```
Conversion = β₀ + β_treatment × Treatment + β_country × Country + β_age × Age + β_browser × Browser + β_tod × TimeOfDay + ε
```

The goal was to estimate β_treatment cleanly. Country, age, browser, and time-of-day were included as **controls** — variables you added to soak up variance or reduce omitted variable bias in the treatment estimate, not because you wanted causal estimates of *their* effects.

---

## Why the Country Coefficient Doesn't Straightforwardly Mean "Country Causes Conversion"

### 1. Controls Are Not the Focus of the Identification Strategy

Your experiment (or quasi-experiment) was designed to identify the causal effect of *treatment*, not of country. The identifying assumptions — randomization, as-good-as-random assignment, an instrument, etc. — apply to treatment. Country was never randomized and has no analogous identification strategy in this regression. Its coefficient is just an OLS partial correlation, conditioned on whatever else is in the model.

### 2. Country Is Almost Certainly Correlated With Dozens of Omitted Variables

Country absorbs an enormous bundle of things: purchasing power, language, cultural attitudes toward online shopping, local competition, payment infrastructure, device quality, internet speed, baseline brand awareness, and more. Many of these are unmeasured. That means the country coefficient has substantial omitted variable bias — it is picking up the influence of all those confounders. "Country has a big coefficient" really means "the cluster of things correlated with country explains a lot of variance in conversion." That is very different from a causal claim.

### 3. The Table 2 Fallacy

This situation has a name in the epidemiology and econometrics literature: the **Table 2 Fallacy** (Westreich & Greenland, 2013). In many research papers, Table 1 shows descriptive statistics and Table 2 shows the regression with every coefficient reported. Readers (and sometimes authors) mistake the coefficients on control variables for causal estimates. They are not. Each coefficient in a multivariable regression answers the question "what is the partial association of this variable with the outcome, holding all other included variables fixed?" — but that partial association is only causally interpretable if the identification conditions for *that specific variable* are satisfied. For treatment, you presumably satisfied those conditions. For country, you almost certainly did not.

### 4. Multicollinearity and Coefficient Instability

Country likely correlates with your other controls (age distributions differ by country, browser usage differs by country, time-of-day patterns differ by country). This means the country coefficient is sensitive to what else is in the model. Add or remove one control and the country coefficient can shift dramatically. A causally meaningful estimate should not behave that way.

### 5. What "Significant" Means Here

Statistical significance (low p-value) tells you the signal is large relative to noise *in this sample and model*. It says nothing about whether the association is causal. A spurious correlation can be highly significant. Country has many observations per level and large between-country variation in conversion, so of course the standard error is small and the t-statistic is large. That is a sample-size and variance story, not a causal story.

---

## What the Country Coefficient *Is* Useful For

- **Improving your treatment estimate**: By controlling for country, you reduce residual variance and remove a potential confounder from the treatment coefficient. That is its legitimate job here.
- **Prediction**: If you wanted to build a model that predicts conversion for a new visitor, a large country coefficient is useful signal.
- **Descriptive insight**: "Users from Country X convert at a higher rate than Country Y, conditional on these other observables" is a valid descriptive finding — just not a causal one.

---

## What You Would Need to Make a Causal Claim About Country

To claim country *causes* higher conversion, you would need:

1. **Exogenous variation in country** — e.g., a natural experiment where users were quasi-randomly assigned to experience the site as if they were from a different country (like a geo-targeting glitch or a randomized locale experiment).
2. **A credible identification strategy** — an instrument for country, a regression discontinuity at a border, or a difference-in-differences design exploiting a country-specific policy change.
3. **A theory of the mechanism** — what specifically about being in Country X causes conversion? Without a mechanism, even a clean estimate is hard to interpret.

---

## Summary

| Question | Answer |
|---|---|
| Is the treatment coefficient a causal estimate? | Yes, if your identification strategy is valid |
| Is the country coefficient a causal estimate? | No — it's a partial correlation with omitted variable bias |
| Does a large, significant country coefficient mean country causes conversion? | No — it means country (and the bundle of things it proxies) is strongly *associated* with conversion |
| Should you report the country coefficient as a finding? | Only as a descriptive association, with explicit caveats |

The bottom line: focus on β_treatment, which is what your design identified. The country coefficient is doing its job as a control variable — it is not a result you should interpret causally.
