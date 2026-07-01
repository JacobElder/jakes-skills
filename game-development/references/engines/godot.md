# Godot 4.x (GDScript)

Godot's model is **nodes** composed into **scenes**, communicating via **signals**, with behavior in **GDScript** (Python-like) or C#. This file covers the idioms that make Godot code clean and the antipatterns generated code falls into. Pair with the core references — this is the Godot-flavored "how," not a replacement for the loop/feel/architecture "what." Current stable is 4.7; everything here applies to 4.x.

## Contents
- The mental model: nodes, scenes, instancing
- `_process` vs `_physics_process`
- Signals (and the EventBus pattern)
- Composition with component nodes
- Movement: CharacterBody2D & move_and_slide
- Resources for data-driven design
- Tweens & AnimationPlayer for feel
- Common antipatterns
- GDScript niceties

## The mental model: nodes, scenes, instancing

Everything is a **node** (Sprite2D, CharacterBody2D, Area2D, Timer, AudioStreamPlayer, …) arranged in a tree. A **scene** is a saved subtree (a Player, an Enemy, a Bullet, a Level) that you **instance** repeatedly. Build your game as many small scenes instanced and composed, not one big scene with everything in it. A bullet is a scene you `instantiate()` and `add_child()`; an enemy is a scene; a level composes them.

`@export var` exposes a variable to the inspector (and to designers) — use it for every tunable. `@onready var x = $Path` grabs a child node when the node is ready.

## `_process` vs `_physics_process`

- `_physics_process(delta)` — **fixed timestep** (default 60 Hz). Movement, physics, collision, anything needing consistency. This is where `move_and_slide` belongs.
- `_process(delta)` — **once per rendered frame** (variable). Visual-only updates, UI, cosmetic interpolation.

Doing movement in `_process` is a classic generated-code bug (framerate-dependent). Put it in `_physics_process`. (See `game-loop-and-time.md`.)

## Signals (and the EventBus pattern)

Signals are Godot's decoupling mechanism — use them instead of brittle node paths.

```gdscript
signal died
signal health_changed(current: int, max: int)

func take_damage(n: int) -> void:
    health -= n
    health_changed.emit(health, max_health)
    if health <= 0:
        died.emit()
```

Connect in code `enemy.died.connect(_on_enemy_died)` or in the editor. For **cross-cutting global events** (score changed, game over, level complete) that many unrelated nodes care about, make a small **autoload singleton** "EventBus" holding signals, and have anyone emit/listen on it — this avoids `get_node("../../../GameManager")` coupling. Don't route *everything* through it; a parent calling its own child directly is fine. (See `architecture.md`.)

## Composition with component nodes

Idiomatic Godot composition is **child nodes as components**: a `HealthComponent`, `HurtboxComponent` (an `Area2D`), `StateMachine` node hung under the entity, reused across player/enemies/breakables. Prefer this over deep `extends` chains. Use **groups** (`add_to_group("enemies")`) to address sets of nodes without coupling to their location.

## Movement: CharacterBody2D & move_and_slide

For a player or most enemies, use **`CharacterBody2D`** (kinematic), set `velocity`, and call `move_and_slide()` — it handles collision response and sliding. Use `is_on_floor()` for ground checks. Reserve `RigidBody2D` for world physics objects (crates, debris), not the avatar. `move_and_collide()` gives you a single swept move with the collision info when you want manual control (good for bullets/dashes).

```gdscript
func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta
    var dir := Input.get_axis("move_left", "move_right")
    velocity.x = move_toward(velocity.x, dir * SPEED, ACCEL * delta)
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = -JUMP_VELOCITY
    move_and_slide()
```

(Layer the full platformer feel — coyote time, jump buffer, asymmetric gravity, variable height — from `collision-and-physics.md`; a complete tuned reference implementation ships at `assets/godot_platformer_controller.gd`.) Use the **Input Map** (Project Settings) and `Input.is_action_*` / `Input.get_axis`, not hardcoded keycodes, so rebinding and controllers work.

## Resources for data-driven design

Custom **`Resource`** classes are Godot's ScriptableObject equivalent — define a `class_name EnemyStats extends Resource` with `@export` fields, author `.tres` data assets in the editor, and have logic read them. This makes enemies/weapons/levels data, not code. Great for tuning and modding. (See `architecture.md`.)

## Tweens & AnimationPlayer for feel

- **Tweens** for procedural feel: `create_tween()` then `tween_property(sprite, "scale", Vector2(1.2,0.8), 0.1).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)` for squash/pop. Tween anything you'd otherwise snap.
- **AnimationPlayer** for authored sequences; it can key *any* property (including calling methods and emitting at keyframes) — useful for attack timing.
- **GPUParticles2D**/**CPUParticles2D** for dust/sparks/blood; **Camera2D** offset for screenshake (drive with a trauma value, see `game-feel.md`).

## Common antipatterns

- **Movement in `_process`** instead of `_physics_process` → framerate-dependent. Move it.
- **Brittle node paths** like `get_node("../../../Manager")` → breaks on any restructure. Use signals, groups, exported references, or an EventBus.
- **RigidBody for the player** → floaty, slippery, hard to tune. The instinct is to add `linear_damp` and tweak `mass`, but the fix is architectural: switch to `CharacterBody2D` kinematic control. Forces-based motion fights the physics engine for authored feel; kinematic sets velocity directly and gives you the precise control platformers require.
- **Hardcoded keycodes** → use the Input Map.
- **God scripts** — a 400-line `Player.gd` doing movement, combat, UI, audio, and save. Split into component nodes and emit signals.
- **`get_node` in tight loops** / per-frame `find_*` → cache references in `@onready`.
- **Freeing/instancing bullets every frame** → pool them (keep a free list of nodes, hide+reset instead of `queue_free`).
- **Tuning values hardcoded** → `@export` them.
- **Autoload overuse** — having a manager singleton for every system (`GameManager`, `UIManager`, `EnemyManager`, `InventoryManager`, `PlayerManager`, …) creates the same coupling problem as god scripts, just distributed. Every scene now depends on a set of globals; initialization order becomes fragile; state bleeds across scenes. The only autoloads that typically earn their place: an `EventBus` (signals) and maybe a utility like `AudioManager` or `SaveManager`. Everything else should live in scenes that own their state and communicate via signals. If you find yourself reaching for an autoload to pass data around, a signal is almost always the better answer.
- **`lerp(a, b, weight)` in `_process` with a fixed weight** → framerate-dependent smooth follow. See `game-loop-and-time.md` for the exponential-decay fix or move to `_physics_process`.

## GDScript niceties

Use **static typing** (`var speed: float = 200.0`, `func f(x: int) -> void:`) — it catches bugs, speeds up the engine, and improves autocomplete. `@export_range` gives inspector sliders for feel constants. `await` works with signals and tweens (`await tween.finished`). `match` for state machines. Keep scripts focused; one script per node responsibility.
