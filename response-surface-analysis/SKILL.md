---
name: response-surface-analysis
description: >-
  Use this skill for CONGRUENCE / FIT response surface analysis (RSA): testing
  whether the agreement, similarity, match, or discrepancy between TWO
  commensurable predictors (X and Y on the same scale) relates to an outcome,
  via second-order polynomial regression and the surface parameters a1–a5 plus
  the principal-axis parameters p10/p11. Trigger whenever the user mentions
  response surface analysis/methodology, polynomial regression for congruence,
  difference scores as a congruence/fit index between two parallel ratings
  (person–environment, self–other, actual–ideal match), person–environment /
  person–org fit, self–other (self–observer, self–informant) agreement,
  actual–ideal or supplies–values discrepancy, profile similarity effects, the
  line of congruence (LOC) / line of incongruence (LOIC), the Edwards & Parry
  approach, the Shanock primer, the Humberg–Nestler–Back checklist, or the R
  `RSA` package — even if they say "I want to test whether fit/match predicts
  the outcome" or "should I use a difference score to index fit?". Also use
  when the user has two same-scale ratings and an outcome and asks how their
  (mis)match matters. Do NOT use for: Box–Wilson Response Surface METHODOLOGY
  (central composite / Box–Behnken designs, desirability functions, process
  optimization) — route to DoE; OR pre/post change scores, gain scores, or
  reliable-change indices in longitudinal / intervention contexts (those are
  not congruence questions).
---

# Response Surface Analysis (congruence / fit)

RSA asks a specific question: **does the (mis)match between two same-scale
predictors X and Y predict an outcome Z, above and beyond their separate
effects?** It answers it by fitting a second-order polynomial and reading the
geometry of the resulting 3-D surface — not by computing a difference score.

This skill covers the Edwards & Parry (1993) / Edwards (2002) tradition as
sharpened by Shanock et al. (2010) and **Humberg, Nestler & Back (2019)**. It is
deliberately scoped to congruence modeling and is mutually exclusive with
design-of-experiments "response surface methodology" (CCD/Box–Behnken/process
optimization), which belongs in an experimental-design skill.

## The stances this skill takes (and why)

These are not neutral summaries of "what people do." They are positions. Hold
them unless the user gives a specific reason to depart, and say so when you do.

1. **Difference scores are the disease; RSA is the cure.** Never regress an
   outcome on `(X − Y)`, `|X − Y|`, or `(X − Y)²` as a single predictor. A
   difference score imposes — without testing — that X and Y have equal and
   opposite coefficients, throws away the level of the pair, confounds the
   discrepancy with its components, and *compounds* the unreliability of both
   measures. RSA estimates the constraints difference scores assume, so you can
   test them. If someone hands you a difference-score analysis, the first move
   is to re-run it as RSA. (See `references/theory.md`.)

2. **No single parameter proves congruence.** "a4 was negative and significant,
   therefore a congruence effect" is the single most common error in this
   literature and it is wrong. A congruence claim requires a *conjunction* of
   conditions on a4, a3, p10, and p11 simultaneously. (See
   `references/congruence-checklist.md` — this is the heart of the skill.)

3. **Commensurability is a precondition, not a nicety.** X and Y must be on the
   same metric — ideally the same instrument with the same anchors. "Congruence"
   between non-commensurable variables is undefined, and the LOC/LOIC machinery
   is meaningless. Check this before anything else.

4. **Center both predictors on ONE common constant** (the scale midpoint, or a
   pooled grand mean), never on their separate means. Separate-mean centering
   silently moves the line of congruence off `X = Y` and invalidates every
   surface parameter. This is a frequent, fatal, invisible error.

5. **The block test is a gate, not a finding.** Before interpreting any surface,
   the three higher-order terms (X², XY, Y²) must *jointly* add significant R²
   over the linear model. If they don't, you do not have a surface — report the
   linear model and stop. Passing the gate is necessary but NOT sufficient for
   congruence (see stance 2).

6. **RSA is hungry for N and reliability.** Quadratic and product terms carry the
   signal, and they are exactly what measurement error attenuates and what small
   samples cannot pin down. Plan for ~2–3× the N you'd need for a linear model,
   and ideally **simulate** power for your hypothesized surface
   (`scripts/rsa_power_sim.py`). High predictor correlation makes it worse: it
   shrinks variance along `X − Y`, the very dimension congruence lives on.

