# Statistical Network Models: ERGM and SAOM

When the question is "*why* does this network look the way it does?" or "what tie-formation processes generate this structure?", descriptive measures aren't enough — you need a generative statistical model. The two dominant families are **Exponential-family Random Graph Models (ERGMs)** for cross-sectional data and **Stochastic Actor-Oriented Models (SAOMs / RSiena)** for longitudinal data. Both are nuanced; both have nontrivial failure modes that the defaults don't protect you from.

## ERGM: the basic setup

An ERGM defines a probability distribution over the space of graphs on a fixed node set:

`P(Y = y | θ) = exp(θ' g(y)) / κ(θ)`

where g(y) is a vector of network statistics (edge count, triangle count, k-stars, attribute matches), θ is the parameter vector, and κ(θ) is the normalizing constant (sum over all 2^(n choose 2) possible graphs — intractable for non-trivial n; hence MCMC-MLE).

ERGMs are statistical analogs of logistic regression for networks: each statistic g_k(y) is like a "covariate" whose coefficient θ_k says how much more (or less) likely networks with high g_k are.

### What ERGMs can do

- Test hypotheses about endogenous mechanisms: do triangles form more than expected (transitivity)? Is there reciprocity beyond chance?
- Test homophily on attributes: do same-gender ties form more than expected?
- Control for one structural effect while estimating another (e.g., estimating homophily while controlling for popularity)
- Simulate networks from the fitted model (essential for goodness-of-fit)
- Compute conditional log-odds of any specific tie given the rest

## The degeneracy problem

This is THE issue with ERGMs and the reason that naive specifications fail catastrophically. From Handcock (2003), Schweinberger (2011): for many "obvious" model specifications, the implied distribution puts almost all probability on either the empty graph or the complete graph (or a tiny set of bizarre graphs). MCMC chains get stuck, MCMLE diverges, and reported coefficients are meaningless.

### Which terms cause degeneracy

- `triangle`: counting triangles is **almost always degenerate** because adding one triangle often enables many more (each new triangle changes the gradient)
- `kstar(2)`, `kstar(3)`, ...: degree-based terms with no decay
- Any positive coefficient on these "monotonic" statistics tends to explode

### Why it happens

For dyadic-dependent terms, the conditional log-odds of a tie include terms that grow with the number of existing triangles / k-stars. A small positive coefficient creates a positive feedback loop: more triangles → higher tie odds → more ties → more triangles → ... → complete graph.

### The fix: geometrically weighted statistics (Snijders, Pattison, Robins & Handcock 2006; Hunter & Handcock 2006)

Replace monotonic statistics with **geometrically weighted** ones that have *decreasing marginal returns*:

- **GWESP** (geometrically weighted edgewise shared partners): replaces `triangle`. Each additional shared partner contributes less than the last. Decay parameter α (typically 0.25–0.75) controls how fast the contribution decays.
- **GWDEGREE** (geometrically weighted degree): replaces `kstar`. Captures degree heterogeneity without explosive degree effects.
- **GWDSP** (geometrically weighted dyadwise shared partners): pairs at distance 2.
- **GWNSP** (geometrically weighted non-edgewise shared partners): GWDSP minus GWESP.

These produce **curved exponential families** (Efron 1975 sense): the natural parameter θ is a non-linear function of the parameter vector you actually estimate. The MLE is still well-defined but more complex; `ergm` handles it.

In R's `ergm` package:
```r
library(statnet)
fit <- ergm(net ~ edges + 
                  mutual +                          # reciprocity (directed)
                  gwesp(decay=0.5, fixed=TRUE) +    # transitivity, decay fixed
                  gwdegree(decay=0.5, fixed=TRUE) + # degree heterogeneity
                  nodefactor("gender") +            # gender main effect
                  nodematch("gender") +             # gender homophily
                  absdiff("age"),                   # age difference
            control = control.ergm(MCMC.samplesize=10000,
                                    MCMC.burnin=10000,
                                    MCMLE.maxit=20))
summary(fit)
mcmc.diagnostics(fit)   # MUST check
gof_obj <- gof(fit)     # MUST check
plot(gof_obj)
```

**Estimating the decay parameter** (`fixed=FALSE`) instead of fixing it is more principled but harder. Stivala et al. and Schweinberger & Stewart (2020) note that estimating decay from a single network is often unstable; multilevel data (multiple networks with the same model) make it tractable.

### Diagnostics that are not optional

1. **`mcmc.diagnostics()`**: check that MCMC chains have converged. Trace plots should look like stationary noise around a mean, not drift. Autocorrelation should decay. If chains drift to extreme values (empty/full), you're in degeneracy territory — respecify.

2. **`gof()`**: simulate many graphs from the fitted model; check that distributions of degree, edgewise shared partners, geodesic distance match the observed network. Bad GoF means the model misses important structure even if MCMC converges.

3. **Posterior predictive sanity**: are simulated graphs the same density, transitivity, reciprocity as the observed? Compare to the data, not to noise.

