# Inverse Kinematics in Godot 4

Keyframe animation is static: an animator recorded a walk cycle on flat ground, and the character plays that cycle regardless of whether they're on a slope, stairs, or rocky terrain. Feet clip through the ground on inclines, hands miss a grab point by 12 centimeters, the head stares straight ahead while the target is 45 degrees to the right. Inverse kinematics (IK) solves this by working backwards from a desired *end-effector position* (where the foot should land, where the hand should grip) and computing the chain of joint angles that put it there — adapting the skeleton to the world at runtime, on top of whatever the animation system provides.

IK is a post-process on top of animation, not a replacement for it. The animation provides the base pose; IK adjusts specific bone chains to satisfy position constraints. The Godot pipeline is: AnimationTree outputs pose → SkeletonIK3D modifies the skeleton → render.

## FABRIK algorithm

FABRIK (Forward And Backward Reaching IK) is the algorithm Godot's SkeletonIK3D uses internally. It is iterative and geometrically intuitive: given a chain of bones from root to tip, reach the tip toward the target (forward pass), then correct the root back to its original position (backward pass), repeat until the tip is within tolerance of the target or a max iteration count is reached. Convergence is typically within 5–10 iterations for a 2–4 bone chain. FABRIK handles constraints (joint limits) poorly compared to analytic or CCD solvers, but for limb placement — where approximate results are visually acceptable — it is fast and stable.

You rarely implement FABRIK yourself in Godot; SkeletonIK3D wraps it. Knowing the algorithm matters when you need to implement 2D IK manually (GDScript FABRIK for spider legs in 2D), debug why the solver fails on certain configurations, or explain why IK "pops" when the target moves past the maximum chain extension.

## SkeletonIK3D setup

SkeletonIK3D must be a direct child of a Skeleton3D node. It operates on that skeleton's bones. Required properties:

- `root_bone`: the StringName of the chain's root bone (e.g., `&"UpperLeg_L"`). This bone and all bones between it and `tip_bone` are modified by the solver.
- `tip_bone`: the end of the chain (e.g., `&"Foot_L"`). This is the bone you're driving toward the target.
- `target`: a NodePath to a Node3D whose global position becomes the IK target. The solver drives `tip_bone` toward `target.global_position`.
- `interpolation`: float 0.0–1.0. At 0.0 the animation pose is used unchanged; at 1.0 the IK fully overrides the chain. Animate this property to blend IK in/out.
- `magnet`: optional NodePath; biases the chain's "knee" or "elbow" direction (controls which way the joint bends).
- `override_tip_basis`: bool. When true, the tip bone's rotation is fully overridden to match the target node's rotation (useful for aligning a foot to a surface normal). When false, only position is solved and the original tip rotation is preserved.

Call `start()` to activate the solver; call `stop()` to deactivate. The solver runs every frame while active, so use `interpolation = 0.0` instead of `stop()` when you want to blend out smoothly.

```gdscript
@onready var ik_left_foot: SkeletonIK3D = $Skeleton3D/IKLeftFoot
@onready var ik_right_foot: SkeletonIK3D = $Skeleton3D/IKRightFoot
@onready var foot_target_left: Marker3D = $FootTargetLeft
@onready var foot_target_right: Marker3D = $FootTargetRight

func _ready() -> void:
    ik_left_foot.start()
    ik_right_foot.start()
    ik_left_foot.interpolation = 0.0  # start blended out; ramp up in _process
    ik_right_foot.interpolation = 0.0
```

## Procedural foot placement

The goal: each foot rests on the ground surface directly below the animated foot bone position, not at the flat plane y=0 that the animator assumed. This makes the character look grounded on slopes, steps, and uneven terrain.

Architecture: two RayCast3D nodes cast downward from each foot's animated position each frame. The hit point becomes the IK target for that foot. The character's pelvis height adjusts so neither foot is underground. The pelvis rotation tracks the average slope.

