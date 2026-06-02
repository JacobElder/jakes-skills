---
name: multiverse-analysis
description: >-
  Run, build, or report a multiverse / specification-curve analysis: making the
  arbitrary-but-defensible choices in a data analysis explicit, running the analysis under
  every reasonable combination of those choices, and reporting the whole distribution of
  results instead of one hand-picked number. Use this whenever someone wants to test how
  robust a finding is to analytic choices, asks "would the result hold under different
  specifications / outlier rules / covariates / operationalizations", mentions multiverse
  analysis, specification curve analysis, researcher degrees of freedom, garden of
  forking paths, vibration of effects, or sensitivity-to-specification — and also when a
  user is anxious that their regression/effect "might just be an artifact of how I set up
  the analysis" even without knowing the term. Covers eliciting the decision set, enumerating
  and executing universes, plotting the specification curve, quantifying which decisions
  matter, and joint permutation inference, in Python (bundled engine) or R.
---

# Multiverse analysis

A multiverse analysis takes the decisions an analyst usually makes silently — which outliers
to drop, how to operationalize a variable, which covariates to add, which model to fit — and
instead of committing to one path, runs *every reasonable combination* and reports the full
distribution of results. It answers "does this finding actually depend on choices I made
arbitrarily?" The point is transparency and robustness, **not** finding a better single
estimate. (Steegen et al. 2016; Simonsohn, Simmons & Nelson 2020.)

The mechanics are easy. The judgment — choosing a decision set that is complete and
defensible, spotting nonsensical combinations, and framing the result honestly — is where
the value is. Spend your effort there.

## Workflow

Work through these steps. Steps 1–3 are reasoning with the user; 4–7 are execution.

1. **Pin the focal estimand.** Identify the *one* quantity whose robustness is in question —
   a specific coefficient, a mean difference, a correlation. Everything else is a nuisance
   decision the multiverse will vary. If this is unclear, ask before building anything.
2. **Elicit the decision set.** This is the crux. Enumerate the points in the analysis where
   a different, equally defensible choice was possible, and the reasonable options at each.
   Probe the common families below — most analyses have 4–8 live decisions hiding in them,
   and people under-report their own. For each option apply the "reasonable" test: it must be
   theory-consistent, statistically valid, and non-redundant. **Curate** — do not pad with
   options nobody would defend; a bloated multiverse dilutes the signal.
   - **Exclusions**: outlier rules (none / 2.5 SD / 3 SD / IQR / winsorize), quality filters,
     missing-data handling.
   - **Operationalization of the IV/DV**: which measure, composite vs item, binary vs
     continuous, raw vs standardized. *Probe this hardest — it usually drives the most
     variance* (Schweinsberg et al. 2021).
   - **Transformations**: log/sqrt/none, centering, scaling.
   - **Covariates**: which controls, which interactions.
   - **Model/estimator**: OLS vs GLM family, linear vs logistic vs count, random effects,
     robust SEs, frequentist vs Bayesian.
   - **Sample/subgroup**: full vs theoretically motivated subsets.

   Present the set back to the user as a decisions × options table for sign-off. Distinguish
   **principled** decisions (theory gives a range — include it) from **arbitrary** ones
   (include common conventions).
3. **Flag nonsensical cells.** A raw cross-product produces incoherent combinations (a linear
   model on a binary DV; an interaction whose main term is absent; an option only meaningful
   given an upstream choice). List these and encode them as constraints/conditions so they
   never run.
4. **Implement the analysis once, parameterized by the choices, and execute every universe.**
   Use the bundled engine (below) for Python, or `multiverse`/`specr`/`boba` (see
   `references/tooling.md`). One failed universe should be recorded, not fatal.
5. **Describe the distribution.** Draw the specification curve (sorted estimates + a panel
   showing which option was active in each spec). Report the median effect, the share of
   specifications significant and *in which direction*, and how many universes errored. When
   options put the estimate on different scales (e.g. DV measures with different ranges, raw
   vs standardized), put estimates on a **common scale** (a standardized effect) before
   comparing — otherwise the curve conflates unit differences with genuine robustness, and a
   "scale" fork will dominate the variance for trivial reasons.
