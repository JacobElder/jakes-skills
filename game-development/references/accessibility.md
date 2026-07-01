# Game Accessibility

Accessibility is not a feature you bolt on at the end. The players you lock out by ignoring it are real: roughly 8% of men have some form of color vision deficiency, ~15% of the global population lives with a disability affecting gaming (motor, visual, auditory, cognitive). Accessibility settings don't make your game easier — they keep players in it. A game nobody can finish is a bad game, regardless of how clever its mechanics are.

## Contents
- Colorblind modes and the Daltonize shader
- Color design rules
- Subtitle system
- Control remapping
- Text size scaling
- Screen reader and audio descriptions
- Motion sickness reduction
- Difficulty accessibility
- Settings persistence

## Colorblind modes and the Daltonize shader

There are three main types of red-green and blue color vision deficiencies:

- **Protanopia** — red-weak; reds appear dark/black; red and green are confused
- **Deuteranopia** — green-weak; most common; green appears desaturated; red-green confusion
- **Tritanopia** — blue-weak; blue and yellow are confused; rarer (~0.003% of population)

Never convey critical information by color alone. That is the rule. Everything else in this section is how to make it easier, but the rule is prior: if a player must distinguish "red health bar = danger, green = safe" and they have deuteranopia, your game has a hardcoded failure mode. Always pair color with a secondary signal: shape, icon, pattern, or text label.

The Daltonize correction approach transforms the RGB of the entire screen through a 3×3 correction matrix per deficiency type. Implement this as a `CanvasLayer` at a very high layer (128+) containing a full-screen `ColorRect` with a `canvas_item` shader:

```gdscript
# res://autoloads/ColorblindManager.gd
extends Node

enum Mode { NONE, PROTANOPIA, DEUTERANOPIA, TRITANOPIA }

var _layer: CanvasLayer
var _rect: ColorRect
var _shader: Shader = preload("res://shaders/colorblind_correct.gdshader")
var _material: ShaderMaterial

func _ready() -> void:
    _layer = CanvasLayer.new()
    _layer.layer = 128
    add_child(_layer)

    _rect = ColorRect.new()
    _rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _rect.anchor_right = 1.0
    _rect.anchor_bottom = 1.0
    _material = ShaderMaterial.new()
    _material.shader = _shader
    _rect.material = _material
    _layer.add_child(_rect)

    set_mode(Mode.NONE)

func set_mode(mode: Mode) -> void:
    match mode:
        Mode.NONE:
            _rect.visible = false
        Mode.PROTANOPIA:
            _rect.visible = true
            _material.set_shader_parameter("mode", 1)
        Mode.DEUTERANOPIA:
            _rect.visible = true
            _material.set_shader_parameter("mode", 2)
        Mode.TRITANOPIA:
            _rect.visible = true
            _material.set_shader_parameter("mode", 3)
```

The shader samples the screen texture, applies the matrix, and blends it back. Use `hint_screen_texture` to grab the composited frame:

```glsl
// res://shaders/colorblind_correct.gdshader
shader_type canvas_item;

uniform int mode = 0;
uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear_mipmap;

// Daltonize correction matrices (LMS-space simulation → RGB correction)
// These shift problematic channels toward ones the user can see.

// Protanopia: shift red channel toward green+blue
const mat3 PROTANOPIA_MAT = mat3(
    vec3(0.56667, 0.55833, 0.0),
    vec3(0.43333, 0.44167, 0.24167),
    vec3(0.0,     0.0,     0.75833)
);

// Deuteranopia: shift green channel toward red+blue
const mat3 DEUTERANOPIA_MAT = mat3(
    vec3(0.625,   0.70,    0.0),
    vec3(0.375,   0.30,    0.30),
    vec3(0.0,     0.0,     0.70)
);

// Tritanopia: shift blue channel toward red+green
const mat3 TRITANOPIA_MAT = mat3(
    vec3(0.95,    0.0,     0.0),
    vec3(0.05,    0.43333, 0.475),
    vec3(0.0,     0.56667, 0.525)
);

void fragment() {
    vec4 screen_color = texture(SCREEN_TEXTURE, SCREEN_UV);
    vec3 rgb = screen_color.rgb;

    if (mode == 1) {
        rgb = PROTANOPIA_MAT * rgb;
    } else if (mode == 2) {
        rgb = DEUTERANOPIA_MAT * rgb;
    } else if (mode == 3) {
        rgb = TRITANOPIA_MAT * rgb;
    }

    COLOR = vec4(rgb, screen_color.a);
}
```

