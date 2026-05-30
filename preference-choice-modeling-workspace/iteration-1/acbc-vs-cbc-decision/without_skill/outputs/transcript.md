# Transcript — Without Skill Baseline

**Task:** "We're studying a product with 9 attributes including a complex pricing structure (base + add-ons). Sawtooth keeps suggesting ACBC. Worth the complexity?"

**Condition:** No skill assistance (base model only)

**Model:** claude-sonnet-4-6

**Date:** 2026-05-29

---

## Summary of Response

The model provided a structured recommendation covering:

1. **What ACBC does differently** — staged BYO, screening, and tournament phases that reduce cognitive load relative to standard CBC.
2. **Why 9 attributes favors ACBC** — cognitive burden argument; more observations per respondent; concentration of stimuli in each person's consideration zone.
3. **Pricing structure complications** — three options for handling base + add-on pricing in ACBC (composite, separate attributes, dynamic totaling), with a specific caution about BYO screen design.
4. **When to use standard CBC instead** — B2B/expert samples, need for interaction effects, competitive simulation requirements, timeline/cost constraints.
5. **A concrete recommendation** — ACBC favored if B2C, if individual-level utilities needed, if dynamic pricing is implementable; CBC defensible alternative if not.
6. **Estimation note** — HB estimation recommended; Sawtooth HB handles ACBC data well.

## Key Strengths of Response

- Correctly identified the three ACBC phases (BYO, screening, tournament)
- Correctly identified the cognitive load rationale for ACBC at 9+ attributes
- Raised the specific design challenge of add-on pricing in BYO, which is a genuine practical problem
- Mentioned HB estimation as appropriate
- Recommended cognitive piloting

## Key Gaps / Areas Where Skill Might Add Value

- Did not discuss ACBC sample size requirements vs. CBC (ACBC typically needs more respondents to achieve stable HB estimates due to sparser individual-level data)
- Did not mention the "must-haves" / "unacceptables" screening concept specific to ACBC
- Did not discuss attribute importance/sensitivity implications of ACBC's adaptive design
- Pricing treatment options mentioned but not linked to specific Sawtooth design features (e.g., the "summed pricing" feature in Sawtooth's ACBC module)
- No mention of prohibitions or alternative-specific attributes, which are relevant to pricing complexity
- General rather than specific guidance on BYO pricing logic implementation
