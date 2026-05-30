# Ranking 30 Product Benefits: Best Approach and Sample Size

## Recommended Method: MaxDiff (Best-Worst Scaling)

For ranking 30 product benefits by importance, **MaxDiff (Maximum Difference Scaling)**, also called Best-Worst Scaling, is the gold-standard approach. It is far superior to direct rating scales or simple ranking tasks for lists of this size.

### Why MaxDiff?

**Problems with alternatives:**
- **Rating scales (e.g., 1–7 Likert):** Respondents tend to rate everything as important, producing compressed, non-differentiating data. You end up with most benefits rated "6 or 7 out of 7," which is useless for prioritization.
- **Direct ranking all 30:** Asking respondents to rank all 30 items simultaneously is cognitively exhausting and produces unreliable data, especially in the middle of the list.
- **Top-box picking ("choose your top 5"):** Forces a hard cutoff, loses granularity, and doesn't tell you about relative importance among the top or bottom items.

**Why MaxDiff works:**
- Respondents see small sets (usually 4–5 items at a time) and pick the **most** and **least** important in each set.
- Forced trade-offs produce meaningful discrimination — you can't rate everything highly.
- Produces interval-scale importance scores that are comparable across respondents.
- Cognitively manageable even with large item pools (30 items is well within range).

---

## Study Design Parameters

### Number of Items per Set
Use **4 or 5 items per screen**. Four items is common and reduces cognitive load; five items is also standard and slightly more statistically efficient per task.

### Number of Tasks per Respondent
Each respondent should see enough sets to give every item adequate exposure. A common rule of thumb is:

> **Minimum tasks = (number of items × items per set) / (number of items per set × 2)**  
> More practically: aim for each item to appear roughly **3–4 times** per respondent.

For 30 items shown 4 at a time:
- Each task shows 4 items
- To give each item ~3 exposures: (30 × 3) / 4 ≈ **22–24 tasks per respondent**

This is a reasonable burden (roughly 10–15 minutes). If fatigue is a concern, reduce to ~18 tasks and compensate with a larger sample.

---

## Sample Size Recommendation

For a MaxDiff study with 30 items:

| Precision Goal | Recommended N |
|---|---|
| Directional / early-stage messaging exploration | **100–150** |
| Publishable / confident priority rankings | **200–300** |
| Segment-level analysis (e.g., by persona or region) | **200–300 per segment** |

**Practical recommendation: 200 respondents** for a messaging team needing confident, actionable rankings at the total-sample level.

### Why these numbers?
- MaxDiff is statistically efficient because each respondent generates many paired comparisons. With ~22 tasks per respondent and 4 items per task, each respondent produces 22 best choices and 22 worst choices — equivalent to many indirect pairwise comparisons.
- 200 respondents × 22 tasks = 4,400 choice observations, which is more than enough to estimate stable utility scores for 30 items.
- Standard error of MaxDiff scores at N=200 is typically small enough to reliably separate the top tier, middle tier, and bottom tier of benefits.

---

## Analysis and Output

After fielding, analyze with:
1. **Count-based scores** (quick, approximate): For each item, calculate `(# times chosen as "most") − (# times chosen as "least")` divided by total appearances. Produces a simple importance index.
2. **Logit / HB (Hierarchical Bayes) scores** (preferred): Estimates individual-level utilities, allowing segmentation and more precise ranking. Most MaxDiff software (Sawtooth Software, Qualtrics, etc.) does this automatically.

Output is a ranked list of all 30 benefits with importance scores on a 0–100 scale, showing which benefits to lead with in messaging.

---

## Practical Checklist

- [ ] 30 benefits finalized and written in parallel, respondent-friendly language
- [ ] Design generated (balanced incomplete block design) — most MaxDiff tools do this automatically
- [ ] ~22 tasks per respondent, 4–5 items per task
- [ ] N = 200 total respondents (more if planning segment cuts)
- [ ] Screener to ensure respondents are in your target audience
- [ ] Pilot with 10–20 respondents to catch confusing wording before full launch
