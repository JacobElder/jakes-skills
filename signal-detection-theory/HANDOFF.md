# Handoff → Claude Code: benchmark & iterate the `signal-detection-theory` skill

## What this is
A new agent skill teaching rigorous Signal Detection Theory, plus a 15-case eval set. It was researched and drafted in a Claude.ai session (deep research on Green & Swets / Macmillan & Creelman / Stanislaw & Todorov, the unequal-variance and meta-d' literatures, and current Python/R tooling, including the 2026 Cacioli LLM-SDT papers). The computational core is **bilingual and validated against analytic ground truth**: `scripts/sdt.py` (`scripts/test_sdt.py`, all passing — equal-variance reduction of d_a, the A_z identity, the probit-GLM identity, the delta-method SE of d' vs Monte-Carlo, ML recovery of the z-ROC slope) and `scripts/sdt.R`, which is cross-checked to produce **identical numbers**. What hasn't happened yet — because Claude.ai has no subagents — is the **parallel with-skill-vs-baseline benchmark**. That's your job.

## Skill location
```
signal-detection-theory/
├── SKILL.md                      # lean router + non-negotiable stances + anti-patterns
├── references/
│   ├── formulas.md               # measures, derivations, inference (SE/CI/tests), optimal criterion, effect-size bridge
│   ├── tasks.md                  # discrimination-task taxonomy (yes/no, mAFC, same-different, triangle, ...) + sensR routing
│   ├── estimation.md             # corrections, probit-GLM/GLMM, "is SDT redundant given GLM?", Bayesian, Python+R tooling
│   ├── metacognition.md          # type-2 SDT, meta-d', M-ratio, HMeta-d
│   ├── applications.md           # recognition memory, eyewitness ID, diagnostics/ML, LLM-SDT (Cacioli 2026)
│   └── pitfalls.md               # anti-patterns incl. pooling/Simpson's-paradox trap
├── scripts/
│   ├── sdt.py / sdt.R            # mutually cross-validated; sdt.py has a CLI + ML ROC fit
│   └── test_sdt.py               # analytic ground-truth tests
└── evals/evals.json              # 15 evals, each with assertions + baseline_failure_hypothesis
```

## Step 1 — sanity check
```bash
cd signal-detection-theory/scripts && python test_sdt.py   # expect ALL PASS / EXTENDED ALL PASS
Rscript sdt.R                                               # R self-check; numbers must match sdt.py
```
If anything fails (e.g., a numpy/scipy version quirk, or `np.trapezoid` vs `np.trapz`), fix the script, not the assertions. R needs `r-base-core` installed (`apt-get install -y --no-install-recommends r-base-core`); `sensR`/`brms` are only needed for the task-taxonomy and model-based paths, not the core self-check.

## Step 2 — run the harness (the part I couldn't do)
Use the skill-creator workflow. For **each** of the 10 evals in `evals/evals.json`, spawn **two subagents in the same turn**:
- **with-skill**: give it the skill path, the eval `prompt`, save to `signal-detection-theory-workspace/iteration-1/eval-<id>/with_skill/`.
- **baseline (no skill)**: same `prompt`, no skill, save to `.../without_skill/`.

This is a knowledge skill, so the failure modes are about *reasoning*, not file output — capture each subagent's full text answer. Then spawn a **grader subagent** that reads `agents/grader.md`, scores each `assertion` in `evals.json` against the saved answer (`passed` true/false + `evidence`), and writes `grading.json` per run. Aggregate with `python -m scripts.aggregate_benchmark signal-detection-theory-workspace/iteration-1 --skill-name signal-detection-theory` and open the eval viewer.

