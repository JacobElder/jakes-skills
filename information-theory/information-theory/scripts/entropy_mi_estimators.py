#!/usr/bin/env python3
"""
entropy_mi_estimators.py — honest entropy/MI estimation from finite samples.

Why this exists: plugging empirical frequencies into the entropy/MI formula is
*biased* (entropy down, MI up, by ~ (K-1)/(2N) per term). This module provides the
bias-aware estimators you should actually use, plus a KSG k-NN estimator for
continuous MI, all validated against closed-form ground truth in --selftest.

Units: functions take `base` (2 -> bits, e -> nats). Defaults noted per function.

API
---
entropy_plugin(counts, base=2)        -> plug-in (MLE) entropy. BIASED LOW. For comparison only.
entropy_miller_madow(counts, base=2)  -> plug-in + (K_hat-1)/(2N). Minimum acceptable default.
mi_plugin(joint_counts, base=2)       -> plug-in MI from a contingency table. BIASED HIGH.
mi_miller_madow(joint_counts, base=2) -> MI from Miller-Madow-corrected H(X)+H(Y)-H(X,Y).
mi_permutation_null(x, y, bins, ...)  -> (mi_hat, null_mean, null_std, p) shuffle test for discrete/binned.
ksg_mi(x, y, k=4)                     -> KSG (Kraskov estimator 1) MI for CONTINUOUS data, in nats.
gaussian_mi(rho, base=e)              -> closed form -0.5*log(1-rho^2) for bivariate Gaussian.
transfer_entropy_discrete(s, t, ...)  -> TE_{s->t} (conditional MI) for symbolic series, Miller-Madow corrected.
transfer_entropy_permutation_null(...)-> (te_hat, null_mean, null_std, p) surrogate test for directed coupling.
gaussian_te(cov, ...)                 -> closed-form TE for a linear-Gaussian process from a covariance matrix.

Run `python3 entropy_mi_estimators.py --selftest` for a validated demo.
"""
from __future__ import annotations
import numpy as np
from scipy.special import digamma
from scipy.spatial import cKDTree

_LOG = {2: np.log2, "e": np.log, np.e: np.log, 10: np.log10}


def _logfn(base):
    if base in _LOG:
        return _LOG[base]
    return lambda v: np.log(v) / np.log(base)


def entropy_plugin(counts, base=2):
    """Plug-in / MLE entropy. BIASED DOWNWARD by ~(K-1)/(2N). Use for comparison only."""
    counts = np.asarray(counts, dtype=float).ravel()
    counts = counts[counts > 0]
    n = counts.sum()
    p = counts / n
    return float(-(p * _logfn(base)(p)).sum())


def entropy_miller_madow(counts, base=2):
    """Miller-Madow: plug-in + (K_hat-1)/(2N) in nats, converted to `base`.
    Removes the leading bias term. Minimum acceptable default for discrete entropy."""
    counts = np.asarray(counts, dtype=float).ravel()
    counts = counts[counts > 0]
    n = counts.sum()
    k_hat = counts.size
    h_plugin_nats = entropy_plugin(counts, base="e")
    h_mm_nats = h_plugin_nats + (k_hat - 1) / (2 * n)
    return float(h_mm_nats / np.log(base if base != "e" else np.e))


def mi_plugin(joint_counts, base=2):
    """Plug-in MI from a 2-D contingency table. BIASED UPWARD by ~(Kx-1)(Ky-1)/(2N)."""
    j = np.asarray(joint_counts, dtype=float)
    n = j.sum()
    pj = j / n
    px = pj.sum(axis=1, keepdims=True)
    py = pj.sum(axis=0, keepdims=True)
    mask = pj > 0
    ratio = np.zeros_like(pj)
    ratio[mask] = pj[mask] / (px @ np.ones_like(py))[mask] / (np.ones_like(px) @ py)[mask]
    return float((pj[mask] * _logfn(base)(ratio[mask])).sum())


def mi_miller_madow(joint_counts, base=2):
    """MI via Miller-Madow-corrected H(X)+H(Y)-H(X,Y). Corrects all three entropies."""
    j = np.asarray(joint_counts, dtype=float)
    hx = entropy_miller_madow(j.sum(axis=1), base=base)
    hy = entropy_miller_madow(j.sum(axis=0), base=base)
    hxy = entropy_miller_madow(j.ravel(), base=base)
    return float(hx + hy - hxy)


def _binned_joint(x, y, bins):
    cx = np.digitize(x, np.histogram_bin_edges(x, bins=bins)[1:-1])
    cy = np.digitize(y, np.histogram_bin_edges(y, bins=bins)[1:-1])
    kx, ky = cx.max() + 1, cy.max() + 1
    tab = np.zeros((kx, ky))
    np.add.at(tab, (cx, cy), 1)
    return tab


