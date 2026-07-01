# Fog of War and Minimap

## Minimap: two approaches

### Approach 1 — SubViewport (recommended for most games)

A second camera renders the entire level at high zoom-out. The viewport texture is displayed in the HUD.

```gdscript
# MinimapCamera.gd — separate Camera2D inside a SubViewport
extends Camera2D

@export var follow_target: Node2D
@export var minimap_zoom: Vector2 = Vector2(0.12, 0.12)   # zoom out to see the whole map

func _ready() -> void:
    zoom = minimap_zoom

func _physics_process(_delta: float) -> void:
    if follow_target:
        global_position = follow_target.global_position
```

```
SubViewport (size: 200×200, world_2d shared with main viewport)
  └─ MinimapCamera
```

```gdscript
# MinimapDisplay.gd — in the HUD CanvasLayer
@onready var minimap_rect: TextureRect = $MinimapRect
@onready var viewport: SubViewport = $"../MinimapViewport"

func _ready() -> void:
    minimap_rect.texture = viewport.get_texture()
    # Circular mask via shader
    var shader := preload("res://shaders/circle_mask.gdshader")
    minimap_rect.material = ShaderMaterial.new()
    minimap_rect.material.shader = shader
```

```glsl
// circle_mask.gdshader — clips minimap to circle
shader_type canvas_item;
void fragment() {
    float d = distance(UV, vec2(0.5));
    COLOR = texture(TEXTURE, UV);
    COLOR.a *= step(d, 0.5);
}
```

**Shared `World2D`:** assign the same `World2D` to the SubViewport as the main viewport. All nodes render in both. Use a visual layer (VisualInstance2D layer bits) so minimap-only icons show only in the minimap camera, and some objects are excluded from the minimap.

### Approach 2 — Icon overlay (lightweight, no second camera)

Compute each entity's position relative to the player, scale to minimap size, and draw icons.

```gdscript
# MinimapOverlay.gd — Control node in HUD
const MAP_SIZE := Vector2(150, 150)
const WORLD_RADIUS := 400.0   # half-width of visible minimap in world units

@export var player: Node2D
@export var tracked_groups: Array[String] = ["enemies", "pickups", "npcs"]

func _draw() -> void:
    # Background circle
    draw_circle(MAP_SIZE / 2.0, MAP_SIZE.x / 2.0, Color(0, 0, 0, 0.6))
    _draw_entity(player.global_position, Color.GREEN, 5.0)  # player dot
    for group in tracked_groups:
        for node in get_tree().get_nodes_in_group(group):
            if node is Node2D:
                _draw_entity(node.global_position, _color_for_group(group), 3.0)

func _draw_entity(world_pos: Vector2, color: Color, radius: float) -> void:
    var relative := (world_pos - player.global_position) / WORLD_RADIUS
    relative = relative.clamp(Vector2(-1, -1), Vector2(1, 1))
    var map_pos := MAP_SIZE / 2.0 + relative * MAP_SIZE / 2.0
    draw_circle(map_pos, radius, color)

func _physics_process(_delta: float) -> void:
    queue_redraw()  # redraw every physics frame
```

## Fog of war

Grid-based: each cell has a state — UNSEEN, REVEALED (visited but not currently visible), VISIBLE.

