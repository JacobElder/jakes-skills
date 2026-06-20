# jakes-skills Audit Synthesis & Roadmap

Synthesized from audits of 21/23 skills. The two unaudited skills (response-surface-analysis, psychometric-networks) are documented from development memory as high-quality with no critical issues.

---

## Section 1: Cross-Cutting Patterns

### 1.1 Stale or Incomplete benchmark.json (8 skills)

`benchmark.json` files are supposed to record the canonical final eval run, but in multiple skills they contain only a subset of results, a failed run, or an API error response — making benchmarks unreproducible and the deltas in READMEs and the global table unverifiable.

| Skill | Problem |
|---|---|
| clustering | Only eval 22's results — not the full 22-eval run |
| robust-statistics | Only eval_14's results — not the full 37-eval run |
| causal-inference | Only 5 with_skill result files exist; one explicitly fails; 0% trigger recall |
| nilearn-fmri | Root-level evals.json and evals/evals.json have diverged |
| eval-psychometrics | HANDOFF.md referenced but doesn't exist; benchmark claims non-matching counts |
| psychometrics | Iterations 3–7 eval files don't exist; benchmark unreproducible |
| agent-based-modeling | Eval 7 baseline invalid (tool timeout gave 0/5, inflating +29.8pp delta) |
| robust-statistics | eval_22_baseline.json is a 529 API error, not a model response |

**Fix pattern:** After every benchmark run, verify `len(results) == expected_n` before writing `benchmark.json`. Add a CI check or a `verify_benchmark.py` helper that counts entries and flags mismatches.

### 1.2 Missing .skill Package (5 skills)

The install path documented in every README depends on a `.skill` tarball, but five skills have no package file and are therefore uninstallable via the documented method.

| Skill | Status |
|---|---|
| causal-inference | No .skill file |
| experimental-design | No .skill file |
| preference-choice-modeling | No .skill file |
| network-analysis | No .skill file |
| survival-analysis | No .skill file (has SKILL.md but no package) |

**Fix:** Package each of these with `npx skills pack` or the equivalent and commit the resulting `.skill` file alongside `SKILL.md`.

### 1.3 Orphaned / Uncommitted Asset Files (7 skills)

Plots, scripts, and data files exist on disk but are either untracked by git, unreferenced in documentation, or both.

| Skill | Orphaned file(s) |
|---|---|
| boglehead | `fee_drag.png` (untracked, unreferenced) |
| applied-behavioral-design | `diagnosis_first.png` (untracked, not in README) |
| multilevel-modeling | `type1_error_inflation.png` (no generation script) |
| dimensionality-reduction | `evals.json` (9-eval old schema, orphaned alongside 43-eval harness) |
| idiographic-quant | `heterogeneity_analysis.R` (no documentation) |
| eval-psychometrics | `plot_joint_synthesis.py` (196-line script, not referenced anywhere) |
| agent-based-modeling | `sir_sobol_sa.py` (duplicates bundled scripts) |

**Fix pattern:** Either reference the file in README (for plots) or delete it. For generation scripts, add a one-line comment in README pointing to the script. Audit with `git status` before every release.

### 1.4 __pycache__ Committed to Repo (7 skills)

Seven skill directories have `__pycache__` committed to the repo, which pollutes diffs, leaks platform-specific bytecode, and is universally treated as a `.gitignore` pattern.

Affected: `agent-based-modeling`, `dimensionality-reduction`, `experimental-design`, `idiographic-quant`, `response-surface-analysis`, `sequence-analysis-hmm`, `signal-detection-theory`.

**Fix:** Add `**/__pycache__/` and `**/*.pyc` to `.gitignore` at the repo root, then `git rm -r --cached` on all committed `__pycache__` directories.

### 1.5 Incompatible Dual Eval Systems (4 skills)

Four skills have two eval files that use different schemas and different counts, making it impossible to know which is authoritative.

| Skill | System A | System B |
|---|---|---|
| idiographic-quant | `evals.json` (8 evals, assertions schema) | `eval_harness.py` (17 evals, keyword schema) |
| dimensionality-reduction | `evals.json` (9 evals, old schema) | `eval_harness.py` (43 evals) |
| comp-modeling | `evals.md` + `eval_harness.py` | `triggering.json` + `routing.json`/`workflow.json` |
| psychometrics | `psychometrics_behavior_evals.json` (8 evals) | README iteration table (claims 8 evals in iter-2 but they are different evals) |

**Fix pattern:** One authoritative eval file per skill. If an old schema file predates a rewrite, either migrate or delete it. The `eval_harness.py` runner is the more capable system in every case where both exist — archive the old JSON.

### 1.6 Eval Count Mismatches Between README and Actual Files (8 skills)

READMEs, EVALS.md files, and benchmark tables report eval counts that disagree with what is actually runnable.

| Skill | Claimed | Actual |
|---|---|---|
| boglehead | "19 scenarios" | 21 |
| experimental-design | "Seven tasks" | 9 |
| survey-design | 36 assertions | 35 in evals.json |
| robust-statistics | Category 1 includes survival analysis | No such eval exists |
| sequence-analysis-hmm | Docstring says 25 | 28 runnable |
| survival-analysis | README/EVALS.md say 26 | 29 runnable |
| signal-detection-theory | README: 52/42/+19.2pp | Actual: 58/46/+20.7pp (evals 15-16 added) |
| psychometrics | README trigger split 20/5 | Actual JSON: 19/6 |

**Fix pattern:** Automate count verification. After any eval addition, update the README and EVALS.md in the same commit. A `count_evals.py` utility would catch all of these.

### 1.7 Fiction References — Paths That Don't Exist (5 skills)

SKILL.md and reference files point to directories and scripts that don't exist in the repo, causing agents to silently fail when they try to load those resources.

| Skill | Broken reference |
|---|---|
| dimensionality-reduction | `references/` subdirectory (SKILL.md + validation-and-diagnostics.md) |
| dimensionality-reduction | `scripts/dr_diagnostics.py` (no `scripts/` dir) |
| multiverse-analysis | Hardcoded absolute paths in `scripts/multiverse_run.py`, `evals/dissertation_multiverse.py`, `evals/run_wellbeing_multiverse.py` |
| multilevel-modeling | "Mobile-friendly interactive question tool" (SKILL.md line 117) |
| survival-analysis | `SKILL_WITH_REFS` defined but never used in `run_evals.py` |
| causal-inference | `causal-inference-workspace/` dead link in README |
| agent-based-modeling | `forager_landscape.py` references non-existent ODD file |

