# Power Analysis and Sample Size for MLM

Power for multilevel models depends on more than total *n* — it depends on the number of clusters at each level, cluster sizes, ICC, the effect size, and *where* the effect lives (level 1, level 2, cross-level interaction). Closed-form formulas exist for simple designs; for anything realistic, simulation is the standard approach.

## Three questions to ask before any power calculation

1. **Where does the effect of interest live?**
   - Level 1 (within-cluster predictor): power scales with total *n*, attenuated by ICC. Generally well-powered if you have a reasonable number of observations per cluster.
   - Level 2 (between-cluster predictor): power scales with *number of clusters*, not total *n*. Often underpowered even in studies with thousands of observations. **In a cluster RCT where treatment is randomized at the cluster level, the number of clusters per arm is the binding precision constraint — not the total student N.** Adding more students within existing clusters does not add any cluster-level degrees of freedom and does not improve power for the treatment effect. A study with 20 schools per arm has 20 school-level units of comparison regardless of whether each school has 25 students or 250.
   - Cross-level interaction (e.g., does the level-1 effect vary by level-2 group?): power is poor unless both cluster *n* and observations-per-cluster are substantial. Hox suggests ~100 clusters for adequate power on cross-level interactions; simulation is essential.

2. **What ICC are you assuming?** Higher ICC → less effective information per observation for within-cluster effects (more redundancy). Lower ICC → less power for between-cluster effects (less between-cluster signal to detect). Pilot data or published ICC norms for your domain are the right input; don't guess.

3. **Are you planning a confirmatory test of a single effect or building a more complex model?** Power for a single fixed effect is one calculation. Power across multiple fixed effects with random slopes, in a model that might not converge, is qualitatively harder and almost always needs simulation.

## Closed-form approximations (rough planning only)

For a balanced two-level design with a level-1 predictor:

**Effective sample size**: n_eff = n_total / (1 + (m - 1) × ICC), where m is the average cluster size.

So with 1000 observations, 50 clusters of 20 each, and ICC = 0.2: n_eff = 1000 / (1 + 19 × 0.2) = 1000 / 4.8 ≈ 208. Standard error inflation factor (design effect) is √(1 + (m-1)×ICC) ≈ 2.2 compared to OLS.

This is enough to know "we need a lot more than naive OLS power suggests" but not enough for serious planning. Use simulation for anything you'd put in a grant or pre-registration.

## Simulation-based power in R: `simr`

The standard tool. Workflow:

```r
library(simr)
library(lme4)

# 1. Fit a pilot model (or specify one with assumed parameters)
fit_pilot <- lmer(y ~ treatment + (1 + treatment | subject), data = pilot_data)

# 2. Set the effect size you want power for
fixef(fit_pilot)["treatment"] <- 0.3  # the smallest effect you care about detecting

# 3. Run power simulation for that effect
pc <- powerSim(fit_pilot, test = fixed("treatment"), nsim = 1000)
print(pc)
# Power for predictor 'treatment', (95% confidence interval):
#       72.30% (69.41, 75.06)

# 4. Power curve over sample size
pc_curve <- powerCurve(fit_pilot, test = fixed("treatment"),
                       along = "subject", nsim = 500)
plot(pc_curve)
```

`simr` can also extend a fitted model by adding clusters or observations (`extend(fit, along = "subject", n = 100)`), which is how you plan for a study larger than your pilot.

For cross-level interactions, `simr` handles them — but you need to specify the interaction effect size deliberately. Defaults of "use the pilot estimate" are usually overoptimistic because pilot estimates of interactions are noisy.

## Simulation-based power in R: `mixedpower`

Alternative to `simr` that handles GLMMs more gracefully and produces nicer output for varying multiple parameters simultaneously.

```r
library(mixedpower)

power <- mixedpower(
  model = fit_pilot,
  data = pilot_data,
  fixed_effects = c("treatment"),
  simvar = "subject",          # which sample size to vary
  steps = c(30, 50, 100, 150),
  critical_value = 2,           # |t| or |z| threshold
  n_sim = 1000
)
```

## Simulation in Python

No `simr`-equivalent in Python with the same polish. Two practical paths:

**Path 1: roll your own with bambi/PyMC.** Simulate data under your assumed model, fit, count rejections (frequentist) or check posterior intervals (Bayesian), iterate.

