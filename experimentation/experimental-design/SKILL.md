---
name: experimental-design
description: >-
  Design, critique, and troubleshoot experiments, and apply the core principles
  of experimentation — control, randomization, replication, local control,
  pre-specification, and validity. Use whenever the user wants to design or
  evaluate an experiment, A/B test, randomized trial, field experiment, or
  quasi-experiment; mentions sample size, statistical power, minimum detectable
  effect (MDE), treatment/control or holdout groups, randomization, guardrail
  metrics, p-hacking or peeking, confounds, interference/SUTVA, or threats to
  validity; or is choosing between designs (between- vs within-subjects,
  factorial, clustered, stepped-wedge). Trigger even when the user never says
  "experiment" — e.g. "will this change actually move the metric," "how many
  users do I need," "is this result real or just noise," "how do I prove X
  causes Y," or "we shipped to everyone and engagement went up, did it work."
  Prefer this over generic statistics advice for any question about making a
  defensible causal claim.
---

# Experimental Design

Most requests in this space are really one question wearing different clothes:
**how do I learn whether X causes Y, in a way I'd trust enough to act on?**
Everything below exists to answer that defensibly. The job is not to produce a
test plan that looks rigorous — it's to produce one whose result will actually
support the decision the user wants to make, and to be honest when a clean
causal answer isn't reachable.

Work through the design in the order below. Each step constrains the next, so
skipping ahead (especially jumping to sample size before the estimand is fixed)
is the most common way these go wrong.

## The principles, and why they matter

These five are the load-bearing ideas. Every concrete recommendation later
traces back to one of them, so reason from them rather than reciting a
checklist.

1. **Comparison / control.** An effect only means something against a
   counterfactual. "Engagement went up after we shipped" is not evidence the
   change worked — it's evidence engagement went up, which weather, seasonality,
   a marketing push, or a holiday could equally explain. Always ask: *compared
   to what?* The control group is the embodiment of the counterfactual.

2. **Randomization.** Random assignment is what makes the treatment and control
   groups exchangeable — equal in expectation on *everything*, measured and
   unmeasured, except the treatment. That is the entire basis for attributing
   the outcome difference to the treatment rather than to a confound. Without it
   you have a correlational study with extra steps, and you must lean on
   quasi-experimental methods (see `references/quasi-experiments.md`) and weaker
   assumptions.

3. **Replication.** One unit per condition tells you nothing about noise. You
   need enough independent units to (a) estimate variability and (b) detect the
   effect you care about above that variability. This is where power and sample
   size live. Replication is also why the *unit of analysis* must match the
   *unit of randomization* — if you randomize by classroom but analyze by
   student, you've inflated your effective N and your p-values are fiction.

4. **Local control (blocking / stratification / within-subject designs).**
   Variance you can remove by design beats variance you have to overpower with
   sample size. Blocking on a strong predictor of the outcome, stratifying
   randomization, or using each subject as their own control all strip nuisance
   variance out before it ever reaches the comparison. Cheaper than collecting
   more units, and often the difference between a feasible and infeasible study.

5. **Pre-specification.** Decide the primary metric, the test, the population,
   the stopping rule, and the success threshold *before* seeing outcome data.
   The "garden of forking paths" — choosing among many defensible analyses after
   the fact — manufactures false positives even with no intent to cheat. A
   pre-registered analysis plan is the cheapest credibility you will ever buy.

Validity is the lens over all five. Keep four kinds distinct, because fixes for
one often cost another:
- **Internal validity** — does the design license the causal claim? (Threatened
  by confounding, attrition, interference, selection.)
- **External validity** — does it generalize beyond this sample, time, setting?
  (Threatened by novelty/primacy effects, unrepresentative samples, seasonality.)
- **Construct validity** — does the metric actually measure the thing you care
  about? (A proxy that's easy to move but doesn't reflect real value is the
  classic trap.)
- **Statistical conclusion validity** — are the inferential moves sound? (Power,
  assumptions, multiple comparisons, peeking.)

## The design workflow

### 1. Pin down the causal question and the decision

Before anything technical, get the user to state the claim they want to be able
to make, and the decision it feeds. Push for specificity here — vagueness now
metastasizes into an uninterpretable result later. Resolve, explicitly:

- **Unit** — who/what is treated and measured? (user, session, device, store,
  region, classroom)
- **Treatment** — what exactly changes, and what's the comparison condition?
  "New checkout flow vs. current flow," not "improve checkout."
- **Outcome** — the one primary metric that defines success, plus how it's
  operationalized.
