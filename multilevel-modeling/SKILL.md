---
name: multilevel-modeling
description: Use whenever the user is working with nested, clustered, hierarchical, repeated-measures, longitudinal, or crossed-grouping data — students-in-schools, patients-in-hospitals, trials-within-subjects, subjects-and-items, observations-over-time, panel, growth-curve, or multi-site studies. Triggers on terms like HLM, multilevel, mixed-effects, random effects, random slopes, lmer, lme4, lmerTest, brms, glmmTMB, MixedLM, bambi, pymer4, ICC, variance components, longitudinal, nested, crossed, partial pooling, emmeans, marginaleffects, simr, simple slopes. Also use when the user is fitting OLS on data with obvious clustering, planning sample size for a clustered study, or interpreting fitted-model output via predicted means, contrasts, or simple slopes. Covers data-structure diagnosis, random-effects specification, contrast coding, fitting in R and Python, frequentist and Bayesian workflows, convergence troubleshooting, post-estimation, power, and write-up.
---

# Multilevel / Hierarchical Linear Modeling

This skill encodes hard-won practice from Hox, Moerbeek & van de Schoot (*Multilevel Analysis*, 3rd ed.), Gelman & Hill (*Data Analysis Using Regression and Multilevel/Hierarchical Models*), Gelman et al. (*Regression and Other Stories*), Raudenbush & Bryk (*Hierarchical Linear Models*, 2nd ed.), and the methodological literature on random-effects specification (Barr et al., 2013; Schielzeth & Forstmeier, 2009; Bates et al., 2015; Matuschek et al., 2017).

The single most important thing this skill exists to prevent: **fitting an underspecified random-effects structure that inflates Type I error.** Default LLM behavior (and frankly default applied-stats behavior) gravitates toward `y ~ x + (1 | group)` — a single random intercept — even when the data structure demands much more. That choice is rarely defensible and routinely produces false positives at 2–5× the nominal rate. Read the random-effects guidance below carefully.

## When to reach for multilevel modeling

Use MLM whenever observations are **not independent** because they share something — a person, a classroom, a clinic, a stimulus, a time point, a geographic unit. Concretely:

- Repeated measures on the same units (longitudinal, growth curves, EMA, diary studies)
- Students in classrooms in schools; patients in clinics in hospitals
- Trials within subjects (and often within items too — the crossed case)
- Meta-analysis (effect sizes within studies)
- Cross-classified data (e.g., students belonging to both schools and neighborhoods)
- Any time the user mentions ICC, design effect, clustering, or has aggregated data into means to "solve" non-independence

If the user is running OLS, a paired *t*-test, repeated-measures ANOVA, or by-subjects/by-items ANOVA on data with obvious clustering, gently flag that MLM is probably the right tool and explain why.

## The core workflow

Follow these steps in order. Don't skip to fitting until you've done steps 1–3.

If the user is in the planning phase (pre-data-collection) rather than analyzing existing data, also see `references/power_analysis.md` — power in MLM depends on the number of clusters at each level (not total *n*), the ICC, and where the effect lives in the hierarchy, and the field-specific minimums (e.g., 50+ clusters for stable level-2 inference, 100+ for cross-level interactions) are commonly missed.

**Cluster RCT binding constraint (common error):** When treatment is randomized at the cluster level (e.g., schools assigned to intervention vs. control), the number of clusters per arm — not total student N — is the binding precision constraint. Adding more students within existing schools does not add any cluster-level degrees of freedom and does not improve power for the treatment effect. A study with 20 schools per arm has 20 school-level units of comparison regardless of whether each school has 25 or 250 students. Standard power tools (G*Power, typical t-test calculators) ignore this — use `simr`, PowerUp!, or Spybrook et al. formulas that account for ICC and cluster count explicitly.

### Step 1: Map the data structure before touching code

Before writing any model syntax, identify and write down:

1. **The outcome** and its scale (continuous, binary, count, ordinal, time-to-event). This determines whether you need LMM, GLMM, or something else.
2. **Every level of clustering**, and how those grouping factors relate: **nested** (students within one school only), **crossed** (every subject sees every item), **cross-classified** (students in schools and neighborhoods), or **partially crossed** (latin-square designs). Misidentifying this is the most common upstream error — see `references/data_structure.md` for diagnostic code and the ID-uniqueness gotcha that silently breaks nested models.
3. **Where each predictor varies**: at level 1 (within cluster), level 2 (between cluster), or both. A predictor that varies within cluster *can* have a random slope; one that varies only between clusters cannot.
4. **The number of clusters at each level.** This is the binding constraint on what random-effects structure is estimable. Rough guidance from Gelman & Hill and Hox: fewer than ~5 clusters → treat as fixed; 5–~30 → multilevel is fine but expect noisy variance estimates and consider Bayesian partial pooling; >30 → frequentist MLM works well. Hox suggests 50+ clusters for stable level-2 inference, 100+ for cross-level interactions.

