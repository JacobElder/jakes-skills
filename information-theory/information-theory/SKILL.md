---
name: information-theory
description: >-
  Information theory — Shannon entropy/surprisal, entropy rate, differential entropy,
  mutual information/information gain (tree splits, feature selection, Shannon diversity),
  transfer entropy, KL/relative entropy, cross-entropy or log-loss/NLL/perplexity,
  Huffman/arithmetic coding, compression=prediction, rate–distortion/information
  bottleneck, model selection via AIC/AICc/BIC/WAIC/LOO/MDL, and variational inference
  (KL direction). Also covers time-series 'entropies' — sample (SampEn), approximate,
  permutation — and disambiguates them from Shannon. Trigger on phrasings ('how much
  info does X carry', 'bits per character', 'how compressible') even when the user never
  says 'information theory.' The base model knows the formulas but misses what bites:
  estimation bias, KL direction, diff-entropy pitfalls, SampEn vs Shannon, and what each
  criterion estimates. Do NOT use for framework debugging (CrossEntropyLoss shape error),
  website 'information architecture,' or thermodynamic entropy with no Shannon content.
---

# Information Theory

Information theory has a small number of definitions and a large number of ways to
misuse them. The definitions are in every textbook and the base model already knows
them. **The value this skill adds is in the failure modes** — the places where a
confident, formula-correct answer is still wrong in practice. Lead with those.

## The seven theses (internalize these before answering)

These are the load-bearing claims. If an answer contradicts one of them, stop.

1. **Estimation is the whole game; naive plug-in is biased.** Entropy and MI computed
   by plugging empirical frequencies into the formula are *systematically* biased —
   entropy biased **down**, MI biased **up** — by roughly `(K−1)/(2N)` per entropy
   term. Most real-world information-theory errors are estimation errors, not algebra
   errors. Never report a sample entropy/MI without a bias correction and a sense of
   the uncertainty. See `reference/estimation.md`.

2. **Differential entropy is a different object, not "entropy for continuous data."**
   It can be negative, it is **not invariant** under invertible reparameterization
   (it shifts by `E[log|J|]`), and it carries units tied to the measurement scale.
   The quantities that *survive* reparameterization are **KL divergence** and
   **mutual information**. See `reference/entropy.md`.

3. **KL direction is a modeling decision, never a detail.** `KL(p‖q)` (forward,
   mass-covering, zero-avoiding) and `KL(q‖p)` (reverse, mode-seeking, zero-forcing)
   give different answers and encode different tolerances for failure. Variational
   inference uses reverse KL and therefore *underestimates* variance. Never write
   "the KL" without stating the direction and why. See `reference/divergence.md`.

4. **Cross-entropy, log-loss/NLL, MLE, and KL are one fact.** `H(p,q) = H(p) +
   KL(p‖q)`. Minimizing cross-entropy over `q` with `p` = the empirical distribution
   **is** maximum likelihood **is** minimizing `KL(empirical‖q)`. "Cross-entropy
   loss," "negative log-likelihood," and "log loss" name the same objective; bits and
   nats just change the log base. (Disambiguate from the unrelated *cross-entropy
   method* for optimization.) See `reference/divergence.md`.

5. **Compression and prediction are the same problem.** Shannon source coding bounds
   expected codelength below by entropy, and the best prefix code satisfies
   `H ≤ L < H+1`. A probabilistic model *is* a lossless compressor; arithmetic coding
   realizes ~cross-entropy bits. "Bits" is therefore the universal currency for model
   fit, and this is the bridge to MDL. See `reference/coding.md`.

6. **Model-selection criteria estimate predictive KL / expected log-loss — and AIC
   vs BIC answer different questions.** AIC ≈ an unbiased estimate of out-of-sample
   deviance (expected KL up to a constant), penalty `2k`, asymptotically = LOO-CV,
   *efficient but not consistent*. BIC ≈ `−2 log` marginal likelihood via Laplace,
   penalty `k·ln n`, *consistent if the true model is among the candidates* — which it
   usually isn't. "Which is better" is mostly a category error. See
   `reference/model-selection.md`.

7. **"Entropy" is an overloaded word; pin the lineage before computing.** Sample
   entropy (SampEn), approximate entropy (ApEn), permutation/multiscale/spectral
   entropy are **time-series regularity statistics** (Pincus; Richman–Moorman;
   Bandt–Pompe), not Shannon information. They measure how predictable the next value
   is, are destroyed by shuffling, and are **not in bits** — never average them with or
   substitute them for Shannon entropy/MI, and never `log2` a SampEn value. If the user
   has a *distribution*, it's Shannon (this skill's core); if they have an *ordered
   signal* and ask about complexity/regularity/HRV/EEG, it's the SampEn family. When the
   bare word "entropy" is ambiguous, ask which question they're asking. See
   `reference/entropy.md` and `scripts/sample_entropy.py`.