**Fix pattern:** Before any commit, verify that every file path mentioned in SKILL.md and reference files resolves. Hardcoded absolute paths should be replaced with `Path(__file__).parent` relative resolution.

### 1.8 Missing Trigger Eval Files (9 skills)

Trigger evals verify the skill fires on relevant prompts and is silent on out-of-scope ones. Many skills have none, making trigger behavior unverified.

Skills with no trigger eval file: `multilevel-modeling`, `multiverse-analysis`, `network-analysis`, `nilearn-fmri`, `psychometrics`, `robust-statistics`, `signal-detection-theory`, `survey-design`, `survival-analysis`.

**Fix:** Each skill should have a `trigger_evals.json` with at least 10 positive and 5 negative cases, and a runner that reports recall and precision separately.

### 1.9 Policy Violations — "Claude" in Agent-Facing Files (1 confirmed, likely more)

`CLAUDE.md` requires agent-agnostic phrasing in all SKILL.md, README.md, and eval files. Psychometrics SKILL.md violates this (lines 8 and 14 use "Claude"). The pattern of writing these files prior to the CLAUDE.md policy encoding means other skills likely have instances.

**Fix:** Grep all SKILL.md files for the literal string "Claude" and replace with "the agent" or "the model". Run: `grep -rn "\bClaude\b" */SKILL.md`.

### 1.10 Citation and Attribution Errors (5 skills)

| Skill | Error |
|---|---|
| idiographic-quant | mlVAR citation misattributed to Haslbeck & Waldorp (2020) — that is the mgm package |
| multiverse-analysis | Sarma & Kay (2020) links to wrong paper |
| agent-based-modeling | ten Broeke year: 2014 vs. 2016 inconsistency |
| network-analysis | Traag et al. 2019 article number: 5233 vs. 5234 (correct: 5234) |
| network-analysis | Egami & Tchetgen: 2021 (preprint) vs. 2024 (publication) inconsistency |

### 1.11 Hardcoded API Model IDs (2 skills)

| Skill | Problem |
|---|---|
| robust-statistics | `grader_model = "claude-haiku-4-5-20251001"` (date-versioned ID goes stale) |
| (pattern) | Any other harness with date-versioned model strings will silently fail when the model is retired |

**Fix:** Use the non-dated alias (`claude-haiku-4-5`) or parameterize via environment variable.

---

## Section 2: Critical Bugs — Fix Immediately

Ordered by impact (crashes, wrong behavior, inflated benchmark numbers, policy violations).

### BUG-1: eval-psychometrics — Divergence Counting Always Returns Zero
**Skill:** eval-psychometrics
**Issue:** `run_cmdstanpy.py` contains `if False else 0` which always returns 0 divergences regardless of actual MCMC behavior. `run_rstan.R` hardcodes `divergences = 0`. The skill is supposed to diagnose divergence patterns — this makes it blind to the very problem it teaches.
**Fix:** Replace the dead branch with actual divergence extraction: `fit.diagnose()` output in CmdStanPy; `rstan::get_sampler_params()` in R.

### BUG-2: multiverse-analysis — KeyError Crash on Documented Example
**Skill:** multiverse-analysis
**Issue:** `multiverse.py` docstring example at lines 36–37 uses `c["model"]` as a dictionary key. The example decisions dict in the same docstring has no `"model"` key. Any user who copies this example will get a `KeyError` at runtime.
**Fix:** Align the docstring example keys with the actual example dict, or use `c.get("model", default)`.

### BUG-3: nilearn-fmri — Two Invalid API Arguments Will TypeError
**Skill:** nilearn-fmri
**Issue:** (a) `extract_connectome.py` line 171: `ConnectivityMeasure(standardize=...)` is not a valid parameter — this will raise `TypeError` on any nilearn version. (b) `datasets.md` line 211: `resample_to_img(..., copy_header=True)` is not a valid argument — will also `TypeError`.
**Fix:** (a) Remove `standardize` from `ConnectivityMeasure` constructor — standardization is handled at the masker level. (b) Remove `copy_header=True` from `resample_to_img` call.

### BUG-4: survival-analysis — sksurv API Returns Wrong Tuple Arity
**Skill:** survival-analysis
**Issue:** `estimators.md` documents `kaplan_meier_estimator` as returning a 3-tuple. The actual sksurv API returns a 2-tuple `(times, survival_probs)`. Any code copied from this reference will crash with `ValueError: too many values to unpack`.
**Fix:** Update `estimators.md` to unpack two values and verify against the current sksurv API.

### BUG-5: sequence-analysis-hmm — Baum-Welch Teaching Example Fails for T > ~100
**Skill:** sequence-analysis-hmm
**Issue:** `algorithms.md` mixes scaled forward probabilities with unscaled backward probabilities in the Baum-Welch step. This will produce numerical underflow (all zeros) for sequences longer than approximately 100 time steps. For a reference document used in teaching, this is a critical correctness error.
**Fix:** Either use fully scaled forward-backward throughout, or use log-space computations for both passes.

### BUG-6: dimensionality-reduction — Two Code Bugs in Shipped Scripts
**Skill:** dimensionality-reduction
**Issue:** (a) `pipeline_example.py`: `continuity_score` is computed identically to `trustworthiness_score` — wrong metric, silently returns the same number twice. (b) `efa_with_parallel_analysis.py`: uses covariance matrix eigenvalues instead of correlation matrix eigenvalues for parallel analysis. Parallel analysis is defined over the correlation matrix; the covariance version gives wrong retention decisions when variables have different scales.
**Fix:** (a) Implement the correct continuity formula (it is the transpose of trustworthiness). (b) Standardize or correlation-ize the matrix before computing eigenvalues in the PA routine.

