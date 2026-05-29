# Reporting Template for MLM Analyses

A complete MLM write-up needs more than fixed-effect estimates and *p*-values. Use the structure below as a checklist. Adapt for the venue (concise for high-impact short-format; expanded for methods sections in psychology, education, biostatistics journals).

## The minimum complete report

### 1. Data structure and model rationale

State the clustering structure plainly. Examples:

> Our data consisted of 4,832 trials nested within 60 participants and crossed with 80 items. Each participant completed all items in both conditions; condition therefore varied within both participants and items.

> Students (n = 12,743) were nested within classrooms (n = 421) within schools (n = 67). The treatment was assigned at the school level.

Justify MLM over OLS or ANOVA explicitly — even if briefly:

> Because trials were not independent (multiple trials per participant and per item), we used a linear mixed-effects model with crossed random effects for participants and items (Baayen, Davidson, & Bates, 2008).

### 2. Model specification

Give the full model. Two acceptable formats — pick one and use it consistently:

**Equation form** (Raudenbush & Bryk style, useful when you want to highlight cross-level effects):

> Level 1: y_ij = β_0j + β_1j × x_ij + r_ij
> Level 2: β_0j = γ_00 + γ_01 × z_j + u_0j
> Level 2: β_1j = γ_10 + γ_11 × z_j + u_1j

**Formula form** (compact, common in psycholinguistics and ecology):

> rt ~ condition × distractor + (1 + condition × distractor | subject) + (1 + condition | item)

For Bayesian fits, also state the priors:

> Priors were weakly informative: Normal(0, 100) on fixed-effect coefficients, Student-t(3, 0, 150) on all SDs, and LKJ(2) on random-effect correlation matrices.

### 3. Random-effects structure: how you chose it

This is the single most important methodological detail and the most commonly omitted. State both your starting structure and any simplifications:

> Following Barr et al. (2013), we began with the maximal random-effects structure justified by the design: by-participant random intercepts and random slopes for condition, distractor, and their interaction; by-item random intercepts and random slope for condition (distractor was between-items).

> The maximal model converged with a singular fit (correlation between the by-participant random intercept and condition slope estimated at -1.00). Following Bates et al. (2015), we removed the correlation parameters (using `||` syntax) and refit. The resulting model converged without singularity, and we report it below.

If you couldn't fit the maximal structure even with simplification, say so and explain what you did instead.

### 4. Estimation details

> Models were fit with lme4 1.1-35 (Bates, Mächler, Bolker, & Walker, 2015) in R 4.3.2, using REML estimation with the bobyqa optimizer (maxfun = 100000). Degrees of freedom and *p*-values for fixed effects were obtained via the Satterthwaite approximation using lmerTest 3.1-3 (Kuznetsova, Brockhoff, & Christensen, 2017).

For Bayesian fits:

> Models were fit with brms 2.20.4 (Bürkner, 2017) using Stan 2.32 (Stan Development Team, 2023). We ran 4 chains of 4000 iterations (first 2000 as warmup), with `adapt_delta = 0.95` and `max_treedepth = 12`. All R-hat values were below 1.01 and bulk ESS exceeded 1000 for all parameters.

### 5. Convergence and diagnostics

Don't bury this. Report:

- For frequentist: convergence status, singular fit check, any optimizer warnings
- For Bayesian: R-hat, ESS (bulk and tail), divergent transitions, treedepth saturation

> The model converged without warnings. `isSingular()` returned FALSE; the random-effects PCA showed all variance components substantively above zero (smallest λ = 0.04). Residual diagnostic plots showed no concerning deviations from assumptions.

### 6. Fixed-effect results

Report **estimate, standard error, confidence/credible interval, and test statistic** for each fixed effect of interest. *p*-values are fine to include but should not be the only inferential information.

A table is usually clearest:

| Term | Estimate | SE | 95% CI | t | df | p |
|---|---|---|---|---|---|---|
| (Intercept) | 612.3 | 18.4 | [576, 648] | — | — | — |
| Condition | 23.7 | 6.2 | [11.4, 36.0] | 3.82 | 58.4 | < .001 |
| Distractor | 12.1 | 5.8 | [0.6, 23.6] | 2.09 | 47.2 | .042 |
| Condition × Distractor | -2.4 | 9.0 | [-20.4, 15.6] | -0.27 | 41.8 | .79 |

