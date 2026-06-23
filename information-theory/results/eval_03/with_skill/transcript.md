# Why Mean-Field VI Posteriors Are Overconfident: The KL Direction Argument

Yes, there is a principled reason — and it is not a quirk of your implementation or your
choice of variational family. It is a direct consequence of the objective mean-field VI
minimizes.

## The root cause: you are minimizing reverse KL

Standard variational inference maximizes the ELBO, which is equivalent to minimizing
`KL(q ‖ p)` — the **reverse KL**, where `q` is the variational posterior you control
and `p` is the true posterior you are approximating.

The expectation in reverse KL is under **`q`**, not under `p`:

```
KL(q ‖ p) = E_q[ log q − log p ]
```

This single fact determines the failure mode. Because `q` is penalized only for placing
mass where `p` is *low*, it is free to simply ignore regions of `p`'s support where `q`
places no mass. The optimizer pays no penalty for leaving probability mass on the table.
The result is an approximation that **locks onto one high-probability region and
underestimates spread** — which is precisely what you are seeing as narrow credible intervals.

## Contrast with forward KL (what MCMC samples)

If you instead minimized `KL(p ‖ q)` — the **forward KL** — the expectation would be
under the true posterior `p`:

```
KL(p ‖ q) = E_p[ log p − log q ]
```

Wherever `p` has mass, `q` gets penalized hard for being near zero (`log p/q → ∞`).
The optimizer is forced to **cover all of `p`'s support**. If `q` is too simple for a
multimodal posterior, it spreads out and places mass between modes — overestimates
spread rather than underestimates it. This mass-covering behavior is what maximum
likelihood (and, roughly, what MCMC is calibrated to) produces.

The table of failure modes:

| Direction | Penalty regime | Failure mode when `q` is too simple |
|---|---|---|
| `KL(p ‖ q)` — forward | Penalized for missing mass under `p` | Too wide; bridges modes |
| `KL(q ‖ p)` — reverse | Penalized for placing mass where `p` is low | Too narrow; collapses to one mode |

Your MCMC reference characterizes `KL(p ‖ q)` behavior (it draws from the true posterior);
your VI posterior minimizes `KL(q ‖ p)`. The gap you see between MCMC intervals and VI
intervals *is* this directional asymmetry, not a convergence failure.

## The mean-field compound makes this worse

Mean-field VI adds a second structural constraint: the variational family factorizes
fully across dimensions, `q(θ) = ∏ᵢ qᵢ(θᵢ)`. This forces all posterior correlations to
zero. For a posterior with strong off-diagonal structure (correlated parameters), the
mean-field approximation must compromise: it typically finds an approximation that is too
narrow in the marginals to be consistent with ignoring the correlation structure. The
result is that marginal credible intervals are compressed even beyond what reverse KL
alone would produce.

Concretely: if the true posterior has `Cov(θ₁, θ₂) > 0`, the marginal variance of `θ₁`
under the true posterior is larger than the conditional variance holding `θ₂` fixed. Mean-field
ignores this covariance contribution, so its marginal variance for `θ₁` is systematically too
small.

## What to do about it

The choices, roughly in order of increasing fidelity:

1. **Full-rank (dense) variational family.** Replace the mean-field factorization with a
   multivariate Gaussian whose full covariance is estimated. This recovers linear correlations.
   Quadratic cost in the number of parameters, but often the dominant fix for the overconfidence
   problem in low-to-moderate dimensions.

2. **Normalizing flows / auxiliary variable methods.** Extend the variational family to be
   expressive enough that reverse KL minimization finds something closer to the true posterior.
   The objective is still reverse KL, so mode-seeking is still the failure mode, but a richer
   family is more capable of approximating the true shape.

3. **Expectation Propagation (EP).** EP minimizes forward KL *locally*, making it
   mass-covering rather than mode-seeking. It tends to produce overdispersed rather than
   underdispersed posteriors — the opposite failure mode — and is well-suited when missing
   probability mass is the more dangerous error.

4. **α-divergence interpolation.** Power EP and Rényi VI interpolate between forward and
   reverse KL via a tunable `α`. At `α=0`, you recover reverse KL; at `α=1`, forward KL.
   Setting `α` closer to 1 progressively recovers mass-covering behavior at computational cost.

5. **MCMC when fidelity is required.** If the posterior geometry is complex and the
   overconfidence is consequential (e.g., downstream decisions are sensitive to tail mass),
   VI may not be the right tool. NUTS/HMC with a calibrated warmup is the reference for a reason.

## The honest summary

The overconfidence is not a bug in your code. It is the principled, expected output of an
algorithm that minimizes `KL(q ‖ p)` with a fully factorized family. The direction of that
divergence makes the approximation mode-seeking and zero-forcing; the factorization removes
the covariance contribution to marginal variance. Both effects push credible intervals
inward. When you compare to MCMC, you are comparing the I-projection (reverse KL optimum)
against samples from the true posterior — they will differ systematically, not randomly.

Never treat a VI posterior's interval width as a calibrated uncertainty estimate without
either (a) verifying against a higher-fidelity reference or (b) explicitly accounting for
the approximation gap.
