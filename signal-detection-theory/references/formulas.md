# SDT Formulas — measures, derivations, and convention traps

Notation: `z(p) = Φ⁻¹(p)` (inverse standard-normal CDF; `qnorm` in R, `scipy.stats.norm.ppf` in Python). `Φ` is the standard-normal CDF.

## Contents
1. The 2×2 table and rates
2. Equal-variance measures (d', c, c', β)
3. Worked example (equal variance)
4. Unequal-variance measures (d_a, A_z, c_a) and the z-ROC
5. The convention trap in d_a
6. Forced-choice (2AFC / m-AFC)
7. Nonparametric measures (A', B''D) and why to avoid them
8. Sanity checks
9. Inference on d' (standard error, CI, significance)
10. Optimal criterion under base rates and payoffs
11. A_z as an effect size (the Mann–Whitney / AUC bridge)

---

## 1. The 2×2 table and rates

| | "yes" (signal) | "no" (noise) |
|---|---|---|
| **signal present** | Hit (H) | Miss |
| **signal absent** | False Alarm (FA) | Correct Rejection (CR) |

- Hit rate `HR = Hits / (Hits + Misses) = P("yes" | signal)`
- False-alarm rate `FAR = FA / (FA + CR) = P("yes" | noise)`

Misses and correct rejections carry no information beyond HR and FAR (they're the complements), but you need the raw counts to apply corrections and to weight model-based estimates.

## 2. Equal-variance Gaussian measures

Model: noise ~ N(0, 1), signal ~ N(d', 1). Observer says "yes" when evidence exceeds criterion location `k`. Then:

- **Sensitivity:** `d' = z(HR) − z(FAR)`. Distance between distribution means in SD units. d' = 0 is chance; d' ≈ 1 is moderate; d' ≈ 2 is strong; d' > 4 is near-ceiling and usually means you need the log-linear correction.
- **Criterion (bias):** `c = −0.5·[z(HR) + z(FAR)]`.
  - `c = 0` unbiased (criterion at the midpoint between the means).
  - `c > 0` **conservative** — biased toward "no", few false alarms, more misses.
  - `c < 0` **liberal** — biased toward "yes", many hits *and* false alarms.
  - Derivation: with k = the criterion in noise-SD units, k = −z(FAR) and the midpoint is d'/2, so c = k − d'/2 = −z(FAR) − (z(HR)−z(FAR))/2 = −0.5[z(HR)+z(FAR)].
- **Relative criterion:** `c' = c / d'`. Bias scaled by sensitivity (how far the criterion sits relative to the gap). Useful for comparing bias across observers with different d'.
- **Likelihood-ratio criterion:** `ln β = c · d' = −0.5·[z(HR)² − z(FAR)²]`, `β = exp(ln β)`. β is the ratio of signal-to-noise evidence density *at the criterion*, equivalently the slope of the ROC at the operating point. `β = 1` is the neutral (and for equal priors/payoffs, optimal) criterion. β > 1 conservative, β < 1 liberal.

**Do not confuse c and β.** They encode the same bias on different scales; c is additive (in SD units) and symmetric around 0, β is multiplicative and centered on 1. Mixing them up, or flipping the sign of c, is the single most common SDT mistake.

## 3. Worked example (equal variance)

50 signal trials, 50 noise trials. 45 hits, 5 misses, 12 false alarms, 38 correct rejections.

With the **log-linear** correction (add 0.5 to all cells):
- HR = (45 + 0.5)/(50 + 1) = 0.8922 → z(HR) = 1.237
- FAR = (12 + 0.5)/(50 + 1) = 0.2451 → z(FAR) = −0.690
- d' = 1.237 − (−0.690) = **1.93** (strong discriminability)
- c = −0.5·(1.237 − 0.690) = **−0.27** (mildly **liberal** — leans toward "yes")
- c' = −0.27 / 1.93 = −0.14
- ln β = −0.27 × 1.93 = −0.53 → β = **0.59** (< 1, confirms liberal)

Interpretation: this observer discriminates well but errs toward saying "signal present", accepting extra false alarms to catch more signals. (Verify with `python scripts/sdt.py --hits 45 --misses 5 --fa 12 --cr 38`.)

## 4. Unequal-variance measures and the z-ROC

When signal and noise distributions have **different** variances, a single (HR, FAR) point no longer pins down sensitivity — the same d' formula gives different answers at different criteria. You need the **ROC** (sweep the criterion via confidence ratings) and you work on the **z-ROC** (ROC plotted in z-coordinates), which is a straight line:

`z(HR) = a + s · z(FAR)`

- **slope `s = σ_noise / σ_signal`** — the ratio of the noise SD to the signal SD.
- **intercept `a`** — z(HR) when z(FAR) = 0.

In recognition memory, `s ≈ 0.8` reliably (target/old evidence is *more* variable than lure/new evidence), so the slope is below 1. A slope of exactly 1 means equal variance (and then d_a = d').

- **Unequal-variance sensitivity:** `d_a = √(2/(1+s²)) · (z(HR) − s·z(FAR))`. Equivalently `d_a = a·√(2/(1+s²))` evaluated on the fitted line. It is the mean separation divided by the root-mean-square of the two SDs.
- **Area under the ROC:** `A_z = Φ(d_a/√2) = Φ(a/√(1+s²))`. This is the model-based AUC — the probability that a random signal trial yields more evidence than a random noise trial.
- **Bias under unequal variance:** the equal-variance `c` is no longer quite right when s ≠ 1. A natural generalization that reduces to `c` at s = 1 is `c_a = −[z(HR) + z(FAR)] / (1 + s)` (the "2" in c becomes "1 + s"). Conventions for unequal-variance bias genuinely vary in the literature, so also report the unambiguous **noise-referenced criterion** `k = −z(FAR)` (the criterion's location in noise-SD units). Don't quote an equal-variance `c` for a task you've shown is unequal-variance without noting it.

Estimate s by fitting a line to the empirical z-ROC points (or, better, by maximum likelihood / a Bayesian ordinal-probit model — see `estimation.md`). `scripts/sdt.py`'s `fit_zroc()` returns the operating points, slope, intercept, d_a, A_z, and the empirical trapezoidal AUC from rating counts.

## 5. The convention trap in d_a

The d_a formula appears in the literature in two forms:

- Under **s = σ_noise/σ_signal** (z-ROC slope; this skill's convention): `d_a = √(2/(1+s²))·(z(HR) − s·z(FAR))`.
- Under **s = σ_signal/σ_noise** (the reciprocal): `d_a = √(2/(1+s²))·(s·z(HR) − z(FAR))`.

Both are correct *for their own definition of s*, and they give the same number when you plug in the matching slope. But copy one paper's formula and another paper's slope and you get a wrong answer that still "looks like d_a." The safe check: **at equal variance (s = 1) any correct form must reduce to d' = z(HR) − z(FAR), and must reduce to Φ(d'/√2) for A_z.** The bundled script is internally consistent under the σ_noise/σ_signal convention; verify any hand formula against the s = 1 reduction before trusting it.

## 6. Forced-choice (2AFC and m-AFC)

In m-AFC the observer compares signal and noise directly and picks the larger, so there is little room for response bias — sensitivity falls out of percent correct.

- **2AFC, unbiased:** `d' = √2 · z(Pc)`, where Pc is proportion correct. Inverse: `Pc = Φ(d'/√2)`.
- The √2 arises because the decision variable is the *difference* of two independent draws (variance 1 + 1 = 2).
- **Critical:** a 2AFC d' and a yes/no d' are on the **same underlying scale only after this conversion**. Reporting "2AFC accuracy = 85%" next to a yes/no d' without converting is an apples-to-oranges error. (85% → d' = √2·z(0.85) = √2·1.036 = 1.47.)
- m-AFC (m > 2) requires numerical integration over the max of m−1 noise draws vs. one signal draw; use tables (Hacker & Ratcliff 1979) or `sdt`-style helpers in `psyphy`/`sensR` (R).

Forced choice trades the bias problem for more trials and a different task; it does not measure criterion, by design.

## 7. Nonparametric measures (A', B''D) — and why to avoid them as headline numbers

These are widely taught as "assumption-free" alternatives to d' and c:

- **A'** (Pollack & Norman 1964; sensitivity), ranges ~0.5 (chance) to 1 (perfect).
- **B''D** (Grier 1971; bias), ranges −1 (liberal) to +1 (conservative).

Problems:
- They are **not actually distribution-free** (Smith 1995; Pastore, Crawley, Berens & Skelly 2003). A' has documented anomalies, behaves oddly near ceiling, and is not a consistent estimator of area under any single ROC.
- **Multiple incompatible formulas** circulate under the name "A'" (and B'' vs B''D get conflated), so two papers reporting "A'" may not be computing the same thing.

**Preferred alternatives:**
- Parametric: d' (equal var) or d_a/A_z (unequal var).
- Genuinely nonparametric sensitivity: the **empirical trapezoidal AUC** from a rating ROC (`fit_zroc()` returns it). This makes no Gaussian assumption and is a proper area estimate.

Only report A'/B''D if you must match a legacy analysis, and flag the caveat when you do.

## 8. Sanity checks (run these mentally on every result)

- d' should be ≥ 0 for above-chance performance; a negative d' means HR < FAR (responding *against* the signal) — usually a coding error (swapped labels).
- c and β must agree in direction: c > 0 ⟺ β > 1 (conservative); c < 0 ⟺ β < 1 (liberal).
- If HR or FAR is exactly 0 or 1 and you didn't correct, your z is ±∞ — that's a bug, not a finding.
- d_a must equal d' when the z-ROC slope is 1.
- A 2AFC d' that's wildly larger than a yes/no d' from the same observer often means someone forgot the √2 conversion.
- Very large d' (> 4) with small N is almost always an artifact of an uncorrected ceiling cell.

## 9. Inference on d' (standard error, CI, significance)

A d' is an estimate with sampling error; for a single observer it has a variance you can compute analytically (delta method; Gourevitch & Galanter 1967; Miller 1996). HR and FAR are binomial proportions, and d(z)/dp = 1/φ(z(p)), so:

`Var(d') = HR(1−HR) / [N_signal · φ(z(HR))²]  +  FAR(1−FAR) / [N_noise · φ(z(FAR))²]`

where φ is the standard-normal **pdf** (not Φ). Signal and noise trials are independent, so the two variances add. Then `SE(d') = √Var(d')`, a Wald CI is `d' ± z_{α/2}·SE`, and a test that d' > 0 is `z = d'/SE`. (`sdt.py`/`sdt.R`: `se_dprime`, `dprime_ci`, `dprime_test_zero`.)

Caveats:
- This needs the **corrected** HR/FAR (use the same ones you used for d'); near 0/1 the variance explodes, which is the formula correctly telling you a ceiling cell carries little information.
- To compare **two independent** observers' d's, use `compare_dprimes` (variances add). For **within-subject** or multi-condition designs, do **not** chain these per-subject SEs into a t-test — fit a probit **GLMM** instead (`estimation.md`); it handles the correlation structure and trial-count weighting properly.

## 10. Optimal criterion under base rates and payoffs

The "neutral" criterion (c = 0, β = 1) is only optimal when signals and noise are equally likely and all outcomes are equally valued. In general the expected-value-maximizing criterion is (Green & Swets 1966):

`β_opt = [P(noise)/P(signal)] · [(value_CR + cost_FA) / (value_H + cost_M)]`

with values/costs as positive magnitudes. `c_opt = ln(β_opt)/d'`. Consequences:
- **Rare signals → β_opt > 1 → the optimal observer is conservative.** A low hit rate when signals are rare can be perfectly rational, not "poor performance" (see `pitfalls.md` #12). Example: P(signal)=0.2, equal payoffs → β_opt = (0.8/0.2)·1 = 4, c_opt = ln(4)/d'.
- **Asymmetric costs shift the criterion** even at equal base rates (e.g., a missed tumor costs more than a false alarm → be liberal). Interpret an observed `c` *relative to `c_opt`*, not relative to 0. (`sdt.py`/`sdt.R`: `optimal_criterion`.)

## 11. A_z as an effect size (the Mann–Whitney / AUC bridge)

`A_z` (and the empirical AUC) equals **P(signal draw > noise draw)** — exactly the probability of superiority / common-language effect size, and the population quantity the Mann–Whitney U statistic estimates. So an SDT sensitivity result translates directly into the broader effect-size vocabulary: AUC = 0.5 is chance, and under equal variance `AUC = Φ(d'/√2)` (d' = 1 ↔ AUC ≈ 0.76; d' = 2 ↔ AUC ≈ 0.92). This is the clean way to relate d' to ROC/AUC reported in ML or biostatistics — but the equivalence to a *single* d' holds only under equal variance; otherwise relate AUC to A_z and report the z-ROC slope (`pitfalls.md` #8).
