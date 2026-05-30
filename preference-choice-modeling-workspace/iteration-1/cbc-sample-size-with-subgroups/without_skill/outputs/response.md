# CBC Sample Size for Pricing Tier Study with Segment Comparison

## Your Study Setup

- **6 attributes**: brand, price, + 4 features
- **Goal**: Compare enterprise vs. SMB segments (≈50/50 split)
- **Method**: Choice-Based Conjoint (CBC)

---

## Key Principles for CBC Sample Sizing

CBC sample size depends on several factors: the number of attributes and levels, number of choice tasks per respondent, number of alternatives per task, and the precision needed for subgroup analysis.

### Common Rules of Thumb

The most widely cited rule in conjoint research comes from Sawtooth Software and related practitioners:

**Minimum cells rule:**
```
n ≥ (500 × c) / (t × a)
```

Where:
- `c` = number of levels for the attribute with the most levels
- `t` = number of choice tasks per respondent
- `a` = number of alternatives per task (excluding "none")

For example, if price has 4 levels, you run 12 tasks, and show 3 alternatives per task:
```
n ≥ (500 × 4) / (12 × 3) = 2000 / 36 ≈ 56 per cell
```

This gives a **floor**, not a target. For segmentation, multiply by the number of segments.

---

## Sizing for Segment Comparison (Enterprise vs. SMB)

When your primary goal is to **compare two segments**, you need each segment to be independently analyzable and the comparison to have sufficient statistical power.

### Recommended Per-Segment Sample Size

For subgroup-level HB (Hierarchical Bayes) or aggregate logit analysis with 6 attributes, a common practitioner target is:

- **150–200 respondents per segment** as a working minimum for stable part-worth estimation
- **200–300 per segment** if you want reliable segment-level preference maps and competitive simulations
- **300+ per segment** if you need tight confidence intervals on willingness-to-pay or price elasticity

### For a 50/50 Split

| Precision Goal | Per Segment | Total N |
|---|---|---|
| Minimum viable (exploratory) | 150 | 300 |
| Standard commercial study | 200–250 | 400–500 |
| High-confidence pricing decisions | 300+ | 600+ |

**Recommendation: Target ~250 per segment → 500 total.**

This gives you:
- Stable segment-level part-worths
- Reasonable power to detect meaningful preference differences between enterprise and SMB
- Enough respondents for sensitivity/simulation analyses

---

## Design Considerations That Affect This

### Number of Tasks and Alternatives

More tasks per respondent can reduce required N. A typical CBC design might use:
- 12–15 choice tasks
- 3 alternatives per task (+ optional "none")

If you drop to 8 tasks, you'll want to increase N. If you go to 16+ tasks, be aware of respondent fatigue.

### Attribute Levels Matter

With 6 attributes, a rough breakdown might be:
- Brand: 3–4 levels
- Price: 4–5 levels (critical for pricing tiers)
- Feature 1–4: 2–3 levels each

More levels = more parameters to estimate = larger N needed for stable estimates. If any single attribute has 5+ levels, push toward the higher end of the range.

### Analysis Method

- **Aggregate logit**: Smaller N can work, but you lose individual-level estimates
- **Latent class**: Needs larger N (300+ total at minimum, ideally 500+)
- **HB (Hierarchical Bayes)**: The gold standard for CBC; allows individual-level estimates and is relatively data-efficient — 200–250 per segment is reasonable with HB

---

## Power for Segment Comparison

If you want to formally test whether enterprise and SMB differ on a key attribute (e.g., price sensitivity), you need statistical power for that comparison. A rough power calculation for detecting a medium effect size (Cohen's d ≈ 0.4) between two groups at 80% power and α = 0.05 requires:

- **~100 per group** (very rough minimum)
- **~200 per group** for more stable detection of smaller but meaningful differences

For pricing studies, you generally want to be able to detect differences in willingness-to-pay of ~10–15% between segments. This typically requires 200+ per segment.

---

## Practical Bottom Line

**Target 500 total respondents (250 enterprise, 250 SMB).**

If budget or feasibility is constrained, 400 (200 per segment) is defensible for most commercial decisions. Below 300 total (150 per segment), segment-level estimates become unreliable and you should be cautious about drawing firm conclusions from comparisons.

If you plan to run HB estimation and primarily care about market simulation accuracy rather than hypothesis testing, 200 per segment (400 total) is a reasonable threshold.

---

## Quick Checklist Before Finalizing

- [ ] Confirm number of levels per attribute (especially price — more levels = larger N)
- [ ] Decide number of choice tasks (12 is a common default)
- [ ] Decide on "none" option inclusion (affects design and analysis)
- [ ] Confirm analysis method (HB, latent class, aggregate logit)
- [ ] Check if you need within-segment subgroup analysis (e.g., company size within enterprise) — if so, increase N further
