# Lighting and Global Illumination (Godot 4)

Godot 4 offers three GI systems: LightmapGI (baked, fastest at runtime), VoxelGI (baked probe grid, dynamic objects), and SDFGI (fully real-time, largest scene support). Choosing the wrong one is the most common lighting setup mistake — each has a specific use case that the others cannot cover.

## Contents
- Choosing the right GI system
- LightmapGI: setup, UV unwrapping, baking
- LightmapGIProbe for dynamic objects
- VoxelGI: when to use it
- SDFGI: open-world use case
- DirectionalLight3D and shadow settings
- OmniLight3D and SpotLight3D
- WorldEnvironment: sky, fog, tone mapping
- Common baking mistakes
- Performance comparison

## Choosing the right GI system

| System | Static objects | Dynamic objects | Scene size | Runtime cost |
|---|---|---|---|---|
| LightmapGI | ✓ perfect | ✗ (probes only) | Any | Zero (texture lookup) |
| VoxelGI | ✓ good | ✓ good | Medium (< 200m) | Low–medium |
| SDFGI | ✓ good | ✓ partial | Large (open world) | Medium–high |

**Decision rule:**
- Indoor scenes, corridors, rooms, tight maps → **LightmapGI**
- Medium outdoor scene with many dynamic objects (characters, vehicles) → **VoxelGI**
- Open world or large outdoor scene where baking is impractical → **SDFGI**
- No GI needed (stylized / flat-lit art style) → **DirectionalLight + ambient color only**

Never enable both LightmapGI and VoxelGI on the same geometry — they produce additive double-lighting.

## LightmapGI: setup and baking

**Step 1: UV2 unwrap all static meshes.**

Every mesh that receives baked lighting needs a non-overlapping UV2 channel. In Godot:
- Select a MeshInstance3D → Import tab → check "Generate Lightmap UV2"
- Or: open the mesh in the editor → Mesh menu → "Unwrap UV2 for Lightmap/AO"

Overlapping UV2s produce light bleeding — dark or bright patches that belong to another surface.

**Step 2: Mark static geometry as Static.**

Set `GeometryInstance3D.gi_mode = GI_MODE_STATIC` on all static geometry. Dynamic objects should use `GI_MODE_DYNAMIC` (they won't be baked but will receive probe lighting).

**Step 3: Add a LightmapGI node to the scene.**

```gdscript
# LightmapGI node — in the Inspector:
# Quality: Low (dev iteration), High (final build)
# Bounces: 2 (indoor) or 3 (outdoor)
# Use Denoiser: true (requires OIDN; improves result significantly)
# Texel Scale: 1.0 (increase for more detail, larger texture)
```

**Step 4: Add LightmapGIProbe nodes for dynamic object areas.**

LightmapGIProbe nodes bake spherical harmonics at their location. Dynamic objects (CharacterBody3D, enemies) receive indirect lighting by sampling the nearest probes.

Place probes:
- At head height in every room
- Along corridors every 4–6 meters
- Near light transitions (doorways, windows)

```gdscript
# Place LightmapGIProbe nodes manually; they appear as small spheres in editor
# Density: 1.0 (default) — increases number of probes within the bounds box
```

**Step 5: Bake.**

Scene menu → "Bake LightMaps". Store the `.lmbake` file in your project (it's binary, check into version control). Export builds use the baked file directly — baking is an editor operation only.

## Common baking mistakes

**Missing UV2**: mesh receives no lighting or has ugly splotches. Fix: enable "Generate Lightmap UV2" on import.

**Dynamic lights included in bake**: point lights and spot lights are baked into the lightmap by default. Set `OmniLight3D.light_bake_mode = LIGHT_BAKE_DISABLED` for dynamic lights that will move or change at runtime (e.g. a flickering fire). Only bake lights that will never change.

**Texel scale too low**: lightmap texture is blurry. Increase `LightmapGI.texel_scale` from 1.0 to 2.0. Doubles texture size.

**Denoiser not enabled**: baked result is noisy. Enable `use_denoiser = true`. Requires Intel OIDN — install via the Godot editor's denoiser setting.

**No LightmapGIProbe nodes**: dynamic objects (player, enemies) appear unlit or use ambient-only lighting. Always place probes throughout the playable space.

## VoxelGI: when to use it

VoxelGI bakes a voxel grid of radiance data. It updates in real time for dynamic objects inside the grid and is re-bakeable in-editor with a button click.

```gdscript
# VoxelGI node
# Size: set to cover the playable area
# Subdiv: 64 (default) — increase for more detail (128/256)
# Bake: Scene menu → Bake VoxelGI
```

VoxelGI shines for medium-size interior spaces with NPCs that need indirect lighting. It cannot cover large open worlds — the voxel grid would need to be enormous.

## SDFGI: open-world use case

SDFGI (Signed Distance Field GI) runs in real time using the GPU's compute pipeline. No baking required. Enable via `WorldEnvironment → Environment → SDFGI`.

```gdscript
# WorldEnvironment node → Environment resource
# SDFGI → Enabled: true
# Energy: 1.0 (boost for brighter indirect light)
# Min Cell Size: 0.2 (smaller = more detail, higher GPU cost)
# Cascade Count: 8 (covers more distance)
```

SDFGI is the right choice for open worlds where baking is impractical. GPU cost is significant — target high-end or mid-range desktop; it's not viable on mobile or low-spec hardware without reducing cascade count and min cell size.

## DirectionalLight3D and shadows

```gdscript
# DirectionalLight3D — the sun
var sun := DirectionalLight3D.new()
sun.shadow_enabled = true
sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS  # good default
sun.directional_shadow_split_1 = 0.1  # first cascade: close detail
sun.directional_shadow_split_2 = 0.2
sun.directional_shadow_split_3 = 0.5
sun.directional_shadow_max_distance = 200.0  # meters

# Shadow bias — prevents shadow acne (self-shadowing artifacts)
sun.shadow_bias = 0.05  # increase if acne; decrease if peter-panning
```

`SHADOW_PARALLEL_4_SPLITS` (PSSM4) gives four cascades: close shadows are sharp, far shadows are lower resolution. This is the correct mode for outdoor/open scenes. `SHADOW_PARALLEL_2_SPLITS` for performance-constrained platforms.

## WorldEnvironment: sky and tone mapping

```gdscript
# WorldEnvironment node → Environment resource
# Sky: PhysicalSkyMaterial or ProceduralSkyMaterial
# Tone Mapping: Filmic (most natural), ACES (high contrast), Linear (flat/debug)
# Ambient Light: match to sky (use Sky mode, not Color)
# Fog: Enabled for atmosphere, density 0.005–0.02 for outdoor scenes
```

Tone mapping is not optional — without it, HDR lighting produces blown-out whites. Filmic is the standard for realistic 3D. Set ambient light to "Sky" mode so it matches the sky color automatically.

## Performance comparison

| GI | Memory | CPU | GPU | Re-bake time |
|---|---|---|---|---|
| None | 0 | 0 | 0 | — |
| LightmapGI | Medium (texture) | 0 | 0 | Minutes |
| VoxelGI | Medium (voxel grid) | Low | Low | Seconds |
| SDFGI | Low | 0 | Medium–High | None (real-time) |

For mobile or Switch-level hardware: use LightmapGI only. VoxelGI and SDFGI are desktop-only in practice.
