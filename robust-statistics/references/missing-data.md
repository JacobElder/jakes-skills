# Missing Data

Missing data are nearly universal in applied research. The decision about how to handle them hinges on **why the data are missing**, not merely on how much is missing.

## Contents
- MCAR / MAR / MNAR: Rubin's taxonomy
- Complete-case analysis: when it works and when it doesn't
- Single and mean imputation: the variance understatement trap
- Multiple imputation and FIML under MAR
- MNAR: no data-only fix
- Outcome missingness vs predictor missingness

---

## MCAR / MAR / MNAR: Rubin's taxonomy

*(Rubin, 1976)*

The standard taxonomy classifies the **missingness mechanism** — what determines whether a value is observed or missing:

**MCAR — Missing Completely At Random.** The probability of missingness is unrelated to both observed and unobserved data. Missing values are a simple random subsample of the data. This is the strongest (and most convenient) assumption.

**MAR — Missing At Random.** Missingness depends on observed variables but, *conditional on those observed variables*, is unrelated to the unobserved value itself. "At random" is misleading — it does not mean random; it means the missingness is explainable by what you can see. Example: younger respondents skip the income question more often, but among people of the same age, skipping is unrelated to their actual income. MAR is **not fully testable from the observed data alone** — you cannot observe the missing values to check whether they differ from a MAR prediction.

**MNAR — Missing Not At Random.** Missingness depends on the unobserved value itself, even after conditioning on all observed covariates. High earners may be especially likely to skip the income question *because* their income is high. Like MAR, MNAR is also **not testable from observed data alone** — MAR and MNAR are observationally indistinguishable in the data you have.

The practical consequence: you cannot prove the mechanism is MAR or MCAR from the data. You argue for it from substantive knowledge and prior information, and you assess sensitivity to violations.

---

## Complete-case analysis: when it works and when it doesn't

Complete-case analysis (listwise deletion) drops any row with a missing value and analyzes only the complete rows. This is the default in most software and it is frequently used without justification.

**When it gives unbiased estimates:**
- **MCAR**: dropping incomplete rows is equivalent to a random subsample — unbiased, but inefficient (standard errors are wider because information is discarded).
- **MAR with outcome missingness in a regression**: if the *outcome* is missing and missingness depends only on covariates that are *included in the model* (not on the outcome itself, conditional on those covariates), complete-case analysis yields unbiased regression coefficient estimates. This is an important and commonly underappreciated subtlety: the condition is that the missingness mechanism is a function only of the model's predictors, not of the outcome given those predictors.

**When it is biased:**
- **MNAR**: complete cases are a selected subsample that systematically differs on the outcome. No adjustment within the observed data corrects this selection.
- **MAR where missingness depends on the outcome given covariates**: if people who fare poorly drop out and that dropout is related to the unobserved outcome (not just the observed predictors), complete-case estimates are biased.
- **Large missingness fractions**: even under MCAR, discarding a substantial fraction of the sample (say, >10–15%) inflates standard errors and may jeopardize study power.

---

## Single and mean imputation: the variance understatement trap

Replacing missing values with a single value — the mean, a regression-predicted value, or any point estimate — treats the imputed values **as if they were known**, which they are not.

**Consequences:**
- **Understated variance**: downstream analyses treat imputed values as observed data, reducing spread artificially. Confidence intervals are too narrow; standard errors are too small; p-values are too optimistic.
- **Correlation attenuation**: mean imputation in particular shrinks the variance of the imputed variable (adding values at the mean adds no spread), attenuating correlations involving that variable.

Single imputation may be tolerable for MCAR data with small missingness fractions in exploratory contexts, but should not be used for final inferential results where standard errors matter.

---

## Multiple imputation and FIML under MAR

Under MAR, two principled approaches exist that properly propagate missing-data uncertainty:

**Multiple imputation (MI).** Generate *m* plausible complete datasets by drawing from the predictive distribution of the missing data given the observed data and model. Analyze each dataset separately with the intended analysis. Combine the *m* results using **Rubin's rules**: the parameter estimate is the mean across the *m* analyses; the variance is the within-imputation variance plus a between-imputation term that captures imputation uncertainty. This between-imputation term is what single imputation discards — it can be substantial when missingness is high or the imputation model is uncertain.

Practical notes: the imputation model should include all variables in the analysis model plus auxiliary variables that predict missingness or the missing values themselves. Excluding important predictors from the imputation model can introduce bias even under MAR. Standard implementations: `mice` (R), `statsmodels`/`IterativeImputer` (Python).

**Full information maximum likelihood (FIML).** Rather than imputing, FIML uses all observed data for each case in a likelihood framework, integrating over the missing values. It is asymptotically equivalent to MI under MAR and is especially natural for structural equation models and repeated-measures designs. It is not available in all modeling contexts because it requires a likelihood to integrate over.

Both MI and FIML are valid **under MAR** — they do not handle MNAR.

---

## MNAR: no data-only fix

When the missingness mechanism is MNAR, neither MI nor FIML nor any other method "fixes" the problem from the data alone. The missing values are systematically different from the observed values in ways that cannot be estimated from what you see.

**What you can do:**
- **Sensitivity analysis.** Vary the assumed relationship between missingness and the missing value (e.g., pattern-mixture models; the delta-adjustment / tipping-point approach). Report how large the MNAR departure would have to be to change your substantive conclusions.
- **Explicit MNAR models.** Selection models (Heckman-style) or pattern-mixture models can model the missingness mechanism, but they require strong untestable assumptions about the *form* of the MNAR process and are sensitive to those assumptions.
- **Worst-case / bounds analysis.** Fill in missing values with the most adverse plausible values (e.g. treatment failures for missing outcomes in a trial) and report the range of estimates across plausible extreme scenarios.

The honest position: if the mechanism is MNAR, results carry a large asterisk and require a sensitivity analysis, not a claim of unbiasedness.

---

## Outcome missingness vs predictor missingness

The two cases behave differently and are worth keeping straight:

**Missing outcome.** This is where the missingness mechanism matters most for unbiasedness of the main estimand. MNAR outcome missingness means all available-case or imputation-based estimates may be biased. Complete-case analysis can be unbiased under MCAR, or under MAR where missingness is determined only by observed predictors in the model (see above). Multiple imputation is preferred when outcome missingness is substantial and covariates that explain missingness are available.

**Missing predictors.** Complete-case analysis is unbiased under MCAR, but when predictors are missing under MAR the condition for validity differs. If a predictor's missingness depends on the outcome (even given other covariates), the complete-case estimate of the predictor's coefficient is biased. Multiple imputation is generally preferable to complete-case when predictors are missing at even moderate rates, because it uses all available information to fill in the predictor.

**Practical checklist:**
1. How much is missing, and on which variables?
2. What substantive reason do you have to believe the mechanism is MCAR / MAR / MNAR?
3. Do completers and non-completers differ on observed auxiliaries? (Suggests departure from MCAR)
4. Is the goal inference on regression coefficients, or on means/proportions? (The valid-mechanism conditions differ)
5. If MAR is plausible: use MI or FIML. If MNAR is possible: run a sensitivity analysis regardless of the main method.
