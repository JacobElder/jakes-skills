# Comparing Bayesian Hierarchical Models by Expected Predictive Accuracy in PyMC

## Short answer

WAIC is a reasonable starting point, but you should not rely on WAIC alone. Use `az.compare()` with both WAIC and LOO-CV (leave-one-out cross-validation via PSIS), check the diagnostics on each, and treat the comparison as reliable only after those diagnostics pass.

---

## Why not just compare WAIC values

WAIC (Watanabe-Akaike Information Criterion) estimates expected log predictive density (ELPD) for new data by correcting the in-sample log-likelihood with a penalty for effective parameter count. It is asymptotically equivalent to Bayesian LOO-CV under mild regularity conditions. That sounds reassuring, but several things can go wrong:

**1. WAIC is computed pointwise, and hierarchical models create trouble at the observation level.**

In a hierarchical model, the natural "observation" for the likelihood is often a group-level unit (e.g., a subject or a school), not a single data point. If you treat each row of data as an independent observation when groups share a random effect, you understate the effective number of parameters and get an overoptimistic ELPD estimate. Make sure the log-likelihood tensor you pass to `az.waic()` or `az.loo()` has the right observation structure — usually `(chain, draw, n_observations)` where `n_observations` matches the level at which predictions are actually independent.

**2. The WAIC penalty relies on variance across posterior draws being a good proxy for the LOO influence of each point.**

This assumption breaks down when:
- Posterior draws are poorly mixed (low ESS per observation).
- The model is misspecified in ways that produce a multimodal posterior.
- A small number of observations are highly influential (high-leverage points in a regression, rare events, outlier groups in a hierarchical model).

When it breaks down, WAIC can be badly wrong — sometimes by more than the difference between the two models you are comparing.

**3. WAIC gives you a point estimate with no uncertainty quantification by default.**

Two models can appear to differ in WAIC when the uncertainty in both estimates overlaps substantially. Comparing raw WAIC values without standard errors is like comparing two regression coefficients without their SEs.

---

## What to do instead (or in addition)

### Use PSIS-LOO as your primary metric

Pareto-smoothed importance sampling LOO (PSIS-LOO, implemented as `az.loo()` in ArviZ) is more robust than WAIC and comes with a critical diagnostic: the Pareto-k values.

```python
import arviz as az

# Fit models and extract InferenceData objects
idata1 = ...  # model 1
idata2 = ...  # model 2

loo1 = az.loo(idata1, pointwise=True)
loo2 = az.loo(idata2, pointwise=True)
```

### Check the Pareto-k diagnostic before trusting the numbers

Every observation gets a Pareto-k value. The thresholds to know:

| k range | Interpretation |
|---------|----------------|
| k < 0.5 | Good — importance weights are reliable |
| 0.5 ≤ k < 0.7 | OK — mild concern, watch these points |
| 0.7 ≤ k < 1.0 | Bad — LOO estimate for this point is unreliable |
| k ≥ 1.0 | Very bad — the importance sampling has failed |

If many observations have k ≥ 0.7, the LOO estimate is not trustworthy. ArviZ will print a warning. In that case:

- Run exact LOO-CV for the flagged observations using `az.reloo()` (refits the model leaving each problematic observation out — expensive but correct).
- Or use k-fold cross-validation instead.

```python
# Check Pareto-k values
print(loo1)           # summary including the k-hat diagnostic
az.plot_khat(loo1)    # visual inspection
```

### Use az.compare() to get uncertainty-aware comparison

```python
comparison = az.compare(
    {"model1": idata1, "model2": idata2},
    ic="loo",           # or "waic"
    method="stacking",  # or "BB-pseudo-BMA" for Bayesian model averaging weights
    scale="log"         # ELPD on log scale
)
print(comparison)
```

The output includes:
- **elpd_loo**: estimated ELPD (higher is better)
- **p_loo**: effective number of parameters
- **elpd_diff**: difference relative to the best model
- **dse**: standard error of the *difference* (this is what matters for significance)
- **warning**: flag if Pareto-k diagnostics failed

The `dse` column is critical. A difference of 4 ELPD points sounds meaningful, but if `dse` is 6, it is not. The rule of thumb: a difference is practically meaningful when `|elpd_diff| > 4 * dse`.

---

## Additional checks before trusting the comparison

### 1. Confirm convergence in both models

A model with poor mixing produces a biased posterior, which contaminates the log-likelihood calculations underpinning both WAIC and LOO. Check:

```python
az.summary(idata1, var_names=["~log_likelihood"])  # R-hat, ESS
```

R-hat should be < 1.01 for all parameters. Bulk and tail ESS should be > 400 (ideally > 1000). If a model has not converged, fix convergence before comparing.

### 2. Check that the log-likelihood is stored correctly

ArviZ computes WAIC/LOO from the `log_likelihood` group of your InferenceData object. In PyMC, this is populated when you use `pm.sample_posterior_predictive()` with `extend_inferencedata=True` and `pm.compute_log_likelihood()`.

```python
with model1:
    idata1 = pm.sample()
    pm.compute_log_likelihood(idata1)
```

If the log-likelihood group is missing or has the wrong shape, ArviZ will either error or silently compute nonsense.

### 3. Verify that both models use the same likelihood and observation structure

WAIC and LOO compare models on the same predictive task. If model 1 predicts at the individual level and model 2 predicts at the group level, the ELPD scores are not comparable — they measure different things.

### 4. Understand what the comparison is telling you

WAIC/LOO compare **predictive accuracy**, not truth. A model can have better LOO-ELPD because it fits the data better (good) or because it overfits idiosyncratic features of your sample (bad, and LOO is supposed to correct for this, but imperfectly). If the winning model is much more complex, inspect `p_loo`: a suspiciously large effective parameter count can flag pathological behavior.

---

## Practical workflow summary

1. Fit both models; call `pm.compute_log_likelihood()` on each InferenceData.
2. Check R-hat and ESS — fix convergence issues first.
3. Run `az.loo(idata, pointwise=True)` on each model; inspect Pareto-k values.
4. If k < 0.7 for essentially all observations, the LOO estimate is reliable.
5. If flagged observations exist, run `az.reloo()` or note the caveat.
6. Call `az.compare({"m1": idata1, "m2": idata2}, ic="loo")`.
7. Interpret using `elpd_diff` and `dse` together, not ELPD in isolation.

WAIC and LOO will usually agree on which model is better when diagnostics pass. When they disagree substantially, trust LOO — WAIC has no built-in reliability diagnostic, while the Pareto-k values give you something concrete to act on.
