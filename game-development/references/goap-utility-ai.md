# GOAP and Utility AI

FSMs work for enemies with fewer than 8 clear states. Behavior Trees work when behavior is hierarchical and subtrees are reusable. When enemies need to dynamically weigh trade-offs between many actions — or plan multi-step sequences to achieve goals — you need Utility AI or GOAP.

Neither is always the right answer. Utility AI is the right default for most games with complex enemies. GOAP is a specialized tool for emergent multi-step planning.

## Contents
- The three AI tiers and when to use each
- Utility AI: scoring, action selection
- Utility AI GDScript implementation
- Tuning utility scores
- GOAP: world state, actions, planning
- GOAP planner implementation
- Combining BT + Utility AI
- Combining BT + GOAP
- Performance
- Common mistakes

## The three AI tiers and when to use each

**FSM** — best for: < 8 states, explicit transitions, simple enemies (slimes, turrets, patrol guards). Cost: minimal. Break point: transition logic becomes O(n²); cross-cutting concerns (death, stun, flee) require checking from every state.

**Behavior Tree** — best for: hierarchical behavior with shared subtrees; cross-cutting concerns via Decorator nodes; complex enemies where subtree reuse matters. Cost: moderate (tick overhead). Break point: when the enemy's actions are genuine trade-offs between continuous options (attack vs flee vs heal); BTs are bad at "which of these 10 actions is most appropriate right now?"

**Utility AI** — best for: enemies that weigh multiple continuous options (attack vs retreat vs take cover vs heal — the best choice varies smoothly with game state). Cost: score evaluation per tick interval. Break point: when actions require planning multi-step sequences to achieve.

**GOAP** — best for: enemies that need to reason "I have no ammo → I must find ammo → then take cover → then reload → then attack" as a planned sequence. Cost: A* search over state space. Use sparingly. F.E.A.R. AI is the canonical example.

**Decision rule**: Start FSM. Move to BT when FSM transitions get tangled. Add Utility AI inside BT combat nodes when choices have continuous trade-offs. Reach for GOAP only if enemies genuinely need multi-step planning.

## Utility AI: scoring and action selection

Each action has a `score(actor)` method that returns a float in [0, 1]. The agent evaluates all available actions each tick, picks the highest-scoring one, and executes it.

```gdscript
# UtilityAction.gd — base class
class_name UtilityAction
extends RefCounted

func can_use(actor: Node) -> bool:
    return true  # override with prerequisites

func score(actor: Node) -> float:
    return 0.0   # override with scoring logic

func execute(actor: Node) -> void:
    pass         # override with action behavior
```

Concrete actions:

```gdscript
# AttackAction.gd
class_name AttackAction
extends UtilityAction

func can_use(actor: Node) -> bool:
    return actor.target != null and actor.ammo > 0

func score(actor: Node) -> float:
    var distance_score := 1.0 - clamp(actor.distance_to_target / actor.attack_range, 0.0, 1.0)
    var health_score := actor.health / actor.max_health  # prefer to attack when healthy
    return distance_score * 0.7 + health_score * 0.3

# FleeAction.gd
class_name FleeAction
extends UtilityAction

func score(actor: Node) -> float:
    var low_health := 1.0 - (actor.health / actor.max_health)
    var low_ammo := 1.0 - (float(actor.ammo) / actor.max_ammo)
    return low_health * 0.6 + low_ammo * 0.4

# HealAction.gd
class_name HealAction
extends UtilityAction

func can_use(actor: Node) -> bool:
    return actor.healing_items > 0

func score(actor: Node) -> float:
    return 1.0 - (actor.health / actor.max_health)  # higher score when low health

# TakeCoverAction.gd
class_name TakeCoverAction
extends UtilityAction

func can_use(actor: Node) -> bool:
    return actor.nearest_cover != null

func score(actor: Node) -> float:
    var threat := clamp(actor.received_damage_last_second / 30.0, 0.0, 1.0)
    return threat * 0.8
```

## Utility AI GDScript implementation

