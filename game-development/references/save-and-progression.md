# Save systems and meta-progression

Save systems are one of the last things a game needs and one of the first things that breaks when content ships. The pattern that causes endless pain: serialize the scene tree, skip versioning, and scatter save calls throughout the codebase. Fix all three from day one. This file covers when to use which save type, what to serialize, the dual-file meta-progression pattern, versioning/migrations, Godot 4 implementation, Unity equivalents, and the anti-patterns that produce corrupted saves in production.

---

## The three save types

### (a) Run save — roguelikes and single-session games

Volatile. One file. Deleted on death, on completion, or on quit (write on suspend, delete on next launch if the run is over). The sole purpose is to allow the player to close the game mid-run and resume from the same state — not to persist anything permanently.

**What it contains:** everything needed to reconstruct the current run from scratch — random seed, floor number, current entity positions and stats (as data IDs and values, not node references), inventory as item ID / quantity pairs, elapsed time, flags for events that happened this run. Nothing else.

**File:** a single `user://run.json` (or `run.save`). No slots, no rotating history. If a run file exists on startup, offer "Resume run?" or auto-resume. On death/win, delete the file, then update the meta file.

### (b) Checkpoint save — action games and platformers

Written at designated points only: after a boss, when the player steps into a save room, when they interact with a campfire or waypoint. The game reverts to the last checkpoint on death — the player re-traverses the segment.

Multiple slots are common (manual saves in addition to auto-checkpoint). File per slot: `user://saves/slot_0.json`, `slot_1.json`, etc. Each slot is independent: reading slot 1 has no effect on slot 0.

Checkpoint saves contain more than a run save: world state flags ("boss_A_dead": true), permanent unlocked areas, NPC state, current gear/stats. They do **not** re-save after every step — only at designated trigger points.

### (c) Continuous/autosave — RPGs and open-world games

Writes periodically (every N minutes) and on meaningful events (fast-travel, level-up, safe-zone entry, before a major story choice). Never block the main thread — disk writes on the main thread cause frame hitches. Use a background thread or async write.

In Godot 4: kick off a `Thread` that does the file write. In Unity: use `async Task` with `await File.WriteAllTextAsync(...)`. The game state is copied to an immutable snapshot dict/struct before handing it to the thread — you cannot let the thread read live game state while the main thread is mutating it.

Autosave slots: one or two rotating autosave slots plus the player's manual saves. Rotating prevents a single bad autosave from being the only option. Always write to `autosave_0.json`, then `autosave_1.json`, then back to 0 (round-robin).

---

## What to serialize vs what not to

**The model is the save; the view is rebuilt from it.**

Entity nodes, scene trees, Resources with signals, AnimationPlayers, physics state — none of these are serialized. They are recreated by the engine when the scene loads. The save file tells the game *what the world contains and what state those things are in*; the engine's scene system reconstructs the rendered, interactive version from that data.

### Serialize: the logical data model

- Entity IDs (string or int) plus their stat values (health, level, position)
- Positions as plain dicts: `{"x": 120.0, "y": -32.0}` or `{"x": 0.0, "y": 1.0, "z": 5.0}` — not as Vector2/Vector3 objects, which are engine types and not guaranteed to survive engine version changes or cross-engine loads
- Item IDs and quantities — `[{"id": "sword_iron", "qty": 1}, {"id": "potion_hp", "qty": 4}]` — not item objects or nodes
- The dungeon/world seed (an int or string) and enough parameters to regenerate the same world
- Floor/level number and name
- Boolean flags for story events, unlocks, tutorial completion, collectibles
- Timestamps (for "time played" and autosave metadata)
- Settings that affect gameplay (difficulty, assist options) — separate from display/audio settings

### Do not serialize

- Engine objects: Nodes, Resources (the Godot Resource class with signals), RigidBodies mid-physics, scene paths
- Textures, audio streams, shader parameters — rebuild from file at load time using preload/load
- Runtime caches: computed pathfinding data, spatial partitions, enemy perception state — these are transient and rebuilt on spawn
- Node paths or scene-relative indices — these break the moment you restructure a scene
- References to other nodes (use IDs and a lookup table instead)

---

## Meta-progression pattern

Two files, two separate lifetimes:

**`user://run.json`** — volatile, exists only during an active run. Created when a new run begins. Updated on meaningful run events and on game close. Deleted on death, win, or abandon. If present at startup, offer resume.

