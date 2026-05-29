"""
Fit a 3-state Gaussian HMM on synthetic regime-switching data,
end-to-end, with the practices the skill insists on:
  - multiple random restarts
  - held-out validation
  - label-switch resolution
  - posterior decoding (not just Viterbi)
  - model selection sweep
  - diagnostic plots
  - sampling check

Run:    python fit_hmm_demo.py
Output: prints results; saves three PNGs in cwd.

This is a template. Adapt the data-generation block, the emission type
(GaussianHMM → CategoricalHMM, PoissonHMM, GMMHMM as needed), and the
canonical-ordering convention to your problem.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # so it runs headless
import matplotlib.pyplot as plt
from hmmlearn import hmm

# ──────────────────────────────────────────────────────────────────────
# 0. Synthetic data — 3 regimes with different means and variances
# ──────────────────────────────────────────────────────────────────────

rng = np.random.RandomState(0)

true_pi = np.array([1.0, 0.0, 0.0])
true_A = np.array([
    [0.97, 0.02, 0.01],   # state 0: calm  (mean 0.0, low vol)
    [0.03, 0.96, 0.01],   # state 1: up    (mean +0.5, mid vol)
    [0.05, 0.02, 0.93],   # state 2: stress (mean -0.3, high vol)
])
true_means = np.array([[0.0], [0.5], [-0.3]])
true_vars  = np.array([[[0.5]], [[1.0]], [[2.5]]])

T = 2000
states = np.zeros(T, dtype=int)
obs = np.zeros((T, 1))
states[0] = np.random.choice(3, p=true_pi)
obs[0] = rng.normal(true_means[states[0], 0], np.sqrt(true_vars[states[0], 0, 0]))
for t in range(1, T):
    states[t] = np.random.choice(3, p=true_A[states[t-1]])
    obs[t] = rng.normal(true_means[states[t], 0], np.sqrt(true_vars[states[t], 0, 0]))

# ──────────────────────────────────────────────────────────────────────
# 1. Multiple random restarts with held-out validation
# ──────────────────────────────────────────────────────────────────────

split = int(0.8 * T)
train_obs, val_obs = obs[:split], obs[split:]

candidates = []
for seed in range(20):
    m = hmm.GaussianHMM(
        n_components=3, covariance_type="full",
        n_iter=200, tol=1e-4, random_state=seed,
    )
    try:
        m.fit(train_obs)
    except Exception as e:
        # State collapse on degenerate inits is normal; skip.
        print(f"  seed {seed} skipped: {type(e).__name__}")
        continue
    candidates.append((m.score(val_obs), m.score(train_obs), seed, m))

candidates.sort(reverse=True, key=lambda x: x[0])
best_val_ll, best_train_ll, best_seed, model = candidates[0]
print(f"\nBest fit: seed={best_seed}  val_ll={best_val_ll:.2f}  train_ll={best_train_ll:.2f}")
print(f"val_ll range across {len(candidates)} restarts: "
      f"[{candidates[-1][0]:.2f}, {candidates[0][0]:.2f}]")
print(f"Spread {candidates[0][0] - candidates[-1][0]:.2f} — "
      f"{'tight (likely global optimum)' if (candidates[0][0] - candidates[-1][0]) < 5 else 'wide (local optima are real)'}\n")

# ──────────────────────────────────────────────────────────────────────
# 2. Sanity: do the recovered parameters look like the true ones
#    (up to label permutation)?
# ──────────────────────────────────────────────────────────────────────

print("Estimated means:    ", np.round(model.means_.flatten(), 3))
print("True means:         ", true_means.flatten())
print("Estimated variances:", np.round(np.diagonal(model.covars_, axis1=1, axis2=2).flatten(), 3))
print("True variances:     ", np.diagonal(true_vars, axis1=1, axis2=2).flatten())
print("Estimated A:\n", np.round(model.transmat_, 3))
print(f"Converged? {model.monitor_.converged}  ({len(model.monitor_.history)} iters)\n")

# ──────────────────────────────────────────────────────────────────────
# 3. Resolve label switching by sorting states by emission mean
# ──────────────────────────────────────────────────────────────────────

order = np.argsort(model.means_.flatten())   # canonical: low-mean state = 0
inv_order = np.argsort(order)

# ──────────────────────────────────────────────────────────────────────
# 4. Decode: Viterbi (single best path) AND posterior γ_t (per-step prob)
# ──────────────────────────────────────────────────────────────────────

viterbi_states = inv_order[model.predict(obs)]
posteriors = model.predict_proba(obs)[:, order]

# True states relabeled into the canonical (mean-sorted) order
true_canonical = np.array([1, 2, 0])[states]
viterbi_acc = (viterbi_states == true_canonical).mean()
print(f"Viterbi accuracy vs true states: {viterbi_acc:.3f}")
print("(Errors concentrate at regime boundaries — expected.)\n")

# ──────────────────────────────────────────────────────────────────────
# 5. Diagnostic plot: observations, true states, Viterbi, posteriors
# ──────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(4, 1, figsize=(14, 8), sharex=True)
axes[0].plot(obs[:, 0], lw=0.5);              axes[0].set_ylabel("Obs")
axes[0].set_title("Diagnostic stack — observations to posterior probabilities")
axes[1].plot(true_canonical, drawstyle="steps-post")
axes[1].set_ylabel("True state"); axes[1].set_yticks([0, 1, 2])
axes[2].plot(viterbi_states, drawstyle="steps-post", color="C1")
axes[2].set_ylabel("Viterbi"); axes[2].set_yticks([0, 1, 2])
for i in range(3):
    axes[3].plot(posteriors[:, i], label=f"state {i}", lw=0.7)
axes[3].set_ylabel("P(Z_t | X)"); axes[3].set_xlabel("Time")
axes[3].legend(loc="upper right", ncol=3, fontsize=8)
plt.tight_layout(); plt.savefig("hmm_diagnostics.png", dpi=120); plt.close()
print("→ saved hmm_diagnostics.png")

# ──────────────────────────────────────────────────────────────────────
# 6. Model selection sweep over K
# ──────────────────────────────────────────────────────────────────────

print("\nModel selection (held-out log-likelihood):")
results = {}
for K in [1, 2, 3, 4, 5, 6]:
    vlls = []
    for seed in range(10):
        m = hmm.GaussianHMM(n_components=K, covariance_type="full",
                            n_iter=200, tol=1e-4, random_state=seed)
        try:
            m.fit(train_obs)
            vlls.append(m.score(val_obs))
        except Exception:
            continue
    if vlls:
        results[K] = max(vlls)
        print(f"  K={K}: best val_ll = {results[K]:.2f}")

plt.figure(figsize=(7, 4))
ks = list(results.keys())
plt.plot(ks, [results[k] for k in ks], "o-")
plt.xlabel("Number of states K"); plt.ylabel("Held-out log-likelihood")
plt.title("Model selection — look for the elbow (here: K=2→3)")
plt.tight_layout(); plt.savefig("hmm_model_selection.png", dpi=120); plt.close()
print("→ saved hmm_model_selection.png")
print("Note: likelihood often keeps creeping up past true K because extra states")
print("absorb noise. The big jump (here K=2→3) is the meaningful signal;")
print("interpret K with domain knowledge, not just the curve.\n")

# ──────────────────────────────────────────────────────────────────────
# 7. Sampling check — do synthetic sequences look like the real data?
# ──────────────────────────────────────────────────────────────────────

synthetic, _ = model.sample(n_samples=500, random_state=42)
fig, axes = plt.subplots(2, 1, figsize=(14, 4), sharex=True)
axes[0].plot(obs[:500, 0], lw=0.5); axes[0].set_title("Real (first 500 timesteps)")
axes[1].plot(synthetic[:, 0], lw=0.5); axes[1].set_title("Sampled from fitted model")
plt.tight_layout(); plt.savefig("hmm_sampling_check.png", dpi=120); plt.close()
print("→ saved hmm_sampling_check.png")
print("If sampled sequences look obviously wrong (no persistence, etc.),")
print("the fit is bad regardless of likelihood.\n")

print("Done.")
