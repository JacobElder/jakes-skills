# The ODD Protocol — Documenting (and Designing) ABMs

**Contents**
1. What ODD is and why it exists
2. The seven elements
3. The eleven design concepts (also a design checklist)
4. The 2020 update: rationale, evaluation, complex-model structure
5. Extensions: ODD+D and TRACE
6. Common ODD failures and a completeness checklist

---

## 1. What ODD is and why it exists

ODD (**O**verview, **D**esign concepts, **D**etails) is the standard format for
describing agent-based and individual-based models, introduced by Grimm et al.
(2006), updated in 2010, and updated again in 2020 (Grimm et al. 2020, *JASSS*
23(2):7). Before ODD, ABM descriptions had no agreed structure, so readers never
knew where to find what, descriptions were routinely incomplete, and models
couldn't be replicated — a direct violation of the basic scientific requirement
that methods be specified well enough to reproduce results. ODD is one of several
responses to the broader replication crisis.

ODD is written in **prose for humans**, independent of the software used. It can
contain equations and short pseudocode but is not code. Its hierarchical
structure lets a reader grasp the whole model before drilling into detail; the
deliberate mild redundancy is a feature, not a bug.

Use ODD for two jobs:
- **Documentation** — the methods section of a paper, a model's standalone
  description, a reproducibility appendix.
- **Design** — walking the seven elements and especially the eleven design
  concepts *while building* forces you to make (and notice) every modeling
  decision. Many groups use ODD as a design workflow, not just a writeup format.

For a journal article, write a concise **ODD summary** and put the full detail in
supplementary material; the 2020 update gives explicit guidance for this and for
pointing readers to specific sections of the model code.

---

## 2. The seven elements

Grouped into the three ODD blocks. Write them in this order.

### Overview

**1. Purpose and patterns.**
State precisely what question the model answers and for whom — a model is built
*for a purpose*, and every later decision is judged against it. The 2020 update
adds **patterns**: name the real-world patterns that make the model useful and
that serve as criteria for its usefulness (this is the hook for pattern-oriented
modeling). "The purpose is to explore X" plus "the model is considered useful if
it reproduces patterns A, B, C."

**2. Entities, state variables, and scales.**
What kinds of agents/entities exist (e.g. individuals, households, firms, cells,
plus the environment/grid). For each, the **state variables** that characterize
it (and only state variables — quantities that are either constant or change over
time, not outputs derived from them). The **scales**: spatial extent and grain,
temporal extent and the length of one time step, and what those units mean in the
real world. A reader should be able to draw the model's data structure from this.

**3. Process overview and scheduling.**
What the agents and the environment *do* — the processes — and crucially **in what
order and how often** they execute, including how time advances and how
simultaneity is handled (e.g. are state changes applied immediately or
synchronously after all agents decide?). Scheduling is a frequent source of
artefacts, so it must be explicit. Name the processes here; the actual equations
and rules go in element 7 (Submodels).

### Design concepts

**4. Design concepts.**
Not subdivided into a fixed schema, but you address the eleven concepts in §3
below. This is what makes an ODD an ABM description rather than a generic model
description — it explains *why* the model is built the way it is and exposes the
emergent vs. imposed distinction.

### Details

**5. Initialization.**
The exact initial state: how many agents, their starting state-variable values,
the starting environment, and whether initialization is deterministic or drawn
from distributions (and if so, which). Enough to set up run number one
identically.

**6. Input data.**
External data driving the model *during* a run (e.g. a time series of weather,
prices, or policy that the model reads in) — as opposed to parameters. If the
model uses no external input, say so explicitly (a common omission).

**7. Submodels.**
The detailed specification of every process named in element 3: the equations,
algorithms, rules, parameters, and their values/units, plus the rationale and any
supporting evidence for each. This is the longest part and the one that makes
reimplementation possible. Each submodel should be testable in isolation.

---

## 3. The eleven design concepts

Address each explicitly; if one doesn't apply, say "not applicable" rather than
omitting it silently — its absence is itself informative. These double as a
**design checklist**: deciding each one *is* designing the model.

1. **Basic principles.** What general theories, concepts, hypotheses, or modeling
   approaches underlie the design? How does the model connect to them?
2. **Emergence.** Which results emerge from agent interactions and adaptation
   (and are therefore the interesting, explanatory outputs), versus which are
   imposed by fixed rules or forced to match data? This is the most important
   concept — the more a key output emerges, the more the model explains and the
   more flexible/predictive it tends to be.
