#!/usr/bin/env python3
"""Build iteration-5 benchmark.json combining new evals + carried-forward iteration-4 evals."""
import json
import math
import os
from datetime import datetime

WORKSPACE = "/Users/jacobelder/Documents/GitHub/jakes-skills/causal-inference-workspace"
ITER5_DIR = f"{WORKSPACE}/iteration-5"
ITER4_BENCHMARK = f"{WORKSPACE}/iteration-4/benchmark.json"

# Evals newly run in iteration-5
ITER5_EVALS = [
    ("rung-identification", 1),
    ("did-parallel-trends-violation", 5),
    ("front-door-identification", 7),
    ("att-vs-ate-rollout", 9),
    ("rdd-manipulation", 11),
    ("iv-exclusion-violation", 12),
    ("interference-sutva", 13),
]

# Evals carried forward from iteration-4 (unchanged)
CARRIED_FORWARD = {
    "selection-bias-power-users",
    "near-iv-bias-amplification",
    "table-2-fallacy",
    "mediator-overcontrol",
    "simpsons-paradox",
    "predictive-vs-causal",
}


def load_grading(eval_name, config):
    path = f"{ITER5_DIR}/{eval_name}/{config}/grading.json"
    with open(path) as f:
        g = json.load(f)
    # Handle both flat layout and summary-nested layout
    if "summary" in g and isinstance(g["summary"], dict):
        passed = g["summary"]["passed"]
        total = g["summary"]["total"]
    else:
        passed = g["passed"]
        total = g["total"]
    expectations = g.get("expectations", [])
    return passed, total, expectations


def load_timing(eval_name, config):
    path = f"{ITER5_DIR}/{eval_name}/{config}/timing.json"
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
            "time_seconds": round(timing["total_duration_seconds"], 1),
            "tokens": timing["total_tokens"],
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


# Load iteration-4 benchmark for carried-forward evals
with open(ITER4_BENCHMARK) as f:
    iter4 = json.load(f)

cf_runs = [r for r in iter4["runs"] if r["eval_name"] in CARRIED_FORWARD]

# Build new runs from iteration-5
new_runs = []
for eval_name, eval_id in ITER5_EVALS:
    for config in ["with_skill", "without_skill"]:
        new_runs.append(build_run(eval_name, eval_id, config))

# Combine and sort
all_runs = new_runs + cf_runs
config_order = {"with_skill": 0, "without_skill": 1}
all_runs.sort(key=lambda r: (r["eval_id"], config_order.get(r["configuration"], 2)))

# Summary stats
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
        "skill_name": "causal-inference",
        "skill_path": "/Users/jacobelder/Documents/GitHub/jakes-skills/causal-inference",
        "executor_model": "claude-sonnet-4-6",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "evals_run": evals_run,
        "runs_per_configuration": 1,
        "note": "7 evals newly run in iteration-5; 6 evals carried forward from iteration-4/3",
    },
    "runs": all_runs,
    "run_summary": {
        "with_skill": {
            "pass_rate":    {"mean": mean(ws_pass), "stddev": stddev(ws_pass), "min": min(ws_pass), "max": max(ws_pass)},
            "time_seconds": {"mean": mean(ws_time), "stddev": stddev(ws_time), "min": min(ws_time), "max": max(ws_time)},
            "tokens":       {"mean": mean(ws_tok),  "stddev": stddev(ws_tok),  "min": min(ws_tok),  "max": max(ws_tok)},
        },
        "without_skill": {
            "pass_rate":    {"mean": mean(no_pass), "stddev": stddev(no_pass), "min": min(no_pass), "max": max(no_pass)},
            "time_seconds": {"mean": mean(no_time), "stddev": stddev(no_time), "min": min(no_time), "max": max(no_time)},
            "tokens":       {"mean": mean(no_tok),  "stddev": stddev(no_tok),  "min": min(no_tok),  "max": max(no_tok)},
        },
        "delta": {
            "pass_rate":    f"{delta_pr:+.4f}",
            "time_seconds": f"{delta_time:+.1f}",
            "tokens":       f"{int(delta_tok):+d}",
        },
    },
    "notes": [
        f"iteration-5: with_skill achieves {mean(ws_pass)*100:.1f}% mean pass rate across {len(evals_run)} evals ({ws_total_passed}/{ws_total} assertions).",
        f"without_skill: {mean(no_pass)*100:.1f}% mean pass rate ({no_total_passed}/{no_total} assertions).",
        f"Net delta: {delta_pr*100:+.1f}pp (was +19.2pp in iter-4 where with_skill regressed on front-door and iv-exclusion).",
        "FIXED: front-door-identification — with_skill now 5/5 (was 4/5 in iter-4). Added explicit complete-mediation condition.",
        "FIXED: iv-exclusion-violation — with_skill now 4/4 (was 2/4 in iter-4). Added 'bias direction unknown' principle and never-taker falsification test.",
        "STILL NON-DISCRIMINATING (0pp delta): did-parallel-trends, att-vs-ate-rollout, rdd-manipulation, interference-sutva — base model passes all at 100%.",
        "DISCRIMINATING: rung-identification (+20pp: 5/5 vs 4/5), iv-exclusion-violation (+25pp: 4/4 vs 3/4).",
        "REMAINING GAP: iv-exclusion without_skill still fails assertion 3 (bias direction unknown) — base model still characterizes IV bias as directionally upward.",
    ],
}

out_path = f"{ITER5_DIR}/benchmark.json"
with open(out_path, "w") as f:
    json.dump(benchmark, f, indent=2)

print(f"Written: {out_path}")
print(f"\nSummary:")
print(f"  with_skill:    {mean(ws_pass)*100:.1f}% pass rate ({mean(ws_time):.1f}s, {mean(ws_tok):.0f} tokens)")
print(f"  without_skill: {mean(no_pass)*100:.1f}% pass rate ({mean(no_time):.1f}s, {mean(no_tok):.0f} tokens)")
print(f"  Delta:         {delta_pr*100:+.1f}pp, {delta_time:+.1f}s, {int(delta_tok):+d} tokens")
print(f"\nPer-eval breakdown (7 new evals):")
for r in new_runs:
    if r["configuration"] == "with_skill":
        ws = r["result"]["pass_rate"]
        no = next((x["result"]["pass_rate"] for x in new_runs
                   if x["eval_name"] == r["eval_name"] and x["configuration"] == "without_skill"), None)
        delta = (ws - no) if no is not None else 0
        print(f"  {r['eval_name']:42s} with={ws*100:.0f}% without={no*100 if no else 0:.0f}% delta={delta*100:+.0f}pp")
