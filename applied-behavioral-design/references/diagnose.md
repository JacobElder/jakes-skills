# Diagnose: map the behavior, then hypothesize bottlenecks

This is the heart of the method and the stage people most want to skip. The goal: a
**decision-action map** of the path to the target behavior, plus a set of **evidence-backed
hypotheses** about the behavioral bottlenecks that break that path. "Don't suppose, diagnose."

Diagnosis is iterative and medical, not a one-pass classification. You chart the path, form
hypotheses about the psychology at play, look for evidence in the field, and refine — the way a
diagnostician cycles between symptoms and hypotheses rather than naming a disease on sight.

## Step 1: Build a decision-action map

A decision-action map is a chronological chart of the decisions and actions a person takes on
the way to the target behavior.

- A **decision** is a choice about a future course of action (draw it as a diamond). "Decide to
  go to the gym."
- An **action** is a step taken to follow through on a decision (draw it as a rectangle). "Set
  the alarm," "pack the bag," "drive there."
- Sometimes decision and action collapse into one moment (walking past the candy bowl).

**Start simple and grow it.** Begin with the coarse path and add decisions/actions only where
they help locate where things break. Do **not** build an exhaustive process map up front — that's
busywork that buries the few steps that matter. The map is a living artifact you revise as
ethnography teaches you what really happens.

Example — target behavior "Sally goes to the gym in the morning":

```
[Decide to go]→[Decide what time]→(Set alarm)→(Wake up)→(Pack gym bag)→(Go to gym)
   diamond         diamond          action     action      action        TARGET
```

For each step you'll ask: for a *decision*, what factors influence it? For an *action*, what has
to happen for it to be taken? The drop-off points are where you focus diagnosis.

**Not a journey map.** If you come from UX, resist turning this into a service blueprint or
experience journey map. A journey map documents the whole experience over time across
touchpoints; a decision-action map is narrower and sharper — it traces the specific decisions and
actions leading to *one target behavior* so you can locate exactly where and why the path breaks.
Keep it behavior-specific and barrier-oriented, not a panorama of the user's day.

## Step 2: Look for barriers — in the context, not the person

A **barrier** is a feature of the person's *context* that prevents a decision or action. Context
means the physical environment (objects, people, processes, forms, interfaces) and the person's
in-the-moment state (fatigue, stress, mood, cognitive load). Context is explicitly **distinct
from attitudes and beliefs** — those are dispositional and come up later, in design.

This is the central reframe of the whole discipline. When a behavior isn't happening, the
amateur asks "what's wrong with these people?" and the answer is always "lazy / ignorant /
doesn't care," which licenses nagging and pamphlets. The behavioral designer asks "what about
the **situation** makes this hard, forgettable, or unattractive *right here*?" Almost always,
small contextual frictions explain outsized behavior gaps — a 100-question form suppresses
college enrollment worth thousands of dollars (the FAFSA result).

## Step 3: Generate hypotheses with the lenses — as idea generators, NOT slots

ideas42 offers a set of perspectives to interrogate each step. **These are explicitly not a
classification scheme** — you are not trying to file each barrier under the "correct" lens. The
same barrier shows up under several lenses; different people see it under different ones. The
lenses exist to *generate more hypotheses than you'd think of on your own.* Use them like a
checklist of questions, then throw the labels away.

### Decision lenses (five perspectives on a choice)

1. **Moment of choice** — Does the choice even present itself, at a good moment? Is the person
   busy, distracted, depleted? Where and through what medium (a form? a screen? in their head?)
   is it made, and does that medium add friction? *Could they fail to choose at all because the
   decision was never salient?*
2. **Angle on the choice** — How is the person constructing the choice? What do they think it's
   *about*? Does it touch an identity they embrace or reject? (Going to the gym as "health" vs.
   "being a gym person" vs. "keeping a promise to a friend" → completely different designs.)
