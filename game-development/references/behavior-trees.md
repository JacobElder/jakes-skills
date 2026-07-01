# Behavior Trees for Game AI

Finite state machines break down when enemy behavior grows past 6–8 states. The problem is not the states — it's the transitions: every state must check "am I dead? stunned? out of range? player invisible?" and those cross-cutting concerns produce an N×N transition matrix. A guard enemy with Idle, Patrol, Investigate, Alerted, Chase, FlankLeft, FlankRight, Attack, MeleeAttack, Cover, Reload, Flee, and Dead states has 169 possible transition pairs; you'll implement ~40 and spend two weeks debugging the other 129. Behavior trees solve this by expressing behavior as a priority-ordered **tree of reusable nodes** rather than a flat table. The cost is a few hundred lines of infrastructure and a steeper learning curve. Don't pay the cost for a slime with three states.

## When BTs beat FSMs

Pay for a behavior tree when at least two of these are true: the enemy needs more than ~8 distinct states; multiple states share the same interrupt conditions (low-health check appears in 6 states); you need to reuse a subtree across enemy types (patrol logic shared between guard, soldier, and captain); behavior must compose from independent modules a designer can reconfigure. The canonical breaking point: you add "melee enemy starts throwing grenades when backed into a corner" and realize you need to add that corner-check to six existing transition conditions. In a BT, you add one new Selector at the top that checks corner status and routes to the grenade subtree — existing logic is untouched.

FSMs remain correct for enemies with 3–5 states and no cross-cutting interrupts. A vampire bat with Idle → Chase → Attack → Flee doesn't need a BT. An RPG companion NPC with 15 behavior modes does.

## Node types and their semantics

