# Rate-Distortion for a Gaussian Source Under MSE

## Setup

We have a zero-mean Gaussian source with variance $\sigma^2 = 4$. We want to find the rate $R$ (bits per sample) required to achieve a given mean-squared-error (MSE) distortion $D$ using the rate-distortion function.

---

## The Gaussian Rate-Distortion Function

For a zero-mean Gaussian source with variance $\sigma^2$, the rate-distortion function under MSE distortion is:

$$R(D) = \frac{1}{2} \log_2\!\left(\frac{\sigma^2}{D}\right), \quad 0 \leq D \leq \sigma^2$$

For $D > \sigma^2$, $R(D) = 0$ (no bits needed; just output zero).

This function gives the **minimum number of bits per sample** needed to achieve average MSE $\leq D$.

---

## Case 1: MSE = 1

Given $\sigma^2 = 4$, $D = 1$:

$$R(1) = \frac{1}{2} \log_2\!\left(\frac{4}{1}\right) = \frac{1}{2} \log_2(4) = \frac{1}{2} \times 2 = 1 \text{ bit/sample}$$

**Answer: 1 bit per sample.**

---

## Case 2: MSE = 0.25

Given $\sigma^2 = 4$, $D = 0.25$:

$$R(0.25) = \frac{1}{2} \log_2\!\left(\frac{4}{0.25}\right) = \frac{1}{2} \log_2(16) = \frac{1}{2} \times 4 = 2 \text{ bits/sample}$$

**Answer: 2 bits per sample.**

---

## General Rule

For a zero-mean Gaussian with variance $\sigma^2$ and target MSE $D$:

$$\boxed{R(D) = \frac{1}{2} \log_2\!\left(\frac{\sigma^2}{D}\right)}$$

**Interpretation:** Every time you halve the distortion $D$ (i.e., reduce MSE by a factor of 2), you need **one additional half-bit per sample** — or equivalently, every time you reduce $D$ by a factor of 4, you need **one additional bit per sample**. This reflects the fundamental exponential relationship between rate and distortion for Gaussian sources.

**Inverse form** (distortion achieved at rate $R$):

$$D(R) = \sigma^2 \cdot 2^{-2R}$$

Each additional bit per sample reduces achievable MSE by a factor of 4.

---

## Summary Table

| MSE ($D$) | $\sigma^2 / D$ | $\log_2(\sigma^2/D)$ | $R(D)$ |
|-----------|----------------|----------------------|--------|
| 4 (= $\sigma^2$) | 1 | 0 | 0 bits/sample |
| 1 | 4 | 2 | 1 bit/sample |
| 0.25 | 16 | 4 | 2 bits/sample |
| 0.0625 | 64 | 6 | 3 bits/sample |

Each additional bit halves the standard deviation of the reconstruction error, or equivalently, quartering the MSE costs one more bit per sample.
