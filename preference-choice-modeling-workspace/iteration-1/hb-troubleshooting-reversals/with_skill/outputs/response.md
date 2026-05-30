# HB Price Part-Worth Reversals: Diagnosis and Decision

## Short answer

~4% is within the normal range for HB reversals and is almost certainly not a problem requiring immediate action. Do not reflexively constrain monotonicity — but do investigate before closing the file.

---

## Why reversals happen in HB

HB shrinks each respondent's individual utility vector toward the population mean. Respondents who provided limited information — few tasks, inconsistent choices, or both — get pulled hard toward the group center. The shrinkage is asymmetric: a respondent who was mildly price-sensitive in their actual choices can end up with a slightly positive price slope after shrinkage, purely because the population mean for price is near zero and the individual data doesn't overwhelm it.

At 4%, this is well within the 1–5% range that is statistically expected from sparse individual data, not from genuine conspicuous-consumption preferences. It is not a sign that the design or estimation broke.

---

## What to do first: investigate before deciding

Don't assume the reversals are all noise. They fall into three categories and the action differs by category.

**Category 1: Shrinkage artifacts**
Respondents with few completed tasks (or tasks where price wasn't a discriminating attribute) will have weakly identified individual price slopes. HB shrinkage drags these toward the mean. Look at the respondents with positive price part-worths and check:
- How many tasks did they complete?
- Did their choices show any pattern on price (did they ever choose a cheaper option)?
- Is their posterior variance wide (high uncertainty)? Most HB software can report posterior SDs per respondent.

If these respondents have wide posteriors and inconsistent choice behavior, the reversals are artifacts — leave them alone.

**Category 2: Data quality issues**
Speed demons, straightliners, and inattentive respondents can generate reversals. Check response time per task for the reversal group. If they're outliers on response time (either very fast or very slow), consider flagging for exclusion using whatever quality criteria you established before data collection.

**Category 3: Genuine preference heterogeneity**
A small fraction of respondents may legitimately use price as a quality signal — particularly in categories with strong conspicuous-consumption dynamics (luxury goods, professional services, status-linked categories). If your category has this character, positive price utilities may reflect real behavior. Do not constrain these respondents away.

---

## On constraining monotonicity

Monotonicity constraints in HB (or in post-processing) force all respondents to have price part-worths in the expected direction. The tradeoff:

**Arguments for constraining:**
- Produces cleaner simulator output, especially at the tails
- Avoids embarrassing questions from stakeholders about "why does this segment prefer higher prices"
- Justified if you're confident price is unambiguously monotonic for the entire population

**Arguments against constraining:**
- Constraints inject opinion into the model — you are overriding what the data says
- If even a tiny fraction genuinely prefers higher-price signals, constraining removes a real segment
- In HB specifically, the most common implementation of monotonicity constraints (truncating the prior or using order-constrained priors) changes the model in ways that affect all respondents, not just the reversal cases
- If the reversals are shrinkage artifacts (Category 1), constraining is unnecessary — the aggregate and simulator outputs will be fine without it because posterior means with the wrong sign but wide posteriors have low weight in market simulations

**The practical recommendation at 4%:** Do not constrain. At 4%, the effect on aggregate utilities, segment summaries, and simulator shares is negligible. Constraining introduces complexity and the appearance of having manipulated results without a meaningful improvement in output quality. If this were 15–20%, the calculus shifts.

---

## Effect on downstream outputs

For share-of-preference simulators: run your simulation on full posterior draws (not just posterior means). Respondents with reversed price utilities who are genuinely uncertain (wide posteriors) will contribute less extreme values in the simulation because their uncertainty is propagated. Respondents with narrow posteriors and reversed signs deserve deeper investigation.

For segment analysis: if you're reporting price sensitivity by segment, check whether the reversal group concentrates in any particular segment. A cluster of positive-price-utility respondents in a single demo cell could indicate either a real subgroup or a data quality issue confined to that recruit source.

---

## Summary checklist

1. Pull the ~4% reversal group. Check posterior SDs, task counts, and response times.
2. If they're noisy responders with wide posteriors: leave the model as-is. Note in documentation.
3. If they're fast/inattentive: apply quality exclusions and re-run.
4. If they look attentive and high-quality and the reversal persists: investigate whether the category supports a conspicuous-consumption interpretation. Report as a finding, not an artifact.
5. Do not constrain monotonicity unless the reversal rate climbs above ~10–15% or you have strong substantive reason to rule out the real-preference interpretation.
