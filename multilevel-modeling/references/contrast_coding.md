# Contrast Coding for Categorical Predictors in MLM

Contrast coding decides what your fixed-effect coefficients *mean*. The same model fit with different contrasts gives mathematically equivalent predictions but radically different parameter interpretations — especially when interactions are involved. Getting this wrong is a quiet, widespread error in applied MLM, and a particular trap when porting ANOVA habits to lme4.

The canonical modern treatment is Schad, Vasishth, Hohenstein & Kliegl (2020), "How to capitalize on a priori contrasts in linear (mixed) models," *Journal of Memory and Language*, 110, 104038.

## Why contrast coding matters more in MLM than OLS

In OLS, contrast choice mostly affects how you read the coefficient table — the inference for any contrast you actually care about is recoverable with `emmeans` or hand calculation. In MLM, contrast coding has three additional consequences:

1. **Random slopes change meaning.** A random slope for a 2-level factor with treatment coding represents between-cluster variability in "the difference between control and treatment for this cluster." With sum/contrast coding (-0.5, 0.5), it represents the same thing but centered, which often makes the random-effects covariance better conditioned and less prone to convergence problems.

2. **Main effects in interaction models change meaning.** With treatment coding and an interaction A × B, the "main effect" of A is *the effect of A when B is at its reference level*, not the average effect of A. People constantly misread these as average effects. With sum/effects coding, main effects are average effects (what most people actually wanted).

3. **Convergence and singular fits.** Treatment-coded factors with interactions create correlations among predictors that show up in the random-effects covariance matrix. Sum coding decorrelates these and substantially reduces convergence failures in maximal models — independent of any inferential consideration.

## The four codings you need to know

For a 2-level factor with levels {A, B}:

| Coding | Values | Intercept means | Slope means |
|---|---|---|---|
| Treatment (R default) | A=0, B=1 | Predicted value at A | Difference B − A |
| Sum / effects | A=−1, B=+1 | Grand mean of A and B | Half of difference B − A |
| Contrast / "deviation" | A=−0.5, B=+0.5 | Grand mean of A and B | Difference B − A |
| Helmert | varies | Grand mean | Successive contrasts |

The (−0.5, +0.5) contrast coding is what Schad et al. recommend as a default for 2-level factors: intercept is the grand mean (good), and the slope is directly the difference between conditions (good — no factor-of-2 confusion).

For factors with more than 2 levels, the choice is more consequential and should map to your *a priori* hypotheses:

- **Treatment**: compare each level to a reference. Right when one level is genuinely the baseline (control vs. drug 1, drug 2, drug 3).
- **Sum/effects**: each non-reference level vs. the grand mean. Sensible when no level is special.
- **Helmert / reverse Helmert**: ordered comparisons (level 2 vs. level 1, level 3 vs. average of 1+2, etc.). Right for ordered conditions where you want to test successive differences.
- **Polynomial**: linear, quadratic, cubic trends across ordered levels. Right when the levels represent equally spaced values of a continuous-ish construct (dose, age band).
- **Custom orthogonal contrasts**: encode your specific hypotheses. The best choice when you have a small number of theoretically motivated contrasts.

The cleanest practice: write down your *a priori* hypotheses, then choose the coding that makes those hypotheses correspond to single coefficients you can read directly off the table.

## How to set contrasts in R

```r
# Inspect default
contrasts(d$condition)

# Change to sum coding (-1, +1 for 2-level; sum-to-zero for more levels)
contrasts(d$condition) <- contr.sum(levels(d$condition))

# Change to (-0.5, +0.5) for 2 levels
contrasts(d$condition) <- matrix(c(-0.5, 0.5), ncol = 1,
                                  dimnames = list(NULL, "B_vs_A"))

# Helmert
contrasts(d$condition) <- contr.helmert(3)

# Polynomial (for an ordered factor)
contrasts(d$dose) <- contr.poly(4)

# Custom contrasts: rows = levels, columns = contrasts
# Example: 3 levels {control, dose1, dose2}; two contrasts: drug-vs-control and dose1-vs-dose2
contrasts(d$condition) <- matrix(
  c(-2/3,  1/3,  1/3,    # drug vs. control
    0,    -1/2,  1/2),   # dose1 vs. dose2
  ncol = 2,
  dimnames = list(NULL, c("drug_vs_ctrl", "dose1_vs_dose2"))
)
```

A useful trick: use the `hypr` package (Rabe et al., 2020), which lets you specify hypotheses in plain notation and generates the contrast matrix automatically. Cleaner than hand-coding for non-trivial contrasts.

```r
library(hypr)
h <- hypr(
  drug_vs_ctrl = (dose1 + dose2)/2 ~ control,
  dose1_vs_dose2 = dose1 ~ dose2,
  levels = c("control", "dose1", "dose2")
)
contrasts(d$condition) <- contr.hypothesis(h)
```

## How to set contrasts in Python

statsmodels uses Patsy formulas with contrast specifications:

```python
import statsmodels.formula.api as smf

# Treatment (default in patsy too)
fit = smf.mixedlm("y ~ C(condition, Treatment(reference='control'))", 
                  data=d, groups=d["subject"]).fit()

# Sum coding
fit = smf.mixedlm("y ~ C(condition, Sum)", data=d, groups=d["subject"]).fit()

# Helmert
fit = smf.mixedlm("y ~ C(condition, Helmert)", data=d, groups=d["subject"]).fit()
```

For bambi, use the same Patsy-style notation in the formula.

