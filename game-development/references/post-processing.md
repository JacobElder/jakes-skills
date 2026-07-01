# Full-Screen Post-Processing

## 2D post-processing pipeline

3D post-processing (bloom, DOF, SSAO) lives in `WorldEnvironment` and affects the 3D viewport. **It has no effect on 2D CanvasItems.** For 2D games — or for overlaying 2D effects over 3D — use the screen-texture pipeline:

**Node structure:**
```
CanvasLayer (layer = 127)
  └─ ColorRect (anchors FULL_RECT, size matches viewport)
       └─ ShaderMaterial
```

The `ColorRect` covers the full screen. Its shader samples the screen texture and applies effects. Placing it in a `CanvasLayer` at a high layer number (127 is conventional) puts it above all game content.

```gdscript
# Attach to the CanvasLayer node
func _ready() -> void:
    var rect := $ColorRect
    rect.set_anchors_preset(Control.PRESET_FULL_RECT)
    var mat := ShaderMaterial.new()
    mat.shader = preload("res://shaders/post_process.gdshader")
    rect.material = mat
```

## Screen texture in Godot 4

```glsl
// post_process.gdshader
shader_type canvas_item;

uniform sampler2D SCREEN_TEXTURE : hint_screen_texture, filter_linear_mipmap;
uniform float effect_strength : hint_range(0.0, 1.0) = 0.5;

void fragment() {
    vec4 col = texture(SCREEN_TEXTURE, SCREEN_UV);
    // apply effects here
    COLOR = col;
}
```

`hint_screen_texture` tells Godot this uniform receives the rendered screen. Use `SCREEN_UV` (not `UV`) to sample screen-space positions correctly. Calling `texture(SCREEN_TEXTURE, UV)` samples the ColorRect's own UV space, which is the same as SCREEN_UV only if the rect fills the viewport exactly.

**Common mistake**: using `hint_texture` instead of `hint_screen_texture`, or sampling with `UV` instead of `SCREEN_UV`.

## Vignette

```glsl
void fragment() {
    vec4 col = texture(SCREEN_TEXTURE, SCREEN_UV);
    vec2 uv = SCREEN_UV - 0.5;
    float vig = 1.0 - dot(uv * vec2(1.4, 1.0), uv * vec2(1.4, 1.0)) * vignette_strength;
    vig = clamp(vig, 0.0, 1.0);
    COLOR = vec4(col.rgb * vig, col.a);
}
```

## Chromatic aberration

```glsl
uniform float aberration : hint_range(0.0, 0.02) = 0.005;

void fragment() {
    float r = texture(SCREEN_TEXTURE, SCREEN_UV + vec2(aberration, 0.0)).r;
    float g = texture(SCREEN_TEXTURE, SCREEN_UV).g;
    float b = texture(SCREEN_TEXTURE, SCREEN_UV - vec2(aberration, 0.0)).b;
    COLOR = vec4(r, g, b, 1.0);
}
```

Use chromatic aberration sparingly — trigger it on hits or screen flash, then tween `aberration` back to zero.

## Scanlines (CRT effect)

```glsl
uniform float scanline_strength : hint_range(0.0, 0.5) = 0.15;
uniform float scanline_count : hint_range(100.0, 800.0) = 240.0;

void fragment() {
    vec4 col = texture(SCREEN_TEXTURE, SCREEN_UV);
    float scanline = sin(SCREEN_UV.y * scanline_count * PI) * 0.5 + 0.5;
    col.rgb -= scanline_strength * (1.0 - scanline);
    COLOR = col;
}
```

## Barrel distortion (CRT shape)

```glsl
uniform float distortion : hint_range(0.0, 0.5) = 0.1;

vec2 barrel(vec2 uv) {
    uv -= 0.5;
    float r2 = dot(uv, uv);
    uv *= 1.0 + distortion * r2;
    return uv + 0.5;
}

void fragment() {
    vec2 uv = barrel(SCREEN_UV);
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        COLOR = vec4(0.0);
        return;
    }
    COLOR = texture(SCREEN_TEXTURE, uv);
}
```

## Color grading (LUT)

```glsl
uniform sampler2D lut : hint_default_white;
uniform float lut_strength : hint_range(0.0, 1.0) = 1.0;

void fragment() {
    vec4 col = texture(SCREEN_TEXTURE, SCREEN_UV);
    // 16x16x16 LUT packed as 256x16 strip
    float lut_size = 16.0;
    float r = col.r * (lut_size - 1.0) / lut_size + 0.5 / lut_size;
    float g = col.g * (lut_size - 1.0) / lut_size + 0.5 / lut_size;
    float b = floor(col.b * lut_size) / lut_size;
    vec2 lut_uv = vec2(b + r / lut_size, g);
    vec4 graded = texture(lut, lut_uv);
    COLOR = mix(col, graded, lut_strength);
}
```

## Combining effects in one pass

Chain all effects in a single shader's `fragment()` function. Each additional screen texture read costs performance; keep it to one per pass when possible.

## Toggling effects at runtime

```gdscript
func set_aberration(amount: float) -> void:
    $CanvasLayer/ColorRect.material.set_shader_parameter("aberration", amount)

func flash_aberration() -> void:
    set_aberration(0.02)
    var tw := create_tween()
    tw.tween_method(set_aberration, 0.02, 0.0, 0.3)
```

## WorldEnvironment (3D only)

`WorldEnvironment` controls bloom, DOF, SSAO, SDFGI, tone mapping, and ambient light for the **3D** render pipeline. These have zero effect on 2D sprites. For a 2D game that wants bloom-like glow, use `CanvasItem.use_parent_material` or a custom shader; for light bleeding from bright sprites, `Light2D` with high energy is the correct approach.

## Performance

- Screen texture reads are expensive on mobile — profile on target hardware.
- One full-screen pass is usually fine; avoid chaining multiple `SubViewport` renders.
- For selective effects (only on a region), use a `ColorRect` with a smaller size and clip it with a `ClipChildren` mask.
