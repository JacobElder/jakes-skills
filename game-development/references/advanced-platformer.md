# Advanced Platformer Mechanics

## Wall jump and wall slide

The most common mistake: applying forces instead of setting velocity directly, or getting the horizontal direction wrong on wall jump.

```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_velocity: float = -480.0
@export var gravity_up: float = 900.0
@export var gravity_down: float = 1600.0
@export var wall_slide_gravity: float = 200.0   # much lower than falling gravity
@export var wall_jump_horizontal: float = 250.0
@export var wall_jump_vertical: float = -420.0
@export var wall_cling_time: float = 0.15       # grace window after leaving wall

var _wall_cling_timer: float = 0.0
var _wall_normal: Vector2 = Vector2.ZERO

func _physics_process(delta: float) -> void:
    var on_floor := is_on_floor()
    var on_wall  := is_on_wall_only()

    # Track wall normal for jump direction
    if on_wall:
        _wall_normal = get_wall_normal()
        _wall_cling_timer = wall_cling_time
    elif _wall_cling_timer > 0.0:
        _wall_cling_timer -= delta

    # Wall slide: reduce gravity while pressing into wall and falling
    var dir := Input.get_axis("move_left", "move_right")
    var pressing_into_wall := on_wall and (
        (dir > 0 and _wall_normal.x < 0) or
        (dir < 0 and _wall_normal.x > 0)
    )

    if pressing_into_wall and velocity.y > 0:
        velocity.y += wall_slide_gravity * delta
        velocity.y = min(velocity.y, 80.0)  # cap slide speed
    else:
        var grav := gravity_up if velocity.y < 0 else gravity_down
        velocity.y += grav * delta

    # Wall jump: available during cling window even after leaving wall
    if Input.is_action_just_pressed("jump") and _wall_cling_timer > 0.0 and not on_floor:
        # Jump AWAY from wall — direction is the stored wall normal
        velocity.x = _wall_normal.x * wall_jump_horizontal
        velocity.y = wall_jump_vertical
        _wall_cling_timer = 0.0
    elif Input.is_action_just_pressed("jump") and on_floor:
        velocity.y = jump_velocity

    # Horizontal movement (don't override wall-jump impulse immediately)
    velocity.x = move_toward(velocity.x, dir * speed, 800.0 * delta)

    move_and_slide()
```

Key details:
- `_wall_normal` must be saved while on wall — `get_wall_normal()` returns zero when not on wall.
- `is_on_wall_only()` excludes floor contact; use it to prevent wall-jump triggers when sliding against a wall on the floor.
- `wall_cling_timer` mirrors coyote time — gives a grace window after leaving the wall surface so wall jumps don't require pixel-perfect timing.
- Wall jump velocity is **set**, never added — adding to existing velocity produces unpredictable results.

## Dash

Dash mistakes: using forces (physics fights you), not locking direction, no invincibility frames.

```gdscript
@export var dash_speed: float = 600.0
@export var dash_duration: float = 0.18
@export var dash_cooldown: float = 0.6

var _dashing: bool = false
var _dash_timer: float = 0.0
var _dash_cooldown_timer: float = 0.0
var _dash_direction: Vector2 = Vector2.RIGHT

func _physics_process(delta: float) -> void:
    _dash_cooldown_timer = max(0.0, _dash_cooldown_timer - delta)

    if _dashing:
        _dash_timer -= delta
        if _dash_timer <= 0.0:
            _end_dash()
            return
        velocity = _dash_direction * dash_speed  # override all other velocity
        move_and_slide()
        return  # skip normal movement during dash

    # Normal movement...
    if Input.is_action_just_pressed("dash") and _dash_cooldown_timer <= 0.0:
        _start_dash()

func _start_dash() -> void:
    _dashing = true
    _dash_timer = dash_duration
    _dash_cooldown_timer = dash_cooldown

    # Lock direction at moment of dash press
    var dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    _dash_direction = dir.normalized() if dir.length() > 0.1 else Vector2(facing_direction, 0.0)

    # Invincibility frames: disable hitbox layer
    set_collision_layer_value(2, false)   # layer 2 = enemy damage hitbox
    # Optional: ghost trail effect
    _spawn_dash_trail()

func _end_dash() -> void:
    _dashing = false
    set_collision_layer_value(2, true)
    velocity = _dash_direction * (speed * 0.5)  # carry some momentum out of dash
```

Why `set_collision_layer_value` for i-frames: disabling the layer the enemy hitboxes test against is instantaneous and exact — no need to track whether damage was taken.

## One-way platforms (drop-through)

