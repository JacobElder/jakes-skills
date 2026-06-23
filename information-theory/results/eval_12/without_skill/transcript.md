# EEG Signal Complexity: Which Entropy to Compute and How to Read It

## The Short Answer

For a 10-minute EEG channel at 256 Hz, **Sample Entropy (SampEn)** is the recommended starting point. It is the most widely validated measure of signal irregularity for continuous physiological time series, it is robust to noise, and its behavior on EEG data is well understood. If you need a multiscale view of complexity, pair it with **Multiscale Entropy (MSE)** across scales 1–20.

---

## Why Not Shannon Entropy?

Shannon entropy measures the distribution of symbol probabilities in a discrete alphabet. Applied raw to a continuous EEG signal, it requires an arbitrary binning or quantization step, and the result reflects amplitude distribution, not temporal unpredictability. You can have a signal with a flat amplitude histogram (high Shannon entropy) that is perfectly periodic — or vice versa. Shannon entropy is the wrong tool unless you have already performed symbolic encoding with a principled method (e.g., permutation encoding).

---

## The Right Measures

### 1. Sample Entropy (SampEn)

**What it measures.** SampEn quantifies how likely it is that sequences of *m* consecutive samples that are similar within tolerance *r* remain similar when one more sample is added. High SampEn → the signal is irregular and hard to predict. Low SampEn → the signal is regular or stereotyped.

**Why not Approximate Entropy (ApEn)?** ApEn is biased because it counts self-matches; SampEn removes self-matches and is less sensitive to record length. For a 10-minute × 256 Hz = 153,600-sample record, this bias is negligible in practice, but SampEn is still preferred and is the field standard.

**Standard parameters for EEG:**
- Embedding dimension *m* = 2
- Tolerance *r* = 0.15 × SD(signal) — computed per-channel, per-epoch
- Sometimes *r* = 0.20 × SD is used; document which you chose

**How to compute it (Python):**
```python
import antropy as ant
import numpy as np

# signal: 1-D numpy array, single channel
samp_en = ant.sample_entropy(signal, order=2, metric='chebyshev')
```

Or using `nolds`:
```python
import nolds
samp_en = nolds.sampen(signal, emb_dim=2, tolerance=0.15 * np.std(signal))
```

**How to read it:**
- Typical EEG SampEn values fall roughly in the range **0.5 – 2.5** (depends on band, state, electrode site).
- Higher SampEn = more complex / irregular = less predictable.
- Waking resting-state EEG is more complex than sleep stage N3; anesthesia dramatically reduces SampEn; epileptic ictal activity collapses SampEn toward zero.
- Compare within-participant or within-condition — absolute values are not universal benchmarks.

---

### 2. Permutation Entropy (PeEn)

**What it measures.** PeEn maps overlapping windows of length *L* to one of *L!* ordinal patterns (ranks of consecutive samples), then computes Shannon entropy over the pattern distribution. It is fast, parameter-light, and robust to amplitude artifacts.

**Standard parameters for EEG:**
- Ordinal order *L* = 3–7; *L* = 5 or 6 is common
- At *L* = 6, there are 720 possible patterns; you want >> 720 samples per epoch — satisfied easily by 10 min at 256 Hz
- Delay *τ* = 1 sample (or set to 1/dominant frequency × sample rate for band-specific analysis)

**How to compute it (Python):**
```python
import antropy as ant
perm_en = ant.perm_entropy(signal, order=5, delay=1, normalize=True)
```

`normalize=True` divides by log(*L!*), giving a value in [0, 1].

**How to read it:**
- Values near 1 → maximally disordered (complex, stochastic-looking).
- Values near 0 → maximally ordered (periodic or constant).
- PeEn is sensitive to changes in signal dynamics at the timescale set by *L × τ* samples. At *L* = 5, *τ* = 1, that is 5/256 ≈ 20 ms — fast dynamics.

---

### 3. Multiscale Entropy (MSE)

**What it measures.** MSE applies coarse-graining at scales *s* = 1, 2, …, 20 (averaging non-overlapping windows of length *s*) and computes SampEn at each scale. The resulting MSE curve reveals complexity across timescales.

**Why this matters for EEG.** EEG complexity is not scale-invariant. Resting wakefulness tends to show higher entropy than sleep across *all* scales, but some pathological states differ from healthy ones only at specific scales.

**Standard parameters:**
- Scales 1–20 (at 256 Hz, scale 20 corresponds to ~78 ms averaging windows)
- SampEn parameters: *m* = 2, *r* = 0.15 × SD of the **original** signal (held fixed across scales)

**How to compute it (Python):**
```python
from EntroPy import multiscale_entropy  # or use antropy/neurokit2

import neurokit2 as nk
mse = nk.entropy_multiscale(signal, dimension=2, tolerance=0.15*np.std(signal),
                             scale=20, method='SampEn')
```

**How to read it:**
- Plot SampEn (y-axis) vs. scale (x-axis).
- A healthy, complex signal maintains moderate-to-high entropy across scales.
- A pathological or over-regular signal may show high entropy only at short scales (noise-like at fine resolution but simple at longer timescales) — the MSE curve drops steeply.
- Summarize with the **area under the MSE curve** (often called the Complexity Index, CI) for a single-number comparison across participants or conditions.

---

## Practical Checklist for Your 10-Minute Recording

| Step | Action |
|------|--------|
| 1 | Preprocess: bandpass filter (0.5–45 Hz typical), re-reference, remove eye/muscle artifacts |
| 2 | Epoch or use the full 10-min record (full record is fine for SampEn; epoch to ~2–4 min if comparing conditions) |
| 3 | Set *r* = 0.15 × SD per channel after artifact removal |
| 4 | Compute SampEn (*m*=2) as your primary metric |
| 5 | Optionally compute PeEn (*L*=5) and MSE (scales 1–20) for a fuller picture |
| 6 | Report parameter choices explicitly — entropy values are not comparable across studies unless parameters match |

---

## Common Pitfalls

**Artifact contamination inflates entropy.** Muscle artifact (EMG) looks like high-frequency noise, which appears complex. Clean your data before computing entropy, not after.

**Stationarity.** These measures assume approximate stationarity within the analysis window. A 10-minute resting-state recording at a single condition is usually acceptable. Avoid mixing task conditions within a single entropy estimate.

**Epoch length and *r* tradeoff.** Shorter epochs → fewer template matches → noisier SampEn estimates. For very short epochs (< 30 s), consider reducing *m* to 1 or use PeEn instead.

**Multiple channels.** If you have a full montage, compute per-channel and examine topographic patterns (e.g., occipital vs. frontal entropy differences at rest). Or compute a global complexity index averaged across channels.

---

## Summary

| Measure | Best for | Key parameter | Output range | Interpretation |
|---------|----------|---------------|--------------|----------------|
| SampEn | Single-timescale complexity | *m*=2, *r*=0.15×SD | ~0 – 3+ | Higher = more complex |
| PeEn (normalized) | Fast, robust ordinal complexity | *L*=5, *τ*=1 | 0 – 1 | Higher = more disordered |
| MSE | Multiscale complexity profile | Scales 1–20 | Curve + CI | Maintained entropy across scales = healthy complexity |

For a single number to report in a paper: **SampEn** with *m*=2, *r*=0.15×SD.  
For a richer characterization: **MSE curve + Complexity Index**.  
For speed and robustness to amplitude artifacts: **normalized PeEn** with *L*=5.
