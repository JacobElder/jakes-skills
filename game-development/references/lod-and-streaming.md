# LOD Systems and Scene Streaming

A 3D open world with 500 trees rendered at full polygon count regardless of distance is not a performance problem — it is an architecture problem. The same triangle budget that renders one tree 2m away renders one tree 800m away. LOD (Level of Detail) and scene streaming are the two systems that make large worlds viable.

## Contents
- LOD: why it matters and what it costs
- GeometryInstance3D LOD in Godot 4
- MultiMeshInstance3D for repeated objects
- Shadow culling
- Occlusion culling
- Chunk-based scene streaming
- Async loading with ResourceLoader
- ChunkManager autoload pattern
- Entity interest management
- Level streaming in Unity
- Performance budgeting

## LOD: why it matters

At 800m, a 10,000-polygon tree contributes roughly 4 pixels to the final image. The GPU still transforms all 10,000 vertices. A 50-polygon billboard that looks identical at that distance costs 0.5% as much. The mismatch between geometric cost and visual contribution is the core problem LOD solves.

"Reduce draw distance" is the wrong tool — it causes jarring pop-in. LOD transitions are gradual and, done well, invisible to players.

## GeometryInstance3D LOD in Godot 4

Every `MeshInstance3D` inherits from `GeometryInstance3D` and has two LOD properties:

- `lod_min_distance` — distance at which the engine starts considering lower LOD meshes (default: 0)
- `lod_max_distance` — distance at which the lowest-detail mesh is used (default: 0 = auto)

The correct workflow is to create multiple `MeshInstance3D` siblings under the same parent, each set to a different mesh complexity:

```
TreeRoot (Node3D)
├── LOD0_MeshInstance (MeshInstance3D)   # 8,000 polygons, used < 30m
├── LOD1_MeshInstance (MeshInstance3D)   # 1,200 polygons, used 30-100m
├── LOD2_MeshInstance (MeshInstance3D)   # 150 polygons, used 100-300m
└── LOD3_MeshInstance (MeshInstance3D)   # billboard quad, used > 300m
```

Set each `MeshInstance3D.lod_min_distance` and `lod_max_distance` to define the distance range it is active. Godot selects the appropriate mesh automatically based on camera distance.

```gdscript
# Runtime LOD adjustment (e.g. quality setting)
func apply_lod_quality(multiplier: float) -> void:
    $LOD0_MeshInstance.lod_max_distance = 30.0 * multiplier
    $LOD1_MeshInstance.lod_min_distance = 30.0 * multiplier
    $LOD1_MeshInstance.lod_max_distance = 100.0 * multiplier
    $LOD2_MeshInstance.lod_min_distance = 100.0 * multiplier
    $LOD2_MeshInstance.lod_max_distance = 300.0 * multiplier
```

Set `GeometryInstance3D.visibility_range_fade_mode = VISIBILITY_RANGE_FADE_SELF` for a cross-fade transition instead of a hard pop.

## MultiMeshInstance3D for repeated objects

For large numbers of identical static objects — 5,000 trees, 10,000 grass blades, 2,000 rocks — `MultiMeshInstance3D` renders all instances in a single draw call via GPU instancing.

```gdscript
# Spawn 5000 trees via MultiMesh (one draw call)
func populate_forest(mesh: Mesh, count: int, area: Rect2) -> void:
    var mm := MultiMesh.new()
    mm.mesh = mesh
    mm.transform_format = MultiMesh.TRANSFORM_3D
    mm.instance_count = count

    for i in count:
        var pos := Vector3(
            randf_range(area.position.x, area.end.x),
            0.0,
            randf_range(area.position.y, area.end.y)
        )
        mm.set_instance_transform(i, Transform3D(Basis(), pos))

    $MultiMeshInstance3D.multimesh = mm
```

Collision for a MultiMesh forest uses a single `StaticBody3D` with `HeightMapShape3D` for the terrain — not per-tree collision. Individual tree collision (for chopping, etc.) uses separate invisible `StaticBody3D` nodes only within interaction range.

MultiMesh also supports `set_instance_color()` and `set_instance_custom_data()` for per-instance tinting and shader variation without additional draw calls.

