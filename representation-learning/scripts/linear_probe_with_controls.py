#!/usr/bin/env python3
"""
linear_probe_with_controls.py — does the representation ENCODE a property, or is
your probe just memorizing? Decodability is not use, and high probe accuracy
alone proves neither.

Implements the Hewitt & Liang (2019) control-task protocol:

  real accuracy      a FROZEN, LINEAR probe (logistic regression) trained to
                     predict the real labels from frozen features.

  control accuracy   the same probe trained to predict CONTROL labels: random
                     labels assigned consistently per "type" (e.g. per word
                     type), so the control task has the same structure but no
                     linguistic signal. If the probe can fit this, the probe
                     (or feature dimensionality) is doing the work, not the
                     representation.

  selectivity        real_acc - control_acc. HIGH selectivity = the property is
                     genuinely linearly present in the features. LOW selectivity
                     (even with high real_acc) = the decodability claim is
                     unreliable; you are measuring probe capacity.

Rules baked in: the probe is LINEAR (no hidden layer) and the encoder is FROZEN
(you pass in precomputed features). This script measures *decodability*. It does
NOT establish that the model *uses* the property -- for that you need an
intervention (amnesic probing / INLP, or activation patching), which is a
separate tool.

Usage:
    from linear_probe_with_controls import probe_with_control
    probe_with_control(X, y, types=word_ids)   # types -> structured control
    python linear_probe_with_controls.py --selftest
"""
from __future__ import annotations
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def _make_control_labels(y: np.ndarray, types: np.ndarray | None,
                         seed: int = 0) -> np.ndarray:
    """Random labels drawn from y's label set, fixed per type (Hewitt & Liang).
    If types is None, assign per-example (a weaker control)."""
    rng = np.random.default_rng(seed)
    classes = np.unique(y)
    if types is None:
        return rng.choice(classes, size=len(y))
    control = np.empty(len(y), dtype=classes.dtype)
    for t in np.unique(types):
        control[types == t] = rng.choice(classes)
    return control


def _fit_linear(X_tr, y_tr, X_te, y_te, C: float = 1.0) -> float:
    clf = LogisticRegression(max_iter=2000, C=C)
    clf.fit(X_tr, y_tr)
    return float(clf.score(X_te, y_te))


def probe_with_control(X: np.ndarray, y: np.ndarray,
                       types: np.ndarray | None = None,
                       C: float = 1.0, test_size: float = 0.3,
                       seed: int = 0) -> dict:
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    control = _make_control_labels(y, types, seed=seed)

    idx = np.arange(len(y))
    tr, te = train_test_split(idx, test_size=test_size, random_state=seed,
                              stratify=y if len(np.unique(y)) > 1 else None)
    real_acc = _fit_linear(X[tr], y[tr], X[te], y[te], C=C)
    ctrl_acc = _fit_linear(X[tr], control[tr], X[te], control[te], C=C)
    majority = float(np.max(np.bincount(
        np.searchsorted(np.unique(y), y[te]))) / len(te))

    out = {
        "real_accuracy": real_acc,
        "control_accuracy": ctrl_acc,
        "selectivity": real_acc - ctrl_acc,
        "majority_baseline": majority,
        "n_classes": int(len(np.unique(y))),
        "structured_control": types is not None,
    }
    flags = []
    if out["selectivity"] < 0.10:
        flags.append("LOW SELECTIVITY: the probe fits the control nearly as "
                     "well as the real task, so high accuracy reflects probe "
                     "capacity, not the representation. Do not claim the "
                     "property is encoded on this evidence.")
    if real_acc - majority < 0.05:
        flags.append("NEAR-MAJORITY: real accuracy barely beats the majority "
                     "class; little is linearly decodable here.")
    flags.append("NOTE: decodability != use. To claim the model USES this "
                 "property, run an intervention (amnesic probing/INLP or "
                 "activation patching), not a probe.")
    out["flags"] = flags
    return out


# --------------------------------------------------------------------------- #
def _selftest() -> None:
    rng = np.random.default_rng(0)
    ok = True

    # 1. Genuine linear signal: label is sign of a linear projection.
    n, d = 3000, 50
    X = rng.standard_normal((n, d))
    w = rng.standard_normal(d)
    y = (X @ w > 0).astype(int)
    types = rng.integers(0, 400, size=n)            # arbitrary "word types"
    r = probe_with_control(X, y, types=types, seed=1)
    cond = r["real_accuracy"] > 0.9 and r["control_accuracy"] < 0.7 and r["selectivity"] > 0.2
    print(f"[genuine signal] real={r['real_accuracy']:.3f} "
          f"ctrl={r['control_accuracy']:.3f} sel={r['selectivity']:.3f}  "
          f"-> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 2. Pure memorization regime: features high-dim vs few samples, random
    #    labels -> probe fits BOTH real and control -> low selectivity. This is
    #    exactly the case the control task is designed to catch.
    n2, d2 = 200, 800
    Xm = rng.standard_normal((n2, d2))
    ym = rng.integers(0, 2, size=n2)                # random, no signal
    types2 = np.arange(n2)                           # each example its own type
    rm = probe_with_control(Xm, ym, types=types2, C=10.0, seed=2)
    cond = rm["selectivity"] < 0.15 and any("LOW SELECTIVITY" in f for f in rm["flags"])
    print(f"[memorization] real={rm['real_accuracy']:.3f} "
          f"ctrl={rm['control_accuracy']:.3f} sel={rm['selectivity']:.3f}  "
          f"-> {'PASS' if cond else 'FAIL'}")
    ok &= cond

    # 3. The decodability!=use note is always present.
    cond = any("decodability != use" in f for f in r["flags"])
    print(f"[decodability!=use note present]  -> {'PASS' if cond else 'FAIL'}")
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
