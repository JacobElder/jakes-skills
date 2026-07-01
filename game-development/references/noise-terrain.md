# Noise-Based Terrain and Procedural World Generation

Procedural terrain is not about randomness — it is about controlled, tunable randomness. The tools are noise functions, biome logic, and mesh generation. The failure mode is generating lumpy featureless terrain with no variation and no visual identity.

## Contents
- FastNoiseLite in Godot 4
- Height map terrain mesh generation
- Computing normals from height data
- Biome systems: elevation + moisture maps
- Biome blending and texture splatting
- Domain warping for organic shapes
- Chunk-based terrain generation with seeds
- Runtime mesh generation on threads
- Wave Function Collapse (WFC)
- WFC vs BSP dungeon generation
- Performance

## FastNoiseLite in Godot 4

`FastNoiseLite` is Godot 4's built-in noise class. It wraps the FastNoiseLite C++ library and supports Perlin, Simplex, Cellular (Worley), Value, and several fractal modes.

```gdscript
var noise := FastNoiseLite.new()
noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH  # smoothest for terrain
noise.seed = 42
noise.frequency = 0.003       # lower = larger features
noise.fractal_type = FastNoiseLite.FRACTAL_FBM
noise.fractal_octaves = 6     # more octaves = more detail layers
noise.fractal_lacunarity = 2.0  # frequency multiplier per octave
noise.fractal_gain = 0.5        # amplitude multiplier per octave

# Returns float in [-1, 1]
var height: float = noise.get_noise_2d(world_x, world_z)
```

`get_noise_2d(x, z)` is the primary call for terrain. Map to a world height range:

```gdscript
const MIN_HEIGHT := -20.0
const MAX_HEIGHT := 80.0

func sample_height(world_x: float, world_z: float) -> float:
    var n := noise.get_noise_2d(world_x, world_z)  # [-1, 1]
    return remap(n, -1.0, 1.0, MIN_HEIGHT, MAX_HEIGHT)
```

Multiple noise layers with different frequencies produce convincing terrain: one low-frequency noise for continental shape, one mid-frequency for hills, one high-frequency for surface roughness. Sum them with decreasing amplitude. This is what `fractal_octaves` automates.

## Height map terrain mesh generation

Use `SurfaceTool` to build a quad-grid mesh from height samples. For a `resolution × resolution` grid covering `size × size` world units:

```gdscript
func generate_mesh(resolution: int, size: float) -> Mesh:
    var st := SurfaceTool.new()
    st.begin(Mesh.PRIMITIVE_TRIANGLES)

    var step := size / float(resolution - 1)

    for z in resolution:
        for x in resolution:
            var wx := x * step
            var wz := z * step
            var wy := sample_height(wx + chunk_origin.x, wz + chunk_origin.z)

            st.set_uv(Vector2(float(x) / resolution, float(z) / resolution))
            st.set_normal(_compute_normal(wx, wz, step))
            st.add_vertex(Vector3(wx, wy, wz))

    # Triangulate: two triangles per quad
    for z in resolution - 1:
        for x in resolution - 1:
            var i := z * resolution + x
            st.add_index(i)
            st.add_index(i + resolution)
            st.add_index(i + 1)
            st.add_index(i + 1)
            st.add_index(i + resolution)
            st.add_index(i + resolution + 1)

    return st.commit()
```

Resolution of 64-128 vertices per side is sufficient for most chunk sizes. Higher resolution consumes more memory and vertex processing time with diminishing visual returns.

## Computing normals from height data

The normal at each vertex is perpendicular to the local terrain slope. Compute it using the central difference of neighboring height samples:

```gdscript
func _compute_normal(wx: float, wz: float, step: float) -> Vector3:
    var height_l := sample_height(wx - step, wz)
    var height_r := sample_height(wx + step, wz)
    var height_d := sample_height(wx, wz - step)
    var height_u := sample_height(wx, wz + step)

    # Cross product of the two tangent vectors
    var tangent_x := Vector3(2.0 * step, height_r - height_l, 0.0)
    var tangent_z := Vector3(0.0, height_u - height_d, 2.0 * step)
    return tangent_z.cross(tangent_x).normalized()
```

Calling `st.generate_normals()` after building the mesh is an alternative, but computing normals per-vertex before adding them to SurfaceTool avoids a second pass over all geometry.

## Biome systems: elevation + moisture maps

A single noise map produces uniform terrain with no identity. Biomes come from combining two or more independent noise maps.

**Elevation map** — same as the height map, or a separate large-scale noise pass for continental shape.

**Moisture map** — a second `FastNoiseLite` instance with a different seed and lower frequency. High moisture = jungle/swamp/tundra; low moisture = desert/savanna.