3. **Adaptation.** What adaptive traits do agents have? Do they make decisions in
   response to changes in themselves or their environment? Are these decisions
   modeled as direct objective-seeking, or as fixed rules that merely correlate
   with fitness?
4. **Objectives.** If agents make goal-directed decisions, what objective measure
   (utility, fitness, payoff) do they use, and why?
5. **Learning.** Do agents change their adaptive behavior over time based on
   experience? If so, how is the learning represented?
6. **Prediction.** When agents make decisions, do they predict future conditions?
   How — via internal models, simple heuristics ("tacit prediction"), or assumed
   knowledge?
7. **Sensing.** What internal and environmental state variables can agents
   perceive, and over what range? Be explicit about what is assumed known vs.
   sensed, because "agents can see X" is a strong and often hidden assumption.
8. **Interaction.** What kinds of interaction occur among agents and with the
   environment — direct (agents affect each other) or mediated (via a shared
   resource)? Who can interact with whom (neighbors, network ties, global)?
9. **Stochasticity.** Where and why is randomness used (to represent
   unresolved variability, to initialize, to break ties)? Justify each use —
   stochasticity is not free and shapes the output distribution you'll later
   analyze.
10. **Collectives.** Do agents form or belong to higher-level aggregations (packs,
    households, firms, coalitions) that have their own state and behavior? How are
    these represented — emergent, or imposed?
11. **Observation.** What data are collected from the model for analysis, and how?
    This is the model's "measurement instrument" — define the outputs and summary
    statistics you'll compute, ideally before running, so analysis isn't post-hoc
    fishing.

---

## 4. The 2020 update

The second update (Grimm et al. 2020) responded to recurring problems: ODDs were
too long, struggled with very complex models, often still didn't permit
reimplementation, and lacked room for *why* the model was designed as it was and
*how well it works*. Key additions worth applying:

- **Model rationale / narrative.** Explicit room to explain design decisions and
  the model's underlying "story," not just its mechanics.
- **Evaluation.** A place to describe how the model's fitness for purpose was
  assessed (links naturally to validation — see
  `validation-and-calibration.md`).
- **Structuring complex models.** Guidance for breaking large ODDs into a summary
  plus modular detail, and for referencing the code.
- **ODD for any simulation model.** The authors argue ODD can document non-ABM
  simulations too, aiming at a shared "lingua franca."

---

## 5. Extensions

- **ODD+D (ODD + Decision).** Müller et al. (2013) extension that expands the
  design-concepts section to document **human decision-making** thoroughly —
  theoretical grounding, individual vs. collective decisions, learning, the role
  of uncertainty. Use it when agents represent people and the decision model is
  central (social, economic, land-use models).
- **TRACE (TRAnsparent and Comprehensive Ecological [model] documentation).**
  Grimm et al. (2014) / Schmolke et al. (2010): a documentation format for the
  *entire model development and testing process* — problem formulation, data,
  conceptual model, parameterization, calibration, verification, validation,
  uncertainty — aimed at models used to support decisions/policy. Use TRACE
  alongside ODD when the model needs to be *trusted*, not just understood. ODD
  describes the model; TRACE documents the evidence that it's good enough.

---

## 6. Common ODD failures + completeness checklist

Frequent gaps (call these out when reviewing someone's ODD):

- Purpose stated vaguely, so nothing downstream can be judged against it.
- State variables confused with outputs/auxiliary variables.
- Scheduling and update order left implicit — a top source of irreproducibility
  and artefacts.
- "Input data" omitted entirely instead of stating there is none.
- Design concepts skipped (especially stochasticity, observation, sensing) — so
  the emergent-vs-imposed line is invisible.
- Submodels without parameter values, units, or sources, so reimplementation is
  impossible.
- No statement of how the model was evaluated.

**Quick checklist** — an ODD is reproducible-complete when an independent
modeler could, from the text alone:
- [ ] state the model's purpose and the patterns it targets;
- [ ] enumerate every entity type and its state variables;
- [ ] reconstruct the schedule and update semantics exactly;
- [ ] set up the initial state and identify every input data stream (or confirm none);
- [ ] reimplement every submodel with its parameters, values, units, and rationale;
- [ ] understand which outputs emerge vs. are imposed (design concepts);
- [ ] know what was measured (observation) and how the model was evaluated.
