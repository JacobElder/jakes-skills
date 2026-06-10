"""
Eval runner for multiverse-analysis skill.

For each eval in evals.json:
  1. Get baseline response (no skill) — sonnet executor.
  2. Get with-skill response (SKILL.md + references) — sonnet executor.
  3. Grade each assertion — haiku grader (faster, sufficient for PASS/FAIL).
  4. Save per-eval results and a summary benchmark.json.

Usage:
    python evals/run_evals.py [--evals 0,1,2,3,4] [--condition baseline|with_skill|both]
    python evals/run_evals.py --skip-existing          # reload cached results
"""

from __future__ import annotations
import argparse
import json
import subprocess
import time
from pathlib import Path

REPO       = Path(__file__).parent.parent
SKILL_MD   = (REPO / "SKILL.md").read_text()
REF_DIR    = REPO / "references"
EVALS_JSON = Path(__file__).parent / "evals.json"

REF_NAMES = ["methodology.md", "tooling.md"]
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
    cmd = ["claude", "-p", prompt,
           "--model", model,
           "--dangerously-skip-permissions"]
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


def _assertion_text(a) -> str:
    """Accept assertion as string or {'text': ..., 'type': ...} dict."""
    return a["text"] if isinstance(a, dict) else a


def grade_assertions(response: str, assertions: list) -> list[bool]:
    texts = [_assertion_text(a) for a in assertions]
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    resp_trunc = response[:5000] + ("…" if len(response) > 5000 else "")
    prompt = f"Response:\n{resp_trunc}\n\nAssertions:\n{numbered}"
    raw = call_claude(prompt, system_extra=GRADER_SYSTEM,
                      model=GRADER_MODEL, timeout=300)
    results: list[bool] = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        results.append("PASS" in line.upper())
    while len(results) < len(assertions):
        results.append(False)
    return results[:len(assertions)]


def passes_threshold(passes: list[bool], assertions: list) -> bool:
    """True iff all must_pass assertions pass AND >=80% of scored assertions pass."""
    must_pass_ok = all(
        passes[i] for i, a in enumerate(assertions)
        if isinstance(a, dict) and a.get("type") == "must_pass"
    )
    scored = [
        passes[i] for i, a in enumerate(assertions)
        if not (isinstance(a, dict) and a.get("type") == "must_pass")
    ]
    scored_rate = sum(scored) / len(scored) if scored else 1.0
    return must_pass_ok and scored_rate >= 0.80


