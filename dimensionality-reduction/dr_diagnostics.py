#!/usr/bin/env python3
"""
dr_diagnostics.py — quantitative quality metrics for a dimensionality-reduction embedding.

The whole point of this script: stop judging embeddings by how nice the 2D picture looks.
That is circular — you will always be able to find a perplexity / seed / method that produces
the clusters you were hoping to see. These metrics ask a harder, falsifiable question:
"does the low-dimensional embedding actually preserve the neighbourhood / distance structure
of the original space?"

Metrics computed (all in [0,1] or [-1,1], higher = better unless noted):
  - trustworthiness        : are the embedding's near-neighbours genuinely near in HD space?
                             (penalises FALSE neighbours introduced by the embedding)
  - continuity             : are HD near-neighbours kept near in the embedding?
                             (penalises TRUE neighbours torn apart by the embedding)
  - knn_overlap@k          : mean fraction of each point's k HD-neighbours retained in LD
  - shepard_pearson /      : correlation between HD and LD pairwise distances.
    shepard_spearman         Low values are the quantitative form of "you cannot read
                             distances off a t-SNE/UMAP plot."
  - label_knn_accuracy     : (optional, needs labels) k-NN classification accuracy IN HD space.
                             Reported so you compare the embedding against the signal that
                             actually exists in the data, not against a perfect oracle.
  - label_knn_accuracy_ld  : (optional) same, computed on the embedding. If LD >> HD here,
                             treat it as a red flag for label leakage / over-clustering rather
                             than a triumph (see Chari & Pachter 2023 and its rebuttals).

Dependencies: numpy, scikit-learn, scipy. No GPU, no embedding library required —
you pass in the embedding you already computed.

CLI:
  python dr_diagnostics.py --hd X.npy --ld Y.npy [--labels y.npy] [--k 15] [--max-pairs 50000]
  (also accepts .csv for any of the three; assumes no header / numeric, or pass --csv-header)

Library:
  from dr_diagnostics import diagnose
  report = diagnose(X_highdim, Y_embedding, labels=y, k=15)
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import pearsonr, spearmanr
from sklearn.manifold import trustworthiness as _sk_trustworthiness
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier


def _knn_indices(D_or_X: np.ndarray, k: int, metric: str = "euclidean") -> np.ndarray:
    """Return (n, k) array of nearest-neighbour indices, excluding self."""
    nn = NearestNeighbors(n_neighbors=k + 1, metric=metric)
    nn.fit(D_or_X)
    idx = nn.kneighbors(D_or_X, return_distance=False)
    return idx[:, 1:]  # drop self


def continuity(X: np.ndarray, Y: np.ndarray, k: int) -> float:
    """Continuity is the dual of trustworthiness: it penalises HD neighbours that the
    embedding tears apart. sklearn ships trustworthiness but not continuity, so we
    compute it by swapping the roles of the two spaces (continuity(X,Y) == trust(Y,X))."""
    return float(_sk_trustworthiness(Y, X, n_neighbors=k))


def knn_overlap(X: np.ndarray, Y: np.ndarray, k: int) -> float:
    hd = _knn_indices(X, k)
    ld = _knn_indices(Y, k)
    overlaps = [len(set(hd[i]) & set(ld[i])) / k for i in range(X.shape[0])]
    return float(np.mean(overlaps))


def shepard_correlation(X: np.ndarray, Y: np.ndarray, max_pairs: int = 50000,
                        seed: int = 0) -> dict:
    """Correlation between HD and LD pairwise distances. Subsamples pairs for tractability."""
    n = X.shape[0]
    n_pairs = n * (n - 1) // 2
    if n_pairs <= max_pairs:
        dh = pdist(X)
        dl = pdist(Y)
    else:
        rng = np.random.default_rng(seed)
        i = rng.integers(0, n, size=max_pairs)
        j = rng.integers(0, n, size=max_pairs)
        mask = i != j
        i, j = i[mask], j[mask]
        dh = np.linalg.norm(X[i] - X[j], axis=1)
        dl = np.linalg.norm(Y[i] - Y[j], axis=1)
    return {
        "shepard_pearson": float(pearsonr(dh, dl)[0]),
        "shepard_spearman": float(spearmanr(dh, dl)[0]),
    }


def _knn_cv_accuracy(X: np.ndarray, y: np.ndarray, k: int) -> float:
    k_eff = min(k, max(1, np.bincount(y).min() - 1)) if y.dtype.kind in "iu" else k
    k_eff = max(1, k_eff)
    clf = KNeighborsClassifier(n_neighbors=k_eff)
    scores = cross_val_score(clf, X, y, cv=min(5, np.unique(y, return_counts=True)[1].min()))
    return float(np.mean(scores))


def diagnose(X: np.ndarray, Y: np.ndarray, labels: Optional[np.ndarray] = None,
             k: int = 15, max_pairs: int = 50000) -> dict:
    """Compute the full diagnostic report. X = high-dim data, Y = embedding."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if X.shape[0] != Y.shape[0]:
        raise ValueError(f"row mismatch: HD has {X.shape[0]}, LD has {Y.shape[0]}")
    n = X.shape[0]
    k = min(k, n - 1)

    report = {
        "n_samples": int(n),
        "hd_dims": int(X.shape[1]),
        "ld_dims": int(Y.shape[1]),
        "k": int(k),
        "trustworthiness": float(_sk_trustworthiness(X, Y, n_neighbors=k)),
        "continuity": continuity(X, Y, k),
        "knn_overlap": knn_overlap(X, Y, k),
    }
    report.update(shepard_correlation(X, Y, max_pairs=max_pairs))

    if labels is not None:
        labels = np.asarray(labels)
        if labels.dtype.kind == "f":
            labels = labels.astype(int)
        try:
            report["label_knn_accuracy_hd"] = _knn_cv_accuracy(X, labels, k)
            report["label_knn_accuracy_ld"] = _knn_cv_accuracy(Y, labels, k)
        except Exception as e:  # pragma: no cover - defensive
            report["label_knn_accuracy_error"] = str(e)

    report["interpretation"] = _interpret(report)
    return report


