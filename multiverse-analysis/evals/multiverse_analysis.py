import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import itertools
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

# --- Data (first 20 rows as provided) ---
data = {
    "subject_id": [
        "S001","S002","S003","S004","S005","S006","S007","S008","S009","S010",
        "S011","S012","S013","S014","S015","S016","S017","S018","S019","S020",
    ],
    "group": [0,0,0,1,0,1,1,0,0,0,1,1,1,0,0,1,1,0,1,1],
    "wellbeing_pre": [
        56.3,60.0,52.5,58.7,49.7,52.1,51.9,45.4,58.9,51.2,
        55.1,58.8,58.6,60.3,54.2,51.6,54.4,41.5,43.4,44.4,
    ],
    "wellbeing_post": [
        59.0,64.0,59.5,74.5,72.5,20.0,74.6,39.7,63.1,52.9,
        59.1,63.6,68.4,72.4,49.7,68.9,65.4,53.7,74.4,70.6,
    ],
}
df = pd.DataFrame(data)
N_FULL = len(df)

# --- Multiverse dimensions ---
OUTLIER_RULES   = ["none", "2.5 SD", "3 SD"]
COVARIATES      = ["none", "wellbeing_pre"]
TRANSFORMATIONS = ["raw", "log"]

results = []

for outlier, cov, transform in itertools.product(OUTLIER_RULES, COVARIATES, TRANSFORMATIONS):
    wdf = df.copy()

    # 1. Outlier exclusion (applied to wellbeing_post before transformation)
    n_excluded = 0
    if outlier != "none":
        threshold = 2.5 if "2.5" in outlier else 3.0
        mu = wdf["wellbeing_post"].mean()
        sd = wdf["wellbeing_post"].std(ddof=1)
        mask = (wdf["wellbeing_post"] - mu).abs() <= threshold * sd
        n_excluded = (~mask).sum()
        wdf = wdf[mask].reset_index(drop=True)

    n = len(wdf)

    # 2. Outcome transformation
    if transform == "log":
        wdf["outcome"] = np.log(wdf["wellbeing_post"])
    else:
        wdf["outcome"] = wdf["wellbeing_post"]

    # 3. Model fit
    formula = "outcome ~ group" if cov == "none" else "outcome ~ group + wellbeing_pre"
    fit = smf.ols(formula, data=wdf).fit()

    coef   = fit.params["group"]
    se     = fit.bse["group"]
    tstat  = fit.tvalues["group"]
    pval   = fit.pvalues["group"]
    ci_lo  = fit.conf_int().loc["group", 0]
    ci_hi  = fit.conf_int().loc["group", 1]
    is_orig = (outlier == "none" and cov == "none" and transform == "raw")

    results.append({
        "Outlier rule": outlier,
        "Covariate":    cov,
        "Transform":    transform,
        "n": n, "n_excl": n_excluded,
        "β(group)": coef, "SE": se,
        "t": tstat, "p": pval,
        "95% CI low": ci_lo, "95% CI high": ci_hi,
        "p < .05": pval < 0.05,
        "original": is_orig,
    })

rdf = pd.DataFrame(results)

# ── Pretty-print results table ─────────────────────────────────────────────
print("=" * 90)
print("MULTIVERSE ANALYSIS — mindfulness RCT (n=20 rows analysed)")
print(f"12 specifications: 3 outlier rules × 2 covariates × 2 transformations")
print("=" * 90)

display_cols = ["Outlier rule","Covariate","Transform","n","β(group)","SE","p","95% CI low","95% CI high","p < .05","original"]
pd.set_option("display.float_format", "{:.3f}".format)
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 200)
print(rdf[display_cols].to_string(index=False))

sig_count = rdf["p < .05"].sum()
print(f"\n{sig_count}/12 specifications reach p < .05")

orig_row = rdf[rdf["original"]].iloc[0]
print(f"\nOriginal specification: β = {orig_row['β(group)']:.3f}, SE = {orig_row['SE']:.3f}, "
      f"p = {orig_row['p']:.3f}, 95% CI [{orig_row['95% CI low']:.3f}, {orig_row['95% CI high']:.3f}]")

# ── Effect size summary across specs ──────────────────────────────────────
raw_specs = rdf[rdf["Transform"] == "raw"]
log_specs  = rdf[rdf["Transform"] == "log"]
print(f"\nRaw-scale specs  (n=6): median β = {raw_specs['β(group)'].median():.3f}, "
      f"range [{raw_specs['β(group)'].min():.3f}, {raw_specs['β(group)'].max():.3f}]")
