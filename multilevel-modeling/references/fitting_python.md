# Fitting MLMs in Python

Python's MLM ecosystem has improved substantially but still lags R. Be honest about this with the user: for complex random-effects structures, R (lme4, brms) remains the more capable tool, and bridges like `pymer4` exist for a reason.

## Package selection

| Need | Use | Notes |
|---|---|---|
| LMM (simple) | `statsmodels.regression.mixed_linear_model.MixedLM` | Works but limited: only one random-effects grouping factor at a time (no native crossed random effects without workarounds); no Satterthwaite/KR df. |
| LMM (complex, lme4-style) | `pymer4.models.Lmer` | Wraps lme4 via rpy2. Same syntax, same capabilities. Best option for serious frequentist MLM in Python if you can install R alongside. |
| Bayesian, formula-driven | `bambi` | Uses PyMC backend, lme4-style formulas. Closest Python equivalent to brms. |
| Bayesian, full control | `PyMC` directly | More flexible but you write the model. Use for non-standard structures. |
| Bayesian alternative | `numpyro` | Faster MCMC via JAX. Less mature ecosystem. |
| GEE (marginal/pop-avg alternative) | `statsmodels.gee.GEE` | Not MLM, but worth knowing about for the "I just want population-average effects" case. |

## statsmodels MixedLM

Adequate for simple two-level models. Limitations to be aware of upfront:

- One grouping factor at a time via `groups`. Multiple grouping factors and crossed random effects require a `vc_formula` workaround.
- No Satterthwaite or Kenward-Roger degrees of freedom; *p*-values use a Wald approximation with a degrees-of-freedom heuristic. Less reliable for small numbers of clusters.
- REML is the default; switch with `reml=False` for LRTs of fixed effects.

### Basic two-level random intercept + slope

```python
import statsmodels.formula.api as smf

model = smf.mixedlm(
    "rt ~ condition * distractor",
    data=d,
    groups=d["subject"],
    re_formula="1 + condition * distractor",  # random slopes
)
fit = model.fit(reml=True, method="lbfgs")
print(fit.summary())
```

### Crossed random effects (subjects × items) — workaround

statsmodels doesn't support this natively. The workaround uses variance-components formulas, but it's clunky:

```python
import statsmodels.formula.api as smf

# Code subject and item as variance components
vc = {"subject": "0 + C(subject)", "item": "0 + C(item)"}
model = smf.mixedlm(
    "rt ~ condition * distractor",
    data=d,
    groups=np.ones(len(d)),  # dummy grouping
    vc_formula=vc,
    re_formula="0",
)
fit = model.fit()
```

This works for random intercepts on crossed factors but is awkward for crossed random slopes. **For non-trivial crossed designs, use `pymer4` or `bambi` instead.**

### Singular fits and convergence in statsmodels

`fit.converged` is the flag to check. If False, try:

- `method="bfgs"` or `method="cg"` instead of default `lbfgs`
- Center and scale predictors
- Reduce the random-effects structure (per the principled order in `random_effects_specification.md`)

statsmodels doesn't expose nice singularity diagnostics. Look at the random-effects covariance manually: `fit.cov_re`.

## pymer4 — lme4 from Python

If you have R installed alongside Python, `pymer4` gives you lme4's full power with a Python interface. **Strongly recommended over statsmodels for any non-trivial MLM in Python.**

```python
from pymer4.models import Lmer

fit = Lmer(
    "rt ~ condition * distractor + "
    "(1 + condition * distractor | subject) + "
    "(1 + condition | item)",
    data=d,
)
fit.fit(REML=True, control="optimizer='bobyqa'")
print(fit.summary())

# Random effects, ICC, predictions, etc., all work like lme4
print(fit.ranef)
print(fit.coefs)
```

`pymer4` reports lmerTest Satterthwaite *p*-values by default. Singular fits, `rePCA`, and the rest of lme4's diagnostic apparatus are available.

Installation requires R + lme4 + lmerTest installed and accessible from rpy2. Worth the setup cost.

## bambi — Bayesian MLM with lme4 syntax

`bambi` is the Python brms equivalent: lme4-style formulas, PyMC backend, sensible defaults for priors.

```python
import bambi as bmb

model = bmb.Model(
    "rt ~ condition * distractor + "
    "(1 + condition * distractor | subject) + "
    "(1 + condition | item)",
    data=d,
    family="gaussian",
)

# Inspect default priors before fitting
model.build()
print(model)

# Customize priors if needed
priors = {
    "condition": bmb.Prior("Normal", mu=0, sigma=100),
    "Intercept": bmb.Prior("Normal", mu=d["rt"].mean(), sigma=d["rt"].std() * 2),
}
model = bmb.Model(formula, data=d, priors=priors, family="gaussian")

idata = model.fit(
    draws=2000,
    tune=1000,
    chains=4,
    target_accept=0.95,  # bump up if you get divergences
)

import arviz as az
az.summary(idata)
az.plot_trace(idata)
```

