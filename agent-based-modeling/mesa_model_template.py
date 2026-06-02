#!/usr/bin/env python3
"""
mesa_model_template.py — A minimal, runnable ABM you can copy and adapt.

This is Schelling's segregation model (the canonical emergence example): agents of
two types sit on a grid; an agent is "happy" if at least a fraction `homophily` of
its occupied-neighbor cells share its type, and relocates to a random empty cell
otherwise. Mild individual preferences produce strong macro-level segregation —
nobody coded "segregate," it emerges. That gap between micro-rules and macro-
outcome is the whole point of ABM.

It is deliberately small but complete, and it demonstrates the pieces every ABM
needs and the ODD elements they map to:
  - an Agent with a decision rule           (ODD: submodels, adaptation, sensing)
  - a Model with a space and a schedule     (ODD: entities, scheduling)
  - explicit, reported stochasticity         (ODD: stochasticity; reproducible seed)
  - a DataCollector measuring an output      (ODD: observation)
  - a main() that runs ONE replication and reports the emergent metric

Written for Mesa 3.x (uses the AgentSet API: model.agents.shuffle_do(...)).
    pip install mesa --break-system-packages

To turn this into a real study, do NOT just run it once. Pair it with the bundled
scripts: wrap run_once() to return your output and feed it to
replication_convergence.py, then define a `problem` and feed a parameterized
version to sensitivity_analysis.py.

    python mesa_model_template.py            # one run, prints the emergent metric
    python mesa_model_template.py --converge # uses the replication helper if present
"""
from __future__ import annotations

import argparse
import warnings

try:
    import mesa
    from mesa.space import SingleGrid
    from mesa.datacollection import DataCollector
except ImportError as e:  # pragma: no cover
    raise SystemExit("Mesa is required: pip install mesa --break-system-packages") from e

# Mesa 3.5+ prefers `rng=` over `seed=` for the Model RNG (a FutureWarning, no
# functional change yet). We keep `seed=` for compatibility across all 3.x and
# silence only that one warning so the template's output stays clean. On newer
# Mesa you can switch the super().__init__ call below to rng=seed.
warnings.filterwarnings("ignore", message=".*`seed` keyword argument is deprecated.*")


class SchellingAgent(mesa.Agent):
    """An agent of a given type that wants enough same-type neighbors."""

    def __init__(self, model, agent_type: int):
        super().__init__(model)
        self.type = agent_type

    def step(self) -> None:
        # SENSING: look at the 8 surrounding cells (Moore neighborhood).
        # NB: neighborhood shape is a *design choice* and a known artefact source —
        # try von Neumann (moore=False) and check your conclusions survive.
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False
        )
        same = sum(1 for n in neighbors if n.type == self.type)
        total = len(neighbors)
        # ADAPTATION / decision rule (a submodel): move if not enough similar.
        if total > 0 and (same / total) < self.model.homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1


class Schelling(mesa.Model):
    """The model: builds the world, schedules agents, collects output."""

    def __init__(self, width=20, height=20, density=0.8, minority_pc=0.3,
                 homophily=0.4, seed=None):
        super().__init__(seed=seed)  # seeding the Model RNG => reproducible run
        self.homophily = homophily
        self.happy = 0
        self.grid = SingleGrid(width, height, torus=True)  # torus => no edge artefacts

        # INITIALIZATION: place agents stochastically on empty cells.
        for _, pos in self.grid.coord_iter():
            if self.random.random() < density:
                agent_type = 1 if self.random.random() < minority_pc else 0
                agent = SchellingAgent(self, agent_type)
                self.grid.place_agent(agent, pos)

        # OBSERVATION: the emergent metric we actually study.
        self.datacollector = DataCollector(
            model_reporters={
                "happy": "happy",
                "segregation": compute_segregation,
            }
        )
        self.running = True
        self.datacollector.collect(self)

    def step(self) -> None:
        self.happy = 0
        # SCHEDULING: shuffle agent order each step (asynchronous activation).
        # Update order is a design choice — report it; it can change results.
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
        if self.happy == len(self.agents):
            self.running = False  # everyone content => converged


def compute_segregation(model) -> float:
    """Mean fraction of same-type neighbors across agents — the macro pattern."""
    fracs = []
    for agent in model.agents:
        neighbors = model.grid.get_neighbors(agent.pos, moore=True, include_center=False)
        if neighbors:
            same = sum(1 for n in neighbors if n.type == agent.type)
            fracs.append(same / len(neighbors))
    return sum(fracs) / len(fracs) if fracs else 0.0


def run_once(seed: int, max_steps: int = 100, **params) -> float:
    """Run ONE replication; return the emergent output of interest (segregation).

    This is the function shape the bundled analysis scripts expect:
    model_fn(seed) -> scalar  (for replication_convergence.py), or wrap it as
    model_fn(param_dict, seed) -> scalar for sensitivity_analysis.py.
    """
    model = Schelling(seed=seed, **params)
    steps = 0
    while model.running and steps < max_steps:
        model.step()
        steps += 1
    return compute_segregation(model)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--homophily", type=float, default=0.4)
    p.add_argument("--converge", action="store_true",
                   help="estimate replications needed (uses replication_convergence.py)")
    args = p.parse_args()

    if args.converge:
        try:
            from replication_convergence import replication_convergence
        except ImportError:
            raise SystemExit("Put replication_convergence.py alongside this file.")
        res = replication_convergence(
            lambda s: run_once(s, homophily=args.homophily), max_reps=300
        )
        print(f"recommended replications: {res['recommended_reps']}  "
              f"(mean segregation {res['final_mean']:.3f}, CV {res['final_cv']:.3f})")
        return

    final = run_once(args.seed, homophily=args.homophily)
    print(f"seed={args.seed} homophily={args.homophily} "
          f"-> emergent segregation index = {final:.3f}")
    print("One run is an anecdote. Use --converge, then run a sensitivity analysis.")


if __name__ == "__main__":
    main()
