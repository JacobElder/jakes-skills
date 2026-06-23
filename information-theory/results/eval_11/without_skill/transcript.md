# Sample Entropy of RR Interval Series

## Input Data

**RR intervals (ms):**
```
[820, 835, 810, 845, 830, 815, 840, 825, 800, 855,
 828, 812, 848, 833, 818, 842, 827, 805, 852, 831,
 816, 844, 829, 809, 850, 834, 819, 841, 826, 807]
```

N = 30 observations, mean HR ≈ 72.4 bpm.

---

## Step 1: Descriptive Statistics

| Statistic | Value |
|---|---|
| N | 30 |
| Mean RR | 828.20 ms |
| SD (sample) | 15.12 ms |
| RMSSD | 25.30 ms |
| pNN50 | 3.4% |
| Range | 55 ms (800–855) |

The SD is relatively small (CV ≈ 1.8%), which is the first hint that this series is not highly variable — important context for interpreting sample entropy.

---

## Step 2: Tolerance Parameter

Sample entropy uses a tolerance threshold **r** that scales with the spread of the series:

$$r = 0.2 \times SD = 0.2 \times 15.12 = \mathbf{3.02 \text{ ms}}$$

This is the maximum point-wise absolute difference allowed for two subsequences to be counted as "matching."

---

## Step 3: Sample Entropy Algorithm

Sample entropy (SampEn) with embedding dimension *m* and tolerance *r* is defined as:

$$\text{SampEn}(m, r, N) = -\ln\!\left(\frac{A}{B}\right)$$

where:
- **B** = number of template pairs of length *m* with Chebyshev distance < *r* (excluding self-matches)
- **A** = number of template pairs of length *m* + 1 with Chebyshev distance < *r*

The Chebyshev distance between two length-*m* vectors is their maximum point-wise absolute difference. Critically, SampEn does **not** count self-matches (i ≠ j), which removes the bias that affects approximate entropy (ApEn).

---

## Step 4: Counting Matches (m = 2, r = 3.02 ms)

**For m = 2:** Slide a window of length 2 through the series, producing 28 templates (indices 0–27). For every pair (i, j) with i ≠ j, check whether max|rr[i] − rr[j]|, |rr[i+1] − rr[j+1]|| < 3.02.

**Result: B = 48**

**For m + 1 = 3:** Same procedure but with windows of length 3, producing 27 templates.

**Result: A = 28**

---

## Step 5: Final Calculation

$$\text{SampEn}(2,\ 0.2\cdot SD,\ 30) = -\ln\!\left(\frac{28}{48}\right) = -\ln(0.5833) = \boxed{0.539}$$

---

## Step 6: Interpretation

### 6.1 What the number means intrinsically

Sample entropy measures the **conditional probability that two sequences similar for *m* points remain similar for *m* + 1 points**, expressed as a negative log. Higher values indicate that knowing a short pattern gives you little ability to predict the next step — i.e., greater irregularity and complexity. Lower values indicate that similar short patterns tend to continue similarly — i.e., more regularity and predictability.

Here, approximately 58% of length-2 matches also matched when extended to length 3. That is a moderately high continuation probability, yielding a relatively low entropy of 0.539.

### 6.2 What this says about the signal

**The series is quasi-periodic with reduced complexity.** Inspecting the data reveals a clear ~3-beat oscillatory pattern embedded in a slow drift:

- Every 3rd value starting at index 0: 820, 845, 840, 855, 848, 842, 852, 844, 850, 841 (high values, slowly trending)
- Every 3rd value starting at index 1: 835, 830, 825, 828, 833, 827, 831, 829, 834, 826 (mid values, nearly flat)
- Every 3rd value starting at index 2: 810, 815, 800, 812, 818, 805, 816, 809, 819, 807 (low values, slowly trending)

This tri-modal cycling pattern means that when the algorithm finds two similar length-2 subsequences, they are very likely to be in the same phase of the oscillation — so the third point also matches. This boosts A relative to B and depresses SampEn.

### 6.3 Physiological and clinical context

Reference SampEn values from the literature (m = 2, r = 0.2×SD, typical N = 200–1000):

| Population | Typical SampEn |
|---|---|
| Healthy young adults (resting) | 1.2–2.0 |
| Healthy older adults | 0.8–1.4 |
| Mild cardiac dysfunction | 0.5–1.0 |
| Congestive heart failure | 0.3–0.8 |
| Atrial fibrillation | Often > 2.0 (chaotic) |

A value of **0.539 is lower than expected for a healthy resting adult** and falls in the range associated with reduced autonomic modulation. Possible explanations include:

1. **Respiratory entrainment / RSA:** If breathing is slow and paced (e.g., ~0.17 Hz with a 3-beat cycle at 72 bpm), heart rate variability will be locked into a respiratory cycle, reducing SampEn. The ~3-beat oscillation here is consistent with respiratory sinus arrhythmia at a paced breathing rate.

2. **Autonomic suppression:** Elevated sympathetic tone or vagal withdrawal (stress, medication, poor fitness) reduces the complexity of cardiac control, producing predictable, repetitive patterns.

3. **Small N artifact:** With only N = 30, SampEn estimates are unstable. Most guidelines recommend N ≥ 200 for reliable SampEn estimation. With small N, the number of template matches is sparse (B = 48, A = 28), and a change of 1–2 matches can shift SampEn appreciably. The value 0.539 should be interpreted cautiously.

### 6.4 Summary statement

**SampEn = 0.539 indicates a low-complexity, highly regular RR series.** The signal contains a dominant quasi-periodic oscillation (~3-beat cycle) that makes consecutive RR patterns strongly predictable. In a clinical or research HRV context, this level of regularity suggests reduced autonomic flexibility — whether from paced respiration, autonomic suppression, or a pathological reduction in vagal tone. Given the small sample (N = 30), the estimate carries substantial uncertainty, but the quasi-periodic structure visible in the raw data independently corroborates the low-entropy finding.

---

## Calculation Summary

| Parameter | Value |
|---|---|
| m (embedding dimension) | 2 |
| SD | 15.12 ms |
| r = 0.2 × SD | 3.02 ms |
| B (m=2 matches) | 48 |
| A (m=3 matches) | 28 |
| A/B | 0.5833 |
| **SampEn** | **0.539** |
