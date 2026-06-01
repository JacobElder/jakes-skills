# Transcript — CBC Sample Size (Without Skill)

**Condition:** No skill loaded. Response from base model built-in knowledge only.

**Prompt:**
> Planning a CBC for a new pricing tier. 6 attributes (brand, price, 4 features). Need to compare enterprise vs. SMB segments (roughly 50/50 in our population). What's the right sample size?

**Model response summary:**

- Cited Sawtooth "rule of 500" heuristic and the `n × t × a ≥ 1,000 × c` formulation.
- Correctly identified that subgroup comparison (enterprise vs. SMB) shifts the sizing logic — subgroup precision, not just overall aggregate precision, becomes the binding constraint.
- Recommended 200 per segment (400 total) as the pragmatic target with HB estimation.
- Provided a tiered table: 300 minimum viable, 400 recommended, 600 conservative.
- Discussed interaction between design parameters (tasks per respondent, alternatives per task, levels per attribute) and required n.
- Noted estimation method differences (aggregate logit, HB, latent class).
- Flagged practical caveats: attrition buffer, recruiting/quota enforcement, price attribute design considerations.

**Notable gaps / potential issues without skill:**
- Did not cite the formal `n ≥ 200 × c / (t × (a-1))` or equivalent information-theoretic formulas used in academic/practitioner literature.
- Did not mention the `c` (maximum levels) constraint operationally — mentioned it but did not compute a worked example.
- No mention of minimum per-cell counts (e.g., each level combination appearing ≥ N times) as a design diagnostic.
- Power calculation framing was informal (cited Cohen's d heuristics rather than a formal CBC-specific power analysis framework).
- Did not reference specific software conventions (Sawtooth, Lighthouse Studio defaults) or cite original sample-size papers.
