# Mobile and Touch Input (Godot 4)

Mobile games require a different input model than desktop. `InputEventScreenTouch` fires on finger down/up; `InputEventScreenDrag` fires while a finger moves. Neither maps to keyboard/mouse events — you cannot substitute `Input.is_action_pressed()` for touch without explicit action bindings.

## Contents
- InputEventScreenTouch and InputEventScreenDrag
- Virtual thumbstick implementation
- Dead zone and normalized delta
- Multi-touch tracking
- Gesture detection (pinch zoom, swipe)
- Adaptive UI layout for varied screen sizes
- Safe area insets (notch/cutout)
- Godot export settings for Android and iOS
- Mobile performance checklist

## InputEventScreenTouch and InputEventScreenDrag

```gdscript
func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed:
            _on_finger_down(event.index, event.position)
        else:
            _on_finger_up(event.index, event.position)
    elif event is InputEventScreenDrag:
        _on_finger_drag(event.index, event.position, event.relative)
```

`event.index` is the finger ID (0 = first finger, 1 = second, etc.). Track fingers by index for multi-touch. Do not assume `index == 0` is always the same finger — lift and re-press produces a new `index` from 0.

Enable multi-touch in **Project Settings → Input Devices → Pointing → Emulate Touch From Mouse** (for editor testing only — disable in production builds or it double-fires).

## Virtual thumbstick implementation

The thumbstick has a **center** (where the finger first touched) and a **knob** (tracks finger position within a max radius). Output is the normalized vector from center to knob.

```gdscript
# VirtualJoystick.gd — Control node, anchored bottom-left or bottom-right
extends Control

const MAX_RADIUS := 60.0    # pixels; visual extent of the stick
const DEAD_ZONE := 0.15     # ignore inputs below this magnitude (0–1)

var _active_finger: int = -1      # finger index currently driving this stick
var _origin: Vector2 = Vector2.ZERO
var _knob_offset: Vector2 = Vector2.ZERO

@onready var base: TextureRect = $Base
@onready var knob: TextureRect = $Knob

# The normalized input vector — read this from your player controller
var direction: Vector2:
    get:
        var raw := _knob_offset / MAX_RADIUS  # [-1, 1]
        if raw.length() < DEAD_ZONE:
            return Vector2.ZERO
        return raw.normalized() * ((raw.length() - DEAD_ZONE) / (1.0 - DEAD_ZONE))

func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed and _active_finger == -1:
            if _is_in_joystick_area(event.position):
                _active_finger = event.index
                _origin = event.position
                base.global_position = _origin - base.size / 2.0
                base.visible = true
        elif not event.pressed and event.index == _active_finger:
            _release()

    elif event is InputEventScreenDrag and event.index == _active_finger:
        _knob_offset = (event.position - _origin).limit_length(MAX_RADIUS)
        knob.global_position = _origin + _knob_offset - knob.size / 2.0

func _release() -> void:
    _active_finger = -1
    _knob_offset = Vector2.ZERO
    knob.global_position = _origin - knob.size / 2.0
    base.visible = false

func _is_in_joystick_area(pos: Vector2) -> bool:
    return get_global_rect().has_point(pos)
```

**In the player controller:**
```gdscript
@onready var joystick: VirtualJoystick = $CanvasLayer/LeftJoystick

func _physics_process(delta: float) -> void:
    var dir: Vector2 = joystick.direction
    # On desktop, fall back to keyboard
    if dir.is_zero_approx():
        dir = Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = dir * speed
    move_and_slide()
```

## Dead zone and normalized delta

Raw `_knob_offset / MAX_RADIUS` includes a dead zone where the stick rests at ~0 but not exactly 0 — produces drift and unwanted tiny movements. Apply dead zone elimination:

```gdscript
# Correct dead zone that re-maps the remaining range to [0, 1]:
static func apply_dead_zone(raw: Vector2, dead_zone: float) -> Vector2:
    var magnitude := raw.length()
    if magnitude < dead_zone:
        return Vector2.ZERO
    var normalized := raw / magnitude
    var adjusted := (magnitude - dead_zone) / (1.0 - dead_zone)
    return normalized * clamp(adjusted, 0.0, 1.0)
```

Never just check `if magnitude > dead_zone: return raw` — that produces a sudden jump from 0 to `dead_zone` magnitude when the threshold is crossed.

## Multi-touch tracking

```gdscript
# Track multiple fingers
var _touches: Dictionary = {}   # index → Vector2 (position)

func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed:
            _touches[event.index] = event.position
        else:
            _touches.erase(event.index)
    elif event is InputEventScreenDrag:
        _touches[event.index] = event.position
```

## Pinch-to-zoom gesture

