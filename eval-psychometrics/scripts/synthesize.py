#!/usr/bin/env python3
"""
synthesize.py — Turn a joint_glmm fit into ONE clear read: plain-language interpretation of
IRT + SDT + G-theory + calibration together, plus a single multi-panel figure.

It deliberately does two things models usually skip:
  * says what the numbers MEAN and what to DO, in plain terms, per framework;
  * adds two insights beyond the raw parameters —
      - an item–person (Wright) map: are your eval cases actually targeted at your variants' ability?
      - a pairwise separation matrix: which variants can you actually tell apart, and which overlap?

INPUT  : the JSON written by `joint_glmm.py --out joint.json`
USAGE  : python synthesize.py joint.json [--fig synthesis.png] [--md synthesis.md]
Dependencies: numpy, matplotlib. (Reads summary stats only; no re-fitting.)
"""
import argparse, json, sys
import numpy as np
from scipy.stats import norm

PASS = lambda x: x  # noqa


def arr(rows, k="est"):
    return np.array([r[k] for r in rows], dtype=float)


def load(path):
    d = json.load(open(path))
    if "theta" not in d or "difficulty" not in d:
        sys.exit("ERROR: not a joint_glmm output JSON (need theta + difficulty).")
    return d


# ---------------- plain-language synthesis ----------------
def narrate(d, gt=None, sdt=None):
    th = d["theta"]; tm = arr(th); tl = arr(th, "lo"); thi = arr(th, "hi")
    tsd = np.array(d.get("theta_sd", [(h - l) / 3.92 for l, h in zip(tl, thi)]))
    names = [r["id"] for r in th]
    b = arr(d["difficulty"]); a = arr(d["discrimination"])
    rel = d.get("empirical_reliability", float("nan"))
    diag = d.get("diagnostics", {})
    lines = []

    # Convergence caution first (honesty gate)
    if diag and (diag.get("max_rhat", 0) > 1.01 or diag.get("divergences", 0) > 0):
        lines.append(f"⚠ FIT QUALITY: max R-hat {diag.get('max_rhat')}, "
                     f"{diag.get('divergences')} divergences — the fit hasn't fully converged. "
                     f"Read everything below as provisional; re-run with more tuning/draws before deciding.")

    # IRT + targeting
    order = np.argsort(-tm)
    flat = int(np.sum(a < 0.5)); sharp = int(np.sum(a > 1.0))
    bspan = (b.min(), b.max()); tspan = (tm.min(), tm.max())
    gap = "well-targeted" if (b.min() <= tspan[0] + 0.5 and b.max() >= tspan[1] - 0.5) else \
          ("too easy — no items at the top of your ability range, so your best variants aren't tested"
           if b.max() < tspan[1] - 0.5 else
           "too hard — items sit above your variants, wasting cases at the bottom")
    lines.append(f"IRT: {len(b)} items span difficulty [{bspan[0]:+.1f}, {bspan[1]:+.1f}]; your "
                 f"{len(tm)} variants span ability [{tspan[0]:+.1f}, {tspan[1]:+.1f}]. The suite is "
                 f"{gap}. {sharp} item(s) discriminate well (a>1); {flat} are nearly flat (a<0.5) and "
                 f"are candidates to cut.")

    # SDT — prefer real triggering d'/criterion if provided; else the probit reading
    if sdt and sdt.get("skills"):
        sk = sdt["skills"]
        shy = [s["skill_id"] for s in sk if s["criterion"] > 0.3]
        eager = [s["skill_id"] for s in sk if s["criterion"] < -0.3]
        dull = [s["skill_id"] for s in sk if s["dprime"] < 1.0]
        msg = f"SDT (triggering): {len(sk)} skill(s) analyzed. "
        if dull:
            msg += f"{', '.join(dull)} can't tell in- from out-of-scope (low d') → rewrite the description CONTENT. "
        if shy:
            msg += f"{', '.join(shy)} under-fire (shy) → make the trigger pushier. "
        if eager:
            msg += f"{', '.join(eager)} over-fire (eager) → tighten/qualify the trigger. "
        if not (dull or shy or eager):
            msg += "all are sensitive and roughly neutral on bias."
        lines.append(msg)
    else:
        imax = int(np.argmax(a))
        if a[imax] > 5:
            lines.append(f"SDT (probit reading): discrimination is detection sensitivity. NB the largest "
                         f"a={a[imax]:.1f} ({d['discrimination'][imax]['id']}) is implausibly high — at this "
                         f"N that's a near-separation artifact, not a real super-item; trust the ranking, "
                         f"not the extreme discriminations. (For triggering d'/criterion, pass --sdt.)")
        else:
            lines.append(f"SDT (probit reading): discrimination is detection sensitivity; sharpest item "
                         f"{d['discrimination'][imax]['id']} a={a[imax]:.1f}. For triggering bias "
                         f"(d'/criterion per skill), run sdt_trigger.py and pass --sdt.")

    # G-theory — prefer the real variance decomposition if provided; else the reliability bridge
    if gt and gt.get("variance_components"):
        vc = gt["variance_components"]; tot = sum(vc.values())
        pct = {k: 100 * v / tot for k, v in vc.items()}
        dom = gt.get("dominant_error", "")
        tgt = gt.get("erho2_target_items")
        seed_note = " Seed/run noise exceeds residual — add SEEDS before cases." if gt.get("seed_exceeds_residual") else ""
        dstudy = (f" To reach Eρ²≥0.80, grow to ~{tgt} cases." if tgt else
                  " Eρ²≥0.80 isn't reachable by adding cases alone — check seed noise or that variants truly differ.")
        lines.append(f"G-theory: Eρ²={gt['erho2']:.2f} (rank), Φ={gt['phi']:.2f} (threshold) — {gt.get('verdict','')}. "
                     f"Variance: version {pct.get('version',0):.0f}% (wanted), item {pct.get('item',0):.0f}%, "
                     f"residual {pct.get('version_x_item',0):.0f}%"
                     + (f", seed {pct.get('seed_run',0):.0f}%" if 'seed_run' in pct else "")
                     + f". Largest error: {dom}.{dstudy}{seed_note}")
    else:
        verdict = ("trustworthy for ranking" if rel >= 0.8 else
                   "provisional — usable for direction, not fine ranking" if rel >= 0.6 else
                   "not yet reliable for ranking variants")
        lines.append(f"G-theory (reliability bridge): ≈ {rel:.2f} ({verdict}); mean ability uncertainty "
                     f"±{d.get('mean_theta_sd', np.mean(tsd)):.2f}. For the full variance decomposition "
                     f"(version/item/seed) and a D-study, run gtheory_eval.py and pass --gtheory.")

    # Effort coupling
    if "rho_theta_tau" in d:
        r = d["rho_theta_tau"]; wide = (r["hi"] - r["lo"]) > 1.0
        lines.append(f"Effort channel: ability–effort correlation {r['est']:+.2f} "
                     f"[{r['lo']:+.2f}, {r['hi']:+.2f}]. "
                     + ("The correlation itself is weakly identified, but the channel still tightened "
                        "ability — keep it, don't over-read the number."
                        if wide else "This channel is meaningfully informing ability estimates."))

    # Calibration
    if "cal_slope" in d:
        cs = arr(d["cal_slope"]); good = int(np.sum(np.abs(cs - 1) < 0.4))
        lines.append(f"Calibration: {good}/{len(cs)} variants track their own confidence well "
                     f"(slope≈1). Slopes far below 1 = overconfident; far above = underconfident.")

    # Pairwise separation
    P = pairwise(tm, tsd)
    npairs = len(tm) * (len(tm) - 1) // 2
    clear = int((P[np.triu_indices(len(tm), 1)] > 0.95).sum() +
                (P[np.triu_indices(len(tm), 1)] < 0.05).sum())
    lines.append(f"Separation: of {npairs} variant pairs, {clear} are clearly distinguishable "
                 f"(P>0.95); the rest overlap — you can't confidently rank those yet.")

    # Single top recommendation
    rec = top_recommendation(rel, a, b, tm, gap, P)
    lines.append(f"➤ DO NEXT: {rec}")
    return lines, order


