extends CharacterBody2D
## Player platformer controller — tuned for tight, responsive feel.
## All feel constants are exported so you can tune them by playing, not editing code.

# --- Horizontal movement ---
@export var max_speed: float = 220.0
@export var accel: float = 2000.0          # how fast we reach max_speed
@export var decel: float = 2600.0          # decel is higher than accel -> crisp stops
@export var air_control: float = 0.65      # fraction of ground control while airborne

# --- Jump feel ---
@export var jump_velocity: float = 430.0
@export var rise_gravity: float = 1100.0   # gravity while moving up
@export var fall_gravity: float = 1700.0   # heavier on the way down -> snappy, not floaty
@export var max_fall_speed: float = 900.0
@export var jump_cut: float = 0.45         # release early -> keep this fraction of up-velocity

# --- Forgiveness windows (these make it feel fair, not "broken") ---
@export var coyote_time: float = 0.10      # can still jump shortly after leaving a ledge
@export var jump_buffer_time: float = 0.10 # pressing jump just before landing still works

var _coyote := 0.0
var _jump_buffer := 0.0

@onready var sprite: Node2D = $Sprite2D    # used for squash/stretch juice

func _physics_process(delta: float) -> void:
	# ---- timers (frame-independent) ----
	if is_on_floor():
		_coyote = coyote_time
	else:
		_coyote -= delta

	if Input.is_action_just_pressed("jump"):
		_jump_buffer = jump_buffer_time
	else:
		_jump_buffer -= delta

	# ---- gravity (asymmetric) ----
	var g := rise_gravity if velocity.y < 0.0 else fall_gravity
	velocity.y = min(velocity.y + g * delta, max_fall_speed)

	# ---- jump (buffer + coyote) ----
	if _jump_buffer > 0.0 and _coyote > 0.0:
		velocity.y = -jump_velocity
		_jump_buffer = 0.0
		_coyote = 0.0
		_on_jump()

	# ---- variable jump height ----
	if Input.is_action_just_released("jump") and velocity.y < 0.0:
		velocity.y *= jump_cut

	# ---- horizontal accel/decel ----
	var dir := Input.get_axis("move_left", "move_right")
	var control := 1.0 if is_on_floor() else air_control
	var rate := (accel if dir != 0.0 else decel) * control
	velocity.x = move_toward(velocity.x, dir * max_speed, rate * delta)

	var was_on_floor := is_on_floor()
	move_and_slide()

	# landing detection -> squash + (hook your dust particle / land sound here)
	if is_on_floor() and not was_on_floor:
		_on_land()

# --- Juice hooks (cheap, high impact) ---
func _on_jump() -> void:
	# stretch vertically on launch
	var t := create_tween()
	t.tween_property(sprite, "scale", Vector2(0.8, 1.2), 0.06)
	t.tween_property(sprite, "scale", Vector2.ONE, 0.10).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	# AudioManager.play("jump")   # pitch-randomize at the source
	# spawn_dust(global_position)

func _on_land() -> void:
	# squash on landing, then spring back
	var t := create_tween()
	t.tween_property(sprite, "scale", Vector2(1.25, 0.75), 0.05)
	t.tween_property(sprite, "scale", Vector2.ONE, 0.12).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	# AudioManager.play("land")
	# spawn_dust(global_position)
	# small screenshake on hard landings: Camera.add_trauma(0.2)
