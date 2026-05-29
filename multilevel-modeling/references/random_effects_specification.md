# Random-Effects Specification

This is the single most consequential modeling decision in MLM, and the one most commonly botched. This document gives you the framework to specify the random-effects structure deliberately rather than by reflex.

## The core tension

Two camps in the literature, both right about different things:

**The "Keep it maximal" view (Barr, Levy, Scheepers & Tily, 2013).** Use the maximal random-effects structure justified by the design. Omitting random slopes for within-cluster predictors inflates Type I error — sometimes massively (their simulations show false-positive rates of 20–50% at nominal α=.05 for certain designs when random slopes are omitted). This is the most-cited paper on the topic and the default starting point for psycholinguistics and cognitive psychology.

**The "Parsimonious mixed models" response (Bates, Kliegl, Vasishth & Baayen, 2015; Matuschek, Kliegl, Vasishth, Baayen & Bates, 2017).** Maximal models are often *over-specified* for the data — variance components get estimated at zero, correlation parameters at ±1, models fail to converge or yield singular fits. When that happens, the maximal model isn't actually being fit; it just looks like it is. Matuschek et al. show that data-driven reduction of unsupported random effects can yield better power without much Type I inflation, *if done carefully*.

**The synthesis these papers actually agree on:** Start from the design-justified maximal structure, then simplify in a principled way only when the data can't support it. Don't simplify by reflex, and don't simplify because the maximal model is "complicated" — simplify because variance components are at the boundary, correlations are degenerate, or the model genuinely fails to converge after honest debugging.

Other foundational work in this space:

- **Schielzeth & Forstmeier (2009)** showed in behavioral ecology that omitting random slopes inflates Type I error for within-cluster predictors. This is the same phenomenon Barr et al. document in psycholinguistics — it generalizes broadly.
- **Clark (1973)** — the original "language-as-fixed-effect fallacy" paper. Treating items (stimuli) as fixed when they're sampled from a population grossly inflates Type I error for between-condition comparisons. Modern crossed-random-effects models solve this.

## The decision procedure

For a given design, decide on random effects in this order:

### 1. List your grouping factors

