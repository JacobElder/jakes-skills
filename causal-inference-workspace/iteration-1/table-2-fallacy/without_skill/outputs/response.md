# Does a Large, Significant Country Coefficient Mean Country Has a Big Causal Effect?

**Short answer: Not necessarily — and conflating "statistically significant control variable" with "causal effect" is one of the most common mistakes in applied regression analysis. This mistake even has a name: the Table 2 Fallacy.**

---

## What You Actually Estimated

When you ran your regression, you specified a single model:

```
Conversion ~ Treatment + Age + Country + Browser + TimeOfDay + ε
```

Every coefficient in this model — including the country coefficient — comes out of the same ordinary least squares fit. But here is the critical point: **the model was not designed to give country a causal interpretation.** It was designed to give `Treatment` a causal interpretation, and country was included as a control to soak up confounding variance.

---

## The Table 2 Fallacy

The term "Table 2 Fallacy" was coined by Westreich & Greenland (2013) in epidemiology, but the underlying problem is universal in any field that uses regression for causal inference. The fallacy works like this:

1. A researcher runs a regression with one focal exposure (e.g., a treatment) and several covariates (e.g., age, country, browser).
2. The regression table prints a coefficient and p-value for every variable.
3. The researcher (or reader) interprets the covariate coefficients as if they were also causal effect estimates.

This is wrong for several interconnected reasons.

---

## Why Country's Coefficient Is Not a Causal Effect Estimate

### 1. The Adjustment Set Was Chosen for Treatment, Not for Country

To estimate the causal effect of Treatment on Conversion, you chose controls that block confounding backdoor paths into Treatment. This adjustment set is appropriate for identifying the Treatment effect.

But the causal effect of Country on Conversion requires its own, potentially different, adjustment set. Confounders of the Country → Conversion relationship might include socioeconomic factors, internet infrastructure quality, cultural attitudes toward online purchasing, and currency/payment method availability — some of which may not be in your model at all.

### 2. Controlling for Mediators Biases Causal Estimates

Suppose "Browser" is partly a consequence of country (Safari is more common in wealthy countries that also buy Apple products). When you control for Browser, you absorb some of the variation in Conversion that flows through the pathway:

```
Country → Browser → Conversion
```

This makes the country coefficient an estimate of the **direct** effect of country net of browser, not the **total** effect. Depending on your research question, neither may be what you want.

### 3. Collider Bias Can Be Introduced

If one of your other controls is a common effect of both Country and Conversion (a "collider"), controlling for it opens a spurious backdoor path, making country's coefficient larger, smaller, or even the wrong sign relative to the truth.

### 4. Measurement and Aggregation Issues

"Country" is a highly aggregated variable. Its coefficient absorbs all between-country variation unexplained by other controls. This reflects unmeasured confounders (GDP, regulatory environment, brand awareness), structural funnel differences, and selection into the sample — none of which constitute "the causal effect of being from Country X."

---

## What the Country Coefficient Does Tell You

The country coefficient is a valid **descriptive/predictive** statement, conditional on your model:

> "After adjusting for age, browser, and time-of-day, users from Country X convert at a rate Y percentage points higher than the reference country, on average in this dataset."

This is useful for prediction, prioritization, and diagnostic checks on randomization balance. It is not valid for inferring that country causally drives conversion or designing interventions based on the coefficient alone.

---

## The Broader Lesson: Different Causal Questions Require Different Models

A single regression model cannot simultaneously be optimally specified for all of its variables' causal interpretations. Each causal question requires:

1. A separate causal diagram (DAG) articulating the assumed data-generating process
2. An adjustment set derived from that diagram for that specific exposure
3. Verification that chosen controls do not introduce bias for that exposure

When you run one regression and read off every coefficient as a causal effect, you are implicitly assuming the same adjustment set is valid for every variable simultaneously. This is almost never true.

---

## Practical Guidance

| Goal | What to Do |
|---|---|
| Estimate causal effect of Treatment | Your current model is fine (assuming valid randomization/design) |
| Estimate causal effect of Country | Draw a new DAG with Country as the exposure; derive the correct adjustment set; fit a separate model |
| Predict conversion for a new user | Your current model's coefficients are fine to use — no causality claim needed |
| Understand what drives country differences | Descriptive analysis, qualitative research, or a properly specified causal model for country |

---

## Key Takeaway

A large, statistically significant country coefficient means country is a strong **predictor** of conversion, conditional on your other controls. It does not mean country has a large causal effect on conversion. The model was specified to identify the causal effect of treatment, and the adjustment set that serves that goal does not automatically serve the goal of identifying country's causal effect. Interpreting every coefficient in a regression table as a causal effect estimate — the Table 2 Fallacy — is a common but serious analytical error.
