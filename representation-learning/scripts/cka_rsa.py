#!/usr/bin/env python3
"""
cka_rsa.py — compare two representations of the SAME items the right way.

To ask "did models A and B learn similar representations?" you cannot compare
neuron-by-neuron (different bases) and you cannot use raw cosine across two
independently-trained spaces (not aligned). Use a similarity measure that is
invariant to the transformations that shouldn't matter:

  linear CKA      Kornblith et al. (2019). Invariant to orthogonal transforms
                  and isotropic scaling; NOT invariant to arbitrary invertible
                  linear maps (which is why it is preferred over CCA-based
                  scores that are). CKA(X, X)=1; CKA(X, XQ)=1 for orthogonal Q.

  RBF CKA         same, with a Gaussian kernel (captures nonlinear similarity).

  RSA            representational similarity analysis (Kriegeskorte 2008):
                  build a representational dissimilarity matrix (RDM) for each
                  space, then Spearman-correlate the off-diagonal entries. The
                  neuroscience-native tool; also works to compare an ANN to
                  brain data. NOTE: invariances depend on the RDM metric --
                  a Euclidean RDM makes RSA invariant to orthogonal transforms
                  (and, via Spearman, to scaling); a correlation RDM (the
                  common default) additionally removes per-item mean/scale but
                  is NOT orthogonal-invariant in feature space.

  Procrustes     orthogonal alignment: best rotation/reflection mapping X to Y,
                  with a normalized disparity in [0, 1] (0 = identical up to
                  rotation+scale). Use when you want to ALIGN two embedding sets
                  of the same items, not just score them.

All four take X (n x p) and Y (n x q): n matched items, possibly different
feature dims. Rows must correspond.

Usage:
    from cka_rsa import linear_cka, rbf_cka, rsa, procrustes_disparity
    python cka_rsa.py --selftest
"""
from __future__ import annotations
import numpy as np
from scipy.stats import spearmanr
from scipy.spatial.distance import pdist


def _center_gram(K: np.ndarray) -> np.ndarray:
    n = K.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    return H @ K @ H


def _hsic(K: np.ndarray, L: np.ndarray) -> float:
    Kc, Lc = _center_gram(K), _center_gram(L)
    return float(np.sum(Kc * Lc))


def linear_cka(X: np.ndarray, Y: np.ndarray) -> float:
    """Linear CKA in [0, 1]; 1 = identical up to orthogonal transform + scale."""
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    K, L = X @ X.T, Y @ Y.T
    hkl = _hsic(K, L)
    hkk = _hsic(K, K)
    hll = _hsic(L, L)
    denom = np.sqrt(hkk * hll)
    return float(hkl / denom) if denom > 0 else 0.0


def _rbf_kernel(X: np.ndarray, sigma_scale: float = 1.0) -> np.ndarray:
    sq = np.sum(X ** 2, axis=1)
    d2 = np.clip(sq[:, None] + sq[None, :] - 2 * X @ X.T, 0, None)
    med = np.median(d2[d2 > 0]) if np.any(d2 > 0) else 1.0
    return np.exp(-d2 / (2.0 * sigma_scale * med + 1e-12))


def rbf_cka(X: np.ndarray, Y: np.ndarray, sigma_scale: float = 1.0) -> float:
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    K, L = _rbf_kernel(X, sigma_scale), _rbf_kernel(Y, sigma_scale)
    hkl, hkk, hll = _hsic(K, L), _hsic(K, K), _hsic(L, L)
    denom = np.sqrt(hkk * hll)
    return float(hkl / denom) if denom > 0 else 0.0


def rsa(X: np.ndarray, Y: np.ndarray, metric: str = "correlation") -> float:
    """Spearman correlation between the two RDMs (upper triangles)."""
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    dx = pdist(X, metric=metric)
    dy = pdist(Y, metric=metric)
    rho, _ = spearmanr(dx, dy)
    return float(rho)


def procrustes_disparity(X: np.ndarray, Y: np.ndarray) -> float:
    """Normalized orthogonal-Procrustes disparity in [0,1]; 0 = identical up to
    rotation/reflection/scale/translation. (scipy's M^2 statistic.)"""
    from scipy.spatial import procrustes
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    # procrustes needs equal columns; pad the narrower with zeros.
    p, q = X.shape[1], Y.shape[1]
    if p < q:
        X = np.pad(X, ((0, 0), (0, q - p)))
    elif q < p:
        Y = np.pad(Y, ((0, 0), (0, p - q)))
    _, _, disparity = procrustes(X, Y)
    return float(disparity)


def compare(X: np.ndarray, Y: np.ndarray) -> dict:
    return {
        "linear_cka": linear_cka(X, Y),
        "rbf_cka": rbf_cka(X, Y),
        "rsa_spearman": rsa(X, Y),
        "procrustes_disparity": procrustes_disparity(X, Y),
    }


# --------------------------------------------------------------------------- #
def _ortho(d: int, seed: int) -> np.ndarray:
    a = np.random.default_rng(seed).standard_normal((d, d))
    q, _ = np.linalg.qr(a)
    return q


def _selftest() -> None:
    rng = np.random.default_rng(0)
    ok = True
    n, d = 500, 40
    X = rng.standard_normal((n, d))

    # 1. Identity: all measures say "same".
    cond = (abs(linear_cka(X, X) - 1) < 1e-6 and abs(rbf_cka(X, X) - 1) < 1e-6
            and abs(rsa(X, X) - 1) < 1e-6 and procrustes_disparity(X, X) < 1e-6)
    print(f"[identity] cka={linear_cka(X, X):.4f} rsa={rsa(X, X):.4f} "
          f"proc={procrustes_disparity(X, X):.2e}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 2. Orthogonal-transform + scale invariance (the whole point).
    Q = _ortho(d, 1)
    XQ = 3.0 * (X @ Q)
    cond = (abs(linear_cka(X, XQ) - 1) < 1e-4
            and abs(rsa(X, XQ, metric='euclidean') - 1) < 1e-4
            and procrustes_disparity(X, XQ) < 1e-6)
    print(f"[orthogonal+scale invariant] cka={linear_cka(X, XQ):.4f} "
          f"rsa_euc={rsa(X, XQ, metric='euclidean'):.4f} "
          f"proc={procrustes_disparity(X, XQ):.2e}  "
          f"-> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 3. Independent random space: low similarity, high disparity.
    Z = rng.standard_normal((n, d))
    cond = linear_cka(X, Z) < 0.15 and abs(rsa(X, Z)) < 0.15 and procrustes_disparity(X, Z) > 0.8
    print(f"[independent] cka={linear_cka(X, Z):.4f} rsa={rsa(X, Z):.4f} "
          f"proc={procrustes_disparity(X, Z):.3f}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 4. Partial shared structure: shared signal + private noise -> intermediate.
    S = rng.standard_normal((n, d))
    A = S @ _ortho(d, 2) + 0.6 * rng.standard_normal((n, d))
    B = S @ _ortho(d, 3) + 0.6 * rng.standard_normal((n, d))
    c = linear_cka(A, B)
    cond = 0.2 < c < 0.95
    print(f"[partial shared] cka={c:.3f} (expect intermediate)  "
          f"-> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 5. Different feature dims still compare (n matched, p != q).
    Y2 = X @ rng.standard_normal((d, 17))     # project to 17 dims
    val = linear_cka(X, Y2)
    cond = 0.0 <= val <= 1.0
    print(f"[different dims p!=q] cka={val:.3f}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    print("ALL PASS" if ok else "SOME FAILED")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