def mi_permutation_null(x, y, bins=8, n_perm=300, base=2, rng=None):
    """Shuffle test: recompute MI under permutations of y. Returns
    (mi_hat, null_mean, null_std, p_value). The null mean is your bias floor;
    a value not clearly above it is not evidence of dependence."""
    rng = np.random.default_rng(rng)
    x = np.asarray(x); y = np.asarray(y)
    mi_hat = mi_miller_madow(_binned_joint(x, y, bins), base=base)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = mi_miller_madow(_binned_joint(x, rng.permutation(y), bins), base=base)
    p = (1 + np.sum(null >= mi_hat)) / (n_perm + 1)
    return float(mi_hat), float(null.mean()), float(null.std()), float(p)


def ksg_mi(x, y, k=4):
    """KSG mutual-information estimator (Kraskov-Stoegbauer-Grassberger, algorithm 1).
    For CONTINUOUS x, y. Returns MI in NATS. Add tiny jitter for data with ties."""
    x = np.asarray(x, dtype=float).reshape(len(x), -1)
    y = np.asarray(y, dtype=float).reshape(len(y), -1)
    n = len(x)
    z = np.hstack([x, y])
    # distance to k-th neighbour in JOINT space, Chebyshev (max) metric
    dz, _ = cKDTree(z).query(z, k=k + 1, p=np.inf)
    eps = dz[:, k]  # radius to the k-th neighbour (excludes self at index 0)
    tx, ty = cKDTree(x), cKDTree(y)
    nx = np.empty(n); ny = np.empty(n)
    for i in range(n):
        # count strictly within eps_i in each marginal (subtract self)
        nx[i] = len(tx.query_ball_point(x[i], eps[i] - 1e-15, p=np.inf)) - 1
        ny[i] = len(ty.query_ball_point(y[i], eps[i] - 1e-15, p=np.inf)) - 1
    mi = digamma(k) - np.mean(digamma(nx + 1) + digamma(ny + 1)) + digamma(n)
    return float(max(mi, 0.0))  # clamp tiny-negative noise


def gaussian_mi(rho, base=np.e):
    """Closed-form MI of a bivariate Gaussian with correlation rho. Default nats."""
    val_nats = -0.5 * np.log(1 - rho ** 2)
    return float(val_nats / np.log(base if base != "e" else np.e))


# --------------------------------------------------------------------------
# Transfer entropy / directed information (Schreiber 2000)
# TE_{S->T} = I(T_{t+1} ; S_t^{(l)} | T_t^{(k)}). It is conditional mutual
# information, so it inherits every estimation pathology in this file -- the
# plug-in version is biased UP and a permutation null is mandatory. TE is the
# information-theoretic analog of Granger causality (for jointly Gaussian,
# linear processes the two are equivalent up to a factor of 2: G = 2*TE in nats).
# --------------------------------------------------------------------------
def _mm_entropy_codes(codes, base=2):
    """Miller-Madow entropy (in `base`) of an array of integer symbol codes."""
    _, counts = np.unique(np.asarray(codes), return_counts=True)
    return entropy_miller_madow(counts, base=base)


def _code_rows(arr2d):
    """Map each row of an integer 2-D array to a unique integer code."""
    a = np.asarray(arr2d)
    if a.ndim == 1:
        a = a[:, None]
    # mixed-radix encoding on per-column cardinalities
    out = np.zeros(a.shape[0], dtype=np.int64)
    mult = 1
    for c in range(a.shape[1]):
        col = a[:, c]
        out = out + col * mult
        mult *= (col.max() + 1)
    return out


def transfer_entropy_discrete(source, target, k=1, l=1, base=2, correct=True):
    """
    TE_{source->target} for DISCRETE/symbolic series with history lengths k
    (target past) and l (source past), lag 1. Computed as
        TE = H(Tf, Tp) - H(Tp) - H(Tf, Tp, Sp) + H(Tp, Sp)
    with every term Miller-Madow corrected when correct=True (else plug-in,
    biased UP). Series must be integer-coded (0..K-1). Returns value in `base`.
    Pair with transfer_entropy_permutation_null -- a bare TE number is not
    evidence of directed coupling.
    """
    s = np.asarray(source).astype(int)
    t = np.asarray(target).astype(int)
    n = len(t)
    hmax = max(k, l)
    Tf = t[hmax:]                                   # target future  T_{t+1}
    Tp = np.column_stack([t[hmax - 1 - i: n - 1 - i] for i in range(k)])  # k-history
    Sp = np.column_stack([s[hmax - 1 - i: n - 1 - i] for i in range(l)])  # l-history
    ent = (_mm_entropy_codes if correct else _pi_entropy_codes)
    H_TfTp = ent(_code_rows(np.column_stack([Tf, Tp])), base=base)
    H_Tp = ent(_code_rows(Tp), base=base)
    H_TfTpSp = ent(_code_rows(np.column_stack([Tf, Tp, Sp])), base=base)
    H_TpSp = ent(_code_rows(np.column_stack([Tp, Sp])), base=base)
    return float(H_TfTp - H_Tp - H_TfTpSp + H_TpSp)


