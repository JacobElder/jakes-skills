# Bayesian Learning Models

Read this when the user is modeling learning under uncertainty in a way that treats the learner as performing approximate Bayesian inference — the Behrens et al. (2007) volatility task, Kalman-filter bandits, ideal-observer analyses, the Hierarchical Gaussian Filter (HGF), change-point detection models (Nassar et al.), or any case where learning rate is expected to *adapt* to environmental statistics rather than being a fixed parameter.

These models matter because they explain phenomena that fixed-α Rescorla-Wagner cannot — e.g., why learning rates rise after environmental change, why uncertainty about uncertainty modulates updating, why subjects' learning rates differ between stable and volatile blocks.

Canonical references: Kalman (1960) is the foundation; Daw, O'Doherty, Dayan, Seymour & Dolan (2006) for the Kalman bandit in human decision-making; Behrens, Woolrich, Walton & Rushworth (2007, *Nature Neuroscience*) for the volatility model; Mathys et al. (2011, 2014) for the HGF; Nassar et al. (2010, 2012) for change-point models.

## Why Bayesian learning models

In a stationary environment, the optimal learning rate decreases over time (you accumulate evidence). In a volatile environment, the optimal learning rate stays high (the world keeps changing). Rescorla-Wagner with a fixed α can't do this — it gives the same update regardless of what the agent thinks about the environment's stability.

Bayesian learning models track *uncertainty* explicitly, and derive their effective learning rate from that uncertainty. This is normatively correct, fits human behavior better in volatile environments, and predicts that effective learning rate should rise after change points (which it does, both behaviorally and in pupil/ACC signals).

## Kalman filter for bandits — the basic case

Treats each arm's reward as a Gaussian random walk; the agent maintains a mean and variance for each arm's value and updates them via Bayes rule. For the restless 4-armed bandit (Daw et al. 2006), this is the standard model.

State equations (per arm):

$$\mu_t = \mu_{t-1} + \text{innovation}, \quad \text{innovation} \sim N(0, \sigma_d^2)$$

$$r_t = \mu_t + \text{observation noise}, \quad \text{noise} \sim N(0, \sigma_o^2)$$

For the chosen arm at trial `t`, given the prior `N(μ̂_{t-1}, σ̂²_{t-1} + σ_d²)`:

- Posterior mean: `μ̂_t = μ̂_{t-1} + K_t · (r_t - μ̂_{t-1})`
- Kalman gain: `K_t = (σ̂²_{t-1} + σ_d²) / (σ̂²_{t-1} + σ_d² + σ_o²)`
- Posterior variance: `σ̂²_t = (1 - K_t) · (σ̂²_{t-1} + σ_d²)`

Unchosen arms: just inflate variance by `σ_d²` (no observation, but the world drifted).

The Kalman gain `K_t` is the *effective* learning rate on trial `t`. It's high when uncertainty is high (more weight on new data), low when uncertainty is low (more weight on prior). This is the key adaptive behavior.

Free parameters per subject: `σ_d` (diffusion noise — how fast the world is changing), `σ_o` (observation noise), initial mean and variance for each arm, plus whatever choice rule (softmax β, possibly directed exploration bonus).

### Directed exploration in Kalman bandits

Daw et al. (2006) showed humans don't just maximize expected value — they also seek information. The standard fit adds an exploration bonus that scales with posterior uncertainty:

$$V_i^{eff} = \mu_i + \phi \cdot \sigma_i$$

`φ` is the exploration bonus parameter. Positive `φ` = uncertainty-seeking (directed exploration); negative `φ` = uncertainty-averse.

This is then plugged into softmax. The model captures both random exploration (via β) and directed exploration (via φ). Wilson, Geana, White, Ludvig & Cohen (2014) and Gershman (2018) extend this approach.

### Stan code (sketch)

```stan
model {
  // per subject, per trial
  vector[K] mu = mu_init;
  vector[K] sigma2 = rep_vector(sigma2_init, K);
  for (t in 1:T) {
    vector[K] V_eff = mu + phi * sqrt(sigma2);  // exploration bonus
    choice[t] ~ categorical_logit(beta * V_eff);
    
    // Update: prior variance for chosen arm includes diffusion
    real prior_var_chosen = sigma2[choice[t]] + sigma_d^2;
    real K_gain = prior_var_chosen / (prior_var_chosen + sigma_o^2);
    
    mu[choice[t]]    += K_gain * (reward[t] - mu[choice[t]]);
    sigma2[choice[t]] = (1 - K_gain) * prior_var_chosen;
    
    // Unchosen arms: diffuse only
    for (k in 1:K) {
      if (k != choice[t]) sigma2[k] += sigma_d^2;
    }
  }
}
```

