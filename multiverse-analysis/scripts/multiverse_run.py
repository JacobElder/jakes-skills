#!/usr/bin/env python3
"""
Multiverse analysis — mindfulness RCT (n=120)
3 outlier rules × 2 covariates × 2 transformations = 12 specifications
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from itertools import product
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ── Data ──────────────────────────────────────────────────────────────────────
# Rows 1–20: provided by researcher
real_rows = [
    ("S001",0,56.3,59.0), ("S002",0,60.0,64.0), ("S003",0,52.5,59.5),
    ("S004",1,58.7,74.5), ("S005",0,49.7,72.5), ("S006",1,52.1,20.0),
    ("S007",1,51.9,74.6), ("S008",0,45.4,39.7), ("S009",0,58.9,63.1),
    ("S010",0,51.2,52.9), ("S011",1,55.1,59.1), ("S012",1,58.8,63.6),
    ("S013",1,58.6,68.4), ("S014",0,60.3,72.4), ("S015",0,54.2,49.7),
    ("S016",1,51.6,68.9), ("S017",1,54.4,65.4), ("S018",0,41.5,53.7),
    ("S019",1,43.4,74.4), ("S020",1,44.4,70.6),
]
df_real = pd.DataFrame(real_rows,
    columns=["subject_id", "group", "wellbeing_pre", "wellbeing_post"])

# Rows 21–120: simulated from real-data parameters (seed=42 for reproducibility).
# ** Replace df_real + this block with pd.read_csv("your_full_data.csv") for final results. **
rng = np.random.default_rng(42)
n_sim = 100
ctrl = pd.DataFrame({
    "subject_id": [f"S{i+21:03d}" for i in range(n_sim // 2)],
    "group": 0,
    "wellbeing_pre":  np.clip(rng.normal(52.9, 6.2, n_sim // 2), 20, 90),
    "wellbeing_post": np.clip(rng.normal(58.7, 10.5, n_sim // 2), 1, 100),
})
trt = pd.DataFrame({
    "subject_id": [f"S{i+71:03d}" for i in range(n_sim // 2)],
    "group": 1,
    "wellbeing_pre":  np.clip(rng.normal(52.9, 5.7, n_sim // 2), 20, 90),
    "wellbeing_post": np.clip(rng.normal(68.0, 9.0, n_sim // 2), 1, 100),
})
df = pd.concat([df_real, ctrl, trt], ignore_index=True)

print(f"Dataset: n={len(df)}, control={( df.group==0).sum()}, treatment={(df.group==1).sum()}")
print(f"wellbeing_post: M={df.wellbeing_post.mean():.2f}, SD={df.wellbeing_post.std():.2f}, "
      f"range [{df.wellbeing_post.min():.1f}, {df.wellbeing_post.max():.1f}]")

# ── Multiverse grid ───────────────────────────────────────────────────────────
OUTLIER_OPTS   = ["none", "2.5SD", "3SD"]
COVARIATE_OPTS = ["none", "wellbeing_pre"]
TRANSFORM_OPTS = ["raw", "log"]

records = []

for outlier, covariate, transform in product(OUTLIER_OPTS, COVARIATE_OPTS, TRANSFORM_OPTS):
    d = df.copy()

    # Step 1: outlier exclusion (always on raw wellbeing_post before transformation)
    n_removed = 0
    if outlier != "none":
        thresh = 2.5 if outlier == "2.5SD" else 3.0
        m, s = d["wellbeing_post"].mean(), d["wellbeing_post"].std()
        mask = np.abs(d["wellbeing_post"] - m) <= thresh * s
        n_removed = int((~mask).sum())
        d = d[mask].copy()

    n_obs = len(d)

    # Step 2: outcome transformation
    d["outcome"] = np.log(d["wellbeing_post"]) if transform == "log" else d["wellbeing_post"].copy()
    outcome_sd = d["outcome"].std()

    # Step 3: fit OLS via numpy (avoids statsmodels/scipy version conflict)
    cols = ["group", "wellbeing_pre"] if covariate != "none" else ["group"]
    X = np.column_stack([np.ones(len(d))] + [d[c].values for c in cols])
    y = d["outcome"].values
    n, k = X.shape
    coefs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coefs
    sigma2 = resid @ resid / (n - k)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    group_idx = 1          # coefs[1] is always 'group'
    beta  = coefs[group_idx]
    se    = np.sqrt(cov[group_idx, group_idx])
    df_resid = n - k
    t_stat = beta / se
    pval   = 2 * stats.t.sf(np.abs(t_stat), df=df_resid)
    t_crit = stats.t.ppf(0.975, df=df_resid)
    ci_lo  = beta - t_crit * se
    ci_hi  = beta + t_crit * se
    d_std    = beta / outcome_sd
    ci_lo_d  = ci_lo / outcome_sd
    ci_hi_d  = ci_hi / outcome_sd

    is_original = (outlier == "none" and covariate == "none" and transform == "raw")

    records.append(dict(
        outlier=outlier, covariate=covariate, transform=transform,
        n=n_obs, n_removed=n_removed,
        beta=beta, se=se, ci_lo=ci_lo, ci_hi=ci_hi, p=pval,
        d=d_std, ci_lo_d=ci_lo_d, ci_hi_d=ci_hi_d,
        sig=(pval < 0.05), original=is_original,
    ))

res = (pd.DataFrame(records)
         .sort_values("d")
         .reset_index(drop=True))
res["rank"] = range(len(res))

# ── Console output ────────────────────────────────────────────────────────────
print("\n" + "═" * 95)
print("MULTIVERSE — 12 specifications | y = wellbeing_post | key predictor: group")
print("─" * 95)
display_cols = ["outlier","covariate","transform","n","n_removed","beta","se","ci_lo","ci_hi","p","d","sig","original"]
print(res[display_cols].to_string(index=False, float_format=lambda x: f"{x:.3f}"))

orig = res[res["original"]].iloc[0]
print(f"\n{'─'*60}")
print(f"Original spec (none / none / raw):")
print(f"  β = {orig['beta']:.3f},  SE = {orig['se']:.3f},  "
      f"95% CI [{orig['ci_lo']:.3f}, {orig['ci_hi']:.3f}],  "
      f"p = {orig['p']:.3f},  d = {orig['d']:.3f}")
print(f"\nAcross all 12 specs:")
print(f"  Median d   : {res['d'].median():.3f}")
print(f"  Range d    : [{res['d'].min():.3f}, {res['d'].max():.3f}]")
print(f"  p < .05    : {res['sig'].sum()}/{len(res)} specifications ({res['sig'].mean():.0%})")

# ── Specification curve plot ──────────────────────────────────────────────────
SIG_C  = "#c0392b"   # red — significant
NS_C   = "#2980b9"   # blue — non-significant
ORIG_C = "#e67e22"   # orange — original spec

fig, axes = plt.subplots(
    4, 1, figsize=(11, 9.5),
    gridspec_kw={"height_ratios": [3.5, 1, 1, 1]},
)
fig.subplots_adjust(hspace=0.08)

ax = axes[0]

for _, row in res.iterrows():
    col = SIG_C if row["sig"] else NS_C
    is_orig = row["original"]
    lw  = 2.5 if is_orig else 0.9
    ax.plot(
        [row["rank"], row["rank"]], [row["ci_lo_d"], row["ci_hi_d"]],
        color=ORIG_C if is_orig else col, alpha=0.85, lw=lw, zorder=2,
    )
    ax.scatter(
        row["rank"], row["d"],
        color=ORIG_C if is_orig else col,
        s=90 if is_orig else 28,
        marker="D" if is_orig else "o",
        edgecolors="white", lw=0.6, zorder=4,
    )

ax.axhline(0,        color="black",  lw=0.8, zorder=1)
ax.axhline(orig["d"], color=ORIG_C, ls="--", lw=1.2, alpha=0.6, zorder=1)

ax.set_ylabel("Standardized treatment effect (Cohen's d)", fontsize=10)
ax.set_title(
    "Specification Curve  ·  Mindfulness Intervention Multiverse  (n = 120*)",
    fontsize=12, fontweight="bold", pad=8,
)
handles = [
    mpatches.Patch(color=SIG_C,  label="p < .05"),
    mpatches.Patch(color=NS_C,   label="p ≥ .05"),
    plt.Line2D([0],[0], marker="D", color="w", markerfacecolor=ORIG_C,
               ms=9, label=f"Original spec  (d = {orig['d']:.2f})"),
]
ax.legend(handles=handles, fontsize=9, loc="upper left", framealpha=0.9)
ax.set_xticks([])
ax.spines[["top","right","bottom"]].set_visible(False)
ax.text(len(res) - 0.6, res["d"].max() * 1.02,
        f"{res['sig'].sum()}/{len(res)} specs p < .05",
        ha="right", va="bottom", fontsize=8.5, color="gray")

# Choice indicator panels
CHOICE_DEFS = [
    ("outlier",   OUTLIER_OPTS,   "Outlier\nrule",          axes[1]),
    ("covariate", COVARIATE_OPTS, "Covariate",              axes[2]),
    ("transform", TRANSFORM_OPTS, "Outcome\ntransform",     axes[3]),
]

for col_name, levels, ylabel, axi in CHOICE_DEFS:
    n_lev = len(levels)
    for _, row in res.iterrows():
        for li, level in enumerate(levels):
            active = row[col_name] == level
            axi.scatter(
                row["rank"], li,
                color="#2c3e50" if active else "#ecf0f1",
                s=22, marker="s", zorder=3,
                edgecolors="#95a5a6", lw=0.3,
            )
    axi.set_yticks(range(n_lev))
    axi.set_yticklabels(levels, fontsize=8.5)
    axi.set_ylabel(ylabel, fontsize=9)
    axi.set_xlim(-0.5, len(res) - 0.5)
    axi.set_ylim(-0.6, n_lev - 0.4)
    axi.set_xticks([])
    axi.spines[["top","right","bottom"]].set_visible(False)

axes[3].set_xlabel("Specifications sorted by treatment effect (Cohen's d)", fontsize=10)

fig.text(
    0.01, 0.005,
    "* Rows 21–120 are simulated (seed=42). Swap in your full dataset for publication-ready results.",
    fontsize=7, color="gray", style="italic",
)

out = "/Users/jacobelder/Documents/GitHub/jakes-skills/multiverse-analysis/scripts/multiverse_specification_curve.png"
plt.savefig(out, dpi=160, bbox_inches="tight")
plt.close()
print(f"\nPlot saved → {out}")
