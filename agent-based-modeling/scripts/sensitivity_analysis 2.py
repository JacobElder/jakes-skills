#!/usr/bin/env python3
"""
sensitivity_analysis.py — Global sensitivity analysis for (stochastic) ABMs.

Which parameters actually drive your model's output, and how robust is each
conclusion? One-factor-at-a-time (OFAT) sweeps are good for *illustrating* a
mechanism but miss interactions, so they can't establish robustness on their own.
This script runs proper GLOBAL sensitivity analysis via SALib:

  * Morris elementary effects  — cheap SCREENING. Ranks parameters into
    "negligible / linear / non-linear-or-interacting" so you can drop the ones
    that don't matter before spending real compute. Run this FIRST.
  * Sobol variance-based indices — the informative-but-expensive method. S1
    (first-order) is a parameter's direct share of output variance; ST
    (total-effect) includes its interactions. Spend this budget on the few
    parameters Morris flags as important.

ABM-specific handling: ABMs are stochastic, so each sampled parameter point is
evaluated `reps` times with different seeds and AVERAGED. Without this you cannot
tell a parameter effect from random-seed noise. Increase `reps` near regimes
where output variance is high (use replication_convergence.py to gauge it).

Requires SALib and numpy:   pip install SALib numpy --break-system-packages

USAGE (library — the normal case):

    from sensitivity_analysis import morris_screen, sobol_analyze

    problem = {
        "num_vars": 3,
        "names": ["infection_rate", "recovery_rate", "n_contacts"],
        "bounds": [[0.01, 0.5], [0.05, 0.4], [2, 20]],
    }

    def model(params, seed):
        # params is a dict {name: value}; run ONE replication; return a scalar
        ...
        return output

    morris_screen(model, problem, trajectories=20, reps=5)
    sobol_analyze(model, problem, n=256, reps=5)

USAGE (demo):

    python sensitivity_analysis.py --demo
"""
from __future__ import annotations

from typing import Callable, Dict, List

try:
    import numpy as np
except ImportError as e:  # pragma: no cover
    raise SystemExit("numpy is required: pip install numpy --break-system-packages") from e


def _eval_samples(model_fn: Callable[[Dict[str, float], int], float],
                  names: List[str], X: "np.ndarray", reps: int,
                  seed0: int = 0) -> "np.ndarray":
    """Evaluate every sampled parameter row, averaging `reps` stochastic runs."""
    Y = np.empty(X.shape[0], dtype=float)
    for i, row in enumerate(X):
        params = {name: row[j] for j, name in enumerate(names)}
        vals = [model_fn(params, seed0 + i * reps + r) for r in range(reps)]
        Y[i] = float(np.mean(vals))
    return Y


def morris_screen(model_fn, problem, trajectories: int = 20, reps: int = 5,
                  num_levels: int = 4, seed0: int = 0, print_results: bool = True):
    """Morris elementary-effects screening. Returns the SALib Si dict.

    Interpretation: mu_star ranks overall importance; a large sigma relative to
    mu_star flags interactions or non-linearity. Parameters with mu_star near
    zero can usually be fixed and dropped from further analysis.
    """
    from SALib.sample import morris as morris_sample
    from SALib.analyze import morris as morris_analyze

    X = morris_sample.sample(problem, N=trajectories, num_levels=num_levels)
    Y = _eval_samples(model_fn, problem["names"], X, reps, seed0)
    Si = morris_analyze.analyze(problem, X, Y, num_levels=num_levels,
                                print_to_console=False)
    if print_results:
        print(f"\n=== Morris screening ({X.shape[0]} samples x {reps} reps) ===")
        print(f"{'parameter':<20}{'mu_star':>12}{'sigma':>12}")
        order = np.argsort(Si["mu_star"])[::-1]
        for k in order:
            print(f"{problem['names'][k]:<20}{Si['mu_star'][k]:>12.4g}"
                  f"{Si['sigma'][k]:>12.4g}")
        print("Tip: fix parameters with mu_star near 0; large sigma/mu_star => "
              "interactions or non-linearity.")
    return Si


def sobol_analyze(model_fn, problem, n: int = 256, reps: int = 5,
                  calc_second_order: bool = False, seed0: int = 0,
                  print_results: bool = True):
    """Sobol variance-based indices. Returns the SALib Si dict.

    n is the base sample size; total model evaluations are
    n*(num_vars+2) (first-order/total) or n*(2*num_vars+2) (with second order),
    each times `reps` stochastic replications. Use a power of 2 for n.

    Interpretation: S1 = direct share of output variance; ST = total incl.
    interactions. ST >> S1 means the parameter acts mostly through interactions.
    sum(S1) much below 1 also indicates strong interaction effects.
    """
    from SALib.sample import sobol as sobol_sample
    from SALib.analyze import sobol as sobol_analyze_

    X = sobol_sample.sample(problem, N=n, calc_second_order=calc_second_order)
    Y = _eval_samples(model_fn, problem["names"], X, reps, seed0)
    Si = sobol_analyze_.analyze(problem, Y, calc_second_order=calc_second_order,
                                print_to_console=False)
    if print_results:
        print(f"\n=== Sobol indices ({X.shape[0]} samples x {reps} reps) ===")
        print(f"{'parameter':<20}{'S1':>10}{'S1_conf':>10}{'ST':>10}{'ST_conf':>10}")
        for k, name in enumerate(problem["names"]):
            print(f"{name:<20}{Si['S1'][k]:>10.3f}{Si['S1_conf'][k]:>10.3f}"
                  f"{Si['ST'][k]:>10.3f}{Si['ST_conf'][k]:>10.3f}")
        s1_sum = float(np.sum(Si["S1"]))
        hint = "(close to 1 => mostly additive, weak interactions)" if s1_sum >= 0.9 \
            else "(well below 1 => interactions account for much of the variance)"
        print(f"sum(S1) = {s1_sum:.3f}  {hint}")
    return Si


def _demo():
    """Toy stochastic model with a known structure: x0 strong, x1 via interaction
    with x0, x2 nearly irrelevant — so Morris should rank x0 > x1 >> x2 and Sobol
    should show ST(x1) > S1(x1)."""
    import random

    problem = {
        "num_vars": 3,
        "names": ["x0", "x1", "x2"],
        "bounds": [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]],
    }

    def model(params, seed):
        rng = random.Random(seed)
        x0, x1, x2 = params["x0"], params["x1"], params["x2"]
        signal = 3.0 * x0 + 2.0 * x0 * x1 + 0.05 * x2  # x2 barely matters
        return signal + rng.gauss(0, 0.15)             # stochastic noise

    morris_screen(model, problem, trajectories=20, reps=5)
    sobol_analyze(model, problem, n=256, reps=5)
    print("\nExpected: x0 dominant; x1 acts mainly through interaction with x0 "
          "(ST>>S1); x2 negligible.")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--demo", action="store_true", help="run a self-contained demo")
    args = p.parse_args()
    if args.demo:
        _demo()
    else:
        print("Import morris_screen / sobol_analyze, or run with --demo.")
