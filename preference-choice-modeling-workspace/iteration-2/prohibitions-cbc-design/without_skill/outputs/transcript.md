# Transcript — Baseline (No Skill)

**Condition:** without_skill  
**Model:** claude-sonnet-4-6  
**Date:** 2026-05-29  
**Eval item:** prohibitions-cbc-design

---

**User prompt:**
> We're running a CBC with 4 brands and 5 price tiers. Our premium brand should never appear at the bottom 2 price tiers — those combinations don't exist in the market. Should I use prohibitions in the design to exclude them?

**Agent response summary:**
- Recommended using prohibitions: Yes, this is the standard approach for excluding market-impossible combinations.
- Identified the two specific prohibitions needed: Premium Brand × Price Tier 1, Premium Brand × Price Tier 2.
- Noted trade-offs: reduced D-efficiency, inability to estimate utilities at prohibited cells, extrapolation risk near the boundary.
- Flagged that HB cannot estimate utilities for combinations that never appeared.
- Recommended checking design efficiency statistics after applying prohibitions.
- Advised documenting prohibitions in study protocol.
- Mentioned that "never vs. rarely" is worth considering (full prohibition vs. frequency reduction).
- Mentioned "none" option as standard CBC practice.

**Key claims made (to be scored against rubric):**
1. Prohibitions are the correct approach for market-impossible combinations.
2. They reduce design orthogonality/efficiency — should verify D-efficiency post-constraint.
3. HB cannot estimate utilities for level combinations that never appear.
4. With 2 of 20 combinations excluded, the efficiency loss is modest.
5. Consider whether the restriction is truly absolute vs. partial.
6. Document prohibitions for analysts.
7. Do not interpret utilities for prohibited cells.
