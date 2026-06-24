# Game Development Skill

A skill that gives the agent the procedural knowledge to build games that feel good and ship — not just games that compile. It encodes the techniques that separate "a programmer made this" from "this is a game": frame-independent movement, asymmetric jump gravity with coyote time and jump buffering, the juice toolkit (hitstop, trauma-based screenshake, tweening/easing, squash-and-stretch), ECS architecture for many-entity games, spatial-hash collision for hundreds of objects, flow-field pathfinding for enemy hordes, and the prototype → vertical-slice → ship process that prevents projects from dying in scope creep.

Covers **pixel art and retro games** (Zelda-like top-down, JRPG turn-based combat, Stardew-style farming sims) including pixel-perfect rendering setup (Nearest filter + integer scaling + camera snapping), grid-locked movement with tween animation, TileMap workflows, and sprite animation pipelines. Also covers **3D games**: CharacterBody3D controllers, SpringArm3D camera rigs that auto-prevent wall clipping, camera-relative movement, 3D pathfinding via NavigationAgent3D, skeletal animation blend trees, baked lighting, and modular level design.

Also covers **RPG systems** (status effects with per-effect StackPolicy, stat modifiers via additive + multiplicative formula, inventory, ability systems, crafting), **audio architecture** (bus hierarchy for volume sliders, stem-based adaptive music that syncs playback position instead of stop-and-start crossfade, 3D spatial audio, AudioPool), **shaders and visual effects** (hit flash, 8-direction sprite outline, dissolve via discard not alpha=0, palette swap, post-process), **multiplayer and netcode** (scope reality check, local co-op before online, rollback vs delay-based, authoritative server, relay services), and **save systems and meta-progression** (dual-file roguelike saves, version field from day 1, migration chains).

