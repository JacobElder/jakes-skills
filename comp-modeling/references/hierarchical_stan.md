# Hierarchical Bayesian Modeling in Stan — Templates and Patterns

Read this when the user is writing or debugging hierarchical Bayesian Stan code for a cognitive model, or when they're choosing between hBayesDM and rolling their own. Mostly contains reusable templates and the "gotchas" specific to cognitive-modeling-in-Stan.

Canonical references: Stan User's Guide (mc-stan.org); Lee & Wagenmakers (2014) *Bayesian Cognitive Modeling*; Ahn, Haines & Zhang (2017) for hBayesDM patterns; Betancourt (2017) "A Conceptual Introduction to Hamiltonian Monte Carlo" — essential reading; Gelman et al. *Bayesian Data Analysis 3rd ed.*

## When to roll your own vs. use a toolbox

Use **hBayesDM** when:
- Your task is one of the ~24 it supports (bandit, IGT, gng, two-step, ra, dd, prl, ts, etc.).
- You want sensible priors out of the box.
- You don't need a non-standard variant.

Use **HDDM** when:
- You're fitting any flavor of DDM or RL-DDM.

Roll your own Stan when:
- The task or model is non-standard (joint models, custom decision rules, latent class membership).
- You need a parameter the toolbox doesn't expose.
- You're publishing methodology and need full transparency.

Rolling your own is also useful pedagogically — but for production research, the toolboxes are battle-tested in ways your one-off Stan code isn't.

## The standard hierarchical structure

The recurring pattern for cognitive models:

```
hyperprior on group-level mean (μ_pr)
hyperprior on group-level SD (σ)
subject-level offset (z, with prior N(0,1))
subject parameter = transform(μ_pr + σ · z)
```

The transform squashes the unconstrained `μ_pr + σ·z` into the parameter's natural range (e.g., [0,1] for learning rate, [0,∞) for inverse temperature). This is the **non-centered parameterization** and it is essential — without it, hierarchical RL/PT/DDM models routinely diverge in Stan.

Typical transforms:
- Bounded [0, 1] (learning rates, weights): `Phi_approx(x)` or `inv_logit(x)`
- Bounded [0, U] (inverse temperatures, certain bounded params): `Phi_approx(x) * U`
- Lower-bounded [0, ∞) (drift, decay): `exp(x)`
- Real-valued (drift signs, biases): identity

## A reusable hierarchical template

Here's a fully worked example for a 2-parameter RL model (`alpha`, `beta`) with subject-level and group-level estimation:

```stan
// hier_rl_2param.stan
data {
  int<lower=1> N;                       // number of subjects
  int<lower=1> T;                       // max trials per subject
  array[N] int<lower=1, upper=T> Tsubj; // actual trials per subject
  array[N, T] int<lower=0, upper=2> choice;  // 1, 2; 0 = padding
  array[N, T] real outcome;
}

parameters {
  // Group-level means (on unconstrained scale)
  vector[2] mu_pr;
  // Group-level SDs (strictly positive)
  vector<lower=0>[2] sigma;
  // Subject-level offsets (non-centered)
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
  // Hyperpriors: weakly informative
  mu_pr    ~ normal(0, 1);
  sigma    ~ normal(0, 0.2);
  // Subject-level: standard normal (non-centered)
  alpha_pr ~ normal(0, 1);
  beta_pr  ~ normal(0, 1);
  
  // Likelihood
  for (i in 1:N) {
    vector[2] Q = rep_vector(0.0, 2);
    for (t in 1:Tsubj[i]) {
      choice[i, t] ~ categorical_logit(beta[i] * Q);
      Q[choice[i, t]] += alpha[i] * (outcome[i, t] - Q[choice[i, t]]);
    }
  }
}

generated quantities {
  // Group-level posterior estimates (back-transformed)
  real<lower=0, upper=1> mu_alpha = Phi_approx(mu_pr[1]);
  real<lower=0, upper=20> mu_beta = Phi_approx(mu_pr[2]) * 20;
  
  // Per-trial log-likelihood for LOO/WAIC
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

Calling from R:

```r
library(cmdstanr)
mod <- cmdstan_model("hier_rl_2param.stan")
fit <- mod$sample(
  data = list(N = n_subj, T = max_trials, Tsubj = trials_per_subj,
              choice = choice_mat, outcome = outcome_mat),
  chains = 4, parallel_chains = 4,
  iter_warmup = 1000, iter_sampling = 2000,
  adapt_delta = 0.95,
  max_treedepth = 12
)

# Diagnostics
fit$cmdstan_diagnose()  # checks R-hat, ESS, divergences
fit$summary(c("mu_alpha", "mu_beta", "sigma"))
```

Calling from Python:

```python
from cmdstanpy import CmdStanModel
import numpy as np

