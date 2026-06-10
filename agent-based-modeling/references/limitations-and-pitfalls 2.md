# Limitations, Pitfalls, and Boundary Conditions

ABM's strengths (heterogeneity, interaction, emergence, few simplifying
assumptions) are the same features that create its characteristic failure modes.
Use this both to avoid the traps when building, and as a checklist when reviewing
or critiquing a model.

**Contents**
1. Pros and cons at a glance
2. Over-parameterization and overfitting
3. Errors vs. artefacts
4. The black-box / interpretability problem
5. Calibration-data scaling and identifiability
6. Computational cost
7. Boundary conditions — the limits on any ABM claim
8. When ABM is the wrong tool (and what to use instead)
9. A critique checklist

---

## 1. Pros and cons at a glance

**Strengths.**
- Represents **heterogeneous** agents directly, instead of a representative average.
- Captures **local interaction, networks, and space** that well-mixed models erase.
- Models **adaptation, learning, and bounded rationality** rather than global
  optimization with perfect foresight.
- **Grows** macro patterns from micro rules ("generative" explanation), revealing
  emergence, non-linearity, tipping points, and second-order effects.
- Excellent for **what-if scenario exploration** and finding vulnerabilities that
  aggregate models miss.

**Weaknesses.**
- Many parameters and rules, often weakly grounded → **over-parameterization /
  overfitting** and "ad-hoc assumption" criticism.
- Hard to **validate and calibrate**; results can be **artefacts**; the
  micro→macro mapping can be a **black box**.
- **Computationally expensive**; stochastic, so needs many replications.
- Gives **distributions of simulated outcomes, not theorems or reliable point
  predictions**.
- Reproducibility has historically been poor without disciplined documentation.

The honest summary: ABMs are powerful for *understanding mechanisms and exploring
possibilities*, and risky as *prediction engines*. Match the claim to the tool.

---

## 2. Over-parameterization and overfitting

The dominant methodological risk. An over-parameterized model includes variables
and dynamics beyond what the evidence supports. Extra degrees of freedom make it
easier to fit observations and **more likely to overfit** — to match the
calibration data while generalizing poorly out of sample, adding cost and
complexity for minimal theoretical benefit (Lee et al. 2015).

A subtle, important result: the data required to constrain a model grows fast with
complexity. Even adding a single interaction term can demand disproportionately
more (and more spatially-resolved) data to identify; limited or spatially
aggregated data may be unable to distinguish a model *with* inter-agent
interactions from one *without*, even at only ~four parameters (Srikrishnan &
Keller 2021/arXiv 1811.08524). Implications:
- Resist "just one more rule." Add a parameter only if you can name its data or
  theory source.
- Use **informative priors** when calibrating descriptive ABMs — flat priors plus
  thin data leave parameters unidentified.
- Bring **independent lines of evidence** (multiple patterns; spatially explicit
  data) to select structure, since aggregate fit alone won't.

Note this cuts both ways: equation-based models (e.g. DSGE) also make arbitrary
choices — they're just hidden inside functional forms. The fix is honesty about
assumptions, not abandoning ABM.

---

## 3. Errors vs. artefacts