Anything you sampled from a population of like units. Subjects (you'd run a different study with different people). Items/stimuli (you'd use different ones). Schools, clinics, sessions, raters. Time points are usually *not* a grouping factor in this sense (they're a predictor) unless you're modeling many timepoints with their own variation.

### 2. For each grouping factor, every predictor that varies within it is a *candidate* random slope

Mechanical rule:

- Predictor varies **within** a grouping factor → candidate for random slope on that grouping factor
- Predictor varies **between** that grouping factor (i.e., is constant within each level) → cannot have a random slope on that grouping factor; only the intercept varies

Examples:

- Subjects see all conditions of a within-subjects manipulation → by-subject random slope for condition.
- Each item appears in only one condition → no by-item random slope for condition; only by-item random intercept. (This is item-as-blocking-factor; the item-level variability in condition effect can't be separated from condition × item interaction with one observation per item per condition.)
- Subjects are nested in schools, and all subjects in a school get the same treatment → no by-school random slope for treatment from a within-school perspective; treatment is between-school.

### 3. Include interactions as random slopes too when their components vary within

If A and B both vary within subjects, and you care about A×B, the maximal by-subject structure is `(1 + A + B + A:B | subject)`. Dropping the interaction's random slope can inflate Type I error for the interaction test specifically (Barr et al. discuss this).

### 4. Decide whether to estimate random-effect correlations

The maximal model estimates correlations among random effects (e.g., between random intercepts and random slopes). Each correlation parameter is one more thing to estimate. With limited data, these are often what fails first.

Two reasonable starting points:

- **Maximal with correlations**: `(1 + x | subject)` in lme4 syntax. Estimates intercept variance, slope variance, and their correlation.
- **Maximal without correlations**: `(1 + x || subject)` in lme4 syntax. Same variances, no correlation. More parsimonious; often the right "first fallback" when the full model has degenerate correlations.

Note: `||` in lme4 only suppresses correlations cleanly for numeric predictors; for factors with multiple levels, you may need to expand the formula manually (`(1 | subject) + (0 + x | subject)`).

### 5. Write down the random-effects structure explicitly before fitting

This sounds trivial but it's the discipline that prevents reflexive single-intercept models. Something like:

> "By-subject random intercepts and random slopes for condition (within-subjects), distractor type (within-subjects), and their interaction, with correlations estimated. By-item random intercepts and a random slope for condition (each item appears in both conditions). Distractor type is between-items, so no by-item slope for distractor."

That's a fully specified maximal model. It maps directly to:

```r
y ~ condition * distractor + 
    (1 + condition * distractor | subject) + 
    (1 + condition | item)
```

## What to do when the maximal model has problems

Order of operations when convergence fails or you get a singular fit:

### a. Diagnose, don't just simplify

- Scale and center continuous predictors (Gelman & Hill: divide by 2 SDs)
- Use sum/effect coding instead of treatment coding for factors (especially when interactions are involved)
- Try a different optimizer (`bobyqa`, `nloptwrap`, `Nelder_Mead` in lme4)
- Increase max iterations
- Check for predictors that are nearly collinear within clusters

These fixes often resolve "convergence" issues without dropping any structure.

### b. Inspect the random-effects covariance matrix

```r
summary(model)$varcor
VarCorr(model)
isSingular(model)
```

Look for variance components estimated at exactly 0 and correlations at exactly ±1. Those are the parts the data doesn't support.

`rePCA()` in lme4 gives a PCA of the random-effects covariance and tells you how many dimensions are actually supported — Bates et al. (2015) recommend this directly.

### c. Drop in a principled order

1. First, drop correlation parameters (`||` instead of `|`) for the random-effects term with the degenerate correlation.
2. Next, drop the random slope for the *highest-order interaction* if its variance is at zero — and only on the grouping factor where the variance was zero.
3. Then lower-order interaction slopes, then main-effect slopes.
4. Never drop the random intercept (unless you have a strong reason, like a strictly within-subjects design with truly no between-subject variation — rare).

Document every drop and the diagnostic that motivated it.

### d. Consider a Bayesian fit instead

With weakly informative priors on variance components and an LKJ prior on the correlation matrix, brms or rstanarm will fit maximal models that lme4 chokes on. This is often the cleanest solution: you keep the design-justified structure, and the prior regularizes the variance components away from the boundary without forcing them to exactly zero. The Stan team and Gelman explicitly recommend this approach.

## Special cases worth knowing

### Crossed random effects (subjects × items)

Standard in psycholinguistics, vision, and judgment research. lme4 handles it natively: `y ~ x + (1 + x | subject) + (1 + x | item)`. No special syntax needed — lme4 figures out the crossing from the data.

### Nested random effects

Two levels nested (students in schools): `(1 | school/student)` is shorthand for `(1 | school) + (1 | school:student)`. But if your student IDs are unique across schools, `(1 | school) + (1 | student)` works the same way. If IDs are not unique (student 1 in school A and student 1 in school B are different people but share the ID), use the explicit nesting syntax or recode IDs to be unique.

### Cross-classified

Students belong to both schools and neighborhoods, which don't nest into each other. Specify both as crossed random effects: `(1 | school) + (1 | neighborhood)`.

### Random effects of time in longitudinal data

For growth-curve models, at minimum include a random slope for time: `(1 + time | subject)`. For nonlinear growth, consider random slopes for polynomial terms or splines, though these get expensive quickly. Gelman & Hill and Singer & Willett (*Applied Longitudinal Data Analysis*) cover this in depth.

### Heterogeneous variances

Sometimes you want different residual variances for different groups (e.g., experimental conditions). lme4 doesn't support this directly; use `nlme::lme` with `weights = varIdent(form = ~ 1 | group)` or `glmmTMB` with the `dispformula` argument, or just go Bayesian.

## A pre-flight checklist before fitting

Before running the model, you should be able to answer:

1. What are my grouping factors, and are they nested or crossed?
2. For each predictor, where does it vary (within/between each grouping factor)?
3. What's my maximal design-justified random-effects structure?
4. If the maximal model fails, what's my principled simplification path?
5. How many clusters do I have at each level — is frequentist estimation reasonable, or should I go Bayesian for regularization?

If you can't answer these, stop and ask the user. Don't fit first and rationalize after.

## Key references

- Barr, D. J., Levy, R., Scheepers, C., & Tily, H. J. (2013). Random effects structure for confirmatory hypothesis testing: Keep it maximal. *Journal of Memory and Language*, 68(3), 255–278.
- Bates, D., Kliegl, R., Vasishth, S., & Baayen, H. (2015). Parsimonious mixed models. arXiv:1506.04967.
- Matuschek, H., Kliegl, R., Vasishth, S., Baayen, H., & Bates, D. (2017). Balancing Type I error and power in linear mixed models. *Journal of Memory and Language*, 94, 305–315.
- Schielzeth, H., & Forstmeier, W. (2009). Conclusions beyond support: overconfident estimates in mixed models. *Behavioral Ecology*, 20(2), 416–420.
- Clark, H. H. (1973). The language-as-fixed-effect fallacy: A critique of language statistics in psychological research. *Journal of Verbal Learning and Verbal Behavior*, 12(4), 335–359.