**`user://meta.json`** — persistent forever, survives across runs, never deleted (only updated). Tracks:
- `unlocked_characters: Array[String]` — IDs of characters unlocked through gameplay
- `unlocked_items: Array[String]` — items available in future runs via meta unlock
- `total_currency: int` — cumulative meta-currency across all runs
- `best_run: Dict` — `{"floor": int, "score": int, "character": String, "timestamp": int}`
- `total_runs: int`, `total_wins: int`
- `achievement_flags: Dict[String, bool]` — one key per achievement
- `version: int` — required, see below

**On run completion or death:**
1. Tally run score
2. Load meta file (or create defaults if first run)
3. Update meta: add earned currency, check/set achievements, update best run if better, increment counters
4. Save updated meta
5. Delete run file

**On game launch:**
1. Load meta (create with defaults if missing)
2. Check for run file — if present, prompt "Resume run?" or auto-resume based on genre convention
3. If no run file: go to main menu

**On starting a new run:**
1. Delete any existing run file (belt and suspenders — there should not be one)
2. Apply any meta unlocks to the run's starting state (starting character choice, unlocked starting items)
3. Write initial run file

---

## Save format versioning

Every save file gets a `"version": int` field from day one. Not when it seems necessary — from day one. Missing this field means every content update that adds a new stat or changes a data structure has the potential to corrupt existing saves.

**Load function contract:**

```
1. Read the file
2. Check "version" field (default to 0 if missing — old saves before versioning was added)
3. Run migration functions in sequence until at current version
4. Back up original before migration (copy to .bak)
5. Return migrated data
```

**Migration function skeleton (GDScript):**

```gdscript
const CURRENT_VERSION := 3

func load_with_migration(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    
    var file := FileAccess.open(path, FileAccess.READ)
    var data: Dictionary = JSON.parse_string(file.get_as_text())
    file.close()
    
    if data.is_empty():
        push_error("Save file corrupt or unreadable: %s" % path)
        return {}
    
    var version: int = data.get("version", 0)
    
    # Back up before any migration
    if version < CURRENT_VERSION:
        DirAccess.copy_absolute(path, path + ".bak")
    
    # Run each migration in order
    if version < 1:
        data = _migrate_v0_to_v1(data)
    if version < 2:
        data = _migrate_v1_to_v2(data)
    if version < 3:
        data = _migrate_v2_to_v3(data)
    
    data["version"] = CURRENT_VERSION
    return data

func _migrate_v0_to_v1(data: Dictionary) -> Dictionary:
    # v1 added "total_runs" — default to 0 for existing saves
    data["total_runs"] = data.get("total_runs", 0)
    return data

func _migrate_v1_to_v2(data: Dictionary) -> Dictionary:
    # v2 added "unlocked_items" array and renamed "gold" to "total_currency"
    data["unlocked_items"] = data.get("unlocked_items", [])
    if "gold" in data:
        data["total_currency"] = data["gold"]
        data.erase("gold")
    else:
        data["total_currency"] = data.get("total_currency", 0)
    return data

func _migrate_v2_to_v3(data: Dictionary) -> Dictionary:
    # v3 split best_score (int) into best_run (dict)
    if "best_score" in data:
        data["best_run"] = {"floor": 0, "score": data["best_score"], "character": "unknown", "timestamp": 0}
        data.erase("best_score")
    else:
        data["best_run"] = data.get("best_run", {"floor": 0, "score": 0, "character": "none", "timestamp": 0})
    return data
```

The migration chain is append-only. Never edit an existing migration function — add a new one. Migrations should never fail on reasonable inputs; inject safe defaults for missing keys rather than crashing.

---

## Godot 4 implementation

### Paths

`user://` is the user data directory — writable on all platforms (desktop, mobile, console-export paths vary but Godot handles routing). Never write save files to `res://`; that path is read-only in exported games.

```
user://meta.json          # meta-progression
user://run.json           # active run (roguelike)
user://saves/slot_0.json  # checkpoint slot 0
user://saves/slot_1.json  # checkpoint slot 1
user://settings.cfg       # audio, display, keybindings (ConfigFile)
```

### JSON save (recommended for development; debuggable in any text editor)

```gdscript
const META_PATH := "user://meta.json"
const RUN_PATH := "user://run.json"

func save_json(path: String, data: Dictionary) -> void:
    var dir := path.get_base_dir()
    if not DirAccess.dir_exists_absolute(dir):
        DirAccess.make_dir_recursive_absolute(dir)
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        push_error("Cannot open save file for writing: %s" % path)
        return
    file.store_string(JSON.stringify(data, "\t"))
    file.close()

func load_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        push_error("Cannot open save file for reading: %s" % path)
        return {}
    var text := file.get_as_text()
    file.close()
    var result = JSON.parse_string(text)
    if result == null or not result is Dictionary:
        push_error("Save file parse failed: %s" % path)
        return {}
    return result
```

