# AnimationTree, Blend Trees, and Layered Animation

Calling `animation_player.play("run")` directly is the wrong pattern for any character with more than two states. It produces hard cuts between animations, breaks blending, and makes layered animation (upper body aiming while legs run) impossible. The correct architecture is: AnimationPlayer owns the raw clips → AnimationTree orchestrates blending and state transitions → GDScript sets parameters on the tree rather than driving playback directly. This gives you crossfades, blend spaces, and layered masking for free.

## AnimationTree node setup

Add an `AnimationTree` node as a sibling of (or child alongside) `AnimationPlayer`. Set `AnimationTree.anim_player` to point at the AnimationPlayer. Set `AnimationTree.active = true` in `_ready()` or via the inspector. The `tree_root` property of AnimationTree holds an `AnimationNode` — this is where the logic lives.

Two main `tree_root` choices: `AnimationNodeStateMachine` for state-based characters (most cases), and `AnimationNodeBlendTree` when you need explicit node graph control (blending layers manually). For a typical platformer or RPG character, start with StateMachine; add a BlendTree inside when you need upper/lower body separation.

The AnimationTree parameters API uses a path string that mirrors the node graph: `"parameters/StateMachine/conditions/is_jumping"` or `"parameters/BlendSpace1D/blend_position"`. Set them with `animation_tree.set(path, value)` or `animation_tree["parameters/..."] = value`. Read them with `animation_tree.get(path)`.

```gdscript
@onready var anim_tree: AnimationTree = $AnimationTree

func _physics_process(delta: float) -> void:
    var speed = velocity.length()
    anim_tree["parameters/LocomotionBlend/blend_position"] = speed
    anim_tree["parameters/conditions/is_grounded"] = is_on_floor()
    anim_tree["parameters/conditions/is_falling"] = velocity.y < -0.5 and not is_on_floor()
```

Never call `anim_player.play()` directly on a character that uses AnimationTree. The tree and the player will fight over which animation is active, producing invisible-blend bugs that are nearly impossible to diagnose.

## AnimationNodeStateMachine

The StateMachine is the default root for characters. Each **state** contains an AnimationNode (usually an Animation or a BlendSpace). **Transitions** connect states and have four key properties: `advance_condition` (a boolean blackboard key set by GDScript), `transition_time` (crossfade duration in seconds — 0.15–0.25s is usually right), `switch_mode` (Immediate, Sync, or AtEnd), and `auto_advance` (only useful for one-shot states that fall through when done).

`switch_mode`:
- **Immediate** — transition fires the instant the condition is true. Correct for jumps, hits, deaths.
- **AtEnd** — waits until the current animation loop completes, then transitions. Use for attacks and reloads so they never cut mid-swing.
- **Sync** — matches the blend position of the new state to the old state's playback position. Rarely needed.

Add a state in GDScript for a condition-based jump:

```gdscript
# Set this each frame; StateMachine's "is_jumping" condition reads it automatically
anim_tree["parameters/StateMachine/conditions/is_jumping"] = (
    Input.is_action_just_pressed("jump") and is_on_floor()
)
```

A one-shot melee attack state uses `switch_mode = AtEnd` so the attack finishes fully, then an `auto_advance` transition returns to locomotion. Connect the AnimationPlayer's `animation_finished` signal as a backup for edge cases where the state machine doesn't advance.

## BlendSpace1D for locomotion

BlendSpace1D blends animations along a single float axis. The canonical use is idle (speed=0) → walk (speed=3) → run (speed=7). Add the three animations at those positions on the axis. Each frame, set `blend_position` to the character's actual speed:

```gdscript
@onready var anim_tree: AnimationTree = $AnimationTree
@onready var nav: NavigationAgent3D = $NavigationAgent3D

func _physics_process(delta: float) -> void:
    var horizontal_vel = Vector3(velocity.x, 0.0, velocity.z)
    var speed = horizontal_vel.length()
    # Smoothly approach the actual speed to avoid jitter from small velocity noise
    var current = anim_tree["parameters/LocomotionBlend/blend_position"]
    anim_tree["parameters/LocomotionBlend/blend_position"] = lerpf(current, speed, delta * 10.0)
```

The lerp smooths out jitter from physics velocity noise. Without it, the blend position jumps between 0 and 2 m/s during idle, producing a subtle foot-sliding shimmy.

**Root motion vs. in-place**: root motion means the animation itself contains positional displacement (the animator moved the root bone forward in the DCC tool). Godot extracts this via `anim_tree.get_root_motion_position()` and the character's actual physics velocity should be driven by the extracted motion. In-place animations keep the root bone stationary and let GDScript control velocity — simpler and usually correct for responsive gameplay. Use root motion only when animation fidelity of footstep contact matters more than direct movement control (cutscenes, cinematic-quality characters).

## BlendSpace2D for strafing and directional movement

