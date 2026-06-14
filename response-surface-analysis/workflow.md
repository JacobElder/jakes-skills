# Workflow: from question to report

A concrete recipe. Each step has a failure mode that should stop you.

## Step 0 — Is this a congruence question? (frame)

Confirm three things before touching data:
- **Two predictors, one outcome**, and the *match between the predictors* is the
  theoretical interest (fit, agreement, similarity, discrepancy).
- **Commensurability:** X and Y are on the *same metric*. Same instrument, same
  anchors, same units. (Self-rated competence vs. job-demanded competence on the
  same 1–7 scale: yes. Salary in dollars vs. satisfaction in Likert: no.)
- **A reason match should matter.** If the theory is just "X and Y interact,"
  use a plain moderated regression and say so. RSA is for *congruence*, not any
  curved surface.

STOP if predictors aren't commensurable — congruence is undefined.

## Step 1 — Center on a common constant

Subtract ONE value from BOTH predictors: the scale midpoint (e.g. 4 on 1–7) or a
pooled grand mean. Never center each predictor on its own mean. After centering,
`X = Y` (the LOC) corresponds to genuine agreement and `X = −Y` (the LOIC) to
genuine disagreement.

FAILURE MODE: separate-mean centering. It moves the LOC off the agreement
diagonal and silently corrupts a1–a5, p10, p11. If you inherit an analysis, check
how it was centered first.

## Step 2 — Descriptives and feasibility

- Tabulate how many cases fall *above*, *below*, and *in agreement* (within, say,
  half a scale point) on the two predictors (Shanock et al., 2010 Step 1). If
  almost everyone agrees, there is little variance along the LOIC and the
  congruence test is underpowered no matter the N.
- Check predictor correlation. High r(X,Y) shrinks variance in `X − Y` — the
  congruence dimension — and tanks power. Report it.
- Check reliability of both predictors. Measurement error attenuates the
  higher-order terms most. Note it; consider latent-variable RSA (see
  `extensions.md`) if reliabilities are modest.

## Step 3 — The block test (gate)

Fit the linear model `Z ~ X + Y` and the full model
`Z ~ X + Y + X² + XY + Y²`. Test whether the three higher-order terms *jointly*
add R² (incremental F, or LR test). 

GATE: if they don't (p ≥ your α), you do not have a surface. Report the linear
model and STOP. Do not interpret a1–a5 or p10/p11 — and remember that *passing*
the gate is necessary but not sufficient for congruence.

## Step 4 — Estimate parameters with bootstrap CIs

Fit the full model. Compute a1–a5, p10, p11. Get **bootstrap percentile CIs** for
all of them (2000+ resamples). Delta-method SEs are unreliable for these
nonlinear functions in typical samples.

## Step 5 — Evaluate congruence (checklist or model comparison)

Run `references/congruence-checklist.md`:
- Broad congruence: a4 < 0, a3 = 0, p10 = 0, p11 = 1 (all four).
- Strict congruence: also a1 = 0 and a2 = 0.
Or, for confirmatory work, compare a pre-registered constrained model (SQD /
SRSQD) against the full polynomial and named rivals via AIC/BIC + LR tests.

Interpret a3 carefully: only if a3 ≠ 0 may you make a directional claim, and that
means the effect is asymmetric rather than pure congruence.

## Step 6 — Plot

Render the 3-D surface with the LOC, LOIC, and first principal axis drawn on it.
A contour plot is a useful companion. The picture should match the parameter
story; if it doesn't, recheck centering and the gate.

## Step 7 — Report

A complete RSA report contains, at minimum:

```
- N, and a power/sample-size justification (ideally a simulation for the
  hypothesized surface; at least an argument that N exceeds 2–3× the linear-model
  requirement).
- Predictor reliabilities and r(X, Y); the agreement/over/under frequency table.
- How predictors were centered (the common constant used).
- The full polynomial coefficients (b1–b5) with SEs.
- The block test: ΔR² and its F/LR test.
- a1–a5, p10, p11, each with bootstrap CIs.
- The congruence verdict stated as a conjunction (which conditions held / failed),
  OR the model-comparison table if you used that route.
- A surface plot with LOC/LOIC/FPA.
- An explicit statement of broad vs. strict, and — if a3 ≈ 0 — an explicit note
  that the surface does NOT speak to direction of mismatch.
```

Things reviewers catch and you should pre-empt: claiming congruence from a4
alone; reading direction off a symmetric surface; not reporting how centering was
done; interpreting p10/p11 from a surface that failed the gate; and an N that
could not plausibly detect the curvature claimed.
