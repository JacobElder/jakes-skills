# Architecture: Keeping a Game From Becoming Spaghetti

Small games rot in a predictable way: one giant `Player`/`Game` class accretes responsibilities, objects reach into each other's internals, and a deep inheritance tree makes every new enemy a refactor. The patterns here prevent that. None are heavyweight — they're the cheap structure that keeps a small game malleable enough to keep tuning, which is where games are actually made.

## Contents
- Composition over inheritance
- Decoupling with events / signals / messages
- Finite state machines
- Data-driven design
- The update-order trap
- Save systems
- Don't over-architect

## Composition over inheritance

The instinct to model a `Goblin` as `Goblin → Enemy → Character → Entity` feels clean and turns painful fast: behavior you want to share cuts *across* the tree (a destructible crate and a player both have health; a player and a homing missile both move toward a target), and inheritance can't express "has some of these, not others." You end up with god base classes and duplicated code.

Instead, **build entities by composing small pieces**: a `Health` piece, a `Velocity` piece, a `Hurtbox`, an `AIBrain`, a `SpriteAnimator`. An entity *is* the set of pieces it has.

- **Godot:** compose with **child nodes**. A `HealthComponent` node, a `HurtboxComponent` node, a `StateMachine` node, hung under the entity. Reusable across players, enemies, breakables.
- **Unity:** compose with **MonoBehaviour components** on a GameObject; prefer many small components over one large one. ScriptableObjects hold shared data.
- **Code-first / Bevy:** this is literally ECS — entities are IDs, components are plain data, systems operate over "all entities with components X and Y." Bevy is built on this; in LÖVE/PyGame you can adopt a lightweight ECS or a simpler component-bag per entity.

Rule of thumb: when your class tree goes past two levels, or you're tempted to copy a method between siblings, switch that axis of behavior to a component.

## Decoupling with events / signals / messages

The fastest way to a tangled codebase is direct cross-references: the player calling `ui.health_bar.set_value()`, calling `audio.play()`, calling `achievements.check()`. Now the player knows about the UI, the audio bus, and the achievement system, and you can't test or reuse it.

Invert it: the player **announces** what happened and doesn't care who listens.

```
# Coupled — player reaches into everyone
func take_damage(n):
    health -= n
    ui.health_bar.set_value(health)
    audio.play("hurt")
    if health <= 0: game.show_game_over()

# Decoupled — player announces; listeners react
func take_damage(n):
    health -= n
    emit("damaged", health)
    if health <= 0: emit("died")
```

The HUD subscribes to `damaged`, the audio system plays a hurt sound on `damaged`, the game-over flow listens for `died`. Each can change independently.

- **Godot:** **signals** are built for this. `signal damaged(health)`, then `emit_signal("damaged", health)`, and connect listeners (in code or the editor). For cross-cutting global events, a small autoload "EventBus" singleton with signals avoids deep node-path coupling. Prefer signals over `get_node("../../../Manager")` paths — brittle paths are a top Godot smell.
- **Unity:** C# `event`/`Action`, `UnityEvent`, or a ScriptableObject-based event channel (a designer-friendly pattern: events are assets that emitters raise and listeners subscribe to). Avoid `GameObject.Find`/`SendMessage` in hot paths.
- **Code-first:** a tiny observer/pub-sub registry, or in ECS, events as components/resources that systems read.

Don't overdo it: a parent directly calling a method on its own child is fine. Events earn their keep for *cross-cutting* and *one-to-many* communication, not every call.

## Finite state machines

Entities and the game itself are almost always in exactly one of several states (Idle, Run, Jump, Attack, Hurt, Dead; or MainMenu, Playing, Paused, GameOver). Modeling that with a pile of booleans (`is_jumping`, `is_attacking`, `can_move`) produces impossible combinations and bugs. A **finite state machine** makes the current state explicit and transitions controlled.

Minimum viable FSM: each state is an object/enum with `enter()`, `update(delta)`, and `exit()`; the machine holds the current state and swaps it on transition, calling `exit` then `enter`. This cleanly localizes "what can happen right now" and is the standard structure for both character behavior and overall game flow.

- Keep transition rules in one place so they're auditable.
- For richer character behavior, a hierarchical state machine (substates under "Grounded"/"Airborne") scales further, but don't reach for it until a flat FSM hurts.
- **Godot** has community StateChart/FSM addons and the pattern is idiomatic with nodes; **Unity** has Animator state machines (fine for animation, often too clunky for gameplay logic — a code FSM is usually cleaner for behavior).

## Data-driven design

The bulk of game development is **tuning**: changing numbers and content, then playing again. If those values are buried in code, every tweak is a code edit and a recompile, and a non-programmer can't help. So **separate data from logic**:

- Enemy stats, weapon definitions, level layouts, dialogue, loot tables, and tuning constants live in **data** — Godot **Resources** (custom `Resource` classes, editable in the inspector), Unity **ScriptableObjects**, or plain JSON/CSV/TOML for code-first.
- Logic reads the data and acts on it generically. Adding a new enemy becomes "author a new data asset," not "write a new class."

This pays off enormously: it makes balancing fast, enables modding, and lets designers iterate without touching code. Expose feel constants (jump height, acceleration, screenshake amount) the same way — they get changed constantly.

## The update-order trap

When many systems run each tick, *order* causes subtle bugs: if input is read after movement, you get a one-frame lag; if collision resolves before movement, objects pass through. Decide and document the per-tick order — typically **input → AI/decision → movement → collision resolution → triggers/events → animation → camera**. Camera should usually update *after* the thing it follows has moved (in Godot, late via `_process` after `_physics_process`; in Unity, `LateUpdate`), or the camera lags by a frame.

## Save systems

Keep saving simple and decoupled: serialize a plain data snapshot of game state (a dict/struct of the values that matter), not live engine objects. Each savable entity exposes `to_data()`/`from_data()`. Write JSON for debuggability while developing; switch to a binary or compressed format later only if size/tamper-resistance matters. Version your save format from day one (store a `version` field) so you can migrate later. Don't try to serialize the whole scene graph — snapshot the *model*, rebuild the *view*.

## Don't over-architect

All of this is in service of keeping a *small* game tunable, not building enterprise software. A game jam entry doesn't need an event bus and a data-driven enemy pipeline. Add structure when the pain appears: the second time you copy-paste a behavior, the third boolean flag on an entity, the first brittle node path. Premature ECS frameworks and elaborate manager hierarchies kill small projects as surely as spaghetti does. Match the architecture to the scope.

### On ECS specifically

ECS (Entity-Component-System) is a real architectural pattern with real benefits — at scale. It earns its overhead when you have **10,000+ entities with cache-sensitive simulation**: factory/colony sims, crowd simulations, physics sandboxes. For a roguelike with 20 enemy types, a platformer, or a survivors-like under a few thousand entities, a full ECS framework adds cognitive overhead, tooling friction, and integration complexity without meaningful performance gain.

The composition patterns in this file (Godot child nodes, Unity MonoBehaviours, simple component bags in code-first engines) *are* compositional design — they just aren't a formalized ECS. That's the right level of architecture for most small games. "Is this professional?" — yes, composition without ECS is what shipped games use at this scale. Reach for ECS when the profiler says so, not when the project starts.
