#!/usr/bin/env python3
"""Build iteration-4 benchmark.json combining new evals + carried-forward iteration-3 evals."""
import json
import math
import os
from datetime import datetime

WORKSPACE = "/Users/jacobelder/Documents/GitHub/jakes-skills/causal-inference-workspace"
ITER4_DIR = f"{WORKSPACE}/iteration-4"
ITER3_BENCHMARK = f"{WORKSPACE}/iteration-3/benchmark.json"

# Evals in iteration-4 (newly run)
ITER4_EVALS = [
    ("rung-identification", 1),
    ("did-parallel-trends-violation", 5),
    ("front-door-identification", 7),
    ("att-vs-ate-rollout", 9),
    ("rdd-manipulation", 11),
    ("iv-exclusion-violation", 12),
    ("interference-sutva", 13),
]

# Carried-forward eval names from iteration-3
CARRIED_FORWARD = {
    "selection-bias-power-users",
    "near-iv-bias-amplification",
    "table-2-fallacy",
    "mediator-overcontrol",
    "simpsons-paradox",
    "predictive-vs-causal",
}

def load_grading(eval_name, config):
    path = f"{ITER4_DIR}/{eval_name}/{config}/grading.json"
    with open(path) as f:
        return json.load(f)

def load_timing(eval_name, config):
    path = f"{ITER4_DIR}/{eval_name}/{config}/timing.json"
    with open(path) as f:
        return json.load(f)

def build_run(eval_name, eval_id, config):
    grading = load_grading(eval_name, config)
    timing = load_timing(eval_name, config)
    passed = grading["passed"]
    total = grading["total"]
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
            "errors": 0
        },
        "expectations": grading["expectations"]
    }

def stddev(values):
    n = len(values)
    if n == 0:
        return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return round(math.sqrt(var), 4)

def mean(values):
    return round(sum(values) / len(values), 4) if values else 0.0

# Load iteration-3 benchmark for carried-forward evals
with open(ITER3_BENCHMARK) as f:
    iter3 = json.load(f)

# Pull carried-forward runs from iteration-3
cf_runs = [r for r in iter3["runs"] if r["eval_name"] in CARRIED_FORWARD]

# Build new runs from iteration-4
new_runs = []
for eval_name, eval_id in ITER4_EVALS:
    for config in ["with_skill", "without_skill"]:
        run = build_run(eval_name, eval_id, config)
        new_runs.append(run)

# Combine: new evals first (sorted by eval_id), then carried-forward
all_runs = new_runs + cf_runs

# Sort by eval_id, then config (with_skill first)
config_order = {"with_skill": 0, "without_skill": 1}
all_runs.sort(key=lambda r: (r["eval_id"], config_order.get(r["configuration"], 2)))

# Compute summary stats
ws_pass = [r["result"]["pass_rate"] for r in all_runs if r["configuration"] == "with_skill"]
ws_time = [r["result"]["time_seconds"] for r in all_runs if r["configuration"] == "with_skill"]
ws_tok  = [r["result"]["tokens"] for r in all_runs if r["configuration"] == "with_skill"]

no_pass = [r["result"]["pass_rate"] for r in all_runs if r["configuration"] == "without_skill"]
no_time = [r["result"]["time_seconds"] for r in all_runs if r["configuration"] == "without_skill"]
no_tok  = [r["result"]["tokens"] for r in all_runs if r["configuration"] == "without_skill"]

delta_pr = mean(ws_pass) - mean(no_pass)
delta_time = mean(ws_time) - mean(no_time)
delta_tok  = mean(ws_tok) - mean(no_tok)

evals_run = sorted(set(r["eval_name"] for r in all_runs))

