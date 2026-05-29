# Should You Report These ERGM Results?

**Short answer: No — not as-is. The model almost certainly degenerated, and your reported results are likely meaningless.**

---

## The Core Problem: Model Degeneracy

The `triangle` term is well-known to cause near-certain degeneracy in ERGMs. Degeneracy means the MCMC sampler gets stuck in one of two extreme modes: it either generates the empty graph or the complete graph, and nothing in between. The fitted distribution has essentially no mass over realistic networks like the one you observed.

A coefficient of 0.85 on `triangle` is a red flag, not a finding. When a model is degenerate, the MCMC chain does not mix properly, the likelihood surface is numerically pathological, and maximum pseudolikelihood or MLE estimates are unreliable. The standard errors and p-values are invalid. Significant coefficients from a degenerate ERGM tell you nothing about your data.

---

## How to Diagnose Degeneracy

Before trusting any ERGM output, you must run MCMC diagnostics. In `statnet`:

```r
mcmc.diagnostics(fit)
```

Look for:
- **Trace plots** that fail to mix — a chain that flatlines or oscillates between extreme values rather than exploring the parameter space
- **Sample statistics** that deviate far from the observed network statistics (the "observed vs. simulated" plots)
- **Goodness-of-fit** checks where simulated networks look nothing like your observed network

If the trace plots show poor mixing or the simulated statistics are way off from your observed values, the model has degenerated regardless of what the coefficient table says.

You can also do a quick sanity check by simulating networks from your fitted model:

```r
sim_nets <- simulate(fit, nsim = 100)
```

If many of those simulations are near-empty or near-complete graphs, that is strong evidence of degeneracy.

---

## Why `triangle` Is the Problem

The `triangle` term counts the number of closed triangles in the network. Because triangles share edges, each additional edge can close many triangles at once, creating a sharp phase transition in the likelihood. A slightly positive triangle coefficient can send the model toward near-complete graphs; a slightly negative one can send it toward empty graphs. The model rarely finds a stable intermediate regime.

This is a known, long-standing limitation of ERGMs. The problem is not unique to your data or your software — it is a structural property of the `triangle` statistic.

---

## The Fix: Use Geometrically-Weighted Terms

The standard solution is to replace `triangle` and `kstar(2)` with their geometrically-weighted analogs:

```r
fit <- ergm(net ~ edges +
              gwesp(decay = 0.5, fixed = TRUE) +
              gwdegree(decay = 0.5, fixed = TRUE) +
              nodematch('gender'))
```

- **`gwesp`** (geometrically-weighted edgewise shared partners) captures transitivity/clustering. It models the same substantive idea as `triangle` — friends of friends become friends — but with diminishing returns for each additional shared partner. This prevents the explosive feedback that causes degeneracy.
- **`gwdegree`** (geometrically-weighted degree) captures popularity/degree heterogeneity. It replaces `kstar(2)` for the same reason.

The `decay` parameter controls how steeply the weights diminish. A common starting value is 0.5, but you can estimate it (set `fixed = FALSE`) or try a range of fixed values and compare AIC/BIC. In practice many researchers fix the decay to avoid convergence difficulties; the choice should be reported and ideally justified or sensitivity-tested.

---

## Revised Workflow

1. Refit with `gwesp` and `gwdegree` as above
2. Run `mcmc.diagnostics(fit)` — confirm trace plots mix well and sample statistics track observed values
3. Run `gof(fit)` — confirm the model reproduces degree distribution, edgewise shared partners distribution, and geodesic distance distribution
4. If GOF is acceptable, report the results with the decay parameter values disclosed

---

## A Note on `kstar(2)` Alone

Even if you dropped `triangle` but kept `kstar(2)`, you would likely still have degeneracy problems. Higher-order `kstar` terms are also known to produce degenerate models. The `gwdegree` term is the appropriate replacement.

---

## Summary

| Term in your model | Problem | Replacement |
|---|---|---|
| `triangle` | Near-certain degeneracy | `gwesp(decay, fixed=TRUE)` |
| `kstar(2)` | Degeneracy-prone | `gwdegree(decay, fixed=TRUE)` |
| `nodematch('gender')` | Fine as-is | Keep |
| `edges` | Fine as-is | Keep |

The significant p-values and the triangle coefficient of 0.85 should not be reported as substantive findings. They are artifacts of a model that almost certainly did not converge to a proper distribution. Refit with geometrically-weighted terms, verify diagnostics, and then report.
