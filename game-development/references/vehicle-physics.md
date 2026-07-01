# Vehicle Physics

Vehicle physics in Godot 4 are built on `VehicleBody3D`, which extends `RigidBody3D`. This is not a kinematic approximation — the vehicle has real mass, real suspension springs, and real lateral grip. That means the physics engine does the heavy lifting for weight transfer, body roll, and wheel slip, but it also means the tuning parameters are physical quantities (spring stiffness, damping ratios) rather than arbitrary game feel knobs. This file covers correct setup, tuning, surface detection, drift, and the most common failure modes.

## Contents
- Node structure and VehicleWheel3D configuration
- Center of mass
- Engine torque curve
- Steering and speed-dependent angle limiting
- Handbrake and drift
- Surface detection and per-surface friction
- Skidmarks
- Anti-roll bar
- Drift tuning
- Unity equivalent (WheelCollider)
- Common mistakes

## Node structure and VehicleWheel3D configuration

The hierarchy for a complete vehicle:

```
VehicleBody3D          ← the car; has mass, physics material
  MeshInstance3D       ← car body visual
  CollisionShape3D     ← approximate convex hull of the chassis
  VehicleWheel3D (FL)  ← front-left
    MeshInstance3D     ← wheel mesh (visual only)
  VehicleWheel3D (FR)  ← front-right
    MeshInstance3D
  VehicleWheel3D (RL)  ← rear-left
    MeshInstance3D
  VehicleWheel3D (RR)  ← rear-right
    MeshInstance3D
```

Each `VehicleWheel3D` is positioned at the wheel contact point. The node's local Y axis is up; the suspension travels downward in local space. Properties to set:

```gdscript
# Front wheels (steering only)
wheel_FL.use_as_steering = true
wheel_FL.use_as_traction = false

# Rear wheels (drive only — rear-wheel drive)
wheel_RL.use_as_traction = true
wheel_RL.use_as_steering = false

# All four wheels
for wheel in [wheel_FL, wheel_FR, wheel_RL, wheel_RR]:
    wheel.wheel_radius          = 0.35    # meters; match your mesh
    wheel.suspension_travel     = 0.15    # spring max travel in meters
    wheel.suspension_stiffness  = 30.0   # N/m; 20 = soft, 50 = stiff race car
    wheel.suspension_damping    = 0.3    # critically damped ≈ 0.7; lower for bouncier
    wheel.suspension_max_force  = 6000.0 # N; cap to prevent explosion on big hits
    wheel.wheel_friction_slip   = 1.0    # lateral grip; 0.5 = ice, 1.5 = race slick
    wheel.damping_compression   = 0.3
    wheel.damping_relaxation    = 0.5
```

`suspension_stiffness` is the spring constant. A car with mass 1200 kg on four wheels needs roughly `(1200 * 9.8) / (4 * suspension_travel)` N/m to support its weight at mid-travel — about 19,600 N/m for 0.15 m travel. Start near that and tune for feel.

## Center of mass

`VehicleBody3D` exposes `center_of_mass_mode` and `center_of_mass`. Lower the center of mass below the geometric center of the chassis for stability:

```gdscript
func _ready() -> void:
    center_of_mass_mode = RigidBody3D.CENTER_OF_MASS_MODE_CUSTOM
    center_of_mass = Vector3(0.0, -0.25, 0.0)   # 25 cm below geometry center
```

Higher center of mass (toward 0.0 or positive Y) increases body roll and makes rollovers easier. This is physically correct — an SUV tips more than a sports car. Tune this first when the car feels unstable.

Also set `mass` in the Inspector (not in code, unless at runtime). A passenger car is 1000–1500 kg. A too-light body produces moon-gravity suspension behavior even with correct stiffness values.

## Engine torque curve

A constant `engine_force` gives instant top speed and no discernible acceleration feel. Real engines produce maximum torque at mid-RPM, trailing off at high speed. Model this with a `Curve` resource:

```gdscript
@export var torque_curve: Curve    # x = 0-1 (speed ratio), y = 0-1 (torque ratio)
@export var max_engine_force: float = 2500.0   # N
@export var max_speed: float = 40.0            # m/s (~144 km/h)

func _physics_process(delta: float) -> void:
    var speed       := linear_velocity.dot(-global_transform.basis.z)
    var speed_ratio := clampf(absf(speed) / max_speed, 0.0, 1.0)
    var throttle    := Input.get_axis(&"brake", &"accelerate")
    var torque      := torque_curve.sample(speed_ratio) * max_engine_force
    engine_force    = throttle * torque

    var steer_input := Input.get_axis(&"steer_right", &"steer_left")
    steering = _speed_limited_steering(steer_input, speed_ratio)

    braking = Input.get_action_strength(&"brake") * 20.0
```

