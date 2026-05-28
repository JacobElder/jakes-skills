# ERGM Model Review: Degeneracy Warning

## Short answer: No, do not report these results as valid.

Your model specification contains two terms — `triangle` and `kstar(2)` — that are well-documented causes of ERGM degeneracy. The significant coefficients you received are almost certainly artifacts of a degenerate model, not meaningful estimates of transitivity and popularity effects in your friendship network. Here is a detailed breakdown of what went wrong and how to fix it.

---

## What is ERGM degeneracy and why does it matter here?

An ERGM defines a probability distribution over graphs:

`P(Y = y | θ) = exp(θ' g(y)) / κ(θ)`

The statistics vector g(y) includes your edge count, triangle count, 2-star count, and gender match count. For dyadic-dependent terms like `triangle` and `kstar(2)`, the conditional log-odds of any single tie depends on how many triangles and k-stars already exist in the rest of the network. This creates a feedback loop:

- A small positive coefficient on `triangle` means each existing triangle makes adjacent ties slightly more likely.
- More ties create more triangles.
- More triangles raise the log-odds of yet more ties.
- The MCMC chain collapses to either the empty graph or the complete graph.

When this happens, the MCMLE algorithm may still return estimates — it does not always crash or warn loudly — but those estimates describe the degenerate distribution, not your friendship network. A triangle coefficient of 0.85 with p < 0.001 in a degenerate model is meaningless: the significance reflects the collapse dynamics, not real transitivity.

This is not a fringe concern. Handcock (2003) and Schweinberger (2011) formally characterized this failure. The `triangle` and raw `kstar` terms are listed in the canonical literature as almost always degenerate for networks with the densities and clustering levels typical of friendship data. A 180-student friendship network with real transitivity is exactly the regime where naive specifications collapse.

---

## How to tell if your model is actually degenerate

Before respecifying, run these two diagnostics on your existing fit:

```r
mcmc.diagnostics(fit)
gof_obj <- gof(fit)
plot(gof_obj)
```

Signs of degeneracy to look for in `mcmc.diagnostics()`:
- Trace plots that drift toward very high or very low values rather than wandering around a stationary mean
- Extremely high autocorrelation in the MCMC samples
- Chains that get stuck at one extreme (full or empty graph territory)

Signs in `gof()`:
- Simulated degree distributions that look nothing like your observed network (e.g., most simulated graphs are nearly complete or nearly empty)
- Simulated edgewise shared partners distribution that is wildly off
- Geodesic distance distributions that are impossible (all paths length 1, or completely disconnected)

If any of these fire, the coefficients are invalid regardless of their p-values.

---

## The fix: geometrically weighted statistics

Snijders, Pattison, Robins & Handcock (2006) and Hunter & Handcock (2006) solved this by replacing monotonic statistics with geometrically weighted versions that have decreasing marginal returns. Each additional triangle contributes less than the last, breaking the positive feedback loop. These produce curved exponential family models with well-defined MLEs.

Here is the corrected specification for your research question:

```r
library(statnet)

fit <- ergm(net ~ edges +
                  gwesp(decay = 0.5, fixed = TRUE) +   # transitivity — replaces triangle
                  gwdegree(decay = 0.5, fixed = TRUE) + # popularity — replaces kstar(2)
                  nodematch("gender"),                   # gender homophily
            control = control.ergm(
              MCMC.samplesize = 10000,
              MCMC.burnin     = 10000,
              MCMLE.maxit     = 20
            ))

summary(fit)
mcmc.diagnostics(fit)   # not optional
gof_obj <- gof(fit)
plot(gof_obj)
```

**Term-by-term substitutions:**

| Your original term | Correct replacement | What it models |
|---|---|---|
| `triangle` | `gwesp(decay, fixed=TRUE)` | Transitivity / friends-of-friends closure, with diminishing returns per additional shared partner |
| `kstar(2)` | `gwdegree(decay, fixed=TRUE)` | Degree heterogeneity / popularity, with diminishing returns at higher degrees |
| `nodematch("gender")` | Keep as-is | Gender homophily — this term is dyadic-independent and never causes degeneracy |

