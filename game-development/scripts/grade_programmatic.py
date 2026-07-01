#!/usr/bin/env python3
"""
Programmatic grader for the game-development skill evals.

Scope: the deterministic, pattern-checkable assertions — primarily eval 0
(the Godot platformer controller), where the output is code we can inspect for
the presence of specific feel techniques. Subjective assertions (juice quality,
scope judgment, engine-selection reasoning) are graded by an LLM/human grader
in the benchmark loop; this script handles the part that should never be
eyeballed twice.

Usage:
    python grade_programmatic.py <output_file> [--eval godot-platformer-feel]

<output_file> is the raw text/code the model produced for that eval.
Exits 0 always; prints a JSON report of {assertion, passed, evidence}.
"""
import sys
import re
import json
import argparse


def _find(pattern, text, flags=re.IGNORECASE):
    m = re.search(pattern, text, flags)
    return m.group(0).strip()[:80] if m else None


def grade_godot_platformer(text: str):
    """Checks for the platformer-controller recipe in Godot output."""
    results = []

    def check(name, passed, evidence):
        results.append({"text": name, "passed": bool(passed), "evidence": evidence or "not found"})

    # 1. movement in _physics_process, not _process
    has_phys = _find(r"_physics_process", text)
    # crude: flag if velocity/move_and_slide appears under _process without _physics_process
    move_in_process = bool(re.search(r"func\s+_process\b[\s\S]{0,400}?(move_and_slide|velocity\s*[+\-*]?=)", text, re.IGNORECASE)) and not has_phys
    check("Movement in _physics_process (fixed step), not _process",
          bool(has_phys) and not move_in_process, has_phys)

    # 2. coyote time
    coyote = _find(r"coyote", text)
    check("Implements coyote time", coyote, coyote)

    # 3. jump buffer
    buf = _find(r"(jump_?buffer|buffer_?time|buffer_?counter|jump_?buffered)", text)
    check("Implements jump buffering", buf, buf)

    # 4. variable jump height: cutting upward velocity on release
    var_jump = re.search(r"(is_action_just_released|jump.*released|released.*jump)[\s\S]{0,160}?velocity\.y\s*[*]?=|velocity\.y\s*\*=\s*0?\.", text, re.IGNORECASE)
    check("Implements variable jump height (cut velocity on early release)",
          var_jump, var_jump.group(0).strip()[:80] if var_jump else None)

    # 5. asymmetric gravity: two distinct gravity-like constants
    grav_consts = re.findall(r"(?:^|\b)([A-Za-z_]*(?:fall|rise|jump|up|down)[A-Za-z_]*gravity|[A-Za-z_]*gravity[A-Za-z_]*(?:fall|rise|up|down)[A-Za-z_]*)", text, re.IGNORECASE)
    two_gravities = len(set(g.lower() for g in grav_consts)) >= 2
    # fallback: a ternary picking gravity by velocity sign
    grav_branch = re.search(r"velocity\.y\s*[<>]\s*0[\s\S]{0,60}?gravity|gravity[\s\S]{0,60}?velocity\.y\s*[<>]\s*0", text, re.IGNORECASE)
    check("Uses asymmetric gravity (fall faster than rise)",
          two_gravities or grav_branch, (", ".join(sorted(set(grav_consts)))[:80] if grav_consts else (grav_branch.group(0)[:80] if grav_branch else None)))

    # 6. CharacterBody2D kinematic, not RigidBody for avatar
    cb = _find(r"CharacterBody2D", text)
    mas = _find(r"move_and_slide", text)
    rb_avatar = bool(re.search(r"extends\s+RigidBody2D", text, re.IGNORECASE))
    check("Uses CharacterBody2D + move_and_slide (kinematic), not RigidBody avatar",
          (cb or mas) and not rb_avatar, cb or mas)

    # 7. @export tunables
    exports = re.findall(r"@export", text)
    check("Exposes feel constants as @export tunables",
          len(exports) >= 2, f"{len(exports)} @export(s)")

    # 8. acceleration/deceleration rather than snapping
    accel = _find(r"(move_toward|lerp|accel|deceler|friction)", text)
    check("Uses acceleration/deceleration (move_toward/lerp), not instant snap",
          accel, accel)

    # 10. Input Map, not hardcoded keycodes
    inputmap = _find(r"(Input\.get_axis|Input\.is_action_|get_action_strength)", text)
    keycodes = _find(r"(KEY_[A-Z]|Input\.is_key_pressed)", text)
    check("Uses Input Map (get_axis/is_action_*), not hardcoded keycodes",
          inputmap and not keycodes, inputmap or (("hardcoded: " + keycodes) if keycodes else None))

    return results


