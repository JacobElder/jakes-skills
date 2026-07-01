# Procedural Generation & Controlled Randomness

Procgen is what gives roguelikes, survivors-likes, and many sims their replayability — and it's where generated code is most likely to produce something that's *random* but not *fun*: clumpy loot, disconnected dungeons, unfair card draws, samey levels. The craft is in **controlling** randomness, not just calling it. This file covers seeding, generation techniques, the make-it-fair toolkit, and — importantly — when not to use procgen at all.

## Contents
- Seed everything
- Controlled randomness, not pure randomness
- Level/dungeon generation techniques
- Generate, then validate
- The control spectrum: procedural ↔ authored
- Spawn directors & difficulty
- Loot & reward tables
- When NOT to use procgen

## Seed everything

Thread a **single seeded RNG** through generation; never call the global/unseeded random in generation code. Store the seed. This buys you: reproducible runs (the same seed = the same world, essential for debugging "the level that softlocked"), **shareable/daily seeds** (a feature players love), and determinism that plays nicely with the fixed-timestep story in `game-loop-and-time.md`. Keep *generation* RNG separate from *gameplay* RNG so that, e.g., combat rolls don't shift the world layout.

## Controlled randomness, not pure randomness

Independent uniform random *feels* unfair and clumpy to humans — three misses in a row, two of the same reward back-to-back, an item that never drops. Shape the distribution:

- **Weighted tables** — pick from entries with weights, not uniform. The bread and butter of loot/enemy/event selection.
- **Bag / deck draw (without replacement)** — instead of independently rolling each time, fill a "bag" with the intended distribution and draw from it, refilling when empty. Guarantees the long-run mix and prevents droughts/streaks. (This is how Tetris piece order works; it's also ideal for card rewards.)
- **Pity timers / bad-luck protection** — increase a rare drop's odds each time it *doesn't* drop, resetting on success. Players forgive randomness that can't screw them indefinitely.
- **Constraints + reroll** — generate, check it meets rules (min spacing between hazards, no two elites adjacent), regenerate or nudge if not. Cheap and very effective.
- **Distance/lerp shaping** — bias values toward a curve (e.g., enemy strength scales with depth ± a little noise) rather than full-range random.

For a deckbuilder specifically: use bag-draw for card rewards and weighted+pity for rare cards, so the player's run feels varied but never starved of options.

## Level/dungeon generation techniques

Choose by the *feel* you want; don't reach for the fanciest one:

- **Random room placement + corridors** — scatter non-overlapping rooms, connect them. Simple, controllable, the classic roguelike look.
- **BSP (binary space partitioning)** — recursively split the space, put a room in each leaf, connect siblings. Clean, non-overlapping, structured.
- **Cellular automata** — start noisy, smooth over a few passes. Great for *organic caves*.
- **Drunkard's walk / random walk** — carve by wandering a digger. Winding, connected caves; dead simple.
- **Grammar / template (set-piece) based** — stitch hand-authored chunks/rooms with rules. The best **control-vs-variety** tradeoff for designed-feeling content (Spelunky's room templates, Dead Cells' biomes).
- **Wave Function Collapse** — constraint-solve a tilemap from an example so everything fits. Coherent tile output, but finicky to author and debug — reach for it when tile *coherence* is the whole point, not as a default.

## Generate, then validate

The step beginners skip and the one that prevents broken runs: after generating, **verify the result is playable**. Flood-fill from the start to confirm the exit (and all key rooms/keys) are reachable; check the player can't spawn trapped; ensure required encounters fit. If validation fails, regenerate or patch (carve a connecting corridor). Always-valid-by-construction (template stitching) or generate-and-check both work; silent generation that occasionally softlocks does not.

## The control spectrum: procedural ↔ authored

There's a spectrum from **fully procedural** (cheap, infinite, but can feel soulless/samey) to **fully authored** (curated and intentional, but expensive and finite). The sweet spot for most small games is the **hybrid**: procedurally *arrange* hand-made pieces — authored rooms/encounters/set-pieces placed in a generated layout. You get authored quality *and* run-to-run variety (Spelunky, Dead Cells, Hades). State this as the default recommendation: hand-craft the *pieces*, proceduralize the *arrangement*.

## Spawn directors & difficulty

For wave/horde games, don't hand-place every enemy — drive spawning with a **director**:

- **Budget-based waves** — each wave gets a points budget; spend it on a weighted pool of enemy types (a basic enemy costs 1, an elite costs 10). Scale the budget over time for a difficulty curve.
- **Pacing director (Left-4-Dead style)** — track player tension/intensity and modulate spawns: ramp up, then deliberately ease off so there are peaks and valleys rather than constant pressure. Even a crude version (quiet beat after a big wave) improves feel a lot.
- **Spawn placement** — spawn off-screen / out of sight and feed enemies in via the flow field (`enemy-ai.md`); avoid popping enemies into the player's face.

## Loot & reward tables

Weighted, usually **tiered** (common/rare/epic with per-tier odds), and worth layering pity/bad-luck protection on the rare tiers. Make tables **data**, not code (`architecture.md`), so balancing is fast. Bias rewards toward what the player's build needs only if you want a "smart" feel — pure-random rewards are fine and sometimes fairer-feeling than a system that thinks it knows best.

## When NOT to use procgen

Procgen trades *authored intentionality* for *variety and content-scale*. If the fun of your game is in **crafted** experiences — a tightly designed puzzle, a hand-tuned platformer gauntlet, a story beat — procgen dilutes the very thing that makes it good. Don't proceduralize reflexively because the genre "usually" does. Ask: does randomness add replay value here, or just remove the designer's hand from where it's most needed? Often the right answer for a small game is **a lot of authored content with a little procedural variation**, not the reverse.
