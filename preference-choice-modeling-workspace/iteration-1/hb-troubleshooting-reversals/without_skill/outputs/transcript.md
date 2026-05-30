# Transcript — HB Price Reversal Question (Without Skill)

**Run type:** Baseline (no skill)
**Date:** 2026-05-29
**Model:** claude-sonnet-4-6

## Prompt

> Just ran HB on a CBC and ~4% of respondents have negative price part-worths (preferring higher prices). Is this a problem? Should I constrain monotonicity on price?

## Summary of Response

The response addressed three main areas:

1. **Why reversals occur**: HB's normal population distribution allows individual-level estimates to cross zero (shrinkage toward group mean, noisy respondents, limited price variation, genuine Veblen-good preferences).

2. **Is 4% a problem?**: Judged as within normal range (typical studies see 3–8%). Not alarming at the aggregate level. Flagged as potentially more important if individual-level WTP is the goal or if reversals cluster in a key segment.

3. **Should you constrain?**: Recommended against constraining for most applications. Key reasons: bias-variance tradeoff (constraints bias individual estimates), aggregate results are minimally affected, and model fit may deteriorate. Suggested alternatives include data quality investigation, log-normal/truncated-normal priors in HB, and WTP winsorizing as a lighter-weight fix.

## Key concepts referenced

- HB shrinkage and population-level normal prior
- Individual vs. aggregate part-worth interpretation
- Bias-variance tradeoff under monotonicity constraints
- WTP computation and pathological values
- Log-normal prior as principled alternative to hard constraints
- Design considerations (price level spread, task count)
