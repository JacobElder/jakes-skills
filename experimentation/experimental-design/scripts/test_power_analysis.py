#!/usr/bin/env python3
"""
Unit tests for power_analysis.py.

Verifies the four canonical benchmark values (checked against textbook references)
and a round-trip: solve for N, then solve for power at that N ≈ 0.80.

All stdlib — no numpy/scipy or other third-party imports.
Run with: python -m unittest scripts/test_power_analysis.py
"""

import math
import sys
import unittest
from pathlib import Path

# Allow running from the repo root or the scripts/ directory.
sys.path.insert(0, str(Path(__file__).parent))
from power_analysis import (
    n_for_mean,
    n_for_proportion,
    norm_ppf,
    power_for_mean,
    power_for_proportion,
)


def _n_prop(baseline, mde_abs, alpha=0.05, power=0.80, sided=2):
    p2 = baseline + mde_abs
    return math.ceil(n_for_proportion(baseline, p2, alpha, power, sided))


def _n_mean(delta, sd, alpha=0.05, power=0.80, sided=2):
    return math.ceil(n_for_mean(delta, sd, alpha, power, sided))


class TestBenchmarkValues(unittest.TestCase):
    """Four verified benchmark values — tolerance ±1% of stated N."""

    def _assert_n(self, actual, expected, label):
        tol = max(50, int(expected * 0.01))
        self.assertAlmostEqual(
            actual,
            expected,
            delta=tol,
            msg=f"{label}: got {actual}, expected {expected} ± {tol}",
        )

    def test_proportion_10pct_to_11pct(self):
        # 10% → 11% (1pp abs), α=.05, 80% power → 14,751 / arm
        n = _n_prop(0.10, 0.01)
        self._assert_n(n, 14751, "10%→11% proportion")

    def test_mean_diff_0_5_sd_4(self):
        # mean diff 0.5, sd=4, α=.05, 80% power → 1,005 / arm
        n = _n_mean(0.5, 4.0)
        self._assert_n(n, 1005, "mean diff 0.5, sd=4")

    def test_proportion_22pct_plus_2pp(self):
        # baseline 22%, +2pp abs, α=.05, 80% power → 6,950 / arm
        n = _n_prop(0.22, 0.02)
        self._assert_n(n, 6950, "22%+2pp proportion")

    def test_proportion_4_2pct_5pct_relative(self):
        # baseline 4.2%, +5% relative → +0.21pp abs → ~146,642 / arm
        mde_abs = 0.042 * 0.05
        n = _n_prop(0.042, mde_abs)
        self._assert_n(n, 146642, "4.2% + 5% relative")


class TestRoundTrip(unittest.TestCase):
    """Solve for N, then verify power at that N ≈ 0.80."""

    def _round_trip_prop(self, baseline, mde_abs, alpha=0.05, target_power=0.80, sided=2):
        p2 = baseline + mde_abs
        n_raw = n_for_proportion(baseline, p2, alpha, target_power, sided)
        n = math.ceil(n_raw)
        achieved = power_for_proportion(baseline, p2, n, alpha, sided)
        self.assertGreaterEqual(achieved, target_power - 0.005,
            f"Power at ceil(N) should be ≥ target: got {achieved:.4f}")
        # Using floor(n_raw) should be slightly below target power
        n_floor = max(1, math.floor(n_raw))
        achieved_floor = power_for_proportion(baseline, p2, n_floor, alpha, sided)
        self.assertLessEqual(achieved_floor, target_power + 0.01,
            f"Power at floor(N) should not far exceed target: got {achieved_floor:.4f}")

    def _round_trip_mean(self, delta, sd, alpha=0.05, target_power=0.80, sided=2):
        n_raw = n_for_mean(delta, sd, alpha, target_power, sided)
        n = math.ceil(n_raw)
        achieved = power_for_mean(delta, sd, n, alpha, sided)
        self.assertGreaterEqual(achieved, target_power - 0.005,
            f"Power at ceil(N) should be ≥ target: got {achieved:.4f}")

    def test_round_trip_proportion_10_to_11(self):
        self._round_trip_prop(0.10, 0.01)

    def test_round_trip_proportion_22_plus_2pp(self):
        self._round_trip_prop(0.22, 0.02)

    def test_round_trip_mean_0_5_sd_4(self):
        self._round_trip_mean(0.5, 4.0)


class TestNormHelpers(unittest.TestCase):
    """Basic sanity on the normal distribution helpers."""

    def test_ppf_known_quantiles(self):
        self.assertAlmostEqual(norm_ppf(0.975), 1.96, places=2)
        self.assertAlmostEqual(norm_ppf(0.5), 0.0, places=6)
        self.assertAlmostEqual(norm_ppf(0.841), 1.0, places=2)

    def test_ppf_symmetry(self):
        for p in [0.1, 0.25, 0.75, 0.9]:
            self.assertAlmostEqual(norm_ppf(p) + norm_ppf(1 - p), 0.0, places=8)


if __name__ == "__main__":
    unittest.main()
