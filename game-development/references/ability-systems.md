# Ability Systems (GAS-lite)

Copy-pasted timer logic per ability is not a scalability problem — it is an architecture problem. When every ability has its own `_cooldown_timer`, `_is_casting`, `_mana_cost` variable, and duplicate interrupt/cancel code, adding a 10th ability means touching 10 files. A proper ability system encodes the pipeline once and drives it from data.

This file describes a "GAS-lite" (Godot Ability System, lighter than Unreal's full GAS) that covers the full activation pipeline: resource cost, cooldown, cast time, channeling, interrupt handling, and tag gating.

## Contents
- AbilityData Resource (the schema)
- AbilityComponent (the runtime)
- Activation pipeline step by step
- Interrupt and cancel
- Cooldown tracking
- Tag-based gating (Silence, Stun)
- Global cooldown (GCD)
- UI integration via signals
- Ability slot system
- Progression and upgrades
- Common mistakes

## AbilityData Resource

`AbilityData` is a `Resource` subclass — immutable shared data that describes what an ability is, not its runtime state:

```gdscript
# AbilityData.gd
class_name AbilityData
extends Resource

@export var ability_id: StringName = &""
@export var display_name: String = ""
@export var icon: Texture2D

# Cost
@export var mana_cost: float = 0.0
@export var health_cost: float = 0.0   # some abilities cost HP

# Timing
@export var cast_time: float = 0.0     # 0 = instant
@export var channel_time: float = 0.0  # 0 = not channeled; > 0 = holds for this duration
@export var channel_tick_interval: float = 0.5  # how often channel fires its effect

# Cooldown
@export var cooldown: float = 0.0

# Tags
@export var tags: Array[StringName] = []        # what this ability IS: ["spell", "projectile"]
@export var blocked_by: Array[StringName] = []  # debuffs that prevent it: ["silence", "stun"]
@export var required_tags: Array[StringName] = [] # tags actor must have: ["grounded"]

# Behavior flags
@export var interruptible: bool = true          # can cast be interrupted mid-cast?
@export var cancellable: bool = true            # can player cancel channel manually?

# Effect — implemented by subclass or assigned as a Callable
@export var effect_scene: PackedScene           # optional: spawn this scene on fire
```

`AbilityData` objects are `.tres` files in `res://abilities/`. They are shared across all actors of the same type — do NOT store per-actor runtime state (cooldowns, cast progress) in them.

## AbilityComponent

`AbilityComponent` is a `Node` added to any actor that can use abilities. It owns all runtime state:

```gdscript
# AbilityComponent.gd
class_name AbilityComponent
extends Node

signal ability_activated(ability: AbilityData)
signal ability_interrupted(ability: AbilityData)
signal ability_ready(ability: AbilityData)
signal ability_blocked(ability: AbilityData, blocker_tag: StringName)

enum State { IDLE, CASTING, CHANNELING }

var _state: State = State.IDLE
var _active_ability: AbilityData = null
var _cast_timer: float = 0.0
var _channel_timer: float = 0.0
var _channel_tick_timer: float = 0.0
var _cooldowns: Dictionary = {}         # ability_id → remaining seconds
var _active_effect_tags: Dictionary = {}  # tag → reference count (for stacking debuffs)

# Reference to actor's resource pool (mana/health)
@export var actor: Node  # must have .mana, .max_mana, .health properties

func _process(delta: float) -> void:
    _tick_cooldowns(delta)
    _tick_cast(delta)
    _tick_channel(delta)
```

## Activation pipeline

```gdscript
func try_activate(ability: AbilityData) -> bool:
    # 1. Not already casting/channeling something non-cancellable
    if _state != State.IDLE:
        if _state == State.CHANNELING and _active_ability.cancellable:
            cancel()  # cancel current channel and continue
        else:
            return false

    # 2. Tag gates: blocked_by
    for blocker in ability.blocked_by:
        if _active_effect_tags.has(blocker) and _active_effect_tags[blocker] > 0:
            ability_blocked.emit(ability, blocker)
            return false

    # 3. Tag gates: required_tags
    for required in ability.required_tags:
        if not _active_effect_tags.has(required) or _active_effect_tags[required] == 0:
            return false

    # 4. Cooldown check
    if _cooldowns.get(ability.ability_id, 0.0) > 0.0:
        return false

    # 5. Resource cost check
    if actor.mana < ability.mana_cost:
        return false

    # 6. Consume resources
    actor.mana -= ability.mana_cost
    actor.health -= ability.health_cost

    # 7. Begin cast or fire immediately
    _active_ability = ability
    if ability.cast_time > 0.0:
        _state = State.CASTING
        _cast_timer = ability.cast_time
    elif ability.channel_time > 0.0:
        _begin_channel()
    else:
        _fire(ability)

    return true

func _tick_cast(delta: float) -> void:
    if _state != State.CASTING:
        return
    _cast_timer -= delta
    if _cast_timer <= 0.0:
        if _active_ability.channel_time > 0.0:
            _begin_channel()
        else:
            _fire(_active_ability)

func _begin_channel() -> void:
    _state = State.CHANNELING
    _channel_timer = _active_ability.channel_time
    _channel_tick_timer = _active_ability.channel_tick_interval
    _fire_channel_tick()  # fire immediately on start

func _tick_channel(delta: float) -> void:
    if _state != State.CHANNELING:
        return
    _channel_timer -= delta
    _channel_tick_timer -= delta
    if _channel_tick_timer <= 0.0:
        _fire_channel_tick()
        _channel_tick_timer = _active_ability.channel_tick_interval
    if _channel_timer <= 0.0:
        _finish(_active_ability)

func _fire(ability: AbilityData) -> void:
    _execute_effect(ability)
    _finish(ability)

func _fire_channel_tick() -> void:
    _execute_effect(_active_ability)  # repeated effect (e.g. healing beam tick)

func _finish(ability: AbilityData) -> void:
    _state = State.IDLE
    _cooldowns[ability.ability_id] = ability.cooldown
    ability_activated.emit(ability)
    _active_ability = null
```

## Interrupt and cancel

Interrupt is externally triggered (enemy Silence, knockback). Cancel is player-initiated.

```gdscript
func interrupt() -> void:
    if _state == State.IDLE:
        return
    if not _active_ability.interruptible:
        return  # non-interruptible abilities ignore interrupt calls
    var interrupted := _active_ability
    _refund_cost(interrupted)  # return mana on interrupt
    _state = State.IDLE
    _active_ability = null
    _cast_timer = 0.0
    _channel_timer = 0.0
    ability_interrupted.emit(interrupted)

func cancel() -> void:
    if _state != State.CHANNELING or not _active_ability.cancellable:
        return
    # Cancels don't refund — player chose to stop early
    _state = State.IDLE
    _active_ability = null
    _channel_timer = 0.0

func _refund_cost(ability: AbilityData) -> void:
    actor.mana += ability.mana_cost
    actor.health += ability.health_cost
```

The distinction between `interruptible` and `cancellable` is a balance lever: a channeled healing spell might be `interruptible` (enemy CC breaks it) but also `cancellable` (player can stop early). An ultimate might be `interruptible: false` (enemy CC cannot stop it once started) but still `cancellable: true`.

## Cooldown tracking

```gdscript
func _tick_cooldowns(delta: float) -> void:
    for id in _cooldowns.keys():
        _cooldowns[id] -= delta
        if _cooldowns[id] <= 0.0:
            var ability := _find_ability_by_id(id)
            _cooldowns.erase(id)
            if ability:
                ability_ready.emit(ability)

func cooldown_remaining(ability: AbilityData) -> float:
    return max(0.0, _cooldowns.get(ability.ability_id, 0.0))

func is_on_cooldown(ability: AbilityData) -> bool:
    return _cooldowns.get(ability.ability_id, 0.0) > 0.0
```

Cooldown state lives in `AbilityComponent`, not in `AbilityData`. `AbilityData` is shared across all actors of the same type — if cooldown were stored there, all actors would share the same cooldown.

## Tag-based gating

`AbilityComponent` maintains a reference-counted tag dictionary. Status effects add/remove tags through the same interface, allowing stacking debuffs:

```gdscript
func add_effect_tag(tag: StringName) -> void:
    _active_effect_tags[tag] = _active_effect_tags.get(tag, 0) + 1

func remove_effect_tag(tag: StringName) -> void:
    var count: int = _active_effect_tags.get(tag, 0) - 1
    if count <= 0:
        _active_effect_tags.erase(tag)
    else:
        _active_effect_tags[tag] = count

func has_effect_tag(tag: StringName) -> bool:
    return _active_effect_tags.get(tag, 0) > 0
```

When `EffectManager` applies a Silence status effect, it calls `ability_component.add_effect_tag(&"silence")`. On expiry, `remove_effect_tag(&"silence")`. The `AbilityComponent` never needs to know about Silence specifically — it checks `ability.blocked_by` against the tag dictionary.

For a Stun that blocks all abilities, either: (a) all abilities include `&"stunned"` in their `blocked_by`, or (b) `AbilityComponent` adds a fast-path check at the top of `try_activate()`:

```gdscript
# Fast-path: stunned blocks everything
if has_effect_tag(&"stunned"):
    return false
```

## Global cooldown (GCD)

Many games (MMOs, MOBAs) implement a shared cooldown that applies after any ability use. This prevents button mashing and enforces pacing:

```gdscript
const GCD_DURATION := 0.5  # seconds

var _gcd_remaining: float = 0.0

func _process(delta: float) -> void:
    _gcd_remaining = max(0.0, _gcd_remaining - delta)
    # ... other ticks

func try_activate(ability: AbilityData) -> bool:
    if _gcd_remaining > 0.0 and not ability.tags.has(&"no_gcd"):
        return false  # GCD prevents activation
    # ... rest of pipeline
    _gcd_remaining = GCD_DURATION  # set after successful activation
    return true
```

Tag abilities with `&"no_gcd"` to exempt items, auto-attacks, or off-GCD abilities.

## UI integration via signals

The HUD never reads ability state directly — it connects to signals:

```gdscript
# HUD setup
ability_component.ability_activated.connect(_on_ability_activated)
ability_component.ability_ready.connect(_on_ability_ready)
ability_component.ability_blocked.connect(_on_ability_blocked)

func _on_ability_activated(ability: AbilityData) -> void:
    var slot := _slots[ability.ability_id]
    slot.start_cooldown_overlay(ability.cooldown)

func _on_ability_ready(ability: AbilityData) -> void:
    var slot := _slots[ability.ability_id]
    slot.flash_ready_animation()

func _on_ability_blocked(ability: AbilityData, blocker: StringName) -> void:
    _show_blocked_feedback(ability)  # e.g. "Silenced" tooltip flash
```

Never `get_node("AbilityComponent").cooldown_remaining(ability)` in `_process` for display — that's polling. Signals keep the HUD reactive without coupling it to game logic.

## Ability slot system

The hotbar is separate from the ability system — it is just an assignment layer:

```gdscript
# AbilityHotbar.gd
class_name AbilityHotbar
extends Node

var slots: Array[AbilityData] = []  # index → ability (null = empty)

func assign(slot_idx: int, ability: AbilityData) -> void:
    slots[slot_idx] = ability

func activate_slot(slot_idx: int) -> void:
    var ability := slots[slot_idx]
    if ability:
        _ability_component.try_activate(ability)
```

Players rearrange slots freely at runtime. The `AbilityComponent` does not know about slots — it only executes abilities by data reference.

## Common mistakes

**Storing cooldown in AbilityData**: all actors share the same Resource instance, so one actor's cooldown would affect all actors of that type. Cooldown is runtime state — it belongs in `AbilityComponent`.

**if/elif chain per ability**: `if ability.ability_id == "fireball": cast_fireball()` collapses the data-driven architecture. The effect implementation should be in the ability's `PackedScene`, a Callable, or an `AbilityEffect` subclass — dispatched generically, not named in the pipeline.

**Timer nodes per ability**: `$FireballCooldownTimer`, `$HealCooldownTimer` — this creates a node for every ability and makes cooldowns invisible to the rest of the system. The Dictionary approach in `AbilityComponent` is cheaper and queryable.

**Not emitting `ability_ready`**: UIs that only react to `ability_activated` can't flash the "ready" state when the cooldown ends. Emit both signals.