```gdscript
# FogOfWar.gd — autoload or level node
extends Node2D

enum CellState { UNSEEN, REVEALED, VISIBLE }

@export var cell_size: int = 32
@export var vision_radius: int = 5   # in cells
@export var map_width: int = 40
@export var map_height: int = 30

var _grid: PackedByteArray  # CellState per cell, flat array

func _ready() -> void:
    _grid.resize(map_width * map_height)
    _grid.fill(CellState.UNSEEN)
    queue_redraw()

func update_vision(player_world_pos: Vector2) -> void:
    var px := int(player_world_pos.x / cell_size)
    var py := int(player_world_pos.y / cell_size)

    # Mark all currently VISIBLE as REVEALED first
    for i in _grid.size():
        if _grid[i] == CellState.VISIBLE:
            _grid[i] = CellState.REVEALED

    # Reveal cells in vision radius
    for dy in range(-vision_radius, vision_radius + 1):
        for dx in range(-vision_radius, vision_radius + 1):
            if dx * dx + dy * dy > vision_radius * vision_radius:
                continue  # circular mask
            var cx := px + dx
            var cy := py + dy
            if cx < 0 or cy < 0 or cx >= map_width or cy >= map_height:
                continue
            # Optional: raycast for line-of-sight fog (skip for simple fog)
            _grid[cy * map_width + cx] = CellState.VISIBLE

    queue_redraw()

func _draw() -> void:
    for cy in map_height:
        for cx in map_width:
            var state: int = _grid[cy * map_width + cx]
            var rect := Rect2(cx * cell_size, cy * cell_size, cell_size, cell_size)
            match state:
                CellState.UNSEEN:
                    draw_rect(rect, Color(0, 0, 0, 1.0))
                CellState.REVEALED:
                    draw_rect(rect, Color(0, 0, 0, 0.55))
                CellState.VISIBLE:
                    pass  # transparent

func get_cell_state(world_pos: Vector2) -> int:
    var cx := int(world_pos.x / cell_size)
    var cy := int(world_pos.y / cell_size)
    if cx < 0 or cy < 0 or cx >= map_width or cy >= map_height:
        return CellState.UNSEEN
    return _grid[cy * map_width + cx]
```

Call `FogOfWar.update_vision(player.global_position)` each physics frame.

### Persisting fog across sessions

```gdscript
# In save_game():
save_data["fog_grid"] = _grid.hex_encode()

# In load_game():
_grid = PackedByteArray.hex_decode(save_data["fog_grid"])
queue_redraw()
```

`PackedByteArray.hex_encode()` serializes the entire grid as a compact hex string. For a 40×30 map that's 1200 bytes → 2400-char hex string. Well within JSON limits.

### Line-of-sight fog (walls block vision)

For the visibility pass, replace the direct write with a raycast per cell:

```gdscript
func _cell_has_los(from_cell: Vector2i, to_cell: Vector2i) -> bool:
    var from_world := Vector2(from_cell) * cell_size + Vector2(cell_size, cell_size) / 2.0
    var to_world   := Vector2(to_cell)   * cell_size + Vector2(cell_size, cell_size) / 2.0
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(from_world, to_world, 0b0100)  # wall layer
    return get_world_2d().direct_space_state.intersect_ray(query).is_empty()
```

This is expensive for a large radius — cache it or run it on a background thread (Godot 4's `WorkerThreadPool`).

## Integrating fog with the minimap

Hide enemies on the minimap if their cell is UNSEEN:

```gdscript
func _draw_entity(world_pos: Vector2, color: Color, radius: float) -> void:
    if FogOfWar.get_cell_state(world_pos) == FogOfWar.CellState.UNSEEN:
        return   # don't show on minimap if never explored
    # ... draw icon
```

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| Calling `queue_redraw()` every `_process` frame | Redraws fog every frame even when nothing changed | Call only when player moves to a new cell |
| Storing `Vector2` objects in the fog grid | Memory-heavy; slow to iterate | `PackedByteArray` — one byte per cell |
| Fog layer drawn over entire scene in one ColorRect | Can't do partial reveal or LOS | Per-cell state grid + `_draw()` |
| Minimap in a separate scene not sharing World2D | Enemies don't appear on minimap | Share `World2D` between main and minimap viewports |
| Clearing fog on scene reload | Player loses all exploration progress | Serialize fog grid to save data |
| O(n²) LOS raycasts every frame | Stalls on large maps | Only raycast during `update_vision`, cache results, or use shadow-casting |

## Unity equivalents

| Godot | Unity |
|---|---|
| `SubViewport` + `get_texture()` | `RenderTexture` + `Camera.targetTexture` |
| `CanvasItem._draw()` + `draw_rect` | `OnGUI` or `Graphics.DrawMesh` with custom texture |
| `PackedByteArray` fog grid | `byte[]` + `Texture2D.SetPixels32` |
| `WorldEnvironment` fog | Built-in Unity fog settings |
| Shared `World2D` across viewports | Shared Unity Scene — two cameras, different layers |