Biome lookup as a 2D table:

```gdscript
enum Biome { OCEAN, BEACH, DESERT, SAVANNA, FOREST, RAINFOREST, SNOW, TUNDRA, MOUNTAIN }

func get_biome(elevation: float, moisture: float) -> Biome:
    if elevation < 0.1: return Biome.OCEAN
    if elevation < 0.15: return Biome.BEACH
    if elevation > 0.75:
        return Biome.SNOW if moisture > 0.4 else Biome.MOUNTAIN
    if moisture < 0.2: return Biome.DESERT
    if moisture < 0.45: return Biome.SAVANNA
    if moisture < 0.7: return Biome.FOREST
    return Biome.RAINFOREST
```

Both maps use normalized [0, 1] values:

```gdscript
func sample_elevation(x: float, z: float) -> float:
    return remap(elevation_noise.get_noise_2d(x, z), -1.0, 1.0, 0.0, 1.0)

func sample_moisture(x: float, z: float) -> float:
    return remap(moisture_noise.get_noise_2d(x, z), -1.0, 1.0, 0.0, 1.0)
```

## Biome blending and texture splatting

Hard biome cutoffs produce ugly seams. Blend adjacent biomes by sampling their weights at multiple nearby points and weighting by distance.

**Texture splatting** — the standard technique for multi-biome terrain textures. A shader samples 3-4 terrain textures (grass, rock, sand, snow) and blends them by weights stored as vertex colors:

```glsl
// terrain.gdshader
shader_type spatial;

uniform sampler2D tex_grass : source_color;
uniform sampler2D tex_rock  : source_color;
uniform sampler2D tex_sand  : source_color;
uniform sampler2D tex_snow  : source_color;
uniform vec2 uv_scale = vec2(20.0);

void fragment() {
    vec2 uv = UV * uv_scale;
    vec4 grass = texture(tex_grass, uv);
    vec4 rock  = texture(tex_rock, uv);
    vec4 sand  = texture(tex_sand, uv);
    vec4 snow  = texture(tex_snow, uv);

    // Vertex colors carry biome blend weights (r=grass, g=rock, b=sand, a=snow)
    ALBEDO = (grass * COLOR.r + rock * COLOR.g + sand * COLOR.b + snow * COLOR.a).rgb;
    ROUGHNESS = 0.9;
}
```

Set vertex colors from GDScript during mesh generation based on biome weights at each vertex. `st.set_color(Color(grass_w, rock_w, sand_w, snow_w))` before `st.add_vertex()`.

## Domain warping for organic shapes

Sampling noise at plain `(x, z)` produces smooth but geometrically regular terrain. Domain warping samples at offset coordinates, producing organic coastlines, cave shapes, and river-like features:

```gdscript
# Warp the sample coordinate before reading height
func sample_warped_height(x: float, z: float) -> float:
    var warp_x := warp_noise.get_noise_2d(x, z) * warp_strength
    var warp_z := warp_noise.get_noise_2d(x + 100.0, z + 100.0) * warp_strength
    return sample_height(x + warp_x, z + warp_z)
```

`warp_strength` of 30-80 world units produces visibly non-circular terrain shapes. Two passes of warping (warp → warp again → sample) produces dramatically organic results at the cost of two extra noise lookups per vertex.

## Chunk-based terrain generation with seeds

A deterministic world requires deterministic chunk generation. Each chunk's noise seed is derived from the world seed and chunk coordinates:

```gdscript
func get_chunk_seed(world_seed: int, chunk_coord: Vector2i) -> int:
    # Hash chunk coordinates with world seed
    return world_seed ^ (chunk_coord.x * 1_000_003) ^ (chunk_coord.y * 999_983)
```

For `FastNoiseLite`, set `noise.seed = get_chunk_seed(world_seed, coord)` before sampling. This ensures the same world regenerates identically after a reload. Never use `randi()` or `randf()` directly for world generation — always seed deterministically from the world seed + position.

## Runtime mesh generation on threads

Generating a 128×128 resolution mesh takes 5-20ms on the main thread — enough to cause a visible hitch. Move generation to a `Thread`:

```gdscript
var _thread := Thread.new()

func generate_chunk_async(coord: Vector2i) -> void:
    _thread.start(_thread_generate.bind(coord))

func _thread_generate(coord: Vector2i) -> void:
    var mesh := _build_terrain_mesh(coord)
    # Assign mesh on main thread via call_deferred
    call_deferred("_apply_mesh", coord, mesh)

func _apply_mesh(coord: Vector2i, mesh: Mesh) -> void:
    if _thread.is_started():
        _thread.wait_to_finish()
    _chunk_mesh_instances[coord].mesh = mesh
```

