#!/usr/bin/env python3
"""
collapse_spectrum.py — diagnose representation collapse from the singular spectrum.

Collapse = the representation stops using its available capacity. Two flavors,
distinguished here (people routinely conflate them):

  complete collapse     embeddings are ~constant; almost no variance in any
                        direction. Total variance near zero. The encoder output
                        is (nearly) the same vector for every input.

  dimensional collapse  embeddings vary, but only inside a low-dimensional
                        subspace: the singular-value spectrum falls off a cliff
                        and the tail is ~0. Probe accuracy can still look fine,
                        yet nearest-neighbour discrimination and robustness
                        suffer (Jing et al. 2022, "Understanding dimensional
                        collapse in contrastive self-supervised learning").

This reports the normalized spectrum, a log-spectrum cliff locator, the variance
captured per #directions, and effective rank, then flags which collapse (if any)
is present. It does NOT "fix" anything — mitigations are a covariance/variance
term (VICReg), whitening, stronger/again-valid augmentations, or temperature.

Usage:
    from collapse_spectrum import diagnose
    diagnose(embeddings)                 # (n, d) array
    python collapse_spectrum.py --selftest
"""
from __future__ import annotations
import numpy as np


def singular_values(embeddings: np.ndarray, center: bool = True) -> np.ndarray:
    x = np.asarray(embeddings, dtype=np.float64)
    if center:
        x = x - x.mean(axis=0, keepdims=True)
    return np.linalg.svd(x, compute_uv=False)


def effective_rank(s: np.ndarray, eps: float = 1e-12) -> float:
    s = np.asarray(s, dtype=np.float64)
    s = s[s > eps]
    if s.size == 0:
        return 0.0
    p = s / s.sum()
    return float(np.exp(-np.sum(p * np.log(p))))


def variance_curve(s: np.ndarray) -> np.ndarray:
    """Cumulative fraction of variance vs #directions (variance ~ s^2)."""
    var = np.asarray(s, dtype=np.float64) ** 2
    if var.sum() == 0:
        return np.zeros_like(var)
    return np.cumsum(var) / var.sum()


def cliff_index(s: np.ndarray, drop_decades: float = 2.0) -> int | None:
    """First index where the singular value has dropped >= drop_decades orders
    of magnitude below the top one (the 'cliff'). None if no such cliff."""
    s = np.asarray(s, dtype=np.float64)
    if s.size == 0 or s[0] <= 0:
        return None
    log_ratio = np.log10(s[0]) - np.log10(np.clip(s, 1e-300, None))
    idx = np.argmax(log_ratio >= drop_decades)
    if log_ratio[idx] >= drop_decades:
        return int(idx)
    return None


def diagnose(embeddings: np.ndarray,
             complete_var_frac: float = 1e-3) -> dict:
    x = np.asarray(embeddings, dtype=np.float64)
    n, d = x.shape
    raw_scale = float(np.mean(np.var(x, axis=0)))          # before centering
    s = singular_values(x, center=True)
    total_var = float(np.sum(s ** 2))
    er = effective_rank(s)
    vc = variance_curve(s)
    dims99 = int(np.searchsorted(vc, 0.99) + 1) if vc.sum() > 0 else 0
    cliff = cliff_index(s)

    out = {
        "n": int(n),
        "nominal_dim": int(d),
        "mean_feature_variance": raw_scale,
        "effective_rank": er,
        "effective_rank_ratio": er / d,
        "dims_for_99pct_variance": dims99,
        "cliff_after_dim": cliff,
        "top5_normalized_singular_values":
            (s[:5] / s[0]).tolist() if s.size and s[0] > 0 else [],
    }

    flags = []
    # complete collapse: essentially no spread relative to the embedding scale.
    emb_scale = float(np.mean(np.linalg.norm(x, axis=1)) ** 2) + 1e-12
    if total_var / emb_scale < complete_var_frac:
        flags.append("COMPLETE COLLAPSE: embeddings are ~constant (variance ~0 "
                     "relative to their norm). The encoder is ignoring the "
                     "input. Check loss for a trivial solution; you likely need "
                     "negatives / an anti-collapse mechanism.")
    elif er / d < 0.1 or (cliff is not None and cliff < 0.1 * d):
        flags.append(f"DIMENSIONAL COLLAPSE: effective rank {er:.1f} of {d} "
                     f"(99% of variance in {dims99} dims). Probe accuracy may "
                     f"still look ok, but kNN/retrieval discrimination and "
                     f"robustness suffer. Mitigate with a covariance/variance "
                     f"term (VICReg), whitening, or augmentation/temperature.")
    out["flags"] = flags
    return out


# --------------------------------------------------------------------------- #
def _selftest() -> None:
    rng = np.random.default_rng(7)
    ok = True

    # 1. Healthy isotropic: effective rank ~ d, no flags.
    d = 128
    healthy = rng.standard_normal((5000, d))
    r = diagnose(healthy)
    cond = r["effective_rank_ratio"] > 0.85 and not r["flags"]
    print(f"[healthy] eff_rank_ratio={r['effective_rank_ratio']:.2f} "
          f"flags={r['flags']}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 2. Dimensional collapse: 4-dim signal in 128 dims.
    k = 4
    z = rng.standard_normal((5000, k)) @ rng.standard_normal((k, d))
    z = z + 1e-3 * rng.standard_normal((5000, d))
    r = diagnose(z)
    cond = (r["dims_for_99pct_variance"] <= k + 1
            and any("DIMENSIONAL COLLAPSE" in f for f in r["flags"])
            and r["cliff_after_dim"] is not None and r["cliff_after_dim"] <= k)
    print(f"[dim-collapse k={k}] dims@99%={r['dims_for_99pct_variance']} "
          f"cliff={r['cliff_after_dim']} flags={len(r['flags'])}  "
          f"-> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 3. Complete collapse: near-constant output.
    const = np.ones((5000, d)) * 3.0 + 1e-6 * rng.standard_normal((5000, d))
    r = diagnose(const)
    cond = any("COMPLETE COLLAPSE" in f for f in r["flags"])
    print(f"[complete-collapse] flags={r['flags'][:1]}  "
          f"-> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 4. Distinguishes the two: dim-collapse must NOT be tagged complete.
    cond = not any("COMPLETE COLLAPSE" in f for f in diagnose(z)["flags"])
    print(f"[no false complete-collapse on dim-collapse]  "
          f"-> {'PASS' if cond else 'FAIL'}")
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
