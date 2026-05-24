"""
Posterior predictive check (PPC) helpers for behavioral cognitive models.

The general PPC workflow:
  1. Draw parameter sets from the posterior (or use point estimates with
     uncertainty, or use simulated draws from MLE bootstrap).
  2. For each draw, simulate behavior on the same task structure.
  3. Compute summary statistics on the simulated data and the real data.
  4. Compare distributions of simulated summary stats to the observed value.

These helpers are model-agnostic — they take a simulator function and a list
of summary-statistic functions and do the rest.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Callable


def run_ppc(
    posterior_samples: pd.DataFrame,
    simulate_fn: Callable,
    summary_fns: dict[str, Callable],
    observed_data: dict,
    n_ppc_draws: int = 200,
    seed: int | None = 42,
    extra_sim_kwargs: dict | None = None,
) -> pd.DataFrame:
    """Run a posterior predictive check.

    Parameters
    ----------
    posterior_samples : DataFrame
        Each row is one posterior sample with the parameters needed by simulate_fn.
    simulate_fn : callable
        Same signature as for parameter recovery: takes a dict of params and
        returns a data dict.
    summary_fns : dict[name -> callable(data) -> float]
        Each function takes the data dict (real or simulated) and returns a scalar.
    observed_data : dict
        The actual data (same dict format as simulate output).
    n_ppc_draws : int
        Number of posterior draws to use (subsampled if posterior has more rows).
    extra_sim_kwargs : dict
        Forwarded to simulate_fn.

    Returns
    -------
    DataFrame with one row per ppc draw and one column per summary stat,
    plus an attribute ``observed`` (dict of observed values).
    """
    rng = np.random.default_rng(seed)
    extra_sim_kwargs = extra_sim_kwargs or {}

    # Subsample posterior if needed
    if len(posterior_samples) > n_ppc_draws:
        idx = rng.choice(len(posterior_samples), n_ppc_draws, replace=False)
        sub = posterior_samples.iloc[idx].reset_index(drop=True)
    else:
        sub = posterior_samples.reset_index(drop=True)

    # Observed values
    observed = {name: float(fn(observed_data)) for name, fn in summary_fns.items()}

    rows = []
    for _, params_row in sub.iterrows():
        params = dict(params_row)
        sim = simulate_fn(params, **extra_sim_kwargs)
        rec = {name: float(fn(sim)) for name, fn in summary_fns.items()}
        rows.append(rec)

    df = pd.DataFrame(rows)
    df.attrs["observed"] = observed
    return df


def ppc_p_values(ppc_df: pd.DataFrame) -> pd.Series:
    """For each summary stat, the posterior predictive p-value:
    P(sim >= observed). Values near 0 or 1 indicate misfit; values near 0.5
    indicate the model captures that statistic.
    """
    observed = ppc_df.attrs.get("observed")
    if observed is None:
        raise ValueError("ppc_df has no 'observed' attribute — run via run_ppc()")
    out = {}
    for col in ppc_df.columns:
        obs_val = observed[col]
        sim_vals = ppc_df[col].values
        p = (np.sum(sim_vals >= obs_val) + 0.5 * np.sum(sim_vals == obs_val)) / len(sim_vals)
        out[col] = float(p)
    return pd.Series(out, name="ppc_p_value")


# --------------------------------------------------------------------
# Library of common behavioral summary statistics.
# --------------------------------------------------------------------

def stat_accuracy(data: dict, correct_key: str = "correct") -> float:
    return float(np.mean(data[correct_key]))


def stat_win_stay(data: dict, choice_key: str = "choices",
                  reward_key: str = "rewards") -> float:
    """P(repeat choice | reward = 1)."""
    ch = np.asarray(data[choice_key])
    rw = np.asarray(data[reward_key])
    if len(ch) < 2:
        return np.nan
    rewarded = rw[:-1] == 1
    if rewarded.sum() == 0:
        return np.nan
    stayed = ch[1:] == ch[:-1]
    return float(stayed[rewarded].mean())


def stat_lose_shift(data: dict, choice_key: str = "choices",
                    reward_key: str = "rewards") -> float:
    """P(switch choice | reward = 0)."""
    ch = np.asarray(data[choice_key])
    rw = np.asarray(data[reward_key])
    if len(ch) < 2:
        return np.nan
    no_rew = rw[:-1] == 0
    if no_rew.sum() == 0:
        return np.nan
    switched = ch[1:] != ch[:-1]
    return float(switched[no_rew].mean())


def stat_choice_autocorr(data: dict, lag: int = 1,
                         choice_key: str = "choices") -> float:
    """Lag-1 autocorrelation of choice (perseveration index)."""
    ch = np.asarray(data[choice_key]).astype(float)
    if len(ch) <= lag:
        return np.nan
    a, b = ch[:-lag], ch[lag:]
    a = a - a.mean(); b = b - b.mean()
    denom = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    if denom == 0:
        return np.nan
    return float((a * b).sum() / denom)


def stat_rt_quantile(q: float = 0.5, rt_key: str = "rts") -> Callable:
    """Factory: q-th RT quantile."""
    def _f(data):
        return float(np.quantile(data[rt_key], q))
    _f.__name__ = f"rt_q{int(q * 100)}"
    return _f


def stat_p_choice(option: int, choice_key: str = "choices") -> Callable:
    """Factory: P(choice == option)."""
    def _f(data):
        return float(np.mean(np.asarray(data[choice_key]) == option))
    _f.__name__ = f"p_choice_{option}"
    return _f


if __name__ == "__main__":
    # Self-test: fit a 2-arm RW + softmax, then PPC.
    from scipy.optimize import minimize

    rng = np.random.default_rng(0)
    true_alpha, true_beta = 0.25, 4.0
    reward_probs = (0.75, 0.25)

    Q = np.zeros(2); ch, rw = [], []
    for _ in range(300):
        p = np.exp(true_beta * Q - np.max(true_beta * Q)); p /= p.sum()
        c = int(rng.choice(2, p=p))
        r = float(rng.random() < reward_probs[c])
        Q[c] += true_alpha * (r - Q[c])
        ch.append(c); rw.append(r)
    real_data = {"choices": np.array(ch), "rewards": np.array(rw)}

    def nll(x):
        a, b = x; Q = np.zeros(2); ll = 0.0
        for c, r in zip(real_data["choices"], real_data["rewards"]):
            m = np.max(b * Q)
            ll += b * Q[c] - (m + np.log(np.sum(np.exp(b * Q - m))))
            Q[c] += a * (r - Q[c])
        return -ll
    res = minimize(nll, [0.3, 3.0], method="L-BFGS-B",
                   bounds=[(1e-4, 1 - 1e-4), (1e-4, 30)])
    a_hat, b_hat = res.x
    posterior = pd.DataFrame({
        "alpha": np.clip(rng.normal(a_hat, 0.04, 400), 0.01, 0.99),
        "beta":  np.clip(rng.normal(b_hat, 0.5, 400), 0.1, 20.0),
    })

    def sim(params, n_trials=300, reward_probs=(0.75, 0.25)):
        rng2 = np.random.default_rng()
        a, b = params["alpha"], params["beta"]
        Q = np.zeros(2); ch, rw = [], []
        for _ in range(n_trials):
            p = np.exp(b * Q - np.max(b * Q)); p /= p.sum()
            c = int(rng2.choice(2, p=p))
            r = float(rng2.random() < reward_probs[c])
            Q[c] += a * (r - Q[c])
            ch.append(c); rw.append(r)
        return {"choices": np.array(ch), "rewards": np.array(rw)}

    summary_fns = {
        "p_choice_better": stat_p_choice(0),
        "win_stay": stat_win_stay,
        "lose_shift": stat_lose_shift,
        "choice_autocorr_lag1": stat_choice_autocorr,
    }

    ppc = run_ppc(posterior, sim, summary_fns, real_data,
                  extra_sim_kwargs={"reward_probs": reward_probs})
    p_vals = ppc_p_values(ppc)
    print("PPC summary (observed vs simulated):")
    hdr = f"{'stat':22s}  {'observed':>10s}  {'sim_mean':>10s}  {'sim_2.5%':>10s}  {'sim_97.5%':>10s}  {'p-value':>8s}"
    print(hdr)
    for name in summary_fns:
        obs = ppc.attrs["observed"][name]
        sims = ppc[name].values
        print(f"{name:22s}  {obs:10.3f}  {sims.mean():10.3f}  "
              f"{np.quantile(sims, 0.025):10.3f}  {np.quantile(sims, 0.975):10.3f}  "
              f"{p_vals[name]:8.3f}")
    print()
    print("p-values near 0.5 mean the model reproduces the statistic.")
    print("Values near 0 or 1 mean misfit on that statistic — investigate.")
