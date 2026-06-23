# Game Development Skill

A skill that gives the agent the procedural knowledge to build games that feel good and ship — not just games that compile. It encodes the techniques that separate "a programmer made this" from "this is a game": frame-independent movement, asymmetric jump gravity with coyote time and jump buffering, the juice toolkit (hitstop, trauma-based screenshake, tweening/easing, squash-and-stretch), ECS architecture for many-entity games, spatial-hash collision for hundreds of objects, flow-field pathfinding for enemy hordes, and the prototype → vertical-slice → ship process that prevents projects from dying in scope creep.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/game-development
```

Or manually:

```bash
cp -r jakes-skills/game-development ~/.claude/skills/game-development
```

Once installed, the skill applies automatically when the user wants to build or improve a game in Godot, Unity, LÖVE, PyGame, Bevy, or Phaser — including character controllers, collision, enemy AI, procedural generation, game feel, engine selection, or scoping a project.

---

## Example use cases

### "My platformer movement feels floaty"

> My 2D Unity action game technically works but it feels lifeless and floaty, and hitting enemies has no impact. What can I do?

Without the skill, the response covers hitstop, screenshake, particles, and sound — but never mentions tweening/easing on animation transitions or squash-and-stretch, which are the primary culprits for "floaty" character feel:

> **Hits feel weightless — add hitstop first.** When a developer says "I added particles, sounds, and screenshake but hits still feel weak," the missing ingredient is almost always hitstop...
>
> **Add screenshake on hits.** Screenshake pairs with hitstop to sell impact. The right implementation uses a trauma value, not a fixed shake...
>
> **Spawn hit particles.** A small burst of sparks or blood on contact...
>
> **Sound on every action.** Sound is the cheapest high-impact improvement. Wire an impact sound to every hit, with pitch randomization to prevent machine-gun sameness...

With the skill, the response leads with tweening/easing and squash-and-stretch as named, primary techniques alongside hitstop and screenshake:

> ## 1. Floaty movement — fix the controller architecture and add easing
>
> Before adding any juice, check whether your player uses a **dynamic Rigidbody2D driven by forces**. If it does, that's your floatiness — forces feel slippery because you're fighting the physics engine's momentum model. The fix is architectural: switch to a **kinematic Rigidbody2D** and set velocity directly...
>
> ### Tweening and easing on animation transitions
>
> **Instant snaps from idle → run → idle are a major source of "floatiness."** The fix is to tween or blend transitions rather than cutting between them.
>
> ```csharp
> // Wrong: instant snap
> transform.localScale = new Vector3(1f, 1f, 1f);
>
> // Right: tween with an easing curve
> transform.DOScale(new Vector3(1f, 1f, 1f), 0.1f).SetEase(Ease.OutBack);
> ```
>
> ## 2. Squash-and-stretch on the player character
>
> **Squash-and-stretch is the single most effective tool for making 2D characters feel alive.** Without it, characters look pasted onto the world. Apply on jump takeoff, landing, and attack:
>
> ```csharp
> // On jump:
> transform.DOKill();
> transform.DOScaleY(0.7f, 0.05f).SetEase(Ease.OutQuad)
>     .OnComplete(() =>
>         transform.DOScaleY(1.2f, 0.08f).SetEase(Ease.OutQuad)
>     );
>
> // On land:
> transform.DOScaleY(0.6f, 0.04f).SetEase(Ease.OutQuad)
>     .OnComplete(() =>
>         transform.DOScale(Vector3.one, 0.12f).SetEase(Ease.OutBounce)
>     );
> ```
>
> Keep the deformation subtle (0.7–1.3 range) unless your art style is intentionally cartoonish. The goal is subconscious weight, not obvious distortion.

---

### "My Godot platformer character feels floaty when jumping"

> I'm making a platformer in Godot 4. My character can jump but it feels floaty and imprecise. The movement is all done in _process. What's wrong and how do I fix it?

Without the skill, the response moves physics to `_physics_process` and gives gravity, but generates symmetric-gravity code without coyote time, jump buffering, or variable jump height:

> ```gdscript
> extends CharacterBody2D
>
> const SPEED = 200.0
> const JUMP_VELOCITY = -400.0
> var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")
>
> func _physics_process(delta):
>     if not is_on_floor():
>         velocity.y += gravity * delta
>     if Input.is_action_just_pressed("ui_accept") and is_on_floor():
>         velocity.y = JUMP_VELOCITY
>     var direction = Input.get_axis("ui_left", "ui_right")
>     velocity.x = direction * SPEED
>     move_and_slide()
> ```

With the skill, the response produces the complete platformer recipe — asymmetric gravity, coyote time, jump buffer, and variable jump height:

> ```gdscript
> extends CharacterBody2D
>
> @export var speed: float = 200.0
> @export var jump_velocity: float = -480.0
> @export var gravity_up: float = 900.0     # slower on the way up
> @export var gravity_down: float = 1600.0  # faster on the way down — the key to not feeling floaty
> @export var coyote_time: float = 0.12     # seconds of grace after walking off a ledge
> @export var jump_buffer_time: float = 0.12 # seconds to buffer a jump input before landing
>
> var coyote_timer: float = 0.0
> var jump_buffer_timer: float = 0.0
>
> func _physics_process(delta: float) -> void:
>     var on_floor := is_on_floor()
>
>     # Coyote time: decay after leaving floor, reset on landing
>     if on_floor:
>         coyote_timer = coyote_time
>     else:
>         coyote_timer = max(0.0, coyote_timer - delta)
>
>     # Jump buffer: keep the intent for a short window
>     if Input.is_action_just_pressed("jump"):
>         jump_buffer_timer = jump_buffer_time
>     else:
>         jump_buffer_timer = max(0.0, jump_buffer_timer - delta)
>
>     # Jump: consume both coyote time and buffer together
>     if jump_buffer_timer > 0.0 and coyote_timer > 0.0:
>         velocity.y = jump_velocity
>         coyote_timer = 0.0
>         jump_buffer_timer = 0.0
>
>     # Variable jump height: release early to cut the arc short
>     if Input.is_action_just_released("jump") and velocity.y < 0:
>         velocity.y *= 0.45
>
>     # Asymmetric gravity: snappy up, weighty down
>     var grav := gravity_up if velocity.y < 0 else gravity_down
>     velocity.y += grav * delta
>
>     var direction := Input.get_axis("move_left", "move_right")
>     velocity.x = direction * speed
>     move_and_slide()
> ```

The jump arc looks fundamentally different — tighter, more responsive, and more predictable:

![Jump feel: base model (symmetric) vs. with-skill (asymmetric gravity + coyote + buffer)](jump_feel_comparison.gif)

**Red** — base model output: symmetric parabola, no coyote time, no jump buffer. The character misses ledges by one frame and the arc feels floaty. **Green** — with-skill output: asymmetric gravity (fast up, weighted down), coyote time for grace after ledge edges, jump buffer so pre-pressed inputs land correctly.

---

### "Vampire Survivors clone in LÖVE — how do I handle hundreds of entities?"

> I want to build a Vampire Survivors style game in LÖVE where there can be hundreds of enemies and projectiles on screen at once. How should I structure it and handle all the collision checks so it doesn't grind to a halt?

Without the skill, the response organises code into flat modules but never names ECS as the architecture for many-entity games and never explains *why* class hierarchies break down at scale:

> I'd recommend a modular structure: `main.lua` orchestrates the loop, `enemy.lua` manages enemy state, `player.lua` handles input, `collision.lua` does detection. For collision at scale, use a spatial grid rather than checking every pair...

With the skill, the response opens with the ECS case, explains metatable overhead at scale, and provides a complete spatial-hash + pool architecture:

> ## Why Not a Class Hierarchy
>
> The intuitive approach is `Enemy extends Character extends Entity` with a big `update()` method on each class. This breaks down fast in a survivors-like:
>
> - Every call to `update()` dispatches through Lua's metatable inheritance chain for each of hundreds of objects — measurable overhead at scale.
> - Shared state accumulates on base classes, creating an implicit god object spread across a hierarchy.
>
> The right model for a many-entity game is **ECS-ish**: entities are plain data tables with no methods, and behavior lives in separate system functions that iterate over the relevant data.
>
> ## Spatial Hash: Kill the O(n²)
>
> With 300 enemies and 200 bullets, naive all-pairs collision is 60,000 tests per frame. A spatial hash reduces that to a handful per bullet.
>
> ```lua
> function SpatialHash:query_nearby(wx, wy, callback)
>     local cs = self.cell_size
>     local cx = math.floor(wx / cs)
>     local cy = math.floor(wy / cs)
>     for dy = -1, 1 do
>         for dx = -1, 1 do
>             local key = self:_key(cx + dx, cy + dy)
>             local cell = self.cells[key]
>             if cell then
>                 for i = 1, #cell do callback(cell[i]) end
>             end
>         end
>     end
> end
> ```

The result in motion — 22 enemies, same starting positions, same target:

![Enemy horde: beeline stacking (base model) vs. flow field + separation steering (with skill)](enemy_horde_comparison.gif)

**Left** — base model output: every enemy beelines directly to the player, all stacking into an indistinguishable blob. **Right** — with-skill output: flow field navigation + boids-style separation steering keeps enemies spread, readable, and encircling — the spread bar shows the difference quantitatively.

---

## What the skill does

The base model knows game development concepts. The skill gives the agent the *specific non-negotiables* to apply them correctly. The five moves:

- **Frame independence without exception.** Every generated movement line is audited before return: `position += speed` is flagged and corrected to `position += speed * delta`. Physics in `_physics_process`/`FixedUpdate`, not `_process`/`Update`. This is the most common silent defect in generated game code.
- **Full platformer feel recipe.** Godot and Unity platformer requests get the complete set: asymmetric gravity (fast up, weighted down), coyote time, jump buffer, variable jump height. The base model produces working but floaty code missing exactly these four.
- **Juice toolkit by name.** Diagnosing "floaty" or "lifeless" triggers explicit naming of: tweening/easing (not instant snaps), squash-and-stretch on 2D characters, hitstop (Time.timeScale freeze), trauma-based screenshake, knockback, hit flash, and sound with pitch randomization. Not just "add particles."
- **ECS for many-entity games.** Survivors-like, bullet-hell, or RTS prompts get an explicit ECS or ECS-ish recommendation with the reason — metatable dispatch overhead at scale, god objects spread across class hierarchies — and a working flat-data-table + system-function architecture.
- **Deliberate engine selection.** The default is Godot 4.x for most small 2D and indie 3D — stated with a reason, not hedged. Python game → not PyGame for Steam, Godot with GDExtension or Godot 4's Python-like GDScript. Casual web → Phaser, not Unity WebGL.

---

## Benchmark: skill vs. base model

Evaluated across 14 scenarios covering the core game-development failure modes. Evals are LLM-graded against specific, objective assertions; executor and grader are separate calls to prevent self-grading inflation.

```
with_skill:    100%   (92/92 expectations)
without_skill:  81.5%  (75/92 expectations)
delta:         +18.5pp
```

![Benchmark: skill vs. base model per eval](benchmark_comparison.png)

### Results by eval

| Eval | Without skill | With skill | Delta |
|------|:---:|:---:|:---:|
| scope-finish-deckbuilder | 3/7 (43%) | **7/7 (100%)** | +57pp |
| hitstop-priority-trap | 3/5 (60%) | **5/5 (100%)** | +40pp |
| rigidbody-avatar-trap | 3/5 (60%) | **5/5 (100%)** | +40pp |
| enemy-horde-pathing | 5/7 (71%) | **7/7 (100%)** | +29pp |
| godot-platformer-feel | 8/10 (80%) | **10/10 (100%)** | +20pp |
| godot-autoload-overuse | 4/5 (80%) | **5/5 (100%)** | +20pp |
| procgen-dungeon-validate | 5/6 (83%) | **6/6 (100%)** | +17pp |
| framerate-dependent-debug | 5/6 (83%) | **6/6 (100%)** | +17pp |
| engine-select-python-cozy-sim | 7/8 (88%) | **8/8 (100%)** | +12pp |
| survivors-collision-love | 6/7 (86%) | **7/7 (100%)** | +14pp |
| game-feel-diagnosis | 9/9 (100%) | 9/9 (100%) | +0pp |
| survivors-like-perf-love | 7/7 (100%) | 7/7 (100%) | +0pp |
| camera-lerp-framerate-trap | 5/5 (100%) | 5/5 (100%) | +0pp |
| ecs-small-game-trap | 5/5 (100%) | 5/5 (100%) | +0pp |

### Where the skill makes the biggest difference

| Scenario | Base model gap | What the skill adds |
|---|:---:|---|
| scope-finish-deckbuilder | 43% base | Leads with toy→prototype→vertical-slice→ship; names the next cut; refuses to scaffold saves/menus before fun is proven |
| hitstop-priority-trap | 60% base | Names hitstop as the highest-ROI fix for weak combat; gives correct frame-duration guidance (30–130 ms); warns against maxing it out |
| rigidbody-avatar-trap | 60% base | Identifies force-driven Rigidbody2D as the architectural root cause of floatiness; recommends kinematic controller switch |
| enemy-horde-pathing | 71% base | Recommends a shared flow field (Dijkstra-map) instead of per-enemy A*; names separation steering to prevent stacking |
| godot-platformer-feel | 80% base | Full platformer recipe: asymmetric gravity + coyote time + jump buffer + variable jump height (all four, not just gravity) |
| godot-autoload-overuse | 80% base | Doesn't open with "solid starting point"; names the antipattern immediately; doesn't hedge with "will ship fine for small games" |

### Evals where the base model already performs well (regression guards)

| Eval | Note |
|---|---|
| game-feel-diagnosis | Base model names all feedback channels; these evals serve as non-regression guards |
| survivors-like-perf-love | Base model covers spatial hashing and pooling on this specific framing |
| camera-lerp-framerate-trap | Frame-independence diagnostic already correct in base model |
| ecs-small-game-trap | Base model appropriately recommends against ECS for tiny single-mechanic games |

---

## Eval suite

| # | Eval | Non-negotiable(s) tested |
|---|------|--------------------------|
| 0 | `godot-platformer-feel` | Frame independence + jump recipe + Godot idioms |
| 1 | `survivors-like-perf-love` | Frame independence + decoupling/ECS + spatial partitioning + pooling (LÖVE) |
| 2 | `scope-finish-deckbuilder` | Find the fun / scope / prototype process |
| 3 | `engine-select-python-cozy-sim` | Deliberate engine selection + data-driven architecture |
| 4 | `game-feel-diagnosis` | Full juice toolkit: tweening/easing, squash-stretch, hitstop, screenshake (Unity) |
| 5 | `enemy-horde-pathing` | Enemy AI: flow fields + separation + many-agent perf |
| 6 | `procgen-dungeon-validate` | Procedural generation: seed + technique + generate-then-validate |
| 7 | `framerate-dependent-debug` | Frame independence: diagnostic framing (broken code given) |
| 8 | `survivors-collision-love` | Spatial hash + pooling as code (LÖVE/Lua) |
| 9 | `camera-lerp-framerate-trap` | Frame independence trap: lerp called with constant 0.1, not dt-scaled |
| 10 | `rigidbody-avatar-trap` | Force-driven Rigidbody2D as root cause of floatiness |
| 11 | `ecs-small-game-trap` | Anti-over-engineering: don't recommend ECS for tiny single-mechanic games |
| 12 | `hitstop-priority-trap` | Juice priority: hitstop first, not particles first |
| 13 | `godot-autoload-overuse` | Godot idioms: autoload overuse antipattern diagnosis |

---

## Sources

- **Vlambeer / Jan Willem Nijman (2013).** "The Art of Screenshake." GDC talk. — Canonical reference for game-feel techniques: hitstop, screenshake, squash-stretch, audio layers, juice priority order.
- **Celeste (Matt Thorson, Noel Berry).** The textbook implementation of the platformer feel recipe: asymmetric gravity, coyote time, jump buffering, variable jump height. Codebase analysis widely discussed in the platformer dev community.
- **Game Programming Patterns (Robert Nystrom, 2014).** `gameprogrammingpatterns.com` — Patterns: Component, Event Queue, Spatial Partition, Object Pool, Game Loop, Update Method. Free online.
- **Fix Your Timestep (Glenn Fiedler, 2004).** `gafferongames.com/post/fix_your_timestep/` — The definitive reference for fixed-timestep simulation with interpolated rendering.
- **Screen Space (various).** Trauma-based screenshake: `squirrel.pl/media/gdc2012_camera.pdf` (Squirrel Eiserloh, GDC 2012).
- **Bevy ECS documentation.** `bevyengine.org` — Reference ECS architecture for Rust game development; patterns portable to LÖVE/Lua flat-table ECS-ish.
- **Godot 4 documentation.** `docs.godotengine.org` — CharacterBody2D, move_and_slide, signal system, autoload/singleton antipattern notes.
- **Unity Manual.** `docs.unity3d.com` — Rigidbody2D kinematic mode, FixedUpdate, CharacterController, Time.timeScale, Cinemachine ImpulseSource.
- **LÖVE documentation.** `love2d.org/wiki/` — love.update(dt), love.physics, love.graphics. Reference for all LÖVE eval patterns.
