# Cross-Entropy Loss, Negative Log-Likelihood, and KL Divergence

They feel like three separate concepts because you encountered them in three separate contexts — classification tutorials, probabilistic modeling, and information theory papers. But they are the same object viewed from different angles. Once you see the algebraic chain linking them, the confusion dissolves.

---

## Start with entropy

Before the three concepts, you need entropy. Shannon entropy of a distribution P is:

```
H(P) = -∑ P(x) log P(x)
```

It measures the average surprise (in bits or nats) of drawing from P. A peaked distribution has low entropy; a flat one has high entropy.

---

## KL divergence

KL divergence measures how much information is lost when you use an approximate distribution Q to represent the true distribution P:

```
KL(P || Q) = ∑ P(x) log [P(x) / Q(x)]
           = ∑ P(x) log P(x) - ∑ P(x) log Q(x)
           = -H(P) + H(P, Q)
```

where H(P, Q) is the **cross-entropy**:

```
H(P, Q) = -∑ P(x) log Q(x)
```

So:

```
KL(P || Q) = H(P, Q) - H(P)
```

KL divergence = cross-entropy minus the entropy of the true distribution.

---

## Cross-entropy

Cross-entropy H(P, Q) measures the average number of bits needed to encode samples from P using a code optimized for Q. When Q = P, this equals H(P) — you can't do better. When Q ≠ P, the cross-entropy is always higher by exactly KL(P || Q).

In machine learning, P is the empirical data distribution (the labels), and Q is the model's predicted distribution. Minimizing cross-entropy loss over the training set is therefore equivalent to minimizing KL(P || Q), because H(P) is constant with respect to the model parameters — it's a property of the data, not the model:

```
argmin_θ H(P, Q_θ) = argmin_θ KL(P || Q_θ)
```

This is why "minimizing cross-entropy" and "minimizing KL divergence from data to model" are interchangeable objectives.

---

## Negative log-likelihood

Now take a single training example with true label y and model-predicted probability Q(y). The log-likelihood contribution is:

```
log Q(y)
```

Averaged (or summed) over the dataset with empirical distribution P:

```
E_P[log Q(y)] = ∑ P(y) log Q(y) = -H(P, Q)
```

So **negative log-likelihood = cross-entropy** (up to a sign and a constant factor depending on whether you sum or average).

When you write the NLL loss in PyTorch or TensorFlow as `-log(model_output[true_class])`, you are computing exactly one term of the cross-entropy sum for that example. Average it over the batch and you have the batch cross-entropy.

---

## The complete chain

```
NLL = -∑ P(x) log Q(x)        (definition of NLL / cross-entropy)
    = H(P, Q)                   (cross-entropy notation)
    = H(P) + KL(P || Q)         (decomposition into entropy + KL)
```

Minimizing NLL over model parameters θ:

- H(P) is fixed (it's the data entropy), so it doesn't affect the gradient.
- You are therefore directly minimizing KL(P || Q_θ).
- This is maximum likelihood estimation (MLE) — it is equivalent to KL minimization.

---

## Why this matters in practice

**When P is one-hot (classification):** H(P) = 0, so cross-entropy and KL divergence are numerically identical. The "entropy" term vanishes because a deterministic label has zero uncertainty.

**When P is a soft distribution (distillation, label smoothing):** H(P) > 0. Cross-entropy and KL divergence differ by a constant, but the minimizer is still the same. If you are comparing losses across different P distributions (e.g., different teachers in knowledge distillation), you need to track KL, not raw cross-entropy, because H(P) changes.

**Variational inference (VAE, etc.):** The ELBO loss contains a KL term explicitly. That KL is between two distributions neither of which is the empirical data distribution — it's between the approximate posterior and the prior. This is the same formula but a different application; don't confuse it with the training-loss KL above.

**Numerical stability:** In code, `log Q(x)` can blow up as Q(x) → 0. `torch.nn.CrossEntropyLoss` applies `log_softmax` rather than `log(softmax(...))` to avoid this. The math is the same; the implementation is numerically better.

---

## One-sentence summary of each

| Concept | What it computes |
|---|---|
| Cross-entropy H(P, Q) | Expected bits needed to encode P-samples with a Q-code |
| Negative log-likelihood | The same quantity, expressed as a sum over training data |
| KL divergence KL(P ∥ Q) | Cross-entropy minus the irreducible entropy of P |

They are not three concepts. They are one concept — the mismatch between a true distribution and a model — described in three notational dialects.
