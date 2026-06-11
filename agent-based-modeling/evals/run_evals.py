#!/usr/bin/env python3
"""
Eval runner for the agent-based-modeling skill.

For each eval in evals.json:
  1. Get baseline response (no skill).
  2. Get with-skill response (SKILL.md + all references).
  3. Grade each assertion with a strict haiku grader.
  4. Save per-eval results and a summary benchmark.json.

Usage:
    python evals/run_evals.py [--evals 0,1,2] [--condition baseline|with_skill|both]
    python evals/run_evals.py --trigger        # run trigger_eval.json instead
    python evals/run_evals.py --skip-existing  # use cached results
"""

from __future__ import annotations
import argparse
import json
import subprocess
import time
from pathlib import Path

REPO     = Path(__file__).parent.parent
SKILL_MD = (REPO / "SKILL.md").read_text()
REF_DIR  = REPO / "references"

REF_NAMES = [
    "odd-protocol.md",
    "validation-and-calibration.md",
    "analysis-and-experiments.md",
    "limitations-and-pitfalls.md",
    "frameworks-and-tools.md",
    "generative-llm-agents.md",
    "key-literature.md",
]

ref_parts = []
for name in REF_NAMES:
    p = REF_DIR / name
    if p.exists():
        ref_parts.append(f"# {name}\n{p.read_text()}")

SKILL_WITH_REFS = SKILL_MD + "\n\n---\n\n" + "\n\n---\n\n".join(ref_parts)

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

EXECUTOR_MODEL = "claude-sonnet-4-6"
GRADER_MODEL   = "claude-haiku-4-5-20251001"

RATE_LIMIT_PHRASES = ["you've hit your limit", "you have hit your limit"]


def call_claude(prompt: str, system_extra: str | None = None,
                model: str = EXECUTOR_MODEL, timeout: int = 900) -> str:
    cmd = ["claude", "-p", prompt, "--model", model, "--dangerously-skip-permissions"]
    if system_extra:
        cmd += ["--append-system-prompt", system_extra]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    text = r.stdout.strip()
    if any(p in text.lower() for p in RATE_LIMIT_PHRASES):
        raise RuntimeError(f"Rate limited: {text}")
    return text


GRADER_SYSTEM = (
    "You are a strict grader. Given a response and numbered assertions, "
    "output one line per assertion: '1: PASS' or '1: FAIL'. "
    "PASS only when the response clearly and explicitly demonstrates the assertion. "
    "No explanations, no other text."
)


def grade_assertions(response: str, assertions: list[str]) -> list[bool]:
    numbered = "\n".join(f"{i+1}. {a}" for i, a in enumerate(assertions))
    resp = response[:20000] + ("…" if len(response) > 20000 else "")
    prompt = f"Response:\n{resp}\n\nAssertions:\n{numbered}"
    raw = call_claude(prompt, system_extra=GRADER_SYSTEM,
                      model=GRADER_MODEL, timeout=120)
    results: list[bool] = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        results.append("PASS" in line.upper())
    while len(results) < len(assertions):
        results.append(False)
    return results[:len(assertions)]


def run_capability_evals(eval_ids: list[int] | None, conditions: list[str],
                         delay: float = 2.0, skip_existing: bool = False) -> None:
    evals_data = json.loads((REPO / "evals" / "evals.json").read_text())["evals"]
    if eval_ids:
        evals_data = [e for e in evals_data if e["id"] in eval_ids]

    all_results: list[dict] = []

    for ev in evals_data:
        eid        = ev["id"]
        prompt     = ev["prompt"]
        assertions = [a["text"] for a in ev["assertions"]]
        print(f"\n=== Eval {eid}: {ev['name']} ===")
        print(f"  {prompt[:80]}…")

        for condition in conditions:
            result_path = RESULTS_DIR / f"eval_{eid:02d}_{condition}.json"
            if skip_existing and result_path.exists():
                existing = json.loads(result_path.read_text())
                all_results.append(existing)
                marks = "".join("+" if p else "-" for p in existing["assertion_results"])
                print(f"  [{condition}] CACHED  {existing['passed']}/{existing['total']}  [{marks}]")
                continue

            system = SKILL_WITH_REFS if condition == "with_skill" else None
            print(f"  [{condition}] executor…", end=" ", flush=True)
            try:
                response = call_claude(prompt, system_extra=system)
            except RuntimeError as e:
                print(f"SKIPPED ({e})")
                continue
            time.sleep(delay)

            print("grader…", end=" ", flush=True)
            passes = grade_assertions(response, assertions)
            time.sleep(delay)

            n_pass, n_total = sum(passes), len(assertions)
            marks = "".join("+" if p else "-" for p in passes)
            print(f"{n_pass}/{n_total}  [{marks}]")

            result = {
                "eval_id":          eid,
                "name":             ev["name"],
                "condition":        condition,
                "prompt":           prompt,
                "response":         response,
                "assertions":       assertions,
                "assertion_results": passes,
                "passed":           n_pass,
                "total":            n_total,
                "pass_rate":        n_pass / n_total if n_total else 0.0,
            }
            all_results.append(result)
            result_path.write_text(json.dumps(result, indent=2))

    _print_summary(all_results, conditions, "agent-based-modeling")


