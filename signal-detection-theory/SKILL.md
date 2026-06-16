---
name: signal-detection-theory
description: Apply Signal Detection Theory (SDT) to any task where two classes of events must be told apart and you need to separate SENSITIVITY from RESPONSE BIAS — perception/psychophysics, recognition memory, diagnostic and medical decisions, lie/deception detection, eyewitness identification, vigilance, and yes/no, 2AFC, or confidence-rating tasks. Use this skill whenever the user mentions d-prime (d'), sensitivity vs. bias, criterion, hit rate / false-alarm rate, a confusion matrix of hits/misses/false-alarms/correct-rejections, an ROC or z-ROC framed as a detection/discrimination problem, beta or likelihood-ratio criterion, meta-d' / M-ratio / metacognitive efficiency, recognition-memory old/new ROCs, the diagnosticity ratio, or percent-correct that conflates accuracy and bias — even casually. Also use it whenever someone is about to summarize a discrimination task with a single accuracy number, because that almost always needs SDT's two-parameter decomposition. Do NOT assume generic stats knowledge suffices: the field is full of formulas copied across incompatible conventions (especially the unequal-variance d_a), and the default "report accuracy" instinct is exactly the mistake SDT exists to fix.
---

# Signal Detection Theory

SDT exists to answer one question that a single accuracy number cannot: **when someone (or some system) sorts events into two classes, how much of their behavior reflects genuine ability to tell the classes apart, and how much reflects where they chose to put their threshold?** Ability and threshold are different things, they move independently, and almost every interesting result in detection/discrimination depends on separating them. A model that reports "84% correct" or "hit rate = 0.9" has thrown that separation away before the analysis even started.

The whole skill flows from that one idea. Sensitivity (d', d_a, A_z) measures how far apart the two evidence distributions are. Bias (c, c', β) measures where the decision threshold sits. Report both, always, or you haven't done SDT.

## The non-negotiable stances

These are the documented consensus of the detection-theory literature (Green & Swets 1966; Macmillan & Creelman 2005; Stanislaw & Todorov 1999), not stylistic preferences. State them with directional confidence.

- **Never collapse a discrimination task to one number.** Percent correct, raw hit rate, accuracy, F1, or a single ROC point all confound sensitivity and bias. The first move on any detection problem is to recover the 2×2 table (hits, misses, false alarms, correct rejections) and split it into a sensitivity measure and a bias measure. If you can only report one thing, you are answering the wrong question.

- **The diagnosticity ratio (hit rate / false-alarm rate) is not a sensitivity measure.** It is confounded with response bias: change how willing the observer is to say "yes" and the ratio changes even when true discriminability is identical. This is the core of the eyewitness-ID debate (see `references/applications.md`). Same verdict for "PPV", "% of positives that were correct", and other ratio-of-rates shortcuts.

- **`c`, not `β`, is the default bias measure, and watch the sign.** `c = −0.5·[z(H) + z(F)]`. **c > 0 is conservative** (biased toward "no"); **c < 0 is liberal** (biased toward "yes"). β is a likelihood-ratio criterion and is fine to report alongside, but its scale is multiplicative and less intuitive, and confusing β with c (or flipping c's sign) is one of the most common SDT errors. Never report β as if it were c.

- **Handle 0/1 cells with the log-linear correction, applied uniformly.** A hit or false-alarm rate of exactly 0 or 1 gives an infinite z-score. Add 0.5 to **all four** cells (Hautus 1995) for **every** subject/condition — not just the ones with extreme cells. Correcting only the extreme cells distorts between-condition comparisons. Avoid the 1/(2N) rule as a default (more biased, errs in either direction). See `references/estimation.md`.

- **Single-point d' assumes equal variance — and that assumption is usually false in recognition memory.** A d' from one (H, F) pair is only valid if the signal and noise evidence distributions have equal variance. In recognition memory the target distribution is reliably *wider* than the lure distribution (z-ROC slope ≈ 0.8 < 1) — **this is the expected finding, not an exception**. When you report a z-ROC slope < 1 for a recognition-memory old/new task, explicitly note that wider target/old than lure/new variance is the standard pattern in this literature. Single-point d' is therefore biased and criterion-dependent for recognition memory. If you have confidence ratings, fit the full z-ROC and report **d_a** and **A_z** instead. If you only have one point and suspect unequal variance, say so explicitly.

- **A' and B''D are not "assumption-free," despite how they're taught.** The nonparametric sensitivity index A' and bias index B''D (Grier) have documented anomalies, are not actually distribution-free (Smith 1995; Pastore et al.), and several incompatible formulas circulate under the same name. Prefer parametric **d'/d_a** as the principled sensitivity measure. If you genuinely need a distribution-free sensitivity measure, use the **empirical (trapezoidal) AUC** from a rating ROC — that is the principled nonparametric option, not A'. If a reviewer insists on A' despite pushback, **report it with explicit caveats**: state that A' is not distribution-free, has known anomalies near ceiling, and that multiple incompatible formulas share the name — do not report A' silently as if the reviewer's premise were correct.

- **SDT is a GLM; for multi-subject or multi-condition designs, fit one model rather than plugging in per-subject d's.** Equal-variance yes/no SDT is exactly a probit binomial regression (intercept = z(F), stimulus coefficient = d'; DeCarlo 1998). The common "two-step" workflow — compute a d' per subject, then run a t-test/ANOVA on those — loses power, ignores differing trial counts and estimation uncertainty, and forces ad-hoc extreme-cell fixes. A probit GLMM is the modern best practice; the `signal:condition` interaction in the fixed effects gives the condition difference in d' directly with proper uncertainty. **Always include random effects for both subjects and items** — stimuli always vary in difficulty, and by-subjects-only models inflate Type-I error (the classic "language-as-fixed-effect fallacy"). The minimal correct random-effects structure for a within-subjects design: `(signal * condition | subject) + (signal | item)`. The GLM is the *estimation engine*; SDT is the *measurement theory* that names the coefficients sensitivity and bias and supplies the decision-theory layer — they're complementary, not redundant. See `references/estimation.md`.

- **A d' is an estimate — report its uncertainty, and never pool cells across heterogeneous observers.** For a single observer, d' has a closed-form delta-method standard error; use it for CIs and "is d' > 0?" tests. Do **not** form a "group d'" by summing everyone's hits/FAs into one table, or by averaging rates before z-transforming (z is nonlinear) — that's an aggregation artifact (the SDT version of Simpson's paradox). Compute per-subject d's and summarize them, or fit a GLMM. See `formulas.md` §9 and `pitfalls.md` #13.

- **The neutral criterion (c = 0) is not always the optimal one.** Under unequal base rates or asymmetric payoffs the expected-value-maximizing criterion shifts (`β_opt = [P(N)/P(S)]·[payoff ratio]`); rare signals make conservatism *rational*. Interpret an observed `c` relative to `c_opt`, not relative to 0. See `formulas.md` §10.

- **Metacognition needs meta-d', not a confidence–accuracy correlation.** Raw correlations (gamma, phi, point-biserial) between confidence and accuracy are confounded by type-1 sensitivity and bias. meta-d' (Maniscalco & Lau 2012) expresses metacognitive sensitivity in the same units as d'; **M-ratio = meta-d'/d'** is the efficiency measure. Use hierarchical Bayesian estimation (HMeta-d) when data per subject are limited. See `references/metacognition.md`.

## Things the field genuinely disagrees about

Surface the spectrum; don't manufacture a single right answer.

- **Why z-ROC slopes are < 1 in recognition memory.** The unequal-variance single-process account (UVSD: target evidence is just more variable) and the dual-process account (DPSD: recollection + familiarity) both fit, make subtly different predictions, and remain contested (Wixted; Yonelinas; Rotello). Present both.
- **ROC/AUC vs. process models for eyewitness identification.** Wixted & Mickes argue ROC/AUC is the right tool for measuring witness discriminability; Wells and colleagues argue the 2×2 reduction discards the diagnostic structure of a real 3×2 lineup (fillers, rejections). Both critiques are partly right (see `references/applications.md`).
- **How much to lean on β vs. c vs. c' for bias**, and whether the observer's criterion is best described as fixed in evidence units or in likelihood-ratio units. Reasonable detection theorists differ.
- **Equal- vs. unequal-variance as the default model** when you have no rating data to estimate the slope. Some default to equal variance for parsimony; others treat it as known-to-be-wrong and prefer forced-choice designs that sidestep it.

## Workflow: how to approach an SDT request

1. **Identify the task structure first**, because it dictates every formula:
   - **Yes/No (single-interval):** one stimulus per trial, "signal present?" → d', c. The bias problem is live here.
   - **Rating / confidence:** yes/no plus a confidence scale → a full ROC. Fit the z-ROC, get slope s, d_a, A_z. *Strongly preferred* whenever feasible because it tests the equal-variance assumption instead of assuming it.
   - **m-AFC (2AFC, etc.):** signal vs. noise presented together, pick the interval. Largely removes the bias problem; d' relates to percent correct (2AFC: `d' = √2 · z(Pc)`). You **cannot** compare a 2AFC d' to a yes/no d' without this conversion.
   - **Same-different:** two stimuli per trial, judge "same" or "different." **The 2AFC formula does NOT apply here** — the task structure is fundamentally different and same-different is **much less efficient than 2AFC** (a given d' yields substantially lower Pc). Additionally, the Pc↔d' mapping depends on the decision rule (independent-observation vs. differencing). Always break down performance by stimulus type (same-pair vs. different-pair), not just overall Pc. Route to `sensR::samediff()` — see `references/tasks.md`.
   - **Triangle / tetrad / ABX:** sensory discrimination protocols with 3–4 stimuli; highly inefficient. Always use `sensR::discrim(..., method=)` — never apply 2AFC formulas here either.
2. **Recover the 2×2 (or rating) table.** If given only summary rates, reconstruct counts where possible (you need N to apply corrections and to weight a model).
3. **Apply the log-linear correction** if any cell is 0/1 (or, by default, uniformly).
4. **Compute sensitivity AND bias.** Use the bundled script — do not re-derive formulas by hand; the convention traps (below) are real.
5. **Check the equal-variance assumption** if you have rating data; report d_a/A_z when slope ≠ 1.
6. **For groups/conditions/covariates,** prefer a probit GLMM over per-subject plug-in estimates.
7. **Report** with the template below, including the correction used and the assumption status.

## Use the bundled scripts — don't hand-derive

`scripts/sdt.py` (Python) and `scripts/sdt.R` (R) are tested, mutually cross-validated implementations that produce **identical numbers** — use whichever language the user's pipeline is in. They were validated against analytic ground truth (the equal-variance reduction of d_a, the A_z identity, the probit-GLM identity, the delta-method SE of d' against Monte Carlo, and ML recovery of the z-ROC slope). They cover: rates + corrections; d'/c/c'/β; **SE, CI, and significance tests of d'** (delta method); unequal-variance d_a/A_z/c_a; **optimal criterion** under base rates and payoffs; z-ROC fitting (least-squares **and** a maximum-likelihood rating fit in Python); empirical AUC; and 2AFC conversion.

```bash
# from counts, with optional z-ROC slope for unequal-variance d_a
python scripts/sdt.py --hits 45 --misses 5 --fa 12 --cr 38 --slope 0.8
Rscript scripts/sdt.R          # R self-check (same numbers)
```

Or import: `from sdt import report, dprime, criterion, se_dprime, dprime_test_zero, da, criterion_uv, optimal_criterion, fit_zroc_mle, dprime_2afc` (Python) / `source("scripts/sdt.R")` then `sdt_report(...)`, `se_dprime(...)`, `optimal_criterion(...)` (R). For anything beyond yes/no and 2AFC (m-AFC, same-different, triangle/tetrad, ABX), use R's `sensR::discrim(..., method=...)` — see `references/tasks.md`.

**The convention trap that justifies the script:** the unequal-variance formula is written two different ways in the literature depending on whether `s` means σ_noise/σ_signal or its reciprocal, which flips whether `s` multiplies z(H) or z(F). This skill and the scripts use **s = z-ROC slope = σ_noise/σ_signal**, giving `d_a = √(2/(1+s²))·(z(H) − s·z(F))`, which correctly reduces to d' at s = 1. If you copy a formula from a paper, check which convention it uses before trusting it.

## Reporting template

ALWAYS report at least:

```
- Task type: [yes-no / rating / m-AFC / same-different / triangle / ...]
- N: [signal trials], [noise trials]
- Hit rate, False-alarm rate (and the 0/1 correction used, e.g. "log-linear")
- Sensitivity: d' = X.XX [± SE, or 95% CI]   (or d_a = X.XX, A_z = 0.XX if unequal variance)
- Bias: c = X.XX  ([conservative / liberal]);  c' = X.XX;  β = X.XX
  (and, if base rates/payoffs are asymmetric, c relative to c_opt)
- Equal-variance assumption: [tested via z-ROC slope = X.XX / assumed, untested]
- For groups: model-based estimates (probit GLMM / Bayesian) with uncertainty
  intervals — never a d' from pooled cells or from averaged rates
```

Then interpret sensitivity and bias *separately*: e.g., "discriminability was high (d' = 2.3) but the observer was liberal (c = −0.5), trading misses for false alarms."

## Reference files — read the one that matches the task

- `references/formulas.md` — every measure, equal and unequal variance, all task types, worked numeric examples, the convention pitfalls, inference (SE/CI/tests of d'), the optimal criterion, the A_z↔effect-size bridge, and sanity checks. Read when you need the math or a derivation.
- `references/tasks.md` — the discrimination-task taxonomy (yes/no, m-AFC, same-different, ABX, oddity/triangle/tetrad, rating) and how task structure + decision rule fix the d' model. Read whenever the task is anything other than plain yes/no or 2AFC, or when you must compare across task types.
- `references/estimation.md` — corrections in depth, MLE vs. plug-in, the probit-GLM and GLMM reframe (and why SDT isn't redundant given the GLM), hierarchical Bayesian SDT, and current Python/R tooling with code. Read for any multi-subject/multi-condition design or when choosing an estimator.
- `references/metacognition.md` — type-1 vs type-2, meta-d', M-ratio, HMeta-d, AUROC2, caveats, tooling. Read for anything about confidence, metacognitive sensitivity/efficiency, or "are people's confidence judgments well-calibrated."
- `references/applications.md` — recognition memory (UVSD vs DPSD), eyewitness ID (ROC vs diagnosticity debate), medical/ML diagnostics, and SDT applied to LLM classifiers. Read for domain framing and the live debates.
- `references/pitfalls.md` — the anti-patterns catalog with wrong-vs-right worked examples. Skim before finalizing any analysis.

## When NOT to use this skill (route to a sibling)

SDT shares machinery with several adjacent skills; keep the boundary clean.

- **Tuning a classifier threshold or just reporting ROC/AUC for an ML model**, with no latent-evidence/decision framing → that's an **ML-evaluation** task. (The bridge is real — AUC *is* an SDT quantity and threshold *is* a criterion — so borrow the vocabulary, but don't pull in the full psychophysics apparatus.)
- **Modeling the *time course* of a decision** (reaction-time distributions, evidence accumulation: DDM, LBA, race models) → **computational/cognitive-modeling** skill. SDT is the static, threshold cousin of those dynamic models; mention the relationship but hand off the RT modeling.
- **Test/item measurement** (reliability, IRT item difficulty/discrimination, factor structure) → **psychometrics** skill. Note the false friend: SDT "sensitivity" is *not* item "discrimination," and SDT "criterion" is *not* an IRT threshold/difficulty parameter, despite the overlapping words.
- **Multidimensional stimuli where perceptual and decisional separability are the question** (does attending one dimension leak into another?) → that's **General Recognition Theory (GRT; Ashby & Townsend)**, the multivariate generalization of SDT. This skill is the univariate core; flag GRT as the right tool and don't try to force a 1-D d' onto a genuinely 2-D problem.
