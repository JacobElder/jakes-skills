# Quasi-Experiments (When You Cannot Randomize)

When assignment can't be randomized — the change already shipped to everyone, a
policy applies by rule, ethics forbid withholding, or the unit is a single
market — you can still estimate a causal effect, but every method below
substitutes an *untestable assumption* for the protection randomization gave you
for free. The discipline is to name that assumption out loud and treat it as the
thing the conclusion rests on. A quasi-experiment with a hidden assumption is
just a correlation wearing a lab coat.

## Table of contents
- Difference-in-differences
- Regression discontinuity
- Interrupted time series
- Synthetic control
- Matching / propensity weighting
- Instrumental variables (brief)
- Choosing among them

## Difference-in-differences (DiD)

Compare the before→after change in a treated group to the before→after change in
an untreated comparison group; the difference of the differences nets out both
fixed group differences and common time trends. **Identifying assumption:
parallel trends** — absent treatment, the two groups would have moved in
parallel. Support it (don't prove it) by showing the groups tracked together for
several pre-periods. Threats: a shock that hits one group at the same time as
treatment; treatment timing correlated with pre-existing divergent trends.
Staggered adoption across many units needs modern estimators — the naive
two-way fixed-effects regression is biased when effects vary over time.

## Regression discontinuity (RDD)

When treatment is assigned by a threshold on a continuous running variable
(score ≥ cutoff gets the program), units just above and just below the cutoff
are comparable as-if-random. Estimate the jump in the outcome at the cutoff.
**Identifying assumption: continuity** — everything else varies smoothly through
the cutoff, so the only thing that jumps is treatment. Strong local internal
validity; the estimate is *local* to the cutoff and may not generalize away from
it. Check for manipulation of the running variable (bunching just past the
cutoff) and for other policies sharing the same threshold.

## Interrupted time series (ITS)

Model the outcome's trajectory before an intervention and test for a change in
level and/or slope after it. **Identifying assumption:** absent the
intervention, the pre-trend would have continued unchanged. Strongest when the
series is long and stable and the intervention is sharp and dated; weak against
anything else that happened at the same time. A control series that *didn't* get
the intervention (comparative ITS) greatly strengthens it.

## Synthetic control

For a single treated unit (one state, one market), build a weighted combination
of untreated units that reproduces the treated unit's pre-period trajectory,
then read the gap post-treatment. **Assumption:** the synthetic match captures
the treated unit's counterfactual path. Best with many candidate donors and a
long, well-fit pre-period. Inference is via placebo permutations across donors.

## Matching / propensity weighting

Make treated and untreated units comparable on *observed* covariates — match,
stratify, or weight by the propensity score (modeled probability of treatment).
**Assumption: no unmeasured confounding** (selection on observables / ignorability)
— you've measured and adjusted for everything that drives both assignment and
outcome. This is a strong and untestable assumption; it's the weakest of the
designs here precisely because it offers no protection against the confounder
you didn't think to measure. Always pair with a sensitivity analysis asking how
strong an unmeasured confounder would have to be to overturn the result.

## Instrumental variables (brief)

If you have an instrument — something that shifts treatment but affects the
outcome *only* through treatment (exclusion restriction) and isn't confounded —
you can recover a causal effect (a local average treatment effect) despite
unmeasured confounding. The exclusion restriction is untestable and usually the
contentious part. Powerful when a credible instrument exists (e.g., a lottery,
an arbitrary rule); rare in practice.

## Choosing among them

Pick by which assumption is most defensible for the specific situation, not by
familiarity:

| Situation | Method | Rests on |
|---|---|---|
| Treated + comparison group, panel data, sharp start | DiD | Parallel trends |
| Threshold-based assignment | RDD | Continuity at cutoff |
| One unit, sharp dated change, long series | ITS / synthetic control | Stable pre-trend / good match |
| Rich covariates, plausibly no hidden confounder | Matching / IPW | Selection on observables |
| Credible instrument available | IV | Exclusion restriction |

Whatever you choose, report the assumption as the headline caveat and, where
possible, run a falsification test (placebo outcome, placebo timing, placebo
group) that *should* show no effect if the design is sound.
