# Quantifying EEG Complexity: Which Entropy and How to Read It

You have a 10-minute EEG channel at 256 Hz — that is 153,600 samples. The word "entropy"
is doing a lot of work here and the right answer depends on which question you actually
mean.

---

## Step 1: Identify the question you are asking

There are two fundamentally different questions that both use the word "entropy":

| Question | Framework | Destroyed by shuffling? |
|---|---|---|
| "How many bits does the *amplitude distribution* carry?" | Shannon entropy (or differential entropy) | No — it is order-invariant |
| "How predictable is the *next sample* given recent history?" | Sample/permutation/multiscale entropy | Yes — these measure temporal regularity |

For EEG complexity and unpredictability, you almost certainly mean the second question.
"Complex" and "unpredictable" in physiological signal analysis means the signal resists
prediction from its own past — which is what **sample entropy (SampEn)** and its family
measure. If you shuffled the signal and the answer stayed the same, that is not the
complexity you care about.

Do not reach for Shannon entropy here. Shannon entropy of the amplitude distribution
ignores temporal order entirely. A perfectly periodic 10 Hz sine wave and white noise
can be made to have the same amplitude histogram and therefore the same Shannon entropy,
but they are maximally different in their complexity. Shannon entropy is the wrong tool.

---

## The recommended measure: Sample Entropy (SampEn)

SampEn measures how often a short template of the signal (length `m`) continues to match
at length `m+1`. High SampEn = complex/irregular; low SampEn = regular/repetitive.

**Algorithm** (Richman & Moorman 2000):

1. Choose embedding dimension `m` (conventional default: `m = 2`) and tolerance `r`
   (conventional default: `r = 0.2 × std(signal)`).
2. Count all pairs of length-`m` subsequences that match within Chebyshev distance `r`.
   Call this count `B`.
3. Count pairs that still match at length `m+1`. Call this `A`.
4. `SampEn(m, r) = −ln(A / B)`

Self-matches are explicitly excluded. This is the entire improvement over the older
approximate entropy (ApEn): ApEn includes self-matches, which biases it toward "more
regular" and makes it series-length–dependent. Use SampEn; mention ApEn only if you
need backward comparability with older clinical literature.

---

## How to read the number

- **Low SampEn (near 0):** the signal is highly regular — templates at length `m`
  almost always extend to `m+1`. Seen in pathological states (anesthesia, severe seizure),
  drowsiness, artifacts from movement contamination.
- **High SampEn:** the signal is irregular/complex. Healthy resting-state EEG
  typically shows higher entropy than pathological states.
- **SampEn = +∞:** `A = 0`, meaning no template ever matched at length `m+1`. This is
  not a real result — raise `r` or, less likely, lengthen the series. Do not report infinity.
- **Units:** SampEn is not in bits. It is a log-ratio of match counts. Never take `log2`
  of a SampEn value or average it with a Shannon entropy; that is a category error.

---

## The parameter sensitivity warning (do not skip)

SampEn depends on three things you chose: `m`, `r`, and the series length `N`.

- `m = 2` and `r = 0.2 × SD` are conventional, not ground truth.
- `r` is a fraction of the series SD — this means **two channels with different variance
  will have different effective tolerances** unless you fix `r` to a common value or
  standardize the signal first. When comparing EEG channels or subjects, be explicit
  about which you chose.
- **Never compare SampEn values across studies that used different `(m, r, N)`.**
  A "higher entropy in patients" result from one paper and a "lower entropy in patients"
  result from another may simply reflect different parameter choices, not a contradiction.

Report your `(m, r, N)` alongside every SampEn value, always.

---

## Also consider: permutation entropy and multiscale entropy

### Permutation entropy (PE)

Take the rank-order pattern (argsort) of each length-`order` window and compute the
**Shannon entropy of the motif-frequency distribution**, normalized by `log₂(order!)`.
This one *is* a genuine Shannon entropy — but of ordinal patterns, not of amplitudes, so
it captures temporal structure. Result is in `[0, 1]` after normalization.

