---
name: idiographic-quant
description: >-
  Design and analyze idiographic (person-specific, N-of-1, within-person)
  quantitative studies — variation WITHIN a single unit over time, as opposed
  to nomothetic between-person averages. Use whenever the question is about an
  individual not a population: one patient's symptom dynamics, one user's
  behavior over time, "what predicts THIS person's mood," personalized
  intervention effects, intensive longitudinal data (ESM/EMA/diary/sensor)
  analyzed per-person, single-case experiments (ABAB, multiple baseline,
  alternating treatment), N-of-1 trials, person-specific networks
  (graphicalVAR, mlVAR, GIMME), dynamic SEM (DSEM), P-technique factor
  analysis, or fitting a model to one person's repeated measurements. ALSO
  trigger when someone is about to apply a group-level model to an individual
  (the ergodicity trap), asks whether group findings "apply to this person,"
  or has dense repeated measures on few units. Covers method selection, the
  ergodicity argument, data-density needs, stationarity, reliability, reporting.
---

# Idiographic Quantitative Methods

## The one idea that makes this skill necessary

Almost all quantitative psychology and social science estimates **between-person**
structure — it correlates people against each other and reports the average. The
silent assumption is that this average also describes the **within-person** process
unfolding over time inside any given individual. That assumption is **ergodicity**,
and it requires two conditions that real psychological processes essentially never
satisfy: every person obeys the *same* model (homogeneity) and that model does not
change over time (stationarity). When ergodicity fails, the group result is not an
approximation of the individual — it can be unrelated to, or the *reverse* of, what
is true for any real person. Fisher, Medaglia & Jeronimus (2018, PNAS) showed
empirically that within-person variance was two to four times larger than
between-person variance across six datasets: the group is a poor stand-in for the
person.

So the core stance of this skill is blunt: **if your question is about an
individual, a between-person average is not a shortcut to the answer — it is
usually a different question with a different answer.** To learn how a process works
inside a person, you have to measure that person repeatedly and model their own
data. That is what "idiographic" means here — not qualitative, not anecdotal, but a
rigorous *quantitative* science of intraindividual variation.

**But idiographic is not automatically "better," and this skill refuses to cheerlead
it.** Person-specific models are data-hungry, fragile, and easy to do badly. A
graphicalVAR network fit to 40 noisy ESM beeps is often uninterpretable noise dressed
up as insight. The honest position is: use idiographic methods *when the question is
genuinely about within-person process and you have the data density to support them*,
and otherwise don't. Most of the value this skill adds is in saying no — to
underpowered networks, to stationarity assumed rather than checked, to dynamics read
off too few time points.

## Step 0 — Is this even an idiographic question?

Before choosing a method, classify the question. Get this wrong and everything
downstream is wasted.

- **"How does X work inside this person / unit, over time?"** → idiographic. Proceed.
- **"Does this intervention change THIS person's behavior?"** → idiographic *causal*
  (single-case / N-of-1). Proceed, go to the experimental-design branch.
- **"What's the average effect across people?"** → nomothetic. This skill is the
  wrong tool, and saying so is a *correct* use of it, not a failure. Recommend the
  standard between-person approach by name (e.g., a regression / mixed model / RCT or
  A/B test), explain briefly why aggregation is the right move *here* (the decision is
  about the population, not any one unit), and stop. Do not strain to find an
  idiographic angle, and do not push person-specific methods onto a genuinely
  population-level question — over-applying idiographic methods is its own failure mode.
- **"Does the group finding apply to this individual?"** → this is the ergodicity
  trap. The answer is "only if the process is ergodic, which you must not assume."
  Read `references/foundations.md` and steer them toward measuring the individual.
- **"I want both — what's general AND what's person-specific?"** → a pooled
  person-specific method (GIMME, DSEM, mlVAR) that estimates individual models while
  borrowing strength across people. This is usually the most defensible real-world
  choice.

Do not let a request for idiographic analysis go unchallenged if the data can't
support it. If someone has 15 time points and wants a 6-node lagged network, the
correct response is to explain why that won't work and offer a feasible alternative
(fewer nodes, contemporaneous-only, descriptive plots, or collecting more data).

