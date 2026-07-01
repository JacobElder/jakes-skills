# Shaders and Visual Effects

Shaders are the fastest route from "looks like a prototype" to "looks like a shipped game." Most of the effects players associate with polish — hit feedback, outlines, dissolves, vignettes — are 20–80 lines of GLSL. Writing them yourself rather than hunting for asset-store plugins keeps your bundle small and the effect tunable from code.

## Godot shader basics

Godot uses a custom shading language that is GLSL-compatible syntax. Every shader starts with a `shader_type` declaration that determines the built-ins available:

| `shader_type` | Used on | Key built-ins |
|---|---|---|
| `canvas_item` | Sprite2D, MeshInstance2D, ColorRect, Control nodes | `TEXTURE`, `UV`, `COLOR`, `SCREEN_TEXTURE` |
| `spatial` | MeshInstance3D, any 3D surface | `ALBEDO`, `ROUGHNESS`, `METALLIC`, `NORMAL`, `VERTEX` |
| `sky` | Sky resource | `SKY`, `EYEDIR`, `RADIANCE` |
| `particles` | GPUParticles2D/3D | `TRANSFORM`, `VELOCITY`, `COLOR` |

For 2D sprite effects, you almost always want `canvas_item`. For 3D surface effects, `spatial`.

### The two core functions

`vertex()` runs once per vertex and can transform geometry. For sprite effects it is rarely needed.

`fragment()` runs once per pixel and is where all the interesting 2D work happens. The default pass-through:

```glsl
shader_type canvas_item;

void fragment() {
    COLOR = texture(TEXTURE, UV);
}
```

`TEXTURE` is the sprite's source texture. `UV` is the texture coordinate at the current pixel (0,0 top-left to 1,1 bottom-right). `texture(TEXTURE, UV)` returns a `vec4` (r, g, b, a). `COLOR` is the output pixel color including alpha.

### Uniforms — parameters editable from the Inspector and GDScript

Uniforms are shader inputs you expose to the outside world. Declare them at the top of the shader:

```glsl
uniform float flash_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 outline_color : source_color = vec4(1.0, 0.0, 0.0, 1.0);
uniform sampler2D noise_tex : hint_default_black;
```

- `hint_range(min, max)` adds an Inspector slider
- `source_color` tells the editor to show a color picker with gamma correction
- `hint_default_black` / `hint_default_white` sets the fallback texture

**Setting uniforms from GDScript:**

```gdscript
# On the node that has a ShaderMaterial:
$Sprite2D.material.set_shader_parameter("flash_amount", 1.0)

# Reading back:
var val = $Sprite2D.material.get_shader_parameter("flash_amount")
```

### Applying a shader

1. Select a Sprite2D (or MeshInstance2D, ColorRect, etc.) in the Inspector.
2. Under Material, click the empty slot and choose **New ShaderMaterial**.
3. Click the ShaderMaterial to expand it, then click Shader → New Shader.
4. The shader editor opens. Paste your code. The effect is live in the viewport immediately.

Shaders are per-material, not per-node-type. Any node with a material slot can carry one.

---

## Hit flash

A hit flash is a purely visual one-frame-ish overlay that communicates damage received. It is **not** hitstop (which freezes game time) — they often combine, but they are separate mechanisms. Hitstop freezes the simulation; hit flash replaces pixel color with white while preserving shape.

**The shader:**

```glsl
shader_type canvas_item;

uniform float flash_active : hint_range(0.0, 1.0) = 0.0;

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    // Blend between normal color and full-white at original alpha
    COLOR = mix(tex, vec4(1.0, 1.0, 1.0, tex.a), flash_active);
}
```

Using `mix()` with `flash_active` as the blend weight means you can also do partial-intensity flashes (e.g., 0.5 for a softer glow). At `flash_active = 1.0`, every opaque pixel goes white; transparent pixels stay transparent because `tex.a` is applied to the white.

**Triggering from GDScript — tween approach (preferred):**

