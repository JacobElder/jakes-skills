# Analytics and Playtesting Instrumentation

Playtesting tells you what players do in the room with you. Telemetry tells you what they do at scale across all your players. Both are required: watching 5 people play reveals UX friction and confusing mechanics; telemetry from 500 sessions reveals balance issues, drop-off points, and which abilities are never used.

The implementation cost is low. The failure mode is either instrumenting nothing (flying blind) or instrumenting everything every frame (drowning in noise).

## Contents
- The right granularity: events, not sampling
- TelemetryManager autoload
- Session lifecycle events
- Core event set (minimum viable)
- Death heatmap
- Player path recording
- Storage: local file vs server
- Privacy and anonymization
- Stripping telemetry from release builds
- Playtest build instrumentation
- Input frequency analysis
- Post-playtest analysis workflow

## The right granularity: events, not sampling

**Don't sample state every frame.** Storing `{position, health, ammo}` 60 times per second for a 30-minute session produces 108,000 data points per variable. It's expensive to write, expensive to analyze, and mostly noise.

**Do emit discrete events when something notable happens.** A `player_died` event with position and cause contains everything you need for a death heatmap — without logging 108,000 health values to find the one where health hit 0.

The right question before adding any telemetry: "What decision will I make differently based on this data?" If you can't name the decision, don't collect the data.

## TelemetryManager autoload

```gdscript
# TelemetryManager.gd — autoload at /root/TelemetryManager
extends Node

const FLUSH_INTERVAL := 60.0  # write to disk every 60 seconds
const MAX_BUFFER := 200        # also flush if buffer gets large

var session_id: String = ""
var _event_buffer: Array[Dictionary] = []
var _flush_timer: float = 0.0
var _log_file: FileAccess = null

func _ready() -> void:
    if not TELEMETRY_ENABLED:
        return
    session_id = _generate_session_id()
    var path := "user://telemetry/%s.jsonl" % session_id
    DirAccess.make_dir_recursive_absolute("user://telemetry")
    _log_file = FileAccess.open(path, FileAccess.WRITE)
    emit_event("session_started", {
        "build_version": ProjectSettings.get_setting("application/config/version", "unknown"),
        "platform": OS.get_name(),
        "display_resolution": "%dx%d" % [DisplayServer.window_get_size().x, DisplayServer.window_get_size().y],
    })

func _process(delta: float) -> void:
    if not TELEMETRY_ENABLED:
        return
    _flush_timer += delta
    if _flush_timer >= FLUSH_INTERVAL or _event_buffer.size() >= MAX_BUFFER:
        _flush()

func _notification(what: int) -> void:
    if what == NOTIFICATION_WM_CLOSE_REQUEST:
        emit_event("session_ended", {
            "total_playtime": Time.get_ticks_msec() / 1000.0,
        })
        _flush()

func emit_event(event_name: String, payload: Dictionary = {}) -> void:
    if not TELEMETRY_ENABLED:
        return
    var event := {
        "event": event_name,
        "time": Time.get_unix_time_from_system(),
        "session": session_id,
    }
    event.merge(payload)
    _event_buffer.append(event)

func _flush() -> void:
    if _log_file == null or _event_buffer.is_empty():
        return
    for event in _event_buffer:
        _log_file.store_line(JSON.stringify(event))
    _log_file.flush()
    _event_buffer.clear()
    _flush_timer = 0.0

func _generate_session_id() -> String:
    # Random 12-hex-char ID — not tied to player identity
    return "%08x%04x" % [randi(), randi() & 0xFFFF]
```

`TELEMETRY_ENABLED` is a project-level const defined in an autoload or a global script, controlled by a build flag. Never call emit_event() inside code that won't be stripped in release builds.

## Session lifecycle events

```gdscript
# On level start
TelemetryManager.emit_event("level_started", {
    "level_id": level_id,
    "attempt": _attempt_number,
})

# On level complete
TelemetryManager.emit_event("level_completed", {
    "level_id": level_id,
    "time_seconds": _level_timer,
    "deaths": _death_count,
})

# On player death
TelemetryManager.emit_event("player_died", {
    "level_id": level_id,
    "position": {"x": player.position.x, "y": player.position.y},
    "cause": death_cause,       # "enemy_contact", "fall", "projectile", etc.
    "time_alive": _time_alive,
    "enemy_type": last_attacker_type,
})

# On ability use
TelemetryManager.emit_event("ability_used", {
    "ability_id": ability.ability_id,
    "hit": did_hit,
    "target_type": target_type,
})
```

