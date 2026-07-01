# Combo Systems and Frame Data

Melee combat feels tight or sloppy based almost entirely on how the input buffer and animation events are wired. Generated code defaults to `Input.is_action_just_pressed()` checked every frame and a boolean `attacking` flag — that approach produces phantom inputs, eaten inputs, and combo windows that only work if the player times button presses with sub-frame precision. This file describes the data-driven alternative used in commercial action games.

## Contents
- Input buffer: why and how
- Combo state machine and data resources
- Cancel windows
- Hit detection via animation call tracks
- Hitstun, hitstop, and frame data
- Launchers and juggles
- Input priority ordering
- Complete GDScript example
- Common mistakes

## Input buffer: why and how

The input buffer stores recent inputs so the game can "remember" a press that arrived slightly early — during an attack's recovery frames — and execute it at the first legal moment. Without a buffer, the timing window for chaining attacks is measured in single frames (16 ms) and most players miss it. With a buffer of 120 ms, the window feels responsive without being automatic.

**Never use a boolean flag.** `attacking = true` gives you no timestamp and no way to match an input against a time window. You cannot tell whether the stored press is from 5 ms ago or 300 ms ago, so you cannot decide whether to honor it.

**Use a circular array of (action_name, timestamp) pairs.** On each confirmed press, append to the buffer. To consume a matching input, scan from oldest to newest, find the first entry with `action == desired_action` and `Time.get_ticks_msec() - timestamp < BUFFER_WINDOW_MS`, remove it, and return `true`. If none match, return `false`.

```gdscript
const BUFFER_WINDOW_MS := 120   # 0.12 s; tune per-game (60-150 ms range)
const BUFFER_MAX_SIZE  := 8

class InputBuffer:
    var _entries: Array = []    # each entry: [action: StringName, time_ms: int]

    func push(action: StringName) -> void:
        _entries.append([action, Time.get_ticks_msec()])
        if _entries.size() > BUFFER_MAX_SIZE:
            _entries.pop_front()

    # Returns true and removes the entry if a recent matching input exists.
    func consume(action: StringName) -> bool:
        var now := Time.get_ticks_msec()
        for i in _entries.size():
            var entry = _entries[i]
            if entry[0] == action and now - entry[1] <= BUFFER_WINDOW_MS:
                _entries.remove_at(i)
                return true
        return false

    func flush() -> void:
        _entries.clear()
```

Call `push()` inside `_unhandled_input()` (not `_process()`) so each physical key-down generates exactly one entry, even if the frame rate is high. Call `consume()` from the cancel window checker every fixed step.

## Combo state machine and data resources

Define each step of a combo as a Resource so designers can author combos in the Inspector without touching code.

```gdscript
# combo_step_data.gd
class_name ComboStepData extends Resource

@export var animation: StringName = &"light_1"
@export var damage: int = 10
## Normalized 0-1 positions within the animation where hitbox is live.
@export var hit_start: float = 0.2
@export var hit_end:   float = 0.45
## Normalized window during which the player can cancel into the next step.
@export var cancel_start: float = 0.35
@export var cancel_end:   float = 0.75
## Maps input action names to the next ComboStepData index.
## Key: StringName (e.g. &"light"), Value: int (index in parent ComboData.steps)
@export var next_inputs: Dictionary = {}
```

```gdscript
# combo_data.gd
class_name ComboData extends Resource

@export var combo_name: String = "Light Chain"
@export var steps: Array[ComboStepData] = []
```

The state machine index into `steps[]` is the only runtime state needed for a simple chain. More complex systems layer multiple `ComboData` resources (light combos, heavy combos, aerial combos) and select among them based on air/ground state before consulting `next_inputs`.

## Cancel windows

A cancel window is the portion of an attack animation during which the player can cancel into the next attack (or a dodge/block). Outside the window the current attack is "committed" — this is what gives combat weight. Inside the window, the move can be interrupted.

Implement cancel windows against the AnimationPlayer's current playback position:

```gdscript
func _physics_process(delta: float) -> void:
    if _current_step == null:
        return
    var t: float = _anim.current_animation_position / _anim.current_animation_length
    if t >= _current_step.cancel_start and t <= _current_step.cancel_end:
        _check_cancel()

func _check_cancel() -> void:
    # Priority: dodge/block > next combo step > new combo start
    if _input_buffer.consume(&"dodge"):
        _enter_dodge()
        return
    if _input_buffer.consume(&"block"):
        _enter_block()
        return
    for action in _current_step.next_inputs:
        if _input_buffer.consume(action):
            var next_idx: int = _current_step.next_inputs[action]
            _enter_step(next_idx)
            return
```

The cancel does NOT require the player to release the button first. Most action games (Devil May Cry, God of War, Bayonetta) allow immediate cancel to any valid next action the moment the window opens.

When the animation finishes outside a cancel window or no cancel was consumed, return to idle and flush the buffer.

## Hit detection via animation call tracks

