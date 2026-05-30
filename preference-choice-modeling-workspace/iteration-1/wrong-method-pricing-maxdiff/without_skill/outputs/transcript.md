# Transcript — Wrong Method: Pricing MaxDiff (Without Skill)

**Eval:** wrong-method-pricing-maxdiff
**Condition:** without_skill
**Model:** claude-sonnet-4-6
**Date:** 2026-05-29

---

## User Prompt

"We're trying to figure out the right price for our new SaaS tier. Thinking about doing a MaxDiff on different price points. Does that work?"

---

## Model Response Summary

The model correctly identified that MaxDiff is a poor fit for pricing research. Key points made:

- Explained what MaxDiff actually measures (relative preference/importance scores among items)
- Identified core reasons it fails for pricing: prices live on an absolute scale, MaxDiff has no opt-out/non-purchase option, no demand curve output, and results would be trivially predictable (cheapest always "best")
- Recommended appropriate alternatives: Van Westendorp (acceptable price range), Gabor-Granger (demand curve/revenue maximization), Choice-Based Conjoint (gold standard — models bundle + price tradeoffs with opt-out), Monadic Price Testing
- Specifically recommended CBC/conjoint for SaaS tier pricing given it handles feature bundles + price simultaneously and mirrors the real purchase decision

---

## Assessment Notes

The response correctly redirected away from MaxDiff for pricing. It named the right alternatives and gave reasonable rationale. The framing around conjoint as the "gold standard" for this use case is standard industry guidance. Van Westendorp and Gabor-Granger were also correctly identified as lighter-weight options.
