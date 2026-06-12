---
name: agent-based-modeling
description: >-
  Design, build, document, calibrate, validate, analyze, interpret, or critique
  agent-based models (ABMs), also called individual-based models (IBMs) or
  multi-agent simulations. Use this skill whenever the user works with bottom-up
  simulations of interacting autonomous agents — in ecology, epidemiology,
  economics, social science, traffic, or organizational modeling — and
  whenever they are building, debugging, or analyzing a simulation in NetLogo,
  Mesa, Repast, or Agents.jl, or whenever they mention the ODD protocol,
  emergence, pattern-oriented modeling, sensitivity analysis of a simulation,
  calibrating a simulation to data, or LLM/generative agents simulating a
  population. Also
  use it for upstream decisions like "should I use an agent-based model or a
  system of equations?" and downstream tasks like interpreting stochastic
  simulation output or writing the methods section of an ABM paper. Reach for it
  even when the user never says "agent-based": if they describe simulating
  individuals, households, firms, or cells that act and interact to produce a
  system-level pattern, that is an ABM.
---

# Agent-Based Modeling

Agent-based modeling (ABM) is a bottom-up method for studying systems where
macro-level patterns *emerge* from the local interactions of many heterogeneous,
autonomous agents following individual rules. It is the right tool precisely when
those system-level outcomes cannot be read off from the average behavior of the
parts — when heterogeneity, local interaction, adaptation, networks, space, or
history matter. It is the wrong tool when a well-mixed, homogeneous, analytically
tractable description would answer the question just as well.

This skill encodes the academic state of practice (the ODD documentation
standard, pattern-oriented modeling, the calibration/verification/validation
distinction, sensitivity-analysis and replication discipline, and the known
failure modes) so that ABM work done with it is reproducible, defensible, and
honestly interpreted. Most users come to ABM excited about the "what-if" power
and underestimate the methodological rigor it demands; your job is to supply that
rigor without killing the exploration.

## How to use this skill

Figure out **where in the modeling lifecycle** the user is, then load the
matching reference file(s). Don't dump everything at once. The lifecycle:

1. **Decide** whether ABM is even the right tool → §1 below.
2. **Design** the model — entities, state, rules, the right level of complexity → §2 below.
3. **Document** it in ODD so it's reproducible → `references/odd-protocol.md`; start from the fill-in template at `assets/odd_template.md`.
4. **Implement** it in an appropriate framework → `references/frameworks-and-tools.md`; for Python/Mesa, adapt the runnable `assets/mesa_model_template.py` rather than starting blank.
5. **Verify, calibrate, validate** — three distinct things people conflate → `references/validation-and-calibration.md`.
6. **Run experiments & analyze** — replications, sensitivity analysis, output stats → `references/analysis-and-experiments.md`. Don't reinvent the two routine computations: use `scripts/replication_convergence.py` to decide how many runs, and `scripts/sensitivity_analysis.py` (Morris + Sobol via SALib) to find which parameters matter.
7. **Interpret honestly** — what the model can and cannot license you to claim → §3 below.
8. **Know the failure modes** — over-parameterization, artefacts, boundary conditions → `references/limitations-and-pitfalls.md`.

