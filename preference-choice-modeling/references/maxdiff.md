# MaxDiff: Advanced Reference

Table of contents:
1. The model and what utilities mean
2. Design: full vs. sparse, showings-per-item math
3. Sparse MaxDiff in depth
4. Sample size derivation
5. Anchored MaxDiff (and why unanchored is usually wrong for stakeholders)
6. Bandit / Adaptive MaxDiff
7. HB estimation specifics for MaxDiff
8. Quality controls
9. Reporting and common failure modes

---

## 1. The model

MaxDiff is best-worst scaling Case 1 (Louviere). Each set of `m` items shown to a respondent produces two observations: a "best" pick and a "worst" pick. The standard model is multinomial logit on the implied paired comparisons:

```
P(i chosen as best) = exp(U_i) / Σ_j exp(U_j)
P(k chosen as worst | i was best) ≈ exp(-U_k) / Σ_{j≠i} exp(-U_j)
```

The utility scale is logit, so a one-unit difference means the higher-utility item is `e^1 ≈ 2.7×` more likely to be chosen over the lower in a pairwise comparison. This is the scale stakeholders read backwards most often — they treat "utility = 80, utility = 40" as "twice as important," when on a probability-of-choice basis the difference is enormous.

**Rescaled utilities** (sum-to-100 or 0–100 rescale) are what's typically reported, but they obscure the multiplicative nature of the logit. When a stakeholder needs intuition, translate to **probability scores**: `exp(U_i) / Σ exp(U_j)` ×  k, normalized so an average item = 100/k. This makes "item X is twice the average" interpretable.

---

## 2. Design: how showings-per-item drives precision

The key design parameters:
- **k** = number of items
- **m** = items per set (typically 4 or 5)
- **s** = sets shown to each respondent
- **r** = showings per item per respondent = `s × m / k`
- **n** = respondents

Total observations per item across the study = `n × r`. Precision on item utility scales as approximately `1 / sqrt(n × r)`.

For a **balanced full design** every item appears the same number of times for each respondent (`r` is the same for all items per respondent). This is the default in Sawtooth/Qualtrics for moderate k.

Sets needed for a balanced design with `r` showings per item:
```
s = k × r / m
```

Example: k = 20, m = 4, target r = 5 → s = 25 sets per respondent. That's a long survey. Most practitioners cap at s ≈ 12–18 sets and accept lower r.

**The respondent burden ceiling**: most respondents tolerate 12–15 MaxDiff sets without quality degradation. Beyond ~18, response times collapse and the worst-pick especially gets noisy (respondents pattern-respond). So for k > 15 you cannot maintain r = 5 per respondent without splitting the design across respondents — which is exactly what sparse MaxDiff does.

---

## 3. Sparse MaxDiff in depth

In sparse MaxDiff, each respondent only sees a *subset* of items. The full design is balanced **across respondents**, not within. Different respondents see different items, but at the population level every item is seen by roughly the same number of respondents the same number of times.

**Design parameters that matter:**
- `r_pop` = showings per item across the population = (n × s × m) / k
- `n_per_item` = unique respondents who see item i ≈ (s × m × n) / k (when each respondent sees each item at most once)

The crucial constraint: every item needs enough showings *and* enough unique respondents for stable estimation. With HB, the model borrows strength from the population prior, so items can be estimated reasonably even with modest per-item exposure — but only if the *covariance* of co-occurrence is sufficient. If two items never co-occur in any set, their relative utility is identified only through the chain of co-occurrences with other items, and HB shrinkage will pull them toward the mean.

**Rule of thumb for sparse design:**
- Each item should co-occur with every other item at least 2–3 times across the population.
- Each respondent should see each shown item at least 3 times (3 showings per item per respondent within their subset) to enable individual-level estimation at all. Fewer than 3 showings → that respondent's individual utilities are essentially the population prior; you cannot do meaningful segmentation.

**Worked example**, k = 60, m = 4:
- If each respondent sees all 60 items 3× each, that's 45 sets per respondent. Infeasible.
- Sparse alternative: each respondent sees 20 of the 60 items, 3× each → 15 sets per respondent. Feasible.
- For pop-level coverage with n = 600: each item appears in (600 × 20/60) = 200 respondents' sets, each seeing it 3× → r_pop = 600 per item. Plenty.
- For individual-level: each respondent has 15 sets × 4 items = 60 item-observations across 20 items = 3 per item. Borderline for HB; consider 4–5 per item by expanding the subset to 24 items and 18 sets, or accepting more sets.