```gdscript
func take_hit():
    var mat = $Sprite2D.material
    mat.set_shader_parameter("flash_active", 1.0)
    # Tween back to 0 in 0.08 seconds
    var tween = create_tween()
    tween.tween_method(
        func(v): mat.set_shader_parameter("flash_active", v),
        1.0, 0.0, 0.08
    )
```

**Timer approach (simpler, but binary on/off):**

```gdscript
func take_hit():
    $Sprite2D.material.set_shader_parameter("flash_active", 1.0)
    await get_tree().create_timer(0.08).timeout
    $Sprite2D.material.set_shader_parameter("flash_active", 0.0)
```

Works identically with AnimatedSprite2D — the shader operates on whatever texture the sprite is currently displaying, so frame changes don't break it.

---

## Sprite outline

An outline shader samples the texture in 4 or 8 neighboring directions. If the current pixel is transparent but any neighbor is opaque, it draws the outline color. If the current pixel is opaque, it draws normally. The result is a clean pixel-perfect (or smooth) border without any mesh changes.

**The shader (8-direction, suitable for most uses):**

```glsl
shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_size : hint_range(0.0, 8.0) = 1.0;

void fragment() {
    vec2 size = outline_size / vec2(textureSize(TEXTURE, 0));

    vec4 tex = texture(TEXTURE, UV);

    // Sample all 8 neighbors
    float neighbor_alpha = 0.0;
    neighbor_alpha += texture(TEXTURE, UV + vec2(size.x,  0.0)).a;
    neighbor_alpha += texture(TEXTURE, UV + vec2(-size.x, 0.0)).a;
    neighbor_alpha += texture(TEXTURE, UV + vec2(0.0,  size.y)).a;
    neighbor_alpha += texture(TEXTURE, UV + vec2(0.0, -size.y)).a;
    neighbor_alpha += texture(TEXTURE, UV + vec2(size.x,  size.y)).a;
    neighbor_alpha += texture(TEXTURE, UV + vec2(-size.x, size.y)).a;
    neighbor_alpha += texture(TEXTURE, UV + vec2(size.x, -size.y)).a;
    neighbor_alpha += texture(TEXTURE, UV + vec2(-size.x,-size.y)).a;

    // Current pixel is transparent but has an opaque neighbor → outline
    if (tex.a < 0.1 && neighbor_alpha > 0.0) {
        COLOR = outline_color;
    } else {
        COLOR = tex;
    }
}
```

`textureSize(TEXTURE, 0)` returns the texture's pixel dimensions as an `ivec2`; dividing `outline_size` by it converts pixels to UV space.

**Critical: texture filtering for pixel art.** For pixel art sprites, the outline only looks correct when the texture filter is **Nearest** (not Linear). Linear filtering blurs the alpha edge and the outline samples will pick up partial-alpha values instead of clean 0 or 1, producing fuzzy or doubled borders. Set this in Project Settings → Rendering → Textures → Canvas Textures → Default Texture Filter → **Nearest**. Or per-sprite by clicking the texture in the FileSystem dock → Import tab → Filter: Nearest.

For smooth/painted sprites where Linear filtering is appropriate, increase `outline_size` to 2–3 pixels; the blurred alpha edge means a 1-pixel sample may miss the boundary.

**Toggling the outline from GDScript:**

```gdscript
func set_selected(selected: bool):
    var mat = $Sprite2D.material
    mat.set_shader_parameter("outline_color",
        Color(1.0, 0.8, 0.0, 1.0) if selected else Color(0, 0, 0, 0))
```

Setting `outline_color.a = 0` is the cleanest on/off toggle; it avoids shader branching and lets the outline fade in if you tween the alpha.

---

## Dissolve effect

A dissolve uses a noise texture as a threshold map. Pixels with noise values below `dissolve_amount` are discarded (made invisible). An edge glow — pixels just above the threshold — adds fire/energy for free. Tweening `dissolve_amount` 0→1 from GDScript produces the full character-death-burst effect.

**MUST use `discard`, not `alpha = 0`.** Alpha-zeroed pixels still exist in the depth buffer and can occlude other transparent objects. `discard` removes the pixel from the pipeline entirely, which is correct for transparent rendering order.

**The shader:**

