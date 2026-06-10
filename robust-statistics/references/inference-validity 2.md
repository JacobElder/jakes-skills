# Inference Validity: Threats Beyond Distributional Assumptions

Four pathologies that corrupt inference even when the distributional model is correct. Each is about the interpretation of p-values and confidence intervals — not about whether residuals are normal or whether counts are overdispersed.

## Contents
- "A difference in significance is not a significant difference"
- Type M and Type S errors: the significance filter under low power
- The Table 2 fallacy
- Post-selection inference and the garden of forking paths

---

## "A difference in significance is not a significant difference"

*(Gelman & Stern, 2006)*

Observing that one effect is statistically significant while another is not is **not** evidence that the two effects differ. This comparison is made constantly — "the drug worked in men (p = 0.03) but not in women (p = 0.15), so the effect differs by sex" — and is almost always invalid as stated.

Why it fails: two estimates can each be individually "significant vs not" while their *difference* is nowhere near significant, and conversely two estimates can each be individually non-significant while their difference is highly significant. The significance thresholds for the individual tests are not designed to serve as a test of equality between them.

**The correct move: test the difference directly.**
- In a regression: add an **interaction term** (treatment × group) and test its coefficient.
- In a two-estimate comparison: form the contrast directly and compute its SE — under independence, SE(β̂₁ − β̂₂) = √(SE₁² + SE₂²) — then test or compute a CI for the difference.
- In a mixed model: the group-by-condition interaction is the formal test.

**Magnitude check.** It often helps to display the two point estimates with their confidence intervals side by side. Substantial CI overlap casts doubt on any claim that the effects differ.

**What this failure mode looks like in practice:**
- "The intervention improved outcomes in the high-risk group (p = 0.04) but not the low-risk group (p = 0.09) — targeted delivery is vindicated."
- "The effect held in men (β = 0.42, p = 0.03) but not women (β = 0.31, p = 0.12)."
- "The correlation was significant in Year 1 but not Year 2."

In each case, the correct question is: is the interaction or difference between the estimates itself significant? That may well be no.

---

## Type M and Type S errors: the significance filter under low power

*(Gelman & Carlin, 2014)*

When a study is underpowered and uses a significance threshold to decide whether to report an effect, the estimates that pass the filter are **not a representative sample** of the true effect — they are drawn from the tails of the sampling distribution. Two systematic distortions follow.

**Type M error (magnitude / exaggeration ratio).** Significant estimates from underpowered studies overstate the true effect size. The exaggeration ratio is E[|β̂| | |β̂| > crit] / |β_true|. For a study with 25% power testing a real effect of d = 0.3, the exaggerated estimate that clears the threshold will typically be 2–4× the true effect. The smaller the power, the larger the exaggeration.

**Type S error (sign / direction).** Under low power, a non-trivial fraction of significant estimates will be **the wrong sign**. For studies near the power floor (say, 15–20%), Type S rates can reach 5–20%.

**The winner's curse.** A "large, significant effect from a small study" is not reassuring; it is the expected output of a significance filter applied to a noisy, underpowered experiment. The observed effect size is almost certainly overstated — sometimes massively. The correct interpretation: the data are consistent with a *range* of effect sizes, and the significant point estimate should not be taken at face value.

**Practical implications:**
- "Large + significant + small n" is a red flag, not validation. Ask: what was the a-priori power and what would the minimum-detectable effect have been?
- Replication failures are predictable: a first underpowered study finds a large, significant exaggerated effect; the replication (at only adequate power) finds a smaller, non-significant one. The first study didn't lie — it was the winner of a noisy contest.
- Meta-analyses weighting by precision partially correct the exaggeration; naive vote-counting ("how many studies replicated?") does not.

**Connection to Type I errors and multiple testing.** Type M and S are not about Type I errors (false positives when the null is true); they are about distortions *conditional on the null being false but power being low*. Both problems coexist with nominal Type I error control.

---

## The Table 2 fallacy

*(Westreich & Greenland, 2013)*

In a multivariable regression fit to estimate the effect of one focal exposure, the coefficients on the other covariates (control variables, confounders) are **not** each interpretable as the total causal effect of that variable on the outcome.

**Why not:**

1. **Different confounding structures.** The model was built to adjust for confounders of the main exposure. Those particular confounders are not necessarily the right adjustment set for estimating each covariate's own causal effect. For any given covariate, the other model terms might be its confounders, mediators, or colliders — and conditioning on mediators or colliders biases estimation of that covariate's effect.

2. **Mediator conditioning.** If one covariate mediates part of the main exposure's effect, the main model may or may not condition on it. Either way, the coefficient on that covariate (and on the main exposure) reflects a partial-effect estimand that is not the total causal effect of either variable.

3. **Conditional, not total, effects.** Each coefficient is "the effect of this variable holding all others constant." For most policy or scientific questions, the relevant quantity is the total (marginal) effect, which is not what a conditional multivariable coefficient delivers.

**What Table 2 looks like in practice.** A paper fits a logistic regression for stroke with the main exposure being hypertension, controlling for age, sex, smoking, and diabetes. Table 2 reports coefficients for all five variables and labels them "effects." The hypertension OR was the target of deliberate design and adjustment; the "effects" of age, sex, smoking, and diabetes in that same model were not — each is subject to its own confounding structure that the model was not designed to handle.

