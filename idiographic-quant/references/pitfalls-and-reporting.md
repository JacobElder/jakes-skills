# Pitfalls, recurring critiques, and reporting

This is where idiographic projects live or die. Reviewers and skeptics attack the same
points every time; address them before they're raised.

## 1. The pitfalls, in priority order

1. **Too few time points for the model.** The dominant failure. Network parameters
   grow ~quadratically with node count; a regularized lag-1 network over k nodes is
   estimating on the order of k² + k(k+1)/2 parameters from T occasions. With small T
   the estimates are noise. **Fix:** cut nodes, drop the temporal layer (keep
   contemporaneous), or collect more occasions. Reducing the model is a *result*, not a
   failure.
2. **Stationarity assumed, not checked.** Most VAR/network/DSEM output is meaningless
   if the dynamics drift over the window — and theory often predicts drift. **Fix:**
   plot and test for trends/level-shifts/variance changes; detrend, split regimes, or
   use models that allow time-varying parameters (e.g., TV-VAR / GAM-based, or
   change-point approaches).
3. **Unreliable person-specific estimates treated as portraits.** Idiographic networks
   can differ substantially across waves for the *same* person; lagged edges are less
   reproducible than contemporaneous ones; sometimes only a minority of fitted networks
   are interpretable at all, and they may yield no actionable intervention targets.
   **Fix:** quantify stability concretely — bootnet (edge-weight and case-drop
   bootstraps) for regularized networks, posterior intervals for DSEM, or refit on split
   halves / successive waves and report what survives. Don't present point estimates as
   fact; an edge that doesn't survive resampling is not a finding.
4. **Within-person reliability ≠ between-person reliability.** A scale validated
   between people may be unreliable for tracking one person's fluctuations. Centering on
   noisy observed person means induces **Lüdtke** and **Nickell** biases. **Fix:** use
   latent person-mean centering (DSEM); assess within-person reliability directly.
5. **Sampling interval mismatched to the process — or unequally spaced.** Lagged effects
   are defined by the lag; the wrong interval studies the wrong construct or misses the
   dynamic entirely. And ESM beeps are usually *unequally* spaced, which biases
   discrete-time lagged estimates. **Fix:** justify the interval from theory; for
   irregular spacing use a continuous-time model (ctsem) or DSEM `TINTERVAL`.
6. **Ordinary inferential stats on serially dependent single-case data.** t-tests on
   autocorrelated points inflate false positives. **Fix:** randomization tests +
   single-case effect sizes + structured visual analysis.
7. **The silent ergodicity slide.** Estimating between-person structure and narrating
   it as within-person mechanism. **Fix:** keep the level of the claim equal to the
   level of the analysis.

## 2. The recurring critiques (and the honest responses)

- *"n=1 — you found a pattern in noise."* → Pre-registered design, randomization-based
  inference, replication across cases, reported stability/uncertainty.
- *"Your network is just unstable."* → Report multi-wave/bootstrap stability; lean on
  contemporaneous structure; don't overstate lagged edges.
- *"Comparing within vs between proves nothing (Hamaker & Ryan)."* → Agreed in the
  abstract; the point is that a person-level question demands person-level data, which
  is why you measured the individual — not a claim that group methods are universally
  invalid.
- *"This contradicts your own dynamic-systems theory (stationarity)."* → Acknowledge the
  tension; test stationarity; model nonstationarity rather than assuming it away.

## 3. Interpreting a network without fooling yourself

Fitting the network is the easy part; reading it is where the damage happens, especially
when the goal is to "pick an intervention target." Guard against four seductive errors:

- **Centrality is not a treatment-target finder.** The reflex is "the most central node is
  the thing to intervene on." But centrality indices (especially betweenness and closeness)
  are poorly behaved in psychological networks — they were built for sparse routing-type
  graphs, not dense partial-correlation graphs, and they're often unstable across bootstraps
  (Bringmann et al., 2019, *J. Abnormal Psychology*). Strength is the least bad of them, but
  a high-strength node is a *hypothesis* about a target, not a demonstration. Whether
  intervening on it actually helps is a causal/experimental question the network can't
  answer.
- **Directed (lagged) edges are not causal arrows.** A lag-1 edge from rumination to mood
  means rumination predicts later mood *in this data*, conditional on the included nodes. An
  omitted common cause, the chosen lag interval, or measurement timing can all produce or
  erase it. Don't narrate temporal precedence as mechanism.
- **Cross-sectional symptom networks don't license individual claims.** A network estimated
  from one timepoint across many people is a *between-person* object — it cannot tell you how
  symptoms drive each other within a person over time, and a central node there is not "the
  individual's" target. This is the ergodicity slide wearing network clothing. If you want a
  person's structure, you need that person's time series.
- **Density/connectivity comparisons are fragile.** "This person's network is denser, so
  they're more dysregulated" depends on regularization settings, T, and variance, which
  differ across people. Compare with great caution and only with matched estimation.

The honest framing for any single fitted network: *here is an estimated, uncertain map of
associations; the central nodes are hypotheses worth testing, not established levers.*

## 4. Reporting checklist (general idiographic / intensive longitudinal)

- T per unit; sampling scheme and interval; study duration.
- Compliance and missingness over time (not just an overall %).
- Stationarity: what you checked and what you did about it.
- Model specification: lags, regularization/EBIC gamma or priors, centering approach,
  estimator (and one-step vs two-step for DSEM).
- Raw time series shown alongside the fitted model.
- Uncertainty/stability quantified, not just point estimates.
- Per-person results when multiple units — resist collapsing to an average that
  re-hides the heterogeneity you set out to study.

## 5. Formal reporting standards

- **SCRIBE** — Single-Case Reporting guideline In BEhavioural interventions; the
  standard for behavioral single-case experiments.
- **CENT** — CONSORT Extension for N-of-1 Trials; for (series of) N-of-1 clinical
  trials.
- **What Works Clearinghouse** single-case design standards — widely used quality
  criteria (e.g., minimum phases, data points per phase, demonstrations of effect) for
  judging SCED rigor.

Cite the one that matches your design and follow its item list; reviewers in the
relevant field will expect it.