```gdscript
# foot_ik_controller.gd — attach to the character's root node
class_name FootIKController extends Node

@export var skeleton_path: NodePath
@export var body: CharacterBody3D  # the character root

@onready var skeleton: Skeleton3D = get_node(skeleton_path)
@onready var ik_l: SkeletonIK3D = skeleton.get_node("IKLeftFoot")
@onready var ik_r: SkeletonIK3D = skeleton.get_node("IKRightFoot")
@onready var target_l: Marker3D = $FootTargetLeft
@onready var target_r: Marker3D = $FootTargetRight
@onready var ray_l: RayCast3D = $RayLeft
@onready var ray_r: RayCast3D = $RayRight

const RAY_LENGTH := 1.2        # cast this far below foot start
const PELVIS_SMOOTH := 8.0     # lerp speed for pelvis height adjustment
const IK_SMOOTH := 10.0        # lerp speed for foot target movement
const FOOT_OFFSET := 0.05      # keep foot slightly above collision surface

var _pelvis_offset: float = 0.0
var _pelvis_bone_idx: int = -1

func _ready() -> void:
    ik_l.start()
    ik_r.start()
    _pelvis_bone_idx = skeleton.find_bone("Pelvis")

func _process(delta: float) -> void:
    _update_foot(delta, ik_l, ray_l, target_l, "LeftFoot")
    _update_foot(delta, ik_r, ray_r, target_r, "RightFoot")
    _update_pelvis(delta)

func _update_foot(delta: float, ik: SkeletonIK3D, ray: RayCast3D,
                  target: Marker3D, bone_name: String) -> void:
    var bone_idx = skeleton.find_bone(bone_name)
    # Get the current animated world position of this foot bone
    var bone_global_pose = skeleton.get_bone_global_pose(bone_idx)
    var foot_world_pos = skeleton.global_transform * bone_global_pose.origin

    # Position the ray above the foot and cast down
    ray.global_position = foot_world_pos + Vector3.UP * 0.5
    ray.target_position = Vector3.DOWN * RAY_LENGTH

    if ray.is_colliding():
        var hit = ray.get_collision_point()
        var normal = ray.get_collision_normal()
        hit.y += FOOT_OFFSET

        # Smooth the foot target toward the hit point
        var current = target.global_position
        target.global_position = current.lerp(hit, delta * IK_SMOOTH)

        # Align foot to surface normal: rotate the target marker
        var up = normal
        var forward = -body.global_transform.basis.z
        var right = forward.cross(up).normalized()
        forward = up.cross(right).normalized()
        target.global_transform.basis = Basis(right, up, -forward)

        # Blend IK fully in when on terrain
        ik.interpolation = lerpf(ik.interpolation, 1.0, delta * IK_SMOOTH)
    else:
        # No ground found (over a ledge, in air) — blend IK out
        ik.interpolation = lerpf(ik.interpolation, 0.0, delta * IK_SMOOTH)

func _update_pelvis(delta: float) -> void:
    # Adjust pelvis height so neither foot is underground
    # Find how far each foot target is below the animated bone position
    var l_bone = skeleton.global_transform * skeleton.get_bone_global_pose(
        skeleton.find_bone("LeftFoot")).origin
    var r_bone = skeleton.global_transform * skeleton.get_bone_global_pose(
        skeleton.find_bone("RightFoot")).origin
    var l_delta = target_l.global_position.y - l_bone.y
    var r_delta = target_r.global_position.y - r_bone.y
    # Use the minimum offset (lowest foot needs to go up the most)
    var desired_offset = minf(l_delta, r_delta)
    _pelvis_offset = lerpf(_pelvis_offset, desired_offset, delta * PELVIS_SMOOTH)

    # Apply pelvis offset via bone pose modification
    if _pelvis_bone_idx >= 0:
        var pose = skeleton.get_bone_pose(_pelvis_bone_idx)
        pose.origin.y += _pelvis_offset
        skeleton.set_bone_pose(_pelvis_bone_idx, pose)
```

Run foot IK updates in `_process` (visual, not physics). The raycast positions update every visual frame so the feet track the terrain smoothly. Don't run this in `_physics_process` — it introduces visual jitter because physics runs at a fixed rate that doesn't match render frames.

