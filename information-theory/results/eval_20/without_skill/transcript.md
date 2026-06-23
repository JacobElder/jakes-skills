# Best Achievable Error Rate from Mutual Information

## Setup

- **Classes:** K = 10
- **Label entropy:** H(Y) = log₂(10) ≈ 3.322 bits
- **Mutual information:** I(X; Y) = 1.5 bits
- **Conditional entropy (equivocation):** H(Y | X) = H(Y) − I(X; Y)

## Step 1: Compute the Conditional Entropy

The conditional entropy tells us how much uncertainty about Y remains after observing the features X:

```
H(Y | X) = H(Y) − I(X; Y)
          = log₂(10) − 1.5
          ≈ 3.3219 − 1.5
          = 1.8219 bits
```

This is the irreducible uncertainty left in the label even with perfect use of the features.

## Step 2: Apply Fano's Inequality

Fano's inequality gives a lower bound on the probability of error P_e for any classifier (deterministic or stochastic) operating on these features:

```
H(Y | X) ≤ H(P_e) + P_e · log₂(K − 1)
```

where:
- H(P_e) = −P_e log₂(P_e) − (1 − P_e) log₂(1 − P_e) is the binary entropy of the error probability
- K = 10 is the number of classes
- K − 1 = 9

Rearranged as a bound:

```
P_e ≥ (H(Y | X) − H(P_e)) / log₂(K − 1)
```

But since H(P_e) ≤ 1 bit, the weakest (easiest to compute) form of Fano's inequality drops the binary entropy term:

```
H(Y | X) ≤ H(P_e) + P_e · log₂(K − 1)
         ≤ 1 + P_e · log₂(9)
```

Solving for P_e:

```
P_e ≥ (H(Y | X) − 1) / log₂(9)
    = (1.8219 − 1) / log₂(9)
    = 0.8219 / 3.1699
    ≈ 0.259
```

So **P_e ≥ 0.259** — no classifier can achieve error below roughly 26%.

## Step 3: Tighten the Bound (Numerical Solve)

The loosened bound above uses H(P_e) ≤ 1. For a tighter estimate, solve the full inequality numerically. We need the largest P_e satisfying:

```
H(P_e) + P_e · log₂(9) = H(Y | X) = 1.8219
```

Try P_e = 0.30:
```
H(0.30) + 0.30 · log₂(9)
= (−0.30·log₂(0.30) − 0.70·log₂(0.70)) + 0.30 · 3.1699
= (0.5211 + 0.3602) + 0.9510
= 0.8813 + 0.9510
= 1.8323   ← slightly above 1.8219
```

Try P_e = 0.295:
```
H(0.295) + 0.295 · 3.1699
= (−0.295·log₂(0.295) − 0.705·log₂(0.705)) + 0.9351
= (0.5283 + 0.3545) + 0.9351
= 0.8828 + 0.9351
= 1.8179   ← slightly below 1.8219
```

Interpolating linearly between P_e = 0.295 and 0.300:
```
target = 1.8219
at 0.295: 1.8179, at 0.300: 1.8323
gap = 1.8323 − 1.8179 = 0.0144
need = 1.8219 − 1.8179 = 0.0040
fraction = 0.0040 / 0.0144 ≈ 0.278
P_e ≈ 0.295 + 0.278 · 0.005 ≈ 0.2964
```

The tightest Fano bound places **P_e ≥ ≈ 0.296** (roughly 29.6%).

## Summary of Results

| Quantity | Value |
|---|---|
| H(Y) | log₂(10) ≈ 3.322 bits |
| I(X; Y) | 1.5 bits |
| H(Y \| X) | ≈ 1.822 bits |
| Fano lower bound on P_e (loose) | ≥ 25.9% |
| Fano lower bound on P_e (tight) | ≥ 29.6% |

## What This Means

With only 1.5 bits of mutual information between features and a 10-class label, the features resolve less than half of the label's 3.32-bit entropy. Fano's inequality guarantees that **no predictor — regardless of model complexity or training data size — can achieve an error rate below roughly 30%**. This is a property of the data-generating distribution, not of any particular model.

A few interpretive notes:

1. **Fano is a lower bound, not an achievable rate.** The true Bayes error could be higher than 30% if the remaining 1.822 bits of conditional entropy are spread adversarially across classes. Fano guarantees you cannot do better; it does not guarantee you can achieve 30%.

2. **Mutual information of 1.5 bits out of 3.32 bits means the features explain ~45% of the label uncertainty** in an information-theoretic sense. That is a moderate signal — enough to predict with meaningful accuracy, but with substantial irreducible error.

3. **Implication for modeling:** If a model is reporting error rates near or below 30% on held-out data, that is consistent with the bound. If it claims error near 0%, that violates the information-theoretic constraint and suggests overfitting, data leakage, or an incorrect MI estimate.