## VisibilityNotifier3D

Attach `VisibilityNotifier3D` to any node whose processing is wasteful when off-screen. Connect its `screen_exited` signal to pause AI, animation, and `_process`:

```gdscript
func _on_screen_exited() -> void:
    set_process(false)
    $AnimationPlayer.stop()
    $AIController.set_physics_process(false)

func _on_screen_entered() -> void:
    set_process(true)
    $AnimationPlayer.play("idle")
    $AIController.set_physics_process(true)
```

This is CPU-side optimization; LOD handles the GPU side. Both are required for large scenes.

## Shadow culling

Shadows are often the largest GPU cost in many-object outdoor scenes. Apply two rules:

1. **Disable shadow casting on LOD1+ meshes.** Close-up shadows matter; shadows from a low-poly distant tree do not.

```gdscript
$LOD1_MeshInstance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
$LOD2_MeshInstance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
```

2. **Limit shadow distance on the light.** `DirectionalLight3D` has `directional_shadow_max_distance`. Set this to cover only the area the player can actually inspect closely (150-400m depending on game scale). Terrain beyond that distance uses baked lightmaps or ambient color.

```gdscript
$DirectionalLight3D.directional_shadow_max_distance = 200.0
```

## Occlusion culling

Occlusion culling tells the GPU not to render objects hidden behind solid geometry. In Godot 4:

1. Add `OccluderInstance3D` nodes to large solid objects (buildings, cliff faces, hills).
2. Bake occluders: Scene → Bake Occluders (editor tool).
3. Enable in Project Settings → Rendering → Occlusion Culling → Use Occlusion Culling.

Occlusion culling is most valuable for indoor/urban scenes with many overlapping objects. For open outdoor terrain with scattered trees, LOD and frustum culling (built-in) are usually sufficient.

## Chunk-based scene streaming

A 4km×4km world cannot fit in RAM. Even if it could, simulating 100,000 NPC positions and colliders every frame is not viable.

The solution is a chunk grid: divide the world into fixed-size square chunks. Only chunks within the player's load radius are instantiated; chunks beyond the unload radius are freed.

**Chunk size**: 64-256 world units is typical. Smaller chunks = finer granularity, more loading operations; larger chunks = coarser, larger memory spikes. 128m×128m is a good default.

**Load/unload radius**: load 3-5 chunks out from the player in each direction (a 7×7 or 11×11 grid). Set unload radius slightly larger than load radius (hysteresis) to prevent chunks from repeatedly loading and unloading as the player hovers near a boundary.

## Async loading with ResourceLoader

**Never use `load(path)` for chunks in a running game.** `load()` blocks the main thread for the full duration of the disk read, causing frame hitches.

```gdscript
# WRONG — blocks for 200ms+
var chunk_scene: PackedScene = load("res://world/chunk_4_7.tscn")

# CORRECT — async, non-blocking
ResourceLoader.load_threaded_request("res://world/chunk_4_7.tscn")
```

Poll in `_process`:

```gdscript
func _process(_delta: float) -> void:
    for path in _loading_requests.duplicate():
        var status := ResourceLoader.load_threaded_get_status(path)
        match status:
            ResourceLoader.THREAD_LOAD_LOADED:
                var scene: PackedScene = ResourceLoader.load_threaded_get(path)
                _instantiate_chunk(path, scene)
                _loading_requests.erase(path)
            ResourceLoader.THREAD_LOAD_FAILED:
                push_error("Chunk load failed: " + path)
                _loading_requests.erase(path)
```

Limit concurrent requests to 2-3 to avoid memory spikes from too many simultaneously loading resources.

## ChunkManager autoload pattern

