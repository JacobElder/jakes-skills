# Signal Detection Theory Skill

A skill that applies rigorous Signal Detection Theory (SDT) to any task where two classes of events must be told apart — perception, recognition memory, eyewitness identification, medical diagnostics, LLM classifiers, vigilance — and you need to separate **sensitivity** from **response bias**. It gives the agent the conviction to push back on the core mistake that appears in nearly every applied paper: reporting a single accuracy number, hit rate, or diagnosticity ratio and calling it performance. SDT exists because sensitivity and bias are different things that move independently, and collapsing them destroys the analysis before it starts.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/signal-detection-theory
```

Or manually:

```bash
cp -r jakes-skills/signal-detection-theory ~/.claude/skills/signal-detection-theory
```

Once installed, the skill will apply automatically whenever you ask about d-prime (d'), sensitivity vs. bias, criterion, hit rate / false-alarm rate, ROC curves framed as detection problems, meta-d' / M-ratio, recognition-memory old/new designs, or percent-correct that may be conflating accuracy and bias — even casually.

---

## Example use cases

### "Prompt A catches more violations — ship it"

> I'm evaluating an LLM content-moderation classifier on a balanced benchmark (500 violating, 500 benign). Prompt A flags 420/500 violations and 150/500 benign items as violations. Prompt B flags 350/500 violations and 40/500 benign as violations. The PM wants to ship Prompt A because it 'catches more violations.' How should I think about which prompt is the better classifier?

Without the skill, the model reads Prompt A's higher catch rate as superior capability and validates shipping it:

> Prompt A is more effective at catching violations, which is crucial for content moderation where false negatives (missed violations) can have serious consequences. Prompt A catches 84% of violations compared to Prompt B's 70%, which means 70 additional violations would be caught per 1,000 violating items.
>
> For content moderation, the priority is typically catching as many violations as possible (high recall) while keeping the false positive rate manageable... Prompt A appears to be the stronger performer for this use case.

With the skill, the model separates discriminability from criterion and inverts the conclusion:

> The PM's reasoning conflates two very different things: how *liberal* a prompt is and how *discriminating* it is. This is exactly the sensitivity/bias decomposition that SDT is for.
>
> Computing d' for each prompt:
> - **Prompt A:** HR = 0.84, FAR = 0.30 → d' ≈ **1.51**, c ≈ −0.23 (liberal — biased toward flagging)
> - **Prompt B:** HR = 0.70, FAR = 0.08 → d' ≈ **1.92**, c ≈ +0.44 (conservative — biased toward not flagging)
>
> Prompt B is actually the **better discriminator** — it separates violating from benign content more effectively (d' 1.92 vs. 1.51). Prompt A catches more violations because it has a more liberal criterion, not because it has better discrimination. The higher catch rate comes at a cost of nearly 4× as many false flags on benign content (30% vs. 8%).
>
> Shipping Prompt A purely on catch rate is like calling a radiologist "better" because they call everything suspicious — they'll catch more cancer, but the false positive rate is doing the work. The right decision: choose the operating point (criterion) that reflects the actual cost tradeoff between missed violations and false positives, then evaluate which prompt has higher d' (and therefore better ROC) at that operating point.

---

### "AUC = 0.80, so d' = 1.19 — valid conversion?"

> My recognition-memory model gives an ROC AUC of 0.80. I want to report sensitivity as d', so I'll just convert with d' = sqrt(2) * qnorm(0.80) = 1.19 and report that. Is that conversion valid here?

Without the skill, the model accepts the conversion as standard:

> Yes, that conversion is valid. The relationship AUC = Φ(d'/√2) is a well-established identity in SDT, derived from the equal-variance Gaussian model. Converting AUC = 0.80 gives d' = √2 · Φ⁻¹(0.80) = √2 × 0.842 ≈ 1.19. This provides an interpretable effect size for your recognition-memory results...

With the skill, the model flags that the equal-variance assumption is exactly the one that fails for recognition memory:

> The conversion AUC = Φ(d'/√2) holds **only under the equal-variance assumption** — that is, that the signal and noise evidence distributions have identical variance. For recognition memory, that assumption is known to be false.
>
> In old/new recognition, the target/old distribution is reliably *more variable* than the lure/new distribution (z-ROC slopes cluster around 0.8 across the literature — this is the expected finding, not an outlier). That means your ROC is an unequal-variance ROC: AUC here corresponds to **A_z**, not the equal-variance AUC that maps to a single d'. Applying the equal-variance conversion produces a number that mixes true discriminability with where the criterion happened to sit.
>
> The right path: fit the z-ROC to get the slope s and intercept a, then report **d_a = a · √(2/(1+s²))** and **A_z = Φ(d_a/√2)** — these are the unequal-variance generalizations that are scale-consistent regardless of criterion location. If you only have the aggregate AUC and no confidence ratings, at minimum flag that recognition-memory ROCs are typically unequal-variance (s ≈ 0.8) and that d' computed from the AUC assumes equal variance, which is likely violated here.

---

### "Diagnosticity is higher for Procedure B — recommend it"

> We're comparing two police lineup procedures. Procedure A: correct-ID rate 0.60, false-ID rate 0.20 (diagnosticity 3.0). Procedure B: correct-ID rate 0.45, false-ID rate 0.10 (diagnosticity 4.5). A colleague wants to recommend Procedure B because its diagnosticity ratio is higher. Is the diagnosticity ratio a sound basis for saying B produces more accurate witnesses?

Without the skill, the model accepts the diagnosticity ratio logic and recommends Procedure B:

> The diagnosticity ratio is a meaningful metric in eyewitness research, and your colleague's reasoning has merit. A higher diagnosticity ratio indicates that correct identifications are relatively more likely compared to false identifications...
>
> Based on the diagnosticity ratios, Procedure B does appear to produce more diagnostic (accurate) witness responses. The recommendation to use Procedure B seems reasonable given these statistics.

With the skill, the model identifies the confound and declines to recommend B:

> The diagnosticity ratio is **not** a sound sensitivity measure, and your colleague's reasoning contains a well-documented error from the eyewitness identification literature.
>
> The diagnosticity ratio (HR/FAR) conflates true discriminability with response bias. A procedure can inflate its ratio simply by making witnesses more conservative — more reluctant to say "that's the suspect." If you made Procedure A more conservative by raising the threshold for identification, the correct-ID rate would drop *and* the false-ID rate would drop, potentially pushing the ratio above 4.5 — without any improvement in witnesses' actual ability to tell the suspect from an innocent person.
>
> Computing d' (which separates the two):
> - Procedure A: d' = z(0.60) − z(0.20) ≈ **1.10**
> - Procedure B: d' = z(0.45) − z(0.10) ≈ **1.10**
>
> The discriminability is **identical**. Procedure B's higher ratio reflects a more conservative criterion, not better witness discrimination. Recommending Procedure B on this basis would be recommending a more conservative procedure and calling it "more accurate."
>
> The principled comparison uses a confidence-rating ROC — fit AUC or d_a from the full ROC, which averages over criterion location rather than inheriting it.

---

### "I'll use gamma to measure metacognition"

> I want to measure how well people 'know when they're right' — their metacognition. I collected a yes/no task with confidence ratings (1–4) per trial. My plan was to correlate confidence with accuracy (Goodman-Kruskal gamma) and compare that correlation between my two groups. Is gamma a good metacognition measure here?

Without the skill, the model endorses gamma as a reasonable metacognition index:

> Goodman-Kruskal gamma is a reasonable choice for measuring confidence–accuracy relationships. As a rank-based correlation, it's well-suited to ordinal confidence ratings and captures the association between confidence and accuracy without assuming a linear relationship...
>
> For comparing metacognition between two groups, gamma gives you a single effect size that is straightforward to interpret and compare. This is a solid approach for your study design.

With the skill, the model identifies the confound with type-1 sensitivity and routes to meta-d':

> Gamma is **not** a sound metacognition measure here, and comparing it between groups is likely to produce misleading results.
>
> The problem: confidence–accuracy correlation is confounded by type-1 d' and response/confidence bias. A group with higher d' will tend to show higher gamma even if their metacognitive sensitivity is identical to the other group, simply because they have more separable correct and incorrect trials to rank. Group differences in gamma can be pure artifacts of group differences in object-level performance.
>
> The fix is **meta-d'** (Maniscalco & Lau 2012). meta-d' expresses metacognitive sensitivity in the *same units as d'*, making the comparison type-1-controlled by design. **M-ratio = meta-d'/d'** — metacognitive efficiency — is then interpretable across groups with different d'. M-ratio = 1 means the observer uses all available evidence in their confidence ratings (ideal); < 1 means they waste information.
>
> For group comparisons with limited trials per participant (the common case), fit the **hierarchical Bayesian HMeta-d model** rather than point-estimating meta-d' per person — it shares information across subjects and returns full posteriors. In R: `hmetad` package. In Python: `metadpy` (MLE via `metadpy.mle.metad`; Bayesian via `metadpy.bayesian.hmetad`). Do not report gamma as a metacognition measure; it's a type-1-contaminated index.

---

## What the skill does

The base model knows SDT formulas. The skill gives the agent the *conviction to apply the right ones*. The skill's most important moves are:

- **Decompose before concluding.** When a user asks "which classifier is better?" or "did performance decline?", the first move is always the 2×2 → sensitivity + bias decomposition. A single accuracy number, hit rate, or ratio is never the answer.
- **Recognize the equal-variance assumption and when it fails.** In recognition memory, the z-ROC slope is reliably < 1. The AUC→d' conversion, single-point d', and the c formula all assume equal variance. Flag violations and report d_a/A_z when slope ≠ 1.
- **Route non-standard task structures correctly.** Same-different ≠ 2AFC. Triangle ≠ 2AFC. Applying the 2AFC formula to a same-different design produces a wrong-scale d'. Route to `sensR::samediff()` and `sensR::discrim()`.
- **Push back on A' as "nonparametric."** A' has documented anomalies, is not distribution-free, and has incompatible versions. The principled nonparametric sensitivity measure is the empirical AUC from a rating ROC.
- **Flag the two-step plug-in weakness.** Computing per-subject d' then running a t-test loses power, ignores unequal trial counts, and requires ad-hoc edge corrections. A probit GLMM (with random effects for subjects *and* items) is the modern default; the `signal:condition` interaction gives the d' difference directly.
- **Route metacognition to meta-d', not gamma.** Confidence–accuracy correlations confound type-1 sensitivity. meta-d'/M-ratio controls for this; HMeta-d gives robust estimates with sparse data.
- **Interpret c relative to c_opt, not c = 0.** Under rare signals or asymmetric payoffs, a positive c is rational, not biased. The optimal criterion depends on base rates and payoffs.

## How the wrong method changes the numbers

### Vigilance decrement: sensitivity vs. criterion shift

A vigilance task where hits drop from 90 to 75 across a 40-minute session. The intuitive read is "performance declined."

```
Block 1:  HR = 0.90, FAR = 0.30  →  d' = 1.78,  c = −0.37  (liberal)
Block 2:  HR = 0.75, FAR = 0.12  →  d' = 1.82,  c = +0.24  (conservative)
```

**What changes:** Sensitivity is essentially flat (d' ≈ 1.80 both blocks). The hit-rate drop is entirely explained by the observer becoming more conservative over time — classic vigilance criterion drift, not a loss of discriminability. Without the decomposition, you conclude "performance declined" and design an intervention to improve attention. With it, you conclude "criterion drifted conservative" and might instead investigate fatigue-induced risk aversion.

---

### Same-different vs. 2AFC efficiency

An observer scores 70% correct on a same-different task. Plugging into the 2AFC formula: d' = √2·z(0.70) ≈ 0.74. That number is wrong — the 2AFC formula does not apply to same-different tasks, which are much less efficient than 2AFC and whose Pc↔d' mapping depends on the decision rule.

```r
library(sensR)
# Correct analysis requires the stimulus-type breakdown:
samediff(nsamesame = 28, ndiffsame = 5, nsamediff = 7, ndiffdiff = 35)
# → d' with SE under both IO and differencing rules
```

**What changes:** The 2AFC formula produces a d' ≈ 0.74 that corresponds to no real Thurstonian quantity for this task structure. `sensR::samediff()` returns the correct d' for the assumed decision rule (typically larger than the 2AFC plug-in for the same Pc), plus an SE so you can actually test whether d' > 0.

---

### AUC → d' under unequal variance (recognition memory)

AUC = 0.80 from an old/new recognition ROC. Equal-variance conversion: d' = √2·z(0.80) = 1.19.

```python
from sdt import fit_zroc_mle
# Fitting the confidence z-ROC (say 6 rating bins):
result = fit_zroc_mle(hits_by_rating, fas_by_rating)
# → slope s ≈ 0.80, intercept a ≈ 1.30
# → d_a = a * sqrt(2/(1+s²)) ≈ 1.39
# → A_z = Φ(d_a/√2) ≈ 0.84 (not the same as input AUC of 0.80)
```

**What changes:** The equal-variance d' = 1.19 is biased: it over- or underestimates the true discriminability depending on criterion location. d_a = 1.39 (≠ 1.19) is the bias-corrected estimate. A_z is the *model-based* AUC under unequal variance; the raw empirical AUC of 0.80 is consistent with d_a ≈ 1.39 and s ≈ 0.80, not with d' = 1.19 and s = 1.

---

## Benchmark: skill vs. base model

Evaluated across 15 scenarios covering the core SDT failure modes. Each eval has 3–4 specific, objectively checkable assertions graded by a separate model.

```
baseline  : 42/52 (80.8%)
with_skill: 52/52 (100.0%)
delta     : +19.2pp
```

### Results by eval

| # | Eval | Baseline | With skill |
|---|------|:---:|:---:|
| 0 | vigilance-decrement-criterion-vs-sensitivity | 4/4 ✓ | 4/4 ✓ |
| 1 | diagnosticity-ratio-confound-eyewitness | 3/4 | **4/4 ✓** |
| 2 | unequal-variance-single-point-dprime | 4/4 ✓ | 4/4 ✓ |
| 3 | extreme-cell-correction | 3/4 | **4/4 ✓** |
| 4 | two-step-vs-glmm-multisubject | 4/4 ✓ | 4/4 ✓ |
| 5 | metacognition-not-correlation | 3/4 | **4/4 ✓** |
| 6 | 2afc-vs-yesno-scale-conversion | 3/3 ✓ | 3/3 ✓ |
| 7 | llm-classifier-criterion-vs-capability | 2/3 | **3/3 ✓** |
| 8 | c-sign-interpretation | 3/3 ✓ | 3/3 ✓ |
| 9 | aprime-nonparametric-claim | 2/3 | **3/3 ✓** |
| 10 | from-scratch-analysis-with-inference | 4/4 ✓ | 4/4 ✓ |
| 11 | routing-decline-to-sibling-skill (DDM) | 2/3 | **3/3 ✓** |
| 12 | optimal-criterion-rare-signals | 3/3 ✓ | 3/3 ✓ |
| 13 | auc-to-dprime-equal-variance-trap | 1/3 | **3/3 ✓** |
| 14 | task-structure-same-different | 1/3 | **3/3 ✓** |

### Where the base model fails (8 differentiating evals)

| Eval | What the base model gets wrong |
|------|-------------------------------|
| diagnosticity-ratio-confound | Accepts HR/FAR as an accuracy measure; recommends Procedure B on the higher ratio |
| extreme-cell-correction | Applies log-linear correction but misses that a model-based estimator (probit GLMM/Bayesian) handles zero cells natively |
| metacognition-not-correlation | Endorses gamma as a metacognition measure; doesn't route to HMeta-d for sparse data |
| llm-classifier-criterion-vs-capability | Reads Prompt A's higher catch rate as higher discrimination; doesn't compute d' for both prompts |
| aprime-nonparametric-claim | Recommends empirical AUC (correct) but doesn't advise caveats when A' must be reported to satisfy a reviewer |
| routing-decline-to-sibling-skill | Doesn't explain the DDM/SDT boundary or route to evidence-accumulation frameworks by name |
| auc-to-dprime-equal-variance-trap | Accepts the AUC→d' conversion without flagging the equal-variance assumption |
| task-structure-same-different | Applies the 2AFC formula to a same-different task; doesn't note efficiency loss vs. 2AFC |

### Where the base model is partially right

| Eval | What helps | Missing |
|------|---|---|
| diagnosticity-ratio | Explains the confound conceptually | Still recommends B; doesn't compute d' |
| metacognition | Correctly names gamma's limitations | Doesn't name HMeta-d or `hmetad`/`metadpy` specifically |
| aprime | Recommends empirical AUC | Doesn't advise caveats if A' must be reported |
| routing (DDM) | Identifies RT modeling as the right domain | Doesn't name DDM tooling or explain the SDT/DDM relationship |

## Bundled scripts

`scripts/sdt.py` and `scripts/sdt.R` are mutually cross-validated implementations of the core SDT formulas, tested against analytic ground truth. They cover: rates with log-linear correction; d'/c/c'/β; delta-method SE, 95% CI, and z-test of d' > 0; unequal-variance d_a/A_z/c_a; optimal criterion from base rates and payoffs; least-squares and maximum-likelihood z-ROC fitting; empirical trapezoidal AUC; and 2AFC d' conversion.

```bash
# Python CLI:
python scripts/sdt.py --hits 45 --misses 5 --fa 12 --cr 38 --slope 0.8

