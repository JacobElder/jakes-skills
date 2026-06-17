"""
Eval runner for causal-inference skill.

For each eval in evals/evals.json:
  1. Get baseline response (no skill).
  2. Get with-skill response (SKILL.md + all reference files appended).
  3. Grade each assertion with a separate grader call.
  4. Save per-eval results and a summary benchmark.json.

Usage:
    python evals/run_evals.py [--evals 1,2,3] [--condition baseline|with_skill|both]
                              [--delay 15] [--executor-model ...] [--grader-model ...]
"""

from __future__ import annotations
import argparse
import json
import subprocess
import time
from pathlib import Path

REPO       = Path(__file__).parent.parent
SKILL_MD   = (REPO / "SKILL.md").read_text()
EVALS_JSON = REPO / "evals" / "evals.json"

REF_NAMES = [
    "adjustment.md",
    "controls.md",
    "counterfactuals.md",
]
ref_parts = []
for name in REF_NAMES:
    p = REPO / "references" / name
    if p.exists():
        ref_parts.append(f"# {name}\n{p.read_text()}")
REFS = "\n\n---\n\n".join(ref_parts)
SKILL_WITH_REFS = SKILL_MD + "\n\n---\n\n" + REFS

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

RATE_LIMIT_SENTINEL = "__RATE_LIMITED__"


def call_claude(prompt: str, system_extra: str | None = None,
                model: str = "claude-sonnet-4-6",
                timeout: int = 600,
                retries: int = 2,
                retry_delay: float = 30.0) -> str:
    for attempt in range(retries + 1):
        cmd = ["claude",
               "--dangerously-skip-permissions",
               "--model", model,
               "--output-format", "text",
               "-p", prompt]
        if system_extra:
            cmd += ["--append-system-prompt", system_extra]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(REPO),
        )
        out = result.stdout.strip()

        if any(p in out.lower() for p in ("hit your limit", "hit your session limit",
                                          "rate limit", "session limit")):
            if attempt < retries:
                print(f"\n  [rate-limited, waiting {retry_delay}s before retry "
                      f"{attempt+1}/{retries}]", end=" ", flush=True)
                time.sleep(retry_delay)
                continue
            return RATE_LIMIT_SENTINEL
        if out:
            return out

        if result.stderr and attempt < retries:
            time.sleep(retry_delay)
            continue
    return out


GRADER_SYSTEM = """You are a strict grader for causal inference evals.
You will be shown a response to a causal inference methodology question and a list of assertions.
For each assertion, output exactly one line: the assertion number followed by PASS or FAIL.
Criterion: PASS means the response clearly demonstrates the expected behavior.
FAIL means it does not, or only partially does (partial credit = FAIL).
Output format (nothing else, no extra text):
1: PASS
2: FAIL
Do not include explanations or extra lines."""


def grade_assertions(response: str, assertions: list[dict],
                     grader_model: str = "claude-haiku-4-5-20251001") -> list[bool] | None:
    if not response or response == RATE_LIMIT_SENTINEL:
        return [False] * len(assertions)
    texts = [a["text"] for a in assertions]
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    resp_trunc = response[:6000] + ("..." if len(response) > 6000 else "")
    prompt = (
        f"Response to grade:\n\n{resp_trunc}\n\n"
        f"Assertions to evaluate:\n{numbered}"
    )
    raw = call_claude(prompt, system_extra=GRADER_SYSTEM, model=grader_model)
    if not raw or raw == RATE_LIMIT_SENTINEL:
        return None
    results = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        results.append("PASS" in line.upper())
    while len(results) < len(assertions):
        results.append(False)
    return results[:len(assertions)]