```python
import numpy as np
import bambi as bmb

def simulate_one(n_subjects, n_per_subject, effect_size, sigma_u=1.0, sigma_e=1.0, seed=None):
    rng = np.random.default_rng(seed)
    subject_ids = np.repeat(np.arange(n_subjects), n_per_subject)
    treatment = rng.choice([0, 1], size=n_subjects * n_per_subject)
    u = rng.normal(0, sigma_u, n_subjects)[subject_ids]
    e = rng.normal(0, sigma_e, n_subjects * n_per_subject)
    y = effect_size * treatment + u + e
    return pd.DataFrame({"y": y, "treatment": treatment, "subject": subject_ids})

n_sims, rejections = 500, 0
for i in range(n_sims):
    d = simulate_one(50, 20, effect_size=0.3, seed=i)
    # Frequentist path: fit with pymer4 or statsmodels, check p < .05
    try:
        from pymer4.models import Lmer
        fit = Lmer("y ~ treatment + (1 | subject)", data=d)
        result = fit.fit(REML=False)
        p_val = result["P-val"]["treatment"]
        if p_val < 0.05:
            rejections += 1
    except Exception:
        pass  # skip failed fits
power = rejections / n_sims
```

**Path 2: call `simr` from Python via rpy2.** Fastest if you're comfortable with both.

## Bayesian "power" (design analysis)

Bayesians don't have a binary reject/fail-to-reject, so "power" is reframed:

- **Probability that the 95% credible interval excludes 0** under an assumed true effect — close to frequentist power
- **Probability that the posterior puts > 95% mass above 0** — direction-of-effect certainty
- **Expected posterior precision** — width of the credible interval you'll get
- **Type S (sign) error rate** (Gelman & Carlin, 2014) — probability of getting the *wrong sign* on the effect, given that the effect is "significant"
- **Type M (magnitude) error** — expected exaggeration ratio of significant estimates

Gelman & Carlin's design analysis framework is especially useful for small-cluster studies where Type S and Type M errors are non-trivial even when nominal power looks fine. Compute by simulation:

```r
# For each simulated dataset, fit and check:
# - sign(estimate) == sign(true_effect)
# - |estimate| / |true_effect|
# Average over many sims under the assumed true effect.
```

## Cluster RCT power: the binding constraint

This section covers the most commonly misunderstood aspect of cluster RCT power.

**The binding precision constraint for a cluster-level treatment effect is the number of clusters per arm, not total student N.**

When treatment is randomized at the school level (or clinic, village, etc.), the school count per arm is what determines power for the treatment effect. Adding more students within existing schools increases within-school precision but contributes zero additional cluster-level degrees of freedom. A study with 20 schools per arm has 20 school-level comparisons regardless of whether each school has 25 students or 250. Adding 500 more students spread evenly across the same 20 schools does not improve power for the treatment effect one bit.

This is true even if you analyze school means. Two studies, both with 20 school means per arm:
- Study A: means based on n = 10 students per school
- Study B: means based on n = 100 students per school

Study B's school means are estimated more precisely (less within-school sampling error), which can improve power modestly. But the school-level sample size (20 per arm) is still the primary power driver — and once cluster sizes are reasonably large (say, n ≥ 20–30), additional students yield diminishing returns relative to adding more clusters.

**When someone reports G*Power results for a cluster RCT:**

Even if the user correctly treats the school as the unit of analysis (comparing school means, k = 20 per arm), G*Power still falls short:

1. The effect size input must be in school-mean SD units, not student-level SD. These differ by a factor of √(ρ + (1 − ρ)/n) where ρ = ICC and n = students per school. If the user entered a student-level Cohen's d, the power estimate is wrong.
2. G*Power does not accept ICC as an explicit input. The ICC-to-effect-size conversion must be done manually before entering G*Power.
3. G*Power does not produce a sensitivity analysis over plausible ICC values, which grant reviewers (especially NIH/IES study sections) require.

**Recommended tools for cluster RCT power:**
- **PowerUp! / PowerUpR** (Dong & Maynard, 2013) — purpose-built for cluster RCTs, ICC is an explicit input, widely cited in IES proposals
- **Spybrook et al. formulas** — the analytic standard for two-level cluster RCTs in education research
- **`simr` in R** — simulation-based, handles unequal cluster sizes, covariate adjustment, and produces power curves
- **Optimal Design / PowerUp!** — free tools with GUI for non-R users