6. **Quantify which decisions matter.** Report per-decision influence (η² / spread) so you
   can say *which* forks drive the dispersion — e.g. "the effect is significant only when
   outliers are kept."
7. **Do joint inference if an inferential claim is wanted.** Permutation test on the curve as
   a whole (below). Then **report honestly** using the template in `references/methodology.md`.

For the conceptual depth behind any step — the data-vs-modelling multiverse, the
"reasonable specification" criteria, inference caveats, interpretation, and the reporting
template — read `references/methodology.md`.

## Executing with the bundled engine

`scripts/multiverse.py` is a dependency-light engine (pandas/numpy/matplotlib only). You
supply one `analyze(data, choices)` function returning a results dict; the engine enumerates
the grid (honoring constraints), runs every universe without letting failures cascade,
tidies the output, and provides the curve, decision-importance, and permutation inference.

```python
import sys; sys.path.insert(0, "<path-to-skill>/scripts")
from multiverse import Multiverse, specification_curve, decision_importance, permutation_test

def analyze(data, c):                       # c = {decision: resolved_option_value}
    df = data.copy()
    if c["outliers"] is not None:
        z = (df[c["dv"]] - df[c["dv"]].mean()) / df[c["dv"]].std()
        df = df[z.abs() <= c["outliers"]]
    import statsmodels.formula.api as smf
    rhs = " + ".join(["group"] + c["covariate"])
    m = smf.ols(f'{c["dv"]} ~ {rhs}', data=df).fit()
    return {"estimate": m.params["group"], "p_value": m.pvalues["group"],
            "ci_low": m.conf_int().loc["group", 0],
            "ci_high": m.conf_int().loc["group", 1], "n": len(df)}

mv = Multiverse(
    decisions={
        "outliers":  {"none": None, "3sd": 3.0, "2sd": 2.0},
        "dv":        {"time": "time_to_top", "falls": "num_falls"},
        "covariate": {"none": [], "tod": ["time_of_day"]},
    },
    # drop nonsensical combos before they run; return False to exclude:
    constraints=[lambda c: True],
)

print(mv.summary())                  # universe counts before running
res = mv.run(analyze, data)          # tidy DataFrame; failed cells in res[".error"]
print(decision_importance(res))      # which decisions move the estimate
specification_curve(res, outfile="curve.png")
permutation_test(mv, analyze, data, shuffle="group", n_perm=500)  # joint inference
```

If `analyze` needs a package that is missing, install it (`pip install statsmodels
--break-system-packages`). The engine itself needs nothing beyond the core scientific stack.
For very large grids, pass `max_universes=N` to `run()` to estimate a random subset. Full API
and the R/Boba equivalents are in `references/tooling.md`.

## Joint inference, briefly

With hundreds of specifications, some will be significant by chance, so "is any single spec
significant?" is the wrong question. The right one is "is the curve *as a whole* inconsistent
with the null?" `permutation_test()` answers it: it shuffles the focal predictor to break its
link with the outcome, re-runs the entire multiverse on each shuffled dataset, and compares
the observed statistics (median effect; share significant in the predicted direction) to
their null distributions. Use ≥500 permutations for anything you would report.

## Framing the result honestly

- A multiverse is a **robustness/transparency** tool, not a way to select the specification
  you like. Never present the curve as cover for one cherry-picked path.
- Report where the user's *original* analysis falls within the distribution.
- "Robust" looks like: tight cluster, consistent sign, large share significant one way, joint
  test rejects null. "Fragile" looks like: estimates straddling zero, sign flips, minority
  significant, null not rejected — say so plainly.
- The share of significant specifications is **not** the probability the effect is real;
  specifications are neither independent nor equally likely. It is a sensitivity display.

## Output

When the user wants a write-up, produce: the focal estimand; the decisions × options table
with one-line justifications (and notable rejected options); universe count and any sampling;
the specification curve figure; median effect and share/direction significant; the
decision-importance summary; the joint-inference result if claimed; and where the original
analysis sits. Save the curve as a figure and, for a substantial deliverable, the tidy
results table as CSV so the multiverse can be re-run or extended.
