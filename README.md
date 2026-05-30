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
| [sequence-analysis-hmm](#sequence-analysis-hmm) | Hidden Markov Models & sequence analysis | +40pp across 10 content evals |
| [survival-analysis](#survival-analysis) | Time-to-event modeling (R & Python) | 26/26 analytically graded evals passing |
| [multilevel-modeling](#multilevel-modeling) | Hierarchical / mixed-effects modeling (R & Python) | Ceiling on iter-1; trap-based evals in iteration 2 |
| [network-analysis](#network-analysis) | Network science & social network analysis | +32.5pp across 8 trap-based evals |
| [psychometric-networks](#psychometric-networks) | Network approach to psychological measurement | +12.8pp across 8 scenarios (intersection skill) |

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

## sequence-analysis-hmm

Apply Hidden Markov Models and related sequence analysis techniques to problems with discrete latent structure. Covers three domains — bioinformatics (profile HMMs, HMMER, Pfam), time series (regime detection, anomaly detection, activity recognition), and NLP/speech (POS tagging, CRF comparison, ASR lineage) — plus the core algorithms (forward-backward, Viterbi, Baum-Welch) and the practical decisions that determine whether a model actually works.

**Why it matters:** The base model treats casual HMM questions as an invitation to enumerate subcomponents in bold bullets, produces single-restart fits (the most common source of bad HMM answers), and misses specific pitfalls like the geometric duration assumption by name. The skill enforces prose answers for conceptual questions, mandates multi-restart fitting with held-out validation, and redirects cleanly when a Kalman filter, CRF, or change-point method is the right tool instead.

**Gap:** +40pp on content evals (10/10 with skill vs. 6/10 base). Biggest wins on response formatting, code patterns, and pitfall diagnosis.

→ [sequence-analysis-hmm/](sequence-analysis-hmm/)

---

## survival-analysis

Apply survival analysis (time-to-event modeling) correctly in R and Python. Covers the full workflow from Kaplan-Meier and log-rank through Cox PH, parametric AFT, Royston-Parmar splines, competing risks (cause-specific Cox and Fine-Gray), recurrent events (Andersen-Gill, PWP), frailty, multi-state models, interval censoring, and left truncation.

**Why it matters:** The base model validates common errors rather than catching them. It accepts immortal-time-biased covariate definitions, treats competing events as censoring and reports 1−KM as cumulative incidence, follows up a crossing-curve KM with a standard log-rank test and reports "no significant difference," and returns `coxph` output as a real HR when complete separation makes the partial likelihood diverge. The skill names these errors by name and provides the specific fix — time-varying covariate for immortal time bias, Aalen-Johansen CIF and Fine-Gray for competing risks, MaxCombo or FH(0,1) for non-PH alternatives, Firth-penalized Cox for separation.

**Gap:** 26/26 analytically graded eval prompts passing across 7 categories (method selection, pitfall detection, code correctness, communication, R/Python consistency, adversarial cases, multi-turn coherence).

→ [survival-analysis/](survival-analysis/)

---

## multilevel-modeling

Apply hierarchical / multilevel / mixed-effects models correctly across the full analysis lifecycle — data-structure diagnosis, random-effects specification, contrast coding, fitting in R (lme4, lmerTest, glmmTMB, brms) and Python (statsmodels, bambi, PyMC), convergence troubleshooting, post-estimation, power analysis, and write-up.

**Why it matters:** The base model knows multilevel modeling but defaults to hedging on wrong analyses. The most consequential failure is validating or gently caveating a random-intercepts-only model when the design has within-cluster manipulations — an omission that inflates Type I error 2–5× at nominal α = .05 (Barr et al., 2013; Schielzeth & Forstmeier, 2009). The skill opens with a firm no on that case, enforces diagnosis before any simplification of singular models, and corrects the common reflex to recommend MLM for every repeated-measures question even when a paired t-test is the defensible answer.

**Gap:** Iteration 1 evals hit 100% for both configurations — a ceiling that reflects the base model's strong factual coverage when asked direct questions. The harder behavioral test (trap prompts where the user presents a wrong model as already done) is the planned iteration 2. Pattern matches the psychometrics skill: large deltas appear when the user is already satisfied with a flawed analysis, not when asking from scratch.

→ [multilevel-modeling/](multilevel-modeling/)

---

## network-analysis

Apply practitioner-grade methodology to network analysis, social network analysis (SNA), and graph problems. Covers bipartite projection, community detection, peer effects, ERGMs, temporal networks, centrality, large-scale tools, and GNN link prediction.

**Why it matters:** The base model knows network methods but validates common plans without flagging structural artifacts. The most dangerous defaults: calling a bipartite→projection→Louvain pipeline "standard and defensible" without naming SDSM/FDSM backbone extraction; treating Q = 0.67 as a reliability certificate and proceeding to name communities without stability analysis; naming IV generically for peer effects without identifying the Bramoullé friends-of-friends instrument that actually solves the cross-sectional identification problem; and treating static betweenness as informative about communication dynamics in a temporally aggregated network.

**Gap:** +32.5pp on 8 trap-based evals (100% with skill, 67.5% without). Largest wins on bipartite projection (+60pp), community stability (+60pp), and temporal aggregation (+60pp).

→ [network-analysis/](network-analysis/)

---

## psychometric-networks

Apply the network approach to psychological measurement — GGMs on questionnaire items and clinical symptoms using EBICglasso/bootnet/qgraph — with the field-specific conventions the base model underuses. An intersection skill: assumes psychometrics and network-analysis parent skills are loaded and adds only what is specific to these methods.

**Why it matters:** The base model gives solid general-purpose network and psychometrics answers but misses the field-specific layer: leading with `goldbricker` for node redundancy before estimation, applying CS-coefficient thresholds precisely (≥ 0.5 acceptable, ≥ 0.25 minimum, < 0.25 do not interpret), choosing Expected Influence over Strength for mixed-valence affect networks, naming Burger et al. (2023) as the authoritative reporting checklist, and framing causal limitations as a required element of any cross-sectional GGM write-up.

**Gap:** +12.8pp across 8 scenarios (97.4% with skill, 84.6% without). Largest gaps on node selection (+25pp), Expected Influence vs. Strength (+20pp), bootstrap CI vs. difference test (+20pp), and reporting standards (+20pp).

→ [psychometric-networks/](psychometric-networks/)

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