model = CmdStanModel(stan_file='hier_rl_2param.stan')
fit = model.sample(
    data={'N': n_subj, 'T': max_trials, 'Tsubj': trials_per_subj.tolist(),
          'choice': choice_mat.tolist(), 'outcome': outcome_mat.tolist()},
    chains=4, parallel_chains=4,
    iter_warmup=1000, iter_sampling=2000,
    adapt_delta=0.95, max_treedepth=12
)
print(fit.diagnose())
print(fit.summary().filter(regex='mu_alpha|mu_beta|sigma', axis=0))
```

## Convergence diagnostics — what to check

After fitting, always check:

- **R-hat < 1.01** for every parameter of interest. R-hat between 1.01 and 1.05 is borderline; > 1.05 means chains haven't mixed and you cannot trust the posterior.
- **ESS > 400** (bulk and tail) for every parameter of interest. Lower ESS means high autocorrelation; estimates are imprecise.
- **Zero divergent transitions** after warmup. Even a few divergences mean the posterior geometry is hard and some regions are being missed; the estimates are biased.
- **Tree depth not saturated.** If many iterations hit `max_treedepth`, sampling is inefficient (not invalid).
- **Energy diagnostics** (Bayesian Fraction of Missing Information): E-BFMI > 0.3 ideal.

Cmdstan's `diagnose` checks most of these automatically. `bayesplot::mcmc_trace`, `bayesplot::mcmc_pairs`, and `bayesplot::mcmc_neff_hist` are the right visual diagnostics.

## Common Stan-cognitive-modeling pitfalls

- **Centered parameterization in hierarchical models.** If you wrote `alpha[i] ~ normal(mu_alpha, sigma_alpha)` directly, you're in the centered parameterization and you'll likely diverge. Switch to non-centered.
- **Putting the transform inside `parameters`.** Don't. Put it in `transformed parameters`. Otherwise the implicit Jacobian is wrong.
- **Forgetting the Jacobian when transforming a parameter manually.** If you declare an unconstrained parameter and then constrain it inside `model`, you need to add the log-Jacobian. The `<lower=, upper=>` bounds in `parameters` handle this automatically; manual transforms need `target += log_abs_det_jacobian`. Use built-in bounds whenever possible.
- **Poorly scaled outcomes.** If your rewards range over many orders of magnitude, scale them. Stan's defaults for adapt_delta, mass matrix, etc. assume reasonably scaled parameters.
- **Loops over trials with vectorization opportunities.** Stan's vectorized statements are much faster. Where possible, vectorize the likelihood (e.g., batched `categorical_logit_lpmf`). Trial-sequential models (RL, DDM with trial dependencies) inherently can't vectorize the inner loop but can vectorize across subjects with a `for (i in 1:N)` outer loop on the parallel side.
- **Storing `log_lik` for huge T × N.** This blows up the output file. For LOO purposes, only store what you need; for very large datasets, consider per-subject LOO instead of per-trial.
- **Setting `sigma ~ normal(0, very_small)`.** Too tight a hyperprior squashes individual differences and gives misleading group-level conclusions. `normal(0, 0.5)` or `normal(0, 1)` on the unconstrained scale is usually safe; smaller values should be justified.
- **Setting `adapt_delta` too low.** Default 0.8 is fine for easy models; cognitive models often need 0.9–0.99 to avoid divergences. Increase it before adding model complexity.
- **Mixing priors and constraints inconsistently.** If you declare `real<lower=0> beta;` and put `beta ~ normal(0, 1)` you're putting a half-normal prior on β — that's usually fine, but be deliberate about it.

## Patterns for specific cognitive models

### Adding a parameter that varies by condition

Two common approaches:

**Subject-level parameter for each condition.** Replicates the parameter structure per condition; each condition's parameter is drawn from a (possibly shared) group distribution. Most flexible; uses more parameters.

**Regression form.** Subject's parameter is `μ + β_cond · cond_indicator`. Lets you directly estimate the condition effect with a single estimable parameter. Cleaner when the contrast is the focus.

Choose based on whether the question is "does condition X have an effect" (regression form) or "what are the parameters in each condition" (replicate form).

### Modeling individual differences by group (e.g., patients vs controls)

```stan
parameters {
  vector[2] mu_pr_grp[2];           // group means for each of 2 groups
  vector<lower=0>[2] sigma;          // shared SD across groups
  vector[N] alpha_pr;
  vector[N] beta_pr;
}
transformed parameters {
  vector<lower=0, upper=1>[N] alpha;
  vector<lower=0, upper=20>[N] beta;
  for (i in 1:N) {
    alpha[i] = Phi_approx(mu_pr_grp[group[i], 1] + sigma[1] * alpha_pr[i]);
    beta[i]  = Phi_approx(mu_pr_grp[group[i], 2] + sigma[2] * beta_pr[i]) * 20;
  }
}
```

Now `mu_pr_grp[1, ]` vs `mu_pr_grp[2, ]` gives you the group difference at the unconstrained scale. Transform back for interpretation. Compute `mu_alpha_diff = Phi_approx(mu_pr_grp[1, 1]) - Phi_approx(mu_pr_grp[2, 1])` in `generated quantities`.

### Modeling RT and choice jointly (RL-DDM in Stan)

Stan's `wiener_lpdf` for DDM combined with RL update for drift:

```stan
model {
  for (i in 1:N) {
    vector[2] Q = rep_vector(0.0, 2);
    for (t in 1:Tsubj[i]) {
      real drift = v_mod[i] * (Q[2] - Q[1]);
      if (choice[i, t] == 2)  // upper boundary
        rt[i, t] ~ wiener(alpha[i], tau[i], beta[i], drift);
      else
        rt[i, t] ~ wiener(alpha[i], tau[i], 1 - beta[i], -drift);
      Q[choice[i, t]] += lr[i] * (reward[i, t] - Q[choice[i, t]]);
    }
  }
}
```

Per-subject parameters: `alpha` (boundary), `tau` (non-decision time), `beta` (starting point bias), `v_mod` (drift scaling), `lr` (RL learning rate). All hierarchical with non-centered parameterization. This is what `HDDMrl` does internally, more or less.

### Posterior predictive checks

In `generated quantities`, simulate new behavior from the fitted parameters and store it. For RL:

```stan
generated quantities {
  array[N, T] int y_pred = rep_array(-1, N, T);
  for (i in 1:N) {
    vector[2] Q = rep_vector(0.0, 2);
    for (t in 1:Tsubj[i]) {
      y_pred[i, t] = categorical_logit_rng(beta[i] * Q);
      // For PPC we use the *observed* outcome to maintain comparability
      Q[choice[i, t]] += alpha[i] * (outcome[i, t] - Q[choice[i, t]]);
    }
  }
}
```

Then compare summary stats of `y_pred` (per-condition accuracy, switch rates, etc.) to the same stats in the real data.

## Speed tips

- Use `cmdstanr`/`cmdstanpy` over older `rstan`/`pystan`. Faster and more reliable.
- Run chains in parallel (`parallel_chains = 4`).
- Inside-chain threading: Stan 2.18+ supports `reduce_sum` and `map_rect` for within-chain parallelism. Useful when you have many subjects and the per-subject likelihood is the bottleneck.
- For exploration, fit with fewer iterations first (e.g., `iter_warmup = 500`, `iter_sampling = 1000`) and increase once the model is debugged.
- Reduce `log_lik` output if it's the bottleneck.
- Consider variational inference (`vb` / `pathfinder`) for prototyping. Not for publication-grade fits, but good for sanity-checking.

## When the model doesn't converge

Decision tree:

1. **Reparameterize.** Non-centered scales; logit/Phi transforms for bounded parameters; log for positive parameters. This fixes 80% of cases.
2. **Tighten weakly identified priors.** A flat prior on a poorly identified parameter creates funnels that HMC can't traverse. Replace with `normal(0, 1)` or similar.
3. **Increase `adapt_delta`** to 0.95 or 0.99.
4. **Inspect pair plots** of poorly-mixing parameters. Funnels, banana shapes, multimodality all need reparameterization.
5. **Simplify the model.** Drop a poorly identified parameter; see if it converges. If yes, you've identified the troublemaker — either keep dropping it, fix to a value, or constrain it harder.
6. **Check for label-switching.** Mixture models, latent class models often have label switching. Add an ordering constraint or reparameterize.
7. **Validate on synthetic data.** Simulate from your model with known parameters; refit; see if you recover them. If the simulated-and-refit version converges and recovers, your real data has features (outliers, contamination, model misspecification) the model can't handle. Refine the model or clean the data.

## hBayesDM cheat sheet

For users who want to skip writing Stan when possible. A few of the most-used models:

```r
library(hBayesDM)

# Standard 2-arm bandit, hyperbolic RW + softmax
fit <- bandit2arm_delta(data = your_data, niter = 4000, nwarmup = 1000)

# Iowa gambling, PVL-delta
fit <- igt_pvl_delta(data = your_data, niter = 4000)

# Prospect theory, risk aversion task (Sokol-Hessner)
fit <- ra_prospect(data = your_data, niter = 4000)

# Drift diffusion, basic
fit <- choiceRT_ddm(data = your_data, niter = 4000)

# Delay discounting, hyperbolic
fit <- dd_hyperbolic(data = your_data, niter = 4000)

# Two-step task, full 7-param hybrid
fit <- ts_par7(data = your_data, niter = 4000)

# Standard outputs
plot(fit)
plotInd(fit, "alpha")    # individual-subject estimates
printFit(fit, ic = "looic")
```

If hBayesDM does what you need, use it. Saves a day's work and avoids Stan-bug-creation.