```gdscript
# UtilityAgent.gd
class_name UtilityAgent
extends Node

@export var actions: Array[UtilityAction] = []
@export var decision_interval: float = 0.25  # re-evaluate every 0.25 seconds
@export var score_noise: float = 0.05        # small random offset breaks ties

var _current_action: UtilityAction = null
var _decision_timer: float = 0.0

func _physics_process(delta: float) -> void:
    _decision_timer -= delta
    if _decision_timer <= 0.0:
        _decision_timer = decision_interval
        _decide()

    if _current_action:
        _current_action.execute(owner)

func _decide() -> void:
    var best_action: UtilityAction = null
    var best_score := -1.0

    for action in actions:
        if not action.can_use(owner):
            continue
        var s := action.score(owner) + randf_range(0.0, score_noise)
        if s > best_score:
            best_score = s
            best_action = action

    _current_action = best_action
```

Attach `UtilityAgent` to the enemy node. Set `owner` or pass the actor explicitly. The `decision_interval` of 0.25s means AI re-evaluates 4× per second, not every frame — reduces CPU cost without perceptible lag.

## Tuning utility scores

**All scores must be normalized to [0, 1].** An attack score of 10 cannot be compared to a heal score of 0.8 — the attack always wins regardless of health. Normalize every input:

```gdscript
# WRONG: raw values are incomparable
func score_attack(actor) -> float:
    return 100.0 - actor.distance_to_target  # distance in world units

# CORRECT: normalized
func score_attack(actor) -> float:
    return 1.0 - clamp(actor.distance_to_target / actor.attack_range, 0.0, 1.0)
```

**Score noise prevents mechanical behavior.** Without noise, enemies with identical state make identical decisions. Add `randf_range(0, 0.05)` to break ties and produce human-seeming variation.

**Weighted combinations.** Use weighted sums when multiple factors contribute:

```gdscript
func score(actor: Node) -> float:
    var health_w := 0.4
    var distance_w := 0.4
    var ammo_w := 0.2
    var health_score := actor.health / actor.max_health
    var distance_score := 1.0 - clamp(actor.distance / actor.range, 0.0, 1.0)
    var ammo_score := float(actor.ammo) / actor.max_ammo
    return health_score * health_w + distance_score * distance_w + ammo_score * ammo_w
```

Tune weights in the inspector by exporting them as `@export var w_health: float = 0.4`.

## GOAP: world state, actions, planning

GOAP represents the world as a flat dictionary of boolean facts:

```gdscript
var world_state := {
    "has_ammo": true,
    "enemy_visible": true,
    "in_cover": false,
    "enemy_dead": false,
    "at_ammo_cache": false,
}

var goal_state := {"enemy_dead": true}
```

Each action has `preconditions` (required world state), `effects` (state changes after execution), and `cost`:

```gdscript
class_name GOAPAction
extends RefCounted

var action_name: String = ""
var preconditions: Dictionary = {}  # {"has_ammo": true, "enemy_visible": true}
var effects: Dictionary = {}        # {"enemy_dead": true}
var cost: float = 1.0

func is_applicable(state: Dictionary) -> bool:
    for key in preconditions:
        if state.get(key, false) != preconditions[key]:
            return false
    return true

func apply(state: Dictionary) -> Dictionary:
    var new_state := state.duplicate()
    for key in effects:
        new_state[key] = effects[key]
    return new_state

func execute(actor: Node) -> void:
    pass  # override: move to cover, reload, fire, etc.
```

Example action set:

```gdscript
# AttackEnemyAction
preconditions = {"has_ammo": true, "enemy_visible": true}
effects = {"enemy_dead": true}
cost = 1.0

# TakeCoverAction
preconditions = {"enemy_visible": true}
effects = {"in_cover": true}
cost = 2.0

# ReloadAction
preconditions = {"in_cover": true}
effects = {"has_ammo": true}
cost = 1.5

# FindAmmoAction
preconditions = {}
effects = {"has_ammo": true, "at_ammo_cache": true}
cost = 5.0  # high cost — moving to ammo is expensive
```

## GOAP planner implementation

The planner is A* over the space of world states:

