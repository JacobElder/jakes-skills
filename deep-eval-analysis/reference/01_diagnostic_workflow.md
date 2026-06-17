# 01 — Diagnostic Workflow

The end-to-end audit: from "here are my eval results" to a documented trim/ship/trust/diagnose
decision. This file ties the others together and owns the **decision rules**.

## Input schema (what every script expects)

A single **long-format** table of results, one row per scored attempt:

```
taker_id,item_id,score[,judge_id,seed,in_scope,fired]
```

- `taker_id` — version / model tier / ablation (the column of the response matrix).
- `item_id` — eval case.
- `score` — pass=1 / fail=0, or partial credit in [0,1].
- `judge_id`, `seed` — optional; needed for G-theory facets and judge calibration.
- `in_scope`, `fired` — optional; needed for SDT triggering (`in_scope`=should-fire,
  `fired`=did-fire). Triggering rows can live in a separate file.

Get results into this shape first; everything downstream keys off it.

## Step 0 — Name the decision

Before any statistics, write one sentence: *what will change based on this analysis?* The decision
sets the method and the coefficient:

| Decision | Lead method | Key output |
|---|---|---|
| "Which cases do I cut?" | CTT item analysis (+IRT if bank) | trim/fix lists |
| "Is version B actually better than A?" | G-theory (Eρ²) + per-item deltas | dependability-adjusted comparison |
| "Did we clear the 80% bar?" | G-theory (Φ) | absolute dependability |
| "Why won't my eval move?" | CTT + G-theory | saturation / variance-source diagnosis |
| "Can I trust these scores at all?" | Judge calibration | κ / AUC gate |
| "Does the skill fire correctly?" | SDT triggering | d′ / criterion per skill |
| "How many cases/seeds do I need?" | G-theory D-study | sizing table |

## Step 1 — Regime check (do not skip)

Count your **takers** (distinct `taker_id`). Route per the SKILL.md regime table:

```
takers < ~30 ............ small-N iteration → G-theory + CTT + SDT; read 07 first.
                          IRT only via fixed-item anchoring or hierarchical shrinkage.
takers ≥ ~30 ............ model-bank → IRT is available; still run CTT/G-theory.
labels from LLM/human ... run the judge gate (step 2) regardless of regime.
triggering question ..... SDT branch (needs in_scope/fired data with real noise trials).
```

If you're under ~30 takers, your *first* move is usually to inflate the taker dimension
(model tiers + ablations + seeds + history) per `07_small_sample_playbook.md` §1, then re-check.

## Step 2 — Judge gate

If labels came from anything other than an exact programmatic check, run
`scripts/judge_calibration.py` on the subset with reference labels (or on multi-judge data).
**Stop and fix the rubric if κ is near chance or AUC≈0.5.** Carry the judge κ forward as the floor
on label noise. (`06_judge_calibration.md`.)

## Step 3 — CTT item pass (every regime)

Run `scripts/eval_item_analysis.py`. No model fitting, no distributional assumptions — the two
core statistics map directly onto "is this item too easy/hard?" and "does it separate good runs
from bad ones?" This step works at any N and is the only item-level method when takers < ~30.

**Item difficulty (p):** per-item pass rate. Higher p = easier.

| p range | Meaning | Action |
|---|---|---|
| p ≥ 0.95 | Saturated | Carries ~no info about version differences. Trim unless it guards a known regression (then keep as insurance). |
| 0.30–0.70 | Mid-range | Max discriminative information. Keep. |
| p ≤ 0.05 | Floored | Too hard *or* broken/mis-specified. Inspect before cutting. |

**Item discrimination (item–rest correlation, r_rest):** correlate each taker's score on item i
with that taker's rest score (sum over all other items). Avoids self-correlation inflation.

| r_rest | Meaning | Action |
|---|---|---|
| ≥ 0.30 | Strong — good runs pass, weak runs fail | Keep; core signal. |
| 0.15–0.30 | Acceptable | Keep. |
| 0–0.15 | Non-discriminating | Trim candidate. Adds runtime, not signal. |
| **< 0** | **Broken — worse runs pass more than better runs** | **Urgent fix, not trim.** Wrong gold label, inverted grader, or perverse rubric. A single negative-discrimination item can flip a version comparison. |

At tiny N (< ~8 takers), supplement with the **discrimination index** proxy: mean pass rate of
the top-third takers minus the bottom-third (`D = p_top − p_bottom`). Flag `D < 0.15` as weak,
`D < 0` as broken. More stable than r_rest at very small taker counts.

