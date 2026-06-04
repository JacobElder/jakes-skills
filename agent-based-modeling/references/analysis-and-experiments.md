# Experiments and Analysis of ABM Output

An ABM is an instrument that generates data; running it well is a designed
experiment, and reading the data well is statistics on a stochastic process.
Most ABM mistakes at this stage come from treating runs as if they were
deterministic answers.

**Contents**
1. The core problem: stochastic output
2. How many replications? (the convergence method)
3. Designing simulation experiments
4. Sensitivity analysis: local vs. global
5. Transient vs. steady state (burn-in)
6. Analyzing and reporting output
7. Common analysis traps

---

## 1. The core problem: stochastic output

Almost every ABM uses randomness — in initialization, in tie-breaking, in agent
decisions. So for a *fixed* parameter set, each run with a different random seed
gives a different result. The model's "answer" at a parameter set is therefore a
**distribution**, sampled by Monte Carlo: rerun with independent seeds and treat
the collected outcomes as a sample. Everything downstream (means, comparisons,
sensitivity) is inference about that distribution.

Two consequences:
- A single run is anecdote. Never draw conclusions from one trajectory.
- You need *enough* runs that your summary statistics are stable, but not so many
  that you waste compute or manufacture significance (see §6).

---

## 2. How many replications?

Don't guess and don't copy "we ran it 100 times" from another paper. Determine it
empirically:

**Convergence of the coefficient of variation (CV).** Run the model with an
increasing number of replications and track the CV (std/mean) of the output of
interest. As replications increase, the CV stabilizes; the number at which it
stops meaningfully changing is a reasonable replication count (Lorscheid et al.
2012; ten Broeke et al. 2014). Practically: plot the running CV (or the running
mean ± its standard error) against replication count and stop when the curve
flattens.

Caveats:
- Do this **per output and per regime.** Different outputs and different parameter
  regions converge at different rates; a count that suffices near the middle of
  parameter space may be far too few near a tipping point where variance explodes.
- **Non-linear input–output relationships break the assumption** that convergence
  is uniform — recheck near bifurcations and phase transitions.
- More expensive models force a trade-off; if you can only afford few replicates,
  say so and widen your uncertainty claims accordingly.

For sensitivity-analysis sample points, you still need a few replicates *each* to
average out stochastic noise before attributing output variation to the parameter
— otherwise you can't tell parameter effects from seed effects.

---

## 3. Designing simulation experiments

Treat parameter exploration as **design of experiments (DoE)**, not ad-hoc poking:

- Define factors (parameters), their plausible ranges, and the responses (the
  observation variables from ODD). Decide these *before* running, to avoid
  post-hoc fishing.
- Choose a sampling design appropriate to the question: full factorial for a few
  factors, **Latin Hypercube** or other space-filling designs for many, focused
  one-factor sweeps to illustrate a mechanism.
- Hold the random-seed handling explicit: either common random numbers across
  conditions (to reduce variance when comparing) or independent seeds (for honest
  variance estimates) — and report which.
- For the model behavior to be interpretable, you often want to **explore the
  full parameter space first** (verification/understanding) before fitting to data.

NetLogo's **BehaviorSpace**, Mesa's **batch_run**, and equivalents automate
running the design and collecting output; use them rather than scripting runs by
hand.

---

## 4. Sensitivity analysis: local vs. global

Sensitivity analysis (SA) answers "which parameters/assumptions actually drive the
results, and how robust is each conclusion?" It is not optional for a model you
intend to believe.

**Local / one-factor-at-a-time (OFAT / OAT).**
Vary one parameter across a range, holding others at defaults; plot output vs.
parameter. Cheap, intuitive, good for *showing the form* of a relationship and
spotting tipping points. Its blind spot: it never varies parameters together, so
it **misses interaction effects** and only probes a thin cross of the space around
the defaults. Fine for illustration; insufficient as the only SA for a model with
interacting parameters.

