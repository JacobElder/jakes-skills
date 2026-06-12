#!/usr/bin/env python3
"""
forager_landscape.py — Foragers competing for patchily distributed food.

N foragers search a toroidal L×L grid for food distributed in K Gaussian
patches. Competition is purely exploitative: foragers that land on the same
cell after movement share the available food proportionally. Each forager uses
a softmax gradient-climb rule, weighting the food levels of its 8 Moore
neighbors and its current cell to choose a destination each step.

See the companion ODD description (forager_landscape_odd.md) for the full
model specification. Parameters here match that document exactly.

Usage:
    python forager_landscape.py                     # one run, prints summary
    python forager_landscape.py --steps 1000 --plot # longer run with figures
    python forager_landscape.py --seed 7 --n-foragers 30 --beta 4.0
"""
from __future__ import annotations

import argparse
import math
import warnings
from collections import Counter, defaultdict

import numpy as np

try:
    import mesa
    from mesa.space import MultiGrid
    from mesa.datacollection import DataCollector
except ImportError as e:
    raise SystemExit("Mesa is required: pip install mesa --break-system-packages") from e

warnings.filterwarnings("ignore", message=".*`seed` keyword argument is deprecated.*")


# ── Default parameters  ─────────────────────────────────────────────────────
# All names and values correspond to the ODD description exactly.
DEFAULTS: dict = dict(
    grid_size      = 50,    # L: one side of the square toroidal grid (cells)
    n_foragers     = 25,    # N: initial number of foragers
    n_patches      = 8,     # K: number of food patches
    patch_sigma    = 5.0,   # σ: Gaussian SD of each patch (cells)
    food_max       = 10.0,  # F_max: cell carrying capacity (food units)
    regrowth_rate  = 0.05,  # r: logistic regrowth coefficient (per step)
    intake_rate    = 1.0,   # α: max food a single forager consumes per step
    metabolic_cost = 0.3,   # c: energy deducted per forager per step
    energy_init    = 10.0,  # E₀: starting energy for every forager
    energy_max     = 20.0,  # E_max: energy ceiling (surplus is discarded)
    beta           = 2.0,   # β: softmax selectivity (higher → more greedy)
)


# ── Agent ────────────────────────────────────────────────────────────────────

