# Question Wording

The conventional wisdom, distilled across hundreds of methods texts (Krosnick & Presser
2010), reduces to eight rules. They look obvious; the value is in catching violations,
because almost every real draft breaks several. For each defect below: name it, say which
cognitive step it harms (comprehension, retrieval, judgment, or mapping), and supply a
concrete rewrite. A diagnosis without a rewrite is not useful to the person.

## Contents
1. One thing at a time (double-barreled)
2. No leading or loaded wording
3. No presupposition; framing effects
4. Unambiguous, concrete words
5. Negations and double negatives
6. Vague quantifiers and reference periods
7. Mutually exclusive and exhaustive options
8. Sensitive questions and social desirability
9. Demographic and identity questions
7. Mutually exclusive and exhaustive options
8. Sensitive questions and social desirability

---

## 1. One thing at a time — double-barreled questions
A double-barreled question asks about two (or more) things but allows one answer. Anyone who
feels differently about the parts cannot answer truthfully; their response is uninterpretable
because you can't tell which part it refers to. The tell is a conjunction ("and"/"or") joining
two evaluable objects, or a stem that bundles an action with a justification.

- ✗ "How satisfied are you with the pay and benefits?" → split into pay, and benefits.
- ✗ "Should the city raise taxes to fund new parks?" → bundles support-for-parks with
  support-for-a-tax. Ask each separately.
- ✗ "Was the agent friendly and helpful?" → friendliness ≠ helpfulness.

Fix: one object per question. If the parts are genuinely linked for the decision, ask them
as separate items and analyze the relationship.

## 2. No leading or loaded wording
Leading wording signals the expected or socially approved answer; loaded wording attaches
charged associations to one side. Both bias the judgment step. Sources of leading: citing an
authority ("Most doctors recommend… do you agree?"), one-sided framing that names only one
alternative, and emotionally loaded terms.

- ✗ "Don't you agree that the new policy is an improvement?" → "Do you think the new policy
  is better, worse, or about the same as the old one?"
- ✗ "How wasteful is government spending?" (presumes waste) → "How would you rate the
  government's use of tax money?"
- Offer both poles explicitly. "Do you favor the proposal?" invites acquiescence; "Do you
  favor or oppose the proposal?" is balanced.

## 3. No presupposition; framing effects
A presupposition embeds an unverified assumption the respondent must accept to answer.
Classic: "How fast was the car going when it smashed into the other car?" yields higher
speed estimates than "…hit…" (Loftus) — the verb frames the event.

Framing effects are real and large even when content is logically equivalent:
- **Forbid vs allow.** Far fewer people will "forbid" X than will "not allow" X — a ~20-point
  asymmetry for the same underlying position (Rugg 1941; replicated by Schuman & Presser).
  When measuring a single direction, this means the verb choice is part of your result.
- **Gain vs loss framing** (Tversky & Kahneman): "90% survive" ≠ "10% die" in elicited
  preference, despite identical facts.

Mitigation: state both alternatives in the stem, prefer neutral verbs, and where a construct
is direction-sensitive, run a **split-ballot** experiment (randomize wording across
respondents) so the framing artifact is measured rather than silently baked in.

## 4. Unambiguous, concrete words
Aim for wording every respondent interprets the same way (comprehension step). Avoid jargon,
technical terms, slang, and abstractions. Concrete and specific beats general and abstract.
"How often do you exercise?" hides definitional variance (does gardening count? over what
period?). Prefer "In the past 7 days, on how many days did you do at least 20 minutes of
physical activity that raised your heart rate?" Define the term, the period, and the threshold.

## 5. Negations and double negatives
Negations add comprehension load and invite errors; double negatives are worse because
agreeing/disagreeing with a negative statement is genuinely confusing.
- ✗ "Teachers should not be required to not assign homework." → rewrite positively.
- ✗ Reverse-keyed item "I am not someone who dislikes crowds" → state the trait directly.
Note this interacts with acquiescence remedies: naive reverse-wording to "balance" a scale
often introduces negations and method artifacts (see `response-styles-and-error.md`). Prefer
item-specific formats over reverse-wording.

## 6. Vague quantifiers and reference periods
Response options like "often / sometimes / rarely" are interpreted differently by different
people and across topics ("often" for headaches ≠ "often" for elections). When you need
frequency, ask for an actual count over a bounded period (see Rule 4). When vague quantifiers
are unavoidable, label every point and choose terms that carve the continuum into roughly
equal steps. Always anchor reference periods ("in the past 30 days," not "recently"); long or
fuzzy recall windows degrade the retrieval step and invite telescoping (mis-dating events into
the period).

## 7. Mutually exclusive and exhaustive options
For closed questions, the option set must cover all real answers (exhaustive) without overlap
(mutually exclusive), or respondents can't map their judgment.
- ✗ Age bands "18–25, 25–35, 35–45" overlap at the boundaries. Use 18–24, 25–34, …
- ✗ "Where did you hear about us? TV / Radio / Online" omits common channels — add the
  realistic ones; an "Other (please specify)" catches the tail, but note respondents tend to
  stick to the listed options, so the visible list must be comprehensive on its own.

