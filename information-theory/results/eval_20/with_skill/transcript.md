# Fano's Inequality and the Best Achievable Error Rate

## Setup

- **K = 10 classes** (labels Y ∈ {1, …, 10})
- **I(X; Y) = 1.5 bits** (honest estimate of mutual information between features and label)
- **H(Y) = log₂(10) ≈ 3.3219 bits** (uniform label entropy — maximum over K classes)

All quantities are in bits throughout.

---

## Step 1: Compute the Residual Uncertainty H(Y | X)

The key identity connecting mutual information to prediction difficulty is:

```
I(X; Y) = H(Y) − H(Y | X)
```

Rearranging:

```
H(Y | X) = H(Y) − I(X; Y)
           = log₂(10) − 1.5
           = 3.3219 − 1.5
           = 1.8219 bits
```

**Interpretation.** H(Y | X) = 1.8219 bits is the irreducible remaining uncertainty about the label *after* observing your features. No matter how expressive your model is, you cannot reduce the label's uncertainty below this value. The data-processing inequality (DPI) guarantees this: any function of X — a neural network, gradient boosting, a learned embedding — is a downstream processing step that cannot *create* information. So 1.8219 bits of residual uncertainty is the hard ceiling set by the data itself.

---

## Step 2: State Fano's Inequality

For any estimator Ŷ = f(X) of a K-class label Y, with error probability Pₑ = P(Ŷ ≠ Y):

```
H(Y | X) ≤ H(Pₑ) + Pₑ · log₂(K − 1)
```

where H(Pₑ) = −Pₑ log₂(Pₑ) − (1 − Pₑ) log₂(1 − Pₑ) is the binary entropy of the error probability.

This is an *upper bound on the left side*, which means it becomes a **lower bound on Pₑ** once we know H(Y | X): the error rate cannot be so low that the right-hand side drops below H(Y | X). Any claimed model performance with Pₑ lower than the Fano-implied floor is either leakage, a broken evaluation, or an error.

With K = 10:

```
1.8219 ≤ H(Pₑ) + Pₑ · log₂(9)
```

---

## Step 3: Quick Lower Bound (Napkin Form)

The reference gives a weak but instantly computable form:

```
Pₑ ≥ (H(Y | X) − 1) / log₂(K)
```

Plugging in:

```
Pₑ ≥ (1.8219 − 1) / log₂(10)
   = 0.8219 / 3.3219
   ≈ 0.247
```

So the quick napkin bound says: **no classifier can achieve error below ~24.7%** given these features.

This form drops the H(Pₑ) term (which is ≤ 1 bit) and uses log₂(K) rather than log₂(K−1), making it slightly loose but trivial to evaluate mentally.

---

## Step 4: Solve the Tight Fano Bound

The exact Fano bound requires solving the equality case numerically. We solve:

```
H(Pₑ) + Pₑ · log₂(9) = 1.8219
```

Expand H(Pₑ):

```
−Pₑ log₂(Pₑ) − (1 − Pₑ) log₂(1 − Pₑ) + Pₑ · log₂(9) = 1.8219
```

The right-hand side as a function of Pₑ is unimodal and monotonically increasing over [0, 1 − 1/K], so there is a unique Pₑ satisfying the equality. Evaluating numerically (bisection, or reading from a table):

| Pₑ   | H(Pₑ)  | Pₑ · log₂(9) | Sum    |
|------|--------|--------------|--------|
| 0.25 | 0.8113 | 0.7925       | 1.6038 |
| 0.30 | 0.8813 | 0.9510       | 1.8323 |
| 0.29 | 0.8727 | 0.9193       | 1.7920 |
| 0.295| 0.8770 | 0.9352       | 1.8122 |
| 0.298| 0.8796 | 0.9447       | 1.8243 |
| 0.297| 0.8788 | 0.9415       | 1.8203 |

The equality is satisfied at approximately **Pₑ ≈ 0.298**, confirming the tight Fano floor is just under 30%.

---

## Step 5: Interpretation and What This Means Practically

### What it says

| Bound          | Value   | Interpretation                                      |
|----------------|---------|-----------------------------------------------------|
| Weak Fano floor| ≥ 24.7% | Quick check; any model below this is suspect        |
| Tight Fano floor| ≥ 29.8% | Hard limit; no classifier on these features can beat this |
| Accuracy ceiling| ≤ 70.2%| Best achievable top-1 accuracy, ever, on this data  |

### What it does not say

- It does not say a *specific* model will achieve 70.2% accuracy. Most models will do worse, because the bound is achieved only by the Bayes-optimal classifier.
- It does not penalize model complexity or finite data. These are population-level bounds on the data generating process, not finite-sample guarantees.

### Practical diagnostic use

**Before spending compute on architectures:** If a baseline model is already near 70% accuracy, you are close to the ceiling and architecture search will yield diminishing returns. Invest in features or data.

**Too-good-to-be-true detector:** If a model reports 85% accuracy on this problem, with H(Y|X) = 1.8219 bits, something is wrong — the Fano floor is inviolable. Likely causes: label leakage, test-set contamination, or a broken evaluation (e.g., train-test overlap).

**Estimation caveat.** The 1.5-bit MI figure itself was described as an "honest estimate." If that estimate came from a plug-in (histogram) estimator on finite data, it is biased *upward*, which means the true I(X; Y) could be less than 1.5 bits, making H(Y | X) *larger* and Pₑ *higher* than computed here. A biased-up MI gives an over-optimistic (too-low) Fano floor — always note this direction when reporting bounds derived from sample MI.

---

## Summary

```
H(Y | X) = log₂(10) − 1.5 = 1.8219 bits   [residual uncertainty]

Fano: H(Y|X) ≤ H(Pₑ) + Pₑ · log₂(K−1)

Weak floor:  Pₑ ≥ (1.8219 − 1) / 3.3219 ≈ 0.247   (~24.7%)
Tight floor: Pₑ ≈ 0.298                              (~29.8%)

Best achievable top-1 accuracy: ~70.2%
```

No classifier, regardless of architecture or training procedure, can achieve error below ≈29.8% on features carrying I(X; Y) = 1.5 bits about a 10-class label with H(Y) = log₂(10) bits.