```gdscript
# On the platform CollisionShape2D:
# Enable "One Way Collision" in the inspector (or via script):
platform_collision.one_way_collision = true

# Player: drop through when pressing down + jump
func _physics_process(delta: float) -> void:
    if Input.is_action_just_pressed("jump") and Input.is_action_pressed("move_down"):
        # Temporarily disable one-way collision response
        set_collision_mask_value(3, false)  # layer 3 = one-way platform layer
        await get_tree().create_timer(0.2).timeout
        set_collision_mask_value(3, true)
```

Alternative using `move_and_slide` position_mode:
```gdscript
# Disable the platform collision for the player for one frame
motion_mode = CharacterBody2D.MOTION_MODE_GROUNDED
platform_floor_layers = 0  # temporarily clear; restore after 0.2s
```

## Moving platforms (velocity inheritance)

The failure mode: player snaps back or slides off platforms because platform velocity is not transferred.

```gdscript
# Godot 4 — get_platform_velocity() is built in
func _physics_process(delta: float) -> void:
    if is_on_floor():
        # Add platform velocity to player velocity this frame
        velocity += get_platform_velocity()

    # ... rest of movement
    move_and_slide()
```

For the platform itself:
```gdscript
# MovingPlatform.gd — use AnimatableBody2D (not RigidBody2D)
extends AnimatableBody2D

@export var waypoints: Array[Vector2] = []
@export var speed: float = 80.0

var _target_index: int = 0

func _physics_process(delta: float) -> void:
    if waypoints.is_empty():
        return
    var target := waypoints[_target_index]
    var dir := (target - global_position)
    if dir.length() < 2.0:
        _target_index = (_target_index + 1) % waypoints.size()
    else:
        # Use move_and_collide so the platform pushes CharacterBody2D players
        move_and_collide(dir.normalized() * speed * delta)
```

`AnimatableBody2D` (not `StaticBody2D`) with `sync_to_physics = true` is required for `get_platform_velocity()` to return a non-zero value on the player. `StaticBody2D` reports no velocity.

## Ledge grab and mantling

```gdscript
@export var ledge_grab_reach: float = 32.0
@export var ledge_climb_duration: float = 0.25

var _grabbing_ledge: bool = false
var _ledge_position: Vector2 = Vector2.ZERO

func _check_ledge() -> void:
    if velocity.y >= 0.0 or is_on_floor():
        return
    # Cast ray forward at hand height
    var hand_height := global_position + Vector2(facing_direction * 16.0, -36.0)
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(
        hand_height, hand_height + Vector2(facing_direction * ledge_grab_reach, 0.0))
    var hit := space.intersect_ray(query)
    if hit and hit.normal.y < -0.5:  # hit a top surface
        _grab_ledge(hit.position)

func _grab_ledge(pos: Vector2) -> void:
    _grabbing_ledge = true
    _ledge_position = pos
    velocity = Vector2.ZERO
    # Freeze player at ledge until input
    set_physics_process(false)
    # Animate hang
    await get_tree().process_frame  # let position settle

func _climb_ledge() -> void:
    set_physics_process(true)
    _grabbing_ledge = false
    var tween := create_tween()
    tween.tween_property(self, "global_position",
        _ledge_position + Vector2(0.0, -48.0), ledge_climb_duration
    ).set_ease(Tween.EASE_OUT)
    await tween.finished
```

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| `apply_force()` for dash | Physics fights player; dash feels sludgy | Set `velocity` directly during dash |
| Wall jump in same direction as wall | Player bounces back into wall | Use `get_wall_normal()` for horizontal push |
| No `wall_cling_timer` | Wall jump requires pixel-perfect timing | Grace window after leaving wall surface |
| `StaticBody2D` for moving platform | `get_platform_velocity()` returns zero | Use `AnimatableBody2D` |
| `collision.one_way_collision` without mask toggle | Can't drop through platforms | Clear mask temporarily on down+jump |
| No i-frames during dash | Dash has no defensive value | Disable hitbox layer with `set_collision_layer_value` |
| Locking direction after dash starts | Input direction during dash changes course | Capture and lock direction in `_start_dash` |

## Unity equivalents

| Godot | Unity |
|---|---|
| `is_on_wall_only()` + `get_wall_normal()` | `Physics2D.Raycast` sideways from character |
| `get_platform_velocity()` | Track `Rigidbody2D.velocity` of platform manually |
| `AnimatableBody2D` with `move_and_collide` | `Rigidbody2D.MovePosition` with kinematic mode |
| `set_collision_layer_value` | `Physics2D.IgnoreLayerCollision` |
| `CharacterBody2D.motion_mode` | `CharacterController` is always grounded-mode |