### BUG-7: causal-inference — Eval Asserts Wrong Answer Is Correct
**Skill:** causal-inference
**Issue:** Eval 1, assertion 2 penalizes the correct answer. The rubric awards points for agreeing with an incorrect claim. This means the eval as written is measuring the wrong thing: a better model will score lower.
**Fix:** Audit the expected_output for eval 1 and invert the penalized assertion. Then re-run the benchmark — the reported +19pp gap is based on this corrupted eval.

### BUG-8: causal-inference — 0% Trigger Recall, Entire Skill Unfired
**Skill:** causal-inference
**Issue:** All 12 positive cases in `trigger_eval_results.json` have 0% recall. The skill's trigger description is not matching. Every benchmark number reported for causal-inference was generated with the skill potentially never loading.
**Fix:** Rewrite the skill description to match the actual prompts in the trigger eval set. Re-run the full benchmark after confirming triggers fire.

### BUG-9: nilearn-fmri — Hardcoded True Inflates E8 and E12 Baseline Scores
**Skill:** nilearn-fmri
**Issue:** `run_without_skill.py` line 485–486: two narrative checks hardcoded to `True` (should be `False`) for E8. Line 739: "Reports mean off-diagonal" hardcoded `True` for E12. This inflates the reported baseline, making the skill's measured delta smaller than it actually is. The +42pp headline number is an underestimate.
**Fix:** Set the hardcoded checks to `False`, re-run the baseline, update the benchmark and README.

### BUG-10: survival-analysis — R Robust SE Fix Is Wrong
**Skill:** survival-analysis
**Issue:** `recurrent-events.md` describes `robust=TRUE` as a `coxph()` argument in R for robust standard errors. This argument does not exist in the R `survival` package. The correct R idiom is to include `cluster(id)` in the formula. Any user who follows this reference will get an unrecognized argument error.
**Fix:** Replace `robust=TRUE` with the `cluster(id)` formula idiom in the R code examples.

### BUG-11: psychometrics — SKILL.md Uses "Claude" (Policy Violation)
**Skill:** psychometrics
**Issue:** SKILL.md lines 8 and 14 use "Claude" to refer to the model executing the skill, violating the agent-agnostic language policy in `CLAUDE.md`.
**Fix:** Replace both instances with "the agent" or "the model."

### BUG-12: nilearn-fmri — StratifiedKFold on Regression Task
**Skill:** nilearn-fmri
**Issue:** `scripts/run_decoder.py` uses `StratifiedKFold` for a regression decoding task. `StratifiedKFold` requires discrete class labels and will raise `ValueError` when given continuous targets. Regression decoding requires `KFold`.
**Fix:** Replace `StratifiedKFold` with `KFold` for continuous prediction targets.

---

## Section 3: Prioritized Fix Roadmap

### Tier 1: Systemic — Affect Multiple Skills

**T1-A: Repo-wide .gitignore for __pycache__**
One commit fixes 7 skills. Add `**/__pycache__/` and `**/*.pyc` to `.gitignore` at repo root, then `git rm -r --cached` on each committed `__pycache__`.

**T1-B: Benchmark count verification utility**
Write `tools/verify_benchmark.py`: reads a skill's `benchmark.json` and `eval_harness.py`, asserts `len(results) == expected_n`, flags API error responses, and prints a diff of what is missing. Run against all 21 audited skills and produce the first accurate global count table.

**T1-C: Policy compliance grep**
`grep -rn "\bClaude\b" */SKILL.md */README.md */evals*.json` and fix all hits. Add to pre-commit or CI. Confirmed hit: psychometrics/SKILL.md. Likely additional hits in older skills.

**T1-D: Package the 5 skills missing .skill files**
causal-inference, experimental-design, preference-choice-modeling, network-analysis, survival-analysis. Without these, the install path documented in the repo README is broken for nearly a quarter of the skills.

**T1-E: Resolve dual-eval-system conflicts**
idiographic-quant, dimensionality-reduction, comp-modeling, psychometrics each have two incompatible eval systems. In each case: designate `eval_harness.py` as authoritative, migrate any evals unique to the old JSON, delete or archive the stale file, and update the README count.

**T1-F: Replace all hardcoded absolute paths**
multiverse-analysis `scripts/multiverse_run.py`, `evals/dissertation_multiverse.py`, `evals/run_wellbeing_multiverse.py`. Pattern: replace `"/Users/..."` with `Path(__file__).parent / "..."`.

**T1-G: Replace date-versioned model IDs**
Grep for `claude-.*-\d{8}` in all `run_evals.py` and `eval_harness.py` files. Replace with non-dated aliases or `os.environ.get("GRADER_MODEL", "claude-haiku-4-5")`.

### Tier 2: Single-Skill Correctness Bugs

**T2-A: causal-inference** — Fix eval 1 assertion 2 (wrong answer penalized), fix trigger description for 0% recall, add `.skill` package, re-run the entire benchmark from scratch. The current benchmark numbers are not trustworthy. Priority: highest, because the skill is effectively undeployed (trigger never fires) and the benchmark is corrupted.

**T2-B: eval-psychometrics** — Fix divergence counting (`if False else 0` → actual extraction). Fix `run_rstan.R` hardcoded `divergences = 0`. Delete or create `HANDOFF.md`. Fix eval 6 grader contradiction. Move eval 13 to correct array position.

**T2-C: multiverse-analysis** — Fix `multiverse.py` docstring KeyError. Fix `Sarma & Kay` citation. Fix hardcoded paths (T1-F covers this). Add R-workflow eval.

**T2-D: nilearn-fmri** — Fix `ConnectivityMeasure(standardize=...)` TypeError. Fix `copy_header=True` TypeError. Fix `StratifiedKFold` on regression. Fix hardcoded True values in E8/E12 baseline grader. Reconcile root vs. evals/ JSON files. Re-run baseline after grader fix.

**T2-E: survival-analysis** — Fix sksurv 3-tuple to 2-tuple. Fix `robust=TRUE` R idiom to `cluster(id)`. Fix SKILL_WITH_REFS to actually load refs. Reconcile eval count (26 documented, 29 runnable). Update `--delay` default to ≥15.

**T2-F: dimensionality-reduction** — Fix `continuity_score` metric. Fix EFA parallel analysis to use correlation eigenvalues. Fix missing `references/` directory (either create or remove references to it). Fix `scripts/dr_diagnostics.py` path.

