# Survey Review: 4-Question Customer Satisfaction Phone Survey

There are five significant problems here — three at the question level and two that cut across the whole instrument. I'll go question by question, name each defect, explain what it does to the data, and give you a concrete fix. Then I'll cover the two instrument-level issues at the end.

---

## Question 1: "How satisfied were you with the speed and friendliness of our support team?" (1–5)

**Defect: Double-barreled.**

This question asks about two distinct things — speed and friendliness — but accepts one answer. A respondent who thought the agent was warm and patient but slow, or fast but brusque, cannot answer truthfully. Whatever number they give you, you cannot tell which dimension it reflects. The response is uninterpretable.

Fix: split into two separate items, each with a fully-labeled 5-point scale.

> Q1a. How would you rate the speed of our support team's response? *(1 = Very slow, 2 = Slow, 3 = Neither slow nor fast, 4 = Fast, 5 = Very fast)*
>
> Q1b. How would you rate the friendliness of our support team? *(1 = Very unfriendly, 2 = Unfriendly, 3 = Neither friendly nor unfriendly, 4 = Friendly, 5 = Very friendly)*

These are item-specific rating scales, which is the right format for evaluating intensity of a single attribute. If you only have room for one item, pick the dimension your team actually uses for decisions and drop the other, or write a single-construct item: "How would you rate the overall quality of service you received?" with the same labeled 5-point scale.

---

## Question 2: "Don't you agree that our pricing is fair?" (Strongly agree / Agree / Neither / Disagree / Strongly disagree)

**Two defects: leading wording and the agree/disagree format.**

**Leading wording.** "Don't you agree…?" is a textbook leading question. It signals the expected answer before the respondent has formed a judgment — "agree" is already embedded in the question stem. The phrasing biases the judgment step. It's the survey equivalent of "Most people think our pricing is fair — and don't you agree?" Wording alone can shift responses by 20 percentage points or more on questions like this.

**Agree/disagree format.** Even if the stem were neutral, the agree/disagree scale carries its own problem: acquiescence. Some respondents — disproportionately those who are lower-education, distracted, or in high-deference social contexts — tend to agree with whatever assertion is placed before them, regardless of content. On a phone survey where a live human is asking, social deference is an especially real pressure. The "agree" response becomes the path of least resistance.

**Fix: item-specific response options with a neutral stem.**

> Q2. How would you rate the fairness of our pricing? *(1 = Very unfair, 2 = Unfair, 3 = Neither fair nor unfair, 4 = Fair, 5 = Very fair)*

This removes the agreement dimension and the leading stem in one move. The respondent evaluates pricing directly on a continuum that goes both directions, without being nudged toward the favorable end.

---

## Question 3: "Which of these did you use? (select all that apply): Live chat, Phone, Email, Help center"

**Defect: "Select all that apply" format invites satisficing.**

Research by Smyth et al. (2006) shows that check-all-that-apply questions systematically undercount endorsements because respondents satisfice — they stop checking after a few items rather than evaluating each option independently. Two people who used the same three channels can give you completely different response patterns depending on when they stopped.

**Fix: forced-choice yes/no for each option.**

Ask respondents to evaluate each channel individually:

> Q3. For each of the following, did you use this channel during your support experience? Please answer yes or no for each one.
>
> - Live chat: Yes / No
> - Phone: Yes / No
> - Email: Yes / No
> - Help center: Yes / No

This takes slightly more time to administer, but on a 4-question phone survey that's minimal. You get complete, comparable data across respondents, and you can tell whether someone deliberately didn't use a channel versus just stopped checking.

**Note on phone administration:** Since your reps are reading this aloud, the forced-choice format is especially important. "Select all that apply" is visually intuitive but aurally awkward — respondents won't have a list in front of them and may not hold all options in mind. Reading each channel with "yes or no?" is far cleaner for a phone mode.

---

## Question 4: "What is your household income? ___"

**Defect: sensitive question administered in the wrong mode and position.**

