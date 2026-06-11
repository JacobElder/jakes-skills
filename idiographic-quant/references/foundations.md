# Foundations: ergodicity and when idiographic analysis is warranted

## Contents
1. The ergodicity argument
2. The two conditions
3. The empirical evidence (Fisher et al.) and the counterargument (Hamaker & Ryan)
4. When idiographic is warranted — and when it isn't
5. The relationship between idiographic and nomothetic

---

## 1. The ergodicity argument

A process is **ergodic** if its structure of variation *between cases* (interindividual,
estimated across people at one time) equals its structure of variation *within a case*
over time (intraindividual). Molenaar's 2004 "manifesto" (*Measurement*, 2, 201–218)
made the consequence explicit: the classical ergodic theorems say that you may
generalize a between-person structure to the within-person process **only** if the
process is ergodic. Psychological processes generally are not. Therefore the standard
move — estimate a model across people, then talk as if it describes an individual — is
"incomplete," in his words, and what is missing is the scientific study of the
individual.

This is not a minor caveat. ANOVA, regression, path analysis, factor analysis, SEM,
and ordinary multilevel/mixed models all infer structure from interindividual
variation. Under nonergodicity, none of their parameters is guaranteed to describe any
real person. The classic illustration is the typing-speed example and its many
descendants: across people, more anxiety may correlate with worse performance, while
within a given person a bit of arousal *improves* performance — opposite signs, both
correct, describing different things. Aggregating hides this (the ecological fallacy /
Simpson's paradox lives here).

## 2. The two conditions

For ergodicity (specifically, the weak/second-order form relevant to most modeling)
two conditions must hold:

- **Homogeneity** — the same model, with the same parameters, governs every individual
  in the population. "The main features of a statistical model describing the data are
  invariant across subjects." In factor-analytic terms: identical number of factors,
  loadings, and error variances for everyone.
- **Stationarity** — the model does not change over time for a given individual. Means,
  variances, and dynamic (lagged) relations are stable across the observation window.

Real processes violate **both**. People differ in structure, not just level
(heterogeneity), and the structure itself develops, learns, adapts, and responds to
context (nonstationarity). Molenaar & Campbell (2009) treat nonstationarity as a
chronic source of nonergodicity. The uncomfortable corollary for personality and
clinical work: dynamic-systems theories of the constructs themselves *predict*
nonstationarity, so the very theories motivating idiographic study often undercut the
stationarity assumption the standard idiographic models rely on. Take this tension
seriously rather than wishing it away.

## 3. Evidence and counterargument

**Fisher, Medaglia & Jeronimus (2018, PNAS, 115(27):E6106).** Across six
intensive repeated-measures datasets (≈87–94 people, matched number of assessments),
they compared the distribution of within-person correlations to between-person
correlations. Central tendencies (means) agreed reasonably, but the **variance around
the expected value was two to four times larger within individuals than between**. The
practical reading: aggregate estimates are far more imprecise as descriptions of
individuals than their standard errors suggest, and the social/medical literatures
likely overstate how well group estimates describe people.

**The counterargument — Hamaker & Ryan (2019, PNAS comment).** They argue the
comparison is partly an artifact: cross-sectional (between-person) estimates from a
single occasion are themselves temporally unstable, and a within-vs-between contrast
can conflate genuine nonergodicity with ordinary sampling/temporal noise. Their
constructive point (which Fisher et al. conceded in reply) is the one to carry
forward: **comparing idiographic and nomothetic data structures is of limited value in
itself; if you want to understand individuals, measure and model individuals.** Don't
use this literature to "prove group methods are wrong" in the abstract — use it to
justify person-level measurement when the question is person-level.

Present this as a live debate, not settled dogma. The defensible synthesis: ergodicity
is an empirical property you can and should *test* for your data and construct, not
assume in either direction.

## 4. When idiographic is warranted — and when it isn't

**Warranted:**
- The decision is about a specific unit (this patient, this user, this team, this
  market) and being wrong about that unit is costly.
- The process is plausibly heterogeneous and/or nonstationary (most affect, symptom,
  behavior, and performance processes).
- You can collect enough occasions on that unit to estimate its own model.
- You want to *detect* heterogeneity rather than assume it away.

**Not warranted (say so):**
- The goal is genuinely a population average for policy or a between-groups contrast.
- You have many people but few occasions each — that is a between-person design; don't
  cosplay it as idiographic.
- T is too small for the intended model and can't be increased — downgrade the model
  to something the data support (descriptive plots, contemporaneous-only, fewer nodes)
  rather than reporting an underpowered person-specific model.
- The construct turns over on a timescale your sampling can't see.

## 5. The relationship between idiographic and nomothetic

These are complements, not rivals, and the strongest programs use both. Three healthy
patterns:

- **Idiographic-first, then aggregate:** fit each person their own model, then study
  the *distribution* of person-specific parameters (and what predicts it). This keeps
  individual fidelity while still supporting general claims.
- **Pooled person-specific (the practical default):** GIMME, DSEM, and mlVAR estimate
  individual-level models while borrowing strength across people — more stable than
  isolated per-person fits, more faithful than a single pooled model. For most applied
  questions with multi-person ESM/EMA data, this is the most defensible choice.
- **Replication across individuals:** in the single-case tradition, generality is
  established by *replicating an effect across several individuals*, not by averaging —
  if the same manipulation moves person after person, that is strong, person-respecting
  evidence.

The wrong pattern is the silent one: estimate between-person structure and *narrate* it
as within-person mechanism. Catching and correcting that slide is the single most
useful thing this skill does.