Every BT node has exactly one method: `tick()`. It returns one of three statuses: **SUCCESS**, **FAILURE**, or **RUNNING** (meaning it's in the middle of a multi-frame operation and needs to be ticked again next frame). No other return values. This uniformity is what makes composition possible — a parent node doesn't know or care whether its child is a Condition, an Action, or an entire subtree.

**Sequence** (AND): ticks children left to right. Returns SUCCESS only if *all* children succeed. On the first FAILURE, short-circuits immediately and returns FAILURE without ticking remaining children. On RUNNING, returns RUNNING and remembers which child is running (so next tick resumes there, not at the start). Use a Sequence to express "do A, then B, then C, in order, and stop if any fails."

**Selector** (OR): ticks children left to right. Returns SUCCESS as soon as *any* child succeeds. On the first SUCCESS, short-circuits without ticking remaining children. On all FAILURE, returns FAILURE. Use a Selector to express "try A; if that fails, try B; if that fails, try C." Priority comes from order: the leftmost child is always tried first.

**Decorator**: wraps exactly one child and modifies its behavior or result. Common decorators:
- **Inverter** — flips SUCCESS to FAILURE and vice versa; RUNNING passes through unchanged.
- **Repeater** — ticks the child N times or until it fails, returning RUNNING each intermediate tick.
- **Cooldown** — after the child succeeds, returns FAILURE for a duration (prevents ability spam without cluttering the Action node with timer logic).
- **ForceSuccess / ForceFailure** — always return that status regardless of child result; used to make optional branches always "pass."
- **Timeout** — if child is still RUNNING after N seconds, force FAILURE.

**Leaf nodes** — no children. Two subtypes:
- **Condition**: checks the blackboard or game state and returns SUCCESS or FAILURE immediately (never RUNNING). Examples: `IsPlayerInRange`, `HasAmmo`, `IsHealthBelow30Pct`.
- **Action**: does something in the world and may return RUNNING across multiple ticks. Examples: `MoveToTarget`, `PlayAttackAnimation`, `Reload`, `FireProjectile`.

The Sequence+Selector combination is enough to express most game AI. Decorators are sugar. Keep the node library small — 10–15 node types covers 95% of cases.

## How execution flows

The root node is ticked once per "AI update" (not necessarily every frame — see performance below). The tick propagates down the tree following the short-circuit rules. A Sequence of three children where the second returns RUNNING: the Sequence stores child index 1 as its "running child" and returns RUNNING to its parent. Next tick, the Sequence jumps straight to child 1 without re-ticking child 0. This "resume from running child" behavior is the **standard** approach; the alternative (restart from the root every tick) is called a "reactive" tree and is more expensive but makes interrupts automatic.

Reactive trees check every tick whether higher-priority branches have become valid. This is how "stop attacking if player runs out of range" works automatically: the Selector at the top tries the chase branch (higher priority), which fails because the player is now in range of something else, so it falls through to attack. In a standard (non-reactive) tree, you'd need to manually interrupt the running attack action when conditions change. Reactive trees are the default in LimboAI and in most production BT implementations.

## Blackboard

The blackboard is a shared dictionary that all nodes in the tree read and write. It is the communication contract between conditions and actions — nodes must not hold references to each other or call each other's methods. A guard's blackboard might contain: `target_node: Node`, `last_known_target_position: Vector3`, `alert_level: float`, `patrol_index: int`, `time_since_last_shot: float`, `is_in_cover: bool`. A Condition node `IsTargetVisible` reads `target_node` from the blackboard and does a raycast; the Action node `MoveToTarget` reads `last_known_target_position` from the blackboard to navigate. Neither knows the other exists.

Scope matters: a key can be **local** (per-agent, the default) or **global** (shared across all agents on an Autoload-style board). Use a global blackboard for team coordination ("is any ally currently attacking the player from the left?"). Keep it narrow — a bloated global blackboard is the behavior-tree equivalent of God Object.

In GDScript, a minimal Blackboard is just a `Dictionary` wrapped in a Resource for easy inspector assignment:

```gdscript
# blackboard.gd
class_name Blackboard extends Resource

var data: Dictionary = {}

func set_value(key: StringName, value: Variant) -> void:
    data[key] = value

func get_value(key: StringName, default: Variant = null) -> Variant:
    return data.get(key, default)

func has(key: StringName) -> bool:
    return data.has(key)
```

## Implementation options in Godot 4

**LimboAI** (github.com/limbonaut/limboai) is the production-grade option. It integrates into the Godot editor with a visual BT editor, built-in node library, blackboard editor, and a BTDebugger that overlays the tree in-game. It ships with ~30 built-in task nodes and full GDScript + C# scripting. Use LimboAI for any serious project. Its nodes subclass `BTAction` or `BTCondition` and override `_tick()`.

**Beehave** (github.com/bitbra1n/beehave) is a lighter alternative, also editor-integrated, with a simpler API. Fewer built-in nodes but easier to customize. Good for projects that want minimal dependencies.

**Hand-rolled** is correct when the game has a specific BT requirement that plugins don't serve well, or when the team needs to understand the system fully. The hand-rolled version below is ~150 lines and covers all node types needed for complex enemy AI.

## Hand-rolled BT base pattern

```gdscript
# bt_node.gd — Base class for all BT nodes
class_name BTNode extends RefCounted

enum Status { SUCCESS, FAILURE, RUNNING }

# Called once per AI tick. Override in subclasses.
func tick(agent: Node, blackboard: Blackboard) -> Status:
    return Status.FAILURE

# Optional: called when this node is interrupted mid-RUNNING.
func interrupt(agent: Node, blackboard: Blackboard) -> void:
    pass
```

```gdscript
# bt_sequence.gd — AND: all children must succeed in order
class_name BTSequence extends BTNode

var children: Array[BTNode] = []
var _current_child: int = 0

func tick(agent: Node, blackboard: Blackboard) -> Status:
    while _current_child < children.size():
        var status = children[_current_child].tick(agent, blackboard)
        match status:
            Status.RUNNING:
                return Status.RUNNING
            Status.FAILURE:
                _current_child = 0  # reset for next entry
                return Status.FAILURE
            Status.SUCCESS:
                _current_child += 1
    _current_child = 0
    return Status.SUCCESS
```

```gdscript
# bt_selector.gd — OR: first success wins
class_name BTSelector extends BTNode

var children: Array[BTNode] = []
var _current_child: int = 0

func tick(agent: Node, blackboard: Blackboard) -> Status:
    while _current_child < children.size():
        var status = children[_current_child].tick(agent, blackboard)
        match status:
            Status.RUNNING:
                return Status.RUNNING
            Status.SUCCESS:
                _current_child = 0
                return Status.SUCCESS
            Status.FAILURE:
                _current_child += 1
    _current_child = 0
    return Status.FAILURE
```

```gdscript
# bt_inverter.gd — Decorator: flips SUCCESS/FAILURE
class_name BTInverter extends BTNode

var child: BTNode

func tick(agent: Node, blackboard: Blackboard) -> Status:
    var status = child.tick(agent, blackboard)
    match status:
        Status.SUCCESS: return Status.FAILURE
        Status.FAILURE: return Status.SUCCESS
        _: return Status.RUNNING
```

```gdscript
# bt_cooldown.gd — Decorator: rate-limits a subtree
class_name BTCooldown extends BTNode

var child: BTNode
@export var cooldown_sec: float = 2.0
var _elapsed: float = INF  # starts "ready"

func tick(agent: Node, blackboard: Blackboard) -> Status:
    _elapsed += agent.get_process_delta_time()
    if _elapsed < cooldown_sec:
        return Status.FAILURE
    var status = child.tick(agent, blackboard)
    if status == Status.SUCCESS:
        _elapsed = 0.0
    return status
```

The runner lives on the enemy itself:

```gdscript
# enemy_brain.gd — Tick the tree at a controlled rate
class_name EnemyBrain extends Node

@export var tick_interval: float = 0.1  # 10 Hz; tune per enemy type
var blackboard: Blackboard
var root: BTNode
var _timer: float = 0.0

func _ready() -> void:
    blackboard = Blackboard.new()
    root = _build_tree()

func _physics_process(delta: float) -> void:
    _timer += delta
    if _timer >= tick_interval:
        _timer = 0.0
        root.tick(owner, blackboard)

func _build_tree() -> BTNode:
    # Override in subclass or build procedurally here
    return BTSelector.new()
```

## Concrete example: guard patrol + chase + attack

The tree in pseudocode:
```
Selector (root)
├── Sequence (attack)
│   ├── Condition: IsTargetInAttackRange
│   └── Action: FireAtTarget
├── Sequence (chase)
│   ├── Condition: HasTarget
│   └── Action: MoveToTarget
├── Sequence (investigate)
│   ├── Condition: HasLastKnownPosition
│   └── Sequence
│       ├── Action: MoveToLastKnownPosition
│       └── Action: LookAround
└── Action: Patrol
```

Reading the priority order: try to attack first; if not in range but have a target, chase; if target lost but we know where it was, investigate; default to patrol.

```gdscript
# condition_is_target_in_range.gd
class_name ConditionIsTargetInRange extends BTNode

@export var range_sq: float = 40000.0  # 200 units squared

func tick(agent: Node, blackboard: Blackboard) -> Status:
    var target = blackboard.get_value(&"target_node") as Node3D
    if target == null:
        return Status.FAILURE
    var dist_sq = agent.global_position.distance_squared_to(target.global_position)
    return Status.SUCCESS if dist_sq <= range_sq else Status.FAILURE
```

```gdscript
# action_move_to_target.gd
class_name ActionMoveToTarget extends BTNode

@export var arrival_distance: float = 1.5

func tick(agent: Node, blackboard: Blackboard) -> Status:
    var nav: NavigationAgent3D = agent.get_node("NavigationAgent3D")
    var target = blackboard.get_value(&"target_node") as Node3D

    if target == null:
        return Status.FAILURE

    # Update nav target only when target moved significantly (avoids nav spam)
    var desired_pos = target.global_position
    if nav.target_position.distance_squared_to(desired_pos) > 4.0:
        nav.target_position = desired_pos

    if agent.global_position.distance_to(desired_pos) <= arrival_distance:
        return Status.SUCCESS

    # Movement is handled by the agent's _physics_process reading nav.get_next_path_position()
    # This Action just keeps returning RUNNING while the agent moves
    return Status.RUNNING
```

```gdscript
# action_fire_at_target.gd
class_name ActionFireAtTarget extends BTNode

func tick(agent: Node, blackboard: Blackboard) -> Status:
    var target = blackboard.get_value(&"target_node") as Node3D
    if target == null:
        return Status.FAILURE
    agent.fire_weapon(target.global_position)
    return Status.SUCCESS  # fire completes in one tick; cooldown decorator handles rate
```

Wire the tree in `_build_tree()`:

```gdscript
func _build_tree() -> BTNode:
    var fire_seq = BTSequence.new()
    fire_seq.children = [
        ConditionIsTargetInRange.new(),
        BTCooldown.new().init(ActionFireAtTarget.new(), 0.5),
    ]

    var chase_seq = BTSequence.new()
    chase_seq.children = [
        ConditionHasTarget.new(),
        ActionMoveToTarget.new(),
    ]

    var root = BTSelector.new()
    root.children = [fire_seq, chase_seq, ActionPatrol.new()]
    return root
```

## Composability: sharing subtrees

The patrol subtree (move to waypoint → wait → advance index) is identical for guard, captain, and sniper. Don't copy it — build it once as a factory function or Resource:

```gdscript
# subtree_patrol.gd
static func build(waypoints: Array[Vector3]) -> BTNode:
    var seq = BTSequence.new()
    seq.children = [
        ActionMoveToWaypoint.new().init(waypoints),
        ActionWaitAtWaypoint.new().init(2.0),
        ActionAdvancePatrolIndex.new(),
    ]
    return seq
```

The guard's `_build_tree()` calls `SubtreePatrol.build(patrol_points)` at one leaf; the captain calls it too with different waypoints. No duplication, and a change to patrol logic propagates to all enemy types.

## Debugging

The hardest part of a BT is understanding why a branch fired. Two tools:

Add a `label` property to `BTNode` and print it on each tick when debug mode is on:

```gdscript
# In BTNode.tick():
if OS.is_debug_build() and label != "":
    print("[BT] %s → %s" % [label, Status.keys()[result]])
```

For LimboAI, enable the BTDebugger node (add it to the scene) and it renders the live tree with each node's last status color-coded in the Godot editor's debug viewport. This is worth the dependency alone.

Write a `print_tree_status()` helper that walks the tree and prints each node's name and last returned status with indentation:

```gdscript
func print_tree_status(node: BTNode, indent: int = 0) -> void:
    print("  ".repeat(indent) + "%s [%s]" % [node.get_class(), node.last_status])
    for child in node.get_children_nodes():
        print_tree_status(child, indent + 1)
```

Run it in `_process()` when a debug key is held. The output shows exactly which branches are active and which are failing, turning a 20-minute debugging session into a 30-second read.

## When NOT to use behavior trees

**Simple 3-state enemies**: an enemy with Idle → Chase → Attack is cleaner as an FSM or even a few `if/elif` blocks in `_physics_process`. The BT infrastructure adds ~200 lines with zero benefit when the behavior fits on a napkin.

**Scripted cinematic sequences**: a cutscene where an enemy walks to a door, kicks it open, scans the room, and triggers a dialogue isn't behavioral — it's a linear script. Use an AnimationPlayer with call tracks, or a `Tween` chain, or a coroutine. BTs are for *reactive* agents that respond to game state; scripted sequences have no game state to respond to.

**Performance at extreme scale**: ticking every node of a 30-node tree for 500 enemies every 100ms is 150,000 node ticks/sec. That's usually fine, but if profiling shows BT ticking in the hot path, coarsen the tick interval (200ms for background enemies), use a reactive-only root Selector that short-circuits quickly for inactive agents, or switch distant enemies to FSMs. The `enemy-ai.md` performance section covers time-slicing and LOD AI.

**One-off special behaviors**: if an enemy does a specific thing exactly once (drops a key, says a line, explodes), handle it with a signal and a one-shot function. Don't wrap it in a BT node.