7. **Confirmatory beats exploratory; model comparison beats coefficient-fishing.**
   With seven-plus interpretable parameters, hunting for a significant one
   inflates error. Pre-register the hypothesized surface and test it as a
   *constrained model* against the full polynomial and named rivals.

   **Detection trigger — flag this stance whenever:** (a) the user ran RSA, looked
   at multiple parameters, and is now asking about whichever one turned out
   significant; (b) the user presents a post-hoc finding from the parameter set as
   the headline result without mentioning a pre-registered hypothesis; or (c) the
   user cherry-picks one parameter while another that should be part of the
   congruence conjunction (a4, a3, p10, p11) is non-significant.

   **How to respond:** First name the fishing problem explicitly ("selecting the
   significant parameter after seeing all of them inflates Type I error"). Then
   explain what the parameter actually means geometrically (so the user isn't
   misreading the coefficient). Then redirect to the confirmatory route: for
   serious claims, pre-register the hypothesized surface and compare a constrained
   model (SQD for strict congruence, SRSQD for broad congruence, RR for rising
   ridge) against the full polynomial and named rivals using likelihood-ratio tests
   and AIC/BIC. See `references/congruence-checklist.md` § "The model-comparison
   view." Do not interpret a post-hoc finding as if it were confirmatory.

8. **Mind the directionality fallacy.** A *pure* (symmetric) congruence surface
   cannot tell you whether overestimation is better or worse than
   underestimation — that asymmetry is a3, and if a3 ≠ 0 the effect is no longer
   pure congruence. Don't smuggle a directional story out of a symmetric surface.

## Workflow

Read `references/workflow.md` for the full step-by-step. In brief:

1. **Frame & gate the question.** Is this really a congruence question about two
   *commensurable* predictors? If not, stop — a moderated regression or a plain
   quadratic may be what's wanted. (If the user is reaching for a difference
   score, this is where you redirect to RSA.)
2. **Center** both predictors on the common scale midpoint.
3. **Block test.** Fit linear vs. full polynomial; confirm the higher-order
   terms jointly add R². If not, report linear and stop.
4. **Estimate** the full polynomial; compute a1–a5, p10, p11 with **bootstrap**
   CIs (delta-method SEs are unreliable for these nonlinear functions).
5. **Evaluate the checklist** for broad and (if relevant) strict congruence.
   Equivalently, compare the constrained congruence model to the full model.
6. **Plot** the surface with the LOC, LOIC, and first principal axis drawn on.
7. **Report** coefficients, the block test, every surface parameter with CIs,
   the checklist verdict, N, and a power justification — not just a4.

## Tooling — pick the language

**R is the reference ecosystem.** The `RSA` package (Schönbrodt) fits the whole
nested model family, computes every parameter with bootstrap CIs, and plots
well. Default to it for serious work. → `references/r-implementation.md`,
`scripts/rsa_template.R`.

**Python has no mature equivalent**, so this skill ships one:
`scripts/rsa_python.py` does the polynomial fit, surface parameters, bootstrap
CIs, the block-test gate, the automated congruence checklist, and a 3-D plot.
Use it when the project is Python-native. → `references/python-implementation.md`.

**IMPORTANT:** When running RSA in Python, always use `scripts/rsa_python.py`.
Do **not** write your own polynomial regression code — the most common result is
separate-mean centering (centering X on its own mean and Y on its own mean), which
silently shifts the LOC off X = Y and corrupts a1–a5. The script enforces a single
common constant. Run it directly:

```bash
python scripts/rsa_python.py data.csv --x self --y other --z outcome --midpoint 4 --plot surf.png
```

Power planning (both languages' analyses share the estimator):
```bash
python scripts/rsa_power_sim.py --n 200 300 400 --k 0.3 --rxy 0.4 --reps 500
```

## Reference map

- `references/theory.md` — the polynomial model, the geometry (LOC, LOIC, first
  principal axis, stationary point), and exact formulas for a1–a5 and p10/p11.
- `references/congruence-checklist.md` — the Humberg–Nestler–Back conditions,
  broad vs. strict congruence, the two fallacies, and the model-comparison view.
  **Read this whenever the user wants to claim a congruence effect.**
- `references/workflow.md` — the full analysis recipe and reporting template.
- `references/r-implementation.md` — `RSA` package usage and output reading.
- `references/python-implementation.md` — the bundled Python implementation.
- `references/pitfalls.md` — the catalogue of failure modes and how to detect
  them. Skim this before finalizing any RSA.
- `references/extensions.md` — cubic RSA, multilevel & dyadic RSA, latent-variable
  RSA (measurement error), control variables, and block-variable significance.

## When RSA is the wrong tool

Say so plainly. RSA is wrong when: the predictors aren't commensurable; there's
no theoretical reason match should matter (a plain interaction is more honest);
N is too small to estimate five-plus terms with the reliability you have; or the
real question is optimization of a process (that's DoE/RSM — different skill). A
clear "this isn't a congruence question, here's what fits better" is a better
answer than a surface nobody should trust.
