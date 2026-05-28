# Handoff prompt for Claude Code — psychometric-networks skill eval run

Copy everything below the line into Claude Code. Before sending, replace `<PATH>` with the path to your unzipped `psychometric-networks/` folder (containing `SKILL.md` and `evals/evals.json`).

---

I want you to run a full eval loop on a skill I've drafted: `psychometric-networks`. It covers the network approach to psychological measurement (GGMs on items, Ising on binary symptoms, graphicalVAR on ESM data, the Borsboom/Epskamp/Fried tradition). It's deliberately scoped to be mutually exclusive from my parent skills on general psychometrics and general network analysis — so this skill should only earn its keep on the *intersection* (field-specific estimators, bootnet stability culture, Strength/Expected Influence centrality conventions, the latent-vs-network debate, node-selection issues).

The skill and evals are at: `<PATH>`

There are 8 evals in `evals/evals.json`. Please use the skill-creator skill at `/mnt/skills/examples/skill-creator/` to orchestrate the workflow:

## What to do

1. **Read** `<PATH>/SKILL.md` and `<PATH>/evals/evals.json` so you understand what's being tested.

2. **Set up a workspace** as a sibling to the skill directory: `psychometric-networks-workspace/iteration-1/`, with one subdirectory per eval, each containing `with_skill/` and `without_skill/` subdirs.

3. **Run each eval in both configurations** — once with the skill loaded, once without. The evals are all conversational (no file outputs), so save the model's full response to `outputs/response.md` in each run directory. Run in parallel where you can; that's 8 × 2 = 16 runs.

4. **Grade each run** against the `expectations` array in evals.json. Follow the grader pattern in `/mnt/skills/examples/skill-creator/agents/grader.md`. Save per-run grading to `grading.json` with one entry per expectation: `{text, passed, evidence}`.

5. **Aggregate into a benchmark** using `/mnt/skills/examples/skill-creator/scripts/aggregate_benchmark.py`, then **open the eval viewer** at `/mnt/skills/examples/skill-creator/eval-viewer/viewer.html` so I can review side-by-side.

6. **Do an analyst pass** and report back with:
   - Per-eval pass-rate delta (with-skill vs without-skill)
   - Which expectations always pass regardless of skill (non-discriminating — wasted slots)
   - Which expectations always fail regardless of skill (skill not addressing them — possible gap)
   - Whether **eval 7 (negative trigger)** shows the desired *lack* of meaningful difference, or whether the skill is causing over-triggering
   - Whether **eval 8 (definitional baseline)** shows the desired with-skill improvement on the substantive framing points (#2 and #3 of its expectations) — that's the cleanest "does the skill teach something" signal
   - Any expectation wording that you found subjective or that pushed you toward inconsistent grading

7. **Report back before iterating.** Don't auto-rewrite. Show me the numbers, the viewer, and your observations; I'll decide whether to revise the skill, prune evals, or ship.

## Grading judgment — please follow these conventions

This is a research-methods skill, so a lot of expectations are about *substantive points* that can be made with or without specific citations. Default to scoring the idea, not the attribution:

- **When an expectation mentions a specific author or paper, the substantive point is what matters.** A response that makes the right argument without naming Epskamp or Bringmann should pass; one that name-drops without the substance should fail. The expectations have been written to reflect this — most say "OR makes the equivalent substantive point" — please honor that.

- **Eval 5 is the most numerically precise one.** The user provides CS-coefficients (0.36, 0.13, 0.05, 0.44) and the response must correctly apply the field thresholds (≥0.25 minimum to interpret; ≥0.5 acceptable). Grade strictly on whether the model assigns each centrality index to the right interpretability bucket — vague generic stability advice without applying the thresholds to these specific numbers should fail expectation 1.

- **Eval 7 (negative trigger) is a triggering-precision test.** A failure here is *over-triggering*: the with-skill response gets dragged into psychopathology talk instead of answering the generic graph-theory question. Pass if the response is a normal explanation of betweenness with at least one non-psychometric example; fail if symptom networks dominate the response. A brief side-note about the psychometric exception is fine and even a small positive.

- **Eval 8 (definitional baseline)** is where the with-skill response should show the clearest improvement on the conceptual framing — specifically expectations 2 and 3, where a no-skill answer is likely to call networks "a different visualization" rather than capturing the substantive common-cause-vs-direct-interaction claim. If the with-skill response also fails to make this distinction, that's a real problem with the skill, not the grading.

Go ahead and start.
