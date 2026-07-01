# Stealth AI

## Detection architecture

Never do detection in one step. The correct order — cheapest first — is:

1. **Distance check** (O(1), one subtraction + compare)
2. **Angle / FOV check** (dot product, O(1))
3. **Line-of-sight raycast** (expensive — only fire when steps 1 and 2 pass)

```gdscript
# Guard.gd
@export var detection_range: float = 200.0
@export var fov_degrees: float = 90.0         # half-angle = 45° on each side
@export var detection_rate: float = 1.0       # points/sec when player in cone
@export var suspicion_decay: float = 0.4      # points/sec when player out of sight

var detection_level: float = 0.0             # 0 = unaware, 1+ = fully alerted
var last_known_position: Vector2 = Vector2.ZERO

func _physics_process(delta: float) -> void:
    _update_detection(delta)
    _run_state(delta)

func _can_see_player() -> bool:
    var to_player := player.global_position - global_position
    # 1. Distance
    if to_player.length() > detection_range:
        return false
    # 2. Angle (dot product vs forward direction)
    var half_fov := deg_to_rad(fov_degrees / 2.0)
    if to_player.normalized().dot(facing_direction()) < cos(half_fov):
        return false
    # 3. Line of sight raycast
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(
        global_position,
        player.global_position,
        0b0100   # layer 3: walls only — exclude other guards, items, etc.
    )
    query.exclude = [self]
    var hit := space.intersect_ray(query)
    return hit.is_empty() or hit["collider"] == player

func _update_detection(delta: float) -> void:
    if _can_see_player():
        # Detection fills faster if player is moving or close
        var dist_factor := 1.0 - (global_position.distance_to(player.global_position) / detection_range)
        var move_factor := 1.5 if player.velocity.length() > 10.0 else 1.0
        detection_level += detection_rate * dist_factor * move_factor * delta
        if detection_level >= 1.0:
            detection_level = 1.0
            last_known_position = player.global_position
    else:
        detection_level = max(0.0, detection_level - suspicion_decay * delta)
```

## Alert state machine

Five states — not three booleans:

```
PATROL → (detection ≥ 0.3) → SUSPICIOUS
SUSPICIOUS → (detection ≥ 1.0) → ALERT
SUSPICIOUS → (lost sight, detection dropped) → SEARCH → PATROL
ALERT → (lost sight) → SEARCH
SEARCH → (found nothing for search_time) → PATROL
```

```gdscript
enum State { PATROL, SUSPICIOUS, ALERT, SEARCH, RETURNING }

var _state: State = State.PATROL
var _search_timer: float = 0.0
var _search_positions: Array[Vector2] = []
var _current_waypoint: int = 0

@export var waypoints: Array[Vector2] = []
@export var patrol_speed: float = 60.0
@export var alert_speed: float = 140.0
@export var search_duration: float = 8.0

func _run_state(delta: float) -> void:
    match _state:
        State.PATROL:      _tick_patrol(delta)
        State.SUSPICIOUS:  _tick_suspicious(delta)
        State.ALERT:       _tick_alert(delta)
        State.SEARCH:      _tick_search(delta)
        State.RETURNING:   _tick_returning(delta)

    # State transitions from detection level
    match _state:
        State.PATROL, State.RETURNING:
            if detection_level >= 0.3:
                _enter_state(State.SUSPICIOUS)
        State.SUSPICIOUS:
            if detection_level >= 1.0:
                _enter_state(State.ALERT)
            elif detection_level <= 0.0:
                _enter_state(State.SEARCH)
        State.ALERT:
            if not _can_see_player() and detection_level < 0.3:
                _search_timer = search_duration
                _search_positions = _generate_search_positions(last_known_position)
                _enter_state(State.SEARCH)

func _enter_state(new_state: State) -> void:
    _state = new_state
    match new_state:
        State.SUSPICIOUS:
            animation_player.play("look_around")
            _nav_agent.max_speed = patrol_speed * 0.7
        State.ALERT:
            _play_alert_bark()
            _nav_agent.max_speed = alert_speed
            # Optional: radio other guards
            emit_signal("guard_alerted", last_known_position)
        State.SEARCH:
            _nav_agent.max_speed = patrol_speed * 0.9
        State.PATROL:
            _nav_agent.max_speed = patrol_speed

func _tick_patrol(delta: float) -> void:
    if waypoints.is_empty():
        return
    var target := waypoints[_current_waypoint]
    _nav_agent.target_position = target
    if _nav_agent.is_navigation_finished():
        _current_waypoint = (_current_waypoint + 1) % waypoints.size()
        # Brief pause at each waypoint
        await get_tree().create_timer(randf_range(0.5, 1.5)).timeout
    _move_toward_target(delta)

func _tick_suspicious(delta: float) -> void:
    # Turn toward where the player was last seen
    var to_player := last_known_position - global_position
    _look_toward(to_player.normalized(), delta)

func _tick_alert(delta: float) -> void:
    last_known_position = player.global_position
    _nav_agent.target_position = last_known_position
    _move_toward_target(delta)

func _tick_search(delta: float) -> void:
    _search_timer -= delta
    if _search_timer <= 0.0 or _search_positions.is_empty():
        _enter_state(State.RETURNING)
        return
    if _nav_agent.is_navigation_finished() and not _search_positions.is_empty():
        _search_positions.pop_front()
        if not _search_positions.is_empty():
            _nav_agent.target_position = _search_positions[0]
    _move_toward_target(delta)

func _generate_search_positions(origin: Vector2) -> Array[Vector2]:
    # Check last known position, then fan out in a small radius
    return [
        origin,
        origin + Vector2(randf_range(-60, 60), randf_range(-60, 60)),
        origin + Vector2(randf_range(-60, 60), randf_range(-60, 60)),
    ]
```

