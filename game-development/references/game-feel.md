# Game Feel ("Juice")

Game feel is the moment-to-moment tactile sensation of play — the weight of a jump, the crunch of a hit, the way the screen reacts. It is *most* of why a polished game feels good and a functional one feels dead, and almost all of it is cheap to add. The canonical sources are Steve Swink's book *Game Feel*, the "Juice it or lose it" talk (Martin Jonasson & Petri Purho), and Jan Willem Nijman's "The Art of Screenshake" (Vlambeer). The core lesson of all three: **the same mechanics feel completely different depending on feedback**, and you should build feel into the first prototype, not bolt it on at the end.

## Contents
- The principle: every action gets multi-channel feedback
- The juice toolkit
- Easing & tweening (stop snapping)
- Screenshake
- Hitstop / hitlag
- Squash & stretch and anticipation
- Particles and secondary motion
- Audio
- Camera feel
- A worked example
- Restraint

## The principle

Pick any action the player takes or witnesses — jump, shoot, hit, collect, die, land — and give it feedback across **several channels at once**: visual, motion, audio, and time. One channel reads as "the code worked"; three or four read as "that felt good." A coin pickup isn't `score += 1`; it's `score += 1` **and** a pop sound **and** the coin scaling up then vanishing **and** a little sparkle **and** the counter punching up in size. Same logic, totally different game.

## The juice toolkit

These are the standard moves. Most are a few lines each. Reach for several per important action.

- **Tweening/easing** instead of instant changes (movement, scale, color, UI).
- **Screenshake** on impacts and big events.
- **Hitstop** (brief freeze) on hits to sell impact.
- **Squash & stretch** on jump, land, hit, spawn.
- **Anticipation** (a wind-up frame) before big actions.
- **Particles**: dust on landing, sparks on hit, debris on death.
- **Knockback & recoil**: the shooter kicks back, the hit thing flies.
- **Flash**: white/red flash on a sprite when damaged.
- **Color & contrast pops**, brief slow-motion on a kill, chromatic aberration on big hits (use sparingly).
- **Sound on every action** — the single highest feel-per-effort item.
- **Number/score punch**: counters scale up briefly when they change; floating damage numbers.
- **Trails** behind fast objects; afterimages on dashes.

## Easing & tweening (stop snapping)

Linear motion and instant state changes feel robotic. Real things accelerate and decelerate. Replace "set value now" with "ease value over ~0.1–0.3 s" using an easing curve:

- **ease-out** (fast then settling) for things arriving — UI sliding in, camera catching up. Feels responsive.
- **ease-in** for things leaving.
- **ease-out-back / elastic** (overshoot then settle) for pickups, pop-ins, button presses — that little overshoot reads as "bouncy" and alive.

Every engine has a tween system — use it rather than hand-rolling lerps: **Godot** `create_tween()` with `set_ease`/`set_trans`; **Unity** coroutines or a library like DOTween; code-first, a small tween helper or manual lerp toward a target each frame. Rule: if you're about to set position/scale/color/alpha instantly and it's something the player sees, tween it instead.

## Screenshake

A short positional (and sometimes rotational) jitter of the camera on impact. It's possibly the highest-impact single effect ("The Art of Screenshake"). Implementation that actually feels good:

- Drive it with a **trauma** value (0..1). Add trauma on events (small hit +0.2, explosion +0.8). Each frame, offset the camera by `max_offset * trauma²` (squaring makes small shakes subtle and big ones punchy) in a random or noise-driven direction, then **decay trauma** toward 0 over time.
- Use **noise** (or random per-frame) for the offset, and shake **rotation** a touch too, not just position.
- Keep it **short and snappy**; long shakes nauseate. Always offset a *camera*, never the world objects.
- Give the player a way to scale it down — screenshake is an accessibility consideration (motion sensitivity).

A ready-to-use trauma-based **Godot Camera2D** implementation (with the engine-agnostic algorithm in comments to port elsewhere) ships at `assets/godot_screenshake.gd` — prefer adapting it to re-deriving shake from scratch, since the common mistakes (linear decay, shaking world objects, no squaring) all read as cheap.

## Hitstop / hitlag

