# Input Remapping and Gamepad Support

## Runtime input remapping

InputMap is writable at runtime. To rebind an action, clear its existing events and add the new one:

```gdscript
func rebind_action(action: StringName, new_event: InputEvent) -> void:
    InputMap.action_erase_events(action)
    InputMap.action_add_event(action, new_event)
```

To capture a new binding (wait for any input):

```gdscript
# BindingCapture.gd — set process_unhandled_input = true while capturing
var _action_to_bind: StringName = ""

func start_capture(action: StringName) -> void:
    _action_to_bind = action
    set_process_unhandled_input(true)

func _unhandled_input(event: InputEvent) -> void:
    if not _action_to_bind:
        return
    if event is InputEventKey and event.pressed:
        rebind_action(_action_to_bind, event)
        _action_to_bind = ""
        set_process_unhandled_input(false)
    elif event is InputEventJoypadButton and event.pressed:
        rebind_action(_action_to_bind, event)
        _action_to_bind = ""
        set_process_unhandled_input(false)
```

## Conflict detection

Before applying a new binding, check whether the event already drives another action:

```gdscript
func find_conflicting_action(new_event: InputEvent, skip_action: StringName) -> StringName:
    for action in InputMap.get_actions():
        if action == skip_action:
            continue
        for event in InputMap.action_get_events(action):
            if event.is_match(new_event):
                return action
    return ""
```

If a conflict exists, prompt the user to swap, overwrite, or cancel.

## Saving and loading remapped bindings

InputEvent objects cannot be serialized directly. Serialize the relevant fields by event type:

```gdscript
func serialize_event(event: InputEvent) -> Dictionary:
    if event is InputEventKey:
        return {"type": "key", "keycode": event.keycode, "physical": event.physical_keycode}
    elif event is InputEventJoypadButton:
        return {"type": "joypad_button", "button_index": event.button_index}
    elif event is InputEventJoypadMotion:
        return {"type": "joypad_motion", "axis": event.axis, "axis_value": event.axis_value}
    elif event is InputEventMouseButton:
        return {"type": "mouse_button", "button_index": event.button_index}
    return {}

func deserialize_event(data: Dictionary) -> InputEvent:
    match data.get("type", ""):
        "key":
            var e := InputEventKey.new()
            e.keycode = data["keycode"]
            e.physical_keycode = data.get("physical", 0)
            return e
        "joypad_button":
            var e := InputEventJoypadButton.new()
            e.button_index = data["button_index"]
            return e
        "joypad_motion":
            var e := InputEventJoypadMotion.new()
            e.axis = data["axis"]
            e.axis_value = data["axis_value"]
            return e
        "mouse_button":
            var e := InputEventMouseButton.new()
            e.button_index = data["button_index"]
            return e
    return null

func save_bindings() -> void:
    var bindings := {}
    for action in InputMap.get_actions():
        var events := []
        for event in InputMap.action_get_events(action):
            var s := serialize_event(event)
            if not s.is_empty():
                events.append(s)
        if not events.is_empty():
            bindings[action] = events
    var f := FileAccess.open("user://bindings.json", FileAccess.WRITE)
    f.store_string(JSON.stringify(bindings))

func load_bindings() -> void:
    if not FileAccess.file_exists("user://bindings.json"):
        return
    var f := FileAccess.open("user://bindings.json", FileAccess.READ)
    var bindings: Dictionary = JSON.parse_string(f.get_as_text())
    for action in bindings:
        if not InputMap.has_action(action):
            continue
        InputMap.action_erase_events(action)
        for event_data in bindings[action]:
            var event := deserialize_event(event_data)
            if event:
                InputMap.action_add_event(action, event)
```

## Analog action strength and deadzone

For triggers and sticks, use `Input.get_action_strength()` — not `is_action_pressed()`:

```gdscript
# Trigger pull: 0.0 (not pressed) to 1.0 (fully pressed)
var trigger := Input.get_action_strength("accelerate")

# Axis: returns -1.0 to 1.0 for a stick mapped to two actions
var move_x := Input.get_axis("move_left", "move_right")
var move_y := Input.get_axis("move_up", "move_down")
```

Set per-action deadzone in InputMap (prevents stick drift from registering):

```gdscript
InputMap.action_set_deadzone("move_right", 0.2)
```

The deadzone is applied automatically — `get_action_strength()` returns 0.0 until the raw axis value exceeds the deadzone, then remaps the remainder to 0.0–1.0.

## JoyAxis and JoyButton enums (Godot 4)

Godot 4 uses enums, not the integer constants from Godot 3:

```gdscript
# Godot 4 — correct
var e := InputEventJoypadButton.new()
e.button_index = JoyButton.JOYPAD_BUTTON_A   # cross / A
e.button_index = JoyButton.JOYPAD_BUTTON_B   # circle / B

var m := InputEventJoypadMotion.new()
m.axis = JoyAxis.JOYPAD_AXIS_LEFT_X          # left stick horizontal
m.axis = JoyAxis.JOYPAD_AXIS_TRIGGER_LEFT    # left trigger (0.0–1.0)
```

Common Godot 3 mistake: using integer literals like `JOY_BUTTON_0` or `JOY_AXIS_0` — these are renamed in Godot 4.

## Controller detection

```gdscript
func _ready() -> void:
    Input.joy_connection_changed.connect(_on_controller_changed)
    _update_controller_state(not Input.get_connected_joypads().is_empty())

func _on_controller_changed(device: int, connected: bool) -> void:
    _update_controller_state(connected)

func _update_controller_state(has_controller: bool) -> void:
    # Show/hide controller prompts in UI
    $ControllerHints.visible = has_controller
    $KeyboardHints.visible = not has_controller
```

`Input.get_connected_joypads()` returns an `Array[int]` of device IDs. Use device ID 0 for the primary controller; check the array for multiplayer.

## Detecting active input device

For mixed keyboard+controller UI (show the right prompt):

```gdscript
enum InputDevice { KEYBOARD, GAMEPAD }
var active_device := InputDevice.KEYBOARD

func _input(event: InputEvent) -> void:
    if event is InputEventKey or event is InputEventMouseButton:
        active_device = InputDevice.KEYBOARD
    elif event is InputEventJoypadButton or event is InputEventJoypadMotion:
        if (event as InputEventJoypadMotion).axis_value > 0.1:
            active_device = InputDevice.GAMEPAD
```

## Rumble / haptic feedback

```gdscript
func rumble(weak: float, strong: float, duration: float, device: int = 0) -> void:
    Input.start_joy_vibration(device, weak, strong, duration)

# Stop early (e.g. player death)
func stop_rumble(device: int = 0) -> void:
    Input.stop_joy_vibration(device)
```

`weak` (0.0–1.0) is high-frequency buzz; `strong` (0.0–1.0) is low-frequency rumble. For hit feedback: weak=0.3, strong=0.6, duration=0.15.

## Resetting to defaults

Store default InputMap actions on first launch by reading them before any rebinding:

```gdscript
var _defaults: Dictionary = {}

func _ready() -> void:
    # Call once before load_bindings()
    for action in InputMap.get_actions():
        _defaults[action] = InputMap.action_get_events(action).duplicate(true)

func reset_to_defaults() -> void:
    for action in _defaults:
        InputMap.action_erase_events(action)
        for event in _defaults[action]:
            InputMap.action_add_event(action, event)
    FileAccess.remove("user://bindings.json")
```
