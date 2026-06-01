# Skill Benchmark: preference-choice-modeling — Iteration 2

**Model**: claude-sonnet-4-6
**Date**: 2026-05-31
**Evals**: 7 (1 run each per configuration)

---

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Assertions passed | 28/29 (96.6%) | 16/29 (55.2%) | **+41.4pp** |
| Per-eval pass rate (mean) | 0.97 ± 0.07 | 0.55 ± 0.10 | — |
| Time (s, mean) | n/a (rate limited) | ~57s (5/7 evals) | — |
| Tokens (mean) | n/a (rate limited) | ~13,150 (5/7 evals) | — |

> **Note**: Most with-skill timing and token data unavailable — API rate limits during the run prevented timing.json writes. The response files were written before limits hit. Based on iteration-1 data, with-skill runs are approximately 23–27k tokens vs. 12–14k without.

---

## Per-Eval Results

| # | Eval Name | With Skill | Without Skill | Delta |
|---|-----------|-----------|---------------|-------|
| 1 | method-selection-maxdiff | 4/4 (100%) | 2/4 (50%) | +50pp |
| 2 | prohibitions-cbc-design | 4/4 (100%) | 2/4 (50%) | +50pp |
| 3 | sparse-maxdiff-design | 4/5 (80%) | 3/5 (60%) | +20pp |
| 4 | cbc-sample-size-with-subgroups | 4/4 (100%) | 2/4 (50%) | +50pp |
| 5 | cross-wave-maxdiff-comparability | 4/4 (100%) | 2/4 (50%) | +50pp |
| 6 | anchoring-absolute-importance | 4/4 (100%) | 2/4 (50%) | +50pp |
| 7 | dual-response-none-cbc | 4/4 (100%) | 3/4 (75%) | +25pp |

---

## Assertion-Level Detail

### Eval 1: method-selection-maxdiff
*"I want to rank 30 product benefits by importance for our messaging team. What's the best approach and roughly how many respondents do I need?"*

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| Recommends MaxDiff (not CBC, not rating scales) | ✓ | ✓ |
| Discusses anchoring (direct binary or dual-response) | ✓ | ✗ |
| Sample size precision-derived, not flat rule-of-thumb | ✓ | ✗ |
| Notes respondent burden / design constraints at k=30 | ✓ | ✓ |

**Key gap**: Without skill, no mention of anchoring anywhere. Sample size given as flat "200–300 respondents."

---

### Eval 2: prohibitions-cbc-design
*"Our premium brand should never appear at the bottom 2 price tiers. Should I use prohibitions?"*

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| Pushes back on prohibitions as primary solution | ✓ | ✗ |
| Explains D-efficiency cost and confounding risk | ✓ | ✓ |
| Recommends alternative-specific attributes as preferred fix | ✓ | ✗ |
| Mentions checking relative D-efficiency if prohibitions used | ✓ | ✓ |

**Key gap**: Without skill, opens with "Yes, using prohibitions is the standard approach" and never recommends alternative-specific design.

---

### Eval 3: sparse-maxdiff-design
*"I have 75 feature ideas. Walk me through items per set, showings per item, sample size."*

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| Recommends sparse MaxDiff | ✓ | ✓ |
| Specifies items-per-respondent-subset, showings/item, sets/respondent with numbers | ✓ | ✓ |
| Discusses co-occurrence balance across population | ✓ | ✓ |
| Sample size 500–1500 range with reasoning | ✓ | ✗ |
| Notes individual-level readout degrades at k=75 | ✗ | ✗ |

**Key gap**: Both configurations missed explicit individual-level degradation framing. Without skill also gives n=200–300 (below range) and implies individual-level is fine with HB. With-skill missed assertion: frames output as aggregate/segment-level but never explicitly names k=75 individual degradation.

---