def _interpret(r: dict) -> list:
    notes = []
    if r["trustworthiness"] < 0.9:
        notes.append("LOW trustworthiness: the embedding invents neighbours that are not "
                     "close in the original space. Do not read fine cluster structure off it.")
    if r["continuity"] < 0.9:
        notes.append("LOW continuity: the embedding tears apart points that are neighbours "
                     "in the original space. Global layout is unreliable.")
    if r["shepard_spearman"] < 0.5:
        notes.append("LOW Shepard correlation: pairwise distances are NOT preserved. "
                     "Inter-cluster gaps in this plot are largely artefacts — do not "
                     "interpret distances between clusters as dissimilarity.")
    if "label_knn_accuracy_ld" in r and "label_knn_accuracy_hd" in r:
        if r["label_knn_accuracy_ld"] > r["label_knn_accuracy_hd"] + 0.05:
            notes.append("Embedding kNN accuracy exceeds HD accuracy: the embedding may be "
                         "manufacturing separation. Validate clusters in HD/PCA space, not here.")
    if not notes:
        notes.append("Neighbourhood structure reasonably preserved at this k. Distances still "
                     "may not be — check the Shepard values before interpreting gaps.")
    return notes


def _load(path: str, csv_header: bool) -> np.ndarray:
    if path.endswith(".npy"):
        return np.load(path)
    skip = 1 if csv_header else 0
    return np.loadtxt(path, delimiter=",", skiprows=skip)


def main(argv=None):
    p = argparse.ArgumentParser(description="Quantitative DR embedding diagnostics.")
    p.add_argument("--hd", required=True, help="high-dim data (.npy or .csv)")
    p.add_argument("--ld", required=True, help="embedding (.npy or .csv)")
    p.add_argument("--labels", default=None, help="optional labels (.npy or .csv)")
    p.add_argument("--k", type=int, default=15, help="neighbourhood size (default 15)")
    p.add_argument("--max-pairs", type=int, default=50000)
    p.add_argument("--csv-header", action="store_true", help="CSV files have a header row")
    p.add_argument("--out", default=None, help="write JSON report here")
    a = p.parse_args(argv)

    X = _load(a.hd, a.csv_header)
    Y = _load(a.ld, a.csv_header)
    y = _load(a.labels, a.csv_header) if a.labels else None
    report = diagnose(X, Y, labels=y, k=a.k, max_pairs=a.max_pairs)

    out = json.dumps(report, indent=2)
    if a.out:
        with open(a.out, "w") as f:
            f.write(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
