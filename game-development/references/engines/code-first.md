# Code-First Engines: LÖVE, PyGame, Phaser, Bevy, Macroquad

No scene editor — you write the loop, the rendering calls, and the structure yourself. That's the point when the goal is understanding or total control. The core references still apply in full (you'll *implement* the fixed timestep, the pooling, the FSM rather than getting them from an editor). This file gives the per-framework shape and the gotchas.

## Contents
- What "code-first" changes
- LÖVE (Lua)
- PyGame (Python)
- Phaser (JS/TS)
- Bevy (Rust, ECS)
- Macroquad (Rust)
- Shared discipline

## What "code-first" changes

You own three things the editor engines hand you: the **main loop** (implement the accumulator/fixed-timestep from `game-loop-and-time.md` yourself for anything physics-y), **structure** (no node tree — impose your own composition/ECS and event system from `architecture.md`), and **everything else** (input mapping, pooling, scenes/states, asset loading). The upside is no magic and no licensing; the cost is more boilerplate. Choose code-first for learning, for jams in a language you love, or for web/Rust targets.

## LÖVE (Lua)

The cleanest pure-2D learning engine. Three callbacks:

```lua
function love.load() end                 -- init
function love.update(dt) end             -- dt = seconds since last frame
function love.draw() end                 -- immediate-mode drawing
```

- `dt` is variable — for physics, add the accumulator/fixed-step yourself. Multiply everything time-based by `dt`.
- Immediate-mode rendering: you draw the whole frame in `love.draw()` every frame.
- Input via `love.keyboard.isDown`/callbacks; `love.audio` for sound; `love.graphics` for sprites/shapes.
- Structure: Lua tables as entities/components; a simple state stack for screens (menu/play/pause); a tiny pub-sub table for events. Libraries: `hump` (gamestate, timer, vector), `anim8` (sprite animation), `bump` (AABB collision with swept resolution — saves you writing tunneling-safe collision), `baton` (input). For a many-entity survivors-like, a bundled uniform-spatial-hash + object-pool reference ships at `assets/love_spatial_hash_pool.lua`.
- Ships easily cross-platform; great for jams. Lua is small and forgiving (watch for `nil` and 1-based indexing).

## PyGame (Python)

Right specifically when the user is a Python person building a toy/learning game and wants to stay in Python. Be honest that it's not the path to a polished commercial title (performance and distribution are weaker) — for that, steer a Python dev to **Godot** (GDScript transfers almost directly).

```python
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000.0          # seconds; multiply time-based values by dt
    for event in pygame.event.get(): ...  # input
    update(dt)
    screen.fill(bg); draw(screen); pygame.display.flip()
```

- `pygame.sprite.Group` gives basic batching/collision (`spritecollide`); fine for small counts. For many objects, add a spatial grid yourself (see `collision-and-physics.md`).
- It's a low-level multimedia library, not a full engine: no scene system, you build state management, you build pooling. Use `Vector2`, blit sprites, `pygame.mixer` for audio.
- Watch the framerate-independence trap especially hard here — naive PyGame tutorials often omit `dt`.

## Phaser (JS/TS)

The default for a casual **web** 2D game. Scene-based, batteries-included for web:

- `Scene` objects with `preload()` / `create()` / `update(time, delta)` — `delta` is in **milliseconds**.
- Built-in **Arcade Physics** (fast AABB, good for platformers/top-down) or **Matter.js** (full rigid-body) — use Arcade unless you need real physics.
- Built-in tweens (`this.tweens.add(...)`), particles, input, audio, asset loader, sprite atlases — good juice support out of the box.
- Ships as a webpage; trivial to embed on itch.io or your site. TypeScript strongly recommended for anything non-trivial.

## Bevy (Rust, ECS)

Data-oriented **ECS** engine. Correct when the user is Rust-native and the game is simulation-heavy. Pre-1.0 (0.18 as of early 2026) with **breaking changes ~quarterly** — pin your version and expect migration on upgrade; check current-version syntax rather than trusting memory.

- **Entities** are IDs, **Components** are plain structs, **Systems** are functions over queries (`Query<(&mut Transform, &Velocity)>`). The scheduler runs systems in parallel automatically (the borrow checker proves safety).
- Use the **`FixedUpdate`** schedule for simulation, **`Update`** for per-frame. Multiply by the fixed step / `Time` delta accordingly.
- You assemble the stack from crates: **Avian** (Bevy-native) or **Rapier** for physics, **leafwing-input-manager** for input (near-mandatory beyond toys), **bevy_ecs_tilemap** for 2D tiles, **bevy_kira_audio** for audio. The 2D tooling story is surprisingly good.
- Don't put Bevy in front of someone who isn't already comfortable in Rust — Rust + ECS + moving API is too much for a first game. Validate with a one-week web-build prototype before committing a real project.

## Macroquad (Rust)

Minimal, Raylib-inspired, near-zero-friction Rust 2D. Ideal for a **one-week jam** or learning Rust gamedev without ECS ceremony:

```rust
#[macroquad::main("Game")]
async fn main() {
    loop {
        let dt = get_frame_time();   // seconds
        // update with dt, then draw
        next_frame().await;
    }
}
```

Trivial WASM builds for web. Prototype here; port to Bevy later only if the idea earns the heavier architecture. Other Rust options: **ggez** (comfortable 2D defaults), **Fyrox** (full 3D engine with editor).

## Shared discipline

Because nothing is handed to you, the core-reference patterns aren't optional niceties — they're things you must actively implement:
- **Fixed timestep accumulator** for anything physics/deterministic (`game-loop-and-time.md`).
- **A state/scene stack** (menu → play → pause) — don't cram everything into one `update`.
- **An event/pub-sub layer** for decoupling (`architecture.md`).
- **Object pooling** and a **spatial grid** the moment object counts climb (`collision-and-physics.md`).
- **Data in files** (JSON/TOML/Lua tables), not hardcoded.
- **Game feel from day one** — these frameworks give you direct control over tweening/shake/particles, so there's no excuse to skip juice (`game-feel.md`).
