#!/usr/bin/env python3
"""
item_drift.py — Catch eval cases that changed content while keeping the same name.

The hidden failure: `it07` in last month's run is not the same `it07` after someone reworded the
prompt or swapped the gold answer — but the column name is identical, so every downstream analysis
silently pools two different items and the difficulty/ability estimates drift for reasons that have
nothing to do with your skill. This is a measurement-invariance / equating problem, and column
names are not trustworthy keys. Content hashes are.

What it does:
  * hashes each eval case's content (normalized) per run/version;
  * flags any item_id whose content changed across runs (DRIFT) — these must NOT be treated as the
    same item;
  * reports the STABLE items (one hash everywhere) — your anchor set for linking runs onto a common
    scale;
  * optionally, if score data is present, quantifies how much a drifted item's pass-rate moved.

INPUT  : a manifest CSV with one row per (item, run) and the case content:
           item_id, run_id, item_text     (run_id = version/date/commit; item_text = prompt[+gold])
         OR pre-hashed:  item_id, run_id, content_hash
         (optional) score column to quantify pass-rate movement.
USAGE  : python item_drift.py manifest.csv [--text-col item_text] [--run-col run_id]
              [--score-col score] [--out drift.json]
Dependencies: pandas (+ stdlib hashlib).
"""
import argparse, hashlib, json, re, sys
import pandas as pd


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def h(s):
    return hashlib.sha1(norm(s).encode()).hexdigest()[:12]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--item-col", default="item_id")
    ap.add_argument("--run-col", default="run_id")
    ap.add_argument("--text-col", default="item_text")
    ap.add_argument("--hash-col", default="content_hash")
    ap.add_argument("--score-col", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if args.item_col not in df.columns:
        sys.exit(f"ERROR: need an item column '{args.item_col}'")
    if args.hash_col in df.columns:
        df["_h"] = df[args.hash_col].astype(str)
    elif args.text_col in df.columns:
        df["_h"] = df[args.text_col].map(h)
    else:
        sys.exit(f"ERROR: need either '{args.text_col}' (content) or '{args.hash_col}' (precomputed hash). "
                 "Column names alone can't detect drift — log the case content or a hash of it.")
    has_run = args.run_col in df.columns

    print("# Eval item drift / measurement-invariance check\n")
    drifted, stable = [], []
    for item, sub in df.groupby(args.item_col):
        hashes = sub["_h"].unique()
        if len(hashes) > 1:
            runs = (sub.groupby("_h")[args.run_col].apply(lambda r: ",".join(map(str, sorted(set(r)))))
                    if has_run else pd.Series({hh: "?" for hh in hashes}))
            entry = {"item_id": str(item), "n_versions": int(len(hashes)),
                     "variants": {hh: runs.get(hh, "?") for hh in hashes}}
            if args.score_col and args.score_col in df.columns:
                pr = sub.groupby("_h")[args.score_col].mean()
                entry["passrate_by_version"] = {k: round(float(v), 3) for k, v in pr.items()}
                entry["passrate_swing"] = round(float(pr.max() - pr.min()), 3)
            drifted.append(entry)
        else:
            stable.append(str(item))

    if drifted:
        print(f"## DRIFTED — {len(drifted)} item(s) changed content under a stable name "
              f"(do NOT pool these across runs)\n")
        for e in sorted(drifted, key=lambda x: -x.get("passrate_swing", 0)):
            swing = (f"  pass-rate swing {e['passrate_swing']:+.2f}"
                     if "passrate_swing" in e else "")
            print(f"  {e['item_id']}: {e['n_versions']} content versions{swing}")
            for hh, runs in e["variants"].items():
                pr = (f"  pass={e['passrate_by_version'][hh]:.2f}" if "passrate_by_version" in e else "")
                print(f"      {hh}  (runs: {runs}){pr}")
        print()
    else:
        print("## No drift detected — every item_id has one content hash across runs.\n")

    print(f"## STABLE anchor set — {len(stable)} item(s) unchanged everywhere")
    print("   Use these as anchor items to link runs onto a common scale (fix their parameters in")
    print("   irt_latent.py --fixed-items, or keep them in every run as common items for equating).\n")

    # guidance
    if drifted:
        print("## What to do")
        print("  1. Treat each drifted item's versions as DIFFERENT items (suffix the hash, e.g. it07@a1b2).")
        print("  2. Re-estimate with the stable set as anchors so pre/post runs share a scale "
              "(reference/13).")
        print("  3. A large pass-rate swing on a 'cosmetic' edit means the edit wasn't cosmetic — "
              "the item now measures something else (DIF). Review it before trusting any trend.")

    if args.out:
        json.dump({"drifted": drifted, "stable": stable,
                   "n_drifted": len(drifted), "n_stable": len(stable)},
                  open(args.out, "w"), indent=2)
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
