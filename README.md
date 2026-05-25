# jakes-skills

A collection of domain-specific agent skills that give AI models the conviction and precision to apply specialized knowledge correctly — not just recall facts, but act on them under pressure.

Each skill ships with a `SKILL.md` (instructions loaded at runtime), curated `references/` files (pulled on demand), and an eval suite benchmarking skill vs. base model performance.

## Skills

| Skill | Domain | Benchmark improvement |
|---|---|---|
| [boglehead](#boglehead) | Personal investing | +24pp on original 10 scenarios |
| [causal-inference](#causal-inference) | Causal reasoning & experiment design | +19pp across 13 scenarios |
| [nilearn-fmri](#nilearn-fmri) | fMRI analysis with nilearn | +42pp across 8 scenarios |
| [psychometrics](#psychometrics) | Measurement theory & scale development | +97.5pp across 8 scenarios |
| [comp-modeling](#comp-modeling) | Computational & cognitive modeling | Eval suite included |

---

## boglehead

Apply the [Boglehead investing philosophy](https://www.bogleheads.org/) to any personal finance question. Covers asset allocation, fund selection, retirement accounts, tax-efficient placement, and the specific anti-patterns (whole life insurance, AUM advisors, dividend strategies, market timing) where Bogleheads diverge sharply from mainstream financial advice.

**Why it matters:** The base model knows Boglehead facts but gives hedged, balanced responses on the cases where the Boglehead position is actually clear. The skill gives the agent the conviction to push back on bad products, hold positions under pressure from authority figures, and walk through the full funding waterfall before answering the literal question.

**Gap:** +24pp on the original 10 scenarios, up to +60pp on the hardest cases (investment waterfall ordering, whole life rejection, dividend strategy debunking).

→ [boglehead/](boglehead/)

---

## causal-inference

Apply Pearl's framework for causal reasoning — the Ladder of Causation, DAGs, identification strategies, and the structural distinction between confounders, mediators, and colliders — to data analysis and experiment design questions.

**Why it matters:** The base model handles the structural mechanics of causal methods reliably. It struggles on identification edge cases: correctly characterizing what happens when an assumption fails, knowing the bias direction is *unknown* (not just upward) when an exclusion restriction is violated, and recognizing when the right answer is "disaggregate" vs. "don't" in a Simpson's paradox.

**Gap:** +19pp overall; up to +50pp on IV exclusion restriction violations, Simpson's paradox disambiguation, and the Table 2 Fallacy.

→ [causal-inference/](causal-inference/)

---

## nilearn-fmri

Run reproducible fMRI analyses with [nilearn](https://nilearn.github.io). Covers four workflows: first- and second-level GLM, functional connectivity, MVPA decoding, and brain visualization/reporting.

**Why it matters:** The base model handles standard first-level GLM well, but fails silently on the next-level workflows. The most dangerous failures produce plausible-looking but wrong outputs — a `NiftiMapsMasker` on a label atlas runs without error and returns a `(150, 1)` timeseries instead of `(150, 6)`, a display threshold gets reported as FDR correction, `detrend=True` produces a tSNR map of all zeros. The skill routes to the correct masker class, statistical inference APIs, and the `standardize='zscore_sample'` deprecation fix.

**Gap:** +42pp overall; up to +64pp on connectivity masker selection and second-level GLM model class.

→ [nilearn-fmri/](nilearn-fmri/)

---

## psychometrics

Apply rigorous measurement theory to surveys, scales, questionnaires, and latent-variable models. Covers scale development, reliability (alpha vs. omega), factor analysis (EFA vs. PCA, rotation choice, factor retention), CFA/SEM, IRT, and measurement invariance.

**Why it matters:** The base model fails on every psychometric trap — validates PCA as a subscale-finder, opens "Yes, alpha = 0.73 is adequate," calls `ICC = 0.72` moderate-to-good for a state measure (inverted logic), and skips construct definition to jump straight into pilot testing. The skill holds the methodologically correct position on all eight traps, including positions that require overriding what reviewers or advisors asked for.

**Gap:** +97.5pp — the largest gap in this collection. The base model scores near zero on the trap-based eval suite.

→ [psychometrics/](psychometrics/)

---

## comp-modeling

Fit generative process models of behavior — RL, prospect theory, drift-diffusion, category learning, delay discounting, Bayesian learning models — to trial-by-trial choice and RT data. Built around the methodological consensus of Daw (2011), Wilson & Collins (2019), Palminteri et al. (2017), and Lee & Wagenmakers (2014).

**Why it matters:** The skill enforces the simulate → recover → fit → compare → PPC workflow and flags the field-wide failure modes that separate publishable modeling from plausible-looking but unreliable results: parameter recovery before trusting estimates, model recovery before trusting comparisons, and the α/β identifiability trap that invalidates fits for subjects near the boundary.

→ [comp-modeling/](comp-modeling/)

---

## Installation

Each skill is self-contained. Install individually:

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/<skill-name>
```

Or manually copy to your skills directory:

```bash
git clone https://github.com/JacobElder/jakes-skills.git
cp -r jakes-skills/<skill-name> ~/.claude/skills/<skill-name>
```

Skills trigger automatically based on their `description` field — no manual invocation needed once installed.