Keep payloads flat dictionaries. Avoid nesting beyond one level — it complicates analysis queries.

## Core event set (minimum viable)

These 6 events answer the most important design questions for any game:

| Event | Key payload fields | Answers |
|---|---|---|
| `session_started` | build_version, platform | How many sessions? Which platform? Which build? |
| `level_started` | level_id, attempt | Which levels do players reach? How many attempts per level? |
| `player_died` | level_id, position, cause | Where and why do players die? (heatmap) |
| `level_completed` | level_id, time_seconds, deaths | What % complete? How long does each level take? |
| `ability_used` | ability_id, hit | Are all abilities being used? Which have low hit rates? |
| `session_ended` | total_playtime, levels_completed | Session length, retention |

Add events for specific systems (item_purchased, checkpoint_reached, tutorial_skipped) as those systems mature and design questions arise.

## Death heatmap

Death positions are the highest-signal single data type in most action games. They reveal: unfair difficulty spikes, unclear hazards, confusing layout, and successful challenge points.

```gdscript
# DeathHeatmap.gd — debug overlay
extends Node2D

const DEATH_RADIUS := 8.0
const MAX_DEATHS_FOR_FULL_COLOR := 5.0
const GRADIENT := {0.0: Color.BLUE, 0.5: Color.YELLOW, 1.0: Color.RED}

var death_positions: Array[Vector2] = []

func load_from_telemetry(session_files: Array[String]) -> void:
    for path in session_files:
        var file := FileAccess.open(path, FileAccess.READ)
        while not file.eof_reached():
            var line := file.get_line()
            var event: Dictionary = JSON.parse_string(line)
            if event.get("event") == "player_died":
                death_positions.append(Vector2(event["position"]["x"], event["position"]["y"]))
    queue_redraw()

func _draw() -> void:
    for pos in death_positions:
        # Compute local density
        var nearby_count := 0
        for other in death_positions:
            if pos.distance_to(other) < DEATH_RADIUS * 2.0:
                nearby_count += 1
        var density := clamp(float(nearby_count) / MAX_DEATHS_FOR_FULL_COLOR, 0.0, 1.0)
        var color := Color.BLUE.lerp(Color.RED, density)
        color.a = 0.6
        draw_circle(pos, DEATH_RADIUS, color)
```

Attach this as a child of the level's canvas layer in debug builds. Call `load_from_telemetry()` with the telemetry files from a completed playtest.

## Player path recording

Sample player position every 3-5 seconds. Not every frame — that's 10,800 points per 30-minute session, overwhelming to visualize and expensive to store. Every 5 seconds is 360 points — enough to see routes clearly.

```gdscript
# PathRecorder.gd
extends Node

const SAMPLE_INTERVAL := 5.0

var _timer: float = 0.0
var _path: Array[Vector2] = []

func _process(delta: float) -> void:
    if not TELEMETRY_ENABLED:
        return
    _timer += delta
    if _timer >= SAMPLE_INTERVAL:
        _timer = 0.0
        _path.append(owner.global_position)

func flush() -> void:
    TelemetryManager.emit_event("player_path", {
        "level_id": LevelManager.current_level_id,
        "positions": _path.map(func(p): return {"x": p.x, "y": p.y}),
    })
    _path.clear()
```

