# Open World Architecture

A 4 km × 4 km world at standard density (trees, rocks, NPCs, enemies, loot) does not fit in RAM. Even if it did, simulating everything every frame would kill performance on any consumer hardware. Open-world architecture is the art of making a large world appear seamless while actually only holding a small active slice in memory and simulation at any moment. This file covers the concrete systems required: chunking, async streaming, entity hibernation, floating-point origin shifting, navigation stitching, and time-of-day coordination.

## Contents
- The core constraint
- Chunk system design
- Async chunk loading
- Entity interest management and hibernation
- World coordinate system and float precision
- Origin shifting
- Save/load world state
- Navigation in open worlds
- Quest and event scripting
- LOD budget and simulation tiers
- Time-of-day and dynamic world
- Common mistakes

## The core constraint

The core challenge is not graphics — it is simulation budget. Geometry can be streamed and LOD'd. The expensive parts are: running AI for hundreds of NPCs, ticking physics for thousands of objects, and updating navigation meshes. The architecture must ensure that only a small radius around the player is fully simulated at any time.

**Do not attempt to solve open-world scale with a single large scene.** Godot will load and hold the entire `.tscn` in memory. Even if the runtime cost is manageable, the iteration cost (waiting for the editor to load a 50,000-node scene) is not.

## Chunk system design

Divide the world into a uniform grid of chunks. Each chunk is an independently loadable resource containing geometry, navigation data, and an entity manifest.

```gdscript
const CHUNK_SIZE       := 128     # world units per chunk edge
const LOAD_RADIUS      := 3       # load all chunks within this many chunks of player
const UNLOAD_RADIUS    := 4       # unload chunks beyond this radius (hysteresis gap)
const MAX_INFLIGHT     := 2       # max concurrent async load requests

# Chunk address: Vector2i(x_index, z_index) where index = floor(world_pos / CHUNK_SIZE)
```

The hysteresis gap between `LOAD_RADIUS` and `UNLOAD_RADIUS` prevents a chunk flickering in and out as the player walks along a chunk boundary. A chunk loads when it enters `LOAD_RADIUS` and only unloads when it exits `UNLOAD_RADIUS`. This single-radius-per-action rule is non-negotiable — without it you get visible pop.

`ChunkManager` is an autoload that owns the loaded-chunk registry:

```gdscript
# chunk_manager.gd — autoload as ChunkManager
class_name ChunkManager extends Node

var loaded_chunks: Dictionary = {}     # Vector2i → ChunkInstance
var _pending_loads: Dictionary = {}    # Vector2i → ResourceLoader request token
var _player: Node3D

func _ready() -> void:
    _player = get_tree().get_first_node_in_group(&"player")

func _physics_process(_delta: float) -> void:
    _update_chunks()

func _update_chunks() -> void:
    var player_chunk := world_to_chunk(_player.global_position)
    _request_needed_chunks(player_chunk)
    _release_distant_chunks(player_chunk)
    _poll_pending_loads()

func world_to_chunk(world_pos: Vector3) -> Vector2i:
    return Vector2i(
        floori(world_pos.x / CHUNK_SIZE),
        floori(world_pos.z / CHUNK_SIZE)
    )

func chunk_to_world_origin(coord: Vector2i) -> Vector3:
    return Vector3(coord.x * CHUNK_SIZE, 0.0, coord.y * CHUNK_SIZE)
```

Each chunk file on disk is a `.tres` (or `.res`) resource with:
- `static_mesh_path: String` — a MeshLibrary or packed scene for the static geometry
- `nav_mesh_path: String` — a pre-baked NavigationMesh resource
- `entity_manifest: Array[Dictionary]` — list of `{type, local_pos, saved_state}` for dynamic objects

Separate these so the static geometry can be loaded once and cached, while entity states are frequently rewritten during save/load.

## Async chunk loading

Never load a chunk synchronously in `_physics_process()`. The stall will produce a visible frame hitch. Use `ResourceLoader.load_threaded_request()` and poll the status each frame.

```gdscript
func _request_needed_chunks(player_chunk: Vector2i) -> void:
    for dz in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
        for dx in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
            var coord := player_chunk + Vector2i(dx, dz)
            if loaded_chunks.has(coord) or _pending_loads.has(coord):
                continue
            if _pending_loads.size() >= MAX_INFLIGHT:
                return   # respect in-flight limit; closer chunks queued first next frame
            var path := _chunk_path(coord)
            if not ResourceLoader.exists(path):
                continue
            ResourceLoader.load_threaded_request(path)
            _pending_loads[coord] = path

func _poll_pending_loads() -> void:
    for coord in _pending_loads.keys():
        var path: String = _pending_loads[coord]
        var status := ResourceLoader.load_threaded_get_status(path)
        if status == ResourceLoader.THREAD_LOAD_LOADED:
            var chunk_res: Resource = ResourceLoader.load_threaded_get(path)
            _instantiate_chunk(coord, chunk_res)
            _pending_loads.erase(coord)
        elif status == ResourceLoader.THREAD_LOAD_FAILED:
            push_error("Chunk load failed: " + path)
            _pending_loads.erase(coord)

func _chunk_path(coord: Vector2i) -> String:
    return "res://world/chunks/chunk_%d_%d.tres" % [coord.x, coord.y]
```

