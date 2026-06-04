#!/usr/bin/env python3
"""
replication_convergence.py — How many replications does a stochastic ABM need?

The number of runs an agent-based model needs is an empirical question, not a
magic constant copied from another paper. This helper runs a model with an
increasing number of replications (different random seeds) and watches a summary
statistic of the output stabilize. The standard criterion (Lorscheid et al. 2012;
ten Broeke et al. 2014) is the convergence of the coefficient of variation
(CV = std / mean): stop when adding more runs no longer meaningfully changes it.

It also reports the standard error of the mean (SEM), which answers the related
question "how tight is my estimate of the mean output?" and is often what you
actually care about when comparing scenarios.

IMPORTANT CAVEATS (see references/analysis-and-experiments.md):
- Do this PER OUTPUT and PER PARAMETER REGIME. Variance often explodes near
  tipping points / phase transitions, so a count that suffices mid-space can be
  far too few near an interesting boundary. Re-run this there.
- Non-linear input-output relationships break the assumption that convergence is
  uniform.
- This treats the output as roughly unimodal. If the output is multimodal or
  heavy-tailed, the mean/CV can describe an outcome the model never produces —
  inspect the full distribution (the script can dump it), don't just trust the CV.

USAGE (as a library — the normal case):

    from replication_convergence import replication_convergence

    def my_model(seed):
        # set up and run ONE replication of your ABM with this seed,
        # return the single scalar output of interest (e.g. final infected count)
        ...
        return output

    result = replication_convergence(my_model, max_reps=500)
    print(result["recommended_reps"])

USAGE (demo, to see it work):

    python replication_convergence.py --demo
    python replication_convergence.py --demo --plot   # needs matplotlib
"""
from __future__ import annotations

import argparse
import math
from typing import Callable, Optional


def replication_convergence(
    model_fn: Callable[[int], float],
    max_reps: int = 500,
    min_reps: int = 10,
    tol: float = 0.01,
    window: int = 20,
    seed0: int = 0,
    verbose: bool = False,
):
    """
    Run model_fn(seed) -> scalar repeatedly and detect when the coefficient of
    variation of the collected outputs has stabilized.

    Args:
        model_fn:  callable taking an integer seed, returning ONE scalar output.
                   It must run a full, independent replication of the model.
        max_reps:  hard cap on replications.
        min_reps:  don't declare convergence before this many runs.
        tol:       convergence threshold — the max relative change in the running
                   CV across `window` consecutive replications to count as "flat".
        window:    how many recent replications the flatness check looks back over.
        seed0:     first seed; subsequent runs use seed0, seed0+1, ...
        verbose:   print running stats.

    Returns dict with:
        recommended_reps: int or None (None => did not converge within max_reps)
        converged:        bool
        outputs:          list[float] of every replication's output (the raw sample)
        running_mean:     list[float]
        running_cv:       list[float]
        running_sem:      list[float]
        final_mean, final_std, final_cv, final_sem
    """
    outputs: list[float] = []
    running_mean: list[float] = []
    running_cv: list[float] = []
    running_sem: list[float] = []
    recommended: Optional[int] = None

    for i in range(max_reps):
        outputs.append(float(model_fn(seed0 + i)))
        n = len(outputs)
        mean = sum(outputs) / n
        if n > 1:
            var = sum((x - mean) ** 2 for x in outputs) / (n - 1)
        else:
            var = 0.0
        std = math.sqrt(var)
        cv = std / mean if mean != 0 else float("inf")
        sem = std / math.sqrt(n)
        running_mean.append(mean)
        running_cv.append(cv)
        running_sem.append(sem)

        if verbose and (n <= 5 or n % 25 == 0):
            print(f"  n={n:4d}  mean={mean:.5g}  cv={cv:.5g}  sem={sem:.5g}")

        # Flatness check: relative change in CV over the last `window` reps.
        if recommended is None and n >= max(min_reps, window + 1):
            recent = running_cv[-window:]
            lo, hi = min(recent), max(recent)
            ref = abs(running_cv[-1]) if running_cv[-1] != 0 else 1.0
            if math.isfinite(lo) and math.isfinite(hi) and (hi - lo) / ref <= tol:
                recommended = n

    final_mean = running_mean[-1]
    final_cv = running_cv[-1]
    return {
        "recommended_reps": recommended,
        "converged": recommended is not None,
        "outputs": outputs,
        "running_mean": running_mean,
        "running_cv": running_cv,
        "running_sem": running_sem,
        "final_mean": final_mean,
        "final_std": final_cv * final_mean if math.isfinite(final_cv) else float("nan"),
        "final_cv": final_cv,
        "final_sem": running_sem[-1],
    }


def _plot(result):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plot (pip install matplotlib).")
        return
    n = range(1, len(result["running_cv"]) + 1)
    fig, ax = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax[0].plot(n, result["running_cv"])
    ax[0].set_ylabel("running CV")
    ax[0].axvline(result["recommended_reps"], color="red", ls="--",
                  label=f"recommended = {result['recommended_reps']}")
    ax[0].legend()
    ax[1].plot(n, result["running_mean"])
    ax[1].set_ylabel("running mean")
    ax[1].set_xlabel("replications")
    fig.suptitle("Replication convergence")
    fig.tight_layout()
    out = "replication_convergence.png"
    fig.savefig(out, dpi=120)
    print(f"Saved {out}")


def _demo(plot: bool):
    """A toy stochastic 'model': output ~ Normal with a touch of skew."""
    import random

    def toy_model(seed: int) -> float:
        rng = random.Random(seed)
        # mean ~50, sd ~12, plus a small skew so it's not perfectly Gaussian
        return 50 + rng.gauss(0, 12) + 0.5 * abs(rng.gauss(0, 8))

    result = replication_convergence(toy_model, max_reps=500, tol=0.01,
                                     window=20, verbose=True)
    print("\nResult:")
    print(f"  converged:        {result['converged']}")
    print(f"  recommended_reps: {result['recommended_reps']}")
    print(f"  final mean:       {result['final_mean']:.4g}")
    print(f"  final CV:         {result['final_cv']:.4g}")
    print(f"  final SEM:        {result['final_sem']:.4g}")
    print("\nReminder: re-run this near tipping points — variance there is larger,")
    print("so the mid-space recommendation will usually be too few.")
    if plot:
        _plot(result)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--demo", action="store_true", help="run a self-contained demo")
    p.add_argument("--plot", action="store_true", help="save a convergence plot (demo)")
    args = p.parse_args()
    if args.demo:
        _demo(args.plot)
    else:
        print("Import this module and call replication_convergence(model_fn). "
              "Run with --demo to see it work.")
