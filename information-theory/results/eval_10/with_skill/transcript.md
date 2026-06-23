# KL Divergence Between Two Gaussians: Asymmetry Demonstrated

## Setup

- p = N(μ_p=0, σ_p²=1) — mean 0, variance 1
- q = N(μ_q=1, σ_q²=2) — mean 1, variance 2

The closed-form 1-D Gaussian KL formula (in nats) is:

```
KL(p‖q) = log(σ_q/σ_p) + (σ_p² + (μ_p − μ_q)²) / (2σ_q²) − ½
```

Equivalently, working entirely in variances:

```
KL(p‖q) = ½ [ ln(var_q/var_p) + (var_p + (μ_p − μ_q)²)/var_q − 1 ]
```

---

## Forward KL: KL(p ‖ q)

Here p is the "true" distribution and q is the approximation.

Substituting: var_p = 1, var_q = 2, μ_p = 0, μ_q = 1.

```
KL(p‖q) = ½ [ ln(2/1) + (1 + (0 − 1)²)/2 − 1 ]
         = ½ [ ln(2) + (1 + 1)/2 − 1 ]
         = ½ [ 0.6931 + 1.0000 − 1.0000 ]
         = ½ × 0.6931
         = 0.3466 nats
```

Converting to bits (divide by ln 2 = 0.6931):

```
0.3466 / 0.6931 = 0.5000 bits  (exactly ½ bit)
```

**KL(p ‖ q) = 0.3466 nats = 0.5 bits exactly.**

Interpretation: q is wider than p (var_q = 2 > var_p = 1), so q spreads mass in the tails beyond where p has meaningful density. The variance mismatch contributes the ln(2) term; the mean offset (1 unit) contributes the (μ_p − μ_q)² / var_q = 1/2 term. These happen to cancel each other in the bracket — the mean-shift penalty equals exactly 1.0 and the variance-correction term also equals 1.0, leaving only the log-variance-ratio term.

---

## Reverse KL: KL(q ‖ p)

Now the roles are swapped: q plays the "true" distribution, p is the approximation. Substituting: var_q = 2, var_p = 1, μ_q = 1, μ_p = 0.

```
KL(q‖p) = ½ [ ln(var_p/var_q) + (var_q + (μ_q − μ_p)²)/var_p − 1 ]
         = ½ [ ln(1/2) + (2 + (1 − 0)²)/1 − 1 ]
         = ½ [ −0.6931 + (2 + 1) − 1 ]
         = ½ [ −0.6931 + 3.0000 − 1.0000 ]
         = ½ × 1.3069
         = 0.6534 nats
```

Converting to bits:

```
0.6534 / 0.6931 ≈ 0.9427 bits
```

**KL(q ‖ p) = 0.6534 nats ≈ 0.9427 bits.**

Interpretation: Here q is broader than p. When we compute the reverse KL, the expectation is under q. Since q has more variance and a shifted mean, it places substantial mass in regions where p is relatively thin. The term (var_q + (μ_q − μ_p)²)/var_p = (2 + 1)/1 = 3 is now large because p's variance is in the denominator — p is the narrow distribution being used as the "code" for draws from q. The reverse KL heavily penalizes q for placing mass in the tails where p is small.

---

## Is KL Symmetric?

**No. KL divergence is not symmetric.**

```
KL(p‖q) = 0.3466 nats  ≠  KL(q‖p) = 0.6534 nats
```

The ratio is almost exactly 2:1. This is not a coincidence of scale — it reflects a structural difference in what each direction measures.

### Why the directions differ: what each direction penalizes

**Forward KL(p ‖ q)** — "mass-covering," M-projection.
The expectation is under p (the true distribution). Wherever p has density, q is penalized for being small. When q is *broader* than p (as here: var_q = 2 > var_p = 1), q already covers p's support generously, so the penalty is modest. The forward KL is tolerant of q placing extra mass in regions where p is thin.

**Reverse KL(q ‖ p)** — "mode-seeking," I-projection.
The expectation is under q. Wherever q has density, p is penalized for being small. Here p is *narrower* than q (var_p = 1 < var_q = 2), so draws from the wider q often fall in regions where the narrow p has low density. This yields a larger divergence. The reverse KL is harsh when the approximation q is broader than the target p — it is not tolerant of q's mass extending beyond p's support.

### The asymmetry has practical consequences

This is not a mathematical curiosity — the direction choice is a real modeling decision:

- **Variational inference minimizes reverse KL(q ‖ p)** (where p = posterior, q = approximate). Because reverse KL is mode-seeking, the approximation q locks onto one mode and is systematically *too narrow*. This is the structural reason mean-field VI gives overconfident posteriors.
- **MLE / training on data minimizes forward KL(p̂ ‖ q)** (where p̂ = empirical distribution, q = model). Because forward KL is mass-covering, the model q is penalized for missing any region where data appears — it must cover all the data's support.

If someone asks "what is the KL between these distributions" without specifying direction, the question is underspecified. The two answers here (0.35 nats vs. 0.65 nats) are not just numerically different — they encode different failure modes.

---

## Summary Table

| Quantity | Nats | Bits |
|---|---|---|
| KL(p ‖ q) — forward | 0.3466 | **0.5000 (exact)** |
| KL(q ‖ p) — reverse | 0.6534 | ≈ 0.9427 |
| Symmetric? | **No** | **No** |

KL divergence is not a metric. It is not symmetric, does not satisfy the triangle inequality, and calling it "KL distance" invites exactly the mistake of treating these two numbers as interchangeable.