## Hand IK for interactive objects

When a character grabs a door handle, climbs a ladder, or picks up a weapon, the hand must reach to a specific world point. The pattern: place a `Marker3D` on the interactive object at the exact grip point (set position/rotation in the editor), and when the character is within range, blend the hand IK target to that marker.

```gdscript
# hand_ik_interactor.gd — attach to character
class_name HandIKInteractor extends Node

@onready var ik_hand_r: SkeletonIK3D = $Skeleton3D/IKRightHand
@onready var ik_target_r: Marker3D = $HandTargetRight

const BLEND_SPEED := 6.0

var _current_grip_point: Marker3D = null

func _ready() -> void:
    ik_hand_r.start()
    ik_hand_r.interpolation = 0.0

func _process(delta: float) -> void:
    if _current_grip_point:
        # Move IK target toward the grip marker
        ik_target_r.global_transform = ik_target_r.global_transform.interpolate_with(
            _current_grip_point.global_transform, delta * BLEND_SPEED
        )
        ik_hand_r.interpolation = lerpf(
            ik_hand_r.interpolation, 1.0, delta * BLEND_SPEED
        )
    else:
        # Blend back to animation
        ik_hand_r.interpolation = lerpf(
            ik_hand_r.interpolation, 0.0, delta * BLEND_SPEED
        )

# Called by the interactive object's Area3D.body_entered signal
func set_grip_point(marker: Marker3D) -> void:
    _current_grip_point = marker

# Called by Area3D.body_exited
func clear_grip_point() -> void:
    _current_grip_point = null
```

The `Marker3D` on the door handle stores both position and rotation. By interpolating `global_transform` (not just `global_position`), the hand aligns to the grip orientation — palm faces the correct direction when grabbing a horizontal bar vs. a vertical pole. Set `ik_hand_r.override_tip_basis = true` so the solver also controls hand rotation.

## IK weight blending

Never toggle `start()` / `stop()` to switch IK on and off. `stop()` is immediate — the skeleton snaps from the IK-solved pose back to the animation pose in a single frame, which is visually jarring even at 60fps. Always use the `interpolation` property to lerp in and out. The same lerp approach applies to any SkeletonIK3D activation:

```gdscript
# Wrong: instant visual snap
ik_hand.stop()

# Correct: fade out over ~0.15s
func deactivate_hand_ik() -> void:
    var tween = create_tween()
    tween.tween_property(ik_hand, "interpolation", 0.0, 0.15)
    tween.tween_callback(ik_hand.stop)  # stop after fade is complete
```

## Head look-at

Full-chain head look-at (spine + neck + head all rotating toward a target) is achievable with SkeletonIK3D using a 2–3 bone chain from spine2 to head, with `root_bone = "Spine2"` and `tip_bone = "Head"`. However, for most games, a simpler approach using `LookAtModifier3D` (available in Godot 4.3+) or manual bone rotation is sufficient:

```gdscript
# Simple head rotation toward a look target
func _process(delta: float) -> void:
    if look_target == null:
        return
    var head_bone_idx = skeleton.find_bone("Head")
    var head_pose = skeleton.get_bone_global_pose(head_bone_idx)
    var head_world = skeleton.global_transform * head_pose

    var dir_to_target = (look_target.global_position - (skeleton.global_transform * head_pose.origin)).normalized()
    var target_basis = Basis.looking_at(dir_to_target, Vector3.UP)
    # Convert to bone local space
    var local_basis = (skeleton.global_transform.basis * head_pose.basis).inverse() * target_basis

    # Clamp to prevent unnatural head twist (±60° horizontal, ±30° vertical)
    var euler = local_basis.get_euler()
    euler.x = clampf(euler.x, -0.52, 0.52)  # ~30°
    euler.y = clampf(euler.y, -1.05, 1.05)  # ~60°
    euler.z = 0.0

    var new_pose = head_pose
    new_pose.basis = Basis.from_euler(euler)
    skeleton.set_bone_pose(head_bone_idx, new_pose)
```

