# Is your MI of 0.42 nats a real relationship?

Short answer: **you don't know yet.** The number you got from sklearn's `mutual_info_score` is almost certainly inflated by estimation bias, and until you run a permutation null you cannot say whether 0.42 nats is a real association or mostly noise dressed up as signal.

Here is why, and exactly what to do.

---

## The bias problem with your setup

Plug-in MI (which is what sklearn's `mutual_info_score` computes under the hood) is **biased upward** by:

```
bias ≈ (K_X − 1)(K_Y − 1) / (2N)
```

For your data:
- K_X = 12 (device_type)
- K_Y = 8 (support_outcome)
- N = 150

```
bias ≈ (12 − 1)(8 − 1) / (2 × 150)
     = (11 × 7) / 300
     = 77 / 300
     ≈ 0.257 nats
```

Your observed MI is 0.42 nats. Your expected bias floor is roughly **0.26 nats** — more than half your observed value. That is not a rounding error; it is the estimator lying to you about how much information exists. Two independent random categorical columns with these cardinalities and this sample size would show a plug-in MI around 0.26 nats on average purely from counting noise.

The fact that 0.42 > 0.26 is *some* evidence of real structure, but the gap (≈ 0.16 nats) is what you are actually measuring, and you still need uncertainty bounds on that gap.

---

## The one test you must run: a permutation null

Shuffle the `support_outcome` column relative to `device_type` (breaking any real relationship), recompute MI, and repeat ≥ 200 times. This directly empiricalizes the bias floor for your specific data rather than relying on the asymptotic formula above.

```python
import numpy as np
from sklearn.metrics import mutual_info_score

# your real MI
observed_mi = mutual_info_score(df["device_type"], df["support_outcome"])

# permutation null
rng = np.random.default_rng(42)
null_mis = [
    mutual_info_score(
        df["device_type"],
        rng.permutation(df["support_outcome"].values)
    )
    for _ in range(500)
]

null_mean = np.mean(null_mis)
null_std  = np.std(null_mis)
p_value   = np.mean(np.array(null_mis) >= observed_mi)

print(f"Observed MI:   {observed_mi:.4f} nats")
print(f"Null mean:     {null_mean:.4f} nats  (≈ bias floor)")
print(f"Null std:      {null_std:.4f} nats")
print(f"Gap (signal):  {observed_mi - null_mean:.4f} nats")
print(f"p-value:       {p_value:.4f}")
```

**Interpreting the output:**
- If `observed_mi` sits well inside the null distribution (p ≈ 0.2 or higher), you have no evidence of a real relationship regardless of the raw nats value.
- If `observed_mi` is clearly above the null (p < 0.05, gap ≥ 2–3 null standard deviations), the relationship is real — but the *magnitude of signal* is `observed_mi − null_mean`, not `observed_mi`.

---

## How undersampled are you?

The rule of thumb from estimation theory: you want N/(K_X × K_Y) ≥ 10 per joint cell on average. Your joint table has 12 × 8 = 96 cells. With 150 rows you average **1.6 rows per cell** — you are substantially undersampled.

This does not mean you cannot learn anything. It means:
1. The plug-in estimator is heavily biased (confirmed above).
2. Many cells will be empty or have counts of 1–2, so the bias formula is itself approximate; the true bias could be larger.
3. A permutation test is not optional — it is the only honest way to assess significance in this regime.

---

## Getting a less-biased point estimate

If the permutation test shows signal, replace `mutual_info_score` with a Miller–Madow-corrected estimate:

```python
from scipy.stats import contingency

# Build the contingency table
ct = pd.crosstab(df["device_type"], df["support_outcome"])
counts = ct.values

N = counts.sum()
K_X, K_Y = counts.shape

# Marginals and joint for plug-in entropy
p_xy = counts / N
p_x  = p_xy.sum(axis=1, keepdims=True)
p_y  = p_xy.sum(axis=0, keepdims=True)

# Plug-in entropies (nats), ignoring zeros
def plugin_H(p):
    p = p[p > 0]
    return -np.sum(p * np.log(p))

H_X  = plugin_H(p_x.flatten())
H_Y  = plugin_H(p_y.flatten())
H_XY = plugin_H(p_xy.flatten())

# Miller–Madow corrections (subtract estimated bias)
K_x_obs = np.sum(p_x.flatten() > 0)
K_y_obs = np.sum(p_y.flatten() > 0)
K_xy_obs = np.sum(p_xy.flatten() > 0)

H_X_mm  = H_X  + (K_x_obs  - 1) / (2 * N)
H_Y_mm  = H_Y  + (K_y_obs  - 1) / (2 * N)
H_XY_mm = H_XY + (K_xy_obs - 1) / (2 * N)

MI_mm = H_X_mm + H_Y_mm - H_XY_mm
print(f"Miller–Madow MI: {MI_mm:.4f} nats")
```

This corrects each entropy term separately (correcting only the marginals and not the joint, or vice versa, reintroduces bias — you must correct all three). Even so, Miller–Madow only removes the leading-order bias term; given how undersampled your table is, treat this as an improved estimate rather than a definitive one.

---

## Putting the magnitude in context

Raw nats are hard to interpret in isolation. Two normalizations that help:

**Normalized MI (0–1 scale):**
```python
NMI = MI / np.sqrt(H_X * H_Y)  # or use min(H_X, H_Y) in denominator
```
An NMI close to 1 means the two variables are nearly determined by each other; close to 0 means near-independence.

**Fano's inequality — what MI implies for classification accuracy:**

`H(Y|X) = H(Y) − I(X;Y)`. If `H(Y)` is, say, around log(8) ≈ 2.08 nats (maximum entropy for 8 uniform classes) and `I(X;Y) ≈ 0.16 nats` (the signal gap after bias removal), then `H(Y|X) ≈ 1.92 nats`, implying the best possible classifier predicting `support_outcome` from `device_type` still faces nearly-maximum residual uncertainty. That is a useful reality check before building a model on this feature alone.

---

## Summary

| Question | Answer |
|---|---|
| Is 0.42 nats a lot? | Probably not — ~0.26 nats of it is expected bias from estimation noise at your sample size. |
| How much signal is likely real? | Roughly 0.42 − (bias floor from permutation null) — run the null to find out. |
| Is the result statistically significant? | Unknown until you run the permutation test; do not skip it. |
| What estimator should you use? | Miller–Madow-corrected MI (at minimum); report the permutation null alongside it. |
| Is 150 rows enough? | You have ~1.6 rows per joint cell on average — you are undersampled; treat the magnitude as approximate. |

The key move is this: **run the permutation null, report `observed MI − null mean` as your signal estimate, and give a p-value.** A bare MI of 0.42 nats without that context is not an answer to whether the relationship is real.