```gdscript
# ChunkManager.gd — autoload
extends Node

const CHUNK_SIZE := 128.0
const LOAD_RADIUS := 3       # chunks
const UNLOAD_RADIUS := 4     # chunks (hysteresis)

var _active_chunks: Dictionary = {}    # Vector2i → Node3D
var _loading_requests: Dictionary = {} # path → Vector2i
var _player: Node3D

func _ready() -> void:
    _player = get_tree().get_first_node_in_group("player")

func _process(_delta: float) -> void:
    _update_chunks()
    _poll_loading()

func _update_chunks() -> void:
    var player_chunk := _world_to_chunk(_player.global_position)

    # Unload distant chunks
    for coord in _active_chunks.keys():
        if coord.distance_to(player_chunk) > UNLOAD_RADIUS:
            _unload_chunk(coord)

    # Queue loading for nearby chunks
    for dx in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
        for dz in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
            var coord := player_chunk + Vector2i(dx, dz)
            if coord not in _active_chunks and coord not in _loading_requests.values():
                _queue_chunk_load(coord)

func _world_to_chunk(pos: Vector3) -> Vector2i:
    return Vector2i(floori(pos.x / CHUNK_SIZE), floori(pos.z / CHUNK_SIZE))

func _chunk_path(coord: Vector2i) -> String:
    return "res://world/chunks/chunk_%d_%d.tscn" % [coord.x, coord.y]

func _queue_chunk_load(coord: Vector2i) -> void:
    var path := _chunk_path(coord)
    if not ResourceLoader.exists(path):
        return
    ResourceLoader.load_threaded_request(path)
    _loading_requests[path] = coord

func _instantiate_chunk(path: String, scene: PackedScene) -> void:
    var coord: Vector2i = _loading_requests[path]
    _loading_requests.erase(path)
    var chunk := scene.instantiate()
    chunk.global_position = Vector3(coord.x * CHUNK_SIZE, 0.0, coord.y * CHUNK_SIZE)
    add_child(chunk)
    _active_chunks[coord] = chunk

func _unload_chunk(coord: Vector2i) -> void:
    var chunk := _active_chunks[coord]
    _save_chunk_state(coord, chunk)
    chunk.queue_free()
    _active_chunks.erase(coord)
```

## Entity interest management

Not all entities need to run AI and physics at full simulation when the player is far away. Use two zones:

- **Active zone** (within 2-3 chunks): full AI, physics, animation.
- **Hibernated zone** (beyond active, within load radius): node exists in scene tree but `set_process(false)`, `set_physics_process(false)`, `$AnimationPlayer.stop()`. NPC position is stored in their script and updated at a coarse interval (once per second).
- **Unloaded zone** (beyond load radius): no node. State serialized to a Dictionary keyed by entity GUID.

On chunk unload, serialize all dynamic entities in it:

```gdscript
func _save_chunk_state(coord: Vector2i, chunk: Node3D) -> void:
    var state := {}
    for entity in chunk.get_children():
        if entity.has_method("serialize"):
            state[entity.entity_id] = entity.serialize()
    WorldState.chunk_states[coord] = state
```

On chunk reload, restore entities from saved state before spawning them fresh.

## Level streaming in Unity

Unity's equivalent is Additive scene loading:

```csharp
// Load chunk scene additively (non-blocking)
IEnumerator LoadChunkAsync(string sceneName) {
    AsyncOperation op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
    op.allowSceneActivation = false;
    while (op.progress < 0.9f) yield return null;
    op.allowSceneActivation = true;
}

// Unload when out of range
IEnumerator UnloadChunkAsync(string sceneName) {
    yield return SceneManager.UnloadSceneAsync(sceneName);
}
```

Unity Addressables provide more control for runtime asset management: `Addressables.LoadAssetAsync<GameObject>()` with `Addressables.ReleaseInstance()` on unload.

## Performance budgeting

60 FPS = 16.67ms per frame. Allocate the budget:

- Chunk loading: max 2-3ms per frame (poll 1 chunk per frame if ResourceLoader gives it ready)
- LOD transition: effectively free (GPU-driven)
- Shadow culling: aim for < 25% of GPU time on lighting
- Entity simulation: budget by tier (active: full cost, hibernated: ~5% of active cost)

Profile with Godot's built-in Profiler (Debugger → Profiler). Watch `_process` cost on ChunkManager — if it exceeds 1ms, the update loop is doing too much per frame. Spread work over multiple frames with a counter:

```gdscript
var _update_frame := 0

func _process(_delta: float) -> void:
    _update_frame = (_update_frame + 1) % 3
    if _update_frame == 0:
        _update_chunks()  # only runs every 3 frames
    _poll_loading()       # always runs (non-blocking anyway)
```
