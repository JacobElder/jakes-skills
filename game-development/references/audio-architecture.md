# Audio Architecture

Audio is the cheapest high-ROI system in a game. A sound on every action costs almost nothing to add and makes the game feel three times more real. But default audio architecture — every sound directly on the Master bus, new nodes allocated per-play, one looping music track — produces a system that's brittle to tune, wastes performance, and can't support the adaptive music that matches the player's situation. This file covers the four pillars: bus hierarchy, adaptive/dynamic music, spatial audio, and audio pooling.

## Contents
- Audio bus hierarchy
- Adaptive music (stem-based)
- 3D spatial audio
- Audio pooling
- Sound design patterns
- Unity equivalents
- Anti-patterns summary

## Audio bus hierarchy

Every game needs a bus tree. Without one, you can't let players independently control music and SFX volume (a basic expectation), can't apply effects selectively (reverb on cave sounds, not on music), and can't mute one category without cutting everything.

**The standard tree:**
```
Master
├── Music
└── SFX
    ├── UI          (optional — footsteps and menu clicks don't need reverb)
    ├── Ambient     (optional — wind, insects; may get low-pass or reverb)
    └── Footsteps   (optional — randomize pitch here via bus or per-player)
```

**Setting this up in Godot 4:** Audio → Audio Bus Layout panel. Add buses, set their "Send" to the parent bus. Name them exactly what you'll reference in code — the name is the string key.

Wire any `AudioStreamPlayer`, `AudioStreamPlayer2D`, or `AudioStreamPlayer3D` to a bus via the `bus` property (Inspector dropdown, or in code: `player.bus = "SFX"`). The node emits into that bus; the bus tree routes to Master.

**Volume control — do it on the bus, not on the players:**

```gdscript
# settings_menu.gd

func _on_music_slider_changed(linear_value: float) -> void:
    # Slider range should be 0.0..1.0 (linear)
    # AudioServer works in decibels — convert, but clamp to avoid log(0)
    var db := linear_to_db(max(linear_value, 0.0001))
    AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), db)

func _on_sfx_slider_changed(linear_value: float) -> void:
    var db := linear_to_db(max(linear_value, 0.0001))
    AudioServer.set_bus_volume_db(AudioServer.get_bus_index("SFX"), db)

func _on_mute_music_toggled(pressed: bool) -> void:
    AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"), pressed)
```

**Anti-pattern: setting `volume_db` directly on AudioStreamPlayer nodes.** It works but is the wrong level — you'd have to track and adjust every active player when the slider changes, and players spawned after the slider moved inherit the wrong volume. Set it once on the bus; all players routed to that bus inherit it automatically.

**Persisting settings (Godot):**

```gdscript
const SETTINGS_PATH := "user://settings.cfg"

func save_audio_settings() -> void:
    var cfg := ConfigFile.new()
    cfg.set_value("audio", "music_volume",
        db_to_linear(AudioServer.get_bus_volume_db(AudioServer.get_bus_index("Music"))))
    cfg.set_value("audio", "sfx_volume",
        db_to_linear(AudioServer.get_bus_volume_db(AudioServer.get_bus_index("SFX"))))
    cfg.set_value("audio", "music_muted",
        AudioServer.is_bus_mute(AudioServer.get_bus_index("Music")))
    cfg.save(SETTINGS_PATH)

func load_audio_settings() -> void:
    var cfg := ConfigFile.new()
    if cfg.load(SETTINGS_PATH) != OK:
        return
    _on_music_slider_changed(cfg.get_value("audio", "music_volume", 1.0))
    _on_sfx_slider_changed(cfg.get_value("audio", "sfx_volume", 1.0))
    AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"),
        cfg.get_value("audio", "music_muted", false))
```

**Bus effects.** Each bus has an Effects chain in the Audio Bus Layout. Add a `AudioEffectReverb` to an "Ambient" sub-bus for cave echoes; add a `AudioEffectLowPassFilter` to a "Muffled" sub-bus for underwater sections. Route the appropriate players to those buses — never apply environmental effects globally on Master.

## Adaptive music (stem-based)

A single looping track can't follow the game. Combat escalates tension; exploration breathes; boss fights need their own energy. The pattern that handles this without audible gaps or sync loss: **multiple synchronized stem players, volume-controlled by a state machine**.

