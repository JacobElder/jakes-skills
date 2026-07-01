# Cutscene and Cinematic Systems (Godot 4)

A cutscene is a time-sequenced scene that takes control from the player, directs cameras and actors, and optionally allows skipping. The implementation involves three concerns: sequencing (what happens when), camera direction (where the player looks), and skip handling (returning gracefully to gameplay state regardless of where skipping occurs).

## Contents
- AnimationPlayer as the cutscene sequencer
- Camera handoff pattern
- AnimationPlayer call tracks for game events
- Skippable cutscene state machine
- Capturing input during cutscenes
- Cutscene Resource for data-driven sequences
- Blend-in/blend-out transitions
- CinematicCamera3D and Camera2D techniques
- Long cutscene: streaming multiple AnimationPlayers

## AnimationPlayer as the cutscene sequencer

The `AnimationPlayer` node is Godot's built-in time sequencer. For cutscenes, it drives:
- Node property tracks (camera position, NPC position, light intensity, color)
- Call Method tracks (spawn events, trigger dialogue, play audio, update game state)
- Audio tracks (play/stop AudioStreamPlayer at precise frames)
- Animation tracks (play sub-animations on characters)

One `AnimationPlayer` per cutscene is the standard pattern. Each cutscene is a named animation on that player.

```gdscript
# CutscenePlayer.gd — autoload or node in the cutscene scene
extends Node

signal cutscene_finished

@onready var anim_player: AnimationPlayer = $AnimationPlayer
@onready var cutscene_camera: Camera3D = $CutsceneCamera

var _active: bool = false
var _skippable: bool = true

func play_cutscene(anim_name: String, skippable: bool = true) -> void:
    _skippable = skippable
    _active = true
    get_tree().paused = false  # cutscene may need physics for character movement
    cutscene_camera.make_current()  # hand control to cutscene camera
    anim_player.play(anim_name)
    anim_player.animation_finished.connect(_on_animation_finished, CONNECT_ONE_SHOT)

func _on_animation_finished(_anim_name: String) -> void:
    _finish_cutscene()

func _finish_cutscene() -> void:
    _active = false
    PlayerManager.player_camera.make_current()  # return control to player
    cutscene_camera.position = Vector3.ZERO     # reset for next use
    anim_player.stop()
    cutscene_finished.emit()

func skip() -> void:
    if not _active or not _skippable:
        return
    anim_player.animation_finished.disconnect(_on_animation_finished)
    _finish_cutscene()
```

## Camera handoff pattern

Multiple `Camera3D` nodes can exist in the scene. The active camera is whichever last called `make_current()`. The handoff sequence:

```gdscript
# Before cutscene:
cutscene_camera.make_current()
# → player sees the cutscene camera

# After cutscene (or on skip):
player_camera.make_current()
# → player sees their camera again
```

For smooth transitions, tween the camera using `RemoteTransform3D` or a `CameraRig` node rather than snapping. During the cutscene, `CutsceneCamera` animates along a path (via `PathFollow3D` or direct property tracks in the AnimationPlayer).

```gdscript
# Smooth camera blend using Tween before switching:
func _start_with_blend(anim_name: String) -> void:
    var tween := create_tween()
    tween.tween_property(cutscene_camera, "global_position",
        cutscene_start_position, 0.5).set_ease(Tween.EASE_IN_OUT)
    await tween.finished
    cutscene_camera.make_current()
    anim_player.play(anim_name)
```

## AnimationPlayer call tracks for game events

Call Method tracks fire GDScript methods at precise animation times. Use them to:
- Spawn or despawn actors
- Trigger dialogue bubbles
- Fire audio cues
- Enable/disable game systems (e.g. pause enemy AI)

In the AnimationPlayer timeline editor:
1. Select the cutscene animation
2. Add Track → Call Method Track → select the target node
3. Right-click at the desired time → "Add Call"
4. Choose the method and arguments

```gdscript
# Methods called from AnimationPlayer call tracks:
func _spawn_npc_from_cutscene() -> void:
    var npc := npc_scene.instantiate()
    add_child(npc)

func _play_explosion_sound() -> void:
    $ExplosionAudio.play()

func _trigger_dialogue(speaker_id: String, text: String) -> void:
    DialogueManager.show(speaker_id, text)

func _enable_enemy_ai() -> void:
    get_tree().call_group("enemies", "set_ai_active", true)
```

## Skippable cutscene state machine

The skip system must handle: input capture during cutscene, press-to-confirm skip pattern (single press shows "press again to skip" prompt, second press skips), and ensuring the game returns to a valid gameplay state regardless of skip point.

