# Bullet Hell and Danmaku Patterns

## The one rule: pool everything

A bullet hell game can spawn thousands of bullets. Never use `instantiate()` in the firing loop — it allocates, which causes GC pauses at exactly the wrong moment.

```gdscript
# BulletPool.gd — autoload, pre-allocate on _ready
extends Node

const POOL_SIZE := 800

var _pool: Array[Bullet] = []
var _active: Array[Bullet] = []

func _ready() -> void:
    for i in POOL_SIZE:
        var b: Bullet = preload("res://scenes/Bullet.tscn").instantiate()
        add_child(b)
        b.hide()
        _pool.append(b)

func spawn(pos: Vector2, direction: Vector2, data: BulletData) -> Bullet:
    var b: Bullet
    if _pool.is_empty():
        # Grow pool only when exhausted — never in hot path normally
        b = preload("res://scenes/Bullet.tscn").instantiate()
        add_child(b)
    else:
        b = _pool.pop_back()
    b.init(pos, direction, data)
    b.show()
    _active.append(b)
    return b

func return_bullet(b: Bullet) -> void:
    _active.erase(b)
    b.hide()
    b.set_physics_process(false)
    _pool.append(b)
```

```gdscript
# Bullet.gd
class_name Bullet
extends Area2D

var _velocity: Vector2
var _data: BulletData
var _lifetime: float

func init(pos: Vector2, dir: Vector2, data: BulletData) -> void:
    global_position = pos
    _velocity = dir.normalized() * data.speed
    _data = data
    _lifetime = data.lifetime
    set_physics_process(true)
    $Sprite2D.texture = data.sprite

func _physics_process(delta: float) -> void:
    _lifetime -= delta
    if _lifetime <= 0.0:
        BulletPool.return_bullet(self)
        return
    # Acceleration (homing, spiral, etc. applied here)
    if _data.angular_velocity != 0.0:
        _velocity = _velocity.rotated(_data.angular_velocity * delta)
    if _data.acceleration != 0.0:
        _velocity = _velocity.normalized() * (_velocity.length() + _data.acceleration * delta)
    global_position += _velocity * delta

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("player"):
        body.take_damage(_data.damage)
    BulletPool.return_bullet(self)
```

## BulletData resource

```gdscript
class_name BulletData
extends Resource

@export var speed: float = 200.0
@export var damage: float = 10.0
@export var lifetime: float = 5.0
@export var angular_velocity: float = 0.0    # rad/sec; positive = clockwise curve
@export var acceleration: float = 0.0        # speed change per second
@export var sprite: Texture2D
@export var hitbox_radius: float = 6.0
@export var is_homing: bool = false          # if true, apply homing logic
@export var homing_strength: float = 1.5    # rad/sec turn speed toward player
```

## Pattern system: polar coordinates

Always use **polar coordinates** (angle + distance) for pattern math — never hardcode offsets.

```gdscript
# PatternEmitter.gd
class_name PatternEmitter
extends Node2D

@export var data: BulletPatternData

var _time: float = 0.0

func _physics_process(delta: float) -> void:
    if not data.active:
        return
    _time += delta
    if _time >= 1.0 / data.fire_rate:
        _time = 0.0
        _fire()

func _fire() -> void:
    match data.pattern_type:
        BulletPatternData.PatternType.CIRCLE:
            _fire_circle()
        BulletPatternData.PatternType.SPIRAL:
            _fire_spiral()
        BulletPatternData.PatternType.AIMED:
            _fire_aimed()
        BulletPatternData.PatternType.RANDOM:
            _fire_random()

func _fire_circle() -> void:
    var step := TAU / data.bullet_count
    for i in data.bullet_count:
        var angle := step * i + deg_to_rad(data.rotation_offset)
        var dir := Vector2.from_angle(angle)
        BulletPool.spawn(global_position, dir, data.bullet_data)

func _fire_spiral() -> void:
    # One bullet per tick, angle advances over time
    var angle := _spiral_angle + deg_to_rad(data.rotation_offset)
    _spiral_angle += deg_to_rad(data.spiral_step_degrees)
    BulletPool.spawn(global_position, Vector2.from_angle(angle), data.bullet_data)

var _spiral_angle: float = 0.0

func _fire_aimed() -> void:
    # All bullets aimed at player, spread within arc
    var to_player := (player.global_position - global_position).normalized()
    var base_angle := to_player.angle()
    var step := deg_to_rad(data.spread_angle) / max(1, data.bullet_count - 1)
    var start_angle := base_angle - deg_to_rad(data.spread_angle) / 2.0
    for i in data.bullet_count:
        var dir := Vector2.from_angle(start_angle + step * i)
        BulletPool.spawn(global_position, dir, data.bullet_data)

func _fire_random() -> void:
    for i in data.bullet_count:
        var angle := randf() * TAU
        BulletPool.spawn(global_position, Vector2.from_angle(angle), data.bullet_data)
```