## 8. Sensitive questions and social desirability
On sensitive topics (income, health, drug use, voting, prejudice, anything reputational)
respondents misreport toward the socially approved answer — a motivated distortion of the
mapping step. Design remedies, strongest first:
- **Self-administered mode.** Removing the interviewer sharply reduces social-desirability
  bias; web/CASI beats phone/face-to-face for sensitive items.
- **Confidentiality assurance**, stated plainly and early.
- **Forgiving / normalizing wording** that makes every answer feel acceptable: "Many people
  don't get a chance to vote in every election. Did you happen to vote in…?" lowers
  over-reporting.
- **Load the question with the assumption of the behavior** for embarrassing-but-common acts,
  so admitting it is the path of least resistance.
- **Indirect techniques** when direct measurement is hopeless: the **item-count / list
  experiment** and **randomized response** estimate prevalence without linking any individual
  to the sensitive answer (these trade precision for protection). The **bogus-pipeline**
  raises honesty by implying the truth is detectable.
Detecting how much social-desirability bias remains, and statistically modeling it, is a
psychometrics task — hand it off.

## 9. Demographic and identity questions

Demographic questions are among the most commonly botched items in applied surveys because
researchers borrow inconsistent formats from old instruments without auditing whether those
formats are accurate for their population or current in their context. The stakes are
practical: bad demographic items produce data that can't be used for subgroup analysis, exclude
part of the population from answering honestly, or generate nonresponse on items that should be
near-universal.

### Gender

The **two-step approach** separates sex assigned at birth from current gender identity because
they measure distinct constructs and collapse differently in analysis (GenIUSS Group 2014;
Bauer et al. 2017). Use it whenever gender subgroup analyses are planned or the population
includes people with diverse gender identities.

Step 1 — Sex assigned at birth:
> "What sex were you assigned at birth, on your original birth certificate?"
> ○ Male  ○ Female  ○ Prefer not to say

Step 2 — Current gender identity (separate question):
> "What is your current gender identity? (Select all that apply)"
> ☐ Man / Boy  ☐ Woman / Girl  ☐ Non-binary  ☐ Transgender  ☐ Genderqueer or gender-fluid
> ☐ I use a different term: ___  ☐ Prefer not to say

For studies where gender identity is not the focus, a single-item approach is often acceptable:
> "What is your gender?"
> ○ Man  ○ Woman  ○ Non-binary / third gender  ○ Prefer to self-describe: ___  ○ Prefer not to say

Avoid "Male/Female" as the only options on a gender (not sex) item — these are sex categories,
and using them as the sole gender options excludes non-binary respondents entirely.

### Race and ethnicity

Follow the construct-first principle: decide whether you need (a) a single combined race/ethnicity
item, (b) separate ethnicity (Hispanic/Latino) and race items, or (c) ancestry. The U.S. Census
two-question approach (ethnicity first, then race) is standard for federal data-collection
requirements and enables separate analysis; a single combined item reduces response burden.

Key design rules:
- **Allow multi-select.** Race is not mutually exclusive; respondents may identify with more than
  one category. Forced single-select produces incorrect classifications for multiracial respondents.
- **Include write-in fields.** Provide "Another race or ethnicity (please specify): ___" to
  catch groups not listed. Closed-only lists systematically undercount minority groups.
- **Be specific.** "Asian" covers dozens of distinct ethnicities; if subgroup analysis of Asian
  respondents is planned, offer specific options (Chinese, Filipino, Indian, Korean, Vietnamese,
  etc.) with a write-in. The aggregated category loses the variation you may need.
- **Label "Hispanic or Latino/a/x" explicitly** if you use a two-question approach; don't rely
  on respondents parsing "ethnicity" vs "race" without guidance.

### Age

Use non-overlapping, contiguous bands with a consistent interval. The most common mistake is
overlapping endpoints:

- ✗ "18–25, 25–35, 35–45" — respondents who are exactly 25 or 35 fit two categories.
- ✓ "18–24, 25–34, 35–44, 45–54, 55–64, 65 or older"

If the study needs to estimate age precisely (e.g., for age-normed comparisons), collect birth
year as an open numeric field and compute age; closed bands cannot be disaggregated later.
Always include a "Prefer not to say" option for age.

### Prefer not to say / decline to state

Include a "Prefer not to say" option on all demographic items. Omitting it forces a choice
between answering and leaving the item blank (which creates missing data), and many respondents
will skip the item entirely. A "prefer not to say" response is useful data — it tells you the
item was seen and declined, not skipped accidentally.

### Accessibility and wording

- Write at a reading level appropriate to your population; avoid jargon ("cisgender" may be
  unfamiliar to some respondents — pair it with a plain-language gloss or skip the term).
- Place demographic items at the **end** of the instrument, not the beginning. Opening with
  demographics can prime identity-threat effects that alter substantive responses.
- If the instrument is used across cultures or languages, pretest every demographic item
  separately; categories that are standard in one country may be offensive, meaningless, or
  legally restricted in another.
