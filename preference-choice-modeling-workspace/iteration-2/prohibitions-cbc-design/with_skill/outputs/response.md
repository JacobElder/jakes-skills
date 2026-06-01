# Should You Use Prohibitions to Exclude Premium Brand + Low Price Tiers?

**Short answer: No — use an alternative-specific design instead.**

Prohibitions are the intuitive fix, but they're statistically expensive and there's a structurally cleaner solution for your exact situation.

---

## What prohibitions cost you

When you tell the design engine to exclude premium brand × bottom two price tiers, two things happen:

1. **D-efficiency drops.** Even a handful of prohibitions can cost 1–3% relative D-efficiency; enough prohibitions can push you below 80%, which is a real estimation problem. For your study (2 prohibited combinations out of 20 possible brand-price pairs), the hit is likely modest — probably 1–2% — but it's still a cost you don't need to pay.

2. **Brand and price become partially confounded.** If premium brand never appears at the low tiers, the design cannot independently estimate how respondents would react to that combination. Your premium brand's price part-worths are estimated only in the mid-to-high range, and the "premium brand effect" absorbs some of what is actually the price effect at those tiers. The confound is partial, not total, but it's there.

3. **The simulator loses that region.** If anyone later asks "what would happen to premium brand's share if it competed at a lower price?" — the simulator has no basis for that answer. The CBCpart-worth for premium brand at tier 1 or tier 2 was never identified. You'd be extrapolating outside the design space, and the estimate would be unreliable.

---

## The better approach: alternative-specific design

Rather than prohibiting combinations after the fact, structure the design so each brand has its own price range from the start. This is called an **alternative-specific attribute** design:

- Premium brand: price tiers 3, 4, 5
- Other brands: price tiers 1, 2, 3, 4, 5 (or whatever is appropriate for them)

Sawtooth supports this directly under "alternative-specific attributes." The design engine knows the valid brand-price space per brand and samples accordingly. You get:

- Full D-efficiency (no prohibition penalty)
- No confounding — each brand's price effects are estimated cleanly within its own price range
- A structurally honest model that reflects how these brands actually compete

---

## If alternative-specific design isn't feasible

If your platform or workflow makes alternative-specific design impractical, and you do use prohibitions:

1. **Generate the design and check relative D-efficiency before fielding.** Sawtooth reports this after design generation. If it's below 85%, you're paying a real cost — either increase sample size to compensate or revisit the design structure.

2. **Know what your simulator can and can't do.** Any simulation of premium brand at the bottom two price tiers is an extrapolation, not an interpolation. Don't report those estimates with confidence.

3. **Check the information matrix for confounding.** If your platform shows it, look for substantial off-diagonal covariance between the premium brand indicator and the low-price indicators. That's the confound showing up numerically.

---

## The one question to ask first

Before committing to either approach: will your study ever need to simulate premium brand at a low price point? If the answer is "no, that's not a scenario we'd ever model," then the prohibition's cost of losing that simulator region is a non-issue. But if there's any chance a stakeholder will later ask "what if we ran a promotion that put premium brand at a lower price?" — prohibitions will leave you unable to answer that question reliably. Alternative-specific design preserves the optionality; prohibitions eliminate it.

For a 4-brand, 5-tier CBC where brand positioning genuinely differs across the price spectrum, alternative-specific attributes are almost always the right structural choice.
