# MaxDiff for Pricing: Does It Work?

MaxDiff (Maximum Difference Scaling, or Best-Worst Scaling) is a great technique for understanding the *relative importance or preference* among a set of items — features, messages, brand attributes, etc. However, using it to set prices for a SaaS tier is a **poor fit**, and here's why.

---

## What MaxDiff Actually Measures

In a MaxDiff study, respondents see sets of items and choose the "best" and "worst" (or most/least preferred) from each set. The output is a set of utility scores that tell you the rank-ordered preference across items. It answers: "Which of these things do people care about most?"

The key property of MaxDiff is that it gives you **relative** preference scores — they sum to a constant and are only meaningful compared to each other within the study. There is no absolute zero; the scores tell you ordering and relative distance, not willingness to pay.

---

## Why MaxDiff Doesn't Work Well for Pricing

1. **Prices exist on an absolute scale, not a relative preference scale.** When you show someone $9/mo, $19/mo, and $49/mo, they're not choosing a "favorite" price the way they'd pick a favorite feature. They're making a value judgment anchored to the actual dollar amounts. MaxDiff strips away that absolute context.

2. **MaxDiff doesn't model the purchase decision.** The goal in pricing research is to understand *at what price people stop buying*, not which price they "prefer" in the abstract. MaxDiff doesn't capture non-purchase (opting out entirely).

3. **No demand curve output.** You can't derive price elasticity, revenue-maximizing price points, or revenue curves from MaxDiff scores on price points.

4. **Results can be misleading.** Respondents will systematically choose the lowest price as "best" and the highest as "worst," giving you a trivially predictable result that doesn't inform strategy.

---

## Better Methods for SaaS Pricing Research

### Van Westendorp Price Sensitivity Meter
Ask four direct questions about too cheap, cheap, expensive, and too expensive thresholds. Fast, easy, gives you an acceptable price range. Good for early-stage exploration.

### Gabor-Granger
Present a price and ask purchase intent at that price. Repeat at different prices across respondents (or within, with care for order effects). Directly gives you a demand curve and revenue-maximizing price point.

### Conjoint Analysis (especially Choice-Based Conjoint / CBC)
Show respondents choice sets containing product configurations at different prices and ask them to choose. This is the gold standard for pricing SaaS tiers because:
- It mimics the real purchase decision (buy vs. not buy vs. buy a competitor)
- It incorporates an opt-out/no-choice option
- You get part-worth utilities and willingness-to-pay estimates
- You can simulate market share at different price points
- It handles bundles of features + price simultaneously, which is exactly what a SaaS tier decision looks like

### Monadic Price Testing
Show a single price to each respondent and measure purchase intent. Clean between-subjects design. Simple and credible.

---

## Recommendation

For a SaaS tier pricing decision, **Choice-Based Conjoint** is likely your best option if you want to test price alongside feature bundles (which you almost certainly do for tier differentiation). If you just want a quick read on the price range, **Van Westendorp** or **Gabor-Granger** will give you actionable data with less complexity.

MaxDiff shines when you're trying to prioritize which features to include in the tier, which value propositions to emphasize in marketing, or how different customer segments weight different benefits — not for setting the price itself.