The interesting signal is the **delta**: each eval encodes a `baseline_failure_hypothesis` — the specific mistake a no-skill agent is expected to make (e.g., reading the vigilance hit-rate drop as a sensitivity loss; treating the diagnosticity ratio as accuracy; reporting single-point d' under unequal variance; endorsing the 0.99 substitution; gamma-as-metacognition; comparing 2AFC% to yes/no d' unconverted; shipping the more-liberal LLM prompt as "better"). The skill earns its keep only where baseline fails **and** with-skill passes. Pay special attention to:
- **eval 2** (d_a convention trap): baseline often reports single-point d'≈1.56 or the reciprocal-convention 1.47; correct is **d_a≈1.62**. This is the highest-value discriminator.
- **eval 7** (LLM classifier): baseline ships Prompt A on catch rate; correct answer is Prompt B is the better discriminator (d' 1.92 vs 1.51) and A is just more liberal.

## Step 3 — iterate, but PROTECT THE STRONG CLAIMS
Standard loop: read transcripts, find where with-skill still fails, patch the skill, rerun into `iteration-2/`. **Hard rule (do not break this):** the value of this skill is its *directional confidence*. Do **not** dilute the non-negotiable stances in SKILL.md into hedged "it depends" language during polish. If with-skill fails an eval, the fix is almost always **sharper routing or a clearer worked example**, not softening a claim. Specifically, keep intact:
- "Never collapse a discrimination task to one number" / always report sensitivity AND bias.
- The diagnosticity-ratio-is-bias-confounded stance.
- log-linear correction applied **uniformly**; reject ad-hoc 0.99 substitution.
- single-point d' is biased under unequal variance → d_a/A_z.
- A'/B''D are **not** assumption-free → prefer d_a or empirical AUC.
- two-step plug-in is weak → probit GLMM.
- meta-d'/M-ratio over confidence–accuracy correlation.
- the σ_noise/σ_signal d_a convention (must reduce to d' at s=1).
- report uncertainty on d' (SE/CI), never a d' from pooled cells or averaged rates.
- interpret c relative to the optimal criterion (base rates/payoffs), not relative to 0.

The genuine disagreements (UVSD vs DPSD; ROC vs full-lineup structure; equal- vs unequal-variance default) must stay presented **even-handedly** — don't let polish collapse those into a single "right" answer either.

## Step 4 — expand the eval set (most of the obvious gaps are now covered)
The 15 evals already span the core decomposition, diagnosticity confound, unequal-variance d_a, extreme cells, two-step/GLMM, metacognition, 2AFC conversion, LLM-classifier criterion-vs-capability, c-sign, A', a from-scratch analysis **with inference**, a sibling-routing **decline** (DDM/RT), the optimal-criterion/base-rate case, the AUC→d' equal-variance trap, and same-different task structure. Remaining additions worth making: (a) a rating-data eval that requires fitting the z-ROC and reporting d_a/A_z from confidence counts (exercises `fit_zroc_mle`); (b) a numeric meta-d'/M-ratio case if you wire up `metadpy`; (c) a triangle/tetrad sensory case to stress the `sensR` routing; (d) a multi-subject eval scored on whether the agent actually specifies the GLMM formula (random slopes for the within manipulation, by-subject and by-item). Keep the wrong-vs-right structure and verify any quantitative ground truth with the scripts.

## Step 5 — description optimization & packaging
Run the description optimizer (`run_loop.py`) on a fresh 20-query trigger set — include near-miss negatives that should route to the **ML-evaluation** skill (pure classifier threshold tuning, no latent-evidence framing), the **cognitive-modeling** skill (RT/DDM evidence accumulation), and the **psychometrics** skill (IRT item discrimination — the "discrimination" false friend). The current "When NOT to use this skill" block in SKILL.md encodes those boundaries; make sure triggering respects them. Then `package_skill.py` and you're done.

## Notes from the build
- Modern frontier worth keeping visible: SDT is increasingly applied to **LLM classifiers** (separating model discriminability from prompt/temperature/persona-induced criterion shifts). `applications.md` carries this; it's the most Jake-relevant extension and a good source of future evals.
- Tooling current as of the build: Python `metadpy` (Legrand) for SDT + (H)meta-d'; R `hmetad` package supersedes the MATLAB HMeta-d toolbox; `brms`/`sensR` for model-based SDT. Re-verify versions if much time has passed.
