#!/usr/bin/env python3
"""
SIR ABM sensitivity analysis demo.

Runs:
  1. Replication convergence check (how many runs per sample point do we need?)
  2. Morris screening (cheap — which params are negligible?)
  3. Sobol indices (expensive — precise variance decomposition)

Model: stochastic SIR on a well-mixed population of 1000 agents.
  - infection_rate: per-contact transmission probability
  - recovery_rate:  per-step recovery probability for infected agents
  - n_contacts:     number of random contacts each susceptible agent makes per step
"""
import random
import sys
import os

# ── SIR model ─────────────────────────────────────────────────────────────────
N_AGENTS = 1000
N_STEPS  = 200

def run(params: dict, seed: int) -> float:
    """One replication. Returns final infected count (cumulative recovered + current I)."""
    rng = random.Random(seed)
    infection_rate = params["infection_rate"]
    recovery_rate  = params["recovery_rate"]
    n_contacts     = int(round(params["n_contacts"]))

    # States: 0=S, 1=I, 2=R
    states = [0] * N_AGENTS
    # Seed one infected agent
    states[rng.randrange(N_AGENTS)] = 1

    total_ever_infected = 1

    for _ in range(N_STEPS):
        infected_indices = [i for i, s in enumerate(states) if s == 1]
        if not infected_indices:
            break

        new_states = states[:]

        # Susceptible agents make n_contacts random contacts
        for i, s in enumerate(states):
            if s == 0:
                contacts = rng.choices(range(N_AGENTS), k=n_contacts)
                for c in contacts:
                    if states[c] == 1 and rng.random() < infection_rate:
                        new_states[i] = 1
                        total_ever_infected += 1
                        break  # one new infection per step per agent

        # Infected agents recover
        for i in infected_indices:
            if rng.random() < recovery_rate:
                new_states[i] = 2

        states = new_states

    return float(total_ever_infected)


# ── Problem definition ────────────────────────────────────────────────────────
problem = {
    "num_vars": 3,
    "names":  ["infection_rate", "recovery_rate", "n_contacts"],
    "bounds": [[0.01, 0.5], [0.05, 0.4], [2, 20]],
}

# ── Step 1: replication convergence ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from replication_convergence import replication_convergence

print("=" * 60)
print("STEP 1 — Replication convergence (mid-space parameter point)")
print("=" * 60)
mid_params = {"infection_rate": 0.1, "recovery_rate": 0.15, "n_contacts": 8}

def model_fixed_params(seed):
    return run(mid_params, seed)

result = replication_convergence(model_fixed_params, max_reps=300, tol=0.01, window=20, verbose=False)
reps_needed = result["recommended_reps"] or 20
print(f"  Recommended reps at mid-space:  {reps_needed}")
print(f"  Final mean output:              {result['final_mean']:.1f}")
print(f"  Final CV:                       {result['final_cv']:.3f}")
print(f"  Final SEM:                      {result['final_sem']:.2f}")

# Cap reps for sensitivity analysis so it stays fast; use at least 5
SA_REPS = max(5, min(reps_needed, 10))
print(f"\n  Using {SA_REPS} reps per SA sample point (capped for speed).")
print("\n  NOTE: Re-run convergence near the epidemic threshold (low infection_rate,")
print("  high recovery_rate) — variance there is much larger.\n")

# ── Step 2: Morris screening ──────────────────────────────────────────────────
from sensitivity_analysis import morris_screen, sobol_analyze

print("=" * 60)
print("STEP 2 — Morris elementary-effects screening")
print("=" * 60)
morris_si = morris_screen(run, problem, trajectories=30, reps=SA_REPS)

# ── Step 3: Sobol variance decomposition ─────────────────────────────────────
print()
print("=" * 60)
print("STEP 3 — Sobol variance-based indices (n=512)")
print("=" * 60)
sobol_si = sobol_analyze(run, problem, n=512, reps=SA_REPS)

# ── Step 4: interpretation ────────────────────────────────────────────────────
import numpy as np

print()
print("=" * 60)
print("INTERPRETATION")
print("=" * 60)

names    = problem["names"]
mu_star  = morris_si["mu_star"]
sigma    = morris_si["sigma"]
S1       = sobol_si["S1"]
ST       = sobol_si["ST"]
S1_conf  = sobol_si["S1_conf"]
ST_conf  = sobol_si["ST_conf"]

order = np.argsort(ST)[::-1]

for k in order:
    n    = names[k]
    flag = ""
    if sigma[k] / (mu_star[k] + 1e-9) > 1.5:
        flag = "  ← strong non-linearity / interactions"
    elif mu_star[k] < 0.05 * np.max(mu_star):
        flag = "  ← NEGLIGIBLE (can fix this parameter)"
    print(f"  {n:<20}  Morris mu*={mu_star[k]:.3f}  "
          f"Sobol S1={S1[k]:.3f}±{S1_conf[k]:.3f}  "
          f"ST={ST[k]:.3f}±{ST_conf[k]:.3f}{flag}")

s1_sum = float(np.sum(S1))
print(f"\n  sum(S1) = {s1_sum:.3f}")
if s1_sum < 0.7:
    print("  → Well below 1: interactions between parameters account for a "
          "substantial share of output variance. ST >> S1 parameters are")
    print("    acting mainly through their interactions with others.")
elif s1_sum >= 0.9:
    print("  → Close to 1: parameters act mostly additively; interactions are weak.")
else:
    print("  → Moderate interaction effects present.")

print()
print("  Practical take:")
for k in order:
    n   = names[k]
    dom = ST[k] / (np.sum(ST) + 1e-9)
    if mu_star[k] < 0.05 * np.max(mu_star):
        print(f"  - {n}: NEGLIGIBLE — safe to fix at any value in range.")
    elif sigma[k] / (mu_star[k] + 1e-9) > 1.5 and (ST[k] - S1[k]) > 0.05:
        print(f"  - {n}: ~{dom*100:.0f}% of total-effect variance, acting largely "
              "through interactions — effect depends on other params.")
    else:
        print(f"  - {n}: ~{dom*100:.0f}% of total-effect variance, mostly direct effect.")
