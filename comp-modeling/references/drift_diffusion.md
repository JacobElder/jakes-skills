# Drift-Diffusion and Sequential Sampling Models

Read this when the user is modeling two-choice (or multi-choice) decisions with reaction time data — perceptual decision tasks (random-dot motion, brightness discrimination), lexical decision, recognition memory, simple speeded categorization, anything where both *which* choice was made and *how long it took* are informative.

Canonical references: Ratcliff (1978) — the original DDM; Ratcliff & McKoon (2008) for the modern review; Wiecki, Sofer & Frank (2013) for HDDM; Brown & Heathcote (2008) for LBA; Pedersen & Frank (2020) for RL-DDM; Voss, Voss & Lerche (2015) for diagnostics.

## What the DDM models

The drift-diffusion model treats a two-alternative speeded choice as a noisy accumulation of evidence over time toward one of two thresholds. The decision time is the first-passage time to a boundary; the choice is which boundary is hit. The model jointly fits the choice and the entire RT distribution — that's its power.

Free parameters of the basic DDM:

- **`v` — drift rate.** Average rate of evidence accumulation. Higher |v| means faster, more accurate decisions. v > 0 means evidence drifts toward the upper boundary (typically "correct"); v < 0 toward the lower. Units: evidence per second.
- **`a` — boundary separation.** Distance between the two decision thresholds. Higher `a` means more cautious — slower, more accurate. The classic "speed-accuracy tradeoff" knob.
- **`z` — starting point.** Where the accumulator begins, expressed as a proportion of `a` (0 < z < 1). z = 0.5 is unbiased. z > 0.5 means a bias toward the upper boundary, which produces faster and more frequent upper-boundary responses.
- **`t` — non-decision time** (Ter). The portion of RT not spent accumulating — encoding the stimulus and executing the motor response. Subtracted from RT before fitting.

These four are the "main" parameters. The full DDM adds three inter-trial variability parameters that capture distributional features the basic model misses:

- **`sv` — variability in drift across trials.** Explains the slow-error pattern (errors are slower than correct responses at high difficulty).
- **`sz` — variability in starting point across trials.** Explains fast errors at easy conditions.
- **`st` — variability in non-decision time.** Smooths the leading edge of the RT distribution.

The trade-off: the inter-trial variabilities make the model fit better at the cost of estimation stability. Default for most applications: fix sv, sz, st to zero unless you have lots of data per condition. HDDM lets you estimate them at the group level only (subject-level fixed to group mean) as a compromise.

## When to use DDM vs alternatives

- **DDM** — the default for binary speeded decisions. Closed-form likelihood (Navarro & Fuss 2009 series approximation) makes it fast. Constraint: two response options only (extensions exist but are clunky).
- **LBA — Linear Ballistic Accumulator** (Brown & Heathcote 2008) — race between deterministic accumulators with between-trial variability. No within-trial noise. Naturally handles N > 2 alternatives. Closed-form likelihood. Often preferred for multi-choice tasks.
- **Race models / RDM** — N independent stochastic accumulators racing to threshold. Likelihood usually not closed-form; needs simulation-based methods.
- **Leaky competing accumulator (LCA, Usher & McClelland 2001)** — accumulators with leak and lateral inhibition. More biologically motivated; harder to fit; usually requires sbi/BayesFlow.
- **EZ-diffusion** (Wagenmakers, van der Maas, Grasman 2007) — analytic formulas for `v`, `a`, `t` from mean RT, RT variance, and accuracy. Trivially fast, useful as a sanity check. Doesn't fit RT distributions, just summary stats.
- **RL-DDM** (Pedersen & Frank 2020; Fontanesi et al. 2019; Frank et al. 2015) — DDM with the drift rate driven by Q-value differences that update by RL. Now standard for instrumental learning tasks where RTs matter.

## What the DDM is *not* for

- Free-response tasks (>2 s untimed). DDM assumes RT < ~3 s and that the response is the result of evidence reaching threshold; long decisions involve different processes.
- Tasks with strong response collapsing or urgency signals. Standard DDM has constant boundaries; collapsing-bound variants exist but require simulation-based fitting.
- Very fast decisions (< ~250 ms) where non-decision time swamps the decision time. The model can be fit but interpretations are dubious.
- Tasks where the user only cares about accuracy, not RTs. Then a logistic GLM or RL model is simpler.

## How to map parameters to manipulations

The DDM's appeal in cognitive neuroscience is that manipulations map cleanly onto specific parameters:

- **Stimulus discriminability / signal strength → drift rate `v`.** Easier trials = higher |v|.
- **Speed/accuracy instructions → boundary `a`.** Speed instructions reduce `a`.
- **Response bias (asymmetric reward, prior probability) → starting point `z`** OR **drift bias** (additive offset to v). These two can produce similar bias signatures but predict different RT-distribution shifts; you usually want to test both.
- **Stimulus encoding difficulty (e.g., perceptual masking) → non-decision time `t`.**
- **Attention / state effects → can go to several places.** Be explicit about which parameter you think is moving and why.

Standard reporting practice: fit a model where the manipulation affects each candidate parameter, compare via DIC/WAIC/LOO, interpret the winner. HDDM makes this trivial via its regression interface.

## Using HDDM (the default for Bayesian DDM fits)

HDDM is the de facto standard. Basic usage:

```python
import hddm

# Data: pandas DataFrame with columns 'subj_idx', 'response' (0/1), 'rt' (seconds, > 0)
m = hddm.HDDM(data, include=('sv',))   # add inter-trial variability in drift
m.find_starting_values()
m.sample(2000, burn=500, dbname='trace.db', db='pickle')

# Inspect
stats = m.gen_stats()
print(stats[['mean', 'std', '2.5q', '97.5q']])

# Convergence
hddm.utils.compare_models([m1, m2], method='DIC')
```

Regression interface for condition effects:

```python
m_reg = hddm.HDDMRegressor(data, 'v ~ stim_strength + C(condition)', include=('sv',))
m_reg.sample(2000, burn=500)
```

For learning tasks where drift varies trial-by-trial based on Q-value differences:

```python
from hddm.models import HDDMrl
m_rl = HDDMrl(data, include=('v', 'a', 't', 'alpha'))
m_rl.sample(2000, burn=500)
```

A few important notes:
- HDDM expects RTs in **seconds**, not ms.
- HDDM codes the response either as 0/1 (and you tell it which boundary maps to "correct") or as signed RT (negative for lower-boundary responses). The conventions matter for `v` interpretation.
- For multi-condition models, use `depends_on={'v': 'condition'}` for legacy syntax or the regression interface for anything more complex.
- Inter-trial variability priors are informative by default — this is what stabilizes estimation. Don't override unless you know what you're doing.

## A custom DDM likelihood in Stan

For fully custom models, Stan has a built-in `wiener_lpdf` for the Wiener first-passage time likelihood:

```stan
data {
  int<lower=1> N;
  array[N] real<lower=0> rt;
  array[N] int<lower=0, upper=1> response;  // 1 = upper, 0 = lower
}
parameters {
  real<lower=0> alpha;             // boundary separation 'a'
  real<lower=0> tau;               // non-decision time 't'
  real<lower=0, upper=1> beta;     // relative starting point 'z' (in [0,1])
  real delta;                      // drift rate 'v'
}
model {
  alpha ~ normal(1.5, 0.5);
  tau   ~ normal(0.3, 0.1);
  beta  ~ beta(2, 2);
  delta ~ normal(0, 2);
  for (n in 1:N) {
    if (response[n] == 1)
      rt[n] ~ wiener(alpha, tau, beta, delta);
    else
      rt[n] ~ wiener(alpha, tau, 1 - beta, -delta);  // flip for lower boundary
  }
}
```

Note the boundary flip: Stan's `wiener_lpdf` is defined for first-passage to the upper boundary; for lower-boundary responses, flip the sign of `delta` and use `1 - beta`.

For hierarchical Bayesian DDM at scale, HDDM is faster and battle-tested. Write Stan only when you need a custom likelihood that HDDM doesn't support.

## Parameter ranges to expect

From decades of fits (Ratcliff & McKoon 2008; Voss et al. 2013):

- **`v`**: typically -3 to 3 for standardized tasks; sign depends on coding
- **`a`**: 0.8 to 2.5; speed-stressed tasks lower, accuracy-stressed higher
- **`t`**: 0.2 to 0.6 seconds; perceptual tasks faster, memory tasks slower
- **`z`**: 0.4 to 0.6 absent strong bias; rare to see outside 0.3–0.7
- **`sv`**: 0 to ~2
- **`sz`**: 0 to ~0.3
- **`st`**: 0 to ~0.2

Estimates wildly outside these ranges usually mean a coding issue (RT in ms not s; response coded wrong; outliers not filtered).

## Required data preprocessing

Standard DDM analysis requires:

- RT in seconds, > 0, typically truncated at a reasonable maximum (e.g., 3 s). Anything beyond is treated as outlier or contaminated.
- Fast outlier exclusion: cut RTs < ~150–200 ms; these are usually anticipations and violate the model.
- Slow outlier handling: either cut (e.g., > mean + 3 SD per subject) or model contaminants explicitly (HDDM has `p_outlier` for this).
- Sufficient trials: rule of thumb, > 50–100 per condition for stable per-subject DDM. For hierarchical fits you can get away with fewer per subject because of shrinkage; 20–30 may suffice.

## Common pitfalls in DDM fitting

- **RT in ms instead of seconds.** Everyone makes this mistake once. The fit will look terrible. Check units first.
- **Conflating boundary separation and non-decision time.** Both add to mean RT; the model identifies them through the *shape* of the RT distribution. If your task has narrow RT range (e.g., everyone responds in 400–600 ms), `a` and `t` will be poorly identified.
- **Estimating all three inter-trial variabilities by default.** This is asking for trouble. Start with sv only, add others only if there's a specific need. HDDM defaults to estimating all three at the group level — overriding to group-only is often the right call for smaller datasets.
- **Starting point bias vs drift bias.** Both can produce response asymmetry. They differ in how they affect the RT distribution. If you have a bias, fit both and compare; don't just assume one.
- **Fast errors vs slow errors.** Fast errors implicate starting-point variability or low drift; slow errors implicate drift variability. The model fits these endogenously, but if you see the wrong pattern in residuals, your model is missing structure.
- **Mixing trial types without separating drift.** If your task has easy and hard trials and you fit one drift across them, the model will average — and the fit will be terrible. Always let `v` vary by condition.
- **Outlier RTs swamp the fit.** Without preprocessing or `p_outlier`, a single 10 s response can shift `t` enormously. Always trim or model contaminants.
- **Comparing nested DDMs without WAIC/LOO.** Likelihood-ratio tests are technically valid for nested DDM variants but ignore the prior. WAIC/LOO via HDDM-with-`log_lik` is the modern standard.

## RL-DDM in more detail

The natural extension when you have a learning task with RT data. The trial-by-trial drift rate is a function of the (RL-updated) value difference:

$$v_t = v_{mod} \cdot (Q_{upper,t} - Q_{lower,t})$$

where `v_mod` is a free scaling parameter and Q-values update via standard RL. This means a single integrated model captures both choice (via the boundary hit) and RT (via the first-passage time), with the value difference doing dual duty.

`HDDMrl` in HDDM 0.9+ implements this with the basic RW + softmax-replaced-by-DDM. Pedersen & Frank (2020) is the tutorial. Be aware:

- Convergence is harder than vanilla DDM; expect to tune adapt_delta.
- Parameter recovery for `v_mod` is touchy; verify on simulated data first.
- The combined model usually beats separate RL-then-DDM on LOO, but only if both pieces have enough data.

## Posterior predictive checks for DDM

The standard PPC: simulate RTs from the fitted model and compare to data on:

- **RT quantiles by condition and response** (0.1, 0.3, 0.5, 0.7, 0.9 quantiles, separately for correct and incorrect).
- **Accuracy by condition.**
- **Mean RT by condition × correctness.**
- **The leading edge of the RT distribution** — if simulated RTs are systematically too slow at the fast end, `t` or `st` is off.
- **The tail** — if simulated RTs are too short at the slow end, `sv` may be needed.

HDDM has `m.plot_posterior_predictive()` for this.

## Diagnostic checklist before reporting a DDM fit

- All R-hat < 1.01? (`m.gelman_rubin()`)
- ESS > 400 for parameters of interest?
- No divergent transitions if using HMC?
- PPC reproduces RT quantiles? (`m.plot_posterior_predictive()`)
- Parameter recovery confirmed on simulated data with the same trial counts?
- Drift rate ordered as expected by stimulus condition?
- Group-level effect sizes meaningful relative to between-subject SDs?

If any of these fail, debug before reporting.

---

**See also:**
- `references/recovery.md` — drift/boundary trade-off when RT range is narrow; recovery at realistic trial counts.
- `references/model_comparison.md` — WAIC/LOO for comparing DDM variants (e.g., fixed vs variable inter-trial drift).
- `references/hierarchical_stan.md` — Stan `wiener_lpdf` template for custom DDM likelihoods; convergence debugging.
- `references/reinforcement_learning.md` — for RL-DDM (trial-by-trial drift from Q-value differences); `HDDMrl`.