Show a preview swatch in your options menu that renders a small test image (a color wheel or your HUD palette sample) through the same shader — players cannot judge whether a mode helps without seeing it applied.

## Color design rules

The red/green pair is the single most common failure point. Red enemies on a green background, a red "danger" indicator vs. a green "safe" indicator — these are the exact combinations that deuteranopia makes indistinguishable. Use them sparingly and never alone as the primary signal.

Palette substitutions that work for most deficiencies:
- Blue and orange: high contrast for all three deficiency types
- Purple and yellow: works for protanopia and deuteranopia; test against tritanopia
- Adding brightness contrast (light vs. dark) in addition to hue contrast is the safest universal approach

Concrete rules for common elements:

**Health bars.** Never just a color gradient from red to green. Acceptable: color + numeric value + an icon (heart/shield) that changes at thresholds. Even better: a segmented bar where segments disappear rather than a continuous fill that changes color.

```gdscript
# HealthBar.gd — always show numeric alongside color
func update_health(current: int, maximum: int) -> void:
    var ratio := float(current) / float(maximum)
    fill_bar.value = ratio * 100.0
    # Color is a secondary reinforcement, not the sole signal
    if ratio > 0.5:
        fill_bar.modulate = Color.GREEN
    elif ratio > 0.25:
        fill_bar.modulate = Color.YELLOW
    else:
        fill_bar.modulate = Color.RED
    # Primary signals: number and icon
    numeric_label.text = "%d / %d" % [current, maximum]
    warning_icon.visible = ratio <= 0.25  # skull icon at low health
```

**Minimap enemy icons.** Shape-coded, not just colored dots. Triangles for aggressive enemies, circles for passive, squares for bosses. Color can reinforce but must not be the only differentiator.

**Puzzle elements.** If a color-matching puzzle requires distinguishing red from green (e.g., wiring puzzles, sorting), add labels, symbols, or patterns. Wire puzzles: label each wire with a letter or number.

**Status effects.** Poison: a skull or drip icon, not just green. Fire: a flame icon, not just orange. Freeze: a snowflake icon. Color is accent, icon is signal.

## Subtitle system

Subtitles are for deaf and hard-of-hearing players, players in noisy environments, players in a language they are still learning, and players who simply prefer reading. They cost very little to implement correctly and the value-add is enormous.

The `SubtitleManager` is an autoload, always present, operating on a `CanvasLayer` at layer 128 (same as the colorblind layer — give it a higher sublayer or use layer 129 to render on top):

```gdscript
# res://autoloads/SubtitleManager.gd
extends Node

signal subtitle_started(text: String)
signal subtitle_ended

const LAYER := 129
const DEFAULT_DURATION := 4.0

var text_size_scale: float = 1.0
var background_opacity: float = 0.6
var subtitles_enabled: bool = true

var _layer: CanvasLayer
var _panel: Panel
var _label: Label
var _timer: Timer
var _queue: Array[Dictionary] = []
var _showing: bool = false

func _ready() -> void:
    _layer = CanvasLayer.new()
    _layer.layer = LAYER
    add_child(_layer)

    _panel = Panel.new()
    _panel.anchor_left = 0.1
    _panel.anchor_right = 0.9
    _panel.anchor_top = 0.82
    _panel.anchor_bottom = 0.95
    _panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _layer.add_child(_panel)

    _label = Label.new()
    _label.anchor_right = 1.0
    _label.anchor_bottom = 1.0
    _label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    _label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    _panel.add_child(_label)

    _timer = Timer.new()
    _timer.one_shot = true
    _timer.timeout.connect(_on_timer_timeout)
    add_child(_timer)

    _panel.visible = false
    _apply_settings()

func show_subtitle(text: String, speaker: String = "", duration: float = DEFAULT_DURATION) -> void:
    if not subtitles_enabled:
        return
    var entry := {"text": text, "speaker": speaker, "duration": duration}
    if _showing:
        _queue.append(entry)
    else:
        _display(entry)

func _display(entry: Dictionary) -> void:
    _showing = true
    var display_text := entry.text
    if entry.speaker != "":
        display_text = "[b]%s:[/b] %s" % [entry.speaker, entry.text]
    _label.text = display_text
    _panel.visible = true
    _timer.start(entry.duration)
    subtitle_started.emit(entry.text)

func _on_timer_timeout() -> void:
    if _queue.is_empty():
        _panel.visible = false
        _showing = false
        subtitle_ended.emit()
    else:
        _display(_queue.pop_front())

func _apply_settings() -> void:
    var base_size := 16
    _label.add_theme_font_size_override("font_size", int(base_size * text_size_scale))
    var panel_style := _panel.get_theme_stylebox("panel").duplicate()
    if panel_style is StyleBoxFlat:
        var c := panel_style.bg_color
        c.a = background_opacity
        panel_style.bg_color = c
        _panel.add_theme_stylebox_override("panel", panel_style)

func apply_settings(scale: float, opacity: float, enabled: bool) -> void:
    text_size_scale = scale
    background_opacity = opacity
    subtitles_enabled = enabled
    _apply_settings()
```

