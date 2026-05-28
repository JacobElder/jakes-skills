# ERGM Transitivity Modeling: Should You Report These Results?

**Short answer: No, you should not report these results as-is. Your model is almost certainly degenerate, and the `triangle` term is the primary cause.**

---

## The Core Problem: ERGM Degeneracy with the `triangle` Term

The `triangle` statistic is well-known in the ERGM literature to cause **model degeneracy**. A degenerate ERGM is one where the fitted model places nearly all probability mass on a very small number of network configurations — typically either the empty graph or the complete graph — rather than distributing it sensibly across realistic networks.

A large positive `triangle` coefficient (your estimate of 0.85) is a classic degeneracy signature. The model is essentially saying "every triangle I see should be replicated massively," which creates a runaway feedback loop: more triangles → higher probability of ties that close triangles → even more triangles → fully connected clique. The MCMC sampler can still produce *some* output and report *some* standard errors, but those estimates are unreliable artifacts of an ill-specified model.

The fact that you got convergence and significant p-values does not mean the model is valid. The `ergm` package in statnet may still return estimates even when the model is degenerate.

---

## How to Diagnose Degeneracy

Before trusting any results, run MCMC diagnostics:

```r
# Check MCMC diagnostics
mcmc.diagnostics(fit)

# Simulate networks from the fitted model and compare to observed
sim_nets <- simulate(fit, nsim = 100)
# Compare key statistics to observed network
summary(net)  # observed
sapply(sim_nets, function(x) network.size(x))  # simulated densities, etc.
```

Signs of degeneracy in `mcmc.diagnostics()`:
- MCMC chains that are not mixing (stuck at extreme values)
- Trace plots that flatline near 0 or near the theoretical maximum
- Poor correspondence between observed network statistics and those from simulated networks

If your simulated networks are mostly empty or fully connected, and your observed network sits nowhere near the modal simulated network, you have a degenerate model.

---

## Why `triangle` Is Problematic

The `triangle` term counts the number of closed triangles in the network. It sounds like the natural way to model transitivity, but it has two serious problems:

1. **Near-degeneracy**: The triangle statistic is highly curved — small changes in tie probability create enormous changes in triangle counts, making the model numerically unstable.

2. **Interdependence explosion**: Triangles share edges with many other triangles, creating complex, hard-to-estimate dependencies.

This is not a new finding. Handcock (2003) and Snijders et al. (2006) specifically warn against `triangle` for these reasons.

---

## What to Use Instead

The statnet team developed **geometrically weighted statistics** precisely to model transitivity and degree heterogeneity without degeneracy:

### For transitivity (replace `triangle`)
```r
# Geometrically Weighted Edgewise Shared Partners
gwesp(decay, fixed = FALSE)
```

`gwesp` captures the tendency for edges to be embedded in triangles (edgewise shared partners), but with a geometrically declining weight that prevents the runaway feedback that causes degeneracy. Start with `fixed = FALSE` to let the decay parameter be estimated, or fix it at a common starting value like 0.5 or 0.7.

### For popularity/degree effects (replace `kstar(2)`)
```r
# Geometrically Weighted Degree
gwdegree(decay, fixed = FALSE)
```

`kstar(2)` (and higher-order kstar terms) suffer from the same degeneracy problem as `triangle`. `gwdegree` models the degree distribution with geometric weighting, capturing whether some nodes attract many ties without creating the same instability.

### Your revised model specification
```r
fit2 <- ergm(net ~ edges 
             + gwesp(0.5, fixed = FALSE)   # transitivity
             + gwdegree(0.5, fixed = FALSE) # popularity/degree heterogeneity
             + nodematch('gender'))         # gender homophily
summary(fit2)
mcmc.diagnostics(fit2)
```

---

## What "Significant" Means in a Degenerate Model

The p < 0.001 on your triangle coefficient is misleading. When a model is degenerate:

- Standard errors are unreliable (the MCMC is not exploring the parameter space properly)
- The likelihood surface is flat or multimodal in ways that make optimization unreliable
- Hypothesis tests based on those SEs are invalid

Statistical significance from a degenerate model is not informative about the true network generating process.

---

## Keeping `nodematch('gender')`

The `nodematch('gender')` term for homophily is fine and is correctly specified. It measures the tendency for same-gender ties to be more (or less) common than chance, controlling for the other terms. This term alone does not cause degeneracy.

---

## Recommended Next Steps

1. **Run `mcmc.diagnostics(fit)`** on your current model to confirm degeneracy.
2. **Respecify** using `gwesp` and `gwdegree` in place of `triangle` and `kstar(2)`.
3. **Run diagnostics again** on the new model to verify MCMC mixing and goodness of fit.
4. **Run `gof(fit2)`** (goodness of fit) to check whether the model reproduces key features of the observed network (degree distribution, geodesic distribution, shared partner distribution).
5. Report the gwesp/gwdegree results instead.

---

## Summary

| Term | Status | Replacement |
|---|---|---|
| `edges` | OK | Keep |
| `triangle` | Causes degeneracy | `gwesp(decay, fixed=FALSE)` |
| `kstar(2)` | Causes degeneracy | `gwdegree(decay, fixed=FALSE)` |
| `nodematch('gender')` | OK | Keep |

Your triangle coefficient of 0.85 (p < 0.001) is not a trustworthy substantive finding — it is an artifact of a degenerate model. Respecify with the geometrically weighted alternatives, validate with diagnostics and goodness-of-fit, and then report.
