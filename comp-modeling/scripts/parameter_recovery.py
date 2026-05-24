"""
Generic parameter recovery utilities.

Given a simulate function, a fit function, and a parameter grid, this runs
the recovery loop and returns a tidy DataFrame plus recovery statistics.

Usage:

    def simulate(params, n_trials=200):
        # ... return choices, rewards (or any task-appropriate data)
        return data_dict

    def fit(data_dict):
        # ... return dict of recovered param estimates
        return param_dict

    results = run_recovery(
        simulate_fn=simulate,
        fit_fn=fit,
        param_ranges={'alpha': (0.05, 0.95), 'beta': (1, 8)},
        n_sims=100,
        n_trials=200,
    )

    summarize_recovery(results)
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from typing import Callable
import warnings


def run_recovery(
    simulate_fn: Callable,
    fit_fn: Callable,
    param_ranges: dict[str, tuple[float, float]],
    n_sims: int = 100,
    n_trials: int = 200,
    sampling: str = "uniform",
    seed: int | None = 42,
    extra_sim_kwargs: dict | None = None,
) -> pd.DataFrame:
    """Run a parameter recovery loop.

    Parameters
    ----------
    simulate_fn : callable
        Takes (params_dict, n_trials=n_trials, **extra_sim_kwargs) and returns
        a data dict that fit_fn can consume.
    fit_fn : callable
        Takes a data dict, returns a dict of recovered parameter values.
    param_ranges : dict
        Mapping from param name to (low, high) generating range.
    n_sims : int
        Number of simulated subjects.
    n_trials : int
        Trials per simulated subject.
    sampling : {"uniform", "grid", "lhs"}
        How to sample the generating params over their ranges.
    seed : int or None
        RNG seed.
    extra_sim_kwargs : dict
        Extra kwargs passed to simulate_fn (e.g., reward probabilities).

    Returns
    -------
    DataFrame with columns ``true_<param>`` and ``recovered_<param>`` for each param.
    """
    rng = np.random.default_rng(seed)
    extra_sim_kwargs = extra_sim_kwargs or {}
    pnames = list(param_ranges.keys())

    # Generate the true parameter sets
    if sampling == "uniform":
        true_params = {
            p: rng.uniform(lo, hi, n_sims) for p, (lo, hi) in param_ranges.items()
        }
    elif sampling == "grid":
        # 1D grids per param, broadcast — only sensible for low dim
        side = int(np.ceil(n_sims ** (1.0 / len(pnames))))
        grids = [np.linspace(lo, hi, side) for lo, hi in param_ranges.values()]
        mesh = np.meshgrid(*grids, indexing="ij")
        flat = np.stack([m.ravel() for m in mesh], axis=1)
        if len(flat) > n_sims:
            idx = rng.choice(len(flat), n_sims, replace=False)
            flat = flat[idx]
        true_params = {p: flat[:, i] for i, p in enumerate(pnames)}
    elif sampling == "lhs":
        try:
            from scipy.stats import qmc
        except ImportError:
            raise ImportError("Latin hypercube sampling needs scipy >= 1.7")
        sampler = qmc.LatinHypercube(d=len(pnames), seed=seed)
        samples = sampler.random(n=n_sims)  # in [0, 1)^d
        lows = np.array([lo for lo, _ in param_ranges.values()])
        highs = np.array([hi for _, hi in param_ranges.values()])
        scaled = lows + samples * (highs - lows)
        true_params = {p: scaled[:, i] for i, p in enumerate(pnames)}
    else:
        raise ValueError(f"Unknown sampling scheme {sampling!r}")

    # Recovery loop
    records = []
    for i in range(n_sims):
        truth = {p: float(true_params[p][i]) for p in pnames}
        data = simulate_fn(truth, n_trials=n_trials, **extra_sim_kwargs)
        try:
            recovered = fit_fn(data)
        except Exception as exc:
            warnings.warn(f"Fit failed on sim {i} with params {truth}: {exc}")
            recovered = {p: np.nan for p in pnames}

        rec = {f"true_{p}": truth[p] for p in pnames}
        rec.update({f"recovered_{p}": recovered.get(p, np.nan) for p in pnames})
        rec["sim_idx"] = i
        records.append(rec)

    return pd.DataFrame.from_records(records)


def summarize_recovery(df: pd.DataFrame, method: str = "spearman") -> pd.DataFrame:
    """Report per-parameter recovery correlations + cross-parameter recovery
    correlations of recovered estimates.

    Returns a DataFrame with rows = parameters, columns = recovery statistics.
    """
    pnames = [c.removeprefix("true_") for c in df.columns if c.startswith("true_")]
    rows = []
    corr_fn = spearmanr if method == "spearman" else pearsonr
    for p in pnames:
        t = df[f"true_{p}"].values
        r = df[f"recovered_{p}"].values
        valid = ~np.isnan(t) & ~np.isnan(r)
        if valid.sum() < 3:
            rows.append({"param": p, "rho": np.nan, "bias": np.nan,
                         "rmse": np.nan, "n_valid": int(valid.sum())})
            continue
        rho, _ = corr_fn(t[valid], r[valid])
        bias = float(np.mean(r[valid] - t[valid]))
        rmse = float(np.sqrt(np.mean((r[valid] - t[valid]) ** 2)))
        rows.append({"param": p, "rho": float(rho), "bias": bias,
                     "rmse": rmse, "n_valid": int(valid.sum())})

    summary = pd.DataFrame(rows).set_index("param")

    # Cross-parameter correlations of recovered estimates
    rec_only = df[[f"recovered_{p}" for p in pnames]].copy()
    rec_only.columns = pnames
    summary.attrs["cross_param_recovered_corr"] = rec_only.corr(method=method)

    return summary


def recovery_quality_label(rho: float) -> str:
    """Human-readable label for a recovery correlation."""
    if rho >= 0.9:
        return "excellent"
    elif rho >= 0.7:
        return "good (usable for individual-difference work)"
    elif rho >= 0.4:
        return "marginal (group-level inferences only)"
    elif rho >= 0:
        return "poor (do not interpret individual estimates)"
    else:
        return "negative — check for bugs"


def print_recovery_report(df: pd.DataFrame, method: str = "spearman") -> None:
    """Pretty-print a recovery report to stdout."""
    summary = summarize_recovery(df, method=method)
    print(f"Parameter recovery summary (n = {len(df)}, method = {method})")
    print("-" * 70)
    for param, row in summary.iterrows():
        rho = row["rho"]
        print(f"  {param:>12s}: ρ = {rho:.3f} ({recovery_quality_label(rho)})")
        print(f"  {'':>12s}  bias = {row['bias']:+.4f}, RMSE = {row['rmse']:.4f}")
    print()
    print("Cross-parameter recovered correlations (off-diagonals > |0.5| indicate")
    print("trade-offs — interpret marginals with caution):")
    cross = summary.attrs["cross_param_recovered_corr"]
    print(cross.round(3))


if __name__ == "__main__":
    # Self-test on a 2-param Rescorla-Wagner + softmax bandit
    from scipy.optimize import minimize

    def sim_rl(params, n_trials=200, reward_probs=(0.7, 0.3), seed=None):
        rng = np.random.default_rng(seed)
        alpha, beta = params["alpha"], params["beta"]
        Q = np.zeros(2)
        choices, rewards = [], []
        for _ in range(n_trials):
            p = np.exp(beta * Q - np.max(beta * Q))
            p = p / p.sum()
            c = int(rng.choice(2, p=p))
            r = float(rng.random() < reward_probs[c])
            Q[c] += alpha * (r - Q[c])
            choices.append(c)
            rewards.append(r)
        return {"choices": np.array(choices), "rewards": np.array(rewards)}

    def fit_rl(data):
        ch = data["choices"]
        rw = data["rewards"]

        def nll(params):
            a, b = params
            Q = np.zeros(2)
            ll = 0.0
            for c, r in zip(ch, rw):
                m = np.max(b * Q)
                log_p_chosen = b * Q[c] - (m + np.log(np.sum(np.exp(b * Q - m))))
                ll += log_p_chosen
                Q[c] += a * (r - Q[c])
            return -ll

        best = None
        rng = np.random.default_rng()
        for _ in range(8):
            x0 = [rng.uniform(0.05, 0.95), rng.uniform(0.5, 10)]
            res = minimize(nll, x0, method="L-BFGS-B",
                           bounds=[(1e-4, 1 - 1e-4), (1e-4, 30)])
            if best is None or res.fun < best.fun:
                best = res
        return {"alpha": best.x[0], "beta": best.x[1]}

    df = run_recovery(
        simulate_fn=sim_rl, fit_fn=fit_rl,
        param_ranges={"alpha": (0.05, 0.95), "beta": (1, 8)},
        n_sims=40, n_trials=200,
    )
    print_recovery_report(df)
