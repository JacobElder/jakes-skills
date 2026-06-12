# Behavioral & Field Experiments (Lab / UXR / Social Science)

Covers experiments where the units are people responding to designed stimuli or
interventions: usability and UXR studies, psychology paradigms, survey
experiments, field interventions. The principles are the same; the threats are
human-specific.

## Table of contents
- Within-subject designs and counterbalancing
- Factorial and mixed designs in practice
- Manipulation checks
- Demand characteristics and blinding
- Survey experiments
- Common UXR / psychology pitfalls
- Mixed methods

## Within-subject designs and counterbalancing

People are wildly heterogeneous, so within-subject designs (each participant
sees multiple conditions) pay off enormously in power — but only if order is
handled. Order, practice, fatigue, and carryover all confound condition with
sequence unless you break the link:

- **Full counterbalancing** — every possible order appears equally often.
  Feasible only with few conditions (k! orders).
- **Latin square** — each condition appears in each position once; balances
  first-order order effects with far fewer sequences.
- **Randomized order per participant** — fine at scale; counterbalancing is the
  small-sample concern.

Add washout/filler tasks between conditions when carryover is plausible. When
the manipulation is something a participant can't un-learn (a strategy, a piece
of information, a strong framing), within-subjects is off the table — use
between-subjects.

## Factorial and mixed designs in practice

A 2×2 (e.g., framing × incentive) gives main effects plus the interaction.
Behavioral work lives on interactions ("the effect held only for novices"), so
factorial designs are the norm. Mixed designs — a between-subjects manipulation
crossed with a within-subjects measure like pre/post or repeated trials — are
analyzed with mixed-effects models carrying random intercepts (and often slopes)
for participants and, where relevant, for stimuli. Crossing the random effect of
*stimulus* as well as *participant* matters whenever you generalize beyond the
specific items used; ignoring it is a known cause of inflated false positives in
language and perception research.

## Manipulation checks

Include a measure confirming the manipulation did what you intended (did the
"high-stress" condition actually raise reported stress?). A null result on the
primary outcome means something completely different depending on whether the
manipulation landed: a failed manipulation check turns "the effect doesn't
exist" into "we never tested it." Pre-specify the manipulation check and what a
failure implies.

## Demand characteristics and blinding

Participants infer the hypothesis and (consciously or not) play along — *demand
characteristics*. Experimenters unconsciously cue expected responses —
*experimenter effects*. Defenses:
- **Blind** participants to condition where possible, and the experimenter to
  condition (double-blind).
- Use cover stories or neutral framing so the hypothesis isn't transparent.
- Automate delivery and scoring to remove experimenter contact.
- Consider between-subjects when within-subjects would make the contrast obvious.

## Survey experiments

Randomize question wording, vignette attributes (conjoint/factorial vignettes),
or information provision across respondents. Power is usually generous, so the
binding constraints are construct validity (does the item measure the construct?)
and external validity (does a hypothetical vignette predict real behavior?).
Attention checks and pre-registration of the coding scheme matter more than
sample size here.

## Common UXR / psychology pitfalls

- **Unit-of-analysis errors** — multiple trials per participant analyzed as if
  independent. Aggregate to the participant or use a mixed model; never treat
  trials as the N.
- **Optional stopping** — collecting until p < 0.05. Same false-positive
  inflation as online peeking; fix N (or use a sequential method) in advance.
- **Garden of forking paths** — many defensible outcome codings, exclusions, and
  covariate sets. Pre-register the primary analysis; label the rest exploratory.
- **Underpowered interaction tests** — detecting an interaction often needs ~4×
  the N of the corresponding main effect. Most "the effect was significant in
  group A but not group B" claims are really underpowered interactions.
- **Differential attrition** — if dropout differs by condition, randomization is
  broken even though assignment was random. Compare attrition across arms.
- **Pseudo-replication of stimuli** — generalizing across items while treating
  items as fixed. Model stimuli as a random effect.

## Mixed methods

Quant experiments answer "did it move the metric and by how much"; qualitative
work answers "why, and what did people experience." They compose well: use the
experiment for the causal estimate and embedded qualitative sessions or
open-text coding to interpret mechanism and surface unanticipated effects.
Don't use qualitative impressions to override the causal estimate, or the
experiment to dismiss a real usability problem that didn't reach the chosen
metric.