Whenever sample size at a level is small, prefer Bayesian estimation with weakly informative priors — REML/ML estimates of variance components can collapse to zero or be wildly imprecise with few clusters, while priors regularize them sensibly.

### Step 2: Specify the random-effects structure deliberately

**This is where most analyses go wrong.** The default of a single random intercept is almost never the right answer for experimental or repeated-measures data. See `references/random_effects_specification.md` for the full treatment — read it before recommending a model structure for any non-trivial design.

The short version: for confirmatory hypothesis testing with experimental designs, start from the **maximal random-effects structure justified by the design** (Barr et al., 2013): random intercepts *and* random slopes for every within-cluster predictor, at every grouping factor that the predictor varies within. Then, if and only if the model fails to converge or is degenerate, simplify in a principled way (Bates et al., 2015; Matuschek et al., 2017). Don't simplify by reflex.

Common omissions to check for explicitly:

- **By-item random effects in addition to by-subject** when stimuli are sampled (psycholinguistics, vision, judgment studies). Omitting items inflates Type I error catastrophically — Clark's (1973) "language-as-fixed-effect fallacy."
- **Random slopes for within-cluster manipulations.** A treatment that varies within subjects needs a by-subject random slope; otherwise the test of the treatment effect uses the wrong error term and the *p*-value is anti-conservative.
- **Random slopes for time** in growth models. Different people grow at different rates.

### Step 3: Center predictors and choose contrast codings thoughtfully

For continuous predictors that vary within and between clusters, decide between:

- **Grand-mean centering**: useful for interpretation; level-1 coefficient is a blend of within- and between-cluster effects.
- **Group-mean (within-cluster) centering**: separates within- and between-cluster effects cleanly. Often what researchers actually want for level-1 predictors. Add the cluster mean back as a level-2 predictor to recover the between-cluster effect ("contextual effect").

Hox calls this the within/between decomposition; Raudenbush & Bryk discuss it extensively. Gelman & Hill recommend centering and rescaling continuous predictors (often dividing by 2 SDs) for interpretability and to help convergence.

For categorical predictors, the **contrast coding** choice matters more in MLM than OLS — it changes what main effects mean in interaction models, what random slopes represent, and often whether the model converges at all. The lme4 default of treatment coding is a poor choice for most interaction models. See `references/contrast_coding.md` for the full guidance (Schad et al., 2020); the short version is to use sum or (−0.5, +0.5) contrast coding for 2-level factors and orthogonal contrasts mapped to your *a priori* hypotheses for multi-level factors.

### Step 4: Fit, diagnose, interpret

Software details and the full reference set:
- `references/data_structure.md` — diagnosing nested vs crossed vs cross-classified, formula syntax cheat sheet
- `references/random_effects_specification.md` — the full random-effects decision procedure
- `references/contrast_coding.md` — categorical predictor coding and what it means for interpretation
- `references/fitting_r.md` — lme4, lmerTest, glmmTMB, brms, ordinal, survival workflows
- `references/fitting_python.md` — statsmodels MixedLM, PyMC, bambi, pymer4
- `references/bayesian_workflow.md` — priors, diagnostics, posterior summaries, model comparison
- `references/convergence_troubleshooting.md` — consolidated decision tree for when models fail to fit
- `references/post_estimation.md` — emmeans and marginaleffects for interpretable contrasts, simple slopes, marginal effects
- `references/power_analysis.md` — simulation-based power for MLM with simr, mixedpower, and Bayesian design analysis
- `references/common_patterns.md` — recurring designs (psycholinguistic, longitudinal, cluster RCT, EMA, GLMM) and their pitfalls
- `references/reporting_template.md` — what to include in a complete write-up

Always check:
1. **Convergence**: REML/ML warnings in lme4, R-hat and ESS in Bayesian fits, gradient/Hessian in statsmodels
2. **Singular fits**: variance components estimated at zero or correlations at ±1 signal an overspecified random structure for the data
3. **ICC and variance partitioning**: report ICC at each level; this tells the reader how much clustering matters
4. **Residual diagnostics at each level**: not just `plot(model)` — examine level-2 residuals (EBLUPs/BLUPs/random effects) for normality and influential clusters too

For inference:
- In lme4, *p*-values aren't reported by default for a reason — degrees of freedom are not obvious in the unbalanced case. Use `lmerTest` (Satterthwaite or Kenward-Roger) for LMMs, parametric bootstrap or profile CIs for harder cases, and likelihood-ratio tests with caution (anti-conservative for variance components; use REML=FALSE for fixed-effect LRTs).
- For GLMMs, Wald tests are usually fine for fixed effects with enough clusters; for variance components, profile or bootstrap CIs are better than Wald.
- In Bayesian fits, report posterior medians/means and credible intervals; avoid framing posterior probabilities as *p*-values.

### Step 5: Write up

A complete MLM write-up specifies:

