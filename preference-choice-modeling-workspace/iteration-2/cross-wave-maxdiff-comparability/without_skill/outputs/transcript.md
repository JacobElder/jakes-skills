# Transcript — Without Skill Baseline

**Task:** Cross-wave MaxDiff comparability (25 items Wave 1, 27 items Wave 2 with 5 added and 3 swapped)

**Condition:** No skill loaded — answer from built-in model knowledge only

**Model:** claude-sonnet-4-6

---

## Prompt

> We ran a MaxDiff on 25 product benefits last year and want to run it again this year with 5 new items added and 3 old ones swapped out. Can we compare the utility scores across waves to see which benefits have grown or declined in importance?

## Summary of Response

The model correctly identified the core problem (scale indeterminacy / item-set relativity) and gave a substantive multi-part answer:

- Explained why raw utilities are not directly comparable when the item set changes
- Distinguished the two change types: adding new items (dilutes competition) vs. swapping/removing items (concentrates choices)
- Identified that 22 items overlap and are the basis for any cross-wave comparison
- Recommended rank-order comparisons as the most robust approach
- Described z-score equating / regression equating on the overlap set as an approximate quantitative fix
- Mentioned anchored MaxDiff as the gold-standard future solution
- Mentioned bridging study designs for longitudinal tracking
- Provided a clear summary table of feasibility by comparison type

## Key concepts covered

- MaxDiff scale indeterminacy (utilities are relative to item set)
- Item-set change effects on utility estimation
- Common-item equating / z-score rescaling
- Anchored MaxDiff
- Bridging / bridge condition study design
- Rank-order vs. utility-magnitude comparisons

## Key concepts NOT covered or thin

- Hierarchical Bayes (HB) estimation specifics and whether posterior means behave differently from aggregate logit in this context
- The distinction between zero-centered diffs and probability (share-of-preference) scores and how each is affected
- Formal equating literature from psychometrics (IRT linking)
- The role of sample size on the precision of equating
- Sensitivity analysis / simulation approaches to bound the scale-shift uncertainty
- Sequential testing / change detection frameworks
- Any reference to specific software (Lighthouse Studio, Sawtooth, etc.) or published academic guidance on this topic

## Assessment

The response is directionally correct and would help a practitioner avoid the most common mistake (treating raw cross-wave utilities as directly comparable). However, it is somewhat general and does not go deep on the formal psychometric machinery for equating or the practical decision rules for when differences are "large enough" to be meaningful despite scale shift. A skill with specialist MaxDiff knowledge would be expected to add precision on equating methodology, HB-specific considerations, and actionable thresholds.
