# Quarterly Employee Engagement Pulse Survey

## Draft Questionnaire

---

**[Survey Header — shown on landing page]**

*This survey takes about 3 minutes. Your responses are completely anonymous — no individual data will be shared with managers or HR. Results are aggregated across teams before review. Thank you for your candor.*

---

### Section 1: Manager Support

**Q1.** My manager gives me the guidance and support I need to do my job well.

- Strongly agree
- Agree
- Neither agree nor disagree
- Disagree
- Strongly disagree

**Q2.** My manager genuinely cares about my wellbeing, not just my output.

- Strongly agree
- Agree
- Neither agree nor disagree
- Disagree
- Strongly disagree

---

### Section 2: Workload

**Q3.** My workload is manageable — I can get my work done without consistently working unreasonable hours.

- Strongly agree
- Agree
- Neither agree nor disagree
- Disagree
- Strongly disagree

**Q4.** I have the resources, tools, and time I need to do quality work.

- Strongly agree
- Agree
- Neither agree nor disagree
- Disagree
- Strongly disagree

---

### Section 3: Psychological Safety

**Q5.** I feel comfortable raising concerns or disagreeing with decisions without fear of negative consequences.

- Strongly agree
- Agree
- Neither agree nor disagree
- Disagree
- Strongly disagree

**Q6.** On this team, it is safe to take risks and admit mistakes.

- Strongly agree
- Agree
- Neither agree nor disagree
- Disagree
- Strongly disagree

---

### Section 4: Retention Signal

**Q7.** I am currently thinking about leaving this company within the next 6 months.

- Definitely not
- Probably not
- Unsure
- Probably yes
- Definitely yes

---

### Section 5: Open Response (Optional)

**Q8.** Is there anything else you'd like to share — a specific challenge, something that's working well, or a suggestion?

*[Free text field — 500 character limit]*

---

## Format Choices and Rationale

### 1. Scale type: 5-point Likert for most items

A 5-point symmetric agree–disagree scale is the most widely used and understood format for employee surveys. It provides enough granularity to detect meaningful movement quarter over quarter without imposing cognitive load. A 4-point forced-choice scale (dropping the midpoint) is sometimes used to prevent "fence-sitting," but for pulse surveys where people are often genuinely neutral, removing the midpoint inflates artificial disagreement and erodes trust in the tool. The 5-point scale is kept.

### 2. Scale labels: fully labeled, not numeric

Each point is given a verbal label rather than just anchoring the ends (e.g., "1 = Strongly Disagree, 5 = Strongly Agree"). Partial labeling causes respondents to interpret middle points inconsistently, introducing noise into trend data. Full labels reduce that ambiguity.

### 3. Item phrasing: positively worded, behaviorally grounded

Items are written to describe observable conditions ("My manager gives me guidance…") rather than abstract sentiment ("I am satisfied with my manager"). Behavioral anchors are more actionable for managers reviewing results and more reliably interpreted across respondents. Negatively worded items (reverse-keyed) are avoided in a short pulse because they increase completion time and error rates without adding enough precision to be worth it at this scale.

### 4. Retention item: separate response scale

The flight-risk item (Q7) uses a different 5-point scale ("Definitely not" → "Definitely yes") rather than agree–disagree, because the underlying construct is intention, not agreement with a statement. Framing it as "I am thinking about leaving" on an agree–disagree scale would work, but the intention framing ("Definitely yes/no") is more direct and produces a cleaner distribution that is easier to threshold for risk flags.

### 5. Survey length: 7 closed items + 1 optional open text

At 300 employees, a very short pulse (3–4 minutes) maximizes completion rates and minimizes survey fatigue. Research on pulse surveys consistently finds that response rates drop significantly beyond 10 items. Keeping to 7 closed items preserves breadth across three domains while staying under the fatigue threshold. The optional open text provides qualitative signal without penalizing respondents who just want to click through.

### 6. Anonymous, not confidential

The header explicitly says "anonymous" rather than "confidential." Confidential means identifiable data is held by a third party; anonymous means no identity is linked to responses at all. For a web-based survey at 300 people, true anonymity is achievable (no login, no IP logging if configured correctly, aggregation-only reporting). Using the correct term matters — employees who have been told "confidential" and later discovered their responses were traceable lose trust permanently.

### 7. No demographic slicing by default

No department, tenure, or role questions are included in this draft. At 300 people, even a simple two-way cut (e.g., "Engineering, <2 years tenure") can produce cells of 5–8 people where individual responses are inferable. If leadership wants demographic breakdowns, the recommendation is to consult with HR/legal about minimum cell-size reporting thresholds (typically n ≥ 10) before adding those fields.

### 8. Quarterly cadence alignment

The retention item asks about the next 6 months rather than 3 months. Six months maps better to actual job search timelines (most people who are thinking about leaving take 3–6 months to act) and reduces false positives from people who are momentarily frustrated but not actually at risk. At quarterly cadence, the question will be repeated in 3 months anyway, catching people whose intent has solidified.

---

## Recommended Reporting Structure

- Report **mean scores** and **% favorable** (Agree + Strongly Agree) per construct, not individual items, to reduce noise.
- Flag retention risk as: **% who answered "Probably yes" or "Definitely yes"** on Q7 — this number is the one executives typically want to track.
- Set a **minimum reporting threshold of n = 10** for any subgroup cut.
- Trend lines become meaningful after **2–3 quarters** of data; caution against over-interpreting the first wave.
