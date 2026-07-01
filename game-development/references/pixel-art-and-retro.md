# Pixel Art & Retro Games

Pixel art games fail in a predictable set of ways: blurry upscaling, sub-pixel jitter that makes tiles shimmer, movement that doesn't respect the grid, and combat state machines that collapse into a spaghetti of booleans. This file gives the setup and patterns that make retro-style games look and feel right — covering top-down action-RPGs (Zelda), JRPGs (Final Fantasy), and farming/cozy sims (Stardew).

## Contents
- Pixel-perfect rendering setup (the #1 mistake)
- Tile-based worlds: TileMap workflow
- Top-down movement: Zelda-style
- 4-directional animation from velocity
- Screen transitions (room-to-room)
- JRPG turn-based battle state machine
- Dialogue systems
- Sprite animation pipeline
- Retro aesthetics

## Pixel-perfect rendering setup

The single most common mistake in pixel art games: upscaling with **bilinear filtering**, which blurs every pixel edge. The fix is two settings that must both be right.

**Step 1 — Nearest-neighbor filtering (no blurring).**
- **Godot 4:** Project Settings → Rendering → Textures → Canvas Textures → Default Texture Filter → **Nearest**. Any sprite that imports before this is set may also need its own import override (select the texture, Import tab, set filter to Nearest). Individual sprites can override it on their `CanvasItem` node too (`texture_filter = TEXTURE_FILTER_NEAREST`).
- **Unity:** Select each sprite asset → Filter Mode → **Point (no filter)**. For consistency, set the default texture preset. In the Universal Render Pipeline (URP), ensure the camera isn't using anti-aliasing on a pixel art target.
- **Phaser:** `pixelArt: true` in the game config — this sets `antialias: false` and enables the correct Canvas/WebGL pixel-snapping flags.

**Step 2 — Integer scaling (no fractional pixel rows).**
Run the game at a small "virtual" resolution (e.g. 320×180, 384×216, 256×144) and scale it up to the window by an integer factor (2×, 3×, 4×). A fractional scale (like 2.7×) means different pixels map to different numbers of screen pixels, producing a shimmering, uneven grid.
- **Godot 4:** Project Settings → Display → Window → Stretch Mode → **canvas_items**; Stretch Aspect → **keep**. Set Viewport Width/Height to your target small resolution (e.g. 320×180). Godot picks the largest integer scale that fits. **canvas_items** (not "viewport") lets UI render at native resolution while the game renders at pixel scale.
- **Unity:** Set the camera to an orthographic projection with a small `orthographicSize` (e.g. 2.0 gives 4 units vertical at 16px/unit). Use a `PixelPerfectCamera` component (2D package) — it exposes assets-per-unit and guarantees integer upscaling.

**Step 3 — Snap the camera to the pixel grid.**
Without this, a smoothly scrolling world produces sub-pixel jitter — every tile shimmers slightly. Round the camera's pixel position to the nearest integer each frame before rendering.

```gdscript
# Godot 4 — snap camera to pixel grid
func _physics_process(_delta: float) -> void:
    var target := player.global_position
    # Snap to nearest pixel before assigning
    global_position = target.round()
```

For a smooth-scrolling camera that *also* snaps, apply lerp toward the target, then `round()` the result before it writes to the camera transform. The lerp gives smooth catch-up; the rounding eliminates sub-pixel positions.

## Tile-based worlds: TileMap workflow

**Godot 4 TileMap:**
- Add a **TileMap** node; assign a **TileSet** resource (create in the inspector).
- Paint tiles in the TileMap editor. For collision, select a tile in the TileSet editor and add a collision polygon (or use the physics layer auto-tile feature).
- Layers: use multiple TileMap layers (or multiple TileMap nodes) for ground, decorations, and objects. A typical Zelda-like: Layer 0 = floor, Layer 1 = walls/trees (with collision), Layer 2 = above-player canopy.
- `TileMap.map_to_local(cell)` and `TileMap.local_to_map(pos)` convert between tile coordinates and world positions. Use these for grid snapping, pathfinding, and interactive tiles (farming soil, chest locations).
- For autotiles/terrains (automatic tile joining like Stardew's grass borders), use the **Terrain** feature in Godot's TileSet editor — paint a terrain, define neighbor rules, and Godot picks the correct tile automatically.

**Unity 2D Tilemap:**
- Window → 2D → Tile Palette; create a grid with a Tilemap component.
- Tilemap Collider 2D + Composite Collider 2D for efficient merged collision (avoids per-tile edge colliders).
- Use Rule Tiles for autotiling behavior.

## Top-down movement: Zelda-style

Two flavors: **grid-locked** (original Zelda — player snaps between tiles, movement is tile-to-tile) and **free top-down** (Link's Awakening remake, Stardew — pixel-precise position, but interactions snap to the grid).

### Grid-locked movement (original Zelda)

The logical position is always a tile coordinate. Input triggers a move to an adjacent tile. Animate the *visual* position sliding between tiles using a tween; the *logical* grid position updates instantly when the move is committed.

```gdscript
# Godot 4 — grid-locked top-down
const TILE_SIZE := 16
var grid_pos := Vector2i.ZERO   # logical position in tile coords
var moving := false

func _physics_process(_delta: float) -> void:
    if moving: return
    var dir := Vector2i(
        int(Input.get_axis("move_left", "move_right")),
        int(Input.get_axis("move_up", "move_down"))
    )
    if dir == Vector2i.ZERO: return
    # prefer horizontal over diagonal (classic Zelda feel)
    if dir.x != 0: dir.y = 0
    var next := grid_pos + dir
    if not is_wall(next):
        grid_pos = next
        moving = true
        var tween := create_tween()
        tween.tween_property(self, "position",
            Vector2(grid_pos * TILE_SIZE), 0.12)
        tween.tween_callback(func(): moving = false)
```

### Free top-down movement (Stardew-style)

Use CharacterBody2D + move_and_slide exactly as in a platformer, but with no gravity. Normalize the input vector so diagonals aren't 41% faster.

```gdscript
func _physics_process(delta: float) -> void:
    var dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = dir * SPEED
    move_and_slide()
    update_facing(dir)
```

For interactions (talking to NPCs, planting crops, opening chests), snap the action target to the nearest tile: `tilemap.local_to_map(player.global_position + facing_dir * TILE_SIZE)`.

## 4-directional animation from velocity

Store the last non-zero direction as the "facing" direction. Derive the animation from it, not from the raw input (the player should keep facing the last direction when standing still).

```gdscript
var facing := Vector2.DOWN   # start facing down

func update_facing(dir: Vector2) -> void:
    if dir == Vector2.ZERO: return   # keep last facing
    # For 4-directional: snap to cardinal
    if abs(dir.x) > abs(dir.y):
        facing = Vector2(sign(dir.x), 0)
    else:
        facing = Vector2(0, sign(dir.y))
    # Drive animation
    var anim := "walk_"
    if facing == Vector2.RIGHT:   anim += "right"
    elif facing == Vector2.LEFT:  anim += "left"
    elif facing == Vector2.UP:    anim += "up"
    else:                         anim += "down"
    animated_sprite.play(anim)
```

## Screen transitions (room-to-room)

The original Zelda uses per-room screens that pan in when the player exits an edge — the world is a 2D array of discrete rooms. The simplest implementation:

- A `WorldMap` resource holds a 2D grid of room scene paths.
- When the player walks off a screen edge, load the adjacent room scene and pan the camera (or pan the two rooms) across the viewport width/height.
- Keep the player's position relative to the entry edge: if they exit the right edge, place them at the left edge of the new room.

```gdscript
# Detecting exit — Godot 4
func _physics_process(delta: float) -> void:
    move_and_slide()
    var vp := get_viewport_rect()
    if global_position.x > vp.size.x:
        transition_to(Vector2i(room.x + 1, room.y), "left")
    elif global_position.x < 0:
        transition_to(Vector2i(room.x - 1, room.y), "right")
    # ... up/down similarly
```

For the pan, use a Tween on the camera offset or simply animate two `SubViewportContainer` nodes side-by-side.

## JRPG turn-based battle state machine

Turn-based combat (Final Fantasy-style) is a state machine, and implementing it as a pile of booleans (`is_enemy_attacking`, `waiting_for_input`, `is_animation_playing`) guarantees impossible states and bugs. Model it explicitly.

```
States:
  RoundStart     → determine turn order (by speed/ATB/initiative)
  PlayerTurn     → show action menu, wait for selection
  SelectingTarget → highlight target, wait for confirm
  ExecutingAction → play attacker animation, apply damage, play hit animation
  CheckBattleEnd → win/lose/continue? → if done → BattleOver, else → RoundStart
  BattleOver     → show result screen, return to world
```

Each state has `enter()`, `update(delta)`, and `exit()`. The machine only advances on explicit transitions.

**ATB (Active Time Battle — FF4–6 style):** each combatant has an `atb_gauge` that fills at a rate proportional to their speed stat. When a gauge fills, that actor's turn fires (queue their PlayerTurn or enemy AI). The machine needs a "waiting for animation" pause state that freezes all gauges while VFX play.

```gdscript
# Godot 4 — ATB tick (runs during ExecutingAction's sibling idle time)
func tick_atb(delta: float) -> void:
    for combatant in all_combatants:
        if combatant.is_alive and not action_resolving:
            combatant.atb += combatant.speed * delta
            if combatant.atb >= ATB_MAX and combatant not in ready_queue:
                ready_queue.append(combatant)
```

**Damage formula** — keep it in a data resource (`WeaponData`, `AbilityData`) so balance lives in the inspector, not code.

## Dialogue systems

A text box that reveals characters one-by-one is the JRPG staple. The core parts:

1. **Dialogue data** — store in JSON, Godot Resources, or a dedicated tool like Dialogic/Yarn Spinner. Do not hardcode strings in scripts.
2. **Character-by-character reveal** — a timer or accumulator appends one character per tick. `@export var chars_per_sec: float = 40.0`.
3. **Advance / skip** — pressing confirm either skips to the full line (first press) or advances to the next line (second press).
4. **Speaker portrait** — a separate sprite node swaps its texture based on the dialogue entry's `speaker` field.
5. **Pause game** — while a dialogue box is active, the game world should pause (`get_tree().paused = true`) or at minimum suppress movement input.

```gdscript
# Godot 4 — character reveal
var full_text: String = ""
var revealed: float = 0.0

func _process(delta: float) -> void:
    if revealed < full_text.length():
        revealed += chars_per_sec * delta
        label.text = full_text.substr(0, int(revealed))
        if Input.is_action_just_pressed("confirm"):
            revealed = full_text.length()   # skip to end
```

For branching dialogue and conditions, reach for **Dialogic 2** (Godot addon) or **Yarn Spinner** (Unity) rather than building a full dialogue graph from scratch — they're well-tested and handle jumps, variables, and conditions.

## Sprite animation pipeline

- **Sprite sheets:** a single image with all frames laid out in a grid. In Godot, use **AnimatedSprite2D** with a **SpriteFrames** resource (drag the sheet in, set hframes/vframes, assign frame ranges to named animations). In Unity, use the Sprite Editor to slice the sheet, then the Animator.
- **Animation names by convention:** `walk_down`, `walk_up`, `walk_left`, `walk_right`, `idle_down`, `attack_down`, etc. Derive the suffix from the facing direction (above).
- **Frame counts:** retro walk cycles are typically 2–4 frames. Use fewer frames and let the sound + squash/stretch carry the feel rather than animating every nuance. A 4-frame walk with a subtle vertical bob and a footstep sound reads as lively.
- **Flip horizontally** instead of authoring both left and right walk cycles — `animated_sprite.flip_h = (facing.x < 0)`. Only author a separate left cycle if the sprite is asymmetric in a way flipping breaks.

## Retro aesthetics

- **Color palettes:** constrain to a fixed palette (Pico-8's 16 colors, Gameboy 4 greens, etc.) for cohesion. In Godot, a palette-swap shader (`uniform sampler2D palette`) does this at runtime without re-authoring art — swap the palette to give enemies variants or a night-mode filter.
- **Pixel fonts:** import fonts as bitmap fonts at exactly 1× scale (no scaling smoothing). In Godot, import as `BitmapFont` or use a `.fnt` file. Never scale a pixel font to a non-integer size.
- **CRT / scanline shader (optional):** a post-process shader on a `SubViewport` that adds horizontal scanlines and slight barrel distortion. Cheap and effective for the retro feel — but offer it as a toggle; some players find it unreadable.
- **Limited screen shake:** retro games use shake sparingly. On a pixel grid, even 1–2 pixel offset reads as a hard jolt. Scale screenshake values down significantly compared to a modern action game.
- **Sound design:** 8-bit / chiptune SFX alongside or instead of sampled audio. Pitch-randomize (+/- 1–2 semitones) to avoid machine-gun repetition on frequent sounds. Music loop points matter a lot — avoid a perceptible click at the loop.
