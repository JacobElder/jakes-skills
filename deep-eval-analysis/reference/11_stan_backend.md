# 11 — Stan / RStan backend (version-proof alternative to PyMC)

The joint engine is also available as a plain **Stan model** (`stan/joint_glmm.stan`) with runners
for Python and R. Use it when PyMC is unavailable or pinned to a version you can't change — Stan's
language is far more stable across releases than any Python modeling API, and the same model file
drives cmdstanpy (Python), cmdstanr, or RStan (R).

```
# Python (CmdStanPy)
python stan/run_cmdstanpy.py results.csv --channels acc,latency,confidence --slip --out joint.json
python scripts/synthesize.py joint.json --fig synthesis.png

# R (cmdstanr or rstan)
Rscript stan/run_rstan.R results.csv acc,latency,confidence cot_len slip
python scripts/synthesize.py joint.json --fig synthesis.png
```

Both runners emit the **same JSON schema** as `scripts/joint_glmm.py`, so `synthesize.py` works on a
Stan fit unchanged — the whole synthesis/visualization layer is backend-agnostic.

## Why Stan here (the version story)

PyMC has had hard API breaks. If your approved PyMC is **3.x**, the engine's PyMC script will not
run at all — v3 used the Theano backend, returned `MultiTrace` rather than `InferenceData`, and had
a different `pm.math`. An older **5.x** will likely run with minor edits. Rather than carry
version-specific PyMC code paths, use the Stan model: it is one artifact that runs everywhere.

Two Stan-side compatibility choices already made for you:
- **Old array syntax.** The model uses `int tv[N]` / `vector[N] lnT`, not the post-2.26
  `array[N] int tv`. Old syntax parses on both old and new Stan; the new syntax does not parse on
  older RStan. So an older approved RStan will accept this file.
- **No exotic functions.** Probit via `Phi`, half-priors via `<lower=0>` bounds — nothing that
  moved between releases.

## brms — the lowest-risk R path

If you're in R, `stan/brms_alternative.R` expresses the accuracy (2PL) and latency channels as a
multivariate GLMM and lets **brms generate Stan for whatever version you have installed** — which
removes both the hand-written-Stan risk and the PyMC-version problem. It covers most of the model;
the 4PL slip needs a custom brms family, so for that use the hand-written `joint_glmm.stan`. The
shared `(1 | v | taker_id)` grouping across the two responses is what estimates the ability↔effort
correlation (the van der Linden term), and `VarCorr(fit)` gives the G-theory variance components.

## PyMC ↔ Stan correspondence (they are the same model)

| Quantity | PyMC (`joint_glmm.py`) | Stan (`joint_glmm.stan`) |
|---|---|---|
| ability | `theta ~ Normal(0,1)` | `theta ~ std_normal()` |
| difficulty | `b ~ Normal(mu_b, sig_b)` | identical |
| log-discrimination | `loga ~ Normal(mu_la, sig_la)`, `sig_la ~ HalfCauchy(0.5)` | identical (adaptive shrinkage) |
| accuracy link | `invprobit(a·(θ−b))` | `Phi(a·(θ−b))` |
| 4PL slip | `Beta(20,1)` upper asymptote | `d_up ~ beta(20,1)` |
| latency | `lnT ~ Normal(λ−κ·τ, σ_T)` | identical |
| θ–τ correlation | `τ = ρ·θ + √(1−ρ²)·e` | identical |
| calibration | `logit(conf) ~ Normal(g0+(g1+gc)(θ−b), σ_C)` | identical |

Priors and parameterization match line-for-line, so the two backends should agree within MC error.

## Verify first (because this wasn't compiled where it was written)

The Stan model was written to mirror the tested PyMC model but compiled/checked **in your
environment**, not where it was authored. First two steps there:
1. `stanc stan/joint_glmm.stan` (or let the runner compile) to confirm it parses on your toolchain.
2. Run both backends on the same CSV and confirm θ ranks and item parameters agree within Monte
   Carlo error — this is the cross-backend agreement check (also in `HANDOFF.md`). Once it passes,
   pick whichever backend your environment blesses; the synthesis layer doesn't care which produced
   the JSON.
