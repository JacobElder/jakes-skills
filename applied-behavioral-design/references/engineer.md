# Engineer (Design): turn bottlenecks into interventions

Input to this stage: a prioritized list of barriers, each tied to a contextual feature and
backed by evidence. Output: a small set of intervention concepts worth prototyping. The
discipline here is to **generate broadly before selecting**, address the barrier you actually
diagnosed, and re-diagnose your own design before you fall in love with it.

## The core heuristic: lower / around / over

Treat each barrier as a physical obstacle on the path to the target behavior. There are exactly
three ways past an obstacle, and **every barrier should be attacked from all three** before you
pick:

1. **Lower or eliminate the barrier** — change the *contextual feature* that creates it.
   (Shorten the form, pre-fill the data, add signage, fix the confusing label.)
2. **Go around the barrier** — change the *decision-action map* so the person never has to make
   that decision or take that action. (Flip the default so no choice is needed; automate the
   step; remove it; move it to a moment when it's easy.)
3. **Go over the barrier** — raise the person's *motivation* to push through it. (Reminders of
   their goal, social proof, commitment devices, incentives.)

Phrase each as a **"How might we…"** to open the brainstorm:

> Barrier: caregiver forgets to bring chlorine when fetching water.
> - *Lower:* How might we make the chlorine impossible to miss at the well?
> - *Around:* How might we make the water arrive already treated, so she needn't remember at all?
> - *Over:* How might we make remembering matter more to her in the moment?

**The most common failure is reaching straight for "go over."** When a behavior isn't happening,
people instinctively try to motivate harder — exhort, incentivize, educate. But "go around"
(delete the decision, flip the default, automate it) is usually cheaper, more durable, and more
respectful of the person's bandwidth. *Always put the "around" option on the table, and bias
toward it.* "Over" is the option of last resort, not first.

## Brainstorm like it matters

- **Brainstorm even if you already have a workable idea.** We default to the first plausible
  solution and tweak it incrementally; that's almost never the best. Deliberately generate
  alternatives before committing.
- **Individuals first, then combine.** Structured brainstorming (people ideate alone, then
  build on each other's ideas) beats free-form group brainstorming, which loses productivity to
  groupthink and turn-taking.
- **Defer judgment, encourage wild ideas, build on others, one conversation at a time, stay on
  topic.** Wild ideas seed plausible ones you'd never reach directly.
- **Narrowing the frame boosts creativity.** Adding a constraint ("…without sending a
  notification," "…without the user opening the app") generates *more* varied ideas, not fewer.
- Ignore others' solutions during initial ideation; bring them in afterward so they don't anchor
  you. Then explicitly seed the brainstorm with the intervention families below.

## Common intervention families (seed material, not a menu to grab from blindly)

Match these to the diagnosed barrier — never apply one because it's fashionable:

- **Simplify / reduce friction** — cut or consolidate steps, pre-fill, provide hands-on
  assistance. (FAFSA assistance tripled submission and lifted enrollment 29%; tetanus-shot
  follow-through rose 3%→28% just by adding where/when info.)
- **Defaults** — make the welfare-improving option automatic. (401(k) auto-enrollment 37%→85%.)
  Use only where it's ethical, legal, and genuinely in the person's interest.
- **Reminders & prompts** — at the moment of action; often beat financial incentives (Uganda
  loan-repayment texts; appointment reminders; college "summer melt" texts).
- **Choice architecture** — present and order options so the better one is salient and
  comparable (MPG→gallons-per-100-miles; group large choice sets by risk; personalized
  shortlists for Medicare plans).
- **Commitment devices** — let people bind their future selves (StickK contracts;
  Save-More-Tomorrow pre-commitment of future raises; behavioral contracts).
- **Social norms / proof** — truthfully signal that similar others do the desired thing (energy
  and water usage comparisons cut consumption). Watch for normalizing the bad behavior.
- **Framing** — gain vs. loss; loss-framed incentives (teacher bonuses) outperformed standard
  ones. Make immediate what was distant.
- **Incentives — last, and carefully.** See below.

## The trouble with incentives

Incentives are seductive and frequently the wrong first move. Before proposing one, internalize
the failure modes:

- **Crowding out intrinsic motivation** — paying for a behavior can signal it's unpleasant or
  that the person isn't trusted, reducing the internal drive that was already working.
- **"A fine is a price"** — pricing a behavior can *license* it: the daycare that fined late
  pickups got *more* late pickups, because guilt was replaced by a fee people happily paid.
- **They must be big enough and well-targeted, or they fail** — under-powered incentives
  (HIV-adherence payments) simply don't move behavior; money is often the expensive way to buy a
  result a reminder would have bought.
- **Scale economics** — an incentive that works in a pilot may be unaffordable at 100×.

If you do use incentives: enhance them behaviorally (loss-framed, salient, probabilistic — a
1%-chance-of-$100 lottery beat certain small payments for medication adherence), tie them to
clearly defined behaviors, and **state in advance how you'll detect backfire** (crowding-out,
gaming, licensing).

## Select concepts deliberately

Don't carry every idea forward. For each promising concept:

- Sketch a **mini theory of change**: inputs → outputs → defeat of the barrier → target behavior.
- **Mentally simulate** executing it end to end — what did you miss?
- **List what could go wrong**: stakeholder resistance, system inertia, new failure points.
- Rough **cost/benefit**, including at scale.
- Eliminate the weak; keep a few of the most promising to prototype.

## Design & Diagnose Redux — re-diagnose your own design

Before you prototype, **run the design back through Diagnosis.** Every intervention adds steps,
shifts effort, or creates new choices — and often the new barrier lands on someone you weren't
designing for:

- Does the new flow add a hassle, a decision, a delay?
- What must **front-line staff / caseworkers / implementers** now do differently, and what are
  *their* barriers? (They have the same biases as everyone else.)
- Share concepts with the implementing organization as a reality check on constraints.

The more complex the design, the more essential this step. Skipping it is how a "fix" quietly
introduces the next bottleneck.

## Watch for unintended consequences

Effects depend on context and can reverse:

- **Licensing effect** — efficient irrigation subsidies *raised* water use, because farmers felt
  they'd "earned" the right to use more.
- **System effects** — subsidizing coconut farming to reduce overfishing backfired when higher
  incomes funded more leisure fishing and better fishing gear.

Ask, for each design: who else changes behavior in response, and could that swamp the intended
effect? Carry these as risks into Assess.

## Hand-offs

If selecting interventions requires knowing **what people actually value/trade off**, route to
the **preference-choice-modeling** skill (MaxDiff/conjoint) rather than guessing. If you need to
**target the intervention to specific behavioral segments**, route to
segmentation/**cluster-analysis**. The behavioral design happens here; the measurement happens
there.
