# Review: Exit Survey for Web-Based UX Study

This is a well-constructed short instrument. The item wording is clean, the format choices are
mostly correct, and the administration decisions (self-administered, post-task, anonymous) are
all evidence-based. That said, there are a few targeted improvements worth making, and one
instrument-level decision that deserves a closer look.

---

## Item-by-item review

### Item 1 — Overall experience rating

> "Overall, how would you rate your experience completing the task today?"
> Very poor / Poor / Fair / Good / Excellent

**Verdict: Good. Minor labeling note.**

This is an item-specific rating scale — the correct format for evaluating intensity of a single
experience. Using item-specific options here rather than an agree/disagree stem is the right call;
it avoids acquiescence and reduces cognitive load.

The 5-point scale with fully verbal labels is appropriate for a unipolar evaluation construct
(experience quality runs from poor to excellent, not from poor through neutral to excellent in a
bipolar sense). Five fully-labeled points will serve you well here.

One small note: "Fair" sits between "Poor" and "Good" and functions as the midpoint. This is
standard in experience-rating scales, but verify that "Fair" is understood as neutral — some
respondents read it as mildly positive ("fair enough"). If true neutrality is important, "Neither
poor nor good" is less ambiguous. For most UX contexts, "Fair" is fine.

**No rewrite needed.**

---

### Item 2 — Task difficulty

> "How difficult was the task?"
> Very easy / Easy / Neither easy nor difficult / Difficult / Very difficult

**Verdict: Good as stated. One structural clarification.**

The wording is unambiguous and concrete. The 5-point difficulty scale is fully labeled. The
midpoint ("Neither easy nor difficult") is explicit and appropriate — true neutrality on
difficulty is psychologically real, and including it correctly avoids forcing respondents who
genuinely had a moderate experience to mismap.

Note that this scale is arranged from low to high difficulty on the right side (easy→difficult),
with "Very easy" at the left. This is fine and consistent with the Q1 valence direction (better
experience → higher difficulty would put their answers in opposite directions, which is fine for
a 4-item exit survey where no grid straightlining risk exists). If you later add a grid of
several items, ensure scale direction is consistent within blocks.

**No rewrite needed.**

---

### Item 3 — Open-ended confusing parts

> "Which parts of the interface did you find most confusing, if any? (Leave blank if none)"

**Verdict: Good, with a minor framing note.**

This is a well-placed open-ended item. Open text is correct for "which parts" — a closed list
would be premature before you know which elements are actually confusing, and a closed list could
prime respondents to identify only those elements rather than surfacing genuine problem areas.

The escape clause "(Leave blank if none)" is appropriate — it normalizes having nothing to report
without actively leading respondents toward the null answer.

One framing caution: "most confusing" sets a relative comparison that may suppress mentions of
moderately confusing elements. If you need all confusing elements, not just the single worst one,
consider: "Were any parts of the interface confusing? If so, please describe them." That said, for
an exit survey where brevity matters, "most confusing, if any" is a reasonable trade-off. Keep it
as-is unless exhaustive recall matters more than task efficiency.

**No rewrite needed; optional minor revision if exhaustive listing is the goal.**

---

### Item 4 — Likelihood of future use

> "How likely are you to use this type of tool again in your research?"
> Very unlikely / Unlikely / Neither likely nor unlikely / Likely / Very likely

**Verdict: Good format and labels. One scope question.**

Item-specific likelihood rating, 5 points, fully labeled, appropriate midpoint. This is all correct.

One wording flag: "this type of tool" is slightly ambiguous — it could mean this specific tool,
web-based UX research tools in general, or the category of task you were studying. If respondents
interpret it differently, their answers measure different things. If you mean this specific tool or
prototype, say so: "How likely are you to use this tool again in your research?" If you mean the
class of tools, "web-based [task type] tools" is more precise.

**Suggested rewrite (if specificity matters):**
> "How likely are you to use this tool again in your research?" *(if the prototype is the referent)*

Or:

> "How likely are you to use a web-based [task name] tool in your future research?" *(if the category is the referent)*

---

## Instrument-level review

### What works well

- **Post-task administration** is correct. Placing the survey after the task eliminates demand
  characteristics that would arise from respondents knowing they'll be evaluated, and avoids
  priming task behavior with survey framing.
- **Anonymous and self-administered** is the right mode for this type of study. It reduces social
  desirability on the experience and difficulty ratings, both of which could be inflated upward if
  respondents felt they were being evaluated or wanted to seem capable.
- **Topic order** is sensible: overall experience → difficulty → specific interface problem →
  future intent. This is a general-to-specific flow within a coherent topic, which matches the
  recommended assembly pattern (open with easy, topic-grouped, general before specific).
- **Length** is excellent. Four items is short enough to have no fatigue risk. All four items are
  clearly decision-relevant (experience, difficulty, interface problems, behavioral intent). Nothing
  appears to be "nice to know."

### The randomization decision — needs reconsideration

You noted: "I'll randomize nothing since these items are already in a logical topic order."

This is partially correct reasoning, but it deserves a sharper distinction:

**Within-battery option order (ordinal scales):** You are right not to scramble these. Reversing
the direction of a labeled ordinal scale ("Excellent → Very poor" vs. "Very poor → Excellent")
would be unusual, and randomizing ordinal point order is not standard. These stay fixed.

**Item order (Q1–Q4):** Your topic-order logic is solid — the four items form a natural narrative
arc and should stay in this order. No change recommended.

**However: response-option order for Item 3** (the open-ended item) has no option list, so nothing
to randomize there.

**The one option-list item that warrants attention:** None of your closed items involve unordered
nominal categories, so there is no primacy/recency correction needed on those. For ordinal scales
like Q1, Q2, and Q4, keeping the natural progression is correct.

In short: your "randomize nothing" decision is defensible for this instrument. The explicit
reasoning holds up.

### No pretesting mentioned — recommend at minimum a cognitive walkthrough

The skill guidance is to recommend pretesting proportionate to stakes. For a 4-item exit survey, a
full cognitive-interview pretest is probably not necessary, but a brief think-aloud with 2–3
representative participants before fielding would surface any comprehension issues — particularly on
Item 4's "this type of tool" ambiguity and the open-text item. Cognitive walkthroughs catch problems
that expert review misses, and at this scale the effort is small.

---

## Priority action list

1. **Clarify "this type of tool" in Item 4.** This is the one wording issue that could genuinely
   obscure what you're measuring. Decide whether the referent is the specific tool or the category,
   and tighten accordingly.

2. **Consider "most confusing" vs. "any confusing" in Item 3.** If you need exhaustive identification
   of problem areas rather than a single worst-one, revise to "Were any parts of the interface
   confusing? If so, please describe them." If rough triage is enough, keep the current wording.

3. **(Optional) Pretest with 2–3 users** before full fielding to catch any comprehension issues,
   particularly on Q4.

Everything else — scale points, labels, midpoints, format choices, order, mode, timing — is
well-executed. This is a clean, appropriately brief exit instrument.
