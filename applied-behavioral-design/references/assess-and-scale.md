# Assess (Test) & Scale

Two stages, joined here because both are where behavioral designers most often either fool
themselves (Assess) or watch a promising pilot die (Scale). Assess proves the design actually
caused the behavior change. Scale is the constraint you should have been designing against the
whole time.

---

## Assess: prototype to learn, then evaluate against a counterfactual

### Prototype to learn, not to perfect

Before any rigorous test, **build a rough prototype to learn** — to surface the nuances your
team hasn't articulated and to watch real people react. ideas42 "builds to learn": the point is
information, not a polished artifact.

- **Test early and often**, with cheap, tangible prototypes (a squirt bottle and a hand-made
  sign at the well; a paper form; a fake door).
- **Observe behavior; don't rely on what people say.** People are poor predictors and narrators
  of their own behavior. Amazon discovered Kindle readers switch hands (which they denied doing)
  only by *watching* them — hence page-turn buttons on both sides.
- **Unexpected results are the most informative.** A prototype that "fails" tells you whether
  (1) the insight was weak, (2) the insight was right but the concept didn't embody it, or
  (3) the concept solved a different need than you thought. In post-test interviews, listen for
  comparisons, changes in behavior/attitude/emotion, projections about others, defensiveness,
  and new stories — these reveal how people actually relate to the design.

### Then field-test against a counterfactual

A prototype tells you what people *might* do; a field test tells you what they *actually* do —
and whether your design *caused* the outcome. The core question is the **counterfactual**: what
would have happened without the intervention? Correlation isn't causation; a before/after
improvement may be driven by an external factor that would dwarf or fake your effect.

Evaluation approaches, in order of rigor:

- **Randomized controlled trial (RCT) — the default standard.** Randomly assign who gets the
  intervention. Randomization cancels out both observable and **unobservable** differences and
  defeats **selection bias** (the people who opt into a program would often have improved
  anyway — the Financial Health Check looked far better in naive comparison than in its RCT).
  Random assignment is also a fair way to ration a scarce program.
- **Before/after (pre/post) — a fallback.** Easy (measure outcome before and after), but the
  "before" is a weak counterfactual: external changes over the window can masquerade as effects.
  Use only when randomization is impossible, and explicitly reason about confounds.
- **Matching — a fallback.** Compare your group to a non-treated group matched on observed
  characteristics. Weakness: you can only match on what you thought to measure; unobservables
  still bias the estimate.

### Hand off the statistics — do not reinvent them here

This skill's job is to insist on a counterfactual and pick the right *kind* of evaluation. The
moment the work becomes test design, randomization scheme, sample size / power, ratio metrics,
sequential or Bayesian testing → **route to the experimental-design skill.** Estimating effects
from observational data (no clean randomization, diff-in-diff, RDD, synthetic control,
instrumental variables) → **route to the causal-inference skill.** Modeling *when* people drop
off rather than *whether* → **survival-analysis.** Behavioral design supplies the hypothesis and
the outcome that matters; those skills supply the rigor.

### Measure the mechanism, not just the outcome

A test that only moves the outcome tells you *that* it worked, not *why* — and "why" is what lets
you iterate, generalize, and avoid cargo-culting. Whenever feasible, measure the **mechanism**:
did the barrier you diagnosed actually shift? If you hypothesized forgetting and shipped a
reminder, did the reminder reduce *missed action windows*, or did the outcome move for some
unrelated reason? A null on the mechanism with a win on the outcome means you don't yet understand
your own intervention; a win on the mechanism with a null on the outcome means the barrier was
real but not the binding one (go find the next bottleneck). Specify mechanism measures alongside
the primary outcome before you run.

### Check for heterogeneous and equity effects

An average effect can hide opposite effects across subgroups, and behavioral interventions
routinely have **distributional consequences**: information-heavy designs tend to help the
already-advantaged, while defaults and friction reduction tend to help the inattentive and
overloaded. A nudge that lifts the average can still widen a gap. Pre-specify the subgroups you
care about and check whether the intervention helps or harms each — especially the worst-off.
(Route the subgroup/segmentation analysis to the cluster-analysis and experimental-design skills;
the point here is to *ask the question* by design, not after the fact.)

A null or negative result feeds the iteration loop: the **design** may be weak (refine it), the
diagnosed **bottleneck** may be wrong (re-diagnose), or the **problem/target behavior** may be
mis-framed (redefine). Failure localizes the error; it doesn't end the project.

---

## Scale: a design constraint from day one, not an afterthought

A solution that can't scale isn't a solution — it's a pilot with a good story. ideas42 treats
scalability as something you design *toward* from the start.

### Interrogate scalability while designing

- **What breaks at 100×?** Volume, cost, supply (is there a dependable supply of the thing your
  design requires?), staffing.
- **Can it be automated**, or does it need expert judgment / hand-tuning per case or per site?
  Bespoke judgment doesn't scale.
- **What must front-line staff do differently**, and can ordinary (not hand-picked, not
  over-supervised) staff execute it reliably? Re-diagnose *their* barriers (see `engineer.md`).
- **Cost per unit of behavior change** at scale — incentives and 1:1 assistance often look great
  in pilots and collapse on budget.

### Beyond design: the non-behavioral barriers to scale

Solid behavioral design alone won't carry an intervention to scale. Plan for:

- **Pathways to sustainability/profitability** — who pays for this indefinitely?
- **Organizational impediments** — the institution adopting it has its own inertia, incentives,
  and politics. The people running the rollout have the **same behavioral biases** as the
  beneficiaries; design for them too.
- **Regulatory / policy environment** — what rules enable or block the design at scale?

### Designing under scarcity (a recurring scale context)

When the population lives under chronic scarcity — low income, time poverty, high stress,
caregiving load — bandwidth is taxed and the usual "just add a step" instincts backfire. Apply
the **Poverty Interrupted** design principles:

- **Cut the costs** — strip every non-essential step, form field, and decision; reduce the
  bandwidth the action demands.
- **Create slack** — build in buffers (time, money, attempts) so a single slip doesn't cascade
  into failure.
- **Reframe and empower** — design to restore agency and dignity, not to surveil or shame;
  fight the stigma that scarcity already imposes.

These aren't charity-specific niceties — they're how to make *any* intervention robust for
people who can't afford the cognitive overhead a comfortable designer doesn't notice adding.
