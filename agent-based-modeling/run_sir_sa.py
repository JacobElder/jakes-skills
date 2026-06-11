#!/usr/bin/env python3
"""
SIR ABM global sensitivity analysis.

Model: 500 agents, random contact process.
  - infection_rate  : prob a contact with an infected agent infects a susceptible
  - recovery_rate   : prob an infected agent recovers each tick
  - n_contacts      : number of random agents each infected agent contacts per tick

Returns: total fraction of population ever infected (outbreak size).

Swap in your own run(params, seed) below and rerun.
"""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from scripts.replication_convergence import replication_convergence
from scripts.sensitivity_analysis import morris_screen, sobol_analyze

# ── SIR model ────────────────────────────────────────────────────────────────

N_AGENTS    = 500
N_INITIAL_I = 5
MAX_STEPS   = 2000

def run(params: dict, seed: int) -> float:
    """One SIR replication. Returns fraction of population ever infected."""
    rng = random.Random(seed)
    ir  = params["infection_rate"]
    rr  = params["recovery_rate"]
    nc  = int(round(params["n_contacts"]))

    S = set(range(N_AGENTS))
    I = set(rng.sample(list(S), N_INITIAL_I))
    S -= I
    R: set = set()

    for _ in range(MAX_STEPS):
        if not I:
            break
        new_I: set = set()
        new_R: set = set()
        for agent in I:
            # recovery
            if rng.random() < rr:
                new_R.add(agent)
            # contacts
            contacts = rng.choices(list(S | I | R), k=nc)
            for c in contacts:
                if c in S and rng.random() < ir:
                    new_I.add(c)
        I = (I - new_R) | new_I
        S -= new_I
        R |= new_R

    ever_infected = N_AGENTS - len(S)
    return ever_infected / N_AGENTS


# ── SA problem definition ─────────────────────────────────────────────────────

problem = {
    "num_vars": 3,
    "names":  ["infection_rate", "recovery_rate", "n_contacts"],
    "bounds": [[0.01, 0.5], [0.05, 0.4], [2, 20]],
}

# ── Step 1: how many reps do we need? ────────────────────────────────────────

print("=" * 60)
print("STEP 1 — Replication convergence (midpoint params)")
print("=" * 60)

MID = {"infection_rate": 0.25, "recovery_rate": 0.22, "n_contacts": 11}

result = replication_convergence(
    lambda seed: run(MID, seed),
    max_reps=300,
    tol=0.01,
    window=20,
    verbose=False,
)
reps_needed = result["recommended_reps"] or 30
print(f"  converged:        {result['converged']}")
print(f"  recommended_reps: {reps_needed}")
print(f"  final mean:       {result['final_mean']:.4g}  (fraction infected)")
print(f"  final CV:         {result['final_cv']:.4g}")
print(f"  final SEM:        {result['final_sem']:.4g}")
print()
print("  NOTE: variance near tipping points (R0 ≈ 1) will be higher.")
print("  Capping SA reps at max(reps_needed, 8) for speed; raise for publication.")

SA_REPS = max(reps_needed, 8)

# ── Step 2: Morris screening ──────────────────────────────────────────────────

print()
print("=" * 60)
print(f"STEP 2 — Morris screening (trajectories=30, reps={SA_REPS})")
print("=" * 60)

morris_si = morris_screen(run, problem, trajectories=30, reps=SA_REPS)

# ── Step 3: Sobol variance decomposition ─────────────────────────────────────

print()
print("=" * 60)
print(f"STEP 3 — Sobol indices (n=256, reps={SA_REPS})")
print("=" * 60)

sobol_si = sobol_analyze(run, problem, n=256, reps=SA_REPS)

# ── Step 4: plain-English interpretation ─────────────────────────────────────

import numpy as np

print()
print("=" * 60)
print("INTERPRETATION")
print("=" * 60)

names  = problem["names"]
mu_star = morris_si["mu_star"]
sigma   = morris_si["sigma"]
S1      = sobol_si["S1"]
ST      = sobol_si["ST"]
S1_conf = sobol_si["S1_conf"]
ST_conf = sobol_si["ST_conf"]

order = np.argsort(ST)[::-1]
for rank, k in enumerate(order, 1):
    interaction = "acts mainly through INTERACTIONS" if ST[k] > 2 * max(S1[k], 0.01) else "mostly additive effect"
    print(f"  #{rank}  {names[k]:<18}  ST={ST[k]:.3f}±{ST_conf[k]:.3f}  S1={S1[k]:.3f}±{S1_conf[k]:.3f}  ({interaction})")

s1_sum = float(np.sum(S1))
print()
print(f"  sum(S1) = {s1_sum:.3f}")
if s1_sum < 0.7:
    print("  → Strong interaction effects: parameters don't drive output independently.")
elif s1_sum < 0.9:
    print("  → Moderate interactions present.")
else:
    print("  → Mostly additive: parameters act largely independently.")

print()
print("  Morris note:")
for k, name in enumerate(names):
    tag = "non-linear / interacting" if sigma[k] > 0.5 * mu_star[k] and mu_star[k] > 0.01 \
          else ("NEGLIGIBLE — safe to fix" if mu_star[k] < 0.05 * max(mu_star) else "roughly linear")
    print(f"    {name:<18}  mu*={mu_star[k]:.4g}  sigma={sigma[k]:.4g}  → {tag}")