A typical torque curve for an arcade car: high torque (0.8–1.0) from speed_ratio 0.0–0.3, gradually falling to 0.1 at speed_ratio 1.0. This produces a satisfying lurch from standstill and a soft top-speed ceiling.

## Steering and speed-dependent angle limiting

Full steering lock at highway speed produces a spin. Linearly reduce the maximum steering angle as speed increases:

```gdscript
@export var max_steer_angle_low:  float = 0.52   # radians ~30°, low speed
@export var max_steer_angle_high: float = 0.12   # radians ~7°, top speed

func _speed_limited_steering(input: float, speed_ratio: float) -> float:
    var max_angle := lerpf(max_steer_angle_low, max_steer_angle_high, speed_ratio)
    return input * max_angle
```

Add steering interpolation (lerp the current steering value toward the target each frame) for a heavier, more physical feel:

```gdscript
var _current_steering := 0.0

func _apply_steering(target: float, delta: float) -> void:
    _current_steering = lerpf(_current_steering, target, 8.0 * delta)
    steering = _current_steering
```

## Handbrake and drift

The handbrake locks the rear wheels, causing the rear end to slide:

```gdscript
func _apply_handbrake(active: bool) -> void:
    if active:
        wheel_RL.wheel_friction_slip = 0.4    # reduced grip → slide
        wheel_RR.wheel_friction_slip = 0.4
        wheel_RL.braking = 30.0
        wheel_RR.braking = 30.0
        engine_force = 0.0
    else:
        wheel_RL.wheel_friction_slip = _base_friction
        wheel_RR.wheel_friction_slip = _base_friction
        wheel_RL.braking = 0.0
        wheel_RR.braking = 0.0
```

Spawn a skidmark particle at each rear wheel contact point while handbrake is active and wheels are above the slip threshold.

## Surface detection and per-surface friction

Cast a ray downward from each wheel to detect the surface material and set wheel friction accordingly:

```gdscript
func _update_surface_friction() -> void:
    var space := get_world_3d().direct_space_state
    for wheel in [wheel_FL, wheel_FR, wheel_RL, wheel_RR]:
        var query := PhysicsRayQueryParameters3D.create(
            wheel.global_position,
            wheel.global_position + Vector3.DOWN * (wheel.suspension_travel + wheel.wheel_radius + 0.1)
        )
        query.exclude = [self]
        var result := space.intersect_ray(query)
        if result.is_empty():
            continue
        var collider := result["collider"]
        if collider is StaticBody3D and collider.physics_material_override:
            var mat: PhysicsMaterial = collider.physics_material_override
            # PhysicsMaterial.friction ranges 0-1; map to wheel slip range 0.5-1.5
            wheel.wheel_friction_slip = lerpf(0.5, 1.5, mat.friction)
        _last_contacts[wheel] = result["position"]
```

Cache `_last_contacts` for skidmark generation. PhysicsMaterial assets on `StaticBody3D` nodes are the cleanest way to encode surface properties — one asset per surface type (asphalt, gravel, ice, mud).

## Skidmarks

Generate skidmarks by tracking each wheel's contact point and comparing the wheel's lateral velocity against a slip threshold:

```gdscript
const SKID_THRESHOLD := 2.0   # m/s lateral slip

func _update_skidmarks() -> void:
    for wheel in [wheel_FL, wheel_FR, wheel_RL, wheel_RR]:
        # Lateral slip = velocity component perpendicular to wheel's forward direction
        var wheel_right  := wheel.global_transform.basis.x
        var lateral_vel  := linear_velocity.dot(wheel_right)
        if absf(lateral_vel) > SKID_THRESHOLD and _last_contacts.has(wheel):
            _skidmark_manager.extend_mark(wheel, _last_contacts[wheel])
        else:
            _skidmark_manager.end_mark(wheel)
```

The skidmark manager holds a pool of `ImmediateMesh` instances per wheel, each a triangle strip that grows along the contact path. Cap the strip length at a maximum vertex count and remove old strips. Fade alpha on old segments via a `StandardMaterial3D` with `vertex_color_use_as_albedo = true`, encoding alpha in vertex color.

## Anti-roll bar

Without an anti-roll bar, a car with soft suspension leans dramatically in corners and can roll over. Simulate an anti-roll bar by applying a counter-torque proportional to the roll angle:

```gdscript
@export var anti_roll_stiffness: float = 8000.0   # N·m per radian

func _apply_anti_roll() -> void:
    # Measure roll as difference in left/right wheel suspension compression.
    var travel_fl := wheel_FL.get_skidinfo()   # 0-1: 0 = fully compressed, 1 = at rest
    var travel_fr := wheel_FR.get_skidinfo()
    var roll_diff  := travel_fl - travel_fr
    var anti_torque := roll_diff * anti_roll_stiffness
    # Apply to the chassis Z axis (roll axis)
    apply_torque(global_transform.basis.z * anti_torque)
```

`VehicleWheel3D` does not directly expose suspension compression. Use `get_skidinfo()` as a proxy (it reflects traction loss which correlates with extension), or cast rays from each wheel to measure actual ground distance. An alternative is to read `wheel.position` delta from its rest position, which requires caching the rest position.

## Drift tuning

To make a car drift controllably:

1. Reduce rear wheel `wheel_friction_slip` to 0.6–0.8 (enough grip to steer, not enough to prevent slide).
2. Apply a small engine boost to rear wheels while drifting (counter-steers energy loss).
3. Clamp the body's angular velocity to prevent full spin-out: `angular_velocity.y = clampf(angular_velocity.y, -2.5, 2.5)`.
4. Compute the visual drift angle for UI/effects: `drift_angle = atan2(linear_velocity.dot(global_transform.basis.x), linear_velocity.dot(-global_transform.basis.z))`.

```gdscript
func _apply_drift_mode(active: bool, delta: float) -> void:
    var target_friction := 0.65 if active else _base_friction
    var friction        := lerpf(wheel_RL.wheel_friction_slip, target_friction, 10.0 * delta)
    wheel_RL.wheel_friction_slip = friction
    wheel_RR.wheel_friction_slip = friction
    if active:
        var clamp_av := angular_velocity
        clamp_av.y   = clampf(clamp_av.y, -2.5, 2.5)
        angular_velocity = clamp_av
```

## Unity equivalent (WheelCollider)

In Unity, `WheelCollider` drives vehicle physics on a `Rigidbody`:

```csharp
// WheelCollider properties
wheelCollider.motorTorque  = throttleInput * torqueCurve.Evaluate(speedRatio) * maxTorque;
wheelCollider.steerAngle   = steerInput * Mathf.Lerp(maxSteer, minSteer, speedRatio) * Mathf.Rad2Deg;
wheelCollider.brakeTorque  = brakeInput * brakePower;

// CRITICAL: sync visual mesh to collider pose — WheelCollider does NOT move its child meshes.
Vector3 pos; Quaternion rot;
wheelCollider.GetWorldPose(out pos, out rot);
wheelMesh.transform.SetPositionAndRotation(pos, rot);
```

The `GetWorldPose()` sync is mandatory and is the single most common Unity vehicle bug. The visual wheel mesh is not a child of the WheelCollider in the hierarchy in a way that auto-follows — you must call `GetWorldPose()` in `Update()` for every wheel.

Override `Rigidbody.centerOfMass` on the vehicle:
```csharp
GetComponent<Rigidbody>().centerOfMass = new Vector3(0f, -0.3f, 0f);
```

Unity's `WheelCollider.forwardFriction` and `sidewaysFriction` use `WheelFrictionCurve` with `extremumSlip`, `extremumValue`, `asymptoteSlip`, `asymptoteValue` — equivalent to the Pacejka tire model. Set `stiffness` on both curves to simulate surface traction.

## Common mistakes

**Making the vehicle a CharacterBody3D** — manually computing velocity and collision response throws away all real suspension, weight transfer, body roll, and grip physics. The car will feel like a hovercraft. Use `VehicleBody3D`.

**Forgetting visual wheel sync** — in both Godot and Unity, the visual wheel mesh does not automatically follow the physics wheel. In Godot, `VehicleWheel3D` child meshes DO follow the node, so place visual meshes as children of the wheel node. In Unity, you must call `GetWorldPose()` every frame.

**Constant engine_force without a torque curve** — this gives immediate top speed from standstill with no feel of acceleration. The torque curve is 10 lines of code and transforms driving feel completely.

**Too-light vehicle mass** — a 50 kg vehicle with the same suspension stiffness as a 1200 kg car flies into the air on minor bumps. Set mass to a physically plausible value first, then tune stiffness.

**Not resetting wheel_friction_slip after handbrake release** — leaving rear grip at the handbrake value after releasing the key means the car permanently understeers. Always restore base friction on release.

**Ignoring suspension_max_force** — without a cap, driving over a large step can generate a suspension force spike that launches the car skyward. Set `suspension_max_force` to ~5× the per-wheel static load.