Do not check hitbox overlap in `_process()`. Doing so can trigger damage on startup frames (before the swing) and recovery frames (after it), producing unfair hits and making the damage timing invisible to designers.

Instead, use AnimationPlayer's **Call Method track**:

1. Create an `Area2D` (or `Area3D`) child named `Hitbox` on the character. Keep it disabled (`monitoring = false`) by default.
2. In the AnimationPlayer, add a **Call Method** track on the character node.
3. At the `hit_start` keyframe, insert a call to `enable_hitbox()`.
4. At the `hit_end` keyframe, insert a call to `disable_hitbox()`.

```gdscript
func enable_hitbox() -> void:
    $Hitbox.monitoring = true

func disable_hitbox() -> void:
    $Hitbox.monitoring = false

func _on_hitbox_area_entered(area: Area2D) -> void:
    if area.is_in_group(&"hurtbox"):
        var target := area.get_parent()
        if target.has_method(&"take_damage"):
            target.take_damage(_current_step.damage, self)
            _apply_hitstop()
```

This approach ties hit window precisely to the visual swing, is visible in the AnimationPlayer timeline, and requires zero manual frame-counting code.

For data-driven hit detection without hand-keyframing every animation, compute `hit_start` and `hit_end` from `ComboStepData` at animation start:

```gdscript
func _enter_step(idx: int) -> void:
    _current_step = _current_combo.steps[idx]
    _anim.play(_current_step.animation)
    var length: float = _anim.get_animation(_current_step.animation).length
    # Schedule enable/disable via a one-shot timer pair.
    _hitbox_enable_timer.start(_current_step.hit_start  * length)
    _hitbox_disable_timer.start(_current_step.hit_end   * length)
```

Use whichever approach is easier to maintain on your project — call tracks are more explicit; timer offsets are more data-driven.

## Hitstun, hitstop, and frame data

**Hitstop** is the brief freeze both attacker and defender experience on a successful hit. It sells impact. Without it, hits feel like swinging through air.

```gdscript
const HITSTOP_DURATION := 0.06   # seconds; 3-4 frames at 60 fps

func _apply_hitstop() -> void:
    # Pause the animation player; unpause after hitstop_duration.
    _anim.speed_scale = 0.0
    await get_tree().create_timer(HITSTOP_DURATION, false).timeout
    _anim.speed_scale = 1.0
```

Avoid `Engine.time_scale` for hitstop — it affects the entire game including UI timers and audio. Pause only the attacker's AnimationPlayer (and optionally the defender's).

**Hitstun** prevents the defender from acting for a fixed number of frames after being hit. Implement it as a state in the defender's state machine:

```gdscript
# On the defender, called from take_damage()
func enter_hitstun(duration_frames: int) -> void:
    _state = State.HITSTUN
    _hitstun_frames_remaining = duration_frames

func _physics_process(delta: float) -> void:
    if _state == State.HITSTUN:
        _hitstun_frames_remaining -= 1
        if _hitstun_frames_remaining <= 0:
            _state = State.IDLE
        return   # block all other input processing
```

**Frame data vocabulary:**
- **Startup frames** — frames from input to first active hitbox frame. Lower startup = faster attack.
- **Active frames** — frames the hitbox is live (hit detection window).
- **Recovery frames** — frames after the last active frame until the character is controllable again.
- **Advantage on hit/block** — (attacker's recovery) minus (defender's hitstun). Positive = attacker can act first.

Store these as integers on `ComboStepData` if you need frame-data-accurate design; derive the normalized floats from `frame / total_frames` when building animations.

## Launchers and juggles

A launcher sends the enemy airborne, enabling aerial combos. The key rules:

1. Apply an upward velocity impulse to the defender's `CharacterBody2D`/`RigidBody2D` on hit.
2. Track `juggle_count` on the defender — incremented each time they're hit while airborne. When `juggle_count >= max_juggle_count`, the defender becomes immune to further launches (they tumble to the ground instead). This prevents infinite air combos.
3. On the attacker side, lock camera follow upward during an aerial combo so the action stays on screen.

```gdscript
# On the defender
var juggle_count: int = 0
const MAX_JUGGLE := 5

func take_damage(damage: int, attacker: Node, is_launcher: bool = false) -> void:
    hp -= damage
    if is_launcher and not _is_grounded():
        if juggle_count < MAX_JUGGLE:
            juggle_count += 1
            velocity.y = -600.0   # launch impulse
        # else: apply ground-slam effect instead
    elif _is_grounded():
        juggle_count = 0          # reset on landing
```

## Input priority ordering

When multiple actions are buffered simultaneously, check in this order inside `_check_cancel()`:

1. **Dodge / roll** — highest priority; preserves defensive options.
2. **Block** — defensive priority after dodge.
3. **Combo cancel** — next step in the current combo chain.
4. **New combo start** — begin a different combo from idle if no chain exists.

