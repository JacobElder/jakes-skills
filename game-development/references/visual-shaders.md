# Visual Shaders and Shader Graph in Godot 4

## When to use the visual shader editor vs code

| Situation | Use |
|---|---|
| Artist on team, not comfortable with GLSL | Visual shader editor |
| Rapid prototyping with preview | Visual shader editor |
| Complex procedural math (domain warping, noise stacking) | Code (ShaderMaterial) |
| Shared shader logic across materials | Code (include files via `#include`) |
| Performance-critical inner loop (strip dead nodes) | Code |
| Needs to be modified programmatically at runtime via `set_shader_parameter()` | Either — params work the same |
| Needs compile-time branching (`#ifdef`) | Code only |

Both produce identical bytecode — the visual editor is a node graph front-end that generates GLSL. Performance is determined by the generated GLSL, not the authoring tool.

## Node-to-GLSL mapping

| Visual shader node | GLSL equivalent |
|---|---|
| `FragmentOutput` | `void fragment()` function body |
| `VertexOutput` | `void vertex()` function body |
| `UV` | `UV` (vec2 built-in) |
| `Time` | `TIME` |
| `Texture2D` (sampler) | `texture(tex, uv)` |
| `ColorUniform` / `FloatUniform` | `uniform vec4 color` / `uniform float val` |
| `VectorOp (Add)` | `a + b` |
| `VectorOp (Multiply)` | `a * b` |
| `Mix` | `mix(a, b, weight)` |
| `Clamp` | `clamp(val, min, max)` |
| `Step` | `step(edge, x)` |
| `SmoothStep` | `smoothstep(e0, e1, x)` |
| `Expression` node | Inline GLSL block — bridge to arbitrary code |
| `GroupOutput` / `GroupInput` | Sub-graph encapsulation (no GLSL equivalent) |

## Reading a visual shader as GLSL

A visual shader is a directed acyclic graph. Reading order: follow connections from left (inputs/uniforms) to right (FragmentOutput). Each node is a function call; connections are variable assignments.

Example — tinted texture with pulse:
```
Texture2D → Multiply → FragmentOutput.albedo
                ↑
           ColorUniform × (sin(Time × speed) × 0.5 + 0.5)
```

Generated GLSL equivalent:
```glsl
void fragment() {
    vec4 tex_color = texture(albedo_tex, UV);
    float pulse = sin(TIME * speed) * 0.5 + 0.5;
    ALBEDO = (tex_color * tint_color * pulse).rgb;
}
```

## Modifying visual shaders at runtime

`set_shader_parameter()` works identically for visual and code shaders. Uniform nodes in the visual editor become `uniform` variables in the generated GLSL:

```gdscript
# Works regardless of whether the shader was made in visual editor or code
$MeshInstance3D.material_override.set_shader_parameter("tint_color", Color.RED)
$MeshInstance3D.material_override.set_shader_parameter("speed", 2.5)
```

## Bridging visual and code shaders: the Expression node

The `Expression` node lets you write raw GLSL inside a visual shader, exposing named input ports and one output port. Use it for math that's tedious in node graphs (e.g., hash functions, custom noise):

```
Expression node inputs: uv (vec2)
Expression body:
    return fract(sin(dot(uv, vec2(127.1, 311.7))) * 43758.5453);
```

This returns a float pseudo-random value per UV position, usable downstream in the graph.

## Converting visual shader to code

In the editor: select the ShaderMaterial → click the shader resource → `Convert to Text`. This gives the generated GLSL. From then on it's a pure code shader. **Conversion is one-way** — you cannot convert back to visual shader.

Use this when:
- You need `#ifdef` branching (e.g., low-quality fallback)
- You need `#include` for shared functions
- The generated GLSL reveals a redundant calculation you want to optimize

## Common mistakes

**Leaving disconnected nodes active**: Disconnected nodes still compile and may generate unused uniforms. Delete nodes you're not using — they add compile overhead.

**Uniform name collisions**: If two uniforms share a name across different materials on the same node, Godot will warn. Prefix uniform names with the shader's purpose: `hit_flash_color`, not just `color`.

**Forgetting `render_mode`**: The visual editor defaults to `spatial` render mode. For unlit effects (UI, emissive-only), set render_mode to `unshaded` in Shader Settings — otherwise Godot wastes time on lighting calculations the shader ignores.

**Artist exports as new ShaderMaterial each time**: Set up a `.tres` ShaderMaterial resource (not inline) so artists can edit the visual shader without breaking references in scenes.