PE is cheap, robust to monotone amplitude transforms (amplifier gain changes do not move
it), and a good first-pass complexity screen. Use `order = 3–7` for EEG; `order = 5 or 6`
at 256 Hz is common.

### Multiscale entropy (MSE)

Coarse-grain the signal at scales `τ = 1, 2, …, 20` (average non-overlapping windows of
length `τ`) and compute SampEn at each scale. The **curve** is the object of interest, not
a single number.

- White noise: SampEn falls off as `τ` increases (the coarse-graining destroys the
  apparent complexity because white noise has no structure to preserve at longer scales).
- Healthy `1/f`-like signals (typical EEG): SampEn stays relatively high across scales.
- Pathological/over-regular signals: low SampEn at all scales.

MSE is especially useful for EEG because it separates genuine multiscale complexity from
signals that are merely noisy at fine scales.

---

## What Shannon / differential entropy is NOT giving you here

For completeness: if you histogram the EEG amplitudes and compute `H = −Σ p̂ᵢ log p̂ᵢ`,
you get the **differential entropy approximation** of the amplitude distribution. This:

- Ignores temporal order completely (shuffle the signal and get the same number).
- Is sensitive to your bin width — different binning gives different values with no
  principled scale.
- Can be negative (differential entropy can be negative for continuous distributions
  concentrated in a small range).
- Changes if you change units (millivolts vs microvolts) even though the signal is
  physically identical.

For a continuous-valued sensor signal, the coordinate-invariant analogs of Shannon entropy
are **KL divergence** and **mutual information** — but those answer different questions
(distance between distributions; shared information between two variables). They are not
what you want for "how complex is this signal."

---

## Practical code sketch

```python
import numpy as np

def sample_entropy(x, m=2, r=None):
    """
    Compute SampEn(m, r) for time series x.
    r defaults to 0.2 * std(x).
    Returns (SampEn value, A, B, r_used).
    """
    if r is None:
        r = 0.2 * np.std(x, ddof=1)
    N = len(x)

    def count_matches(x, m, r):
        templates = np.array([x[i:i+m] for i in range(N - m)])
        count = 0
        for i in range(len(templates)):
            dists = np.max(np.abs(templates - templates[i]), axis=1)
            # Exclude self-match (i == i)
            dists[i] = r + 1
            count += np.sum(dists <= r)
        return count

    B = count_matches(x, m, r)
    A = count_matches(x, m + 1, r)

    if A == 0:
        return float('inf'), A, B, r
    return -np.log(A / B), A, B, r

# Example usage on your 10-min / 256 Hz EEG channel:
# signal = ...  # shape (153600,)
# sampen, A, B, r = sample_entropy(signal, m=2)
# print(f"SampEn(m=2, r={r:.4f}) = {sampen:.4f}  [A={A}, B={B}]")
```

For production use, prefer the `antropy` library (`pip install antropy`) which implements
SampEn, permutation entropy, and multiscale entropy with validated results and better
performance on long series.

```python
import antropy as ant
import numpy as np

signal = ...  # your EEG array, shape (153600,)

# Sample entropy
se = ant.sample_entropy(signal, order=2, metric='chebyshev')
print(f"SampEn = {se:.4f}  (m=2, r=0.2*SD)")

# Permutation entropy (normalized)
pe = ant.perm_entropy(signal, order=5, normalize=True)
print(f"PermEn = {pe:.4f}  (order=5, normalized)")
```

---

## Summary of recommendations

| Measure | What it tells you | When to use |
|---|---|---|
| **Sample entropy (SampEn)** | Predictability from recent history; the standard for physiological signals | Default; report `m`, `r`, `N` always |
| **Permutation entropy** | Complexity of temporal rank-order patterns; cheap and robust | First-pass screen; insensitive to amplitude rescaling |
| **Multiscale entropy (MSE)** | Whether complexity persists across time scales | When you want to distinguish genuine complexity from noise |
| Shannon entropy of amplitudes | Spread of the amplitude distribution | Not recommended for complexity questions; ignores time |

For a single-number complexity summary of your EEG channel: **SampEn with `m=2`,
`r=0.2×SD`**. For a richer picture: add permutation entropy and an MSE curve.
Report all parameters alongside every number.
