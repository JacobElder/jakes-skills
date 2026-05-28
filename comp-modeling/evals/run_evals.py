"""
Run comp-modeling skill evals against the claude CLI.

Two conditions:
  baseline  -- claude -p "<prompt>"
  with_skill -- claude -p "<prompt>" --append-system-prompt "<SKILL.md>"

Only content evals are runnable here. Routing evals test file-loading mechanics
(which references the agent actually reads), and those only work inside a real
skill install where the agent can invoke Read on the reference files. Passing
routing IDs via --ids will print an explanatory message and exit cleanly.
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


# ── eval definitions ──────────────────────────────────────────────────────────
from eval_harness import EVALS, score_response

# Content evals: baseline vs SKILL.md-only (the always-loaded layer).
# This tests whether the instruction layer changes behavior — the core question.
#
# Routing evals test file-loading mechanics that only work in a real skill
# install; skip them here.
CONTENT_EVALS  = [e for e in EVALS if e.category == "content"]
ROUTING_EVALS  = [e for e in EVALS if e.category == "routing"]
RUNNABLE = CONTENT_EVALS   # default: content only


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


def run_all(model: str = "haiku", delay: float = 4.0,
            evals: list | None = None) -> dict:
    evals = RUNNABLE if evals is None else evals
    results = {"model": model, "evals": {}}
    total = len(evals)
    for i, ev in enumerate(evals, 1):
        print(f"  [{i}/{total}] {ev.id} ...", end=" ", flush=True)

        # baseline — no extra context
        base_resp = call_claude(ev.prompt, system_extra=None, model=model)
        time.sleep(delay)

        # with skill — SKILL.md only (always-loaded layer; refs are progressive)
        skill_resp = call_claude(ev.prompt, system_extra=SKILL_MD, model=model)
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
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--delay", type=float, default=4.0,
                    help="Seconds between API calls")
    ap.add_argument("--ids", nargs="*",
                    help="Run only specific eval IDs, e.g. C1 C2 C3")
    args = ap.parse_args()

    subset = [e for e in CONTENT_EVALS
              if not args.ids or e.id in args.ids]

    if not subset:
        known_routing = [e.id for e in ROUTING_EVALS]
        hint = ""
        if args.ids and all(i in known_routing for i in args.ids):
            hint = " (routing eval IDs were passed — this harness only runs content evals)"
        print(f"No content evals matched {args.ids}.{hint}")
        sys.exit(0)

    print(f"\nRunning {len(subset)} content evals "
          f"(baseline vs with-skill, model={args.model})...\n")

    results = run_all(model=args.model, delay=args.delay, evals=subset)

    out_path = RESULTS_DIR / f"run_live_{args.model}.json"
    # merge with any prior run
    if out_path.exists():
        prior = json.loads(out_path.read_text())
        prior["evals"].update(results["evals"])
        results = prior
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
