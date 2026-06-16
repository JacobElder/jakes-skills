# SDT Anti-Patterns — wrong vs. right

Skim this before finalizing any detection/discrimination analysis. Each entry is a mistake that looks reasonable and is common in published work.

## 1. Reporting a single accuracy number for a discrimination task
**Wrong:** "The model detected violations with 84% accuracy." / "Hit rate was 0.90, so performance was good."
**Why it fails:** 84% can reflect great discriminability with a neutral criterion, or mediocre discriminability rescued by a base rate, or a strong bias. Hit rate alone says nothing without the false-alarm rate.
**Right:** Recover the 2×2, report sensitivity *and* bias. "d' = 1.9 (strong discriminability), c = −0.27 (mildly liberal)." Now you know *what* drove the number.

## 2. Using the diagnosticity ratio (HR/FAR) as a sensitivity measure
**Wrong:** "Procedure A has diagnosticity 3.0 vs. B's 2.0, so A produces more accurate witnesses."
**Why it fails:** HR/FAR is confounded with bias — making witnesses more conservative inflates it without improving discriminability.
**Right:** Build a confidence ROC and compare AUC, or fit d'/d_a. Treat the ratio as a bias-contaminated quantity, not an accuracy one. (See `applications.md`.)

## 3. Single-point d' when variance is unequal
**Wrong:** Computing one d' from one (HR, FAR) pair on a recognition-memory old/new task and comparing it across conditions.
**Why it fails:** Recognition z-ROCs have slope ≈ 0.8 (unequal variance), so single-point d' depends on where the criterion sat and is biased.
**Right:** If you have confidence ratings, fit the z-ROC and report **d_a** and **A_z**. If you only have one point, flag that d' assumes equal variance and may be biased.

## 4. Confusing c and β, or flipping the sign of c
**Wrong:** "c = 2.1, so the observer is liberal." / Reporting β where c was expected.
**Why it fails:** c > 0 is *conservative*, not liberal. β lives on a multiplicative scale centered at 1; c is additive centered at 0. They're not interchangeable.
**Right:** State the convention explicitly: c < 0 = liberal (toward "yes"), c > 0 = conservative (toward "no"); β < 1 liberal, β > 1 conservative. Sanity-check that c and β agree in direction.

## 5. Ad-hoc handling of 0/1 cells (or correcting only the extreme ones)
**Wrong:** "HR was 1.0 so I set it to 0.99." / Correcting only subjects who hit a ceiling cell.
**Why it fails:** Arbitrary substitution biases d' unpredictably; correcting only extreme subjects creates a systematic gap between them and everyone else.
**Right:** Apply the **log-linear** correction (add 0.5 to all four cells) **uniformly** to every subject/condition, or fit a model that handles zero cells via the likelihood. (See `estimation.md`.)

## 6. A' / B''D as "assumption-free" headline measures
**Wrong:** "We used the nonparametric A' to avoid distributional assumptions."
**Why it fails:** A' is not actually distribution-free, has documented anomalies, and several incompatible formulas share the name.
**Right:** Use d'/d_a, or — if you truly need a nonparametric sensitivity index — the **empirical trapezoidal AUC** from a rating ROC. Only report A' to match a legacy analysis, with the caveat stated.

## 7. Two-step plug-in for a multi-subject design
**Wrong:** Compute one d' per subject, then run a t-test/ANOVA on those d' values.
**Why it fails:** Ignores trial-count differences and estimation uncertainty, forces per-subject edge corrections, and (if items vary) inflates Type-I error.
**Right:** Fit a **probit GLMM** with random effects over subjects *and* items (or a Bayesian equivalent). The stimulus × condition interaction gives the d' difference with proper uncertainty. (See `estimation.md` §3–4.)

## 8. Treating AUC and d' as interchangeable without noting the assumption
**Wrong:** "AUC = 0.84, equivalently d' = 1.4" stated as a fixed identity.
**Why it fails:** AUC ↔ d' mapping (`AUC = Φ(d'/√2)`) holds **only under equal variance**. Under unequal variance, AUC corresponds to A_z and the conversion uses d_a, not d'.
**Right:** Convert only when equal variance holds (or you've checked the z-ROC slope ≈ 1); otherwise relate AUC to **A_z** and report the slope.

## 9. Confidence–accuracy correlation as "metacognition"
**Wrong:** "Confidence correlated with accuracy (gamma = 0.4), showing good metacognition."
**Why it fails:** Gamma is confounded by type-1 d' and by bias; group differences in it can be pure type-1 artifacts.
**Right:** Report **meta-d'** and **M-ratio** (meta-d'/d'), ideally hierarchical Bayesian. (See `metacognition.md`.)

## 10. Comparing 2AFC and yes/no d' without the √2 conversion
**Wrong:** "2AFC accuracy was 85% (≈ d' implied), higher than the yes/no d' of 1.2."
**Why it fails:** A 2AFC proportion-correct and a yes/no d' are on different scales. 85% → d' = √2·z(0.85) = 1.47.
**Right:** Convert 2AFC to the common scale (`d' = √2·z(Pc)`) before any comparison.

## 11. Swapped labels producing a negative d'
**Wrong:** Reporting d' = −0.8 and interpreting it as "below chance."
**Why it fails:** Below-chance responding is rare; a negative d' almost always means hits/false-alarms (or signal/noise trials) were coded backwards, so HR < FAR mechanically.
**Right:** Audit the coding. Genuine below-chance performance needs a substantive explanation; a coding swap needs a fix.

## 12. Ignoring base rates when interpreting bias
**Wrong:** Concluding an observer is "biased" because they say "yes" rarely, without noting signals were rare.
**Why it fails:** The *optimal* criterion shifts with the signal base rate and payoff structure; a conservative c can be perfectly rational when signals are rare.
**Right:** Interpret c relative to the optimal criterion for the actual base rate/payoffs, not relative to 0 in the abstract.

## 13. Pooling cells across heterogeneous subjects before computing d'
**Wrong:** Sum hits/misses/FAs/CRs across all subjects into one big 2×2, then compute a single "group d'". Or average each subject's HR and FAR and compute d' from the averages.
**Why it fails:** Pooling counts across observers who differ in sensitivity *and* criterion creates an aggregation artifact: the pooled HR/FAR mix together people sitting at different operating points, so the group d' can be biased downward (and the pooled criterion is meaningless). This is the SDT version of Simpson's paradox — the aggregate can misrepresent or even reverse the within-subject pattern. Averaging rates first is also wrong because z() is nonlinear, so mean(z) ≠ z(mean).
**Right:** Compute d' and c **per subject**, then summarize the distribution of those — or, better, fit a probit **GLMM** to trial-level data with subject (and item) random effects, which models the heterogeneity instead of averaging it away. If you must report a single number, the mean of per-subject d's is far safer than a d' from pooled cells.
