"""
Multiverse analysis: randomized mindfulness intervention
Outcome: wellbeing_post (0-100), predictor: group (1=treatment, 0=control)
3 decisions × 12 universes total:
  - outlier rule : none | 2.5 SD | 3 SD  (on wellbeing_post)
  - covariate    : none | wellbeing_pre
  - transformation: raw | log(wellbeing_post)

Original analysis: no outliers, no covariate, raw outcome.
"""

import io
import sys
import os
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from multiverse import Multiverse, specification_curve, decision_importance, permutation_test

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
RAW = """subject_id,group,wellbeing_pre,wellbeing_post
S001,0,56.3,59.0
S002,0,60.0,64.0
S003,0,52.5,59.5
S004,1,58.7,74.5
S005,0,49.7,72.5
S006,1,52.1,20.0
S007,1,51.9,74.6
S008,0,45.4,39.7
S009,0,58.9,63.1
S010,0,51.2,52.9
S011,1,55.1,59.1
S012,1,58.8,63.6
S013,1,58.6,68.4
S014,0,60.3,72.4
S015,0,54.2,49.7
S016,1,51.6,68.9
S017,1,54.4,65.4
S018,0,41.5,53.7
S019,1,43.4,74.4
S020,1,44.4,70.6"""

df_full = pd.read_csv(io.StringIO(RAW))

# ---------------------------------------------------------------------------
# Analysis function
# ---------------------------------------------------------------------------
def _ols(y: np.ndarray, X: np.ndarray):
    """Return (coefs, se, t, p, r2) via closed-form OLS. X must include an intercept column."""
    n, k = X.shape
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    s2 = (resid @ resid) / (n - k)
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), df=n - k)
    ss_res = resid @ resid
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return beta, se, t, p, r2


def analyze(data: pd.DataFrame, choices: dict) -> dict:
    df = data.copy()

    # 1. outlier exclusion on the RAW outcome (before transformation)
    sd_thresh = choices["outlier_rule"]   # None, 2.5, or 3.0
    if sd_thresh is not None:
        mu, sigma = df["wellbeing_post"].mean(), df["wellbeing_post"].std(ddof=1)
        z = (df["wellbeing_post"] - mu).abs() / sigma
        n_before = len(df)
        df = df[z <= sd_thresh].copy()
        n_excluded = n_before - len(df)
    else:
        n_excluded = 0

    # 2. outcome transformation
    if choices["transformation"] == "log":
        y = np.log(df["wellbeing_post"].values)
    else:
        y = df["wellbeing_post"].values.astype(float)

    # 3. build design matrix
    cols = [np.ones(len(df)), df["group"].values.astype(float)]
    col_names = ["intercept", "group"]
    if choices["covariate"] == "wellbeing_pre":
        cols.append(df["wellbeing_pre"].values.astype(float))
        col_names.append("wellbeing_pre")
    X = np.column_stack(cols)

    beta, se, t, p, r2 = _ols(y, X)
    idx = col_names.index("group")
    df_res = len(df) - len(col_names)
    ci_lo = beta[idx] - stats.t.ppf(0.975, df_res) * se[idx]
    ci_hi = beta[idx] + stats.t.ppf(0.975, df_res) * se[idx]

    return {
        "estimate":   float(beta[idx]),
        "se":         float(se[idx]),
        "t_stat":     float(t[idx]),
        "p_value":    float(p[idx]),
        "ci_low":     float(ci_lo),
        "ci_high":    float(ci_hi),
        "n":          len(df),
        "n_excluded": n_excluded,
        "r_squared":  float(r2),
    }


# ---------------------------------------------------------------------------
# Multiverse
# ---------------------------------------------------------------------------
mv = Multiverse(
    decisions={
        "outlier_rule":   {"none": None, "3 SD": 3.0, "2.5 SD": 2.5},
        "covariate":      {"none": None, "wellbeing_pre": "wellbeing_pre"},
        "transformation": {"raw": "raw", "log": "log"},
    }
)

print(mv.summary())
print()

results = mv.run(analyze, df_full, progress=False)

# ---------------------------------------------------------------------------
# Print full results table
# ---------------------------------------------------------------------------
DISPLAY_COLS = [
    "outlier_rule", "covariate", "transformation",
    "n", "n_excluded", "estimate", "se", "t_stat", "p_value",
    "ci_low", "ci_high", "r_squared",
]
fmt = results[DISPLAY_COLS].copy()
for col in ["estimate", "se", "t_stat", "ci_low", "ci_high"]:
    fmt[col] = fmt[col].map(lambda x: f"{x:+.3f}")
fmt["p_value"]   = fmt["p_value"].map(lambda x: f"{x:.4f}")
fmt["r_squared"] = fmt["r_squared"].map(lambda x: f"{x:.3f}")

print("=== All 12 universes ===")
print(fmt.to_string(index=False))
print()

# ---------------------------------------------------------------------------
# Highlight the original specification
# ---------------------------------------------------------------------------
original = {"outlier_rule": "none", "covariate": "none", "transformation": "raw"}
orig_row = results[
    (results["outlier_rule"] == "none") &
    (results["covariate"] == "none") &
    (results["transformation"] == "raw")
].iloc[0]

print("=== Original specification ===")
print(f"  b = {orig_row['estimate']:+.3f}, SE = {orig_row['se']:.3f}, "
      f"t = {orig_row['t_stat']:+.3f}, p = {orig_row['p_value']:.4f}, "
      f"95% CI [{orig_row['ci_low']:+.3f}, {orig_row['ci_high']:+.3f}], n = {int(orig_row['n'])}")
print()

# ---------------------------------------------------------------------------
# Summary statistics across the multiverse
# ---------------------------------------------------------------------------
ok = results[results[".error"].isna()].copy()
print("=== Multiverse summary ===")
print(f"  Specifications run:        {len(ok)} / {len(results)}")
print(f"  Estimate range:            {ok['estimate'].min():+.3f} to {ok['estimate'].max():+.3f}")
print(f"  Median estimate:           {ok['estimate'].median():+.3f}")
print(f"  % specs p < .05:           {(ok['p_value'] < .05).mean():.0%}")
print(f"  % specs p < .05 & b > 0:   {((ok['p_value'] < .05) & (ok['estimate'] > 0)).mean():.0%}")
print()

# ---------------------------------------------------------------------------
# Decision importance
# ---------------------------------------------------------------------------
print("=== Decision importance (eta-squared) ===")
imp = decision_importance(results, decisions=["outlier_rule", "covariate", "transformation"])
print(imp.to_string(index=False))
print()

# ---------------------------------------------------------------------------
# Specification curve plot
# ---------------------------------------------------------------------------
outfile = os.path.join(os.path.dirname(__file__), "..", "mindfulness_curve.png")
fig = specification_curve(
    results,
    highlight=original,
    title="Specification curve — mindfulness intervention (treatment effect on wellbeing_post)",
    outfile=outfile,
)

# ---------------------------------------------------------------------------
# Permutation test (joint inference)
# ---------------------------------------------------------------------------
print("=== Joint permutation inference (n_perm=500) ===")
perm = permutation_test(mv, analyze, df_full, shuffle="group", n_perm=500, seed=42)
