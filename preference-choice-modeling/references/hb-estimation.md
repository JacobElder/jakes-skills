# Hierarchical Bayes for Preference & Choice Models

HB is the modern standard for estimating individual-level utilities in MaxDiff and CBC. This reference covers the parts that matter for analysis decisions and that platform documentation typically skips.

## The model in one paragraph

HB assumes each respondent has their own utility vector β_i, drawn from a population-level distribution: β_i ~ Normal(μ, Σ). The Gibbs sampler alternates between sampling β_i given (μ, Σ, choices) and sampling (μ, Σ) given all β_i. After burn-in, the saved draws give a posterior distribution for each respondent's utilities, which can be summarized as posterior means for point estimates, or kept as draws for the simulator.

The key feature: **shrinkage**. Each respondent's β_i is pulled toward μ by an amount inversely proportional to how much information they provide. Respondents with few choices, or with inconsistent choices, get more shrinkage; respondents with lots of consistent choices get less. This is the right thing to do, but it has consequences (see below).

---

## Priors that actually matter

**Mean prior on μ (the population mean of utilities)**: typically diffuse normal centered at zero on effects-coded parameters. Don't change. Changing it amounts to injecting opinion about which attributes are important *before* seeing data, which the stakeholder didn't ask you to do.

**Prior on Σ (the covariance of respondent utilities)**:

The standard prior is an inverse-Wishart with `df` degrees of freedom and a scale matrix that's a diagonal of prior variances. Two parameters matter:

- **Degrees of freedom (df)**: higher df = stronger prior, more shrinkage of individual β_i toward μ. Lower df = weaker prior, more between-respondent variation captured.
  - Sawtooth default: typically k + 5 (where k = number of parameters)
  - For studies emphasizing segmentation or individual differences, try **k + 2** to allow more between-respondent variation
  - For sparse designs with weak individual-level data, stick with the default — lower df will introduce noise without identifying real heterogeneity

- **Prior variance**: usually 1 or 2 on effects-coded utilities. Higher = weaker shrinkage on the absolute spread. For MaxDiff with very different item importance, prior variance of 2 may fit better than 1.

**A practical heuristic**: run with the default, then run with df = k + 2 and prior variance = 2. If the conclusions are stable across both, you're done. If they differ, the data is too thin to identify the heterogeneity at the level you're trying to claim — report only the aggregate result.

---

## Iterations and convergence

**Burn-in**: 20,000 is a safer default than the 10,000 some platforms ship with. For sparse MaxDiff or CBC with many prohibitions, push to 30,000–50,000.

**Used draws**: 20,000–40,000 after burn-in, with thinning so the saved set is 1,000–2,000 draws per respondent. Each saved draw should be roughly independent (autocorrelation < 0.1 at the thinning interval).

**Convergence diagnostics that matter:**

1. **Log-likelihood trace plot**: should look flat and stationary after burn-in. If it's still trending, you haven't burned in enough.

2. **Trace of μ (population mean utilities)**: should oscillate around a stable mean without drift.

3. **Trace of Σ diagonal elements**: easy to skip but matters. The covariance matrix often takes longer to converge than the means.

4. **Trace of a few individual β_i**: especially for "extreme" respondents — if their utilities are still drifting after burn-in, the chain isn't mixing well.

5. **Multiple chains from different starting points**: if available, run two or three chains and check they reach the same answer. Sawtooth doesn't natively support this; bayesm in R does, as does Stan if you've rolled your own.

**Convergence pathologies and what they mean:**

- **One parameter bouncing wildly between two values**: bimodal posterior, often from an unidentified or weakly-identified contrast. Common with heavy prohibitions in CBC.
- **Covariance matrix near-singular**: too many parameters for the sample size, or strong collinearity between attributes. Drop a parameter or simplify the design.
- **Likelihood keeps drifting up**: not converged. Run more iterations.
- **Likelihood drifting *down*** after seeming to converge: numerical instability, often from extreme prior values. Re-check priors.