benchmark = {
    "metadata": {
        "skill_name": "causal-inference",
        "skill_path": "/Users/jacobelder/Documents/GitHub/jakes-skills/causal-inference",
        "executor_model": "claude-sonnet-4-6",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "evals_run": evals_run,
        "runs_per_configuration": 1,
        "note": "7 evals newly run in iteration-4; 6 evals carried forward from iteration-3"
    },
    "runs": all_runs,
    "run_summary": {
        "with_skill": {
            "pass_rate": {"mean": mean(ws_pass), "stddev": stddev(ws_pass), "min": min(ws_pass), "max": max(ws_pass)},
            "time_seconds": {"mean": mean(ws_time), "stddev": stddev(ws_time), "min": min(ws_time), "max": max(ws_time)},
            "tokens": {"mean": mean(ws_tok), "stddev": stddev(ws_tok), "min": min(ws_tok), "max": max(ws_tok)}
        },
        "without_skill": {
            "pass_rate": {"mean": mean(no_pass), "stddev": stddev(no_pass), "min": min(no_pass), "max": max(no_pass)},
            "time_seconds": {"mean": mean(no_time), "stddev": stddev(no_time), "min": min(no_time), "max": max(no_time)},
            "tokens": {"mean": mean(no_tok), "stddev": stddev(no_tok), "min": min(no_tok), "max": max(no_tok)}
        },
        "delta": {
            "pass_rate": f"{delta_pr:+.4f}",
            "time_seconds": f"{delta_time:+.1f}",
            "tokens": f"{int(delta_tok):+d}"
        }
    },
    "notes": [
        f"iteration-4: with_skill achieves {mean(ws_pass)*100:.1f}% mean pass rate across 13 evals ({sum(int(r['result']['passed']) for r in all_runs if r['configuration']=='with_skill')}/{sum(int(r['result']['total']) for r in all_runs if r['configuration']=='with_skill')} assertions). Compared to iteration-3 (100%), this represents a regression.",
        f"without_skill: {mean(no_pass)*100:.1f}% mean pass rate ({sum(int(r['result']['passed']) for r in all_runs if r['configuration']=='without_skill')}/{sum(int(r['result']['total']) for r in all_runs if r['configuration']=='without_skill')} assertions), up from 75.0% in iter-3 due to harder evals being added.",
        f"Net delta: {delta_pr*100:+.1f}pp — down from +25.0pp in iter-3.",
        "REGRESSION: iv-exclusion-violation shows -25pp delta (with_skill 50% vs without_skill 75%). Skill characterizes exclusion bias direction as upward/SES instead of unknown.",
        "REGRESSION: front-door-identification shows -20pp delta (with_skill 80% vs without_skill 100%). Skill misses complete mediation condition that base model correctly flags.",
        "NON-DISCRIMINATING (0pp delta): did-parallel-trends, att-vs-ate-rollout, rdd-manipulation — base model already handles these at 100%. These evals need harder assertions.",
        "DISCRIMINATING (+25pp): interference-sutva — skill correctly explains spillover extrapolation failure while base model misses control contamination mechanism.",
        "DISCRIMINATING (+20pp): rung-identification — skill correctly flags alternative identification strategies beyond balance tests.",
        "SKILL IMPROVEMENT NEEDED: Add complete mediation condition to front-door section, clarify that exclusion violation biases in UNKNOWN direction (not just SES), add falsification test recommendation for IV instruments."
    ]
}

out_path = f"{ITER4_DIR}/benchmark.json"
with open(out_path, "w") as f:
    json.dump(benchmark, f, indent=2)

print(f"Written: {out_path}")
print(f"\nSummary:")
print(f"  with_skill:    {mean(ws_pass)*100:.1f}% pass rate ({mean(ws_time):.1f}s, {mean(ws_tok):.0f} tokens)")
print(f"  without_skill: {mean(no_pass)*100:.1f}% pass rate ({mean(no_time):.1f}s, {mean(no_tok):.0f} tokens)")
print(f"  Delta:         {delta_pr*100:+.1f}pp pass rate, {delta_time:+.1f}s, {int(delta_tok):+d} tokens")
print(f"\nPer-eval breakdown:")
for r in all_runs:
    if r["configuration"] == "with_skill":
        ws = r["result"]["pass_rate"]
        # find matching without_skill
        no = next((x["result"]["pass_rate"] for x in all_runs
                   if x["eval_name"] == r["eval_name"] and x["configuration"] == "without_skill"), None)
        delta = (ws - no) if no is not None else 0
        print(f"  {r['eval_name']:40s} with={ws*100:.0f}% without={no*100:.0f}% delta={delta*100:+.0f}pp")
