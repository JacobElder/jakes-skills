#!/usr/bin/env python3
"""Aggregate grading.json files into benchmark.json for this workspace layout."""

import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).parent
SKILL_NAME = "psychometric-networks"
MODEL = "claude-sonnet-4-6"

EVAL_ORDER = [
    "ggm-estimation-likert",
    "centrality-review-betweenness",
    "latent-vs-network-debate",
    "esm-temporal-network",
    "stability-interpretation",
    "node-selection-question",
    "negative-trigger-generic-network",
    "definitional-baseline",
]


def load_results():
    runs = []
    for eval_name in EVAL_ORDER:
        for config in ["with_skill", "without_skill"]:
            grading_file = WORKSPACE / eval_name / config / "grading.json"
            timing_file = WORKSPACE / eval_name / config / "timing.json"
            if not grading_file.exists():
                print(f"WARNING: missing {grading_file}")
                continue
            g = json.loads(grading_file.read_text())
            timing = json.loads(timing_file.read_text()) if timing_file.exists() else {}
            runs.append({
                "eval_id": g.get("eval_id", eval_name),
                "eval_name": eval_name,
                "configuration": config,
                "run_number": 1,
                "result": {
                    "pass_rate": g.get("summary", {}).get("pass_rate", 0.0),
                    "passed": g.get("passed", g.get("summary", {}).get("passed", 0)),
                    "failed": g.get("summary", {}).get("failed", 0),
                    "total": g.get("total", g.get("summary", {}).get("total", 0)),
                    "time_seconds": timing.get("total_duration_seconds", 0.0),
                },
                "expectations": g.get("expectations", []),
                "notes": [],
            })
    return runs


def aggregate(runs):
    by_config = {}
    for r in runs:
        c = r["configuration"]
        by_config.setdefault(c, []).append(r["result"]["pass_rate"])

    run_summary = {}
    for config, rates in by_config.items():
        n = len(rates)
        mean = sum(rates) / n
        run_summary[config] = {
            "pass_rate": {
                "mean": round(mean, 4),
                "n": n,
            }
        }

    configs = list(by_config.keys())
    if len(configs) >= 2:
        a = run_summary.get("with_skill", {}).get("pass_rate", {}).get("mean", 0)
        b = run_summary.get("without_skill", {}).get("pass_rate", {}).get("mean", 0)
        run_summary["delta"] = {"pass_rate": f"{a - b:+.4f}"}

    return run_summary


def main():
    runs = load_results()
    run_summary = aggregate(runs)

    eval_ids = sorted(set(r["eval_id"] for r in runs))

    benchmark = {
        "metadata": {
            "skill_name": SKILL_NAME,
            "skill_path": f"psychometric-networks/{SKILL_NAME}-SKILL.md",
            "executor_model": MODEL,
            "analyzer_model": MODEL,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": eval_ids,
            "runs_per_configuration": 1,
        },
        "runs": runs,
        "run_summary": run_summary,
        "notes": [],
    }

    out = WORKSPACE / "benchmark.json"
    out.write_text(json.dumps(benchmark, indent=2))
    print(f"Wrote {out}")

    # Print summary table
    print(f"\n{'Eval':<45} {'With':>6} {'Without':>8} {'Delta':>7}")
    print("-" * 70)
    with_total = without_total = with_n = without_n = 0
    for eval_name in EVAL_ORDER:
        w = next((r for r in runs if r["eval_name"] == eval_name and r["configuration"] == "with_skill"), None)
        wo = next((r for r in runs if r["eval_name"] == eval_name and r["configuration"] == "without_skill"), None)
        if w and wo:
            wp = w["result"]["passed"]
            wt = w["result"]["total"]
            wp_r = w["result"]["pass_rate"]
            wop = wo["result"]["passed"]
            wot = wo["result"]["total"]
            wo_r = wo["result"]["pass_rate"]
            delta = wp_r - wo_r
            print(f"{eval_name:<45} {wp}/{wt} ({wp_r*100:.0f}%)  {wop}/{wot} ({wo_r*100:.0f}%)  {delta*100:+.0f}pp")
            with_total += wp; with_n += wt
            without_total += wop; without_n += wot

    print("-" * 70)
    wr = with_total / with_n if with_n else 0
    wor = without_total / without_n if without_n else 0
    print(f"{'OVERALL':<45} {with_total}/{with_n} ({wr*100:.1f}%)  {without_total}/{without_n} ({wor*100:.1f}%)  {(wr-wor)*100:+.1f}pp")


if __name__ == "__main__":
    main()