---

## Individual-level utilities

The posterior mean β_i for each respondent is what most analysts use for downstream work — simulators, segmentation, "% of respondents who rate X above the mean." This is fine, but it has well-known pitfalls:

**Shrinkage on the extremes**: respondents who genuinely have extreme preferences get shrunk toward the mean more than they should. The deepest fans of Brand A look less fanatical than they are; the most price-sensitive look less so. For first-choice simulators this matters less; for tail-of-distribution claims ("our most loyal customers want X"), it matters a lot.

**Individual utilities are posterior means, not measurements**: each respondent's β_i has its own posterior distribution. Reporting "respondent 47 has utility = 72" without uncertainty is the same crime as reporting a sample mean without an SE.

**Use posterior draws, not means, when integrating across respondents**: for share-of-preference simulations, run the simulator on each draw and then summarize across draws. This propagates uncertainty correctly. Using only posterior means understates uncertainty by 20–40% in typical studies.

---

## Covariates in the upper-level model

Standard HB: β_i ~ Normal(μ, Σ).

Extended HB with covariates: β_i ~ Normal(μ + Z_i γ, Σ), where Z_i is a vector of respondent characteristics (segment dummies, demographics, etc.) and γ captures how those characteristics shift the mean utility.

**When to use covariates:**
- The deliverable is segment differences and you want HB to share information across segments rather than estimating each segment independently
- You have a small segment that would have weak utilities on its own
- You want to test whether a hypothesized segmentation explains heterogeneity

**When NOT to use covariates:**
- The deliverable is overall utility ranking — covariates can shift individual utilities away from the data
- You're including covariates that are themselves outcomes of preferences (e.g., past purchase) — this confounds the model
- You have many covariates and small sample — risks overfitting the upper-level model

**Implementation note**: Sawtooth supports covariates in HB via "constraints / covariates" settings. R's bayesm has it natively. The right covariates can sharpen analysis; the wrong ones can introduce subtle bias.

---

## Common HB pathologies and fixes

**"My utilities flipped sign for a few respondents on price/quality"**: reversals. Usually a small fraction (1–5%) of respondents and an artifact of HB shrinkage + sparse individual data. Three options: (1) leave alone, (2) impose monotonicity constraints if you're confident the attribute is monotonic for the population, (3) investigate — sometimes reversals indicate a real subgroup (e.g., conspicuous-consumption respondents who prefer high price as a status signal).

**"Aggregate utilities differ from HB posterior means"**: yes, they will. Aggregate logit ignores heterogeneity; HB respects it. The HB posterior means are the better summary, but they're not identical to aggregate logit even when averaging.

**"Importance scores changed when I added a covariate"**: yes. The covariate explains some of the between-respondent variance; the leftover variance is what feeds the importance score derivation. Be transparent about which model produced which numbers.

**"The model fit is great but stakeholders don't believe the results"**: model fit (RLH, hit rate) doesn't validate that the model captures the right construct. Cross-check against external data — known market shares, claimed importance from a separate question, prior research. If the model fit is fine but the predictions are absurd, the design or the question framing is the problem, not the estimation.

**"HB takes too long to run"**: most platforms parallelize across respondents now. If you're using software that doesn't (or you're running 50,000+ respondents), consider running aggregate logit for the directional answer while HB runs, but never report aggregate logit as your final answer if HB is feasible.

---

## When NOT to use HB

- **Single-task validation studies**: if everyone saw the same single task and you just want frequencies, MNL suffices.
- **Very small samples (< 75 respondents) for studies with many parameters**: HB will be dominated by the prior; aggregate logit at least makes the dominance explicit.
- **Pre-existing constraint structures (e.g., DCM with strict monotonicity)**: implement directly in MNL with constraints rather than fighting HB priors.

For ~95% of MaxDiff and CBC studies, HB is the right tool. Aggregate logit is faster but loses too much information about heterogeneity to be the primary readout.
