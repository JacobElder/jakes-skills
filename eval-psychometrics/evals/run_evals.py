"""
Eval runner for deep-eval-analysis skill.

For each eval in evals/evals.json:
  1. Get baseline response (no skill).
  2. Get with-skill response (SKILL.md + all reference files appended).
  3. Grade each assertion with a separate grader call.
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
EVALS_JSON = REPO / "evals" / "evals.json"

REF_NAMES = [
    "01_diagnostic_workflow.md",
    "02_ctt_item_analysis.md",
    "03_generalizability_theory.md",
    "04_irt_for_evals.md",
    "05_sdt_for_triggering.md",
    "06_judge_calibration.md",
    "07_small_sample_playbook.md",
    "08_latent_estimation.md",
    "09_joint_glmm.md",
    "10_synthesis.md",
    "11_stan_backend.md",
    "12_facets_and_confounding.md",
    "13_item_drift.md",
]
ref_parts = []
for name in REF_NAMES:
    p = REPO / "reference" / name
    if p.exists():
        ref_parts.append(f"# {name}\n{p.read_text()}")
REFS = "\n\n---\n\n".join(ref_parts)
SKILL_WITH_REFS = SKILL_MD + "\n\n---\n\n" + REFS

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

RATE_LIMIT_SENTINEL = "__RATE_LIMITED__"


def build_prompt(ev: dict) -> str:
    """Build executor prompt, appending any referenced fixture files inline."""
    prompt = ev["prompt"]
    files = ev.get("files", [])
    if files:
        prompt += "\n\n---\nFIXTURE DATA:\n"
        for rel_path in files:
            fpath = REPO / rel_path
            if fpath.exists():
                content = fpath.read_text()
                # Truncate large files to avoid context overflow
                if len(content) > 8000:
                    lines = content.splitlines()
                    content = "\n".join(lines[:120]) + f"\n... [{len(lines)} rows total, first 120 shown]"
                prompt += f"\n## {rel_path}\n```\n{content}\n```\n"
            else:
                prompt += f"\n## {rel_path}\n[file not found]\n"
    return prompt


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


GRADER_SYSTEM = """You are a strict grader for the deep-eval-analysis skill evals.

You will be shown:
1. The eval prompt (what the user asked).
2. The model response to grade.
3. A list of assertions — each a specific claim that should be true of a good answer.

For each assertion output one line: the assertion number followed by PASS or FAIL.
PASS = the response clearly and specifically demonstrates the expected behavior.
FAIL = it does not, or only gestures at it vaguely (partial credit = FAIL).

Domain-specific rules:
- "Refuses free 2PL at small N": PASS only if the output declines/strongly warns AND gives the reason (item params estimated across takers; ~hundreds needed). A caveat + recipe = FAIL.
- "σ_a ≈ 0 means cannot resolve discrimination" / "says colleague is WRONG": PASS only if both (a) σ_a is identified as the key signal that discrimination isn't resolvable AND (b) the response explicitly says the colleague is wrong / the a=2.1 estimate is not trustworthy. A hedge or "proceed with caution" = FAIL.
- "model collapses toward Rasch" / "collapses toward Rasch regardless": PASS if the response says EITHER (a) σ_a near 0 means the model is behaving like / collapsing toward Rasch (data-driven framing), OR (b) at N takers < ~8–15 the model will always collapse toward Rasch (structural framing). Both are correct statements of the same phenomenon.
- "Uses kappa not raw agreement": PASS if it names an agreement-beyond-chance statistic (Cohen's/Fleiss' kappa) as the reliability metric. Does not require an explanation of why raw agreement is inflated.
- "Separates low-d' from biased-criterion": PASS only if BOTH branches are present AND mapped to different fixes.
- "Reports item-level structure": PASS only if per-item difficulty AND a discrimination statistic are both produced or clearly described.
- "Mutual-exclusion routing": PASS if the output recognizes a pure-method-theory request and defers to the dedicated skill. FAIL if it invokes the eval-audit workflow for a derivation question.
- "Says advisor is wrong" / "does NOT clear the gate" / "does not green-light": these require an explicit negative statement, not a hedge or "proceed with caution."
- "Internal consistency wrong construct" / "does NOT recommend alpha or omega as primary": PASS only if the response explicitly says internal consistency is the wrong construct for diverse eval suites (not just a hedge like "alpha has limitations"). A response that recommends omega as the primary reliability metric = FAIL even if it also mentions G-theory.
- "tau-equivalence" (when IC is the secondary topic): PASS only if omega is named AND tau-equivalence is named as the violated assumption.
- "kappa clears reliability but NOT calibration; both required": PASS only if the response explicitly distinguishes the two gates AND says calibration (ECE/Brier) is a SEPARATE required check. A response that says "you can proceed" with binary labels while ignoring whether confidence calibration was checked = FAIL.
- "Recommends computing ECE or Brier score": PASS only if the response explicitly recommends computing ECE or Brier score on the confidence scores (not just "ignore the confidence scores" without first quantifying them).
- "Distinguishes triggering-SDT as a separate response process": PASS if the response EITHER (a) explicitly states that triggering / skill-firing is a separate response process from task-ability theta and should not be merged, OR (b) correctly characterizes the SDT output of the joint model as the IRT probit reading of task performance (sensitivity to ability differences) WITHOUT claiming it covers trigger-bias detection. FAIL only if the response claims the joint GLMM handles trigger-firing analysis or merges trigger discrimination into task-ability theta.
- "Names the specific failure mode: overconfident judge" / "downstream effect on pass-rate uncertainty": PASS only if BOTH (a) the response names the overconfidence pattern (high stated confidence vs. lower actual accuracy, e.g., 0.90+ stated but only ~70% correct) AND (b) names the downstream consequence — that pass-rate uncertainty estimates will appear artificially tight / more precise than they actually are. Recommending to ignore confidence scores WITHOUT naming this downstream precision illusion = FAIL.

