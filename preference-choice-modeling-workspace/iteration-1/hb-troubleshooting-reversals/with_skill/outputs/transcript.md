# Eval Transcript — HB Troubleshooting: Price Part-Worth Reversals

## Condition
with_skill

## Skill used
preference-choice-modeling (SKILL.md + references/hb-estimation.md)

## Task prompt
"Just ran HB on a CBC and ~4% of respondents have negative price part-worths (preferring higher prices). Is this a problem? Should I constrain monotonicity on price?"

## References consulted
- `/preference-choice-modeling/SKILL.md` — general orientation, noted that HB utility weirdness usually comes from insufficient burn-in, prohibitions, attribute reversals in a non-trivial fraction of respondents, or bad respondents not filtered
- `/preference-choice-modeling/references/hb-estimation.md` — section "Common HB pathologies and fixes": reversals are an artifact of HB shrinkage + sparse individual data at 1–5%; three options enumerated (leave alone, impose monotonicity, investigate); also covered shrinkage behavior, individual-level posterior uncertainty, and when NOT to use constraints

## Key skill guidance applied
1. The 1–5% reversal range is explicitly called out as expected from HB shrinkage, not a design failure.
2. Three-option framework: leave alone / constrain / investigate — with the instruction to investigate whether reversals indicate a real subgroup (e.g., conspicuous-consumption).
3. Posterior draws vs. posterior means for simulation — using draws propagates uncertainty from wide-posterior reversal cases correctly, reducing their distorting effect.
4. Shrinkage mechanics: respondents with sparse/inconsistent data get more shrinkage; this is the proximate cause of most reversals in well-designed studies.

## Response summary
Response advised against constraining at 4%, provided a three-category diagnostic framework (shrinkage artifact / data quality / genuine heterogeneity), explained the tradeoffs of monotonicity constraints in HB, and gave a practical threshold (10–15%) at which constraining becomes worth considering. Ended with a five-step checklist.
