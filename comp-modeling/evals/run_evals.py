"""
Run comp-modeling skill evals against the claude CLI.

Two conditions:
  baseline  -- claude -p "<prompt>"
  with_skill -- claude -p "<prompt>" --append-system-prompt "<SKILL.md + relevant refs>"

For routing evals, appends the full reference set so we can check routing logic.
For content evals, appends SKILL.md only (the always-loaded layer).
"""

import json
import subprocess
import sys
import time
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────────
REPO = Path(__file__).parent.parent
SKILL_MD = (REPO / "SKILL.md").read_text()
REF_DIR = REPO / "references"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

REF_FILES = {
    "reinforcement_learning.md": (REF_DIR / "reinforcement_learning.md").read_text(),
    "prospect_theory.md":        (REF_DIR / "prospect_theory.md").read_text(),
    "drift_diffusion.md":        (REF_DIR / "drift_diffusion.md").read_text(),
    "category_learning.md":      (REF_DIR / "category_learning.md").read_text(),
    "delay_discounting.md":      (REF_DIR / "delay_discounting.md").read_text(),
    "bayesian_learning.md":      (REF_DIR / "bayesian_learning.md").read_text(),
    "recovery.md":               (REF_DIR / "recovery.md").read_text(),
    "model_comparison.md":       (REF_DIR / "model_comparison.md").read_text(),
    "hierarchical_stan.md":      (REF_DIR / "hierarchical_stan.md").read_text(),
}

ALL_REFS = "\n\n---\n\n".join(
    f"# {name}\n{content}" for name, content in REF_FILES.items()
)

SKILL_WITH_REFS = SKILL_MD + "\n\n" + ALL_REFS


# ── eval definitions (subset focused on content + routing) ───────────────────
from eval_harness import EVALS, score_response

# Run content + routing evals (triggering requires observing file-load events)
RUNNABLE = [e for e in EVALS if e.category in ("content", "routing")]


# ── runner ────────────────────────────────────────────────────────────────────
def call_claude(prompt: str, system_extra: str | None = None,
                model: str = "haiku") -> str:
    cmd = ["claude", "-p", prompt,
           "--model", model,
           "--dangerously-skip-permissions"]
    if system_extra:
        cmd += ["--append-system-prompt", system_extra]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.stdout.strip()


def run_all(model: str = "haiku", delay: float = 1.5) -> dict:
    results = {"model": model, "evals": {}}
    total = len(RUNNABLE)
    for i, ev in enumerate(RUNNABLE, 1):
        print(f"  [{i}/{total}] {ev.id} ...", end=" ", flush=True)

        # baseline
        base_resp = call_claude(ev.prompt, system_extra=None, model=model)
        time.sleep(delay)

        # with skill
        skill_resp = call_claude(ev.prompt, system_extra=SKILL_WITH_REFS, model=model)
        time.sleep(delay)

        base_score  = score_response(ev, base_resp)
        skill_score = score_response(ev, skill_resp)

        results["evals"][ev.id] = {
            "category":    ev.category,
            "prompt":      ev.prompt,
            "base":  {"response": base_resp,  "pass": base_score["pass"],  "notes": base_score["notes"]},
            "skill": {"response": skill_resp, "pass": skill_score["pass"], "notes": skill_score["notes"]},
        }
        status = ("✓" if skill_score["pass"] else "✗") + (" base✓" if base_score["pass"] else " base✗")
        print(status)

    return results


# ── summary helpers ────────────────────────────────────────────────────────────
def summarize(results: dict) -> dict:
    by_cat: dict[str, dict] = {}
    for ev_id, ev in results["evals"].items():
        cat = ev["category"]
        if cat not in by_cat:
            by_cat[cat] = {"skill_pass": 0, "base_pass": 0, "total": 0}
        by_cat[cat]["total"] += 1
        if ev["skill"]["pass"]:
            by_cat[cat]["skill_pass"] += 1
        if ev["base"]["pass"]:
            by_cat[cat]["base_pass"] += 1
    return by_cat


# ── main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "haiku"
    print(f"\nRunning {len(RUNNABLE)} evals (baseline vs with-skill) on {model}...\n")

    results = run_all(model=model)

    out_path = RESULTS_DIR / f"run_live_{model}.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved → {out_path}")

    summary = summarize(results)
    print("\nSummary:")
    print(f"{'category':<15} {'skill':>8} {'base':>8} {'total':>7}")
    print("-" * 42)
    overall_skill = overall_base = overall_total = 0
    for cat, s in sorted(summary.items()):
        skill_rate = s["skill_pass"] / s["total"]
        base_rate  = s["base_pass"]  / s["total"]
        print(f"{cat:<15} {s['skill_pass']}/{s['total']} ({skill_rate:.0%})  "
              f"{s['base_pass']}/{s['total']} ({base_rate:.0%})")
        overall_skill += s["skill_pass"]
        overall_base  += s["base_pass"]
        overall_total += s["total"]
    print("-" * 42)
    print(f"{'overall':<15} {overall_skill}/{overall_total} ({overall_skill/overall_total:.0%})  "
          f"{overall_base}/{overall_total} ({overall_base/overall_total:.0%})")
