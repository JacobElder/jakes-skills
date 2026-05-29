#!/usr/bin/env python3
"""Build iteration-1 benchmark.json for the multilevel-modeling skill."""
import json
import math
import os
from datetime import datetime

ITER_DIR = os.path.dirname(os.path.abspath(__file__))

EVALS = [
    ("crossed-random-effects",            1),
    ("three-level-small-clusters",        2),
    ("cluster-rct-power",                 3),
    ("random-intercept-only-pushback",    4),
    ("singular-fit-troubleshooting",      5),
    ("nested-id-uniqueness",              6),
    ("treatment-coding-simple-effects",   7),
    ("ab-test-clustering",                8),
    ("bayesian-credible-interval",        9),
    ("logistic-glmm-interpretation",     10),
    ("icc-definition",                   11),
    ("paired-t-test",                    12),
]


def load_grading(eval_name, config):
    path = os.path.join(ITER_DIR, eval_name, config, "grading.json")
    with open(path) as f:
        g = json.load(f)
    summary = g.get("summary", {})
    passed = summary.get("passed", g.get("passed", 0))
    total  = summary.get("total",  g.get("total",  0))
    expectations = g.get("expectations", [])
    return passed, total, expectations


def build_run(eval_name, eval_id, config):
    passed, total, expectations = load_grading(eval_name, config)
    return {
        "eval_id": eval_id,
        "eval_name": eval_name,
        "configuration": config,
        "run_number": 1,
        "result": {
            "pass_rate": round(passed / total, 4) if total else 0.0,
            "passed": passed,
            "failed": total - passed,
            "total": total,
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
no_pass = [r["result"]["pass_rate"] for r in all_runs if r["configuration"] == "without_skill"]
delta_pr = mean(ws_pass) - mean(no_pass)

evals_run = sorted(set(r["eval_name"] for r in all_runs))
ws_total_passed = sum(r["result"]["passed"] for r in all_runs if r["configuration"] == "with_skill")
ws_total        = sum(r["result"]["total"]  for r in all_runs if r["configuration"] == "with_skill")
no_total_passed = sum(r["result"]["passed"] for r in all_runs if r["configuration"] == "without_skill")
no_total        = sum(r["result"]["total"]  for r in all_runs if r["configuration"] == "without_skill")

benchmark = {
    "metadata": {
        "skill_name": "multilevel-modeling",
        "skill_path": "/Users/jacobelder/Documents/GitHub/jakes-skills/multilevel-modeling/multilevel-modeling.skill",
        "executor_model": "claude-sonnet-4-6",
        "timestamp": datetime.now().isoformat() + "Z",
        "evals_run": evals_run,
        "runs_per_configuration": 1,
        "iteration": 1,
        "eval_design_note": (
            "Iteration-1 uses 12 direct content-quality evals covering specification correctness, "
            "pushback on bad models, brevity calibration, and triggering. Each expectation is a "
            "specific, objectively checkable assertion. Both configurations score 100% — a full "
            "ceiling effect. The base model answers direct MLM questions correctly; the skill's "
            "behavioral value (changing defaults when a user presents a wrong analysis as apparently "
            "acceptable) is not captured by these prompts. Iteration-2 will use trap-based prompts "
            "where the user presents a flawed analysis and asks for validation."
        ),
    },
    "runs": all_runs,
    "run_summary": {
        "with_skill": {
            "pass_rate": {
                "mean": mean(ws_pass),
                "stddev": stddev(ws_pass),
                "min": min(ws_pass) if ws_pass else 0.0,
                "max": max(ws_pass) if ws_pass else 0.0,
            },
        },
        "without_skill": {
            "pass_rate": {
                "mean": mean(no_pass),
                "stddev": stddev(no_pass),
                "min": min(no_pass) if no_pass else 0.0,
                "max": max(no_pass) if no_pass else 0.0,
            },
        },
        "delta": {"pass_rate": f"{delta_pr:+.4f}"},
        "totals": {
            "with_skill":    f"{ws_total_passed}/{ws_total}",
            "without_skill": f"{no_total_passed}/{no_total}",
        },
    },
}

out_path = os.path.join(ITER_DIR, "benchmark.json")
with open(out_path, "w") as f:
    json.dump(benchmark, f, indent=2)

print(f"Written: {out_path}")
print(f"\nSummary:")
print(f"  with_skill:    {mean(ws_pass)*100:.1f}% ({ws_total_passed}/{ws_total})")
print(f"  without_skill: {mean(no_pass)*100:.1f}% ({no_total_passed}/{no_total})")
print(f"  Delta:         {delta_pr*100:+.1f}pp")
print(f"\nPer-eval:")
for name, _ in EVALS:
    ws_r = next((r for r in all_runs if r["eval_name"] == name and r["configuration"] == "with_skill"),  None)
    no_r = next((r for r in all_runs if r["eval_name"] == name and r["configuration"] == "without_skill"), None)
    if ws_r and no_r:
        gap = ws_r["result"]["pass_rate"] - no_r["result"]["pass_rate"]
        print(f"  {name:40s}  with={ws_r['result']['passed']}/{ws_r['result']['total']}  "
              f"without={no_r['result']['passed']}/{no_r['result']['total']}  delta={gap*100:+.0f}pp")
