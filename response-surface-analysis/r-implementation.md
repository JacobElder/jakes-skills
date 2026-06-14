# R implementation — the `RSA` package

The `RSA` package (Felix Schönbrodt; v0.10.x, lavaan backend) is the reference
implementation. Prefer it for serious work: it fits the full nested model family,
bootstraps every parameter, and plots well. Runnable template:
`scripts/rsa_template.R`.

## Install and fit

```r
install.packages("RSA")
library(RSA)

MID <- 4                      # YOUR scale midpoint
df$X <- df$predX - MID        # center BOTH on the common constant
df$Y <- df$predY - MID

r <- RSA(Z ~ X * Y, data = df,
         models = c("full","SQD","SSQD","SRSQD","RR"),
         center = "none")     # we centered manually; don't double-center
```

The `Z ~ X * Y` formula is special syntax: RSA expands it to the full
second-order polynomial internally. `center = "none"` tells it to trust your
pre-centering.

## The model family (what the names mean)

| Model | Meaning | Use |
|-------|---------|-----|
| `full` | unconstrained 2nd-order polynomial | the reference model |
| `SQD` | basic squared difference `Z = b0 − k(X−Y)²` | **strict** congruence target |
| `SSQD` | shifted squared difference | congruence whose peak is shifted along the LOC |
| `SRSQD` | shifted & rotated squared difference | **broad** congruence target |
| `RR` | rising ridge | congruence *plus* a linear LOC effect (level matters) |
| `RRCA`/`CA` | (rotated) level-/asymmetry- dependent | asymmetric congruence |

Confirmatory logic: pre-register your target (often `SRSQD` for broad, `SQD` for
strict) and rivals, then `compare(r)`.

## Read the output

```r
compare(r)                 # model comparison: df, AIC, BIC, CFI, LR tests
summary(r$models$full)     # lavaan summary of the full model
getPar(r, "coef")          # b's AND a1..a5, p10, p11 with CIs
getPar(r, "R2")            # R^2
```

For bootstrap CIs (recommended — the a's and p's are nonlinear in the b's):

```r
r_boot <- RSA(Z ~ X * Y, data = df, models = "full",
              center = "none", se = "boot")
getPar(r_boot, "coef")     # CIs are now bootstrapped
```

Map `getPar` output to the checklist: `a4` (want CI < 0), `a3` (want CI ∋ 0),
`p10` (want CI ∋ 0), `p11` (want CI ∋ 1). For strict, add `a1`, `a2` (want CI ∋ 0).

## Plot

```r
plot(r, model = "full",
     xlab="X (centered)", ylab="Y (centered)", zlab="Outcome",
     legend = TRUE, project = c("LOC","LOIC","PA1"))
plot(r, type = "contour")        # contour companion
plot(r, type = "interactive")    # rgl 3-D (needs rgl)
```

## Gotchas

- **Double-centering.** If you both pre-center and leave `center` at its default,
  you center twice. Pick one; the template pre-centers and sets `center="none"`.
- **lavaan convergence.** Constrained models occasionally fail to converge,
  especially with small N or extreme collinearity. Check `compare()` warnings;
  don't compare to a model that didn't converge.
- **`se = "boot"` is slower** but correct; budget for it on the final fit.
- The package also handles **multilevel** (`RSA` with cluster structure via
  helper functions) and **dyadic** designs — see `extensions.md`.

References shipped with the package: Edwards (2002); Humberg, Nestler & Back
(2019); Nestler, Humberg & Schönbrodt (2019, multilevel); Humberg et al. (cubic).
