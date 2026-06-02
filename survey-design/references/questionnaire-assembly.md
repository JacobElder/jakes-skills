# Questionnaire Assembly: Order, Length, Nonresponse, Fielding, Pretesting

Item-level quality is necessary but not sufficient. The order items appear in, the length of
the whole, who answers at all, and how the instrument is fielded each inject their own error.

## Contents
1. Question order and context effects
2. Response-option order (primacy vs recency)
3. Anchoring through context
4. Survey length and fatigue
5. Nonresponse: unit vs item, and why rate ≠ bias
6. Fielding levers
7. Pretesting
8. Attention checks and data-quality screens

---

## 1. Question order and context effects
Earlier questions change how later ones are answered, because they prime concepts, set a
standard of comparison, or invoke a norm of consistency. The main patterns:
- **Assimilation**: a primed consideration gets pulled into a later judgment, moving it toward
  the prime.
- **Contrast**: a respondent excludes what they already covered from a later judgment, moving
  it away.
- **Part–whole**: a specific question asked *before* a general one alters the general answer.
  The classic Schuman case: ask about marital satisfaction, then life satisfaction, and the
  general item shifts (people subtract or anchor on what they just reported). Reverse the order
  and the effect changes.

Assembly rules:
- Open with **easy, pleasant, on-topic** questions that build rapport; the first items should
  match the survey topic the respondent was promised.
- Move **general → specific** within a topic, and **group items by topic** so respondents aren't
  whiplashed between frames.
- Place **sensitive** items late, after trust is established.
- Use **filter questions** so people aren't asked items that don't apply.
- **Randomize order within item batteries** so any order effect is distributed across items
  rather than always penalizing the same one; randomize block order where blocks are independent.

## 2. Response-option order (primacy vs recency)
Order within a single item's option list also biases choice, and the direction depends on mode:
- **Visual / self-administered**: **primacy** — earlier options are more likely chosen
  (respondents satisfice down from the top and stop at the first acceptable one).
- **Aural / interviewer-administered**: **recency** — later options are favored (the last-heard
  options are freshest in memory).
