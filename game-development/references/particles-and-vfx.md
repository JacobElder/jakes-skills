# Particles and VFX

## GPUParticles2D vs CPUParticles2D

| | GPUParticles2D / GPUParticles3D | CPUParticles2D / CPUParticles3D |
|---|---|---|
| Processing | GPU compute shader | CPU, GDScript-accessible |
| Count | Hundreds to thousands efficiently | Best under ~50 |
| Mobile | Needs Vulkan/GLES3 | Works everywhere |
| Server/headless | Won't run | Works |
| Sub-emitters | Yes | No |
| Readable from code | No per-particle access | Full per-particle access |

**Default**: use `GPUParticles2D`. Switch to `CPUParticles2D` only for low-end mobile targets or when you need per-particle scripted logic.

## ParticleProcessMaterial key properties

```gdscript
var mat := ParticleProcessMaterial.new()
mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
mat.emission_sphere_radius = 4.0
mat.direction = Vector3(0, -1, 0)   # gravity-like downward
mat.spread = 45.0                   # cone spread in degrees
mat.gravity = Vector3(0, 9.8, 0)    # actual gravity pull
mat.initial_velocity_min = 60.0
mat.initial_velocity_max = 120.0
mat.scale_min = 0.5
mat.scale_max = 1.5
mat.color = Color.WHITE

# Fade out over lifetime
var grad := Gradient.new()
grad.set_color(0, Color(1, 0.6, 0.2, 1.0))
grad.set_color(1, Color(1, 0.6, 0.2, 0.0))
mat.color_ramp = GradientTexture1D.new()
mat.color_ramp.gradient = grad

$GPUParticles2D.process_material = mat
```

## One-shot impact effects

Set `one_shot = true` and `lifetime` to the effect duration. Trigger by setting `emitting = true`.

```gdscript
# Burst effect node
@export var amount := 16

func _ready() -> void:
    $Particles.one_shot = true
    $Particles.amount = amount
    $Particles.emitting = false
    $Particles.finished.connect(queue_free)  # self-cleanup

func play() -> void:
    $Particles.restart()   # resets timer and re-emits
    $Particles.emitting = true
```

**`restart()`** is required before re-triggering a one-shot — `emitting = true` alone won't re-fire if it already ran.

## Sub-emitters

Sub-emitters fire a secondary particle system when a parent particle collides or ends its lifetime.

```gdscript
# On the parent GPUParticles2D's ParticleProcessMaterial:
mat.sub_emitter = preload("res://effects/spark_sub.tres")
mat.sub_emitter_mode = ParticleProcessMaterial.SUB_EMITTER_END_OF_LIFE
mat.sub_emitter_amount_at_end = 4
```

The sub-emitter `.tres` is another `ParticleProcessMaterial`. The child particles inherit the parent particle's position and velocity at the moment they spawn. Use `SUB_EMITTER_COLLISION` for bounce sparks, `SUB_EMITTER_END_OF_LIFE` for dissolve or debris effects.

## Particle pool for hit VFX

Allocating a new `GPUParticles2D` per hit causes GC spikes. Pre-allocate a fixed pool and recycle by connecting `finished`:

```gdscript
# ParticlePool autoload
const POOL_SIZE := 16
const EffectScene := preload("res://effects/hit_burst.tscn")

var _pool: Array[GPUParticles2D] = []

func _ready() -> void:
    for i in POOL_SIZE:
        var fx: GPUParticles2D = EffectScene.instantiate()
        add_child(fx)
        fx.emitting = false
        fx.finished.connect(_return_to_pool.bind(fx))
        _pool.append(fx)

func play_at(pos: Vector2) -> void:
    if _pool.is_empty():
        return          # drop the effect rather than spike
    var fx := _pool.pop_back()
    fx.global_position = pos
    fx.restart()
    fx.emitting = true

func _return_to_pool(fx: GPUParticles2D) -> void:
    fx.emitting = false
    _pool.append(fx)
```

## Hit VFX composition

A convincing hit effect layers several systems simultaneously. Never rely on particles alone:

```gdscript
func play_hit_vfx(pos: Vector2) -> void:
    # 1. Particle burst (GPUParticles2D pool)
    ParticlePool.play_at(pos)
    # 2. Sprite flash on the target
    target.modulate = Color.WHITE
    var tw := create_tween()
    tw.tween_property(target, "modulate", Color.WHITE, 0.0)
    tw.tween_property(target, "modulate", Color(1,1,1,1), 0.08)
    # 3. Sound (pooled AudioStreamPlayer)
    AudioManager.play_sfx("hit", pos)
    # 4. Hitstop (optional, see game-feel.md)
    Engine.time_scale = 0.05
    await get_tree().create_timer(0.04, true, false, true).timeout
    Engine.time_scale = 1.0
```

## amount_ratio for runtime density scaling

`amount` is the fixed particle count for the process material. `amount_ratio` (0.0–1.0) scales active particles at runtime without changing timing:

```gdscript
# Scale particle density by game quality setting
$Particles.amount_ratio = GameSettings.particle_quality  # 0.25 / 0.5 / 1.0
```

Use `amount_ratio` instead of changing `amount` at runtime — changing `amount` restarts the particle system.

## Trail particles

```gdscript
$Particles.trail_enabled = true
$Particles.trail_lifetime = 0.3
```

For projectile trails, parent the GPUParticles2D to the projectile and enable trail mode. Disable `local_coords` so the trail remains in world space when the particle moves.

## Visibility culling

Set `visibility_aabb` on GPUParticles3D to a tight bounding box so the GPU skips off-screen particle systems. In 2D, `GPUParticles2D` uses the standard `CanvasItem` visibility rect — ensure the node's bounding rect covers the full effect area or particles will pop out at screen edges.

## Common mistakes

- Forgetting `restart()` before re-triggering one-shot effects
- Using `CPUParticles2D` for large counts (> 100) on mobile
- Not pooling VFX nodes — new instance per hit creates GC pressure
- `local_coords = true` on projectile trails — trail bends with parent rotation instead of staying in world space
- Sub-emitter `.tres` using the wrong `sub_emitter_mode` (END_OF_LIFE vs COLLISION)