## Sound propagation (simplified)

```gdscript
# SoundEvent.gd — emitted by player actions
class_name SoundEvent

var position: Vector2
var radius: float
var is_alert: bool   # true = immediate alert; false = suspicious

# Player emits sounds on actions:
func _on_jump() -> void:
    SoundManager.emit_sound(SoundEvent.new(global_position, 120.0, false))

func _on_land() -> void:
    SoundManager.emit_sound(SoundEvent.new(global_position, 200.0, true if crouching else false))
```

```gdscript
# SoundManager.gd — autoload
func emit_sound(event: SoundEvent) -> void:
    for guard in get_tree().get_nodes_in_group("guards"):
        var dist := guard.global_position.distance_to(event.position)
        if dist <= event.radius:
            guard.hear_sound(event)
```

```gdscript
# Guard.gd
func hear_sound(event: SoundEvent) -> void:
    last_known_position = event.position
    if event.is_alert:
        detection_level = 1.0
        _enter_state(State.ALERT)
    else:
        detection_level = max(detection_level, 0.5)
        _enter_state(State.SUSPICIOUS)
```

## Detection meter UI

Show the player how detected they are — never let detection be invisible.

```gdscript
# DetectionMeter.gd — attached to guard, visible above their head
@onready var meter: ProgressBar = $ProgressBar
@onready var icon: Sprite2D = $Icon        # ? icon for suspicious, ! for alert

func _process(_delta: float) -> void:
    meter.value = guard.detection_level * 100.0
    meter.visible = guard.detection_level > 0.0
    match guard._state:
        Guard.State.SUSPICIOUS: icon.texture = suspicious_icon
        Guard.State.ALERT:      icon.texture = alert_icon
        _:                      icon.texture = null
```

## Patrol waypoint setup (Godot)

```gdscript
# Place Path2D nodes in the editor; guard follows the curve's points
@export var patrol_path: Path2D

func _ready() -> void:
    if patrol_path:
        waypoints = patrol_path.curve.get_baked_points()
        # Find nearest waypoint to start from (don't snap to path[0])
        _current_waypoint = _nearest_waypoint_index()
```

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| Raycast every frame without distance/angle pre-check | Expensive; raycast fires even for far-away guards | Distance → angle → raycast (cheapest first) |
| Instant detection | No player agency; feels unfair | Detection meter fills over time |
| Three boolean flags (`is_suspicious`, `is_alert`, `is_searching`) | State logic leaks everywhere | Enum state machine with `_enter_state` |
| All guards share one `last_known_position` | One guard alerts all guards to exact position | Each guard has its own `last_known_position`; emit signal with approximate area |
| Guard returns to start of patrol route after search | Obvious tell; player can exploit it | Return to nearest waypoint, not waypoint[0] |
| Global alert instantly | Removes stealth; feels oppressive | Alert spreads within a radio radius, not globally |

## Unity equivalents

| Godot | Unity |
|---|---|
| `PhysicsRayQueryParameters2D` + `direct_space_state.intersect_ray` | `Physics2D.Raycast` |
| Guard state enum + `_enter_state` | Animator `StateMachineBehaviour` or custom FSM |
| `NavigationAgent2D` | `NavMeshAgent` |
| `Path2D` waypoints | `Transform[]` array of waypoint GameObjects |
| `emit_signal("guard_alerted", pos)` | `UnityEvent<Vector3>` or C# event |