A crucial distinction (Galán et al. 2009, "Errors and Artefacts in Agent-Based
Modelling"):

- **Errors** — mismatches between what the developer *believes* the model is and
  what it *actually* is. Bugs, in code or in the conceptual-to-code translation.
- **Artefacts** — real, significant phenomena in the model caused by *accessory
  assumptions* mistakenly considered insignificant: grid topology (von Neumann vs.
  Moore neighborhood, torus vs. bounded edges), agent **update order** and
  synchronous vs. asynchronous updating, tie-breaking rules, time-step size,
  random-number details.

Both produce output that looks like a finding but is an accident of
implementation. Because ABM dynamics are often so complex that even their
developers can't fully trace how a result arises, it can be genuinely hard to tell
a legitimate implication of your assumptions from an artefact. Defenses:
- Before believing a striking result, **change the incidental choices** (topology,
  update scheme, boundaries, seed handling) and check it survives.
- Study the **full parameter space** before fitting to data, so strange/incoherent
  output surfaces early rather than being rationalized later.
- Independent **reimplementation** is the strongest artefact detector.

---

## 4. The black-box / interpretability problem

The same emergence that makes ABMs valuable makes them opaque: it can be hard to
attribute a macro outcome to specific micro rules, which invites a "black box"
perception and undercuts trust. Mitigations:
- Build up **incrementally** (KISS), so you know which mechanism added which
  behavior.
- Use **sensitivity analysis** to map which parameters drive which outputs.
- Trace mechanisms with controlled experiments: switch a single mechanism off and
  observe what disappears.
- Document the reasoning with **TRACE** (see `odd-protocol.md`) when the model must
  be trusted for decisions.

Note: using **LLM-driven (generative) agents** makes this far worse — the decision
rule itself becomes an opaque neural net, and apparent emergence can be the model
recalling training data rather than generating the pattern. See
`generative-llm-agents.md` before going down that road.

---

## 5. Calibration-data scaling and identifiability

(Closely tied to §2.) Two practical limits:
- **Identifiability / equifinality** — multiple parameter sets, and even multiple
  model structures, can reproduce the same observations. A single "best-fit" point
  can be illusory; report the acceptable *region* and test whether the data
  actually distinguish competing structures.
- **Data hunger** — realistic, often aggregated, datasets frequently can't pin down
  the micro-rules ABMs encode. Spatially or temporally resolved data, and multiple
  independent patterns, are worth far more than more of the same aggregate series.

---

## 6. Computational cost

Large agent populations, rich rules, many replications, and wide parameter sweeps
multiply quickly; this can make thorough calibration and global sensitivity
analysis infeasible. Levers:
- Reduce model complexity to what the purpose requires (KISS again).
- Use **emulators/surrogates** to stand in for the full model during calibration
  and GSA (see `validation-and-calibration.md`).
- Use performance-oriented frameworks or hardware (RepastHPC, MASON's distributed
  mode, FLAME GPU; compiled languages; Agents.jl) — see `frameworks-and-tools.md`.
- Budget honestly: if you can only afford few replicates or a coarse sweep, widen
  your stated uncertainty rather than overclaiming.

---

## 7. Boundary conditions — the limits on any ABM claim

Every ABM result is conditional. State these limits explicitly with any finding:
- **Parameter ranges** actually explored — no extrapolation beyond the swept region.
- **Scales** — spatial extent/grain and temporal step/horizon; behavior can change
  qualitatively at other scales.
- **Structural assumptions** — interaction topology, what agents can sense, the
  decision model, the sources of stochasticity. Conclusions are contingent on these.
- **Interaction/network topology specifically.** When agents interact over a
  network, the network *is* a major modeling assumption, not scenery: the degree
  distribution, clustering, and how the network was generated (random, small-world,
  scale-free, or empirical) can change the macro outcome as much as any parameter.
  If you generated the network, its structure is an assumption to justify and vary;
  if you measured it, its sampling is a boundary condition. Treat "which network?"
  as a factor in sensitivity analysis, not a fixed backdrop.
- **Initial conditions and path dependence** — non-ergodic models can land in
  different regimes from different starts; one initialization isn't general.
- **Population size / well-mixedness regime** — interaction effects that dominate in
  small/structured populations may wash out in large well-mixed ones (where an
  equation-based model would have sufficed).
- **The model's stated purpose** — a model validated for explanation is not thereby
  licensed for prediction or policy point-estimates.

---

## 8. When ABM is the wrong tool

Reach for something simpler when:
- The system is **well-mixed and homogeneous** enough that a compartmental/ODE
  model, Markov chain, or regression answers the question. Calibrated ODE models
  often reproduce ABM output closely under these conditions (Rahmandad & Sterman
  2008) — the ABM's extra cost buys nothing.
- You need **analytical results** (equilibria, closed-form sensitivities, proofs).
- You lack data or theory to ground agent rules — the model becomes an expensive
  way to encode assumptions.
- A **hybrid** is better: a cheap equation-based surrogate for the bulk, with the
  ABM reserved for the regimes where heterogeneity/interaction genuinely dominate.

Alternatives to weigh: ordinary/partial differential equations and system
dynamics; compartmental models (e.g. SIR) in epidemiology; DSGE and other
equilibrium models in economics; microsimulation (agents that don't interact);
discrete-event simulation (process/queue-oriented); network/game-theoretic models.
The choice is about whether *interaction and heterogeneity* are essential to the
answer.

---

## 9. A critique checklist

When reviewing an ABM (or your own), ask:
- [ ] Is ABM justified, or would a simpler model have sufficed?
- [ ] Is the purpose explicit, and is everything judged against it?
- [ ] Is it documented in ODD well enough to reimplement? (see `odd-protocol.md`)
- [ ] Verify → calibrate → validate kept distinct; validation on *independent*
      patterns/data, not the calibration target?
- [ ] How many parameters are free, and where does each value come from?
      Any sign of over-parameterization?
- [ ] Were results checked against artefacts (topology, update order, boundaries,
      seeds)? Any independent reimplementation?
- [ ] Are results reported as distributions over enough replications, with
      sensitivity analysis (ideally global, not just OFAT)?
- [ ] Are statistical claims paired with effect sizes (not significance from sheer
      run count)?
- [ ] Are the boundary conditions (ranges, scales, assumptions, initial conditions)
      stated, with no extrapolation past them?
- [ ] Are code, parameters, seeds, and data shared for reproducibility?
