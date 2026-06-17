# 04 — IRT Applied to Evals

This file is **IRT used on eval data and its eval-specific pitfalls** — not how IRT works. For
model forms, ICCs, ability estimation, and assumptions, defer to the **item-response-theory
skill**. Use this only in the **model-bank regime** (≥ ~30 takers, ideally far more). In small-N
iteration, IRT is the wrong default — see `07_small_sample_playbook.md`. Script:
`scripts/irt_eval.py`.

## The eval → IRT mapping

| IRT concept | Eval-world meaning |
|---|---|
| Person / examinee | **Taker**: a model, checkpoint, skill version, or ablation |
| Latent ability θ | The taker's underlying capability on what the suite measures |
| Item | An eval case |
| Item difficulty b | How hard the case is — the θ at which pass probability is 50% |
| Item discrimination a | How sharply the case separates takers around its difficulty |
| Guessing c (3PL) | Floor pass probability independent of ability — **contamination/luck signal** |
| Response x | Pass (1) / fail (0) on that case (binarize partial credit with one declared threshold) |

Fit on a binary response matrix `Y ∈ {0,1}^(L takers × N items)`; the model jointly estimates
each taker's θ and each item's (a, b[, c]).

## The hard requirement: a taker bank

Item parameters are learned *across takers*. With a handful of versions there is no information to
estimate them — the fit returns confident noise. Every credible application of IRT to LLM
benchmarks fits on a **bank of many models** (dozens to hundreds), not on a few versions of one
system. So before fitting IRT, ensure you have either:

- a public leaderboard's per-item responses across many models, or
- your own one-time sweep running many models/tiers on the suite.

If you can't assemble ~30+ takers, **stop** and use G-theory + CTT (and fixed-item anchoring, see
below) instead. Below ~30, only a **hierarchical adaptive-shrinkage** fit is defensible, and even
then prefer to report it alongside CTT.

## What IRT tells you that CTT doesn't

1. **A latent-ability ranking that's robust to which items you happened to include.** Two suites
   with different item mixes still place takers on a comparable θ scale (CTT pass rates don't —
   they're suite-specific). This is why IRT-based rankings stay stable under item subsampling
   while raw-score rankings wobble.
2. **Difficulty and discrimination *jointly*, on a principled scale.** The discrimination
   parameter `a` is the model-based analogue of the item–rest correlation: low-`a` items are
   flat ICCs that don't separate takers → trim candidates. High-`a` mid-`b` items are your most
   informative cases.
3. **Saturation, precisely.** Plot test information against θ. If information collapses at the
   high-θ end, the suite can't distinguish your *top* takers no matter the pass rate — the formal
   version of "saturated." Items with `b` far below your takers' θ are dead weight for ranking
   frontier systems.
4. **Contamination / luck via the guessing parameter.** A 3PL `c` well above 0 on an item means
   takers pass it at a rate untethered from ability — classic on contaminated or guess-able
   multiple-choice items. A cluster of high-`c` items inflates scores without measuring capability.
5. **Mislabel auditing.** Items where high-θ takers fail and low-θ takers pass (negative effective
   discrimination under the model) surface likely **gold-label errors** — IRT-based mislabel
   detectors flag these at high precision on real benchmarks. This is the model-bank analogue of
   CTT's negative item–rest correlation, and it's one of IRT's highest-value eval uses.

## Fixed-item (anchor) calibration — the bridge to small N

The move that makes IRT useful even when you only have a few versions to *score*: **calibrate
items once on the bank, freeze (a, b[, c]), then estimate only θ for each new version against the
fixed items.** Estimating 6 abilities against known items is well-posed at any N; estimating items
*and* abilities from 6 takers is not. Workflow:

1. Assemble the bank, fit 2PL/3PL, save item parameters.
2. For each new skill version, score it on (a subset of) the calibrated items.
3. Estimate θ_version by MLE/EAP against the **fixed** item parameters; report θ with its standard
   error.

This is the tinyBenchmarks deployment pattern and the cleanest way to get a stable latent ranking
of your versions during iteration.

## IRT-based suite shrinking ("trim the fat," validated)

To cut a large suite to a small representative one without losing the ability to estimate
performance:

1. Fit IRT on the bank to get per-item (a, b).
2. Select an **anchor set** of items that are individually informative (mid-`b`, high-`a`) and
   jointly cover the θ range — e.g., cluster items by their IRT parameters and pick representatives,
   or maximize test information across the θ range you care about.
3. Estimate new takers' performance from the anchor set, optionally with an IRT-based correction
   (the `p-IRT`/`IRT++` estimators) that adjusts the raw anchor score using the fitted item
   parameters.

This reliably estimates full-suite performance from ~100 well-chosen items where naive random
subsampling is high-variance. The simpler **mid-range difficulty filter** (`02_ctt_item_analysis.md`)
is the optimization-free cousin and a fine default; IRT selection wins when you need maximum
compression with calibrated error bars and you already have the bank.

## Model choice and fitting cautions

- Prefer **2PL** (difficulty + discrimination) as the workhorse; add the **3PL** guessing
  parameter only when contamination/guessing is the actual question, since `c` is the least stable
  parameter and needs the most data.
- Below ~30 takers, only fit with **hierarchical shrinkage** on `a` (and ideally `b`); see
  `07_small_sample_playbook.md` §5. Never report a free MML 2PL fit from a tiny taker set.
- Check unidimensionality before trusting a single θ — agent suites often bundle distinct skills
  (routing vs. execution vs. format). If they don't load on one dimension, either split the suite
  or use a multidimensional IRT model and report θ per dimension.
- The script supports a Rasch (1PL) fit (statsmodels-free, scipy-based) and a 2PL fit with an
  optional log-discrimination ridge penalty as a lightweight stand-in for full hierarchical
  shrinkage; it prints a loud warning and refuses a free 2PL below the taker threshold unless
  `--force` is passed.

**For actual latent estimates** (ability per variant + difficulty/discrimination per item with
intervals), use the dedicated engine `scripts/irt_latent.py` and `08_latent_estimation.md` rather
than `irt_eval.py`. `irt_eval.py` is the *audit* tool (saturation, contamination, item flags, the
small-N guard); `irt_latent.py` is the *measurement model* (hierarchical 2PL via MCMC with adaptive
shrinkage, stable Rasch, or fixed-item anchoring).