**T2-G: sequence-analysis-hmm** — Fix Baum-Welch forward-backward scaling mismatch in `algorithms.md`. Add deprecation note for `MultinomialHMM` in hmmlearn 0.3+. Add note that `sklearn-crfsuite` is unmaintained. Fix `fit_hmm_demo.py` RNG mixing.

**T2-H: idiographic-quant** — Fix Haslbeck & Waldorp citation (mlVAR vs. mgm). Fix E7 ordering in harness. Fix Mermaid chart baseline bars. Document or delete `heterogeneity_analysis.R`.

**T2-I: psychometrics** — Fix "Claude" policy violations in SKILL.md. Create missing iteration 3–7 eval files or update README to accurately describe what was actually run. Align README iteration table with actual `psychometrics_behavior_evals.json`.

**T2-J: network-analysis** — Fix `network_diagnostics.py` line 162 (PageRank is the fix, not the problem). Fix dead branch in `centrality_battery.py` lines 81–84. Fix Traag article number to 5234. Fix `.skill` package absence.

**T2-K: agent-based-modeling** — Fix ten Broeke year (verify and pick one). Investigate eval 7 timeout baseline — if invalid, re-run with a working tool call and update benchmark. Delete `__pycache__`. Fix or delete `forager_landscape.py` ODD reference.

**T2-L: clustering** — Fix Affinity Propagation taxonomy (not spectral). Fix `cluster_diagnostics.py` GMM covariance contradiction. Fix eval 18 rubric. Fix benchmark.json to contain all 22 evals.

**T2-M: signal-detection-theory** — Update README to 58/46/+20.7pp. Add `ln_beta` to `sdt.R`. Delete `__pycache__`.

**T2-N: boglehead** — Fix "19 scenarios" to "21 scenarios". Update mermaid chart to include scenarios 20–21. Resolve waterfall ordering inconsistency (pick one ordering across all files). Fix eval #4 internal contradiction. Create or remove reference to RESULTS.md.

**T2-O: multilevel-modeling** — Fix Python power simulation placeholder (remove ellipsis or implement). Add ICC guidance for GLMMs. Remove "mobile-friendly interactive question tool" reference. Add EMA/within-between centering eval (the largest documented gap).

**T2-P: applied-behavioral-design** — Elevate scarcity-population guidance to first-class stance in SKILL.md. Add heterogeneous/equity effects section. Reference or delete `diagnosis_first.png`. Merge or delete duplicate Gate 1 evals 15 and 18.

**T2-Q: comp-modeling** — Fix C15 rubric_keywords: remove "more iter" as a passing token for wrong Rhat fix. Resolve four-system eval conflict (T1-E). Fix C18 motivated-cognition contradiction. Fix C2 encoding fragility. Update evals.md to include C16–C23.

**T2-R: robust-statistics** — Fix benchmark.json to contain all 37 evals. Remove false survival analysis coverage claim. Fix eval_16 classification (it is differentiating). Re-run eval_22 (current result is an API error).

**T2-S: preference-choice-modeling** — Add IIA content to SKILL.md (advertised in README, absent in skill). Reconcile CBC sample-size assertion (800–1200 vs. 800 per segment = 1600). Move sparse MaxDiff co-occurrence balance from reference to SKILL.md. Add `.skill` package.

**T2-T: experimental-design** — Add `.skill` package. Fix README false claim about `power_analysis.py` runtime reporting. Fix evals.json description ("Seven tasks" → "Nine tasks"). Fix peeking false-positive rate inconsistency (pick one number across all files). Add factorial design eval.

### Tier 3: Stale Content, Eval Gaps, Documentation Improvements

- **boglehead**: Update 2024 contribution limits to 2026 values (IRS publishes annually).
- **multilevel-modeling**: Add REML vs. ML LRT eval. Add EMA/within-between centering eval.
- **network-analysis**: Add snowball sampling bias eval, SAOM vs. STERGM eval, power-law MLE eval.
- **signal-detection-theory**: Add m-AFC/triangle task eval. Add negative d'/label swap eval. Add GRT routing eval.
- **survival-analysis**: Add IPCW for dependent censoring. Add landmarking eval.
- **robust-statistics**: Add survival analysis eval and content. Add mediation analysis eval.
- **preference-choice-modeling**: Add SE formula disambiguation across SKILL.md and reference files.
- **nilearn-fmri**: Add `load_confounds_strategy` eval, `non_parametric_inference` eval, `MultiNiftiLabelsMasker` eval, beta-series/LSS decoding eval.
- **causal-inference**: Add M-bias eval. Add counterfactual/attribution eval (e.g., Shapley values in causal context).
- **survey-design**: Add demographic/identity question eval. Add mode effects eval. Add question order effects eval. Add trigger eval file. Add run_evals.py harness.
- **applied-behavioral-design**: Add theory-of-change/logic-model eval.
- **comp-modeling**: Add workflow.json runner.

---

## Section 4: Eval Suite Gaps — Cross-Skill

These gaps appear across multiple skills and represent systematically undertested territory.

### Gap A: Code that Runs but Produces Wrong Output (vs. Code that Crashes)
Most evals test whether the model gives correct conceptual guidance. Almost none test the subtler failure: code that executes without error but computes the wrong thing. Examples of this pattern found in audits: `continuity_score = trustworthiness_score` (dimensionality-reduction), scaled forward × unscaled backward (sequence-analysis-hmm), parallel analysis using covariance eigenvalues (dimensionality-reduction), StratifiedKFold on regression (nilearn-fmri). An "implementation correctness" eval category would test whether the model's code actually produces the right number, not just structurally correct-looking code.

### Gap B: Correct Advice + Immediate Compliance After Pushback
Many skills have a pushback eval (user disagrees with correct advice). Fewer test the follow-through scenario: the model gives correct pushback, the user says "I understand the concern but I need to proceed anyway," and the model either (a) correctly provides a guarded implementation or (b) incorrectly abandons the correct position. The survey-design skill is the only one with a dedicated pushback eval; it should become a standard eval category across all skills.