## Behrens volatility model (HGF lite)

**Behrens, Woolrich, Walton & Rushworth (2007).** Subjects in a probabilistic reversal task implicitly track not just the current reward probability `p` but also the *volatility* `v` of that probability — how fast `p` is changing. When `v` is high (frequent reversals), `p` updates faster; when `v` is low (stable blocks), `p` updates more conservatively.

The model is a 3-level hierarchical Bayes:
- **Level 1:** observed outcome (binary reward).
- **Level 2:** `p`, the underlying reward probability, drifts according to a Gaussian random walk with step-size determined by `v`.
- **Level 3:** `v`, the log-volatility, itself drifts according to a slower random walk.

Approximate inference (Behrens et al. used a particle filter; subsequent work has used the variational HGF by Mathys et al.) produces trial-by-trial estimates of `p`, `v`, and their uncertainties. These have been mapped onto ACC and other regions in fMRI.

**When to use it:** when your design has changing reward probabilities and you want to argue that subjects adaptively scale learning rate. The Behrens model fits this paradigm better than constant-α RW.

**Practical implementation:** The full model has no closed-form likelihood and requires either particle filtering or variational approximation. The HGF (see next section) is the modern, more tractable version. Don't roll your own — use the toolbox.

## Hierarchical Gaussian Filter (HGF)

**Mathys, Daunizeau, Friston & Stephan (2011); Mathys et al. (2014).** A generalization of the Behrens model with an analytic variational approximation, making it tractable for behavioral fitting and fMRI analysis.

The HGF is structured as a hierarchical chain of states, each evolving as a Gaussian random walk whose step-size is controlled by the next level up. The variational approximation gives closed-form update equations that resemble RW with adaptive learning rates and precision-weighted prediction errors. This is the appeal: an ideal-observer model that "lands" on equations interpretable as a more sophisticated RW.

**Free parameters:** `ω` (tonic volatilities at each level), `κ` (coupling between levels), `θ` (volatility of the top level), plus an observation/decision model on top (usually softmax or unit-square sigmoid).

**Implementations:**
- **TAPAS toolbox** (`tapas_hgf`, MATLAB/Python) — the canonical implementation by Mathys et al.
- **`hgf` R package** — wraps TAPAS for R users.
- **PyHGF** — newer Python implementation with PyMC/JAX backends.

**When to use:** when the user explicitly wants the HGF — or when the design demands trial-by-trial belief and uncertainty regressors, e.g., for model-based fMRI in a probabilistic task. For pure behavioral modeling, vanilla RW or Kalman bandits usually suffice and are easier to defend.

**Be aware:** the HGF has many parameters and known recovery issues, especially for `θ`. Always run parameter recovery before drawing parameter-level conclusions. Mathys et al. recommend specific priors that constrain the model to behavior; respect those defaults unless you have a reason not to.

## Change-point and surprise-based models

**Nassar, Wilson, Heasly & Gold (2010); Nassar et al. (2012)** — change-point models for predictive inference tasks. The agent infers when the underlying mean has changed, and resets its estimate after detected change points.

The key equation is a "change-point probability" `Ω_t` (probability that a change occurred at trial `t`), and the effective learning rate becomes a mixture:

$$\alpha_t^{\text{eff}} = \Omega_t + (1 - \Omega_t) \cdot \alpha_{\text{baseline},t}$$

where `α_baseline` decreases over time within a stable run. After a change point, the learning rate spikes to 1 (full reset).

**When to use:** when your task has discrete, identifiable change points and you want to argue subjects detect and respond to them. Pupil dilation correlates beautifully with `Ω_t`, making this a popular model for arousal/uncertainty studies (Joshi et al. 2016; Sales et al. 2019).

## Descriptive vs normative analysis of block-wise learning rates

A common pattern: a user fits Rescorla-Wagner with separate α parameters for a volatile block and a stable block, finds α_volatile > α_stable, and interprets this as evidence that subjects "adapt their learning rate."