```gdscript
class_name GOAPPlanner

static func plan(current_state: Dictionary, goal_state: Dictionary,
                 available_actions: Array[GOAPAction]) -> Array[GOAPAction]:

    # Priority queue: [cost, state, action_sequence]
    var open_list := []
    open_list.append([0.0, current_state, []])

    while not open_list.is_empty():
        # Sort by cost (min-heap behavior)
        open_list.sort_custom(func(a, b): return a[0] < b[0])
        var node := open_list.pop_front()
        var g_cost: float = node[0]
        var state: Dictionary = node[1]
        var plan: Array = node[2]

        # Goal check
        if _satisfies_goal(state, goal_state):
            return plan

        # Expand applicable actions
        for action in available_actions:
            if action.is_applicable(state):
                var new_state := action.apply(state)
                var new_cost := g_cost + action.cost
                var heuristic := _unsatisfied_count(new_state, goal_state)
                open_list.append([new_cost + heuristic, new_state, plan + [action]])

    return []  # no plan found

static func _satisfies_goal(state: Dictionary, goal: Dictionary) -> bool:
    for key in goal:
        if state.get(key, false) != goal[key]:
            return false
    return true

static func _unsatisfied_count(state: Dictionary, goal: Dictionary) -> float:
    var count := 0
    for key in goal:
        if state.get(key, false) != goal[key]:
            count += 1
    return float(count)
```

Execute the plan in sequence on the GOAPAgent. Replan when: the current action fails, world state changes significantly, or a fixed re-evaluate timer fires.

```gdscript
# GOAPAgent.gd
var _plan: Array[GOAPAction] = []
var _current_action_idx := 0

func _physics_process(_delta: float) -> void:
    if _plan.is_empty() or _current_action_idx >= _plan.size():
        _replan()
        return
    var action := _plan[_current_action_idx]
    action.execute(self)
    # Check if action completed (implementation-specific)
    if _action_complete(action):
        _current_action_idx += 1

func _replan() -> void:
    _plan = GOAPPlanner.plan(_get_world_state(), {"enemy_dead": true}, _available_actions)
    _current_action_idx = 0
```

## Combining BT + Utility AI

The most practical pattern for rich enemy AI: BT handles the high-level mode switch (Patrol / Combat / Flee), Utility AI runs inside Combat to choose which combat action.

```
Root Selector
├── [Condition: health < 20%] → FleeSubtree
├── [Condition: enemy_visible] → CombatUtilityLeaf  ← UtilityAgent evaluates here
└── PatrolSubtree
```

`CombatUtilityLeaf` is a BT Action node that delegates to a `UtilityAgent` component each tick. This separates macro-level state (BT's domain) from micro-level action selection (Utility's domain).

## Combining BT + GOAP

GOAP works as a BT leaf: when the BT enters a complex goal (e.g. "acquire ammo"), a GOAPPlannerLeaf node calls `GOAPPlanner.plan()` once, caches the result, and executes actions from the plan sequentially, returning RUNNING until the plan completes or fails.

```gdscript
# GOAPPlannerLeaf.gd — a BT Action node
func _tick(actor: Node) -> Status:
    if _plan.is_empty():
        _plan = GOAPPlanner.plan(actor.get_world_state(), _goal, actor.available_actions)
        if _plan.is_empty():
            return Status.FAILURE  # no plan found

    var action := _plan[_action_idx]
    action.execute(actor)
    if _action_complete(action):
        _action_idx += 1
    if _action_idx >= _plan.size():
        _plan.clear()
        return Status.SUCCESS
    return Status.RUNNING
```

## Performance

- Utility AI: O(n) where n = number of actions. With 10 actions and a 0.25s interval, this is trivially cheap — < 0.01ms per agent.
- GOAP planner: O(b^d) where b = applicable actions per state and d = plan depth. For a 10-action, 5-step plan this is manageable. For 30 actions and 10 steps, it can take 5-20ms. Mitigations:
  - Only replan when world state changes or plan fails.
  - Limit action set per enemy type.
  - Run planner on a Thread for complex goals.
  - Cap search depth.
- Both systems: set `decision_interval` to at least 0.2s. Don't re-evaluate every frame.

## Common mistakes

**Unnormalized scores**: attack score of 100 always beats heal score of 0.8. Normalize everything to [0, 1].

**Replanning every frame in GOAP**: the planner is not free. Cache the plan; replan only on failure or significant world-state change.

**Using GOAP when Utility AI suffices**: if the enemy's decisions are independent per-tick trade-offs (attack vs flee vs heal), Utility AI is 90% simpler to implement and tune. GOAP adds value only when sequencing is needed.

**Ignoring `can_use()`**: scoring an action the enemy can't actually perform (no ammo, no cover nearby) produces a high-score action that immediately fails when executed. Always gate on `can_use()` before scoring.

**Hardcoded weights in score functions**: weights will be tuned dozens of times during development. Export them as `@export var w_health: float = 0.4` from the first iteration.