GRADERS = {"godot-platformer-feel": grade_godot_platformer}


def grade_framerate_debug(text: str):
    """eval 7: diagnose + fix framerate-dependent movement."""
    results = []

    def check(name, passed, evidence):
        results.append({"text": name, "passed": bool(passed), "evidence": evidence or "not found"})

    diag = _find(r"(per[ -]?frame|frame ?rate|fps|frames per second|more frames|each frame)", text)
    check("Diagnoses framerate dependence (movement is per-frame, scales with FPS)", diag, diag)

    delta_fix = re.search(r"\*\s*delta|delta\s*\*", text, re.IGNORECASE)
    check("Fixes movement to per-second by multiplying by delta",
          delta_fix, delta_fix.group(0) if delta_fix else None)

    phys = _find(r"_physics_process", text)
    check("Recommends _physics_process (fixed timestep) for movement/physics", phys, phys)

    return results


def grade_enemy_horde(text: str):
    """eval 5: many-agents-one-target movement/pathing."""
    results = []

    def check(name, passed, evidence):
        results.append({"text": name, "passed": bool(passed), "evidence": evidence or "not found"})

    flow = _find(r"(flow ?field|vector ?field|dijkstra|integration field)", text)
    check("Recommends a shared flow field / vector-field path instead of per-agent A*", flow, flow)

    sep = _find(r"(separation|boids|flock|push (?:away|apart)|spread out)", text)
    check("Recommends separation steering so enemies don't stack into a blob", sep, sep)

    return results


def grade_love_survivors(text: str):
    """eval 8: LÖVE core systems for hundreds of projectiles vs enemies."""
    results = []

    def check(name, passed, evidence):
        results.append({"text": name, "passed": bool(passed), "evidence": evidence or "not found"})

    hashgrid = _find(r"(spatial ?hash|spatial ?grid|\bbucket|\bcell[s_]|grid\b)", text)
    check("Uses a spatial hash/grid (broad phase), not all-pairs", hashgrid, hashgrid)

    # heuristic: cell-keyed lookup present (math.floor(x / cell) style or for_nearby)
    cellquery = re.search(r"math\.floor\([^)]*/[^)]*\)|for_?nearby|query|cells?\[", text, re.IGNORECASE)
    check("Queries nearby cells rather than scanning every entity",
          cellquery, cellquery.group(0).strip()[:60] if cellquery else None)

    pool = _find(r"(pool|free ?list|acquire|release|reuse|_alive|inactive|dead)", text)
    check("Pools/reuses objects instead of allocating every frame", pool, pool)

    dt = re.search(r"\*\s*dt\b|\bdt\b", text)
    check("Frame-independent (uses dt on movement)", dt, dt.group(0) if dt else None)

    love_cb = _find(r"love\.(update|load|draw)", text)
    check("Uses LÖVE callbacks (love.update(dt) etc.)", love_cb, love_cb)

    return results


GRADERS["framerate-dependent-debug"] = grade_framerate_debug
GRADERS["enemy-horde-pathing"] = grade_enemy_horde
GRADERS["survivors-collision-love"] = grade_love_survivors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_file")
    ap.add_argument("--eval", default="godot-platformer-feel", choices=list(GRADERS))
    args = ap.parse_args()

    with open(args.output_file, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    results = GRADERS[args.eval](text)
    passed = sum(1 for r in results if r["passed"])
    report = {
        "eval": args.eval,
        "pass_count": passed,
        "total": len(results),
        "pass_rate": round(passed / len(results), 3) if results else 0.0,
        "expectations": results,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