```glsl
shader_type canvas_item;

uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform float edge_width : hint_range(0.0, 0.2) = 0.05;
uniform vec4 edge_color : source_color = vec4(1.0, 0.4, 0.0, 1.0);
uniform sampler2D noise_tex : hint_default_black;

void fragment() {
    vec4 tex = texture(TEXTURE, UV);

    // Don't process fully transparent pixels at all
    if (tex.a < 0.01) {
        discard;
    }

    float noise_val = texture(noise_tex, UV).r;

    if (noise_val < dissolve_amount) {
        discard;
    } else if (noise_val < dissolve_amount + edge_width) {
        // Edge glow band
        COLOR = edge_color;
        COLOR.a = tex.a;
    } else {
        COLOR = tex;
    }
}
```

**Setting up the noise texture in Godot.** Create a NoiseTexture2D resource (Inspector → New NoiseTexture2D). Assign a FastNoiseLite inside it. Set Width/Height to match or tile against your sprite size (128×128 or 256×256 is usually enough). Assign the resource to the `noise_tex` uniform.

**Triggering from GDScript on death:**

```gdscript
func die():
    var mat = $Sprite2D.material
    var tween = create_tween()
    tween.tween_method(
        func(v): mat.set_shader_parameter("dissolve_amount", v),
        0.0, 1.0, 0.6   # 0.6 seconds to fully dissolve
    )
    tween.tween_callback(queue_free)
```

**Edge color tips.** For fire: orange/red. For ice/freeze: pale blue. For death/ghost: white. For acid: lime green. Tween the `edge_width` alongside `dissolve_amount` to make the glow pulse as it disappears (widen early, narrow at the end).

---

## Palette swap

Palette swapping renders a source sprite's colors through a remapping table, enabling unlimited color variants from a single spritesheet. Used for enemy variants, team colors, and day/night palette shifts in retro-style games.

**How it works.** The source art must use a small, indexed palette — each unique color maps to a distinct row or column in a 1D palette texture. The shader samples the source color, looks up its index in a small lookup table (LUT), then fetches the replacement color from the current palette texture.

**In practice for Godot pixel art:** Create a palette texture that is N pixels wide by 2+ pixels tall. Row 0 is the original palette, row 1 is the first variant, row 2 is the second, etc. The shader reads the source pixel, finds its position in row 0, then returns the pixel at the same x position in the active row.

```glsl
shader_type canvas_item;

uniform sampler2D palette_tex;   // The palette strip (original + variants)
uniform int palette_index = 0;   // 0 = original, 1 = variant 1, etc.
uniform int palette_width = 8;   // Number of colors in the palette

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    if (tex.a < 0.01) {
        COLOR = tex;
        return;
    }

    // Convert source color to UV into the palette strip's top row
    float palette_row_count = float(textureSize(palette_tex, 0).y);
    float match_u = -1.0;
    float orig_row_v = 0.5 / palette_row_count;  // Center of row 0

    // Search for the source color in the original palette row
    for (int i = 0; i < palette_width; i++) {
        float check_u = (float(i) + 0.5) / float(palette_width);
        vec4 palette_color = texture(palette_tex, vec2(check_u, orig_row_v));
        if (distance(tex.rgb, palette_color.rgb) < 0.01) {
            match_u = check_u;
            break;
        }
    }

    if (match_u >= 0.0) {
        float target_v = (float(palette_index) + 0.5) / palette_row_count;
        COLOR = texture(palette_tex, vec2(match_u, target_v));
        COLOR.a = tex.a;
    } else {
        COLOR = tex;   // Color not in palette — pass through unchanged
    }
}
```

**Notes.** The palette texture must use Nearest filtering (no blending between palette entries). Keep palette size small — the linear search in the shader is fine for 8–16 colors, gets expensive past 32. For day/night shifts, tween `palette_index` through a float and sample two rows, mixing between them.

---

## Post-process effects

Post-process effects are applied to the entire rendered frame rather than to individual sprites. In Godot 2D, the standard approach is a CanvasLayer at the top of the scene tree containing a ColorRect stretched to fill the screen, with a ShaderMaterial on it that reads `SCREEN_TEXTURE`.

