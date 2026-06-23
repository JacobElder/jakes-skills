---
name: game-development
description: Procedural knowledge for designing and coding video games — game loops, game feel/juice, entity architecture, collision and physics, character controllers, enemy AI and pathfinding, procedural generation, the prototype-to-ship process, pixel art and retro games, and 3D game development — plus opinionated engine selection across Godot, Unity, Bevy, LÖVE, PyGame, and Phaser. Use this whenever the user wants to build, prototype, or improve a game or game system, including character and platformer controllers, game loops, collision, enemy AI, spawning, pathfinding or flow fields, procedural level and content generation, making a game feel juicier, fixing framerate-dependent movement, choosing an engine, or scoping a game so it ships. Also trigger on Godot, Unity, Bevy, LÖVE/love2d, Pygame, Phaser, GDScript, sprites, tilemaps, ECS, or game jams, or a bare genre like platformer, roguelike, shooter, survivors-like, puzzle, top-down, action-RPG, JRPG, farming sim, or 3D platformer. Trigger on pixel art, pixel-perfect, retro, 8-bit, 16-bit, Stardew-like, Zelda-like, Final Fantasy-like, TileMap, spritesheet, turn-based combat, dialogue system, or wanting to make a pixel art game. Trigger on 3D controller, third-person camera, first-person shooter, SpringArm, NavigationAgent, skeletal animation, blend tree, LOD, NavMesh, CharacterBody3D, or any 3D game question. The patterns go well beyond default code generation.
---

# Game Development

## What this skill is for

Default code generation produces games that **compile but feel dead**: movement tied to frame rate, a single god object with a 400-line `update()`, instant state changes with no weight, collision that tunnels at speed, and a scope so large the project never ships. This skill encodes the procedural knowledge that separates that from games that feel good and get finished.

The audience is small-scale games — solo and small-team 2D (including pixel art and retro-style), plus modest 3D. Everything here is scoped to what one person or a few people can actually build and ship. It is engine-aware but engine-agnostic at the core: the loop, the feel, the architecture, and the process matter more than the tool.

## The five non-negotiables

These apply to **every** game and every engine. Violating one is the difference between "a programmer made this" and "this is a game." Check your output against all five before you hand back code.

**1. Frame independence — never tie simulation to frame rate.** Movement, physics, timers, and animation must be expressed per *second*, then multiplied by `delta` (elapsed time), or stepped on a **fixed timestep**. `position += speed` is a bug; `position += speed * delta` is correct. Anything with physics, collision, or determinism needs a fixed timestep, not raw delta. This is the single most common defect in generated game code. → `references/game-loop-and-time.md`

**2. Find the fun before you build the game.** The first thing you build is the smallest interactive *toy* that proves the core loop is fun — a character that moves, a thing that shoots, a block that falls. Not menus, not save systems, not an inventory. If the toy is not fun, no amount of content fixes it. Scope is the number-one killer of small games; treat every system as a cost to justify, not a feature to add. → `references/production-and-scope.md`

**3. Decouple — composition and messages, not god objects and inheritance.** Build behavior from small composable pieces (components/nodes/systems), and let them communicate through events/signals/messages rather than reaching into each other. A `Player` should *emit* "took damage," not call `hud.health_bar.set_value(...)` directly. Prefer composition over deep inheritance hierarchies — the `Goblin extends Enemy extends Character extends Entity` tree is a classic trap that gets painful fast. For many-entity games (survivors-like, bullet-hell, RTS) with hundreds or thousands of objects on screen, explicitly adopt an **ECS (Entity-Component-System)** architecture or its close equivalent: each "thing" is an ID, and behavior is in pure Systems that operate on arrays of component data — this is what keeps update loops fast and avoids the god-object spiral at scale. → `references/architecture.md`

**4. Juice is core, not polish you add later.** "Game feel" — the moment-to-moment tactile response — is most of why a game feels good, and it is cheap. Every action gets feedback across multiple channels: a **tween with an easing curve** (never an instant snap), a sound, a particle burst, a hitstop, a screenshake, and a **squash-and-stretch** on characters/projectiles in 2D. When a player says movement feels "floaty" or hits feel "weak," the missing ingredients are almost always (a) tweening/easing on position and animation transitions rather than instant snaps, (b) squash-stretch on jump arcs and landings, (c) hitstop on contact, and (d) camera trauma. Name all of these when diagnosing game feel. Budget for juice in the *first* prototype, not the last sprint. → `references/game-feel.md`

