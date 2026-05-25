# Reinforcement Learning Models

Read this when the user's question involves learning from feedback over trials — bandit tasks, probabilistic reversal, Iowa Gambling, two-step tasks, go/no-go, instrumental learning, Pavlovian conditioning paradigms, "fit a learning rate to my data," anything involving Q-values or prediction errors.

The textbook reference is Sutton & Barto (2018). For behavioral fitting in particular, Daw (2011), Wilson & Collins (2019), and Ahn et al. (2017) are the operational references.

## The core building blocks

Almost every RL model for behavior is built from a small set of pieces. You compose these into a specific model.

**1. A value representation.** Usually `Q(s, a)` for state-action values, or `V(s)` for state values, or just `Q(a)` for context-free bandits.

**2. An update rule** (the "learning model"). The basic Rescorla-Wagner / delta rule:

$$Q_{t+1}(a_t) = Q_t(a_t) + \alpha \cdot (r_t - Q_t(a_t))$$

where α ∈ [0,1] is the learning rate and `(r - Q)` is the *reward prediction error* (RPE). Unchosen options are typically not updated (in bandit) or updated with assumed counterfactual outcomes (fictive RL).

**3. A choice rule** (the "observation model"). Softmax is the workhorse:

$$P(a_i \mid \mathbf{Q}) = \frac{\exp(\beta \cdot Q(a_i))}{\sum_j \exp(\beta \cdot Q(a_j))}$$

β is the inverse temperature ("exploration-exploitation"); β → 0 is uniform random, β → ∞ is deterministic argmax. Alternatives: ε-greedy (rarely used in behavioral fitting because the likelihood is degenerate), Thompson sampling (for Bayesian models).

The genius of Daw's "learning model vs. observation model" split is that these compose freely: you can plug a Kalman filter learner into a softmax choice rule, or a Rescorla-Wagner learner into a probit, etc.

## Common variants — and when to use each

**Rescorla-Wagner / standard Q-learning (1 α, 1 β).** The default starting point for any new task. 2 free parameters per subject. Fits almost any reinforcement-based task adequately. Always include this as a baseline even if you think you need something fancier.

**Dual learning rates (α⁺, α⁻, β).** Separate learning rates for positive (better-than-expected) and negative (worse-than-expected) RPEs. 3 parameters. Captures optimism/pessimism asymmetries; relevant for studies of depression, dopamine, etc. Frank et al. (2007) is canonical. Be aware: α⁺ and α⁻ often trade off with β and with each other; recovery is harder than for the single-α model. Always check parameter recovery before interpreting an asymmetry.

**Q-learning with decay/forgetting (α, β, γ).** Unchosen options decay toward 0 (or toward initial value) at rate γ. Important when there are long gaps between visits to an option. Niv et al. (2015), Collins & Frank (2012).

**SARSA vs Q-learning.** SARSA updates `Q(s,a)` toward `r + γ Q(s', a')` — the value of the *next chosen action*. Q-learning updates toward `r + γ max_a' Q(s', a')` — the value of the next *best* action. SARSA is on-policy; Q-learning is off-policy. For single-stage bandits they're identical. The distinction matters for multi-step tasks.

**Actor-critic.** Separate value (critic) and policy (actor) representations updated by the same RPE. Mostly used when the theoretical claim involves the actor/critic distinction (e.g., dopamine target hypothesis). Slightly different parameter recovery properties than pure Q-learning.

**Model-based RL and the two-step task.** Daw et al. (2011) introduced the two-step Markov decision task to dissociate **model-free** (cached values, updated by RPE) from **model-based** (planning using a learned transition model) RL. The "hybrid" model has a weight `w` ∈ [0,1] mixing the two. Fitting requires careful Stan/PyMC code because of the two-stage choice structure; the canonical implementation is in Daw et al. (2011); `hBayesDM::ts_par7` and friends are the off-the-shelf option. Pearson et al., Otto et al., Gillan et al. have used this paradigm in clinical/individual-differences work; be aware the test-retest reliability of `w` is mediocre (Brown et al. 2020).