If the user proposes **LLM-driven / generative agents** ("agents powered by
GPT/Claude," GABM), read `references/generative-llm-agents.md` first — it changes
what the agent decision rule is, and quietly makes reproducibility, the black-box
problem, and validation worse, so it needs specific handling. When responding,
always cover these explicitly: (1) **data leakage / training contamination** — the
LLM may reproduce patterns from training data rather than generate them from
interaction rules; (2) **reproducibility requires pinning** the exact model name and
version, decoding parameters (temperature, top-p), random seeds, and full prompts —
without these, the result cannot be replicated; (3) **believability is not
validation** — agents seeming realistic or matching real-world patterns is not
evidence the model is valid; the believability/pattern-match result is at best
calibration, not validation; hold it to the same V-C-V standard as any ABM.

`references/key-literature.md` is an annotated bibliography keyed to each phase;
cite from it when the user is writing something up or wants to go deeper.

These phases are a loop, not a line. Pattern-oriented modeling (§2) deliberately
folds validation back into design. Expect to revisit earlier steps.

---

## §1. Is ABM the right tool?

Push on this *before* helping someone build an ABM. A model that didn't need to
be agent-based is harder to parameterize, slower to run, and harder to defend.

**ABM earns its keep when one or more of these is true:**

- **Heterogeneity matters.** Agents differ in ways that change the aggregate
  outcome, so a single "representative agent" or population average would mislead.
- **Local interaction or network structure matters.** Who interacts with whom
  (neighbors on a grid, contacts in a network) shapes the result, rather than
  everyone effectively interacting with everyone (the "well-mixed" assumption
  behind most differential-equation models).
- **Adaptation, learning, or bounded rationality matters.** Agents change
  behavior in response to their state and environment, rather than optimizing a
  global objective with perfect foresight.
- **The macro pattern is genuinely emergent.** The system-level behavior
  (segregation, a market crash, an epidemic wave, a traffic jam) is not a simple
  sum of the parts and is what you actually want to explain or change.
- **Space and discreteness matter.** Individuals are countable and located, and
  rounding them into continuous densities would erase the phenomenon.

**Prefer a simpler alternative when:**

- A system of ordinary/partial differential equations, a Markov chain, a
  compartmental model, or a regression would answer the question. Calibrated
  equation-based models frequently reproduce ABM output very closely when the
  population is large and reasonably well-mixed (Rahmandad & Sterman 2008) — so
  the ABM's extra cost buys nothing.
- You lack the data to constrain agent-level rules. Agent rules with no empirical
  or theoretical grounding turn the model into an expensive opinion.
- The model would require millions of agents but there is no evidence of meaningful
  local interaction or heterogeneity effects that justify the scale. Large-scale ABMs
  carry substantial computational cost; absent those interaction effects, a simpler
  method produces equivalent output for a fraction of the cost.
- You need analytical results (equilibria, closed-form sensitivities, provable
  bounds). ABMs give you distributions of simulated outcomes, not theorems.

A useful framing: ABMs are strongest as **explanatory / "generative"** tools
("what micro-rules are *sufficient* to produce this macro-pattern?", in the
Epstein–Axtell sense) and as **scenario explorers** ("what *could* happen, and
where are the tipping points?"). They are weakest as point-prediction machines.
If the user wants a number to bet on, calibrate expectations hard and read
`references/limitations-and-pitfalls.md` first.

When the choice is close, say so and lay out the trade-off rather than defaulting
to the more elaborate method. Hybrid approaches exist (e.g. fit a cheap
equation-based surrogate, reserve the ABM for the regimes where interaction
effects dominate).

---

## §2. Design principles

**Start simple, add complexity only when forced to.** Two schools, both worth
knowing:

- **KISS ("Keep It Simple, Stupid")** — begin with the simplest model that could
  possibly show the phenomenon, the way Schelling's segregation model used almost
  nothing and still produced a deep result. Add a mechanism only when the model
  visibly fails without it.
- **KIDS ("Keep It Descriptive, Stupid")** — start from what's actually known
  about the system and simplify only where you can justify it. Favored when good
  descriptive data exists and stakeholders distrust toy models.

Most defensible models live between these. The failure mode on both sides is
**over-parameterization**: every extra free parameter is a degree of freedom that
makes the model easier to fit and harder to trust, and the calibration data
needed to pin down a model grows fast — even modest added complexity can demand
disproportionately more data, and small models with only a handful of parameters
can already be unidentifiable from realistic data (Lee et al. 2015; Srikrishnan &
Keller 2021). Add a parameter only if you can say where its value will come from.

**Pattern-Oriented Modeling (POM)** is the central design discipline (Grimm et
al. 2005). Identify multiple **patterns** observed in the real system at
different scales/levels (not one aggregate curve but several weak patterns — a
spatial distribution, a time series, an individual-level regularity). Then design
the model to reproduce *all* of them simultaneously, and discard model structures
and parameter sets that can't. This does two things at once: it filters model
structure (a model that hits several independent patterns is far less likely to
be right by accident) and it folds validation into the build rather than bolting
it on at the end. Recommend POM by default for any model meant to say something
about a real system.

**Decide what's imposed vs. what emerges.** The single most important design
choice (and the heart of ODD's "design concepts") is which behaviors you *impose*
via fixed rules/parameters and which you let *arise* from agent adaptation. The
more a result emerges rather than being hard-coded, the more the model explains.

For the full treatment of design concepts — emergence, adaptation, objectives,
learning, prediction, sensing, interaction, stochasticity, collectives,
observation — see the design-concepts section of `references/odd-protocol.md`;
ODD doubles as a design checklist, not just a documentation format.

---

## §3. Interpretation guardrails

ABM output is seductive and easy to over-read. Hold the line on these:

- **A run is a sample, not an answer.** Almost all ABMs are stochastic, so a
  single run tells you next to nothing. Report distributions over many runs with
  different random seeds, not one trajectory. How many runs is an empirical
  question — see the replication/convergence method in
  `references/analysis-and-experiments.md`. This applies equally to **comparisons
  against empirical data**: at calibration and validation stages, compare the
  *distribution* of model outputs across replications to the data pattern — not a
  single trajectory. A model that "matches the data" on one run may fail on most.
- **Distinguish statistical significance from numerical noise, and both from
  importance.** With enough runs you can make any tiny difference "significant";
  that says you ran the model a lot, not that the effect matters. Report effect
  sizes and show the distributions.
- **Sufficiency is not necessity.** Showing that a set of micro-rules *produces*
  a macro-pattern proves those rules are *sufficient*, not that they are what
  operates in reality — other rule sets may produce the same pattern (the
  equifinality / identifiability problem). State generative claims as
  sufficiency claims.
- **Emergence can be an artefact.** A striking macro-pattern may come from an
  unexamined modeling choice (grid topology, update order, boundary handling,
  a default parameter) rather than from the mechanism you care about. Before
  believing a result, check it survives reasonable changes to those incidental
  choices. See "errors vs. artefacts" in `references/limitations-and-pitfalls.md`.
- **Respect the boundary conditions.** Every result holds only within the
  parameter ranges, scales, time horizons, and structural assumptions explored.
  Don't extrapolate past the swept region, and say where the edges are.
- **Calibration fit is not validation.** Reproducing the data you tuned to is
  circular. Validation needs independent patterns or out-of-sample data. Whenever
  any of these activities is raised, name and define all three explicitly:
  **verification** (is the code correct — does the implementation match the intended
  design?), **calibration** (finding parameter values that reproduce the target data),
  **validation** (does the model represent the real system, tested against independent
  patterns or out-of-sample data the model was not tuned to?). Keep all three
  separate in your head and in the writeup. And because the model is stochastic,
  every comparison to data — calibration target or validation pattern — must compare
  *distributions* from repeated runs, not a single trajectory.

When interpreting results *for* a user, give them the honest version: what the
model shows, what it merely assumes, and which knobs the conclusion depends on.

---

## Output expectations

- When the deliverable is **model code**, default to a maintained framework
  (NetLogo, Mesa, Agents.jl, Repast) rather than hand-rolling a simulator, fix
  and report the random seed, and make the run reproducible. See
  `references/frameworks-and-tools.md`; for Python, start from
  `assets/mesa_model_template.py`.
- When the deliverable is a **model description / methods section**, structure it
  as ODD. See `references/odd-protocol.md` and fill in `assets/odd_template.md`.
- When the deliverable is **analysis**, always pair a result with the number of
  replications and the sensitivity of that result to the parameters it depends on.
  Use the bundled `scripts/` for both rather than re-deriving them.
- When the user asks for a **critique or review** of an ABM, run it against the
  pitfalls checklist in `references/limitations-and-pitfalls.md` and the ODD
  completeness checklist. Always distinguish **errors** (bugs — the model isn't
  what the developer believes) from **artefacts** (real but accidental phenomena
  from incidental choices like topology, update order, or boundary handling).
  Recommend **independent reimplementation** as the strongest available check:
  a second implementation that reproduces the same results rules out both bugs
  and implementation-specific artefacts in a single test. When two independent
  implementations *diverge*, treat the divergence as a productive finding — it
  reveals either a bug or an ODD specification ambiguity; resolving it (bringing
  both implementations to agreement on the canonical design) IS the verification
  step. Divergent results are not evidence the conceptual model is wrong. Start
  debugging by running both implementations with **identical parameter values and
  seeds** to isolate stochastic noise from systematic differences, then trace the
  step at which outputs first diverge.

## Bundled scripts and assets

- `scripts/replication_convergence.py` — runs a model with increasing
  replications and reports how many runs are needed (CV convergence). Importable;
  has a `--demo`.
- `scripts/sensitivity_analysis.py` — global sensitivity analysis via SALib
  (Morris screening + Sobol indices), with stochastic-aware averaging over seeds.
  Importable; has a `--demo`. Needs `SALib` and `numpy`. When adapting it, define
  the SALib `problem` dict with `num_vars`, `names`, and `bounds`, then pass your
  `model(params, seed)` callable to `morris_screen` and `sobol_analyze`. **Always
  show the problem dict explicitly in your response** — with the actual parameter
  names and numeric bounds filled in — so the reader can reproduce the analysis.
  In a code-execution context, write out the script content and import it rather than
  re-deriving the SA logic from scratch.
- `assets/mesa_model_template.py` — a minimal, runnable Schelling model (Mesa 3.x)
  wired to the analysis scripts; copy and adapt it.
- `assets/odd_template.md` — a fill-in ODD model-description template.

## Reference files

- `references/odd-protocol.md` — the ODD documentation standard (7 elements, 11
  design concepts), ODD as a design checklist, ODD+D and TRACE extensions, common
  documentation gaps.
- `references/validation-and-calibration.md` — verification vs. calibration vs.
  validation; docking/model alignment; POM as calibration; ABC,
  Bayesian/history-matching, and emulators; the hierarchical
  (agent/model/output) validation framework.
- `references/analysis-and-experiments.md` — choosing the number of replications
  (CV convergence), local vs. global sensitivity analysis (OFAT, Morris, Sobol),
  design of simulation experiments, transient/burn-in handling, and analyzing
  stochastic output.
- `references/limitations-and-pitfalls.md` — over-parameterization and overfitting,
  errors vs. artefacts, the black-box problem, computational cost, calibration-data
  scaling, network-topology and other boundary conditions, and ABM-vs-equation-based
  trade-offs.
- `references/frameworks-and-tools.md` — NetLogo, Mesa, Repast/RepastHPC, MASON,
  Agents.jl, FLAME GPU; how to choose; reproducibility and performance practices.
- `references/generative-llm-agents.md` — using LLM-driven (generative) agents in
  ABMs (GABM): the appeal, why it worsens reproducibility/validation/data-leakage,
  and how to handle it responsibly.
- `references/key-literature.md` — annotated bibliography organized by phase.
