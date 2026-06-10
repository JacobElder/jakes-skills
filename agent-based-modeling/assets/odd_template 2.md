# ODD Model Description: [MODEL NAME]

> Fill-in template for an ODD (Overview, Design concepts, Details) model
> description, following Grimm et al. (2020). Replace every `[...]` and delete the
> `>` guidance lines before use. Keep it prose for humans; equations and short
> pseudocode are fine, code is not. For a journal article, keep this as a concise
> *ODD summary* and push exhaustive detail to supplementary material.
>
> Authors / version / date: [...]   Corresponds to code version/commit: [...]

## 1. Purpose and patterns

> One or two sentences: what question does this model answer, and for whom?
> Then the patterns: which real-world patterns make the model useful and serve as
> the criteria for judging it? (These are the hook for pattern-oriented modeling.)

- **Purpose:** [...]
- **Patterns used as criteria for usefulness:** [pattern 1 at scale X], [pattern 2 at scale Y], [...]

## 2. Entities, state variables, and scales

> Every kind of entity (agent types + the environment/grid), the state variables
> that characterize each (only true state variables — not outputs derived from
> them), and the scales (spatial extent & grain, temporal extent & step length)
> with their real-world meaning.

- **Entities:** [agent type(s)], [environment / spatial unit], [collectives, if any]
- **State variables per entity:**
  - [Agent type A]: [var1 (units), var2 (units), ...]
  - [Environment cell]: [var1 (units), ...]
- **Scales:** 1 time step = [...]; total duration = [...]; spatial grain = [...]; extent = [...].

## 3. Process overview and scheduling

> What do entities and the environment DO, in WHAT ORDER, and HOW OFTEN? State how
> time advances and whether state updates are synchronous (all decide, then all
> update) or asynchronous (each acts in turn) — this is a frequent source of
> artefacts, so be explicit. Name processes here; specify them in §7.

Each time step, in order:
1. [process 1 — which entities, brief]
2. [process 2 — ...]
3. [observation / data collection]

Update semantics: [synchronous / asynchronous]; agent execution order: [fixed / shuffled each step / by attribute].

## 4. Design concepts

> Address each. If one does not apply, write "Not applicable" rather than omitting
> it — its absence is informative. The pivotal one is Emergence: state which
> outcomes you let arise vs. impose.

- **Basic principles:** [theories/concepts the model builds on]
- **Emergence:** [what emerges from interaction/adaptation] vs. **imposed:** [what is fixed by rules/parameters]
- **Adaptation:** [adaptive traits / decisions agents make]
- **Objectives:** [objective/utility/fitness measure, if any]
- **Learning:** [how behavior changes with experience, or N/A]
- **Prediction:** [how agents anticipate future conditions, or N/A]
- **Sensing:** [what each agent can perceive, and over what range]
- **Interaction:** [direct/mediated; who interacts with whom — neighbors/network/global]
- **Stochasticity:** [where randomness is used and why]
- **Collectives:** [higher-level groupings and how represented, or N/A]
- **Observation:** [what data are collected for analysis, and how]

## 5. Initialization

> The exact initial state: how many entities, their starting values, the starting
> environment, and whether initialization is deterministic or drawn from
> distributions (which ones). Enough to set up run #1 identically.

[...]

## 6. Input data

> External data that drive the model DURING a run (time series of weather, prices,
> policy, etc.) — as opposed to parameters. If there are none, say so explicitly.

[The model does not use external input data. — OR — describe sources/format.]

## 7. Submodels

> The detailed specification of every process named in §3: equations, algorithms,
> rules, all parameters with VALUES, UNITS, and SOURCES/RATIONALE. This is what
> makes reimplementation possible; each submodel should be testable in isolation.

### 7.1 [Submodel / process name]
- Description / equation / pseudocode: [...]
- Parameters: [name = value (units), source/justification], [...]

### 7.2 [...]

---

## Evaluation (recommended; 2020 update)

> How was the model's fitness for purpose assessed? Verification done, calibration
> approach and data, validation against which independent patterns/data, key
> sensitivity-analysis findings. For decision-support models, document this fully
> with TRACE alongside this ODD.

- Verification: [...]
- Calibration: [parameters calibrated, method, data]
- Validation: [independent patterns/data, results]
- Sensitivity analysis: [method, which parameters dominate]
