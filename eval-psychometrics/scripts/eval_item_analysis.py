#!/usr/bin/env python3
"""
eval_item_analysis.py — Classical item analysis on eval data.

Robust first-look item statistics that work in every regime (no model fitting).
Computes per-item difficulty, item-rest (point-biserial) discrimination, a
small-N-robust discrimination index, item-item redundancy, bootstrap CIs, and
emits trim / fix / keep lists per the decision rules in reference/01.

INPUT  : long-format CSV with columns: taker_id, item_id, score
         score is 1/0 (pass/fail) or partial credit in [0,1].
USAGE  : python eval_item_analysis.py results.csv [--boot 2000] [--seed 0] [--out report.csv]

Dependencies: numpy, pandas, scipy.
"""
import argparse, sys
import numpy as np
import pandas as pd


def load_matrix(path):
    df = pd.read_csv(path)
    need = {"taker_id", "item_id", "score"}
    if not need.issubset(df.columns):
        sys.exit(f"ERROR: CSV must have columns {need}; found {list(df.columns)}")
    # average duplicate (taker,item) cells (e.g. multiple seeds) into a single score
    df = df.groupby(["taker_id", "item_id"], as_index=False)["score"].mean()
    mat = df.pivot(index="taker_id", columns="item_id", values="score")
    return mat


def item_rest_corr(mat):
    """Point-biserial item-rest correlation: corr(item, sum of other items)."""
    X = mat.values.astype(float)
    n_takers, n_items = X.shape
    out = {}
    total = np.nansum(X, axis=1)
    for j, item in enumerate(mat.columns):
        col = X[:, j]
        rest = total - np.where(np.isnan(col), 0.0, col)
        mask = ~np.isnan(col)
        if mask.sum() < 3 or np.nanstd(col[mask]) == 0 or np.nanstd(rest[mask]) == 0:
            out[item] = np.nan
        else:
            out[item] = np.corrcoef(col[mask], rest[mask])[0, 1]
    return pd.Series(out)


def discrimination_index(mat, frac=1 / 3):
    """Mokken-style proxy: pass rate of top-third takers minus bottom-third.
    Robust at tiny N where the correlation is unstable."""
    total = mat.sum(axis=1)
    order = total.sort_values().index
    k = max(1, int(len(order) * frac))
    bottom, top = order[:k], order[-k:]
    return (mat.loc[top].mean() - mat.loc[bottom].mean())


def bootstrap_cis(mat, n_boot, seed):
    """Bootstrap over takers (rows) for difficulty and item-rest correlation."""
    rng = np.random.default_rng(seed)
    takers = mat.index.to_numpy()
    diffs, rrs = [], []
    for _ in range(n_boot):
        idx = rng.choice(len(takers), len(takers), replace=True)
        bs = mat.iloc[idx]
        diffs.append(bs.mean(axis=0).values)
        rrs.append(item_rest_corr(bs).reindex(mat.columns).values)
    diffs = np.array(diffs); rrs = np.array(rrs)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        q = lambda a, p: np.nanpercentile(a, p, axis=0)
        return (q(diffs, 2.5), q(diffs, 97.5), q(rrs, 2.5), q(rrs, 97.5))


def classify(diff, rr, di):
    if pd.notna(rr) and rr < 0:
        return "FIX:negative_discrimination"
    if pd.notna(di) and di < 0 and (pd.isna(rr)):
        return "FIX:negative_discrimination"
    if diff >= 0.95:
        return "TRIM:saturated"
    if diff <= 0.05:
        return "HOLD:floored"
    disc = rr if pd.notna(rr) else di
    if pd.notna(disc) and disc < 0.15:
        return "TRIM:non_discriminating"
    if 0.30 <= diff <= 0.70 and pd.notna(disc) and disc >= 0.15:
        return "KEEP:signal"
    return "KEEP"


def redundancy(mat, thresh=0.95):
    C = mat.corr()
    pairs = []
    items = list(C.columns)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if pd.notna(C.iloc[i, j]) and C.iloc[i, j] >= thresh:
                pairs.append((items[i], items[j], round(float(C.iloc[i, j]), 3)))
    return pairs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--boot", type=int, default=2000, help="bootstrap resamples (0 to skip)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None, help="write per-item table to this CSV")
    args = ap.parse_args()

    mat = load_matrix(args.csv)
    n_takers, n_items = mat.shape
    print(f"# CTT item analysis  |  {n_takers} takers x {n_items} items")
    if n_takers < 30:
        print(f"!! small-N regime ({n_takers} takers). CTT is usable but noisy; lean on the")
        print(f"!! bootstrap CIs and read reference/07_small_sample_playbook.md. IRT not advised.")

    diff = mat.mean(axis=0)
    rr = item_rest_corr(mat)
    di = discrimination_index(mat)
    table = pd.DataFrame({"difficulty_p": diff, "item_rest_r": rr, "disc_index": di})

    if args.boot and n_takers >= 4:
        dlo, dhi, rlo, rhi = bootstrap_cis(mat, args.boot, args.seed)
        table["p_lo"], table["p_hi"] = dlo, dhi
        table["r_lo"], table["r_hi"] = rlo, rhi

    table["flag"] = [classify(table.loc[i, "difficulty_p"], table.loc[i, "item_rest_r"],
                              table.loc[i, "disc_index"]) for i in table.index]
    table = table.round(3).sort_values(
        by="flag", key=lambda s: s.map(lambda x: 0 if x.startswith("FIX") else
                                       1 if x.startswith("TRIM") else
                                       2 if x.startswith("HOLD") else 3))

    pd.set_option("display.width", 200, "display.max_rows", None)
    print("\n## Per-item table (fixes first, then trims)\n")
    print(table.to_string())

    fixes = table.index[table.flag.str.startswith("FIX")].tolist()
    trims = table.index[table.flag.str.startswith("TRIM")].tolist()
    holds = table.index[table.flag.str.startswith("HOLD")].tolist()
    print("\n## Decision lists")
    print(f"FIX  (urgent, do not trim): {fixes or 'none'}")
    print(f"TRIM (dead weight, verify guard role first): {trims or 'none'}")
    print(f"HOLD (floored — informative-but-hard or broken?): {holds or 'none'}")

    med = float(np.nanmedian(diff))
    print(f"\n## Suite-level")
    print(f"median difficulty = {med:.2f}  ->", "SATURATED suite (aged out; add harder cases)"
          if med > 0.9 else "FLOORED suite (too hard; check grader/scope)" if med < 0.15
          else "healthy spread")
    midrange = table.index[(diff >= 0.30) & (diff <= 0.70)].tolist()
    print(f"mid-range (0.30–0.70) items, the discriminating core: {len(midrange)}/{n_items}")

    red = redundancy(mat)
    if red:
        print("\n## Redundant item pairs (r>=0.95 across takers — keep one):")
        for a, b, r in red:
            print(f"  {a}  <->  {b}   (r={r})")

    if args.out:
        table.to_csv(args.out)
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
