#!/usr/bin/env python3
"""
Eval harness for multilevel-modeling skill — iteration 2 (trap-based evals).
Runs each eval with and without the skill system prompt via the claude CLI,
grades responses with a separate LLM judge, saves all artifacts.
"""

import json
import time
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).parent
SKILL_DIR = WORKSPACE.parent.parent / "multilevel-modeling"
EVALS_JSON = SKILL_DIR / "multilevel-modeling-evals.json"
SKILL_MD = SKILL_DIR / "SKILL.md"

MODEL = "claude-sonnet-4-6"
SKILL_SYSTEM = SKILL_MD.read_text()

GRADER_SYSTEM = """You are a rigorous grader evaluating AI model responses against a set of expectations.

Rules:
- Score the IDEA, not the attribution. A response that makes the right argument without a specific citation passes; name-dropping without substance fails.
- The burden of proof to pass is on the expectation. If you can't find clear evidence, it's a FAIL.
- No partial credit. Each expectation is pass or fail only.
- For negative expectations (things the response should NOT do), fail if the bad thing happens.
- For "does NOT validate" expectations: if the response hedges weakly ("some would argue...") but still effectively lets the user proceed, that counts as validating — FAIL.

Output valid JSON only — no markdown, no code fences. Schema:
{
  "expectations": [
    {"text": "...", "passed": true/false, "evidence": "specific quote or description"}
  ],
  "summary": {"passed": 0, "failed": 0, "total": 0, "pass_rate": 0.0}
}"""

INTER_CALL_DELAY = 15


def run_claude(prompt: str, system: str, is_grader: bool = False) -> tuple[str, float]:
    if not is_grader:
        time.sleep(INTER_CALL_DELAY)

    t0 = time.time()
    result = subprocess.run(
        ["claude", "--print", "--model", MODEL, "--system-prompt", system],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=180,
    )
    duration = time.time() - t0
    out = result.stdout.strip()

    if "hit your limit" in out or "hit your limit" in result.stderr:
        raise RuntimeError(f"Rate limit hit. Response: {out[:120]}")

    if result.returncode != 0 and not out:
        raise RuntimeError(
            f"claude CLI failed (rc={result.returncode})\n"
            f"stderr: {result.stderr[:800]}\nstdout: {out[:200]}"
        )
    return out, duration


def grade_response(eval_name, prompt, expectations, response_text, config) -> dict:
    grader_prompt = (
        f"Eval: {eval_name}\nConfig: {config}\n\n"
        f"USER PROMPT:\n{prompt}\n\n"
        f"MODEL RESPONSE:\n{response_text}\n\n"
        f"EXPECTATIONS:\n{json.dumps(expectations, indent=2)}\n\n"
        "Grade each expectation. Return valid JSON only — no markdown fences."
    )
    raw, _ = run_claude(grader_prompt, GRADER_SYSTEM, is_grader=True)

    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                raw = part
                break

    start = raw.find("{")
    if start != -1:
        raw = raw[start:]
    depth = 0
    end = len(raw)
    for i, ch in enumerate(raw):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    raw = raw[:end]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        retry_prompt = (
            "The following text should be a JSON object but failed to parse. "
            "Return ONLY a corrected valid JSON object, no other text:\n\n" + raw[:3000]
        )
        for _ in range(2):
            fixed, _ = run_claude(retry_prompt, "You output only valid JSON objects.", is_grader=True)
            start = fixed.find("{")
            if start != -1:
                fixed = fixed[start:]
                end = len(fixed)
                depth = 0
                for i, ch in enumerate(fixed):
                    if ch == "{": depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                fixed = fixed[:end]
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                continue
        print("  WARNING: grading failed to parse, returning unknown grades", flush=True)
        return {
            "expectations": [{"text": e, "passed": False, "evidence": "GRADING_FAILED"} for e in expectations],
            "summary": {"passed": 0, "failed": len(expectations), "total": len(expectations), "pass_rate": 0.0},
        }


def run_eval(eval_obj: dict, config: str, use_skill: bool) -> dict:
    eval_name = eval_obj["name"]
    prompt = eval_obj["prompt"]
    expectations = eval_obj["expectations"]

    out_dir = WORKSPACE / eval_name / config
    (out_dir / "outputs").mkdir(parents=True, exist_ok=True)
    response_file = out_dir / "outputs" / "response.txt"
    grading_file = out_dir / "grading.json"
    timing_file = out_dir / "timing.json"

    print(f"  [{config}] {eval_name} ...", flush=True)

    system = SKILL_SYSTEM if use_skill else "You are a helpful assistant."
    response_text, exec_duration = run_claude(prompt, system)
    response_file.write_text(response_text)

    grading = grade_response(eval_name, prompt, expectations, response_text, config)

    expectations_out = []
    for exp_text, graded in zip(expectations, grading["expectations"]):
        expectations_out.append({
            "text": graded.get("text", exp_text),
            "passed": graded["passed"],
            "evidence": graded.get("evidence", ""),
        })

    passed = sum(1 for e in expectations_out if e["passed"])
    total = len(expectations_out)

    grading_out = {
        "run_id": f"{eval_name}-{config}",
        "eval_id": eval_obj["id"],
        "eval_name": eval_name,
        "config": config,
        "passed": passed,
        "total": total,
        "expectations": expectations_out,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
    }
    grading_file.write_text(json.dumps(grading_out, indent=2))

    timing_out = {
        "eval_name": eval_name,
        "config": config,
        "executor_duration_seconds": round(exec_duration, 2),
        "total_duration_seconds": round(exec_duration, 2),
    }
    timing_file.write_text(json.dumps(timing_out, indent=2))

    pct = passed / total * 100 if total else 0
    print(f"    -> {passed}/{total} ({pct:.0f}%) in {exec_duration:.1f}s", flush=True)
    return grading_out


def main():
    evals_data = json.loads(EVALS_JSON.read_text())
    evals = evals_data["evals"]

    print(f"Running {len(evals)} evals x 2 configs = {len(evals) * 2} runs\n")

    results = []
    for eval_obj in evals:
        print(f"\nEval {eval_obj['id']}: {eval_obj['name']}")
        for config, use_skill in [("with_skill", True), ("without_skill", False)]:
            grading_file = WORKSPACE / eval_obj["name"] / config / "grading.json"
            if grading_file.exists():
                print(f"  [{config}] {eval_obj['name']} ... (already done, loading)")
                result = json.loads(grading_file.read_text())
                results.append(result)
                continue
            result = run_eval(eval_obj, config, use_skill)
            results.append(result)

    print("\n=== SUMMARY ===")
    with_skill = [r for r in results if r["config"] == "with_skill"]
    without_skill = [r for r in results if r["config"] == "without_skill"]

    for r in results:
        pct = r["passed"] / r["total"] * 100 if r["total"] else 0
        print(f"  {r['eval_name']:50s} [{r['config']:14s}] {r['passed']}/{r['total']} ({pct:.0f}%)")

    ws_passed = sum(r["passed"] for r in with_skill)
    ws_total = sum(r["total"] for r in with_skill)
    nos_passed = sum(r["passed"] for r in without_skill)
    nos_total = sum(r["total"] for r in without_skill)

    print(f"\n  with_skill:    {ws_passed}/{ws_total} ({ws_passed/ws_total*100:.1f}%)")
    print(f"  without_skill: {nos_passed}/{nos_total} ({nos_passed/nos_total*100:.1f}%)")
    print(f"  delta:         +{(ws_passed/ws_total - nos_passed/nos_total)*100:.1f}pp")


if __name__ == "__main__":
    main()