**Still planning data collection?** Then the highest-leverage work is the protocol, not
the model — the worst idiographic mistakes are baked in before any data exists. Read
`references/measurement-design.md` first (sampling scheme, beeps/day vs. process timescale,
the common-vs-personalized item decision, compliance, reactivity). A bad protocol produces
data no method can rescue.

## Step 1 — Match method to question and data

Pick the branch, then read the matching reference file. Don't load all of them.

### A. Describe one person's dynamics (no manipulation)
You have dense repeated measures on a single unit and want to characterize its
structure or temporal dependencies.

| Goal | Method | Read |
|---|---|---|
| Temporal + contemporaneous associations among several variables | **graphicalVAR** (lag-1 + contemporaneous, regularized) | `references/time-series-networks.md` |
| Same, but pool across people to stabilize each person's estimate | **mlVAR** (multilevel VAR) | `references/time-series-networks.md` |
| Data-driven person-specific path model, separating group/subgroup/individual effects | **GIMME / gimmeSEM** | `references/time-series-networks.md` |
| Latent factor structure *for this person* (does the Big Five even hold for them?) | **P-technique factor analysis / idiographic EFA** | `references/time-series-networks.md` |
| Latent dynamics + measurement model + between-person differences in one framework | **DSEM** (Mplus) | `references/time-series-networks.md` |
| Measurements are **unequally spaced** in time (most ESM/EMA) | **continuous-time models** (ctsem; or DSEM `TINTERVAL`) | `references/time-series-networks.md` |
| Just look at it honestly first | time plots, ACF/PACF, per-variable trends | `references/time-series-networks.md` |

### B. Test whether something *causes* a change in one unit
You can manipulate a condition and want a defensible causal claim about *this* unit.

| Design | When | Read |
|---|---|---|
| **ABAB / withdrawal** | effect is reversible, withdrawal is ethical | `references/single-case-designs.md` |
| **Multiple baseline** (across behaviors/settings/people) | effect is *not* reversible | `references/single-case-designs.md` |
| **Alternating treatments** | comparing 2+ treatments, rapid switching | `references/single-case-designs.md` |
| **Changing criterion** | shaping a behavior toward a stepped goal | `references/single-case-designs.md` |
| **N-of-1 trial** (randomized crossover, often medical) | individual treatment-effect estimate, blinding possible | `references/single-case-designs.md` |

Analyze these with **randomization tests** (valid p-values from the design's own
randomization, no distributional assumptions), effect sizes appropriate to
single-case data, and structured **visual analysis** — not a t-test on autocorrelated
points. Details and the analysis hierarchy are in the reference file.

### C. Diagnose the ergodicity / heterogeneity problem itself
Someone wants evidence about *whether* pooling is even defensible for their data, or a
reviewer is demanding it. Use `scripts/check_ergodicity.py` to compare the
within-person vs between-person association distributions (the Fisher et al. logic).
A large gap is direct evidence that the group model does not describe individuals.

## Step 2 — Check the assumptions BEFORE interpreting anything

These are non-negotiable. Skipping them is the most common way idiographic analyses
go wrong, and most published critiques target exactly these failures.

1. **Enough time points (T).** Person-specific dynamics need many occasions, not many
   people. Rough, defensible floors: descriptive time-series ≥ ~30; a small
   regularized graphicalVAR ≥ ~50–100 and ideally far more; DSEM benefits from 50+
   per person. If T is too small for the number of parameters, *reduce the model*,
   don't push through. Parameters scale roughly with the square of the node count for
   networks — every node you add is expensive. Planning a study? Don't guess the
   needed T from a rule of thumb — simulate: generate data from a plausible model at
   candidate T values and check whether the analysis recovers the parameters.
2. **Stationarity.** VAR/network/DSEM models assume the dynamics don't drift over the
   observation window. But dynamic-systems theories of the very constructs being
   studied (mood, personality) predict that they *do* drift — so stationarity is often
   in direct tension with the theory motivating the study. Check for trends, regime
   shifts, and changing variance; detrend or model nonstationarity explicitly if
   present. Never assume it silently.
