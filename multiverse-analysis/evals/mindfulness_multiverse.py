"""
Mindfulness intervention multiverse analysis.

Focal estimand: treatment effect of group (1=treatment, 0=control) on wellbeing_post.
12 universes: 3 outlier rules × 2 covariate specs × 2 outcome transforms.

Scale note: raw and log-transformed estimates live on different scales, so
estimates are standardized by SD(outcome) within each universe before the
specification curve and decision-importance calculations. All reported
estimates are Cohen's-d-like standardized effects.
"""
import sys, os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from multiverse import Multiverse, specification_curve, decision_importance, permutation_test

# ── 1. Data ───────────────────────────────────────────────────────────────────
data = pd.read_csv(os.path.join(os.path.dirname(__file__), "wellbeing_study.csv"))
print(f"Dataset: n={len(data)}  (treatment={data['group'].sum()}, control={(data['group']==0).sum()})")
print(f"wellbeing_post: M={data['wellbeing_post'].mean():.1f}, SD={data['wellbeing_post'].std():.1f}")
print(f"Control post:   M={data[data.group==0]['wellbeing_post'].mean():.1f}")
print(f"Treatment post: M={data[data.group==1]['wellbeing_post'].mean():.1f}")

# ── 2. Analysis function ──────────────────────────────────────────────────────
def analyze(data, c):
    df = data.copy()

    # Outlier exclusion on raw wellbeing_post (before transformation so thresholds
    # stay on an interpretable scale regardless of which transform is active)
    if c["outliers"] is not None:
        z = (df["wellbeing_post"] - df["wellbeing_post"].mean()) / df["wellbeing_post"].std()
        df = df[z.abs() <= c["outliers"]]

    # Outcome transformation
    if c["transform"] == "log":
        df = df.assign(dv=np.log(df["wellbeing_post"]))
    else:
        df = df.assign(dv=df["wellbeing_post"])

    # Fit model
    rhs = " + ".join(["group"] + c["covariate"])
    m = smf.ols(f"dv ~ {rhs}", data=df).fit()

    est   = m.params["group"]
    dv_sd = df["dv"].std()
    ci    = m.conf_int().loc["group"]
    return {
        "estimate":     est / dv_sd,          # standardized for comparability
        "raw_estimate": est,
        "p_value":      m.pvalues["group"],
        "ci_low":       ci[0] / dv_sd,
        "ci_high":      ci[1] / dv_sd,
        "n":            int(len(df)),
    }

# ── 3. Multiverse setup ───────────────────────────────────────────────────────
mv = Multiverse(
    decisions={
        "outliers":  {"none": None, "3sd": 3.0, "2.5sd": 2.5},
        "covariate": {"none": [], "pre": ["wellbeing_pre"]},
        "transform": {"raw": "raw", "log": "log"},
    },
    constraints=[lambda c: True],
)
print("\n" + mv.summary())

# ── 4. Run all universes ──────────────────────────────────────────────────────
res = mv.run(analyze, data)

print("\nAll universes (sorted by standardized estimate):")
cols = ["outliers", "covariate", "transform", "estimate", "raw_estimate", "p_value", "n"]
print(res.sort_values("estimate")[cols].reset_index(drop=True)
      .to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# Where does the original analysis land?
orig = res[(res["outliers"]=="none") & (res["covariate"]=="none") & (res["transform"]=="raw")]
orig_est = orig["estimate"].values[0]
orig_p   = orig["p_value"].values[0]
orig_rank = int((res["estimate"] < orig_est).sum()) + 1
print(f"\nOriginal analysis (no exclusions, no covariate, raw outcome): "
      f"d = {orig_est:.3f}, p = {orig_p:.3f}  [rank {orig_rank} of {len(res)}]")

# ── 5. Decision importance ────────────────────────────────────────────────────
print("\n── Decision importance ──────────────────────────────────────────────────")
imp = decision_importance(res)
print(imp.to_string(index=False))

# ── 6. Specification curve ────────────────────────────────────────────────────
specification_curve(
    res,
    outfile=os.path.join(os.path.dirname(__file__), "mindfulness_curve.png"),
)
print("\nCurve saved → evals/mindfulness_curve.png")

# ── 7. Joint permutation inference ───────────────────────────────────────────
print("\n── Joint permutation test (500 perms, direction=positive) ───────────────")
permutation_test(mv, analyze, data, shuffle="group", n_perm=500, direction="positive")

# ── 8. Save tidy results ──────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "mindfulness_results.csv")
res.to_csv(out, index=False)
print(f"Results saved → {out}")