Position subtitles at the bottom third of the screen (anchors 0.82–0.95 vertically), never center-screen where they overlap gameplay. Speaker name prefixed in bold: `"Guard: Hey, stop!"`. When lines overlap (fast-paced dialogue), queue them and auto-play sequentially.

Fire subtitles from wherever sound/dialogue originates:

```gdscript
# In your DialogueManager or SoundManager:
func play_dialogue(line: DialogueLine) -> void:
    audio_player.stream = line.audio_clip
    audio_player.play()
    SubtitleManager.show_subtitle(line.text, line.speaker, line.audio_clip.get_length() + 0.5)
```

## Control remapping

Hardcoded controls are an accessibility failure. Motor disabilities, left-handed players, and personal preference all require remapping. In Godot 4, InputMap holds all actions and can be modified at runtime:

```gdscript
# res://autoloads/ControlsManager.gd
extends Node

const SAVE_PATH := "user://controls.json"

# Call this after the user assigns a new key in the UI
func remap_action(action_name: String, new_event: InputEvent) -> bool:
    # Check for conflicts before accepting
    var conflict := _find_conflict(action_name, new_event)
    if conflict != "":
        push_warning("Key conflict with action: %s" % conflict)
        return false  # Caller must warn the user

    InputMap.action_erase_events(action_name)
    InputMap.action_add_event(action_name, new_event)
    save_bindings()
    return true

func _find_conflict(action_name: String, event: InputEvent) -> String:
    for action in InputMap.get_actions():
        if action == action_name:
            continue
        for existing_event in InputMap.action_get_events(action):
            if existing_event.is_match(event):
                return action
    return ""

func save_bindings() -> void:
    var data := {}
    for action in InputMap.get_actions():
        var events := []
        for event in InputMap.action_get_events(action):
            if event is InputEventKey:
                events.append({"type": "key", "keycode": event.keycode, "physical": event.physical_keycode})
            elif event is InputEventMouseButton:
                events.append({"type": "mouse_button", "button_index": event.button_index})
            elif event is InputEventJoypadButton:
                events.append({"type": "joypad_button", "button_index": event.button_index})
        if not events.is_empty():
            data[action] = events
    var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    file.store_string(JSON.stringify(data))

func load_bindings() -> void:
    if not FileAccess.file_exists(SAVE_PATH):
        return
    var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    var data: Dictionary = JSON.parse_string(file.get_as_text())
    for action in data:
        if not InputMap.has_action(action):
            continue
        InputMap.action_erase_events(action)
        for event_data in data[action]:
            var event: InputEvent
            match event_data.type:
                "key":
                    var key_event := InputEventKey.new()
                    key_event.keycode = event_data.keycode
                    event = key_event
                "mouse_button":
                    var mouse_event := InputEventMouseButton.new()
                    mouse_event.button_index = event_data.button_index
                    event = mouse_event
                "joypad_button":
                    var joy_event := InputEventJoypadButton.new()
                    joy_event.button_index = event_data.button_index
                    event = joy_event
            if event:
                InputMap.action_add_event(action, event)
```

In the UI, never display "Press E to interact" — display the current binding dynamically:

```gdscript
func _update_prompt_label() -> void:
    var events := InputMap.action_get_events("interact")
    if events.is_empty():
        prompt_label.text = "Interact (unbound)"
        return
    var event := events[0]
    prompt_label.text = "Press %s to interact" % event.as_text()
```

