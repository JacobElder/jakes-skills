#!/usr/bin/env python3
"""
sample_entropy.py -- regularity / complexity "entropies" for TIME SERIES.

READ THIS FIRST. The functions here are NOT Shannon information theory, even
though they share the word "entropy." Sample entropy (SampEn), approximate
entropy (ApEn), and permutation entropy (PermEn) are *regularity statistics*
for an ordered sequence: they ask "how predictable is the next value given
recent history," not "how many bits does this distribution carry." They come
out of nonlinear-dynamics / physiological-signal analysis (Pincus 1991;
Richman & Moorman 2000; Bandt & Pompe 2002), a different intellectual lineage
from Shannon (1948). Do not average them with bits, do not feed them a
probability vector, and do not call np.log2 on them expecting "information."
For Shannon entropy / mutual information of a distribution, use
entropy_mi_estimators.py instead.

What they DO buy you: a single scalar summarizing how self-similar a trajectory
is. Regular/periodic signal -> low value. Noisy/complex signal -> high value.
Useful for HRV, EEG, behavioral streams, sensor data, regime/anomaly screens.

Conventions match antropy/standard practice so results are cross-checkable:
  - embedding dimension m (a.k.a. order), default 2
  - tolerance r, default 0.2 * std(x) with population std (ddof=0)
  - Chebyshev (max-coordinate) distance
  - SampEn excludes self-matches (the fix over ApEn's regularity bias)

Self-test cross-validates SampEn/ApEn/PermEn against `antropy` when installed,
and checks the qualitative law regular << random.

Run:  python3 sample_entropy.py --selftest
"""
from __future__ import annotations
import math
import numpy as np


# --------------------------------------------------------------------------
# Embedding helper
# --------------------------------------------------------------------------
def _embed(x: np.ndarray, m: int) -> np.ndarray:
    """Return the (N-m+1, m) matrix of length-m delay vectors (delay=1)."""
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    if N < m + 1:
        raise ValueError(f"series length {N} too short for embedding dim {m}")
    idx = np.arange(N - m + 1)[:, None] + np.arange(m)[None, :]
    return x[idx]


def _phi_count(x: np.ndarray, m: int, r: float, exclude_self: bool) -> float:
    """
    Average number of templates within Chebyshev distance r of each template.

    exclude_self=True  -> SampEn-style counting (no i==j), denominator (Nm-1).
    exclude_self=False -> ApEn-style counting   (include i==j), denominator Nm.
    Returns the *average match fraction* (a number in (0, 1]).
    """
    V = _embed(x, m)                      # (Nm, m)
    Nm = V.shape[0]
    # Chebyshev distance matrix via broadcasting; fine for educational N (<~5000).
    # For large N, replace with a KD-tree (sklearn KDTree, metric='chebyshev').
    d = np.max(np.abs(V[:, None, :] - V[None, :, :]), axis=2)  # (Nm, Nm)
    within = d <= r
    if exclude_self:
        np.fill_diagonal(within, False)
        counts = within.sum(axis=1)
        # average over templates that have the *potential* for Nm-1 neighbors
        return np.mean(counts / (Nm - 1))
    else:
        counts = within.sum(axis=1)       # includes self
        return np.mean(counts / Nm)


# --------------------------------------------------------------------------
# Sample entropy (Richman & Moorman 2000)
# --------------------------------------------------------------------------
def sample_entropy(x, m: int = 2, tolerance: float | None = None,
                   r_factor: float = 0.2) -> float:
    """
    SampEn = -ln( A / B ), where
      B = number of template pairs (i != j) matching within r at length m,
      A = number matching within r at length m+1.
    Self-matches excluded (this is the key difference from ApEn). Higher =
    more complex/irregular; ~0 = highly regular. Returns +inf if A == 0
    (no longer-template matches at this r -- raise r or lengthen the series).
    """
    x = np.asarray(x, dtype=float)
    if tolerance is None:
        tolerance = r_factor * np.std(x)  # population std, ddof=0
    if tolerance <= 0:
        raise ValueError("tolerance must be > 0 (is the series constant?)")
    # Use the matched-count form so A and B share the same i,j universe.
    V_m = _embed(x, m)
    V_m1 = _embed(x, m + 1)
    Nm1 = V_m1.shape[0]            # = N - m ; align both lengths to this
    Vm = V_m[:Nm1]                # truncate length-m set to match m+1 set

    dm = np.max(np.abs(Vm[:, None, :] - Vm[None, :, :]), axis=2)
    dm1 = np.max(np.abs(V_m1[:, None, :] - V_m1[None, :, :]), axis=2)
    np.fill_diagonal(dm, np.inf)
    np.fill_diagonal(dm1, np.inf)
    B = np.sum(dm <= tolerance)
    A = np.sum(dm1 <= tolerance)
    if B == 0:
        return np.inf
    if A == 0:
        return np.inf
    return -np.log(A / B)


# --------------------------------------------------------------------------
# Approximate entropy (Pincus 1991) -- included mostly to show its bias
# --------------------------------------------------------------------------
def approximate_entropy(x, m: int = 2, tolerance: float | None = None,
                        r_factor: float = 0.2) -> float:
    """
    ApEn = phi(m) - phi(m+1), with phi the mean of ln(match-fraction) and
    self-matches INCLUDED. The self-match inclusion biases ApEn toward calling
    signals more regular than they are, especially for short series; SampEn was
    designed to remove exactly this bias. Provided for comparison only.
    """
    x = np.asarray(x, dtype=float)
    if tolerance is None:
        tolerance = r_factor * np.std(x)
    if tolerance <= 0:
        raise ValueError("tolerance must be > 0 (is the series constant?)")

    def _phi(mm: int) -> float:
        V = _embed(x, mm)
        Nm = V.shape[0]
        d = np.max(np.abs(V[:, None, :] - V[None, :, :]), axis=2)
        C = (d <= tolerance).sum(axis=1) / Nm   # includes self-match
        return np.mean(np.log(C))

    return _phi(m) - _phi(m + 1)