Flush on level complete or death. Visualize as a polyline in the debug overlay — areas with few or no paths are exploration deserts (players aren't finding that content).

## Storage: local file vs server

**Development and playtests**: write to `user://telemetry/{session_id}.jsonl` as line-delimited JSON (one event per line, append mode). Files persist between runs and are easy to parse with a Python script.

**Production** (if shipping telemetry): POST events to an endpoint in batches:

```gdscript
func _send_to_server(events: Array[Dictionary]) -> void:
    var body := JSON.stringify({"events": events})
    var headers := ["Content-Type: application/json"]
    var http := HTTPRequest.new()
    add_child(http)
    http.request(TELEMETRY_ENDPOINT, headers, HTTPClient.METHOD_POST, body)
    http.request_completed.connect(func(_result, _code, _h, _body): http.queue_free())
```

Never block gameplay waiting for the network. Fire-and-forget. Queue events locally if the network is unavailable, retry on next flush.

## Privacy and anonymization

- **session_id is random** — not a player username, Steam ID, email address, or device fingerprint. Generate via `randi()`.
- **Positions are level-relative**, not absolute world coordinates. A death at `(42, 18)` in `level_04` is not personally identifiable.
- **No PII (personally identifiable information)**: no names, emails, IP addresses, or account IDs in telemetry events.
- **GDPR/CCPA**: if your game ships in the EU or California, you need a consent prompt before collecting telemetry. Display it at first launch. Respect the player's choice. Store consent in `user://settings.json`.

For internal playtests: inform testers in writing that the session is being logged. Anonymize tester IDs (assign `Tester_01`, `Tester_02`) rather than using names.

## Stripping telemetry from release builds

```gdscript
# globals.gd (autoload)
const TELEMETRY_ENABLED: bool = OS.is_debug_build()
# Or use a build-time export flag:
# const TELEMETRY_ENABLED: bool = false  # set to true for analytics builds
```

All `TelemetryManager.emit_event()` calls check this constant first. In release builds the entire method body is skipped. Do not ship debug telemetry endpoints or local file paths to players without explicit opt-in.

## Playtest build instrumentation

Before a playtest session with external testers, add these four features — they cost < 2 hours to implement and dramatically improve the quality of data and feedback:

**1. Auto-generated session log:**
```gdscript
func _ready() -> void:
    var log_path := "user://playtest_logs/session_%s.json" % session_id
    DirAccess.make_dir_recursive_absolute("user://playtest_logs")
    _session_data = {
        "session_id": session_id,
        "build": ProjectSettings.get_setting("application/config/version", "dev"),
        "start_time": Time.get_datetime_string_from_system(),
        "levels": [],
    }
```

**2. Screenshot shortcut:**
```gdscript
func _input(event: InputEvent) -> void:
    if event.is_action_just_pressed("debug_screenshot"):
        var img := get_viewport().get_texture().get_image()
        var ts := Time.get_unix_time_from_system()
        var path := "user://screenshots/screenshot_%d_%s.png" % [ts, LevelManager.current_level_id]
        DirAccess.make_dir_recursive_absolute("user://screenshots")
        img.save_png(path)
```

Bind to F9 or a controller shortcut unused in gameplay.

**3. In-game feedback button:**
A small floating button (always visible, partial opacity). On click: opens a one-field LineEdit for text input. On submit: appends `{time, level_id, position, text}` to the session log. Players type "this gap is confusing" where they're standing, not after the fact.

**4. Build version display:**
```gdscript
# Always-visible small label in a corner CanvasLayer
$BuildLabel.text = "v%s (%s)" % [
    ProjectSettings.get_setting("application/config/version", "dev"),
    ProjectSettings.get_setting("application/config/version/build_date", ""),
]
```

Critical for correlating feedback to a specific build when iterating rapidly across multiple playtest days.

## Input frequency analysis

Which abilities are being ignored?

```gdscript
# InputAnalyzer.gd
extends Node

var _action_counts: Dictionary = {}

func _input(event: InputEvent) -> void:
    if not TELEMETRY_ENABLED:
        return
    for action in InputMap.get_actions():
        if event.is_action_pressed(action):
            _action_counts[action] = _action_counts.get(action, 0) + 1

func flush_to_telemetry() -> void:
    TelemetryManager.emit_event("input_frequency", {
        "level_id": LevelManager.current_level_id,
        "counts": _action_counts,
        "duration_seconds": _session_duration,
    })
    _action_counts.clear()
```

An ability with 0 uses in a 30-minute session is either undiscoverable, feels weak, or has confusing keybinding. An ability used 1,200 times in 30 minutes has probably become an exploit.

## Post-playtest analysis workflow

1. **Collect files**: copy `user://telemetry/` and `user://playtest_logs/` from each tester's machine (or receive as uploads).
2. **Aggregate deaths**: parse all JSONL files, filter `player_died` events, render death heatmap over a level screenshot.
3. **Completion funnel**: count `level_started` vs `level_completed` per level_id → completion rate. Any level below 60% is failing (too hard, too confusing, or broken).
4. **Time analysis**: histogram of `level_completed.time_seconds` per level — identify outliers (players taking 10× the average probably got lost).
5. **Ability usage**: sort abilities by use count — bottom 20% are candidates for redesign or visibility improvement.
6. **Path visualization**: overlay path recordings on the level map — identify rooms no one visits, corridors everyone skips, and bottleneck areas where all paths converge.
7. **Feedback correlation**: match tester feedback notes (from the in-game feedback button) to position + time — map written notes to specific game moments.

A Python script with `json`, `matplotlib`, and `PIL` (for overlaying on level screenshots) handles all of this in < 100 lines.
