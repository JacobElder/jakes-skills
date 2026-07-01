# Enemy AI & Pathfinding

Most action, roguelike, and shooter games live or die on how enemies behave and move. Generated code tends to do one of two bad things: give every enemy an independent A* path to the player (which melts the CPU and makes them clump into a single-file conga line), or hardcode "move toward player" with no avoidance, no spacing, and no readability. This file covers the layers that fix both, with the right tool for each scale.

## Contents
- Separate the two layers: decide vs. move
- Decision-making: FSM, behavior trees, utility AI
- Steering behaviors (organic movement)
- The "don't pile up" problem
- Pathfinding: A*, navmesh, and when to use them
- Flow fields: the answer for many-agents-one-target
- Targeting, aggro, and perception
- Performance for many agents
- Make it fun, not optimal

## Separate the two layers: decide vs. move

Keep **what to do** (the decision/brain layer — chase, flee, attack, patrol) separate from **how to get there** (the movement layer — steering, pathfinding). Conflating them produces tangled code where changing the chase logic breaks the wall-avoidance. The brain outputs an *intent* ("go to point X" / "attack target T"); the movement layer realizes it. This separation is what lets you reuse the same steering for ten different enemy brains.

## Decision-making: FSM, behavior trees, utility AI

Pick the lightest tool that holds the behavior:

- **Finite state machine (default for small games).** Idle → Patrol → Chase → Attack → Flee, with explicit transitions. Clean, debuggable, and enough for the vast majority of enemies. Use the FSM structure from `architecture.md`. Reach past it only when the state count and shared-transition logic genuinely hurt.
- **Behavior tree.** When an FSM's transitions explode into spaghetti (every state needs to check "am I dead / stunned / out of range"), a behavior tree composes behavior from reusable nodes (sequences, selectors, conditions, actions) with priority fallback. Better for richer enemies and bosses. More machinery — don't pay for it on a slime that just walks left.
- **Utility AI.** When the enemy should *weigh* options ("how much do I want to heal vs. attack vs. retreat right now?"), score each action from the game state and pick the highest. Good for sims and nuanced opponents. Overkill for most arcade enemies.
- **GOAP / planners.** Mentioned only to wave off: planning systems are almost always overkill for a small game. If you're tempted, you probably want a behavior tree.

Opinionated default: **FSM for ordinary enemies, behavior tree for bosses and complex actors, utility AI only when choices are genuinely tradeoffs.**

## Steering behaviors (organic movement)

Craig Reynolds' steering behaviors give lifelike movement by computing a *steering force* each frame rather than snapping toward a target. The staples:

- **Seek / Flee** — accelerate toward / away from a point.
- **Arrive** — seek that eases to a stop at the target (no overshoot jitter).
- **Pursue / Evade** — seek/flee the target's *predicted future* position (lead it), so chasers feel smart.
- **Wander** — smooth idle roaming (jitter a point on a small circle ahead).
- **Obstacle avoidance** — steer around obstacles detected by a feeler/whisker ahead.
- **Separation, Cohesion, Alignment** — the three boids rules; combined they give flocking and, crucially, keep a crowd from overlapping.

Combine multiple behaviors by **weighted sum** (cheap, can cancel out) or **priority** (use the highest-priority non-zero force; better for "avoid wall *then* chase"). Steering belongs in the fixed-step update and uses accel/decel like a character controller (`collision-and-physics.md`) — that's what makes enemies feel weighty rather than robotic.

## The "don't pile up" problem

When many enemies chase one player, naive "move toward player" stacks them all on the same pixel into one super-enemy. The fix is **separation steering**: each enemy also pushes gently away from nearby enemies, so they spread into a natural crowd around the target. Back the "nearby enemies" query with the spatial grid from `collision-and-physics.md`, not an all-pairs scan. Separation + a shared flow field (below) is the standard recipe for good-looking hordes.

## Pathfinding: A*, navmesh, and when to use them

When enemies must navigate *around walls* (not just open arenas), you need pathfinding:

- **A\*** on a grid is the workhorse: finds the shortest path on a tile graph with a heuristic. Fine for a handful of agents, turn-based games, or one-off path requests.
- **Navmesh** (navigation mesh) suits continuous/3D space and is what engines provide: Godot `NavigationAgent2D/3D` + `NavigationServer`, Unity `NavMesh`/`NavMeshAgent`, Bevy via crates. Prefer the engine's navmesh over hand-rolling A* for anything non-trivial — it handles funneling, off-mesh links, and agent radius.
- **Don't path every frame.** Compute a path on a target change or on a timer (e.g., re-path 2–4×/sec), cache it, and *steer along* the cached path with the movement layer. Per-frame A* for every enemy is the classic performance killer.
- **Don't path at all when you don't need to.** Open arena with no walls? Pure steering (seek + separation + obstacle avoidance) is cheaper and smoother than pathfinding.

## Flow fields: the answer for many-agents-one-target

This is the technique generated code reliably misses. When you have **hundreds of agents all heading to the same goal** (survivors-like, tower-defense creeps, zombie horde), do **not** run A* per agent. Instead compute a **flow field** (a.k.a. vector-field / Dijkstra-map pathfinding) once:

1. From the goal cell, run a breadth-first / Dijkstra pass over the grid to get each cell's distance-to-goal (an "integration field"), respecting walls.
2. For each cell, store the direction toward its lowest-distance neighbor — a grid of arrows pointing "downhill" to the goal.
3. Every agent just **samples the arrow in its current cell** and steers along it. O(1) per agent.

Cost is one field computation per goal change (or per few frames if the goal moves), shared by *all* agents — versus N separate A* searches. Layer separation steering on top so they fan out. For a Vampire-Survivors-like, this is the difference between 50 enemies and 2,000. Recompute the field when the player moves enough to matter (e.g., crosses a cell, or on a short timer), not every frame.

## Targeting, aggro, and perception

- **Target selection:** nearest, lowest-health, highest-threat, or in-line-of-sight. Use a **range query against the spatial grid** ("enemies/targets within R"), not a full scan.
- **Perception:** sight (range + field-of-view cone + a line-of-sight raycast so walls block vision), hearing (radius around noise events). Gate aggro on perception so enemies don't omnisciently track through walls — that reads as unfair.
- **Aggro/threat:** for group AI, a simple threat table (who dealt damage / is closest) decides focus. Add hysteresis so they don't flip targets every frame.

## Performance for many agents

When "lots of enemies" is the ask, the levers, in order: **shared flow field** instead of per-agent pathing; **spatial grid** for all "who's near me" queries; **time-slice the brains** (run each enemy's decision logic every few frames on a rotating schedule, not all every frame); **LOD AI** (distant/off-screen enemies think and animate less); and **pool** the enemy instances (`collision-and-physics.md`). Movement can still run every fixed step even when decisions are time-sliced.

## Make it fun, not optimal

The goal is an enemy that's *satisfying to fight*, not one that plays perfectly — a pathfinding-perfect, frame-perfect-aiming enemy is miserable. Build in:

- **Telegraphing / anticipation** — a wind-up before attacks (rear back, flash, sound) so the player can react. This is `game-feel.md` anticipation doing double duty as fairness.
- **Reaction time** — a beat between perceiving and acting, so players can juke.
- **Imperfect aim/prediction** — add spread or lead error; perfect aim feels cheap.
- **Readable states** — the player should *see* whether an enemy is idle, alerted, or attacking (animation/color/sound per state).
- **Tunable everything** — aggro range, speed, reaction time, attack windup as exposed data (`architecture.md`), because enemy feel is tuned by playtesting like everything else.