## Routing table

Read the reference file before answering anything non-trivial in its area. Each is
self-contained and dense; do not reconstruct this content from memory.

| If the question touches…                                                              | Read                              |
|---------------------------------------------------------------------------------------|-----------------------------------|
| Shannon/joint/conditional entropy, **entropy rate** (per-symbol, Markov, bits/char), differential entropy, max-entropy, Rényi/Tsallis | `reference/entropy.md` |
| **Sample/approximate/permutation/multiscale/spectral entropy** (time-series regularity, *not* Shannon) | `reference/entropy.md` + `scripts/sample_entropy.py` |
| KL/relative entropy, cross-entropy, f-divergences, MLE bridge, proper scoring rules, **Fisher information / information geometry** | `reference/divergence.md` |
| Mutual information, information gain, data-processing inequality, **Fano's inequality**, multivariate info, **transfer entropy / directed information** | `reference/mutual-information.md` + `scripts/entropy_mi_estimators.py` |
| **Estimating** any of the above from finite samples (bias, MM, NSB, KSG, MINE, CIs)   | `reference/estimation.md`         |
| Source coding, Kraft, Huffman, arithmetic coding, compression = prediction, MDL bridge, **rate–distortion & information bottleneck** (lossy) | `reference/coding.md` |
| AIC / AICc / BIC / WAIC / LOO / DIC / MDL / NML, the AIC-vs-BIC debate, recipes        | `reference/model-selection.md`    |

## Scripts (prefer these over re-deriving)

Run with `python3`; both have a `--selftest` that prints verified numbers against
closed-form ground truth. Read the file header for the API.

- `scripts/entropy_mi_estimators.py` — plug-in vs Miller–Madow entropy, plug-in MI
  with bias demonstration, a KSG k-NN estimator for **continuous** MI validated
  against the bivariate-Gaussian closed form `I = −½ ln(1−ρ²)`, and **transfer entropy**
  (discrete with a permutation null, plus a Gaussian closed form cross-checked against a
  known linear VAR — directionality recovered, reverse direction at chance).
- `scripts/info_criteria.py` — AIC, AICc, BIC from a log-likelihood; WAIC from a
  pointwise log-likelihood matrix; a polynomial-order selftest showing the criteria
  recover the generating model and where AIC and BIC diverge.
- `scripts/sample_entropy.py` — the time-series regularity family (**not** Shannon):
  sample entropy (SampEn), approximate entropy (ApEn), and permutation entropy,
  cross-validated against `antropy`. Use this when the user means complexity/regularity
  of an ordered signal, and read thesis #7 before reaching for it.

## How to answer (workflow)

1. **Name the object precisely.** Discrete entropy vs differential entropy; which KL
   direction; population quantity vs sample estimate. Most confusion dissolves here.
2. **If data is finite and real, treat it as an estimation problem.** Reach for
   `reference/estimation.md` and the estimator script before quoting a number.
3. **State units.** Bits (log₂) or nats (ln). Perplexity = `exp(H)` in the matching
   base. Keep them consistent end to end.
4. **Give the honest caveat, not the textbook caveat.** E.g. "MI here is invariant to
   monotone rescaling, which is why it found this relationship that Pearson r missed —
   but it's estimated from 80 points, so treat the magnitude as a rank, not a value."
5. **Show the small computation** when a closed form exists (Gaussian entropy, binary
   entropy, KL between Gaussians); use a script when it's an estimate from data.

## Opinionated defaults

- Estimating entropy/MI from counts: **Miller–Madow minimum**, NSB or Chao–Shen when
  undersampled (`N` not ≫ number of categories). Continuous MI: **KSG (k-NN)**, not
  fixed-bin histograms. Report a bootstrap or shuffle-based interval.
- Comparing models for **prediction**: AIC / AICc, or better, **LOO-CV / PSIS-LOO**
  (WAIC for Bayesian). Comparing for **"which is the true sparse model"**: BIC, knowing
  the assumption you're buying. Don't average the two criteria; pick the one whose
  target loss matches the question.
- "How surprising / how much information": work in **bits** for communication and
  storage framing, **nats** for anything you'll differentiate (it removes `ln 2`
  factors). Be explicit either way.
- Never let a polish/cleanup pass soften thesis #1 or #3 into "you may wish to
  consider bias correction." The bias is not optional; it is the answer.
