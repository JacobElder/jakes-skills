# ACBC vs. CBC for a 9-Attribute Product with Complex Pricing: Is ACBC Worth the Complexity?

## Short Answer

For a 9-attribute product with a complex pricing structure (base + add-ons), ACBC is often the right call — but it depends on how your attributes are structured and what your research objectives are. Sawtooth's recommendation is reasonable, but it's not automatic.

---

## What ACBC Does That CBC Doesn't

Adaptive Choice-Based Conjoint (ACBC) breaks the interview into staged sections:

1. **Build Your Own (BYO):** Respondents configure their ideal product. This anchors the subsequent tasks to the individual.
2. **Screening:** Near-neighbor concepts are shown; respondents simply accept or reject each (a much easier cognitive task than a full choice).
3. **Choice Tournament:** Only concepts that survived screening are shown in a final tournament of small choice sets.

The result is that each respondent effectively customizes their own interview path. You get far more attribute-level observations per respondent than in standard CBC, and the adaptive design concentrates stimulus near each person's consideration zone.

---

## Why 9 Attributes Favors ACBC

Standard CBC with 9 attributes is cognitively demanding. To estimate main effects plus some interactions you'd need large designs, and respondents often resort to heuristics (ignoring some attributes, lexico-graphic shortcuts) rather than genuine tradeoff processing. ACBC helps because:

- The BYO screen forces respondents to engage with every attribute once, in a natural "build" framing rather than simultaneous comparison.
- Screening tasks are low-cognitive-load binary evaluations — you get many data points without fatiguing respondents.
- The tournament stage focuses respondents only on realistic concepts, avoiding the hollow-exercise feeling of CBC where dominated options are included for design balance.

If many of your 9 attributes are categorical with many levels, ACBC's ability to customize the attribute space per respondent is especially valuable.

---

## The Pricing Structure Complication

A **base price + add-ons** structure is one area where ACBC requires careful design thinking:

### Option A: Treat pricing as a single composite attribute
Compute a total-cost variable and treat it as one attribute. This is clean but loses the additive structure (respondents may respond differently to base price vs. add-on price).

### Option B: Model base price and add-on prices as separate attributes
This is more realistic but adds to your attribute count and can cause problems in the BYO section — respondents may select add-ons without seeing the marginal cost impact dynamically, unless you build pricing logic into your survey platform.

### Option C: Use a price-build logic with dynamic totaling
Sawtooth Software's ACBC module supports dynamic price computation in BYO (summing base + selected add-ons), but you need to implement this carefully. This is arguably the best approach for your situation but requires more setup time.

**Key risk:** If respondents don't understand that add-ons are incrementally priced during BYO, the BYO anchor will be unreliable and contaminate downstream screening and tournament tasks.

---

## When to Stick with Standard CBC Instead

ACBC may not be worth it if:

- **Your attribute count is lower in practice.** If some of your 9 "attributes" are really sub-items under a single price (e.g., 5 optional add-ons plus a base price), restructuring as a simpler attribute set could make standard CBC tractable.
- **You need interaction effects between pricing tiers.** CBC gives you more direct control over what combinations appear, making it easier to estimate specific two-way interactions (e.g., how does add-on A's value depend on whether add-on B is present?).
- **Your sample is B2B or involves expert respondents** who can handle complex simultaneous comparisons better than general consumers.
- **Speed/cost is a constraint.** ACBC interviews are longer and more expensive to program. Standard CBC with a well-designed 9-attribute study (using prohibitions to keep combinations realistic) can be adequate.
- **You're running a shelf or choice simulation** where you need the choice sets to mirror a specific competitive landscape. ACBC's adaptive design makes this harder to control.

---

## Recommendation

**Go with ACBC if:**
- Your sample is general consumers (B2C)
- You want individual-level utilities with high precision (e.g., for segmentation or personalization)
- You're comfortable implementing dynamic pricing logic in BYO
- You have time to program and pilot the instrument

**Consider CBC if:**
- You need tight control over which combinations appear (important for realistic competitive simulations)
- Your pricing logic is complex enough that ACBC's BYO section would confuse respondents
- You're on a timeline or budget that doesn't accommodate ACBC programming

**In either case:** Run a cognitive pilot (5–8 respondents thinking aloud). For a pricing-heavy instrument with add-on structure, the risk of respondent confusion is non-trivial, and you'll catch design problems faster in pilot than in a full-scale launch.

---

## On Estimation

If you do run ACBC, plan for Hierarchical Bayes (HB) estimation — it's the standard for both ACBC and CBC in this kind of study, and it handles individual-level utility recovery well even when each person sees a different subset of attribute combinations (as happens in ACBC). Sawtooth's built-in HB module handles ACBC data well, though you'll want to check convergence diagnostics.

---

## Bottom Line

Sawtooth's ACBC recommendation is sensible for your situation — 9 attributes is in the range where cognitive load starts hurting CBC data quality, and the adaptive design genuinely helps. The main work is on the pricing side: invest time in making the add-on pricing transparent and cumulative in the BYO screen, and pilot it carefully. If that's not feasible given your timeline, a well-designed CBC study (with attribute count reduced where possible) is a defensible alternative.
