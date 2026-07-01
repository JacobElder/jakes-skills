# Collision, Physics & Character Controllers

Two distinct problems live here: **collision** (detecting and resolving overlaps, performantly, with many objects) and **character control** (making a player-controlled body move in a way that feels good). Generated code tends to do naive O(n²) checks, discrete collision that tunnels at speed, and floaty controllers with no game feel. This file fixes all three.

## Contents
- Use the engine's physics — until you shouldn't
- Collision shapes & the broad/narrow phase split
- AABB and the separating-axis idea
- The tunneling problem and swept/continuous collision
- Spatial partitioning for many objects
- Object pooling
- The platformer character-controller recipe
- Top-down and other controllers
- Collision layers/masks

## Use the engine's physics — until you shouldn't

For most small games, **use the engine's built-in collision/physics** rather than writing your own: Godot's `CharacterBody2D`/`move_and_slide` and area/body detection, Unity's `Rigidbody`/`Collider`, Bevy's Avian/Rapier. They handle the hard cases (resolution, slopes, continuous detection) and are well-tested.

The big exception that trips people up: **don't use a full rigid-body dynamics simulation for a player character.** Platformer and most action protagonists feel best with a **kinematic** controller — you set velocity and move the body explicitly with collision response, rather than applying forces to a dynamic rigid body and hoping it feels right. Forces give you "realistic" but floaty, hard-to-tune movement; kinematic control gives you the crisp, authored feel players expect. Use dynamic rigid bodies for *physics objects* in the world (crates, ragdolls, debris), kinematic for the avatar.

Write your own collision only when you specifically need it: a deterministic lockstep sim, a very large number of simple objects where the engine's general solver is overkill, or a learning project. The rest of this file is what you need then (and to understand what the engine is doing).

## Collision shapes & the broad/narrow phase split

Cheapest shapes first: **circle/sphere** (distance check) and **axis-aligned bounding box / AABB** (min/max compare) are the workhorses; use them for the vast majority of gameplay collision. Reserve oriented boxes, polygons, and per-pixel checks for when you truly need them — they're far costlier.

Collision detection splits into two phases, and conflating them is why naive code is slow:
- **Broad phase:** quickly find *candidate* pairs that *might* collide, cheaply, using a spatial structure (below). Throws out the vast majority of pairs.
- **Narrow phase:** do the exact shape-vs-shape test only on those candidates.

## AABB and the separating-axis idea

AABB overlap is the bread and butter of 2D collision:

```
overlap = a.min.x < b.max.x and a.max.x > b.min.x
      and a.min.y < b.max.y and a.max.y > b.min.y
```

If there's a gap on *any* axis, they don't overlap — that's the separating-axis idea in its simplest form. To **resolve** an AABB overlap, compute penetration depth on each axis and push out along the axis of *least* penetration (smallest correction), which gives natural sliding along walls and floors.

## The tunneling problem and swept/continuous collision

Discrete collision checks position *after* a move. A fast object (a bullet, a falling player at high speed) can jump from "before the wall" to "past the wall" in one step, never overlapping it, and pass straight through. This is **tunneling**, and it's the collision half of the fixed-timestep story (`game-loop-and-time.md` is the time half).

Fixes, in order of preference for a small game:
1. **Fixed timestep** with small enough steps so per-step movement is less than the thinnest collider — solves most cases for free.
2. **Continuous / swept collision:** instead of testing the destination point, test the *swept* volume along the movement vector (a ray or a swept AABB) and stop at the first contact. Engines expose this (Godot: `move_and_collide` is swept; Unity: continuous collision detection on the Rigidbody, or `Physics.Raycast`/`BoxCast` for fast projectiles). For a bullet, raycast from last position to new position rather than checking the bullet's box at its new spot.
3. **Substep** very fast objects: split a big move into several small ones and check each.

If you're writing your own, swept AABB ("slab" / minkowski) gives the time-of-impact `t` in [0,1]; move to `t`, resolve, and optionally slide with the remaining motion.

## Spatial partitioning for many objects

Checking every object against every other is **O(n²)** — fine for 20 objects, catastrophic for 2,000 (the survivors-like / bullet-hell case). The broad phase needs a spatial structure so each object only checks nearby ones:

- **Uniform grid (spatial hash):** divide space into cells (cell size ≈ the typical object size or query radius); bucket each object into the cell(s) it overlaps; only test objects sharing or neighboring a cell. Simple, fast, and the right default for games with many similarly-sized objects spread out — e.g. a Vampire-Survivors-like with hundreds of enemies and projectiles.
- **Quadtree (2D) / octree (3D):** recursively subdivide; better when object sizes/densities vary a lot. More overhead than a grid; only reach for it when a uniform grid's cell sizing is awkward.
- Many engines do broad-phase for you; this matters most when you write your own collision or do custom queries (e.g. "all enemies within range" every frame — back that with a grid, not a full scan).