### Eval 4: cbc-sample-size-with-subgroups
*"6-attribute CBC, enterprise vs. SMB (50/50). What's the right sample size?"*

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| No flat rule-of-thumb without precision conditioning | ✓ | ✗ |
| Surfaces required precision (SE, share difference) | ✓ | ✓ |
| Discusses per-segment precision floor | ✓ | ✓ |
| Derives n in 800–1200 range | ✓ | ✗ |

**Key gap**: Without skill gives "300–400 respondents as a reasonable starting point" and tops out at n=600. Primary recommendation is n=400 total vs. n=800 from skill guidance.

---

### Eval 5: cross-wave-maxdiff-comparability
*"We ran MaxDiff on 25 benefits last year, adding 5 and swapping 3 this year. Can we compare utility scores across waves?"*

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| States raw utilities non-comparable across different item sets | ✓ | ✓ |
| Explains why: different normalizations | ✓ | ✓ |
| Names anchored share-above-anchor as valid cross-wave metric | ✓ | ✗ |
| Addresses unanchored prior wave (re-field or flag clearly) | ✓ | ✗ |

**Key gap**: Without skill recommends z-score equating on common items as the primary cross-wave solution — an approximation the skill correctly identifies as insufficient. Without skill never names share-above-anchor as the correct metric and doesn't give a clear "re-field" recommendation for unanchored prior waves.

---

### Eval 6: anchoring-absolute-importance
*"My stakeholder asks 'which features are actually important' not just 'which are more important than others'. How do I get to that from MaxDiff?"*

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| States unanchored utilities cannot support absolute importance | ✓ | ✓ |
| Recommends direct binary anchor as default | ✓ | ✗ |
| Mentions dual-response anchor as alternative | ✓ | ✓ |
| Discusses share-above-anchor as reporting format | ✓ | ✗ |

**Key gap**: Without skill gives 5 options in parallel without naming a default. Direct binary anchor absent. Share-above-anchor concept absent; replaced with chance-threshold heuristic and top-box analysis.

---

### Eval 7: dual-response-none-cbc
*"Our PM says to leave out the None option since this is an existing market. Is that right?"*

| Assertion | With Skill | Without Skill |
|-----------|-----------|---------------|
| Disagrees with PM's argument | ✓ | ✓ |
| Recommends dual-response None as the default | ✓ | ✗ |
| Explains omitting None inflates shares / conflates signals | ✓ | ✓ |
| Notes defensible context (forced-choice competitive simulation) | ✓ | ✓ |

**Key gap**: Without skill treats explicit None (Option A) and dual-response (Option B) as equally defensible. Never establishes dual-response as the specific recommended default.

---

## Observations

1. **Consistent with-skill pattern**: The skill delivers correct nuanced guidance on every eval. The one miss (individual-level degradation at k=75) is a framing gap — the response implicitly treats aggregate as the target but doesn't name the k=75 ceiling explicitly. Minor fix to SKILL.md would close this.

2. **Consistent without-skill failure modes**:
   - Missing anchoring guidance despite explicit "importance" language
   - Underpowered sample sizes (flat rules vs. precision-derived derivations)
   - Prohibitions treated as standard rather than efficiency-destroying last resort
   - Cross-wave equating approaches instead of re-field recommendation
   - Dual-response None not identified as the specific default

3. **Eval-5 without-skill is actively misleading**: z-score equating recommendation gives practitioners false confidence they can compare across unanchored waves when they cannot. Highest-risk gap identified.

4. **Discriminating range**: 5 of 7 evals show +50pp delta. Two are softer (eval-3 at +20pp, eval-7 at +25pp). The evals are well-calibrated for detecting the skill's value-add — the base model gets the macro-method right but fails on the specific guard rails that prevent study design errors.

5. **Iteration-2 vs. iteration-1**: Iteration-1 with-skill was also 100% across 7 evals. Without-skill was 70.4% on different evals. This iteration's without-skill baseline is 55.2% — suggesting the new eval set targets harder gaps where the base model is more reliably wrong.
