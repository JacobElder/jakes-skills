# UI and HUD Systems

## The cardinal rule: HUD listens, game emits

The most common mistake in generated UI code: game logic calls into the UI directly.

```gdscript
# WRONG — player script reaches into the HUD
func take_damage(amount):
    hp -= amount
    get_node("/root/HUD/HealthBar").value = hp  # tight coupling, breaks on scene change
```

```gdscript
# RIGHT — player emits a signal; HUD listens
signal health_changed(new_hp: int, max_hp: int)

func take_damage(amount: int) -> void:
    hp = max(0, hp - amount)
    health_changed.emit(hp, max_hp)
```

```gdscript
# HUD script — connect in _ready or via editor
func _ready() -> void:
    player.health_changed.connect(_on_health_changed)

func _on_health_changed(new_hp: int, max_hp: int) -> void:
    var tween := create_tween()
    tween.tween_property(health_bar, "value", float(new_hp) / max_hp, 0.15)
```

Rules:
- Game logic never holds a reference to any HUD node.
- HUD never reads game state directly — it only responds to signals.
- Tween the bar, never set it instantly (instant snaps look cheap and miss hits).

## Control node tree structure

```
CanvasLayer (layer = 1, so it draws above the game)
  └─ HUD (Control, anchors = full_rect)
       ├─ TopBar (HBoxContainer, anchor top)
       │    ├─ HealthContainer (VBoxContainer)
       │    │    ├─ HealthLabel (Label)
       │    │    └─ HealthBar (TextureProgressBar or ProgressBar)
       │    └─ CurrencyLabel (Label)
       ├─ BossHealthBar (TextureProgressBar, anchor bottom, hidden by default)
       └─ DialogueBox (NinePatchRect, anchor bottom, hidden by default)
```

Put the HUD scene inside a CanvasLayer so it's immune to camera movement and zoom. Use `anchor_left = 0`, `anchor_right = 1` etc. (full_rect preset) on the root Control so it fills any window size.

## Health bar patterns

Use `TextureProgressBar` for custom art; `ProgressBar` for prototypes.

```gdscript
# Animate to new value; tween the ratio, not the pixel position
func set_health(current: int, maximum: int) -> void:
    var ratio := float(current) / float(maximum)
    var tw := create_tween()
    tw.tween_property(bar, "value", ratio * bar.max_value, 0.2).set_ease(Tween.EASE_OUT)
    # optional: flash red on damage
    if ratio < bar.value / bar.max_value:
        tw.parallel().tween_property(bar, "modulate", Color.RED, 0.05)
        tw.tween_property(bar, "modulate", Color.WHITE, 0.1)
```

For a "depleting ghost bar" effect (the white bar that lingers then drains):
```gdscript
@export var ghost_bar: ProgressBar  # second bar behind the main one, same size

func set_health(ratio: float) -> void:
    bar.value = ratio * bar.max_value
    await get_tree().create_timer(0.4).timeout
    var tw := create_tween()
    tw.tween_property(ghost_bar, "value", ratio * ghost_bar.max_value, 0.3)
```

## Scene transitions

Every scene change should fade through black — instant cuts feel like crashes.

```gdscript
# TransitionLayer.gd — autoload singleton
extends CanvasLayer

@onready var overlay: ColorRect = $ColorRect  # fill, black, alpha 0 initially

func fade_to_scene(path: String, duration: float = 0.4) -> void:
    var tw := create_tween()
    tw.tween_property(overlay, "modulate:a", 1.0, duration)
    await tw.finished
    get_tree().change_scene_to_file(path)
    tw = create_tween()
    tw.tween_property(overlay, "modulate:a", 0.0, duration)
```

```gdscript
# Anywhere in game code
TransitionLayer.fade_to_scene("res://scenes/level_2.tscn")
```

The `CanvasLayer` autoload renders above everything. Set its `layer` to a high number (128) so it's always on top.

## Pause menu

