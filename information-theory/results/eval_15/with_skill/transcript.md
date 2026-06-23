# Comparing Bayesian Hierarchical Models by Expected Predictive Accuracy

Short answer: **don't just compare WAIC — prefer PSIS-LOO, and run the Pareto k̂ diagnostic before trusting either number.** Here is the full picture.

---

## What WAIC is actually estimating

Every model-selection criterion here is trying to estimate the same thing: **expected log predictive density on new data from the same process**, or equivalently, out-of-sample deviance (KL divergence from the data-generating process to your fitted model, up to a constant). In-sample log-likelihood is an optimistically biased estimate of this quantity because you fit to the noise; WAIC corrects that bias.

WAIC is defined as:

```
WAIC = −2 (lppd − p_waic)

lppd   = Σ_i log E_post[ p(y_i | θ) ]   # log pointwise predictive density
p_waic = Σ_i Var_post[ log p(y_i | θ) ] # effective number of parameters
```

Both quantities are computed from the **pointwise log-likelihood matrix** — the `(S × N)` array of `log p(y_i | θ^(s))` values drawn from your posterior. In PyMC you get this matrix via `pm.compute_log_likelihood` followed by `az.waic(idata)`.

The key difference from AIC/BIC: `p_waic` is **estimated from the posterior variance of the log-likelihood**, not by counting parameters. That is exactly what you want for hierarchical models, where "number of parameters" is not well-defined — a random-effects model with 1,000 group-level parameters can have an effective count of 3 if the groups pool heavily.

---

## Why PSIS-LOO is the modern default

PSIS-LOO (Pareto-smoothed importance sampling leave-one-out; `az.loo(idata)`) estimates the same out-of-sample expected log predictive density as WAIC, but it has one decisive advantage: **it comes with a per-observation diagnostic**.

The Pareto shape parameter k̂ is fit to the tail of the importance weights for each observation. The thresholds are:

| k̂ | Interpretation |
|---|---|
| < 0.5 | Reliable |
| 0.5 – 0.7 | OK, small bias |
| 0.7 – 1.0 | Unreliable; the importance weights have a heavy tail |
| > 1.0 | Very unreliable; mean may not exist |

When k̂ > 0.7 for a meaningful fraction of observations, PSIS-LOO is telling you the single-chain posterior is not a good proposal for leave-one-out: those points are influential enough that removing one substantially changes the posterior. That is **exactly the case where WAIC also fails** (WAIC relies on a local approximation that breaks down for influential observations) — but WAIC gives you no warning. PSIS-LOO surfaces the problem.

**Rule of thumb:** use `az.compare({"model_a": idata_a, "model_b": idata_b})` which runs PSIS-LOO with diagnostics by default. Fall back to WAIC only if there is a specific reason.

---

## Checklist before trusting the numbers

### 1. Same data, same likelihood scale

WAIC and LOO are only comparable across models fit to **identical observations with the same response variable**. If one model transforms `y` (e.g., log-transforms it) and the other does not, the log-likelihoods live on different scales and the comparison is meaningless. Both models must predict the same `y_i` values.

This applies equally to missing data: if listwise deletion produces different `N` per model, the numbers are not comparable. Impute or use the same complete-case dataset.

### 2. Check Pareto k̂ per observation

```python
import arviz as az

loo_a = az.loo(idata_a, pointwise=True)
loo_b = az.loo(idata_b, pointwise=True)

# Flagged observations
print((loo_a.pareto_k > 0.7).sum(), "high-k observations in model A")
print((loo_b.pareto_k > 0.7).sum(), "high-k observations in model B")
```

If you see a non-trivial number of k̂ > 0.7 flags, the LOO estimate is unreliable. Options:
- Run exact subsampling LOO for those observations (set `k_threshold` in ArviZ or do it manually).
- Use moment matching to improve the importance weights (`az.loo` with `method="psis"` and `reff` parameter).
- Refit with a more robust likelihood or heavier tails.

### 3. Check the standard error of the difference, not just the point estimate

`az.compare` returns `elpd_diff` and `se` (the standard error of the pointwise difference). The comparison is not decisive unless `|elpd_diff| > 2 × se`. A difference of 4 ELPD with SE 6 is noise.

```python
comp = az.compare({"model_a": idata_a, "model_b": idata_b})
print(comp[["elpd_loo", "se", "elpd_diff", "dse", "warning"]])
```

The `dse` column is the SE on the difference (not the SE of each model individually); use `dse` for the decision rule, not `se`.

### 4. Verify you have enough posterior samples

`p_waic` and the Pareto diagnostics are estimated from the posterior draws. With very few draws (< 500 effective samples per parameter) the variance estimates are noisy. Check `az.ess_bulk(idata)` for the key parameters. PyMC defaults are usually fine; just don't subsample aggressively before computing.

### 5. WAIC and LOO are not goodness-of-fit tests

A model that "wins" the comparison may still be badly calibrated in absolute terms. Pair the comparison with:
- **Posterior predictive checks** (`az.plot_ppc`) to check that the winning model's posterior predictive distribution actually covers the data.
- **Calibration checks** if the models are used for probability outputs.

A lower WAIC/higher ELPD means "less bad than the alternative on this dataset," not "good."

---

## What to report

Show a table, not just a winner:

```python
comp = az.compare({"model_a": idata_a, "model_b": idata_b}, ic="loo")
print(comp)
```

This gives you `elpd_loo`, `p_loo` (effective parameters), `elpd_diff`, `dse`, and a `warning` flag for high-k̂ observations. Present the full table so readers can see how decisive the comparison is. A difference of `|ΔELPD| < 2` is effectively a tie.

---

## Summary

| Step | What to do |
|---|---|
| **Criterion** | Use PSIS-LOO (`az.loo`) by default, not WAIC — same target, but with a diagnostic |
| **Same data** | Confirm both models are fit to identical observations on the same scale |
| **Pareto k̂** | Flag and handle observations with k̂ > 0.7 before trusting the comparison |
| **SE on the difference** | Use `dse` from `az.compare`; treat `|ΔELPD| < 2×dse` as indeterminate |
| **Absolute quality** | Run posterior predictive checks on the winner — LOO tells you which is better, not whether either is good |
| **If k̂ failures are widespread** | Consider resampling exact LOO for flagged points, or interpret with caution |
