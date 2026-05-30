# MaxDiff for pricing: short answer is no

MaxDiff on price points is almost never the right tool for a pricing decision, and it will give you misleading output if you use it here.

## What MaxDiff actually produces

MaxDiff gives you a *relative importance ranking* of the items in the set. If you include five price points — say $9, $19, $29, $49, $79 — MaxDiff will tell you that respondents prefer lower prices over higher prices. You already know that. More importantly, the utilities it produces are not willingness-to-pay estimates and cannot be used to derive a demand curve. They tell you that $9 is "more preferred" than $79, but they cannot tell you:

- How many customers would actually buy at $29 vs. $49 (no demand curve)
- How price trades off against features, brand, or plan tier (no feature-price interaction)
- What the revenue-maximizing price is (requires volume or share prediction, not relative preference)

The SKILL.md puts it directly: "MaxDiff on price points gives a relative preference among prices, which is not the same as willingness to pay or demand curve."

## What you should use instead

The right method depends on what decision you are actually making:

**If you need to understand price sensitivity and set one price for the tier:**
Use **Gabor-Granger** or **Van Westendorp**. These are purpose-built pricing methods. Gabor-Granger asks respondents whether they would buy at each price point (sequential reveal), giving you a direct purchase-likelihood curve by price. Van Westendorp gives you the acceptable price range through four diagnostic questions. Both are fast, cheap, and designed for exactly the question you have.

**If price is one of several attributes you are still configuring (what features come with which tier, at what price):**
Use **Choice-Based Conjoint (CBC)** with price as an attribute alongside the features. CBC forces trade-offs across attributes and lets you build a market simulator. You can then ask: "If we offer these three features at $29/month, vs. these two features at $19/month, what share chooses each?" That is the output you actually need to make a packaging and pricing decision.

**If you have a complex multi-tier structure with optional add-ons:**
Consider **Menu-Based Conjoint**, which models the configuration behavior explicitly, including the option to buy nothing.

## The design failure if you proceed with MaxDiff

Even setting aside the conceptual mismatch, a MaxDiff on price points has a structural problem: the items are ordered. Respondents will trivially pick the lowest price as "best" and the highest price as "worst" in nearly every set. The design produces extreme utilities for a construct (price preference) that has no discriminant validity for your actual decision. You will have high statistical precision on a meaningless result.

## Recommendation

If you are at the stage of "we have a rough price range in mind and want to validate it and find the optimal point," run a Gabor-Granger. It takes 3–4 survey questions, works in Qualtrics or Typeform without any specialized tool, and gives you a purchase-likelihood curve you can apply a margin assumption to.

If you are simultaneously deciding what goes in the tier and what it costs, run CBC with price as one attribute (3–5 levels covering your feasible range) and 2–4 key feature attributes. That gives you the trade-off model you need.

Either way, drop the MaxDiff for this decision.
