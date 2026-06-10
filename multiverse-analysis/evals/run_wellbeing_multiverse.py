import sys
sys.path.insert(0, "/Users/jacobelder/Documents/GitHub/jakes-skills/multiverse-analysis/scripts")
from multiverse import Multiverse, specification_curve, decision_importance, permutation_test

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

data = pd.read_csv(
    "/Users/jacobelder/Documents/GitHub/jakes-skills/multiverse-analysis/evals/wellbeing_study.csv"
)

def analyze(data, c):
    df = data.copy()

    # 1. Apply outcome transformation
    if c["transformation"] == "log":
        df["dv"] = np.log(df["wellbeing_post"])
    else:
        df["dv"] = df["wellbeing_post"]

    # 2. Outlier exclusion on the (possibly transformed) DV
    if c["outliers"] is not None:
        z = (df["dv"] - df["dv"].mean()) / df["dv"].std()
        df = df[z.abs() <= c["outliers"]].copy()

    # 3. Fit OLS; covariate is [] or ["wellbeing_pre"]
    covs = c["covariate"]
    rhs = " + ".join(["group"] + covs) if covs else "group"
    m = smf.ols(f"dv ~ {rhs}", data=df).fit()

    # Standardize by the DV SD within this universe so raw and log estimates are comparable
    dv_sd = df["dv"].std(ddof=1)
    return {
        "estimate":     m.params["group"] / dv_sd,
        "raw_estimate": m.params["group"],
        "p_value":      m.pvalues["group"],
        "ci_low":       m.conf_int().loc["group", 0] / dv_sd,
        "ci_high":      m.conf_int().loc["group", 1] / dv_sd,
        "n":            len(df),
    }

mv = Multiverse(
    decisions={
        "outliers":       {"none": None, "3sd": 3.0, "2.5sd": 2.5},
        "covariate":      {"none": [], "wellbeing_pre": ["wellbeing_pre"]},
        "transformation": {"raw": "raw", "log": "log"},
    }
)

print("=" * 60)
print(mv.summary())
print("=" * 60)

res = mv.run(analyze, data, progress=False)

# Per-universe table
display_cols = ["outliers", "covariate", "transformation",
                "estimate", "raw_estimate", "p_value", "n"]
print("\nAll 12 universes:")
print(res[display_cols].round(4).to_string(index=False))

# Decision importance
print("\nDecision importance:")
print(decision_importance(res).round(4).to_string(index=False))

# Specification curve
specification_curve(
    res,
    title="Treatment effect (standardized β) — mindfulness RCT wellbeing",
    highlight={"outliers": "none", "covariate": "none", "transformation": "raw"},
    outfile="/Users/jacobelder/Documents/GitHub/jakes-skills/multiverse-analysis/evals/multiverse_wellbeing_curve.png",
    figsize=(11, 7),
)

# Save tidy results
res.to_csv(
    "/Users/jacobelder/Documents/GitHub/jakes-skills/multiverse-analysis/evals/multiverse_wellbeing_results.csv",
    index=False,
)
print("\nResults saved to multiverse_wellbeing_results.csv")

# Joint permutation inference (500 permutations)
print("\nRunning joint permutation test (500 perms)…")
perm = permutation_test(
    mv, analyze, data,
    shuffle="group",
    n_perm=500,
    direction="positive",
)
