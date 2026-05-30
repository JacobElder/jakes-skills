# Eval Transcript — ACBC vs. CBC Decision

## Eval metadata

- **Skill**: preference-choice-modeling
- **Iteration**: 1
- **Condition**: with_skill
- **Task**: acbc-vs-cbc-decision
- **Date**: 2026-05-29

---

## Task prompt

> "We're studying a product with 9 attributes including a complex pricing structure (base + add-ons). Sawtooth keeps suggesting ACBC. Worth the complexity?"

---

## Skill files read

1. `/Users/jacobelder/Documents/GitHub/jakes-skills/preference-choice-modeling/SKILL.md`
2. `/Users/jacobelder/Documents/GitHub/jakes-skills/preference-choice-modeling/references/conjoint.md` (Section 6: ACBC, and surrounding context)

---

## Key skill guidance applied

**From SKILL.md — "Should we use ACBC instead of CBC?" handler:**
> Default no unless the product has many attributes (≥8) and a complex pricing structure. ACBC adds complexity and respondent fatigue; the gains are real but situation-dependent.

**From SKILL.md — attribute count guidance:**
> ACBC: handles more attributes (10–12 comfortably) because the BYO and Screener stages narrow the design space before the Choice Tournament.

**From conjoint.md — Section 6: ACBC — When ACBC pays:**
> - Many attributes (≥8) — BYO and Screener stages reduce design space before Tournament
> - Complex pricing (summed price across optional components) — ACBC's summed pricing engine handles this natively
> - Strong must-have / unacceptable patterns — ACBC identifies these per respondent

**From conjoint.md — Section 6: ACBC — When ACBC hurts:**
> - Few attributes (≤5) — BYO just adds survey length without gain
> - Trying to simulate products far from any respondent's consideration set

**From conjoint.md — Section 6: ACBC failure modes:**
> - BYO seeding bias: importance scores from ACBC tend to be more spread than CBC equivalents
> - Unacceptable inflation: watch average possibility set size; if <8, the Tournament is under-powered

**From conjoint.md — Section 7: Menu-Based Conjoint:**
> Use MBC when respondents assemble their own bundle from optional add-ons. Standard independent-logit MBC misses correlation between add-on selections.

**From conjoint.md — Section 3: Attributes (k):**
> 9+ attributes: use partial-profile CBC or ACBC

---

## Response strategy

The task introduced a subtle ambiguity: "complex pricing structure (base + add-ons)" could describe either (a) summed pricing in ACBC's native sense, (b) a true menu/configuration problem that belongs in MBC, or (c) a simplified multi-level price attribute. The skill's guidance on MBC (Section 7) and prohibitions (Section 4) informed the decision to surface this ambiguity as the most important clarifying question before locking the design.

The response:
1. Validated Sawtooth's ACBC recommendation for the 9-attribute count
2. Identified the pricing structure as potentially belonging in MBC rather than ACBC
3. Listed concrete ACBC gains (must-haves, consideration-set concentration, summed pricing)
4. Listed concrete ACBC costs (simulator coverage, BYO bias, survey length, unacceptable inflation)
5. Provided a decision table and practical soft-launch diagnostics
6. Avoided recommending a final instrument without resolving the pricing-structure ambiguity

---

## Output file

`/Users/jacobelder/Documents/GitHub/jakes-skills/preference-choice-modeling-workspace/iteration-1/acbc-vs-cbc-decision/with_skill/outputs/response.md`