class ForagerAgent(mesa.Agent):
    """A single forager. Carries energy; chooses a move each step."""

    def __init__(self, model: "ForagerLandscape", energy: float) -> None:
        super().__init__(model)
        self.energy = energy
        self._next_pos: tuple[int, int] | None = None

    def choose_destination(self, food_snapshot: np.ndarray) -> None:
        """
        Softmax gradient-climb over the Moore neighborhood + current cell.

        Probability of choosing cell j:
            p_j ∝ exp(β · F_j)
        where F_j is the food level in the pre-step snapshot. Subtracting the
        maximum before exponentiation prevents overflow without changing the
        distribution.
        """
        L = self.model.grid_size
        x, y = self.pos
        candidates: list[tuple[int, int, float]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx = (x + dx) % L
                ny = (y + dy) % L
                candidates.append((nx, ny, food_snapshot[nx, ny]))
        foods = np.array([c[2] for c in candidates], dtype=float)
        foods -= foods.max()
        weights = np.exp(self.model.beta * foods)
        weights /= weights.sum()
        idx = int(self.model.np_rng.choice(len(candidates), p=weights))
        self._next_pos = (candidates[idx][0], candidates[idx][1])


# ── Model ────────────────────────────────────────────────────────────────────

class ForagerLandscape(mesa.Model):
    """
    Toroidal landscape with patchily distributed food and competing foragers.

    Keyword parameters override DEFAULTS; all others keep their default values.
    Provide `seed` for reproducibility.
    """

    def __init__(self, *, seed: int | None = None, **kwargs) -> None:
        super().__init__(seed=seed)
        params = {**DEFAULTS, **{k: v for k, v in kwargs.items() if k in DEFAULTS}}
        for k, v in params.items():
            setattr(self, k, v)
        self.np_rng = np.random.default_rng(seed)

        self.food = self._init_food()
        self.grid = MultiGrid(self.grid_size, self.grid_size, torus=True)
        for _ in range(self.n_foragers):
            agent = ForagerAgent(self, energy=self.energy_init)
            x = self.random.randrange(self.grid_size)
            y = self.random.randrange(self.grid_size)
            self.grid.place_agent(agent, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "n_alive":     lambda m: len(list(m.agents)),
                "mean_energy": lambda m: (
                    float(np.mean([a.energy for a in m.agents]))
                    if list(m.agents) else 0.0
                ),
                "total_food":  lambda m: float(m.food.sum()),
                "pielou_J":    _pielou_evenness,
            }
        )
        self.running = True
        self.datacollector.collect(self)

    # ── Private helpers ──────────────────────────────────────────────────────

    def _init_food(self) -> np.ndarray:
        """
        Superposition of K toroidal Gaussian bumps, clipped to [0, F_max].

        Each patch centre is drawn uniformly; the Gaussian uses toroidal
        (minimum-image) distance so patches near an edge wrap correctly.
        """
        L = self.grid_size
        xs, ys = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
        food = np.zeros((L, L))
        for _ in range(self.n_patches):
            cx = self.random.randrange(L)
            cy = self.random.randrange(L)
            dx = np.minimum(np.abs(xs - cx), L - np.abs(xs - cx))
            dy = np.minimum(np.abs(ys - cy), L - np.abs(ys - cy))
            food += self.food_max * np.exp(
                -(dx ** 2 + dy ** 2) / (2.0 * self.patch_sigma ** 2)
            )
        return np.clip(food, 0.0, self.food_max)

    # ── Scheduling ───────────────────────────────────────────────────────────

    def step(self) -> None:
        """
        One time step — five processes in order:
          1. Food regrowth (all cells, synchronous)
          2. Movement decisions (all foragers see pre-step food snapshot)
          3. Movement execution (all foragers move simultaneously)
          4. Consumption (foragers sharing a cell split food proportionally)
          5. Metabolic cost + mortality
        """
        # 1. Logistic regrowth
        self.food += self.regrowth_rate * self.food * (1.0 - self.food / self.food_max)
        np.clip(self.food, 0.0, self.food_max, out=self.food)

        # 2. Movement decisions — snapshot prevents decision/outcome coupling
        snapshot = self.food.copy()
        agents = list(self.agents)
        for agent in agents:
            agent.choose_destination(snapshot)

        # 3. Move all foragers
        for agent in agents:
            self.grid.move_agent(agent, agent._next_pos)  # type: ignore[arg-type]

        # 4. Proportional food sharing on each occupied cell
        cell_map: dict[tuple[int, int], list[ForagerAgent]] = defaultdict(list)
        for agent in agents:
            cell_map[agent.pos].append(agent)  # type: ignore[index]

        for pos, occupants in cell_map.items():
            n_f = len(occupants)
            available = float(self.food[pos[0], pos[1]])
            consumed = min(n_f * self.intake_rate, available)
            self.food[pos[0], pos[1]] -= consumed
            share = consumed / n_f
            for agent in occupants:
                agent.energy = min(agent.energy + share, self.energy_max)

        # 5. Metabolic cost then mortality
        dead = []
        for agent in agents:
            agent.energy -= self.metabolic_cost
            if agent.energy <= 0.0:
                dead.append(agent)
        for agent in dead:
            self.grid.remove_agent(agent)
            agent.remove()

        if not list(self.agents):
            self.running = False

        self.datacollector.collect(self)


# ── Observation helper ───────────────────────────────────────────────────────

def _pielou_evenness(model: ForagerLandscape) -> float:
    """
    Pielou's J for the spatial distribution of foragers across occupied cells.

    J = H / ln(S), where H is Shannon entropy and S is the number of
    occupied cells. J = 1: perfectly even; J → 0: all foragers on one cell.
    Returns NaN when no foragers remain.
    """
    agents = list(model.agents)
    if not agents:
        return float("nan")
    counts = Counter(a.pos for a in agents)
    if len(counts) == 1:
        return 0.0
    total = sum(counts.values())
    probs = np.array(list(counts.values()), dtype=float) / total
    H = -float(np.sum(probs * np.log(probs + 1e-15)))
    return H / math.log(len(counts))