### Gap C: Bayesian Alternatives
Across computational and statistical skills, the base model treats frequentist and Bayesian approaches interchangeably without routing correctly. Almost no skills have a dedicated eval for: "when does Bayesian estimation materially change the recommendation?" Most relevant in: multilevel-modeling (brms vs. lme4 for small clusters), comp-modeling (hierarchical Bayes for individual differences), psychometrics (BSEM, Bayesian omega), signal-detection-theory (hierarchical SDT).

### Gap D: Software Version Handling
APIs change. Skills that reference code examples almost never include version guards or deprecation checks. The nilearn-fmri skill has the most acute version problem (multiple deprecated arguments), but the same issue exists for: `MultinomialHMM` in hmmlearn 0.3+ (sequence-analysis-hmm), `sklearn-crfsuite` (sequence-analysis-hmm), sksurv API arity (survival-analysis). No skill has an eval for: "what should the model do when the user is on an older package version than the reference code assumes?"

### Gap E: Reproducibility and Seed Setting
Most code examples in scripts and evals don't address reproducibility. Only one eval (comp-modeling) covers parameter recovery, which is the closest analogue. Missing eval type: "does the model set and document random seeds, control stochastic restarts, and explain which results are stochastic vs. deterministic?" Relevant in: clustering (k-means restarts), ABM (stochastic replication), sequence-analysis-hmm (multi-restart fitting), comp-modeling (parameter recovery), dimensionality-reduction (UMAP/t-SNE).

### Gap F: Multi-Turn Coherence and State Management
Almost all evals are single-turn. The boglehead skill has one multi-turn prompt but it is a description rather than actual turns. Real user sessions involve: the model giving advice, the user following up with "I tried that and got error X," the model integrating new information. No skill has a proper multi-turn eval with actual turn structure. This is the most important gap for deployment: skills need to hold their position across turns, integrate new evidence correctly, and not drift back to accommodating defaults.

### Gap G: Out-of-Scope Routing
Skills should correctly identify when a user's question falls outside their scope and route to a better skill. Almost no eval tests this. Idiographic-quant is the exception (has a nomothetic guard eval). A "negative case" category in every skill would test: "when user asks X, which is a Z question not a Y question, does the model route to Z rather than answering in the Y frame?"

### Gap H: Interaction Effects Between Skills
When multiple skills are loaded simultaneously (e.g., psychometrics + psychometric-networks), can they conflict? Do they produce redundant output? No evals exist for multi-skill loading scenarios. This is particularly relevant for intersection skills (psychometric-networks is explicitly designed to co-load with psychometrics and network-analysis).

### Gap I: Post-Estimation and Interpretation
Many skills cover model fitting but undertest the downstream step: interpreting output for a collaborator, reporting for a paper, or communicating uncertainty to a stakeholder. The multilevel-modeling and robust-statistics skills have some coverage here; others do not. Missing: "here is the model output, write the results paragraph" as an eval format.

### Gap J: Failure Mode Taxonomy Completeness
Looking across all skills, the failure mode taxonomies were developed through iterative evals (the skills with the highest deltas went through 4–7 iterations). Several skills still in iter-1 or iter-2 have taxonomies that likely miss large categories of base model errors. The idiographic-quant (+67pp), survey-design (+52pp), and eval-psychometrics (+40pp) gaps suggest the underlying base model failure rates are very high when failure modes are fully enumerated. Skills in the 15–25pp range (dimensionality-reduction +14pp, psychometric-networks +15.4pp, multilevel-modeling +13.7pp) likely have undiscovered failure modes that would push them much higher.

---

## Section 5: New Skill Ideas

### 5.1 Causal Machine Learning (causal-ml)
**Description:** Apply causal ML estimators — double ML, causal forests, X-learner, R-learner, T-learner, DML, synthetic DML — to heterogeneous treatment effect estimation and policy learning from observational data.

**Fit:** Extends the existing causal-inference skill into the ML/econometrics intersection. EconML and causalml are widely used but misapplied — users treat CATE estimates as valid without cross-fitting, apply single-learner S-learner to high-dimensional data, and confuse the propensity score nuisance model with the causal estimate.

**Estimated difficulty:** Medium-high. Failure modes are specific and well-documented in the EconML paper and Chernozhukov et al. (2018). The distinction between the nuisance models and the causal estimator is the single biggest conceptual gap.

**Key evals needed:**
1. "I fitted a causal forest and here are the CATE estimates — does this population heterogeneity mean some subgroups benefit?" (validate subgroup claims require honest uncertainty bounds, not point estimates)
2. "Should I use S-learner or T-learner for my 50-feature dataset?" (S-learner regularizes away treatment, T-learner explodes, X-learner or causal forest is right)
3. "My DML estimate changed when I swapped the ML learner for the outcome — does that mean it's wrong?" (cross-fitting sensitivity check, not a sign of bias)

---

### 5.2 Structural Equation Modeling (structural-equation-modeling)
**Description:** Specify, identify, fit, and interpret path models and latent variable SEM in lavaan and sem/semopy — including mediation, moderation, MIMIC, second-order factors, and the identification rules that determine whether a model is estimable.

**Fit:** SEM is one of the most commonly misused methods in behavioral and social science. The psychometrics skill handles CFA but explicitly does not cover full SEM path models. Existing failure modes: users fit just-identified models and report goodness of fit, confuse df=0 with df>0 fit tests, interpret indirect effects without bootstrapped CIs, and claim mediation from cross-sectional data. The base model almost always validates these.

**Estimated difficulty:** Medium. The identification rules (t-rule, two-step rule, rank condition) are well-scoped and teachable. The mediation vs. confounding distinction is the hardest conceptual piece.

**Key evals needed:**
1. "My CFI is 0.97 and RMSEA is 0.04, so my model fits well — can I interpret the path coefficients?" (check whether the model is just-identified, in which case fit indices are undefined)
2. "My indirect effect is significant at p < .05, so I have evidence of mediation" (requires bootstrap CI, not delta method; requires temporal ordering argument; requires ruling out confounders)
3. "My model has negative residual variances — should I fix them to zero?" (Heywood case — the model is misspecified, not just a numerical issue)

---