`LookAtModifier3D` in Godot 4.3+ does this with a dedicated node that handles the coordinate space conversion and clamping automatically — prefer it over manual bone pose manipulation when available.

## 2D IK

In Godot 4, 2D IK uses the `Skeleton2D` node with a `SkeletonModificationStack2D` and a `SkeletonModification2DFABRIK` modifier. The setup is analogous to 3D: define the chain from root to tip bone, set a target `Node2D`, and the FABRIK modifier solves the chain each frame.

For a procedurally animated spider with 8 legs, create 8 `SkeletonModification2DFABRIK` modifiers in one stack, each controlling a 3-bone leg chain. Update the 8 target positions each frame by raycasting from an anchor point above each leg:

```gdscript
# spider_ik_2d.gd
func _process(delta: float) -> void:
    for i in 8:
        var anchor_pos = get_leg_anchor_world_pos(i)
        var space = get_world_2d().direct_space_state
        var query = PhysicsRayQueryParameters2D.create(
            anchor_pos, anchor_pos + Vector2.DOWN * 80.0
        )
        var result = space.intersect_ray(query)
        if result:
            leg_targets[i].global_position = result.position
```

2D FABRIK is computationally cheap. Running it for 8 legs on a spider entity costs less than a single 3D SkeletonIK3D solve.

## Performance

IK is per-skeleton per frame. On a scene with 50 enemies each with foot IK, that's 100 SkeletonIK3D solvers running every frame. The mitigation:

**Cache bone indices.** `skeleton.find_bone("LeftFoot")` does a string search each call. Cache it in `_ready()`:

```gdscript
var _foot_l_idx: int
var _foot_r_idx: int
var _pelvis_idx: int

func _ready() -> void:
    _foot_l_idx = skeleton.find_bone("LeftFoot")
    _foot_r_idx = skeleton.find_bone("RightFoot")
    _pelvis_idx = skeleton.find_bone("Pelvis")
```

**Disable off-screen.** Use `VisibilityNotifier3D` (add it to the character, set bounds to match the mesh AABB) and connect `screen_exited` and `screen_entered` signals to blend IK out/in:

```gdscript
@onready var visibility: VisibilityNotifier3D = $VisibilityNotifier3D

func _ready() -> void:
    visibility.screen_exited.connect(_on_screen_exited)
    visibility.screen_entered.connect(_on_screen_entered)

func _on_screen_exited() -> void:
    # Stop IK entirely when not visible — no point solving invisible characters
    ik_l.stop()
    ik_r.stop()

func _on_screen_entered() -> void:
    ik_l.start()
    ik_r.start()
```

**Coarse tick rate for background enemies.** For enemies that are visible but not the focus (background crowd), run IK updates every other frame:

```gdscript
func _process(delta: float) -> void:
    if Engine.get_frames_drawn() % 2 == 0:
        _update_foot_ik(delta * 2.0)  # pass doubled delta for lerp continuity
```

## Common mistakes

**Setting IK target to a raw world-space Vector3 by assigning `target` path to nothing and manually setting `target_node.global_position`** is correct only if the target node's position is in world space. The `SkeletonIK3D.target` property is a NodePath — it must point to a Node3D in the scene tree. If you want to drive the target programmatically, create a `Marker3D` in the scene and move that node each frame; don't try to set the target position directly on the SkeletonIK3D.

**Forgetting `override_tip_basis = true` for hand IK** means the hand reaches the correct *position* but with the wrong *rotation* — the palm faces a random direction instead of aligning to the grip marker's orientation. For foot IK on flat terrain it doesn't matter; for hand IK on interactive objects, always set it to true.

**Running foot IK in `_physics_process`** introduces a one-frame lag between physics and rendering, causing feet to visibly vibrate at physics step boundaries. Foot IK is a visual system — run it in `_process`.

**Not blending `interpolation` from 0 on character spawn** causes a one-frame snap from the T-pose (or bind pose) to the IK-solved pose when the character first appears. Set `interpolation = 0.0` in `_ready()` and ramp up to 1.0 in the first few frames.
