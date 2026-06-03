# Quarterly Employee Engagement Pulse Survey — Draft and Design Rationale

---

## The Questionnaire

**[Survey header shown to respondents]**

> This survey is completely anonymous — no individual responses will ever be shared or attributed. Results will be reported only as group aggregates. There are no right or wrong answers. The survey takes about 3 minutes.

---

### Section 1: Manager Support

**Q1.** How would you rate the support your manager provides to help you do your job well?

○ Very poor  
○ Poor  
○ Neither good nor poor  
○ Good  
○ Excellent

---

**Q2.** How often does your manager give you useful feedback on your work?

○ Never  
○ Rarely  
○ Sometimes  
○ Often  
○ Always

---

### Section 2: Workload

**Q3.** How manageable is your current workload on a typical week?

○ Completely unmanageable  
○ Somewhat difficult to manage  
○ About right  
○ Somewhat light  
○ Very light

---

**Q4.** In the past 4 weeks, how often did work demands leave you feeling burned out or depleted at the end of the day?

○ Never  
○ Rarely (1–2 days total)  
○ Sometimes (about once a week)  
○ Often (several days a week)  
○ Almost every day

---

### Section 3: Psychological Safety — Speaking Up

**Q5.** At this company, how comfortable do you feel speaking up when you have a concern or a different point of view?

○ Very uncomfortable  
○ Uncomfortable  
○ Neither comfortable nor uncomfortable  
○ Comfortable  
○ Very comfortable

---

**Q6.** If you raised a concern or disagreed with a decision at work, how likely is it that it would be taken seriously?

○ Very unlikely  
○ Unlikely  
○ Neither likely nor unlikely  
○ Likely  
○ Very likely

---

### Section 4: Retention Intent

**Q7.** How often do you think about leaving this company for a job somewhere else?

○ Never  
○ Rarely  
○ Sometimes  
○ Often  
○ Very often

---

**[Optional open-ended — placed last, clearly marked as optional]**

**Q8 (Optional).** Is there anything else you'd like to share about your experience working here?

[Open text box]

---

## Design Rationale

### Why item-specific rating scales instead of agree/disagree statements

Every substantive question uses an item-specific response format ("How would you rate…", "How comfortable do you feel…") rather than Likert-type agree/disagree statements ("My manager gives me good feedback — Strongly agree … Strongly disagree"). This is the most consequential format choice in the draft.

Agree/disagree scales invite acquiescence bias: the tendency to agree with assertions regardless of content. Acquiescence is not random noise — it inflates endorsement of whatever you happen to phrase positively, and it is stronger among lower-education respondents and in cultures that value deference. In a 300-person workforce with varied educational backgrounds, this is a real risk. Item-specific scales remove the agreement dimension entirely, so there is nothing for acquiescence to act on. The research evidence favors item-specific formats on data quality grounds (Saris et al. 2010; Revilla, Saris & Krosnick 2014).

### Why 5 points on every scale

Each item uses a 5-point scale with all five points labeled in words. The evidence is that reliability and validity rise as scale points are added, then plateau around 5–7. For attitude/evaluation content, 5 points is defensible and has a practical advantage: every point can be clearly labeled in plain English. A 7-point scale is harder to label evenly, and the cognitive benefit of the extra resolution is marginal at best. For agree/disagree scales specifically, 5-point versions outperform 7- and 11-point versions in measurement quality experiments (Revilla, Saris & Krosnick 2014) — and there is no reason to expect different results for item-specific formats.

### Why every point is verbally labeled

All five response options on every item use words, not numbers. Numeric-only scales (e.g., 1–5 with only endpoint labels) require respondents to invent a verbal meaning for each intermediate number before they can map their judgment onto the scale. This adds cognitive burden and introduces idiosyncratic variation. Fully verbal labeling gives each point a shared, stable meaning and has been shown to raise data quality, with the largest benefit for lower-education respondents (Krosnick & Berent 1993; Menold et al. 2014).

### Why a midpoint is included on every item

Each scale includes a neutral midpoint (e.g., "Neither good nor poor," "Neither likely nor unlikely"). For these constructs — evaluation of manager support, comfort speaking up, perceived likelihood of being taken seriously — genuine neutrality is a psychologically real position. An employee who genuinely has no strong view should not be forced to mismap onto a slightly positive or slightly negative option. Omitting the midpoint would push true neutrals into inaccurate responses and inflate apparent polarization.

The one design watch-out: a fat midpoint can indicate satisficing (respondents parking in the middle to avoid the decision). Tracking the midpoint distribution over time is a useful data-quality diagnostic — if midpoint rates spike on a specific item quarter over quarter, that warrants a closer look at question clarity.

### Why the retention item uses frequency rather than intention

Q7 asks how often respondents *think about* leaving rather than asking "Do you intend to leave in the next 6 months?" The frequency framing has two advantages. First, thinking about leaving is less socially threatening to admit than a declared intention; the frequency framing normalizes the experience ("lots of people think about this sometimes") without trivializing it. Second, it is more action-relevant at the company level: frequency of attrition thoughts is a reliable leading indicator of actual departure, and the full range from "never" to "very often" allows tracking of workforce sentiment shifts that binary intent questions miss.

The response scale ("Never … Very often") is genuinely unipolar — there is no meaningful opposite to "never thinking about leaving" — so 5 points fits the construct structure. The reference period is implied as present (current feelings), which is appropriate for a pulse survey tracking real-time sentiment rather than a retrospective measure.

### Why the burnout item (Q4) uses a bounded reference period

