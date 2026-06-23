# Why Mean-Field Variational Inference Produces Overconfident Posteriors

Yes, there is a very principled reason — it follows directly from the objective function mean-field VI optimizes and the geometry of the KL divergence.

---

## The Core Issue: Which KL Are You Minimizing?

Mean-field variational inference minimizes the **forward KL divergence** in the "wrong" direction — or more precisely, it minimizes:

$$\text{KL}(q \,\|\, p) = \mathbb{E}_q\left[\log \frac{q(\theta)}{p(\theta \mid y)}\right]$$

This is sometimes called the **exclusive** or **reverse** KL (depending on your convention). The key asymmetry is in **what happens when** $q(\theta) > 0$ **but** $p(\theta \mid y) \approx 0$:

- The ratio $q / p$ blows up, making the KL divergence infinite or very large.
- The optimizer is therefore strongly penalized for placing mass where the true posterior is near zero.

### Consequence: Zero-Forcing / Mass-Avoiding Behavior

To avoid blowing up the KL, the variational family is pushed toward **concentrating** $q$ on a single mode of $p$. The approximate posterior avoids all regions where $p(\theta \mid y)$ is small — even if those regions contain substantial posterior probability that is spread across multiple modes or in elongated tails.

This is sometimes called **zero-forcing** or **mass-avoiding** behavior:

- $q$ collapses onto a mode and assigns essentially zero density elsewhere.
- Because it ignores the tails and the spread of $p$, its marginal variances are systematically too small.
- The credible intervals it produces are therefore too narrow.

---

## The Contrast: Forward KL Would Give the Opposite Pathology

If instead you minimized:

$$\text{KL}(p \,\|\, q) = \mathbb{E}_p\left[\log \frac{p(\theta \mid y)}{q(\theta)}\right]$$

Now the penalty fires when $p(\theta \mid y) > 0$ but $q(\theta) \approx 0$: the divergence blows up wherever the true posterior has mass but $q$ doesn't. This forces $q$ to cover all modes — producing **mass-covering** behavior. The result is overdispersed, not underdispersed, approximate posteriors.

Expectation propagation (EP) approximately minimizes this forward KL and tends to produce wider, often better-calibrated marginals, at the cost of not always converging.

---

## The Mean-Field Factorization Makes It Worse

Beyond the KL direction, the **mean-field factorization assumption**:

$$q(\theta) = \prod_i q_i(\theta_i)$$

forces all parameters to be independent under the approximation. The true posterior almost certainly has **posterior correlations** between parameters. By zeroing out all off-diagonal covariance structure, the mean-field family cannot represent elongated or banana-shaped posteriors. The only way the optimizer can compensate when forced into a factored Gaussian is to make each marginal very tight — again, the result is overconfidence.

For example, if the true posterior is a thin, diagonal ridge in a 2D space (strong correlation between $\theta_1$ and $\theta_2$), the best mean-field approximation will be a small ellipse centered on the mode. Each marginal of that ellipse will be much narrower than the true marginal, which spreads along the ridge.

---

## Information-Theoretic Framing

The ELBO (evidence lower bound), which VI maximizes, can be written as:

$$\text{ELBO}(q) = \mathbb{E}_q[\log p(y, \theta)] - \mathbb{E}_q[\log q(\theta)]$$

The second term is the **entropy** of $q$. Maximizing the ELBO requires balancing:

1. Fitting the data well (first term — pushes $q$ toward the posterior mode).
2. Being as spread out as possible (entropy — pushes against overconcentration).

In principle the entropy term should keep the posterior from collapsing entirely. But when the mean-field family cannot represent the true shape of $p(\theta \mid y)$ — especially when it cannot represent correlations — the entropy of the best-fitting $q$ is structurally limited. The optimizer finds the best compromise, but that compromise still results in marginals that are too tight because the family simply cannot accommodate the full posterior volume.

---

## Practical Implications

| Symptom | Mechanism |
|---|---|
| Marginal CIs too narrow | KL zero-forcing; mass concentrated on mode |
| Misses secondary modes | Zero-forcing; $q$ avoids low-$p$ regions |
| Underestimates marginal variance in correlated models | Mean-field zeroes out all covariances |
| Worse for hierarchical models | Hyperparameters and latents are highly correlated; factorization incurs large penalty |

---

## Remedies

1. **Structured VI / full-rank Gaussian VI**: Allow off-diagonal covariance (e.g., full-rank or low-rank covariance families). This doesn't fix the KL direction but does allow the approximation to match posterior correlations, reducing the narrowness problem.

2. **Normalizing flows**: Use a more expressive $q$ family (invertible neural networks) that can represent multimodal and non-Gaussian posteriors. Still optimizes $\text{KL}(q \| p)$, so mass-avoiding behavior persists, but the family has enough capacity to better match the true posterior volume.

3. **Importance-weighted ELBO (IWAE)**: Uses importance sampling corrections to get a tighter bound. Doesn't fully fix overconfidence but reduces it.

4. **Expectation Propagation**: Minimizes $\text{KL}(p \| q)$ locally, producing mass-covering behavior. Better calibrated marginals, but convergence is not guaranteed.

5. **Stochastic VI with better families**: Reparameterization gradient estimators (the "reparameterization trick") allow backprop through the sampling step, making it tractable to use more expressive families.

6. **Laplace approximation**: Fits a Gaussian centered at the MAP with curvature given by the Hessian. Also overconfident, but at least it captures some local curvature, including correlations. Often competitive with mean-field VI in practice.

---

## Summary

The overconfidence of mean-field VI is a direct, principled consequence of two factors:

1. **KL direction**: Minimizing $\text{KL}(q \| p)$ penalizes $q$ for placing mass where $p$ is small, pushing $q$ to concentrate on modes and ignore tails — yielding systematically too-narrow marginals.
2. **Factorization constraint**: The independence assumption eliminates all posterior correlation structure, causing the approximation to underestimate the spread of each marginal when the true posterior has elongated or correlated geometry.

These are not bugs or numerical issues — they are structural properties of the objective and the approximating family. If calibrated uncertainty is critical, you need either a more expressive variational family, a different divergence objective, or MCMC.