BlendSpace2D blends by two floats — typically `velocity.x` and `velocity.z` in a top-down shooter, or `input.x` and `input.y` for a character that animates differently moving forward, backward, and sideways. Place 8 directional animations at the cardinal and diagonal positions of the 2D space:

```gdscript
# For a 3D character with strafing animations
var local_vel = transform.basis.inverse() * Vector3(velocity.x, 0, velocity.z)
anim_tree["parameters/StrafeBlend/blend_position"] = Vector2(local_vel.x, -local_vel.z)
```

The `transform.basis.inverse()` converts world-space velocity to local space so the blend is relative to the character's facing direction — moving left always blends to the strafe-left animation regardless of world orientation.

## AnimationNodeBlendTree for layered animation

BlendTree is a manual node graph where you wire nodes together. The key nodes for layered animation:

- **AnimationNodeAnimation** — plays a single clip.
- **AnimationNodeBlendSpace1D / 2D** — a blend space inside the graph.
- **AnimationNodeAdd2** — adds two animations together (additive blending, correct for aim offsets).
- **AnimationNodeBlend2** — lerps between two animations with a 0–1 weight. Use for upper/lower body split.
- **AnimationNodeTimeSeek** — forces a child to a specific time, useful for sync.

For upper/lower body separation (legs play locomotion, torso plays aim or attack), use `AnimationNodeBlend2` with a bone mask. In the Blend2 node's inspector, set `filter_enabled = true` and mark the upper-body bones (spine, shoulders, arms) as filtered. The Blend2 output routes locomotion to the lower body and the attack animation to the upper body:

```
BlendTree root
├── AnimationNodeBlend2 (weight = 1.0, filter: upper body bones)
│   ├── [In0] BlendSpace1D (locomotion: idle/walk/run)
│   └── [In1] AnimationNodeAnimation ("upper_body_attack")
└── → Output
```

At `weight = 0.0`, only locomotion plays everywhere. At `weight = 1.0`, locomotion plays on lower body and the attack animation overrides upper body. Animate the weight from 0 to 1 when an attack starts and back to 0 when it finishes:

```gdscript
func _on_attack_started() -> void:
    var tween = create_tween()
    tween.tween_method(
        func(w): anim_tree["parameters/UpperBodyBlend/blend_amount"] = w,
        0.0, 1.0, 0.08
    )

func _on_attack_finished() -> void:
    var tween = create_tween()
    tween.tween_method(
        func(w): anim_tree["parameters/UpperBodyBlend/blend_amount"] = w,
        1.0, 0.0, 0.12
    )
```

## Transition conditions in GDScript

StateMachine transitions read from the `conditions` dictionary in `parameters/StateMachine/conditions/`. Setting a condition to `true` for a single frame is usually enough to trigger a transition, but make sure the condition key matches exactly what you named it in the editor. A mismatch silently does nothing:

```gdscript
# Set conditions in _physics_process or _process
func _update_anim_conditions() -> void:
    anim_tree["parameters/StateMachine/conditions/jump_pressed"] = (
        Input.is_action_just_pressed("jump") and is_on_floor()
    )
    anim_tree["parameters/StateMachine/conditions/landed"] = (
        is_on_floor() and was_airborne
    )
    anim_tree["parameters/StateMachine/conditions/attack_pressed"] = (
        Input.is_action_just_pressed("attack")
    )
    was_airborne = not is_on_floor()
```

For a one-shot transition you want to fire once and reset (like landing), reset the condition the frame after setting it:

```gdscript
if just_landed:
    anim_tree["parameters/StateMachine/conditions/landed"] = true
    await get_tree().process_frame
    anim_tree["parameters/StateMachine/conditions/landed"] = false
```

Alternatively, use `AnimationNodeStateMachineTransition.advance_expression` (a GDExpression string evaluated each tick) for stateless condition logic that doesn't need GDScript to manage reset.

## Root motion

When using root motion clips: in each frame, extract the delta position the animation wants the character to move, then apply it to the CharacterBody3D's velocity instead of (or in addition to) your physics velocity:

```gdscript
func _physics_process(delta: float) -> void:
    # AnimationTree must be ticked first; it updates root motion data
    var rm_pos = anim_tree.get_root_motion_position()
    var rm_vel = rm_pos / delta  # Convert position delta to velocity

    # Transform from animation-local space to world space
    var world_rm_vel = global_transform.basis * rm_vel

    velocity.x = world_rm_vel.x
    velocity.z = world_rm_vel.z
    # Don't override Y; let gravity handle it
    move_and_slide()
```

Root motion and direct velocity control are mutually exclusive for horizontal movement. Commit to one or the other per character — mixing them produces drifting.

## AimOffset / BlendSpace2D aim layer

An aim offset (Unity term) or aim blend space (Godot pattern) lets a character's spine and head rotate to track a target without a separate aim IK pass. Create a BlendSpace2D with animations for aim-up, aim-down, aim-left, aim-right, and center. The blend position is the 2D angle between the character's forward vector and the aim direction:

```gdscript
func _update_aim_blend() -> void:
    if not has_target:
        return
    var to_target = (aim_target - global_position).normalized()
    # Project onto character's local axes
    var local_dir = global_transform.basis.inverse() * to_target
    # local_dir.z is forward/back, local_dir.x is left/right, local_dir.y is up/down
    var aim_h = clampf(local_dir.x, -1.0, 1.0)  # horizontal [-1, 1]
    var aim_v = clampf(local_dir.y, -1.0, 1.0)  # vertical [-1, 1]
    anim_tree["parameters/AimOffset/blend_position"] = Vector2(aim_h, aim_v)
```

This approach is entirely in animation-space and cheaper than SkeletonIK for aim tracking. Combine with IK for exact hand/weapon placement (see `inverse-kinematics.md`).

## Animation events via call track

Godot's AnimationPlayer supports a **Call Method Track** — a track that calls a method on a node at a specific frame. This is how you:
- Trigger footstep sounds at foot-plant frames (not on a timer)
- Spawn hit-detection hitboxes at the exact attack frame
- Enable/disable particle effects at animation-defined moments

Add a Call Method Track to the attack animation: at frame 8 (the swing impact frame), call `enemy.enable_hitbox(true)`; at frame 12, call `enemy.enable_hitbox(false)`. The hitbox is active for exactly 4 frames regardless of game speed, time scale, or animation blend weight. This is the correct approach — hitbox timing from a timer or from code logic is always out of sync.

```gdscript
# Called by AnimationPlayer's method track at the correct frame
func enable_hitbox(enabled: bool) -> void:
    $HitboxArea3D/CollisionShape3D.disabled = not enabled
    if enabled:
        $HitboxArea3D.monitoring = true
    else:
        $HitboxArea3D.monitoring = false
```

In Unity, Animation Events serve the same purpose: add an event at a keyframe in the Animation clip, set the function name and parameter, and the Animator calls it on the attached MonoBehaviour at that frame.

## One-shot animations

A melee attack plays once and returns to locomotion. In Godot, the cleanest approach is an `AnimationNodeOneShot` node inside a BlendTree, or a separate state in the StateMachine with `AtEnd` transition mode. The `AnimationNodeOneShot` approach:

The OneShot node sits between the locomotion output and the blend tree output. When `request = ONE_SHOT_REQUEST_FIRE`, it plays the assigned animation once, blending over the locomotion, then transitions back. Trigger it:

```gdscript
anim_tree["parameters/AttackOneShot/request"] = AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE
```

Abort it early (interrupted by stagger, death):
```gdscript
anim_tree["parameters/AttackOneShot/request"] = AnimationNodeOneShot.ONE_SHOT_REQUEST_ABORT
```

The OneShot node's `fadein_time` and `fadeout_time` properties control blend duration at both ends — 0.08s in, 0.15s out is typical for melee.

Alternatively, connect `AnimationPlayer.animation_finished` signal to detect when the attack clip ends and manually reset state:

```gdscript
func _on_animation_finished(anim_name: StringName) -> void:
    if anim_name == &"melee_attack":
        is_attacking = false
        anim_tree["parameters/StateMachine/conditions/attack_done"] = true
```

## SkeletonIK3D integration

AnimationTree drives the skeleton pose each frame. SkeletonIK3D runs after AnimationTree and modifies specific bone positions to satisfy IK constraints (foot on ground, hand on handle). The integration is automatic — add SkeletonIK3D as a child of Skeleton3D, call `start()`, and it post-processes the animation output. The `interpolation` property (0–1) blends between pure animation and full IK, letting you fade IK in/out smoothly. See `inverse-kinematics.md` for the full foot placement and hand IK setup.

## Common mistakes

**Calling `anim_player.play()` directly on an AnimationTree character** is the most common mistake. It temporarily takes control away from AnimationTree, which snaps back on the next frame with whatever state the tree was last in — you see a 1-frame flash of the wrong animation, or the character freezes mid-blend. All animation control for a character using AnimationTree goes through `anim_tree.set()` parameter calls only.

**Setting blend_position without smoothing** causes visible snapping in locomotion blends when the character starts or stops suddenly. Always lerp toward the target blend position rather than setting it directly, unless you specifically want a snap (hit stagger, landing impact).

**Reusing one AnimationPlayer for multiple AnimationTree nodes** breaks both trees. Each AnimationTree needs its own AnimationPlayer. If two characters share clips, use a shared AnimationLibrary resource instead of sharing the AnimationPlayer node.

**Using StateMachine for everything including blend trees**: a StateMachine state can *contain* a BlendTree (or a BlendSpace) as its nested animation node. This is correct for locomotion-within-a-state. Don't create 8 separate states for 8-directional movement — one state with a BlendSpace2D inside handles all directions with proper blending.