**Saturation / contamination / redundancy heuristics:**

- **Suite saturation:** median difficulty very high (most items p > 0.9) → suite has aged out;
  top takers are all bunched near ceiling, version differences are invisible. Add harder cases.
- **Contamination smell:** a cluster of easy + non-discriminating items (p ≈ high ∧ r_rest ≈ 0)
  whose answers are likely in training data. CTT flags the pattern; confirming contamination needs
  the IRT 3PL guessing parameter or provenance checks (`04_irt_for_evals.md`).
- **Redundant items:** very high inter-item correlation between two cases → they measure the same
  thing. Keep one. The script reports an item–item matrix to spot clusters.

Read the output for:

- **negative-discrimination items** → fix list (urgent; can flip comparisons),
- **saturated / floored / non-discriminating items** → trim candidates,
- **redundant clusters** → keep-one candidates,
- **overall saturation** (median difficulty very high) → suite has aged out.

## Step 4 — Reliability & sizing

Run `scripts/gtheory_eval.py` with your facets. Read the dependability coefficient against the
decision (Eρ² for ranking, Φ for thresholds) and the **D-study** for the cheapest path to adequate
reliability. (`03_generalizability_theory.md`.) This is also where "version B beat A by 3 points"
gets adjudicated: if suite dependability is low, that delta is noise.

## Step 5 — IRT (model-bank only)

If takers ≥ ~30, run `scripts/irt_eval.py` for latent ability, item information/saturation, the
3PL guessing/contamination read, mislabel surfacing, and IRT-based item selection. Otherwise use
fixed-item anchoring for a latent version ranking, or skip. (`04_irt_for_evals.md`.)

## Step 6 — Triggering (if asked)

Run `scripts/sdt_trigger.py` on `in_scope`/`fired` data. Translate each skill's d′/criterion into
"rewrite content" (low d′) vs. "tune eagerness" (biased criterion), and read cross-skill false
alarms for routing overlaps. (`05_sdt_for_triggering.md`.)

## Decision rules — trim / keep / fix

Apply per item, in this precedence (a higher rule wins):

1. **FIX (never trim):** item–rest correlation `< 0` (or IRT effective discrimination `< 0`).
   Broken: rewards the wrong behavior, wrong gold label, or inverted grader. Investigate before
   trusting suite-level numbers.
2. **KEEP as guard (label it):** any item — even saturated — that guards a known regression,
   safety, or compliance failure. "Everyone passes" is the *goal* for a guard, not a reason to cut.
   Tag these `guard` so future trims skip them.
3. **KEEP as signal:** mid-range difficulty (0.30–0.70) **and** discrimination ≥ 0.15. The core of
   the suite.
4. **TRIM (dead weight):** discrimination in [0, 0.15] (passing it is unrelated to quality), or
   saturated (p ≥ 0.95) / floored (p ≤ 0.05) with no guard role, or a redundant duplicate of a
   kept item.
5. **HOLD / inspect:** floored items (p ≤ 0.05) that might be informative-but-too-hard rather than
   broken — keep if they discriminate among your strongest takers; otherwise revisit when takers
   improve.

Two global guards on the trimming itself:

- **Never trim below the reliability your decision needs.** Check the post-trim suite against the
  G-theory D-study — if cutting to 8 items drops Eρ² under your bar, you over-trimmed. The mid-range
  filter typically supports large cuts (44–70%) *while preserving ranking*; verify, don't assume.
- **Attach intervals.** Every trim/fix flag at small N gets a bootstrap CI. Don't cut an item whose
  discrimination CI comfortably includes 0.3 just because the point estimate is 0.1.

## Output format — the audit summary

Deliver, in this order:
1. **Decision + regime** (one line each).
2. **Judge gate result** (κ/AUC, or "exact check — n/a").
3. **Headline reliability** (Eρ² or Φ with interval) and the **one-line verdict** ("the suite can
   /cannot reliably support this decision").
4. **Item table**: difficulty, discrimination, flag — sorted fixes first, then trims.
5. **Trim/keep/fix lists** with the rule that fired and a CI on each.
6. **Sizing recommendation** from the D-study (if relevant).
7. **Triggering table** (if relevant): per-skill d′, criterion, and the content-vs-eagerness verdict.
8. **Decision thresholds used** — written down, so the next iteration is comparable.