1. The full model equation — both the scalar and multilevel forms, or the lme4-style formula with random-effects structure spelled out
2. Estimation method (REML, ML, MCMC) and software/version
3. The random-effects structure and how it was chosen (was it the maximal model? Was it simplified? On what grounds?)
4. Fixed-effect estimates with SEs and CIs (not just *p*-values)
5. Variance components and ICC(s)
6. Convergence/diagnostic information
7. If Bayesian: priors, chains, iterations, R-hat, ESS

`references/reporting_template.md` has a fill-in-the-blanks structure that meets APA / journal standards.

## Common questions to ask the user

If the user's request is underspecified, ask before fitting. Useful elicitation questions:

- "What's the unit of observation, and what are the grouping factors? Are they nested or crossed?"
- "How many groups do you have at each level? (Not how many observations — how many clusters.)"
- "Is this a confirmatory test of a specific hypothesis, or exploratory model-building? The random-effects guidance differs."
- "For each predictor, does it vary within clusters, between clusters, or both?"
- "Are you committed to frequentist, or open to a Bayesian fit? With few clusters or convergence trouble, Bayesian regularization helps a lot."

Don't ask more than 3 questions at once.

## When NOT to use MLM — and what to use instead

Three approaches handle clustered data. They are **not interchangeable**, especially for nonlinear outcomes:

| Approach | Effect type | Best when |
|---|---|---|
| **MLM / mixed effects** | Cluster-specific (conditional) | Need cluster-level predictions, variance decomposition, ICC; have ≥5 clusters; cluster-level variation is substantively interesting |
| **GEE** | Population-average (marginal) | Want effect interpretable across the population, not conditional on a cluster's random effect; binary/count outcome where conditional ≠ marginal; comfortable specifying a working correlation |
| **Cluster-robust SEs (OLS/GLM + sandwich)** | Population-average (marginal) | Large N, clustering is a nuisance, OLS otherwise appropriate; need simplest approach; ≥30 clusters for reliable sandwich variance |

**The conditional vs. marginal distinction matters for GLMMs.** A GLMM coefficient says "for a given cluster at its random-effect value, a one-unit change in X multiplies the odds by exp(β)." A GEE coefficient says "in the population, a one-unit change in X multiplies the odds by exp(β) on average across clusters." These are numerically different because the logistic transformation is nonlinear — the population-average odds ratio is always closer to 1 than the cluster-specific one. For linear outcomes (LMM), the two coincide. See `references/common_patterns.md` for the decision pattern with software.

Hard stops for MLM:
- **<5 clusters**: use fixed effects (dummies) instead of a random effect.
- **Fixed, known set of clusters you care about individually**: those are fixed effects, not random.

Prefer GEE when:
- You have binary/count outcomes and want a population-average effect that stakeholders can interpret directly.
- You explicitly don't want predictions for specific clusters.

Prefer cluster-robust SEs when:
- The outcome is continuous, OLS is otherwise fine, and you want the simplest defensible approach.
- N is large and you have ≥30 clusters (below ~30, sandwich variance estimates are unreliable).

## Anti-patterns to watch for and push back on

1. **`y ~ x + (1|subject)` as a default for within-subjects experiments.** Almost always wrong. Needs random slopes for within-subjects predictors.
2. **Dropping items as a random effect** because "we used the same items for everyone." That's exactly when you need by-item random effects.
3. **Aggregating to cluster means** to "solve" the non-independence problem. This throws away within-cluster information and inflates Type II error.
4. **Treating school/site as a fixed effect with dummies** when there are 30+ sites and you want to generalize. Use random effects so you get partial pooling and can predict for new sites.
5. **Reporting only the fixed-effect *p*-values** with no variance components, ICC, or random-effects structure. Reviewers (and methodologists) will rightly object.
6. **"My model didn't converge so I dropped the random slopes"** without diagnosing why. Often the fix is centering, scaling, or a different optimizer — not dropping structure that the design requires.
7. **Using likelihood-ratio tests on variance components against a χ² distribution** without the boundary correction (the true null distribution is a mixture because variances can't be negative).
8. **Using total student N (not cluster N) as the basis for cluster RCT power.** When treatment is randomized at the cluster level, power for the treatment effect scales with the *number of clusters per arm*, not with total student N. A study with 20 schools per arm has 20 school-level comparisons regardless of whether each school has 25 or 250 students. Adding students within existing schools does not add cluster-level degrees of freedom and does not solve a cluster-level power problem. Flag this when reviewing any power analysis for a cluster RCT that uses G*Power, a t-test calculator, or any tool that ignores the clustering structure.

## A note on AI-generated MLM code

Generated MLM code (including from AI models) routinely defaults to single-random-intercept models because that's the modal example in training data. When generating code, explicitly justify the random-effects structure in a comment, and flag to the user if the structure is a simplification of the maximal model. If unsure about the design, ask before fitting.
