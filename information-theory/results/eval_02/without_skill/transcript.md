# Response

No, that's not a bug. A differential entropy of −2.4 is perfectly valid.

## Shannon entropy vs. differential entropy

Shannon (discrete) entropy is always non-negative. For a discrete distribution over *k* outcomes, H = −∑ p_i log p_i ≥ 0, because every term p_i log p_i ≤ 0 and the sum is bounded below by 0.

Differential entropy is the continuous analogue: h(X) = −∫ f(x) log f(x) dx. It does **not** share the non-negativity guarantee, and negative values are not only possible — they are common and meaningful.

## Why differential entropy can be negative

The core issue is that a probability density f(x) is not a probability. It can exceed 1 over intervals where the distribution is highly concentrated. When f(x) > 1, log f(x) > 0, so −f(x) log f(x) < 0. If those negative contributions dominate the integral, h(X) < 0.

A clean example: if X ~ Uniform(0, a), then h(X) = log(a). For a < 1 (e.g., a = 0.5), log(0.5) ≈ −0.693 in nats, which is negative. The distribution is concentrated in a narrow interval, so uncertainty is low — lower, in fact, than the reference measure implicitly baked into the log.

A Gaussian with very small variance also has negative differential entropy: h = ½ log(2πeσ²), which goes negative when σ² < 1/(2πe) ≈ 0.059.

## What differential entropy actually measures

Unlike Shannon entropy, differential entropy is not an absolute measure of uncertainty. It is a measure of uncertainty **relative to a reference density** (usually Lebesgue measure). This means:

- It can be negative (the distribution is more concentrated than the reference).
- It is not invariant to changes of variables (a nonlinear transform changes h(X)).
- It can be −∞ for degenerate distributions.

The quantity that is always non-negative and invariant to such issues is **KL divergence** (relative entropy), not differential entropy itself.

## Sanity-checking your value

A differential entropy of −2.4 nats is consistent with a distribution that is quite narrow. For a Gaussian, −2.4 = ½ log(2πeσ²) implies σ ≈ 0.10. For a uniform on [0, a], −2.4 = log(a) implies a ≈ 0.09. Both are physically reasonable if your feature is measured on a scale where values are tightly clustered near a point.

If you want to double-check the implementation rather than the sign, verify:

1. The numerical integration or histogram-bin widths are correct (bin width matters; omitting it shifts h by a constant).
2. The log base is consistent (nats use ln, bits use log₂; mixing them shifts the scale).
3. The density estimator (KDE bandwidth, histogram bins) is reasonable — too-narrow bins inflate density estimates and push entropy downward.

But the negative sign itself is expected behavior, not a bug.
