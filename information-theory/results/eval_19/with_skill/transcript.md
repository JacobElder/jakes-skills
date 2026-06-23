# Rate–Distortion for a Gaussian Source: How Many Bits to Hit a Target MSE?

## The setup

Source: `X ~ N(0, σ²)` with `σ² = 4`.  
Distortion measure: mean-squared error (MSE), `d(x, x̂) = (x − x̂)²`.  
Question: what is the minimum rate `R` (bits/sample) to achieve average distortion `≤ D`?

---

## The rate–distortion function for a Gaussian source

For a zero-mean Gaussian source under squared-error distortion, the rate–distortion function has a
closed form:

```
R(D) = ½ log₂(σ²/D)    for 0 ≤ D ≤ σ²
R(D) = 0               for D > σ²
```

This is the **minimum** bits per sample achievable at distortion `D` — no code, no matter how
cleverly designed, can do better. It follows from the general definition

```
R(D) = min_{ p(x̂|x) : E[d(X,X̂)] ≤ D }  I(X ; X̂)
```

where the Gaussian achieves the minimum because it is the maximum-entropy distribution for a fixed
variance: the hardest source to compress at a given distortion level.

---

## Case 1: D = 1, σ² = 4

```
R(1) = ½ log₂(4/1)
     = ½ log₂(4)
     = ½ × 2
     = 1.0 bit/sample
```

**Interpretation.** Starting from a source with variance 4, you need exactly **1 bit per sample**
to reconstruct with average squared error no greater than 1. At 1 bit/sample, the optimal
encoder effectively specifies which of two equiprobable half-spaces the sample falls into; the
Gaussian geometry makes this exact.

---

## Case 2: D = 0.25, σ² = 4

```
R(0.25) = ½ log₂(4/0.25)
        = ½ log₂(16)
        = ½ × 4
        = 2.0 bits/sample
```

**Interpretation.** Tightening the fidelity target from MSE = 1 down to MSE = 0.25 — a 4× reduction
in allowed error — requires **2 bits/sample**, double the previous figure.

---

## The general rule: halving MSE costs exactly ½ bit per sample

From the closed form:

```
R(D) = ½ log₂(σ²/D)
```

If you replace `D` with `D/2` (halve the allowed distortion):

```
R(D/2) = ½ log₂(σ²/(D/2))
        = ½ log₂(2 · σ²/D)
        = ½ [log₂(2) + log₂(σ²/D)]
        = ½ · 1 + ½ log₂(σ²/D)
        = R(D) + ½
```

So **every halving of the MSE budget costs exactly ½ bit per sample**, regardless of the absolute
level of `D` or `σ²`. This is the Gaussian rate–distortion rule of thumb: each additional bit of
rate reduces the minimum achievable MSE by a factor of 4 (two halvings → 1 bit).

Equivalently, doubling the rate (adding 1 bit/sample) reduces MSE by a factor of 4:

```
R → R + 1  ⟹  D → D / 4
```

---

## Summary table

| D (MSE) | σ²/D | log₂(σ²/D) | R(D) = ½ log₂(σ²/D) |
|---------|------|------------|----------------------|
| 4.0     | 1    | 0          | 0.0 bits/sample      |
| 2.0     | 2    | 1          | 0.5 bits/sample      |
| 1.0     | 4    | 2          | **1.0 bits/sample**  |
| 0.5     | 8    | 3          | 1.5 bits/sample      |
| 0.25    | 16   | 4          | **2.0 bits/sample**  |
| 0.125   | 32   | 5          | 2.5 bits/sample      |

At `D = σ² = 4`, the rate drops to 0: you can "reproduce" the source by always outputting its mean
(zero) and the average squared error equals the variance — no bits needed. That's the upper
boundary of the non-trivial regime.

---

## What this means in practice

The Gaussian R(D) curve is a **lower bound** on any real system:

- **Scalar quantization** (e.g., rounding to `b`-bit fixed-point) achieves roughly
  `R ≈ b − ½ log₂(2πe/12)` bits at MSE ≈ `σ²/2^{2b}` — a constant gap above the R(D) curve
  (~1.53 bits at high rates due to the granularity gain of uniform vs. Gaussian-optimal quantization).
- **Vector quantization** over long blocks approaches the R(D) bound asymptotically (Shannon's
  source coding theorem for lossy coding), but at the cost of exponential complexity in block length.
- The ½ bit/halving-of-MSE rule is the right mental model for **audio, image, and sensor compression
  budgets**: if you know the signal variance and target SNR, R(D) tells you the irreducible bit-rate
  floor before any implementation overhead.
