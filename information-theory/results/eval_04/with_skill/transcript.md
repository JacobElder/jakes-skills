# Cross-Entropy Loss, NLL, and KL Divergence: They Are One Fact

The short answer: these are not three separate concepts. They are three names for the same objective, derived from a single identity. Once you see the identity, the confusion dissolves.

## The identity

```
H(p, q) = H(p) + D_KL(p ‖ q)
```

Where:
- `H(p, q) = −Σ p(x) log q(x)` is **cross-entropy** — the expected log-loss under the true distribution `p` when you use model `q`
- `H(p) = −Σ p(x) log p(x)` is the **Shannon entropy** of the true distribution — a constant that does not depend on your model `q`
- `D_KL(p ‖ q) = Σ p(x) log[p(x)/q(x)]` is the **KL divergence** from `q` to `p` — the extra bits you pay for using the wrong model

Because `H(p)` is a constant with respect to `q`, **minimizing cross-entropy over `q` is exactly minimizing KL divergence from your model to the data**. And when `p` is the empirical distribution of your training set (each data point equally weighted), that minimization is precisely **maximum likelihood estimation**:

```
argmin_q H(p̂, q)  =  argmin_q D_KL(p̂ ‖ q)  =  argmax_q Σᵢ log q(xᵢ)  =  MLE
```

So the chain is:

> Cross-entropy loss = negative log-likelihood = minimizing KL(empirical ‖ model)

These three phrases describe the same computation. The only surface differences are:

| Name | Difference |
|---|---|
| Cross-entropy loss | Averages `−log q(xᵢ)` over examples; log base sets units (bits vs nats) |
| Negative log-likelihood (NLL) | Usually sums rather than averages; nats by convention |
| Minimizing KL | Frames it as divergence minimization; the `H(p)` term vanishes since it's a constant |

Switching between bits (log₂) and nats (ln) rescales by `ln 2` ≈ 0.693 — it changes the number but not the argmin. If you see a loss value in bits, multiply by `ln 2` to convert to nats.

## What each framing emphasizes

The same objective has different framing depending on context:

**NLL / MLE framing** (statistics): You're finding parameters that maximize the probability of observing your data. Each data point contributes `log q(xᵢ)`.

**Cross-entropy framing** (machine learning): You're measuring how many bits your model needs to encode each example under the true label distribution. In classification, `p` is a one-hot distribution over classes, so `H(p, q) = −log q(\text{true class})` per example — the familiar per-example cross-entropy loss.

**KL framing** (information theory): You're measuring how much probability mass your model is misallocating relative to the data. The KL direction here is `D_KL(p̂ ‖ q)` — forward KL, where the expectation is under the empirical data distribution. This is the **mass-covering** direction: the model is penalized hard for putting near-zero probability anywhere the data puts mass.

## The KL direction matters — don't ignore it

The identity connects to **forward KL** specifically: `D_KL(p ‖ q)` where `p` is the data and `q` is your model. This means standard MLE/cross-entropy training is inherently mass-covering: your model is strongly penalized for assigning low probability to any region where the data appears.

This is different from **reverse KL**, `D_KL(q ‖ p)`, which is what standard variational inference minimizes (via the ELBO). Reverse KL is mode-seeking — it allows `q` to ignore regions of `p` as long as `q` doesn't put mass there either. The consequence: VI posteriors from mean-field approximations are systematically **too narrow** and **overconfident**, because reverse KL never penalizes the approximation for missing modes.

When someone says "minimize the KL" without specifying direction, the answer is undefined. The direction is a modeling decision, not a detail.

## A concrete example

Suppose `p` is the true class distribution (one-hot) for a single example: class 2 out of 3.

```
p = [0, 1, 0]
q = [0.1, 0.7, 0.2]   ← model's predicted probabilities
```

Cross-entropy: `H(p, q) = −(0·log 0.1 + 1·log 0.7 + 0·log 0.2) = −log 0.7 ≈ 0.357 nats`

Shannon entropy of `p`: `H(p) = 0` (one-hot is perfectly certain)

KL divergence: `D_KL(p ‖ q) = 0.357 − 0 = 0.357 nats`

So cross-entropy loss = NLL = KL divergence here, exactly. The cross-entropy and KL are identical whenever `p` is a one-hot (zero entropy), which is the standard classification case.

## Perplexity: same thing, exponentiated

Perplexity = `exp(cross-entropy)` in the matching base. If a language model has average NLL of 2.3 nats/token, its perplexity is `exp(2.3) ≈ 10`. If you work in bits, perplexity = `2^(bits/token)`. Perplexity is not a separate concept — it is cross-entropy in exponentiated form, chosen because exponentiating converts from "log space" to "effective vocabulary size the model is uncertain over."

## Summary

There is one underlying objective. Cross-entropy loss, NLL, and KL divergence (forward, to the data) are the same function of your model parameters `q`. The only decision is:

1. **Which KL direction?** Forward KL (`p ‖ q`, mass-covering) = MLE = cross-entropy loss. Reverse KL (`q ‖ p`, mode-seeking) = variational inference. Never omit the direction.
2. **Bits or nats?** Log₂ gives bits; ln gives nats. Rescales by `ln 2`, does not change the argmin.
3. **Sum or average?** NLL typically sums over examples; cross-entropy loss typically averages. Same argmin, different scales.

Once the identity `H(p, q) = H(p) + D_KL(p ‖ q)` is internalized, these three names stop feeling like separate concepts — they're three windows into the same object.