Household income is among the highest social-desirability-risk items in any survey. Respondents underreport, selectively round, or skip income questions at higher rates than almost any other demographic. On a phone survey where a live rep is asking, social desirability pressure is at its highest — the interviewer-administered mode is the worst possible context for a sensitive financial question. Self-administered modes (web, mail) consistently produce more honest reporting on income precisely because no one is listening.

There's also a placement problem: demographic items should appear at the end of the survey, and this one does appear last, which is correct. But if you need household income for subgroup analysis, you should seriously consider whether this phone mode can deliver usable data on this item.

**Fixes, in order of priority:**

1. **Ask on a different mode if you need reliable data.** If you're running a follow-up web survey, collect income there.

2. **If you must ask here, use non-overlapping income bands with a "Prefer not to say" option:**

> Q4. Which of the following best describes your total household income before taxes?
> ○ Under $25,000
> ○ $25,000–$49,999
> ○ $50,000–$74,999
> ○ $75,000–$99,999
> ○ $100,000–$149,999
> ○ $150,000 or more
> ○ Prefer not to say

The open-ended blank you currently have ("___") will produce a mess of formats (hourly vs. annual, gross vs. net, rounded vs. precise), higher refusal rates, and more social desirability distortion than a banded question. Do not bin at the collection stage if you want to retain flexibility — but a banded format with "Prefer not to say" will get you far more usable responses than an open blank on a phone call.

**Always include "Prefer not to say" on income.** Without it, respondents who don't want to answer must either lie or leave the item blank (which creates missing data you can't distinguish from a skip). A "prefer not to say" response tells you the item was reached and declined — useful for tracking nonresponse patterns.

---

## Instrument-level issues

### Unlabeled rating scale (affects Q1 and any other 1–5 items)

You asked about showing only the numbers 1–5 with no verbal labels, to keep things clean. **Don't do this.** Bare numbers have no inherent meaning — each respondent invents their own verbal equivalent before they can map their judgment onto the scale, which adds cognitive burden and injects idiosyncratic variance into your data. Does a "3" mean average? Acceptable? Neither good nor bad? Different respondents mean different things, and you lose comparability across responses.

This problem is worse on a phone survey, where respondents can't even see the scale — they're just hearing "on a scale of 1 to 5." Without anchors, the rep has to clarify what each end means anyway, which means you're either doing the work in training or in the call itself, inconsistently.

**Fix:** Label every point with words. A fully labeled 5-point scale for satisfaction looks like:

> 1 = Very dissatisfied, 2 = Dissatisfied, 3 = Neither satisfied nor dissatisfied, 4 = Satisfied, 5 = Very satisfied

The rep reads the full scale once to orient the respondent, then reads only the numbers and their labels when the respondent needs a reminder. This is standard phone survey practice. It's not less clean — it's what makes the data meaningful.

### Mode effects on Q3 option order

For a phone survey, the response-option order in Q3 matters differently than for a web survey. Aural modes produce recency bias — options heard last are more likely to be chosen. For Q3 in the forced-choice yes/no format this is less of an issue (each option gets a direct question), but worth knowing: if you rotate or script this survey across multiple reps, keep the option order consistent so any recency effect is at least constant across the dataset.

---

## Summary of changes

| Item | Problem | Fix |
|---|---|---|
| Q1 | Double-barreled (speed + friendliness) | Split into two item-specific rating questions |
| Q2 | Leading stem + acquiescence-prone A/D format | Rewrite as item-specific rating with neutral stem |
| Q3 | "Select all that apply" invites satisficing | Convert to forced-choice yes/no per channel |
| Q4 | Sensitive item in high-SDB mode; open blank; missing "Prefer not to say" | Use banded options + "Prefer not to say"; consider moving to self-administered mode |
| Scale labels | Numeric-only 1–5 forces respondents to invent meanings | Label every point with words |

**Pretest before you launch.** Have two or three reps do a mock call with colleagues playing customers. Listen for: places where the customer asks "what does that mean?", hesitation on the income question, or confusion about the yes/no format on Q3. Even an informal walkthrough will surface things this written review can't catch.