**The fix:** Report and interpret only the pre-specified estimand (the main exposure). If multiple exposures are of substantive interest, each deserves its own identification analysis with its own adjustment set determined by the causal structure for *that* exposure. Alternatively, be transparent that the reported associations are descriptive conditional associations in the presence of the other model terms, not causal-effect claims.

---

## Post-selection inference and the garden of forking paths

*(Gelman & Loken, 2014; Berk et al., 2013)*

Selecting a model or variable set from the data and then reporting CIs and p-values from that selected model as if the model were pre-specified is **anti-conservative**: the nominal error rates are wrong and the true Type I error rate is much higher than advertised.

**Why the problem exists.** A p-value or CI is calibrated under the assumption that the analysis was fully determined before seeing the data. Stepwise variable selection, AIC/BIC model selection, covariate selection based on observed correlations with the outcome — all constitute a search through model space that consumes degrees of freedom the final analysis pretends it had. The selected model is better than average at producing small p-values *by construction*.

**This is the pretest-bias problem generalized.** The skill already identifies that pretesting an assumption and then choosing a procedure based on the test result distorts the final inference. Post-selection inference is the same pathology applied to model selection: a statistical procedure is used to choose the analysis, and the final inference ignores that choice.

**The garden of forking paths** (Gelman & Loken). Even without explicit multiple testing, an analyst who makes flexible choices — about outlier handling, transformations, which covariates to include, how to aggregate a scale, which time window to use — arrives at a "final" model via an implicit search. The p-value from the chosen model does not reflect the probability of observing a result as extreme *under all the models the analyst implicitly considered*. The implicit multiplicity inflates false positives even when no single test is run multiple times.

**Mitigations:**
- **Pre-registration.** Commit to the analysis plan (variables, model form, exclusion criteria) before seeing the data or outcomes.
- **Sample splitting.** Use one subset for exploration/selection and a held-out subset for confirmatory inference on the selected model. The held-out p-values are valid because the selection did not use those data.
- **Selective inference methods.** Conditional on the selected model, adjusted inference (e.g. PoSI bounds, the knockoff filter, data-splitting methods) maintains correct operating characteristics.
- **Honest labeling.** Exploratory results should be labeled as exploratory. Do not present a data-driven analysis as pre-specified confirmatory inference.

**Stepwise regression in particular** combines several problems: the model-based p-values in the final model are not valid (selection effect), the standard errors assume fixed predictors (not a search), and the model often does not generalize (overfits the search). Using final-model p-values from stepwise selection for inference is not defensible — treat results as hypotheses to be tested on new data.

---

## Multiple comparisons: when correction is and isn't required

Multiple comparisons corrections are widely mandated but widely misunderstood. The correct question is not "did you run more than one test?" but "what error rate are you trying to control, and is that the right criterion here?"

**Family-wise error rate (FWER).** FWER is the probability of at least one false positive across a family of tests. With k independent tests at α = .05, FWER ≈ 1 − .95^k. Bonferroni controls FWER by testing each hypothesis at α/k — simple and exact under independence, slightly conservative under positive correlation (the Holm–Bonferroni step-down procedure is uniformly more powerful than Bonferroni and should be preferred: it applies α/k to the most significant, then α/(k−1) to the next, stopping at first non-rejection).

**When FWER control is appropriate.** The logical structure matters:
- *OR logic* (any significant outcome declares success): unadjusted FWER is ~ 1 − (1−α)^k and is a real problem.
- *AND logic* (all outcomes must be significant for a claim): no correction is needed — the conjunction is automatically more conservative than a single test.
- *Pre-specified confirmatory outcomes* in a clinical trial: regulatory bodies typically require FWER control because a single false positive triggers approval.
- *Post-hoc or exploratory tests*: Bonferroni is the wrong frame; FDR control or honest exploratory labeling is more appropriate.

**False discovery rate (FDR).** When the goal is to identify a list of interesting findings (genomics, neuroimaging, social science with many predictors), FWER is too strict — it keeps the false-positive count near zero at the cost of missing most true positives. The Benjamini–Hochberg (BH) procedure controls FDR: the expected proportion of false positives among declared significant results. BH is appropriate when you can tolerate some false positives if most declared findings are true.

**Pre-specified outcomes — the nuance reviewers miss.** Pre-specifying a small number of primary outcomes does not eliminate multiplicity — it just makes the family well-defined. For three pre-specified primary outcomes, multiplicity control is a judgment call:
- If the trial claims success on *any* significant primary outcome, FWER control is needed.
- If the three outcomes are independent scientific questions (not a single claim), each can be treated separately.
- Bonferroni at k=3 is conservative (power loss is modest); Holm is strictly better and should be preferred when correction is needed.
- Reviewers who say "you must apply Bonferroni" without engaging with the logical structure and number of outcomes are applying a rote rule, not statistical reasoning.

**The key principle.** Correction protects the false-positive rate in the current study; whether that matters depends on the inferential goal, the logical structure of the claims, and the downstream consequences of a false positive. A blanket "correct all tests" rule and a blanket "pre-specified tests need no correction" rule are both wrong.
