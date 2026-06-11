#!/usr/bin/env python3
"""
cluster_diagnostics.py — a standard diagnostic battery for a numeric dataset.

This is deliberately a *starting harness*, not a black box. It runs the steps the
cluster-analysis skill argues you should always run, so you don't re-derive them each
time. Read it, then EDIT it for your dataset (the right scaling, metric, and method are
data-specific decisions — see the references/ files).

What it does, in order:
  1. Clusterability   — Hopkins statistic (is there structure at all?).
  2. k-selection      — sweep k for KMeans; report silhouette (higher=better),
                        Davies-Bouldin (lower=better), Calinski-Harabasz (higher=better),
                        and GMM BIC (lower=better). Multiple criteria on purpose: they
                        disagree, and that disagreement is information.
  3. Method comparison— fit several families at a chosen k and report internal indices
                        plus where they DISAGREE on labels (pairwise ARI). Density methods
                        choose their own cluster count.
  4. Stability        — bootstrap ARI for one method/k. The validation that matters most:
                        a real structure reproduces under resampling; an artifact doesn't.

Philosophy reminders baked into the output:
  - Internal indices (silhouette/DB/CH) assume convex clusters. Do NOT use them to rank a
    density/manifold clustering against a centroid one — they share k-means' bias.
  - No single number is the answer. Triangulate, weight stability, and bring judgment.

Usage:
  python cluster_diagnostics.py data.csv --max-k 10 --scale standard
  python cluster_diagnostics.py data.csv --methods kmeans,gmm,hdbscan,ward --k 4
  python cluster_diagnostics.py data.csv --k 4 --stability-method kmeans --plots out/

Notes:
  - Uses only numeric columns (drops non-numeric with a warning). Handle categorical/mixed
    data per references/preprocessing.md before bringing it here.
  - hdbscan is optional; install `hdbscan` or use scikit-learn>=1.3's cluster.HDBSCAN.
"""

import argparse
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
)

# Optional HDBSCAN: prefer sklearn's, fall back to the standalone package.
_HDBSCAN = None
try:
    from sklearn.cluster import HDBSCAN as _HDBSCAN  # sklearn >= 1.3
except Exception:
    try:
        from hdbscan import HDBSCAN as _HDBSCAN
    except Exception:
        _HDBSCAN = None


def load_numeric(path):
    df = pd.read_csv(path)
    num = df.select_dtypes(include=[np.number])
    dropped = [c for c in df.columns if c not in num.columns]
    if dropped:
        warnings.warn(
            f"Dropping non-numeric columns {dropped}. Encode/handle these per "
            f"references/preprocessing.md (Gower/k-prototypes/LCA) before clustering."
        )
    X = num.dropna()
    if len(X) < len(num):
        warnings.warn(f"Dropped {len(num) - len(X)} rows with NaNs.")
    if X.shape[1] == 0:
        sys.exit("No numeric columns to cluster. See references/preprocessing.md.")
    return X.values, list(num.columns)


def scale(X, how):
    if how == "none":
        return X
    scaler = {"standard": StandardScaler, "minmax": MinMaxScaler,
              "robust": RobustScaler}[how]()
    return scaler.fit_transform(X)


def hopkins(X, n_samples=None, seed=0):
    """Hopkins statistic. ~0.5 => indistinguishable from uniform (no cluster tendency);
    ->1 => strong tendency. Crude and dimensionality-sensitive — a sanity check, not proof."""
    from sklearn.neighbors import NearestNeighbors
    rng = np.random.RandomState(seed)
    n, d = X.shape
    m = n_samples or min(int(0.1 * n) + 1, n - 1, 200)
    nbrs = NearestNeighbors(n_neighbors=2).fit(X)
    # distances from real sampled points to their nearest *other* real point
    idx = rng.choice(n, m, replace=False)
    w = nbrs.kneighbors(X[idx], return_distance=True)[0][:, 1]
    # distances from uniform random points (in data's bounding box) to nearest real point
    mins, maxs = X.min(0), X.max(0)
    U = rng.uniform(mins, maxs, (m, d))
    u = nbrs.kneighbors(U, n_neighbors=1, return_distance=True)[0][:, 0]
    su, sw = u.sum(), w.sum()
    return su / (su + sw) if (su + sw) > 0 else 0.5