### 5.3 Bayesian Workflow (bayesian-workflow)
**Description:** Apply the full Bayesian workflow — prior predictive checks, fitting, posterior predictive checks, Pareto-k diagnostics, LOO-CV, MCMC diagnostics, and principled prior selection — in Stan, brms, PyMC, and NumPyro.

**Fit:** Several skills (multilevel-modeling, comp-modeling, eval-psychometrics) reference Bayesian methods but none own the Bayesian workflow as a first-class domain. The base model fits Stan models without prior checks, reports R̂ > 1.01 as "basically converged," and confuses LOO-CV's ELPD with in-sample fit. The Betancourt (2020) and Gelman et al. (2020) workflow papers provide the authoritative failure mode taxonomy.

**Estimated difficulty:** High. The failure mode space is large and highly interconnected (prior ↔ posterior ↔ predictive checks ↔ model comparison). Would require 25+ evals to cover. However, the payoff is proportionally large.

**Key evals needed:**
1. "My R̂ = 1.05 but the chains look visually mixed — can I proceed?" (no: R̂ > 1.01 with < 400 effective samples is not converged regardless of visual appearance)
2. "I used flat priors to be objective" (flat priors are not non-informative for bounded or scale parameters — prior predictive check would show this immediately)
3. "LOO-CV selected model A over model B by 2.3 ± 3.1 ELPD — model A is better" (the SE exceeds the difference; this is a tie; model A is not selected)

---

### 5.4 Text Analysis and NLP for Social Scientists (text-analysis-social-science)
**Description:** Apply quantitative text analysis methods — topic modeling (LDA, STM, BERTopic), text scaling (Wordfish, Wordscores), sentiment analysis, text embedding, and word embeddings — to social science research questions with appropriate validity checking.

**Fit:** Social scientists treat LDA topics as discovered latent variables and report them without coherence checks. They use off-the-shelf VADER sentiment for domain-specific texts. They interpret cosine similarity between embeddings as semantic proximity without accounting for frequency artifacts. No existing skill covers this territory.

**Estimated difficulty:** Medium. The failure modes are well-known in the computational social science literature (Chang et al. 2009 reading tea leaves, Garg et al. 2018 on embedding bias). The STM package's covariate-topic interaction is the most commonly misapplied method.