**Sparse MaxDiff vs. Express MaxDiff**: Sawtooth's "Express MaxDiff" is one specific implementation of sparse where each respondent sees a random subset. There are smarter sparse designs (block designs, BIBD-derived) that minimize the maximum variance across item pairs. For k up to ~80, a well-constructed block design beats random sparse by a meaningful margin. For k > 100, the difference shrinks.

**When sparse breaks down**: with very large k (>150) or when the items are heterogeneous in expected utility (some items clearly dominant), HB struggles because the shrinkage prior is wrong for the tail items. Symptoms: top items look slightly compressed, bottom items look slightly inflated, the middle is fine. Solution: report aggregate utilities only, or do a two-stage design — sparse MaxDiff to identify the top N, then full MaxDiff on those N in a follow-up wave.

---

## 4. Sample size — derived, not rule-of-thumb

The right question is: **what's the standard error on a single item's utility, and is that small enough to support the decision?**

Approximate SE on a rescaled (0–100) item utility:

```
SE_i ≈ C / sqrt(n × r_i)
```

where r_i is showings per item per respondent (or population-level showings if sparse / scaling adjusted) and C is a study-dependent constant typically in the 8–15 range for 0–100 rescaled scores. The constant depends on the underlying utility spread; tighter utility distributions have lower C.

**Worked example, full design**: k = 20, m = 4, s = 15 → r = 3 per respondent.
- n = 200: SE ≈ 12 / sqrt(200 × 3) = 12 / 24.5 ≈ 0.49 on the logit scale, which is roughly 4–5 points on the 0–100 rescaled scale.
- n = 500: SE ≈ 12 / sqrt(1500) ≈ 0.31 logit ≈ 2.5–3 points on 0–100.
- n = 1000: SE ≈ 12 / sqrt(3000) ≈ 0.22 logit ≈ 1.8–2.2 points.

So with n = 200, two items that differ by 5 points are at the edge of statistical distinguishability. With n = 1000, you can reliably distinguish items 4–5 points apart.

**Decision rule**: ask the stakeholder what gap between items they would treat as "the same." If they say "anything within 5 points," n = 200 might work. If they want a tight rank order across the middle of the list, push for n = 500–1000.

**Sparse adjustment**: replace `r` with `r_pop / n_per_item × respondent_per_item_factor`. Practically, for sparse designs, calculate per-item population showings and use:

```
SE_i ≈ C / sqrt(showings_per_item_in_population)
```

**Subgroup precision**: for a subgroup of prevalence p, multiply required n by 1/p to maintain the same per-item precision. If you have 3 subgroups at 30%/40%/30%, you need ~3× the sample for parity across all three. Budget early — this is where studies most often underspend.

---

## 5. Anchored MaxDiff

Plain MaxDiff utilities are **relative**. They tell you item A > item B but not whether either is "important" in absolute terms. This is the source of most stakeholder miscommunication: a deck showing "Item 1: 85, Item 12: 15" lets the stakeholder conclude Item 12 is unimportant, when both might be above (or both below) the threshold of "would actually motivate a purchase."

Two anchoring methods are commonly used:

**Direct binary anchor (recommended default)**: after the MaxDiff sets, ask respondents to flag every item that meets a threshold ("Would you consider this a benefit?" / "Is this important to you?"). The flagged proportion serves as an anchor. Utilities are rescaled so items above the anchor are >0 and below are <0 in the rescaled space.

- Pros: clean interpretation ("X% of items are above the bar"); easy stakeholder framing.
- Cons: introduces a separate task with its own scale-use issues; the anchor question wording matters enormously.

**Dual-response anchor**: after each best-worst MaxDiff set, ask "Are any of the items you selected actually important to you?" or similar binary. This embeds the anchor in the MaxDiff task itself.

- Pros: lower scale-use bias than direct binary; harder for respondents to game.
- Cons: more complex estimation; longer survey; gives noisier anchors than direct binary at typical sample sizes.

**Default**: direct binary anchor for most studies. Dual-response when the items are evaluative (e.g., "how much do you agree" type statements) where a separate anchor task would feel awkward.

**Reporting anchored scores**: lead with the share of items above the anchor for each respondent (and the average across respondents), then the rescaled utilities. Avoid leading with utilities alone.

---

## 6. Bandit / Adaptive MaxDiff

Adaptive MaxDiff uses early choices to inform later set construction — typically focusing more showings on items where utility is uncertain (often the middle of the distribution), and fewer on items clearly at the top/bottom.

