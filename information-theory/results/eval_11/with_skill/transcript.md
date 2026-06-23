# Sample Entropy of RR Interval Series

## What was asked

Compute sample entropy (SampEn) of 30 inter-beat (RR) intervals in milliseconds,
with embedding dimension m = 2 and tolerance r = 0.2 × SD, and interpret the result.

**Series:** [820, 835, 810, 845, 830, 815, 840, 825, 800, 855, 828, 812, 848, 833,
818, 842, 827, 805, 852, 831, 816, 844, 829, 809, 850, 834, 819, 841, 826, 807]

---

## Step 1: Name the object precisely

This is **not** a Shannon entropy question. The user has an *ordered time series* and
is asking how predictable the next value is given recent history — that is a
time-series regularity question in the Pincus / Richman–Moorman lineage. SampEn is the
right tool. The result is **not in bits** and must not be averaged with or substituted
for Shannon entropy or mutual information.

---

## Step 2: Computation

Using `scripts/sample_entropy.py` with the matched-count formulation (self-matches
excluded, Chebyshev distance, population SD for tolerance):

```
N       = 30
Mean RR = 828.200 ms
SD      = 14.869 ms   (population std, ddof=0)
r       = 2.974 ms    (0.2 × SD)

SampEn(m=2, r=0.2×SD) = 0.606
```

**Algorithm recap (SampEn = −ln(A/B)):**
- Embed the length-30 series into (N−m) = 28 template vectors of length m = 2.
- B = count of template pairs (i ≠ j) whose Chebyshev distance ≤ r at length m = 2.
- A = count of template pairs whose Chebyshev distance ≤ r at length m+1 = 3.
- SampEn = −ln(A/B) ≈ −ln(0.546) ≈ **0.606**.

Self-matches are excluded in both the m and m+1 counts — this is the key design
decision that makes SampEn less biased than ApEn for short series.

---

## Step 3: Interpretation

### What SampEn = 0.606 says about this signal

**Moderate regularity.** The signal sits between the extremes:

| Reference signal (N ≈ 600, m=2) | Typical SampEn |
|----------------------------------|---------------|
| Periodic sine wave               | ≈ 0 (fully predictable) |
| Physiologically healthy HRV      | ≈ 0.8–1.6 |
| White noise                      | ≈ 2.0–2.5 |

A SampEn of 0.606 is lower than what is typically reported for healthy, resting adult
HRV (which commonly ranges 1.0–1.6 at these parameters). That pattern is consistent
with a signal that has **substantial but not pathological regularity** — each 2-beat
window is a fairly reliable predictor of the next beat, but the series is not
perfectly periodic.

Looking at the raw values, this is confirmed by inspection: the series oscillates
with a clear wave-like pattern (values cycle down and back up with period ~ 8–10
beats), explaining why template matches are abundant and SampEn is suppressed
relative to a truly uncorrelated HRV series.

### Three caveats that matter here

1. **N = 30 is short.** Richman & Moorman's original SampEn paper motivates the
   estimator partly by ApEn's instability on short series, but SampEn itself can be
   noisy at N = 30. The value here should be treated as an indicative point estimate,
   not a precise physiological index. Clinical HRV guidelines typically recommend
   N ≥ 200–1000 beats for stable SampEn. The finite-sample variance on a 30-point
   estimate is substantial, and a bootstrap confidence interval would be wide
   (plausibly ± 0.2–0.4 around this value).

2. **Parameter sensitivity is real — always report (m, r, N).** This value is
   SampEn(m=2, r=0.2×SD, N=30) = 0.606. Changing r from 0.2×SD to 0.15×SD or
   0.25×SD, or changing m from 2 to 1 or 3, will move the number. Never compare
   SampEn values across studies that used different (m, r, N). The r = 0.2×SD
   convention normalizes for the series' own variance, which is appropriate here.

3. **SampEn is not in bits; do not log2 it.** The natural log in the formula means
   the scale is notional (larger = more complex/irregular). Reaching for np.log2 on
   this value, or averaging it with a Shannon entropy or MI estimate, is a category
   error. It belongs to the Richman–Moorman lineage, not Shannon (1948).

### Summary sentence

SampEn(m=2, r=0.2×SD) = **0.606** — the series shows moderate but real regularity,
consistent with a quasi-periodic structure visible in the raw values, and meaningfully
lower than typical resting healthy-adult HRV. Treat the exact value cautiously given
N = 30; it is a directional signal, not a precise clinical index.
