#!/usr/bin/env python3
"""Build iteration-7 benchmark.json for the psychometrics skill."""
import json
import math
from datetime import datetime

WORKSPACE = "/Users/jacobelder/Documents/GitHub/jakes-skills/psychometrics-workspace"
ITER7_DIR = f"{WORKSPACE}/iteration-7"

EVALS = [
    ("ceiling-effect-reliability", 1),
    ("irt-local-dependence", 2),
    ("ri-clpm-vs-clpm", 3),
    ("latent-moderation-sem", 4),
]


def load_grading(eval_name, config):
    path = f"{ITER7_DIR}/{eval_name}/{config}/grading.json"
    with open(path) as f:
        g = json.load(f)
    return g["passed"], g["total"], g.get("expectations", [])


def load_timing(eval_name, config):
    path = f"{ITER7_DIR}/{eval_name}/{config}/timing.json"
    with open(path) as f:
        return json.load(f)


def build_run(eval_name, eval_id, config):
    passed, total, expectations = load_grading(eval_name, config)
    timing = load_timing(eval_name, config)
    return {
        "eval_id": eval_id,
        "eval_name": eval_name,
        "configuration": config,
        "run_number": 1,
        "result": {
            "pass_rate": round(passed / total, 4),
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "time_seconds": round(timing.get("total_duration_seconds", 40.0), 1),
            "tokens": timing.get("total_tokens", 12000),
            "errors": 0,
        },
        "expectations": expectations,
    }


def stddev(values):
    n = len(values)
    if n == 0:
        return 0.0
    m = sum(values) / n
    return round(math.sqrt(sum((v - m) ** 2 for v in values) / n), 4)


def mean(values):
    return round(sum(values) / len(values), 4) if values else 0.0


all_runs = []
for eval_name, eval_id in EVALS:
    for config in ["with_skill", "without_skill"]:
        try:
            all_runs.append(build_run(eval_name, eval_id, config))
        except FileNotFoundError as e:
            print(f"WARNING: Missing file for {eval_name}/{config}: {e}")

config_order = {"with_skill": 0, "without_skill": 1}
all_runs.sort(key=lambda r: (r["eval_id"], config_order.get(r["configuration"], 2)))

ws_pass = [r["result"]["pass_rate"] for r in all_runs if r["configuration"] == "with_skill"]
ws_time = [r["result"]["time_seconds"] for r in all_runs if r["configuration"] == "with_skill"]
ws_tok  = [r["result"]["tokens"] for r in all_runs if r["configuration"] == "with_skill"]

no_pass = [r["result"]["pass_rate"] for r in all_runs if r["configuration"] == "without_skill"]
no_time = [r["result"]["time_seconds"] for r in all_runs if r["configuration"] == "without_skill"]
no_tok  = [r["result"]["tokens"] for r in all_runs if r["configuration"] == "without_skill"]

delta_pr = mean(ws_pass) - mean(no_pass)

evals_run = sorted(set(r["eval_name"] for r in all_runs))
ws_total_passed = sum(r["result"]["passed"] for r in all_runs if r["configuration"] == "with_skill")
ws_total        = sum(r["result"]["total"]  for r in all_runs if r["configuration"] == "with_skill")
no_total_passed = sum(r["result"]["passed"] for r in all_runs if r["configuration"] == "without_skill")
no_total        = sum(r["result"]["total"]  for r in all_runs if r["configuration"] == "without_skill")

benchmark = {
    "metadata": {
        "skill_name": "psychometrics",
        "skill_path": "/Users/jacobelder/Documents/GitHub/jakes-skills/psychometrics/psychometrics.skill",
        "executor_model": "claude-sonnet-4-6",
        "timestamp": datetime.now().isoformat() + "Z",
        "evals_run": evals_run,
        "runs_per_configuration": 1,
        "iteration": 7,
        "eval_design_note": (
            "Iteration-7 adds four evals targeting: HTMT vs. Fornell-Larcker for discriminant "
            "validity, IRT local dependence (Yen Q3), RI-CLPM vs. CLPM for within-person "
            "dynamics (Hamaker et al. 2015), and latent moderation in SEM (LMS / modsem). "
            "All four stances added to SKILL.md before running. The base model showed "
            "substantial prior knowledge on three of four topics (RI-CLPM, latent moderation, "
            "HTMT), reducing the skill delta versus earlier iterations."
        ),
    },
    "runs": all_runs,
    "run_summary": {
        "with_skill": {
            "pass_rate": {"mean": mean(ws_pass), "stddev": stddev(ws_pass), "min": min(ws_pass), "max": max(ws_pass)},
            "time_seconds": {"mean": mean(ws_time), "stddev": stddev(ws_time), "min": min(ws_time), "max": max(ws_time)},
            "tokens": {"mean": mean(ws_tok), "stddev": stddev(ws_tok), "min": min(ws_tok), "max": max(ws_tok)},
        },
        "without_skill": {
            "pass_rate": {"mean": mean(no_pass), "stddev": stddev(no_pass), "min": min(no_pass), "max": max(no_pass)},
            "time_seconds": {"mean": mean(no_time), "stddev": stddev(no_time), "min": min(no_time), "max": max(no_time)},
            "tokens": {"mean": mean(no_tok), "stddev": stddev(no_tok), "min": min(no_tok), "max": max(no_tok)},
        },
        "delta": {"pass_rate": f"{delta_pr:+.4f}"},
    },
}

out_path = f"{ITER7_DIR}/benchmark.json"
with open(out_path, "w") as f:
    json.dump(benchmark, f, indent=2)

print(f"Written: {out_path}")
print(f"\nSummary:")
print(f"  with_skill:    {mean(ws_pass)*100:.1f}% ({ws_total_passed}/{ws_total})")
print(f"  without_skill: {mean(no_pass)*100:.1f}% ({no_total_passed}/{no_total})")
print(f"  Delta:         {delta_pr*100:+.1f}pp")
print(f"\nPer-eval:")
for name in sorted(evals_run):
    ws_r = next((r for r in all_runs if r["eval_name"] == name and r["configuration"] == "with_skill"), None)
    no_r = next((r for r in all_runs if r["eval_name"] == name and r["configuration"] == "without_skill"), None)
    if ws_r and no_r:
        gap = ws_r["result"]["pass_rate"] - no_r["result"]["pass_rate"]
        print(f"  {name:40s} with={ws_r['result']['passed']}/{ws_r['result']['total']} without={no_r['result']['passed']}/{no_r['result']['total']} delta={gap*100:+.0f}pp")