Never silently overwrite a conflicting binding. Show a modal: "This key is already used for [Jump]. Reassign anyway?" with Reassign / Cancel options.

## Text size scaling

Fixed font sizes exclude players with low vision and players on small screens. Provide a text_size_scale option (0.75, 1.0, 1.25, 1.5 are reasonable steps) and apply it globally via the project's Theme resource:

```gdscript
# res://autoloads/UIManager.gd
extends Node

const SAVE_PATH := "user://accessibility.json"
const BASE_FONT_SIZE := 16

var text_size_scale: float = 1.0

func set_text_size_scale(scale: float) -> void:
    text_size_scale = scale
    _apply_font_scale()

func _apply_font_scale() -> void:
    var theme := ThemeDB.get_project_theme()
    if theme == null:
        return
    var new_size := int(BASE_FONT_SIZE * text_size_scale)
    theme.default_font_size = new_size
    # Also update named font sizes in the theme if you use them
    for type in ["Label", "Button", "LineEdit", "RichTextLabel"]:
        if theme.has_font_size("font_size", type):
            theme.set_font_size("font_size", type, new_size)
```

Every `Label` in your game must have `autowrap_mode` set — never fixed-width text boxes that clip when the font scale goes up. Use `SIZE_SHRINK_BEGIN` or `FIT_CONTENT` on containers rather than fixed pixel sizes. Test at 1.5× scale: if any text clips, truncates without ellipsis, or overflows its container, fix the layout.

## Screen reader and audio descriptions

For menu-driven and narrative-heavy games, players who are blind or have very low vision depend on OS text-to-speech. Godot 4 exposes `DisplayServer.tts_speak()`:

```gdscript
# res://autoloads/ScreenReaderManager.gd
extends Node

var enabled: bool = false

func speak(text: String, interrupt: bool = true) -> void:
    if not enabled:
        return
    if interrupt:
        DisplayServer.tts_stop()
    DisplayServer.tts_speak(text, DisplayServer.tts_get_voices_for_language("en")[0])

# Wire this to the focus_entered signal of every interactive Control
func _on_control_focused(control: Control) -> void:
    var description := control.get_meta("tts_description", control.name)
    speak(description)
```

Set `tts_description` metadata on every interactive node:

```gdscript
# In your scene setup or _ready():
play_button.set_meta("tts_description", "Play button. Press to start a new game.")
save_slot_1.set_meta("tts_description", "Save slot 1. Level 3, 2 hours 14 minutes playtime.")
```

For 3D games and interactive objects, describe them on inspection:

```gdscript
func _on_player_inspect(object: Node) -> void:
    var desc := object.get_meta("inspect_description", "Unknown object.")
    ScreenReaderManager.speak(desc)
```

`DisplayServer.tts_speak()` uses OS voices — quality varies by platform. It is not perfect. It is vastly better than nothing.

## Motion sickness reduction

Screen shake, chromatic aberration, vignettes, heavy post-processing, and fast FOV changes trigger motion sickness in a subset of players. Provide opt-outs for all of them:

```gdscript
# res://autoloads/AccessibilitySettings.gd
extends Node

var camera_shake_multiplier: float = 1.0  # 0.0 = off
var reduce_screen_effects: bool = false    # chromatic ab, vignette
var fov_3d: float = 75.0                   # 60–110 is typical range

func apply_to_camera(camera: Camera2D) -> void:
    # Called by camera shake routines before applying trauma
    # camera_shake_multiplier = 0.0 means skip shake entirely
    pass
```

In your camera shake implementation:

```gdscript
# CameraShaker.gd
func add_trauma(amount: float) -> void:
    var effective := amount * AccessibilitySettings.camera_shake_multiplier
    trauma = min(trauma + effective, 1.0)
```

For post-process effects, check the setting before activating:

```gdscript
func _apply_post_process() -> void:
    chromatic_aberration.visible = not AccessibilitySettings.reduce_screen_effects
    vignette_overlay.visible = not AccessibilitySettings.reduce_screen_effects
```

For 3D, expose a FOV slider in settings. Rapid FOV changes (zoom effects, sprinting FOV kick) should also respect a `reduce_motion` flag — skip the tween and cut directly.