### Binary save (smaller, faster; not human-readable)

Use `store_var` / `get_var` for binary serialization. Godot serializes most built-in types (Dictionary, Array, int, float, String, Vector2, Vector3, Color). Still prefer storing positions as plain dicts if you care about cross-version stability; Vector2 stored via `store_var` can break between engine versions if the binary format changes.

```gdscript
func save_binary(path: String, data: Dictionary) -> void:
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        return
    file.store_var(data)
    file.close()

func load_binary(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        return {}
    var data = file.get_var()
    file.close()
    return data if data is Dictionary else {}
```

### ConfigFile — settings only, not game state

ConfigFile is right for key-value settings (volume, display resolution, keybindings, accessibility options). It is not appropriate for game state — it has no versioning support and its section/key structure is awkward for nested data.

```gdscript
var config := ConfigFile.new()

func save_settings(volume: float, fullscreen: bool) -> void:
    config.set_value("audio", "master_volume", volume)
    config.set_value("display", "fullscreen", fullscreen)
    config.save("user://settings.cfg")

func load_settings() -> void:
    config.load("user://settings.cfg")
    var volume: float = config.get_value("audio", "master_volume", 1.0)
    var fullscreen: bool = config.get_value("display", "fullscreen", false)
```

### Dual run/meta pattern — full skeleton

```gdscript
extends Node

const RUN_PATH := "user://run.json"
const META_PATH := "user://meta.json"
const META_VERSION := 2
const RUN_VERSION := 1

# --- Meta ---

func load_meta() -> Dictionary:
    var data := load_json(META_PATH)
    if data.is_empty():
        return _default_meta()
    return load_with_migration(META_PATH)  # applies version migrations

func save_meta(meta: Dictionary) -> void:
    meta["version"] = META_VERSION
    save_json(META_PATH, meta)

func _default_meta() -> Dictionary:
    return {
        "version": META_VERSION,
        "unlocked_characters": ["default"],
        "unlocked_items": [],
        "total_currency": 0,
        "total_runs": 0,
        "total_wins": 0,
        "best_run": {"floor": 0, "score": 0, "character": "none", "timestamp": 0},
        "achievement_flags": {}
    }

# --- Run ---

func has_active_run() -> bool:
    return FileAccess.file_exists(RUN_PATH)

func save_run(run_state: Dictionary) -> void:
    run_state["version"] = RUN_VERSION
    save_json(RUN_PATH, run_state)

func load_run() -> Dictionary:
    return load_json(RUN_PATH)

func delete_run() -> void:
    if FileAccess.file_exists(RUN_PATH):
        DirAccess.remove_absolute(RUN_PATH)

# --- On run end (death or win) ---

func on_run_ended(run_state: Dictionary, won: bool) -> void:
    var meta := load_meta()
    
    # Update cumulative stats
    meta["total_runs"] = meta.get("total_runs", 0) + 1
    if won:
        meta["total_wins"] = meta.get("total_wins", 0) + 1
    
    # Add earned currency
    meta["total_currency"] = meta.get("total_currency", 0) + run_state.get("earned_currency", 0)
    
    # Update best run
    var best: Dictionary = meta.get("best_run", {})
    if run_state.get("score", 0) > best.get("score", 0):
        meta["best_run"] = {
            "floor": run_state.get("floor", 0),
            "score": run_state.get("score", 0),
            "character": run_state.get("character_id", "unknown"),
            "timestamp": int(Time.get_unix_time_from_system())
        }
    
    # Unlock any earned unlocks
    for unlock_id in run_state.get("earned_unlocks", []):
        var arr: Array = meta.get("unlocked_characters", [])
        if unlock_id not in arr:
            arr.append(unlock_id)
            meta["unlocked_characters"] = arr
    
    save_meta(meta)
    delete_run()
```

### Async write (continuous autosave — avoid main-thread blocking)

```gdscript
var _save_thread: Thread = null

func autosave_async(path: String, data: Dictionary) -> void:
    if _save_thread != null and _save_thread.is_started():
        _save_thread.wait_to_finish()  # don't queue more than one write at a time
    # Snapshot the data before handing it off — never let a thread read live state
    var snapshot := data.duplicate(true)
    _save_thread = Thread.new()
    _save_thread.start(_write_to_disk.bind(path, snapshot))

func _write_to_disk(path: String, data: Dictionary) -> void:
    save_json(path, data)
    # Thread exits; call wait_to_finish() before starting another
```

Call `_save_thread.wait_to_finish()` in `_notification(NOTIFICATION_WM_CLOSE_REQUEST)` to ensure the final write completes before the process exits.

---

