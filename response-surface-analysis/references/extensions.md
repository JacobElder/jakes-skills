# Extensions and advanced variants

When the basic single-level, observed-variable RSA isn't enough. Each section
says when you need it and where the method lives.

## Cubic RSA (asymmetric & level-dependent congruence)
Second-order RSA can't capture some realistic patterns — e.g. congruence whose
benefit depends on the *level* of agreement, or where the cost of mismatch grows
asymmetrically and nonlinearly. Cubic RSA adds third-order terms
(X³, X²Y, XY², Y³) and a corresponding extended parameter set. Use it when theory
predicts level-dependent or asymmetric congruence and you have the N (cubic terms
are even hungrier). Implementation: the R `RSA` package supports `models` with
third-order options; see Humberg, Schönbrodt, Back & Nestler, *Cubic response
surface analysis*, Psychological Methods. The bundled Python script is quadratic
only — switch to R for cubic.

## Multilevel RSA
When observations are nested (employees in teams, days within persons in ESM
data, pupils in schools) the single-level standard errors are wrong and the
congruence effect itself may vary across or depend on Level-2 covariates. Nestler,
Humberg & Schönbrodt (2019, *Psychological Methods*) extend RSA to multilevel
data: estimate the polynomial in a mixed model, then compute the surface
parameters and their (correct) SEs from the fixed effects. Decide explicitly
whether the congruence effect is modeled as fixed or random across clusters, and
whether it's moderated by a Level-2 variable. This connects to the idiographic /
DSEM world for intensive longitudinal data — keep the levels-of-analysis question
front and center.

## Dyadic RSA
For dyads (couples, supervisor–subordinate, parent–child) where both members
provide predictors and/or outcomes, RSA can be embedded in an APIM-style or SEM
framework. Schönbrodt, Humberg & Nestler (2018) and Nestler et al. (2015) develop
dyadic RSA. Watch non-independence and distinguishability of dyad members.

## Latent-variable / errors-in-variables RSA
Measurement error in the predictors attenuates exactly the quadratic and product
terms that carry the congruence signal (Su, Zhang et al., 2019). When predictor
reliabilities are modest, observed-variable RSA is biased toward null curvature.
Remedies: model the predictors as latent (SEM with product/quadratic indicators,
e.g. via a latent moderated structural approach), or at least report
reliabilities and treat the surface as a lower bound on curvature. The R `RSA`
package's lavaan backend makes some latent extensions feasible; full LMS-style
estimation may need Mplus or a custom lavaan/`modsem` setup.

## Control variables in RSA
Adding covariates is legitimate but subtle: you must add them as *linear* controls
without disturbing the five polynomial terms, and you should think about whether a
control is a confounder (good to include) or a mediator/collider (bad). Centering
of controls doesn't affect the surface parameters but does affect the intercept.
Don't control away the very level/main effects that distinguish broad from strict
congruence unless that's your intent.

## The block-variable significance test
Edwards's "block variable" approach builds a single composite from the weighted
polynomial terms to get an omnibus significance test for the whole surface (useful
for reporting one test of "does the surface matter") and for comparing surfaces
across groups. It complements — does not replace — the parameter-level checklist.
Shanock et al. (2010) walk through it with syntax.

## Comparing surfaces across groups / conditions
To ask whether the congruence effect differs between groups (e.g. men vs. women,
treatment vs. control), fit a model with the group × (all five polynomial terms)
interactions and test the block of interaction terms, or fit RSA per group and
compare parameters with their CIs. Don't eyeball two separate surfaces and declare
a difference.

## Choosing among all of this
Default to single-level observed-variable RSA only when: observations are
independent, predictor reliabilities are good, the quadratic surface is adequate,
and you have one group. Each violated assumption points to a specific extension
above. When several apply at once (e.g. dyadic + latent), you're in SEM territory
and R/Mplus, not the Python script.
