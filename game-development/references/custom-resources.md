# Custom Resources and Data-Driven Design

## Defining a custom Resource

```gdscript
# weapon_data.gd
class_name WeaponData
extends Resource

@export var display_name: String = ""
@export var damage: int = 10
@export var fire_rate: float = 0.2
@export var spread_degrees: float = 5.0
@export var projectile_scene: PackedScene
@export var fire_sound: AudioStream
@export var icon: Texture2D
```

Save as `.tres` (text resource — VCS-friendly, human-readable) in the editor via File → Save As. Reference it from other Resources or load it at runtime. No code is needed to create new content — designers edit `.tres` files directly in the inspector.

## @export organization

```gdscript
class_name EnemyData
extends Resource

@export_group("Combat")
@export var health: int = 100
@export var damage: int = 15
@export var attack_range: float = 60.0

@export_group("Movement")
@export var speed: float = 80.0
@export var patrol_radius: float = 200.0

@export_group("Loot")
@export var drop_table: Array[ItemData] = []
@export var xp_value: int = 10
```

`@export_group` creates collapsible sections in the inspector. Typed arrays (`Array[ItemData]`) give edit-time type checking and correct inspector widgets.

## The shared-reference trap — always .duplicate()

Resource variables in GDScript are **references**. Multiple nodes that load the same `.tres` file share the same object. Mutating it at runtime changes it for every user:

```gdscript
# WRONG — every enemy shares the same EnemyData instance
var data: EnemyData = preload("res://data/goblin.tres")
data.health -= 10  # mutates the shared resource!

# CORRECT — each instance gets its own copy
var data: EnemyData = (preload("res://data/goblin.tres") as EnemyData).duplicate(true)
data.health -= 10  # safe, this instance only
```

`duplicate(true)` performs a **deep** copy — nested Resources (like an `Array[ItemData]`) are also duplicated. `duplicate(false)` (shallow) copies the top-level resource but still shares nested sub-resources.

**Rule**: template Resources stored in `res://data/` are read-only prototypes. Always call `.duplicate(true)` when creating a runtime instance that will be mutated.

## Resource inheritance

```gdscript
# item_data.gd
class_name ItemData
extends Resource
@export var item_name: String
@export var weight: float

# weapon_data.gd — extends ItemData
class_name WeaponData
extends ItemData
@export var damage: int

# consumable_data.gd
class_name ConsumableData
extends ItemData
@export var heal_amount: int
```

The inspector shows all exported properties from the entire inheritance chain. This lets a single inventory system handle any `ItemData` subclass via `is` checks or `match`.

## preload vs load vs ResourceLoader (async)

| | Use when |
|---|---|
| `preload("res://...")` | Small, always-needed data; resolved at compile time; blocks the frame if large |
| `load("res://...")` | One-off runtime loads that are fast (small resources, editor tooling) |
| `ResourceLoader.load_threaded_request()` | Large assets (scenes, audio, textures) needed during gameplay without hitching |

```gdscript
# Async load — call once when entering a loading state
func begin_load(path: String) -> void:
    ResourceLoader.load_threaded_request(path)

# Poll each frame until ready
func _process(_delta: float) -> void:
    match ResourceLoader.load_threaded_get_status(path):
        ResourceLoader.THREAD_LOAD_LOADED:
            var res := ResourceLoader.load_threaded_get(path)
            _on_resource_loaded(res)
        ResourceLoader.THREAD_LOAD_FAILED:
            push_error("Failed to load: " + path)
        _:
            pass  # still loading
```

## Saving a Resource at runtime

```gdscript
# Persist player config, custom item, or save state
func save_config(cfg: GameConfig) -> void:
    var err := ResourceSaver.save(cfg, "user://config.tres")
    if err != OK:
        push_error("Save failed: " + str(err))

func load_config() -> GameConfig:
    if not ResourceLoader.exists("user://config.tres"):
        return GameConfig.new()
    return load("user://config.tres") as GameConfig
```

`user://` maps to the OS-specific user data directory (Documents/AppData on Windows, ~/.local on Linux, etc.). Use `.tres` for human-readable saves, `.res` for binary (smaller, faster, not VCS-friendly).

## ResourceUID for path-independent references

Godot assigns a UID to every resource. Use `uid://...` paths in scripts that reference Resources across project reorganizations — UID references survive file moves and renames, while `res://` paths break:

```gdscript
# Robust — survives moving goblin.tres to a different folder
const GOBLIN := preload("uid://cb4z2...)
# Fragile — breaks if file moves
const GOBLIN := preload("res://data/enemies/goblin.tres")
```

The editor rewrites `res://` paths to `uid://` automatically when you move files inside the editor. Avoid moving files outside the editor (OS file manager).

## Data-driven factory pattern

```gdscript
# EnemySpawner.gd
@export var enemy_types: Array[EnemyData] = []
const EnemyScene := preload("res://scenes/enemy.tscn")

func spawn(data: EnemyData, pos: Vector2) -> Enemy:
    var e: Enemy = EnemyScene.instantiate()
    e.data = data.duplicate(true)  # each enemy gets its own copy
    e.global_position = pos
    add_child(e)
    return e
```

The `Enemy` scene is a single generic scene; the `EnemyData` resource drives all variation. Adding a new enemy type requires only a new `.tres` file, not a new scene or script.

## Arrays in @export — duplicate here too

```gdscript
# WRONG — all instances share the same Array object
class_name Inventory
extends Resource
@export var items: Array[ItemData] = []

# CORRECT — override _init to ensure per-instance arrays
func _init() -> void:
    items = []
```

Or call `inventory.duplicate(true)` when creating runtime instances from a template.

## Common mistakes

- Mutating a shared Resource without `.duplicate(true)` — most common production bug
- Using `preload()` for large scenes/audio inside tight loops — hitches on first load
- Forgetting `duplicate(true)` is deep and `duplicate(false)` (default) is shallow
- Storing mutable runtime state (cooldown timers, current health) in data Resources instead of in component nodes
- Moving resource files outside the editor, breaking `res://` path references