- For **nominal** lists, **randomize or rotate** option order across respondents to balance the
  bias out. For **ordinal scales**, keep the natural progression (don't scramble a 1→7 scale)
  but you can rotate its *direction* across respondents to balance left/right anchoring.

## 3. Anchoring through context
Beyond wording-level anchoring (`question-wording.md`), the instrument context anchors answers:
a number mentioned earlier, a reference value in an instruction, or the range of a preceding
scale can all serve as an anchor that later numeric estimates drift toward. Slider start
positions anchor (`response-formats.md` §2). Avoid seeding numbers you don't want respondents to
anchor on, and keep scale ranges consistent across parallel items so each isn't reanchoring.

## 4. Survey length and fatigue
Length is one of the few quality levers fully under your control. As an instrument runs long,
motivation decays and satisficing rises: more **midpoint and "agree" responses, straightlining,
speeding, item nonresponse**, and outright **breakoff** — and these concentrate in the **later**
portion of the questionnaire. Consequences:
- Cut every item no decision depends on. "Nice to know" is the enemy of "honestly answered."
- **Front-load priority measures** so your most important data are collected while attention is
  highest.
- Treat completion-time and straightlining metrics as fatigue diagnostics, and consider whether
  late-survey items show degraded quality before trusting them.

## 5. Nonresponse: unit vs item, and why rate ≠ bias
- **Unit nonresponse**: the sampled person doesn't participate at all. **Item nonresponse**:
  they skip specific questions (often sensitive or burdensome ones).
- **A response rate is not a bias measure.** Nonresponse bias for a mean ≈ (nonresponse rate) ×
  (difference between respondents and non-respondents on that variable). A low response rate
  produces little bias if non-responders resemble responders on the estimate; a high response
  rate can still hide bias if the missing few differ sharply. Meta-analyses found **no reliable
  relationship between response rate and nonresponse bias** (Groves 2006; Groves & Peytcheva
  2008), and bias is **item-specific** — large on items tied to the survey's salient topic,
  negligible elsewhere.
- Implication: don't fetishize a response-rate threshold. Assess representativeness on the
  estimates that matter — **benchmark** survey distributions against known population totals or
  administrative records, run **level-of-effort / wave analysis** (does the estimate move as
  reluctant respondents come in?), and compare early vs late responders as a nonresponse proxy.

## 6. Fielding levers
To raise participation *and* representativeness (not just the rate):
- **Multiple, well-spaced contacts** and reminders — the most reliable lever.
- **Personalization** of invitations and a credible, relevant sponsor.
- **Incentives**, ideally **prepaid/unconditional** (more effective than promised/contingent).
  Caution: incentives can interact with topic interest (leverage-salience), pulling in people
  with weaker intrinsic interest and changing topic-relevant estimates — so incentives are not
  bias-neutral.
- **Mixed-mode** offering to reach groups a single mode misses — but recall (§7,
  `response-styles-and-error.md`) that mode changes answers, so mixing modes trades coverage
  against comparability.
- **Shorter instruments** raise completion and reduce mid-survey breakoff (§4).

## 7. Pretesting
Never field an instrument you haven't tested; scale the effort to the stakes.
- **Cognitive interviews** (think-aloud + targeted probes): the highest-value method. Watch a
  handful of target respondents answer aloud to expose comprehension failures, impossible
  retrieval, and mapping problems you can't see on paper. A few interviews catch most fatal
  flaws.
- **Expert review** against the wording/format checklists in the other reference files.
- **Behavior coding** of pilot interviews (where interviewers are used) to flag items that
  routinely require clarification or get qualified answers.
- **Split-ballot experiments**: randomize alternative wordings/formats/orders across pilot
  respondents to *measure* an artifact (e.g., a framing or order effect) rather than guess.
- **Field pretest** at small scale to surface routing, length, and breakoff problems live.
- **SQP (Survey Quality Prediction; Saris & Gallhofer)**: a database-backed tool that predicts
  the reliability/validity of a question from its formal features — useful at design time to
  compare candidate formulations before collecting data. (Interpreting the predicted
  reliability/validity coefficients shades into psychometrics.)

## 8. Attention checks and data-quality screens

Inattentive responding — answering without reading — is a real source of noise in online
surveys, but the remedies have real costs. Design with that trade-off explicit.

### Types of attention checks

**Instructional manipulation checks (IMCs)** embed a reading-comprehension directive inside
what looks like a regular survey item. The original form (Oppenheimer et al. 2009):
> "This is an attention check. Please select 'Strongly Disagree' for this item regardless of
> your actual view."
Respondents who fail are likely not reading carefully. IMCs are the most widely validated
check type and have a large discrimination effect (Oppenheimer et al. 2009).

**Bogus items** are questions about non-existent objects ("How familiar are you with the
Vondaloo Effect in behavioral economics?"). Endorsement indicates careless positive
responding. Limitation: false positives from respondents guessing or misremembering rather
than fabricating.

**Trap / consistency items** ask the same question twice with different wording, or embed
a within-item trap ("For this item please select the third option"). Inconsistent or
trap-triggered responses flag poor attention.

**Response-time paradata**: completion times shorter than a plausible minimum (often
computed as words × reading speed) flag speeders. Most survey platforms collect timestamps
per page or per item. Response time is a continuous quality indicator rather than a binary
pass/fail, and it interacts with literacy and motivation — fast completion is not always
inattentive.

### The controversy

Attention checks come with documented costs that complicate their routine use:

- **Reactance among conscientious respondents.** Some attentive respondents are confused or
  annoyed by obvious trick items and may quit or answer subsequent items less carefully
  (Berinsky et al. 2014). The population most harmed by checks is the population you want
  to keep.
- **Altered survey experience.** Including checks changes what the instrument measures: it
  signals distrust, raises self-awareness, and can shift subsequent responses via demand
  characteristics.
- **Population-specificity.** Checks validated on MTurk samples do not transfer directly to
  general population or clinical samples, where literacy, cognitive ability, and English
  proficiency vary.

The design implication: use attention checks when (a) you have strong reason to expect
substantial inattention (long surveys, low-engagement topics, low-pay panels), and
(b) you are prepared to share your exclusion criteria and the check wordings transparently.
Treat them as a data-quality diagnostic, not a magic filter.

### Placement and count

- Use **one or two checks** at most; a battery of checks is itself a burden and changes
  task-difficulty in ways that cascade across the instrument.
- Place the first check **after the initial warm-up questions** (not as the first item, which
  is punishing) and before the substantive core.
- Do not use checks as **tricks the goal is to pass** — frame them as quality controls in
  your pre-registration and methods section.

### What belongs here vs. in psychometrics

**Design and flagging (this skill):** deciding whether to use checks, which type, where to
place them, and how to capture response-time paradata. The output is a flag variable
attached to each response record.

**Exclusion-rule statistics and downstream impact (psychometrics skill):** deciding what
exclusion threshold is appropriate (e.g., "exclude anyone who fails ≥1 check"), testing
whether exclusion changes reliability estimates or factor structure, and reporting the
effect size of exclusion on substantive results. If exclusion decisions should be justified
by their impact on measurement quality, hand that analysis to the psychometrics skill.
