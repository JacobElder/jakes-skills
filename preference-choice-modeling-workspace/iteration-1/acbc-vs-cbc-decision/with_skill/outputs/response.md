# ACBC vs. CBC: Is the Complexity Worth It?

**Short answer**: For a 9-attribute product with a complex pricing structure (base + add-ons), ACBC is likely justified — but the pricing structure specifically needs more scrutiny before you commit.

---

## Why Sawtooth is recommending ACBC

Sawtooth's ACBC prompt triggers on two signals: (1) attribute count in the 8+ range, and (2) complex pricing. You've hit both. The recommendation isn't wrong, but "Sawtooth suggested it" isn't a reason to accept additional complexity without understanding exactly what you gain.

At 9 attributes, standard full-profile CBC is operating near the edge of respondent tolerance. The research on attribute non-attendance shows that above 7–8 attributes, respondents reliably start ignoring 1–2 attributes per task — not because those attributes are unimportant, but because the cognitive load makes it impossible to process all of them. HB will pick this up as low part-worth variance on the ignored attribute and surface it as "low importance." That's a misread of the data, not a true finding.

ACBC's BYO + Screener stages address this directly: by narrowing the design space around each respondent's consideration set before the Choice Tournament begins, each tournament task is cognitively manageable even with many attributes.

---

## The pricing structure question

This is actually the more important factor. What you describe — base price plus add-on prices — is a configuration problem, not just a pricing problem.

**If respondents are choosing a base product and then selecting optional add-ons independently**: this is a Menu-Based Conjoint (MBC) problem, not CBC or ACBC. ACBC won't model the "buy base + choose add-ons" decision structure correctly; it'll treat the full combination as a profile, which forces unrealistic all-or-nothing tradeoffs. MBC lets respondents assemble their own bundle from the menu, which is what they actually do.

**If pricing is summed across selected components and varies together (not independently selected)**: ACBC's summed pricing engine handles this natively and is genuinely the right tool. You specify the price components, define how they sum, and the instrument handles the arithmetic. This is one of ACBC's clearest advantages over standard CBC.

**If the add-ons are just a way of framing a multi-level price attribute** (e.g., "base + add-on A is always $X, base + add-on B is always $Y"): simplify the structure before the design. Model price as a single combined attribute with the relevant levels. You may be able to run standard CBC.

Get clarity on which of these applies before you commit to an instrument.

---

## What you gain with ACBC (when it applies)

- **Must-have and unacceptable identification per respondent** — the Screener stage surfaces individual-level threshold effects that part-worth ranges can't distinguish from preference.
- **Higher data density near the consideration set** — the Tournament concentrates choices where respondents would actually engage, rather than wasting tasks on combinations no one would ever consider.
- **Handles 9 attributes without partial-profile workarounds** — you don't have to decide which attributes to show in each task.

---

## What you give up

- **Simulator coverage outside the consideration set** — ACBC's information is concentrated near each respondent's BYO. If you want to simulate products that a substantial share of respondents marked as outside their consideration set, your simulator estimates will be noisy. This matters if the study needs to evaluate radical product configurations.
- **BYO seeding bias** — respondents anchor on what they built in BYO. Importance scores from ACBC are typically more spread (higher variance across attributes) than CBC equivalents. Don't use ACBC importance scores as a benchmark against prior CBC studies without adjustment.
- **Longer survey** — ACBC is a meaningfully longer instrument. Budget for it in your fielding timeline and watch completion rates.
- **Unacceptable inflation risk** — if the product is in a category where respondents have strong opinions, you can end up with respondents whose possibility set after the Screener is very small (<8 alternatives). Tournament tasks become under-powered. Monitor this in your soft-launch data: if more than ~10–15% of respondents have a possibility set smaller than 8, you have a problem.

---

## The decision framework

| Condition | Recommendation |
|---|---|
| 9 attributes, summed pricing across components (all shown together) | **ACBC** |
| 9 attributes, respondents configure base + add-ons independently | **Menu-Based Conjoint** |
| 9 attributes, pricing is simplified to a single attribute | **ACBC or CBC** (ACBC still preferable at 9 attributes) |
| You need simulator coverage for products far from any current offering | Add CBC as a complement, or accept degraded simulator coverage in ACBC |
| Survey length is a hard constraint | **CBC with partial-profile** (not ACBC) |

---

## Practical recommendations before fielding

1. **Audit the pricing structure first.** Determine whether the add-ons are independently selected (→ MBC), summed into a total price that varies together (→ ACBC summed pricing), or simply alternative framings of price levels (→ simplify).

2. **Run a soft launch of 30–50 completes** before full field. Check: average possibility set size after the Screener, completion rates vs. your other recent studies, and any attributes where the Screener is marking almost all levels unacceptable (a sign the attribute needs reframing).

3. **Set simulator expectations correctly.** ACBC simulators are most reliable for products in or near the consideration zone. Document this limitation for stakeholders before they start asking for simulations of fringe configurations.

4. **Don't over-index on importance scores from ACBC.** They'll be more spread than CBC equivalents due to BYO anchoring. If a prior CBC study exists, report them separately and note the comparability limitation.

---

## Bottom line

ACBC is the right call for 9 attributes. The complexity is real but proportionate — you'd have non-attendance problems in standard CBC at this attribute count, and that's a worse outcome than a more complex instrument. The part that deserves more scrutiny is the pricing structure: if add-ons are independently selected, you should be in Menu-Based Conjoint, not ACBC. Clarify that before the design is locked.
