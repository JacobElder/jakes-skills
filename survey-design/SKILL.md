---
name: survey-design
description: >-
  Use for any question about building, reviewing, or improving surveys and
  questionnaires. Triggers on: checking whether a question is double-barreled,
  leading, or ambiguous; choosing how many scale points to use (5 vs 7 vs more);
  whether to label all points or just endpoints; where to place demographic
  questions; reducing acquiescence ("everyone just picks agree"); handling
  sensitive topics (income, race, gender) in survey form; evaluating NPS or
  customer-satisfaction question formats; picking response formats (Likert,
  rating, ranking, multiple choice, open-ended); setting survey length or
  question order. Also triggers on casual review requests ("look over my survey
  questions") and on feedback forms, rating scales, or engagement polls even when
  "survey" is not said. Does NOT cover post-collection psychometrics: reliability
  coefficients, factor analysis, IRT, and statistical correction of response
  styles belong to the psychometrics skill.
---

# Survey Design

A survey question is a tiny experiment in cognition. Every answer is the output of a
four-step process (Tourangeau): the respondent **comprehends** the question, **retrieves**
relevant information, forms a **judgment**, and **maps** that judgment onto one of the
offered response options. A design flaw at any step injects error that no amount of
analysis can fully remove. The goal of this skill is to make each step easy and unbiased.

The single most useful idea is **satisficing** (Krosnick). When optimizing is hard or
motivation is low, respondents take shortcuts — they pick the first defensible option,
agree reflexively, choose the midpoint, or straightline. Satisficing rises with **task
difficulty**, and falls with respondent **ability** and **motivation**. Most concrete design
rules below are really tactics to reduce difficulty or protect motivation.

## Scope, and the boundary with psychometrics

This skill owns the decisions made *before and during* data collection:
- **How to ask** — question wording, including demographic and identity items.
- **What format** — open vs closed, which closed format, bipolar vs unipolar structure,
  branching / two-step response sequences.
- **How the scale is built** — number of points, midpoint, labeling.
- **How the instrument is assembled** — order, length, mode, fielding, attention checks.
- **The errors that originate in those choices** — response styles (acquiescence,
  extreme, midpoint), social desirability, context/order effects, nonresponse.

The **psychometrics skill** owns what happens *after* the data exists: estimating
reliability (alpha/omega), gathering validity evidence, dimensionality and factor
analysis (EFA/CFA), IRT, measurement invariance / DIF, scoring and norming, the
**statistical correction** of response styles (ipsatization, latent response-style factors),
and formal scale-development pipelines (construct definition through CFA validation).

A few decisions sit on the seam — number of scale points, labeling, and balanced keying
are chosen at design time but justified by their effect on reliability and validity. Make
the *design recommendation* here; defer the *modeling and estimation* to psychometrics.
If a request is mostly "how reliable/valid is this scale" or "fit a measurement model,"
that is a psychometrics task — say so and hand it off rather than improvising statistics here.

**Out of scope for both skills:** sampling frames, probability vs. nonprobability sampling,
and post-collection weighting. These are survey-methodology topics; point users to
Groves et al. *Survey Methodology* or Lohr *Sampling: Design and Analysis*.

## Workflow

### A. Designing a new survey or item set
1. **Pin down the construct and the decision.** What exactly is being measured, at what
   level (one global rating? a multi-item construct?), and what decision will the data
   inform? Vague constructs produce double-barreled, ambiguous questions downstream. If
   the construct is genuinely multi-dimensional or needs a validated scale, flag that this
   crosses into psychometrics (scale construction).
2. **Choose the response format per item** using the decision guide below.
3. **Write the wording** following `references/question-wording.md`.
4. **Build each scale** — points, midpoint, labels — per `references/response-formats.md`.
5. **Assemble the instrument** — order, length, mode — per `references/questionnaire-assembly.md`.
6. **Pre-empt the predictable biases** for this topic/population (sensitive topic → social
   desirability; agree/disagree battery → acquiescence; long grid → straightlining). See
   `references/response-styles-and-error.md`.
7. **Recommend pretesting** proportionate to stakes (at minimum, a cognitive walkthrough).

### B. Reviewing or repairing an existing survey
Go item by item, then look at the whole. For each question, name the specific defect, say
which response step it harms and why, and give a concrete rewrite — not just "this is
leading" but the fixed version. Then audit instrument-level issues: order/context effects,
length/fatigue, a wall of agree/disagree items, missing or mislabeled scale points,
"select all that apply" grids, and nonresponse risk. Prioritize: lead with the flaws that
most distort the data, not the cosmetic ones. Be concrete and surgical; a survey review
that only lists abstract bias names doesn't help the person fix anything.

## Response-format decision guide

Pick the format from what you need to learn, not habit. Detail and evidence in
`references/response-formats.md`.

- **A quantity or amount** (hours, count, dollars, age) → **open numeric** entry. Closed
  ranges leak normative information and bias answers (Schwarz). Don't bin at collection time.
- **Intensity of one attitude/evaluation** → **item-specific rating scale** ("How would you
  rate our support? Very poor … Excellent"). Prefer this over **agree/disagree** statements:
  AD scales carry acquiescence, higher cognitive burden, and lower data quality (Saris et
  al. 2010; Revilla, Saris & Krosnick 2014).
- **One choice among unordered categories** → **single-select multiple choice**. Options
  must be **exhaustive and mutually exclusive**; randomize order to balance primacy/recency.
- **Several applicable categories** → a **forced-choice yes/no grid**, not "select all that
  apply." Check-all invites satisficing (people stop early); forced choice yields more
  complete, comparable data (Smyth et al. 2006).
- **Relative priorities among items** → **ranking** for ≤~5 items, otherwise **MaxDiff**
  (best–worst). Long rank tasks are cognitively brutal and degrade fast.
- **Bipolar attitude on adjective pairs** → **semantic differential** (7 points).
- **Fine-grained magnitude where precision matters** → consider a **slider / visual analog
  scale**, but expect more breakoffs and mobile trouble; default to a labeled discrete scale.

## High-leverage principles (with the evidence)

These are the rules that move data quality the most. Each links to deeper treatment.

- **Ask one thing at a time.** Double-barreled questions ("Is staff friendly and
  knowledgeable?") are unanswerable for anyone who feels differently about the two parts.
  → `question-wording.md`
- **Don't lead, load, or presuppose.** Wording that signals a "right" answer or embeds an
  assumption pulls responses. "Forbid" vs "not allow" alone shifts results ~20 points
  (Rugg). → `question-wording.md`
- **5 or 7 points for most attitude scales.** Below 4 loses information; reliability/validity
  rise with points then plateau around 5–7; past ~7 you usually can't label points well and
  gains vanish. For **agree/disagree** specifically, 5 beats 7 and 11 (Revilla, Saris &
  Krosnick 2014). Use fewer (4–5) for children or low-literacy populations. → `response-formats.md`
- **Label every point with words, not just the ends, and not numbers alone.** Fully verbal
  labeling generally raises reliability/validity (Krosnick & Berent 1993; Menold et al. 2014),
  most for lower-education respondents. Numeric-only scales force respondents to invent their
  own meanings — avoid. Make labels divide the continuum into roughly equal steps. → `response-formats.md`
- **Decide the midpoint deliberately.** Include it when true neutrality is a real position;
  omit it to push people off the fence — but then true neutrals are mismapped, and the
  midpoint is a magnet for satisficers and disguised "don't knows." A midpoint is not a
  "no opinion" option. → `response-formats.md`
- **Don't advertise "Don't know."** An explicit no-opinion option invites satisficing without
  improving quality (Krosnick & Holbrook 2002). For factual items, discourage DK and encourage
  a best guess. → `response-formats.md`
- **Break up agree/disagree batteries.** They breed acquiescence — agreeing regardless of
  content — strongest among lower-education respondents and in high-deference cultures. The
  clean fix is item-specific response options; "balanced" reverse-keying helps detect it but
  adds its own confusion. → `response-styles-and-error.md`
- **Order matters.** Earlier questions prime later ones; specific items bleed into later
  general ones (part–whole). Go general→specific, group by topic, warm up easy, put sensitive
  items late, and randomize order within item batteries. → `questionnaire-assembly.md`
- **Shorter is more honest.** Length drives fatigue → satisficing, straightlining, speeding,
  and dropoff late in the instrument. Cut every item that no decision depends on; put priority
  measures early. → `questionnaire-assembly.md`
- **Response rate is not bias.** A low response rate does not by itself mean nonresponse bias,
  and a high one doesn't guarantee its absence; bias depends on how much responders differ
  from non-responders on the specific estimate (Groves 2006; Groves & Peytcheva 2008). Chase
  representativeness, not a response-rate number. → `questionnaire-assembly.md`
- **Mode shapes answers.** Interviewer-administered modes raise social desirability and favor
  recency in spoken options; self-administered modes reduce social desirability and favor
  primacy in visual options. Keep mode constant or account for it. → `questionnaire-assembly.md`

## Reference files

Read the one that matches the task; each is self-contained.

- `references/question-wording.md` — the wording rules with before/after rewrites:
  double-barreled, leading/loaded, presupposition and framing, ambiguity, negations,
  vague quantifiers, sensitive questions / social-desirability bias, and demographic &
  identity questions (gender, race/ethnicity, age bands, prefer-not-to-say).
- `references/response-formats.md` — open vs closed; the full format taxonomy; bipolar vs
  unipolar structure and branching / two-step sequences; number of scale points (the 5/7/more
  debate and its moderators); midpoint; don't-know/no-opinion; full vs endpoint vs numeric
  labeling; and how numeric scale values themselves bias answers.
- `references/response-styles-and-error.md` — the satisficing model; acquiescence, extreme,
  and midpoint response styles; straightlining/speeding; social desirability; balanced
  design; mode effects on styles; and exactly what to hand to the psychometrics skill.
- `references/questionnaire-assembly.md` — question order and context effects; response-option
  order (primacy vs recency); anchoring through context; survey length and fatigue; unit vs
  item nonresponse and why rate ≠ bias; fielding levers (contacts, incentives, mode);
  pretesting (cognitive interviews, expert review, split-ballot experiments, SQP); and
  attention checks / data-quality screens (IMCs, bogus items, response-time paradata).

---

## Worked example: NPS and what the principles say

NPS ("How likely are you to recommend us to a friend or colleague? 0–10") is ubiquitous,
so it's a useful test case for applying the skill's rules.

**The diagnoses:**

| Issue | Principle violated |
|---|---|
| Only endpoints labeled ("Not at all likely" / "Extremely likely"); points 1–9 bare numbers | Numeric-only scales force respondents to invent meanings — full labeling raises data quality (Gummer et al. 2021). |
| Arbitrary segment cutoffs: ≤6 = detractor, 7–8 = passive, 9–10 = promoter | The split has no psychometric basis; % promoters − % detractors discards ordinal information and is less reliable than a mean. |
| Single item | Single-item reliability is unestimable; one item can't be internally consistent. Adequate only when trend matters more than precision. |
| "Recommend to a friend" conflates satisfaction, public-endorsement willingness, and fit-for-others | Potentially double-barreled; the three components can diverge. |

**What's defensible:** The 0–10 range is a legitimate exception to the 5–7 rule for a
*single global rating* when respondents are familiar with the format (see `response-formats.md §3`).
For a fast operational pulse where trend > precision, simplicity is a real feature.

**The redesign, if precision matters:**
- Replace the single item with 2–3 item-specific items on the dimensions that actually
  drive the decision (overall satisfaction, perceived value, likelihood of return), each on
  a fully-labeled 5-point scale.
- Or at minimum, label all 11 points on the 0–10 scale — at least anchor 0, 5, and 10 with
  words — and report the mean rather than the promoter/detractor arithmetic.