**Note on the decay parameter:** The value 0.5 is a reasonable starting point (typical range is 0.25–0.75). Fixing the decay (`fixed=TRUE`) is standard practice for single-network data; estimating it (`fixed=FALSE`) is possible but often unstable from a single network. If you have a strong theoretical reason to prefer a specific decay, fix it there; otherwise try a few values (0.25, 0.5, 0.75) and check that your substantive conclusions are stable.

---

## Recommended estimation workflow

Build the model incrementally. Do not add all terms at once:

1. **Null model**: `edges` only. Check that the density of simulated graphs matches your observed density.

2. **Dyadic-independent terms only**: `edges + nodematch("gender")`. These are equivalent to logistic regression on dyads and cannot cause degeneracy. Estimate and check GoF.

3. **Add `gwesp`**: `edges + nodematch("gender") + gwesp(0.5, fixed=TRUE)`. Run `mcmc.diagnostics()`. If chains look stationary, run `gof()`.

4. **Add `gwdegree`**: `edges + nodematch("gender") + gwesp(0.5, fixed=TRUE) + gwdegree(0.5, fixed=TRUE)`. Repeat diagnostics.

5. **Evaluate final model**: Only interpret coefficients if MCMC chains are stationary, autocorrelation decays, and GoF plots show simulated networks that resemble your observed network in degree distribution, edgewise shared partners, and geodesic distance.

---

## What to report once the model converges cleanly

When you have a well-specified, converged model, report:

- **MCMC diagnostics**: state that trace plots showed stationarity and autocorrelation was acceptable (or include the plots in supplementary materials)
- **GoF**: show the degree distribution, edgewise shared partners, and geodesic distance plots with the observed values overlaid on the simulated distribution
- **Coefficients**: report as conditional log-odds, not as "effects." For example: "The positive GWESP coefficient (b = X, SE = Y) indicates that, controlling for degree heterogeneity and gender composition, ties closing a triangle are significantly more likely than expected by chance."
- **Decay parameter**: state what value you used and whether it was fixed or estimated

Do not interpret ERGM coefficients causally. They are conditional log-odds in a joint probability model, not directional influence estimates.

---

## Additional note: single wave limits your inference

Your data were collected in one wave, which means ERGM is the right tool (not SAOM, which requires multiple waves). However, be explicit in your write-up that the ERGM estimates the structural tendencies of the observed network — it does not tell you which friendships formed first or whether transitivity is driven by selection or by social influence. A positive GWESP coefficient tells you that triangles are over-represented relative to an Erdős–Rényi baseline controlling for your other terms; it does not tell you that triadic closure is a causal mechanism. If you want to separate selection from influence, you would need longitudinal data and a co-evolution SAOM.

---

## Summary checklist before submission

- [ ] Replace `triangle` with `gwesp(decay, fixed=TRUE)`
- [ ] Replace `kstar(2)` with `gwdegree(decay, fixed=TRUE)`
- [ ] Run `mcmc.diagnostics()` and verify stationary chains
- [ ] Run `gof()` and verify simulated networks resemble your observed network
- [ ] Report MCMC diagnostics and GoF alongside coefficient table
- [ ] Interpret coefficients as conditional log-odds, not causal effects
- [ ] Note that single-wave data limits causal inference about tie formation processes

---

## Canonical references

- Snijders, T. A. B., Pattison, P. E., Robins, G. L., & Handcock, M. S. (2006). New specifications for exponential random graph models. *Sociological Methodology*, 36, 99–153.
- Hunter, D. R., & Handcock, M. S. (2006). Inference in curved exponential family models for networks. *Journal of Computational and Graphical Statistics*, 15, 565–583.
- Hunter, D. R., Handcock, M. S., Butts, C. T., Goodreau, S. M., & Morris, M. (2008). ergm: A package to fit, simulate and diagnose exponential-family models for networks. *Journal of Statistical Software*, 24(3).
- Lusher, D., Koskinen, J., & Robins, G. (2013). *Exponential Random Graph Models for Social Networks*. Cambridge University Press.
