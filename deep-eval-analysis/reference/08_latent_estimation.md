# 08 — Latent Estimation (the measurement model)

This is the skill's **estimation deliverable**: model the eval responses and produce *precise
latent estimates for both items and variants on a common scale, with honest uncertainty.* Use it
when the goal is not "audit the suite" but "give me the numbers" — each skill variant's latent
ability, each eval case's difficulty and discrimination, and how confident we can be in each.
Script: `scripts/irt_latent.py`.

"Precise" here means **well-quantified, not artificially narrow.** At small N the honest estimate
has wide intervals; the engine reports them and flags low-precision rows rather than hiding the
problem. That honesty is the feature — it's what separates a real measurement model from a pass
rate dressed up as a latent score.

## What you get (every run)

- **Per-variant ability θ** with a 95% interval — the latent estimate for each skill version /
  model / ablation, on a shared scale so they're directly comparable and the ranking is robust to
  which items you happened to include.
- **Per-item difficulty b and discrimination a** with intervals — where each case sits and how
  sharply it separates variants.
- **The learned discrimination spread σ_a** — the adaptive-shrinkage state (see below).
- **A saturation read** — test information across the ability range; tells you if the suite can
  still separate your *strongest* variants.

## Choosing the backend

```
--backend auto   (default)  MCMC 2PL if PyMC is installed, else stable Rasch.
--backend mcmc              full hierarchical 2PL via PyMC: per-item difficulty AND
                            discrimination with adaptive shrinkage, exact credible intervals.
                            The headline capability. Slower (seconds–minutes).
--backend rasch            hierarchical 1PL, scipy-only, always available: difficulty + ability
                            with intervals, discrimination FIXED at 1. Fast and dependable.
--fixed-items bank.csv     anchor mode: freeze item params from a calibrated bank and estimate
                            ONLY θ per variant — the most precise small-N path when a bank exists.
```

**Why not a plain free 2PL?** Two hard facts the engine is built around:
1. *MAP/EM point estimation of 2PL discrimination is unstable.* Well-separating items push `a`
   toward infinity (perfect-separation runaway), and the variance component σ_a collapses to 0
   under a joint mode. Only full-Bayes averaging tames both — hence the 2PL path is MCMC, not a
   quick optimizer. (The `rasch` backend sidesteps this by fixing `a=1`, which is why it's the
   safe scipy default.)
2. *Item parameters are learned across variants.* With a few variants there isn't enough
   information to pin per-item discrimination freely; the hierarchical prior (or a calibrated
   bank) is what makes it estimable at all.

## Adaptive shrinkage — what σ_a means

The hierarchical 2PL pools item discriminations under `log(a_i) ~ Normal(μ, σ_a)` with a
half-Cauchy hyperprior on σ_a, and **σ_a is learned from the data**:

- **σ_a near 0 → the model is effectively Rasch, regardless of what the posterior means for a_i
  show.** The per-item discrimination estimates are prior-driven artifacts, not data-estimated.
  A spread of a_i values from 0.3 to 2.1 with σ_a ≈ 0 does not mean some items are highly
  discriminating — it means the prior has pulled them apart while the data had nothing to say.
  With fewer than ~15–20 takers, σ_a will almost always be near 0. This is the honest result;
  don't treat point estimates of a_i as informative in this regime.
- **σ_a larger → the data genuinely distinguish discriminations**, and the pooling relaxes toward full
  2PL behavior. This requires roughly 15–20+ takers before the signal exceeds the prior.

This is regularization that **tightens or loosens itself with the evidence** — the principled form
of "regularize discrimination and relax it as N grows." Variant abilities θ are deliberately *not*
pooled (kept on a fixed N(0,1) scale), because the whole point is to separate variants, not shrink
them together. See `07_small_sample_playbook.md` §5 for the theory.

## Reading the output

- **Wide θ intervals / "low precision" flags** at small N are correct, not a failure. If two
  variants' θ intervals overlap heavily, your suite *cannot* currently tell them apart — adding
  cases/seeds (size it with G-theory, `03`) or anchoring on a bank is the fix, not squinting at
  point estimates.
- **Saturation < ~0.6× mean information at the top** means the suite can't separate your best
  variants — add harder items.
- **σ_a** tells you whether you've earned the right to talk about per-item discrimination yet.
- For decisions, pair this with the reliability read from G-theory: latent θ gives the ranking;
  the dependability coefficient says whether the ranking is trustworthy.

## When to use which path

| Situation | Path |
|---|---|
| Model bank (≥~30 variants) | `--backend mcmc` (or `rasch` for a fast first pass) — full latent estimates |
| Few variants, no bank | `--backend mcmc` for honest pooled estimates with wide intervals, **or** `rasch` if PyMC unavailable; expect to add data |
| Few variants, calibrated bank exists | `--fixed-items` — the precise small-N path |
| Just need a ranking + reliability, not item params | G-theory (`03`) is lighter; come here when you specifically need latent item/variant parameters |

The audit workflow (`01`) and the CTT/G-theory/SDT passes answer "is the suite good / what do I
cut / can I trust it." This file answers "give me the latent estimates." They compose: audit
first, then estimate on the cleaned suite.

## Caveat: binarized scores

Every backend here models **binary** outcomes (pass/fail). If your eval scores are ordered rubric
levels (0/1/2, or a 1–5 quality scale), binarizing at a threshold throws away information and can
distort difficulty estimates. There is no partial-credit / graded-response model implemented yet —
that's a known gap (flagged in `HANDOFF.md`). Until it exists: binarize at a *defensible, pre-
committed* threshold (e.g., "level ≥ 2 = pass"), say which threshold you used, and note that a
graded model would recover more information from the middle levels. Don't silently binarize a rich
rubric and present the θ's as if no information was lost.
