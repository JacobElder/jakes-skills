"""Generate eval barplot for README."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

evals = [
    ("GLM: block design",          1.00, 0.75),
    ("Connectivity (3 sub)",        1.00, 0.36),
    ("MVPA decoding",               1.00, 0.60),
    ("GLM: FDR threshold",          1.00, 0.44),
    ("Group (2nd-level) GLM",       1.00, 0.38),
    ("Seed connectivity",           1.00, 0.67),
    ("NiftiMasker tSNR",            1.00, 0.60),
    ("Multi-run GLM",               1.00, 0.70),
    ("Atlas space mismatch",        1.00, 0.67),
    ("Multi-contrast GLM",          1.00, 0.78),
    ("DecoderRegressor",            1.00, 0.50),
    ("Tangent connectivity",        1.00, 0.44),
    ("Cluster-level threshold",     1.00, 0.38),
    ("first_level_from_bids",       1.00, 0.67),
    ("Interactive HTML viz",        1.00, 0.38),
    ("get_clusters_table peaks",    1.00, 0.25),
]

labels = [e[0] for e in evals]
with_skill = [e[1] for e in evals]
without_skill = [e[2] for e in evals]

n = len(evals)
y = np.arange(n)
height = 0.35

fig, ax = plt.subplots(figsize=(10, 7))
bars1 = ax.barh(y + height/2, with_skill,   height, label="With skill",    color="#2ecc71", alpha=0.9)
bars2 = ax.barh(y - height/2, without_skill, height, label="Without skill", color="#e74c3c", alpha=0.7)

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=9)
ax.set_xlim(0, 1.15)
ax.set_xlabel("Pass rate", fontsize=11)
ax.set_title("nilearn-fmri skill: eval pass rate (16 evals)", fontsize=12, fontweight="bold")
ax.axvline(x=0.5, color="gray", linestyle="--", alpha=0.4, linewidth=0.8)
ax.legend(loc="lower right", fontsize=10)

for bar in bars1:
    w = bar.get_width()
    ax.text(w + 0.01, bar.get_y() + bar.get_height()/2, f"{w:.2f}",
            va="center", ha="left", fontsize=7.5, color="#1a8c50")
for bar in bars2:
    w = bar.get_width()
    ax.text(w + 0.01, bar.get_y() + bar.get_height()/2, f"{w:.2f}",
            va="center", ha="left", fontsize=7.5, color="#a93226")

plt.tight_layout()
plt.savefig("eval_results.png", dpi=150, bbox_inches="tight")
print("Saved eval_results.png")

mean_with = np.mean(with_skill)
mean_without = np.mean(without_skill)
print(f"Mean with skill:    {mean_with:.2f}")
print(f"Mean without skill: {mean_without:.2f}")
print(f"Gap:                +{(mean_with - mean_without)*100:.0f} pp")
