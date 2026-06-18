#!/usr/bin/env python3
"""
sdt_trigger.py — Signal detection theory for skill triggering / routing.

Treats each skill's trigger as a yes/no detector over queries and separates
DISCRIMINABILITY (d', whether the description can tell in-scope from out-of-scope
queries at all) from BIAS (criterion c, whether it fires too eagerly or too
reluctantly). These need different fixes: low d' = rewrite the description's
CONTENT; biased c = tune its EAGERNESS. Raw trigger accuracy hides this split.

INPUT  : long-format CSV: skill_id, in_scope, fired
         in_scope = 1 if the query SHOULD trigger this skill, else 0
         fired    = 1 if the skill DID trigger, else 0
         (You need real out-of-scope "noise" rows or there is no false-alarm rate.)
USAGE  : python sdt_trigger.py triggers.csv [--cross]

--cross also prints a skill x skill false-alarm matrix to localize routing overlap.
Dependencies: numpy, pandas, scipy.
"""
import argparse, sys
import numpy as np
import pandas as pd
from scipy.stats import norm


def rates_loglinear(hits, misses, fa, cr):
    """Hit and FA rates with the log-linear correction (add 0.5 to each cell,
    1.0 to each row total) to keep z-scores finite at small N."""
    H = (hits + 0.5) / (hits + misses + 1.0)
    F = (fa + 0.5) / (fa + cr + 1.0)
    corrected = (hits in (0,) or misses in (0,) or fa in (0,) or cr in (0,))
    return H, F, corrected


def a_prime(H, F):
    if H >= F:
        return 0.5 + ((H - F) * (1 + H - F)) / (4 * H * (1 - F)) if H * (1 - F) else 0.5
    return 0.5 - ((F - H) * (1 + F - H)) / (4 * F * (1 - H)) if F * (1 - H) else 0.5


def b_double_prime(H, F):
    num = (1 - H) * (1 - F) - H * F
    den = (1 - H) * (1 - F) + H * F
    return num / den if den else 0.0


def analyze_skill(sub):
    pos = sub[sub.in_scope == 1]; neg = sub[sub.in_scope == 0]
    hits = int((pos.fired == 1).sum()); misses = int((pos.fired == 0).sum())
    fa = int((neg.fired == 1).sum()); cr = int((neg.fired == 0).sum())
    if (hits + misses) == 0 or (fa + cr) == 0:
        return None, (hits, misses, fa, cr)
    H, F, corrected = rates_loglinear(hits, misses, fa, cr)
    dprime = norm.ppf(H) - norm.ppf(F)
    crit = -0.5 * (norm.ppf(H) + norm.ppf(F))
    res = dict(hits=hits, misses=misses, fa=fa, cr=cr, H=H, F=F,
               dprime=dprime, criterion=crit, Aprime=a_prime(H, F),
               Bpp=b_double_prime(H, F), corrected=corrected,
               accuracy=(hits + cr) / (hits + misses + fa + cr))
    return res, (hits, misses, fa, cr)


def verdict(d, c):
    parts = []
    if d < 1.0:
        parts.append("LOW d' -> the description can't separate in-scope from out-of-scope. "
                     "FIX CONTENT: sharpen what it's for, add distinguishing contexts and "
                     "near-miss carve-outs, resolve overlap with neighbors.")
    else:
        parts.append("d' adequate -> the description discriminates.")
    if c > 0.5:
        parts.append("criterion HIGH (trigger-shy, under-fires) -> make the description pushier; "
                     "add user phrasings that SHOULD match.")
    elif c < -0.5:
        parts.append("criterion LOW (trigger-happy, over-fires) -> tighten/qualify trigger phrases; "
                     "add explicit 'do not use when...' carve-outs.")
    else:
        parts.append("criterion ~neutral.")
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--cross", action="store_true", help="print skill x skill false-alarm matrix")
    ap.add_argument("--out", default=None, help="write per-skill d'/criterion/verdict as JSON")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    need = {"skill_id", "in_scope", "fired"}
    if not need.issubset(df.columns):
        sys.exit(f"ERROR: need columns {need}; found {list(df.columns)}")

    print("# Signal detection theory for triggering\n")
    rows = []
    for skill, sub in df.groupby("skill_id"):
        res, counts = analyze_skill(sub)
        if res is None:
            print(f"## {skill}: SKIP — need both in-scope and out-of-scope rows "
                  f"(got H/M/FA/CR = {counts}). Add real noise trials.")
            continue
        rows.append((skill, res))
        print(f"## {skill}")
        print(f"   counts  H={res['hits']} M={res['misses']} FA={res['fa']} CR={res['cr']}"
              + ("   [log-linear correction active: sparse cells, widen the eval]" if res['corrected'] else ""))
        print(f"   hit rate={res['H']:.2f}  fa rate={res['F']:.2f}  accuracy={res['accuracy']:.2f}")
        print(f"   d'={res['dprime']:.2f}   criterion c={res['criterion']:+.2f}"
              f"   (A'={res['Aprime']:.2f}, B''={res['Bpp']:+.2f})")
        print(f"   -> {verdict(res['dprime'], res['criterion'])}\n")

    if rows:
        print("## Summary")
        print(f"   {'skill':<24} {'d-prime':>8} {'criterion':>10} {'accuracy':>9}")
        for skill, r in sorted(rows, key=lambda x: x[1]['dprime']):
            print(f"   {skill:<24} {r['dprime']:>8.2f} {r['criterion']:>+10.2f} {r['accuracy']:>9.2f}")

    if args.out and rows:
        import json
        skills = [{"skill_id": s, "dprime": round(float(r["dprime"]), 3),
                   "criterion": round(float(r["criterion"]), 3),
                   "accuracy": round(float(r["accuracy"]), 3),
                   "verdict": verdict(r["dprime"], r["criterion"])} for s, r in rows]
        json.dump({"skills": skills}, open(args.out, "w"), indent=2)
        print(f"\nWrote {args.out}")

    if args.cross and "fired" in df.columns:
        # cross false alarms: among queries in-scope for skill A, how often did skill B fire?
        skills = sorted(df.skill_id.unique())
        print("\n## Cross false-alarm matrix (row=in-scope skill, col=skill that fired)")
        print("   high off-diagonal = those two skills are not discriminable from each other")
        hdr = "   " + "".join(f"{s[:8]:>10}" for s in skills)
        print(hdr)
        for a in skills:
            scope = set(df[(df.skill_id == a) & (df.in_scope == 1)].index)
            line = f"   {a[:8]:<10}"
            for b in skills:
                bsub = df[(df.skill_id == b)]
                # rows where query is in-scope for A and skill B fired (proxy if shared query ids exist)
                if "query_id" in df.columns:
                    aq = set(df[(df.skill_id == a) & (df.in_scope == 1)].query_id)
                    bf = df[(df.skill_id == b) & (df.query_id.isin(aq)) & (df.fired == 1)]
                    denom = len(aq) if aq else 1
                    line += f"{len(bf)/denom:>10.2f}"
                else:
                    line += f"{'--':>10}"
            print(line)
        if "query_id" not in df.columns:
            print("   (add a shared 'query_id' column to enable the cross matrix.)")


if __name__ == "__main__":
    main()