3. **Field of choice** — What's actually in their option set (vs. what you assume)? What's top
   of mind, seen first (primacy), seen most often (frequency/mere exposure)? Is the set so large
   it causes choice overload and avoidance?
4. **Consequences of the choice** — Are options understandable and comparable? Are long-term
   consequences as salient as immediate ones (present bias)? Is risk information presented in a
   way people can actually use (MPG vs. gallons-per-100-miles)?
5. **Value of the choice** — How are consequences valued? Does the person weight an attribute
   the way the designer assumes? What's the perceived social norm? Is the option framed as a
   gain or a loss (loss aversion ≈ 2× gain)?

### Action lenses (three perspectives on follow-through)

1. **Moment of action** — Does the person remember and notice when it's time? Is the action
   window narrow? Is there a long gap between intention and action? Are they under cognitive
   load? (Forgetting and limited attention are the dominant action barriers.)
2. **Changing one's mind** — Are they tempted by a foregone or newly appearing option? When is
   the intention weakest (e.g., warm bed at 6am)? Would a commitment device hold them?
3. **Deferring the action** — Are they procrastinating? Overoptimistic about how long it takes
   (planning fallacy)? Can a tiny hassle (credit card in the other room) derail the whole thing?

For the menu of behavioral phenomena these lenses surface — habit, hassle factors, present
bias, defaults/inertia, salience, social norms, mental models, scarcity/tunneling,
prospect-theory effects, and the rest — see `barrier-library.md`. Use it to *seed and name*
hypotheses, never to stop at a label.

## Step 4: For each hypothesis, name the contextual feature and the evidence

A usable diagnosis has three parts per bottleneck:

```
Barrier (psychology)  →  Contextual feature (what you could change)  →  Evidence (confirm/kill)
```

Worked fragment (target behavior: caregiver uses the chlorine dispenser well):

| Barrier | Contextual feature giving rise to it | Evidence to look for |
|---|---|---|
| Habit | The usual well is on the way to other errands; nothing prompts thinking about chlorine | Do people walk past the dispenser well out of routine? Observe routes. |
| Hassle factors | Dispenser instructions look complex; long line anticipated | Time the task; ask about perceived effort; watch first-time use |
| Present bias | Carrying water is hard now; clean water pays off later | Do people skip the extra distance when rushed/tired? |
| Mental model | Current water looks clear and tastes fine, so "it's safe" | Ask how people judge water safety; probe clarity≈safety belief |
| Social norms | Few neighbors visibly use the dispenser | Survey perceived norm; observe usage rates |

Note how one psychology (present bias) recurs at several steps and one step breaks for several
reasons — **there is no clean one-to-one map from psychology to bottleneck.** That's expected.

## Step 5: Gather evidence and prioritize

Diagnosis is evidence-driven, not a brainstorm you fall in love with. Triangulate:

- **Quantitative / behavioral**: funnel and drop-off analysis, conversion and completion rates,
  time-to-event, event logs, administrative data — *what people actually do.* (For the
  *when/how-fast* of drop-off specifically, route to the survival-analysis skill; for *which
  segments* behave differently, route to cluster-analysis/segmentation.)
- **Qualitative**: contextual interviews, observation, ethnography, think-alouds — *why,* and
  the contextual features you'd never guess. Client/front-line interviews are gold.
- **Behavioral observation over self-report**: people are poor narrators of their own behavior.
  Watch the behavior where it happens.

Then prioritize the shortlist of bottlenecks by **severity** (how much of the gap it explains),
**frequency** (how often it bites), **confidence** (how strong the evidence is), and
**intervenability** (how feasibly you can change the contextual feature). Carry the top few into
Engineer. The rest wait.

## Transition to Engineer

You should leave Diagnose with: (1) a decision-action map to the target behavior, and (2) a
prioritized, evidence-backed list of decision/action barriers, each tied to a contextual feature
you could plausibly change. If you only have a list of biases with no map and no evidence, you
haven't diagnosed — you've supposed. Go back.
