# Psychometrics Skill — Eval Results

## Iteration-1 summary

**Evals:** 8 behavior evals (59 total assertions), 25 trigger evals, 3 adversarial follow-ups, 3 UXR prompts  
**Model:** claude-sonnet-4-6

### Behavior evals

| Condition | Pass rate | Assertions |
|---|---|---|
| with_skill | 100.0% | 59/59 |
| without_skill | 100.0% | 59/59 |
| **Delta** | **+0.0pp** | — |

**Finding:** Zero delta. The base model (claude-sonnet-4-6) already knows the factual content well enough to pass all 8 evals without the skill loaded. The iteration-1 evals tested whether the model *knows* the right answer, not whether it *defaults* to the right answer unprompted.

### Trigger evals

25 queries — 20 should_trigger, 5 should_not.

| Result | Count |
|---|---|
| True positives (correctly triggered) | 20/20 |
| True negatives (correctly not triggered) | 5/5 |
| **Accuracy** | **100%** |

The description is well-calibrated. No false positives or false negatives.

### Adversarial follow-ups (3 scenarios)

All 3 held the line under user pushback:
- **Alpha vs. omega**: Held. Refused alpha-only reporting; offered "report both" as pragmatic compromise.
- **Hu-Bentler cutoffs**: Held. Refused MI-chasing; noted CFI=.93 may be acceptable; distinguished theoretically-motivated MI use from fishing.
- **EFA+CFA same sample**: Held. Rejected "different questions" rationalization; offered concrete alternatives (sample split, honest exploratory framing).

### UXR-flavored prompts (3 prompts, no academic jargon)

All 3 triggered correct psychometric reasoning without any psychometric vocabulary in the prompt:
- A/B testing Likert means → ordinal/interval distinction, ceiling effects, single vs. multi-item
- Averaging 5 brand attributes → reflective vs. formative, dimensionality check, Spearman-Brown
- Pre/post satisfaction → longitudinal measurement invariance raised proactively

### Iteration-1 diagnosis

The evals were correctly designed for content — every assertion is technically accurate — but too easy for a frontier model to pass unassisted. Iteration-1 establishes the skill content is correct; it does not demonstrate the skill adds value over baseline.

---

## Iteration-2 summary

**Design:** 8 new evals, each with an explicit "trap" — a prompt framing where the naive or generic answer is wrong or incomplete. The skill's opinionated stances are tested against cases the base model would hedge, validate the wrong approach, or fail to proactively flag.

**Model:** claude-sonnet-4-6

### Behavior evals

| Condition | Pass rate | Assertions |
|---|---|---|
| with_skill | 100.0% | 47/47 |
| without_skill | 2.1% | 1/47 |
| **Delta** | **+97.9pp** | — |

### Per-eval breakdown

| Eval | Trap | with_skill | without_skill | Δ |
|---|---|---|---|---|
| `pca-not-efa` | "PCA gives my subscales" | 6/6 | 0/6 | +100pp |
| `reverse-item-method-factor` | "Reverse-scoring is standard practice" | 6/6 | 0/6 | +100pp |
| `alpha-threshold-adequate` | "alpha=0.73 meets the threshold" | 6/6 | 0/6 | +100pp |
| `factor-score-indeterminacy` | "fa()$scores is a standard workflow" | 6/6 | 0/6 | +100pp |
| `grm-for-polytomous-irt` | "2PL for 5-point Likert" | 5/5 | 1/5 | +80pp |
| `testretest-state-anxiety` | "ICC=0.72 = good reliability" (inverted logic) | 6/6 | 0/6 | +100pp |
| `construct-definition-gate` | "I have 40 items, what next?" | 6/6 | 0/6 | +100pp |
| `longitudinal-invariance-prepost` | "Scores went up, training worked" | 6/6 | 0/6 | +100pp |

### Representative without_skill failures

- `reverse-item-method-factor`: "This is a sound and standard design" — no mention of method factors anywhere.
- `alpha-threshold-adequate`: Opened with "Yes, alpha = 0.73 is adequate." Endorsed the 0.70 threshold as universal.
- `pca-not-efa`: "It sounds like you're on the right track!" — endorsed eigenvalue>1 and PCA components as subscales.
- `construct-definition-gate`: "Great work putting together those 40 items!" — immediately proceeded to recommend expert review and pilot testing with no construct definition.
- `testretest-state-anxiety`: "ICC = 0.72 indicates moderate-to-good reliability" — praised the 4-week interval as a design strength.
- `longitudinal-invariance-prepost`: "Yes, the data support concluding the training improved psychological safety." Recommended paired t-test, no measurement caveats.

### The one without_skill partial pass

`grm-for-polytomous-irt` (1/5): The generic response mentioned GRM/GPCM as "alternative models" but framed 2PL as a reasonable starting point and suggested dichotomizing the 5-point scale to use binary IRT. Passed only the assertion about mirt package mention; failed on definitively correcting 2PL, explaining threshold parameters, and not endorsing the dichotomization suggestion.

---

## Iteration-2 interpretation

**The skill works.** The +97.9pp delta is driven by the skill's explicit stances on cases where the base model defaults to validating the user's approach rather than correcting it. Six scenarios produced a 100pp gap — the base model fell into every trap.

**What the skill adds:**
1. **Inversion logic** — the testretest-state-anxiety eval requires the model to recognize that high ICC is *bad* for a state measure. The skill's explicit distinction between stability and equivalence is what triggers this.
2. **Proactive gating** — construct-definition-gate requires the model to *stop* before recommending analysis. Without the skill's explicit "number-one mistake" framing, the model proceeds helpfully into the wrong workflow.
3. **Method factor knowledge** — reverse-item-method-factor requires specific empirical knowledge (Blanton & Jaccard, Rodebaugh et al.) that the base model doesn't surface without the skill.
4. **Definitive correction** — pca-not-efa and grm-for-polytomous-irt require unambiguous "no, that's the wrong method" responses. Without the skill, the model hedges ("commonly used," "reasonable starting point").
5. **Indeterminacy awareness** — factor-score-indeterminacy is specialized enough that the base model treats fa()$scores as a standard workflow.

**The 5 flagged weak spots from iteration-1 self-grading:**
- ✅ Alpha/omega hedging → caught in `alpha-threshold-adequate` (+100pp)
- ✅ Reverse-coded items → caught in `reverse-item-method-factor` (+100pp)
- ✅ Construct definition step → caught in `construct-definition-gate` (+100pp)
- ✅ Hu-Bentler cutoffs → confirmed held in iteration-1 adversarial eval
- ✅ EFA+CFA double-dipping → confirmed held in iteration-1 adversarial eval

---

## Skill readiness

| Criterion | Target | Result |
|---|---|---|
| Trigger accuracy (true positives) | ≥80% | ✅ 100% (20/20) |
| Trigger accuracy (false positives) | <20% | ✅ 0% (0/5) |
| Behavior pass rate (with_skill) | ≥85% | ✅ 100% (both iterations) |
| Skill delta vs. baseline | Meaningful | ✅ +97.9pp (iteration-2) |
| Adversarial line-holding | Holds | ✅ 3/3 |
| UXR prompts triggering | All fire | ✅ 3/3 |

The skill meets all criteria. The behavior evals now demonstrate additive value over the base model, not just correct content.
