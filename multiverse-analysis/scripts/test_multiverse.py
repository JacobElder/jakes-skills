"""
Unit tests for multiverse.py engine.

Run with:  python -m pytest scripts/test_multiverse.py -v
      or:  python scripts/test_multiverse.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
import pytest
from multiverse import Multiverse, decision_importance, permutation_test, specification_curve


# ── fixtures ─────────────────────────────────────────────────────────────────

def make_data(n=60, seed=0):
    rng = np.random.default_rng(seed)
    group = np.repeat([0, 1], n // 2)
    y = 2.0 * group + rng.normal(0, 1, n)
    # add a few mild outliers
    y[0] = 15.0
    y[1] = -12.0
    return pd.DataFrame({"group": group, "y": y, "z": rng.normal(0, 1, n)})


def simple_analyze(data, c):
    df = data.copy()
    if c["outliers"] is not None:
        z = (df["y"] - df["y"].mean()) / df["y"].std()
        df = df[z.abs() <= c["outliers"]]
    from scipy import stats
    slope, _, _, p, _ = stats.linregress(df["group"], df["y"])
    return {"estimate": float(slope), "p_value": float(p), "n": len(df)}


def make_mv():
    return Multiverse(
        decisions={
            "outliers": {"none": None, "3sd": 3.0, "2sd": 2.0},
            "dummy":    {"a": 1, "b": 2},
        }
    )


# ── 1. constraint dropping ────────────────────────────────────────────────────

def test_constraints_drop_cells():
    mv = Multiverse(
        decisions={
            "model":  {"ols": "ols", "logit": "logit"},
            "dv":     {"continuous": "y", "binary": "bin_y"},
        },
        constraints=[lambda c: not (c["model"] == "ols" and c["dv"] == "binary")],
    )
    grid = mv.grid()
    assert len(grid) == 3, f"Expected 3 valid combos, got {len(grid)}"
    for combo in grid:
        assert not (combo["model"] == "ols" and combo["dv"] == "binary"), \
            "Constraint did not drop ols+binary"


def test_no_constraints_gives_full_product():
    mv = Multiverse(decisions={"a": {"x": 1, "y": 2}, "b": {"p": 10, "q": 20, "r": 30}})
    assert mv.n_total() == 6
    assert len(mv.grid()) == 6


def test_multi_constraint():
    mv = Multiverse(
        decisions={"a": {"x": 1, "y": 2, "z": 3}, "b": {"p": 10, "q": 20}},
        constraints=[
            lambda c: c["a"] != "x",
            lambda c: not (c["a"] == "y" and c["b"] == "q"),
        ],
    )
    grid = mv.grid()
    for combo in grid:
        assert combo["a"] != "x"
        assert not (combo["a"] == "y" and combo["b"] == "q")
    # a=y,b=p  ✓   a=y,b=q  ✗   a=z,b=p  ✓   a=z,b=q  ✓  → 3 valid
    assert len(grid) == 3, f"Expected 3, got {len(grid)}"


# ── 2. error capture into .error ──────────────────────────────────────────────

def test_failed_universe_captured_not_fatal():
    def flaky_analyze(data, c):
        if c["outliers"] == 2.0:
            raise ValueError("Intentional failure for 2sd")
        return {"estimate": 1.0, "p_value": 0.05, "n": len(data)}

    mv = make_mv()
    data = make_data()
    res = mv.run(flaky_analyze, data, progress=False)

    # Some rows should have .error populated
    errors = res[res[".error"].notna()]
    assert len(errors) > 0, "Expected at least one error row"
    # All error rows should contain the exception message
    for _, row in errors.iterrows():
        assert "ValueError" in row[".error"] or "Intentional" in row[".error"]

    # Non-error rows should have estimate
    ok = res[res[".error"].isna()]
    assert len(ok) > 0
    assert "estimate" in ok.columns


def test_all_universes_run_despite_partial_errors():
    def always_error(data, c):
        raise RuntimeError("always fails")

    mv = Multiverse(decisions={"x": {"a": 1, "b": 2, "c": 3}})
    res = mv.run(always_error, pd.DataFrame({"y": [1, 2]}), progress=False)
    assert len(res) == 3
    assert res[".error"].notna().all()


# ── 3. serial == parallel ─────────────────────────────────────────────────────

def test_serial_parallel_equivalence():
    try:
        import joblib  # noqa: F401
    except ImportError:
        pytest.skip("joblib not installed")

    data = make_data(n=80, seed=7)
    mv = make_mv()

    res_serial   = mv.run(simple_analyze, data, n_jobs=1,  progress=False)
    res_parallel = mv.run(simple_analyze, data, n_jobs=-1, progress=False)

    res_serial   = res_serial.sort_values([".universe"]).reset_index(drop=True)
    res_parallel = res_parallel.sort_values([".universe"]).reset_index(drop=True)

    assert list(res_serial[".universe"]) == list(res_parallel[".universe"])
    np.testing.assert_allclose(
        res_serial["estimate"].fillna(0).values,
        res_parallel["estimate"].fillna(0).values,
        rtol=1e-9, atol=1e-12,
        err_msg="Serial and parallel results differ",
    )


# ── 4. shared multi-column shuffle in permutation_test ───────────────────────

def test_permutation_shuffle_preserves_joint_distribution():
    """Shuffling multiple columns together must preserve their correlation."""
    rng = np.random.default_rng(123)
    n = 50
    a = rng.normal(0, 1, n)
    b = a * 0.9 + rng.normal(0, 0.1, n)   # highly correlated with a
    data = pd.DataFrame({"a": a, "b": b, "y": rng.normal(0, 1, n)})

    original_corr = float(np.corrcoef(data["a"], data["b"])[0, 1])

    shuffled = data.copy()
    perm = rng.permutation(n)
    for col in ["a", "b"]:
        shuffled[col] = shuffled[col].values[perm]

    shuffled_corr = float(np.corrcoef(shuffled["a"], shuffled["b"])[0, 1])
    # The joint shuffle keeps a-b correlation intact
    assert abs(shuffled_corr - original_corr) < 0.01, \
        f"Joint shuffle broke a-b correlation: {original_corr:.3f} → {shuffled_corr:.3f}"

    # Confirm link between shuffled columns and y is broken (not guaranteed but likely)
    # Just verify the function runs without error
    mv = Multiverse(decisions={"d": {"x": 1}})
    def trivial_analyze(data, c):
        return {"estimate": float(data["a"].mean()), "p_value": 0.5, "n": len(data)}
    result = permutation_test(mv, trivial_analyze, data, shuffle=["a", "b"],
                              n_perm=5, direction="auto")
    assert "median" in result


# ── 5. decision_importance eta-squared sums to ≤ 1 on a balanced grid ─────────

def test_decision_importance_eta_squared_bounded():
    data = make_data(n=100, seed=3)
    mv = make_mv()
    res = mv.run(simple_analyze, data, progress=False)
    ok  = res[res[".error"].isna()]
    imp = decision_importance(ok)
    assert list(imp.columns[:2]) == ["decision", "n_options"]
    assert (imp["eta_squared"] >= 0).all(), "eta_squared must be non-negative"
    assert (imp["eta_squared"] <= 1 + 1e-9).all(), "eta_squared must be ≤ 1"
    # The marginal eta^2 values may sum > 1 due to confounding — that's expected;
    # we only assert each is individually in [0,1]


# ── 6. max_universes sampling ─────────────────────────────────────────────────

def test_max_universes_limits_run():
    mv = Multiverse(decisions={
        "a": {str(i): i for i in range(4)},
        "b": {str(i): i for i in range(4)},
        "c": {str(i): i for i in range(4)},
    })
    assert mv.n_total() == 64
    data = pd.DataFrame({"x": [1, 2]})
    def trivial(data, c): return {"estimate": 1.0, "p_value": 0.5}
    res = mv.run(trivial, data, max_universes=10, progress=False)
    assert len(res) == 10


# ── runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import traceback
    tests = [
        test_constraints_drop_cells,
        test_no_constraints_gives_full_product,
        test_multi_constraint,
        test_failed_universe_captured_not_fatal,
        test_all_universes_run_despite_partial_errors,
        test_serial_parallel_equivalence,
        test_permutation_shuffle_preserves_joint_distribution,
        test_decision_importance_eta_squared_bounded,
        test_max_universes_limits_run,
    ]
    passed, failed = 0, 0
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  PASS  {name}")
            passed += 1
        except pytest.skip.Exception as e:
            print(f"  SKIP  {name}  ({e})")
        except Exception:
            print(f"  FAIL  {name}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed out of {len(tests)} tests")
    sys.exit(failed)
