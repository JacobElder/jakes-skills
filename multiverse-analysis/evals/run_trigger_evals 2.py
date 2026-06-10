"""
Trigger eval runner for multiverse-analysis skill.

Checks whether each of the 20 queries in trigger-evals.json correctly triggers (or
does not trigger) the skill. A query "triggers" the skill when the model invokes a
skill or directly applies multiverse-analysis concepts (elicitation, specification
curve, etc.) rather than giving a generic statistical response.

Grading logic:
  - should_trigger=True  → PASS iff the response applies the multiverse workflow
    (mentions decisions, universes, specification curve, or analogous concepts from
    the skill) OR invokes the skill by name.
  - should_trigger=False → PASS iff the response does NOT invoke a multiverse
    workflow (e.g. gives a sensible answer that is clearly not a multiverse analysis).

Usage:
    python evals/run_trigger_evals.py [--evals 1,2,3] [--condition baseline|with_skill|both]
    python evals/run_trigger_evals.py --skip-existing
"""

from __future__ import annotations
import argparse
import json
import subprocess
import time
from pathlib import Path

REPO             = Path(__file__).parent.parent
SKILL_MD         = (REPO / "SKILL.md").read_text()
REF_DIR          = REPO / "references"
TRIGGER_JSON     = Path(__file__).parent / "trigger-evals.json"

REF_NAMES = ["methodology.md", "tooling.md"]
ref_parts = []
for name in REF_NAMES:
    p = REF_DIR / name
    if p.exists():
        ref_parts.append(f"# {name}\n{p.read_text()}")
SKILL_WITH_REFS = SKILL_MD + "\n\n---\n\n" + "\n\n---\n\n".join(ref_parts)

RESULTS_DIR = Path(__file__).parent / "trigger_results"
RESULTS_DIR.mkdir(exist_ok=True)

EXECUTOR_MODEL = "claude-sonnet-4-6"
GRADER_MODEL   = "claude-haiku-4-5-20251001"

RATE_LIMIT_PHRASES = ["you've hit your limit", "you have hit your limit"]

GRADER_SYSTEM_TRIGGER = (
    "You are a strict grader for trigger detection. "
    "A response TRIGGERS the multiverse-analysis skill when it applies the multiverse/"
    "specification-curve workflow: mentions decisions and options, enumerating universes, "
    "specification curves, decision importance, permutation inference, or the 'reasonable "
    "specification' criteria — even if it does not use those exact words. A generic "
    "statistical answer that does not apply this workflow does NOT trigger the skill. "
    "Output exactly one line: 'TRIGGERED' or 'NOT_TRIGGERED'. No other text."
)


def call_claude(prompt: str, system_extra: str | None = None,
                model: str = EXECUTOR_MODEL, timeout: int = 120) -> str:
    cmd = ["claude", "-p", prompt, "--model", model, "--dangerously-skip-permissions"]
    if system_extra:
        cmd += ["--append-system-prompt", system_extra]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    text = r.stdout.strip()
    if any(p in text.lower() for p in RATE_LIMIT_PHRASES):
        raise RuntimeError(f"Rate limited: {text}")
    return text



def run(eval_ids: list[int] | None, conditions: list[str],
        delay: float = 1.5, skip_existing: bool = False) -> None:
    data = json.loads(TRIGGER_JSON.read_text())
    evals = data["evals"]
    if eval_ids is not None:
        evals = [e for e in evals if e["id"] in eval_ids]

    all_results: list[dict] = []

    for ev in evals:
        eid           = ev["id"]
        prompt        = ev["prompt"]
        should_trigger = ev["should_trigger"]
        label         = "SHOULD trigger" if should_trigger else "should NOT trigger"
        print(f"\n=== Trigger eval {eid} ({label}) ===")
        print(f"  {prompt[:80]}...")

        for condition in conditions:
            result_path = RESULTS_DIR / f"trigger_{eid:02d}_{condition}.json"
            if skip_existing and result_path.exists():
                existing = json.loads(result_path.read_text())
                ok = "OK" if existing.get("passes") else "FAIL"
                detected = existing.get("triggered")
                print(f"  [{condition}] CACHED  triggered={detected}  expected={should_trigger}  {ok}")
                all_results.append(existing)
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

            print("grader…", end=" ", flush=True)
            try:
                raw = call_claude(f"Response:\n{response[:3000]}",
                                  system_extra=GRADER_SYSTEM_TRIGGER,
                                  model=GRADER_MODEL, timeout=60)
                triggered = "TRIGGERED" in raw.upper() and "NOT_TRIGGERED" not in raw.upper()
                passes = triggered == should_trigger
            except subprocess.TimeoutExpired:
                print("TIMEOUT (grader)")
                continue
            time.sleep(delay)

            ok = "OK" if passes else "FAIL"
            print(f"triggered={triggered}  expected={should_trigger}  {ok}")

            result = {
                "eval_id":        eid,
                "condition":      condition,
                "prompt":         prompt,
                "should_trigger": should_trigger,
                "triggered":      triggered,
                "passes":         passes,
                "response":       response,
            }
            all_results.append(result)
            result_path.write_text(json.dumps(result, indent=2))

    # summary
    print("\n" + "=" * 55)
    for cond in conditions:
        cr = [r for r in all_results if r["condition"] == cond]
        if not cr:
            continue
        n_pass = sum(1 for r in cr if r["passes"])
        n_total = len(cr)
        tp = sum(1 for r in cr if r["should_trigger"] and r["triggered"])
        fp = sum(1 for r in cr if not r["should_trigger"] and r["triggered"])
        fn = sum(1 for r in cr if r["should_trigger"] and not r["triggered"])
        tn = sum(1 for r in cr if not r["should_trigger"] and not r["triggered"])
        print(f"{cond:14s}: {n_pass}/{n_total} pass  "
              f"| TP={tp} TN={tn} FP={fp} FN={fn}")

    summary_path = RESULTS_DIR / "trigger_benchmark.json"
    summary = {
        "skill_name":     "multiverse-analysis",
        "executor_model": EXECUTOR_MODEL,
        "grader_model":   GRADER_MODEL,
        "results":        all_results,
        "summary": {
            cond: {
                "passed":  sum(1 for r in all_results if r["condition"] == cond and r["passes"]),
                "total":   sum(1 for r in all_results if r["condition"] == cond),
                "tp":      sum(1 for r in all_results if r["condition"] == cond
                               and r["should_trigger"] and r["triggered"]),
                "fp":      sum(1 for r in all_results if r["condition"] == cond
                               and not r["should_trigger"] and r["triggered"]),
                "fn":      sum(1 for r in all_results if r["condition"] == cond
                               and r["should_trigger"] and not r["triggered"]),
                "tn":      sum(1 for r in all_results if r["condition"] == cond
                               and not r["should_trigger"] and not r["triggered"]),
            }
            for cond in conditions
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nResults → {summary_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--evals", help="comma-separated eval IDs, e.g. 1,2,3")
    p.add_argument("--condition", default="both",
                   choices=["baseline", "with_skill", "both"])
    p.add_argument("--skip-existing", action="store_true")
    args = p.parse_args()
    eval_ids   = [int(x) for x in args.evals.split(",")] if args.evals else None
    conditions = ["baseline", "with_skill"] if args.condition == "both" else [args.condition]
    run(eval_ids, conditions, skip_existing=args.skip_existing)
