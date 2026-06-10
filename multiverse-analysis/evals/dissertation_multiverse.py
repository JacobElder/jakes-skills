"""
Dissertation multiverse analysis: social media use → anxiety

Decisions:
  IV:      social_media_hours (daily hours) vs social_media_sessions (weekly sessions)
  DV:      anxiety_gad7 (GAD-7, 0-21) vs anxiety_phq4 (PHQ-4 anxiety subscale, 0-12)
  Outlier: no exclusion vs exclude >3 SD on IV

All four variables are on different scales, so every universe uses standardized
betas (z-score both IV and DV within that universe before regression) to make
estimates comparable across specifications.

Original specification: hours→gad7, no outlier exclusion (b=0.47, p=0.02 unstandardized).
"""

import sys
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, "/Users/jacobelder/Documents/GitHub/jakes-skills/multiverse-analysis/scripts")
from multiverse import Multiverse, specification_curve, decision_importance, permutation_test

# ── Real dataset (n=200) ──────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "social_media_anxiety.csv")
data = pd.read_csv(DATA_PATH)
print(f"Loaded {len(data)} rows from {os.path.basename(DATA_PATH)}")
m0 = smf.ols("anxiety_gad7 ~ social_media_hours", data=data).fit()
b0, p0 = m0.params["social_media_hours"], m0.pvalues["social_media_hours"]
print(f"Original spec — hours→gad7 (unstandardized): b={b0:.3f}, p={p0:.3f}")
print(f"Hours M={data.social_media_hours.mean():.2f} SD={data.social_media_hours.std():.2f}  "
      f"GAD-7 M={data.anxiety_gad7.mean():.2f} SD={data.anxiety_gad7.std():.2f}\n")


# ── Analysis function ─────────────────────────────────────────────────────────
def analyze(data, c):
    df = data.copy()
    iv, dv = c["iv"], c["dv"]

    if c["outlier"] == "3sd":
        z_iv = (df[iv] - df[iv].mean()) / df[iv].std()
        df = df[z_iv.abs() <= 3.0]

    # Standardize both variables so β is comparable across all 8 specs
    iv_z = (df[iv] - df[iv].mean()) / df[iv].std()
    dv_z = (df[dv] - df[dv].mean()) / df[dv].std()
    tmp = pd.DataFrame({"iv_z": iv_z.values, "dv_z": dv_z.values})

    m = smf.ols("dv_z ~ iv_z", data=tmp).fit()
    return {
        "estimate": m.params["iv_z"],
        "p_value":  m.pvalues["iv_z"],
        "ci_low":   m.conf_int().loc["iv_z", 0],
        "ci_high":  m.conf_int().loc["iv_z", 1],
        "n":        int(len(tmp)),
    }


# ── Multiverse setup ──────────────────────────────────────────────────────────
mv = Multiverse(
    decisions={
        "iv":      {"hours": "social_media_hours", "sessions": "social_media_sessions"},
        "dv":      {"gad7": "anxiety_gad7",         "phq4": "anxiety_phq4"},
        "outlier": {"none": None,                    "3sd": "3sd"},
    },
    constraints=[lambda c: True],   # all 8 combinations are statistically valid
)
print(mv.summary())

# ── Run all 8 universes ───────────────────────────────────────────────────────
res = mv.run(analyze, data, progress=False)

print("\n=== All 8 specifications (sorted by standardized β) ===")
print(res[["iv", "dv", "outlier", "estimate", "p_value", "n"]]
      .sort_values("estimate")
      .to_string(index=False))

# ── Decision importance ───────────────────────────────────────────────────────
print("\n=== Decision importance (which fork moves the estimate most) ===")
print(decision_importance(res).to_string(index=False))

# ── Specification curve ───────────────────────────────────────────────────────
specification_curve(
    res,
    title="Specification curve: social media use → anxiety",
    outfile="evals/dissertation_curve.png",
    highlight={"iv": "hours", "dv": "gad7", "outlier": "none"},
)

# ── Distribution summary ──────────────────────────────────────────────────────
ok = res[res[".error"].isna()]
n_sig_pos = int(((ok["p_value"] < 0.05) & (ok["estimate"] > 0)).sum())
n_sig_neg = int(((ok["p_value"] < 0.05) & (ok["estimate"] < 0)).sum())
has_sign_flip = ok["estimate"].min() < 0 < ok["estimate"].max()

print(f"\n=== Distribution summary ===")
print(f"  Specifications:         {len(ok)}")
print(f"  Median β:               {ok['estimate'].median():.3f}")
print(f"  Range:                  [{ok['estimate'].min():.3f}, {ok['estimate'].max():.3f}]")
print(f"  Significant positive:   {n_sig_pos}/{len(ok)} ({100*n_sig_pos/len(ok):.0f}%)")
print(f"  Significant negative:   {n_sig_neg}/{len(ok)}")
print(f"  Sign flips:             {'YES' if has_sign_flip else 'no'}")

# ── Original specification ────────────────────────────────────────────────────
orig = ok[(ok["iv"] == "hours") & (ok["dv"] == "gad7") & (ok["outlier"] == "none")]
orig_beta = orig["estimate"].values[0]
orig_p    = orig["p_value"].values[0]
n_below   = int((ok["estimate"] <= orig_beta).sum())

print(f"\n=== Original specification ===")
print(f"  β = {orig_beta:.3f}   p = {orig_p:.3f}")
print(f"  Rank {n_below}/{len(ok)} from bottom  "
      f"({'above' if orig_beta > ok['estimate'].median() else 'below or at'} multiverse median)")

# ── Joint permutation inference ───────────────────────────────────────────────
# Shuffle both IV columns with the same row permutation → breaks all SM→anxiety
# links simultaneously while preserving the hours/sessions correlation structure.
print("\n=== Joint permutation test (n=500, direction=positive) ===")
permutation_test(
    mv, analyze, data,
    shuffle=["social_media_hours", "social_media_sessions"],
    n_perm=500,
    direction="positive",
)
