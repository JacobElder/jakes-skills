# Core HMM Algorithms

Read this before implementing any of these from scratch — every one has a numerical gotcha that bites you the first time. Notation matches SKILL.md: K states, T timesteps, π initial distribution, A transition matrix, B emission model where `b_i(x) = P(X=x | Z=i)`.

The code below is real NumPy, not pseudocode — copy and run it. It's intentionally minimal (no scaling in the "naive" versions, no vectorization beyond NumPy ops) so the logic is visible; production libraries (`hmmlearn`, `dynamax`) do the same things faster.

## Forward algorithm

Computes `α[t, i] = P(X[:t+1], Z[t]=i)`. Summing the final row gives `P(X | model)`.

Recursion: `α[t, j] = b_j(X[t]) * Σ_i α[t-1, i] * A[i, j]`

```python
import numpy as np

def forward_naive(pi, A, B_obs):
    """B_obs[t, i] = b_i(X[t]); precomputed emission likelihoods."""
    T, K = B_obs.shape
    alpha = np.zeros((T, K))
    alpha[0] = pi * B_obs[0]
    for t in range(1, T):
        alpha[t] = B_obs[t] * (alpha[t-1] @ A)
    return alpha, alpha[-1].sum()  # last value is P(X)
```

**Numerical issue:** α values shrink exponentially with t. By t ≈ 100 you hit machine zero and `P(X) = 0`. Two standard fixes; every serious library uses one.

**Fix (a): scaled forward.** Normalize α at each step; recover the log-likelihood from the scaling constants.

```python
def forward_scaled(pi, A, B_obs):
    T, K = B_obs.shape
    alpha = np.zeros((T, K))
    c = np.zeros(T)
    alpha[0] = pi * B_obs[0]
    c[0] = 1.0 / alpha[0].sum()
    alpha[0] *= c[0]                       # now alpha[0] sums to 1
    for t in range(1, T):
        alpha[t] = B_obs[t] * (alpha[t-1] @ A)
        c[t] = 1.0 / alpha[t].sum()
        alpha[t] *= c[t]
    log_likelihood = -np.log(c).sum()
    return alpha, c, log_likelihood
```

**Fix (b): log-space forward.** Carry log-α throughout; replace `sum(α * w)` with `logsumexp(log_α + log_w)`. Slower per-op (logsumexp is exp + log + exp) but cleaner and easier to reason about. Use `scipy.special.logsumexp`.

Pick scaling for speed, log-space for clarity. Never ship a forward algorithm without one of them.

## Backward algorithm

Computes `β[t, i] = P(X[t+1:] | Z[t]=i)`. Used in posterior decoding and Baum-Welch's E-step.

Recursion (runs backwards): `β[t, i] = Σ_j A[i, j] * b_j(X[t+1]) * β[t+1, j]`

```python
def backward_naive(A, B_obs):
    T, K = B_obs.shape
    beta = np.zeros((T, K))
    beta[-1] = 1.0
    for t in range(T - 2, -1, -1):
        beta[t] = A @ (B_obs[t+1] * beta[t+1])
    return beta
```

Same underflow issue. Standard trick: reuse the scaling constants `c[t]` from the forward pass to scale β at the matching timestep. Then `γ[t] = α_scaled[t] * β_scaled[t]` already sums to 1 — useful sanity check.

## Posterior decoding (γ)

`γ[t, i] = P(Z[t]=i | X)` — the marginal posterior over the state at each timestep.

```python
gamma = alpha * beta
gamma /= gamma.sum(axis=1, keepdims=True)
```

The marginal-most-likely state at each t is `gamma.argmax(axis=1)`. **This is not the same as the Viterbi path.** The marginal-argmax sequence can include transitions with zero probability under A (e.g., it might pick state 2 at t=10 and state 5 at t=11 even when A[2, 5] = 0). Use γ for reporting per-position uncertainty; use Viterbi when you need a single self-consistent path.

## Viterbi algorithm

Same shape as forward but with max instead of sum, plus backpointers for the path. Always work in log-space — no underflow, and `max` of logs = log of max of probabilities.

