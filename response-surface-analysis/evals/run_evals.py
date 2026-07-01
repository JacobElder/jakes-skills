"""
Eval runner for response-surface-analysis skill.

For each eval in evals.json:
  1. Get baseline response (no skill).
  2. Get with-skill response (SKILL.md + all reference files appended).
  3. Grade each expectation with a separate grader call.
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
EVALS_JSON = REPO / "evals.json"

REF_NAMES = [
    "theory.md",
    "congruence-checklist.md",
    "workflow.md",
    "pitfalls.md",
    "r-implementation.md",
    "python-implementation.md",
    "extensions.md",
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


GRADER_SYSTEM = """You are a strict grader for response surface analysis (RSA) evals.
You will be shown a response to an RSA methodology question and a list of expectations.
For each expectation, output exactly one line: the expectation number followed by PASS or FAIL.
Criterion: PASS means the response clearly demonstrates the expected behavior.
FAIL means it does not, or only partially does (partial credit = FAIL).
Output format (nothing else, no extra text):
1: PASS
2: FAIL
Do not include explanations or extra lines."""


def grade_expectations(response: str, expectations: list[str],
                       grader_model: str = "claude-haiku-4-5-20251001") -> list[bool] | None:
    if not response or response == RATE_LIMIT_SENTINEL:
        return [False] * len(expectations)
    numbered = "\n".join(f"{i+1}. {e}" for i, e in enumerate(expectations))
    resp_trunc = response[:4000] + ("..." if len(response) > 4000 else "")
    prompt = (
        f"Response to grade:\n\n{resp_trunc}\n\n"
        f"Expectations to evaluate:\n{numbered}"
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
    while len(results) < len(expectations):
        results.append(False)
    return results[:len(expectations)]


def inject_files(prompt: str, files: list[str]) -> str:
    """Append file contents to the prompt for data-bearing evals."""
    for fpath in files:
        # Try evals/files/ first, then root
        candidates = [
            Path(__file__).parent / "files" / Path(fpath).name,
            REPO / fpath,
            REPO / Path(fpath).name,
        ]
        for p in candidates:
            if p.exists():
                content = p.read_text()
                prompt += f"\n\n---\nFile contents ({p.name}):\n```\n{content}\n```"
                break
    return prompt


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
        expectations = ev["expectations"]
        files = ev.get("files", [])

        # Inject file contents for data-bearing evals
        full_prompt = inject_files(base_prompt, files)

        print(f"\n=== Eval {eid} ===")
        print(f"  {base_prompt[:80]}...")

        for condition in conditions:
            system = SKILL_WITH_REFS if condition == "with_skill" else None
            print(f"  [{condition}] executor...", end=" ", flush=True)
            response = call_claude(full_prompt, system_extra=system, model=executor_model)
            time.sleep(delay)

            if not response or response == RATE_LIMIT_SENTINEL:
                print("RATE-LIMITED — skipping grading")
                continue

            print("grader...", end=" ", flush=True)
            passes = grade_expectations(response, expectations, grader_model=grader_model)
            time.sleep(delay)

            if passes is None:
                print("GRADER RATE-LIMITED — skipping")
                continue

            n_pass = sum(passes)
            n_total = len(expectations)
            pass_rate = n_pass / n_total if n_total else 0
            eval_passes = pass_rate >= 0.80

            status = "PASS" if eval_passes else "FAIL"
            print(f"{n_pass}/{n_total} [{status}]  {['+' if p else '-' for p in passes]}")

            result = {
                "eval_id": eid,
                "condition": condition,
                "prompt": base_prompt,
                "response": response,
                "expectations": expectations,
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

    benchmark = {
        "skill_name": "response-surface-analysis",
        "results": all_results,
        "summary": {
            cond: {
                "passed": sum(r["passed"] for r in all_results if r["condition"] == cond),
                "total":  sum(r["total"]  for r in all_results if r["condition"] == cond),
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
