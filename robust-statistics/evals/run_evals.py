"""
Eval runner for robust-statistics skill.

For each eval in evals.json:
  1. Get baseline response (no skill).
  2. Get with-skill response (SKILL.md + all references appended).
  3. Grade each assertion with a separate grader call.
  4. Save per-eval results and a summary benchmark.json.

Usage:
    python evals/run_evals.py [--evals 1,2,3] [--condition baseline|with_skill|both]
"""

from __future__ import annotations
import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path

REPO     = Path(__file__).parent.parent
SKILL_MD = (REPO / "SKILL.md").read_text()
REF_DIR  = REPO / "references"
EVALS_JSON = REPO / "evals.json"

REF_NAMES = [
    "robustness.md", "estimands.md", "glm-families.md",
    "robust-inference.md", "diagnostics.md", "philosophy.md", "worked-examples.md",
    "inference-validity.md", "missing-data.md",
]
ref_parts = []
for name in REF_NAMES:
    p = REF_DIR / name
    if p.exists():
        ref_parts.append(f"# {name}\n{p.read_text()}")
REFS = "\n\n---\n\n".join(ref_parts)
SKILL_WITH_REFS = SKILL_MD + "\n\n---\n\n" + REFS

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def call_claude(prompt: str, system_extra: str | None = None,
                model: str = "claude-sonnet-4-6",
                timeout: int = 600) -> str:
    """Call claude CLI, piping prompt via stdin to avoid long argument issues."""
    cmd = ["claude",
           "--dangerously-skip-permissions",
           "--model", model,
           "--output-format", "text",
           "-p", "-"]          # '-' means read prompt from stdin
    if system_extra:
        cmd += ["--append-system-prompt", system_extra]

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = result.stdout.strip()
    if not out and result.stderr:
        # fallback: some CLI versions don't support '-' as prompt; retry with positional
        cmd2 = ["claude",
                "--dangerously-skip-permissions",
                "--model", model,
                "-p", prompt]
        if system_extra:
            cmd2 += ["--append-system-prompt", system_extra]
        r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=timeout)
        out = r2.stdout.strip()
    return out


GRADER_SYSTEM = """You are a strict grader for statistical methodology evals.
You will be shown a response to a statistical question and a list of assertions.
For each assertion, output exactly one line: the assertion number followed by PASS or FAIL.
Criterion: a PASS means the response clearly demonstrates the behavior described.
A FAIL means it does not, or only partially does (partial credit = FAIL).
Output format (nothing else, no extra text):
1: PASS
2: FAIL
Do not include explanations or extra lines."""


def _assertion_text(a) -> str:
    """Accept bare string or {text, type} object."""
    return a["text"] if isinstance(a, dict) else a


def grade_assertions(response: str, assertions: list) -> list[bool]:
    texts = [_assertion_text(a) for a in assertions]
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    # Truncate response if very long (keep first 2000 chars)
    resp_trunc = response[:2000] + ("..." if len(response) > 2000 else "")
    prompt = (
        f"Response to grade:\n\n{resp_trunc}\n\n"
        f"Assertions to evaluate:\n{numbered}"
    )
    raw = call_claude(prompt, system_extra=GRADER_SYSTEM)
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
        delay: float = 2.0) -> None:
    evals_data = json.loads(EVALS_JSON.read_text())["evals"]
    if eval_ids:
        evals_data = [e for e in evals_data if e["id"] in eval_ids]

    all_results = []

    for ev in evals_data:
        eid = ev["id"]
        prompt = ev["prompt"]
        assertions = ev["assertions"]
        print(f"\n=== Eval {eid} ===")
        print(f"  {prompt[:80]}...")

        for condition in conditions:
            system = SKILL_WITH_REFS if condition == "with_skill" else None
            print(f"  [{condition}] executor...", end=" ", flush=True)
            response = call_claude(prompt, system_extra=system)
            time.sleep(delay)

            print("grader...", end=" ", flush=True)
            passes = grade_assertions(response, assertions)
            time.sleep(delay)

            n_pass = sum(passes)
            n_total = len(assertions)

            # Apply grading rule: must_pass assertions are necessary conditions
            must_pass_fails = [
                i for i, (a, p) in enumerate(zip(assertions, passes))
                if isinstance(a, dict) and a.get("type") == "must_pass" and not p
            ]
            scored_passes = sum(
                p for a, p in zip(assertions, passes)
                if not (isinstance(a, dict) and a.get("type") == "must_pass")
            )
            scored_total = sum(
                1 for a in assertions
                if not (isinstance(a, dict) and a.get("type") == "must_pass")
            )
            scored_rate = scored_passes / scored_total if scored_total else 1.0
            eval_passes = (len(must_pass_fails) == 0) and (scored_rate >= 0.80)

            status = "PASS" if eval_passes else "FAIL"
            if must_pass_fails:
                status += f" (must_pass failed: {[i+1 for i in must_pass_fails]})"
            print(f"{n_pass}/{n_total} [{status}]  {['+' if p else '-' for p in passes]}")

            result = {
                "eval_id": eid,
                "condition": condition,
                "prompt": prompt,
                "response": response,
                "assertions": assertions,
                "assertion_results": passes,
                "passed": n_pass,
                "total": n_total,
                "pass_rate": n_pass / n_total if n_total else 0,
                "eval_passes": eval_passes,
                "must_pass_failed_indices": [i+1 for i in must_pass_fails],
            }
            all_results.append(result)
            out_file = RESULTS_DIR / f"eval_{eid:02d}_{condition}.json"
            out_file.write_text(json.dumps(result, indent=2))

    print("\n" + "="*50)
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
        "skill_name": "robust-statistics",
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
    args = parser.parse_args()

    eval_ids = [int(x) for x in args.evals.split(",")] if args.evals else None
    conditions = (["baseline", "with_skill"] if args.condition == "both"
                  else [args.condition])
    run(eval_ids, conditions)