For Bayesian fits, replace SE with posterior SD, CI with credible interval, and drop the *t*/df columns. Optionally add probability of direction:

| Term | Estimate | SD | 95% CrI | P(direction) |
|---|---|---|---|---|
| Condition | 23.4 | 6.1 | [11.1, 35.7] | > .999 |

### 7. Variance components and ICC

Report variance components and the ICC at each level. This tells the reader **how much clustering matters** — without it, the multilevel structure is invisible.

> Variance components were: subject intercepts σ²_u = 1,847 (SD = 43.0), subject condition slopes σ²_v = 89 (SD = 9.4), item intercepts σ²_w = 312 (SD = 17.7), and residual σ²_e = 2,134 (SD = 46.2). The ICC for participants was 0.40 and for items 0.07; together random effects accounted for 47% of the total variance.

If the model has more components, a small table is cleaner. Always give ICCs.

### 8. Effect sizes

For LMMs, Nakagawa & Schielzeth's marginal R² (fixed effects only) and conditional R² (fixed + random) are widely used and easily computed via `performance::r2()`.

> The marginal R² (variance explained by fixed effects alone) was .12; the conditional R² (fixed plus random effects) was .59.

For specific contrasts, report effect sizes in raw units of the outcome (preferred), or standardized (e.g., Cohen's *d* using a defensible SD — typically the residual SD or the SD of the outcome).

### 9. Robustness / sensitivity (when relevant)

Especially for important findings, demonstrate robustness:

- Refit with a different optimizer; results unchanged.
- Refit a Bayesian version; posterior median consistent with the frequentist point estimate.
- Refit with the maximal structure; the key effect held.
- Refit excluding the most influential cluster (e.g., Cook's D analogue); effect held.

### 10. Limitations specific to MLM

Worth naming when they apply:

- Small number of clusters at level 2 (variance components imprecise)
- Imbalance in cluster sizes
- Convergence warnings on the maximal model that required simplification
- Group-mean centering choices that affect interpretation

---

## A complete model paragraph (psycholinguistics example)

> Reaction times were analyzed with a linear mixed-effects model with crossed random effects for participants (n = 60) and items (n = 80). The fixed-effects structure included condition (within-subjects, within-items), distractor type (within-subjects, between-items), and their interaction, with sum-to-zero contrasts. Following Barr et al. (2013), we specified the maximal random-effects structure justified by the design: by-participant random intercepts and random slopes for condition, distractor, and their interaction, with correlations; by-item random intercepts and random slope for condition. The model was fit with lme4 (Bates et al., 2015) using REML and the bobyqa optimizer; *p*-values were obtained via the Satterthwaite approximation in lmerTest (Kuznetsova et al., 2017). The maximal model produced a singular fit due to a degenerate by-participant correlation; we therefore dropped correlation parameters (using `||` syntax). The reduced model converged without warnings. The main effect of condition was reliable, b = 23.7 ms, SE = 6.2, 95% CI [11.4, 36.0], *t*(58.4) = 3.82, *p* < .001. The interaction was not, b = -2.4, SE = 9.0, *t*(41.8) = -0.27, *p* = .79. Random-effect variances were substantial for participant intercepts (SD = 43.0 ms) and modest for item intercepts (SD = 17.7); the ICC for participants was 0.40. Marginal R² = .12; conditional R² = .59.

That's about 200 words and includes everything a methodologically careful reviewer should expect.

## What reviewers commonly ask for

If you're writing for a careful audience, anticipate these questions:

- "Why this random-effects structure?" → Already answered in step 3.
- "Did you check the maximal structure?" → Already answered.
- "Are *p*-values from Satterthwaite or Kenward-Roger?" → Already answered.
- "Did the model converge?" → Already answered.
- "What's the ICC?" → Already answered.
- "Can you provide the data and code?" → Yes, in a repository. Make this true before submission.
- "Did you try a Bayesian fit?" → If they ask, having one as robustness check is convenient.

Save yourself a revision round by addressing these proactively.