def run(eval_ids: list[int] | None, conditions: list[str],
        delay: float = 2.0, skip_existing: bool = False) -> None:
    evals_data = json.loads(EVALS_JSON.read_text())["evals"]
    if eval_ids is not None:
        evals_data = [e for e in evals_data if e["id"] in eval_ids]

    all_results: list[dict] = []

    for ev in evals_data:
        eid        = ev["id"]
        prompt     = ev["prompt"]
        assertions = ev["assertions"]
        print(f"\n=== Eval {eid}: {ev.get('name', '')} ===")
        print(f"  {prompt[:80]}...")

        for condition in conditions:
            result_path = RESULTS_DIR / f"eval_{eid:02d}_{condition}.json"
            if skip_existing and result_path.exists():
                existing = json.loads(result_path.read_text())
                if existing.get("assertion_results") is None:
                    # partial save (executor done, grader timed out) — re-grade
                    print(f"  [{condition}] RE-GRADING cached response…", end=" ", flush=True)
                    try:
                        passes = grade_assertions(existing["response"], assertions)
                    except subprocess.TimeoutExpired:
                        print("TIMEOUT (grader) again — skipping")
                        continue
                    n_pass, n_total = sum(passes), len(assertions)
                    marks = "".join("+" if p else "-" for p in passes)
                    ok = "OK" if passes_threshold(passes, assertions) else "FAIL"
                    print(f"{n_pass}/{n_total}  [{marks}]  {ok}")
                    existing.update({
                        "assertion_results": passes, "passed": n_pass,
                        "pass_rate": n_pass/n_total if n_total else 0.0,
                        "eval_passes": passes_threshold(passes, assertions),
                    })
                    result_path.write_text(json.dumps(existing, indent=2))
                all_results.append(existing)
                if existing.get("assertion_results") is not None:
                    n_pass, n_total = existing["passed"], existing["total"]
                    marks = "".join("+" if p else "-" for p in existing["assertion_results"])
                    ok = "OK" if passes_threshold(existing["assertion_results"], assertions) else "FAIL"
                    print(f"  [{condition}] CACHED  {n_pass}/{n_total}  [{marks}]  {ok}")
                continue

            system = SKILL_WITH_REFS if condition == "with_skill" else None
            print(f"  [{condition}] executor…", end=" ", flush=True)
            try:
                response = call_claude(prompt, system_extra=system)
            except subprocess.TimeoutExpired:
                print("TIMEOUT (executor)")
                continue
            except RuntimeError as e:
                print(f"SKIPPED ({e})")
                continue
            time.sleep(delay)

            # save response immediately so a grader timeout doesn't lose it
            partial = {
                "eval_id": eid, "condition": condition,
                "prompt": prompt, "response": response,
                "assertions": [_assertion_text(a) for a in assertions],
                "assertion_types": [a.get("type","scored") if isinstance(a,dict) else "scored" for a in assertions],
                "assertion_results": None, "passed": None, "total": len(assertions),
                "pass_rate": None, "eval_passes": None,
            }
            result_path.write_text(json.dumps(partial, indent=2))

            print("grader…", end=" ", flush=True)
            try:
                passes = grade_assertions(response, assertions)
            except subprocess.TimeoutExpired:
                print("TIMEOUT (grader) — response saved, re-run with --skip-existing to re-grade")
                continue
            time.sleep(delay)

            n_pass, n_total = sum(passes), len(assertions)
            marks = "".join("+" if p else "-" for p in passes)
            ok = "OK" if passes_threshold(passes, assertions) else "FAIL"
            print(f"{n_pass}/{n_total}  [{marks}]  {ok}")

            result = {
                "eval_id":           eid,
                "condition":         condition,
                "prompt":            prompt,
                "response":          response,
                "assertions":        [_assertion_text(a) for a in assertions],
                "assertion_types":   [a.get("type","scored") if isinstance(a,dict) else "scored" for a in assertions],
                "assertion_results": passes,
                "passed":            n_pass,
                "total":             n_total,
                "pass_rate":         n_pass / n_total if n_total else 0.0,
                "eval_passes":       passes_threshold(passes, assertions),
            }
            all_results.append(result)
            result_path.write_text(json.dumps(result, indent=2))

    # ── summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    for cond in conditions:
        cr = [r for r in all_results if r["condition"] == cond]
        if not cr:
            continue
        ta = sum(r["total"]  for r in cr)
        tp = sum(r["passed"] for r in cr)
        evals_ok = sum(1 for r in cr if r.get("eval_passes", False))
        print(f"{cond:14s}: {tp}/{ta} assertions ({100*tp/ta:.1f}%)  "
              f"| {evals_ok}/{len(cr)} evals pass")

    if len(conditions) == 2:
        b_p = sum(r["passed"] for r in all_results if r["condition"] == "baseline")
        b_t = sum(r["total"]  for r in all_results if r["condition"] == "baseline")
        w_p = sum(r["passed"] for r in all_results if r["condition"] == "with_skill")
        w_t = sum(r["total"]  for r in all_results if r["condition"] == "with_skill")
        if b_t and w_t:
            print(f"delta         : {100*w_p/w_t - 100*b_p/b_t:+.1f}pp")

    benchmark = {
        "skill_name":     "multiverse-analysis",
        "executor_model": EXECUTOR_MODEL,
        "grader_model":   GRADER_MODEL,
        "results":        all_results,
        "summary": {
            cond: {
                "passed":      sum(r["passed"] for r in all_results if r["condition"] == cond),
                "total":       sum(r["total"]  for r in all_results if r["condition"] == cond),
                "evals_pass":  sum(1 for r in all_results
                                   if r["condition"] == cond and r.get("eval_passes", False)),
                "evals_total": sum(1 for r in all_results if r["condition"] == cond),
            }
            for cond in conditions
        },
    }
    bfile = RESULTS_DIR / "benchmark.json"
    bfile.write_text(json.dumps(benchmark, indent=2))
    print(f"\nResults → {bfile}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--evals", help="comma-separated eval IDs, e.g. 0,1,2")
    p.add_argument("--condition", default="both",
                   choices=["baseline", "with_skill", "both"])
    p.add_argument("--skip-existing", action="store_true",
                   help="reload cached results without re-running")
    args = p.parse_args()
    eval_ids   = [int(x) for x in args.evals.split(",")] if args.evals else None
    conditions = ["baseline", "with_skill"] if args.condition == "both" else [args.condition]
    run(eval_ids, conditions, skip_existing=args.skip_existing)
