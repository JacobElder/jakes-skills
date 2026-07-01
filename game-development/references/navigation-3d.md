# 3D Pathfinding: NavigationAgent3D and NavigationMesh in Godot 4

## Core setup: three nodes you need

```
World (Node3D)
├── NavigationRegion3D     ← defines walkable surface, holds NavigationMesh
│   └── MeshInstance3D     ← or any geometry used as nav source
└── Enemy (CharacterBody3D)
    └── NavigationAgent3D  ← does path queries and avoidance
```

## Baking the NavigationMesh

1. Add a `NavigationRegion3D` to the scene.
2. In the Inspector, create a new `NavigationMesh` resource.
3. Set `NavigationMesh.geometry_parsed_geometry_type` to `MESH_INSTANCES` (or `STATIC_COLLIDERS` to bake from collision shapes).
4. Click **Bake NavigationMesh** in the toolbar, or call in code:

```gdscript
$NavigationRegion3D.bake_navigation_mesh()
# Baking is synchronous by default — use threaded bake for large meshes:
NavigationMeshGenerator.bake_from_source_geometry_data(nav_mesh, source_geometry_data)
```

Key properties to set on the NavigationMesh:
- `cell_size`: granularity of the voxel grid (default 0.25m — halve for finer paths, double for performance)
- `agent_height`: must match your character (blocks paths under low ceilings)
- `agent_radius`: clearance from walls (typically half the character's collision capsule radius)
- `edge_max_slope`: steepest walkable angle in degrees

## NavigationAgent3D: the correct update loop

```gdscript
# Enemy.gd
extends CharacterBody3D

@onready var nav_agent: NavigationAgent3D = $NavigationAgent3D

func _ready() -> void:
    nav_agent.path_desired_distance = 1.0    # how close counts as "reached waypoint"
    nav_agent.target_desired_distance = 1.5  # how close counts as "reached target"
    nav_agent.navigation_finished.connect(_on_navigation_finished)
    nav_agent.velocity_computed.connect(_on_safe_velocity)

func set_target(pos: Vector3) -> void:
    nav_agent.set_target_position(pos)

func _physics_process(delta: float) -> void:
    if nav_agent.is_navigation_finished():
        return
    var next_pos := nav_agent.get_next_path_position()
    var direction := (next_pos - global_position).normalized()
    var desired_velocity := direction * SPEED
    nav_agent.set_velocity(desired_velocity)   # feeds RVO avoidance

func _on_safe_velocity(safe_velocity: Vector3) -> void:
    # Called after avoidance computation — use this instead of desired_velocity
    velocity = safe_velocity
    move_and_slide()

func _on_navigation_finished() -> void:
    # Target reached — stop, switch to attack, idle, etc.
    velocity = Vector3.ZERO
```

**Critical: do not call `navigate_to()` — it does not exist.** The correct method is `set_target_position()`.

**Critical: use `get_next_path_position()` every frame** — this returns the next waypoint on the path, not the final destination. Do not move directly toward the target; the agent manages the route.

## RVO avoidance (agent-to-agent collision)

Enable avoidance on the NavigationAgent3D:
- Set `avoidance_enabled = true`
- Set `radius` to match the character's physical radius
- Call `set_velocity(desired_velocity)` each frame instead of applying velocity directly
- Connect `velocity_computed` and apply the result

Without avoidance, multiple enemies pathfinding to the same target stack on top of each other. The RVO layer prevents this without physics collision between agents.

## Dynamic obstacles

Add `NavigationObstacle3D` to any moving obstacle (e.g., a door that closes):

```gdscript
# Sliding door
@onready var obstacle: NavigationObstacle3D = $NavigationObstacle3D

func close_door() -> void:
    obstacle.avoidance_enabled = true   # agents steer around it
    # For full path rebaking (blocking, not just avoidance):
    $NavigationRegion3D.bake_navigation_mesh()
```

`NavigationObstacle3D` with `avoidance_enabled` steers agents around it in real time without rebaking. Rebaking is required only when the obstacle permanently blocks the walkable surface.

## Multi-floor / multi-region buildings

Use multiple `NavigationRegion3D` nodes (one per floor). Connect them with `NavigationLink3D` nodes that define jump or staircase connections:

```gdscript
var link := NavigationLink3D.new()
link.start_position = stair_bottom
link.end_position   = stair_top
link.bidirectional  = true
add_child(link)
```

Agents automatically use links when they are the shortest path.

## Common mistakes

**Forgetting `navigation_finished` → stuck enemies**: Without connecting the signal, enemies keep calling `get_next_path_position()` after arrival and jitter in place.

**Moving to target directly instead of next waypoint**: `get_next_path_position()` returns the next corner on the path — moving to `nav_agent.target_position` directly ignores obstacles.

**NavigationMesh baked at edit time but geometry added at runtime**: Call `bake_navigation_mesh()` after adding procedural geometry; edit-time bakes don't include runtime-added nodes.

**`agent_height` too small**: Enemies navigate under geometry they should be blocked by. Match `agent_height` to the character's CollisionShape3D capsule height.

**Not waiting one physics frame before querying**: After calling `set_target_position()`, the path is computed asynchronously. Wait one physics frame before calling `get_next_path_position()` or check `is_target_reachable()` first.