**Setup:**

```gdscript
# PostProcess.gd — attach to a CanvasLayer node (layer = 99 or similar)
# Child: ColorRect with anchors set to Full Rect
func _ready():
    $ColorRect.material = ShaderMaterial.new()
    $ColorRect.material.shader = preload("res://shaders/vignette.gdshader")
```

Or set it up manually: CanvasLayer → ColorRect (Layout: Full Rect) → Inspector → Material → New ShaderMaterial → Shader → New Shader.

### Vignette

Darkens the corners and edges of the screen. Classic "focus" effect; also useful for low-health warning states.

```glsl
shader_type canvas_item;

uniform float inner_radius : hint_range(0.0, 1.0) = 0.4;
uniform float outer_radius : hint_range(0.0, 1.5) = 0.9;
uniform float intensity : hint_range(0.0, 1.0) = 0.6;

void fragment() {
    vec4 screen = texture(SCREEN_TEXTURE, SCREEN_UV);
    float dist = distance(SCREEN_UV, vec2(0.5, 0.5));
    float vignette = 1.0 - smoothstep(inner_radius, outer_radius, dist) * intensity;
    COLOR = vec4(screen.rgb * vignette, screen.a);
}
```

For a red pulsing low-health vignette, multiply `intensity` by a sine wave driven from GDScript via a uniform.

### Chromatic aberration

Offsets the R, G, and B channels by slightly different amounts, producing the color-fringe look of a cheap lens. Use sparingly — effective as a hit reaction or screen damage signal.

```glsl
shader_type canvas_item;

uniform float aberration_amount : hint_range(0.0, 0.02) = 0.005;

void fragment() {
    vec2 dir = SCREEN_UV - vec2(0.5);
    float r = texture(SCREEN_TEXTURE, SCREEN_UV + dir * aberration_amount).r;
    float g = texture(SCREEN_TEXTURE, SCREEN_UV).g;
    float b = texture(SCREEN_TEXTURE, SCREEN_UV - dir * aberration_amount).b;
    float a = texture(SCREEN_TEXTURE, SCREEN_UV).a;
    COLOR = vec4(r, g, b, a);
}
```

### Scanlines

CRT-style horizontal scan lines. The `sin()` on the y pixel coordinate creates alternating light/dark bands.

```glsl
shader_type canvas_item;

uniform float line_count : hint_range(100.0, 1000.0) = 240.0;
uniform float line_opacity : hint_range(0.0, 1.0) = 0.15;

void fragment() {
    vec4 screen = texture(SCREEN_TEXTURE, SCREEN_UV);
    float scanline = sin(SCREEN_UV.y * line_count * PI) * 0.5 + 0.5;
    COLOR = vec4(screen.rgb * (1.0 - scanline * line_opacity), screen.a);
}
```

### Color grading with a LUT

A 3D LUT (Look-Up Table) is a 512×512 texture arranged as a 8×8 grid of 64×64 color cubes. Sample it to remap every screen color through an artistic grade — film noir, warm sunset, underwater blue, etc.

```glsl
shader_type canvas_item;

uniform sampler2D lut_tex;
uniform float lut_amount : hint_range(0.0, 1.0) = 1.0;

// Standard 512x512, 8x8 tile LUT lookup
vec3 apply_lut(vec3 color) {
    float lut_size = 64.0;
    float tile_count = 8.0;

    color = clamp(color, 0.0, 1.0);
    float bv = color.b * (lut_size - 1.0);
    float b_lo = floor(bv);
    float b_hi = ceil(bv);
    float b_frac = bv - b_lo;

    vec2 tile_size = vec2(1.0 / tile_count);
    vec2 offset_lo = vec2(mod(b_lo, tile_count), floor(b_lo / tile_count)) * tile_size;
    vec2 offset_hi = vec2(mod(b_hi, tile_count), floor(b_hi / tile_count)) * tile_size;

    vec2 rg = color.rg * ((lut_size - 1.0) / lut_size) * tile_size + tile_size * 0.5 / lut_size;

    vec3 col_lo = texture(lut_tex, offset_lo + rg).rgb;
    vec3 col_hi = texture(lut_tex, offset_hi + rg).rgb;
    return mix(col_lo, col_hi, b_frac);
}

void fragment() {
    vec4 screen = texture(SCREEN_TEXTURE, SCREEN_UV);
    vec3 graded = apply_lut(screen.rgb);
    COLOR = vec4(mix(screen.rgb, graded, lut_amount), screen.a);
}
```