- **Population & timeframe** — who's eligible, over what window.
- **Decision** — what action follows each possible result. If no result would
  change any action, the experiment isn't worth running; say so.

State it back as a single sentence: *"Among [population], does [treatment vs.
control] change [primary outcome] over [window]?"* If you can't write that
sentence cleanly, the design isn't ready.

**Then ask whether it should be run at all.** Experiments act on real people,
and a clean design is not the same as a defensible one. Surface, proportionate
to the stakes:
- **Harm to an arm.** Does the control (or treatment) withhold a known benefit
  or expose people to a known risk? If a treatment is already known to help,
  randomizing people away from it raises an equipoise problem — only experiment
  when there's genuine uncertainty about which arm is better.
- **Consent and expectation.** Would users be upset to learn they were
  experimented on? Manipulating something emotionally or financially
  consequential without awareness is the line the Facebook emotional-contagion
  study crossed — a reputational and ethical hazard, not just an IRB formality.
- **Vulnerable populations and irreversible effects.** Higher bar for minors,
  health, finances, or anything hard to undo.

Calibrate, don't moralize. A button-color or copy test needs a sentence of
acknowledgement at most; a study touching well-being, money, safety, or
deception deserves real treatment and possibly a recommendation to add consent,
debriefing, an ethics review, or a less invasive design. Name the concern and
the lightest mitigation that addresses it, rather than lecturing.

### 2. Choose the estimand

Name the quantity being estimated, because it determines the analysis. Most
common is the **average treatment effect (ATE)**. In any setting with
noncompliance (not everyone assigned to treatment actually receives it),
distinguish **intent-to-treat (ITT)** — effect of *assignment*, which preserves
randomization and is usually what you should report — from the per-protocol or
treatment-on-the-treated effect, which is tempting but reintroduces selection
bias. Flag this early; it changes who you analyze.

### 3. Select the design

Match the design to the constraints, not to habit. Decision points:

- **Randomized vs. quasi-experimental.** Randomize if you possibly can. If you
  can't (ethics, logistics, the change already shipped, a policy applies to
  everyone), move to `references/quasi-experiments.md` — diff-in-diff,
  regression discontinuity, interrupted time series, synthetic control — and be
  explicit about the assumptions each one buys on credit.
