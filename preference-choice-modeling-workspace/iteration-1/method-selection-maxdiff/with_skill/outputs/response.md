# Ranking 30 Product Benefits: Method and Sample Size

## Method: MaxDiff (full design, with direct binary anchor)

For ranking 30 benefits on a single dimension — importance for messaging — **MaxDiff is the right method**. A rating scale will give you 25 of 30 benefits rated "very important" and no real rank order. MaxDiff forces trade-offs, eliminates scale-use bias, and produces a rank order your team can actually act on.

With 30 items you are comfortably in full-design territory (not sparse). Every respondent sees every item, so you get clean individual-level coverage without needing to split the design across respondents.

**Add a direct binary anchor.** Unanchored MaxDiff utilities are relative-only: they tell you benefit A ranks above benefit B, but not whether either is "important" in absolute terms. After the MaxDiff sets, ask respondents to flag every benefit that meets a threshold (e.g., "Would this be a meaningful reason to buy?"). This rescales the utilities so items above the anchor are positive and below are negative, and lets you report "X% of benefits are above the bar" — a stakeholder-friendly framing that avoids the common trap of treating the bottom half of the rank order as "unimportant" when it may just be less important than the top.

---

## Design parameters

- **k = 30** items, **m = 4** items per set
- Sets per respondent: target **r = 3–4 showings per item per respondent**
  - r = 3 → s = 30 × 3 / 4 = 22–23 sets — on the high side of comfortable
  - r = 2.5 → s ≈ 19 sets — more typical, acceptable with a well-balanced design
  - Practical recommendation: **15–18 sets** at 4 items per set, giving r ≈ 2–2.4 per respondent. This keeps the survey under 15 minutes.

For 30 items and 15–18 sets, the design is manageable with any standard platform (Sawtooth, Qualtrics). Use a balanced incomplete block design if you have the tooling; if not, the platform's automatic design at these parameters will be close enough.

---

## Sample size

The right answer depends on two questions your team needs to answer first:

**1. What's the smallest gap you need to reliably distinguish?**

With k = 30, m = 4, and 15 sets per respondent, r ≈ 2 showings per item per respondent. Using C ≈ 12 for the 0–100 rescaled scale:

| n | SE on 0–100 scale | Smallest detectable gap between two items (95% confidence) |
|---|---|---|
| 200 | ~6 pts | ~17 pts |
| 300 | ~5 pts | ~14 pts |
| 500 | ~3.8 pts | ~11 pts |
| 750 | ~3.1 pts | ~9 pts |

If your messaging team needs to separate a tight pack in the middle of the list — distinguishing benefit #12 from #14 — you need n in the 500–750 range. If you mostly need to confirm the top 5–8 and the bottom 5–8, n = 300 may be enough (those items likely span more than 15 points).

**A practical starting recommendation for a 30-item study with no subgroups: n = 400–500.** This gives ~10–11 point detection resolution — enough to support clear tier separations (top tier, middle tier, low priority) without the cost of a larger study.

**2. Will you read out for subgroups?**

If you need segment-level importance rankings (e.g., enterprise vs. SMB, or by customer lifecycle stage), multiply required n by the inverse of the smallest segment's prevalence. A segment that's 25% of your population means you need 4× the base sample to have the same within-segment precision. For two segments at 40/60, design for the 40% segment: roughly 2.5× the base. For subgroup readouts, expect n = 800–1,200 depending on segment sizes.

---

## What to avoid

- **Rating scales** ("Rate each of 30 benefits on a 1–5 scale"): produces ceiling effects and no real discrimination. Do not do this.
- **Conjoint** for this task: CBC models trade-offs across product attributes (including price) to predict choice share. It is the wrong tool for ranking a flat list of messaging benefits. MaxDiff is correct here.
- **Skipping the anchor**: if you report utilities without anchoring, the stakeholder will declare the bottom-ranked benefits "unimportant." They may or may not be — you won't know without an anchor. Add it.
- **Reporting point estimates without uncertainty**: after you run HB, report confidence intervals (or at minimum standard deviations) around the utility estimates. Items that are statistically tied should be presented in the same tier, not ranked sequentially as if the gap were real.

---

## Execution checklist

1. Generate a balanced MaxDiff design for k = 30, m = 4, s = 15–18.
2. Field to at least n = 400 (adjust up if subgroups matter; adjust up to 500 if a tighter rank order is required).
3. Include a direct binary anchor task after the MaxDiff sets.
4. Estimate with HB (not aggregate logit). Run at least 30,000 post-burn-in iterations.
5. Include ≥1 consistency trap set to screen low-quality respondents.
6. Report: anchored rescaled utilities on a 0–100 scale, grouped by statistical significance tier, with CIs visible. Lead with the share of benefits above the anchor, not the raw rank order.
