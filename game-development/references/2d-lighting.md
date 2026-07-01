# 2D Lighting in Godot 4: Light2D, Normal Maps, and Occlusion

## 2D lighting is a separate pipeline from 3D

Godot's 3D GI (LightmapGI, SDFGI) has no effect on 2D scenes. 2D lighting uses `Light2D` nodes with a canvas-space pipeline. WorldEnvironment is also irrelevant for 2D lighting.

## The three nodes you need

| Node | Purpose |
|---|---|
| `CanvasModulate` | Sets ambient color — **required to see lights**; default white = fully lit everywhere |
| `PointLight2D` | Circular light source (torch, lamp, glow) |
| `DirectionalLight2D` | Infinite parallel light (sun, moon for top-down games) |
| `LightOccluder2D` | Casts shadows from a polygon shape |

## Step 1: CanvasModulate (the most-missed setup step)

Without `CanvasModulate`, the scene is fully lit by default and adding lights has no visible effect (they add brightness to an already-white surface). Set the ambient to dark to make lights meaningful:

```gdscript
# Add CanvasModulate to the scene root or a persistent CanvasLayer
var modulate := CanvasModulate.new()
modulate.color = Color(0.05, 0.05, 0.05)  # near-black ambient = torch-lit dungeon
add_child(modulate)
```

In the editor: add a `CanvasModulate` node, set its `color` to a dark grey or black.

## Step 2: PointLight2D setup

```gdscript
# Torch carried by player
@onready var torch_light: PointLight2D = $TorchLight

func _ready() -> void:
    torch_light.texture = preload("res://lights/radial_gradient.png")  # or use default
    torch_light.texture_scale = 3.0      # radius of the light cone
    torch_light.energy = 1.2            # brightness
    torch_light.color = Color(1.0, 0.7, 0.3)  # warm orange torch color
    torch_light.shadow_enabled = true   # enable shadow casting
    torch_light.shadow_filter = Light2D.SHADOW_FILTER_PCF5  # soft shadows
```

**`texture`**: a radial gradient texture (white center → transparent edge). Godot provides a default; create a custom one for sharper falloff. The texture's alpha drives the light intensity at each pixel.

**`range_height`**: the perceived height of the light above the canvas — affects how normal maps respond. 0 = light at canvas level (flat), higher = light more "above" the surface.

## Step 3: Normal maps for depth effect

Normal maps make flat 2D sprites react to Light2D positions, giving a 3D-depth appearance.

**Import setting (most-common mistake):** The normal map texture must be imported as `Normal Map` type, not `Color/SRGB`. In the Import panel: select the normal map texture → set `Detect 3D` to off → set import type to `Normal Map`. Godot will not correctly interpret normal map data imported as a color texture.

```gdscript
# Sprite2D — assign normal map in the Inspector
# Texture: res://sprites/character.png
# Normal Map: res://sprites/character_normal.png
```

Or in code:
```gdscript
var sprite := $Sprite2D
sprite.texture = preload("res://sprites/character.png")
sprite.normal_map = preload("res://sprites/character_normal.png")
```

Normal maps are generated externally (Sprite Illuminator, AwesomeBump, Laigter for pixel art) — Godot doesn't generate them from the sprite. For pixel art, Laigter is the standard tool.

**`range_height` on PointLight2D affects normal map response**: a value of 0 means the light is coplanar with the sprite (only left/right shading); higher values add top-down shading. Typical value: 32–128 for top-down games.

## Step 4: Shadow casting with LightOccluder2D

```
Wall (Sprite2D or TileMapLayer)
└── LightOccluder2D
    └── OccluderPolygon2D    ← polygon traced around the opaque part of the sprite
```

```gdscript
var occluder := LightOccluder2D.new()
var polygon := OccluderPolygon2D.new()
polygon.polygon = PackedVector2Array([
    Vector2(-32, -32), Vector2(32, -32),
    Vector2(32, 32), Vector2(-32, 32)
])
polygon.cull_mode = OccluderPolygon2D.CULL_CLOCKWISE  # solid polygon
occluder.occluder = polygon
$Wall.add_child(occluder)
```

In the editor, draw the polygon with the polygon tool on the OccluderPolygon2D.

**TileMap shadow casting**: On a TileMapLayer, open the TileSet → select a tile → Physics tab → add a LightOccluder polygon per tile. All tiles of that type automatically cast shadows.

## Controlling which layers are lit

`Light2D` has `item_cull_mask` — only sprites on the matching canvas layers receive this light. Use this to:
- Keep UI elements always at full brightness (UI layer excluded from dungeon torch mask)
- Have ceiling sprites unaffected by floor-level torches

```gdscript
torch_light.item_cull_mask = 1   # only lights canvas layer 1 (ground layer)
# HUD CanvasLayer (layer 10) is not affected
```

## Common mistakes

**No CanvasModulate → lights appear to do nothing**: The scene defaults to full ambient white, so adding light has no visible effect. Always add CanvasModulate with a dark color when using 2D lights.

**Normal map imported as Color instead of Normal Map**: The Import panel default is Color/SRGB. If the normal map looks wrong (flat, inverted bumps), check the import type.

**`range_height = 0` with normal maps**: Sprites look correctly lit from the side but have no top-down shading. Raise `range_height` to 64–128 for top-down games.

**Shadow polygon doesn't match sprite**: If the LightOccluder2D polygon is larger than the visible sprite pixels, shadows extend beyond the sprite edge. Trace the polygon tightly around the opaque region.

**Using WorldEnvironment for 2D lighting**: WorldEnvironment only affects the 3D rendering pipeline — it has no effect on 2D sprites or Light2D nodes.