- **Between- vs. within-subjects.** Within-subjects (each unit sees multiple
  conditions) is far more powerful because it removes between-unit variance, but
  it's vulnerable to order/carryover effects and isn't possible when the
  treatment is "sticky" (you can't un-see a redesign). Counterbalance order when
  you use it. See `references/behavioral-experiments.md`.
- **Unit of randomization.** Randomize at the level where interference is
  contained. If treated users affect control users (shared feeds, marketplaces,
  social features, two-sided platforms), individual randomization violates SUTVA
  and biases the estimate — escalate to **cluster randomization** (by region,
  market, time) and accept the loss of power. This is *the* dominant failure
  mode in online experiments; check for it every time. See
  `references/online-experiments.md`.
- **Factorial designs** when several factors are in play — they test multiple
  factors at once and reveal interactions, usually more efficiently than a
  series of one-factor tests.

For the menu of designs with their tradeoffs, read
`references/design-selection.md`.

### 4. Specify metrics: one primary, plus guardrails

- **Primary metric** — exactly one. It must have construct validity (moving it
  means the thing you care about improved) and enough sensitivity to move within
  the study window. Multiple primaries are a multiple-comparisons problem in
  disguise.
- **Secondary metrics** — for understanding mechanism, explicitly not for
  declaring victory.
- **Guardrail metrics** — things that must *not* get worse (latency, crashes,
  unsubscribes, revenue, complaints). A "win" that wrecks a guardrail isn't a
  win. Pre-specify these; they're how you catch a metric being gamed.

Beware proxy metrics that are easy to move but decoupled from value, and beware
surrogate outcomes standing in for long-term effects you didn't measure.

Watch for **ratio metrics** where the analysis unit differs from the measurement
unit — revenue-per-session or clicks-per-pageview when you randomize by user.
Their variance can't be computed as a simple mean or proportion; it needs the
delta method (or bootstrap), and naive variance understates it and inflates
false positives. The bundled script assumes simple means/proportions, so flag
ratio metrics explicitly and see `references/power-and-sample-size.md`.

### 5. Power and sample size

Only now, with estimand and design fixed, compute how many units you need. Four
quantities are interlocked — fix three, solve for the fourth:

- **MDE (minimum detectable effect)** — the smallest effect worth detecting.
  This is a *business/scientific* judgment, not a statistical one: what's the
  smallest effect that would change the decision? Drive the conversation here;
  users routinely under-think it.
- **Significance level (α)** — usually 0.05; lower it for multiple comparisons.
- **Power (1−β)** — usually 0.80; go higher (0.90+) when a miss is costly.
- **Baseline rate / outcome variance** — from historical data where possible.
  For ratio metrics, estimate variance with the delta method, not the raw
  formula (see metrics note above).

Use the bundled calculator rather than deriving by hand:

```bash
python scripts/power_analysis.py --help
```

It handles proportions (conversion-rate style), means (continuous outcomes),
solving for any of {sample size, MDE, power}, cluster-randomization variance
inflation (design effect), and multiple-comparison correction. It assumes the
metric is a simple proportion or mean — for ratio metrics, compute the variance
separately (delta method) and feed that in as the outcome variance. Read
`references/power-and-sample-size.md` for the conceptual grounding, variance
reduction (CUPED), and how to translate N into a realistic run duration given
traffic and exposure.

If the required N is infeasible, that's a finding, not a failure — report it and
discuss variance reduction, a larger MDE, a within-subjects design, or longer
runtime before quietly running an underpowered test that can only produce a
noisy, uninterpretable result.

**Run the script for every sample-size number you state** — including
hypotheticals, ranges, and offhand "you'd need about N" asides, not just the
headline answer. Never report an N from mental math: required sample scales with
1/MDE² (and with the baseline rate for proportions), so intuition is unreliable
and being off by an integer multiple is common. If a number is worth putting in
front of the user, it's worth one more script call to get it right.

### 6. Plan the analysis before collecting data

Write this down before launch; it's the pre-specification principle made
concrete:

- The exact test/model and the population it runs on (ITT by default).
- **Stopping rule.** Fix the sample size or duration in advance. Repeatedly
  checking and stopping when significant ("peeking") inflates the false-positive
  rate dramatically — a nominal 5% test checked daily can exceed 30% real false
  positive rate. If interim looks are needed, use a sequential method built for
  it (group-sequential boundaries, always-valid p-values); don't eyeball a fixed
  test. See `references/online-experiments.md`.
- **Multiple comparisons.** Each extra metric, segment, or variant is another
  shot at a false positive. Pre-specify which comparisons are confirmatory vs.
  exploratory and correct accordingly.
- How attrition and missing data will be handled — and whether attrition itself
  differs by arm (differential attrition silently breaks randomization).
- **Frequentist or Bayesian?** Decide the framework up front, because it changes
  what "done" means. A frequentist plan fixes N and reports a p-value and
  confidence interval against a null. A Bayesian plan reports a posterior — e.g.
  the probability the treatment beats control, or the expected loss from
  shipping — and ships on a decision rule over that posterior; it sidesteps the
  peeking problem differently (the posterior is always valid to read, though
  priors and the decision threshold do real work and must be set in advance, not
  after seeing data). Many modern experimentation platforms default to Bayesian.
  Neither is "more rigorous"; pick deliberately and don't mix their vocabularies.
  See `references/interpreting-results.md`.

### 7. Pre-mortem the threats to validity

Before signing off, walk the four validity types and name the specific threats
this design faces and what each costs:

- **Confounding** — anything correlated with both assignment and outcome.
  Randomization handles the unmeasured ones; quasi-experiments do not.
- **Interference / SUTVA violations** — one unit's treatment affecting another's
  outcome.
- **Attrition** — especially if differential across arms.
- **Novelty & primacy effects** — users react to *change* (or to *newness*), not
  the steady-state treatment; short tests overstate or understate the durable
  effect. Plan for a longer or holdback measurement when this is a risk.
- **Selection** — into the study or into compliance.
- **Seasonality / time confounds** — run long enough to span the relevant cycle;
  don't compare a treatment week to a baseline week with a holiday in it.

## Reading results (when the task is interpretation, not design)

Many requests arrive after the data is in — "is this result real?", "it's
significant, do we ship?". The same principles apply in reverse:

- **Report the interval, not just the verdict.** A confidence (or credible)
  interval shows the range of effects compatible with the data; "p < 0.05" alone
  hides whether the plausible effect is trivial or huge.
- **Statistical ≠ practical significance.** With enough N, a meaningless effect
  clears p < 0.05. Compare the estimate to the MDE that mattered, not to zero.
- **A null is not proof of no effect.** "Not significant" usually means
  underpowered or inconclusive, not "no difference." Say which.
- **Significant wins are biased upward** in underpowered tests (the winner's
  curse / Type-M error) — discount a surprising large effect from a small study.
- Re-check the **SRM and guardrails** before trusting any headline number.

For depth — interval interpretation, practical-significance framing, and how
Bayesian posteriors change the ship decision — see
`references/interpreting-results.md`.

## Output format

Default to delivering a **structured design brief** with these sections, in
prose-forward writing (not a wall of bullets):

```
# Experiment Design: [one-line causal question]
## Decision & hypothesis        — what we'll learn, what we'll do with it
## Design                       — type, unit of randomization, assignment, arms
## Metrics                      — primary (one), secondary, guardrails
## Sample size & duration       — MDE, α, power, baseline → required N → runtime
## Analysis plan                — test, population (ITT), stopping rule, corrections
## Threats & mitigations        — the specific validity risks for THIS design
## Open decisions               — what the user still needs to decide
```

Scale to the request. A quick "how many users do I need" needs the sample-size
math and the MDE conversation, not the full brief. A critique of an existing
design walks the same checklist but in diagnostic mode — find the load-bearing
flaw rather than listing every imperfection. When critiquing, lead with the one
or two issues that would actually change the conclusion, then the rest.

### A worked example (compressed)

*Request:* "Test whether a new recommendation widget lifts add-to-cart rate."

1. **Question/decision:** Among users who reach the product page, does the new
   widget vs. the current page change add-to-cart rate over 2–4 weeks? We ship
   if the lift clears the eng cost. *Ethics:* low-stakes UI change — one line,
   no special handling.
2. **Estimand:** ATE; full compliance, so ITT = ATE here.
3. **Design:** Between-subjects, randomize by **user** (sticky-ish UI, and we
   want per-user consistency). No marketplace/social interference → individual
   randomization is safe. 50/50.
4. **Metrics:** Primary = add-to-cart rate (one). Guardrails = page latency,
   revenue per session, return rate. Add-to-cart is a proxy for purchase, so
   purchase is a secondary to watch, not the primary.
5. **Power:** Baseline 8%, decision-relevant MDE = +0.8pp absolute. `python
   scripts/power_analysis.py --solve n --type proportion --baseline 0.08 --mde
   0.008` → N/arm, then divide by daily triggered traffic for runtime; round up
   to whole weeks.
6. **Analysis plan:** Two-proportion test on the triggered population, ITT,
   fixed N (no peeking), frequentist with a 95% CI; latency checked one-sided.
7. **Pre-mortem:** Novelty effect (run ≥2 weeks, watch the daily curve);
   weekly seasonality (whole weeks); SRM check before reading anything.

Notice the shape: each step narrowed the next, and power came only after the
design was fixed.

## When the honest answer is "you can't cleanly test this"

Sometimes the constraints rule out a defensible causal claim — the change is
already live to everyone, there's no possible control, interference is
unavoidable, or the required sample is years away. Say so plainly, explain which
principle is violated, and offer the best *available* alternative (a
quasi-experimental estimate with stated assumptions, a holdback, a staggered
rollout, a smaller scoped question that *is* testable) rather than dressing up a
weak design as a strong one. Intellectual honesty about what an experiment can
and can't support is the most valuable thing this skill provides.

## Reference files

Read these as the task demands — don't load all of them by default.

- `references/design-selection.md` — the full menu of designs (between/within,
  factorial, crossover, cluster, stepped-wedge) with tradeoffs and a chooser.
- `references/online-experiments.md` — A/B testing at scale: SRM checks,
  CUPED variance reduction, peeking/sequential testing, interference in
  marketplaces and social products, guardrails, ramp-up.
- `references/behavioral-experiments.md` — lab/field behavioral studies:
  within-subject and factorial designs, counterbalancing, manipulation checks,
  mixed designs, common psychology/UXR pitfalls.
- `references/quasi-experiments.md` — when randomization is impossible:
  diff-in-diff, regression discontinuity, interrupted time series, synthetic
  control, matching/IPW, and the assumptions each requires.
- `references/power-and-sample-size.md` — conceptual grounding for power, MDE
  selection, variance, ratio-metric (delta-method) variance, cluster design
  effects, and turning N into runtime.
- `references/interpreting-results.md` — reading results after the fact:
  confidence and credible intervals, statistical vs. practical significance,
  what a null does and doesn't license, and the Bayesian vs. frequentist
  decision framework.
