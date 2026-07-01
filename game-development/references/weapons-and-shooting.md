# Weapons and Shooting Systems

## Hitscan vs. projectile — use the right tool

| | Hitscan | Projectile |
|---|---|---|
| **How** | Raycast → instant result | Spawn a moving node |
| **Best for** | Rifles, lasers, shotguns, sniper, machine gun | Rockets, grenades, arrows, slow bullets |
| **Latency** | Zero (fires same frame) | Flies over time (can be dodged) |
| **Performance** | One raycast | One node per bullet (pool these) |
| **Wrong use** | Pistol that should feel tactile but needs no dodge window | Machine gun (spawning 30 nodes/sec) |

**The expensive mistake:** using a spawned bullet scene for a high-RPS automatic weapon. At 15 rounds/sec × 60 fps, that's 900 bullets alive at once. Use hitscan or a GPU-particle approximation for anything above ~6 rounds/sec.

### Hitscan (Godot 2D)

```gdscript
func fire_hitscan() -> void:
    var space := get_world_2d().direct_space_state
    var muzzle := $MuzzlePoint.global_position
    var aim_dir := _get_aim_direction()
    var query := PhysicsRayQueryParameters2D.create(
        muzzle,
        muzzle + aim_dir * weapon_data.range,
        0b0010   # mask: only layer 2 (enemies)
    )
    var hit := space.intersect_ray(query)
    if hit:
        _apply_hit(hit.collider, hit.position, hit.normal)
    _spawn_tracer(muzzle, hit.get("position", muzzle + aim_dir * weapon_data.range))

func _apply_hit(target: Node, pos: Vector2, normal: Vector2) -> void:
    if target.has_method("take_damage"):
        target.take_damage(weapon_data.damage)
    # Spawn impact VFX at pos
    ImpactPool.spawn(pos, normal)
```

### Projectile (Godot 2D — pooled)

```gdscript
# BulletPool.gd — autoload
var _pool: Array[Bullet] = []

func spawn(pos: Vector2, direction: Vector2, data: WeaponData) -> void:
    var bullet := _get_or_create()
    bullet.init(pos, direction, data)
    bullet.show()

func return_bullet(bullet: Bullet) -> void:
    bullet.hide()
    bullet.set_physics_process(false)
    _pool.append(bullet)

func _get_or_create() -> Bullet:
    if _pool.is_empty():
        var b := preload("res://scenes/bullet.tscn").instantiate()
        add_child(b)
        return b
    return _pool.pop_back()
```

```gdscript
# Bullet.gd
func init(pos: Vector2, dir: Vector2, data: WeaponData) -> void:
    global_position = pos
    _velocity = dir.normalized() * data.bullet_speed
    _damage = data.damage
    _lifetime = data.bullet_lifetime
    set_physics_process(true)

func _physics_process(delta: float) -> void:
    _lifetime -= delta
    if _lifetime <= 0.0:
        BulletPool.return_bullet(self)
        return
    var collision := move_and_collide(_velocity * delta)
    if collision:
        collision.get_collider().take_damage(_damage)
        BulletPool.return_bullet(self)
```

## Weapon state machine

Never nest firing logic in `if is_firing: if ammo > 0: if not reloading:`. Each state owns its own input handling.

```gdscript
# WeaponController.gd
enum State { IDLE, FIRING, RELOADING, EMPTY }

var _state: State = State.IDLE
var _fire_timer: float = 0.0
var _reload_timer: float = 0.0
var _burst_count: int = 0
var _current_ammo: int
var _reserve_ammo: int

func _ready() -> void:
    _current_ammo = weapon_data.magazine_size
    _reserve_ammo = weapon_data.max_reserve

func _physics_process(delta: float) -> void:
    match _state:
        State.IDLE:    _tick_idle(delta)
        State.FIRING:  _tick_firing(delta)
        State.RELOADING: _tick_reloading(delta)
        State.EMPTY:   _tick_empty()

func _tick_idle(delta: float) -> void:
    _fire_timer = max(0.0, _fire_timer - delta)
    var wants_fire := _get_fire_input()
    if wants_fire and _fire_timer <= 0.0:
        if _current_ammo > 0:
            _transition(State.FIRING)
        else:
            _transition(State.EMPTY)
    if Input.is_action_just_pressed("reload") and _current_ammo < weapon_data.magazine_size:
        _transition(State.RELOADING)

func _tick_firing(delta: float) -> void:
    _shoot()
    _current_ammo -= 1
    ammo_changed.emit(_current_ammo, weapon_data.magazine_size)
    _fire_timer = 1.0 / weapon_data.fire_rate

    match weapon_data.fire_mode:
        WeaponData.FireMode.SINGLE:
            _transition(State.IDLE)
        WeaponData.FireMode.BURST:
            _burst_count += 1
            if _burst_count >= weapon_data.burst_count or _current_ammo <= 0:
                _burst_count = 0
                _transition(State.IDLE)
            # else stay in FIRING; next tick shoots next burst round
        WeaponData.FireMode.AUTO:
            if _current_ammo <= 0:
                _transition(State.RELOADING if _reserve_ammo > 0 else State.EMPTY)
            elif not Input.is_action_pressed("fire"):
                _transition(State.IDLE)

func _tick_reloading(delta: float) -> void:
    _reload_timer -= delta
    if _reload_timer <= 0.0:
        var needed := weapon_data.magazine_size - _current_ammo
        var taken := min(needed, _reserve_ammo)
        _current_ammo += taken
        _reserve_ammo -= taken
        ammo_changed.emit(_current_ammo, weapon_data.magazine_size)
        _transition(State.IDLE)

func _transition(new_state: State) -> void:
    _state = new_state
    if new_state == State.RELOADING:
        _reload_timer = weapon_data.reload_time
        reload_started.emit()

func _get_fire_input() -> bool:
    match weapon_data.fire_mode:
        WeaponData.FireMode.SINGLE, WeaponData.FireMode.BURST:
            return Input.is_action_just_pressed("fire")
        WeaponData.FireMode.AUTO:
            return Input.is_action_pressed("fire")
    return false
```

