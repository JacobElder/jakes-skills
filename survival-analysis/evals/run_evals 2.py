"""
Run survival-analysis skill evals against the claude CLI.

Two conditions per runnable eval:
  baseline   -- claude -p "<prompt>"
  with_skill -- claude -p "<prompt>" --append-system-prompt "<SKILL.md + all refs>"

Multi-turn evals (G) are analytical only and not run here.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────────
REPO = Path(__file__).parent.parent
SKILL_MD = (REPO / "SKILL.md").read_text()
REF_DIR = REPO

REF_FILES = {
    "r-recipes.md":              (REF_DIR / "r-recipes.md").read_text(),
    "python-recipes.md":         (REF_DIR / "python-recipes.md").read_text(),
    "estimators.md":             (REF_DIR / "estimators.md").read_text(),
    "cox-and-extensions.md":     (REF_DIR / "cox-and-extensions.md").read_text(),
    "parametric-and-aft.md":     (REF_DIR / "parametric-and-aft.md").read_text(),
    "nonproportional.md":        (REF_DIR / "nonproportional.md").read_text(),
    "competing-risks.md":        (REF_DIR / "competing-risks.md").read_text(),
    "recurrent-events.md":       (REF_DIR / "recurrent-events.md").read_text(),
    "multistate-frailty.md":     (REF_DIR / "multistate-frailty.md").read_text(),
    "special-censoring.md":      (REF_DIR / "special-censoring.md").read_text(),
    "pitfalls-and-diagnostics.md": (REF_DIR / "pitfalls-and-diagnostics.md").read_text(),
    "synthetic-data.md":         (REF_DIR / "synthetic-data.md").read_text(),
}

ALL_REFS = "\n\n---\n\n".join(
    f"# {name}\n{content}" for name, content in REF_FILES.items()
)

SKILL_WITH_REFS = SKILL_MD + "\n\n" + ALL_REFS


# ── eval definitions ──────────────────────────────────────────────────────────
import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent))
from eval_harness import EVALS, score_response

RUNNABLE = [e for e in EVALS if e.category != "multi-turn"]


# ── runner ────────────────────────────────────────────────────────────────────
def call_claude(prompt: str, system_extra: str | None = None,
                model: str = "haiku") -> str:
    cmd = ["claude", "-p", prompt,
           "--model", model,
           "--dangerously-skip-permissions"]
    if system_extra:
        cmd += ["--append-system-prompt", system_extra]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout.strip()


def run_all(model: str = "haiku", delay: float = 30.0,
            evals: list | None = None) -> dict:
    evals = RUNNABLE if evals is None else evals
    results = {"model": model, "evals": {}}
    total = len(evals)
    for i, ev in enumerate(evals, 1):
        print(f"  [{i}/{total}] {ev.id} ({ev.category})...", end=" ", flush=True)

        base_resp  = call_claude(ev.prompt, system_extra=None, model=model)
        time.sleep(delay)

        skill_resp = call_claude(ev.prompt, system_extra=SKILL_MD, model=model)
        time.sleep(delay)

        base_score  = score_response(ev, base_resp)
        skill_score = score_response(ev, skill_resp)

        results["evals"][ev.id] = {
            "category": ev.category,
            "prompt":   ev.prompt,
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
    ap.add_argument("--delay", type=float, default=4.0)
    ap.add_argument("--ids", nargs="*",
                    help="Run only specific eval IDs, e.g. A1 B1 F3")
    args = ap.parse_args()

    subset = [e for e in RUNNABLE
              if not args.ids or e.id in args.ids]

    if not subset:
        print(f"No runnable evals matched {args.ids}. "
              f"Runnable IDs: {[e.id for e in RUNNABLE]}")
        sys.exit(0)

    print(f"\nRunning {len(subset)} evals "
          f"(baseline vs with-skill, model={args.model})...\n")

    results = run_all(model=args.model, delay=args.delay, evals=subset)

    RESULTS_DIR = Path(__file__).parent / "results"
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"run_live_{args.model}.json"
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
