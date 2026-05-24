#!/usr/bin/env python3
"""Build iteration-2 benchmark.json for the psychometrics skill."""
import json
import math
import os
from datetime import datetime

WORKSPACE = "/Users/jacobelder/Documents/GitHub/jakes-skills/psychometrics-workspace"
ITER2_DIR = f"{WORKSPACE}/iteration-2"

EVALS = [
    ("pca-not-efa", 1),
    ("reverse-item-method-factor", 2),
    ("alpha-threshold-adequate", 3),
    ("factor-score-indeterminacy", 4),
    ("grm-for-polytomous-irt", 5),
    ("testretest-state-anxiety", 6),
    ("construct-definition-gate", 7),
    ("longitudinal-invariance-prepost", 8),
]


def load_grading(eval_name, config):
    path = f"{ITER2_DIR}/{eval_name}/{config}/grading.json"
    with open(path) as f:
        g = json.load(f)
    return g["passed"], g["total"], g.get("expectations", [])


def load_timing(eval_name, config):
    path = f"{ITER2_DIR}/{eval_name}/{config}/timing.json"
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

delta_pr   = mean(ws_pass) - mean(no_pass)
delta_time = mean(ws_time) - mean(no_time)
delta_tok  = mean(ws_tok)  - mean(no_tok)

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
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "evals_run": evals_run,
        "runs_per_configuration": 1,
        "iteration": 2,
        "eval_design_note": "Iteration-2 evals target discriminating scenarios — prompts with 'traps' where a weaker response validates the wrong approach or fails to proactively flag a problem. Designed to surface gaps not caught by iteration-1's broadly-correct evals.",
    },
    "runs": all_runs,
    "run_summary": {
        "with_skill": {
            "pass_rate":    {"mean": mean(ws_pass), "stddev": stddev(ws_pass), "min": min(ws_pass) if ws_pass else 0, "max": max(ws_pass) if ws_pass else 0},
            "time_seconds": {"mean": mean(ws_time), "stddev": stddev(ws_time), "min": min(ws_time) if ws_time else 0, "max": max(ws_time) if ws_time else 0},
            "tokens":       {"mean": mean(ws_tok),  "stddev": stddev(ws_tok),  "min": min(ws_tok)  if ws_tok  else 0, "max": max(ws_tok)  if ws_tok  else 0},
        },
        "without_skill": {
            "pass_rate":    {"mean": mean(no_pass), "stddev": stddev(no_pass), "min": min(no_pass) if no_pass else 0, "max": max(no_pass) if no_pass else 0},
            "time_seconds": {"mean": mean(no_time), "stddev": stddev(no_time), "min": min(no_time) if no_time else 0, "max": max(no_time) if no_time else 0},
            "tokens":       {"mean": mean(no_tok),  "stddev": stddev(no_tok),  "min": min(no_tok)  if no_tok  else 0, "max": max(no_tok)  if no_tok  else 0},
        },
        "delta": {
            "pass_rate":    f"{delta_pr:+.4f}",
            "time_seconds": f"{delta_time:+.1f}",
            "tokens":       f"{int(delta_tok):+d}",
        },
    },
}

out_path = f"{ITER2_DIR}/benchmark.json"
with open(out_path, "w") as f:
    json.dump(benchmark, f, indent=2)

print(f"Written: {out_path}")
print(f"\nSummary:")
print(f"  with_skill:    {mean(ws_pass)*100:.1f}% pass rate ({ws_total_passed}/{ws_total} assertions)")
print(f"  without_skill: {mean(no_pass)*100:.1f}% pass rate ({no_total_passed}/{no_total} assertions)")
print(f"  Delta:         {delta_pr*100:+.1f}pp")
print(f"\nPer-eval breakdown:")
for name in sorted(evals_run):
    ws_r = next((r for r in all_runs if r["eval_name"] == name and r["configuration"] == "with_skill"), None)
    no_r = next((r for r in all_runs if r["eval_name"] == name and r["configuration"] == "without_skill"), None)
    if ws_r and no_r:
        gap = ws_r["result"]["pass_rate"] - no_r["result"]["pass_rate"]
        print(f"  {name:45s} with={ws_r['result']['passed']}/{ws_r['result']['total']} without={no_r['result']['passed']}/{no_r['result']['total']} delta={gap*100:+.0f}pp")
    elif ws_r:
        print(f"  {name:45s} with={ws_r['result']['passed']}/{ws_r['result']['total']} without=MISSING")
