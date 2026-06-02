# Design Selection

A chooser for matching an experimental design to the situation. Start from the
constraints (can you randomize? is the treatment sticky? is there interference?
how scarce are units?) and let them eliminate options, rather than starting from
a favorite design.

## Table of contents
- Quick chooser
- Between-subjects (parallel groups)
- Within-subjects (repeated measures / crossover)
- Mixed designs
- Factorial designs
- Cluster-randomized designs
- Stepped-wedge / staggered rollout
- When you cannot randomize

## Quick chooser

| If... | Lean toward |
|---|---|
| Treatment is sticky / can't be undone (redesign, account change) | Between-subjects |
| Treatment is transient and units can see several conditions | Within-subjects (counterbalanced) |
| Units are scarce and outcome variance is high | Within-subjects or heavy blocking |
| Treated units can affect control units (feeds, markets, social) | Cluster-randomized |
| Several factors / you care about interactions | Factorial |
| Rollout must reach everyone eventually, but can be phased | Stepped-wedge |
| Random assignment is impossible | Quasi-experiment (see quasi-experiments.md) |

## Between-subjects (parallel groups)

Each unit experiences exactly one condition. The default for online A/B tests
and most clinical/field work. Robust, simple to analyze, no carryover or order
effects. The cost is statistical efficiency: all between-unit variance lands in
the comparison, so you need more units than a within-subjects design to reach
the same power. Reduce that cost with blocking/stratified randomization on
strong pre-treatment predictors of the outcome, or with covariate adjustment
(CUPED in the online setting).

## Within-subjects (repeated measures / crossover)

Each unit experiences multiple conditions; each serves as its own control,
which removes stable between-unit differences and can cut required sample size
by an order of magnitude when units are heterogeneous.

Costs and guards:
- **Order / carryover effects.** Exposure to one condition contaminates the
  next. **Counterbalance** the order (e.g., Latin square) so order is orthogonal
  to condition, and/or insert washout periods.
- **Not usable for sticky treatments.** You can't show someone the old UI after
  the new one and expect a clean read.
- **Fatigue / practice / demand effects** in human studies grow with the number
  of exposures.

A *crossover* design is the formalized two-period version (AB / BA), common in
clinical trials.

## Mixed designs

At least one between-subjects factor and one within-subjects factor. Standard in
behavioral research — e.g., condition is between-subjects, time (pre/post) is
within-subjects. Analyzed with mixed-effects models that put random effects on
the repeated-measures grouping. Powerful but the analysis must respect the
nesting; the unit-of-analysis rule (match analysis to randomization) is where
people slip.

## Factorial designs

Manipulate two or more factors simultaneously, crossing all levels (a 2×2 tests
factors A and B at two levels each → four cells). Two payoffs: you test multiple
factors for roughly the cost of one, and you can estimate **interactions**
(does the effect of A depend on the level of B?), which separate one-factor-at-
a-time studies can never see. Fractional factorial designs trade some
interaction estimates for far fewer cells when factors are many. Watch the power
math: powering for an interaction typically needs substantially more N than
powering for a main effect.

## Cluster-randomized designs

Randomize groups (regions, stores, schools, time windows) rather than
individuals. The reason is almost always **interference**: when treated units
affect control units, individual randomization violates SUTVA and biases the
estimate. Clustering contains the spillover within a cluster.

The price is power. Outcomes within a cluster are correlated (intracluster
correlation, ICC), so the effective sample size is far below the raw count. The
**design effect** ≈ 1 + (m − 1)·ICC, where m is cluster size — inflate your
required sample by this factor. Even a small ICC with large clusters can multiply
the needed N many times over. Number of clusters matters more than units per
cluster for power; favor more, smaller clusters when you can.

## Stepped-wedge / staggered rollout

Clusters cross over from control to treatment at randomized, staggered times,
until all are treated. Useful when the intervention must eventually reach
everyone (so a permanent control is impossible) and when phased logistics are
required anyway. Every cluster contributes both control and treatment
observations, which helps power, but the design is **confounded with time** by
construction — the analysis must model secular time trends carefully, and an
unexpected external shock during the rollout can be hard to disentangle.

## When you cannot randomize

If assignment can't be randomized at all, you're in quasi-experimental
territory. Don't pretend otherwise — switch to `quasi-experiments.md`, pick the
method whose identifying assumption is most plausible for the situation, and
state that assumption out loud as the thing the conclusion rests on.
