# 3D Game Development

3D games share the same five non-negotiables as 2D — frame independence, scope discipline, decoupling, juice, and deliberate engine choice — but the axis of failure shifts: 3D controllers are harder to author to feel good, camera systems clip through geometry and cause motion sickness, and performance erodes fast without LOD and baked lighting. This file covers the patterns that matter for **small-to-mid scale 3D** (a solo dev or small team making a platformer, action game, first-person game, or simple open-world). Everything here leans Godot 4 but flags Unity equivalents.

## Contents
- CharacterBody3D: the kinematic controller
- Third-person camera: the SpringArm rig
- First-person controller
- Camera-relative movement
- 3D pathfinding (NavigationAgent3D)
- 3D physics layers
- Lighting: baked vs real-time
- LOD and occlusion culling
- Skeletal animation and blend trees
- Modular level design

## CharacterBody3D: the kinematic controller

The same rule as 2D applies harder in 3D: **do not use RigidBody3D for the player avatar**. Physics-based movement gives you realistic-but-frustrating results — the character slides on slopes, can't reliably jump off moving platforms, and resists the authored feel players expect. Use **CharacterBody3D** and set velocity manually.

```gdscript
# Godot 4 — CharacterBody3D skeleton
extends CharacterBody3D

@export var speed: float = 5.0
@export var jump_velocity: float = 5.5
@export var acceleration: float = 20.0
@export var friction: float = 15.0

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

func _physics_process(delta: float) -> void:
    # Gravity — apply before move_and_slide
    if not is_on_floor():
        velocity.y -= gravity * delta

    # Jump
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

    # Horizontal movement — camera-relative (see section below)
    var raw_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var wish_dir := (camera_pivot.global_transform.basis *
                     Vector3(raw_dir.x, 0, raw_dir.y)).normalized()
    wish_dir.y = 0.0

    var rate := acceleration if wish_dir.length() > 0.1 else friction
    velocity.x = move_toward(velocity.x, wish_dir.x * speed, rate * delta)
    velocity.z = move_toward(velocity.z, wish_dir.z * speed, rate * delta)

    move_and_slide()
```

**Key points:**
- Use `get_setting("physics/3d/default_gravity")` rather than hardcoding 9.8 so it matches the engine's physics bodies (important when mixing kinematic + rigidbody objects like rolling crates).
- Asymmetric gravity for platformers works exactly as in 2D: apply more gravity when `velocity.y < 0` (falling) than when rising.
- `move_and_slide()` handles stair-stepping via the `floor_max_angle` and `floor_stop_on_slope` properties. For climbing stairs, `floor_snap_length` snaps the character down onto steps during descent rather than launching off each step edge.
- For coyote time and jump buffering, the logic is identical to 2D — track a `coyote_timer` and `jump_buffer_timer` as floats, decrement each `_physics_process`, allow a jump when either is > 0.
- **Slope sliding:** Godot's `move_and_slide` handles most slopes automatically. For steeper slopes (above `floor_max_angle`), CharacterBody3D treats them as walls. Set the slope angle threshold to match your level geometry.

## Third-person camera: the SpringArm rig

The camera is the hardest single thing to get right in a 3D game. Hard-parenting a Camera3D to the player produces a fixed, motion-sick-inducing view with no spring correction when walls are behind the player. The correct setup is a **SpringArm3D pivot rig**:

```
Player (CharacterBody3D)
└── CameraPivot (Node3D)    ← rotate this for orbit
    └── SpringArm3D          ← extends behind player; auto-shortens on geometry
        └── Camera3D         ← sits at the arm's tip
```

**Why SpringArm3D?** It casts a shape (sphere by default) along its length. When geometry intersects the sweep, it shortens the arm — the camera moves forward to stay in front of the wall. No manual raycast, no camera pop, no geometry clipping. Set `spring_length` to your desired offset (e.g. 4.0 m), `shape` to a small SphereShape3D, and add the environment collision layer to the spring arm's collision mask.

```gdscript
# Godot 4 — CameraPivot rotation from mouse
extends Node3D   # this is CameraPivot

@export var sensitivity_x: float = 0.003
@export var sensitivity_y: float = 0.003
@export var min_pitch: float = -deg_to_rad(70.0)
@export var max_pitch: float = deg_to_rad(80.0)

var pitch: float = 0.0

func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        rotate_y(-event.relative.x * sensitivity_x)
        pitch = clamp(pitch - event.relative.y * sensitivity_y, min_pitch, max_pitch)
        rotation.x = pitch
```

**Character facing:** decouple the camera from the character's visual facing direction. The `CameraPivot` rotates freely; the character mesh (or root Y rotation) turns to face the movement direction, not the camera direction. This allows "camera over left shoulder while character runs right" — the standard third-person feel.

```gdscript
# Rotate character mesh to face movement direction (not camera)
if wish_dir.length() > 0.1:
    var look_target := global_position + wish_dir
    var mesh_node: Node3D = $CharacterMesh
    mesh_node.look_at(look_target, Vector3.UP)
    # Optionally smooth with a slerp for less snappy turning:
    # mesh_node.global_rotation.y = lerp_angle(mesh_node.global_rotation.y,
    #     atan2(-wish_dir.x, -wish_dir.z), 10.0 * delta)
```