def k_sweep(X, max_k):
    print("\n=== k-selection sweep (KMeans + GMM BIC) ===")
    print("Multiple criteria on purpose — expect disagreement; that's information.")
    print(f"{'k':>3} {'silhouette':>11} {'davies_b':>10} {'calinski_h':>11} {'gmm_bic':>12}")
    print(f"{'':>3} {'(higher)':>11} {'(lower)':>10} {'(higher)':>11} {'(lower)':>12}")
    rows = []
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
        labels = km.labels_
        sil = silhouette_score(X, labels)
        db = davies_bouldin_score(X, labels)
        ch = calinski_harabasz_score(X, labels)
        try:
            bic = GaussianMixture(n_components=k, n_init=3,
                                  random_state=0).fit(X).bic(X)
        except Exception:
            bic = float("nan")
        rows.append((k, sil, db, ch, bic))
        print(f"{k:>3} {sil:>11.3f} {db:>10.3f} {ch:>11.1f} {bic:>12.1f}")
    # Suggestions (advisory only)
    best_sil = max(rows, key=lambda r: r[1])[0]
    best_db = min(rows, key=lambda r: r[2])[0]
    best_bic = min(rows, key=lambda r: r[4]
                   if not np.isnan(r[4]) else float("inf"))[0]
    print(f"\nAdvisory: silhouette favors k={best_sil}, "
          f"Davies-Bouldin favors k={best_db}, GMM-BIC favors k={best_bic}.")
    if len({best_sil, best_db, best_bic}) > 1:
        print("They disagree — inspect the silhouette plot, check stability at each "
              "candidate k, and let interpretability break the tie. Do not just take "
              "the best silhouette.")
    return rows