To load closest chunks first, sort the request candidates by distance before issuing requests. A simple priority queue (min-heap keyed by Chebyshev distance to `player_chunk`) is sufficient; a flat sorted array works at the radii typical in most games.

## Entity interest management and hibernation

Entities outside `simulation_radius` (can match `LOAD_RADIUS` or be a separate value) should not run AI, physics, or animations. "Hibernating" an entity means:

1. Record its state to a dictionary (`entity_states[entity_id] = entity.serialize()`).
2. Remove it from the scene tree (`entity.queue_free()`).
3. When the entity's chunk re-enters simulation range, re-instantiate it from `entity_states` if an entry exists, or from the chunk manifest if it was never visited.

```gdscript
# On each entity: implement serialize() / deserialize()
func serialize() -> Dictionary:
    return {
        "type":      _entity_type,
        "local_pos": global_position - ChunkManager.chunk_to_world_origin(_home_chunk),
        "hp":        hp,
        "state":     _state_machine.current_state_name,
    }

func deserialize(data: Dictionary, chunk_origin: Vector3) -> void:
    global_position = chunk_origin + data["local_pos"]
    hp              = data["hp"]
    _state_machine.enter_state(data["state"])
```

This is distinct from chunk geometry loading — geometry always loads when the chunk loads, but entities are only activated when within the simulation radius. A large render distance + small simulation radius gives you visible distant geometry without simulating distant NPCs.

## World coordinate system and float precision

Store entity positions as `(chunk_coord: Vector2i, local_offset: Vector3)`, not as a single world-space `Vector3`. Float32 has ~7 decimal digits of precision. At 4,000 m from origin, the smallest representable step is about 0.5 mm — borderline for physics. At 16,000 m it is 2 mm, which causes visible jitter and physics tunneling.

Convert to world float only for rendering and physics engine calls:

```gdscript
func world_pos(chunk_coord: Vector2i, local_offset: Vector3) -> Vector3:
    return ChunkManager.chunk_to_world_origin(chunk_coord) + local_offset
```

Never store the accumulated world-space `Vector3` of a long-lived entity across multiple saves — precision degrades each time.

## Origin shifting

When the player travels more than `ORIGIN_THRESHOLD` units from the scene origin, shift the entire scene back so the player is near the origin again. This resets float precision for all active objects.

```gdscript
# world_origin_shifter.gd — autoload as WorldOriginShifter
class_name WorldOriginShifter extends Node

signal world_shifted(offset: Vector3)

const ORIGIN_THRESHOLD := 5000.0   # units; shift when player exceeds this from origin

@onready var _player: Node3D = get_tree().get_first_node_in_group(&"player")

func _physics_process(_delta: float) -> void:
    if _player.global_position.length() > ORIGIN_THRESHOLD:
        _shift(-_player.global_position)

func _shift(offset: Vector3) -> void:
    # Move every active node in the scene by offset.
    for node in get_tree().get_nodes_in_group(&"world_object"):
        node.global_position += offset
    world_shifted.emit(offset)
```

Every system that caches a world-space position must connect to `world_shifted` and subtract the offset:

```gdscript
# Example: a projectile that stores its spawn position
func _ready() -> void:
    WorldOriginShifter.world_shifted.connect(_on_world_shifted)

func _on_world_shifted(offset: Vector3) -> void:
    _spawn_position += offset
```

Add all active physics objects, particles, lights, and cameras to the `world_object` group so the shift applies universally. Missing one system produces visible seams.

## Save/load world state

World state is the most error-prone part of open-world save systems. Rules:

- **Save per-chunk state to individual files** — `user://saves/world/chunk_3_-2.json`. Loading the world does not require deserializing the entire save; only touched chunks load their files.
- **Global save file** — `user://saves/global.json` contains: player position (as `chunk_coord + local_offset`), player stats, quest graph state, discovered-chunk set, global flags.
- **Never serialize Godot Nodes or Resources with signals** — these contain scene-tree references that are invalid across sessions. Serialize only plain data: ints, floats, strings, Vector3 as arrays, dictionaries.
- **Mark chunks dirty on modification** — only write the save file for a chunk when it has been modified (entity killed, item picked up, structure placed). Unmodified chunks don't need a save file; they reconstruct from the source resource.

```gdscript
# chunk_instance.gd
var _dirty := false

func mark_dirty() -> void:
    _dirty = true

func save_if_dirty(coord: Vector2i) -> void:
    if not _dirty:
        return
    var data := {"entities": []}
    for entity in _active_entities:
        data["entities"].append(entity.serialize())
    var path := "user://saves/world/chunk_%d_%d.json" % [coord.x, coord.y]
    var file := FileAccess.open(path, FileAccess.WRITE)
    file.store_string(JSON.stringify(data))
```

## Navigation in open worlds

Each chunk gets its own `NavigationRegion3D` with a pre-baked `NavigationMesh`. Bake at editor time whenever possible — runtime baking is expensive and produces hitches on older hardware.