If MCMC diverges:
- Reduce the number of terms; start minimal (`edges + nodematch + gwesp`) and add
- Switch any `triangle`/`kstar` to GW versions
- Try `control.ergm(MCMLE.maxit=...)` increase
- Use Bayesian ERGM (`Bergm` package) which has different convergence behavior
- Consider whether the model is misspecified rather than poorly fit

## Specifications for common scientific questions

| Question | Term to include |
|---|---|
| Is there reciprocity beyond chance? | `mutual` (directed only) |
| Is there transitivity beyond chance? | `gwesp(decay, fixed)` — NOT `triangle` |
| Are popular nodes disproportionately popular? | `gwdegree` (or in-degree analog for directed) |
| Do same-X nodes form ties more often? | `nodematch("X")` (uniform) or `nodematch("X", diff=TRUE)` (category-specific) |
| Does X-attribute predict tie volume? | `nodefactor("X")` |
| Do similar (continuous) X form ties? | `absdiff("X")` (negative coef = similarity) |
| Are there sender/receiver effects? | `sender`, `receiver` for directed |
| Does an external network predict ties? | `edgecov(other_network_matrix)` |

For dyadic covariates, use `edgecov`; for actor covariates, the `node*` family.

## ALAAM: social influence as an ERGM

The Auto-Logistic Actor Attribute Model (Robins, Pattison & Elliott 2001; Daraganova 2009) is the influence-side counterpart of ERGM. ERGM models *tie formation* given attributes; ALAAM models *attribute adoption* given the network and others' attributes. It's logistic regression for behavior with peer effects, with the network treated as fixed. Stivala (2023) shows ALAAMs also benefit from geometrically weighted statistics to avoid near-degeneracy.

R package: `RSiena` and `MPNet` support ALAAM; also `lolog` for latent-order ERGM-like alternatives.

## SAOM (Stochastic Actor-Oriented Models / RSiena)

For **panel data** (network observed at multiple time points), SAOMs (Snijders 2001, 2017) model the network as evolving in continuous time: each actor periodically gets the opportunity to change one outgoing tie, choosing the change that maximizes an "objective function" plus a Gumbel-distributed noise term (random utility / discrete choice). The model is fit by Method of Moments or Maximum Likelihood with simulated likelihood.

### Why SAOM and not just ERGMs at each wave

- SAOM **separates the rate** of change (how often actors update) from the **selection** (which change they make), giving cleaner interpretation
- SAOM handles **simultaneous changes** in network and behavior (co-evolution): you can test whether smoking spreads through friendship versus friends choose other smokers
- Continuous-time framework avoids ambiguity about "between waves" — actors don't see snapshots, they see continuous opportunities
- Coefficients have a **utility interpretation**: how much more does an actor prefer ties with each property?

### The key co-evolution model

Snijders, Steglich & Schweinberger (2010): model behavior y and network x jointly. Each has its own rate function and objective function. The behavior objective includes "similarity to friends" — the **average alter effect** or **total similarity effect** — which is the influence parameter. The network objective includes "friend with similar alter" — the **same-X selection effect** — which is the homophily parameter.

This is **the** principled way to separate influence from selection in observational longitudinal data. It is not a magic bullet (the model is still a model, with assumptions about timing and rationality), but it dominates pre/post regression on friend-mean behavior.

```r
library(RSiena)
# Set up data
mynet <- sienaDependent(array(c(net_t1, net_t2, net_t3), dim=c(n,n,3)))
myalc <- sienaDependent(cbind(alcohol_t1, alcohol_t2, alcohol_t3), type="behavior")
mygender <- coCovar(gender)
mydata <- sienaDataCreate(mynet, myalc, mygender)

# Specify effects
myeff <- getEffects(mydata)
myeff <- includeEffects(myeff, transTrip, cycle3)       # transitivity
myeff <- includeEffects(myeff, egoX, altX, simX, 
                         interaction1="myalc")          # selection on alcohol
myeff <- includeEffects(myeff, avAlt, name="myalc", 
                         interaction1="mynet")          # influence
myeff <- includeEffects(myeff, sameX, interaction1="mygender")

# Estimate
myalg <- sienaAlgorithmCreate(projname="myproj")
fit <- siena07(myalg, data=mydata, effects=myeff, returnDeps=TRUE)

# Convergence
print(fit)  # check t-ratios for convergence < 0.1
# GoF
gof_indeg <- sienaGOF(fit, IndegreeDistribution, varName="mynet")
plot(gof_indeg)
```

### Convergence and goodness-of-fit for SAOM

- **Overall maximum convergence ratio < 0.25**, individual t-ratios < 0.1 — required before interpreting
- **GoF by auxiliary statistics**: indegree distribution, outdegree distribution, triad census, geodesic distribution. The model should reproduce these even though they aren't directly fit.
- If GoF is poor, add effects (more transitivity controls, more degree controls); if convergence fails, simplify and rebuild.

### When SAOM doesn't apply

