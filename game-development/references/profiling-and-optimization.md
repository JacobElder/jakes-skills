# Profiling and Performance Optimization (Godot 4)

Never optimize without profiling first. "My game is slow" has dozens of possible causes — the fix for a GPU-bound game is different from a CPU-bound game, and within CPU bottlenecks, physics is different from GDScript logic. The profiler tells you exactly where time goes; guessing wastes time and introduces complexity.

## Contents
- The profiling workflow
- Godot's built-in Debugger: Profiler tab
- Identifying GPU vs CPU bound
- Reading the Profiler flame chart
- Physics budget
- GDScript hot paths: avoiding per-frame allocations
- Draw call reduction
- VisualServer and RenderingServer stats
- Memory profiling
- Common culprits and fixes
- Mobile-specific optimization

## The profiling workflow

1. **Reproduce the slow moment** — build a test scene that reliably triggers the slowness.
2. **Open Debugger → Profiler tab** — run the game from the editor with profiling enabled.
3. **Identify GPU vs CPU** — press F1 in-game or check "Frame time" vs "Process time" in the Monitor tab.
4. **Find the hot function** — sort by self-time in the Profiler flame chart.
5. **Fix one thing** — change one variable, measure again. Don't batch optimizations.
6. **Verify the fix** — confirm frame time improved; confirm nothing regressed.

## Godot Debugger: Profiler tab

Run the game with **Debug → Run in Debug** (F5 from the editor). In the bottom panel, select **Debugger → Profiler**.

Click **Start** to begin recording. Play for 5–10 seconds in the slow area. Click **Stop**. The flame chart shows function calls sorted by cumulative time.

Key columns:
- **Self (ms)**: time spent inside this function only (not its callees)
- **Total (ms)**: time including all child calls
- **Calls**: invocation count per frame

Sort by **Self** to find functions that are intrinsically expensive. A function with high Total but low Self is not the bottleneck — its callees are.

## Identifying GPU vs CPU bound

Check **Debugger → Monitor → FPS** and **Debugger → Monitor → Process Time** vs **Physics Process Time**.

- If **Process Time ≈ Frame Time**: the bottleneck is CPU (GDScript logic, physics, pathfinding).
- If **Process Time ≪ Frame Time**: the CPU finishes quickly but the GPU is still rendering — GPU bound.

For GPU diagnosis, enable **Rendering → Viewport → Debug Draw → Overdraw** in the editor. Red areas are drawn many times — expensive fragment shaders or transparent layers stacking.

GPU-bound fixes:
- Reduce shadow cascade count or shadow distance
- Lower SDFGI cascade count or disable VoxelGI
- Reduce particle counts
- Check overdraw — opaque geometry before transparent, avoid transparent meshes wherever possible
- Reduce texture resolution for objects at distance

CPU-bound fixes: profiler flame chart → find the hot function.

## Reading the flame chart

```
_physics_process          45ms total  (hot!)
├── NavigationAgent3D.get_next_path_position  30ms  ← find this
│   └── AStarGrid2D.solve()                  30ms
├── CharacterBody3D.move_and_slide            8ms
└── StatusEffectManager._process             7ms
    └── Array.filter()                        5ms  ← per-frame allocation
```

In this example: 30ms in pathfinding is the bottleneck. Fix: reduce pathfinding frequency (not every frame), or switch from A* per agent to a shared flow field (Dijkstra map, computed once per target change).

## GDScript hot paths: per-frame allocation

Creating arrays, dictionaries, or strings inside `_process` or `_physics_process` allocates memory every frame and triggers the garbage collector irregularly.

```gdscript
# WRONG: allocates a new Array every frame
func _process(delta: float) -> void:
    var nearby := get_tree().get_nodes_in_group("enemies")  # allocates
    for enemy in nearby:
        _check_proximity(enemy)

# CORRECT: cache the list; update only when enemies spawn/die
var _enemy_cache: Array[Node] = []

func _ready() -> void:
    get_tree().node_added.connect(_on_node_added)
    get_tree().node_removed.connect(_on_node_removed)

func _on_node_added(node: Node) -> void:
    if node.is_in_group("enemies"):
        _enemy_cache.append(node)

func _on_node_removed(node: Node) -> void:
    _enemy_cache.erase(node)
```

Other per-frame allocation traps:
- `String + String` creates a new String every call — use `str()` or format strings and assign once
- `arr.filter(func(x): ...)` creates a new Array — keep a pre-filtered cache
- `get_node()` by path is slower than `@onready var` — cache node references in `_ready()`

## Draw call reduction