**Global sensitivity analysis (GSA).**
Varies all parameters simultaneously across the whole space and apportions output
variance among them, capturing interactions.
- **Morris elementary effects** — a screening method; cheap, ranks parameters into
  "negligible / linear / non-linear-or-interacting" without full variance
  decomposition. Good first pass to drop unimportant factors.
- **Variance-based (Sobol) indices** — first-order indices give each parameter's
  direct contribution to output variance; total-effect indices include its
  interactions. The most informative, the most expensive.
- For stochastic ABMs, GSA must handle that the response is a *distribution*;
  recent protocols extend variance-based methods and ICE-style plots to separate
  genuine parameter effects from numerical noise, including significance tests for
  small mean differences. Non-numerical "parameters" (a behavioral rule, an
  interaction topology) need design choices that treat them as categorical factors.

**Practical recipe:** screen with Morris to find the parameters that matter, then
spend the Sobol budget on those, and use OFAT plots to communicate the mechanism
of the few that drive the headline result.

---

## 5. Transient vs. steady state (burn-in)

Many ABMs pass through a **transient** before settling into the regime you
actually want to measure: an artificial initial configuration relaxes, populations
find their working levels, a network reaches its operating structure. Averaging
output over the transient contaminates your steady-state estimate with the
arbitrary starting condition.

- **Decide what you're measuring.** If the question is about long-run/steady-state
  behavior, discard an initial **burn-in (warm-up)** period before collecting
  output. If the question is about the *transient itself* (how fast a disease
  takes off, the path to segregation), then the transient *is* the signal — keep
  it, and don't average it away.
- **Find the burn-in empirically.** Plot the output time series across several
  runs and look for where it stops trending and settles into stationary
  fluctuation; discard up to there. Welch's procedure (average across replications,
  smooth, find where the mean flattens) is the standard method. Don't hard-code a
  round number.
- **Beware models that never settle.** Non-ergodic / path-dependent ABMs may have
  no single steady state — different runs settle into different regimes. Then
  "burn-in then average" is the wrong frame; report the distribution over regimes
  and the initial conditions that lead to each (see boundary conditions in
  `limitations-and-pitfalls.md`).
- **Separate run length from replication count.** How long each run must be (to
  clear the transient and sample the steady state) is a different question from how
  many runs you need (§2). Both must be set deliberately.

---

## 6. Analyzing and reporting output

- **Report distributions, not single runs:** means with dispersion, full
  histograms/violin plots where shape matters, and bands (e.g. 95% intervals from
  replications) when comparing to data or across scenarios.
- **Use appropriate statistics on the run pool:** descriptive stats, hypothesis
  tests comparing scenarios, regression/metamodels relating parameters to outputs,
  clustering/PCA to find regimes. The run pool must be large enough for the test
  you're using.
- **Visualize over space and time:** ABM output usually has spatial and temporal
  structure; aggregate-only summaries can hide the very pattern you built the
  model to study.
- **Tie every reported result to (a) its replication count and (b) its
  sensitivity** — i.e. which parameters it depends on and how strongly. A result
  without these two numbers is not yet a finding.

---

## 7. Common analysis traps

- **Significance ≠ importance ≠ signal.** With a cheap model you can run enough
  replications to make any difference statistically significant; that reflects
  sample size, not a meaningful effect. Always pair p-values with effect sizes and
  show the distributions. Conversely, a "non-significant" difference at low
  replication may just be undersampling.
- **Confusing stochastic noise with a parameter effect** because too few
  replicates were run per sample point.
- **OFAT-only SA** on a model with strong interactions, leading to false claims of
  robustness.
- **Reporting the mean of a multimodal/heavy-tailed output**, which can describe an
  outcome the model never actually produces.
- **Extrapolating beyond the swept ranges**, time horizon, or scales — results are
  conditional on the explored region (boundary conditions; see
  `limitations-and-pitfalls.md`).
- **Post-hoc metric selection** — deciding which output "counts" after seeing the
  runs. Pre-register the observation variables (ODD design concept 11).
