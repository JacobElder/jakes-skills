# 06 — Judge Calibration: Trusting Your Grader

This is the **gate that runs before every other analysis.** Difficulty, discrimination, ability,
and reliability are all computed *from pass/fail labels*. If a label-producer (LLM judge or human
rater) is unreliable, every downstream number is noise dressed as signal. Script:
`scripts/judge_calibration.py`. Skip this gate only when labels come from an **exact programmatic
check** (string match, unit test, schema validation) — those are ground truth by construction.

## Three things to check, in order

### 1. Reliability — do graders agree?
If you can't reproduce the same label, the label isn't measuring anything stable.

- **Cohen's κ** (two raters) or **Fleiss' κ** (3+) — agreement *beyond chance*. Use κ, not raw
  agreement %, because on skewed pass rates (most cases pass) raw agreement is inflated by the base
  rate. Rough reading: κ < 0.2 poor, 0.2–0.4 fair, 0.4–0.6 moderate, 0.6–0.8 substantial, > 0.8
  near-ceiling.
- **Benchmark for "good":** strong LLM judges reach roughly **80% agreement with humans — about
  the level humans reach with each other.** That's the realistic ceiling, not 100%. If your
  judge–human agreement is near that, the judge is usable; if it's near chance, fix the rubric
  before trusting any score.
- **κ is criterion-dependent.** Judges often agree on clear-cut rubric dimensions and diverge on
  fuzzy ones. Compute κ per rubric criterion, not just overall — a modest overall κ can hide one
  unreliable criterion dragging it down (which you can then rewrite or drop).

### 2. Discrimination — can the judge tell good from bad?
Against a trusted reference set (human gold labels on a subset), treat the judge as a classifier
and check **ROC-AUC / PR-AUC**. AUC ≈ 0.5 means the judge's pass/fail is unrelated to truth — the
suite is dead on arrival regardless of how its numbers look. This is the judge-level analogue of
item discrimination.

### 3. Calibration — are the judge's confidences honest?
Only if the judge emits a probability/confidence (not just a label). **Calibration is an
independent gate from reliability — clearing kappa does NOT clear calibration.** A judge can
agree with humans 72% of the time (solid kappa) while being severely overconfident (states 0.95
on every judgment). These two problems have different consequences and different fixes.

When the judge emits confidence scores, **compute Brier score and/or ECE** before relying on those
scores in any downstream analysis. Do not skip this step or substitute "it looks overconfident"
for a quantified measurement.

- **Brier score** — mean squared error of probabilistic predictions (lower better). Captures
  accuracy and calibration together.
- **Expected Calibration Error (ECE)** — bin predictions by confidence, compare each bin's mean
  confidence to its empirical accuracy, average the gaps. Low ECE = "when it says 0.8 it's right
  ~80% of the time." High ECE with stated confidence of 0.95 and accuracy of 70% is a concrete
  failure that must be reported.
- **Reliability diagram** — plot predicted confidence vs. observed accuracy per bin; the diagonal
  is perfect. The script returns the binned data for this.
- **Known failure mode:** LLM judges are frequently **overconfident** — high stated confidence
  (0.90–0.98), low ECE improvement as you'd hope. **Don't let a confident judge talk you out of
  the agreement check.** Once you've computed ECE/Brier: if overconfidence is mild, recalibrate
  (Platt/temperature scaling); if severe, ignore the confidence scores entirely and report only
  the binary label with its measured κ.
- **Downstream consequence of overconfidence:** when a judge states 0.90–0.98 confidence but is
  only right ~70% of the time, **pass-rate uncertainty estimates appear artificially tight** —
  you will believe your measurements are more precise than they actually are. This is not a minor
  cosmetic issue: decisions made on apparently-tight uncertainty are under-hedged. Always name
  this consequence explicitly when overconfidence is detected.

**The two-gate rule:** κ clears the *binary-label* gate. ECE/Brier clears the *confidence-score*
gate. Both must be cleared before using confidence scores downstream. A response that only checks
kappa and then proceeds to use confidence scores has skipped a required gate.

## What to do when the judge fails the gate

- **Low κ:** the rubric is ambiguous. Rewrite criteria to be more behavioral/checkable, add
  worked positive and negative examples, decompose a fuzzy criterion into specific sub-checks.
  Re-measure κ on a fresh subset.
- **Low discrimination (AUC≈0.5):** the judge isn't reading the dimension you care about — often
  it's grading style/format instead of correctness. Make the rubric target the actual capability;
  consider a reference-based or pairwise judge.
- **Use pairwise over absolute scoring when you can.** Judges are more reliable making *relative*
  ("which is better, A or B?") than *absolute* ("score this 1–10") decisions, because absolute
  scoring requires calibrating to an abstract scale. For version comparison especially, pairwise
  preference judging usually yields higher κ.
- **Ensemble / self-consistency:** multiple judges (or repeated sampling of one) with majority
  vote raises reliability; report the inter-judge κ so you know how much you're leaning on it.

## Propagate judge uncertainty downstream

A measured judge error rate isn't just a gate — it's an uncertainty you should carry. If the judge
agrees with truth ~85% of the time, your per-item pass labels have ~15% flip noise, which widens
every difficulty/discrimination/ability interval. At minimum, note the judge κ alongside the suite
results so a reader knows the floor on label noise. When stakes are high, run the suite with two
judges and report results under both to show the conclusion is robust to grader choice.