Output format (nothing else, no extra text):
1: PASS
2: FAIL
3: PASS
"""


def grade_assertions(prompt: str, response: str, assertions: list[dict],
                     grader_model: str = "claude-haiku-4-5-20251001") -> list[bool] | None:
    if not response or response == RATE_LIMIT_SENTINEL:
        return [False] * len(assertions)
    texts = [a["text"] for a in assertions]
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    prompt_trunc = prompt[:500] + ("..." if len(prompt) > 500 else "")
    resp_trunc = response[:8000] + ("..." if len(response) > 8000 else "")
    grader_prompt = (
        f"Eval prompt:\n{prompt_trunc}\n\n"
        f"Model response to grade:\n\n{resp_trunc}\n\n"
        f"Assertions to evaluate:\n{numbered}"
    )
    raw = call_claude(grader_prompt, system_extra=GRADER_SYSTEM, model=grader_model)
    if not raw or raw == RATE_LIMIT_SENTINEL:
        return None
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
        delay: float = 15.0,
        executor_model: str = "claude-sonnet-4-6",
        grader_model: str = "claude-haiku-4-5-20251001") -> None:
    evals_data = json.loads(EVALS_JSON.read_text())["evals"]
    if eval_ids:
        evals_data = [e for e in evals_data if e["id"] in eval_ids]

    all_results = []

    for ev in evals_data:
        eid = ev["id"]
        base_prompt = build_prompt(ev)
        assertions = ev["assertions"]

        print(f"\n=== Eval {eid}: {ev['name']} ===")
        print(f"  {ev['prompt'][:80]}...")

        for condition in conditions:
            system = SKILL_WITH_REFS if condition == "with_skill" else None
            print(f"  [{condition}] executor...", end=" ", flush=True)
            response = call_claude(base_prompt, system_extra=system, model=executor_model,
                                   timeout=1200)
            time.sleep(delay)

            if not response or response == RATE_LIMIT_SENTINEL:
                print("RATE-LIMITED — skipping grading")
                continue

            print("grader...", end=" ", flush=True)
            passes = grade_assertions(base_prompt, response, assertions, grader_model=grader_model)
            time.sleep(delay)

            if passes is None:
                print("GRADER RATE-LIMITED — skipping")
                continue

            n_pass = sum(passes)
            n_total = len(assertions)
            pass_rate = n_pass / n_total if n_total else 0
            eval_passes = pass_rate >= 0.80

            status = "PASS" if eval_passes else "FAIL"
            print(f"{n_pass}/{n_total} [{status}]  {['+' if p else '-' for p in passes]}")

            result = {
                "eval_id": eid,
                "name": ev["name"],
                "condition": condition,
                "prompt": ev["prompt"],
                "response": response,
                "assertions": assertions,
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
        evals_pass = sum(1 for r in cond_results if r["eval_passes"])
        print(f"{condition:12s}: {total_p}/{total_a} assertions ({pct:.1f}%)  "
              f"| {evals_pass}/{len(cond_results)} evals pass")

    if len(conditions) == 2:
        b_pass = sum(r["passed"] for r in all_results if r["condition"] == "baseline")
        b_tot  = sum(r["total"]  for r in all_results if r["condition"] == "baseline")
        w_pass = sum(r["passed"] for r in all_results if r["condition"] == "with_skill")
        w_tot  = sum(r["total"]  for r in all_results if r["condition"] == "with_skill")
        if b_tot and w_tot:
            delta = 100 * w_pass / w_tot - 100 * b_pass / b_tot
            print(f"delta       : {delta:+.1f}pp")

    benchmark = {
        "skill_name": "deep-eval-analysis",
        "executor_model": executor_model,
        "grader_model": grader_model,
        "results": all_results,
        "summary": {
            cond: {
                "passed": sum(r["passed"] for r in all_results if r["condition"] == cond),
                "total":  sum(r["total"]  for r in all_results if r["condition"] == cond),
                "evals_pass": sum(1 for r in all_results
                                  if r["condition"] == cond and r["eval_passes"]),
                "evals_total": sum(1 for r in all_results if r["condition"] == cond),
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