```gdscript
# PauseMenu.gd
extends Control

func _ready() -> void:
    hide()
    process_mode = Node.PROCESS_MODE_WHEN_PAUSED  # runs even while tree is paused

func toggle() -> void:
    get_tree().paused = !visible
    visible = !visible

func _on_resume_pressed() -> void:
    toggle()

func _on_quit_pressed() -> void:
    get_tree().quit()
```

```gdscript
# In the player or game controller
func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_just_pressed("pause"):
        pause_menu.toggle()
```

Key: `process_mode = WHEN_PAUSED` on the pause menu Control. Every other node defaults to `INHERIT`, which inherits the paused state. Buttons in the pause menu won't respond unless the menu itself is exempt from pausing.

## Typewriter dialogue effect

```gdscript
# DialogueBox.gd
extends NinePatchRect

@onready var label: RichTextLabel = $Label
@onready var timer: Timer = $Timer
@export var chars_per_second: float = 40.0

var _full_text: String = ""
var _char_index: int = 0

func display(text: String) -> void:
    _full_text = text
    _char_index = 0
    label.text = ""
    timer.wait_time = 1.0 / chars_per_second
    timer.start()

func _on_timer_timeout() -> void:
    if _char_index < _full_text.length():
        label.text += _full_text[_char_index]
        _char_index += 1
        # optional: vary speed on punctuation
        if _full_text[_char_index - 1] in [".", "!", "?"]:
            timer.wait_time = 0.25
        elif _full_text[_char_index - 1] == ",":
            timer.wait_time = 0.1
        else:
            timer.wait_time = 1.0 / chars_per_second
    else:
        timer.stop()
        # show "press to continue" indicator

func skip() -> void:
    timer.stop()
    label.text = _full_text
    _char_index = _full_text.length()
```

Use `RichTextLabel` instead of `Label` to support `[b]bold[/b]`, `[color=red]colored[/color]`, and `[wave]animated[/wave]` BBCode.

## Choice buttons

```gdscript
func show_choices(choices: Array[String]) -> void:
    for child in choice_container.get_children():
        child.queue_free()
    for i in choices.size():
        var btn := Button.new()
        btn.text = choices[i]
        btn.pressed.connect(_on_choice_selected.bind(i))
        choice_container.add_child(btn)
    choice_container.show()

func _on_choice_selected(index: int) -> void:
    choice_selected.emit(index)
    choice_container.hide()
```

## Screen shake (HUD-safe)

Put screenshake on a Camera2D offset, not on the viewport or CanvasLayer — otherwise the HUD shakes with the world.

```gdscript
func shake(trauma: float, duration: float) -> void:
    var tw := create_tween()
    var elapsed := 0.0
    while elapsed < duration:
        var t := trauma * (1.0 - elapsed / duration)
        offset = Vector2(
            randf_range(-1.0, 1.0) * t * 20.0,
            randf_range(-1.0, 1.0) * t * 20.0
        )
        elapsed += 0.05
        await get_tree().process_frame
    offset = Vector2.ZERO
```

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| `hud.health_bar.value = hp` from player | Tight coupling; breaks when HUD changes | Signal `health_changed` |
| `ProgressBar.value = hp` (instant) | Cheap snap; misses hits visually | Tween to new value |
| `get_tree().paused` with UI not exempted | Buttons don't respond when paused | `process_mode = WHEN_PAUSED` |
| Dialogue string arrays with index arithmetic | Unmaintainable branching | Data-driven graph (see dialogue reference) |
| Camera2D parented to player for screenshake | HUD shakes with camera | Shake `offset`, not position |
| UI in the main scene tree without CanvasLayer | UI moves with camera | Wrap in CanvasLayer |

## Unity equivalents

| Godot | Unity |
|---|---|
| `CanvasLayer` | `Canvas` with Screen Space - Overlay |
| `TextureProgressBar` | `Slider` or `Image.fillAmount` |
| `RichTextLabel` | `TextMeshPro` |
| `NinePatchRect` | `9-sliced Sprite` on a Panel |
| `Control.process_mode = WHEN_PAUSED` | `GameObject.SetActive(true)` after `Time.timeScale = 0` |
| Autoload `TransitionLayer` | `DontDestroyOnLoad` singleton |
