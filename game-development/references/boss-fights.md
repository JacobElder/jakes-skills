# Boss Fight Patterns

## Phase-based state machine

The wrong structure is a flat `match current_phase:` with all attack logic inline — it becomes unmaintainable by phase 2 and impossible to add telegraphing. The right structure separates phase data from the controller that runs it.

```gdscript
# BossPhase.gd — one Resource per phase
class_name BossPhase
extends Resource

@export var health_threshold: float = 0.0   # enter this phase when hp drops below threshold
@export var phase_name: String = ""
@export var attacks: Array[AttackData] = []
@export var music_stem: String = ""          # stem to bring up on phase transition
@export var arena_changes: Array[String] = [] # signals to emit (e.g. "spawn_lava_floor")
@export var vulnerability: int = -1          # damage type required; -1 = all damage
```

```gdscript
# AttackData.gd
class_name AttackData
extends Resource

@export var attack_id: String = ""
@export var telegraph_duration: float = 0.8   # seconds of warning before damage
@export var telegraph_animation: String = ""  # animation to play during windup
@export var active_duration: float = 0.4
@export var recovery_duration: float = 0.5
@export var damage: float = 20.0
@export var min_player_distance: float = 0.0  # only use if player is within this range
@export var max_player_distance: float = 9999.0
@export var cooldown: float = 2.5
@export var weight: float = 1.0               # relative selection probability
```

```gdscript
# BossController.gd
extends CharacterBody2D

@export var phases: Array[BossPhase] = []     # ordered by health threshold descending

var _current_phase: BossPhase = null
var _attack_cooldowns: Dictionary = {}        # attack_id → remaining cooldown
var _state: String = "idle"                   # idle / telegraphing / attacking / recovering / stunned

func _ready() -> void:
    _current_phase = phases[0]
    _start_phase(_current_phase)

func take_damage(amount: float, damage_type: int = -1) -> void:
    if _current_phase.vulnerability != -1 and damage_type != _current_phase.vulnerability:
        _show_immune_indicator()
        return
    if _state in ["telegraphing", "attacking"]:
        return   # invincible during own attack animations
    hp -= amount
    _check_phase_transition()

func _check_phase_transition() -> void:
    for phase in phases:
        if hp / max_hp <= phase.health_threshold and phase != _current_phase:
            _transition_phase(phase)
            return

func _transition_phase(new_phase: BossPhase) -> void:
    _current_phase = new_phase
    _start_phase(new_phase)
    # Arena changes
    for signal_name in new_phase.arena_changes:
        emit_signal(signal_name)
    # Music
    if new_phase.music_stem != "":
        MusicManager.set_stem(new_phase.music_stem, 1.0)
    # Brief stun / cutscene moment at phase transition
    _state = "stunned"
    await get_tree().create_timer(1.5).timeout
    _state = "idle"

func _start_phase(phase: BossPhase) -> void:
    _attack_cooldowns.clear()
    for attack in phase.attacks:
        _attack_cooldowns[attack.attack_id] = 0.0

func _tick_idle(delta: float) -> void:
    # Cooldowns
    for key in _attack_cooldowns:
        _attack_cooldowns[key] = max(0.0, _attack_cooldowns[key] - delta)
    # Select next attack
    var attack := _select_attack()
    if attack:
        _execute_attack(attack)

func _select_attack() -> AttackData:
    var dist := global_position.distance_to(player.global_position)
    var available := _current_phase.attacks.filter(func(a: AttackData) -> bool:
        return _attack_cooldowns[a.attack_id] <= 0.0 \
            and dist >= a.min_player_distance \
            and dist <= a.max_player_distance
    )
    if available.is_empty():
        return null
    # Weighted random selection
    var total_weight := available.reduce(func(acc, a): return acc + a.weight, 0.0)
    var roll := randf() * total_weight
    for attack in available:
        roll -= attack.weight
        if roll <= 0.0:
            return attack
    return available[-1]

func _execute_attack(attack: AttackData) -> void:
    _state = "telegraphing"
    _attack_cooldowns[attack.attack_id] = attack.cooldown

    # --- Telegraph phase ---
    animation_player.play(attack.telegraph_animation)
    _show_danger_indicator(attack)
    await get_tree().create_timer(attack.telegraph_duration).timeout

    # --- Active / damage phase ---
    _state = "attacking"
    _activate_hitbox(attack)
    await get_tree().create_timer(attack.active_duration).timeout

    # --- Recovery phase (still somewhat vulnerable) ---
    _state = "recovering"
    _deactivate_hitbox()
    await get_tree().create_timer(attack.recovery_duration).timeout
    _state = "idle"
```

## Telegraphing attacks