bambi handles maximal random-effects structures gracefully — priors regularize the variance components, so singular fits are not the same problem they are in lme4. This is the cleanest Python option for serious work. See `bayesian_workflow.md` for full Bayesian guidance.

## PyMC directly

When you need a non-standard model (custom likelihoods, complex random-effects covariance structures, measurement-error models, IRT-MLM hybrids), build it in PyMC directly. Sketch of a two-level model with crossed random intercepts:

```python
import pymc as pm
import numpy as np

with pm.Model() as model:
    # Fixed effects
    beta = pm.Normal("beta", mu=0, sigma=10, shape=n_predictors)
    
    # Random effects: by-subject and by-item intercepts
    sigma_subj = pm.HalfNormal("sigma_subj", sigma=10)
    sigma_item = pm.HalfNormal("sigma_item", sigma=10)
    u_subj = pm.Normal("u_subj", mu=0, sigma=sigma_subj, shape=n_subjects)
    u_item = pm.Normal("u_item", mu=0, sigma=sigma_item, shape=n_items)
    
    # Residual
    sigma_y = pm.HalfNormal("sigma_y", sigma=10)
    
    # Likelihood
    mu = X @ beta + u_subj[subject_idx] + u_item[item_idx]
    y_obs = pm.Normal("y_obs", mu=mu, sigma=sigma_y, observed=y)
    
    idata = pm.sample(2000, tune=1000, chains=4, target_accept=0.95)
```

For random slopes with correlations, use a multivariate normal with an LKJ prior on the correlation matrix — see `bayesian_workflow.md`.

## ICC and variance components

```python
# For statsmodels
var_re = fit.cov_re.iloc[0, 0]  # random intercept variance
var_resid = fit.scale            # residual variance
icc = var_re / (var_re + var_resid)

# For pymer4
fit.ranef_var

# For bambi/PyMC, compute from posterior samples
import arviz as az
posterior = idata.posterior
icc_samples = posterior["1|subject_sigma"]**2 / (
    posterior["1|subject_sigma"]**2 + posterior["sigma"]**2
)
az.hdi(icc_samples)
```

## Diagnostics

For frequentist fits (statsmodels, pymer4), the same principles as R apply: residual plots at each level, level-2 residual (random effect) inspection, influential-cluster checks.

For Bayesian fits via bambi/PyMC, use `arviz`:

```python
az.plot_trace(idata)
az.plot_energy(idata)
az.summary(idata, hdi_prob=0.95)
az.plot_ppc(idata)  # posterior predictive checks
az.plot_loo_pit(idata)
```

R-hat should be < 1.01, ESS should be in the hundreds at minimum. Divergent transitions indicate posterior geometry problems — see `bayesian_workflow.md` for remedies.

## A complete example (Python, bambi)

```python
import bambi as bmb
import arviz as az
import pandas as pd

d = pd.read_csv("experiment.csv")

# Sum coding for factors
d["condition"] = pd.Categorical(d["condition"])
d["distractor"] = pd.Categorical(d["distractor"])

# Maximal random-effects structure
model = bmb.Model(
    "rt ~ condition * distractor + "
    "(1 + condition * distractor | subject) + "
    "(1 + condition | item)",  # distractor between-items
    data=d,
    family="gaussian",
)

idata = model.fit(
    draws=2000, tune=2000, chains=4,
    target_accept=0.95,
    random_seed=42,
)

# Diagnostics
print(az.summary(idata, var_names=["~_"], filter_vars="like"))
az.plot_trace(idata, var_names=["condition", "distractor"])

# Posterior predictive check
model.predict(idata, kind="response")
az.plot_ppc(idata)
```

## When to use Python vs R for MLM

Honest assessment to share with users:

- **Use R** if you're doing frequentist MLM with complex random-effects structures (crossed, multiple slopes, custom contrasts) and you don't have an existing Python pipeline.
- **Use bambi/PyMC** if you're Bayesian-first or already in a Python ecosystem and want one language. bambi is genuinely good.
- **Use pymer4** if you must be in Python but need lme4's full frequentist capability.
- **Use statsmodels MixedLM** only for simple two-level models with one grouping factor. Beyond that it gets painful.
