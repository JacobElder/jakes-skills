# Do Not Report These Results

No — you should not report these results. The model specification you used is almost certainly **degenerate**, which means the MCMC chain did not explore the true posterior and the coefficients — including that triangle = 0.85, p < 0.001 — are artifacts, not estimates. Reporting them would be misleading regardless of their nominal significance.

Here is exactly what is wrong and how to fix it.

---

## The core problem: `triangle` and `kstar(2)` cause degeneracy

The `triangle` term counts closed triads. Because tie formation is dyadic-dependent, the conditional log-odds of any single tie includes a term that grows with the number of existing triangles involving those nodes. A positive coefficient creates a positive-feedback loop:

> more triangles → higher tie probability → more ties form → more triangles → ... → complete graph (or collapse to empty graph)

The MCMC-MLE cannot find a stable region of the parameter space. It either diverges toward a near-complete graph or collapses to near-empty. The distribution implied by the fitted parameters places almost all probability mass on these degenerate extremes — not on graphs that look like your friendship network.

`kstar(2)` has the same problem: degree-based terms with no marginal decay similarly explode.

The significant p-values you see are not evidence of transitivity. They are an artifact of a non-converged MCMC chain. The reported standard errors and p-values are meaningless when the chain has not explored the distribution correctly.

**This is one of the most common errors in ERGM analysis** — the `triangle` term looks reasonable, the model runs without throwing an error, and the output looks like any other regression table. The failure mode is silent.

---

## The fix: geometrically weighted statistics

The solution, established by Snijders, Pattison, Robins & Handcock (2006) and Hunter & Handcock (2006), is to replace monotonic structural terms with **geometrically weighted** analogs that impose decreasing marginal returns:

| Your term | Replace with | Why |
|---|---|---|
| `triangle` | `gwesp(decay, fixed=TRUE)` | Each additional shared partner contributes geometrically less than the last — breaks the feedback loop |
| `kstar(2)` | `gwdegree(decay, fixed=TRUE)` | Captures degree heterogeneity without explosive degree effects |

`gwesp` (geometrically weighted edgewise shared partners) is the correct term for transitivity. The decay parameter α (typically 0.25–0.75) controls how fast the per-partner contribution diminishes. Start with `decay=0.5` fixed. You can estimate the decay rather than fix it, but estimating it from a single cross-sectional network is often unstable — fix it unless you have strong theoretical reason to estimate it.

---

## Corrected R code

```r
library(statnet)

fit <- ergm(net ~ edges +
                  gwesp(decay = 0.5, fixed = TRUE) +   # transitivity — NOT triangle
                  gwdegree(decay = 0.5, fixed = TRUE) + # popularity/degree spread — NOT kstar(2)
                  nodematch("gender"),                  # gender homophily
            control = control.ergm(
              MCMC.samplesize = 10000,
              MCMC.burnin     = 10000,
              MCMLE.maxit     = 20
            ))

summary(fit)

# Non-optional diagnostics
mcmc.diagnostics(fit)   # check for convergence
gof_obj <- gof(fit)     # check model fit
plot(gof_obj)
```

Build up from a simpler baseline rather than fitting the full model immediately:

1. Start with `edges + nodematch("gender")` — these are dyadic-independent terms and cannot cause degeneracy
2. Add `gwesp` — run diagnostics before continuing
3. Add `gwdegree` — run diagnostics again
4. Only add further terms after confirming each step converges

---

## Diagnostics that are not optional

Two checks are required before you can interpret any ERGM output:

**`mcmc.diagnostics(fit)`** — examine trace plots for each parameter. Converged chains look like stationary noise around a stable mean; autocorrelation should decay quickly. Chains that drift, spike, or show slow mixing indicate the model has not converged. If you see this, do not report anything.

**`gof(fit)`** — simulates many graphs from your fitted model and compares their degree distributions, edgewise shared partner distributions, and geodesic distance distributions to your observed network. A model with "significant" coefficients but poor GoF is misspecified — it may converge numerically but still fail to describe your data. Both diagnostics must pass.

---

## One additional issue: cross-sectional data and the popularity question

You mentioned wanting to model "popularity effects." With a single wave of data, you can model **degree heterogeneity** (whether the degree distribution is more spread out than a Bernoulli random graph predicts) using `gwdegree`. This is a structural property of the network at one time point.

If you are trying to model whether *becoming* popular makes students more likely to receive future friendship nominations — that is a dynamic process and requires longitudinal data (at least two waves). SAOM (RSiena) is the appropriate tool for that question. With cross-sectional data, `gwdegree` captures the static degree distribution; interpret it as degree spread, not as a popularity *process*.

---

## Summary of what needs to change

1. Remove `triangle` and replace with `gwesp(decay=0.5, fixed=TRUE)`
2. Remove `kstar(2)` and replace with `gwdegree(decay=0.5, fixed=TRUE)`
3. Add MCMC control parameters for better convergence behavior
4. Run `mcmc.diagnostics()` — the chain must be stationary before you look at any coefficient
5. Run `gof()` — the model must reproduce degree, shared partners, and geodesic distributions
6. Only after both checks pass should you interpret or report any coefficient

The nodematch("gender") term is fine as-is — dyadic-independent terms cannot cause degeneracy.
