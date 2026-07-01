#!/usr/bin/env python3
"""
alignment_uniformity.py — localize WHY a contrastive embedding is good or bad.

Wang & Isola (2020), "Understanding Contrastive Representation Learning through
Alignment and Uniformity on the Hypersphere." Two scalars, both LOWER = better,
computed on L2-NORMALIZED embeddings:

  alignment    = E_{(x,x+)} || f(x) - f(x+) ||^2
                 over POSITIVE pairs. Measures whether positives land close.
                 0 = positives map to identical points.

  uniformity   = log E_{x,y} exp( -t || f(x) - f(y) ||^2 )
                 over random pairs (default t=2). Measures how evenly the
                 embeddings cover the unit sphere. Very negative = spread out;
                 high (less negative) = clumped.

Why both: a collapsed encoder (everything to one point) has PERFECT alignment
(0) but terrible uniformity. A random encoder may be uniform but unaligned.
Tracking the two separately tells you which failure you have -- a single
"contrastive loss went down" number can't.

For unit vectors, || f(x)-f(y) ||^2 = 2 - 2 cos, so these are functions of the
cosine geometry. We normalize to the sphere by default.

Usage:
    from alignment_uniformity import alignment, uniformity, diagnose
    alignment(z_anchor, z_positive)      # paired rows, (m, d) each
    uniformity(z_all)                    # (n, d)
    python alignment_uniformity.py --selftest
"""
from __future__ import annotations
import numpy as np


def _unit(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)


def alignment(z_anchor: np.ndarray, z_positive: np.ndarray,
              alpha: float = 2.0, normalize: bool = True) -> float:
    """Mean ||a - p||^alpha over positive pairs (alpha=2 is the standard)."""
    a = _unit(z_anchor) if normalize else np.asarray(z_anchor, dtype=np.float64)
    p = _unit(z_positive) if normalize else np.asarray(z_positive, dtype=np.float64)
    if a.shape != p.shape:
        raise ValueError("anchor and positive must be paired, same shape")
    d2 = np.sum((a - p) ** 2, axis=1)
    return float(np.mean(d2 ** (alpha / 2.0)))


def uniformity(z: np.ndarray, t: float = 2.0, normalize: bool = True,
               max_n: int = 4096, seed: int = 0) -> float:
    """log E exp(-t ||x - y||^2) over random pairs (subsampled for O(n^2))."""
    x = _unit(z) if normalize else np.asarray(z, dtype=np.float64)
    n = x.shape[0]
    if n > max_n:
        idx = np.random.default_rng(seed).choice(n, size=max_n, replace=False)
        x = x[idx]
    # pairwise squared distances, exclude the diagonal.
    sq = np.sum(x ** 2, axis=1)
    d2 = sq[:, None] + sq[None, :] - 2.0 * (x @ x.T)
    np.fill_diagonal(d2, np.nan)
    d2 = np.clip(d2, 0.0, None)
    vals = np.exp(-t * d2)
    mean = np.nanmean(vals)
    return float(np.log(mean + 1e-12))


def diagnose(z_anchor: np.ndarray, z_positive: np.ndarray,
             t: float = 2.0) -> dict:
    al = alignment(z_anchor, z_positive)
    # uniformity over the union of both views.
    uni = uniformity(np.vstack([z_anchor, z_positive]), t=t)
    out = {"alignment": al, "uniformity": uni, "t": t}
    flags = []
    if uni > -0.5:
        flags.append("POOR UNIFORMITY: embeddings are clumped/anisotropic; "
                     "combined with low alignment this signals (near-)collapse. "
                     "Check the singular spectrum (collapse_spectrum.py).")
    if al < 1e-4 and uni > -0.5:
        flags.append("COLLAPSE SIGNATURE: ~perfect alignment WITH poor "
                     "uniformity = everything mapped near one point.")
    out["flags"] = flags
    return out


# --------------------------------------------------------------------------- #
def _selftest() -> None:
    rng = np.random.default_rng(0)
    ok = True

    # Uniform-on-sphere reference. For d-dim uniform on the sphere, uniformity
    # is finite and clearly negative; a single collapsed point is ~0.
    d = 32
    sphere = _unit(rng.standard_normal((4000, d)))
    u_uniform = uniformity(sphere)
    collapsed = np.tile(_unit(rng.standard_normal((1, d))), (4000, 1))
    u_collapsed = uniformity(collapsed)
    cond = u_uniform < -1.0 and u_collapsed > -0.01
    print(f"[uniformity] uniform={u_uniform:.3f}  collapsed={u_collapsed:.3f}  "
          f"-> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # Alignment: identical positives -> 0; random positives -> ~2 (mean ||.||^2
    # for two independent unit vectors = E[2 - 2cos] = 2).
    anchors = _unit(rng.standard_normal((4000, d)))
    al_perfect = alignment(anchors, anchors)
    al_random = alignment(anchors, _unit(rng.standard_normal((4000, d))))
    cond = al_perfect < 1e-9 and abs(al_random - 2.0) < 0.1
    print(f"[alignment] identical={al_perfect:.2e}  random={al_random:.3f} "
          f"(expect ~2)  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # Good embedding: tight positives + spread anchors -> low align, low unif.
    base = _unit(rng.standard_normal((4000, d)))
    pos = _unit(base + 0.05 * rng.standard_normal((4000, d)))
    g = diagnose(base, pos)
    cond = g["alignment"] < 0.12 and g["uniformity"] < -1.0 and not g["flags"]
    print(f"[good embedding] align={g['alignment']:.3f} unif={g['uniformity']:.3f} "
          f"flags={g['flags']}  -> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # Collapse signature: positives identical AND everything near one point.
    c = diagnose(collapsed, collapsed)
    cond = any("COLLAPSE SIGNATURE" in f for f in c["flags"])
    print(f"[collapse signature] flags={c['flags'][:1]}  "
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