On a meaningful hit, freeze everything (or just the two combatants) for a few frames — roughly 2–8 frames / ~30–130 ms. The brain reads the pause as *force*. It's why melee in good action games feels heavy. Implement by briefly setting `time_scale = 0` (or skipping sim steps) for the affected entities, then restoring. Pair with screenshake and a flash and you get a satisfying "crunch" from three cheap effects stacked. Don't overuse it on rapid-fire actions or the game feels laggy.

**Hitstop is the single highest-ROI impact technique.** When a developer says "I added particles, sounds, and screenshake but hits still feel weak," the missing ingredient is almost always hitstop. Particles and screenshake tell you *something happened*; hitstop tells you *force was applied*. The brief freeze gives the player's visual cortex time to register the contact. Without it, even beautiful VFX read as decoration rather than physics. Add hitstop before anything else when diagnosing weak-feeling combat — it's 5 lines of code and the effect is disproportionate.

Scale hitstop with hit weight: light attacks 2–3 frames (~30–50 ms), heavy attacks 4–8 frames (~65–130 ms), boss-level impacts up to 12 frames. Above 130 ms it reads as lag rather than force.

## Squash & stretch and anticipation

Borrowed from animation. **Squash & stretch:** scale a sprite non-uniformly to imply force and elasticity — stretch vertically while rising in a jump, squash flat on landing, then spring back (an ease-out-back tween on scale). Even a static sprite gains life from this. **Anticipation:** a brief wind-up before a big action (a crouch before a jump, a pull-back before a punch, an enemy flashing/rearing before it lunges) — it telegraphs to the player *and* makes the action feel powerful. A few frames each; enormous feel return.

## Particles and secondary motion

Spawn small, short-lived particles on events: dust puffs on landing and on direction-changes, sparks/blood on hits, debris and a burst on death, a muzzle flash on firing, a trail on a dash. They make the world feel reactive and physical. Pool them (see `collision-and-physics.md` / architecture) so frequent emission doesn't hitch. Secondary motion — a bobbing idle, hair/cloth lag, a weapon that sways — keeps things from looking frozen between actions.

## Audio

The cheapest big win. A sound on **every** action — footstep, jump, land, shoot, hit, pickup, menu move, UI confirm. Two techniques that prevent "machine-gun sameness": **pitch-randomize** each playback slightly (e.g. ±10–15%) so repeated sounds don't feel robotic, and layer a low "body" with a high "click" for impacts. Music sets tone but SFX is where *feel* lives — wire SFX to the same events your visual juice listens to (this is exactly what the event/signal decoupling in `architecture.md` is for).

## Camera feel

The camera is a character. Don't hard-lock it to the player — have it **ease** toward a target each frame (lag of ~0.1–0.2 s reads as smooth, not sluggish). **Look-ahead:** offset the target in the direction of motion/aim so the player sees where they're going. **Dead zone:** a small region where the player can move without the camera reacting, so it isn't constantly micro-adjusting. Add **punch** (a quick zoom-in/out) on big events, and clamp the camera to level bounds so it never shows the void.

## A worked example: making a jump feel good

A jump that's just "set velocity.y = -jump_force" feels dead. Stack feel onto the same event:
1. **Anticipation:** 2–3 frame crouch (squash) before launch.
2. **Stretch** the sprite vertically as it rises; **squash** on landing, then ease-out-back the scale to normal.
3. **Dust particle** at the feet on takeoff and on landing.
4. **Sound** on jump and a distinct one on land (pitch-randomized).
5. **Asymmetric gravity** — fall faster than you rise — and **variable jump height** (release early = short hop). See the platformer-controller recipe in `collision-and-physics.md`.
6. **Tiny screenshake** on a hard landing; **camera look-ahead** in the air.
7. **Coyote time + jump buffer** so it responds forgivingly (feel *and* fairness).

Each item is a few lines. Together they're the difference between a tech demo and a game.

## Restraint

Juice is seasoning. Everything shaking, flashing, and freezing at once is noise — it buries the feedback that matters and exhausts the player. Reserve the big effects (heavy screenshake, hitstop, slow-mo) for big moments so they keep their punch; let small actions have small, crisp feedback. And honor accessibility: provide options to reduce screenshake and flashing for motion- and photosensitivity. The goal is clarity *and* satisfaction, not maximum spectacle.
