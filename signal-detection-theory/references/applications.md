# SDT Applications and Live Debates

SDT travels well: any two-class discrimination with a tunable threshold is an SDT problem. This file covers the major application domains and — importantly — the places where serious researchers still disagree, so you can present them even-handedly instead of picking a side.

## Recognition memory (old/new)

The canonical cognitive application. Subjects study items, then judge test items as "old" (studied) or "new". Hits = correctly calling old items old; false alarms = calling new items old.

- The recognition z-ROC is consistently **non-unit-slope (≈ 0.8)**: the "old"/target evidence distribution is *wider* than the "new"/lure distribution. So single-point d' is biased here; use d_a / A_z from a confidence ROC.

### Live debate: UVSD vs DPSD (why slope < 1)
- **Unequal-Variance Signal Detection (UVSD):** a single continuous memory-strength signal, with greater variance for targets (because studied items vary in how well they were encoded). Slope < 1 falls out naturally. (Wixted; Mickes; Rotello.)
- **Dual-Process Signal Detection (DPSD):** recognition reflects *two* processes — a continuous **familiarity** signal plus a thresholded **recollection** process — and their mixture bends the z-ROC. (Yonelinas.)
- Both fit standard ROCs well; they diverge on finer predictions (z-ROC curvature, source-memory ROCs, RT-distribution constraints). **This is unresolved. Present both; don't declare a winner.** When someone reports a recognition d' from a single point, the useful contribution is usually "fit the ROC and report d_a, and note which model you're assuming."

## Eyewitness identification

A high-stakes applied case that turns entirely on the sensitivity-vs-bias distinction.

- For decades the field compared lineup procedures using the **diagnosticity ratio** = (correct ID rate)/(false ID rate). Wixted & Mickes (2012, 2014) showed this **confounds discriminability with response bias**: a procedure that merely makes witnesses more cautious raises the ratio without improving their actual ability to tell guilty from innocent suspects. So ranking procedures by diagnosticity is unsound.
- Their fix: collect confidence and build an **ROC** (correct-ID rate vs. false-ID rate across confidence), then compare **AUC** (partial AUC, since only the suspect-ID region is meaningful).

### Live debate: ROC vs. the full lineup structure
- **Wixted & Mickes:** ROC/AUC is the right way to measure witnesses' underlying discriminability independent of bias.
- **Wells, Smalarz, Yang and colleagues:** forcing a real **3×2** lineup (suspect ID / filler ID / rejection × guilty-suspect-present / -absent) into the **2×2** an ROC needs **discards diagnostic information** — filler IDs and rejections carry exonerating value that the 2×2 reduction hides; "filler siphoning" matters; a Bayesian family of diagnosticity functions may capture more.
- Both sides have conceded points to the other. The defensible synthesis: **the diagnosticity-ratio critique is correct (don't rank procedures by a bias-confounded ratio), AND the 2×2 reduction does lose lineup-specific structure.** Use ROC/AUC for the discriminability question; don't pretend it answers every applied question about lineups.

## Medical and machine-learning diagnostics

- A diagnostic test (or ML classifier) with a tunable threshold is pure SDT: sensitivity = hit rate, 1 − specificity = false-alarm rate, the **ROC is the SDT ROC**, and **AUC = A_z** (the model-based version) or the empirical area.
- The threshold a clinician/operator picks **is the criterion**, set by the relative costs of misses vs. false alarms and the base rate — exactly β's job. Moving the threshold trades sensitivity for specificity along the fixed ROC; it does **not** change the test's underlying discriminability.
- This is why "accuracy" is a poor headline for an imbalanced diagnostic problem: it conflates the test's discriminability with the chosen operating point and the base rate. Report AUC (discriminability) *and* the chosen operating point with its sensitivity/specificity (the criterion), not a single accuracy number — the same sensitivity/bias split as everywhere else in SDT.

## SDT for LLM and AI classifiers (the current frontier)

Increasingly, SDT is used to analyze model behavior, and it's a natural fit for evaluation work:

- Treat an LLM doing a binary judgment (toxic/not, relevant/not, violation/not) as an observer: its **discriminability** (can it tell the classes apart?) is separable from its **yes-bias** (how readily it says "positive?").
- Decoding **temperature**, **prompt framing**, **persona**, or a **decision-threshold prompt** primarily shift the *criterion*, while leaving discriminability roughly fixed — so a model that flags "more violations" under one persona may be *more liberal*, not *more accurate*. Reporting only positive-rate or accuracy hides this; reporting d' and c separates it. (Recent work applies exactly this lens to LLM moral-judgment and classification bias.)
- Practical upshot for eval design: when comparing prompts/models on a binary task, fit d' and c (or AUC + operating point), not just F1/accuracy, so you don't mistake a criterion shift for a capability change. This connects directly to ROC-based ML evaluation — the difference is only whether you bring in the latent-evidence framing.

**Key references (recent, directly applicable):**
- **Cacioli, J.-P. (2026). "LLMs as Signal Detectors: Sensitivity, Bias, and the Temperature–Criterion Analogy." arXiv:2603.14893.** Pre-registered; treats 3 LLMs as observers over 168,000 factual-discrimination trials. Finds all models show **unequal-variance evidence distributions (z-ROC slopes 0.52–0.84**, with instruct models *more* asymmetric, 0.52–0.63, than the base model 0.77–0.87 or human recognition memory ≈0.80). Key result: **temperature is not a clean criterion shift** — it raises sensitivity (AUC) *and* moves the criterion, because temperature changes the generated answer itself, not just the confidence attached to it. Models at distinct points in sensitivity–bias space are indistinguishable by calibration metrics (ECE) alone — the SDT decomposition recovers structure those metrics hide.
- **Cacioli, J.-P. (2026). "Do LLMs Know What They Know? Measuring Metacognitive Efficiency with Signal Detection Theory." arXiv:2603.25112.** Companion paper applying **type-2 SDT (meta-d', M-ratio)** to LLMs via internal token log-probabilities (avoiding the discretization of prompted confidence scales). Argues ECE/Brier conflate type-1 knowledge with type-2 self-monitoring; meta-d'/M-ratio separates them (cf. `metacognition.md`).
- **Dai, Y. (2026). "Rescaling Confidence: What Scale Design Reveals about LLM Metacognition." arXiv:2603.09309.** Concurrently applies meta-d' to LLMs using prompted verbal confidence, reporting M-ratios ≈ 0.62–0.92.

These are the clearest worked demonstrations that the full parametric SDT framework — not just AUROC — adds diagnostic value for LLM evaluation, and they make excellent templates for eval design in this skill's domain.

## Other domains (briefly)

- **Vigilance / sustained attention:** the "vigilance decrement" over time is often a **criterion shift** (observers get more conservative), not a sensitivity loss — SDT is what lets you tell which.
- **Psychophysics / perception:** the origin of SDT; detection and discrimination thresholds, often via m-AFC to neutralize bias.
- **Deception/lie detection:** truth/lie discrimination; A'/B'' are common in this literature (often poorly justified — see `formulas.md` §7).
- **Survey/clinical screening:** a screener with a cutoff (e.g., CBCL ≥ 10) is an SDT criterion on an observed decision variable.