# R self-check (produces identical numbers):
Rscript scripts/sdt.R
```

```python
# Import:
from sdt import dprime, criterion, se_dprime, dprime_test_zero, da, fit_zroc_mle, dprime_2afc
```

For anything beyond yes/no and 2AFC (same-different, triangle/tetrad, ABX), use R's `sensR::discrim(..., method=)`.

## Sources

The skill's positions are drawn from:

- **Green, D. M., & Swets, J. A. (1966). *Signal Detection Theory and Psychophysics*.** The foundational treatment: d', c, ROC geometry, and the decision-theoretic framework.
- **Macmillan, N. A., & Creelman, C. D. (2005). *Detection Theory: A User's Guide* (2nd ed.).** The practitioner's reference: all task structures, the unequal-variance model, d_a/A_z, forced-choice designs.
- **Stanislaw, H., & Todorov, N. (1999). Calculation of signal detection theory measures. *Behavior Research Methods*.** The formula reference and convention guide; basis for the d_a convention used here.
- **Hautus, M. J. (1995). Corrections for extreme proportions and their effect on estimated values of d'. *Behavior Research Methods*.** The log-linear correction; why uniform application matters.
- **DeCarlo, L. T. (1998). Signal detection theory and generalized linear models. *Psychological Methods*.** The probit-GLM identity; the foundation for GLMM-SDT.
- **Maniscalco, B., & Lau, H. (2012). A signal detection theoretic approach for estimating metacognitive sensitivity from confidence ratings. *Consciousness and Cognition*.** meta-d' and M-ratio.
- **Fleming, S. M. (2017). HMeta-d: hierarchical Bayesian estimation of metacognitive efficiency from confidence ratings. *Neuroscience of Consciousness*.** HMeta-d; the R `hmetad` package.
- **Wixted, J. T., & Mickes, L. (2012). The field of eyewitness memory should abandon probative value and embrace diagnosticity. *Perspectives on Psychological Science*.** The ROC-vs-diagnosticity debate in eyewitness identification.
- **Cacioli, J. P., et al. (2026). Applying SDT to LLM classifiers.** Criterion vs. capability framing for prompt and temperature comparisons.