Stitch adjacent chunks using `NavigationLink3D` nodes at chunk borders. Place a pair of links (one per direction) at each walkable edge. When a chunk loads, register its `NavigationRegion3D` with `NavigationServer3D.region_set_enabled()`. When a chunk unloads, disable it.

```gdscript
func _instantiate_chunk(coord: Vector2i, res: ChunkResource) -> void:
    var region: NavigationRegion3D = preload("res://world/chunk_nav_region.tscn").instantiate()
    region.navigation_mesh = res.nav_mesh
    region.global_position = chunk_to_world_origin(coord)
    add_child(region)
    # NavigationServer updates automatically on next physics tick.
```

Dynamic obstacles (doors, fallen trees) use `NavigationObstacle3D` — they carve the navmesh in real-time without full rebaking. Use them for runtime blockers rather than triggering a bake.

## Quest and event scripting

Open-world quests must react to world events without polling the world state every frame. Use an event bus:

```gdscript
# event_bus.gd — autoload as EventBus
signal enemy_killed(enemy_id: StringName, killer: Node)
signal item_picked_up(item_id: StringName, picker: Node)
signal npc_spoken_to(npc_id: StringName, player: Node)
signal area_entered(area_id: StringName, entity: Node)
```

Quests are nodes that connect to the relevant signals when activated and disconnect when complete. The quest graph is a directed graph (nodes = quest steps, edges = dependencies). Do not model quests as a linear array — branching and optional steps require a graph.

```gdscript
# quest_kill_bandits.gd
class_name QuestKillBandits extends QuestBase

const REQUIRED_KILLS := 5
var _kills := 0

func _on_activated() -> void:
    EventBus.enemy_killed.connect(_on_enemy_killed)

func _on_enemy_killed(enemy_id: StringName, _killer: Node) -> void:
    if enemy_id == &"bandit":
        _kills += 1
        if _kills >= REQUIRED_KILLS:
            complete()

func _on_completed() -> void:
    EventBus.enemy_killed.disconnect(_on_enemy_killed)
```

Never query the scene tree for enemy count in `_process()` to check completion. Signal-driven quests have zero per-frame overhead when idle.

## LOD budget and simulation tiers

Assign every chunk a simulation tier based on distance from the player:

| Tier | Distance | Behavior |
|---|---|---|
| Active | ≤ LOAD_RADIUS/2 | Full AI, physics, animation, NavMesh live |
| Sleeping | ≤ LOAD_RADIUS | Position stored, AI paused, physics sleeping |
| Distant | > LOAD_RADIUS, ≤ UNLOAD_RADIUS | Static geometry only, no entities |

Implement tier transitions as signals from `ChunkManager` so AI, animation, and physics systems can suspend themselves cleanly rather than being force-stopped externally.

## Time-of-day and dynamic world

A global `Clock` autoload advances game time and emits signals at meaningful boundaries:

```gdscript
# clock.gd — autoload as Clock
signal hour_changed(hour: int)
signal sunrise          # fired at dawn
signal sunset           # fired at dusk
signal midnight

const DAY_LENGTH_SECONDS := 1200.0   # 20 real minutes = one game day
var time_of_day := 0.0               # 0.0-1.0, 0.5 = noon

func _process(delta: float) -> void:
    var prev := time_of_day
    time_of_day = fmod(time_of_day + delta / DAY_LENGTH_SECONDS, 1.0)
    var prev_h := int(prev * 24)
    var curr_h := int(time_of_day * 24)
    if curr_h != prev_h:
        hour_changed.emit(curr_h)
        if curr_h == 6:  sunrise.emit()
        if curr_h == 20: sunset.emit()
        if curr_h == 0:  midnight.emit()
```

Chunk systems subscribe to `Clock` signals to: spawn night enemies at sunset, despawn them at sunrise, open/close shops at business hours, advance crop growth at midnight. Avoid checking `Clock.time_of_day` in `_process()` per entity — subscribe to the hour signal once.

## Common mistakes

**Sync chunk loading in _process()** — `ResourceLoader.load()` blocks the main thread. Always use `load_threaded_request()` with a status poll.

**Single simulation radius for both graphics and AI** — geometry can be visible at long range with no performance cost. AI should be simulated at a much shorter radius. Keep these as separate constants.

**Forgetting origin shift** — skipping `WorldOriginShifter` is fine up to ~1 km. Above 2 km, physics jitter and float precision errors in Godot's physics engine become visible. Any world larger than 2 km needs origin shifting.

**Saving Resources with embedded signals or node references** — `JSON.stringify()` of a Resource that has scene-tree connections will serialize garbage or fail. Serialize plain data structures only.

**Per-entity A\* pathfinding in an open world** — with hundreds of active NPCs, per-entity A* requests every few seconds will saturate the NavigationServer. Use flow fields for crowd-scale pathing or strictly time-slice individual requests.

**No hysteresis on chunk load/unload** — using a single radius causes rapid repeated load/unload when the player walks along a chunk edge. Always load at LOAD_RADIUS and unload at LOAD_RADIUS + 1 or greater.
