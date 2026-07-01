#!/usr/bin/env python3
"""
anisotropy_effective_rank.py — is your embedding space degenerate?

Two cheap, intrinsic diagnostics you should run before trusting cosine numbers
or claiming a space is "rich":

  anisotropy        mean cosine similarity between random pairs of embeddings.
                    ~0 is isotropic (healthy). High (e.g. >0.3) means the
                    vectors live in a narrow cone, so ALL cosines are inflated
                    and compressed -- the classic raw-BERT/contextual-LM
                    pathology (Ethayarajh 2019, "Contextual embeddings:
                    anisotropy and ...").  Fixes: mean-centering, whitening, or
                    a contrastively-trained sentence model. Changing the
                    distance metric does NOT fix a cone.

  effective_rank    how many dimensions the space actually uses. Two standard
                    flavors:
                      - Roy-Vetterli (2007) effective rank = exp(H) where H is
                        the Shannon entropy of the L1-normalized SINGULAR values.
                      - participation ratio = (sum s_i^2)^2 / sum s_i^4 of the
                        singular values (a.k.a. of covariance eigenvalues).
                    Both collapse toward a small number when the embeddings
                    occupy a low-dimensional subspace (dimensional collapse),
                    even while nominal dim stays large.

Closed-form cross-check used in --selftest: for unit vectors u_i = x_i/||x_i||,
E_{i!=j}[u_i . u_j] = ||mean_i u_i||^2, so the sampled mean pairwise cosine must
match the squared norm of the mean unit vector. We assert this holds.

Usage:
    from anisotropy_effective_rank import diagnose
    print(diagnose(embeddings))            # embeddings: (n, d) array
    python anisotropy_effective_rank.py --selftest
"""
from __future__ import annotations
import numpy as np


def _unit(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)


def anisotropy(embeddings: np.ndarray, n_pairs: int = 100_000,
               seed: int = 0) -> float:
    """Mean cosine similarity between random distinct pairs (~0 = isotropic)."""
    x = np.asarray(embeddings, dtype=np.float64)
    n = x.shape[0]
    if n < 2:
        raise ValueError("need >= 2 embeddings")
    u = _unit(x)
    rng = np.random.default_rng(seed)
    i = rng.integers(0, n, size=n_pairs)
    j = rng.integers(0, n, size=n_pairs)
    mask = i != j
    i, j = i[mask], j[mask]
    return float(np.mean(np.sum(u[i] * u[j], axis=1)))


def anisotropy_closed_form(embeddings: np.ndarray) -> float:
    """||mean unit vector||^2 == E_{i!=j}[cos] in expectation. Exact, O(nd)."""
    u = _unit(np.asarray(embeddings, dtype=np.float64))
    return float(np.sum(u.mean(axis=0) ** 2))


def singular_values(embeddings: np.ndarray, center: bool = True) -> np.ndarray:
    x = np.asarray(embeddings, dtype=np.float64)
    if center:
        x = x - x.mean(axis=0, keepdims=True)
    return np.linalg.svd(x, compute_uv=False)


def effective_rank_entropy(s: np.ndarray, eps: float = 1e-12) -> float:
    """Roy-Vetterli effective rank = exp(entropy of normalized singular values)."""
    s = np.asarray(s, dtype=np.float64)
    s = s[s > eps]
    if s.size == 0:
        return 0.0
    p = s / s.sum()
    H = -np.sum(p * np.log(p))
    return float(np.exp(H))


def participation_ratio(s: np.ndarray, eps: float = 1e-12) -> float:
    """(sum s^2)^2 / sum s^4  — soft count of dominant directions."""
    s = np.asarray(s, dtype=np.float64)
    s2 = s ** 2
    denom = np.sum(s2 ** 2)
    if denom < eps:
        return 0.0
    return float(np.sum(s2) ** 2 / denom)


def dims_for_variance(s: np.ndarray, thresholds=(0.90, 0.95, 0.99)) -> dict:
    """Smallest #singular-directions covering each fraction of total variance."""
    var = (np.asarray(s, dtype=np.float64) ** 2)
    if var.sum() == 0:
        return {t: 0 for t in thresholds}
    cum = np.cumsum(var) / var.sum()
    return {t: int(np.searchsorted(cum, t) + 1) for t in thresholds}


def diagnose(embeddings: np.ndarray, n_pairs: int = 100_000,
             seed: int = 0) -> dict:
    x = np.asarray(embeddings, dtype=np.float64)
    s = singular_values(x, center=True)
    nominal = x.shape[1]
    er = effective_rank_entropy(s)
    out = {
        "n": int(x.shape[0]),
        "nominal_dim": int(nominal),
        "anisotropy_sampled": anisotropy(x, n_pairs=n_pairs, seed=seed),
        "anisotropy_closed_form": anisotropy_closed_form(x),
        "effective_rank_entropy": er,
        "effective_rank_ratio": er / nominal,
        "participation_ratio": participation_ratio(s),
        "dims_for_variance": dims_for_variance(s),
    }
    flags = []
    if out["anisotropy_closed_form"] > 0.3:
        flags.append("HIGH ANISOTROPY: cosines inflated/compressed; center or "
                     "whiten, or use a contrastive sentence model. A different "
                     "distance metric will NOT fix this.")
    if out["effective_rank_ratio"] < 0.1:
        flags.append("LIKELY DIMENSIONAL COLLAPSE: effective rank << nominal "
                     "dim; space wastes capacity (can hurt retrieval). Check a "
                     "decorrelation term (VICReg), whitening, or augmentations.")
    out["flags"] = flags
    return out


# --------------------------------------------------------------------------- #
def _selftest() -> None:
    rng = np.random.default_rng(42)
    ok = True

    # 1. Isotropic Gaussian: anisotropy ~ 0, effective rank ~ d.
    d = 64
    x = rng.standard_normal((4000, d))
    r = diagnose(x, seed=1)
    cond = abs(r["anisotropy_closed_form"]) < 0.02 and r["effective_rank_entropy"] > 0.85 * d
    print(f"[isotropic d={d}] anisotropy={r['anisotropy_closed_form']:.4f} "
          f"eff_rank={r['effective_rank_entropy']:.1f}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 2. Sampled anisotropy must match the closed form ||mean unit vec||^2.
    diff = abs(r["anisotropy_sampled"] - r["anisotropy_closed_form"])
    cond = diff < 0.01
    print(f"[sampled==closed-form] |diff|={diff:.4f}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 3. Anisotropic cone: add a large shared offset -> high anisotropy.
    cone = rng.standard_normal((4000, d)) + np.r_[16.0, np.zeros(d - 1)]
    rc = diagnose(cone, seed=2)
    cond = rc["anisotropy_closed_form"] > 0.6 and len(rc["flags"]) >= 1
    print(f"[cone] anisotropy={rc['anisotropy_closed_form']:.3f} "
          f"flags={len(rc['flags'])}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 4. Dimensional collapse: 5-dim signal embedded in 256 dims.
    k = 5
    z = rng.standard_normal((4000, k))
    W = rng.standard_normal((k, 256))
    collapsed = z @ W + 1e-3 * rng.standard_normal((4000, 256))
    rk = diagnose(collapsed, seed=3)
    cond = abs(rk["effective_rank_entropy"] - k) < 1.0 and rk["dims_for_variance"][0.99] <= k + 1
    print(f"[collapse k={k}] eff_rank={rk['effective_rank_entropy']:.2f} "
          f"dims@99%={rk['dims_for_variance'][0.99]}  -> {'PASS' if cond else 'FAIL'}")
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
