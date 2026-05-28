#!/usr/bin/env python3
"""
Iteration-7 eval: latent-moderation-sem
Trap-based eval comparing with_skill vs without_skill conditions.
"""

import anthropic
import json
import os
import time
import zipfile

# ── paths ──────────────────────────────────────────────────────────────────────
SKILL_ZIP   = "/Users/jacobelder/Documents/GitHub/jakes-skills/psychometrics/psychometrics.skill"
METADATA    = "/Users/jacobelder/Documents/GitHub/jakes-skills/psychometrics-workspace/iteration-7/latent-moderation-sem/eval_metadata.json"
BASE_DIR    = "/Users/jacobelder/Documents/GitHub/jakes-skills/psychometrics-workspace/iteration-7/latent-moderation-sem"

MODEL       = "claude-sonnet-4-6"
MAX_TOKENS  = 2000

# ── load eval metadata ─────────────────────────────────────────────────────────
with open(METADATA) as f:
    meta = json.load(f)

PROMPT     = meta["prompt"]
ASSERTIONS = meta["assertions"]

# ── read skill content from ZIP ────────────────────────────────────────────────
with zipfile.ZipFile(SKILL_ZIP) as zf:
    # List contents to find SKILL.md
    names = zf.namelist()
    skill_name = next(n for n in names if n.endswith("SKILL.md") or n == "SKILL.md")
    skill_content = zf.read(skill_name).decode("utf-8")

print(f"Loaded SKILL.md ({len(skill_content)} chars) from {skill_name}")

# ── Anthropic client ────────────────────────────────────────────────────────────
client = anthropic.Anthropic()


def call_api(prompt: str, system: str | None = None) -> tuple[str, dict]:
    """Call the API and return (response_text, timing_dict)."""
    start = time.time()
    kwargs = dict(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    end = time.time()

    text = next((b.text for b in response.content if b.type == "text"), "")
    timing = {
        "total_duration_seconds": round(end - start, 2),
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }
    return text, timing


def grade(response_text: str, assertions: list[str]) -> dict:
    """Grade the response against assertions using the grader model."""
    results = []
    for assertion in assertions:
        grade_prompt = f"""You are grading a psychometrics AI response against a specific assertion.

RESPONSE TO GRADE:
{response_text}

ASSERTION TO CHECK:
{assertion}

Does the response satisfy this assertion? Answer with:
PASS - if the response clearly satisfies the assertion
FAIL - if the response does not satisfy the assertion

Then provide a brief evidence quote (1-2 sentences max) from the response that supports your judgment.

Format:
VERDICT: PASS or FAIL
EVIDENCE: [quote or brief explanation]"""

        grade_response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": grade_prompt}],
        )
        grade_text = next((b.text for b in grade_response.content if b.type == "text"), "")

        passed = "VERDICT: PASS" in grade_text
        # Extract evidence
        evidence = ""
        if "EVIDENCE:" in grade_text:
            evidence = grade_text.split("EVIDENCE:", 1)[1].strip()

        results.append({
            "description": assertion,
            "passed": passed,
            "evidence": evidence,
        })

    passed_count = sum(1 for r in results if r["passed"])
    return {
        "passed": passed_count,
        "total": len(assertions),
        "expectations": results,
    }


def run_condition(condition: str, use_skill: bool):
    """Run a single condition (with_skill or without_skill)."""
    print(f"\n{'='*60}")
    print(f"Running condition: {condition}")
    print(f"{'='*60}")

    system = skill_content if use_skill else None
    response_text, timing = call_api(PROMPT, system=system)

    print(f"Response received ({len(response_text)} chars, {timing['total_duration_seconds']}s)")
    print(f"First 200 chars: {response_text[:200]}...")

    # Grade
    print("Grading...")
    grading = grade(response_text, ASSERTIONS)
    print(f"Score: {grading['passed']}/{grading['total']}")

    # Write outputs
    out_dir = os.path.join(BASE_DIR, condition, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "response.txt"), "w") as f:
        f.write(response_text)

    with open(os.path.join(BASE_DIR, condition, "grading.json"), "w") as f:
        json.dump(grading, f, indent=2)

    with open(os.path.join(BASE_DIR, condition, "timing.json"), "w") as f:
        json.dump(timing, f, indent=2)

    print(f"Files written to {os.path.join(BASE_DIR, condition)}/")
    return grading


# ── run both conditions ─────────────────────────────────────────────────────────
with_skill_grading   = run_condition("with_skill",    use_skill=True)
without_skill_grading = run_condition("without_skill", use_skill=False)

# ── summary ─────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("EVAL SUMMARY")
print("="*60)
print(f"with_skill:    {with_skill_grading['passed']}/{with_skill_grading['total']}")
print(f"without_skill: {without_skill_grading['passed']}/{without_skill_grading['total']}")

print("\nwithout_skill failures:")
for exp in without_skill_grading["expectations"]:
    if not exp["passed"]:
        print(f"  FAIL: {exp['description'][:80]}...")
        print(f"        Evidence: {exp['evidence'][:100]}")