```gdscript
class_name BulletPatternData
extends Resource

enum PatternType { CIRCLE, SPIRAL, AIMED, RANDOM, ARC }

@export var pattern_type: PatternType = PatternType.CIRCLE
@export var bullet_count: int = 8
@export var fire_rate: float = 1.0               # salvos per second
@export var spread_angle: float = 360.0          # for AIMED/ARC patterns
@export var spiral_step_degrees: float = 15.0    # angular step per salvo (SPIRAL)
@export var rotation_offset: float = 0.0         # global rotation of entire pattern
@export var active: bool = true
@export var bullet_data: BulletData
```

## Boss attack composition

A boss phase has multiple emitters firing simultaneously. Each emitter is an independent `PatternEmitter` node — compose them as children of the boss.

```gdscript
# BossPhaseController.gd
@export var emitters_phase_1: Array[PatternEmitter] = []
@export var emitters_phase_2: Array[PatternEmitter] = []

func enter_phase(phase_index: int) -> void:
    var all := emitters_phase_1 + emitters_phase_2
    for e in all:
        e.data.active = false
    var active_set := emitters_phase_1 if phase_index == 0 else emitters_phase_2
    for e in active_set:
        e.data.active = true
        e._spiral_angle = 0.0   # reset angle on phase start
```

For complex timed sequences, drive the emitters from an AnimationPlayer — key `active` on/off and `rotation_offset` to create choreographed patterns.

## Homing bullets

```gdscript
# In Bullet._physics_process, when _data.is_homing:
func _apply_homing(delta: float) -> void:
    if not is_instance_valid(player):
        return
    var to_player := (player.global_position - global_position).normalized()
    var current_dir := _velocity.normalized()
    # Rotate current direction toward target by homing_strength rad/sec
    var angle := current_dir.angle_to(to_player)
    var max_turn := _data.homing_strength * delta
    angle = clamp(angle, -max_turn, max_turn)
    _velocity = _velocity.rotated(angle)
```

## Warning indicators

Show the player where a pattern will spawn before it fires.

```gdscript
# Before firing a large wave, flash spawn markers
func _show_warning(duration: float) -> void:
    var step := TAU / data.bullet_count
    for i in data.bullet_count:
        var angle := step * i + deg_to_rad(data.rotation_offset)
        var spawn_pos := global_position + Vector2.from_angle(angle) * 20.0
        var marker := warning_marker_scene.instantiate()
        add_child(marker)
        marker.global_position = spawn_pos
        marker.start(duration)   # plays blink animation, then queue_free
    await get_tree().create_timer(duration).timeout
    _fire()
```

## Grazing mechanic

Classic bullet hell: reward near-misses with a graze bonus (score, meter fill).

```gdscript
# GrazeDetector.gd — larger Area2D around player, inside hitbox
func _on_area_entered(bullet_area: Area2D) -> void:
    if bullet_area.is_in_group("bullets"):
        GrazeManager.register_graze()

# GrazeManager.gd
var graze_meter: float = 0.0
func register_graze() -> void:
    graze_meter = min(graze_meter + 0.05, 1.0)
    graze_sound.play()
    graze_particles.restart()
    score += 10
```

## Performance notes

- **600 active bullets at 60 fps**: `_physics_process` per bullet × 600 = 36,000 calls/frame. Each must be cheap — no allocation, no dictionary lookups.
- Use `PackedVector2Array` or `PackedFloat32Array` for batch-processing bullet positions if you exceed ~1000 bullets. Consider moving to a GPU compute approach.
- Physics layers: put bullets on layer 4, player hitbox on layer 4. Keep the player's graze detector on layer 5. This avoids bullet-vs-bullet collision checks entirely.
- `Area2D` signals (`body_entered`) fire from the physics server; they're already off the hot render path. Prefer them over manual distance checks.

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| `instantiate()` in the fire loop | GC pause every salvo | Pool: pre-allocate 800+ bullets at start |
| Hardcoded offsets like `Vector2(10, 0), Vector2(-10, 0)` | Pattern breaks on rotation; unmaintainable | Polar: `Vector2.from_angle(angle)` |
| Storing all bullets in an `Array` and iterating for collision | O(n) search per frame per bullet | Area2D signals on each bullet |
| One PatternEmitter per pattern hard-coded in boss script | Can't reuse; impossible to compose | `BulletPatternData` Resources; compose with multiple emitters |
| Homing bullets that always catch the player | Not fun; just a delayed death | Cap homing angle (max_turn per frame) so player can outrun them |
| No warning before dense waves | Unfair deaths from off-screen spawns | Flash warning markers at spawn points before firing |

## Unity equivalents

| Godot | Unity |
|---|---|
| `BulletPool` autoload with `Array[Bullet]` | `ObjectPool<Bullet>` (Unity 2021+) |
| `Area2D` + `body_entered` | `Collider2D` + `OnTriggerEnter2D` |
| `BulletPatternData extends Resource` | `BulletPatternData : ScriptableObject` |
| `Vector2.from_angle(angle)` | `new Vector2(Mathf.Cos(angle), Mathf.Sin(angle))` |
| `PatternEmitter` Node2D children of boss | `Transform` children of Boss GameObject |