**When adaptive helps:**
- Very large item pool (k > 50) where uniform sparse leaves the middle underestimated
- Goal is to rank-order the top 5–10 items with high precision

**When adaptive hurts:**
- Need clean aggregate utilities for *all* items — adaptive creates per-respondent variation in design that complicates aggregate inference
- Need to compare subgroups — adaptive selection can interact with respondent characteristics in unexpected ways
- Sample size is small — the adaptive algorithm has cold-start problems

**Bandit MaxDiff specifically** (Thompson sampling or UCB over items): treats each respondent's task as a multi-armed bandit. Strong for "find the best item" but biased for "estimate all items." Use only when the decision is genuinely top-K identification, not full importance ranking.

**Practical caution**: adaptive designs in commercial platforms (e.g., some Sawtooth implementations) have proprietary algorithms whose statistical properties aren't fully documented. If you can't articulate the adaptation rule, you can't defend the analysis. Default to non-adaptive sparse unless adaptive's specific advantage is needed.

---

## 7. HB estimation for MaxDiff

Aggregate-only logit on MaxDiff data is almost never the right answer. Even when reporting only aggregate utilities, run HB and average — it borrows strength across respondents and produces stabler tail estimates.

**Priors that matter:**
- The covariance prior on the random-effects distribution. Sawtooth's default (degrees of freedom = k + 2, prior variance = 1) is fine for moderate k. For sparse designs with large k, consider weakening the prior on covariance (lower df) to allow more between-respondent variation.
- The mean prior is typically 0 for all items, which is correct under standard normalization. Don't change this.

**Convergence**:
- Run at least 30,000 iterations after burn-in; 100,000 is a safer default. The default 10,000 in some platforms is too few for sparse designs.
- Check: log-likelihood traceplot should stabilize; the variance of mean utility estimates across the last quarter of iterations should be small relative to the SE.
- For sparse designs, also check that the **between-respondent covariance matrix** stabilizes — this is the diagnostic platforms often skip.

**Individual-level utilities**: useful for segmentation, cluster analysis, and reporting "% of respondents who rated Item X above the mean." But never report individual utilities as if they were measurements — they're posterior means with substantial uncertainty for any one person. Report distributions or segment-level summaries.

**Covariates in HB**: you can include respondent covariates (segment, demographics) in the upper-level model. This shrinks individuals toward their segment mean rather than the overall mean, which can sharpen segment differences. Use when segment differences are the deliverable; skip when the deliverable is overall importance ranking.

---

## 8. Quality controls

In order of impact:

**Response time filtering**: drop respondents whose median set completion time is below the bottom 5–10% threshold. Calibrate by looking at the distribution rather than using a fixed seconds-per-set rule.

**Straightlining detection**: in MaxDiff, this looks like always picking the leftmost item as best and rightmost as worst (or some other positional pattern). Calculate position-bias rate per respondent; drop respondents with rate > 80%.

**Internal consistency**: include a duplicated set (or a "trap" set with an obvious dominant item). Drop respondents who flip the dominant item.

**Choice consistency from HB**: HB produces a per-respondent fit statistic. Drop the bottom 5–10% on fit. Be cautious — true segments may look like "bad fit" relative to the population prior, so cross-check with response time before dropping.

**Don't filter on**: utility extremity, segment membership, or anything correlated with the construct you're measuring. That biases the result.

---

## 9. Reporting & common failure modes

**The "rank-order trap"**: stakeholders read a sorted utility list as if the gaps between adjacent items are meaningful. They are not — items 5 and 6 might be statistically indistinguishable. Always show CIs or group-by-significance bands.

**The "absolute importance" trap**: unanchored utilities have no zero. Statements like "Item 12 is unimportant" require an anchor. Without one, the only valid claim is relative ordering.

**The "Top 2 Box" instinct**: stakeholders trained on rating scales want a "% who chose this" summary. The closest valid analog is the anchored share-above-anchor, not the raw rescaled utility. Translate explicitly.

**Segment differences**: if a segment has only 50 respondents in a sparse design with k = 50, individual-item precision within that segment is bad. Pre-compute and report segment-level CIs before sharing segment heatmaps; many "segment differences" disappear under multiple-comparison adjustment.

**Cross-study comparisons**: rescaled utilities from one MaxDiff study are not comparable to those from another (different item set → different normalization). Anchored shares are comparable across studies. If the stakeholder wants to track importance over time, anchor.
