# Should You Use Prohibitions to Exclude Impossible Attribute Combinations in CBC?

## Short Answer

Yes, using prohibitions (also called restrictions or constraints) in your CBC design is the standard approach when certain attribute combinations do not exist in the real market. For your scenario — where the premium brand never appears at the two lowest price tiers — prohibitions are the right mechanism.

## Why Prohibitions Are Appropriate Here

In conjoint analysis, a **prohibition** tells the design algorithm to never generate a profile combining specific attribute levels. In your case, you would prohibit:

- Premium brand × Price Tier 1 (lowest)
- Premium brand × Price Tier 2 (second lowest)

This is warranted because presenting respondents with profiles they would never encounter in reality creates unrealistic choice tasks. If respondents have strong prior beliefs that the premium brand cannot be cheap, seeing such combinations either confuses them, leads to protest responses, or produces utility estimates that don't reflect real market behavior.

## How Prohibitions Work in Practice

Most CBC design software (Sawtooth Software's SSI Web/Lighthouse Studio, JMP, R packages like `idefix` or `support.CEs`) provides a prohibition or constraint mechanism. You specify pairs or combinations of levels that should never co-occur in the same profile.

The design algorithm then ensures those combinations are excluded from all choice tasks across all respondents.

## Important Trade-offs and Cautions

**1. Reduced design efficiency.** Prohibitions reduce the number of valid profiles the algorithm can draw from, which tends to reduce orthogonality and D-efficiency. With only 2 out of 5 price levels prohibited for one brand, the efficiency loss in your case is modest — but it is real. You should re-check the design's efficiency statistics (D-error, A-error) after applying prohibitions.

**2. Confounded estimates near the boundary.** When certain combinations are never shown, the model cannot directly estimate utility for those cells. For the premium brand, you will be extrapolating its price sensitivity at the lower end of the price range from the levels that are shown. This is generally acceptable if those combinations truly do not exist, but you should be aware that interpolating toward prohibited levels is fine; extrapolating far beyond the observed range is riskier.

**3. HB estimation is robust to sparse cells, but not absent ones.** Hierarchical Bayes models borrow strength across respondents to fill in sparse estimates, but they cannot estimate utilities for level combinations that never appeared. This is consistent with using prohibitions — you simply won't interpret utilities for impossible combinations.

**4. Consider whether "never" is truly never.** Prohibitions are binary: the combination either appears or it doesn't. If the premium brand might realistically be heavily discounted (e.g., clearance, promotions), you may want to reconsider whether full exclusion is correct, or whether a partial prohibition (e.g., greatly reducing frequency) via a blocking or weighting strategy is more appropriate. Some software supports "restrictions" that reduce but do not eliminate certain combinations.

**5. Attribute overlap and partial prohibitions.** With 4 brands and 5 price tiers, you have 20 possible brand-price combinations. Excluding 2 of 20 is a 10% reduction in the combinatorial space — modest. Design algorithms typically handle this without major problems.

## Recommended Steps

1. **Apply the prohibitions** in your design software for Premium Brand × Price Tier 1 and Premium Brand × Price Tier 2.
2. **Evaluate the resulting design's efficiency** — compare D-efficiency or A-efficiency to the unconstrained design. A modest reduction (a few percentage points) is acceptable.
3. **Document the prohibitions** in your study protocol so analysts interpreting HB utilities know these cells were excluded by design, not because of missing data.
4. **Do not attempt to interpret utilities for the prohibited combinations** in your part-worth analysis. Report that those combinations were excluded as market-implausible.
5. **Consider a "none" option** in your choice tasks if respondents might realistically choose not to purchase — this is standard practice in CBC and helps anchor the utility scale.

## Bottom Line

Prohibitions are the correct tool for structuring your design around market realities. Presenting impossible combinations undermines internal validity. The minor cost in design efficiency is worth the gain in ecological validity and data quality.
