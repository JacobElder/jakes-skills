# 09 — The Unified Joint GLMM (IRT + SDT + Calibration + G-theory from one fit)

IRT, SDT, calibration, and the variance-components core of G-theory are all readings of one
**generalized linear mixed model.** So yes — you can fit a single hierarchical model and read every
framework's parameters off the same posterior. `scripts/joint_glmm.py` does this. This file is also
the skill's honest answer to "can't I just put it all in one big Stan model?" — the framework is
real, but the small-N caveats are load-bearing.

Backends: `scripts/joint_glmm.py` (PyMC) is the reference implementation. The same model is also a
version-proof **Stan** program — `stan/joint_glmm.stan` with Python and R runners that emit the
identical JSON — for environments with an old/pinned PyMC or an RStan/brms house style. See
`reference/11_stan_backend.md`.

## What comes out of one fit

| Framework | Parameter | Where it comes from |
|---|---|---|
| IRT | item difficulty `b`, discrimination `a`, optional 4PL upper asymptote (slip) | accuracy channel, hierarchical |
| SDT | sensitivity & criterion | the *probit* reading of the accuracy channel: `a_i` = detection sensitivity per unit ability, `b_i` = criterion. d′ between two variants on item i = `a_i·(θ₁−θ₂)` |
| Calibration | per-variant confidence-vs-correctness slope | optional confidence channel (Beta/Gaussian-on-logit) |
| G-theory | reliability | IRT empirical (marginal) reliability `ρ = Var(θ̂)/(Var(θ̂)+mean posterior var)` — the latent analogue of Eρ². Full crossed-facet Eρ²/Φ come from adding judge/seed random effects (or use `gtheory_eval.py`) |

The variant traits (ability θ, and latent speed τ if the latency channel is on) are drawn together
so their correlation is estimated, not assumed.

## The two ideas worth importing (and what they actually buy you)

**1. Latency / CoT-length channel (van der Linden, 2007) — the real identifiability win.**
Model log-latency as `ln T_vi = λ_i − κ·τ_v + ε`, with τ_v (variant speed) correlated with θ_v
(ability). Because the two traits share a covariance, the latency data *informs the ability
estimate*. With only a few variants this is the single best lever for precision: every extra
response channel per cell is extra information about that variant. Demonstrated: on an 8-variant ×
25-item fixture with planted corr(θ,τ)=0.6, adding the channel recovered ρ≈0.59 and shrank the mean
θ posterior SD. **But:** the gain's *size* depends on how strongly latency and accuracy actually
couple in your data, and the correlation itself is weakly identified at small N (wide interval) —
the channel still helps θ, but don't over-read the correlation point estimate. Also note the LLM
caveat: CoT length ↔ accuracy coupling is often *verbosity*- or *reasoning-effort*-ability, and the
sign can flip (more reasoning helps on hard items; more tokens also means more chances to derail).
It is not the clean "faster = abler" of human RT.

**2. 4PL upper asymptote / slip ("Lost in Benchmarks").** The upper asymptote `d_i<1` captures items
even the best variants miss — label noise, ambiguous gold answers, format brittleness. This is the
formal version of the skill's saturation/contamination flag. It is appropriate in the **bank
regime** (dozens+ of variants), where it is genuinely estimated. At small N it sits at its
`Beta(20,1)` prior and is a *robustness device* (it stops a couple of slips from wrecking an item's
difficulty), **not** a measured carelessness rate — the engine prints exactly this warning. Read
small-N slip<~0.85 as "flagged for review," not as a number.

## Which token count actually helps (since latency is rarely logged but tokens always are)

The channel needs *variant*-level variance that *correlates with ability*. Token counts differ
sharply on this:

- **Output tokens / CoT length** — this *is* the channel above (pass `--effort-col output_tokens`).
  A variant's characteristic reasoning length carries ability-correlated signal, so it buys
  identifiability, same modest data-dependent magnitude. The default `cot_len` is output-length-like.
- **Input tokens** — mostly useless for separating variants: input is fixed by the item (same eval
  prompt for every variant); the only variant-level variation is how verbose the *skill/system
  prompt* is, which is footprint, not ability. Exception: multi-turn agent evals, where cumulative
  input tokens ≈ trajectory length / turn count — and that *does* track ability. If you're there,
  feed turn count, not raw input tokens.
- **Total tokens** — usually output-dominated on reasoning tasks, so it behaves like output, diluted
  by the input component.

**The length-bias trap (token count is dirtier than latency).** LLM-judge graders often reward
longer answers. If your accuracy grader is length-biased *and* you feed output length as an
ability-correlated channel, the channel is partly the *same* signal the grader already used — not
independent information — and the model manufactures apparent ability separation. Wall-clock latency
doesn't have this problem (the grader never sees it), which is the one way true latency beats token
count. Before trusting an output-token channel, check the judge for length bias (`judge_calibration.py`);
if it's biased, discount the gain or prefer latency/turn-count.

## The honest feasibility verdict (read before building the mega-model)

The "one multivariate Stan model, correlated covariance matrix shares strength across channels"
pitch is correct in principle and seductive — and it hides the trap that this whole skill exists to
flag. **At a handful of variants you cannot *estimate* a rich trait covariance; you *assert* it via
priors, and the resulting precision is manufactured, not measured.** A 5×5 trait covariance from 6
variants is 6 data points informing 10 correlations — the posterior is the LKJ prior wearing a data
costume. The more channels you stack, the more the model "borrows strength," but borrowed from
priors is not the same as learned from data.

Consequences for design:
- **Modular by default, joint when earned.** Fit only what the data support. The skill's separate
  scripts (`eval_item_analysis`, `gtheory_eval`, `sdt_trigger`, `irt_latent`) are the right default
  for the small-N iteration regime precisely because they fail *loudly* on the underpowered piece
  instead of burying it in a monolith. Reach for `joint_glmm.py` when (a) you're in the bank regime,
  or (b) you have extra channels (latency/confidence) that genuinely add per-cell information.
- **Estimate few correlations, not many.** `joint_glmm.py` estimates a single θ–τ correlation and
  warns at small N. For >2 correlated traits, use `--decouple` and report traits independently
  rather than trusting an LKJ-shaped covariance.
- **SDT for triggering is a *different response process*, not the same θ.** Merging task-ability IRT
  and trigger-bias SDT into one latent variable is a category error. The correct unification is a
  *correlated trait vector* (one variant has a task-ability trait AND a separate trigger-sensitivity
  trait, allowed to covary), with each response channel loading on the relevant trait — not one θ
  doing both jobs. Until a trigger channel is added here, keep triggering in `sdt_trigger.py`.
- **G-theory "for free" needs the facets.** You only get a judge or seed variance component if the
  design actually crosses/nests enough levels of that facet (a variance from 2 judges is worthless).
  The joint model reproduces `gtheory_eval.py` only when those random effects are present and
  estimable.

## When to use this vs. the modular scripts

- Few variants, single channel, iterating fast → modular scripts; this engine is overkill.
- Few variants BUT you log latency and/or confidence → `joint_glmm.py --channels acc,latency[,confidence]`
  to convert those channels into ability precision.
- Bank regime, want the full picture in one object → `joint_glmm.py` with `--slip`, all channels.
- You specifically want only latent ability/difficulty estimates → `irt_latent.py` is lighter.

This engine is a faithful **demonstrator**, not yet a validated instrument: like `irt_latent.py` it
needs simulation-based calibration across regimes (recover known params, check HDI coverage) before
its numbers are trusted for a ship decision. That validation is a `HANDOFF.md` task.