**Architecture:** one `AudioStreamPlayer` per stem, all routed to the Music bus. Each plays the same-length, loop-point-matched audio file continuously. At any moment you want a stem heard, tween its volume up; to silence it, tween down. The simulation never stops or starts players — they run in lockstep from game start.

```
Stems:
  exploration_base.ogg   — always audible at game start
  exploration_melody.ogg — light; plays in safe areas
  combat_drums.ogg       — heavy percussion; fades in on combat
  combat_strings.ogg     — intense strings; fades in on high-threat
```

**Why not stop one track and start another?** Stopping causes an audible silence gap while the new track buffers, and restarting loses sync — the stems drift apart over time. Tween-based crossfades are instant and preserve sync.

**Sync on late entry.** When bringing a new stem in after others have been playing, match position before calling play:

```gdscript
# adaptive_music.gd
extends Node

enum MusicState { EXPLORATION, COMBAT, BOSS_FIGHT, DEAD }

@onready var stems: Dictionary = {
    "exploration_base":    $ExplorationBase,
    "exploration_melody":  $ExplorationMelody,
    "combat_drums":        $CombatDrums,
    "combat_strings":      $CombatStrings,
}

# Which stems are active (full volume) in each state
const STATE_STEMS: Dictionary = {
    MusicState.EXPLORATION: ["exploration_base", "exploration_melody"],
    MusicState.COMBAT:      ["exploration_base", "combat_drums"],
    MusicState.BOSS_FIGHT:  ["exploration_base", "combat_drums", "combat_strings"],
    MusicState.DEAD:        [],
}

const FADE_DURATION := 1.5  # seconds
var current_state: MusicState = MusicState.EXPLORATION

func _ready() -> void:
    # Start all stems silenced, then bring up the initial state
    for stem in stems.values():
        stem.volume_db = -80.0
    _start_all_stems()
    set_state(MusicState.EXPLORATION)

func _start_all_stems() -> void:
    # First stem plays normally; all others sync to it before playing
    var reference_player: AudioStreamPlayer = stems["exploration_base"]
    reference_player.play()
    for key in stems:
        if key == "exploration_base":
            continue
        var player: AudioStreamPlayer = stems[key]
        player.play(reference_player.get_playback_position())

func set_state(new_state: MusicState) -> void:
    if new_state == current_state:
        return
    current_state = new_state
    var active: Array = STATE_STEMS.get(new_state, [])
    _crossfade_stems(active)

func _crossfade_stems(active_stems: Array) -> void:
    for key in stems:
        var player: AudioStreamPlayer = stems[key]
        var target_db: float = 0.0 if key in active_stems else -80.0
        var tween := create_tween()
        tween.tween_property(player, "volume_db", target_db, FADE_DURATION)\
             .set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
```

**Loop points must match.** If exploration_base loops at 32 bars and combat_drums loops at 16, they drift out of sync after one pass. All stems must share the same loop length and loop start/end positions, authored in the DAW and verified before export.

**State machine integration.** Wire `set_state()` to whatever drives game state — an enemy encounter trigger, the enemy-count threshold in your horde manager, a boss spawn signal:

```gdscript
# In your combat manager or enemy spawner:
func _on_combat_started() -> void:
    AdaptiveMusic.set_state(AdaptiveMusic.MusicState.COMBAT)

func _on_all_enemies_killed() -> void:
    AdaptiveMusic.set_state(AdaptiveMusic.MusicState.EXPLORATION)
```

Keep `AdaptiveMusic` as an **autoload singleton** — every system can reach it, but it doesn't reach back into anyone.

## 3D spatial audio

Use the right player node for the context:

| Node | Use for |
|---|---|
| `AudioStreamPlayer` | Non-positional: music, UI sounds, global narrator |
| `AudioStreamPlayer2D` | 2D world sounds: footsteps, projectiles, ambient emitters |
| `AudioStreamPlayer3D` | 3D world sounds: everything in a 3D scene |

**Anti-pattern:** using `AudioStreamPlayer` (non-positional) for in-world sounds in a 3D game. The player hears gunfire and explosions at equal volume from any distance and no spatial cue. Use `AudioStreamPlayer3D`.

**Key parameters on AudioStreamPlayer3D:**

