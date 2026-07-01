# Camera Systems

## Camera2D follow modes

Godot's Camera2D covers basic following. The pitfalls are in *when* to update and *what* the target is.

```gdscript
# PlayerCamera.gd — attached to Camera2D
extends Camera2D

@export var look_ahead_distance: float = 80.0   # offset in movement direction
@export var look_ahead_speed: float = 4.0
@export var vertical_deadzone: float = 40.0     # don't follow small vertical movement

var _look_ahead: Vector2 = Vector2.ZERO

func _physics_process(delta: float) -> void:
    # Look-ahead: offset camera in the direction the player is moving
    var move_dir := player.velocity.normalized()
    _look_ahead = _look_ahead.lerp(move_dir * look_ahead_distance, look_ahead_speed * delta)
    offset = _look_ahead
    # Vertical deadzone: only follow if player leaves a vertical band
    var dy := player.global_position.y - global_position.y
    if abs(dy) < vertical_deadzone:
        global_position.x = player.global_position.x
    else:
        global_position = global_position.lerp(player.global_position, 6.0 * delta)
```

Use `position_smoothing_enabled = true` in the Camera2D inspector for basic lag, but for precise feel (look-ahead, deadzones, room transitions) control `global_position` directly in `_physics_process`.

## Room-based camera zones (Metroid-style)

Each room defines camera bounds. When the player enters a new room, the camera smoothly locks to the new bounds.

```gdscript
# CameraZone.gd — Area2D, one per room
extends Area2D

@export var zoom_level: Vector2 = Vector2.ONE

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("player"):
        CameraController.transition_to_zone(self)
```

```gdscript
# CameraController.gd — autoload
extends Node

var camera: Camera2D

func transition_to_zone(zone: Area2D) -> void:
    var rect: Rect2 = _get_zone_rect(zone)
    # Clamp camera limits to room bounds
    var tween := camera.create_tween()
    tween.set_parallel(true)
    tween.tween_property(camera, "limit_left",   int(rect.position.x),   0.3)
    tween.tween_property(camera, "limit_top",    int(rect.position.y),   0.3)
    tween.tween_property(camera, "limit_right",  int(rect.end.x),        0.3)
    tween.tween_property(camera, "limit_bottom", int(rect.end.y),        0.3)
    if zone.zoom_level != camera.zoom:
        tween.tween_property(camera, "zoom", zone.zoom_level, 0.4)

func _get_zone_rect(zone: Area2D) -> Rect2:
    var shape := zone.get_node("CollisionShape2D").shape as RectangleShape2D
    var half := shape.size / 2.0
    return Rect2(zone.global_position - half, shape.size)
```

The `limit_*` properties on Camera2D already clamp the camera so it doesn't show outside the room — no extra logic needed. Tweak the limits smoothly rather than hard-cutting.

## Cinematic / cutscene cameras

```gdscript
# CinematicCamera.gd
extends Camera2D

signal cutscene_finished

func play_sequence(keyframes: Array[Dictionary]) -> void:
    # keyframes: [{position, zoom, duration, easing}, ...]
    make_current()   # take control from player camera
    for kf in keyframes:
        var tween := create_tween().set_parallel(true)
        tween.tween_property(self, "global_position", kf["position"], kf["duration"]) \
             .set_ease(kf.get("easing", Tween.EASE_IN_OUT))
        if kf.has("zoom"):
            tween.tween_property(self, "zoom", kf["zoom"], kf["duration"])
        await tween.finished
    # Return control to player camera
    player_camera.make_current()
    cutscene_finished.emit()
```

```gdscript
# Usage
await CinematicCamera.play_sequence([
    {"position": Vector2(800, 400), "zoom": Vector2(1.5, 1.5), "duration": 1.0},
    {"position": Vector2(1200, 400), "duration": 0.8},
    {"position": player.global_position, "zoom": Vector2.ONE, "duration": 0.6},
])
```

## Lock-on targeting (3D action games)

