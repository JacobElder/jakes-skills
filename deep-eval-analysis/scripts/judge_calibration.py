#!/usr/bin/env python3
"""
judge_calibration.py — Is your grader trustworthy? (The gate before everything.)

Three checks, in order:
  1. RELIABILITY  — do graders agree beyond chance? (Cohen's / Fleiss' kappa)
  2. DISCRIMINATION — can the judge tell good from bad vs. a reference? (ROC-AUC)
  3. CALIBRATION  — are the judge's confidences honest? (Brier, ECE, reliability bins)

Run this whenever labels come from an LLM or human (skip only for exact
programmatic checks). If kappa is near chance or AUC ~ 0.5, fix the rubric before
trusting any downstream difficulty/discrimination/ability number.

INPUT  : long-format CSV. Provide whichever columns you have:
  - item_id, judge_id, label            -> reliability (multi-judge kappa)
  - item_id, label, reference           -> discrimination (vs. gold)
  - item_id, confidence, reference      -> calibration (Brier/ECE; confidence in [0,1])
USAGE  : python judge_calibration.py grades.csv [--bins 10]
Dependencies: numpy, pandas, scikit-learn.
"""
import argparse, sys
import numpy as np
import pandas as pd


def cohen_kappa(a, b):
    a = np.asarray(a); b = np.asarray(b)
    cats = np.unique(np.concatenate([a, b]))
    n = len(a)
    po = np.mean(a == b)
    pe = sum((np.mean(a == c)) * (np.mean(b == c)) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po


def fleiss_kappa(matrix):
    """matrix: items x categories counts (each row sums to n_raters)."""
    n_items, n_cat = matrix.shape
    n_rat = matrix.sum(axis=1)
    if not np.all(n_rat == n_rat[0]):
        return None
    n = n_rat[0]
    p_j = matrix.sum(axis=0) / (n_items * n)
    P_i = (np.sum(matrix ** 2, axis=1) - n) / (n * (n - 1))
    Pbar = P_i.mean(); Pe = np.sum(p_j ** 2)
    return (Pbar - Pe) / (1 - Pe) if Pe < 1 else 1.0


def kappa_label(k):
    if k is None: return ""
    return ("poor" if k < 0.2 else "fair" if k < 0.4 else "moderate" if k < 0.6
            else "substantial" if k < 0.8 else "near-ceiling")


def ece(conf, correct, bins):
    edges = np.linspace(0, 1, bins + 1)
    e = 0.0; rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf >= lo) & (conf < hi if hi < 1 else conf <= hi)
        if m.sum() == 0:
            rows.append((f"[{lo:.1f},{hi:.1f})", 0, np.nan, np.nan)); continue
        c = conf[m].mean(); acc = correct[m].mean()
        e += (m.sum() / len(conf)) * abs(c - acc)
        rows.append((f"[{lo:.1f},{hi:.1f})", int(m.sum()), round(c, 3), round(acc, 3)))
    return e, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--bins", type=int, default=10)
    args = ap.parse_args()
    df = pd.read_csv(args.csv)
    print("# Judge calibration\n")
    did = False

    # 1. reliability
    if {"item_id", "judge_id", "label"}.issubset(df.columns):
        did = True
        wide = df.pivot_table(index="item_id", columns="judge_id", values="label", aggfunc="first")
        judges = list(wide.columns)
        print(f"## 1. Reliability — {len(judges)} judges, {wide.shape[0]} items")
        if len(judges) == 2:
            sub = wide.dropna()
            k, po = cohen_kappa(sub.iloc[:, 0].values, sub.iloc[:, 1].values)
            print(f"   raw agreement = {po:.2f}   Cohen's kappa = {k:.2f} ({kappa_label(k)})")
        elif len(judges) > 2:
            sub = wide.dropna()
            cats = np.unique(sub.values)
            mat = np.zeros((len(sub), len(cats)))
            for r, (_, row) in enumerate(sub.iterrows()):
                for ci, c in enumerate(cats):
                    mat[r, ci] = (row.values == c).sum()
            fk = fleiss_kappa(mat)
            print(f"   Fleiss' kappa = {fk:.2f} ({kappa_label(fk)})" if fk is not None
                  else "   (unequal raters per item — use pairwise Cohen's kappa)")
            # pairwise
            for i in range(len(judges)):
                for j in range(i + 1, len(judges)):
                    s = wide[[judges[i], judges[j]]].dropna()
                    if len(s):
                        k, _ = cohen_kappa(s.iloc[:, 0].values, s.iloc[:, 1].values)
                        print(f"     {judges[i]} vs {judges[j]}: kappa={k:.2f}")
        print("   benchmark: strong LLM judges ~0.8 agreement w/ humans (≈ human-human ceiling).")
        print("   if near chance -> rewrite rubric to be behavioral/checkable before trusting scores.\n")

    # 2 & 3 need a reference
    if "reference" in df.columns:
        ref = df["reference"].astype(float).values
        if "label" in df.columns:
            did = True
            lab = df["label"].astype(float).values
            try:
                from sklearn.metrics import roc_auc_score
                if len(np.unique(ref)) > 1:
                    auc = roc_auc_score(ref, lab)
                    print(f"## 2. Discrimination vs. reference\n   ROC-AUC = {auc:.2f}", end="")
                    print("  -> judge label ~unrelated to truth; suite is dead on arrival." if auc < 0.6
                          else "  -> judge separates good from bad." )
                    print()
            except Exception as e:
                print(f"   (AUC skipped: {e})")
        if "confidence" in df.columns:
            did = True
            conf = df["confidence"].astype(float).values
            correct = (df.get("label", df["reference"]).astype(float).values == ref).astype(float) \
                if "label" in df.columns else ref
            # if no separate label, treat reference as correctness of a positive prediction
            if "label" not in df.columns:
                correct = ref
            brier = np.mean((conf - correct) ** 2)
            e, rows = ece(conf, correct, args.bins)
            print(f"## 3. Calibration\n   Brier = {brier:.3f}   ECE = {e:.3f}")
            print(f"   {'bin':>12} {'n':>5} {'conf':>7} {'acc':>7}")
            for name, n, c, acc in rows:
                if n: print(f"   {name:>12} {n:>5} {c:>7} {acc:>7}")
            gap = np.nanmean([abs(c - a) for _, n, c, a in rows if n and not np.isnan(c)])
            print(f"   mean bin gap = {gap:.3f}  ->",
                  "well calibrated" if e < 0.05 else "OVERCONFIDENT/miscalibrated — recalibrate "
                  "(temperature/Platt) or drop confidences and use binary label with its kappa.")
            print()

    if not did:
        print("No recognized column combo. Provide one of:")
        print("  item_id,judge_id,label   |   item_id,label,reference   |   item_id,confidence,reference")


if __name__ == "__main__":
    main()