3. **Timescale match — and equal spacing.** The sampling interval must match the
   process. Beeping six times a day cannot capture a dynamic that turns over in
   minutes, and won't reveal one that unfolds over months. Lagged effects are *defined
   by* the lag interval — a "lag-1" effect at 3-hour spacing is a different construct
   than at daily spacing. Related trap: discrete-time VAR/DSEM assume *equal* spacing,
   but ESM beeps are usually semi-random, so consecutive observations are unequally
   spaced. Treating them as equally spaced biases the lagged estimates. Either insert
   placeholder occasions to approximate a grid (DSEM `TINTERVAL`) or, better, use a
   **continuous-time** model (ctsem) that estimates the underlying process and derives
   effects for any interval.
4. **Measurement reliability at the within-person level.** Between-person reliability
   does not transfer. Person-mean centering with unreliable means induces bias
   (Lüdtke bias; Nickell bias in autoregressive terms). See the DSEM section.
5. **Reliability of the person-specific estimates themselves.** Idiographic networks
   can be unstable across waves for the same person, and lagged networks are typically
   *less* reproducible than contemporaneous ones. Treat a single fitted network as an
   estimate with wide uncertainty, not a portrait. Quantify it: bootstrap edge
   stability (bootnet), report posterior intervals (DSEM), or refit on split halves and
   see what survives. "Report stability where you can" means *do this*, not gesture at
   it.

## Step 3 — Report so a skeptic can check you

Idiographic work is held to a high evidentiary bar precisely because n=1 invites the
worry "you found a pattern in noise." Pre-empt it: report T per unit and the
compliance/missingness pattern; report the sampling scheme and interval; state and
*test* stationarity; report the model's regularization/priors; show the raw time
series alongside the fitted model; and quantify uncertainty/stability rather than
presenting point estimates as fact. For single-case experiments follow established
reporting standards (SCRIBE for behavioral SCEDs; CENT for N-of-1 trials).
`references/pitfalls-and-reporting.md` has the full checklist and the standard
critiques to defend against.

**Before you read a network as a treatment plan:** the most central node is a
*hypothesis* about a target, not a lever — centrality measures are unstable and
poorly suited to psychological networks, directed edges aren't causal arrows, and a
cross-sectional network can't speak to an individual at all. The interpretation traps
are in `references/pitfalls-and-reporting.md` (§3); consult it whenever the user wants
to act on a fitted network.

## On tone and point of view

This skill is deliberately opinionated because the value is the judgment, not a
neutral menu. Take clear positions: ergodicity almost never holds; group means don't
describe individuals; underpowered idiographic models are worse than honest
descriptive plots; stationarity must be checked not assumed; pooled person-specific
methods are usually the most defensible real-world choice. When you disagree with what
a user is about to do, say so plainly and explain why — then offer the feasible
alternative. Don't dilute a correct methodological warning into hedged neutrality. But
"opinionated" is not "dogmatic": when the question really is about a population
average, say that nomothetic methods are right and this skill doesn't apply.

## Reference map

- `references/measurement-design.md` — ESM/EMA protocol design BEFORE data collection:
  sampling schemes, beeps/day vs. process timescale, common-vs-personalized items,
  compliance, reactivity, and the design↔analysis contract.
- `references/foundations.md` — ergodicity, the homogeneity/stationarity conditions,
  the Fisher et al. evidence and the Hamaker/Ryan counterargument, when idiographic is
  and isn't warranted, the idiographic↔nomothetic relationship.
- `references/time-series-networks.md` — VAR, graphicalVAR, mlVAR, GIMME, P-technique,
  DSEM, continuous-time (ctsem), and time-varying/regime-switching/early-warning
  methods: what each does, when to use it, software, and annotated code patterns.
- `references/single-case-designs.md` — SCED families, N-of-1 trials, randomization
  tests, single-case effect sizes, visual-analysis standards.
- `references/pitfalls-and-reporting.md` — power/T, stationarity, reliability, network
  interpretation traps (centrality, causal over-reading), recurring critiques, and
  reporting checklists (SCRIBE, CENT).
- `scripts/check_ergodicity.py` — within- vs between-person association diagnostic.
