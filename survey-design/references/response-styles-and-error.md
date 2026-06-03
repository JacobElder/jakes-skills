# Response Styles and Design-Originating Error

Response styles are systematic tendencies to use the response scale in a content-independent
way. They masquerade as substance: a group that acquiesces more will look like it holds
stronger attitudes, and a culture that uses endpoints more will look more extreme — when
nothing about the underlying construct differs. This is most dangerous in **comparisons**
(across groups, cultures, time, or modes), where a pure style difference is misread as a real
difference. Design choices can prevent much of this; the rest is corrected statistically,
which is a psychometrics handoff.

## Contents
1. The satisficing engine behind most styles
2. Acquiescence (ARS)
3. Extreme and midpoint response styles (ERS / MRS)
4. Straightlining and speeding
5. Social desirability (cross-reference)
6. Balanced design and reverse-keying caution
7. Mode effects on styles
8. What to hand to psychometrics

---

## 1. The satisficing engine
Krosnick's satisficing model explains why these styles appear and when. Faced with a question,
a respondent either **optimizes** (does all four cognitive steps well) or **satisfices** (takes
shortcuts). Likelihood of satisficing ≈ high **task difficulty** × low **ability** × low
**motivation**. *Weak* satisficing = sloppy execution of the steps (pick the first acceptable
option, lean on the midpoint). *Strong* satisficing = skipping retrieval and judgment entirely
(agree reflexively, straightline, answer from a wording cue). Every style below is a satisficing
shortcut, so the general antidotes are the same: reduce difficulty (clear wording, good labels,
sensible length) and protect motivation (relevance, brevity, good flow).

## 2. Acquiescence (ARS)
The tendency to **agree** with assertions regardless of content. It inflates endorsement of
whatever you happen to phrase positively and contaminates correlations. It is stronger among
lower-education and lower-ability respondents and in cultures valuing deference/collectivism
and high uncertainty avoidance — which makes it a serious confound in cross-national work.

**Design remedies (ex ante), best first:**
- **Use item-specific response options instead of agree/disagree.** This removes the agreement
  dimension that acquiescence acts on — the cleanest fix.
- If you must use AD items, **balance the keying** (mix items worded so that agreement means
  high *and* low standing on the construct) so acquiescence partly cancels and becomes
  detectable (Billiet & McClendon 2000). But see the caution in §6.

## 3. Extreme and midpoint response styles (ERS / MRS)
- **ERS**: preference for the endpoints ("strongly…") irrespective of content. **MRS**:
  overuse of the middle category. Both vary by personality, education, and culture.
- Design levers: **endpoint-only labeling evokes more extreme responding**, so full labeling
  helps damp ERS (Moors et al. 2014); a midpoint that's doubling as a "don't know" inflates MRS
  — give true non-opinion a separate path. Mode also shifts these (telephone shows less midpoint
  use than self-administered; §7).
- You cannot fully design ERS/MRS away; you reduce its expression and then, if comparisons
  demand it, model it (handoff).

## 4. Straightlining and speeding
In grids and long batteries, satisficers give the **same answer down a column** (straightlining)
or complete the page implausibly fast (speeding). These are the most directly *designed-in*
problems:
- Shorten the instrument and break up large grids (the biggest levers).
- Vary item polarity/wording within a battery so straightlining produces visibly inconsistent
  answers.
- Capture **response-time paradata** and flag speeders; treat straightlining and speeding as
  data-quality screens, not just nuisances.

## 5. Social desirability
A motivated (not lazy) distortion toward the approved answer on sensitive items. Full treatment
of the wording and mode remedies is in `question-wording.md` §8. Key design moves: self-
administered mode, confidentiality, forgiving wording, and indirect techniques (list experiment,
randomized response) when direct measurement is hopeless.

## 6. Balanced design and the reverse-keying caution
Balancing a scale with reverse-worded items is the textbook acquiescence remedy, but it has real
costs: reverse items often introduce **negations** (harder to comprehend; see `question-wording.md`
§5), some respondents miss the reversal and answer as if it weren't reversed, and the negative
items frequently load on a separate **method factor** that muddies dimensionality. So: balancing
is a legitimate detection tool, but it is not free, and it is usually inferior to simply using
**item-specific formats** that don't have an agreement dimension to begin with. Reverse with
care, write the reversed item as a direct positive statement of the opposite (not "I do not…"),
and verify it behaves before trusting it.

## 7. Mode effects on styles
The administration mode systematically changes which styles appear:
- **Interviewer-administered** (face-to-face, phone): more social desirability (a person is
  listening), and for spoken option lists a **recency** bias (last-heard options chosen more).
- **Self-administered** (web, mail): less social desirability, and for visual option lists a
  **primacy** bias (first-seen options chosen more); visual layout/spacing now carries meaning.
- Response-style *levels* differ by mode (e.g., midpoint use), so **mixed-mode** data are not
  automatically comparable. Hold mode constant within a comparison, or measure and adjust for it.

## 8. What to hand to psychometrics
Design reduces these errors; it does not measure or remove them. The following are
**psychometrics-skill** tasks — recommend them, then hand off rather than improvising:
- Estimating how much variance a response style accounts for (latent response-style factors in
  CFA; multidimensional/unfolding IRT models for ERS).
- **Ipsatization** or other statistical correction of acquiescence/extremity before comparison.
- Testing **measurement invariance / DIF** to tell a true group difference from a style artifact.
- Any reliability (alpha/omega) or validity coefficient used to adjudicate a design choice.
The clean division: *this skill decides how to ask so the styles are minimized and detectable;
the psychometrics skill quantifies and corrects what remains.*
