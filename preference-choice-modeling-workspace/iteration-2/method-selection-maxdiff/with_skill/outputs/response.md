# Ranking 30 Product Benefits: Method and Sample Size Guidance

## The right method: MaxDiff (with anchoring)

For ranking a list of 30 benefits on a single dimension — importance or appeal for messaging — **MaxDiff is the correct method**. Rating scales are the wrong tool here: respondents will inflate nearly everything to "very important," leaving you with a ceiling-effect mush where 25 of 30 items are indistinguishable. MaxDiff forces trade-offs by asking respondents to pick the best and worst item from each small set, which produces a clean discrimination that rating scales cannot.

Do not use CBC (conjoint) for this. Conjoint is for situations where a product is a bundle of attributes (price + features + brand) and you need to model multi-attribute trade-offs. Ranking messages or benefits on importance is a single-dimension prioritization question — the exact use case MaxDiff was designed for.

## Design: full vs. sparse

With k = 30 items, you're in the upper range of what's workable as a **full design** (every respondent sees every item). The math:

- 4 items per set, target 4 showings per item per respondent → 30 × 4 / 4 = **30 sets per respondent**. That's too long; response quality degrades badly past ~15–18 sets.
- 4 items per set, 15 sets per respondent → r = 15 × 4 / 30 = 2.0 showings per item per respondent. Achievable but tight.
- 5 items per set, 15 sets per respondent → r = 15 × 5 / 30 = 2.5 showings per item per respondent. Better.

**Recommended design**: 5 items per set, 15 sets per respondent (r = 2.5 per respondent). This keeps the survey length reasonable while giving adequate per-item exposure. If you can stretch to 18 sets, that gets you r = 3.0, which is more comfortable.

Alternatively, a **sparse design** (each respondent sees a subset of items) becomes sensible here if you want r ≥ 4 per item per respondent without burying respondents in sets. With a sparse approach — say, each respondent sees 20 of the 30 items, 3× each → 12 sets × 5 items / item-set math works cleanly — you sacrifice some individual-level utility precision but gain cleaner responses. For 30 items, the full design at 15–18 sets is fine; sparse becomes more compelling above k = 35–40.

## You need anchoring

Before getting to sample size: **this study needs anchored MaxDiff**.

Unanchored MaxDiff utilities are purely relative. They will tell you Benefit A ranks above Benefit B, but they cannot tell you whether either is genuinely important — only which is *more* important within your list. If your messaging team will use results to decide "which of these benefits actually motivates purchase," unanchored scores cannot support that claim. A benefit at the bottom of the list might still clear the "would motivate" bar; one near the top might not.

Use a **direct binary anchor** after the MaxDiff sets: show all 30 benefits and ask respondents to flag every one they'd consider a meaningful benefit, or that would actually influence their decision. This creates a threshold. Benefits above the anchor score > 0 in the rescaled space; below means it didn't clear the bar for most respondents. This is what lets you say "7 of our 30 benefits genuinely resonate; the rest are table stakes or noise" rather than just presenting a rank-ordered list.

## Sample size

With 30 items, 5 per set, 15 sets → r = 2.5 showings per item per respondent. Using C ≈ 12 as the scaling constant:

```
SE_i ≈ 12 / sqrt(n × 2.5)
```

| n | SE on 0–100 scale | Smallest detectable gap (95% CI) |
|---|---|---|
| 200 | ~4.8 | ~13 points |
| 300 | ~3.9 | ~11 points |
| 400 | ~3.4 | ~9.5 points |
| 600 | ~2.8 | ~7.8 points |
| 800 | ~2.4 | ~6.7 points |

What "smallest detectable gap" means in practice: at n = 300, if two benefits have true utility scores 11+ points apart on the 0–100 scale, you can reliably distinguish them. Benefits closer together than that will have overlapping confidence intervals and cannot be reliably rank-ordered relative to each other.

**Practical recommendation**: the right number depends on what your messaging team needs:

- **If they need a broad top-tier / bottom-tier split** and won't be making decisions based on rank differences of 3–5 points: **n = 300–400** is sufficient.
- **If they need to distinguish closely competing benefits** — e.g., choosing between the 4th vs. 5th most important message — **n = 500–700** is more appropriate.
- **If you need to read out for subgroups** (e.g., different customer segments, regions, or personas): multiply by the inverse of your smallest subgroup's prevalence. A subgroup that's 25% of respondents needs 4× the overall sample to get the same precision within that subgroup. For two segments at 40/60, aim for n = 200 per segment minimum → overall n = 500.

**Starting point**: **n = 400–500** for an overall readout with moderate subgroup needs. **n = 600–800** if segment-level importance differences are the real deliverable.

## Estimation: use HB, not aggregate logit

Run the analysis with **Hierarchical Bayes (HB)**, not aggregate logit. Aggregate logit treats all respondents as one person — HB borrows strength across respondents while preserving individual-level variation. Even if you only report aggregate results, HB produces more stable tail-item estimates, which matters for a 30-item list where the bottom third is where you most need reliable signal to know what to drop from messaging.

## What to deliver to the messaging team

1. **Anchored importance scores** (rescaled 0–100) with confidence intervals shown, not just point estimates. Present with significance bands so items that are statistically tied are visually grouped.
2. **Share above anchor** — the percentage of respondents who flagged each benefit as genuinely meaningful. This is the number the messaging team will actually use.
3. **Segment breakouts** if your stakeholder cares about different audience profiles — where do segments diverge on what matters?
4. Explicitly label the items that fall below the anchor as "not cleared the bar" rather than "ranked lowest." These are structurally different conclusions.

## Summary

| Decision | Recommendation |
|---|---|
| Method | MaxDiff with direct binary anchor |
| Items per set | 5 |
| Sets per respondent | 15–18 |
| Overall n (no subgroups) | 400–500 |
| Overall n (with 2–3 subgroups) | 600–800 |
| Estimation | HB (not aggregate logit) |
| Primary output | Anchored share-above-anchor + CIs |
