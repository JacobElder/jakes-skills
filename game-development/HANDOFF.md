# Eval harness & Claude Code handoff — `game-development`

This skill ships with a 5-case eval set (`evals/evals.json`) and a programmatic grader
(`scripts/grade_programmatic.py`). The cases each stress one or more of the five
non-negotiables:

| # | name | stresses |
|---|------|----------|
| 0 | godot-platformer-feel | frame independence + juice + platformer recipe + Godot idioms |
| 1 | survivors-like-perf-love | frame independence + decoupling + spatial partitioning/pooling + LÖVE |
| 2 | scope-finish-deckbuilder | find-the-fun / scope / production process |
| 3 | engine-select-python-cozy-sim | deliberate engine selection + data-driven architecture |
| 4 | game-feel-diagnosis | the juice toolkit (Unity flavor) |
| 5 | enemy-horde-pathing | enemy AI: flow fields + separation + many-agent perf |
| 6 | procgen-dungeon-validate | procedural generation: seed + technique + generate-then-validate |
| 7 | framerate-dependent-debug | frame independence in diagnostic framing (broken code in) |
| 8 | survivors-collision-love | spatial hash + pooling as CODE (LÖVE/Lua — second-engine grader) |

Evals 0, 5, 7, and 8 have programmatic assertions gradeable by `scripts/grade_programmatic.py`
(`--eval godot-platformer-feel | enemy-horde-pathing | framerate-dependent-debug | survivors-collision-love`);
the rest are LLM/human-graded against the assertions in `evals.json`. The grader covers two
engines (Godot/GDScript and LÖVE/Lua).

## What was validated in-session (Claude.ai, no subagents)

Eval 0 was run end-to-end through the grader as a sanity check:

- **with-skill output → 9/9** programmatic checks (`assets/godot_platformer_controller.gd` is that output, promoted to a bundled reference).
- **no-skill baseline** (≈ Godot's built-in CharacterBody2D template) **→ 5/9**, failing exactly the four feel-critical checks: coyote time, jump buffer, variable jump height, asymmetric gravity.

That delta is the thesis of the skill: default output compiles and "works," but misses the
techniques that make movement feel tight rather than floaty. Eval 8's bundled reference (`assets/love_spatial_hash_pool.lua`, Lua-syntax-validated) scores 5/5
programmatic vs a naive all-pairs baseline at 1/5. Routing on the remaining cases was
spot-checked (the SKILL.md table sends each prompt to the right reference[s]).

## Running the full benchmark in Claude Code (recommended)

Claude.ai can't run independent with-skill-vs-baseline subagents, so do the rigorous pass in
Claude Code, where the skill-creator harness works as intended:

1. **Spawn both runs per case in one turn** — a with-skill subagent (skill path provided) and a
   no-skill baseline subagent (same prompt, no skill). Save to
   `game-development-workspace/iteration-N/eval-<name>/{with_skill,without_skill}/outputs/`.
   Use the model id powering the session so the test matches real usage.
2. **Grade.**
   - Eval 0 (and any future code-output evals): run `scripts/grade_programmatic.py <output.gd>`
     for the deterministic checks, then have a grader subagent judge the one subjective
     assertion (juice quality).
   - Evals 1–4: grade with a grader subagent reading `agents/grader.md`, checking each
     assertion in `evals/evals.json`. Write `grading.json` per run using the
     `text`/`passed`/`evidence` fields the viewer expects.
3. **Aggregate**: `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name game-development`
   (from the skill-creator dir), then generate the eval viewer for human review *before*
   self-revising.
4. **Iterate** on whatever the human flags, rerun, repeat.

### Why a no-skill baseline (not an older-version baseline)

This is a new skill, so the baseline is "no skill at all" — that's the comparison that proves
the skill earns its context cost. Watch especially for cases where baseline already does fine
(simple one-step asks) — those shouldn't trigger the skill anyway, and aren't where the value is.

### Expected failure modes to watch for when grading

- **Eval 1**: baseline often writes naive O(n²) all-pairs collision and `table.insert`/GC-per-frame
  spawning. With-skill should name the grid/spatial-hash broad phase + pooling explicitly.
- **Eval 2**: baseline tends to jump straight to a big system/architecture or generic pep-talk.
  With-skill should lead with toy→prototype→slice→production and concrete scope cuts.
- **Eval 3**: baseline frequently reflexively recommends Unity, or recommends PyGame for a Steam
  title without the honest caveat. With-skill should default to Godot *and tie it to the person*.
- **Eval 4**: baseline says "add particles and sound" vaguely. With-skill should name hitstop,
  trauma-based screenshake, knockback, and movement-feel fixes for "floaty" — with restraint.

## Description-optimization (optional, last step)

After the skill is in good shape, run the skill-creator's `run_loop.py` to optimize the
frontmatter `description` for triggering. Generate ~20 trigger queries — include near-miss
negatives that should NOT trigger: **game theory / Nash equilibria** (math, not gamedev),
**gamification of a non-game app**, **playing or buying a game**, **3D modeling/Blender asset
work**, and **game *industry* career/business questions**. These share vocabulary with the skill
but need something else.
