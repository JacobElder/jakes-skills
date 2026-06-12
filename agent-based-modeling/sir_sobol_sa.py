#!/usr/bin/env python3
"""
sir_sobol_sa.py

SIR-style ABM + Sobol global sensitivity analysis.

Parameters under study
  infection_rate  [0.01, 0.50]  per-contact transmission probability
  recovery_rate   [0.05, 0.40]  per-step recovery probability (infected)
  n_contacts      [2,    20  ]  contacts each infected agent makes per step

Output metric: final outbreak size (total ever infected).

Sobol approach
  - Saltelli quasi-random design, N=1024 base samples
    → 1024*(2k+2) = 8192 model evaluations for k=3 parameters
  - Each parameter set averaged over R_REPS independent seeds to
    reduce stochastic noise before variance decomposition.
  - Reports S1 (first-order), ST (total-order), interaction = ST-S1.
"""
from __future__ import annotations

import numpy as np
from SALib.sample import saltelli
from SALib.analyze import sobol

# ── ABM ──────────────────────────────────────────────────────────────────────

N_AGENTS   = 2_000   # population size
N_SEEDS    = 5       # replications per parameter point (stochastic averaging)
MAX_STEPS  = 500     # hard cap; epidemic almost always ends before this
N_INITIAL  = 10      # initially infected


def run(params: dict, seed: int) -> float:
    """
    One SIR replication.

    States: 0=S, 1=I, 2=R
    Each step every infected agent draws n_contacts random targets;
    susceptible targets are infected with prob infection_rate.
    Each infected agent independently recovers with prob recovery_rate.

    Returns total fraction of population ever infected.
    """
    rng = np.random.default_rng(seed)
    inf_rate  = float(params["infection_rate"])
    rec_rate  = float(params["recovery_rate"])
    n_con     = int(round(params["n_contacts"]))

    state = np.zeros(N_AGENTS, dtype=np.int8)  # 0=S
    seeds_idx = rng.choice(N_AGENTS, size=N_INITIAL, replace=False)
    state[seeds_idx] = 1  # 1=I

    for _ in range(MAX_STEPS):
        infected_idx = np.where(state == 1)[0]
        if len(infected_idx) == 0:
            break

        # --- transmission ---
        # All infected agents contact n_con random others simultaneously
        n_inf = len(infected_idx)
        targets = rng.integers(0, N_AGENTS, size=(n_inf, n_con))
        # Bernoulli draw for each contact
        transmits = rng.random(size=(n_inf, n_con)) < inf_rate

        # Collect newly infected (only those currently susceptible)
        new_infected = set()
        for i in range(n_inf):
            for j in range(n_con):
                t = targets[i, j]
                if transmits[i, j] and state[t] == 0:
                    new_infected.add(t)

        # --- recovery ---
        recovers = rng.random(size=n_inf) < rec_rate
        for i, idx in enumerate(infected_idx):
            if recovers[i]:
                state[idx] = 2  # R

        # Apply new infections after recovery (simultaneous update)
        for t in new_infected:
            if state[t] == 0:   # still susceptible after recovery pass
                state[t] = 1

    total_infected = int(np.sum(state != 0))  # I + R
    return total_infected / N_AGENTS


def _mean_run(params: dict, base_seed: int) -> float:
    """Average run() over N_SEEDS starting from base_seed."""
    return float(np.mean([run(params, base_seed + s) for s in range(N_SEEDS)]))


# ── Sobol design ─────────────────────────────────────────────────────────────

problem = {
    "num_vars": 3,
    "names":    ["infection_rate", "recovery_rate", "n_contacts"],
    "bounds":   [[0.01, 0.50], [0.05, 0.40], [2.0, 20.0]],
}

N_BASE = 1024   # Saltelli gives N_BASE*(2k+2) = 8192 model evaluations

print(f"Generating Saltelli sample  (N_BASE={N_BASE}, k=3) …")
param_values = saltelli.sample(problem, N_BASE, calc_second_order=False)
print(f"  Total model evaluations: {len(param_values)} "
      f"(× {N_SEEDS} reps each = {len(param_values)*N_SEEDS} ABM runs)\n")

# ── Evaluate ─────────────────────────────────────────────────────────────────

print("Running ABM … (this takes ~30–60 s on a modern laptop)")
Y = np.empty(len(param_values))
for i, pv in enumerate(param_values):
    params = dict(
        infection_rate = pv[0],
        recovery_rate  = pv[1],
        n_contacts     = pv[2],
    )
    Y[i] = _mean_run(params, base_seed=i * N_SEEDS)
    if (i + 1) % 500 == 0:
        print(f"  … {i+1}/{len(param_values)} done")

print("Done.\n")

# ── Sobol analysis ────────────────────────────────────────────────────────────

Si = sobol.analyze(problem, Y, calc_second_order=False, print_to_console=False)

names      = problem["names"]
S1         = Si["S1"]
S1_conf    = Si["S1_conf"]
ST         = Si["ST"]
ST_conf    = Si["ST_conf"]
interaction = ST - S1   # variance due to interactions with other parameters

# ── Print results ─────────────────────────────────────────────────────────────

print("=" * 60)
print("  Sobol Global Sensitivity Analysis — SIR outbreak size")
print("=" * 60)
print(f"  Population N={N_AGENTS:,}, {N_SEEDS} reps/point, {N_BASE} base samples")
print()

header = f"{'Parameter':<20} {'S1':>8} {'±95%':>8} {'ST':>8} {'±95%':>8} {'interact':>10}"
print(header)
print("-" * len(header))
for i, name in enumerate(names):
    print(f"{name:<20} {S1[i]:>8.3f} {S1_conf[i]:>8.3f} "
          f"{ST[i]:>8.3f} {ST_conf[i]:>8.3f} {interaction[i]:>10.3f}")

print()
total_S1 = S1.sum()
print(f"  Sum of S1 = {total_S1:.3f}  "
      f"({'≈1 ✓ little interaction' if total_S1 > 0.85 else 'sum < 1 → interactions present'})")

print()
print("─" * 60)
print("  INTERPRETATION")
print("─" * 60)
ranked = sorted(zip(names, S1, ST, interaction), key=lambda x: x[3], reverse=True)  # by ST
for name, s1, st, iact in sorted(ranked, key=lambda x: x[2], reverse=True):
    label = "★ dominant" if st > 0.5 else ("  moderate" if st > 0.1 else "  minor   ")
    print(f"  {label}  {name:<20}  ST={st:.3f}  S1={s1:.3f}  interact={iact:.3f}")

print()
# Additional diagnostics
print("  Output stats across the design:")
print(f"    mean outbreak fraction : {Y.mean():.3f}")
print(f"    std                    : {Y.std():.3f}")
print(f"    min / max              : {Y.min():.3f} / {Y.max():.3f}")
print("=" * 60)
