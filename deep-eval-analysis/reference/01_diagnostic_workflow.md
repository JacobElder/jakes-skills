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

## Step 3 — Item-level diagnostics (every regime)

Run `scripts/eval_item_analysis.py`. Two core statistics — difficulty and the negative-discrimination
alarm — work at any N without assuming items measure the same latent trait. Eval suites are
diagnostic batteries covering diverse capabilities by design; items aren't expected to share a
common factor. This means the r_rest *threshold* (e.g., trim if < 0.15) is a weak guide: low
r_rest can mean "tests a unique capability," not "dead weight." Use difficulty and the broken-item
alarm as the primary signals; treat r_rest thresholds as secondary.

**Item difficulty (p):** per-item pass rate. Higher p = easier. Valid regardless of what the item measures.

| p range | Meaning | Action |
|---|---|---|
| p ≥ 0.95 | Saturated | Carries ~no info about version differences. Trim unless it guards a known regression (then label and keep as insurance). |
| 0.30–0.70 | Mid-range | Maximally informative about version differences. Keep. |
| p ≤ 0.05 | Floored | Too hard *or* broken/mis-specified. Inspect before cutting. |

**Broken-item alarm (negative r_rest or negative D):** if versions that do well overall tend to
*fail* this item more than versions that do poorly, the item is actively broken — wrong gold
label, inverted grader, or perverse rubric. Valid regardless of whether items are correlated.

- `r_rest < 0` (item–rest correlation): correlate each taker's score on item i with rest-score.
  Negative → **urgent fix, not trim.** A single broken item can flip a version comparison.
- `D = p_top − p_bottom < 0` (discrimination index): pass rate of the top-third takers minus the
  bottom-third. Negative = same alarm, more robust at tiny N (< ~8 takers).

**Do not use r_rest thresholds as a trim rule in diverse eval suites.** A case with r_rest = 0.08
might be testing a unique capability that no other case covers. The right question before trimming
on low r_rest is: "Is this the only case testing this capability?" If yes, keep it regardless of
the correlation. If you have four similar cases and one has low r_rest, trim the weakest of the
four — not on correlation alone, but on coverage redundancy.

**Saturation / contamination / redundancy heuristics:**

- **Suite saturation:** median difficulty very high (most items p > 0.9) → suite has aged out;
  top takers all bunch near ceiling. Add harder cases.
- **Contamination smell:** a cluster of easy items with near-zero discrimination whose answers are
  likely in training data. CTT flags the pattern (easy ∧ D ≈ 0); confirming needs IRT 3PL or
  provenance checks (`04_irt_for_evals.md`).
- **Redundant items:** two cases with near-identical pass/fail patterns across takers → same
  capability tested twice. Keep one. The script reports pairwise item correlations.

Read the output for:

- **r_rest < 0 or D < 0 items** → fix list (urgent; broken items can flip comparisons),
- **saturated / floored items with no guard role** → trim candidates,
- **redundant pairs** → keep-one candidates,
- **overall saturation** → suite needs harder cases.

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
