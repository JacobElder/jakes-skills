# Engine & Language Selection

The goal is to match the tool to the project *and* the person, then commit. Engine-hopping mid-project is one of the most reliable ways to never ship. Pick deliberately, then stop shopping.

## The decision procedure

Ask (or infer) four things: **dimensionality** (2D vs 3D), **scope/target** (toy/jam vs commercial, and which platforms), **the person's existing skills**, and **how much control vs. batteries-included** they want. Then:

1. **2D game, any scope, no strong reason otherwise → Godot 4.x.** This is the default and you should state it as one. Godot's 2D is a genuine first-class pipeline (real pixel coordinates, dedicated 2D renderer, not 3D-with-z=0), iteration is near-instant, it's MIT-licensed (free at any revenue, no royalties, terms can't be changed on you), and GDScript reads like Python. As of 2026 it's roughly tied with Unity for game-jam usage and Godot Steam releases are doubling year over year.

2. **Modest/stylized 3D, indie scope → Godot 4.x** still holds. Godot 4.6+ made Jolt the default physics engine and closed much of the 3D gap. Reach past it only for the exceptions below.

3. **Console release at launch, or VR/XR/visionOS, or you already have deep Unity muscle memory → Unity 6.x.** Unity has first-party console export, the strongest XR toolchain (XR Interaction Toolkit, AR Foundation, PolySpatial), the largest asset store, and the most job-market value. The 2023 runtime-fee fiasco was reversed in 2024; current terms are free under $200K revenue, then a per-seat Pro subscription, no per-install fee. Godot can reach consoles only via paid third-party porting (e.g. W4 Games), which is a real cost and friction for a launch plan.

4. **Photorealistic / AAA-scale 3D → Unreal 5.** Nanite, Lumen, MetaHuman, Sequencer. Overkill and friction for most small games, and the 5% royalty over $1M matters for thin-margin titles, but nothing else competes at the high fidelity end. Rarely the right call for a *small* game.

5. **You're Rust-native and the game is simulation-heavy (factory/colony sim, lots of entities, physics sandbox, roguelike) → Bevy.** Data-oriented ECS, compile-time-safe parallel systems, free (MIT/Apache), good WebGPU story. Caveat hard: Bevy is pre-1.0 (0.18 as of early 2026), ships breaking changes about every three months, and you assemble much of the stack from crates (Avian or Rapier for physics, leafwing-input-manager for input, bevy_ecs_tilemap for 2D). Only correct when you genuinely want Rust + ECS + open source at once. If the user "fights the borrow checker," steer them elsewhere.

6. **Learning project, or you want to understand the loop from the metal, or pure-code with no editor → LÖVE (Lua) or PyGame (Python).** No scene editor, you write the loop yourself, which is exactly the point when the goal is understanding. LÖVE is the better game-focused choice (clean immediate-mode API, easy distribution); PyGame is the right call specifically when the user is a Python person who wants to stay in Python and is building a toy/learning game rather than something for Steam.

7. **Casual web game meant to run in a browser → Phaser (JS/TS).** Mature 2D web framework, huge install base, trivial to embed. For a Rust web build, Bevy or Macroquad compiled to WASM also works.

8. **One-week jam prototype in Rust → Macroquad.** Minimal-friction, Raylib-inspired, compiles to web easily. Prototype here, port to Bevy later only if the idea earns it.

## Matching to the person, not just the project

- **Knows Python, new to games:** Godot (GDScript transfers almost directly) for anything they want to ship; PyGame only if staying in pure Python matters more than shipping.
- **Knows C# / .NET:** Unity, or Godot with C# (Godot supports C# as a first-class language).
- **Knows JS/TS:** Phaser for web, or Godot/Unity fresh.
- **Knows Rust and loves it:** Bevy or Macroquad. If they don't already love Rust, this is the wrong place to learn both Rust and gamedev at once.
- **Wants a job in games:** Unity or Unreal experience is more marketable today than Godot, though Godot is climbing. Say this honestly.
- **Wants to never pay anyone and never have terms changed on them:** Godot (MIT) removes that whole category of risk.

## Anti-patterns in engine choice

- **Don't recommend Unity reflexively** because it's the most-represented in training data. For a solo 2D game in 2026, Godot is usually the better answer.
- **Don't recommend building a custom engine** for a first game. Writing an engine and writing a game are different projects; pick one. (Custom engines are a legitimate *learning* goal — just be explicit that the deliverable is then the engine, not a shipped game.)
- **Don't recommend Unreal for a 2D or small game.** It's optimized for high-fidelity 3D; the overhead and complexity aren't worth it below that bar.
- **Don't push Bevy on someone who isn't already comfortable in Rust.** The combined learning curve of Rust + ECS + a pre-1.0 API will sink a first project.
- **Don't keep re-litigating the choice.** Once it's made on reasonable grounds, the most important property of an engine is that the user finishes a game in it. "The best engine is the one you ship with."

## Version anchors (as of mid-2026, will drift)

Deliberately **pattern-first, not version-pinned.** A skill is read long after it's written, so hardcoding versions into the advice would rot it: the durable facts (Godot's dedicated 2D pipeline, Unity's console/XR edge, Bevy's pre-1.0 quarterly breakage, the structural MIT-vs-proprietary split) don't drift, while point releases do. Teach the patterns; keep versions as a dated anchor, not load-bearing.

Current anchor for grounding: Godot **4.7** (stable, "Director's Cut"), Unity **6.4** (6.x LTS as the production baseline), Unreal **5.x**, Bevy **0.18**, Macroquad **0.4.x**, LÖVE **11.x**.

**When version actually matters — verify, don't guess.** For project scaffolding or API calls whose syntax differs across releases (Godot 3 vs 4 broke almost everything; Bevy breaks ~quarterly; Unity's input/physics APIs shift), confirm the user's actual version and check current-release syntax rather than trusting this anchor or training-data memory. The patterns in this skill are stable across versions; the exact API surface is not.
