# Response

No, this is not a bug. Differential entropy can be negative, and -2.4 is a perfectly valid result.

## What is happening

The quantity your code computed is **differential entropy**, defined as:

```
h(X) = −∫ f(x) log f(x) dx
```

This is not the continuous analog of Shannon entropy in any deep sense — it is a different mathematical object with different properties, and one of those properties is that it **has no lower bound of zero**. The non-negativity guarantee that holds for discrete entropy (`H(X) ≥ 0` for any distribution over a finite or countable alphabet) does not carry over.

## Why differential entropy goes negative: the concrete example

The clearest demonstration is `Uniform(0, a)` for `a < 1`. Its differential entropy is:

```
h = log(a)
```

For `a = ½`, `h = log(½) = −1 bit` (or `−ln 2 ≈ −0.693` nats). No bug. A narrow, concentrated distribution has *negative* differential entropy because the density values `f(x) = 1/a > 1` make `log f(x)` positive over the support, so `−∫ f log f dx` is negative.

More generally: whenever the density is tightly concentrated (small variance, narrow support), the peak density exceeds 1, and the integral tips negative.

## What the negative value means — and does not mean

It does **not** mean "negative information," "less than nothing," or any incoherent quantity. Differential entropy is not expected surprisal; it is the residual after subtracting an infinite baseline (the `−log Δ` divergence you'd get from binning finer and finer). The number is meaningful only relative to other differential entropies computed at the same scale and in the same units.

## What -2.4 tells you concretely

If your code uses natural log (nats), you can sanity-check against the Gaussian closed form:

```
h(N(μ, σ²)) = ½ ln(2πe σ²)
```

Setting that equal to -2.4 nats gives `σ ≈ 0.078`. That means your feature is quite narrowly concentrated — a standard deviation of roughly 0.08 in whatever units it's measured in. For a feature with small variance or a bounded, narrow support (e.g., values tightly clustered in `[0, 0.2]`), a differential entropy of -2.4 is entirely expected.

## The actual pitfall to watch for

The result is correct, but be careful about what you do with it next. Differential entropy is **not invariant under invertible reparameterization**. If you rescale the feature (say, multiply by 1000 to convert units), the differential entropy shifts by `log 1000` — about 6.9 nats. Two differential entropy values are comparable only if they are in the same units on the same measurement scale.

If your goal is to compare the "informativeness" of differently-scaled features, or to measure dependence between this feature and another variable, **differential entropy is the wrong tool**. Use **mutual information** instead — MI is a difference of entropy terms, so the coordinate-dependent pieces cancel, and the result is both non-negative and reparameterization-invariant.

## Summary

| Property | Discrete entropy `H` | Differential entropy `h` |
|---|---|---|
| Non-negative? | Yes, always | No — can be negative |
| Reparameterization-invariant? | N/A | No — shifts by `E[log\|g′(X)\|]` |
| Comparable across features at different scales? | N/A | No |
| Use for measuring dependence? | Yes (via MI) | Use MI, not `h` directly |

Your -2.4 is a valid number. If the downstream task requires comparing features or measuring relationships, switch to mutual information.