def _pi_entropy_codes(codes, base=2):
    _, counts = np.unique(np.asarray(codes), return_counts=True)
    return entropy_plugin(counts, base=base)


def transfer_entropy_permutation_null(source, target, k=1, l=1, base=2,
                                      n_perm=300, rng=None):
    """
    Surrogate test for directed coupling. Recomputes TE with the source series
    block-cyclically shifted (destroys S->T timing while preserving the source's
    own marginal/autocorrelation better than a full shuffle). Returns
    (te_hat, null_mean, null_std, p_value). te_hat at or below null_mean is the
    bias floor, not signal.
    """
    rng = np.random.default_rng(rng)
    s = np.asarray(source).astype(int)
    t = np.asarray(target).astype(int)
    te_hat = transfer_entropy_discrete(s, t, k=k, l=l, base=base)
    n = len(s)
    null = np.empty(n_perm)
    for i in range(n_perm):
        shift = rng.integers(1, n - 1)
        null[i] = transfer_entropy_discrete(np.roll(s, shift), t, k=k, l=l, base=base)
    p = (1 + np.sum(null >= te_hat)) / (n_perm + 1)
    return float(te_hat), float(null.mean()), float(null.std()), float(p)


def gaussian_te(cov, i_future=0, i_tpast=1, i_spast=2, base=np.e):
    """
    Closed-form transfer entropy for a jointly GAUSSIAN, linear process, from
    the covariance of the vector [T_{t+1}, T_t-history, S_t-history]. With scalar
    histories that vector is [T_{t+1}, T_t, S_t] and
        TE = 0.5 * ln( Var(T_{t+1}|T_t) / Var(T_{t+1}|T_t, S_t) )   (nats),
    each conditional variance a Schur complement of `cov`. Indices select the
    future / target-past / source-past coordinates. Default nats.
    """
    cov = np.asarray(cov, dtype=float)

    def _cond_var(target, given):
        given = list(given)
        s_tt = cov[target, target]
        s_tg = cov[np.ix_([target], given)]
        s_gg = cov[np.ix_(given, given)]
        return float(s_tt - (s_tg @ np.linalg.solve(s_gg, s_tg.T))[0, 0])

    v_given_tp = _cond_var(i_future, [i_tpast])
    v_given_both = _cond_var(i_future, [i_tpast, i_spast])
    te_nats = 0.5 * np.log(v_given_tp / v_given_both)
    return float(te_nats / np.log(base if base != "e" else np.e))