def run_trigger_evals(delay: float = 2.0) -> None:
    trigger_data = json.loads((REPO / "evals" / "trigger_eval.json").read_text())
    desc_text = (REPO / "SKILL.md").read_text().split("---")[0]  # frontmatter + desc

    TRIGGER_SYSTEM = (
        "You are a skill router. Given the skill description below and a user query, "
        "respond with exactly one word: TRIGGER or SKIP.\n\n"
        f"Skill description:\n{desc_text}"
    )

    results = []
    correct = 0
    for item in trigger_data:
        query = item["query"]
        expected = item["should_trigger"]
        raw = call_claude(query, system_extra=TRIGGER_SYSTEM,
                          model=GRADER_MODEL, timeout=60).strip().upper()
        predicted = "TRIGGER" in raw
        ok = predicted == expected
        correct += int(ok)
        mark = "✓" if ok else "✗"
        label = "TRIGGER" if expected else "SKIP"
        print(f"  {mark} [{label}] {query[:70]}…")
        results.append({"query": query, "expected": expected,
                         "predicted": predicted, "correct": ok})
        time.sleep(delay)

    total = len(results)
    print(f"\nTrigger accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
    (RESULTS_DIR / "trigger_results.json").write_text(json.dumps(results, indent=2))


def _print_summary(all_results: list[dict], conditions: list[str],
                   skill_name: str) -> None:
    print("\n" + "=" * 55)
    for cond in conditions:
        cr = [r for r in all_results if r["condition"] == cond]
        if not cr:
            continue
        ta = sum(r["total"]  for r in cr)
        tp = sum(r["passed"] for r in cr)
        print(f"{cond:14s}: {tp}/{ta} ({100*tp/ta:.1f}%)" if ta else f"{cond}: no data")

    if len(conditions) == 2:
        b_p = sum(r["passed"] for r in all_results if r["condition"] == "baseline")
        b_t = sum(r["total"]  for r in all_results if r["condition"] == "baseline")
        w_p = sum(r["passed"] for r in all_results if r["condition"] == "with_skill")
        w_t = sum(r["total"]  for r in all_results if r["condition"] == "with_skill")
        if b_t and w_t:
            print(f"delta         : {100*w_p/w_t - 100*b_p/b_t:+.1f}pp")

    benchmark = {
        "skill_name":     skill_name,
        "executor_model": EXECUTOR_MODEL,
        "grader_model":   GRADER_MODEL,
        "results":        all_results,
        "summary": {
            cond: {
                "passed": sum(r["passed"] for r in all_results if r["condition"] == cond),
                "total":  sum(r["total"]  for r in all_results if r["condition"] == cond),
            }
            for cond in conditions
        },
    }
    bfile = RESULTS_DIR / "benchmark.json"
    bfile.write_text(json.dumps(benchmark, indent=2))
    print(f"\nResults → {bfile}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--evals", help="comma-separated eval IDs, e.g. 0,1,6")
    p.add_argument("--condition", default="both",
                   choices=["baseline", "with_skill", "both"])
    p.add_argument("--trigger", action="store_true",
                   help="run trigger_eval.json instead of capability evals")
    p.add_argument("--skip-existing", action="store_true",
                   help="load cached results instead of re-running completed evals")
    args = p.parse_args()

    if args.trigger:
        run_trigger_evals()
    else:
        eval_ids   = [int(x) for x in args.evals.split(",")] if args.evals else None
        conditions = ["baseline", "with_skill"] if args.condition == "both" else [args.condition]
        run_capability_evals(eval_ids, conditions, skip_existing=args.skip_existing)