Also covers **UI/HUD** (signal-driven HUDs with UpdateResource pattern — game logic never touches HUD nodes directly), **advanced platformer mechanics** (wall jump with wall detection + grace period, one-way moving platforms via `set_collision_mask_value`, scene transitions with typewriter text and fades), **dialogue and narrative systems** (DialogueLineData Resource, branching via option arrays, tool selection: Ink + godot-ink for complex branching vs Dialogic for cutscene-heavy games), **weapons and shooting** (hitscan via `intersect_ray` vs projectile node tradeoffs, multiple firing modes as data-driven WeaponData Resources), **boss fights** (phase-based FSM with mandatory telegraph → active → recovery attack structure, AttackData Resource, invincibility during telegraph/active frames, boss invincibility as a skill loop not a difficulty setting), **camera systems** (room-zone camera transitions using Camera2D `limit_*` properties tweened via Area2D triggers, 3D lock-on camera with FOV + distance check via dot product + `is_instance_valid` guard), **stealth AI** (cone-of-vision detection as a 3-step pipeline: distance check → dot product angle check → raycast wall check; 5-state alert FSM with PATROL/SUSPICIOUS/ALERT/SEARCH/RETURNING), **fog of war and minimap** (PackedByteArray grid with UNSEEN/REVEALED/VISIBLE states, SubViewport-based minimap with shared World2D), and **bullet hell patterns** (BulletPool autoload pre-allocated at game start, BulletPatternData Resources, `Vector2.from_angle()` for polar coordinates, spiral patterns that accumulate angle each fire).

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/game-development
```

Or manually:

```bash
cp -r jakes-skills/game-development ~/.claude/skills/game-development
```

Once installed, the skill applies automatically when the user wants to build or improve a game in Godot, Unity, LÖVE, PyGame, Bevy, or Phaser — including character controllers, collision, enemy AI, procedural generation, game feel, engine selection, pixel art rendering, top-down movement, JRPG turn-based combat, 3D character controllers, third-person cameras, scoping a project, RPG systems (status effects, inventory, stat modifiers), audio architecture (bus hierarchy, adaptive music), shaders and visual effects, multiplayer and netcode, save systems and meta-progression, UI/HUD design, advanced platformer mechanics (wall jump, moving platforms, scene transitions), dialogue and narrative systems, weapons and shooting mechanics, boss fight architecture, camera systems (room zones, lock-on), stealth AI (cone of vision, alert FSM), fog of war and minimap, or bullet hell patterns.

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

### "How do I make enemies flash white on hit and give them an outline in Godot?"

> I want my enemies to flash white when they take damage, and have a colored outline around their sprites at all times. How do I do this in Godot 4?

Without the skill, the response uses `modulate` — a built-in Color property that tints the whole sprite. It works, but produces no outline and the tint is a blunt color shift rather than a clean white flash:

> ```gdscript
> func take_damage():
>     modulate = Color(1.5, 0.5, 0.5)   # reddish tint
>     await get_tree().create_timer(0.1).timeout
>     modulate = Color.WHITE
> ```

With the skill, the response leads with a `canvas_item` shader using `mix()` to blend toward white (preserving alpha), plus a second pass doing the 8-direction UV-offset outline — the correct shader technique for both effects:

> ```glsl
> // HitFlashOutline.gdshader
> shader_type canvas_item;
> uniform float flash_t : hint_range(0.0, 1.0) = 0.0;
> uniform vec4 outline_color : source_color = vec4(1.0, 0.2, 0.2, 1.0);
> uniform float outline_width : hint_range(1.0, 8.0) = 3.0;
>
> void fragment() {
>     vec4 col = texture(TEXTURE, UV);
>     vec2 texel = outline_width / vec2(textureSize(TEXTURE, 0));
>     float a = col.a;
>     a = max(a, texture(TEXTURE, UV + vec2( texel.x,       0.0)).a);
>     a = max(a, texture(TEXTURE, UV + vec2(-texel.x,       0.0)).a);
>     a = max(a, texture(TEXTURE, UV + vec2(      0.0,  texel.y)).a);
>     a = max(a, texture(TEXTURE, UV + vec2(      0.0, -texel.y)).a);
>     // outline where the dilated mask exceeds the original alpha
>     if (col.a < 0.1 && a > 0.1) {
>         COLOR = outline_color;
>         return;
>     }
>     COLOR = mix(col, vec4(1.0), flash_t);  // white flash preserves shape
> }
> ```

The outline is always visible; the flash fires on damage and decays in two frames:

![Hit flash + outline: base model (modulate tint, no outline) vs. with-skill (shader mix() flash + 8-direction outline)](hit_flash_outline_comparison.gif)

**Left** — base model output: a red color modulate tint. No outline, no crisp white flash. **Right** — with-skill output: persistent colored outline using the 8-direction UV-offset technique, plus a clean white flash that fires on impact using `mix()` in the shader (preserving alpha correctly, unlike setting `modulate = Color.WHITE`).

---

### "My enemies dissolve when they die but it looks wrong — just a ghost fade"

> In my Godot game, enemies fade out when they die using `modulate.a = 0`. It looks bad — they turn into a transparent ghost. How do I get a proper dissolve effect?

Without the skill, the response keeps the alpha approach and suggests `Tween` to animate `modulate.a` from 1 to 0 — cleaner code, same ghost result:

> ```gdscript
> func die():
>     var tween = create_tween()
>     tween.tween_property(self, "modulate:a", 0.0, 0.8)
>     await tween.finished
>     queue_free()
> ```

With the skill, the response explains that `alpha = 0` is the wrong tool for dissolve — it fades the whole sprite uniformly, producing a ghost. The correct approach is a noise-texture shader using `discard`, which removes pixels hard-edge based on a threshold, creating a pixel-by-pixel dissolve:

> ```glsl
> // Dissolve.gdshader
> shader_type canvas_item;
> uniform sampler2D noise_texture;
> uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
>
> void fragment() {
>     float noise = texture(noise_texture, UV).r;
>     // discard — not alpha = 0 — so there is no ghost transparency
>     if (noise < dissolve_amount) discard;
>     COLOR = texture(TEXTURE, UV);
> }
> ```
> Drive `dissolve_amount` via AnimationPlayer from 0 → 1 over the death duration.

The visual difference between the two approaches:

![Dissolve shader: base model (uniform alpha fade) vs. with-skill (noise discard dissolve)](dissolve_shader_comparison.gif)

**Left** — base model output: `alpha = 0` fade. The sprite becomes a transparent ghost that lingers. **Right** — with-skill output: `discard` against a smooth noise texture. Pixels wink out individually, edge-first — the standard dissolve effect used in action games and RPGs.

---

## What the skill does

The base model knows game development concepts. The skill gives the agent the *specific non-negotiables* to apply them correctly.

- **Frame independence without exception.** Every generated movement line is audited before return: `position += speed` is flagged and corrected to `position += speed * delta`. Physics in `_physics_process`/`FixedUpdate`, not `_process`/`Update`. This is the most common silent defect in generated game code.
- **Full platformer feel recipe — 2D and 3D.** Godot and Unity platformer requests get the complete set: asymmetric gravity (fast up, weighted down), coyote time, jump buffer, variable jump height. These four apply to 3D (CharacterBody3D) exactly as to 2D. The base model produces working but floaty code missing exactly these four.
- **Juice toolkit by name.** Diagnosing "floaty" or "lifeless" triggers explicit naming of: tweening/easing (not instant snaps), squash-and-stretch on 2D characters, hitstop (Time.timeScale freeze), trauma-based screenshake, knockback, hit flash, and sound with pitch randomization. Not just "add particles."
- **ECS for many-entity games.** Survivors-like, bullet-hell, or RTS prompts get an explicit ECS or ECS-ish recommendation with the reason — metatable dispatch overhead at scale, god objects spread across class hierarchies — and a working flat-data-table + system-function architecture.
- **Deliberate engine selection.** The default is Godot 4.x for most small 2D and indie 3D — stated with a reason, not hedged. Python game → not PyGame for Steam, Godot with GDExtension or Godot 4's Python-like GDScript. Casual web → Phaser, not Unity WebGL.
- **Pixel-perfect rendering, always both settings.** Pixel art requests get both: texture filter → Nearest AND Stretch Mode → canvas_items with a small base resolution. Missing either produces blurry or shimmering pixels. Camera pixel-snapping (round before assign) is included as the third piece.
- **3D camera: SpringArm3D, not a raycast.** Third-person camera requests lead with the SpringArm3D pivot rig (Player → CameraPivot → SpringArm3D → Camera3D) as the singular correct structure. The base model often leads with a manual raycast option; the skill names SpringArm as primary, explains the mask setup (world layer only), and warns against direct Camera3D parenting.
- **Retro/pixel-art patterns.** Zelda-like top-down requests get: grid-locked movement (logical grid position + tween visual), facing direction from last non-zero velocity, 4-directional priority, TileMap layer setup, and collision layer architecture. JRPG requests get: ATB/turn-order state machine pattern, damage formula in data, dialogue character-reveal system.
- **RPG systems: component pattern and correct stat formula.** Status effects are StatusEffectData Resources on an EffectManager component (not subclasses on enemies) with per-effect StackPolicy (REPLACE / ADD / IGNORE) — the base model uses a single global max_stacks flag and misses the per-effect policy. Stat modifiers use the flat-then-additive-then-multiplicative formula; the base model uses simple summation.
- **Audio: bus hierarchy and stem-based adaptive music.** Audio bus setup is always Master → Music / SFX → subgroups, with volume saved as linear [0,1] and converted via `linear_to_db()` at assignment time. Adaptive music uses continuously-playing stems (all tracks run from game start, volumes set to 0), never stop-and-start crossfades that restart from position 0 — the most common mistake in generated adaptive music code, worth 80pp delta in evals.
- **Multiplayer: scope warning and local co-op first.** Any online multiplayer request opens with an honest scope estimate (online multiplayer adds 30–100% dev time, plus hosting costs). The recommendation path is always: local co-op → LAN → online. The base model skips local co-op and jumps to MultiplayerAPI; the skill names it first.
- **Save systems: logical state only, version field mandatory from day 1.** Save code serializes logical data (item IDs, numbers, seeds) — never Nodes, Resources with signals, or scene trees. Version field is included from the first line of the save dict. Roguelike runs use dual-file: volatile run.json (deleted on death) + permanent meta.json (unlocks, currency, records). Save format changes always use a migration chain (migrate_v1_to_v2 functions), never field-presence checks.
- **Signal-driven HUD: never poll, never couple.** HUD scenes connect to signals and receive UpdateResource data objects — they never read game state directly and game logic never references HUD nodes. Base model responses frequently couple HUD to game nodes directly.
- **Boss fight architecture: 3-phase mandatory, invincibility enforced.** Every boss attack has telegraph → active → recovery phases defined in an AttackData Resource. The boss is invincible during telegraph and active frames (take_damage returns early), vulnerable only during recovery. This is the skill loop, not a difficulty setting. Base model produces flat if/elif chains with hardcoded timers.
- **Stealth AI: detection pipeline, not a distance check.** Cone of vision is three sequential checks — distance culling first, then `dot(forward, to_player) > cos(half_fov)` angle check, then a raycast for wall occlusion. The alert FSM has five states (PATROL/SUSPICIOUS/ALERT/SEARCH/RETURNING) with `_enter_state()` centralising side effects and `_generate_search_positions()` on ALERT→SEARCH transition.
- **Camera systems: limits, not lerp.** Room zone transitions tween `Camera2D.limit_left/right/top/bottom` (not camera position) triggered by CameraZone Area2D signals, keeping the camera physically constrained to the room. 3D lock-on uses FOV angle check (dot product) + distance to avoid locking enemies behind the player, lerps to the player–target midpoint, guards with `is_instance_valid()`, and cycles via a sorted candidate list index.
- **Bullet hell: pooled, pattern-as-data.** Bullet pool pre-allocated at game start (800+ bullets), BulletPatternData Resource drives all pattern parameters. Circle patterns use `TAU / bullet_count` step with `Vector2.from_angle()`. Spiral patterns accumulate `_spiral_angle` across fire calls — the angle is never reset. Base model instantiates bullets per-fire and produces drift-prone spiral implementations.
- **Weapons: hitscan vs projectile is a design choice, not a tech choice.** Hitscan (`intersect_ray`) is instant and zero-latency — correct for sniper rifles and shotguns. Projectile nodes (Area2D + velocity) are dodgeable — correct for bullet-hell and skill shots. Recommends both patterns and names the tradeoff. Multiple firing modes use a WeaponData Resource with an enum-driven pattern, cooldown as a float timer.

---

## Benchmark: skill vs. base model

Evaluated across 46 scenarios covering the core game-development failure modes — including pixel art rendering, 3D game development, RPG systems, audio architecture, shaders, multiplayer netcode, save systems, UI/HUD, advanced platformer mechanics, dialogue systems, weapons, boss fights, camera systems, stealth AI, fog of war/minimap, and bullet hell patterns. Evals are LLM-graded against specific, objective assertions; executor and grader are separate calls to prevent self-grading inflation.

```
with_skill:    100%   (285/285 expectations)
without_skill:  71.9%  (205/285 expectations)
delta:         +28.1pp
```

![Benchmark: skill vs. base model per eval](benchmark_comparison.png)

### Results by eval

| Eval | Without skill | With skill | Delta |
|------|:---:|:---:|:---:|
| scope-finish-deckbuilder | 3/7 (43%) | **7/7 (100%)** | +57pp |
| hitstop-priority-trap | 3/5 (60%) | **5/5 (100%)** | +40pp |
| rigidbody-avatar-trap | 3/5 (60%) | **5/5 (100%)** | +40pp |
| 3d-camera-springarm | 4/7 (57%) | **7/7 (100%)** | +43pp |
| zelda-topdown-grid | 4/7 (57%) | **7/7 (100%)** | +43pp |
| enemy-horde-pathing | 5/7 (71%) | **7/7 (100%)** | +29pp |
| 3d-character-controller | 6/7 (86%) | **7/7 (100%)** | +14pp |
| godot-platformer-feel | 8/10 (80%) | **10/10 (100%)** | +20pp |
| godot-autoload-overuse | 4/5 (80%) | **5/5 (100%)** | +20pp |
| procgen-dungeon-validate | 5/6 (83%) | **6/6 (100%)** | +17pp |
| framerate-dependent-debug | 5/6 (83%) | **6/6 (100%)** | +17pp |
| engine-select-python-cozy-sim | 7/8 (88%) | **8/8 (100%)** | +12pp |
| survivors-collision-love | 6/7 (86%) | **7/7 (100%)** | +14pp |
| pixel-perfect-setup | 6/6 (100%) | 6/6 (100%) | +0pp |
| game-feel-diagnosis | 9/9 (100%) | 9/9 (100%) | +0pp |
| survivors-like-perf-love | 7/7 (100%) | 7/7 (100%) | +0pp |
| camera-lerp-framerate-trap | 5/5 (100%) | 5/5 (100%) | +0pp |
| ecs-small-game-trap | 5/5 (100%) | 5/5 (100%) | +0pp |
| adaptive-music | 1/5 (20%) | **5/5 (100%)** | +80pp |
| inventory-equipment-data | 4/6 (67%) | **6/6 (100%)** | +33pp |
| multiplayer-scope-trap | 4/6 (67%) | **6/6 (100%)** | +33pp |
| status-effects-design | 5/6 (83%) | **6/6 (100%)** | +17pp |
| audio-bus-hierarchy | 6/6 (100%) | 6/6 (100%) | +0pp |
| sprite-hit-flash-outline | 6/6 (100%) | 6/6 (100%) | +0pp |
| dissolve-shader | 5/5 (100%) | 5/5 (100%) | +0pp |
| rollback-netcode | 6/6 (100%) | 6/6 (100%) | +0pp |
| roguelike-run-save | 6/6 (100%) | 6/6 (100%) | +0pp |
| save-format-versioning | 6/6 (100%) | 6/6 (100%) | +0pp |
| boss-phase-fsm | 0/6 (0%) | **6/6 (100%)** | +100pp |
| lock-on-camera | 1/6 (17%) | **6/6 (100%)** | +83pp |
| camera-room-zones | 2/6 (33%) | **6/6 (100%)** | +67pp |
| bullet-hell-patterns | 3/6 (50%) | **6/6 (100%)** | +50pp |
| dialogue-tool-choice | 3/6 (50%) | **6/6 (100%)** | +50pp |
| moving-platform-one-way | 3/6 (50%) | **6/6 (100%)** | +50pp |
| scene-transition-typewriter | 3/6 (50%) | **6/6 (100%)** | +50pp |
| wall-jump-slide | 3/6 (50%) | **6/6 (100%)** | +50pp |
| weapon-firing-modes | 3/6 (50%) | **6/6 (100%)** | +50pp |
| alert-state-machine | 4/6 (67%) | **6/6 (100%)** | +33pp |
| boss-telegraph | 4/6 (67%) | **6/6 (100%)** | +33pp |
| branching-dialogue-data | 4/6 (67%) | **6/6 (100%)** | +33pp |
| fog-of-war | 4/6 (67%) | **6/6 (100%)** | +33pp |
| hitscan-vs-projectile | 4/6 (67%) | **6/6 (100%)** | +33pp |
| minimap-implementation | 4/6 (67%) | **6/6 (100%)** | +33pp |
| signal-driven-hud | 4/6 (67%) | **6/6 (100%)** | +33pp |
| cone-of-vision-stealth | 5/6 (83%) | **6/6 (100%)** | +17pp |
| homing-bullet-pool | 6/6 (100%) | 6/6 (100%) | +0pp |

### Where the skill makes the biggest difference

| Scenario | Base model gap | What the skill adds |
|---|:---:|---|
| scope-finish-deckbuilder | 43% base | Leads with toy→prototype→vertical-slice→ship; names the next cut; refuses to scaffold saves/menus before fun is proven |
| hitstop-priority-trap | 60% base | Names hitstop as the highest-ROI fix for weak combat; gives correct frame-duration guidance (30–130 ms); warns against maxing it out |
| rigidbody-avatar-trap | 60% base | Identifies force-driven Rigidbody2D as the architectural root cause of floatiness; recommends kinematic controller switch |
| 3d-camera-springarm | 57% base | Recommends SpringArm3D as the primary (not optional) solution; correctly excludes player/enemy layers from the spring mask; names direct Camera3D parenting as the bug |
| zelda-topdown-grid | 57% base | Implements grid-locked tween pattern explicitly (logical snaps, visual tweens); covers last-facing idle animation; defines layer/mask architecture |
| adaptive-music | 20% base | Stems play continuously at volume 0 (never stop-and-start); late stem entry syncs playback_position from the running stems; base model crossfades by stopping old track and restarting from 0 |
| enemy-horde-pathing | 71% base | Recommends a shared flow field (Dijkstra-map) instead of per-enemy A*; names separation steering to prevent stacking |
| inventory-equipment-data | 67% base | Flat + additive-percent + multiplicative modifier formula; type-agnostic modifier dispatch; base model uses simple summation |
| multiplayer-scope-trap | 67% base | Opens with scope warning (30–100% extra dev time); recommends local co-op before online; base model skips straight to MultiplayerAPI |
| godot-platformer-feel | 80% base | Full platformer recipe: asymmetric gravity + coyote time + jump buffer + variable jump height (all four, not just gravity) |
| godot-autoload-overuse | 80% base | Doesn't open with "solid starting point"; names the antipattern immediately; doesn't hedge with "will ship fine for small games" |
| status-effects-design | 83% base | Per-effect StackPolicy enum (REPLACE/ADD/IGNORE); base model uses a single global max_stacks flag |
| 3d-character-controller | 86% base | Applies all 2D platformer feel techniques (asymmetric gravity, coyote, jump buffer, variable height) to 3D; enforces @export tunables |
| boss-phase-fsm | 0% base | Phase-based boss FSM with mandatory AttackData Resource and `_enter_phase()` side-effect centralisation; base model produces flat if/elif chains with hardcoded per-phase health thresholds |
| lock-on-camera | 17% base | Target acquisition uses FOV angle check (dot product) + distance, not just nearest; camera lerps to player–target midpoint; `is_instance_valid()` guard; cycle index into pre-built candidate list; Sprite3D marker projected to screen |
| camera-room-zones | 33% base | Transitions by tweening Camera2D `limit_left/right/top/bottom` (not camera position); CameraZone as Area2D triggers the autoload CameraController; bounds derived from CollisionShape2D AABB |
| boss-telegraph | 33% base | Mandatory 3-phase structure (telegraph → active → recovery) enforced in data (AttackData.telegraph_duration); boss invincible during telegraph/active; `take_damage()` returns early if state is telegraphing or attacking |
| wall-jump-slide | 50% base | Wall-slide uses `is_on_wall_only()` with capped fall speed; wall-jump requires `last_wall_direction` and jump-grace window (can't be pressed continuously); base model produces instant snap wall-jump with no grace period |
| bullet-hell-patterns | 50% base | BulletPool autoload pre-allocated at game start; BulletPatternData Resource; `Vector2.from_angle()` for polar coordinates; spiral accumulates `_spiral_angle` each fire call (not reset) |
| dialogue-tool-choice | 50% base | Names Ink + godot-ink for complex branching (flags, variables, conditions) vs Dialogic for cutscene-heavy games; base model recommends Dialogic generically without distinguishing use cases |

### Evals where the base model already performs well (regression guards)

| Eval | Note |
|---|---|
| pixel-perfect-setup | Base model knows Nearest filter + canvas_items setup well from Godot documentation |
| game-feel-diagnosis | Base model names all feedback channels; these evals serve as non-regression guards |
| survivors-like-perf-love | Base model covers spatial hashing and pooling on this specific framing |
| camera-lerp-framerate-trap | Frame-independence diagnostic already correct in base model |
| ecs-small-game-trap | Base model appropriately recommends against ECS for tiny single-mechanic games |
| audio-bus-hierarchy | Base model knows AudioServer.set_bus_volume_db() API well |
| sprite-hit-flash-outline | Base model handles basic 2D shader patterns (hit flash, outline) correctly |
| dissolve-shader | Base model uses discard correctly for dissolve effects |
| rollback-netcode | Base model correctly explains rollback, determinism requirement, and recommends godot-rollback-netcode addon |
| roguelike-run-save | Base model uses dual-file pattern and version field when prompted with roguelike context |
| save-format-versioning | Base model implements migration chain pattern when explicitly asked about format migration |
| homing-bullet-pool | Base model identifies the BulletPool pattern and rotation-based homing (not velocity snap) when the problem is framed explicitly as a performance question |

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
| 14 | `pixel-perfect-setup` | Pixel art rendering: Nearest filter + integer scaling + camera snapping |
| 15 | `zelda-topdown-grid` | Pixel art / retro: TileMap, grid-locked movement, 4-directional animation, facing, collision layers |
| 16 | `3d-character-controller` | 3D: CharacterBody3D, manual gravity, camera-relative input, @export, coyote/buffer/variable height in 3D |
| 17 | `3d-camera-springarm` | 3D: SpringArm3D rig as primary solution, mask config, no direct Camera3D parenting |
| 18 | `status-effects-design` | RPG: StatusEffectData Resource, StackPolicy enum (REPLACE/ADD/IGNORE), component pattern |
| 19 | `inventory-equipment-data` | RPG: ItemData + StatModifier, flat+additive-pct+multiplicative formula, type-agnostic dispatch |
| 20 | `audio-bus-hierarchy` | Audio: Master→Music/SFX bus tree, AudioServer.set_bus_volume_db(), linear_to_db() |
| 21 | `adaptive-music` | Audio: stem-based approach (all stems run continuously), playback_position sync for late entry |
| 22 | `sprite-hit-flash-outline` | Shaders: hit flash via mix(), 8-direction outline via textureSize() UV offset |
| 23 | `dissolve-shader` | Shaders: noise texture + discard (not alpha=0), AnimationPlayer-driven threshold |
| 24 | `multiplayer-scope-trap` | Multiplayer: scope warning, local co-op first recommendation, honest time/cost estimate |
| 25 | `rollback-netcode` | Multiplayer: rollback mechanics, determinism requirement, GGPO/godot-rollback-netcode |
| 26 | `roguelike-run-save` | Save systems: dual-file (run.json + meta.json), logical state only, version field |
| 27 | `save-format-versioning` | Save systems: migration chain, sensible defaults, backup before migration |
| 28 | `signal-driven-hud` | UI/HUD: signal-based decoupling, UpdateResource pattern, no game logic in HUD nodes |
| 29 | `scene-transition-typewriter` | UI: typewriter text via Timer + character reveal, scene transition via AnimationPlayer, no blocking await chains |
| 30 | `wall-jump-slide` | Advanced platformer: wall-slide with capped fall speed, wall-jump with `last_wall_direction` and grace window |
| 31 | `moving-platform-one-way` | Advanced platformer: `set_collision_mask_value` for one-way drop-through, `move_and_slide()` on kinematic platform |
| 32 | `branching-dialogue-data` | Dialogue: DialogueLineData Resource with option arrays, signal-driven flow, separation from game logic |
| 33 | `hitscan-vs-projectile` | Weapons: `intersect_ray` for hitscan (instant, zero latency), Area2D projectile for dodgeable shots; tradeoff guidance |
| 34 | `weapon-firing-modes` | Weapons: WeaponData Resource, data-driven firing modes (semi/burst/auto), cooldown as float timer not boolean |
| 35 | `boss-phase-fsm` | Boss fights: phase-based FSM, AttackData Resource, `_enter_phase()` side effects, health threshold triggers |
| 36 | `camera-room-zones` | Camera: Camera2D `limit_*` tweened via CameraZone Area2D; bounds from CollisionShape2D AABB |
| 37 | `cone-of-vision-stealth` | Stealth AI: 3-step cone detection (distance → dot product → raycast); `detection_level` float accumulator |
| 38 | `alert-state-machine` | Stealth AI: 5-state FSM (PATROL/SUSPICIOUS/ALERT/SEARCH/RETURNING); `_enter_state()` centralises side effects |
| 39 | `minimap-implementation` | Minimap: SubViewport + shared World2D vs icon overlay; WORLD_RADIUS coordinate math; viewport-clamp masking |
| 40 | `bullet-hell-patterns` | Bullet hell: BulletPool autoload; BulletPatternData Resource; circle via TAU/count, spiral via accumulated angle |
| 41 | `fog-of-war` | Fog of war: PackedByteArray grid, UNSEEN/REVEALED/VISIBLE states, `_draw()` rects, `hex_encode()` for save |
| 42 | `dialogue-tool-choice` | Dialogue tools: Ink + godot-ink for branching logic; Dialogic for cutscene-heavy games; tags for portrait/audio |
| 43 | `lock-on-camera` | Camera: lock-on with FOV + distance via dot product, lerp to midpoint, `is_instance_valid()`, cycle index |
| 44 | `boss-telegraph` | Boss fights: mandatory 3-phase attacks, AttackData.telegraph_duration, invincibility during telegraph/active |
| 45 | `homing-bullet-pool` | Weapons: BulletPool pre-allocation, rotation-based homing (clamp turn angle × delta), Area2D collision signals |

---

## Sources

- **Vlambeer / Jan Willem Nijman (2013).** "The Art of Screenshake." GDC talk. — Canonical reference for game-feel techniques: hitstop, screenshake, squash-stretch, audio layers, juice priority order.
- **Celeste (Matt Thorson, Noel Berry).** The textbook implementation of the platformer feel recipe: asymmetric gravity, coyote time, jump buffering, variable jump height. Codebase analysis widely discussed in the platformer dev community.
- **Game Programming Patterns (Robert Nystrom, 2014).** `gameprogrammingpatterns.com` — Patterns: Component, Event Queue, Spatial Partition, Object Pool, Game Loop, Update Method. Free online.
- **Fix Your Timestep (Glenn Fiedler, 2004).** `gafferongames.com/post/fix_your_timestep/` — The definitive reference for fixed-timestep simulation with interpolated rendering.
- **Screen Space (various).** Trauma-based screenshake: `squirrel.pl/media/gdc2012_camera.pdf` (Squirrel Eiserloh, GDC 2012).
- **Bevy ECS documentation.** `bevyengine.org` — Reference ECS architecture for Rust game development; patterns portable to LÖVE/Lua flat-table ECS-ish.
- **Godot 4 documentation.** `docs.godotengine.org` — CharacterBody2D, move_and_slide, signal system, autoload/singleton antipattern notes. AudioServer, FileAccess, JSON APIs.
- **Unity Manual.** `docs.unity3d.com` — Rigidbody2D kinematic mode, FixedUpdate, CharacterController, Time.timeScale, Cinemachine ImpulseSource, Audio Mixer.
- **LÖVE documentation.** `love2d.org/wiki/` — love.update(dt), love.physics, love.graphics. Reference for all LÖVE eval patterns.
- **GGPO Networking SDK.** `ggpo.net` — Reference implementation of rollback netcode; the technical standard for fighting games.
- **godot-rollback-netcode (Chris Snopek / Snopek Games).** The community addon for rollback netcode in Godot 4.
- **Nakama (Heroic Labs).** `heroiclabs.com/nakama` — Open-source relay/matchmaking server used in Godot multiplayer architecture recommendations.
- **Photon Engine.** `photonengine.com` — Commercial relay/matchmaking alternative; covered in multiplayer relay services section.