def run(eval_ids: list[int] | None, conditions: list[str],
        delay: float = 15.0,
        executor_model: str = "claude-sonnet-4-6",
        grader_model: str = "claude-haiku-4-5-20251001") -> None:
    evals_data = json.loads(EVALS_JSON.read_text())["evals"]
    if eval_ids:
        evals_data = [e for e in evals_data if e["id"] in eval_ids]

    all_results = []

    for ev in evals_data:
        eid = ev["id"]
        base_prompt = ev["prompt"]
        assertions = ev["assertions"]

        print(f"\n=== Eval {eid}: {ev['name']} ===")
        print(f"  {base_prompt[:80]}...")

        for condition in conditions:
            system = SKILL_WITH_REFS if condition == "with_skill" else None
            print(f"  [{condition}] executor...", end=" ", flush=True)
            response = call_claude(base_prompt, system_extra=system, model=executor_model)
            time.sleep(delay)

            if not response or response == RATE_LIMIT_SENTINEL:
                print("RATE-LIMITED — skipping grading")
                continue

            print("grader...", end=" ", flush=True)
            passes = grade_assertions(response, assertions, grader_model=grader_model)
            time.sleep(delay)

            if passes is None:
                print("GRADER RATE-LIMITED — skipping")
                continue

            n_pass = sum(passes)
            n_total = len(assertions)
            pass_rate = n_pass / n_total if n_total else 0
            eval_passes = pass_rate >= 0.80

            status = "PASS" if eval_passes else "FAIL"
            print(f"{n_pass}/{n_total} [{status}]  {['+' if p else '-' for p in passes]}")

            result = {
                "eval_id": eid,
                "name": ev["name"],
                "condition": condition,
                "prompt": base_prompt,
                "baseline_failure_hypothesis": ev.get("baseline_failure_hypothesis", ""),
                "response": response,
                "assertions": assertions,
                "assertion_results": passes,
                "passed": n_pass,
                "total": n_total,
                "pass_rate": pass_rate,
                "eval_passes": eval_passes,
            }
            all_results.append(result)
            out_file = RESULTS_DIR / f"eval_{eid:02d}_{condition}.json"
            out_file.write_text(json.dumps(result, indent=2))

    print("\n" + "=" * 50)
    for condition in conditions:
        cond_results = [r for r in all_results if r["condition"] == condition]
        if not cond_results:
            continue
        total_a = sum(r["total"] for r in cond_results)
        total_p = sum(r["passed"] for r in cond_results)
        pct = 100 * total_p / total_a if total_a else 0
        print(f"{condition:12s}: {total_p}/{total_a} ({pct:.1f}%)")

    if len(conditions) == 2:
        b_pass = sum(r["passed"] for r in all_results if r["condition"] == "baseline")
        b_tot  = sum(r["total"]  for r in all_results if r["condition"] == "baseline")
        w_pass = sum(r["passed"] for r in all_results if r["condition"] == "with_skill")
        w_tot  = sum(r["total"]  for r in all_results if r["condition"] == "with_skill")
        if b_tot and w_tot:
            delta = 100 * w_pass / w_tot - 100 * b_pass / b_tot
            print(f"delta       : {delta:+.1f}pp")

    import datetime
    benchmark = {
        "skill_name": "causal-inference",
        "generated": datetime.date.today().isoformat(),
        "results": all_results,
        "summary": {
            cond: {
                "passed": sum(r["passed"] for r in all_results if r["condition"] == cond),
                "total":  sum(r["total"]  for r in all_results if r["condition"] == cond),
                "pct": round(
                    100 * sum(r["passed"] for r in all_results if r["condition"] == cond)
                    / max(1, sum(r["total"] for r in all_results if r["condition"] == cond)), 1
                ),
            }
            for cond in conditions
        }
    }
    bfile = RESULTS_DIR / "benchmark.json"
    bfile.write_text(json.dumps(benchmark, indent=2))
    print(f"\nResults → {bfile}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evals", help="comma-separated eval IDs e.g. 1,2,3")
    parser.add_argument("--condition", default="both",
                        choices=["baseline", "with_skill", "both"])
    parser.add_argument("--grader-model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--executor-model", default="claude-sonnet-4-6")
    parser.add_argument("--delay", type=float, default=15.0,
                        help="seconds between API calls (default: 15)")
    args = parser.parse_args()

    eval_ids = [int(x) for x in args.evals.split(",")] if args.evals else None
    conditions = (["baseline", "with_skill"] if args.condition == "both"
                  else [args.condition])
    run(eval_ids, conditions, delay=args.delay,
        executor_model=args.executor_model,
        grader_model=args.grader_model)
