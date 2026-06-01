# Response: Should We Omit the None Option in a B2B CBC?

## Short Answer

Your PM's reasoning is partially right but the conclusion is wrong. Even in markets where everyone uses *some* solution, you should still include a None option in most CBC designs — or at minimum use a dual-response format. Here's why.

---

## The PM's Logic and Where It Breaks Down

The PM is making a reasonable intuition: in a B2B software market with existing incumbents, respondents won't literally go without a tool. Nobody will "choose nothing." So why offer that option?

The flaw is conflating two distinct things:

1. **Whether respondents will go without any software** — probably true they won't
2. **Whether respondents will accept the specific profiles you show them** — a very different question

In CBC, the None option doesn't mean "no software ever." It means "none of *these specific bundles* at *these specific prices* is worth switching to (or buying)." In a B2B context, that often means:

- Sticking with the current incumbent
- Waiting for a better offer
- Continuing to use a workaround or legacy tool
- Escalating the decision (the evaluator isn't the buyer)

If you force-choose among your tested profiles, you're pretending every respondent would realistically switch given the options presented. That's almost never true — especially in B2B where switching costs are high, procurement cycles are long, and inertia is powerful.

---

## The Practical Consequences of Omitting None

### 1. Willingness-to-Pay Estimates Will Be Inflated

When respondents can't say "no thanks," they're forced to choose *something*, even if no profile reflects their real threshold. The resulting part-worth utilities will overstate price insensitivity and inflate WTP estimates. You'll think buyers will pay more than they actually will.

### 2. Market Share Simulations Will Be Unrealistic

Any market simulator built from the conjoint model will assume 100% of the market is capturable if you just configure the right bundle. That produces overly optimistic forecasts. Real markets have non-adopters, deferred purchases, and customers who stay with their current solution.

### 3. Preference Heterogeneity Is Suppressed

Some B2B respondents genuinely have no interest in switching right now regardless of features and price. Forcing a choice from your profiles blends those respondents' responses with genuine preference signals, muddying segment-level estimates.

---

## What to Do Instead

### Option A: Standard None Option

Add a clearly labeled "None of these — I would not switch from my current solution" option to each task. This is the most common best practice for markets with an existing installed base.

Be honest in the framing: label it something like "Keep current solution / None of these" so respondents understand it means status quo, not "go without software."

### Option B: Dual-Response (Anchored) Format

This is often the best approach for B2B markets:

1. **First pass:** Ask respondents to choose the best profile assuming they *must* choose one ("Which of these would you prefer if you had to choose?")
2. **Second pass:** Ask whether they would actually buy/switch, or stick with their current solution ("Would you actually purchase this, or stay with what you have?")

This format recovers both *preference ordering* (useful for understanding which features matter most) and *real purchase likelihood* (useful for realistic WTP and share of wallet estimates).

### Option C: Include a "Current Solution" Profile

A third approach is to explicitly represent the status quo as a profile in each task — defining it by the attributes you're testing (e.g., "your current vendor has X features at Y price"). Respondents compare your new profiles against their actual alternative, not against an abstract "none."

This is powerful for B2B but requires good data on incumbents and can make tasks cognitively heavier.

---

## Summary Recommendation

| Approach | When to Use |
|---|---|
| No None option | Only when you're genuinely simulating a forced-choice scenario (e.g., tender/RFP where a vendor will be selected regardless) |
| None option | Default for most preference research in competitive markets |
| Dual-response | Best for B2B with high switching costs and inertia; clean WTP + realistic share of wallet |
| Status quo profile | When you have reliable data on current solutions; most theoretically clean but most complex |

For a B2B SaaS product with an existing market, dual-response or a None option are both defensible. Dual-response is usually preferred because it recovers preference data cleanly while still anchoring to purchase reality.

Omitting None entirely and force-choosing is the least defensible option — it will make your conjoint model more confident and more wrong.