## Unity equivalents

| Purpose | Godot 4 | Unity |
|---|---|---|
| Simple JSON | `JSON.stringify` / `JSON.parse_string` | `JsonUtility.ToJson` / `FromJson` (limited: no Dictionaries, no polymorphism) |
| Complex JSON | — | **Newtonsoft.Json** (`JsonConvert.SerializeObject`): handles dicts, inheritance, nullables, custom converters — recommended for anything non-trivial |
| Binary | `store_var` / `get_var` | `BinaryFormatter` — **deprecated**, security vulnerabilities (deserialization exploits), do not use in new code; prefer JSON or a serialization library |
| Settings only | `ConfigFile` | `PlayerPrefs` — key/value store backed by registry (Windows) or plist (macOS/iOS); suitable for volume, resolution, keybindings; not for game state |
| Save location | `user://` | `Application.persistentDataPath` — platform-correct writable directory; never use `Application.dataPath` (read-only in builds) |
| Async write | `Thread` + `store_var` | `async Task` + `await File.WriteAllTextAsync(path, json)` |

Unity example — JSON with versioning:

```csharp
[Serializable]
public class MetaSave {
    public int version = 2;
    public List<string> unlockedCharacters = new() { "default" };
    public int totalCurrency;
    public int totalRuns;
    public BestRun bestRun = new();
}

public static void SaveMeta(MetaSave meta) {
    string path = Path.Combine(Application.persistentDataPath, "meta.json");
    string json = JsonConvert.SerializeObject(meta, Formatting.Indented);
    File.WriteAllText(path, json);
}

public static MetaSave LoadMeta() {
    string path = Path.Combine(Application.persistentDataPath, "meta.json");
    if (!File.Exists(path)) return new MetaSave();
    string json = File.ReadAllText(path);
    var data = JsonConvert.DeserializeObject<MetaSave>(json) ?? new MetaSave();
    return Migrate(data);
}
```

---

## Anti-patterns

**Storing the scene tree.** `PackedScene` or node references in a save file couple your serialization to your scene structure. Rename a node, restructure a scene, or change a script and the save breaks silently. Store IDs and data values only.

**No version field.** Ship without versioning, add a new field in a patch, and every existing save file is now missing that field. If you read it with no default, you get a null or error. If the missing field is a required key (say, a character ID), the game crashes or corrupts. A `"version": 0` field costs two lines and prevents this class of problem entirely.

**Saving node paths or get_node paths.** `"/root/World/Enemies/Goblin_3"` is a runtime address. It does not exist in the next session. Save entity IDs (strings or ints managed by your entity registry), and look up the node by ID at load time.

**No validation on load.** Saves can be incomplete (crash mid-write), from older versions (missing fields), or edited by the player. Always inject default values for missing keys; never index a dict without `.get(key, default)`. Validate numeric ranges (health can't be negative; floor can't be 999 if the max is 20). Fail gracefully — if a save is unrecoverable, tell the player and offer to reset to defaults rather than crashing.

**Blocking the main thread on writes.** `FileAccess.open` + `store_string` on the main thread is synchronous. On a large open-world save this can stall for tens of milliseconds — enough to cause a visible frame drop. Move disk writes to a thread. Reads at startup (before the game loop is running) are fine on the main thread.

**Using `GetComponent`/`get_node` paths in save data.** Same as the node path problem: a runtime call result cannot be serialized to disk meaningfully.

**One giant save file for everything.** Mixing settings, run state, and meta-progression in one file means a settings change forces a full game-state write (slow), and a corrupt game state can wipe settings. Keep them separate.

---

## Save encryption and anti-tamper

**Single-player games: not worth it.** Determined players will always extract the key. The complexity cost (key management, cipher integration, decryption at load time) is high; the benefit is near zero for a game with no online leaderboard or competitive mode.

**Competitive / leaderboard games: server-authoritative validation.** The client submits a run result; the server validates it against expected ranges and the run's seed. No amount of client-side encryption prevents a player from submitting arbitrary API calls. The only secure boundary is the server. If the leaderboard matters, validate on the server — client-side protection is theater.

**If you must encrypt (e.g., a publisher requires it for console cert):** AES-256 on the binary save file. Store the key in a compiled constant (not a config file). Accept that a motivated reverser will find it. Use Godot's `FileAccess.open_encrypted_with_pass(path, mode, passphrase)` — built-in, no external library required. The passphrase can be derived from a hardware ID or an online token for slightly better resistance.

The rule: let players edit single-player saves if they want to — save editing is a decades-old tradition and costs you nothing. Protect the things that affect other players (online scores, shared economies) on the server, not through client obfuscation.