# --------------------------------------------------------------------------
# Permutation entropy (Bandt & Pompe 2002) -- a Shannon entropy of ordinal
# patterns. This one IS a Shannon entropy, but of motif frequencies, so it
# lives here with its time-series cousins rather than in the distribution code.
# --------------------------------------------------------------------------
def permutation_entropy(x, order: int = 3, delay: int = 1,
                        normalize: bool = True) -> float:
    """
    Shannon entropy (in bits) of the distribution of ordinal patterns (the
    argsort motif) of length `order`. Captures temporal ordering structure that
    a value-shuffled Shannon entropy would miss. normalize divides by
    log2(order!) so the result lands in [0, 1].
    """
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    n_vec = N - (order - 1) * delay
    if n_vec <= 0:
        raise ValueError("series too short for this order/delay")
    idx = np.arange(n_vec)[:, None] + np.arange(0, order * delay, delay)[None, :]
    patterns = np.argsort(x[idx], axis=1)
    # hash each ordinal pattern to an integer key
    mult = (order ** np.arange(order))
    keys = patterns @ mult
    _, counts = np.unique(keys, return_counts=True)
    p = counts / counts.sum()
    H = -np.sum(p * np.log2(p))
    if normalize:
        H = H / np.log2(math.factorial(order))
    return H


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------
def _selftest() -> None:
    rng = np.random.default_rng(7)

    print("=" * 70)
    print("sample_entropy.py self-test")
    print("=" * 70)

    # Three signals: periodic (regular), AR(1) (some structure), white noise.
    t = np.arange(600)
    periodic = np.sin(2 * np.pi * t / 12)
    noise = rng.standard_normal(600)
    ar = np.zeros(600)
    for i in range(1, 600):
        ar[i] = 0.85 * ar[i - 1] + rng.standard_normal()

    print("\n[1] Qualitative law: regular << structured < random (SampEn, m=2)")
    se_p = sample_entropy(periodic, m=2)
    se_a = sample_entropy(ar, m=2)
    se_n = sample_entropy(noise, m=2)
    print(f"    periodic sine : SampEn = {se_p:.4f}")
    print(f"    AR(1) phi=.85 : SampEn = {se_a:.4f}")
    print(f"    white noise   : SampEn = {se_n:.4f}")
    assert se_p < se_a < se_n, "ordering violated"
    print("    OK: periodic < AR(1) < white noise")

    print("\n[2] ApEn is biased LOW vs SampEn on the same noise (self-matches)")
    ap_n = approximate_entropy(noise, m=2)
    print(f"    white noise   : ApEn = {ap_n:.4f}  SampEn = {se_n:.4f}")
    assert ap_n < se_n, "expected ApEn < SampEn here"
    print("    OK: ApEn < SampEn (self-match regularity bias visible)")

    print("\n[3] Permutation entropy: periodic ~0, noise ~1 (normalized, order=3)")
    pe_p = permutation_entropy(periodic, order=3, normalize=True)
    pe_n = permutation_entropy(noise, order=3, normalize=True)
    print(f"    periodic sine : PermEn = {pe_p:.4f}")
    print(f"    white noise   : PermEn = {pe_n:.4f}")
    assert pe_p < pe_n and pe_n > 0.95, "perm-entropy ordering/scale off"
    print("    OK: periodic < noise, noise saturates near 1")

    # Cross-validation against antropy, if available.
    print("\n[4] Cross-validate against antropy (if installed)")
    try:
        import antropy as ant
        for name, sig in [("periodic", periodic), ("ar", ar), ("noise", noise)]:
            se_mine = sample_entropy(sig, m=2)
            se_ant = ant.sample_entropy(sig, order=2)
            ap_mine = approximate_entropy(sig, m=2)
            ap_ant = ant.app_entropy(sig, order=2)
            pe_mine = permutation_entropy(sig, order=3, normalize=True)
            pe_ant = ant.perm_entropy(sig, order=3, normalize=True)
            print(f"    {name:8s} SampEn mine={se_mine:.4f} antropy={se_ant:.4f} "
                  f"| ApEn mine={ap_mine:.4f} antropy={ap_ant:.4f} "
                  f"| PermEn mine={pe_mine:.4f} antropy={pe_ant:.4f}")
            assert abs(se_mine - se_ant) < 1e-6, f"SampEn mismatch on {name}"
            assert abs(ap_mine - ap_ant) < 1e-6, f"ApEn mismatch on {name}"
            # PermEn can differ at ~1e-3 on signals with EXACT tied values
            # (argsort tie-break convention); identical when there are no ties.
            assert abs(pe_mine - pe_ant) < 5e-3, f"PermEn mismatch on {name}"
        print("    OK: SampEn/ApEn match antropy to <1e-6; PermEn to <5e-3 (ties)")
    except ImportError:
        print("    antropy not installed; skipped external cross-check")

    print("\nAll sample_entropy.py self-tests passed.")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