- `unit_size`: the reference distance at which volume is at 100%. Defaults to 10 m. Set relative to your scene scale — if your character is 2 units tall, 10 m may be fine; if units are centimeters, adjust accordingly.
- `max_distance`: beyond this, the sound is inaudible. Cull aggressively — a distant footstep shouldn't consume CPU.
- `attenuation_model`: `INVERSE` (physically correct, volume ∝ 1/distance²) for realistic acoustics; `LINEAR_DISTANCE` (volume ∝ 1-d/max_d) for more predictable game-feel; `CUSTOM` with an `AudioStreamPlayer3D.attenuation_filter_cutoff_hz` curve for authored control.
- `doppler_tracking`: enable for fast-moving emitters (racing games, projectiles). Set to `FIXED` so the listener compensates rather than the source.
- `panning_strength`: 1.0 by default; reduce slightly in tight spaces where extreme L/R panning reads as unnatural.

**Occlusion.** Godot 4 does not have built-in audio occlusion (walls blocking sound) out of the box. The practical workaround: cast a ray from listener to emitter each frame; if the ray hits geometry, reduce volume or apply a low-pass filter via `AudioServer` bus effects. For a proper solution, a 3D audio middleware plugin (or the `NavigationAudioListener3D` for reverb zone hints) fills the gap.

**The AudioListener3D.** Only one listener is active at a time. In a single-player 3D game, place a `AudioListener3D` node on the camera or the player head bone and make it current. Without it, the engine listens from the scene origin and spatial audio is wrong.

## Audio pooling

Pooling matters the moment you have rapid-fire sounds: gunshots, footsteps, enemy hits, UI clicks. Allocating a new `AudioStreamPlayer` node on every sound invocation does node creation and potential GC pressure every frame — visible as hitches in profiler captures.

**The pattern:** pre-allocate N players at scene start, mark them available/in-use, acquire one per sound request, return it automatically when the stream ends.

```gdscript
# audio_pool.gd — autoload as "AudioPool"
extends Node

const POOL_SIZE := 16
const POOL_BUS := "SFX"

var _pool: Array[AudioStreamPlayer] = []

func _ready() -> void:
    for i in range(POOL_SIZE):
        var player := AudioStreamPlayer.new()
        player.bus = POOL_BUS
        add_child(player)
        player.finished.connect(_on_player_finished.bind(player))
        _pool.append(player)

func play(stream: AudioStream, volume_db: float = 0.0, pitch_scale: float = 1.0) -> AudioStreamPlayer:
    var player := _acquire()
    if player == null:
        return null  # pool exhausted — drop the sound (acceptable for rapid-fire SFX)
    player.stream = stream
    player.volume_db = volume_db
    player.pitch_scale = pitch_scale
    player.play()
    return player

func _acquire() -> AudioStreamPlayer:
    for player in _pool:
        if not player.playing:
            return player
    return null  # all busy

func _on_player_finished(player: AudioStreamPlayer) -> void:
    # Nothing to do — the player.playing flag is already false,
    # so _acquire() will pick it up on the next request.
    pass
```

Usage from anywhere:

```gdscript
# In an enemy hit handler:
AudioPool.play(hit_sound, randf_range(-2.0, 0.0), randf_range(0.9, 1.1))
```

**Pool size.** 16 is a sensible default. For a bullet-hell or survivors-like with hundreds of simultaneous impacts, increase to 32–48. Profile: if `_acquire()` returns null regularly, the pool is undersized.

**Spatial variant.** For a 3D pool, the same pattern using `AudioStreamPlayer3D`; `play()` takes an additional `global_position: Vector3` argument and sets `player.global_position` before calling `player.play()`. Return the player to the pool via `stream_finished`.

**Anti-pattern:** `AudioStreamPlayer.new()` + `add_child()` inside an `_on_enemy_hit()` or bullet-impact handler called 30 times a frame. Every `add_child` allocates a node and registers it with the scene tree — that's GC territory in the hot loop. Pool it.

## Sound design patterns

**One-shot vs looping.** One-shots fire and forget (hits, jumps, pickups). Looping sounds (engines, wind, ambient hum) use `AudioStreamPlayer.stream_paused` or bus muting to stop — never call `stop()` on a looping player mid-loop unless it's intentional, as the next `play()` restarts from zero.

**Pitch and volume randomization.** Repeated identical sounds are the clearest sign of a programmer-made game. On every discrete play, randomize both:

```gdscript
# Call instead of player.play() for one-shot SFX
func play_varied(player: AudioStreamPlayer) -> void:
    player.pitch_scale = randf_range(0.9, 1.1)    # ±10% pitch
    player.volume_db   = randf_range(-2.0, 0.0)   # ±2 dB volume
    player.play()
```

