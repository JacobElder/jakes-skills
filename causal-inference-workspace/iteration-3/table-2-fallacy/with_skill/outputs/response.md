# Does the Country Coefficient Mean Country Has a Big Causal Effect?

No. What you are describing is a textbook instance of the **Table 2 Fallacy**. The short answer: the country coefficient tells you about model fit, not about the causal effect of country on conversion.

---

## 1. Name the rung

Your actual question — "what is the treatment's causal effect on conversion?" — is a **Rung 2 (intervention)** question. You want to know what would happen if you applied the treatment, not just what is correlated with conversion.

The secondary question — "does country have a big causal effect on conversion?" — is also Rung 2. And it is the one that leads people astray here.

---

## 2. The Table 2 Fallacy

When you fit a regression of the form:

```
conversion ~ treatment + age + country + browser + time_of_day
```

you have one **focal coefficient** (treatment) and several **control coefficients** (country, age, etc.). The controls were included for one purpose: to satisfy the back-door criterion for the treatment effect. They work as adjustment variables for `treatment → conversion`.

But that is all they do. The coefficient on country does **not** estimate the causal effect of country on conversion. Even if country is a valid confounder to control for (a good choice structurally), its coefficient in this regression is:

- Identified only if *all direct causes of conversion* are in the model — a condition that almost never holds.
- Describing the conditional association of country with conversion *after partialing out treatment, age, browser, and time-of-day* — which is a model-fit quantity, not a causal quantity.

Westreich and Greenland (2013) named this the Table 2 Fallacy: in a typical regression paper, Table 1 reports descriptive statistics and Table 2 reports the regression coefficients. Analysts routinely interpret every row of Table 2 causally. Only the focal row deserves that interpretation.

Hünermund and Louw (2024) showed something even sharper: a control variable's coefficient can vary wildly across *different valid adjustment sets* even when the focal coefficient is stable across all of them. The control coefficient is not converging on a causal truth — it is a model artifact.

---

## 3. Sketch the DAG and what it implies

A plausible DAG for this setup:

```
country ─────────────────────────────► conversion
   │                                       ▲
   └──► user_characteristics               │
                                           │
age ──────────────────────────────────────►|
browser ──────────────────────────────────►|
time_of_day ──────────────────────────────►|
                                           │
treatment ────────────────────────────────►|
   ▲
   │
country (also affects who gets treated, if non-randomized)
```

If the treatment was randomized (a clean A/B test), then country is a valid control because it may predict conversion strongly, and including it improves precision. In that case, the treatment coefficient is cleanly identified.

But the country coefficient in this model is answering a *different* question than "what is the causal effect of country on conversion?" It is answering: "holding treatment, age, browser, and time-of-day constant, what is the association of country with conversion?" That conditioning set was chosen to identify *treatment*, not to identify *country*. To identify country's causal effect on conversion, you would need to close all back-door paths into country — a completely different adjustment set.

---

## 4. Why does this matter practically?

A large, significant country coefficient is consistent with many explanations:

- **Country is a genuine confounder** (common cause of treatment assignment and conversion) and the coefficient reflects a mix of its causal effect plus whatever confounding is present from unmeasured variables that vary by country.
- **Country is a proxy** for several unmeasured factors (infrastructure, culture, purchasing power, language, device quality) — its coefficient absorbs all of those, making it large but uninterpretable causally.
- **Country correlates with other included controls** — multicollinearity inflates standard errors but does not make the coefficient causally interpretable.
- **Selection effects** — if different countries have different opt-in rates, the country coefficient partly reflects who ends up in the sample.

In every case, "country has a big significant coefficient" means country is doing work in the model. It does not mean "if we could change users' country, conversion would change by that amount."

---

## 5. What you would need to estimate country's causal effect

To get a defensible causal estimate for country → conversion, you would need:

1. **A separate causal model for country as the focal variable.** Draw the DAG with country as X and conversion as Y. Find the back-door paths into country (geography is not randomized; it is determined by a thicket of historical, demographic, and economic factors). Almost none of those confounders are measured in a typical product dataset.

2. **A valid adjustment set for *that* question.** The controls you chose for treatment identification are not the right set for country identification. In fact, some of them (treatment itself, browser, time-of-day) could be mediators or descendants of country — controlling for them would *block* part of the country → conversion path.

3. **Probably a design-based approach.** Country is not randomizable. For plausibly causal country effects, the standard tools are: difference-in-differences around a policy change that varied by country, a regression discontinuity at a geographic border, or an instrumental variable.

---

## 6. The concrete takeaway

| Coefficient | Causal interpretation valid? | Why |
|-------------|------------------------------|-----|
| Treatment | Yes (if the A/B test was clean) | The regression was set up to identify this |
| Country | No | Identified only as a conditional association, adjustment set was chosen for treatment, not country |
| Age, browser, time-of-day | No | Same reason as country |

The country coefficient is **large and significant because country is a strong predictor of conversion** (and probably a confounder for treatment, which is why you included it). That says nothing about causation. If someone asks "should we launch in country X to lift conversion?", this coefficient cannot answer that question. It is a model-fit term, not an intervention estimate.

---

## References

- Westreich, D., & Greenland, S. (2013). *The Table 2 Fallacy: Presenting and Interpreting Confounder and Modifier Coefficients.* American Journal of Epidemiology 177(4).
- Hünermund, P., & Louw, B. (2024). *On the Nuisance of Control Variables in Causal Regression Analysis.* Organizational Research Methods 28(1).
- Cinelli, C., Forney, A., & Pearl, J. (2022). *A Crash Course in Good and Bad Controls.* Sociological Methods & Research.
