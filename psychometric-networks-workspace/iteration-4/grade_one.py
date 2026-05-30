#!/usr/bin/env python3
"""Grade a single eval response file, writing grading.json."""

import json, subprocess, time
from pathlib import Path

WORKSPACE = Path(__file__).parent
SKILL_DIR = WORKSPACE.parent.parent / "psychometric-networks"
EVALS_JSON = SKILL_DIR / "psychometric-networks-evals.json"
MODEL = "claude-sonnet-4-6"

GRADER_SYSTEM = """You are a rigorous grader evaluating AI model responses against a set of expectations.

Rules:
- Score the IDEA, not the attribution. A response that makes the right argument without a specific citation passes; name-dropping without substance fails.
- The burden of proof to pass is on the expectation. If you can't find clear evidence, it's a FAIL.
- No partial credit. Each expectation is pass or fail only.
- When an expectation says "OR makes the equivalent substantive point", honor that.
- For numerical/threshold expectations, grade strictly on whether the exact thresholds were applied to the specific numbers given.
- For negative expectations (things the response should NOT do), fail if the bad thing happens.

Output valid JSON only — no markdown, no code fences. Schema:
{
  "expectations": [
    {"text": "...", "passed": true/false, "evidence": "specific quote or description"}
  ],
  "summary": {"passed": 0, "failed": 0, "total": 0, "pass_rate": 0.0}
}"""

eval_name = "hairball-gamma-tuning"
config = "with_skill"

evals_data = json.loads(EVALS_JSON.read_text())
eval_obj = next(e for e in evals_data["evals"] if e["name"] == eval_name)

out_dir = WORKSPACE / eval_name / config
response_text = (out_dir / "outputs" / "response.txt").read_text()
expectations = eval_obj["expectations"]

grader_prompt = (
    f"Eval: {eval_name}\nConfig: {config}\n\n"
    f"USER PROMPT:\n{eval_obj['prompt']}\n\n"
    f"MODEL RESPONSE:\n{response_text}\n\n"
    f"EXPECTATIONS:\n{json.dumps(expectations, indent=2)}\n\n"
    "Grade each expectation. Return valid JSON only — no markdown fences."
)

print("Calling grader...", flush=True)
t0 = time.time()
result = subprocess.run(
    ["claude", "--print", "--model", MODEL, "--system-prompt", GRADER_SYSTEM],
    input=grader_prompt,
    capture_output=True, text=True, timeout=300,
)
duration = time.time() - t0
raw = result.stdout.strip()
print(f"Grader finished in {duration:.1f}s", flush=True)
print("Raw output:", raw[:500])

# Strip fences
if "```" in raw:
    for part in raw.split("```"):
        part = part.strip().lstrip("json").strip()
        if part.startswith("{"):
            raw = part
            break

start = raw.find("{")
if start != -1:
    raw = raw[start:]
depth, end = 0, len(raw)
for i, ch in enumerate(raw):
    if ch == "{": depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break
raw = raw[:end]

grading = json.loads(raw)

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

out_path = out_dir / "grading.json"
out_path.write_text(json.dumps(grading_out, indent=2))
print(f"\nResult: {passed}/{total} ({passed/total*100:.0f}%)")
for e in expectations_out:
    status = "PASS" if e["passed"] else "FAIL"
    print(f"  [{status}] {e['text'][:80]}")
    if not e["passed"]:
        print(f"         Evidence: {e['evidence'][:120]}")