- Networks where **ties aren't actor-controlled**: citations, follow networks where the cited person doesn't choose
- Very large networks (>~1000 nodes per wave become computationally hard, though Bayesian approximations help)
- Continuous-time event data (use REM or relational event models instead — see Butts 2008)

For non-actor-driven panels, use **STERGM** (Separable Temporal ERGM, Krivitsky & Handcock 2014) instead. STERGM models tie formation and tie dissolution as separate ERGMs, in discrete time.

## ERGM vs. SAOM vs. STERGM: choosing

Following Block, Koskinen, Stadtfeld, Hollway & Steglich (2018):

| | ERGM | STERGM | SAOM |
|---|---|---|---|
| Time | Cross-sectional | Discrete waves | Continuous between waves |
| Causation of ties | "Tie-oriented" — graph-level | Tie-oriented, separate formation/dissolution | "Actor-oriented" — agency-based |
| Interpretation | Conditional log-odds of a tie | Same, with persistence/dissolution | Utility differences for actors |
| Co-evolution with behavior | Hard | Hard | Built-in |
| Sensitive to wave spacing | N/A | Yes (parameters depend on interval length) | No (continuous time) |
| Best for | "Why does this network look this way?" | Network with non-agentic ties over time (citations, etc.) | "How do actors change ties?" with agency |

## Multilevel and multiplex extensions

- **Multilevel ERGM** (Wang, Robins, Pattison, Lazega 2013): combines two-mode (e.g., person→organization) and one-mode (person→person, organization→organization) ties into a single model
- **Multilevel SAOM** (Koskinen & Snijders 2022, *JRSS-A*): hierarchical SAOMs over multiple comparable networks (e.g., classrooms)
- **DyNAM** (Stadtfeld & Block 2017): dynamic network actor model for continuous-time event data; bridges SAOM and REM

## Practical workflow for an ERGM analysis

1. **Data inspection** (see main SKILL.md): n, m, density, components, degree dist, attribute distribution
2. **Specify the null** (`edges` only) and check density matches
3. **Add dyadic-independent terms** (`nodematch`, `nodefactor`, `absdiff`, `edgecov`) — these never cause degeneracy; they're "logistic regression on dyads"
4. **Add dyadic-dependent terms one at a time**: `mutual` first (if directed), then `gwesp`, then `gwdegree`, then `gwdsp`/`gwnsp`
5. **For each addition**: check MCMC convergence, check GoF
6. **If degeneracy appears**: drop the offending term, reduce coefficient via offsets, or switch to a Bayesian implementation with stronger priors
7. **Final model**: report coefficients, SEs, GoF plots, MCMC diagnostics. Interpret coefficients as conditional log-odds.

## Common ERGM/SAOM mistakes

- Using `triangle` instead of `gwesp` (almost always degenerate)
- Not running `mcmc.diagnostics()` and `gof()` (or running them and ignoring bad results)
- Reporting parameter estimates from a non-converged MCMC
- Interpreting ERGM coefficients as "effects" in the causal sense — they are conditional log-odds in a joint distribution
- Using SAOM on data where actors don't choose their ties
- Forgetting that SAOM is sensitive to **composition change** (joiners/leavers); use `sienaCompositionChange()` if the node set varies across waves
- Treating the influence parameter (`avAlt`) and selection parameter (`simX`) as independent — they're identified *jointly*; magnitudes depend on the full model
- Running too few simulations for MCMC-MLE; underestimating SEs

## Canonical references

- Lusher, D., Koskinen, J., & Robins, G. (2013). *Exponential Random Graph Models for Social Networks: Theory, Methods, and Applications*. Cambridge.
- Snijders, T. A. B. (2017). "Stochastic actor-oriented models for network dynamics." *Annual Review of Statistics and Its Application* 4: 343–363.
- Hunter, D. R., Handcock, M. S., Butts, C. T., Goodreau, S. M., & Morris, M. (2008). "ergm: A package to fit, simulate and diagnose exponential-family models for networks." *Journal of Statistical Software* 24(3).
- Snijders, T. A. B., Pattison, P. E., Robins, G. L., & Handcock, M. S. (2006). "New specifications for exponential random graph models." *Sociological Methodology* 36: 99–153.
- Hunter, D. R. & Handcock, M. S. (2006). "Inference in curved exponential family models for networks." *JCGS* 15: 565–583.
- Block, P., Koskinen, J., Stadtfeld, C., Hollway, J., & Steglich, C. (2018). "Change we can believe in: Comparing longitudinal network models on consistency, interpretability and predictive power." *Social Networks* 52: 180–191.
- Krivitsky, P. N. & Handcock, M. S. (2014). "A separable model for dynamic networks." *JRSS-B* 76: 29–46.
- Schweinberger, M., Krivitsky, P. N., Butts, C. T., & Stewart, J. R. (2020). "Exponential-family models of random graphs: Inference in finite, super, and infinite population scenarios." *Statistical Science* 35: 627–662.