**Pavlovian-instrumental transfer / Go-NoGo (Guitart-Masip et al. 2012).** Adds a Pavlovian bias term and a static "go" bias to capture asymmetric learning of approach vs avoidance. 4–6 parameters; `hBayesDM::gng_*` models implement the standard variants.

**Iowa Gambling Task** uses domain-specific models: Prospect Valence Learning (PVL-decay or PVL-delta; Ahn et al. 2014; Worthy et al. 2013), Value-Plus-Perseverance (7 parameters). These layer prospect-theory-like utility on top of an RL update rule. Available as `hBayesDM::igt_*`.

**Risk-sensitive RL** (Mihatsch & Neuneier 2002; Niv et al. 2012): the learning rate itself depends on the sign of the RPE in a way that produces risk-seeking or risk-averse behavior. Useful when subjects show systematic risk preferences in a reward-learning context.

## Parameter ranges to expect

Empirical priors from the literature, useful for setting priors and for sanity-checking estimates:

- **Learning rate α**: roughly 0.05–0.5 for stable adult bandit tasks; can be much higher (0.5–0.9) for volatile environments or trial-and-error tasks; very low values (<0.05) often signal a model misspecification or insufficient data.
- **Inverse temperature β**: in tasks where rewards are scaled to be ~1, typically 1–10. In tasks with raw monetary rewards (e.g., $5), divide accordingly. β at the upper bound usually means the subject is more deterministic than the model can capture or that there's an unmodeled win-stay/lose-shift bias.
- **Discount factor γ** (when used): often fixed to 0.9 or 1; rarely well-identified in short tasks.

Set hierarchical priors that span the range plus some — e.g., for α in Stan, use a non-centered Normal on the unconstrained scale and squash with `Phi` or sigmoid to [0,1], with the group mean ~ Normal(0, 1) and the group SD ~ Normal+(0, 0.5).

## Likelihood function — the canonical Python implementation

For a basic single-α RW + softmax bandit, this is the log-likelihood you'd write for MLE. Use it as a template:

```python
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

def rl_softmax_loglik(params, choices, rewards, n_options=2):
    """
    Negative log-likelihood for Rescorla-Wagner + softmax on a bandit.
    choices: int array of trial-by-trial choices in [0, n_options)
    rewards: float array of trial-by-trial rewards
    """
    alpha, beta = params
    Q = np.zeros(n_options)
    nll = 0.0
    for c, r in zip(choices, rewards):
        # Softmax choice probability for chosen option (log space)
        log_probs = beta * Q - logsumexp(beta * Q)
        nll -= log_probs[c]
        # Delta-rule update
        Q[c] = Q[c] + alpha * (r - Q[c])
    return nll

# Fit with bounded MLE
result = minimize(
    rl_softmax_loglik,
    x0=[0.3, 3.0],
    args=(choices, rewards),
    method='L-BFGS-B',
    bounds=[(1e-4, 1 - 1e-4), (1e-4, 30.0)]
)
alpha_hat, beta_hat = result.x
```

Things to note about this skeleton:

- Compute the softmax in log space via `logsumexp` to avoid overflow when β is large.
- Bound α away from exact 0/1 and β away from 0 to avoid degenerate likelihoods.
- For MAP, add the log prior to `nll` (so you're minimizing negative log posterior).
- For multiple random restarts, wrap in a loop and pick the lowest `nll`.

### R equivalent

```r
rl_softmax_loglik <- function(params, choices, rewards, n_options = 2L) {
  alpha <- params[1]; beta <- params[2]
  Q <- numeric(n_options)
  nll <- 0
  for (t in seq_along(choices)) {
    z  <- beta * Q
    lp <- z - matrixStats::logSumExp(z)
    nll <- nll - lp[choices[t]]
    c <- choices[t]
    Q[c] <- Q[c] + alpha * (rewards[t] - Q[c])
  }
  nll
}

fit <- optim(c(0.3, 3.0), rl_softmax_loglik,
             choices = choices, rewards = rewards,
             method = "L-BFGS-B",
             lower = c(1e-4, 1e-4), upper = c(1 - 1e-4, 30))
```

## A reusable hierarchical Stan template

This is the bare-minimum hierarchical Bayesian RL fit — single α, single β, group-level mean and SD on each, non-centered parameterization. Adapt it as needed.

```stan
data {
  int<lower=1> N;                 // subjects
  int<lower=1> T;                 // max trials per subject
  array[N] int<lower=1, upper=T> Tsubj;  // trials per subject
  array[N, T] int<lower=0, upper=2> choice;   // 1 or 2, 0 = padding
  array[N, T] real outcome;
}
parameters {
  // Group-level
  vector[2] mu_pr;
  vector<lower=0>[2] sigma;
  // Subject-level (non-centered)
  vector[N] alpha_pr;
  vector[N] beta_pr;
}
transformed parameters {
  vector<lower=0, upper=1>[N] alpha;
  vector<lower=0, upper=20>[N] beta;
  for (i in 1:N) {
    alpha[i] = Phi_approx(mu_pr[1] + sigma[1] * alpha_pr[i]);
    beta[i]  = Phi_approx(mu_pr[2] + sigma[2] * beta_pr[i]) * 20;
  }
}
model {
  // Hyperpriors
  mu_pr  ~ normal(0, 1);
  sigma  ~ normal(0, 0.2);
  alpha_pr ~ normal(0, 1);
  beta_pr  ~ normal(0, 1);

  for (i in 1:N) {
    vector[2] Q = rep_vector(0.0, 2);
    for (t in 1:Tsubj[i]) {
      choice[i, t] ~ categorical_logit(beta[i] * Q);
      Q[choice[i, t]] += alpha[i] * (outcome[i, t] - Q[choice[i, t]]);
    }
  }
}
generated quantities {
  // For LOO/WAIC
  array[N, T] real log_lik;
  for (i in 1:N) {
    vector[2] Q = rep_vector(0.0, 2);
    for (t in 1:T) {
      if (t <= Tsubj[i]) {
        log_lik[i, t] = categorical_logit_lpmf(choice[i, t] | beta[i] * Q);
        Q[choice[i, t]] += alpha[i] * (outcome[i, t] - Q[choice[i, t]]);
      } else {
        log_lik[i, t] = 0;
      }
    }
  }
}
```

Notes:
- `Phi_approx` transforms unconstrained subject-level deviations to [0,1]; multiplying by 20 gives β a reasonable upper bound.
- Non-centered parameterization (the `_pr` parameters drawn N(0,1), then transformed) is essential — centered hierarchical Bayesian RL models routinely diverge in Stan.
- `log_lik` is computed for every trial to allow LOO/WAIC via `loo` package.

Calling from R:

```r
library(cmdstanr)
mod <- cmdstan_model("rl.stan")
fit <- mod$sample(data = stan_data, chains = 4, parallel_chains = 4,
                  iter_warmup = 1000, iter_sampling = 2000,
                  adapt_delta = 0.95)
```

Or just use `hBayesDM::bandit2arm_delta(data = your_df, niter = 4000)` and skip writing the Stan file — it does exactly this internally for the standard case.

## Common pitfalls specific to RL

- **The α/β trade-off.** When α is near 1, all choice probability comes from the most recent outcome; β can be anything. When α is small, β controls effective stochasticity. They're partially confounded by design. Always report joint posteriors, not marginals only.
- **Unchosen-option updates.** Decide explicitly: do unchosen options keep their old value, decay toward 0, or get updated counterfactually? This matters enormously for what α means.
- **Initial Q-values.** Common conventions: 0 (assumes no prior bias), 0.5 (for binary reward tasks, no bias toward higher-Q exploration), or fit as free parameter (rarely well-identified). Document the choice.
- **Reward scaling.** β scales inversely with reward magnitude. If you change reward from {0,1} to {0,100}, β values aren't comparable. Either scale rewards consistently across studies or rescale β when reporting.
- **Probabilistic reward tasks vs deterministic.** A "learning rate" in a deterministic shifting environment (reversal) means something different than in a stationary stochastic environment. Same parameter symbol, different psychological meaning.
- **Forgetting / decay confounds with learning rate.** If unchosen options decay at rate γ and chosen options update at rate α, these can trade off. Make sure your model is identifiable.
- **Win-stay-lose-shift is hard to beat.** A simple WSLS heuristic accounts for a huge fraction of variance in bandit choices. Include WSLS as a baseline; if your RL model doesn't beat it on held-out data, the RL story isn't doing real work.
- **The two-step task’s `w` has poor test-retest reliability — flag this before any individual-difference analysis.** Brown et al. (2020) showed that `w` from a single session correlates only weakly with itself on retest. Shahar et al. (2019) and Kool et al. (2016) document the same problem from different angles. When a user wants to use `w` to predict clinical outcomes or group differences, say this explicitly: the test-retest reliability is insufficient for `w` to function as a reliable individual-difference measure without large samples, multiple sessions, or hierarchical pooling across sessions. Report `w` with full uncertainty intervals; never treat it as a precision measurement.
- **Choice perseveration is real and confounds learning-rate estimates.** Many subjects show a tendency to repeat the last choice regardless of outcome. Models without a perseveration term (a stay/switch bias) often inflate α to absorb this. Always test a perseveration-augmented variant.
- **Forgetting / decay is also real and gets absorbed into α** if not modeled. Same lesson.

## Posterior predictive check examples for RL

When validating an RL fit, simulate from the fitted parameters and compare to behavior on these:

- **Learning curve**: P(correct) as a function of trial number, possibly separated by block/condition.
- **Win-stay-lose-shift rates**: P(repeat choice | reward), P(switch choice | no reward). RL models should reproduce these.
- **Reversal recovery**: trials-to-criterion after a contingency reversal.
- **Choice perseveration**: autocorrelation of choices at lag 1.
- **Reaction time × prediction error** (if RTs were collected): faster RTs after high-confidence trials.

If the model nails LOO but misses any of these qualitatively, do not declare victory.

## Typical experimental designs and the model you want

| Task | Default model | Toolbox |
|------|---------------|---------|
| 2-armed bandit, stationary | RW + softmax (α, β) | hBayesDM `bandit2arm_delta` |
| 4-armed bandit, drifting | RW + softmax, possibly with decay | custom Stan; check Daw et al. 2006 |
| Probabilistic reversal | Dual-α RW or HMM-RL | hBayesDM `prl_*` family |
| Iowa Gambling | PVL-decay, PVL-delta, or VPP | hBayesDM `igt_*` family |
| Go/No-Go with reward and punishment | RW + bias + Pavlovian | hBayesDM `gng_*` family |
| Two-step Markov task | Hybrid MF/MB with `w` | hBayesDM `ts_par7` |
| Restless 4-armed bandit | Kalman + softmax (see `bayesian_learning.md`) | custom Stan |
| Volatility task (Behrens et al. 2007) | Hierarchical Bayesian / HGF | `bayesian_learning.md`, `hgf` package |

---

**See also:**
- `references/recovery.md` — run parameter recovery before interpreting α or β as individual differences; the α/β trade-off is documented there with code.
- `references/model_comparison.md` — LOO/WAIC for choosing among RL variants.
- `references/hierarchical_stan.md` — non-centered Stan templates for hierarchical RL fits; hBayesDM cheat sheet.
- `references/bayesian_learning.md` — when the environment is volatile and fixed-α RL isn't enough.
- `references/drift_diffusion.md` — when the task also has RT data and you want RL-DDM.
