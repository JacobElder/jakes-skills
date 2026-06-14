# The congruence checklist (Humberg, Nestler & Back, 2019)

This is the most important reference in the skill. Read it whenever a user wants
to *claim* a congruence effect. The central message: **a congruence effect is a
pattern, not a coefficient.** You verify the whole pattern or you don't claim it.

## The two fallacies to refuse

**Fallacy 1 — the single-parameter fallacy.** "a4 is significant and negative,
so there's a congruence effect." False. A negative a4 only says the surface
curves downward along the LOIC. The ridge could be rotated off the diagonal, or
shifted sideways, or the inverted-U could peak somewhere other than the
congruent point — any of which means the effect is *not* congruence. You must
check a4, a3, p10, and p11 together.

**Fallacy 2 — the directionality fallacy.** "There's a congruence effect, and
the surface shows overestimation is worse than underestimation." If the effect is
*pure* congruence, the surface is symmetric about the LOC and says nothing about
which direction of mismatch is worse. A directional claim requires asymmetry
(a3 ≠ 0), and that asymmetry means you no longer have pure congruence. You can't
have it both ways.

## Broad congruence — the four conditions (all required)

A surface shows a **broad** congruence effect (congruence helps, possibly
alongside main effects) iff *all four* hold simultaneously:

| # | Condition | Reads as | CI check |
|---|-----------|----------|----------|
| C1 | **a4 < 0** | inverted-U over the LOIC: mismatch in either direction lowers the outcome | CI for a4 lies entirely below 0 |
| C2 | **a3 = 0** | symmetric: the inverted-U peaks *at* the congruent point, not off to one side | CI for a3 includes 0 |
| C3 | **p10 = 0** | the ridge is not shifted laterally off the LOC | CI for p10 includes 0 |
| C4 | **p11 = 1** | the ridge is not rotated away from the LOC | CI for p11 includes 1 |

C1 and C2 together say the LOIC cross-section is an inverted-U maximized at (0,0).
C3 and C4 together say the ridge of the whole surface coincides with the diagonal
`X = Y`. Only when both pairs hold does "more agreement → better outcome" actually
describe the surface.

"Broad" permits main effects: the outcome may also rise along the LOC (a1 > 0) or
curve along it (a2 ≠ 0). That's fine — congruence and level effects can coexist.

## Strict congruence — two more conditions

A **strict** congruence effect means *only* agreement matters — the level of the
matched pair is irrelevant. Add:

| # | Condition | Reads as |
|---|-----------|----------|
| C5 | **a1 = 0** | flat ridge: a low–low match is as good as a high–high match |
| C6 | **a2 = 0** | no curvature along the ridge either |

Strict congruence is a strong claim and rarely holds exactly; broad congruence is
usually the honest target. Report which one you tested.

## "Significant" means the CI excludes the reference value

Because a1–a5, p10, p11 are nonlinear functions of the regression coefficients,
test them with **bootstrap** (or otherwise simulation-based) confidence
intervals, not naive delta-method SEs. The reference value is 0 for the a's and
p10, and **1** for p11. `scripts/rsa_python.py` and the R `RSA` package both do
this; the Python script prints the checklist verdict automatically.

## The model-comparison view (preferred for confirmatory work)

Testing four-to-six conditions one at a time multiplies error rates. A cleaner
route, available in the R `RSA` package, is to fit the *constrained* congruence
model — the shifted/rotated squared-difference model (`SRSQD`) for broad
congruence, or the basic squared-difference model (`SQD`) for strict — and
compare it to the full second-order polynomial and to named rival models (rising
ridge `RR`, etc.) using likelihood-ratio tests and AIC/BIC weights.

The logic: if your pre-registered congruence model fits **as well as** the full
polynomial (the constraints don't significantly worsen fit) and **better than**
the rivals, that is coherent, multiple-comparison-honest evidence for congruence.
A constrained model that the full model significantly beats is a congruence
hypothesis the data reject. Pre-register the target model and the rivals.

## One-paragraph decision rule

> Gate on the block test. If it passes, fit the full polynomial and bootstrap
> a1–a5, p10, p11. Check C1–C4 for broad congruence (add C5–C6 for strict).
> Report the verdict as a conjunction, never from a4 alone, and never read
> direction off a symmetric surface. For confirmatory claims, prefer comparing a
> pre-registered constrained model against the full and rival models.

Reference: Humberg, S., Nestler, S., & Back, M. D. (2019). Response Surface
Analysis in Personality and Social Psychology: Checklist and Clarifications for
the Case of Congruence Hypotheses. *SPPS*, 10(3), 409–419.
