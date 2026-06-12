# Online & Product Experimentation (A/B Testing at Scale)

Running A/B tests on a live product introduces failure modes that classical
experimental design textbooks barely mention. This file covers the ones that
actually bite at scale.

## Table of contents
- Sanity checks before you trust anything (SRM)
- Variance reduction (CUPED)
- The peeking problem and sequential testing
- Interference and the unit-of-randomization decision
- Guardrail metrics and metric design
- Ramp-up, exposure, and the analysis population
- Novelty and primacy effects
- Triggered / counterfactual logging

## Sanity checks before you trust anything

**Sample Ratio Mismatch (SRM).** If you assigned 50/50 but observe 50.8/49.2 on
large N, stop — the split is broken and *every* downstream metric is suspect.
Run a chi-square goodness-of-fit on the observed vs. expected allocation; a tiny
p-value (say < 0.001) means something is wrong with assignment, logging, or
filtering (e.g., a redirect that drops one arm, bot traffic hitting one
variant). SRM is the single highest-value check; do it first, every time, before
reading any treatment effect.

Other pre-flight checks: A/A tests (run treatment = control to confirm the
pipeline produces ~5% false positives and not more), and confirming that
pre-experiment metrics are balanced across arms.

## Variance reduction (CUPED)

**CUPED** (Controlled-experiment Using Pre-Experiment Data) regresses out
pre-period values of the metric, exploiting the strong correlation between a
user's past and present behavior. It can cut variance 30–50% on metrics with
high pre/post correlation, which is equivalent to a large free boost in sample
size — often the cheapest way to make an underpowered test feasible. The
adjusted metric is `Y - θ(X - E[X])`, where X is the pre-period covariate and θ
is its regression coefficient. It's unbiased (the covariate is pre-treatment, so
it can't be affected by the treatment) and should be planned in advance.
Stratification and covariate-adjusted regression achieve the same end.

## The peeking problem and sequential testing

A fixed-horizon test is valid *only* if you decide N in advance and look once.
Continuously monitoring and stopping the moment p < 0.05 inflates the
false-positive rate severely — daily peeking on a nominally 5% test can push the
true rate above 30%, because you've given yourself many correlated chances to
cross the line by chance.

Two legitimate ways to look early:
- **Group-sequential designs** — pre-planned interim analyses with adjusted
  boundaries (O'Brien-Fleming, Pocock) that spend the α budget across looks.
- **Always-valid inference** — sequential p-values / confidence sequences
  (mSPRT and related) that remain valid under continuous monitoring, at the cost
  of needing a larger effect or more data to declare significance.

If the platform shows a running "significance" indicator that updates live, it's
either using one of these methods or it's lying to you; find out which.

A **Bayesian** approach is a different answer to the same monitoring pressure:
because a posterior is valid to read at any time, Bayesian platforms let you
monitor continuously without the frequentist peeking penalty — but the prior and
the ship-decision threshold (e.g. "ship when P(treatment > control) > 0.95" or
"when expected loss < ε") do real work and must be fixed in advance, or you've
just moved the garden of forking paths somewhere less visible. See
`interpreting-results.md` for how the two frameworks change the ship decision.

## Interference and the unit-of-randomization decision

Individual-level randomization assumes one user's treatment doesn't affect
another user's outcome (SUTVA). That assumption breaks in:
- **Two-sided marketplaces** — treating buyers changes inventory/prices for
  controls; treating sellers changes what buyers see.
- **Social / network products** — a feature that changes what one user posts
  changes what their friends in control see.
- **Shared resources** — budgets, rankings, supply that treatment and control
  compete over.

When interference is present, individual randomization *biases* the estimate
(often making the effect look bigger than the real launch effect). Remedies:
cluster-randomize by a unit that contains the spillover (geo, market, social
cluster, time-slice/switchback), or use specialized network/marketplace designs.
The bias here is not noise you can average away — it's systematic, so flag it as
a first-class design decision, not a footnote.

## Guardrail metrics and metric design

Pre-specify metrics that must not regress: latency/load time, crash and error
rates, revenue, retention, unsubscribe/complaint rates. A treatment that lifts
the primary metric while degrading a guardrail is usually not shippable. Set
guardrails up as one-sided non-inferiority checks with their own thresholds.

Metric quality principles:
- **One primary**, with construct validity — it should move only when real value
  is created, and be hard to game.
- Watch for **proxy metrics** that are sensitive but decoupled from value (clicks
  that don't convert, sessions inflated by a confusing UI).
- **Surrogate outcomes** (a short-term signal standing in for a long-term one)
  need validation that the surrogate actually predicts the long-term effect, or
  a long-term holdback to check.
- **Ratio metrics with a random denominator** (revenue-per-session,
  clicks-per-pageview when you randomize by user) must be analyzed with
  delta-method or bootstrapped variance, not as a simple mean — the naive
  variance ignores within-user correlation and inflates false positives. See
  `power-and-sample-size.md`.

## Ramp-up, exposure, and the analysis population

Ramp the treatment gradually (1% → 5% → 50%) to catch catastrophic regressions
cheaply before full exposure. The analysis population should be defined by
**triggering**: only users who actually reach the code path where treatment and
control differ should be in the analysis — diluting with users who never saw the
change shrinks the measured effect and wastes power. Analyze by assignment (ITT)
within the triggered population.

## Novelty and primacy effects

Users react to *change itself*. Novelty effects inflate early treatment metrics
(people click the shiny new thing); primacy effects depress them (people are
confused by the unfamiliar, then adapt). Both fade. A one-week test can badly
mis-estimate the steady-state effect. Mitigations: run long enough for the
curves to flatten, analyze new vs. returning users separately, or use a
long-term holdback that keeps a small control group un-treated for months to
read the durable effect.

## Triggered / counterfactual logging

To measure effects cleanly you need to log the counterfactual: for control
users, record where they *would have* hit the treatment path. Without
counterfactual/triggered logging you can't define the triggered population
symmetrically across arms, and the effect estimate gets diluted or biased.