```gdscript
# CutsceneManager.gd — autoload
extends Node

enum SkipState { IDLE, PENDING, CONFIRMED }

var _skip_state: SkipState = SkipState.IDLE
var _skip_confirm_timer: float = 0.0
const SKIP_CONFIRM_WINDOW := 1.5  # seconds to press again

func _input(event: InputEvent) -> void:
    if not CutscenePlayer.is_active():
        return
    if not CutscenePlayer.is_skippable():
        return
    if not event.is_action_just_pressed("skip_cutscene"):
        return
    
    match _skip_state:
        SkipState.IDLE:
            _skip_state = SkipState.PENDING
            _skip_confirm_timer = SKIP_CONFIRM_WINDOW
            SkipPromptUI.show_prompt("Press again to skip")
        SkipState.PENDING:
            _skip_state = SkipState.CONFIRMED
            SkipPromptUI.hide()
            CutscenePlayer.skip()

func _process(delta: float) -> void:
    if _skip_state == SkipState.PENDING:
        _skip_confirm_timer -= delta
        if _skip_confirm_timer <= 0.0:
            _skip_state = SkipState.IDLE
            SkipPromptUI.hide()
```

## Capturing input during cutscenes

Block all gameplay input during a cutscene. The cleanest approach is `get_tree().paused = true` combined with `process_mode = PROCESS_MODE_ALWAYS` on the CutscenePlayer node. This pauses all gameplay nodes while the cutscene continues processing.

```gdscript
func play_cutscene(anim_name: String) -> void:
    get_tree().paused = true        # freeze everything
    # CutscenePlayer has process_mode = PROCESS_MODE_ALWAYS — keeps running
    # Camera3D with process_mode = PROCESS_MODE_ALWAYS — keeps animating
    cutscene_camera.make_current()
    anim_player.play(anim_name)

func _finish_cutscene() -> void:
    get_tree().paused = false       # resume gameplay
    player_camera.make_current()
    cutscene_finished.emit()
```

For cutscenes that require NPCs to physically move (walk to a position), leave `paused = false` and instead disable player input specifically:

```gdscript
func play_cutscene(anim_name: String) -> void:
    PlayerController.input_enabled = false
    cutscene_camera.make_current()
    anim_player.play(anim_name)
```

## Cutscene Resource for data-driven sequences

For games with many cutscenes, define a Resource schema:

```gdscript
# CutsceneData.gd
class_name CutsceneData
extends Resource

@export var cutscene_id: StringName = &""
@export var animation_name: String = ""       # matches AnimationPlayer track name
@export var skippable: bool = true
@export var pause_gameplay: bool = true
@export var camera_blend_time: float = 0.3   # seconds to blend in/out
@export var on_finish_event: StringName = &"" # emitted when complete; connects to quest system
```

CutsceneManager reads `CutsceneData` and handles all the handoff/skip/resume logic generically. Designers create new `.tres` files without writing code.

## Long cutscenes: chaining AnimationPlayers

Cutscenes longer than ~30 seconds should be split across multiple AnimationPlayer animations (or nodes) to keep track counts manageable. Chain them with signals:

```gdscript
func _play_sequence(animations: Array[String]) -> void:
    for anim in animations:
        anim_player.play(anim)
        await anim_player.animation_finished

func start_intro_cutscene() -> void:
    await _play_sequence(["intro_part1", "intro_part2", "intro_part3"])
    _finish_cutscene()
```

## 2D cutscenes with Camera2D

The same pattern applies in 2D. Use `Camera2D.make_current()` for the cutscene camera. Use `RemoteTransform2D` to drive camera position from an animated Path2D:

```gdscript
# Cutscene camera follows a Path2D
@onready var path_follow := $CameraPath/PathFollow2D
@onready var remote := $CameraPath/PathFollow2D/RemoteTransform2D

func _ready() -> void:
    remote.remote_path = $CutsceneCamera.get_path()

# AnimationPlayer animates path_follow.progress (0.0 → 1.0) to move camera along path
```

## Blend-in/blend-out transitions

Don't cut hard into a cutscene. Fade out, switch camera, fade in:

```gdscript
func play_with_fade(anim_name: String) -> void:
    var tween := create_tween()
    tween.tween_property($FadeRect, "modulate:a", 1.0, 0.3)
    await tween.finished
    cutscene_camera.make_current()
    tween.tween_property($FadeRect, "modulate:a", 0.0, 0.3)
    await tween.finished
    anim_player.play(anim_name)

func _finish_cutscene() -> void:
    var tween := create_tween()
    tween.tween_property($FadeRect, "modulate:a", 1.0, 0.3)
    await tween.finished
    player_camera.make_current()
    tween.tween_property($FadeRect, "modulate:a", 0.0, 0.3)
    cutscene_finished.emit()
```

`$FadeRect` is a full-screen ColorRect (black) on a CanvasLayer above the game.
