# KL Divergence Between Two Gaussians

## Setup

We have two normal distributions:

- **p = N(μ_p, σ_p²) = N(0, 1)** — mean 0, variance 1, so σ_p = 1
- **q = N(μ_q, σ_q²) = N(1, 2)** — mean 1, variance 2, so σ_q = √2

---

## General Formula for KL Divergence Between Two Gaussians

For two univariate Gaussians p = N(μ_p, σ_p²) and q = N(μ_q, σ_q²), the KL divergence from p to q is:

$$KL(p \| q) = \log\frac{\sigma_q}{\sigma_p} + \frac{\sigma_p^2 + (\mu_p - \mu_q)^2}{2\sigma_q^2} - \frac{1}{2}$$

This comes from integrating the log-ratio of the two Gaussian densities:

$$KL(p \| q) = \int p(x) \log \frac{p(x)}{q(x)}\, dx$$

Expanding the log ratio of Gaussian densities and collecting terms yields the closed form above.

---

## Direction 1: KL(p ‖ q) — from p = N(0,1) to q = N(1,2)

Plugging in:
- μ_p = 0, σ_p² = 1, σ_p = 1
- μ_q = 1, σ_q² = 2, σ_q = √2

$$KL(p \| q) = \log\frac{\sqrt{2}}{1} + \frac{1 + (0 - 1)^2}{2 \cdot 2} - \frac{1}{2}$$

**Step by step:**

1. **Log term:**
   $$\log\frac{\sqrt{2}}{1} = \log(\sqrt{2}) = \frac{1}{2}\ln 2 \approx \frac{1}{2}(0.6931) = 0.3466$$

2. **Quadratic term (variance + squared mean difference):**
   $$\frac{\sigma_p^2 + (\mu_p - \mu_q)^2}{2\sigma_q^2} = \frac{1 + 1}{4} = \frac{2}{4} = 0.5$$

3. **Constant term:**
   $$-\frac{1}{2} = -0.5$$

**Summing:**

$$KL(p \| q) = 0.3466 + 0.5 - 0.5 = 0.3466$$

$$\boxed{KL(p \| q) \approx 0.3466 = \frac{\ln 2}{2}}$$

---

## Direction 2: KL(q ‖ p) — from q = N(1,2) to p = N(0,1)

Now we swap roles. Using the same formula but with p and q exchanged:

$$KL(q \| p) = \log\frac{\sigma_p}{\sigma_q} + \frac{\sigma_q^2 + (\mu_q - \mu_p)^2}{2\sigma_p^2} - \frac{1}{2}$$

Plugging in:
- Source: q with μ_q = 1, σ_q² = 2, σ_q = √2
- Target: p with μ_p = 0, σ_p² = 1, σ_p = 1

$$KL(q \| p) = \log\frac{1}{\sqrt{2}} + \frac{2 + (1 - 0)^2}{2 \cdot 1} - \frac{1}{2}$$

**Step by step:**

1. **Log term:**
   $$\log\frac{1}{\sqrt{2}} = -\log(\sqrt{2}) = -\frac{1}{2}\ln 2 \approx -0.3466$$

2. **Quadratic term:**
   $$\frac{\sigma_q^2 + (\mu_q - \mu_p)^2}{2\sigma_p^2} = \frac{2 + 1}{2} = \frac{3}{2} = 1.5$$

3. **Constant term:**
   $$-\frac{1}{2} = -0.5$$

**Summing:**

$$KL(q \| p) = -0.3466 + 1.5 - 0.5 = 0.6534$$

$$\boxed{KL(q \| p) \approx 0.6534 = \frac{3}{2} - \frac{\ln 2}{2} - \frac{1}{2} = 1 - \frac{\ln 2}{2}}$$

---

## Summary of Results

| Direction | Value (exact) | Value (approx) |
|---|---|---|
| KL(p ‖ q): N(0,1) → N(1,2) | (ln 2)/2 | 0.3466 |
| KL(q ‖ p): N(1,2) → N(0,1) | 1 − (ln 2)/2 | 0.6534 |

Note: (ln 2)/2 + (1 − ln 2/2) = 1, but they are not equal to each other.

---

## Is KL Divergence Symmetric?

**No. KL divergence is not symmetric.**

This example demonstrates it directly:

$$KL(p \| q) \approx 0.347 \neq 0.653 \approx KL(q \| p)$$

The asymmetry has a concrete interpretation:

- **KL(p ‖ q)** (forward KL, also called "M-projection" or "mean-seeking"): Penalizes cases where p has mass but q does not. Because p = N(0,1) is narrower than q = N(1,2), p's mass lies mostly within a region where q still has reasonable density, so the penalty is smaller.

- **KL(q ‖ p)** (reverse KL, also called "I-projection" or "mode-seeking"): Penalizes cases where q has mass but p does not. Because q = N(1,2) is wider and centered away from p = N(0,1), q assigns substantial mass to regions (e.g., far tails and around x=1) where p has low density — this is expensive, giving a larger KL.

Because KL is not symmetric, it is technically a **divergence**, not a **distance** (a true distance metric requires symmetry). A symmetric variant is the **Jensen-Shannon divergence**, defined as:

$$JSD(p, q) = \frac{1}{2}KL(p \| m) + \frac{1}{2}KL(q \| m), \quad m = \frac{1}{2}(p + q)$$

which satisfies JSD(p,q) = JSD(q,p).
