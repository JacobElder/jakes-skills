# Multiverse analysis — tooling reference

Read this to pick the right tool and recall its syntax. There are three good options; pick
based on the user's language and whether they want a self-contained run or a published
package's conventions.

- [Decision: which tool](#decision-which-tool)
- [Bundled engine (Python, no extra deps)](#bundled-engine-python-no-extra-deps)
- [R: the `multiverse` package](#r-the-multiverse-package)
- [R: `specr` (specification curve)](#r-specr-specification-curve)
- [Python: `specification_curve`](#python-specification_curve)
- [Boba (language-agnostic DSL + visualizer)](#boba-language-agnostic-dsl--visualizer)

## Decision: which tool

- **Working in Python, want a clean self-contained run + the standard curve + joint
  inference** → use the bundled `scripts/multiverse.py`. No install beyond pandas/numpy/
  matplotlib. Best default for analyses run inside this environment.
- **Working in Python on a regression coefficient across model variants** →
  `specification_curve` (pip) is purpose-built and concise.
- **Working in R** → `multiverse` (general, expressive DSL with `branch()`/`%when%`) or
  `specr` (specialized, batteries-included specification curves with nice plots).
- **Polyglot / want the published Boba Visualizer UI** → Boba.

Whatever the tool, the methodology in `methodology.md` is the same. The tool only handles
enumeration, execution, and plotting.

## Bundled engine (Python, no extra deps)

`scripts/multiverse.py`. You write one `analyze(data, choices)` function; the engine does the
rest. `choices` is a dict mapping each decision to its resolved option value.

```python
import sys; sys.path.insert(0, "<skill>/scripts")
from multiverse import Multiverse, specification_curve, decision_importance, permutation_test

def analyze(data, c):
    df = data.copy()
    if c["outliers"] is not None:                      # resolved option value
        z = (df["y"] - df["y"].mean()) / df["y"].std()
        df = df[z.abs() <= c["outliers"]]
    rhs = " + ".join(["group"] + c["covariate"])       # c["covariate"] is a list
    import statsmodels.formula.api as smf
    m = smf.ols(f'{c["dv"]} ~ {rhs}', data=df).fit()
    return {"estimate": m.params["group"], "p_value": m.pvalues["group"],
            "ci_low": m.conf_int().loc["group", 0],
            "ci_high": m.conf_int().loc["group", 1], "n": len(df)}

mv = Multiverse(
    decisions={
        "outliers":  {"none": None, "3sd": 3.0, "2sd": 2.0},      # names -> values
        "dv":        {"time": "time_to_top", "falls": "num_falls"},
        "covariate": {"none": [], "tod": ["time_of_day"]},
    },
    constraints=[lambda c: True],   # return False to drop a nonsensical combo
)

print(mv.summary())                 # counts before running
res = mv.run(analyze, data)         # tidy DataFrame, one row per universe
print(decision_importance(res))     # which decisions move the estimate (eta^2)
specification_curve(res, outfile="curve.png")
permutation_test(mv, analyze, data, shuffle="group", n_perm=500)  # joint inference
```

Key API: `Multiverse(decisions, constraints)`, `.summary()`, `.grid()`, `.n_total()`,
`.run(analyze, data, max_universes=None)`; `specification_curve(res, estimate=, p_value=,
ci=, decisions=, outfile=)`; `decision_importance(res)`; `permutation_test(mv, analyze,
data, shuffle=, stat_col=, n_perm=)`. The result DataFrame has a `.error` column — failed
universes are recorded, not fatal. Return whatever metrics you want from `analyze`; for the
curve, include at least `estimate` and ideally `p_value`, `ci_low`, `ci_high`.

## R: the `multiverse` package

MUCollective (Sarma & Kay). Declares alternatives inline with `branch()` inside a multiverse
object; `%when%` encodes conditions.

```r
library(multiverse); library(dplyr); library(broom)
# Example uses the package's built-in hurricane dataset.
# Column names: Name, alldeaths, MasFem (femininity scale), NDAM (damage),
# Minpressure_Updated_2014. Derive zpressure before building the multiverse.
data("hurricane")
hurricane <- hurricane |> mutate(zpressure = scale(Minpressure_Updated_2014)[, 1])

M <- multiverse()

inside(M, {
  df <- hurricane |>
    filter(branch(outliers,
      "none"      ~ TRUE,
      "exclude2"  ~ !(.data$Name %in% c("Katrina", "Audrey"))))
  fit <- glm(branch(model, "linear" ~ log(alldeaths + 1), "poisson" ~ alldeaths) ~
             MasFem * branch(sev, "damage" ~ NDAM, "pressure" ~ zpressure),
             family = branch(model, "linear" ~ gaussian, "poisson" ~ poisson),
             data = df)
  est <- broom::tidy(fit) |> filter(.data$term == "MasFem")
})

parameters(M)            # decisions + options the package parsed
expand(M)                # one row per universe (the grid)
execute_multiverse(M)    # run all; one failure does not stop the rest
extract_variables(M, est) |> tidyr::unnest(est)   # pull results into a tidy table
```
`branch(<parameter>, "<option>" ~ <expr>, ...)`. Reuse the same parameter name across
several `branch()` calls when one decision changes code in multiple places (same option
names required). Conditions: `"opt" %when% (other_param == "x") ~ <expr>`.

## R: `specr` (specification curve)

Masur & Scharkow. Specialized for specification curves; less boilerplate when the multiverse
is "this y, this x, these controls, these subsets, these models."

```r
library(specr)
specs <- setup(data = d,
  y = c("y1", "y2"), x = c("x1", "x2"),
  model = c("lm", "glm"),
  controls = c("c1", "c2"),
  subsets = list(group = unique(d$group)))
results <- specr(specs)
summary(results)
plot(results)            # the two-panel specification curve
```
Note the authors' explicit caution: specr is for studying how choices affect the outcome,
**not** a tool to fish for a better estimate.

## Python: `specification_curve`

`pip install specification-curve` (aeturrell). Varies a focal coefficient across combinations
of dependent vars, controls, and fixed effects.

```python
from specification_curve import SpecificationCurve
sc = SpecificationCurve(
    df, y_endog=["y1", "y2"], x_exog=["x1"],
    controls=["c1", "c2", "c3"])
sc.fit()                 # runs all specifications
sc.plot()                # specification curve plot
```

## Boba (language-agnostic DSL + visualizer)

`pip install boba boba-visualizer` (Liu, Kale, Althoff & Heer, 2020). Write the shared
analysis once with inline `{{decision}}` placeholders and decision blocks; the compiler
generates one script per universe (Python or R), runs them, merges outputs, and opens an
interactive visualizer. Use when you want the published UI for exploring the decision space,
or a polyglot pipeline.

```python
# template.py  (Boba template; --- markers and placeholders are Boba DSL, not Python)
# --- (BOBA_CONFIG)
# {"decisions":[{"var":"outlier","options":["none","sd3"]}],
#  "constraints":[{"block":"linear","condition":"dv != binary"}]}
# --- (NMO) include / exclude options as decision blocks ...
```
CLI: `boba compile template.py` → `boba run --all` → `boba-visualizer`. The DSL is agnostic
to the underlying analysis language. For most in-environment Python work the bundled engine
is simpler; reach for Boba when the visualizer or multi-language support is the point.
