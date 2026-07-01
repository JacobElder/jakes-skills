# 2D Navigation

## Core setup: NavigationRegion2D + NavigationAgent2D

Three nodes required:
- `NavigationRegion2D` with a `NavigationPolygon` drawn to cover walkable area
- `NavigationAgent2D` child on the character node
- Character must call `set_target_position()` and use `get_next_path_position()` each frame

```gdscript
# Enemy or AI character
var nav_agent: NavigationAgent2D

func _ready() -> void:
    nav_agent = $NavigationAgent2D
    nav_agent.path_desired_distance = 4.0
    nav_agent.target_desired_distance = 4.0
    nav_agent.velocity_computed.connect(_on_safe_velocity)

func _physics_process(_delta: float) -> void:
    if nav_agent.is_navigation_finished():
        return
    var next := nav_agent.get_next_path_position()
    var dir := (next - global_position).normalized()
    nav_agent.set_velocity(dir * SPEED)

func _on_safe_velocity(safe_vel: Vector2) -> void:
    velocity = safe_vel
    move_and_slide()

func set_target(pos: Vector2) -> void:
    nav_agent.set_target_position(pos)
```

**Most-missed step**: `get_next_path_position()` returns the *next waypoint*, not the final destination. Check `is_navigation_finished()` to know when arrival is complete. The method `navigate_to()` **does not exist** in Godot 4 — use `set_target_position()`.

## NavigationPolygon setup

In the editor: select `NavigationRegion2D` → draw the walkable polygon in the viewport via "Add Outline" mode. For a room-based game, draw the floor minus walls/obstacles. Hit "Bake NavigationPolygon" to process it.

For runtime baking:

```gdscript
# Rebake when level changes
$NavigationRegion2D.bake_navigation_polygon()
await $NavigationRegion2D.bake_finished
```

## TileMap navigation integration

Godot 4 TileMap navigation uses per-tile navigation polygons defined in the TileSet, then baked automatically via `NavigationRegion2D`.

**Setup in editor:**
1. Open TileSet editor → select a tile → go to "Navigation" layer tab
2. Draw the walkable polygon for that tile (usually the full tile for floor tiles, none for walls)
3. Add a `NavigationRegion2D` to the scene — it auto-discovers TileMap navigation polygons on `_ready()`
4. Alternatively: `NavigationServer2D.bake_from_source_geometry_data()` for manual control

```gdscript
# TileMap-based bake at runtime
var nav_region: NavigationRegion2D = $NavigationRegion2D

func _ready() -> void:
    nav_region.bake_navigation_polygon()
    await nav_region.bake_finished
    # safe to set targets now
```

**Common mistake**: Setting agent targets before the NavPolygon is baked results in agents that can't find paths. Always await `bake_finished` before starting agent navigation.

## RVO avoidance (2D)

Same pattern as 3D: enable `avoidance_enabled = true` on the agent and connect `velocity_computed`:

```gdscript
func _ready() -> void:
    nav_agent.avoidance_enabled = true
    nav_agent.radius = 12.0
    nav_agent.velocity_computed.connect(_on_safe_velocity)
```

The `set_velocity()` → `velocity_computed` pipeline lets the RVO server compute an avoidance-adjusted velocity without rebaking the navmesh. Use `NavigationObstacle2D` with `avoidance_enabled` for dynamic obstacles like other characters.

## NavigationLink2D for portals and shortcuts

For ladders, doors between disconnected regions, or shortcuts:

```gdscript
var link := NavigationLink2D.new()
link.start_position = ladder_bottom
link.end_position = ladder_top
link.bidirectional = true
add_child(link)
```

## Arrival and re-pathing

```gdscript
func _ready() -> void:
    nav_agent.navigation_finished.connect(_on_arrived)
    nav_agent.target_reached.connect(_on_target_reached)
    nav_agent.path_changed.connect(_on_path_changed)

func _on_arrived() -> void:
    state = State.IDLE

func update_target(pos: Vector2) -> void:
    if nav_agent.target_position.distance_to(pos) > repath_threshold:
        nav_agent.set_target_position(pos)
```

## Reachability check

```gdscript
func can_reach(pos: Vector2) -> bool:
    return nav_agent.is_target_reachable()
```

Call `set_target_position()` first, then check `is_target_reachable()`. If unreachable, fall back to direct movement or switch behavior state.

## Performance notes

- NavigationAgent2D path queries are cheap but not free — avoid calling `set_target_position()` every frame for a pursuing enemy; repath every 0.3–0.5 s or when the target moves more than a threshold.
- For top-down games with many agents (> 30), stagger repath calls across frames using a `NavigationManager` autoload that queues requests.
- Baking is async; always use the callback or `await bake_finished`.
