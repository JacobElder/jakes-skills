# 13 — Eval Content Drift, Measurement Invariance & Equating

**The problem you'll hit and not notice:** eval cases get reworded, gold answers get swapped, a
rubric gets tightened — but the `item_id` (column name) stays the same. Every analysis then pools
two genuinely different items under one name, and difficulty/ability estimates drift for reasons
that have nothing to do with the skill you're measuring. Column names are not trustworthy keys for
a measurement model. **Content hashes are.**

## Detect it: `scripts/item_drift.py`

Log a content hash (or the raw case text) alongside each `item_id` per run, then:

```
python item_drift.py manifest.csv --text-col item_text --run-col run_id --score-col score --out drift.json
```

It flags every `item_id` whose content changed across runs (drift — do not pool), reports the
**stable anchor set** (items unchanged everywhere), and, if scores are present, the pass-rate swing
per drifted item. A large swing on a "cosmetic" edit is the tell that the edit wasn't cosmetic — the
item now measures something else.

## Fix it: treat drift as new items + anchor-link the scale

1. **Don't pool changed items.** Suffix the content hash so a reworded case becomes a distinct item
   (`it07@a1b2` vs `it07@9f3c`). Pooling them is the actual error; renaming prevents it.
2. **Keep an anchor set.** Hold a subset of cases deliberately fixed across runs. These common items
   are what let you put pre- and post-rewrite runs on the **same latent scale** (common-item
   equating): calibrate the anchors once, then estimate everything else against them with
   `irt_latent.py --fixed-items`. Without anchors, a difficulty estimate from run A and one from run
   B are on different, unlinked scales and are not comparable — even if both say "b = 0.4".
3. **Test for DIF (differential item functioning).** Even an "unchanged" item can drift in meaning
   as models change around it. Fit the item's parameters separately in two runs (or for two model
   families) and check whether difficulty/discrimination moved more than Monte-Carlo error. An item
   that's easy for one model lineage and hard for another *at equal ability* is doing something
   other than measuring ability — flag it before trusting any cross-run trend. (A full DIF channel
   in the joint model is a `HANDOFF.md` item.)

## Why this matters for "is my skill improving over time?"

Tracking a skill across iterations is a longitudinal measurement, and longitudinal measurement is
only valid under **invariance** — the instrument has to mean the same thing at each time point. If
your eval suite quietly mutates between v3 and v5, an apparent gain (or regression) can be pure
instrument drift. The discipline is unglamorous but decisive: hash your cases, freeze an anchor set,
treat rewrites as new items, and link through the anchors. Then a movement in θ is a movement in the
skill, not in the ruler.

Related: `reference/12` (judge/model/run as facets) covers the *other* invariance threat — the
grader or base model changing under you — which is the same problem on a different axis.