Always report a sensitivity table over plausible ICC values (e.g., ρ = 0.05–0.20 for educational outcomes) rather than a single power number.

## Practical heuristics from the literature

- **Maas & Hox (2005)** simulation work: with ~30 clusters of ~30, fixed-effect estimates are unbiased but their SEs are downward biased by ~15%. Use Kenward-Roger or Bayesian estimation in this regime.
- **Hox (2010)**: 30/30 minimum for fixed effects, 50/20 for variance components, 100/10 for cross-level interactions (very rough rules of thumb).
- **Kreft & de Leeuw (1998)**: the "30/30 rule" — at least 30 clusters of at least 30 each — is a planning baseline, not a guarantee.
- **Snijders & Bosker (2012)** has the most thorough closed-form treatment for two-level designs; their formulas are implemented in the `PowerUpR` package and the standalone PowerUp! tool.

## What to report from a power analysis

In a grant, registered report, or methods section:

> We conducted simulation-based power analysis using `simr` (Green & MacLeod, 2016). Assuming a treatment effect of d = 0.3, ICC = 0.15, average cluster size of 20, and the maximal random-effects structure justified by the design, we estimated power as a function of the number of clusters. With 40 clusters, simulated power was 0.72 (95% CI [0.69, 0.75]); 60 clusters yielded 0.85 (0.83, 0.88); 80 clusters yielded 0.92 (0.90, 0.94). We targeted 60 clusters to achieve 80% power with margin.

Spell out the assumptions. A power analysis without stated assumed effect size, ICC, and design structure is uninterpretable.

## Common pitfalls

1. **Using OLS power formulas for MLM** (G*Power without the multilevel module, etc.). Massively overestimates power for clustered designs. For cluster RCTs: even if you correctly use the number of *clusters* per arm as the G*Power input (comparing school means), G*Power still fails because (a) the effect size must be in school-mean SD units adjusted for ICC — not student-level SD, and (b) G*Power has no ICC input and produces no sensitivity analysis over ICC. G*Power run on total *students* is additionally wrong because it assumes independence. Use `simr`, PowerUp!, or the Spybrook et al. formulas — these accept ICC as an explicit parameter. The fundamental precision constraint for the treatment effect is the **number of clusters per arm**, not total student N; adding students within existing schools does not add cluster-level degrees of freedom or improve power for the cluster-level treatment effect.
2. **Assuming ICC = 0 to get a "best case" estimate.** That's not best case; that's "no clustering, no MLM needed." Use realistic ICC.
3. **Powering on the pilot estimate of the effect.** Pilot estimates are biased upward (the ones that get followed up are the ones that looked promising). Power on the smallest effect you'd care about, not the one you observed.
4. **Ignoring power for variance components** when those are the inferential target (e.g., is there meaningful between-school variation?). Variance components need many clusters to be precisely estimated, far more than fixed effects do.
5. **Computing post-hoc "achieved" power from your observed effect.** This is mathematically circular; an observed p < .05 always corresponds to observed "power" > 50%. Skip it.

## Key references

- Maas, C. J. M., & Hox, J. J. (2005). Sufficient sample sizes for multilevel modeling. *Methodology*, 1(3), 86–92.
- Green, P., & MacLeod, C. J. (2016). simr: an R package for power analysis of generalized linear mixed models by simulation. *Methods in Ecology and Evolution*, 7(4), 493–498.
- Gelman, A., & Carlin, J. (2014). Beyond power calculations: Assessing Type S (sign) and Type M (magnitude) errors. *Perspectives on Psychological Science*, 9(6), 641–651.
- Snijders, T. A. B., & Bosker, R. J. (2012). *Multilevel Analysis* (2nd ed.). Sage. [Chapter on power.]
- Kreft, I., & de Leeuw, J. (1998). *Introducing Multilevel Modeling*. Sage.
- McNeish, D., & Stapleton, L. M. (2016). The effect of small sample size on two-level model estimates: A review and illustration. *Educational Psychology Review*, 28(2), 295–314.
