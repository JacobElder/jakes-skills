# Eval Psychometrics Skill

A skill that treats an eval suite as a *psychometric instrument* and audits it — diagnosing which items carry signal, which are dead weight, how reliable the whole thing is, and how confidently you can act on a delta between versions. It gives the agent the conviction to push back on the most common failure: reading a pass rate and calling it a measurement.

**The one idea:** A pass rate is a measurement, not *the* measurement. The mean hides whether items actually separate strong runs from weak ones, whether the suite is saturated, whether the grader is trustworthy, and whether a score moved because the system improved or because you reran the dice.

The skill has a strong point of view. It routes to the right method by regime — CTT item analysis and G-theory for small iteration suites (the default), IRT only when there are 30+ "takers" — and explicitly refuses to fit a free 2PL at small N while still delivering latent estimates the right way (hierarchical adaptive shrinkage or fixed-item anchoring). It gates on judge trust before any downstream number. It defers pure-method-theory questions (IRT, SDT derivations) to the dedicated skills for those domains, and focuses entirely on the eval-as-instrument workflow.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/eval-psychometrics
```

Or manually:

```bash
cp -r jakes-skills/eval-psychometrics ~/.claude/skills/eval-psychometrics
```

Once installed, the skill applies automatically whenever you ask about trimming an eval suite, diagnosing why a benchmark won't move, checking whether a delta is real, sizing seeds vs. cases, trusting an LLM grader, diagnosing trigger over/under-firing, or placing versions on a latent ability scale — even when you don't name a method.

---

## Example use cases

### "Which eval cases should I cut?"

> I have eval results for several versions of my agent skill across ~22 cases. I want to shrink this suite without losing signal. Which cases should I cut, and which must I keep?

Without the skill, the model reads the mean pass rate per case and recommends cutting the ones with the lowest variance:

> Cases where all or nearly all versions pass (like case_saturated with >90% pass rate) and cases where no version passes (floor items) contribute little to differentiating your versions. I'd suggest trimming these edge cases to keep the suite focused on the middle range where discrimination is highest.

With the skill, the model produces item-level structure, flags the urgency gradient, and raises the guard-item exception:

> **Per-item CTT analysis:**
> - `case_inverted`: item–rest correlation **−0.31** → this is a broken item. Versions that score better overall are *more likely to fail* this case — a gold-label error or perverse rubric. Fix this urgently; do not trim.
> - `case_saturated`: difficulty 0.96, discrimination ≈ 0 → trim for efficiency — unless it guards against a known regression. A saturated item that tests a behavior you've seen break before is insurance, not dead weight.
> - `case_noise`: item–rest ≈ 0.04 → non-discriminating. Safe to cut.
> - `case_dupe00`: r = 0.92 correlation with `case_01` → redundant. Keep one, trim the other.
>
> At N = 10 takers × 3 seeds, treat these as hypotheses rather than conclusions — confidence intervals on item–rest correlations are wide. Pre-commit the trim thresholds before acting.

---

### "My two versions score 78% vs. 80% — is the newer one better or is that noise?"

> I have 6 versions × 15 cases × 3 seeds. The two newest score 78% and 80%. Is the delta real?

Without the skill, the model reads the 2-point gap and qualifies it informally:

> A 2-point difference across 15 cases is quite small. With only 6 versions, you don't have a lot of statistical power. I'd recommend running more seeds to reduce noise, or using a t-test if you want a formal test of significance.

With the skill, the model routes to G-theory and frames the delta against reliability:

> You're in the small-N iteration regime. The right question is not "is 80% > 78%?" but "is the version-level signal larger than the measurement noise?" — which is what the G-coefficient answers.
>
> A G-study on this design decomposes variance into version effects, case-selection noise (version×item interaction), seed noise, and residual. A 2-point move is within the noise floor for almost any plausible G-coefficient at 15 cases × 3 seeds. **A delta without a dependability coefficient is a vibe.**
>
> Run `scripts/gtheory_eval.py` to get Eρ² and then a D-study: how many cases and seeds would you need to detect a 2pp version difference reliably? The answer is almost always "more cases" — the version×item interaction typically dominates, so doubling seeds barely moves the G-coefficient while adding 10 cases does. Do not fit a free 2PL to 6 versions; G-theory + CTT is the right tool here.

---

### "My skill over-fires on off-topic queries — how do I measure that?"

> My skill fires on queries it shouldn't. I have trigger eval data (in_scope, fired columns). How do I figure out whether the description needs a content rewrite or just needs to be made less eager?

Without the skill, the model reaches for accuracy and F1:

> Calculate precision (of the items that triggered, how many were in-scope?) and recall (of in-scope items, how many triggered?). If precision is low, the skill is triggering on too many out-of-scope items. You could add negative examples or more restrictive language to the description to reduce false triggers.

With the skill, the model routes to SDT and separates the two failure modes:

> Trigger analysis is a binary detection problem. Raw accuracy conflates two very different failures that need different fixes.
>
> From your data: compute hit rate (fired on in-scope) and false-alarm rate (fired on out-of-scope), then:
> - **d' (discriminability):** measures whether the description can actually tell relevant from irrelevant queries. Low d' means the content is too vague — rewrite the description to name specific trigger phrases, task types, or domain signals more precisely.
> - **Criterion (c):** measures eagerness. A liberal criterion means the skill fires at low evidence (over-fires). Tune the tone of the description: "Use whenever…" sets a liberal criterion; "Use only when the user explicitly asks for X" sets a conservative one.
>
> These are independent. A skill can have good discriminability and a bad criterion (it knows what it's for, it's just too eager), or poor discriminability (the description is so broad it can't tell in from out). Precision/F1 collapse them — d' keeps them separate. Apply log-linear correction for extreme rates before computing z-scores.

---

### "kappa = 0.72 with my human rater — I'm good to proceed, right?"

> My LLM grader has kappa = 0.72 with my human reference rater. The judge also outputs confidence scores and usually gives 0.90–0.98 even on cases where it later turns out to disagree with the human.

Without the skill, the model reads kappa as the judgment:

> kappa = 0.72 falls in the substantial agreement range (Landis & Koch scale), which is considered good inter-rater reliability. You can reasonably proceed with your analysis. The high confidence scores are also encouraging.

With the skill, the model separates reliability from calibration as two distinct gates:

> Reliability and calibration are two separate checks — kappa clears the first; you haven't run the second.
>
> **Reliability gate (kappa):** κ = 0.72 is substantial agreement. Gate passes.
>
> **Calibration gate (ECE/Brier):** Your confidence scores (0.90–0.98) are almost certainly miscalibrated. LLM judges are systematically overconfident — high stated confidence, poor empirical accuracy. If the judge states 0.95 confidence on cases where it disagrees with your human rater at a non-trivial rate, the stated confidence is not tracking actual accuracy. Compute Expected Calibration Error (ECE) or Brier score against your human reference. If ECE is high, either apply Platt/temperature scaling to recalibrate, or discard the confidence outputs and use binary labels only.
>
> The downstream effect of overconfidence: your pass-rate uncertainty estimates will appear far tighter than they actually are. You'll think your measurements are precise when they're not. Both gates must pass before trusting downstream analysis.

---

### "Can I use IRT on my 4 skill versions across 18 eval cases?"

> Walk me through fitting a 2PL model to get latent ability estimates for my 4 versions.

Without the skill, the model provides the fitting recipe:

> Sure — with 4 versions as "examinees" and 18 items, you can fit a 2PL using the `mirt` package in R or `py-irt` in Python. The key parameters are discrimination (a) and difficulty (b) per item, and ability (θ) per version...

With the skill, the model refuses the naive fit and offers the right remedies:

> A free 2PL on 4 takers will return confident-looking numbers that are noise. IRT item parameters (discrimination especially) are estimated across *takers* — you need roughly 200–500 takers for stable free-2PL estimates, not 4. With 4 versions, the discrimination parameter has essentially no data to be estimated from.
>
> The correct paths at small N — and you should still deliver latent estimates, just not via the naive fit:
> 1. **Fixed-item anchoring:** if you have pre-calibrated item parameters from a model bank (difficulty/discrimination for each case), fix those and estimate only the 4 version thetas against them. Well-posed at any N; this is `scripts/irt_latent.py --fixed-items`.
> 2. **Hierarchical Rasch (drop to 1PL):** set all discriminations to 1. Fewer parameters to estimate, more stable with few takers. `scripts/irt_latent.py --backend rasch`.
> 3. **Hierarchical 2PL with adaptive shrinkage (MCMC):** hierarchical priors regularize discrimination toward the group mean and relax as N grows. Returns honest, wide intervals. `scripts/irt_latent.py --backend mcmc`. This is the right tool when you want the full 2PL but need to be honest about uncertainty.
> 4. **G-theory + CTT:** skip IRT entirely and answer the reliability/sizing question with generalizability theory, which is well-posed at small N.
>
> Wide theta intervals on 4 versions are the truthful result — not a bug. The fix is expanding the taker dimension (add model tiers, ablations, seeds-as-takers) or anchoring on a calibrated bank.

---

## What the skill does

The base model knows the methods. The skill gives the agent the *conviction to apply the right ones in the right order* and to refuse the dangerous wrong ones. Its most important moves:

- **Route by regime before choosing a method.** The #1 eval failure is fitting a free 2PL to a handful of skill versions. The regime router (small-N iteration → G-theory + CTT; model bank → IRT; trigger analysis → SDT; grader trust → kappa first) runs before anything else.
- **Gate on judge trust.** If the grader isn't reliable AND calibrated, every downstream number is decoration. Kappa clears reliability; ECE/Brier clears calibration. These are two separate gates.
- **Report item-level structure, never just the mean.** Per-item difficulty + discrimination is the minimum output. A suite summarized by one number cannot be audited.
- **Refuse the naive free 2PL but still deliver estimates.** The refusal is targeted at the naive fit, not at latent estimation. Deliver hierarchical pooling with adaptive shrinkage (MCMC) or fixed-item anchoring — with honest wide intervals — rather than either handing over a 2PL recipe or refusing to help.
- **Treat triggering as signal detection.** Separate discriminability (d′ — content fix) from criterion bias (c — eagerness fix). Raw accuracy and F1 collapse the two.
- **Invoke D-study math, not intuition, for sizing decisions.** When version×item interaction dominates (the common case), cases are the high-leverage lever and seeds barely move the G-coefficient. Name the variance ratio; don't hedge.
- **Distinguish saturation from contamination.** Saturated items are non-informative but validity-clean (trim). Contaminated items violate the ICC — weak models pass at rates untethered from ability (outfit inflation, 3PL c > 0.15) — and pollute theta estimates. Audit and remove, don't just trim.

## Benchmark: skill vs. base model

Evaluated across 17 scenarios covering the full diagnostic workflow. Each eval has 3–5 specific, objectively checkable assertions graded strictly against evidence.

```
baseline  : 42/70 (60.0%) | 4/17 evals pass
with_skill: 70/70 (100.0%) | 17/17 evals pass
delta     : +40.0pp
```

### Results by eval

| # | Eval | Baseline | With skill | Delta |
|---|------|:---:|:---:|:---:|
| 1 | trim_decision_ctt | 2/5 | **5/5 ✓** | +60pp |
| 2 | is_the_delta_real_gtheory | 2/5 | **5/5 ✓** | +60pp |
| 3 | sigma_a_interpretation_trap | 1/4 | **4/4 ✓** | +75pp |
| 4 | triggering_sdt | 1/4 | **4/4 ✓** | +75pp |
| 5 | judge_trust_gate | 4/4 ✓ | **4/4 ✓** | 0pp |
| 6 | mutual_exclusion_routing | 1/3 | **3/3 ✓** | +67pp |
| 7 | latent_estimation_bank | 4/5 ✓ | **5/5 ✓** | +20pp |
| 8 | latent_estimation_small_n_done_right | 4/4 ✓ | **4/4 ✓** | 0pp |
| 9 | fixed_item_anchoring | 3/4 | **4/4 ✓** | +25pp |
| 10 | unified_glmm_feasibility | 1/4 | **4/4 ✓** | +75pp |
| 11 | synthesis_interpretation | 3/4 | **4/4 ✓** | +25pp |
| 12 | eval_content_drift | 3/4 | **4/4 ✓** | +25pp |
| 13 | facet_confounding | 3/4 | **4/4 ✓** | +25pp |
| 14 | judge_calibration_vs_reliability | 2/4 | **4/4 ✓** | +50pp |
| 15 | d_study_seed_vs_case_lever | 4/4 ✓ | **4/4 ✓** | 0pp |
| 16 | contamination_vs_saturation | 2/4 | **4/4 ✓** | +50pp |
| 17 | internal_consistency_wrong_construct | 2/4 | **4/4 ✓** | +50pp |

### Where the base model fails

| Eval | What the base model gets wrong |
|------|-------------------------------|
| sigma_a_interpretation_trap (3) | Interprets per-item discrimination point estimates as meaningful at 4 takers; misses that σ_a ≈ 0 means the model collapsed toward Rasch and individual a_i values are prior-driven artifacts |
| triggering_sdt (4) | Reaches for accuracy/precision/recall; doesn't compute d' and c or separate the content-fix from the eagerness-fix |
| mutual_exclusion_routing (6) | Tries to apply the eval-audit workflow to a pure-method-theory question instead of deferring to the dedicated skill |
| unified_glmm_feasibility (10) | Agrees to estimate a full multi-trait covariance at 6 variants; doesn't flag that this is prior-asserted, not data-estimated |
| judge_calibration_vs_reliability (14) | Reads kappa = 0.72 as sufficient to proceed; doesn't separate reliability from calibration or recommend computing ECE/Brier |
| contamination_vs_saturation (16) | Identifies the two failure modes conceptually but relies on pass rates; misses outfit statistics as the contamination diagnostic and misses that contaminated items pollute theta estimates |
| internal_consistency_wrong_construct (17) | Recommends alpha or omega as the reliability metric for a diverse eval suite; doesn't identify that internal consistency is the wrong construct |
| is_the_delta_real (2) | Suggests t-tests or "add more seeds"; doesn't route to G-theory or frame the delta against a dependability coefficient |

### Where the base model is partially right

| Eval | What helps | Missing |
|------|---|---|
| trim_decision_ctt (1) | Flags saturated and floor items | Misses the guard-item exception; doesn't flag negative-discrimination item as FIX (vs. trim) |
| synthesis_interpretation (11) | Synthesizes framework outputs in plain language; flags fit caution | Doesn't explicitly surface item-person targeting and pairwise separation as distinct insights |
| eval_content_drift (12) | Identifies the measurement-invariance framing | Doesn't recommend anchor/common-item linking for cross-run comparability |
| facet_confounding (13) | Identifies the confound; doesn't green-light the conclusion | Doesn't invoke facet/G-theory language or model judge/model/run as facets |

## What's inside

```
SKILL.md                              — skill hub; load this first
reference/
  01_diagnostic_workflow.md          — regime map and the trim/keep/fix decision rules
  02_ctt_item_analysis.md            — difficulty, discrimination, point-biserial, guard items
  03_generalizability_theory.md      — G-coefficient, D-study, variance decomposition
  04_irt_for_evals.md                — IRT for eval suites: contamination, saturation, model-bank requirement
  05_sdt_for_triggering.md           — trigger evals as detection: d', criterion, log-linear correction
  06_judge_calibration.md            — grader reliability (kappa) and calibration (Brier/ECE) — two gates
  07_small_sample_playbook.md        — why standard IRT breaks at small N; the full remedy menu
  08_latent_estimation.md            — hierarchical 2PL (MCMC), Rasch, fixed-item anchoring; honest intervals
  09_joint_glmm.md                   — one model emitting IRT + SDT + calibration + G-theory; small-N limits
  10_synthesis.md                    — plain-language read of all four frameworks; item–person map
  11_stan_backend.md                 — Stan/brms alternative to PyMC for the joint GLMM
  12_facets_and_confounding.md       — judge/base-model/run as facets; confounded designs
  13_item_drift.md                   — content drift and measurement invariance; anchor linking
scripts/
  eval_item_analysis.py              — CTT: difficulty, discrimination, flags, trim report
  gtheory_eval.py                    — variance components, Eρ²/Φ, D-study projection
  irt_eval.py                        — Rasch/2PL audit with small-N guard; fixed-item anchoring
  irt_latent.py                      — latent estimation: hierarchical 2PL (MCMC), Rasch, or anchored
  item_drift.py                      — content-hash drift detection; anchor set identification
  joint_glmm.py                      — unified GLMM engine (PyMC): IRT + SDT + calibration + G-theory
  judge_calibration.py               — kappa, agreement, Brier, ECE, reliability diagram
  sdt_trigger.py                     — d', criterion, A', log-linear correction, per skill
  synthesize.py                      — plain-language synthesis + multi-panel figure
evals/
  evals.json                         — 17 capability evals across the diagnostic workflow
  grader_prompt.md                   — strict assertion-grader instructions
  fixtures/                          — synthetic eval data for all fixture-based evals
```

## License

MIT