# ── Public entry point ───────────────────────────────────────────────────────

def run_once(seed: int = 42, n_steps: int = 500, **params) -> dict:
    """
    Run one replication; return summary statistics and the full time-series df.

    This is the function shape the bundled scripts expect:
      - replication_convergence.py: wrap as  lambda s: run_once(s)["mean_energy"]
      - sensitivity_analysis.py:    problem dict over DEFAULTS keys; call
                                    run_once(seed=seed, **param_dict)["mean_energy"]
    """
    model = ForagerLandscape(seed=seed, **params)
    for _ in range(n_steps):
        if not model.running:
            break
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    return {
        "final_n_alive":    int(df["n_alive"].iloc[-1]),
        "mean_energy":      float(df["mean_energy"].mean()),
        "survival_steps":   int(df["n_alive"].iloc[1:].gt(0).sum()),
        "final_total_food": float(df["total_food"].iloc[-1]),
        "final_pielou_J":   float(df["pielou_J"].dropna().iloc[-1])
                            if df["pielou_J"].notna().any() else float("nan"),
        "df": df,
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description="Forager landscape ABM — one run")
    p.add_argument("--steps",       type=int,   default=500)
    p.add_argument("--seed",        type=int,   default=42)
    p.add_argument("--n-foragers",  type=int,   default=DEFAULTS["n_foragers"],
                   dest="n_foragers")
    p.add_argument("--beta",        type=float, default=DEFAULTS["beta"])
    p.add_argument("--regrowth",    type=float, default=DEFAULTS["regrowth_rate"],
                   dest="regrowth_rate")
    p.add_argument("--plot",        action="store_true")
    args = p.parse_args()

    result = run_once(
        seed=args.seed,
        n_steps=args.steps,
        n_foragers=args.n_foragers,
        beta=args.beta,
        regrowth_rate=args.regrowth_rate,
    )

    print(f"seed={args.seed}  N={args.n_foragers}  β={args.beta}  "
          f"r={args.regrowth_rate}  T={args.steps}")
    print(f"  surviving foragers (final step): {result['final_n_alive']}")
    print(f"  mean energy (time-averaged):     {result['mean_energy']:.3f}")
    print(f"  steps with at least one forager: {result['survival_steps']}/{args.steps}")
    print(f"  total food remaining (final):    {result['final_total_food']:.1f}")
    print(f"  spatial evenness Pielou J (final): {result['final_pielou_J']:.3f}")
    print("\nOne run is an anecdote — use scripts/replication_convergence.py "
          "and scripts/sensitivity_analysis.py for inference.")

    if args.plot:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed; skipping plots.")
            return
        df = result["df"]
        fig, axes = plt.subplots(2, 2, figsize=(10, 7))
        fig.suptitle(
            f"Forager Landscape ABM  (seed={args.seed}, N={args.n_foragers}, β={args.beta})",
            fontsize=12,
        )
        axes[0, 0].plot(df["n_alive"], color="steelblue")
        axes[0, 0].set(title="Population size", xlabel="Step", ylabel="Foragers alive")

        axes[0, 1].plot(df["mean_energy"], color="darkorange")
        axes[0, 1].set(title="Mean forager energy", xlabel="Step", ylabel="Energy units")

        axes[1, 0].plot(df["total_food"], color="forestgreen")
        axes[1, 0].set(title="Total food on landscape", xlabel="Step", ylabel="Food units")

        axes[1, 1].plot(df["pielou_J"], color="orchid")
        axes[1, 1].set(title="Spatial evenness (Pielou J)",
                       xlabel="Step", ylabel="J  (0 = clustered, 1 = even)")

        plt.tight_layout()
        plt.savefig("forager_landscape_output.png", dpi=150)
        print("Plot saved to forager_landscape_output.png")
        plt.show()


if __name__ == "__main__":
    main()