Players die because attacks are invisible or instant. Every attack needs:
1. **Windup animation** — boss changes posture, charges up, glows.
2. **Danger indicator** — show where the attack will land *before* it fires.
3. **Grace window** — 0.5–1.5 seconds between telegraph and damage.

```gdscript
func _show_danger_indicator(attack: AttackData) -> void:
    match attack.attack_id:
        "ground_slam":
            # Show radial warning around impact point
            var indicator := preload("res://scenes/warning_ring.tscn").instantiate()
            get_tree().current_scene.add_child(indicator)
            indicator.global_position = _predict_slam_position()
            indicator.start(attack.telegraph_duration)

        "laser_sweep":
            # Show thin line that sweeps to show trajectory
            laser_indicator.show()
            var tween := create_tween()
            tween.tween_property(laser_indicator, "rotation", target_angle, attack.telegraph_duration)
            await tween.finished
            laser_indicator.hide()

        "charge":
            # Arrow showing charge direction
            charge_arrow.show()
            charge_arrow.global_position = global_position
            charge_arrow.look_at(player.global_position)
```

## Vulnerability windows

Four patterns for damage windows:

1. **Recovery window** (default): boss is vulnerable during recovery frames after each attack. Simple and fair.
2. **Phase-gated vulnerability**: boss has a shield/armor; a specific mechanic must be triggered first (stun by hitting a weak spot, completing a puzzle). Only use if the mechanic is obvious and telegraphed.
3. **Exposed weak point**: boss opens a specific body part during attacks. Hit it to deal bonus damage.
4. **Damage type gate**: boss is immune until player switches weapon type (see `vulnerability` field on `BossPhase`).

```gdscript
# Weak point — separate hitbox that's only active during specific attack
func _execute_attack(attack: AttackData) -> void:
    if attack.attack_id == "arm_slam":
        # Arm weak point is exposed during telegraph
        arm_weakpoint.monitoring = true
        arm_weakpoint.visible = true
        await get_tree().create_timer(attack.telegraph_duration).timeout
        arm_weakpoint.monitoring = false
        arm_weakpoint.visible = false
```

## Arena changes

```gdscript
# Phase 2: lava floor rises, platforms appear
signal spawn_lava_floor
signal activate_platforms

func _on_spawn_lava_floor() -> void:
    lava_floor.show()
    var tween := create_tween()
    tween.tween_property(lava_floor, "position:y", target_y, 2.0).set_ease(Tween.EASE_IN_OUT)

func _on_activate_platforms() -> void:
    for platform in moving_platforms:
        platform.set_physics_process(true)
```

## Death sequence

Don't `queue_free()` the boss immediately — the death should feel earned.

```gdscript
func _die() -> void:
    _state = "dead"
    set_physics_process(false)
    get_node("Hitbox").queue_free()

    # Big death explosion sequence
    for i in 8:
        var pos := global_position + Vector2(randf_range(-60, 60), randf_range(-60, 60))
        ExplosionPool.spawn(pos)
        await get_tree().create_timer(0.15).timeout

    # Screen flash + hitstop
    RenderingServer.set_default_clear_color(Color.WHITE)
    await get_tree().create_timer(0.1).timeout
    RenderingServer.set_default_clear_color(original_clear_color)

    # Victory fanfare
    MusicManager.play_stinger("boss_defeat")
    await get_tree().create_timer(2.0).timeout
    boss_defeated.emit(loot_table)
    queue_free()
```

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| Flat `match state:` with all attack logic inline | Untestable; can't add phases without rewriting | Phase Resource + AttackData Resource |
| Instant attacks (no telegraph) | Player dies unfairly; no skill expression | `telegraph_duration` on every AttackData |
| Boss invincible during all phases | Frustrating; no feedback | Vulnerable during recovery, invincible during attack |
| `queue_free()` immediately on death | Death feels cheap | Death animation sequence with particles and hitstop |
| Equal probability for all attacks | Pattern becomes readable and boring after 3 tries | Weighted selection + distance constraints |
| Phase 2 starts mid-attack | Jarring transition | Brief stun period on phase transition |
| Same arena throughout | Fight feels flat | Arena changes signal on phase transition |

## Unity equivalents

| Godot | Unity |
|---|---|
| `BossPhase extends Resource` | `BossPhase : ScriptableObject` |
| `AnimationPlayer.play(name)` | `Animator.Play(name)` |
| `await get_tree().create_timer(t).timeout` | `yield return new WaitForSeconds(t)` in coroutine |
| `emit_signal(signal_name)` | `SendMessage(eventName)` or C# event |
| Weighted random on `AttackData.weight` | Same pattern; no Unity built-in |