**5. Choose the engine deliberately.** Do not default to whatever is most familiar from training data. Match the tool to the project and the person. There is a real default (Godot 4.x for most small 2D and indie 3D) but also real exceptions. → `references/engine-selection.md`

## Routing — read the reference that fits the task

Read the relevant reference file(s) before writing substantial code. They contain the specifics, code patterns, and engine idioms; this file is just the map. Most non-trivial tasks need two or three.

| If the task involves… | Read |
|---|---|
| Picking an engine/language, or "what should I build this in?" | `references/engine-selection.md` |
| The main loop, update/tick order, delta time, fixed timestep, pause, slow-mo, determinism, replays | `references/game-loop-and-time.md` |
| Project structure, decoupling, state machines, events/signals, components, data-driven design, save systems | `references/architecture.md` |
| Making it feel good: movement feel, screenshake, hitstop, tweening/easing, particles, input buffering, coyote time, audio feedback | `references/game-feel.md` |
| Collision detection, spatial partitioning, "lots of objects on screen," character/platformer controllers, projectiles | `references/collision-and-physics.md` |
| Enemy behavior, AI, steering, flocking, pathfinding, navmesh, flow fields, "enemies that chase / don't pile up," targeting/aggro | `references/enemy-ai.md` |
| Procedural generation, random levels/dungeons, seeds, loot/reward tables, wave/spawn directors, "make it fair" randomness | `references/procedural-generation.md` |
| Scoping, prototyping, "I never finish games," vertical slice, playtesting, milestones, shipping | `references/production-and-scope.md` |
| Anything in **Godot / GDScript** | `references/engines/godot.md` |
| Anything in **Unity / C#** | `references/engines/unity.md` |
| **Code-first** engines: LÖVE/Lua, PyGame, Phaser/JS, Bevy/Rust, Macroquad | `references/engines/code-first.md` |
| **Pixel art / retro games**: blurry pixels, integer scaling, pixel-perfect setup, TileMap, top-down Zelda-like, grid-locked movement, 4-directional animation, screen transitions, JRPG turn-based combat, ATB, dialogue systems, sprite sheets, retro aesthetics, Stardew-like farming sim | `references/pixel-art-and-retro.md` |
| **3D games**: CharacterBody3D, third-person camera, SpringArm, first-person controller, camera-relative movement, 3D pathfinding, NavigationAgent3D, baked vs real-time lighting, LOD, skeletal animation, blend trees, AnimationTree, modular level design, GridMap | `references/3d-games.md` |

## Opinionated defaults (the one-screen version)

When the user has not specified otherwise, these are the stances to take. Each is defended in the references — state the recommendation plainly, then give the one-line reason, and only expand if asked. Do not hedge them into mush.

