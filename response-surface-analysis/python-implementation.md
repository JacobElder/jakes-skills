# Python implementation — `scripts/rsa_python.py`

There is no mature, maintained Python package for congruence RSA, so this skill
ships a transparent one. It mirrors what the R `RSA` package does for the common
single-level case: polynomial fit, surface parameters with bootstrap CIs, the
block-test gate, the automated congruence checklist, and a 3-D plot. Use it when
the project is Python-native; for the full constrained-model family and dyadic /
multilevel designs, fall back to R.

## CLI

```bash
python scripts/rsa_python.py data.csv \
    --x self --y other --z outcome \
    --midpoint 4 \
    --plot surface.png
```

- `--midpoint` is the common centering constant (the scale midpoint). **Always
  supply it.** If omitted, the script emits a loud stderr warning and falls back
  to the pooled data midpoint — which shifts with sample composition and silently
  corrupts a1–a5 and the LOC. Do not suppress or ignore that warning.
- Output includes the b's, the block test (with an explicit STOP message if the
  surface isn't justified), every surface parameter with a 95% bootstrap CI, an
  explicit directionality note keyed to the a3 CI (symmetric vs. asymmetric), and
  the broad/strict checklist verdict.

## As a library

```python
import pandas as pd
from rsa_python import fit_rsa

df = pd.read_csv("data.csv")
res = fit_rsa(df, x="self", y="other", z="outcome", center=4.0, n_boot=2000)

res.summary()                 # prints coefficients, block test, params, checklist
res.checklist()               # dict: each condition -> bool (broad & strict)
res.params                    # a1..a5, p10, p11, stationary point
res.ci                        # bootstrap CIs for each parameter
res.r2_full, res.r2_linear    # for the block test
res.block_F, res.block_p
res.plot("surface.png")       # 3-D surface with LOC (white) and LOIC (red)
```

## What it does, precisely

- **Centering:** subtracts one constant from both predictors. Emits a
  commensurability warning if the two predictors differ markedly in range or
  level — a heuristic nudge to confirm they're on the same metric, not a
  substitute for judgment.
- **Block test (gate):** compares full vs. linear via an incremental F. If
  `p ≥ .05`, `summary()` tells the user the surface isn't justified and to report
  a linear model. Honor that — don't interpret the parameters past a failed gate.
- **Surface parameters:** a1–a5 by the standard formulas; p10/p11 from the
  eigen-structure of the Hessian (sign-convention-safe), with the stationary
  point.
- **Bootstrap CIs:** percentile CIs over 2000 (default) row resamples for every
  parameter — the right inference for these nonlinear functions of the b's.
- **Checklist:** evaluates C1–C4 (broad) and C5–C6 (strict) from the CIs and
  prints PASS/fail per condition, with a standing reminder that a4 < 0 alone is
  insufficient.

## Limitations (use R instead when these bite)

- Single-level only. No multilevel or dyadic estimation.
- OLS, observed-variable. No latent-variable / errors-in-variables correction;
  if predictor reliabilities are modest, prefer SEM-based RSA in R (`extensions.md`).
- Fits the full polynomial and tests the checklist; it does **not** fit the whole
  constrained model family (SQD/SRSQD/RR/…) for AIC/BIC model comparison. For the
  confirmatory model-comparison route, use the R package.
- Quadratic only (no cubic terms). For asymmetric/level-dependent congruence via
  third-order models, use cubic RSA in R.

## Power planning — `scripts/rsa_power_sim.py`

Simulation-based power for the broad-congruence verdict, using the same
estimator so power reflects the analysis you'll actually run:

```bash
python scripts/rsa_power_sim.py --n 150 250 400 --k 0.3 --s 0 --rxy 0.4 --reps 500
```

- `--k` LOIC curvature strength (effect size of the congruence effect),
- `--s` LOC slope (0 = strict congruence; > 0 = level-dependent / broad),
- `--rxy` predictor correlation (higher → lower power; it shrinks `X − Y` variance),
- `--sd-resid` residual SD (noise).

It reports, per N, the probability that *all four* broad-congruence conditions
are simultaneously met — a stricter, more honest target than "a4 is significant."