Footsteps warrant wider pitch range (±15%); UI sounds warrant almost none (±2–3%). Don't randomize music.

**Layered impacts.** A hit that only has a high "smack" reads as thin. Layer: a low "body thud" (bass content, 80–200 Hz) + a high transient "crack" or "click" (2–8 kHz). Both play simultaneously on impact. This is why professional SFX packs ship impacts as layered stems.

**Environmental bus effects.** Author these at the bus level, not per-player:
- Cave/dungeon: reverb on the Ambient sub-bus, decay 1.5–3 s, wet mix 40–60%.
- Underwater: `AudioEffectLowPassFilter` cutoff at 400–800 Hz on a dedicated "Underwater" bus; route all world sounds to it when submerged, not just ambient.
- Radio/phone: bandpass (300–3000 Hz) + slight distortion + subtle reverb on a "Radio" bus for in-game comms.

Transition between environments by tweening which bus players route to, or by tweening the bus effect parameters.

**Music vs ambient layering.** Ambient sound (wind, birds, distant crowd) lives on its own sub-bus under SFX, not under Music. It should duck when the player pauses (mute SFX bus on pause) but not when the player adjusts music volume. Treat ambient as world SFX that happens to loop.

## Unity equivalents

Unity's audio architecture maps closely to Godot's but uses different names:

| Godot | Unity |
|---|---|
| Audio Bus Layout | AudioMixer (Asset in Project window) |
| Bus with volume_db | AudioMixerGroup with volume parameter |
| AudioServer.set_bus_volume_db() | AudioMixer.SetFloat("MusicVolume", db) |
| AudioStreamPlayer.bus | AudioSource.outputAudioMixerGroup |
| AudioServer.set_bus_mute() | AudioMixerGroup with mute via snapshot |

**AudioMixer snapshots** are Unity's mechanism for transitioning between named states (e.g., "Exploration," "Combat," "Underwater"). Each snapshot captures a full parameter set for the mixer; `AudioMixer.TransitionToSnapshots()` blends between them over a duration. This is the Unity equivalent of the stem-fade pattern — use snapshots for bus-effect state (reverb, EQ), stems for actual audio content.

**AudioSource.spatialBlend:** 0 = fully 2D (panned, no distance attenuation), 1 = fully 3D. Always set to 1 for in-world sounds in 3D games. The equivalent of `AudioStreamPlayer3D` in Godot.

**AudioMixer.SetFloat():** exposes a parameter for scripting. Create an "Exposed Parameter" in the mixer, name it (e.g., `"MusicVolume"`), and drive it from code:

```csharp
audioMixer.SetFloat("MusicVolume", Mathf.Log10(Mathf.Max(linearValue, 0.0001f)) * 20f);
```

The `* 20` converts from log10 to decibels — Unity's mixer works in dB but `Mathf.Log10` gives you the raw log.

**Unity audio pooling:** same concept — pre-instantiate a pool of `AudioSource` components on child GameObjects; acquire an inactive one, set its clip, call `Play()`, return it via `StartCoroutine` after `clip.length`. Or use a third-party library (AudioManager patterns are well-established in the Unity community).

## Anti-patterns summary

| Anti-pattern | Why it hurts | Fix |
|---|---|---|
| All sounds on the Master bus | No per-category volume control; can't apply effects selectively | Bus hierarchy: Music, SFX, sub-buses |
| `volume_db` on individual players for volume sliders | Must track every active player; new players inherit wrong volume | Drive volume at the bus level via `AudioServer.set_bus_volume_db()` |
| Stop + play for music transitions | Silence gap; sync loss between stems | Tween stem volumes; never stop playing stems |
| Stem without position sync on late entry | Stems drift out of phase, producing comb filtering | Set `playback_position` from a reference player before calling `play()` |
| `AudioStreamPlayer.new()` per gunshot/footstep | Node allocation in the hot loop; hitches | Pre-allocated audio pool |
| `AudioStreamPlayer` for in-world 3D sounds | No distance attenuation, no panning, no spatial cue | `AudioStreamPlayer3D` with appropriate `unit_size` and `max_distance` |
| Identical pitch/volume every play | Immediately reads as fake; "machine gun" effect | `randf_range` on `pitch_scale` and `volume_db` per play |