**This is a descriptive finding, not a normative one.** The distinction matters:

- **Descriptive claim:** "Fitting RW independently to each block yields a higher α in the volatile block." This is a summary of the data under one model. It says nothing about *why* the learning rate appears higher, and the fitted α values will shift if the model is misspecified (e.g., no perseveration term, wrong reward scaling).

- **Normative claim:** "Subjects track volatility the way an optimal Bayesian agent would." This requires fitting a model with *explicit volatility inference* — one where the effective learning rate adapts as a consequence of the internal computation:
  - **Behrens et al. (2007):** the agent estimates both reward probability `p` and volatility `v`; learning rate rises in volatile blocks because the Bayesian computation says to weight new data more heavily.
  - **Kalman filter:** Kalman gain adapts automatically to posterior uncertainty; higher uncertainty → higher effective learning rate. Parameters: diffusion noise `σ_d` and observation noise `σ_o`.
  - **HGF:** same logic, generalized to multiple levels of hierarchy.

To make the normative claim, you must:
1. Fit the normative model (Behrens/Kalman/HGF) to the data.
2. Show it fits better than fixed-α RW on held-out data (PSIS-LOO or WAIC).
3. Verify that the model's latent volatility/uncertainty tracks the block structure you designed.

If you only have the per-block α comparison, you have a descriptive result — report it as such. Saying "subjects adaptively scaled learning rate" implies the normative model was tested.

## A note on the cost-benefit ratio

These Bayesian models are powerful but more complicated to fit than RW or Q-learning. The decision tree:

- **Is the environment plausibly volatile and does the user care about adaptive learning rates?** If yes, consider Kalman or Behrens. If no, RW is fine.
- **Is the user doing fMRI and wants belief/uncertainty regressors?** HGF or Behrens are the standard tools.
- **Is the user just fitting a stable 2-armed bandit?** RW. No Bayesian elaboration needed.
- **Is the user comparing learning across stable and volatile blocks?** Almost certainly need a Bayesian/adaptive model — RW with fixed α can't capture the block effect by design.

## Common pitfalls

- **The Kalman bandit needs the actual reward variance structure to be plausible** for the model to give sensible estimates. If rewards are bounded {0,1} and the model assumes Gaussian noise, the fit can be off — though in practice it still works decently as a normative approximation.
- **HGF parameter recovery is notoriously fiddly.** Use the TAPAS-recommended priors as a starting point; verify recovery before interpreting parameters as individual differences.
- **The Behrens volatility model and HGF can both make the *qualitative* prediction** that learning rate adapts. Distinguishing them empirically requires data with specific volatility manipulations.
- **"Bayesian learner" is not synonymous with "fits better."** On a stationary bandit, RW and Kalman are often statistically indistinguishable, and RW has fewer parameters. Use Bayesian models when the design specifically demands them.
- **Don't confuse the agent being Bayesian with the analyst being Bayesian.** You can fit a Rescorla-Wagner *agent* with hierarchical Bayesian *estimation* — they're orthogonal choices.

## Connections

- The HGF, when truncated to two levels, approximates the Kalman filter.
- The Behrens et al. model is a special case of the HGF in the binary-outcome setting.
- All of these models, in the limit of constant volatility, reduce to RW with a fixed learning rate that depends on the (assumed-constant) volatility.
- Change-point models can be derived as a particle approximation to a Bayesian inference with a discrete mixture prior on change events.

## What to report

- Specific model variant and the inference scheme (exact Bayes, variational, particle filter).
- All parameters with priors and recovered estimates.
- Whether the model produced the expected adaptive behavior in simulation (e.g., learning rate rising after change points).
- Comparison against a fixed-α baseline (it should win if you're claiming adaptivity matters).
- Trial-by-trial latent variables that were used downstream (e.g., for neural regression), with the model fits that produced them.

---

**See also:**
- `references/recovery.md` — HGF parameter recovery is notoriously fiddly; run it before individual-level interpretation.
- `references/reinforcement_learning.md` — fixed-α RW is the natural baseline; must beat it on LOO before claiming adaptive learning rates.
- `references/model_comparison.md` — Kalman/HGF vs RW comparison via PSIS-LOO.
- `references/hierarchical_stan.md` — Stan sketch for Kalman bandit; PyHGF and TAPAS for HGF.
