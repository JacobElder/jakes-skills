# Is 0.42 nats a Real Relationship?

Short answer: the raw number alone doesn't tell you. You need to normalize it and account for the fact that with small N, mutual information estimates are biased upward by chance.

---

## What 0.42 nats actually means

`sklearn.metrics.mutual_info_score` returns mutual information in nats (natural log base). The number is on an absolute scale that depends on how many categories each variable has — so 0.42 nats is not interpretable without context.

For reference: if two variables were perfectly dependent, the maximum possible MI equals the entropy of the less-entropic variable. If `support_outcome` has 8 equally-probable categories, its entropy is ln(8) ≈ 2.08 nats. If `device_type` has 12 equally-probable categories, its entropy is ln(12) ≈ 2.48 nats. So the ceiling for MI in your case is roughly 2.08 nats.

0.42 / 2.08 ≈ **0.20 normalized** — about 20% of the maximum possible dependence. That's meaningful, but not strong.

---

## The small-N problem: positive bias in MI estimates

With only 150 rows, 12 × 8 = 96 cells in the contingency table, and many cells will be empty or near-zero. Mutual information is estimated from cell frequencies, and the plug-in estimator is **positively biased** when counts are sparse. Even purely independent variables will produce a non-zero MI estimate just from sampling noise.

The bias scales roughly as:

```
Bias ≈ (R - 1)(C - 1) / (2 * N * ln(2))
```

where R = number of rows (12), C = number of columns (8), N = 150. Plugging in:

```
Bias ≈ (11)(7) / (2 * 150) ≈ 77 / 300 ≈ 0.257 nats
```

That is a rough approximation (the exact formula assumes uniform marginals and uses natural logs already, so adjust accordingly), but the order of magnitude is the point: **with 150 rows and 96 cells, a sizable chunk of your 0.42 nats could be noise-induced bias**.

---

## What you should actually do

### 1. Compute Normalized Mutual Information (NMI)

```python
from sklearn.metrics import normalized_mutual_info_score

nmi = normalized_mutual_info_score(df['device_type'], df['support_outcome'])
print(nmi)  # 0 = independent, 1 = perfectly dependent
```

This normalizes by the geometric or arithmetic mean of the two entropies, giving a [0, 1] scale. A value above ~0.15–0.20 with your sample size is worth investigating.

### 2. Permutation test to assess significance

The cleanest way to know whether 0.42 nats exceeds chance:

```python
import numpy as np
from sklearn.metrics import mutual_info_score

observed_mi = mutual_info_score(df['device_type'], df['support_outcome'])

n_permutations = 1000
null_mis = []
rng = np.random.default_rng(42)

for _ in range(n_permutations):
    shuffled = rng.permutation(df['support_outcome'].values)
    null_mis.append(mutual_info_score(df['device_type'], shuffled))

p_value = np.mean(np.array(null_mis) >= observed_mi)
print(f"Observed MI: {observed_mi:.4f} nats")
print(f"Null mean: {np.mean(null_mis):.4f} nats")
print(f"p-value: {p_value:.4f}")
```

If your 0.42 nats is well above the null distribution (p < 0.05), the relationship is real. If the null distribution peaks around 0.3–0.35 nats due to bias, your signal is much weaker than it looks.

### 3. Chi-squared test as a sanity check

For two categorical variables, the classical test is chi-squared:

```python
from scipy.stats import chi2_contingency
import pandas as pd

ct = pd.crosstab(df['device_type'], df['support_outcome'])
chi2, p, dof, expected = chi2_contingency(ct)
print(f"chi2={chi2:.2f}, df={dof}, p={p:.4f}")
```

With 96 cells and only 150 rows, many expected counts will be < 5, which violates chi-squared assumptions — but it's still a useful corroborating signal. You can also use Cramér's V for a normalized effect size:

```python
import numpy as np
n = ct.values.sum()
cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
print(f"Cramér's V = {cramers_v:.3f}")
```

Cramér's V > 0.1 is considered a weak effect, > 0.3 moderate, > 0.5 strong (for larger tables these thresholds are lower).

---

## Summary

| Question | Answer |
|---|---|
| Is 0.42 nats inherently meaningful? | No — it's on an unbounded scale; normalize it first |
| What's the NMI equivalent? | Roughly 0.20 (20% of maximum), a modest association |
| Is small-N bias a concern? | Yes — with 96 cells and 150 rows, estimated bias alone could be ~0.25 nats |
| How to confirm the relationship is real? | Permutation test; if observed MI >> null distribution, it's real |
| Quick classical check? | Chi-squared + Cramér's V |

The most likely honest interpretation: there is **probably some real association** between device type and support outcome, but 0.42 nats inflates the signal due to sparse-cell bias. Run the permutation test — if your observed value sits in the top 5% of the null, you have a defensible claim.