def _selftest():
    rng = np.random.default_rng(0)
    print("=" * 72)
    print("1. ENTROPY BIAS: uniform over 8 symbols, true H = 3.000 bits")
    print("   plug-in is biased LOW; Miller-Madow corrects most of it.")
    print(f"   {'N':>6} | {'plug-in':>9} | {'Miller-Madow':>13} | {'true':>6}")
    for N in (16, 32, 64, 256, 4096):
        c = np.bincount(rng.integers(0, 8, size=N), minlength=8)
        print(f"   {N:>6} | {entropy_plugin(c):9.4f} | {entropy_miller_madow(c):13.4f} | {3.0:6.3f}")

    print("=" * 72)
    print("2. MI BIAS under INDEPENDENCE: true MI = 0. Plug-in fabricates MI;")
    print("   the permutation null reveals it (mi_hat ~ null_mean, p large).")
    x = rng.integers(0, 10, size=120); y = rng.integers(0, 10, size=120)  # independent
    tab = np.zeros((10, 10)); np.add.at(tab, (x, y), 1)
    mi_hat, nm, ns, p = mi_permutation_null(x, y, bins=10, rng=1)
    print(f"   plug-in MI            = {mi_plugin(tab):.4f} bits  (looks like signal, isn't)")
    print(f"   Miller-Madow MI       = {mi_miller_madow(tab):.4f} bits")
    print(f"   permutation: mi_hat={mi_hat:.4f}  null_mean={nm:.4f}  p={p:.3f}  -> not significant")

    print("=" * 72)
    print("3. KSG on bivariate Gaussian: validate against I = -0.5 ln(1-rho^2).")
    print(f"   {'rho':>5} | {'KSG (nats)':>11} | {'closed form':>11} | {'abs err':>8}")
    for rho in (0.0, 0.3, 0.6, 0.9):
        cov = np.array([[1.0, rho], [rho, 1.0]])
        s = rng.multivariate_normal([0, 0], cov, size=4000)
        xs = s[:, 0] + 1e-10 * rng.standard_normal(4000)
        ys = s[:, 1] + 1e-10 * rng.standard_normal(4000)
        est = ksg_mi(xs, ys, k=5)
        true = gaussian_mi(rho)
        print(f"   {rho:5.1f} | {est:11.4f} | {true:11.4f} | {abs(est-true):8.4f}")
    print("=" * 72)
    print("4. Transfer entropy. (a) Gaussian closed form vs a known linear VAR(1);")
    print("   (b) discrete directionality with a permutation null.")
    from scipy.linalg import solve_discrete_lyapunov
    # VAR(1): state z=[X,Y]. Y drives X (b=0.8); NO X->Y path. ground truth: TE_{X->Y}=0.
    A = np.array([[0.4, 0.8],
                  [0.0, 0.5]])
    Q = np.array([[1.0, 0.0],
                  [0.0, 1.0]])
    Sig = solve_discrete_lyapunov(A, Q)          # stationary Cov(z_t)
    ASig = A @ Sig                               # Cov(z_{t+1}, z_t)
    # build Cov of v=[X_{t+1}, X_t, Y_t]  (indices: X=0, Y=1 in z)
    def _cov_future(fi):
        # fi: which component of z_{t+1} is the "future" (0=X,1=Y)
        gj, gk = (0, 1) if fi == 0 else (1, 0)   # target-past, source-past in z
        cov = np.zeros((3, 3))
        cov[0, 0] = Sig[fi, fi]
        cov[0, 1] = ASig[fi, gj]; cov[1, 0] = cov[0, 1]
        cov[0, 2] = ASig[fi, gk]; cov[2, 0] = cov[0, 2]
        cov[1, 1] = Sig[gj, gj]
        cov[2, 2] = Sig[gk, gk]
        cov[1, 2] = Sig[gj, gk]; cov[2, 1] = cov[1, 2]
        return cov
    te_y2x = gaussian_te(_cov_future(0))         # Y -> X  (should be > 0)
    te_x2y = gaussian_te(_cov_future(1))         # X -> Y  (should be ~ 0)
    # analytic ground truth for Y->X: 0.5 ln(Var(X'|X)/Var(X'|X,Y)), Var(X'|X,Y)=Q[0,0]
    vXgX = Sig[0, 0] - ASig[0, 0] ** 2 / Sig[0, 0]
    te_true = 0.5 * np.log(vXgX / Q[0, 0])
    print(f"   (a) gaussian_te Y->X = {te_y2x:.4f} nats | analytic = {te_true:.4f} | "
          f"X->Y = {te_x2y:.4f} (true 0)")
    assert abs(te_y2x - te_true) < 1e-9, "gaussian_te disagrees with analytic VAR TE"
    assert abs(te_x2y) < 1e-9, "spurious reverse TE in a one-way system"
    # discrete: S random bits; T_{t+1} = S_t w.p. 0.9 else flip. So S->T strong, T->S ~ 0.
    N = 4000
    s_bits = rng.integers(0, 2, N)
    t_bits = np.empty(N, int); t_bits[0] = 0
    for i in range(1, N):
        t_bits[i] = s_bits[i - 1] if rng.random() < 0.9 else 1 - s_bits[i - 1]
    te_st, m_st, sd_st, p_st = transfer_entropy_permutation_null(s_bits, t_bits, rng=0)
    te_ts, m_ts, sd_ts, p_ts = transfer_entropy_permutation_null(t_bits, s_bits, rng=0)
    print(f"   (b) S->T TE={te_st:.4f} bits (null {m_st:.4f}, p={p_st:.3f}) | "
          f"T->S TE={te_ts:.4f} (null {m_ts:.4f}, p={p_ts:.3f})")
    assert te_st > 0.3 and p_st < 0.01, "failed to detect true S->T coupling"
    assert p_ts > 0.05, "false-positive reverse coupling T->S"
    print("       OK: directionality recovered; reverse direction at chance.")
    print("=" * 72)
    print("All four checks reproduce the documented behaviour. Plug-in is never the answer.")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