def fit_method(name, X, k):
    """Return labels for a named method. Density methods ignore k and find their own."""
    if name == "kmeans":
        return KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
    if name == "gmm":
        return GaussianMixture(n_components=k, n_init=3,
                               random_state=0).fit_predict(X)
    if name == "ward":
        return AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(X)
    if name == "dbscan":
        return DBSCAN().fit_predict(X)  # default eps=0.5 — TUNE via k-distance plot!
    if name == "hdbscan":
        if _HDBSCAN is None:
            warnings.warn("HDBSCAN unavailable; install `hdbscan` or sklearn>=1.3.")
            return None
        try:
            return _HDBSCAN(min_cluster_size=max(5, len(X) // 100),
                            copy=True).fit_predict(X)
        except TypeError:  # standalone hdbscan package has no copy kwarg
            return _HDBSCAN(min_cluster_size=max(5, len(X) // 100)).fit_predict(X)
    warnings.warn(f"Unknown method '{name}'.")
    return None


def method_comparison(X, methods, k):
    print(f"\n=== Method comparison (k={k} where applicable) ===")
    results = {}
    for m in methods:
        labels = fit_method(m, X, k)
        if labels is None:
            continue
        results[m] = labels
        n_clusters = len(set(labels) - {-1})
        n_noise = int((labels == -1).sum())
        # internal indices need >=2 clusters and undefined with all-noise
        valid = labels != -1
        if len(set(labels[valid])) >= 2 and valid.sum() > len(set(labels[valid])):
            sil = silhouette_score(X[valid], labels[valid])
        else:
            sil = float("nan")
        noise_str = f", noise={n_noise}" if n_noise else ""
        print(f"  {m:>9}: {n_clusters} clusters{noise_str}, silhouette={sil:.3f}")
    # Pairwise ARI — where do methods disagree? Disagreement flags fragile structure.
    names = list(results)
    if len(names) > 1:
        print("\n  Pairwise agreement (ARI; 1=identical, 0=chance):")
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = results[names[i]], results[names[j]]
                ari = adjusted_rand_score(a, b)
                flag = "  <-- low agreement" if ari < 0.5 else ""
                print(f"    {names[i]:>9} vs {names[j]:<9}: ARI={ari:.3f}{flag}")
        print("  Internal indices assume convex clusters — don't use silhouette to "
              "declare a 'winner' across families with different geometry.")
    return results


def stability(X, method, k, n_boot=30, seed=0):
    print(f"\n=== Stability: bootstrap ARI for '{method}' (k={k}, {n_boot} resamples) ===")
    rng = np.random.RandomState(seed)
    base = fit_method(method, X, k)
    if base is None:
        return
    aris = []
    n = len(X)
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        boot_labels = fit_method(method, X[idx], k)
        if boot_labels is None:
            continue
        # compare on the resampled points against the base labels for those same points
        aris.append(adjusted_rand_score(base[idx], boot_labels))
    aris = np.array(aris)
    print(f"  mean ARI = {aris.mean():.3f}  (std {aris.std():.3f}, "
          f"min {aris.min():.3f})")
    if aris.mean() >= 0.75:
        print("  -> Stable. The partition reproduces under resampling.")
    elif aris.mean() >= 0.6:
        print("  -> Marginal. Treat with caution; inspect which clusters dissolve.")
    else:
        print("  -> Unstable. This solution likely does not reflect real structure. "
              "Reconsider k, method, preprocessing — or whether clusters exist at all.")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv", help="Path to a CSV with numeric features.")
    p.add_argument("--scale", default="standard",
                   choices=["standard", "minmax", "robust", "none"],
                   help="Feature scaling (default standard). 'none' if units are already "
                        "comparable, e.g. spatial coords — see preprocessing.md.")
    p.add_argument("--max-k", type=int, default=10, help="Max k for the sweep.")
    p.add_argument("--k", type=int, default=None,
                   help="Fixed k for method comparison & stability (default: best "
                        "silhouette from the sweep).")
    p.add_argument("--methods", default="kmeans,gmm,ward,hdbscan",
                   help="Comma-separated: kmeans,gmm,ward,dbscan,hdbscan.")
    p.add_argument("--stability-method", default="kmeans",
                   help="Which method to bootstrap for stability.")
    p.add_argument("--no-sweep", action="store_true", help="Skip the k sweep.")
    args = p.parse_args()

    X, cols = load_numeric(args.csv)
    print(f"Loaded {X.shape[0]} rows x {X.shape[1]} numeric features: {cols}")
    Xs = scale(X, args.scale)
    print(f"Scaling: {args.scale}")
    if X.shape[1] > 15:
        print("WARNING: high dimensionality. Distances concentrate — reduce dimensions "
              "(PCA/UMAP) or select features before trusting any of this. See "
              "preprocessing.md.")

    h = hopkins(Xs)
    print(f"\n=== Clusterability: Hopkins = {h:.3f} ===")
    if h < 0.6:
        print("  ~0.5 means little/no cluster tendency. Clusters you find may be "
              "artifacts. Consider stopping and reporting 'no robust structure'.")
    else:
        print("  Suggests some cluster tendency. (Crude check — still validate stability.)")

    chosen_k = args.k
    if not args.no_sweep:
        rows = k_sweep(Xs, args.max_k)
        if chosen_k is None:
            chosen_k = max(rows, key=lambda r: r[1])[0]
            print(f"\nUsing k={chosen_k} (best silhouette) for the steps below. "
                  f"This is a default, not a verdict — override with --k.")
    if chosen_k is None:
        chosen_k = 3

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    method_comparison(Xs, methods, chosen_k)
    stability(Xs, args.stability_method, chosen_k)

    print("\nDone. Remember: this harness narrows the field; it does not pick the "
          "answer. Weight stability and interpretability over any single index.")


if __name__ == "__main__":
    main()