## The interaction trap

This is the most consequential reason to care about contrast coding. Consider a 2×2 design with treatment coding (A coded 0/1, B coded 0/1) and the model `y ~ A * B`:

- **Intercept**: predicted y when A=0 AND B=0 (i.e., the cell mean for the reference of both factors). Not the grand mean.
- **Main effect of A** (coefficient on A): difference between A=1 and A=0 *when B=0*. This is a simple effect, not an average effect.
- **Main effect of B**: difference between B=1 and B=0 *when A=0*. Also a simple effect.
- **A:B interaction**: difference in the A effect across levels of B (or equivalently, in the B effect across levels of A).

So in a treatment-coded interaction model, the "main effects" depend on which level you chose as reference for the *other* factor. This is why running the same model with a different reference level gives different main effect coefficients but the same predictions and the same interaction.

With sum coding (−1, +1 or contrast coding −0.5, +0.5) and the same model:

- **Intercept**: grand mean across all four cells.
- **Main effect of A**: average effect of A, marginalized across B. What most analyses actually want.
- **Main effect of B**: average effect of B, marginalized across A.
- **A:B interaction**: same thing as before, but the parametrization is centered.

For analyses where you'd run an ANOVA and report "main effects," sum or contrast coding is what makes the MLM output correspond to those ANOVA main effects. Treatment-coded "main effects" are simple effects under a different name.

## Centering continuous predictors is a related issue

The same logic applies to continuous predictors in interaction models. Without centering, the "main effect" of A in `y ~ A * B` is the effect of A when B = 0 — which may or may not be a meaningful value. After mean-centering B, the main effect of A is the average effect across the range of B (more interpretable).

Gelman's recommendation: center continuous predictors and divide by 2 SDs. This gives coefficients on a comparable scale to dummy-coded binary predictors and reduces collinearity in interaction models.

## Decision flowchart

1. Is the predictor a 2-level factor?
   - **Yes**: Use (−0.5, +0.5) contrast coding. Intercept = grand mean, coefficient = difference. Done.
2. Is the predictor a 3+ level factor with a clear baseline (control)?
   - **Yes**: Treatment coding with control as reference is fine — but be careful interpreting "main effects" in interaction models.
3. Is the predictor a 3+ level factor without a baseline, where you'd report "main effects" in ANOVA terms?
   - **Yes**: Sum or contrast coding so main effects are average effects.
4. Is the predictor a 3+ level factor with theoretically motivated comparisons?
   - **Yes**: Custom orthogonal contrasts (use `hypr` for clarity), or Helmert for successive comparisons.
5. Is the predictor an ordered factor with equally spaced levels representing a continuous construct?
   - **Yes**: Polynomial contrasts (linear, quadratic, etc.).
6. Continuous predictor in an interaction?
   - Mean-center it. Consider dividing by 2 SDs.

## When the coding affects convergence

For complex random-effects structures (random slopes for multiple factors, especially with interactions), sum/contrast coding decorrelates the random-effects covariance and often resolves singular fits that treatment coding produced. If you have a model that won't converge with treatment coding, switching to sum coding before dropping any random effects is one of the first things to try.

This isn't a hack — it's that treatment-coded interaction slopes are *defined* in a way that creates strong correlations among random-effect parameters that have nothing to do with the underlying structure. Sum coding removes that artifact.

## A worked example

A 2 (condition: control vs. treatment) × 2 (timing: early vs. late) within-subjects design.

```r
# Default (treatment) — main effects are simple effects
contrasts(d$condition)  # control=0, treatment=1
contrasts(d$timing)     # early=0, late=1

fit_tx <- lmer(y ~ condition * timing + 
                 (1 + condition * timing | subject), data = d)
# Coefficient "condition": treatment-vs-control AT early timing
# Coefficient "timing": late-vs-early AT control
# Often gets misreported as "average treatment effect"

# Better: contrast coding
contrasts(d$condition) <- matrix(c(-0.5, 0.5), dimnames = list(NULL, "tx"))
contrasts(d$timing)    <- matrix(c(-0.5, 0.5), dimnames = list(NULL, "late"))

fit_c <- lmer(y ~ condition * timing + 
                (1 + condition * timing | subject), data = d)
# Intercept: grand mean across all 4 cells
# "conditiontx": average treatment effect across timing
# "timinglate": average timing effect across condition
# Interaction interpretation: same as before
```

Both models give identical predictions. But `fit_c`'s coefficients map to the inferential questions you probably care about; `fit_tx`'s don't.

## Reporting

In the methods section, state the coding explicitly:

> Categorical predictors were sum-coded so that fixed-effect coefficients represent average effects across levels of other factors (Schad et al., 2020).

Or:

> The treatment factor was coded with control as the reference level (0); coefficients therefore represent treatment-vs-control differences.

Either is fine. Silence on contrast coding leaves the reader to guess.

## Key references

- Schad, D. J., Vasishth, S., Hohenstein, S., & Kliegl, R. (2020). How to capitalize on a priori contrasts in linear (mixed) models: A tutorial. *Journal of Memory and Language*, 110, 104038.
- Rabe, M. M., Vasishth, S., Hohenstein, S., Kliegl, R., & Schad, D. J. (2020). hypr: An R package for hypothesis-driven contrast coding. *Journal of Open Source Software*, 5(48), 2134.
- Brehm, L., & Alday, P. M. (2022). Contrast coding choices in a decade of mixed models. *Journal of Memory and Language*, 125, 104334.
