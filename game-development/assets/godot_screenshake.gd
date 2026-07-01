extends Camera2D
## Trauma-based screenshake for a Godot Camera2D.
##
## Why trauma (not "shake for N seconds"): callers just ADD trauma on events
## (small hit +0.2, explosion +0.8); it decays on its own, multiple events stack,
## and offsetting by trauma SQUARED makes small shakes subtle and big ones punchy.
## Always shake the CAMERA, never world objects. Keep it short; offer a reduce
## option for motion sensitivity.
##
## Engine-agnostic algorithm (port anywhere):
##   add_trauma(amount): trauma = clamp(trauma + amount, 0, 1)
##   each frame:
##     trauma = max(trauma - decay * dt, 0)
##     shake = max_offset * (trauma * trauma)
##     camera.offset = random_in_[-1,1] * shake          # x and y
##     camera.rotation = max_angle * (trauma*trauma) * random_in_[-1,1]

@export var decay: float = 1.2          # trauma lost per second
@export var max_offset: float = 14.0    # pixels at full trauma
@export var max_roll: float = 0.06      # radians at full trauma
@export var shake_scale: float = 1.0    # accessibility: 0 disables, <1 reduces

var _trauma: float = 0.0
var _noise := FastNoiseLite.new()
var _t: float = 0.0

func _ready() -> void:
	_noise.frequency = 2.0

func add_trauma(amount: float) -> void:
	_trauma = clampf(_trauma + amount, 0.0, 1.0)

func _process(delta: float) -> void:   # cosmetic -> _process is correct here
	_t += delta
	if _trauma <= 0.0:
		offset = Vector2.ZERO
		rotation = 0.0
		return
	_trauma = maxf(_trauma - decay * delta, 0.0)
	var amount := _trauma * _trauma * shake_scale        # square = punchy
	# noise (not pure random) reads smoother than per-frame jitter
	var nx := _noise.get_noise_2d(_t * 600.0, 0.0)
	var ny := _noise.get_noise_2d(0.0, _t * 600.0)
	offset = Vector2(nx, ny) * max_offset * amount
	rotation = max_roll * amount * _noise.get_noise_2d(_t * 600.0, 100.0)