Q4 specifies "in the past 4 weeks" rather than asking vaguely "how often do you feel burned out." Vague reference periods degrade the retrieval step: respondents cannot accurately recall an average rate of subjective states over an undefined window. Anchoring to the past 4 weeks — aligning roughly with the quarterly cycle — bounds the retrieval task, reduces telescoping, and produces estimates that are comparable across survey waves (Groves et al.). The frequency options are calibrated to that specific period rather than using generic labels like "often" or "sometimes" alone; Q4 adds a parenthetical count ("1–2 days total," "about once a week") to stabilize what "rarely" and "sometimes" mean for a 4-week window. This follows the principle that vague quantifiers should be anchored with reference counts wherever possible.

### Why the two items per construct

The brief uses two items each for manager support and workload, and two for psychological safety. Single items have unestimable reliability; any one question can be misread, misremembered, or influenced by question-specific wording artifacts. Two items per construct allow a simple internal-consistency check at reporting time and make trends more interpretable when one item shows movement — you can see whether both move or only one. This is the minimum defensible approach for constructs you intend to track over time. If stronger measurement is needed (e.g., for comparisons across teams or demographic subgroups), moving to validated multi-item scales (with reliability analysis) would be the appropriate next step, which crosses into psychometrics.

### Why questions are ordered general → specific, with sensitive content late

The survey opens with manager support, which is the most "professional" and least threatening topic, then moves through workload (more personal but still task-focused), then psychological safety (more personally revealing), and ends with the retention intent item — which is the most personally sensitive question because it implicitly questions loyalty. Placing sensitive items late follows the standard assembly principle: trust and psychological safety build over the course of a short survey, and respondents are more likely to answer honestly on personally sensitive items after they have already invested effort in completing most of the survey. The optional open-text question is placed last, where it imposes no cost on those who skip it and provides a natural completion point for those who want to add context.

### Why the anonymity assurance is upfront and plainly stated

Psychological safety items and the retention intent item are both subject to social desirability pressure in an employment context — respondents may underreport concerns or discomfort for fear of identification. The most effective design remedy for social-desirability bias in a web survey is a genuine anonymity guarantee stated plainly and early. The header assurance does this: it names the protection specifically ("no individual responses will ever be shared or attributed") rather than bureaucratic hedging ("results may be aggregated"), and it frames the purpose positively (using results to improve the workplace). Web-based, self-administered delivery reduces social desirability relative to interviewer-administered modes, which is already a built-in design advantage.

### Why no explicit "Don't know" option appears

None of the items offer a visible "Don't know" or "Prefer not to answer" option. An explicit no-opinion option invites satisficing — respondents who could form a view take the easy exit instead, reducing the information density of the data (Krosnick & Holbrook 2002). For engagement items in an employment context, respondents generally have enough direct experience to form a view; a no-opinion escape is not meaningfully needed for comprehension. The neutral midpoint already provides a legitimate resting point for respondents who genuinely feel ambivalent, which is the appropriate midpoint function.

### Format consistency and straightlining risk

Seven of the eight questions use the same 5-point ordinal format. The consistency speeds completion (a real benefit for a pulse survey) but creates some straightlining risk — respondents who are unmotivated may check the same column repeatedly. Three design features mitigate this. First, the scales are not all oriented the same direction semantically: "Very poor … Excellent" is positive-to-positive, but "Completely unmanageable … Very light" (Q3) and "Almost every day … Never" (Q4) have different top-of-scale anchors, so reflexive column straightlining would produce substantively inconsistent answers. Second, seven questions is a short instrument; completion time for a genuinely engaged respondent should be under 3 minutes, which limits motivation decay. Third, the optional open-text question at the end provides a natural outlet for respondents who want to add nuance, which slightly re-engages attention.

### Survey length and the case for staying short

Eight questions (seven closed, one optional open) is deliberately lean. Pulse surveys exist precisely to impose minimal respondent burden on a recurring basis. Adding more items — even defensible ones — compounds two risks: (a) fatigue-driven satisficing in the later items, which harms data quality on the very questions that should be tracked longitudinally, and (b) declining completion rates on subsequent waves as employees learn the survey takes longer than expected. Every item not included here was implicitly evaluated against whether any decision depends on it. If specific items are needed for particular business decisions (e.g., questions on career development, DEI climate, or specific team dynamics), those should be rotated in as targeted add-ons to different waves rather than added to the core instrument.

### Pretest recommendation

Before fielding, run the instrument through at least three cognitive interviews with employees who represent the range of roles and tenure levels in the workforce. Ask them to think aloud as they complete each item. The specific questions most likely to surface comprehension problems are: (a) Q3, where "manageable" may be interpreted differently by employees with control over their own workload versus those whose workload is externally set; and (b) Q6, where "taken seriously" requires respondents to imagine a counterfactual scenario they may not have experienced. Both items may need wording refinement based on what the cognitive interviews reveal.

---

## Summary of Format Choices

| Question | Format | Points | Rationale |
|---|---|---|---|
| Q1 Manager support quality | Item-specific rating | 5, fully labeled | Evaluation intensity; avoids acquiescence |
| Q2 Manager feedback frequency | Frequency scale | 5, fully labeled | Unipolar frequency; fully labeled |
| Q3 Workload manageability | Item-specific rating | 5, fully labeled | Bipolar construct; midpoint = "about right" |
| Q4 Burnout frequency | Frequency + count anchors | 5, labeled + count | Bounded 4-week period; reduces vague-quantifier ambiguity |
| Q5 Comfort speaking up | Item-specific rating | 5, fully labeled | Psychological safety; item-specific avoids A/D |
| Q6 Likelihood of being heard | Item-specific rating | 5, fully labeled | Complements Q5 with behavioral expectation |
| Q7 Attrition thought frequency | Frequency scale | 5, fully labeled | Frequency > intent; normalizes the question |
| Q8 Open text | Open, optional | — | Interpretive richness; placed last, clearly optional |