**Key evals needed:**
1. "My LDA topics have high coherence scores — are they valid?" (coherence scores correlate with topic usefulness but don't validate that topics correspond to real categories; human evaluation required)
2. "I want to measure political polarization using word embeddings" (requires controlling for frequency; requires temporal alignment if comparing across decades; requires validation against external measures)
3. "My STM shows that liberal documents use X topic more — is this causal?" (STM estimates are descriptive associations, not causal; the user needs a design argument or a quasi-experiment)

---

### 5.5 Missing Data Methods (missing-data)
**Description:** Handle missing data correctly — diagnosing the missing data mechanism (MCAR/MAR/MNAR), choosing between listwise deletion, multiple imputation (mice, Amelia), and full information maximum likelihood (FIML), and reporting uncertainty from imputation correctly.

**Fit:** Every quantitative skill touches missing data but none owns it. The base model defaults to listwise deletion or single imputation without diagnosing the mechanism. It confuses MCAR (deletion is unbiased) with MAR (deletion is biased but MI is consistent) and MNAR (neither is unbiased without additional modeling). The mice and Amelia R packages are widely used but the pooling rules (Rubin's rules) are almost never applied correctly.

**Estimated difficulty:** Medium-low. The MCAR/MAR/MNAR taxonomy is well-defined and the decision tree is compact. The most important failure modes: single imputation treated as equivalent to MI, Rubin's rules not applied when pooling results across imputed datasets, Little's MCAR test misinterpreted as definitive.

**Key evals needed:**
1. "I used mean imputation and then ran a regression — is this valid?" (no: mean imputation attenuates correlations and underestimates standard errors; MI or FIML required under MAR)
2. "Little's MCAR test was not significant, so I can do listwise deletion" (non-significant ≠ MCAR; the test has low power for realistic sample sizes and misses item-level missing patterns)
3. "I ran mice and got 5 imputed datasets — how do I get a single result?" (Rubin's rules: pool point estimates as mean, pool SEs using within + between imputation variance; do not just average p-values)

---

### 5.6 Mediation and Moderation Analysis (mediation-moderation)
**Description:** Apply mediation and moderation analysis correctly — PROCESS macro equivalents in R and Python, bootstrapped indirect effects, the Johnson-Neyman floodlight, index of moderated mediation, and the design requirements that separate causal mediation from descriptive decomposition.

**Fit:** Mediation is one of the most frequently performed and most frequently wrong analyses in behavioral science. The base model runs `mediate()` or PROCESS and reports indirect effects as causal. It does not flag the sequential ignorability assumption, does not distinguish mediation from confounding, and treats moderation as a post-hoc exercise. The multilevel-modeling and robust-statistics skills gesture toward this territory without owning it.

**Estimated difficulty:** Medium. The causal mediation framework (VanderWeele, Imai) is well-documented. The most important evals involve the distinction between descriptive decomposition and causal mediation.

**Key evals needed:**
1. "My indirect effect ab is significant (bootstrapped CI excludes zero) — I have evidence of mediation" (only under sequential ignorability; report the assumption, not just the test)
2. "The interaction is significant — where do I probe it?" (Johnson-Neyman floodlight for continuous × continuous is better than pick-a-point; model the entire region of significance)
3. "I want to do moderated mediation — do I need a bigger sample?" (yes; the index of moderated mediation requires ~ 4× the N of a simple indirect effect for comparable power)

---

### 5.7 Power Analysis and Sample Size Planning (power-and-sample-size)
**Description:** Plan sample sizes correctly for the full range of designs — two-group tests, ANOVA, mixed models, survival analysis, multilevel designs, equivalence tests — using simulation-based power when closed-form solutions don't exist or make unrealistic assumptions.

**Fit:** The experimental-design skill covers power for A/B tests, and the multilevel-modeling skill covers MLM power. Neither owns power analysis as a general domain. The base model uses G*Power rules of thumb for designs they don't apply to, ignores ICC when planning cluster-randomized trials, and never uses simulation when distributional assumptions are unclear.

**Estimated difficulty:** Medium-low. The failure modes are enumerable: wrong formula for design type, ignoring correlation structures, treating effect size as fixed when it is uncertain, not accounting for attrition. Simulation-based power is the authoritative answer for complex designs and is demonstrably teachable.

**Key evals needed:**
1. "I want 80% power for a 2×3 mixed ANOVA" (G*Power for repeated-measures ANOVA requires specifying the correlation among repeated measures, which the user almost never knows; simulation is better)
2. "I need to detect a 5pp difference in conversion rate — how many users per arm?" (requires specifying the baseline rate, the type I error, the one-vs-two-sided decision, and whether it's a proportion or a rate)
3. "My pilot study had d = 0.6 — should I use that for planning?" (pilot effect sizes are biased upward due to selection; shrink toward zero; report sensitivity curves not point power)

---

### 5.8 Item Response Theory in Practice (irt-applied)
**Description:** Apply IRT models correctly for test development, adaptive testing, score equating, and differential item functioning — including Rasch, 2PL, 3PL, graded response, and nominal response models — with practical guidance on sample size requirements and model fit evaluation.

**Fit:** The psychometrics skill covers IRT briefly. A dedicated IRT skill is warranted because IRT analysis has a specific set of failure modes that require their own coverage: fitting a 3PL to 200 examinees (unidentifiable), interpreting discrimination estimates without standard errors, equating test forms without anchor items, and reporting DIF without effect size thresholds. The eval-psychometrics skill explicitly defers "IRT only at model-bank scale (30+ takers)" — this is where a dedicated IRT skill would pick up.

**Estimated difficulty:** Medium-high. The model selection decisions (Rasch vs. 2PL vs. 3PL) are well-scoped. The adaptive testing routing is the hardest piece. DIF analysis via the Lord's chi-squared vs. Mantel-Haenszel distinction is teachable.

**Key evals needed:**
1. "I have 150 examinees and I want to fit a 3PL" (not enough data; 3PL requires 500+ per item; go to 2PL or Rasch)
2. "My person-fit index Lz is significant for 12% of examinees — what do I do?" (person misfit is expected at that rate under the null; use Ht or look at item-level response patterns)
3. "I want to report scores across two test versions — can I just compare raw scores?" (no; equating requires common items or common persons; otherwise you're comparing length in centimeters with length in inches)

---

### 5.9 Longitudinal Data Analysis (longitudinal)
**Description:** Analyze change over time correctly — distinguishing growth curve models, autoregressive models, cross-lagged panel models (and their critique), latent change score models, time series approaches, and the CLPM-vs-RI-CLPM distinction.

**Fit:** The multilevel-modeling skill covers growth curves. The idiographic-quant skill covers person-specific time series. Neither covers the intensive controversy around cross-lagged panel models (Hamaker et al., 2015; the random-intercept CLPM) or latent change score models (McArdle). This is one of the fastest-moving methodological debates in quantitative psychology and the base model is reliably wrong on it.

**Estimated difficulty:** High. The RI-CLPM vs. CLPM debate has no single correct answer — it depends on the theoretical model of stability. Evals would need to teach the base model to present the debate correctly rather than endorse one position.

**Key evals needed:**
1. "I ran a cross-lagged panel model and found that X at T1 predicts Y at T2 — does X cause Y?" (requires RI-CLPM reanalysis to rule out trait-level confounding; the CLPM conflates within-person dynamics with between-person differences)
2. "I want to model trajectories of depression across 4 time points — should I use an LGC or a latent change score model?" (LGC assumes linear change; LCS allows for self-feedback effects; pick based on substantive theory)
3. "My autoregressive coefficient at lag 1 is 0.7 — is my process stationary?" (check for unit root; |AR coefficient| < 1 is necessary but not sufficient for stationarity in multivariate systems)

---

### 5.10 Geospatial and Spatial Statistics (spatial-analysis)
**Description:** Apply spatial data methods correctly — spatial autocorrelation (Moran's I, LISA), spatial regression (spatial lag, spatial error, GWR), point process modeling (spatial randomness tests, kernel density), and the modifiable areal unit problem (MAUP).

**Fit:** No existing skill touches spatial methods. Geospatial analysis is widely used across social science, public health, ecology, and urban planning. The base model validates spatial regression without checking for spatial autocorrelation first, treats Moran's I as a model diagnostic without explaining what violation implies, and ignores MAUP when aggregating to administrative boundaries.

**Estimated difficulty:** Medium. The failure mode taxonomy is well-defined: Tobler's first law violation, ignoring MAUP, conflating spatial autocorrelation with spatial heterogeneity, extrapolating GWR coefficients beyond the observation window.

**Key evals needed:**
1. "I ran an OLS regression on county-level health outcomes — the residuals look fine visually" (visual inspection cannot detect spatial autocorrelation; run Moran's I on residuals first)
2. "My GWR model has locally varying coefficients — does that mean the effect of X on Y changes by location?" (only if the GWR bandwidth cross-validates better than a global model; GWR overfits badly with small N and wide bandwidth)
3. "I aggregated my data to ZIP codes for privacy — is that okay?" (MAUP: results will differ depending on the aggregation scheme; ZIP codes are not meaningful sociological units)

---

### 5.11 Reproducible Research Workflows (reproducible-research)
**Description:** Structure analysis code for reproducibility — project layout, dependency management, `renv`/`conda` environments, parameterized notebooks, Make/targets pipelines, pre-registration practice, and sharing standards (OSF, Zenodo, GitHub Actions).

**Fit:** Every quantitative skill produces code, but none addresses the workflow layer above the code: how do you ensure the analysis runs again in 6 months, on another machine, by another researcher? The base model never asks about this and rarely volunteers it. This crosses all skill domains and would increase the practical value of every other skill in the collection.

**Estimated difficulty:** Low-medium. The decisions are mostly rule-based (pin versions, use `renv`/`conda`, never write to data/, document in README.md). The hardest part is making the skill opinionated enough to be useful.

**Key evals needed:**
1. "Here is my analysis script — is it reproducible?" (check for: hardcoded paths, no seed, unlocked dependencies, raw data being modified in-place, absolute paths)
2. "Should I use Docker or renv for my R analysis?" (renv for R-only workflows; Docker only when system dependencies or non-R tools are required; most academic users are over-engineering)
3. "I want to share my data and code when I publish — what platform?" (OSF for data + preregistration + code; Zenodo for archival DOI; GitHub for versioned code; answer depends on field norms)

---

## Section 6: Future Directions for Existing Skills

### 6.1 causal-inference — Needs a Full Rebuild

This is the most broken skill in the collection. With 0% trigger recall and a corrupted benchmark (eval 1 assertion 2 wrong), the +19pp headline delta is not meaningful. Version 2 should:

1. Rebuild from trigger description first — get triggers firing before running content evals.
2. Add missing failure modes: M-bias (very common in SEM users who add controls), Placebo treatment tests for DiD, Synthetic Control vs. DiD choice, counterfactual attribution, LATE vs. ATE distinction.
3. Add a reference file on IV exclusion restriction violations with specific examples by domain.
4. Package the `.skill` file.
5. Target: 30 evals, 40+ pp delta (the current failure modes suggest a large gap is available once the benchmark is functional).

### 6.2 comp-modeling — Consolidate and Extend

Version 2 priorities:

1. Resolve the four incompatible eval systems into one.
2. Fix C15 rubric_keywords (false-pass for wrong Rhat fix).
3. Add C16–C23 to evals.md (they exist in the harness but not in the documentation).
4. Add a multi-turn eval: user gets a "Rhat > 1.01" error, agent advises correctly, user says "but my advisor says it's close enough," agent holds position.
5. Add a Python-specific MCMC workflow eval (the skill heavily skews R/Stan).

### 6.3 multilevel-modeling — Close the Three Major Gaps

Three specific gaps have large estimated deltas:

1. **EMA/within-between centering**: The user has daily diary data and asks whether to use a MLM. The skill should route through group-mean centering vs. grand-mean centering and the within-between RE specification. Estimated gap: +40pp or more.
2. **GLM-based random effects (GLMMs)**: ICC computation for binary outcomes (tau^2 / (tau^2 + pi^2/3) for logistic link). The skill does not cover this. Estimated gap: +30pp.
3. **REML vs. ML for LRT**: When comparing models with different fixed effects, REML is wrong — use ML. This is one of the most commonly made errors in lme4 workflows. Estimated gap: +20pp.

### 6.4 idiographic-quant — Fix Evals Before Extending

The eval system is the most broken of any high-performing skill (dual incompatible schemas, E7 ordering error, wrong Mermaid chart). Before adding any new content:

1. Consolidate to `eval_harness.py` as authoritative (17 evals).
2. Fix E7 ordering.
3. Fix Mermaid chart bars.
4. Fix Haslbeck citation.

After that, the skill has clear room to add: DFA vs. P-technique, unequal-spacing in ESM (continuous-time models), and DSEM with latent growth + VAR.

### 6.5 psychometrics — Reconstruct the Benchmark

The psychometrics skill has the highest single-skill delta in the collection (+97.5pp) but the benchmark is essentially unverifiable: iterations 3–7 (21 additional evals claimed in README) have no corresponding eval file. Version 2 should:

1. Reconstruct or clearly scope the benchmark to the 8 evals that actually exist.
2. Add IRT routing (currently deferred to eval-psychometrics) for the most common IRT questions.
3. Add measurement invariance (configural → metric → scalar) as a dedicated failure mode.
4. Fix the SKILL.md policy violations.

### 6.6 robust-statistics — Add Missing Domains

The skill's +38pp delta is real but the coverage gaps are large:

1. Add survival analysis content (Category 1 falsely claims this is covered).
2. Add mediation analysis content (one of the most commonly wrong analyses — until the mediation-moderation skill exists, robust-statistics should at least flag the Baron-Kenny procedure as insufficient).
3. Fix the stale `benchmark.json` and re-run a clean 37-eval pass.
4. Add a simulation-based illustration of the subgroup fallacy (the most important teaching case).

### 6.7 eval-psychometrics — Fix Infrastructure First

The divergence counting bug (always returns 0) is a fundamental problem for a skill that diagnoses MCMC quality. Fix this before any content expansion. Then:

1. Fix eval 6 grader contradiction.
2. Resolve `HANDOFF.md` references.
3. Add a dedicated calibration-vs-reliability confusion eval (currently the biggest gap in the field, per audit).
4. Add a contamination detection walkthrough eval (outfit inflation interpretation).

### 6.8 experimental-design — Run the Live Benchmark

The skill has never had a live benchmark run. After packaging the `.skill` file:

1. Run the full eval suite (9 task evals + 26 trigger evals).
2. Add the delta to the README and global table.
3. Add ratio-metric/delta-method eval (the most technically differentiating gap for A/B testing practitioners).
4. Add factorial design eval.
5. Fix the peeking false-positive rate inconsistency across files.

### 6.9 nilearn-fmri — Fix All API Bugs, Then Extend

The two invalid API arguments (`ConnectivityMeasure(standardize=...)` and `copy_header=True`) must be fixed before any user can trust the skill's code output. After that:

1. Fix the baseline grader hardcoded True values and re-run to get an honest delta.
2. Add `load_confounds_strategy` eval (the most commonly used confound removal function, currently untested).
3. Add beta-series/LSS decoding eval (the fastest-growing fMRI decoding paradigm).

### 6.10 survey-design — Add Infrastructure

The survey-design skill has excellent content (+52pp) but no eval runner and no trigger eval file. To make it a full-class skill:

1. Add `run_evals.py` harness compatible with the `eval_harness.py` pattern used by other skills.
2. Add trigger eval file (10 positive, 5 negative).
3. Fix the section cross-reference (§3 → §4).
4. Add demographic/identity question eval and mode effects eval.
5. Fix eval count discrepancy (README says 36, JSON has 35).

---

*This document was generated from audit findings on 21/23 skills in the jakes-skills repository. causal-inference requires the most urgent attention (infrastructure broken, benchmark untrustworthy). The cross-cutting fixes in Tier 1 (pycache cleanup, benchmark verification utility, policy compliance grep, .skill packaging) affect the largest number of skills and should be addressed first.*
