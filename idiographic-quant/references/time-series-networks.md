# Person-specific time series, networks, and latent models

For one unit measured on many occasions. Pick by question and data density; don't fit
the fanciest model the software allows.

## Contents
1. Always look first (descriptive time series)
2. graphicalVAR — the workhorse idiographic network
3. mlVAR — multilevel VAR (pool to stabilize)
4. GIMME — data-driven person-specific path models
5. P-technique / idiographic factor analysis
6. DSEM — dynamic SEM (latent + multilevel + time series)
7. Choosing among them

---

## 1. Always look first

Before any model: plot each variable against time; inspect ACF/PACF for autocorrelation
structure; check for trends, level shifts, and changing variance (nonstationarity); and
look at missingness/compliance over time. Many "surprising network findings" dissolve
once you see a trend or a handful of influential occasions in the raw series. A clean
descriptive figure is often the most honest deliverable when T is modest.

## 2. graphicalVAR — the workhorse idiographic network

**What:** estimates two regularized (LASSO) person-specific networks from one person's
intensive longitudinal data: a **temporal** network (lag-1 directed effects, the
"which-predicts-which-next" structure) and a **contemporaneous** network (partial
correlations of residuals within the same measurement window). Regularization is what
makes it tractable for one person's modest T.

**When:** single person, several variables, you want temporal *and* same-moment
structure, T at least ~50–100 (more is much better; lagged effects are data-hungry).

**Watch:** lagged/temporal networks are typically *less* reliable than contemporaneous
ones — don't over-interpret weak directed edges. Stationarity is assumed; check it.
The lag interval defines the temporal construct. **Assess stability before believing
any edge:** `bootnet` (case-drop subsetting and nonparametric bootstrap) tells you
which edges are distinguishable from zero and from each other; an edge that doesn't
survive bootstrapping is not a finding.

**R (the standard stack):**
```r
library(graphicalVAR)
# data: one person, rows = occasions in time order, columns = variables
# 'beepvar'/'dayvar' let it respect day boundaries so you don't lag across nights
fit <- graphicalVAR(
  data, vars = c("anx","sad","fatigue","rumination"),
  beepvar = "beep", dayvar = "day",
  gamma = 0.5            # EBIC hyperparameter; 0 = less conservative, 0.5 = sparser
)
plot(fit, "temporal")        # via qgraph under the hood
plot(fit, "contemporaneous")
```

## 3. mlVAR — multilevel VAR (pool to stabilize)

**What:** fits VAR to many people *simultaneously* in a multilevel framework, yielding
person-specific temporal, contemporaneous, and between-person networks while shrinking
each person's estimates toward the sample. More stable per-person estimates than
isolated graphicalVAR fits when you have multiple people.

**When:** multi-person ESM/EMA and you want individual structure *and* a defensible
group picture; per-person T is too short for stable standalone fits.

```r
library(mlVAR)
fit <- mlVAR(data, vars = vars, idvar = "id", lags = 1,
             beepvar = "beep", dayvar = "day",
             temporal = "orthogonal")   # 'correlated' if you can afford the params
plot(fit, "temporal");  plot(fit, "contemporaneous");  plot(fit, "between")
```

## 4. GIMME — Group Iterative Multiple Model Estimation

**What:** a data-driven search (Gates & Molenaar, 2012) that builds person-specific
structural models in a principled order: it first finds the directed paths that
replicate across a *majority* of individuals (the group level, to separate signal from
noise), optionally finds subgroup-shared paths via community detection, then frees
person-specific paths. The output is a unified-SEM/VAR path model **for each person**
that includes both lagged and contemporaneous directed effects. Originally for fMRI
effective connectivity; now widely used for ESM/dyadic/diary data.

**When:** you explicitly want to know what is common, what is shared by subgroups, and
what is unique to each person, with directionality — and you distrust hand-specified
structure. This is often the most defensible answer to "what's general AND
person-specific?"

```r
library(gimme)
gimmeSEM(
  data = "path/to/folder_of_per_person_csvs",   # one file per person
  out  = "path/to/output",
  subgroup = TRUE,        # community-detect subgroups
  standardize = TRUE
)
# aggSEM() = group-only; indSEM() = each person independently (no pooling)
```

## 5. P-technique / idiographic factor analysis

**What:** factor-analyze one person's variables across many occasions (occasions play
the role that people play in ordinary R-technique factor analysis). Answers a question
ordinary psychometrics can't: *does this person's own latent structure match the
nomothetic one?* (e.g., do the Big Five even cohere for them?). Classical P-technique
ignores temporal dependence; **dynamic factor analysis** extends it to model lagged
latent structure and is preferable for autocorrelated data.

**When:** the question is about an individual's measurement/latent structure, not just
observed associations. Caution: per-person occasion counts (~60–90) are small for
stable factor recovery — report this limitation explicitly.

## 6. DSEM — dynamic structural equation modeling

**What:** the most general framework here (Asparouhov, Hamaker & Muthén, 2018). It
embeds time-series (lagged) models inside a two-level multilevel SEM: a **within-person**
model for each person's dynamics and a **between-person** model for how those dynamics
differ across people, with latent variables and measurement models available. Estimated
Bayesian in **Mplus** (Version 8+); essentially all published DSEM uses Mplus + Bayes.

**When:** you need latent constructs (multi-item scales) modeled properly, multivariate
mediation over time, dyadic dynamics, or random dynamic parameters across people — i.e.,
the structured questions simpler VAR/network tools can't represent.