**Lock-on / targeting:** when targeting an enemy, override the `CameraPivot` rotation to orbit around the player while keeping the target in frame. Smoothly interpolate — hard snaps feel cheap.

## First-person controller

FPS movement is simpler than third-person camera-wise: the Camera3D is a direct child of the CharacterBody3D, positioned at head height.

```gdscript
# Godot 4 — FPS controller
extends CharacterBody3D

@onready var camera: Camera3D = $Head/Camera3D
@onready var head: Node3D = $Head   # child node at eye height

@export var mouse_sensitivity: float = 0.002
@export var head_clamp_deg: float = 85.0

func _ready() -> void:
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion:
        rotate_y(-event.relative.x * mouse_sensitivity)          # body yaw
        head.rotate_x(-event.relative.y * mouse_sensitivity)     # head pitch
        head.rotation.x = clamp(head.rotation.x,
            -deg_to_rad(head_clamp_deg),  deg_to_rad(head_clamp_deg))

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y -= gravity * delta
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity
    var dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var move := (transform.basis * Vector3(dir.x, 0, dir.y)).normalized()
    velocity.x = move_toward(velocity.x, move.x * speed, accel * delta)
    velocity.z = move_toward(velocity.z, move.z * speed, accel * delta)
    move_and_slide()
```

**FPS feel extras:**
- **Head bob:** a sine wave on the camera's Y position synced to footstep cadence. Keep amplitude small (< 2 px equivalent) and offer a toggle — it causes motion sickness in some players.
- **FOV pulse:** briefly widen FOV on sprint, narrow on aim-down-sights. A tween on `camera.fov` reads as responsive.
- **Weapon sway:** the weapon mesh lags behind camera rotation with a `lerp` — feels physical without actual physics.

## Camera-relative movement

In any third-person game, horizontal movement must be relative to the camera's current facing — not world axes and not the character's facing. If you move along world Z when the camera is angled 45°, the character runs sideways.

```gdscript
# Get camera-relative move direction (y component zeroed, renormalized)
var raw := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
var cam_basis := camera_pivot.global_transform.basis
var wish_dir := (cam_basis * Vector3(raw.x, 0.0, raw.y))
wish_dir.y = 0.0
wish_dir = wish_dir.normalized()
```

The `Basis` multiplication rotates the local input vector into world space, using the camera pivot's orientation. Zero out Y after rotation (don't let camera tilt affect ground movement) and re-normalize.

## 3D pathfinding (NavigationAgent3D)

Godot 4's 3D navigation uses a **NavigationMesh** baked onto level geometry and a **NavigationAgent3D** component on each enemy. For a few dozen enemies, this is the right tool; for hundreds (survivors-like in 3D), mirror the 2D flow-field pattern.

```gdscript
# Enemy — navigate toward player
extends CharacterBody3D
@onready var nav: NavigationAgent3D = $NavigationAgent3D

func _physics_process(delta: float) -> void:
    nav.target_position = player.global_position
    var next := nav.get_next_path_position()
    var dir := (next - global_position).normalized()
    velocity = dir * speed
    if not is_on_floor():
        velocity.y -= gravity * delta
    move_and_slide()
    # Rotate to face movement direction
    if velocity.length() > 0.1:
        look_at(global_position + velocity * Vector3(1,0,1), Vector3.UP)
```

**Baking the NavigationMesh:** add a **NavigationRegion3D** node to your scene, create a `NavigationMesh` resource, and bake (editor button or `bake_navigation_mesh()` at runtime for dynamic levels). Set agent radius and max slope to match your enemy capsule sizes.

**Performance:** NavigationAgent3D recalculates the path when `target_position` changes significantly or an obstacle moves. For many agents all chasing the same target, compute one path and share it, or use a flow field baked from the same NavigationMesh.

## 3D physics layers

Same principle as 2D: use **collision layers and masks** to control what intersects what. A typical 3D setup:
- Layer 1: World (environment, floors, walls)
- Layer 2: Player
- Layer 3: Player hurtbox
- Layer 4: Enemies
- Layer 5: Enemy hurtbox
- Layer 6: Player projectiles
- Layer 7: Enemy projectiles
- Layer 8: Interactables / pickups

SpringArm3D collision mask should include only World (Layer 1) — you don't want it shortened by nearby enemies.

## Lighting: baked vs real-time

Lighting is the biggest 3D performance lever. Choose based on project scope:

**Baked lighting (recommended for most small 3D games):**
- Lightmap-baked global illumination looks beautiful at zero runtime cost once baked.
- In Godot: set `DirectionalLight3D` and environment to baked mode, mark static mesh instances as `Bake Mode: Static`, bake in the editor (Mesh → Lightmap GI).
- Limitation: dynamic objects (moving enemies, the player) don't receive baked GI — add one or two `OmniLight3D` or a `LightmapProbe` cluster around the level so they're lit correctly.
- Godot 4's **VoxelGI** is a fast real-time-baked approximation good for mid-scale scenes: bake at edit time, update dynamically for moving objects.