```gdscript
var _prev_pinch_distance: float = 0.0

func _input(event: InputEvent) -> void:
    if event is InputEventScreenDrag and _touches.size() >= 2:
        var positions := _touches.values()
        var dist := positions[0].distance_to(positions[1])
        if _prev_pinch_distance > 0.0:
            var delta := dist - _prev_pinch_distance
            camera.zoom += Vector2.ONE * (delta * 0.002)
            camera.zoom = camera.zoom.clamp(Vector2(0.5, 0.5), Vector2(4.0, 4.0))
        _prev_pinch_distance = dist
    if event is InputEventScreenTouch and not event.pressed:
        _prev_pinch_distance = 0.0
```

## Adaptive UI layout for varied screen sizes

Mobile screens range from 375×667 (iPhone SE) to 430×932 (iPhone 14 Pro Max) to 2048×1536 (iPad). Fixed-pixel layouts break.

**Godot setup:**
- **Project Settings → Display → Window → Stretch Mode → `canvas_items`**
- **Stretch Aspect → `expand`** — letterboxes on unexpected ratios but never clips
- **Base resolution**: set to your design target (e.g. 1080×1920 portrait or 1920×1080 landscape)

**In UI scenes:**
```gdscript
# Anchor UI elements to screen edges, not pixel positions
# In the Inspector: Layout → Full Rect for panels that should fill screen
# Anchor presets: top-left, top-right, bottom-left, bottom-right for corner HUD elements

# For text: never hardcode font size — use relative sizes and let stretch handle scaling
# Use Theme with font_sizes set to your base-resolution target

# For buttons: minimum touch target = 44×44 dp (Apple HIG) / 48×48 dp (Google Material)
# Set Control.custom_minimum_size = Vector2(44, 44) * DisplayServer.screen_get_scale()
```

## Safe area insets (notch, home bar)

iPhones with notch or Dynamic Island, and Android devices with cutouts, require safe area insets. Content placed outside the safe area is obscured.

```gdscript
# Apply safe area insets to a top-level MarginContainer
func _ready() -> void:
    _apply_safe_area()
    DisplayServer.screen_orientation_changed.connect(_apply_safe_area)

func _apply_safe_area() -> void:
    var safe_area := DisplayServer.get_display_safe_area()
    var screen_size := DisplayServer.screen_get_size()
    var margin_top := safe_area.position.y
    var margin_bottom := screen_size.y - safe_area.end.y
    var margin_left := safe_area.position.x
    var margin_right := screen_size.x - safe_area.end.x
    
    $SafeAreaMargin.add_theme_constant_override("margin_top", margin_top)
    $SafeAreaMargin.add_theme_constant_override("margin_bottom", margin_bottom)
    $SafeAreaMargin.add_theme_constant_override("margin_left", margin_left)
    $SafeAreaMargin.add_theme_constant_override("margin_right", margin_right)
```

## Godot export settings for Android

1. **Install Android export template**: Editor → Manage Export Templates → download.
2. **Add Android export preset**: Project → Export → Add → Android.
3. **Keystore**: generate a release keystore with `keytool`. Store it outside the project directory (never commit to git).
4. **Minimum SDK**: 21 (Android 5.0) for broad compatibility; 24 (Android 7.0) for Vulkan renderer.
5. **Architectures**: arm64-v8a (modern devices) + armeabi-v7a (older devices). Do not add x86_64 unless targeting Chrome OS.
6. **Permissions**: add only what the game needs. Over-requesting permissions triggers Play Store review flags.
7. **Orientation**: set in Project Settings → Display → Window → Handheld → Orientation.

## Godot export settings for iOS

1. **Install iOS export template** (requires macOS for final signing and IPA creation).
2. **Add iOS export preset** → set Bundle Identifier (`com.studio.game`).
3. **Provisioning Profile**: use Xcode or Apple Developer portal to generate. Specify in export settings.
4. **Minimum iOS version**: 14.0 for Vulkan (MoltenVK); 12.0 for OpenGL ES fallback.
5. **Icons and launch images**: provide all required sizes (see iOS HIG). Godot's export dialog lists required sizes.

## Mobile performance checklist

- [ ] Physics FPS set to 30 (not 60) in Project Settings
- [ ] No SDFGI, VoxelGI, SSAO, SSIL — use LightmapGI only
- [ ] Shadow-casting lights ≤ 2
- [ ] No more than 2 post-process effects in WorldEnvironment
- [ ] GPUParticles3D particle count ≤ 500 total on screen
- [ ] MultiMeshInstance3D for any repeated mesh with > 20 instances
- [ ] All textures compressed to ETC2 (Android) or ASTC (iOS/Android)
- [ ] Draw calls ≤ 200 per frame on target device
- [ ] Tested on actual hardware, not just the editor
