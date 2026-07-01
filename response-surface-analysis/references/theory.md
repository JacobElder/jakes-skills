# Theory: the polynomial model and surface geometry

## Contents
1. The model and why difference scores fail
2. The geometry: LOC, LOIC, stationary point, principal axes
3. Exact formulas for a1–a5
4. The principal-axis parameters p10, p11
5. What each parameter answers

---

## 1. The model and why difference scores fail

A congruence hypothesis says the *agreement* between two constructs X and Y
predicts an outcome Z. The tempting shortcut is a difference score: regress Z on
`(X − Y)`, `|X − Y|`, or `(X − Y)²`. Edwards (1994, 2002) showed this is a trap.

Expand the squared difference: `(X − Y)² = X² − 2XY + Y²`. Using it as a single
predictor with coefficient `c` *imposes*, without testing, that:
- the X² and Y² coefficients are equal (both `c`),
- the XY coefficient is exactly `−2c`,
- there are no linear terms in X or Y.

These are four untested constraints, plus the difference score discards the
*level* of the pair (a (6,6) pair and a (2,2) pair have the same difference, 0)
and **compounds unreliability** — the reliability of a difference is typically
lower than that of either component, and lower still when the components
correlate. RSA fits the unconstrained model and lets you *test* those
constraints instead of assuming them.

The model (predictors centered on a common constant `c`, usually the scale
midpoint):

```
Z = b0 + b1·X + b2·Y + b3·X² + b4·XY + b5·Y² + e
```

All five non-intercept terms are entered together. The b's are not interpreted
directly; they feed the surface parameters below.

---

## 2. The geometry

Plot Z over the X–Y plane and you get a curved surface. Three lines matter:

- **Line of Congruence (LOC):** the diagonal `X = Y`. Points where the two
  predictors agree. Walking along it changes the *level* of agreement (low–low to
  high–high). Its slope and curvature are **a1** and **a2**.
- **Line of Incongruence (LOIC):** the anti-diagonal `X = −Y` (in centered
  units). Points where the predictors *disagree*, by more and more as you move
  out. Its slope and curvature are **a3** and **a4**. Congruence effects live
  here: if agreement is good, the surface should fall away as you move along the
  LOIC, i.e. an **inverted-U (a4 < 0)**.
- **First principal axis (FPA), a.k.a. the ridge:** the line on the surface with
  maximal upward (or minimal downward) curvature — the crest of the mountain. Its
  projection onto the X–Y plane is `Y = p10 + p11·X`. For a *clean* congruence
  effect the ridge must lie *on* the LOC: `p10 = 0` (no lateral shift) and
  `p11 = 1` (no rotation).

The **stationary point** `(X0, Y0)` is where the surface's gradient is zero (its
peak, valley, or saddle). The FPA passes through it.

A useful mental picture for a pure congruence surface: a long mountain ridge
running exactly along the `X = Y` diagonal; step off the ridge in either
direction (toward disagreement) and you go downhill.

---

## 3. Exact formulas for a1–a5

From the centered polynomial coefficients:

| Param | Formula | Geometric meaning |
|-------|--------------------|----------------------------------------|
| a1 | b1 + b2 | slope of the surface along the LOC at the center |
| a2 | b3 + b4 + b5 | curvature along the LOC |
| a3 | b1 − b2 | slope along the LOIC at the center |
| a4 | b3 − b4 + b5 | curvature along the LOIC |
| a5 | b3 − b5 | rotation component of the FPA (FPA ∥ LOC iff a5 = 0 given symmetry) |

Quick interpretive notes:
- **a1 > 0:** outcome rises as both predictors increase together (a level/main
  effect along agreement). A1 ≠ 0 means the congruence effect, if present, is
  *level-dependent*.
- **a2 ≠ 0:** the LOC is curved — diminishing or accelerating returns to higher
  matched levels.
- **a3 ≠ 0:** *asymmetry*. The surface is steeper on one side of the LOC than the
  other; one direction of mismatch costs more. This is the **only** parameter
  that licenses a directional claim (e.g. "overestimation is worse"), and its
  presence means the effect is not pure congruence.
- **a4 < 0:** the defining signature of a congruence effect — outcome declines as
  mismatch grows in either direction. **But a4 < 0 alone is not sufficient** (see
  `congruence-checklist.md`).

---

## 4. The principal-axis parameters p10, p11

The FPA projection `Y = p10 + p11·X` comes from the eigen-structure of the
quadratic form matrix `[[b3, b4/2], [b4/2, b5]]`. Closed forms (Edwards, 2002):

```
p11 = ( (b5 − b3) + sqrt((b3 − b5)² + b4²) ) / b4
p10 = Y0 − p11·X0
```

where the stationary point is

```
X0 = (b2·b4 − 2·b1·b5) / (4·b3·b5 − b4²)
Y0 = (b1·b4 − 2·b2·b3) / (4·b3·b5 − b4²)
```

Sign conventions for the closed-form p11 are easy to get wrong; computing the
FPA from the eigenvector of the Hessian (as `scripts/rsa_python.py` does) is
equivalent and unambiguous.

**Caution:** when the surface has little curvature (near-flat, e.g. a pure
main-effects plane), the stationary point and therefore p10/p11 are unstable or
undefined — they can blow up to huge values. This is mathematically correct: a
plane has no ridge. It is also why you gate on the block test first; never
interpret p10/p11 from a surface that failed the gate.

---

## 5. What each parameter answers

| Question | Look at |
|---|---|
| Does the outcome rise as both predictors rise together? | a1 |
| Are there diminishing returns to higher matched levels? | a2 |
| Does one direction of mismatch hurt more than the other? | a3 |
| Does mismatch in *either* direction reduce the outcome? | a4 (< 0) |
| Is the "best fit" ridge actually on the X = Y diagonal? | p10 (= 0), p11 (= 1) |
| Is the congruence effect level-independent (strict)? | a1 = 0 and a2 = 0 |

References: Edwards & Parry (1993); Edwards (2002); Shanock et al. (2010);
Humberg, Nestler & Back (2019).