def pairwise(tm, tsd):
    n = len(tm); P = np.eye(n) * 0.5
    for i in range(n):
        for j in range(n):
            if i != j:
                P[i, j] = norm.cdf((tm[i] - tm[j]) / np.sqrt(tsd[i] ** 2 + tsd[j] ** 2 + 1e-9))
    return P


def top_recommendation(rel, a, b, tm, gap, P):
    iu = np.triu_indices(len(tm), 1)
    overlap = np.mean((P[iu] < 0.95) & (P[iu] > 0.05))
    if "too easy" in gap:
        return f"add harder eval cases (difficulty ≈ {tm.max():+.1f}); your top variants are off the top of the suite."
    if rel < 0.6:
        return "add eval cases — reliability is too low to rank variants; widen the suite before reading rankings."
    if overlap > 0.5:
        return "expand the taker dimension (model tiers/ablations/seeds) or anchor on a bank — most variant pairs still overlap."
    if np.mean(a < 0.5) > 0.3:
        return "trim the flat (a<0.5) items and reinvest the budget in cases near your variants' ability."
    return "the suite is in good shape; lock it and track these estimates across iterations."


# ---------------- figure ----------------
def make_figure(d, order, path, gt=None, sdt=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    INK, GRID, ACC, ACC2, WARM = "#1b1b1f", "#e6e6ea", "#3a6ea5", "#6aa84f", "#c1666b"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#999", "axes.linewidth": .8,
                         "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK,
                         "ytick.color": INK, "figure.facecolor": "white"})
    th = d["theta"]; tm = arr(th); tl = arr(th, "lo"); thi = arr(th, "hi")
    tsd = np.array(d.get("theta_sd", [(h - l) / 3.92 for l, h in zip(tl, thi)]))
    names = [r["id"] for r in th]
    names_i = [r["id"] for r in d["difficulty"]]
    b = arr(d["difficulty"]); a = arr(d["discrimination"])

    fig = plt.figure(figsize=(13, 15))
    fig.suptitle("Eval suite — unified measurement read (IRT · SDT · G-theory · Calibration)",
                 fontsize=13, fontweight="bold", y=0.995)
    from matplotlib.gridspec import GridSpecFromSubplotSpec
    gs = GridSpec(4, 2, figure=fig, hspace=0.55, wspace=0.24,
                  left=0.08, right=0.95, top=0.95, bottom=0.045)

    # Panel 1: item-person (Wright) map
    ax = fig.add_subplot(gs[0, 0])
    o = np.argsort(tm)
    ax.errorbar(tm[o], np.arange(len(tm)), xerr=[tm[o] - tl[o], thi[o] - tm[o]], fmt="o",
                color=ACC, ecolor=ACC, capsize=3, ms=6, zorder=3)
    ax.set_yticks(np.arange(len(tm))); ax.set_yticklabels([names[i] for i in o], fontsize=8)
    for bi, ai in zip(b, a):
        ax.axvline(bi, color=WARM, alpha=min(0.15 + ai / 6, 0.7), lw=1.2, zorder=1)
    xlo = min(tm.min(), float(np.percentile(b, 5))) - 1; xhi = max(tm.max(), float(np.percentile(b, 95))) + 1
    ax.set_xlim(xlo, xhi)
    ax.set_xlabel("latent scale  (θ ability · red lines = item difficulty, darker = sharper)")
    ax.set_title("Item–person map: are cases targeted at your variants?", fontsize=10, loc="left")
    ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)

    # Panel 2: variant forest
    ax = fig.add_subplot(gs[0, 1])
    od = np.argsort(tm)
    ax.errorbar(tm[od], np.arange(len(tm)), xerr=[tm[od] - tl[od], thi[od] - tm[od]], fmt="s",
                color=INK, ecolor="#888", capsize=3, ms=5)
    ax.set_yticks(np.arange(len(tm))); ax.set_yticklabels([names[i] for i in od], fontsize=8)
    ax.axvline(0, color="#bbb", ls="--", lw=.8)
    ax.set_xlabel("θ (95% credible interval)")
    ax.set_title("Variant ranking with uncertainty", fontsize=10, loc="left")
    ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)

    # Panel 3: item information functions (IIF) + test information envelope
    ax = fig.add_subplot(gs[1, 0])
    glo = min(tm.min(), float(np.percentile(b, 5))) - 1; ghi = max(tm.max(), float(np.percentile(b, 95))) + 1
    grid = np.linspace(glo, ghi, 240)
    eta = a[None, :] * (grid[:, None] - b[None, :])
    phi = norm.pdf(eta); Phi = np.clip(norm.cdf(eta), 1e-6, 1 - 1e-6)
    iinfo = a[None, :] ** 2 * phi ** 2 / (Phi * (1 - Phi))   # (grid, I) per-item information
    tinfo = iinfo.sum(1)
    for k in range(iinfo.shape[1]):                          # individual IIFs
        ax.plot(grid, iinfo[:, k], color=ACC, alpha=0.22, lw=0.8)
    top = np.argsort(-iinfo.max(0))[:3]                      # label the most informative items
    for k in top:
        xp = grid[iinfo[:, k].argmax()]; yp = iinfo[:, k].max()
        ax.annotate(names_i[k], (xp, yp), fontsize=7, color=ACC,
                    xytext=(0, 2), textcoords="offset points", ha="center")
    axr = ax.twinx()                                        # test information on its own scale
    axr.plot(grid, tinfo, color=INK, lw=2.0, label="test information")
    axr.fill_between(grid, tinfo, color=INK, alpha=0.05)
    axr.set_ylim(0, tinfo.max() * 1.15); axr.tick_params(labelsize=7)
    axr.set_ylabel("test information", fontsize=8)
    for t in tm:
        ax.axvline(t, color=WARM, alpha=0.30, lw=0.8)
    ax.set_xlim(glo, ghi); ax.set_ylim(0, iinfo.max() * 1.15)
    ax.set_xlabel("θ  (orange lines = your variants)"); ax.set_ylabel("item information", fontsize=8)
    ax.set_title("Item information functions — where each case informs", fontsize=10, loc="left")
    ax.grid(color=GRID); ax.set_axisbelow(True)

    # Panel 4: pairwise separation heatmap
    ax = fig.add_subplot(gs[1, 1])
    od2 = np.argsort(-tm); P = pairwise(tm, tsd)[od2][:, od2]
    im = ax.imshow(P, cmap="RdBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(tm))); ax.set_yticks(range(len(tm)))
    ax.set_xticklabels([names[i] for i in od2], rotation=90, fontsize=7)
    ax.set_yticklabels([names[i] for i in od2], fontsize=7)
    ax.set_title("Pairwise separation  P(row > col)", fontsize=10, loc="left")
    for i in range(len(tm)):
        for j in range(len(tm)):
            if i != j and (P[i, j] > 0.95 or P[i, j] < 0.05):
                ax.text(j, i, "✓", ha="center", va="center", color="#222", fontsize=7)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # Panel 5: calibration
    ax = fig.add_subplot(gs[2, 0])
    if "cal_slope" in d:
        cs = d["cal_slope"]; cm = arr(cs); cl = arr(cs, "lo"); ch = arr(cs, "hi")
        oc = np.argsort(cm)
        ax.errorbar(cm[oc], np.arange(len(cm)), xerr=[cm[oc] - cl[oc], ch[oc] - cm[oc]], fmt="o",
                    color=ACC2, ecolor=ACC2, capsize=3, ms=5)
        ax.axvline(1.0, color=WARM, ls="--", lw=1, label="well-calibrated (slope=1)")
        ax.set_yticks(np.arange(len(cm))); ax.set_yticklabels([cs[i]["id"] for i in oc], fontsize=8)
        ax.set_xlabel("confidence→correctness slope"); ax.legend(fontsize=7, loc="lower right")
        ax.set_title("Calibration by variant", fontsize=10, loc="left")
        ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
    else:
        ax.axis("off"); ax.text(0.5, 0.5, "no confidence channel\n(add a confidence column to enable)",
                                ha="center", va="center", color="#999")

    # Panel 6: G-theory — D-study (top) + variance composition bar (bottom), cleanly separated
    if gt and gt.get("variance_components"):
        subg = GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[2, 1], height_ratios=[2.3, 1.0], hspace=0.65)
        axA = fig.add_subplot(subg[0]); axB = fig.add_subplot(subg[1])
        ds = gt.get("dstudy", [])
        if ds:
            xs = [p["items"] for p in ds]; ye = [p["erho2"] for p in ds]; yp = [p["phi"] for p in ds]
            axA.plot(xs, ye, "-o", color=ACC, ms=3, label="Eρ² (rank)")
            axA.plot(xs, yp, "-o", color=ACC2, ms=3, label="Φ (threshold)")
            axA.axhline(0.8, color=WARM, ls="--", lw=.8)
            axA.set_ylim(min(0.4, min(ye) - .05), 1.0); axA.set_xlabel("# eval cases", fontsize=8)
            axA.tick_params(labelsize=7); axA.legend(fontsize=7, loc="lower right")
            axA.grid(color=GRID); axA.set_axisbelow(True)
        axA.set_title(f"G-theory  ·  Eρ²={gt['erho2']:.2f}  Φ={gt['phi']:.2f}  (D-study)", fontsize=10, loc="left")
        vc = gt["variance_components"]; labels = list(vc.keys()); vals = np.array([vc[k] for k in labels])
        share = 100 * vals / vals.sum()
        cols = {"version": ACC2, "item": ACC, "version_x_item": WARM, "seed_run": "#e8a33d"}
        short = {"version": "version", "item": "item", "version_x_item": "resid", "seed_run": "seed"}
        left = 0; handles = []
        for k, sshare in zip(labels, share):
            bar = axB.barh(0, sshare, left=left, color=cols.get(k, "#999"), edgecolor="white")
            if sshare > 8:
                axB.text(left + sshare / 2, 0, f"{sshare:.0f}%", ha="center", va="center",
                         fontsize=8, color="white", fontweight="bold")
            handles.append((bar, f"{short.get(k, k)} {sshare:.0f}%")); left += sshare
        axB.set_xlim(0, 100); axB.set_ylim(-0.5, 0.5); axB.set_yticks([]); axB.tick_params(labelsize=7)
        axB.set_xlabel("variance share (%)", fontsize=8)
        axB.legend([h[0] for h in handles], [h[1] for h in handles], ncol=len(handles),
                   fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.55), frameon=False)
    else:
        ax = fig.add_subplot(gs[2, 1]); ax.axis("off")
        ax.text(0.5, 0.5, "no G-theory input\nrun gtheory_eval.py --out gt.json\nand pass --gtheory gt.json",
                ha="center", va="center", color="#999")

    # Panel 7: SDT triggering — d' vs criterion quadrant (padded, shaded)
    ax = fig.add_subplot(gs[3, 0])
    if sdt and sdt.get("skills"):
        sk = sdt["skills"]
        dp = np.array([s["dprime"] for s in sk]); cr = np.array([s["criterion"] for s in sk])
        xpad = max(0.4, (cr.max() - cr.min()) * 0.30); ypad = max(0.4, (dp.max() - dp.min()) * 0.22)
        xlo_, xhi_ = cr.min() - xpad, cr.max() + xpad; ylo_, yhi_ = min(0, dp.min() - ypad), dp.max() + ypad
        ax.axhspan(ylo_, 1.0, color=WARM, alpha=0.05)          # low-sensitivity band
        ax.axvline(0, color="#bbb", ls="--", lw=.8); ax.axhline(1.0, color="#bbb", ls="--", lw=.8)
        ax.scatter(cr, dp, color=ACC, s=45, zorder=3)
        for s in sk:
            dy = 8 if s["dprime"] < dp.max() else -12
            ax.annotate(s["skill_id"][:14], (s["criterion"], s["dprime"]), fontsize=7,
                        xytext=(0, dy), textcoords="offset points", ha="center")
        ax.set_xlim(xlo_, xhi_); ax.set_ylim(ylo_, yhi_)
        ax.set_xlabel("criterion c   (< 0 over-fires  ·  > 0 under-fires)")
        ax.set_ylabel("d′  (sensitivity)")
        ax.text(0.5, 0.04, "below dashed line: low d′ → fix description CONTENT",
                transform=ax.transAxes, fontsize=7, color=WARM, ha="center")
        ax.set_title("SDT triggering: sensitivity vs bias", fontsize=10, loc="left")
        ax.grid(color=GRID); ax.set_axisbelow(True)
    else:
        ax.axis("off")
        ax.set_facecolor("#f9f9f9")
        ax.text(0.5, 0.58, "SDT triggering panel", ha="center", va="center",
                color="#aaa", fontsize=10, style="italic")
        ax.text(0.5, 0.42, "pass --sdt sdt_trigger.json to populate",
                ha="center", va="center", color="#bbb", fontsize=8)
        ax.set_title("SDT triggering: sensitivity vs bias", fontsize=10, loc="left")

    # Panel 8: scalar summary card  (bottom-right — the natural resting place for text)
    ax = fig.add_subplot(gs[3, 1]); ax.axis("off")
    rel = d.get("empirical_reliability", float("nan")); diag = d.get("diagnostics", {})
    rho = d.get("rho_theta_tau")
    txt = [f"Reliability (rank variants):  {rel:.2f}",
           f"Mean θ uncertainty:  ±{d.get('mean_theta_sd', np.mean(tsd)):.2f}",
           f"Sharpest item a:  {a.max():.1f}    Flat items (a<0.5):  {int((a < 0.5).sum())}",
           f"Item difficulty span:  [{b.min():+.1f}, {b.max():+.1f}]",
           f"Variant ability span:  [{tm.min():+.1f}, {tm.max():+.1f}]"]
    if rho:
        txt.append(f"Ability–effort corr:  {rho['est']:+.2f} [{rho['lo']:+.2f}, {rho['hi']:+.2f}]")
    if "slip_upper" in d:
        sl = arr(d["slip_upper"]); txt.append(f"Items flagged (slip<0.85):  {int((sl < 0.85).sum())}")
    if gt:
        txt.append(f"G-theory Eρ²/Φ:  {gt.get('erho2','?')} / {gt.get('phi','?')}")
    if diag:
        txt.append(f"Convergence:  R-hat {diag.get('max_rhat')}, div {diag.get('divergences')}")
    ax.text(0.0, 1.0, "Headline numbers", fontsize=11, fontweight="bold", va="top")
    ax.text(0.0, 0.86, "\n".join(txt), fontsize=9.5, va="top", family="monospace", linespacing=1.8)

    fig.savefig(path, dpi=130, bbox_inches="tight")
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json", help="joint_glmm.py --out JSON")
    ap.add_argument("--gtheory", default=None, help="gtheory_eval.py --out JSON (adds variance panel)")
    ap.add_argument("--sdt", default=None, help="sdt_trigger.py --out JSON (adds triggering panel)")
    ap.add_argument("--fig", default="synthesis.png")
    ap.add_argument("--md", default=None)
    args = ap.parse_args()
    d = load(args.json)
    gt = json.load(open(args.gtheory)) if args.gtheory else None
    sdt = json.load(open(args.sdt)) if args.sdt else None
    lines, order = narrate(d, gt, sdt)
    print("\n# Synthesis — what the eval data says\n")
    for ln in lines:
        print("• " + ln + "\n")
    fig = make_figure(d, order, args.fig, gt, sdt)
    print(f"Figure: {fig}")
    if args.md:
        with open(args.md, "w") as f:
            f.write("# Eval synthesis\n\n" + "\n\n".join("- " + ln for ln in lines)
                    + f"\n\n![synthesis]({args.fig})\n")
        print(f"Markdown: {args.md}")


if __name__ == "__main__":
    main()