**Critical estimation detail — centering.** To separate within- from between-person
effects you must handle person means correctly. DSEM's **latent person-mean centering**
avoids two biases that bite naive *observed*-mean centering: **Nickell's bias** (lagged
autoregressive effects biased downward) and **Lüdtke's bias** (person means measured
with error). Use latent centering; don't pre-center by observed means. There are
also **one-step** (full Bayesian, more principled, slower, can struggle to converge with
many random effects) vs **two-step** (faster, more stable) workflows — note which you
used and why.

```
% Mplus sketch — two-level AR(1) with a random autoregressive effect
VARIABLE:  CLUSTER = id;  LAGGED = y(1);
ANALYSIS:  TYPE = TWOLEVEL RANDOM;  ESTIMATOR = BAYES;  PROC = 2;  BITER = (2000);
MODEL:
  %WITHIN%   phi | y ON y&1;        ! person-specific carryover (random slope)
  %BETWEEN%  y;  phi;  y WITH phi;  ! between-person differences in mean & dynamics
```

## 7. Continuous-time models — when the spacing is unequal

**The problem:** every method above is *discrete-time* — it treats consecutive
observations as one fixed "lag" apart. But ESM/EMA beeps are typically semi-random
within blocks, so the real gaps vary (90 minutes here, 5 hours there, overnight). Feeding
unequally spaced data to a discrete-time VAR/DSEM as if it were a clean grid biases the
autoregressive and cross-lagged estimates, because a coefficient that means "carryover
over 90 minutes" is being pooled with one that means "carryover over 5 hours."

**Two fixes, in increasing order of rigor:**

1. **Grid approximation (DSEM `TINTERVAL`).** Mplus inserts missing rows to snap
   observations onto an approximately equal grid, then handles the inserted gaps as
   missing data. Cheap; adequate when spacing is only mildly irregular.
2. **Continuous-time modeling (ctsem in R; the Oud/Voelkle/Driver CT-SEM tradition).**
   Models the underlying process with a stochastic differential equation and *derives*
   the discrete-time effects for any interval you ask about. This is the principled
   answer to irregular spacing, and it also lets you compare dynamics across studies
   with different sampling rates. Steeper learning curve; worth it when spacing is
   genuinely irregular or when the lag interval is itself of interest.

**When to reach for it:** any time the gaps between observations vary enough that "lag-1"
is ambiguous. If beeps are essentially equally spaced (e.g., fixed daily diary), discrete
models are fine and simpler.

## 8. When the dynamics change over time (nonstationary & time-varying methods)

Everything above assumes **stationarity** — the dynamics are constant across the window.
The skill insists you check this, and for the constructs idiographic studies care about
(mood, symptoms, personality) the honest finding is often that it fails: the process drifts,
shifts regime, or escalates. When it does, don't force a stationary model and average over
the change — *model the change*, because the change is frequently the most interesting part.

- **Time-varying VAR / networks.** Let the parameters themselves evolve over time. GAM/
  spline-based time-varying VAR (Bringmann and colleagues) and `tvmgm` in the `mgm` package
  (Haslbeck) estimate how edges strengthen or weaken across the series. Use when you expect
  smooth drift (e.g., a network tightening as someone deteriorates). Costs power — you're
  estimating more — so it needs longer series than a stationary fit.
- **Regime-switching / change-point models.** Assume the person occupies discrete states
  with different dynamics and switches between them (hidden Markov / threshold / change-point
  VAR). Use when you expect distinct phases (well vs. depressed episode) rather than smooth
  drift. Detecting *when* the switch happens is often the clinical payoff.
- **Early-warning signals / critical slowing down.** A specific, high-value application:
  as a dynamical system approaches a transition (relapse, a mood tipping point), it tends to
  show **critical slowing down** — rising autocorrelation and variance, slower recovery from
  perturbation. Tracking these within a person's dense time series has been proposed as a
  *personalized* early-warning signal for upcoming transitions (van de Leemput, Wichers,
  Scheffer and colleagues). This reframes nonstationarity from nuisance to signal: the
  changing dynamics forecast the event. Needs dense, sustained sampling and careful handling
  of trend/missingness, but it's one of the most compelling things idiographic data can do.

Practical note: distinguish a **trend in the mean** (often removable by detrending, and you
should detrend before a stationary VAR rather than letting the trend masquerade as
autocorrelation) from **change in the dynamics** (the lagged structure itself shifts — that's
what the methods above are for). They call for different responses.

## 9. Choosing among them

- **One person, want a quick honest picture:** descriptive series → graphicalVAR.
- **Several people, want individual + group, observed variables:** mlVAR.
- **Want directed structure with principled group/subgroup/individual layers:** GIMME.
- **Need latent constructs / mediation / dyads / random dynamics:** DSEM.
- **Question is about one person's latent/measurement structure:** P-technique /
  dynamic factor analysis.
- **Observations are unequally spaced in time:** continuous-time (ctsem) or DSEM
  `TINTERVAL`, layered on top of whichever structural choice above fits.
- **The dynamics themselves drift / switch / approach a transition:** time-varying VAR
  (`tvmgm`), regime-switching/change-point models, or early-warning-signal tracking.

Across all of them the binding constraints are the same: enough T, checked
stationarity, a sampling interval matched to the process, and uncertainty reported
honestly. The model is the easy part.
