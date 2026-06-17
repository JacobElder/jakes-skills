#!/usr/bin/env python3
"""
plot_joint_synthesis.py — 4-panel synthesis visualization for joint GLMM output.
Usage: python plot_joint_synthesis.py /tmp/joint_out.json [--out synthesis.png]
"""
import json, argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

def load(path):
    with open(path) as f:
        return json.load(f)

def plot(data, out_path):
    theta   = {r["id"]: r for r in data["theta"]}
    diff    = {r["id"]: r for r in data["difficulty"]}
    disc    = {r["id"]: r for r in data["discrimination"]}
    cal     = {r["id"]: r for r in data["cal_slope"]}
    rho     = data.get("rho_theta_tau", None)
    rel     = data["empirical_reliability"]
    diag    = data["diagnostics"]
    variant_order = sorted(theta.keys(), key=lambda v: -theta[v]["est"])

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor("#fafafa")
    gs = GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.38,
                  left=0.08, right=0.97, top=0.91, bottom=0.08)

    BLUE   = "#2d6fa3"
    RED    = "#c0392b"
    ORANGE = "#e67e22"
    GREEN  = "#27ae60"
    GREY   = "#95a5a6"
    LIGHT  = "#ecf0f1"

    # ── Panel A: Item map (b vs a), colour = a-CI width ──────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    items = list(diff.keys())
    b_est  = np.array([diff[i]["est"] for i in items])
    a_est  = np.array([disc[i]["est"] for i in items])
    a_lo   = np.array([disc[i]["lo"]  for i in items])
    a_hi   = np.array([disc[i]["hi"]  for i in items])
    a_width = a_hi - a_lo                         # CI width as uncertainty proxy
    a_capped = np.clip(a_est, 0, 12)              # visual cap for extreme values

    sc = ax1.scatter(b_est, a_capped, c=a_width, cmap="RdYlGn_r",
                     s=70, edgecolors="white", linewidths=0.6,
                     vmin=0, vmax=np.percentile(a_width, 90), zorder=3)
    cb = plt.colorbar(sc, ax=ax1, shrink=0.7, pad=0.02)
    cb.set_label("a CI width (uncertainty)", fontsize=8)
    cb.ax.tick_params(labelsize=7)

    # label a handful of notable items
    notable = {"it02", "it08", "it00", "it20", "it18"}
    for i, item in enumerate(items):
        if item in notable:
            ax1.annotate(item, (b_est[i], a_capped[i]),
                         xytext=(5, 3), textcoords="offset points",
                         fontsize=7.5, color="#333")
    ax1.axhline(1.0, ls="--", lw=0.8, color=GREY, zorder=1)
    ax1.axvline(0,   ls=":",  lw=0.8, color=GREY, zorder=1)
    ax1.set_xlabel("Difficulty  b  (higher = harder)", fontsize=9)
    ax1.set_ylabel("Discrimination  a  [capped at 12]", fontsize=9)
    ax1.set_title("A  —  Item map (IRT / SDT)", fontweight="bold", fontsize=10)
    ax1.set_facecolor(LIGHT)
    ax1.tick_params(labelsize=8)
    ax1.text(0.02, 0.97, "Color = CI width: red = wide (poorly identified)",
             transform=ax1.transAxes, fontsize=7, va="top", color="#555")

    # ── Panel B: Variant theta with CI, colored by cal slope ─────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    cal_vals = np.array([cal[v]["est"] for v in variant_order])
    cmap_cal = plt.cm.RdYlGn
    norm_cal = plt.Normalize(0, 1)
    colors_v  = [cmap_cal(norm_cal(c)) for c in cal_vals]

    y_pos = np.arange(len(variant_order))
    for i, v in enumerate(variant_order):
        t  = theta[v]
        c  = cal[v]
        ax2.barh(i, t["est"], color=colors_v[i], height=0.55, zorder=3)
        ax2.plot([t["lo"], t["hi"]], [i, i], color="#333", lw=1.8, solid_capstyle="round", zorder=4)
        ax2.plot(t["est"], i, "o", color="white", ms=4, zorder=5)
        ax2.text(t["hi"] + 0.08, i, f"cal={c['est']:.2f}", va="center", fontsize=7.5, color="#444")

    ax2.axvline(0, ls="--", lw=1.0, color=GREY)
    ax2.set_yticks(y_pos); ax2.set_yticklabels(variant_order, fontsize=8.5)
    ax2.set_xlabel("Latent ability  θ  (posterior mean ± 95% CI)", fontsize=9)
    ax2.set_title("B  —  Variant ability + calibration", fontweight="bold", fontsize=10)
    ax2.set_facecolor(LIGHT)
    ax2.tick_params(axis="x", labelsize=8)
    sm = plt.cm.ScalarMappable(cmap=cmap_cal, norm=norm_cal)
    sm.set_array([])
    cb2 = plt.colorbar(sm, ax=ax2, shrink=0.7, pad=0.02)
    cb2.set_label("Cal slope (1.0 = ideal)", fontsize=8)
    cb2.ax.tick_params(labelsize=7)

    # ── Panel C: Calibration slopes ───────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    cal_order = sorted(cal.keys(), key=lambda v: -cal[v]["est"])
    y3 = np.arange(len(cal_order))
    for i, v in enumerate(cal_order):
        c = cal[v]
        color = GREEN if c["est"] > 0.7 else (ORANGE if c["est"] > 0.3 else RED)
        ax3.barh(i, c["est"], color=color, height=0.5, zorder=3, alpha=0.85)
        ax3.plot([c["lo"], c["hi"]], [i, i], color="#333", lw=1.8, solid_capstyle="round", zorder=4)
        ax3.plot(c["est"], i, "o", color="white", ms=4, zorder=5)

    ax3.axvline(1.0, ls="--", lw=1.2, color=BLUE, label="ideal (slope=1)")
    ax3.axvline(0,   ls=":",  lw=0.8, color=GREY)
    ax3.set_yticks(y3); ax3.set_yticklabels(cal_order, fontsize=8.5)
    ax3.set_xlabel("Confidence calibration slope", fontsize=9)
    ax3.set_title("C  —  Calibration (confidence ~ correctness)", fontweight="bold", fontsize=10)
    ax3.set_facecolor(LIGHT)
    ax3.tick_params(axis="x", labelsize=8)
    ax3.legend(fontsize=7.5, loc="lower right")
    green_p  = mpatches.Patch(color=GREEN,  label=">0.70 (good)")
    orange_p = mpatches.Patch(color=ORANGE, label="0.30–0.70 (partial)")
    red_p    = mpatches.Patch(color=RED,    label="<0.30 (poor)")
    ax3.legend(handles=[green_p, orange_p, red_p], fontsize=7, loc="lower right")

    # ── Panel D: Reliability + rho + diagnostics summary ─────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(LIGHT)
    ax4.set_xlim(0, 1); ax4.set_ylim(0, 1)
    ax4.axis("off")
    ax4.set_title("D  —  G-theory + diagnostics", fontweight="bold", fontsize=10)

    # reliability gauge bar
    ax4.add_patch(mpatches.FancyBboxPatch((0.05, 0.76), 0.9, 0.10,
                  boxstyle="round,pad=0.01", fc="white", ec="#aaa", lw=0.8))
    rel_color = GREEN if rel >= 0.80 else (ORANGE if rel >= 0.65 else RED)
    ax4.add_patch(mpatches.FancyBboxPatch((0.05, 0.76), 0.9 * rel, 0.10,
                  boxstyle="round,pad=0.01", fc=rel_color, ec="none"))
    ax4.text(0.5, 0.81, f"E-ρ²  =  {rel:.3f}", ha="center", va="center",
             fontsize=11, fontweight="bold", color="white" if rel >= 0.5 else "#333")
    ax4.text(0.05, 0.72, "0", fontsize=7, ha="left", color="#555")
    ax4.text(0.95, 0.72, "1", fontsize=7, ha="right", color="#555")
    ax4.text(0.5,  0.72, "IRT empirical reliability (G-theory E-ρ² analogue)",
             fontsize=7, ha="center", color="#555")

    # rho line
    if rho:
        ax4.text(0.5, 0.60, f"θ–τ correlation (effort coupling)",
                 fontsize=8.5, ha="center", va="center", color="#333")
        r_x = 0.5 + rho["est"] * 0.35
        ax4.plot([0.15, 0.85], [0.54, 0.54], color="#ccc", lw=6, solid_capstyle="round")
        ax4.plot([0.5 + rho["lo"] * 0.35, 0.5 + rho["hi"] * 0.35], [0.54, 0.54],
                 color=BLUE, lw=4, solid_capstyle="round")
        ax4.plot(r_x, 0.54, "o", color="white", ms=7, zorder=5)
        ax4.plot(r_x, 0.54, "o", color=BLUE, ms=5, zorder=6)
        ax4.text(0.15, 0.49, "−1", fontsize=7, ha="center", color="#555")
        ax4.text(0.5,  0.49, "0",  fontsize=7, ha="center", color="#555")
        ax4.text(0.85, 0.49, "+1", fontsize=7, ha="center", color="#555")
        ax4.text(0.5, 0.44, f"ρ̂ = {rho['est']:+.2f}  [{rho['lo']:+.2f}, {rho['hi']:+.2f}]  (wide — prior-influenced at N=8)",
                 fontsize=7.5, ha="center", color="#666")

    # diagnostics
    ndiv  = diag["divergences"]
    rhat  = diag["max_rhat"]
    div_color  = RED    if ndiv  > 0    else GREEN
    rhat_color = RED    if rhat  > 1.01 else GREEN
    ax4.text(0.5, 0.35, "Convergence diagnostics", fontsize=9, ha="center",
             fontweight="bold", color="#333")
    ax4.text(0.5, 0.27,
             f"Divergences: {ndiv}",
             fontsize=10, ha="center", color=div_color, fontweight="bold")
    ax4.text(0.5, 0.19,
             f"Max R-hat: {rhat:.3f}",
             fontsize=10, ha="center", color=rhat_color, fontweight="bold")
    if ndiv > 0:
        ax4.text(0.5, 0.11,
                 "Likely cause: high-a items (it00, it08, it18) + HalfCauchy\n"
                 "on σ_a create funnel geometry. Fix: non-center loga.",
                 fontsize=7.5, ha="center", color=RED, style="italic", wrap=True)

    # figure title
    fig.suptitle("Joint GLMM — IRT · SDT · Calibration · G-theory  (one fit, three channels)",
                 fontsize=12, fontweight="bold", y=0.97)

    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#fafafa")
    print(f"Saved {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--out", default="joint_synthesis.png")
    args = ap.parse_args()
    data = load(args.json)
    plot(data, args.out)

if __name__ == "__main__":
    main()
