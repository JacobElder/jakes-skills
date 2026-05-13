# Does the Country Coefficient Have a Causal Interpretation?

**Short answer:** No. You have run into the **Table 2 Fallacy**. The coefficient on country is not a causal estimate, even if the treatment coefficient is.

---

## 1. Name the Rung

Your core question — "does X cause Y?" — is a **Rung 2 (intervention)** question. You want to know what would happen if you *changed* country membership for a user, not merely what is associated with conversion in your data. Rung-2 questions cannot be answered with Rung-1 tools (regression, correlation) without additional causal assumptions encoded in a DAG.

---

## 2. The Named Trap: The Table 2 Fallacy

When you fit:

```
Conversion ~ Treatment + Age + Country + Browser + TimeOfDay
```

you are running this regression to identify one focal effect: **Treatment → Conversion**. Your controls (age, country, browser, time-of-day) are included to block back-door paths from Treatment to Conversion — that is, to remove confounding from the treatment coefficient.

That is *all* those controls are doing in this regression, structurally speaking.

The **Table 2 Fallacy** (Westreich & Greenland, 2013) is the mistake of reading off every coefficient in such a regression as though each one is a clean causal estimate of that variable's effect on the outcome. It is not. The regression was optimized to identify **one** causal quantity (the treatment effect). It was not designed to identify the causal effect of country, or age, or browser.

---

## 3. Why the Country Coefficient Is Not a Causal Estimate

For the country coefficient to be interpreted as "the causal effect of country on conversion," the regression would need to satisfy an entirely different, much stronger identification condition: every **direct cause of Conversion** would need to be in the model, no back-door paths from Country to Conversion could remain open, and no colliders on paths between Country and Conversion could be inadvertently conditioned upon. That is an "all-causes regression" — a far stricter criterion that your model almost certainly does not meet.

Here is why in DAG terms. Think about what the DAG for "Country → Conversion" might look like:

```
Country ← U1 (cultural norms, economic environment, market maturity)
              ↓
           Conversion

Country → Conversion  (direct)

Country → Browser → Conversion   (partial mediation: country determines browser market share)
Country → TimeOfDay               (time zones)
```

Several problems arise immediately:

- **Unmeasured confounders.** Country is likely confounded by macro-level variables (local economy, cultural attitudes toward online purchases, competition, localization quality) that are not in your regression. Without blocking those back-doors, the country coefficient picks up all of them.

- **Mediation.** Country probably causes some of your other controls — it affects which browser users have, which time zone they are in, even age distributions of the user base. If Browser and TimeOfDay are mediators of Country → Conversion, conditioning on them *blocks* part of country's effect, making the country coefficient estimate only the *residual direct* effect of country after stripping out those channels. That is not the total causal effect of country.

- **The coefficient is adjustment-set-dependent.** Hünermund & Louw (2024) showed that a control variable's own coefficient can vary wildly across different valid adjustment sets for the focal treatment effect, even when the focal treatment coefficient is stable across all of them. In other words: you could include a different but equally valid set of controls for Treatment and get a very different country coefficient. The country coefficient has no fixed causal meaning; it is a residual partial correlation given the other variables in this particular model.

To put it simply: the controls were chosen to identify Treatment → Conversion. They were not chosen to identify Country → Conversion. Those are two different estimation problems requiring two different identification strategies.

---

## 4. What "Huge and Significant" Actually Means Here

A large, significant country coefficient tells you:

> After adjusting for treatment assignment, age, browser, and time-of-day, country is strongly associated with conversion in this sample.

That is a Rung-1 (associational) statement. It is useful for prediction. It is not a causal claim. The coefficient could be large because:

- Country genuinely causes conversion (causal signal)
- Country is correlated with unmeasured confounders that cause conversion (spurious signal)
- Country partially mediates through browser/time-of-day, and those paths are now partially blocked (underestimate of total effect)
- Some combination of all three

You cannot disentangle these from this regression alone.

---

## 5. What Would Be Required for a Causal Interpretation of the Country Coefficient

To estimate the causal effect of Country → Conversion, you would need to:

1. **Draw a DAG specifically for Country → Conversion** — not for Treatment → Conversion. These are different estimands with different valid adjustment sets.

2. **Block all back-door paths from Country to Conversion** in that Country-specific DAG. This means identifying and measuring (or proxying) variables like economic indicators, localization quality, market maturity, and any other common causes of both country assignment and conversion that are not already in the model.

3. **Not condition on mediators** of Country → Conversion (e.g., Browser, TimeOfDay) unless you specifically want the direct effect of country holding those channels fixed.

4. **Acknowledge that country is not randomly assigned.** Users are not randomized to countries. Country is a product of geography, demographics, and self-selection. Any causal interpretation requires credible assumptions about what drives country membership relative to conversion — assumptions that are very hard to defend without a natural experiment or quasi-experimental design.

Realistically, clean causal identification of a "country effect" on conversion would require something like:
- A natural experiment where users were plausibly quasi-randomly assigned to market conditions (e.g., an expansion rolled out in random order across countries)
- An instrumental variable that shifts country-level exposure but has no direct effect on conversion
- A differences-in-differences design if some exogenous policy changed conditions in some countries but not others

---

## 6. Summary

| Question | Answer |
|---|---|
| Is the treatment coefficient a causal estimate? | Potentially yes, if controls were chosen to block treatment's back-doors |
| Is the country coefficient a causal estimate? | No — Table 2 Fallacy |
| What does the country coefficient represent? | A partial association in this model, not an identified causal effect |
| What would we need for a causal country effect? | A separate DAG, additional confounders, and likely a quasi-experimental design |

The treatment coefficient is the one you set the regression up to identify. Every other coefficient in the table is describing model fit, not causal effects. That country's coefficient is large and significant is interesting and worth investigating — but it warrants its own causal analysis, not a reading off the same regression table.