```python
def viterbi(pi, A, B_obs):
    T, K = B_obs.shape
    with np.errstate(divide='ignore'):
        log_pi, log_A, log_B = np.log(pi), np.log(A), np.log(B_obs)
    delta = np.zeros((T, K))
    psi = np.zeros((T, K), dtype=int)
    delta[0] = log_pi + log_B[0]
    for t in range(1, T):
        scores = delta[t-1, :, None] + log_A      # shape (K, K)
        psi[t] = scores.argmax(axis=0)
        delta[t] = scores.max(axis=0) + log_B[t]
    path = np.zeros(T, dtype=int)
    path[-1] = delta[-1].argmax()
    for t in range(T - 2, -1, -1):
        path[t] = psi[t+1, path[t+1]]
    return path, delta[-1].max()
```

**Subtleties:**
- `log(0) = -inf`; NumPy handles `-inf + (-inf) = -inf` correctly. The `errstate` block suppresses the warning.
- Ties: `argmax` picks the lowest index — deterministic for reproducibility, but tied paths aren't all reported.
- Memory: ψ is T × K integers; for very long sequences this can matter.

## Baum-Welch (EM for HMMs)

E-step uses forward-backward to compute posterior expectations; M-step updates parameters in closed form. Iterate to convergence.

```python
def baum_welch_step(X, pi, A, B_obs, emission_distribution):
    """One iteration of EM. Returns updated parameters and log-likelihood."""
    T, K = B_obs.shape

    # E-step
    alpha, c, log_lik = forward_scaled(pi, A, B_obs)
    beta = backward_naive(A, B_obs)               # production: rescale with c
    gamma = alpha * beta
    gamma /= gamma.sum(axis=1, keepdims=True)

    # xi[t, i, j] = P(Z[t]=i, Z[t+1]=j | X)
    xi = np.zeros((T - 1, K, K))
    for t in range(T - 1):
        numer = alpha[t, :, None] * A * B_obs[t+1][None, :] * beta[t+1][None, :]
        xi[t] = numer / numer.sum()

    # M-step
    pi_new = gamma[0]
    A_new = xi.sum(axis=0) / gamma[:-1].sum(axis=0)[:, None]
    # Emission update is distribution-specific:
    #   Gaussian: mu_i = sum_t gamma[t,i] * X[t] / sum_t gamma[t,i]
    #             Sigma_i = weighted covariance using gamma[:, i]
    #   Categorical: b_i[v] = sum_{t: X[t]=v} gamma[t,i] / sum_t gamma[t,i]
    B_obs_new = emission_distribution.update(X, gamma)
    return pi_new, A_new, B_obs_new, log_lik
```

**Things that bite during Baum-Welch:**

1. **Local optima.** EM converges to a local maximum, not a global one. Different inits give different fits. Run from 10+ random starts; keep the best by held-out likelihood. The single practice that separates careful from sloppy HMM work.

2. **State collapse.** A state can lose all posterior mass; re-estimation then gives degenerate parameters. Symptoms: NaN means/covariances, a state with zero stationary probability. Defenses: (a) Dirichlet prior on A and π (pseudo-counts); (b) re-initialize the collapsed state; (c) reduce K. `hmmlearn` handles this with some grace by default, but check.

3. **Singular covariance for Gaussian emissions.** If a state collects very few points, its covariance shrinks toward zero in some directions and the likelihood blows up to +∞. Fix: add `ε * I` to each estimated Σ in the M-step (regularization), or constrain to `covariance_type='diag'` / `'spherical'`.

4. **Convergence check.** Use the **log-likelihood increase**, not parameter change. EM is optimizing likelihood — that's the natural criterion. `tol=1e-4` on log-likelihood per timestep is reasonable.

5. **Multiple sequences.** Sum the sufficient statistics across sequences in the M-step. **Do not** train a separate HMM per sequence and average parameters — that gives nonsense.

## Forward filtering for online use

If you need filtering as data streams in — `P(Z[t]=i | X[:t+1])` — that's just the normalized forward α[t]. No backward needed. O(K²) per new observation, constant memory.

For online smoothing with a fixed lag, run forward as data arrives and run backward over the lag window. Trade-off: longer lag → smoother but higher latency.

## Reading

- Rabiner (1989), "A tutorial on hidden Markov models and selected applications in speech recognition," *Proc. IEEE* 77(2). The canonical reference; still the best single intro 35+ years later.
- Bishop, *Pattern Recognition and Machine Learning* (2006), Chapter 13. Cleaner notation than Rabiner; HMMs as a special case of linear dynamical systems.
- Durbin, Eddy, Krogh, Mitchison, *Biological Sequence Analysis* (1998). The bioinformatics reference; clearest treatment of profile HMMs.
- Murphy, *Machine Learning: A Probabilistic Perspective* (2012), Chapter 17. Bayesian variants and connections to other graphical models.