This ordering means players can always escape a committed attack into a dodge if the cancel window is open, which makes combat feel fair rather than sticky.

## Complete GDScript example

```gdscript
# combo_controller.gd — attach to the player character node.
class_name ComboController extends Node

signal hit_landed(step: ComboStepData, target: Node)

@export var combo_data: ComboData          # assign in Inspector
@export var anim_player: AnimationPlayer

var _buffer   := InputBuffer.new()
var _step_idx := -1                        # -1 = idle
var _in_cancel_window := false

@onready var _hitbox: Area2D = get_parent().get_node("Hitbox")
@onready var _hitbox_enable_timer  := Timer.new()
@onready var _hitbox_disable_timer := Timer.new()

func _ready() -> void:
    add_child(_hitbox_enable_timer)
    add_child(_hitbox_disable_timer)
    _hitbox_enable_timer.one_shot  = true
    _hitbox_disable_timer.one_shot = true
    _hitbox_enable_timer.timeout.connect(_on_hitbox_enable_timeout)
    _hitbox_disable_timer.timeout.connect(_on_hitbox_disable_timeout)
    _hitbox.monitoring = false
    _hitbox.area_entered.connect(_on_hitbox_area_entered)
    anim_player.animation_finished.connect(_on_anim_finished)

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed(&"light"):  _buffer.push(&"light")
    if event.is_action_pressed(&"heavy"):  _buffer.push(&"heavy")
    if event.is_action_pressed(&"dodge"):  _buffer.push(&"dodge")
    if event.is_action_pressed(&"block"):  _buffer.push(&"block")

func _physics_process(_delta: float) -> void:
    if _step_idx == -1:
        # Idle — try to start a combo.
        if _buffer.consume(&"light"):
            _enter_step(0)
        elif _buffer.consume(&"heavy"):
            _enter_step(1)   # assumes heavy is step index 1 in combo_data
        return

    var step := combo_data.steps[_step_idx]
    var t    := anim_player.current_animation_position / anim_player.current_animation_length
    _in_cancel_window = (t >= step.cancel_start and t <= step.cancel_end)
    if _in_cancel_window:
        _try_cancel(step)

func _try_cancel(step: ComboStepData) -> void:
    if _buffer.consume(&"dodge"):
        _enter_idle()
        get_parent().enter_dodge()
        return
    if _buffer.consume(&"block"):
        _enter_idle()
        get_parent().enter_block()
        return
    for action: StringName in step.next_inputs:
        if _buffer.consume(action):
            _enter_step(step.next_inputs[action])
            return

func _enter_step(idx: int) -> void:
    _step_idx = idx
    var step  := combo_data.steps[idx]
    anim_player.play(step.animation)
    var length := anim_player.get_animation(step.animation).length
    _hitbox_enable_timer.start(step.hit_start * length)
    _hitbox_disable_timer.start(step.hit_end  * length)

func _enter_idle() -> void:
    _step_idx = -1
    _hitbox.monitoring = false
    _hitbox_enable_timer.stop()
    _hitbox_disable_timer.stop()
    _buffer.flush()

func _on_anim_finished(_anim_name: StringName) -> void:
    _enter_idle()
    anim_player.play(&"idle")

func _on_hitbox_enable_timeout()  -> void: _hitbox.monitoring = true
func _on_hitbox_disable_timeout() -> void: _hitbox.monitoring = false

func _on_hitbox_area_entered(area: Area2D) -> void:
    if not area.is_in_group(&"hurtbox"):
        return
    var target := area.get_parent()
    var step   := combo_data.steps[_step_idx]
    if target.has_method(&"take_damage"):
        target.take_damage(step.damage, get_parent())
        hit_landed.emit(step, target)
        _apply_hitstop()

func _apply_hitstop() -> void:
    anim_player.speed_scale = 0.0
    await get_tree().create_timer(0.06, false).timeout
    if is_instance_valid(self):
        anim_player.speed_scale = 1.0
```

## Common mistakes

**`Input.is_action_pressed()` for combo detection** — this is `true` every frame the button is held, so the buffer fills with dozens of copies of the same input. Use `is_action_just_pressed()` in `_unhandled_input()` only.

**Hardcoded if/elif chains** — sequences like `if state == LIGHT_1 and just_pressed_heavy: state = HEAVY_FINISH` become unmanageable past 3-4 steps and are impossible for non-programmers to tune. Use `ComboStepData.next_inputs` (data-driven).

**Hit detection in `_process()`** — calling `_hitbox.get_overlapping_areas()` every frame means the hitbox fires on startup and recovery frames. The animation call track approach ties damage to the exact visual swing.

**Forgetting to disable the hitbox on cancel** — if the player cancels mid-active-frames, `disable_hitbox()` must be called immediately, not awaited. Stop the disable timer and call directly in `_enter_idle()`.

**No juggle limit** — without `max_juggle_count`, a player with a fast aerial can loop an enemy indefinitely. Always track and cap juggle count on the defender.