print(f"Log-scale specs  (n=6): median β = {log_specs['β(group)'].median():.3f}, "
      f"range [{log_specs['β(group)'].min():.3f}, {log_specs['β(group)'].max():.3f}]")

# ── Specification curve plot ────────────────────────────────────────────────
# Sort by β(group); for log specs convert to approximate % units for comparability note
plot_rdf = rdf.copy().sort_values("β(group)").reset_index(drop=True)

ORANGE = "#E87722"
BLUE   = "#1F6AA8"
GREY   = "#AAAAAA"

fig, axes = plt.subplots(
    2, 1, figsize=(12, 8),
    gridspec_kw={"height_ratios": [3, 2]},
)

ax_top, ax_bot = axes

# Top panel: effect estimates + CIs
for idx, row in plot_rdf.iterrows():
    color   = ORANGE if row["original"] else (BLUE if row["p < .05"] else GREY)
    zorder  = 5 if row["original"] else 2
    lw      = 2.5 if row["original"] else 1.2

    ax_top.plot([idx, idx], [row["95% CI low"], row["95% CI high"]],
                color=color, lw=lw, zorder=zorder)
    ax_top.scatter(idx, row["β(group)"], color=color, s=60 if row["original"] else 30,
                   zorder=zorder + 1, edgecolors="white", linewidths=0.5)

ax_top.axhline(0, color="black", lw=0.8, ls="--", alpha=0.6)
ax_top.set_ylabel("Treatment effect β (group)", fontsize=11)
ax_top.set_title("Specification curve: treatment effect across 12 analytic choices", fontsize=13, pad=10)
ax_top.set_xlim(-0.7, 11.7)
ax_top.set_xticks([])

# Legend
handles = [
    mpatches.Patch(color=ORANGE, label="Original specification"),
    mpatches.Patch(color=BLUE,   label="p < .05"),
    mpatches.Patch(color=GREY,   label="p ≥ .05"),
]
ax_top.legend(handles=handles, loc="upper left", fontsize=9, framealpha=0.9)

# Bottom panel: specification grid
SPEC_ROWS = {
    "No outlier excl.":  ("Outlier rule", "none"),
    "Excl. >2.5 SD":     ("Outlier rule", "2.5 SD"),
    "Excl. >3 SD":       ("Outlier rule", "3 SD"),
    "No covariate":      ("Covariate",    "none"),
    "Covariate: pre":    ("Covariate",    "wellbeing_pre"),
    "Raw outcome":       ("Transform",    "raw"),
    "Log outcome":       ("Transform",    "log"),
}

row_labels = list(SPEC_ROWS.keys())
n_rows = len(row_labels)
ax_bot.set_xlim(-0.7, 11.7)
ax_bot.set_ylim(-0.5, n_rows - 0.5)
ax_bot.set_yticks(range(n_rows))
ax_bot.set_yticklabels(row_labels[::-1], fontsize=9)
ax_bot.set_xticks([])
ax_bot.set_xlabel("Specifications (sorted by effect size →)", fontsize=10)

# Draw thin horizontal grid lines between spec groups
ax_bot.axhline(3.5, color="black", lw=0.6, alpha=0.4)
ax_bot.axhline(5.5, color="black", lw=0.6, alpha=0.4)

for idx, row in plot_rdf.iterrows():
    is_orig_col = row["original"]
    for r_idx, (label, (col, val)) in enumerate(SPEC_ROWS.items()):
        active = (row[col] == val)
        grid_y = n_rows - 1 - r_idx
        color  = ORANGE if (active and is_orig_col) else (BLUE if (active and row["p < .05"]) else GREY)
        marker_size = 10 if active else 4
        alpha  = 1.0 if active else 0.20
        ax_bot.scatter(idx, grid_y, color=color if active else "#CCCCCC",
                       s=marker_size, alpha=alpha, zorder=2)
        if not active:
            ax_bot.scatter(idx, grid_y, color="#E0E0E0", s=4, alpha=0.3, zorder=1)

plt.tight_layout(h_pad=0.5)
out_path = "/Users/jacobelder/Documents/GitHub/jakes-skills/multiverse-analysis/evals/specification_curve.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"\nSpecification curve saved → {out_path}")