The general move: when "lots of things on screen" performance is the ask, the answer is almost always **a spatial structure for the broad phase plus object pooling**, not micro-optimizing the inner check. A complete, runnable **LÖVE** implementation of a uniform spatial hash + object pool (the survivors-like core) ships at `assets/love_spatial_hash_pool.lua` — adapt it rather than rebuilding the broad phase from scratch.

## Object pooling

Spawning and freeing objects every frame (bullets, particles, enemies, damage numbers) causes allocation churn and GC hitches — visible frame spikes. **Pool** them: pre-allocate a set of reusable instances, take an inactive one on "spawn," return it to the pool on "despawn" (deactivate, don't destroy). Essential for bullet-hell, survivors-likes, and any heavy-particle game. In Godot, keep freed nodes in a list and `reset` them; Unity has a built-in `ObjectPool<T>`; code-first, a simple free-list.

## The platformer character-controller recipe

A jump that just sets `velocity.y` feels bad and unfair. This is the standard set of techniques that make a 2D platformer feel tight and responsive — popularized by Celeste and GMTK's platformer-toolkit work. Implement movement in the **fixed-step** callback (`_physics_process` / `FixedUpdate`), with these on top:

- **Acceleration & deceleration, not instant velocity.** Ramp horizontal speed up and down over a few frames (higher accel than decel often feels good), instead of snapping to max speed. Optionally lower control while airborne.
- **Asymmetric gravity.** Apply *more* gravity when falling than when rising (e.g. fall gravity 1.5–2× rise gravity). Floaty-up, snappy-down feels far better than symmetric.
- **Variable jump height.** Full jump if the button is held; if released early while rising, cut upward velocity (e.g. halve it). Gives precise control between a hop and a full leap.
- **Coyote time.** Allow the jump for a few frames (~0.1 s) *after* walking off a ledge. Players press jump a hair late constantly; without this the game feels broken even though it's "correct."
- **Jump buffering.** If the player presses jump a few frames *before* landing, remember it and jump on touchdown. Same forgiveness at the other end of the jump.
- **Apex modifiers (optional, great feel).** Slightly reduce gravity and grant a touch more horizontal speed at the top of the arc — players read the apex as a moment of control.
- **Corner correction / nudging (optional).** If a jump clips a corner by a pixel or two, nudge the player around it instead of stopping them dead.
- **Clamp fall speed** (terminal velocity) so long falls don't tunnel or feel out of control.

Expose every one of these as a tunable constant — they get adjusted dozens of times by feel. Then layer the *visual* feel from `game-feel.md` (squash/stretch, dust, sound, screenshake on land, coyote/buffer are feel too). The combination is the whole ballgame for platformers.

> A complete, tuned **Godot 4 reference implementation** of this recipe — coyote time, jump buffer, variable height, asymmetric gravity, accel/decel, plus squash/stretch and juice hooks, all `@export`-tunable — ships with this skill at `assets/godot_platformer_controller.gd`. Adapt it to the engine at hand rather than rebuilding the recipe from scratch.

```
# sketch (fixed-step), engine-agnostic
if on_floor: coyote = COYOTE_TIME else: coyote -= STEP
if jump_pressed: buffer = JUMP_BUFFER else: buffer -= STEP

if buffer > 0 and coyote > 0:
    velocity.y = -JUMP_VELOCITY
    buffer = 0; coyote = 0
if jump_released and velocity.y < 0:
    velocity.y *= 0.5                      # variable height

g = FALL_GRAVITY if velocity.y > 0 else RISE_GRAVITY
velocity.y = min(velocity.y + g * STEP, MAX_FALL)

target = input_dir * MAX_SPEED
rate = ACCEL if input_dir != 0 else DECEL
velocity.x = move_toward(velocity.x, target, rate * STEP)
move_with_collision(velocity * STEP)
```

## Top-down and other controllers

- **Top-down (8-way / twin-stick):** normalize the input vector so diagonals aren't faster (`/ sqrt(2)`), then apply the same accel/decel ramp for weight. No gravity; otherwise the feel principles carry over.
- **Grid-based (roguelike/puzzle):** movement is discrete cell-to-cell; animate the *visual* sliding between cells with a tween while the *logical* position snaps instantly — keeps logic simple and motion smooth.
- **Physics-y (e.g. a vehicle, a slime):** here a dynamic rigid body with tuned drag/friction can be the right call; the kinematic rule is specifically about precise avatar control.

## Collision layers/masks

Use the engine's **layers and masks** to control *what collides with what* (player vs. enemy vs. environment vs. pickups vs. enemy-bullets vs. player-bullets) instead of branching in code. It's faster (the engine skips non-matching pairs entirely) and cleaner. Lay out your layers early — it's annoying to retrofit. A typical 2D set: World, Player, PlayerHurtbox, Enemy, EnemyHurtbox, PlayerProjectile, EnemyProjectile, Pickup.
