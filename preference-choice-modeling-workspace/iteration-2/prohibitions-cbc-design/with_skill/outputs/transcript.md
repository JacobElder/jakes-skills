# Reasoning Transcript: Prohibitions in CBC Design

## Task
The user is running a CBC with 4 brands and 5 price tiers. Their premium brand should never appear at the bottom 2 price tiers (those combinations don't exist in the market). They're asking whether to use prohibitions in the design to exclude them.

## Skill Activation
This question directly matches the SKILL.md trigger: "handling prohibitions" and specifically the common request handler: "Should I use prohibitions to block unrealistic combinations in my CBC?" The skill provides a clear default answer (almost always no) and points to the prohibitions section in references/conjoint.md for the detailed treatment.

## Reasoning Steps

### Step 1: Identify what's actually being asked
The user wants to exclude brand × price combinations — specifically, premium brand combined with the two lowest price tiers. This is a classic prohibition scenario: they have a constraint rooted in market reality (premium brand doesn't appear at low price points), and they want the survey stimuli to reflect that.

The instinct is understandable. If respondents see "Premium Brand at $5.99" and the actual market price is $24.99+, they might treat the profile as a trick question or as a novelty, introducing noise. The prohibition feels like it's protecting validity.

### Step 2: What does the skill say about prohibitions?
The conjoint reference (Section 4) is explicit:

- Prohibitions reduce D-efficiency. "A few prohibitions cost 1–3% D-efficiency; many can drop you below 80%."
- They create partial or full confounding between main effects and the prohibition pattern. In this case, brand and price are now partially confounded — we cannot cleanly estimate the premium brand's price sensitivity at the low end, because we never show it there.
- They invalidate the simulator outside the prohibited region. If a stakeholder later wants to run "what if our premium brand went on sale at a lower price point?" — the model cannot answer that question. The parameter space doesn't include it.
- The skill's stated default policy: "use the minimum number of prohibitions necessary to keep the design face-valid."

### Step 3: How serious is the efficiency hit here?
The user has 4 brands × 5 price tiers = 20 possible brand-price combinations. They want to prohibit 2 of those 20 (premium brand × bottom two price tiers). That's 10% of the brand-price space removed.

For a 2-attribute prohibition affecting one brand out of four, this is on the lighter end of prohibition damage. The relative D-efficiency hit is likely 1–3%, which is within the "annoying but not disqualifying" range if the prohibition is truly necessary.

But "within acceptable range" is not the same as "the right approach." The question is whether a better structural solution exists.

### Step 4: What are the alternatives?
The reference gives three alternatives:

**Option A: Alternative-specific design**
Each brand gets its own price range. Premium brand: tiers 3–5. Other brands: tiers 1–5 (or perhaps tiers 1–4, depending on their positioning). This is structurally cleaner than a prohibition — rather than "exclude this combination," you define per-brand price ranges from the start. Sawtooth supports this directly. This is almost certainly the right answer for this study.

**Option B: Conditional (relative) pricing**
Define price levels as relative to each brand's baseline (e.g., -10%, baseline, +10%, +20%, +30%). The premium brand's "bottom" price is still a premium price in absolute terms. This avoids the brand × price confound and avoids showing unrealistic absolute prices. Works especially well if the brands span different price tiers and you want to estimate price sensitivity as a relative concept.

**Option C: Prohibition with D-efficiency monitoring**
If neither option A nor B is feasible (e.g., the platform doesn't support it, or absolute price comparisons across brands are central to the research question), use the prohibition but explicitly check relative D-efficiency post-design generation. Below 85% is a warning sign.

### Step 5: What does this mean for their specific situation?
- 4 brands, 5 price tiers
- Premium brand should never see bottom 2 price tiers
- They want to know: prohibition or not?

The right answer is: don't use a prohibition — restructure the design as alternative-specific instead. Define the premium brand's price range as tiers 3–5 from the outset. The other three brands can span whatever price range is appropriate for them.

This achieves the same face-validity goal (premium brand never appears at the lowest prices) without the statistical cost of a prohibition, and without confounding brand and price effects.

### Step 6: What should they watch for?
If they do proceed with prohibitions (e.g., platform constraints), they should:
1. Generate the design and check relative D-efficiency before fielding.
2. Know that simulator estimates for "premium brand at low price" will be extrapolations outside the design space — those simulations are unreliable.
3. Check that brand and price main effects are not substantially confounded in the information matrix.

### Step 7: Any other considerations?
The user mentions "those combinations don't exist in the market" — this is the correct reason for the restriction. However, it's worth flagging that CBC is often used precisely to estimate hypothetical combinations (counterfactuals, price elasticity). If the study will never ask "what if premium brand went low?" then the prohibition's exclusion of the simulator counterfactual isn't a practical cost. If it will, the cost is severe.

For a 4-brand, 5-price-tier design, alternative-specific attributes are the cleaner path in virtually all cases.
