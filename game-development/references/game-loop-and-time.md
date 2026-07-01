# The Game Loop & Time

The loop is the heartbeat. Getting time wrong here is the most common defect in generated game code, and it produces bugs that *look* like physics or design bugs (jitter, tunneling, "the game runs faster on my friend's PC"). Get this right first.

## Contents
- The three jobs of a loop
- Frame independence: delta time
- The lerp-per-frame antipattern (the subtle one)
- Why raw delta isn't enough: the fixed timestep
- The canonical fixed-timestep loop (with interpolation)
- Determinism
- Pause, slow-motion, and time scale
- Engine-specific notes

## The three jobs of a loop

Every frame does three things, in order: **input → update (simulate) → render**. Keeping these conceptually separate is the foundation of clean game code. Input gathers intent, update advances the simulation by some amount of time, render draws the current state. Don't read input inside your simulation step, and don't mutate game state inside render.

## Frame independence: delta time

A game must behave the same whether it runs at 30, 60, or 240 FPS. The fix is to express every rate **per second** and multiply by `delta` — the seconds elapsed since the last frame.

```
# WRONG — speed is "per frame", so the game runs faster on faster hardware
position.x += 200

# RIGHT — 200 pixels per second, framerate-independent
position.x += 200 * delta
```

This applies to *everything* time-based: movement, gravity, timers/cooldowns, animation, lerping, resource regen. A cooldown is `cooldown -= delta`, not `cooldown -= 1`.

One subtlety: naive Euler integration with variable delta makes acceleration slightly framerate-dependent and can wobble. For simple games it's tolerable; for anything where consistency matters, use a fixed timestep (below).

## The lerp-per-frame antipattern (the subtle one)

