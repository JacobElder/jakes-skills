# Single-case experimental designs and N-of-1 trials

The idiographic branch for **causal** questions: does manipulating X change *this*
unit's behavior? These are true experiments on one (or a few) units — designed before
data collection, not retrospective case reports.

## Contents
1. Design families
2. Randomization — the engine of validity
3. Analysis: visual, effect sizes, randomization tests
4. N-of-1 trials specifically
5. Generality through replication

---

## 1. Design families

| Design | Logic | Use when |
|---|---|---|
| **ABAB / withdrawal** | introduce, withdraw, reintroduce; effect should track the manipulation | effect is reversible and withdrawal is ethical |
| **Multiple baseline** | stagger intervention onset across behaviors, settings, or people; only the targeted series should change at each onset | effect is **not** reversible (you can't un-learn a skill) |
| **Alternating treatments** | rapidly alternate 2+ conditions, often randomized per session | comparing treatments; want fast within-unit contrast |
| **Changing criterion** | move a performance criterion in steps; behavior should track each step | shaping toward a goal (exercise, smoking reduction) |

Common backbone: a **repeated measurement** of the target over time, a **sequential
(often randomized) introduction** of conditions, and **phase-wise** comparison. The
multiple-baseline logic is especially clean: a confound would have to coincidentally
hit each series exactly when (and only when) intervention started — implausible across
several staggered baselines.

## 2. Randomization — the engine of validity

The strongest single-case work builds **randomization into the design**: randomize the
point at which phases switch (within pre-specified windows that guarantee minimum phase
lengths), or randomize condition order in alternating-treatment designs. This is what
lets you run a **randomization test** with a valid p-value derived from the design
itself, and it raises a single-case study from "interesting observation" toward the
top of the evidence hierarchy (a randomized N-of-1 is, for *this patient*, arguably the
highest level of individual evidence). Decide the randomization scheme and total length
a priori and report them.

## 3. Analysis: three layers, used together

No single number settles a single-case study. Use all three:

**Visual analysis (primary in the behavioral tradition).** Judge level, trend,
variability, immediacy of the effect at phase change, overlap between phases, and
consistency across replications. Use structured aids to curb subjectivity — e.g., the
**conservative dual-criterion (CDC)** method, which projects baseline level *and* trend
into the intervention phase and counts how many points exceed both, reducing Type I/II
error versus eyeballing.

**Effect sizes for single-case data.** Overlap indices (PND, NAP, Tau-U) and
regression-/design-based parametric effect sizes. Each has known weaknesses
(insensitivity to trend, ceiling effects, autocorrelation); report which you used and
why, and prefer ones that handle baseline trend when trend is present. These also feed
meta-analysis across cases.

**Randomization tests (inferential).** If you randomized, you can compute an exact
p-value by comparing the observed test statistic to its distribution over all
permissible randomization outcomes — *no* assumption of normality or independence
required, which matters because single-case series are autocorrelated and short.
Pair the p-value with visual and effect-size evidence; a near-1 p-value can coexist
with a clinically real, visually obvious change (and vice versa), so triangulate.

Do **not** run an ordinary t-test/ANOVA on the raw points: serial dependence violates
independence and inflates false positives.

## 4. N-of-1 trials specifically

The medical instantiation: a single participant, **crossover** design, multiple
treatment periods in **sequentially randomized** order, often double-blind with
placebo and washout periods to handle carryover. Yields an **individual-specific
treatment effect** — the right tool under treatment-effect heterogeneity, where the
population-average effect from a parallel-group RCT may not represent the risk/benefit
to a particular patient.

A **series of N-of-1 trials** can be combined (typically in a multilevel/Bayesian
model) to estimate both each individual's effect *and* the population-average effect —
recovering nomothetic inference without discarding individual fidelity. Powering such a
series means specifying treatment sequences, number of participants per sequence, and
measurements per period. Report to the **CENT** extension of CONSORT.

## 5. Generality through replication

The single-case answer to "but it's just one person" is not aggregation — it is
**systematic replication**: demonstrate the effect, then replicate it across additional
individuals, settings, and behaviors. If the manipulation reliably moves person after
person, generality is established *while preserving* the person-level causal claim.
Analyzing the *mechanism* (why the behavior changed) further supports generalization
beyond the specific cases studied.