- **New small 2D or indie 3D game → Godot 4.x.** Free forever (MIT), best-in-class dedicated 2D pipeline, fast iteration, GDScript reads like Python. Exceptions: console-at-launch or VR/XR or you already live in Unity → **Unity 6.x**; photoreal AAA 3D → **Unreal**; you're Rust-native and the game is simulation-heavy → **Bevy**; pure-code learning project or you want to understand the loop from scratch → **LÖVE** (Lua) or **PyGame** (Python); casual web game → **Phaser**; one-week jam prototype in Rust → **Macroquad**.
- **Simulation runs on a fixed timestep; rendering interpolates.** Variable `delta` is fine for purely cosmetic motion, but anything physics-y, deterministic, or networked needs fixed steps.
- **Composition over inheritance, always.** When you catch yourself drawing a class tree more than two levels deep, switch to components.
- **Pool anything you spawn frequently** — bullets, enemies, particles, damage numbers. Allocating in the hot loop causes GC hitches and frame spikes.
- **Separate data from code.** Enemy stats, level layouts, dialogue, and tuning values belong in data files / resources / ScriptableObjects, not hardcoded in logic. It makes tuning (the bulk of game work) fast.
- **Tune by feel, with numbers exposed.** Expose movement and feel constants (jump height, coyote time, acceleration, screenshake magnitude) as editable values, because they will be changed dozens of times during playtesting.
- **Pixel art games need two settings, not one.** Texture filter must be **Nearest** (not Linear/Bilinear) and scaling must be an integer factor of the base resolution. Getting one wrong produces blurry or shimmering pixels. In Godot: Project Settings → Rendering → Textures → Canvas Textures → Default Texture Filter → Nearest, and Stretch Mode → canvas_items with a small base resolution. → `references/pixel-art-and-retro.md`
- **3D character controllers are kinematic, not physics-based.** CharacterBody3D (Godot) or a kinematic Rigidbody controller (Unity) gives the precise authored feel players expect. Leaving movement to forces-and-impulses on a RigidBody produces fighting-the-physics-engine sludge. The 3D platformer feel techniques (coyote time, variable jump, asymmetric gravity, camera-relative input) are the same as 2D. → `references/3d-games.md`
- **3D camera: always use a SpringArm.** A Camera3D parented directly to the player has no wall-clip protection. A SpringArm3D pivot rig (Player → CameraPivot → SpringArm3D → Camera3D) auto-shortens when geometry is in the way, eliminates clipping for free. → `references/3d-games.md`

## How to approach a game-dev request

1. **Establish the target.** Engine/language, genre, scope, and the person's experience level. If they haven't said, infer a sensible default from context and *state your assumption* rather than stalling — but if engine choice materially changes the answer and is genuinely ambiguous, ask once.
2. **Anchor on the core loop.** Identify the 10-second loop (move → shoot → dodge → collect). Build or design that first. Resist scaffolding menus, saves, and meta-systems until the loop is proven.
3. **Read the right references** and write code that honors the five non-negotiables.
4. **Bake in feel from the start** — even a prototype gets delta-correct motion, a tween or two, and a sound hook.
5. **Name the next cut.** When you hand back work, point at the smallest next step and flag what to *not* build yet. Protecting scope is part of the help.

## Self-check before handing back

Default code generation produces plausible game code that quietly violates the basics; the failure is rarely visible until the game runs. Before returning, audit your own output against these — they're where generated game code most often goes wrong:

- **Every time-based value is multiplied by `delta` / stepped on a fixed timestep.** Scan for any movement, gravity, timer, or lerp that isn't. (And in Godot/Unity, movement is in `_physics_process`/`FixedUpdate`, not `_process`/`Update`.)
- **No god object.** If one class/script is doing movement *and* combat *and* UI *and* audio, split it and emit signals/events instead.
- **At least one feel element on the key action.** A tween with easing (not an instant snap), a sound hook, or a particle — even in a prototype. If you wrote a jump/hit/pickup with zero feedback, add it or flag it. When diagnosing "floaty" or "weak," name tweening/easing, squash-stretch, hitstop, and screenshake by name — not just "add particles."
- **Spawned-in-a-loop things are pooled; many-object collision uses a spatial structure**, not allocation-per-frame and not O(n²) all-pairs.
- **Feel/tuning constants are exposed** (`@export` / `[SerializeField]` / data), not buried as magic numbers.
- **Scope is honest.** You built/spec'd the core loop, not a menu-and-save-system scaffold around an unproven idea.
- **Pixel art games: check both Nearest filter AND integer scaling.** Blurry pixels almost always mean one of the two is wrong. Also check that the camera position is rounded to the nearest integer — sub-pixel camera positions cause tile shimmer even with correct filtering.
- **3D controllers: CharacterBody3D (not RigidBody3D) for the player, camera in a SpringArm3D rig.** If you wrote a 3D controller, verify movement uses `move_and_slide()` with manual velocity, not forces/impulses. If you wrote a third-person camera, verify it sits inside a SpringArm3D (not parented directly to the player). Verify input direction is rotated by the camera basis before being applied to velocity.

If output violates one, fix it or call it out explicitly — silently shipping the default mistake is the thing this skill exists to prevent.
