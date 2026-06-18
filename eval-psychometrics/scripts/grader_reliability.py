"""
Inter-rater reliability for binary LLM-grader labels.
Computes pairwise Cohen's kappa, Fleiss' kappa, percent agreement,
per-judge pass rates, and flags high-disagreement items.
"""

import sys
import numpy as np
import pandas as pd
from itertools import combinations

CSV = "evals/fixtures/two_judge_labels.csv"


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    n = len(a)
    po = np.mean(a == b)
    pa1, pb1 = np.mean(a), np.mean(b)
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe)


def fleiss_kappa(wide: pd.DataFrame) -> float:
    """Fleiss' kappa for k=2 categories, arbitrary number of raters."""
    N, n = wide.shape  # items x raters
    # category proportions across all ratings
    p1 = wide.values.mean()
    p0 = 1 - p1
    pe = p1**2 + p0**2

    # per-item agreement
    n1 = wide.sum(axis=1)  # count of "1" votes per item
    n0 = n - n1
    Pi = (n1 * (n1 - 1) + n0 * (n0 - 1)) / (n * (n - 1))
    pbar = Pi.mean()

    return (pbar - pe) / (1 - pe)


def main():
    df = pd.read_csv(CSV)
    wide = df.pivot(index="item_id", columns="judge_id", values="label")
    wide = wide.sort_index()
    judges = list(wide.columns)
    n_items, n_judges = wide.shape

    print(f"Items: {n_items}   Judges: {n_judges}  ({', '.join(judges)})\n")

    # --- per-judge pass rates (potential systematic bias) ---
    print("Pass rates per judge:")
    for j in judges:
        pr = wide[j].mean()
        print(f"  {j}: {pr:.3f}  ({int(wide[j].sum())}/{n_items})")
    print()

    # --- pairwise Cohen's kappa + percent agreement ---
    print("Pairwise agreement:")
    kappas = {}
    for j1, j2 in combinations(judges, 2):
        a, b = wide[j1].values, wide[j2].values
        pct = np.mean(a == b)
        k = cohen_kappa(a, b)
        kappas[(j1, j2)] = k
        label = "slight" if k < 0.21 else "fair" if k < 0.41 else "moderate" if k < 0.61 else "substantial" if k < 0.81 else "almost perfect"
        print(f"  {j1} vs {j2}:  % agree={pct:.3f}   κ={k:.3f}  [{label}]")
    print()

    # --- Fleiss' kappa ---
    fk = fleiss_kappa(wide)
    label = "slight" if fk < 0.21 else "fair" if fk < 0.41 else "moderate" if fk < 0.61 else "substantial" if fk < 0.81 else "almost perfect"
    print(f"Fleiss' κ (all {n_judges} judges): {fk:.3f}  [{label}]\n")

    # --- item-level disagreement ---
    n_agree = wide.apply(lambda r: (r == r.iloc[0]).all(), axis=1)
    n_votes_for_1 = wide.sum(axis=1)
    contested = wide[~n_agree].copy()
    contested["votes_for_pass"] = n_votes_for_1[~n_agree]
    print(f"Unanimous items: {n_agree.sum()}/{n_items}")
    print(f"Contested items: {(~n_agree).sum()}/{n_items}\n")

    print("Contested items (split votes):")
    for item, row in contested.iterrows():
        votes = int(row["votes_for_pass"])
        labels = "  ".join(f"{j}={int(row[j])}" for j in judges)
        print(f"  {item}: {labels}   ({votes}/{n_judges} pass)")


if __name__ == "__main__":
    main()