Each draw call is a GPU command. Too many draw calls (> 1,000 for mobile, > 5,000 for desktop) stalls the GPU driver.

**Check draw call count**: Debugger → Monitor → Render → Draw Calls Per Frame.

**Reduction strategies:**

1. **MultiMeshInstance3D** for many copies of the same mesh (trees, rocks, bullets):
```gdscript
var mm := MultiMesh.new()
mm.transform_format = MultiMesh.TRANSFORM_3D
mm.instance_count = 1000
mm.mesh = rock_mesh

var mmi := MultiMeshInstance3D.new()
mmi.multimesh = mm
add_child(mmi)

# Set transforms:
for i in 1000:
    mm.set_instance_transform(i, Transform3D(Basis(), Vector3(i * 2.0, 0, 0)))
```

2. **Atlas textures** — combine multiple sprites into a single texture sheet. Sprites using the same texture can be batched into one draw call (Godot 2D does this automatically for CanvasItem nodes sharing a texture).

3. **Surface material merging** — meshes sharing the same material can be batched. Minimize unique materials; reuse material instances.

4. **Distance-based disable**: for objects beyond LOD_MAX_DISTANCE, disable their visibility entirely.

## VisibilityNotifier3D for CPU culling

```gdscript
# Attach VisibilityNotifier3D to any node that should stop ticking when offscreen
@onready var vis := $VisibilityNotifier3D

func _ready() -> void:
    vis.screen_entered.connect(func(): set_process(true))
    vis.screen_exited.connect(func(): set_process(false))
```

Stop running `_process` on enemies the camera cannot see. This is free CPU time.

## Physics budget

Physics is the most commonly over-budgeted system. The default physics tick is 60 Hz. Halving to 30 Hz saves half the physics CPU budget with minimal gameplay impact for most games:

```gdscript
# Project Settings → Physics → Common → Physics FPS = 30
```

For individual bodies that don't need 60Hz updates:
```gdscript
# On a RigidBody3D that doesn't need per-frame updates:
body.set_physics_process(false)
# Update manually every N frames:
func _process(delta: float) -> void:
    if Engine.get_physics_frames() % 3 == 0:
        body.apply_force(...)
```

Use `move_and_slide_with_snap()` instead of `move_and_slide()` for CharacterBody3D on stairs — it's cheaper because it avoids the floor normal recalculation loop.

## Memory profiling

Open **Debugger → Monitor → Memory → Static Memory** and **Dynamic Memory**. Resource leaks show as steadily growing dynamic memory.

Common leak sources:
- `await signal` in a loop that never exits — the coroutine keeps the caller alive
- Holding a reference to a freed node — use `is_instance_valid()` before access
- Creating `Timer.new()` inside a loop without `queue_free()` after use — use a pool or `create_timer()` on the scene tree instead

```gdscript
# WRONG: creates a new Timer forever
func apply_effect_with_duration(duration: float) -> void:
    var timer := Timer.new()
    add_child(timer)
    timer.start(duration)
    await timer.timeout
    # timer never freed!

# CORRECT:
func apply_effect_with_duration(duration: float) -> void:
    await get_tree().create_timer(duration).timeout
```

## Common culprits and their fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Frame spikes every 5–30s | GC pause from per-frame allocation | Cache arrays, avoid in-loop String concat |
| Constant 45ms physics | A* per agent per frame | Shared flow field or reduce path frequency |
| GPU bound, many enemies | Too many draw calls from individual MeshInstance3D | MultiMeshInstance3D |
| GPU bound, particles | Too many CPUParticles3D | Switch to GPUParticles3D; reduce count |
| GPU bound, shadows | Full PSSM4 shadows on many lights | Reduce shadow cascade, increase shadow_max_distance, disable shadow on most OmniLight3D |
| CPU spikes at level start | Synchronous resource loading | ResourceLoader.load_threaded_request() |
| Consistent 10ms in _process | `get_nodes_in_group()` per frame | Cache the node list |

## Mobile-specific optimization

Mobile GPUs are fill-rate limited (fragment shader throughput), not vertex limited.

- **Disable SDFGI, VoxelGI, and SSAO** — too expensive for mobile
- **Use LightmapGI** — zero runtime GPU cost
- **Limit OmniLight3D shadows** — shadow rendering is expensive; use at most 2–3 shadow-casting lights on mobile
- **Reduce particle counts by 75%** compared to PC targets
- **Target 30 FPS on mobile** explicitly — 60 FPS is only achievable on high-end mobile with simple scenes
- **Test on device, not the PC editor** — the editor renders on the PC GPU; mobile performance is not predictable from editor frame rate
