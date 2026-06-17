# 10 — Synthesis & Visualization (the unified read)

Parameters aren't insight. `scripts/synthesize.py` takes a `joint_glmm.py --out` JSON and produces
the thing a stakeholder actually wants: **one plain-language read of IRT + SDT + G-theory +
calibration together, plus a single multi-panel figure** — and it adds two insights the raw
parameters don't give you.

```
python joint_glmm.py results.csv --channels acc,latency,confidence --slip --out joint.json
python synthesize.py joint.json --fig synthesis.png --md synthesis.md
```

## What the narrative does

One bullet per framework, each saying *what it means and what to do*, in order:
- **Fit quality first.** If R-hat > 1.01 or there were divergences, the synthesis leads with a
  caution and labels everything provisional. Honesty gate before any interpretation.
- **IRT + targeting** — difficulty span vs ability span, whether the suite is well-targeted / too
  easy / too hard, how many items discriminate vs are flat (cut candidates).
- **SDT (probit reading)** — discrimination as detection sensitivity; and it *flags an implausibly
  large `a` as a small-N near-separation artifact* rather than touting a fake super-item.
- **G-theory** — reliability for ranking variants with a plain verdict (trustworthy / provisional /
  not yet), plus mean ability uncertainty.
- **Effort channel** — the ability–effort correlation, with the "weakly identified but still helps"
  caveat when its interval is wide.
- **Calibration** — how many variants track their own confidence.
- **Separation** — of all variant pairs, how many you can actually tell apart.
- **One ranked recommendation** — the single highest-value next action (add harder items / add cases
  / expand takers / trim flat items / lock the suite), chosen from the diagnostics.

## The figure (eight panels, one image)

1. **Item–person (Wright) map** — variant abilities with intervals against item-difficulty lines on
   the shared latent scale. *The fastest way to see if your cases are aimed where your variants
   actually are.* Items clustered away from the variant band = wasted cases.
2. **Variant ranking** — forest plot of θ with credible intervals; overlapping bars = not separable.
3. **Item information functions (IIF)** — each item's information curve (where on the ability scale
   it discriminates), with the **test-information** envelope (their sum) on a twin axis and your
   variants marked. An item's IIF peaks at its difficulty and rises with its discrimination, so this
   panel answers "which specific case carries information at my variants' ability, and where are the
   gaps?" — the item-selection view, not just the aggregate saturation curve.
4. **Pairwise separation heatmap** — P(θ_row > θ_col) for every pair, ✓ where it's decisive. This is
   the honest answer to "which of these can I actually rank?" (computed from the posterior summary
   via a normal approximation; for exact values use full draws).
5. **Calibration by variant** — confidence→correctness slopes against the 1.0 reference.
6. **G-theory** — a D-study curve (Eρ²/Φ vs number of cases, with the 0.80 line) above a
   variance-composition bar (version / item / residual / seed shares). Tells you both how reliable
   the suite is now and how many cases buy a dependable read.
7. **SDT triggering** — per-skill d′ vs criterion; the shaded low-d′ band means "fix the description
   content," horizontal position means over- vs under-firing. (Needs `--sdt`.)
8. **Headline numbers** — reliability, mean uncertainty, spans, effort correlation, flagged items,
   G-theory coefficients, convergence — the scalar summary, bottom-right.

## Two insights worth calling out

- **Targeting (item–person map).** Most eval suites are accidentally mis-targeted — built around
  cases that felt hard to a human, not cases that sit at the ability band of the variants you're
  comparing. The map makes the mismatch obvious and tells you which difficulty region to add.
- **Pairwise separation.** A ranked list with point estimates invites over-reading. The separation
  matrix replaces "v4 > v5" with "P(v4 > v5) = 0.62 — you can't call it," which is usually the more
  honest and more decision-relevant statement at small N.

## Scope

The synthesis reads the joint fit's four-framework output. Triggering-SDT (a separate response
process) and full crossed-facet G-theory (Eρ²/Φ from judge/seed) live in `sdt_trigger.py` and
`gtheory_eval.py`; fold their numbers into the narrative manually when relevant. Like the engines
it summarizes, this is a clear *read* of the model, not a substitute for validating the model —
the convergence line and the artifact flags are there so the synthesis can't quietly launder a bad
fit into a confident story.