## WeaponData resource

```gdscript
class_name WeaponData
extends Resource

enum FireMode { SINGLE, BURST, AUTO }

@export var name: String = "Pistol"
@export var fire_mode: FireMode = FireMode.SINGLE
@export var fire_rate: float = 4.0          # rounds per second
@export var burst_count: int = 3
@export var magazine_size: int = 10
@export var max_reserve: int = 60
@export var reload_time: float = 1.8
@export var damage: float = 25.0
@export var range: float = 800.0
@export var bullet_speed: float = 600.0
@export var bullet_lifetime: float = 2.0
@export var spread_angle: float = 3.0       # degrees, max angular deviation
@export var use_hitscan: bool = false
```

## Spread / accuracy

```gdscript
func _get_fire_direction() -> Vector2:
    var base_dir := _get_aim_direction()
    if weapon_data.spread_angle <= 0.0:
        return base_dir
    var spread := deg_to_rad(weapon_data.spread_angle)
    # Increase spread while moving, decrease while crouching/aiming
    var spread_mult := 2.0 if player.is_moving else 1.0
    spread_mult *= 0.4 if player.is_aiming else 1.0
    var angle := randf_range(-spread * spread_mult, spread * spread_mult)
    return base_dir.rotated(angle)
```

## Aiming direction

```gdscript
# Top-down mouse aim
func _get_aim_direction() -> Vector2:
    return (get_global_mouse_position() - global_position).normalized()

# Twin-stick controller
func _get_aim_direction() -> Vector2:
    var right_stick := Input.get_vector("aim_left", "aim_right", "aim_up", "aim_down")
    if right_stick.length() > 0.2:   # deadzone
        return right_stick.normalized()
    # Fallback to movement direction
    var move := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    return move.normalized() if move.length() > 0.1 else Vector2(facing_dir, 0.0)

# FPS mouse look (3D)
func _get_aim_direction() -> Vector3:
    return -camera.global_transform.basis.z   # camera forward
```

## Shotgun / multi-pellet

```gdscript
func fire_shotgun() -> void:
    for i in weapon_data.pellet_count:
        var dir := _get_fire_direction()  # each pellet gets its own spread roll
        if weapon_data.use_hitscan:
            fire_hitscan_ray(dir)
        else:
            BulletPool.spawn(muzzle_pos, dir, weapon_data)
```

## Recoil

Visual recoil (weapon sprite) + camera trauma:

```gdscript
func _apply_recoil() -> void:
    # Camera trauma
    Camera.add_trauma(weapon_data.recoil_trauma)
    # Weapon sprite recoil
    var tween := weapon_sprite.create_tween()
    tween.tween_property(weapon_sprite, "position", Vector2(0, 8), 0.04)
    tween.tween_property(weapon_sprite, "position", Vector2.ZERO, 0.12).set_ease(Tween.EASE_OUT)
```

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| Projectile node for machine gun | 900 nodes/sec → frame spikes | Hitscan for high-RPS weapons |
| No bullet pool | GC hitches every time a bullet expires | Pool: init 200 bullets at start |
| Nested `if is_firing and not reloading and ammo > 0` | Spaghetti; can't add states | Enum state machine |
| Single `fire()` function handling all modes | Mode-specific logic bleeds together | `FireMode` enum + per-mode tick |
| Right stick aim without deadzone | Tiny stick drift causes constant rotation | Deadzone threshold (0.15–0.2) |
| Recalculating aim on every bullet in a shotgun | Same base direction, different spread per pellet | Call `_get_aim_direction()` once per pellet |

## Unity equivalents

| Godot | Unity |
|---|---|
| `PhysicsRayQueryParameters2D.create` | `Physics2D.Raycast` |
| Bullet pool via autoload | `ObjectPool<T>` (Unity 2021+) |
| `WeaponData extends Resource` | `WeaponData : ScriptableObject` |
| `Input.is_action_pressed("fire")` | `Input.GetButton("Fire1")` |
| `get_global_mouse_position()` | `Camera.ScreenToWorldPoint(Input.mousePosition)` |