Constant camera velocity is important: avoid sudden acceleration/deceleration in camera movement. Ease-in/ease-out on target following is fine. Instant jumps in camera velocity (not position — velocity) are the trigger.

## Difficulty accessibility

Separate "narrative access" from "challenge." Offer assist modes (player invincibility, slow-motion, reduced enemy aggression) without framing them as "easy mode" — that label discourages players who need them. The framing that works: "Accessibility Options" as a top-level section, not a difficulty level.

```gdscript
# res://autoloads/AssistMode.gd
extends Node

var invincible: bool = false
var time_scale: float = 1.0          # 0.5 = half speed
var enemy_aggression: float = 1.0    # 0.0 = enemies stop attacking

func _ready() -> void:
    # Apply time_scale globally
    Engine.time_scale = time_scale

func set_time_scale(scale: float) -> void:
    time_scale = scale
    Engine.time_scale = scale

# In your enemy AI's attack decision:
# if randf() > AssistMode.enemy_aggression: skip attack
```

Invincibility is applied in the damage system:

```gdscript
func take_damage(amount: int) -> void:
    if AssistMode.invincible:
        return
    health -= amount
    health_changed.emit(health)
```

The philosophy: the goal is more players finishing and enjoying your game. A player using invincibility is a player who is playing your game, seeing your art, and hearing your music — not a player who quit at hour two.

## Settings persistence

All accessibility settings save to `user://accessibility.json`. Load before the main menu renders — not on main menu ready, before it. Apply immediately on change with no "restart required" for any setting covered here.

```gdscript
# res://autoloads/AccessibilitySettings.gd (extended)
extends Node

const SAVE_PATH := "user://accessibility.json"

var colorblind_mode: int = 0
var subtitles_enabled: bool = true
var subtitle_text_scale: float = 1.0
var subtitle_background_opacity: float = 0.6
var text_size_scale: float = 1.0
var camera_shake_multiplier: float = 1.0
var reduce_screen_effects: bool = false
var fov_3d: float = 75.0
var invincible: bool = false
var time_scale: float = 1.0
var screen_reader_enabled: bool = false

func load_settings() -> void:
    if not FileAccess.file_exists(SAVE_PATH):
        return
    var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    var data: Dictionary = JSON.parse_string(file.get_as_text())
    colorblind_mode = data.get("colorblind_mode", 0)
    subtitles_enabled = data.get("subtitles_enabled", true)
    subtitle_text_scale = data.get("subtitle_text_scale", 1.0)
    subtitle_background_opacity = data.get("subtitle_background_opacity", 0.6)
    text_size_scale = data.get("text_size_scale", 1.0)
    camera_shake_multiplier = data.get("camera_shake_multiplier", 1.0)
    reduce_screen_effects = data.get("reduce_screen_effects", false)
    fov_3d = data.get("fov_3d", 75.0)
    invincible = data.get("invincible", false)
    time_scale = data.get("time_scale", 1.0)
    screen_reader_enabled = data.get("screen_reader_enabled", false)
    _apply_all()

func save_settings() -> void:
    var data := {
        "colorblind_mode": colorblind_mode,
        "subtitles_enabled": subtitles_enabled,
        "subtitle_text_scale": subtitle_text_scale,
        "subtitle_background_opacity": subtitle_background_opacity,
        "text_size_scale": text_size_scale,
        "camera_shake_multiplier": camera_shake_multiplier,
        "reduce_screen_effects": reduce_screen_effects,
        "fov_3d": fov_3d,
        "invincible": invincible,
        "time_scale": time_scale,
        "screen_reader_enabled": screen_reader_enabled,
    }
    var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    file.store_string(JSON.stringify(data))

func _apply_all() -> void:
    ColorblindManager.set_mode(colorblind_mode)
    SubtitleManager.apply_settings(subtitle_text_scale, subtitle_background_opacity, subtitles_enabled)
    UIManager.set_text_size_scale(text_size_scale)
    ScreenReaderManager.enabled = screen_reader_enabled
    Engine.time_scale = time_scale
```

Call `AccessibilitySettings.load_settings()` from `_ready()` of your earliest autoload, before any scene is visible. Expose all of these in a dedicated **Accessibility** section in your options menu — not inside Gameplay or Audio. Players who need these settings need to find them immediately.