```gdscript
# LockOnSystem.gd
extends Node3D

@export var lock_on_range: float = 15.0
@export var lock_on_fov: float = 60.0         # degrees of camera forward cone
@export var cycle_input: StringName = "lock_on_next"

var target: Node3D = null
var _candidates: Array[Node3D] = []

func toggle_lock_on() -> void:
    if target:
        _release()
    else:
        _acquire_nearest()

func _acquire_nearest() -> void:
    _candidates = _get_candidates()
    if _candidates.is_empty():
        return
    target = _candidates[0]
    _lock_on_marker.show()
    _lock_on_marker.global_position = target.global_position + Vector3.UP * 1.5

func _get_candidates() -> Array[Node3D]:
    var cam_forward := -camera.global_transform.basis.z
    var enemies := get_tree().get_nodes_in_group("enemies")
    var in_range := enemies.filter(func(e):
        var to_e := (e.global_position - camera.global_position)
        var dist := to_e.length()
        if dist > lock_on_range:
            return false
        var angle := rad_to_deg(cam_forward.angle_to(to_e.normalized()))
        return angle <= lock_on_fov / 2.0
    )
    in_range.sort_custom(func(a, b):
        return a.global_position.distance_to(player.global_position) < \
               b.global_position.distance_to(player.global_position)
    )
    return in_range

func cycle_target() -> void:
    if _candidates.is_empty():
        return
    var idx := (_candidates.find(target) + 1) % _candidates.size()
    target = _candidates[idx]

func _physics_process(delta: float) -> void:
    if not target:
        return
    if not is_instance_valid(target) or target.is_queued_for_deletion():
        _release()
        return
    # Camera looks between player and target
    var midpoint := (player.global_position + target.global_position) / 2.0
    var desired_pos := midpoint + Vector3(0, 3, 6)   # adjust per game
    camera.global_position = camera.global_position.lerp(desired_pos, 6.0 * delta)
    camera.look_at(midpoint, Vector3.UP)
    # Update UI marker
    _lock_on_marker.global_position = target.global_position + Vector3.UP * 1.5

func _release() -> void:
    target = null
    _lock_on_marker.hide()
    # Return camera control to normal follow
```

## Split-screen (local co-op)

```gdscript
# Two SubViewports side by side, each with own Camera2D
# SceneTree: HBoxContainer → [SubViewportContainer → SubViewport → (world + Camera2D p1)]
#                          → [SubViewportContainer → SubViewport → (world + Camera2D p2)]
# Both SubViewports share the same World2D resource so they see the same objects.

func _ready() -> void:
    var world := World2D.new()
    viewport1.world_2d = world
    viewport2.world_2d = world
    camera1.remote_path = player1.get_path()
    camera2.remote_path = player2.get_path()
```

For performance: reduce SubViewport resolution to 50–75% of screen, scale up with `SubViewportContainer`. The render cost doubles but shared World2D means physics and AI run once.

## Screenshake (camera-safe)

```gdscript
# TraumaCamera.gd — Camera2D
var trauma: float = 0.0
var _rng := RandomNumberGenerator.new()

func add_trauma(amount: float) -> void:
    trauma = min(trauma + amount, 1.0)

func _process(delta: float) -> void:
    trauma = max(0.0, trauma - delta * 1.5)
    var shake := trauma * trauma   # square for more natural feel
    offset = Vector2(
        _rng.randf_range(-1.0, 1.0) * shake * 24.0,
        _rng.randf_range(-1.0, 1.0) * shake * 16.0
    )
    rotation = _rng.randf_range(-1.0, 1.0) * shake * 0.05
```

Shake `offset` and `rotation` on the Camera2D — not `position`, not the CanvasLayer, not the viewport. The HUD stays fixed because it's on a CanvasLayer above the camera.

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| Camera2D parented directly to player | No smoothing; jittery on fast movement | Camera follows player via `remote_path` or manual lerp |
| Hard-cutting between camera zones | Jarring, feels like a glitch | Tween `limit_*` properties over 0.3–0.5s |
| Shaking viewport or CanvasLayer | HUD shakes with world | Shake Camera2D `offset`, not position |
| `camera.global_position = player.global_position` in `_process` | No lag, no look-ahead | Lerp in `_physics_process` |
| Separate Camera2D per player without shared World2D | Objects appear in wrong viewport | Assign same `World2D` to both SubViewports |
| Lock-on without range/FOV check | Locks onto enemies behind walls or out of view | Distance + angle check + optional raycast |

## Unity equivalents

| Godot | Unity |
|---|---|
| Camera2D `limit_*` | `CinemachineConfiner2D` bounds |
| Camera2D `position_smoothing` | Cinemachine Virtual Camera damping |
| `make_current()` | `CinemachineBrain` priority / blending |
| `SubViewport` with shared `World2D` | `Camera.targetTexture` on `RenderTexture` |
| TraumaCamera `offset` shake | `CinemachineImpulseSource` |