`lerp(current, target, 0.1)` called every frame is **framerate-dependent** in a way that catches almost everyone. At 60 FPS you apply the factor 60× per second; at 120 FPS, 120×. The camera (or whatever you're smoothing) catches up twice as fast on faster hardware.

The naive "fix" of multiplying by delta — `lerp(current, target, 0.1 * delta)` — is **also wrong**. The rate now becomes nearly zero (0.1 × 0.016 ≈ 0.0017 per frame) and produces a completely different convergence curve.

The correct fix uses **exponential decay**, which is what "approach a fraction per frame" actually means mathematically (successive lerps compound multiplicatively):

```gdscript
# WRONG — framerate-dependent
position = lerp(position, target, 0.1)

# ALSO WRONG — naive delta multiply has different math, not just slower
position = lerp(position, target, 0.1 * delta)

# RIGHT — exponential decay, framerate-independent
# decay = fraction of distance REMAINING after 1 second (0.0 = instant, 0.9 = very slow)
# A decay of 0.01 means 1% remains after 1 second — very fast
const DECAY := 0.05  # 5% remains after 1 second
position = lerp(position, target, 1.0 - pow(DECAY, delta))
```

The `pow(decay, delta)` term computes how much of the gap survives for the actual elapsed time, regardless of FPS. The alternative is to move all smooth-following logic into `_physics_process` (Godot) / `FixedUpdate` (Unity), which runs at a fixed rate and makes the naive per-frame form acceptable since `delta` is always the same.

This antipattern is most visible in cameras, UI animations, and any "ease toward target" logic. It's one of the most common subtle framerate bugs in otherwise correct-looking code.

## Why raw delta isn't enough: the fixed timestep

Variable `delta` breaks down for physics and collision:

- **Tunneling:** a fast object can move so far in one big frame that it passes *through* a wall without ever overlapping it. (See `collision-and-physics.md` for swept collision, the other half of the fix.)
- **Non-determinism:** the same inputs produce different results depending on frame timing, which makes replays, lockstep multiplayer, and reproducible bugs impossible.
- **Instability:** spring/joint/integration math behaves differently at different step sizes; a frame spike can blow it up.

The fix: advance the **simulation** in fixed-size steps (commonly 1/60 s), regardless of how long the frame actually took. Render as often as the display allows, interpolating between the last two simulation states so motion stays smooth.

## The canonical fixed-timestep loop

This is the "fix your timestep" pattern (Gaffer on Games). Memorize its shape — it's the same in every language:

```
const STEP = 1.0 / 60.0   # fixed simulation step, in seconds
accumulator = 0.0
previous_state = current_state

while running:
    frame_time = clock.tick()          # real seconds since last frame
    frame_time = min(frame_time, 0.25) # clamp to avoid "spiral of death" after a stall
    accumulator += frame_time

    input = poll_input()

    while accumulator >= STEP:
        previous_state = current_state
        current_state = simulate(current_state, input, STEP)  # always advance by STEP
        accumulator -= STEP

    alpha = accumulator / STEP          # 0..1 leftover fraction
    render(lerp(previous_state, current_state, alpha))
```

Key points:
- `simulate` always receives the **same** `STEP`, so physics is consistent and deterministic.
- The inner `while` runs zero, one, or several times per frame depending on how the render and sim rates relate.
- **Clamp** `frame_time` so a long stall (debugger breakpoint, OS hiccup) doesn't queue hundreds of catch-up steps — the "spiral of death."
- **Interpolate** on render with `alpha` so you don't get visual stutter when sim and display rates don't divide evenly. Skipping interpolation is acceptable for an early prototype; skipping the fixed step is not.

Most engines give you a version of this for free — use it rather than rolling your own (below). The point is to *understand* which callback is which.

## Determinism

A deterministic simulation produces identical output from identical input every time. You need it for replays, lockstep networking, and reliably reproducing bugs. To get it:

- **Fixed timestep** (above) — non-negotiable for determinism.
- **Seed your RNG** and thread that seed through the simulation; never call a global unseeded random in sim code.
- **Be wary of floating point.** Float results can differ across compilers/platforms. For single-machine replays, normal floats are usually fine; for cross-platform lockstep, you may need fixed-point or to keep the sim integer-based.
- **Order matters.** Iterate entities/systems in a stable, defined order. Iterating a hash map with nondeterministic order will desync.
- **Keep sim and render state separate.** Anything that reads the clock, the mouse position, or wall-time inside the simulation breaks determinism.

Don't over-engineer this: a single-player game with no replays doesn't need bit-exact determinism. Reach for it when a feature actually requires it.

## Pause, slow-motion, and time scale

Because everything is already expressed in terms of `delta`/`STEP`, time effects are easy and this is where a lot of *game feel* comes from (hitstop, bullet-time):

- **Pause:** stop calling `simulate` (or multiply the sim's delta by 0). Keep rendering and keep the UI/menu loop running on real time.
- **Slow-mo / fast-forward:** scale the time you feed the simulation: `simulate(state, input, STEP * time_scale)`. With a fixed timestep, prefer scaling how many steps you take or use a separate accumulator rather than changing `STEP` itself (changing the step size hurts determinism).
- **Hitstop / freeze frames:** briefly set `time_scale` to 0 (or skip sim steps) for a few frames on impact. Tiny in code, huge in feel — see `game-feel.md`.

Keep a distinction between **game time** (pausable, scalable) and **real time** (menus, some animations, music). Don't run your pause menu on game time or it'll freeze with the game.

## Engine-specific notes

- **Godot:** `_physics_process(delta)` runs on a fixed step (default 60 Hz, set by `physics_ticks_per_second`) — put movement, physics, and anything needing consistency here. `_process(delta)` runs once per rendered frame (variable) — use it for cosmetic/visual updates and UI. A frequent generated-code bug is doing movement in `_process`; move it to `_physics_process`.
- **Unity:** `FixedUpdate()` is the fixed-step callback — do `Rigidbody` physics and force application here, using `Time.fixedDeltaTime`. `Update()` is per-frame (variable) — input polling and non-physics logic, using `Time.deltaTime`. Reading input in `FixedUpdate` can drop inputs because it may run zero times in a frame; read in `Update`, consume in `FixedUpdate`. Use `Time.timeScale` for pause/slow-mo.
- **Code-first (LÖVE/PyGame/Bevy/Macroquad):** you own the loop. LÖVE gives you `love.update(dt)` and `love.draw()`; you add the accumulator if you want a fixed step. PyGame: `dt = clock.tick(60) / 1000.0`. Bevy: use `FixedUpdate` schedule for sim, `Update` for per-frame. In all of these, implement the accumulator pattern above for anything physics-driven.