**Real-time lighting:**
- Use sparingly — shadow casters are expensive (each shadow-casting light adds a depth pass per frame). Limit to 3–4 real-time shadow-casting lights per scene.
- **SDFGI** (Godot 4 Vulkan renderer) gives real-time GI for large scenes but requires a modern GPU — verify it runs acceptably on your minimum spec.
- **Ambient light + directional shadow only** is a performant baseline: one DirectionalLight3D with shadows, an ambient color for the sky, and no shadow-casting point lights. Add baked lightmaps or VoxelGI on top.

## LOD and occlusion culling

Performance degrades fast in 3D. The two main tools:

**Level of Detail (LOD):**
- Swap high-poly meshes for low-poly versions at distance. In Godot, use the **LOD** property on MeshInstance3D nodes (set LOD distances in the Inspector) or the `VisibilityNotifier3D` to pause AI/animations on distant enemies.
- For foliage and scattered objects, use `MultiMeshInstance3D` — renders thousands of the same mesh in one draw call.

**Occlusion culling:**
- Godot 4 has an **Occlusion Culling** system (OccluderInstance3D + Occluder3D shapes). Mark large opaque objects (walls, floors) as occluders; Godot's renderer skips geometry behind them.
- Unity's built-in Occlusion Culling bakes an occlusion map from static geometry.
- For a dungeon or interior game, occlusion culling gives a large performance win — rooms behind walls simply aren't rendered.

**Rendering budget target:** aim for < 200k triangles visible per frame and < 100 draw calls on the low-end device you're targeting. Profile with Godot's built-in profiler or RenderDoc/PIX.

## Skeletal animation and blend trees

3D characters use **skeletal rigs**: a hierarchy of bones deforms the mesh. You author animation clips (Idle, Walk, Run, Jump, Fall, Attack) and blend between them at runtime.

**Godot 4 — AnimationTree:**
The AnimationTree node (backed by an AnimationPlayer) is Godot's blend system.
- Set up an **AnimationNodeBlendSpace2D** for locomotion: blend Idle/Walk/Run by speed on one axis, Strafe by horizontal input on another.
- **AnimationNodeStateMachine** for high-level state: Grounded → Airborne → Attack → Death.
- Connect them: the state machine selects which blend space is active; the blend space handles the locomotion detail.

```gdscript
# Drive locomotion blend parameters from velocity
@onready var anim_tree: AnimationTree = $AnimationTree

func _physics_process(delta: float) -> void:
    var horizontal_speed := Vector2(velocity.x, velocity.z).length()
    anim_tree.set("parameters/Locomotion/blend_position", horizontal_speed / speed)
    anim_tree.set("parameters/Airborne/blend_position", velocity.y)
    # Trigger states
    if not is_on_floor():
        anim_tree.set("parameters/StateMachine/transition_request", "Airborne")
    else:
        anim_tree.set("parameters/StateMachine/transition_request", "Grounded")
```

**Unity — Animator Controller:**
Add an Animator component, create an Animator Controller asset, and use the BlendTree node type for locomotion (speed + direction as float parameters), with transition conditions on jump/fall booleans.

**Root motion:** for melee attacks where the character dashes forward, use root motion (the animation drives position, not just the visual mesh). In Godot, enable root motion on the AnimationTree and apply it through `move_and_slide` (via `anim_tree.get_root_motion_position()`).

**IK (Inverse Kinematics):** for feet planting on uneven terrain, a SkeletonIK3D or a 2-bone IK node can solve foot placement dynamically. Start without it — add it when visual foot-sliding is a noticeable problem.

## Modular level design

Building a 3D level out of reusable modular pieces is faster to iterate than sculpting one monolithic mesh, easier to occlude-cull, and enables runtime generation.

**Godot 4:**
- **GridMap**: a voxel-like tile system for 3D. Define a `MeshLibrary` of tile meshes (walls, floors, corners, ramps), then paint tiles in the GridMap editor. Fast for dungeon-style games, limited to grid-aligned shapes.
- **CSG (Constructive Solid Geometry):** boolean operations (CSGBox3D, CSGCylinder3D, CSGCombiner3D) for quick greyboxing and prototyping. Replace with proper meshes before shipping — CSG is expensive at render time and bakes badly.
- **Modular kit:** author asset sets as scenes (wall_2m, wall_4m, corner_inner, corner_outer, pillar, arch) with snap-friendly dimensions (multiples of 0.5 m or 1 m). Instance and snap them with the editor's grid snap. Proper modular kits outperform GridMap for stylized games because the pieces are full meshes with proper normals and LODs.

**Unity:** use **ProBuilder** for rapid greyboxing (built-in since 2018.3), then replace with final art assets. Use the Prefab Variant system to build kit variations from a base prefab.

**Greyboxing first:** always build the level in placeholder geometry before investing in art. Run the 10-second core loop through every room/area. Level design is a feel problem, not an art problem — don't dress a bad layout with pretty meshes.
