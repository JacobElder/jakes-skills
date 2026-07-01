# Unity 6.x (C#)

Unity's model is **GameObjects** with **MonoBehaviour components**, data in **ScriptableObjects**, and a defined script **lifecycle**. This file covers the idioms that keep Unity code clean and the antipatterns generated code falls into. Pair with the core references for the loop/feel/architecture "what." Current baseline is Unity 6.x (6.4 latest, 6.x LTS for production).

## Contents
- The mental model: GameObjects, components, prefabs
- The lifecycle: Update vs FixedUpdate vs LateUpdate
- Composition with small components
- Decoupling: events & ScriptableObject channels
- Movement: kinematic vs Rigidbody
- ScriptableObjects for data
- Feel: tweening, particles, screenshake
- Object pooling
- Common antipatterns

## The mental model: GameObjects, components, prefabs

A **GameObject** is a container; behavior and data come from **components** (MonoBehaviours and built-ins like Rigidbody, Collider, SpriteRenderer). A **prefab** is a saved, reusable GameObject (your Player, Enemy, Bullet) that you instantiate. Build from many small prefabs and many small components, not monolithic objects. `[SerializeField] private` exposes a field to the inspector without making it public — prefer it to public fields.

## The lifecycle: Update vs FixedUpdate vs LateUpdate

- **`FixedUpdate()`** — fixed timestep. All `Rigidbody` physics and force/velocity changes go here, using `Time.fixedDeltaTime`.
- **`Update()`** — once per frame (variable). Input polling and non-physics logic, using `Time.deltaTime`.
- **`LateUpdate()`** — after all Updates. Camera follow and anything that must run *after* its target moved (prevents a one-frame lag).

Critical gotcha: **read input in `Update`, act on it in `FixedUpdate`.** `FixedUpdate` can run zero or multiple times per frame, so polling `GetKeyDown` there drops inputs. Buffer the input in `Update`, consume it in `FixedUpdate`. Use `Time.deltaTime`/`Time.fixedDeltaTime` on everything time-based. (See `game-loop-and-time.md`.)

## Composition with small components

Favor several focused MonoBehaviours (a `Health`, a `Mover`, a `Hurtbox`) over one large one, and over deep inheritance. `GetComponent<T>()` to access siblings — but **cache** the result in `Awake`/`Start`, never call it every frame. Use tags/layers to classify objects rather than type-checking.

## Decoupling: events & ScriptableObject channels

Don't have objects reach into each other. Options, lightest first:
- **C# `event`/`Action`:** `public event Action<int> HealthChanged;` raised by the emitter, subscribed by listeners. Unsubscribe in `OnDisable` to avoid leaks.
- **ScriptableObject event channels** (designer-friendly, idiomatic in modern Unity): an event is an *asset*; emitters `Raise()` it, listeners subscribe. Decouples systems across scenes without singletons. Same idea for shared variables (a `FloatVariable` asset).

Avoid `GameObject.Find`, `SendMessage`, and `FindObjectOfType` in hot paths — slow and brittle. (See `architecture.md`.)

## Movement: kinematic vs Rigidbody

For a precise avatar (platformer/action), prefer **kinematic** control: set velocity and move with collision response rather than applying forces to a dynamic Rigidbody (forces feel floaty and fight your tuning). Two common routes: a kinematic `Rigidbody2D`/`Rigidbody` with `MovePosition` and manual collision, or the `CharacterController` for 3D. Use **dynamic Rigidbodies** for world physics objects (crates, ragdolls), not the player. Enable **continuous collision detection** on fast bodies, and use `Physics.Raycast`/`BoxCast` (or `Physics2D.*`) for fast projectiles to avoid tunneling (see `collision-and-physics.md`). Use the **Input System** package (not legacy `Input.GetKey` everywhere) for rebinding and controller support.

## ScriptableObjects for data

**ScriptableObjects** are the data-driven backbone: define enemy stats, weapon configs, level data as SO assets, author them in the inspector, have logic read them. They live outside scenes, are shared by reference (no duplication), and let designers tune without code. This is the single most idiomatic "separate data from logic" tool in Unity. (See `architecture.md`.)

## Feel: tweening, particles, screenshake

- **Tweening:** Unity has no built-in tween engine; use coroutines for simple cases or a library (DOTween is the standard) for `transform.DOScale(...)`-style juice. Tween instead of snapping.
- **Particle System** for dust/sparks/blood; **Cinemachine** for camera (impulse sources give clean screenshake; follow with damping and a dead zone for camera feel).
- **Time.timeScale** for pause (0) and slow-mo/hitstop; remember UI/audio you want unaffected should use unscaled time (`Time.unscaledDeltaTime`).

## Object pooling

Don't `Instantiate`/`Destroy` bullets, enemies, or particles every frame — it causes GC spikes. Unity provides **`ObjectPool<T>`** (UnityEngine.Pool); use it (or a simple free-list) for anything spawned frequently. (See `collision-and-physics.md`.)

## Common antipatterns

- **`GetComponent`/`Find`/`FindObjectOfType` per frame** → cache in `Awake`/`Start`.
- **Physics or force changes in `Update`** instead of `FixedUpdate` → framerate-dependent physics.
- **Reading `GetKeyDown` in `FixedUpdate`** → dropped inputs. Read in `Update`.
- **Dynamic Rigidbody for a precise avatar** → floaty. Go kinematic.
- **`Instantiate`/`Destroy` in the hot loop** → GC hitches. Pool.
- **public fields everywhere** → use `[SerializeField] private`.
- **God MonoBehaviour** doing everything → split into focused components, communicate via events/SO channels.
- **Missing `Time.deltaTime`** on time-based values → framerate-dependent.
- **Forgetting to unsubscribe** from events in `OnDisable`/`OnDestroy` → leaks and ghost callbacks.