Generate LUT textures in Photoshop (Camera Raw filter → export), DaVinci Resolve, or from a neutral identity LUT run through any color grade.

---

## Unity shader equivalents

Unity URP (Universal Render Pipeline) uses **Shader Graph** for visual node-based authoring — the equivalent of Godot's visual shader editor. For code-first work, URP shaders are HLSL with custom render pipeline hooks.

| Godot | Unity URP equivalent |
|---|---|
| `shader_type canvas_item` | Sprite Lit/Unlit Graph or a custom HLSL shader with `Tags { "Queue" = "Transparent" }` |
| `uniform` | Properties block in ShaderLab; exposed to Material Inspector |
| `texture(TEXTURE, UV)` | `SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, IN.uv)` |
| `SCREEN_TEXTURE` + ColorRect post-process | **Renderer Feature** on the URP Renderer asset; or the Full Screen Pass Renderer Feature (URP 14+) |
| `discard` | `clip(-1)` or `discard` (both work in HLSL) |
| `set_shader_parameter()` | `material.SetFloat("_Name", value)` / `material.SetColor()` / `material.SetTexture()` |

For sprite outlines in Unity URP, the standard approach is an **Outline Renderer Feature** that renders the sprite twice — once at scale with the outline color into a stencil buffer, once normally. Or use a custom shader with the same 8-direction sample approach shown above. The Post-process Volume system (via the Volume component on camera) provides vignette, chromatic aberration, bloom, and color grading built-in without writing shaders.

---

## Performance notes

### `discard` and mobile

`discard` (and its HLSL equivalent `clip`) breaks **early-Z culling** on the GPU — the GPU can no longer reject pixels based on depth before running the fragment shader, because the shader itself decides visibility. On desktop this is usually fine. On mobile (especially tile-based GPUs like Adreno, Mali), heavy use of `discard` in complex scenes is a measurable performance regression. Alternatives for mobile: alpha blend with `COLOR.a = 0.0` where depth precision doesn't matter, or accept slightly incorrect sort order. For dissolve on mobile, consider a simpler threshold-only version without the edge glow pass.

### Texture samples per fragment

Every `texture()` call is a texture fetch. Fragment shaders running at 1080p or higher call once per pixel. 8-direction outline sampling = 8 extra fetches per pixel. For a full-screen post-process, that multiplies by ~2M pixels. Keep post-process shaders at ≤4 fetches for mobile targets; desktop can handle 8–16 comfortably for non-full-screen effects.

### Uniform update cost

`set_shader_parameter()` triggers a material parameter update on the GPU driver. For parameters that change every frame (e.g., a time uniform for animated effects), batch the update into `_process()` once per frame. Do not call it in a loop or from multiple signals per frame.

### Shader compilation stutter

Godot compiles shaders on first use, which can cause a one-frame hitch when a shader is encountered for the first time. For shaders used in critical gameplay moments (hit flash, dissolve), trigger a dummy draw off-screen during the loading screen or level start to pre-compile the shader variant.

### Decision matrix

| Effect | Full-screen? | Mobile safe? | Fetch count |
|---|---|---|---|
| Hit flash | No | Yes | 1 |
| Outline (4-dir) | No | Mostly | 5 |
| Outline (8-dir) | No | Careful | 9 |
| Dissolve (with edge) | No | Careful (`discard`) | 2 |
| Vignette | Yes | Yes | 1 |
| Chromatic aberration | Yes | Careful (3 fetches) | 3 |
| Scanlines | Yes | Yes | 1 |
| Color LUT | Yes | Mostly | 2–3 |
| Palette swap | No | Yes | 1 + search |
