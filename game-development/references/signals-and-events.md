# Signals vs Direct Calls vs Autoloads in Godot 4

## The core rule

**Signals flow upward and sideways. Method calls flow downward.**

- A parent node can call methods on its children directly.
- A child node should never call methods on its parent or siblings by path — it should emit a signal and let the parent wire it up.
- Sibling systems that need to communicate use signals through a common parent, or through an autoload event bus.

## Decision table

| Situation | Use |
|---|---|
| Game logic updates the HUD | Signal from game logic → HUD connects |
| Player takes damage, HUD shows it | Signal `health_changed(new_hp)` emitted by Player |
| Enemy dies, score updates | Signal `enemy_died(points)` → ScoreManager |
| Player controller moves the player's sprite | Direct call — parent controlling child is fine |
| Two unrelated systems need to react to the same event | Autoload event bus or shared signal |
| A system needs data synchronously (not just notification) | Direct call or autoload getter |
| Audio plays on hit across multiple scenes | Autoload `AudioManager.play_sfx("hit")` |

## Signals: the right pattern

The HUD should never import or reference game logic nodes by path. Game logic should never import or reference HUD nodes by path.

```gdscript
# Player.gd — owns and emits the signal
extends CharacterBody2D

signal health_changed(new_health: int)
signal player_died

var _health: int = 100

func take_damage(amount: int) -> void:
    _health = max(0, _health - amount)
    health_changed.emit(_health)
    if _health == 0:
        player_died.emit()
```

```gdscript
# HUD.gd — connects to the signal, never touches Player directly
extends CanvasLayer

func _ready() -> void:
    # Wired up by the scene root that owns both
    pass

func _on_player_health_changed(new_health: int) -> void:
    $HealthBar.value = new_health
```

```gdscript
# Level.gd (scene root) — wires everything up
func _ready() -> void:
    $Player.health_changed.connect($HUD._on_player_health_changed)
    $Player.player_died.connect(_on_player_died)
```

The scene root knows about both children and is allowed to connect them. Neither child knows the other exists.

## Autoload event bus: for decoupled cross-scene events

When signals need to cross scene boundaries (player in one scene, HUD in another), use an autoload as an event relay:

```gdscript
# Events.gd — autoload singleton
extends Node

signal player_health_changed(new_health: int)
signal enemy_died(position: Vector2, points: int)
signal level_completed(level_id: String)
```

```gdscript
# Player.gd — emits through autoload
func take_damage(amount: int) -> void:
    _health = max(0, _health - amount)
    Events.player_health_changed.emit(_health)
```

```gdscript
# HUD.gd — connects to autoload, decoupled from player
func _ready() -> void:
    Events.player_health_changed.connect(_on_health_changed)

func _on_health_changed(hp: int) -> void:
    $HealthBar.value = hp
```

## Direct method calls: when coupling is intentional

Direct calls are correct when the caller owns the callee and the coupling is architectural (not accidental):

```gdscript
# PlayerController.gd calling its own child nodes — correct
func _physics_process(delta: float) -> void:
    $AnimatedSprite2D.play("run" if velocity.x != 0 else "idle")
    $DustParticles.emitting = is_on_floor() and velocity.length() > 10
```

The controller owns these child nodes — the coupling is intentional and local.

## Autoloads: for global state, not global spaghetti

An autoload (singleton) is the right tool when:
- Multiple systems need the same data synchronously (e.g., `GameConfig.master_volume`)
- A service has no natural owner in the scene tree (e.g., `AudioManager`, `SaveManager`)
- You need persistent state across scene changes

Autoloads are wrong when:
- You use them to avoid wiring up signals (lazy coupling)
- You're accessing scene-local state through them (breaks scene encapsulation)
- Every system talks to every other system through the autoload (God Object antipattern)

```gdscript
# Wrong — using autoload to reach into a scene
func some_system() -> void:
    get_node("/root/Level/Player").health  # ← path-dependent, brittle

# Right — player emits, systems subscribe
func take_damage(amount: int) -> void:
    Events.player_health_changed.emit(_health)
```

## One-shot signal connections

For events that should fire once and then disconnect:

```gdscript
# CONNECT_ONE_SHOT flag auto-disconnects after first call
$Door.body_entered.connect(_on_first_entry, CONNECT_ONE_SHOT)

# Or with a lambda:
$AnimationPlayer.animation_finished.connect(
    func(_name): _on_cutscene_done(),
    CONNECT_ONE_SHOT
)
```

## Typed signals (Godot 4)

Always type signal parameters. The static type checker catches mis-wired connections at edit time, not runtime:

```gdscript
signal item_collected(item: ItemData)   # typed — editor warns if handler sig is wrong
signal score_changed(new_score: int)
signal game_state_changed(state: GameManager.State)  # enum type works too
```

## Diagnosing "who's connected to what"

In the editor: select any node → Signal tab → see all outgoing and incoming connections. Use this when debugging unexpected double-fires or missing updates. In code, `signal.get_connections()` returns an Array of dicts with `callable` and `flags`.
