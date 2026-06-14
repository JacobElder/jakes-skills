# Pitfalls: how RSA goes wrong, and how to catch it

Skim this before finalizing any RSA. Each entry: the error, why it's tempting,
how to detect it, the fix.

## 1. Concluding congruence from a4 alone
- **Why tempting:** a4 < 0 *is* the congruence signature, so it feels like the
  test. It isn't.
- **Detect:** any write-up that reports a4 and nothing about a3, p10, p11.
- **Fix:** require the full conjunction (C1–C4). See `congruence-checklist.md`.

## 2. Separate-mean centering
- **Why tempting:** "center your predictors" is generic regression advice, and
  software defaults sometimes mean-center each column.
- **Detect:** the two predictors were centered on different values; the LOC no
  longer corresponds to `X = Y` in raw units.
- **Fix:** center BOTH on one common constant (scale midpoint or pooled grand
  mean). Re-run.

## 3. Non-commensurable predictors
- **Why tempting:** any two predictors can be plugged into the polynomial; the
  math runs.
- **Detect:** X and Y come from different instruments, scales, or units;
  "agreement" between them has no substantive meaning.
- **Fix:** don't run RSA. Congruence is undefined. Use a different model.

## 4. Skipping (or misreading) the block test
- **Why tempting:** people jump straight to the surface parameters.
- **Detect:** no incremental-R² test reported; surface interpreted despite a flat
  model.
- **Fix:** gate on the joint test of X², XY, Y². If it fails, report linear and
  stop. (Note the converse error too: treating a *passed* gate as proof of
  congruence — it only licenses interpreting the surface.)

## 5. Interpreting p10 / p11 from a near-flat surface
- **Why tempting:** the script/package still prints numbers.
- **Detect:** wild **p10/p11** values (e.g. p11 in the dozens, p10 in the
  hundreds) alongside tiny quadratic coefficients.
- **Fix:** a plane has no ridge; the stationary point is undefined. This is a
  symptom of a failed/weak gate. Don't interpret them.
- **Don't confuse this with a cylinder-like ridge.** A *far-away stationary
  point* (huge X0/Y0) is fine **if p10/p11 themselves have tight CIs** — that
  happens when the surface is nearly a perfect symmetric trough (curvature along
  the ridge ≈ 0), so the "peak" is pushed to infinity but the ridge *direction*
  is sharply defined. Judge p10/p11 by their own CIs, not by the magnitude of the
  stationary point. The blow-up that matters for this pitfall is in p10/p11, not
  in X0/Y0.

## 6. The directionality fallacy
- **Why tempting:** stakeholders want "is over- or under-shooting worse?"
- **Detect:** a directional claim ("overestimation hurts more") paired with a
  symmetric surface (a3 ≈ 0).
- **Fix:** direction requires a3 ≠ 0, which means the effect is asymmetric, not
  pure congruence. State the limit honestly.

## 7. Underpowered RSA / ignoring reliability
- **Why tempting:** RSA looks like "just a regression with a few extra terms."
- **Detect:** small N relative to five-plus terms; unreported reliabilities; high
  r(X,Y).
- **Fix:** plan ~2–3× the linear-model N, ideally by simulation
  (`rsa_power_sim.py`). Report reliabilities; consider latent-variable RSA. Flag
  high predictor correlation, which shrinks `X − Y` variance and power.

## 8. Coefficient-fishing across many parameters
- **Why tempting:** seven interpretable parameters, surely one is significant.
- **Detect:** an exploratory hunt presented as a confirmatory test; no correction
  or pre-registration.
- **Fix:** pre-register the hypothesized surface; prefer constrained-model
  comparison (SQD/SRSQD vs. full vs. rivals) over piecemeal coefficient tests.

## 9. Range restriction along the LOIC
- **Why tempting:** invisible unless you look.
- **Detect:** almost all cases agree (few off-diagonal observations); little
  variance to estimate LOIC curvature.
- **Fix:** report the over/under/agreement frequency table; acknowledge the test
  is weak when disagreement is rare. No amount of total N fixes a thin LOIC.

## 10. Endogeneity / omitted common causes
- **Why tempting:** RSA is observational; people read it causally.
- **Detect:** causal language ("fit *causes* satisfaction") from cross-sectional
  self-reports; obvious common causes (e.g. affectivity) uncontrolled.
- **Fix:** add justified controls (carefully — see `extensions.md` on control
  variables in RSA); keep claims associational unless the design supports more.

## 11. Forcing RSA onto an interaction question
- **Why tempting:** RSA is fashionable and looks rigorous.
- **Detect:** no theoretical reason *match* (vs. a generic interaction) should
  matter; the squared-difference framing is decorative.
- **Fix:** if the question is "do X and Y interact," run moderated regression and
  say so. Reserve RSA for genuine congruence hypotheses.

## 12. Confusing this with design-of-experiments RSM
- **Why tempting:** identical name ("response surface").
- **Detect:** talk of central composite / Box–Behnken designs, desirability
  functions, finding process optima.
- **Fix:** that's the Box–Wilson optimization tradition — a different method and
  a different skill. This skill is congruence modeling.