`call_deferred` is required because Godot's scene tree and rendering calls are not thread-safe — only generate the mesh data on the thread, then apply it on the main thread.

## Wave Function Collapse (WFC)

WFC generates tile-based layouts (dungeons, city blocks, island maps) from adjacency rules rather than procedural shape algorithms.

**Core concept:** Each cell starts with a set of all possible tile types. The algorithm repeatedly:
1. Finds the cell with the fewest remaining options (lowest entropy).
2. Randomly collapses it to one option (weighted by tile frequency).
3. Propagates constraints to neighbors, removing options that violate adjacency rules.
4. Repeats until all cells are collapsed or a contradiction is reached.

**Adjacency rules** define what tiles can be next to each other in each direction. A `FLOOR` tile can be adjacent to `FLOOR`, `WALL`, or `DOOR`. A `WATER` tile cannot be adjacent to `FLOOR` directly (must have `SHORE` between them). The rules are the entire design of the algorithm's output.

```gdscript
class_name WFCGrid

var _options: Array  # Array[Array[StringName]] — options per cell
var _rules: Dictionary  # tile_name → {dir: Array[StringName]}
var _width: int
var _height: int

func initialize(width: int, height: int, all_tiles: Array[StringName]) -> void:
    _width = width
    _height = height
    _options.resize(width * height)
    for i in _options.size():
        _options[i] = all_tiles.duplicate()

func collapse_all() -> bool:
    while true:
        var idx := _lowest_entropy_cell()
        if idx == -1:
            return true  # all cells collapsed — done
        if _options[idx].is_empty():
            return false  # contradiction — retry or backtrack
        # Collapse to one random option
        var chosen: StringName = _options[idx].pick_random()
        _options[idx] = [chosen]
        # Propagate
        _propagate(idx)
    return false

func _lowest_entropy_cell() -> int:
    var min_count := INF
    var best := -1
    for i in _options.size():
        var count := _options[i].size()
        if count > 1 and count < min_count:
            min_count = count
            best = i
    return best  # -1 means all cells already collapsed

func _propagate(start_idx: int) -> void:
    var queue := [start_idx]
    while not queue.is_empty():
        var idx := queue.pop_front()
        var coord := Vector2i(idx % _width, idx / _width)
        for dir in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
            var n_coord := coord + dir
            if n_coord.x < 0 or n_coord.x >= _width or n_coord.y < 0 or n_coord.y >= _height:
                continue
            var n_idx := n_coord.y * _width + n_coord.x
            # Find all tiles that could be adjacent to any of our current options in this direction
            var allowed := {}
            for tile in _options[idx]:
                for neighbor_tile in _rules[tile][dir]:
                    allowed[neighbor_tile] = true
            # Remove options from neighbor that aren't in allowed
            var before_count := _options[n_idx].size()
            _options[n_idx] = _options[n_idx].filter(func(t): return allowed.has(t))
            # If options changed, propagate further from this neighbor
            if _options[n_idx].size() < before_count:
                queue.append(n_idx)
```

For contradiction handling, keep a stack of snapshots and backtrack on failure. For small grids (< 64×64), simply restart with a different random seed — WFC is fast enough that 2-3 restarts per generation is acceptable.

## WFC vs BSP dungeon generation

| | BSP | WFC |
|---|---|---|
| Output | Rectangular rooms, corridors | Tile-accurate layouts |
| Speed | O(log n) | O(n log n) — slower |
| Visual variety | Low (always rectangular) | High (organic shapes) |
| Control | Coarse (room count, size range) | Fine (per-tile adjacency rules) |
| Implementation | Simple recursion | Moderate complexity |

Use BSP when: fast, predictable room-based dungeons (Rogue-like, procedural Zelda dungeons).
Use WFC when: organic tile-accurate layouts (caves, islands, city blocks, puzzle rooms).

## Performance

- A 64×64 WFC grid resolves in < 2ms in GDScript. A 256×256 grid can take 50-200ms — run on a Thread.
- Terrain mesh generation for a 128×128 vertex chunk takes 5-20ms — run on a Thread, apply with `call_deferred`.
- Cache generated meshes: do not regenerate a chunk that already has a mesh unless the seed changes.
- Use LOD on terrain chunks (rough mesh at distance) — see `lod-and-streaming.md`.
- FastNoiseLite `get_noise_2d()` is cheap (~100ns per call). A 128×128 grid samples = 16,384 calls ≈ 1.6ms. Not the bottleneck; mesh construction and GDScript Array manipulation are.
