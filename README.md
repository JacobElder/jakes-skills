# jakes-skills

A collection of domain-specific agent skills that give AI models the conviction and precision to apply specialized knowledge correctly — not just recall facts, but act on them under pressure.

Each skill ships with a `SKILL.md` (instructions loaded at runtime), curated `references/` files (pulled on demand), and an eval suite benchmarking skill vs. base model performance.

## Skills

| Skill | Domain | Benchmark improvement |
|---|---|---|
| [agent-based-modeling](#agent-based-modeling) | Agent-based simulation methodology (ODD, Mesa/NetLogo, verification, calibration) | +29.8pp (57/57 with skill, 40/57 base) |
| [applied-behavioral-design](#applied-behavioral-design) | Applied behavioral science diagnosis and intervention design (ideas42 workflow) | +32.5pp (83/83 with skill, 56/83 base) |
| [boglehead](#boglehead) | Personal investing | +24pp on original 10 scenarios |
| [causal-inference](#causal-inference) | Causal reasoning & experiment design | +19pp across 13 scenarios |
| [clustering](#clustering) | Cluster analysis: method selection, validation, mixed-type data | +17.9pp (95/95 with skill, 78/95 base) |
| [comp-modeling](#comp-modeling) | Computational & cognitive modeling | +30pp on content evals (23/23 with skill, 16/23 base); +33pp routing, +10pp triggering |
| [eval-psychometrics](#eval-psychometrics) | Eval-suite auditing: item analysis, reliability, latent estimation, judge calibration | +40.0pp (70/70 with skill, 42/70 base) |
| [dimensionality-reduction](#dimensionality-reduction) | PCA, EFA, t-SNE, UMAP, ICA, NMF and embedding validation | +14pp (43/43 with skill, 37/43 base); +33pp on pitfall traps |
| [experimental-design](#experimental-design) | Experimental and quasi-experimental design (A/B, RCT, power, DiD, RD) | 9 task evals + 26 trigger evals (live benchmark not yet run) |
| [idiographic-quant](#idiographic-quant) | Person-specific / N-of-1 quantitative methods (ESM/EMA, VAR networks, single-case experiments) | +65pp (17/17 with skill, 6/17 base) |
| [multilevel-modeling](#multilevel-modeling) | Hierarchical / mixed-effects modeling (R & Python) | +13.7pp across 16 trap-based evals (100% vs 86.2%); +80pp on singular-fit simplification, +60pp on growth curve time slopes |
| [multiverse-analysis](#multiverse-analysis) | Multiverse / specification-curve analysis | +21.9pp (32/32 with skill, 25/32 base) |
| [network-analysis](#network-analysis) | Network science & social network analysis | +32.5pp across 8 trap-based evals |
| [nilearn-fmri](#nilearn-fmri) | fMRI analysis with nilearn | +42pp across 8 scenarios |
| [preference-choice-modeling](#preference-choice-modeling) | MaxDiff and choice-based conjoint (CBC, ACBC, anchoring) | +44.8pp (29/29 with skill, 16/29 base) |
| [psychometric-networks](#psychometric-networks) | Network approach to psychological measurement | +15.4pp across 8 scenarios (intersection skill) |
| [psychometrics](#psychometrics) | Measurement theory & scale development | +97.5pp across 8 scenarios |
| [response-surface-analysis](#response-surface-analysis) | Congruence RSA (Edwards-Parry polynomial regression, a1–a5) | +31.8pp (66/66 with skill, 45/66 base) |
| [robust-statistics](#robust-statistics) | Applied statistical reasoning: estimands, fallacies, diagnostics, GLMs | +38pp overall (37/37 with skill, 23/37 base) |
| [sequence-analysis-hmm](#sequence-analysis-hmm) | Hidden Markov Models & sequence analysis | +40pp across 10 content evals |
| [signal-detection-theory](#signal-detection-theory) | Signal Detection Theory (d', ROC, meta-d', sensitivity vs. bias) | +20.7pp (58/58 with skill, 46/58 base) |
| [survey-design](#survey-design) | Survey & questionnaire design | +48.6pp across 6 evals (100% vs. 51.4%) |
| [survival-analysis](#survival-analysis) | Time-to-event modeling (R & Python) | +28pp (29/29 with skill, 21/29 base) |

---

## agent-based-modeling

Apply the full agent-based modeling lifecycle correctly — deciding when ABM is the right tool, designing and documenting models with ODD, implementing in Mesa/NetLogo/Agents.jl, verifying → calibrating → validating (in that order), running sensitivity analysis and replications, and interpreting results honestly.

**Why it matters:** The base model knows ABM concepts but validates sloppy practice. The most consequential failure modes: treating one stochastic replicate as a result, using OFAT sweeps to claim robustness, proceeding straight to calibration before verification, and conflating calibration fit with validation. The skill also corrects the assumption that LLM-driven generative agents improve ABM — they make validation harder, not easier. Bundled scripts (`replication_convergence.py`, `sensitivity_analysis.py`, Mesa Schelling template) give the agent actual tools rather than re-deriving computations per session.

**Gap:** +29.8pp — 57/57 with skill (100%) vs. 40/57 base (70.2%). Largest gains on stochastic-output reporting, the verification→calibration→validation distinction, and global sensitivity analysis.

→ [agent-based-modeling/](agent-based-modeling/)

---

## applied-behavioral-design

Apply ideas42-style applied behavioral science to problems where people aren't doing something they could do. Covers the full diagnostic workflow: sorting behavioral from structural constraints (Gate 1), mapping the decision-action path before designing anything (Gate 2), generating competing barrier hypotheses with evidence specs, designing interventions three ways (lower/eliminate the barrier, go around it, raise motivation), and holding incentive skepticism.

**Why it matters:** The base model knows behavioral concepts but is helpfully compliant — when a user arrives with a solution ("we need gamification," "just pay people"), it designs it. The skill enforces diagnosis before design, refuses to behavioralize structural constraints (transport cost, poverty, access), generates competing barrier hypotheses rather than crowning one bias, and raises crowding-out risks before designing incentive programs. It also routes test mechanics to the experimental-design skill rather than improvising sample sizes.

**Gap:** +32.5pp — 83/83 with skill (100%) vs. 56/83 base (67.5%). Largest gains on premature solutioning (+100pp), incentive skepticism (+100pp), and single-bias-guard (+100pp — generates competing hypotheses with evidence specs rather than naming one bias).

→ [applied-behavioral-design/](applied-behavioral-design/)

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

## clustering

Choose, apply, and validate clustering methods correctly — k-means, HDBSCAN, GMM/LPA, agglomerative, spectral, k-prototypes — including preprocessing, distance metric selection, mixed-type data, and the validation workflow that separates real structure from noise artifacts.

**Why it matters:** The base model knows clustering algorithms but validates single validation metrics and treats k-means as universally applicable. The skill enforces the null comparison (shuffled data should score worse — k-means always finds clusters on noise), the preprocessing dominance principle (the distance metric and scaling dominate results more than algorithm choice), HDBSCAN for variable-density data, Gower distance + k-medoids for mixed-type data rather than one-hot + k-means, and the LPA = GMM equivalence for continuous indicators.

**Gap:** +17.9pp — 95/95 with skill (100%) vs. 78/95 base (82.1%). Largest gains on k-selection validation (+60pp), non-convex shape handling (+50pp), mixed-type data (+50pp), and HDBSCAN deployment semantics (+50pp).

→ [clustering/](clustering/)

---

## comp-modeling

Fit generative process models of behavior — RL, prospect theory, drift-diffusion, category learning, delay discounting, Bayesian learning models — to trial-by-trial choice and RT data. Built around the methodological consensus of Daw (2011), Wilson & Collins (2019), Palminteri et al. (2017), and Lee & Wagenmakers (2014).

**Why it matters:** The skill enforces the simulate → recover → fit → compare → PPC workflow and flags the field-wide failure modes that separate publishable modeling from plausible-looking but unreliable results: parameter recovery before trusting estimates, model recovery before trusting comparisons, and the α/β identifiability trap that invalidates fits for subjects near the boundary.

**Gap:** +30pp on content evals — 23/23 with skill (100%) vs. 16/23 base (70%). Largest gains on fitting without recovery or baseline comparison (+100pp), boundary/identifiability traps, and model comparison reliability. Routing evals: +33pp; trigger evals: +10pp.

→ [comp-modeling/](comp-modeling/)

---

## eval-psychometrics

Treat an eval suite as a psychometric instrument and audit it — diagnosing which items carry signal, which are dead weight, how reliable the whole thing is, and how confidently you can act on a delta between versions. Routes by regime: CTT item analysis and G-theory for small iteration suites (the default, 2–8 skill versions), IRT only at model-bank scale (30+ takers), SDT for trigger/routing analysis, and judge calibration gating before any downstream number.

**Why it matters:** The base model reads a pass rate and treats it as a measurement. It fits a free 2PL to 6 versions and hands over discrimination estimates (which are prior noise at that N), recommends t-tests for a 2pp delta (the variance is mostly case-selection, not sampling error), and proceeds through a kappa = 0.72 judge as sufficient without checking whether the confidence scores are calibrated. The skill enforces the full audit chain: gate on judge trust first (kappa for binary reliability, ECE/Brier for calibration — two separate gates), route to G-theory to frame the delta against a dependability coefficient, report item-level structure not just the mean, refuse the naive free 2PL but still deliver latent estimates via hierarchical adaptive shrinkage. It also distinguishes saturation (non-informative but validity-clean — trim) from contamination (weak models pass at rates untethered from ability — outfit inflation pollutes theta — audit and remove).

**Gap:** +40.0pp — 70/70 with skill (100%) vs. 42/70 base (60.0%). Largest gains on regime routing (+75pp on sigma_a interpretation, unified GLMM feasibility), trigger analysis decomposition (+75pp), judge calibration vs. reliability distinction (+50pp), and contamination vs. saturation differentiation (+50pp).

→ [eval-psychometrics/](eval-psychometrics/)

---

## dimensionality-reduction

Choose, apply, validate, and interpret dimensionality reduction correctly — PCA, ICA, NMF, MDS, LDA/GDA, EFA, CFA, t-SNE, UMAP, PaCMAP, TriMap, PHATE, Isomap, LLE, autoencoders, and VAEs. The skill's core value is preventing the most consequential class of errors: misreading what an embedding is and isn't telling you.

**Why it matters:** The base model knows DR methods but validates the user's plan without catching structural errors. It reads t-SNE inter-cluster distances and blob sizes as findings (both are artifacts), agrees that "UMAP preserves global structure" means inter-cluster distances are reportable (they're not), runs CFA on the same data used for EFA and calls it confirmation (it isn't), and validates UMAP silhouette scores as evidence the embedding works (circular). The skill stops these before they become published findings, redirects PCA-as-EFA confusion, enforces quantitative validation over visual tuning, and ships a tested diagnostics script.

**Gap:** +14pp overall — 43/43 with skill (100%) vs. 37/43 base (86%) on haiku, across 6 automated categories. Pitfall category: +33pp (15/15 with skill vs. 10/15 base). Key differentiators: t-SNE distance+size misread, UMAP global structure overclaim, EFA→CFA double-dip, visual hyperparameter cherry-picking, circular embedding validation, kNN accuracy red flag.

→ [dimensionality-reduction/](dimensionality-reduction/)

---

## experimental-design

Design, critique, and size experiments correctly — A/B tests, RCTs, within-subjects, cluster-randomized, quasi-experiments (DiD, RD, ITS, synthetic control). Covers the five core principles (comparison, randomization, replication, local control, pre-specification) and the full power analysis workflow.

**Why it matters:** The skill carries a complete, self-contained power analysis script (`scripts/power_analysis.py`, no dependencies) that handles proportions, means, ratio-metric variance (delta method), and cluster designs with ICC — and gives runnable code rather than rules of thumb. It enforces pre-specification discipline, explains SRM and peeking problems in online experiments, distinguishes ITT from per-protocol, and is honest when a design can't support causal claims.

**Eval suite:** 9 task evals (A/B design, quasi-experiments, sample size, result interpretation, honest limits) + 26 trigger classification queries. Live API benchmark not yet run. `power_analysis.py` is fully tested via a unit suite (`scripts/test_power_analysis.py`).

→ [experimental-design/](experimental-design/)

---

## idiographic-quant

Apply person-specific quantitative methods to questions about variation within a single unit over time. Covers ESM/EMA data analysis, graphicalVAR and mlVAR person-specific networks, GIMME, P-technique factor analysis, DSEM, single-case experimental designs (ABAB, N-of-1), and the ergodicity argument for why group-level findings don't describe individuals.

**Why it matters:** The base model knows idiographic methods but defaults to complying with requests that can't work on the available data, applying group-level frameworks to individual-level questions, and recommending standard regression/MLM when person-specific temporal network methods are the right answer. The skill catches the underpowered-network request before any code is written, names the ergodicity trap when group coefficients are about to be applied to one client, and routes pooled-person-specific questions (mlVAR, GIMME) rather than defaulting to a random-slope mixed model that collapses the temporal structure. It also guards the other direction: when the question is genuinely about a population (A/B tests, group RCTs), the skill identifies it as nomothetic and says so.

**Gap:** +65pp — 17/17 with skill (100%) vs. 6/17 baseline (35%) on haiku. Differentiating on 11/17 evals: underpowered network pushback, ergodicity trap, single-case causal design, nomothetic guard, pooled person-specific routing, P-technique, ergodicity script use, N-of-1 trial design, DSEM for multi-item latent constructs, DFA vs. P-technique when autocorrelation is present, and continuous-time models for unequally-spaced ESM. The 6 evals the base model already passes (centrality trap, stationarity/theory tension, cross-night lag, Nickell bias, ESM protocol design, multiple baseline) serve as regression checks.

→ [idiographic-quant/](idiographic-quant/)

---

## multilevel-modeling

Apply hierarchical / multilevel / mixed-effects models correctly across the full analysis lifecycle — data-structure diagnosis, random-effects specification, contrast coding, fitting in R (lme4, lmerTest, glmmTMB, brms) and Python (statsmodels, bambi, PyMC), convergence troubleshooting, post-estimation, power analysis, and write-up.

**Why it matters:** The base model knows multilevel modeling but defaults to hedging on wrong analyses. The most consequential failure is validating or gently caveating a random-intercepts-only model when the design has within-cluster manipulations — an omission that inflates Type I error 2–5× at nominal α = .05 (Barr et al., 2013; Schielzeth & Forstmeier, 2009). The skill opens with a firm no on that case, enforces diagnosis before any simplification of singular models, and corrects the common reflex to recommend MLM for every repeated-measures question even when a paired t-test is the defensible answer.

**Gap:** +13.7pp across 16 trap-based evals (100% with skill, 86.2% without). Six evals discriminate: singular-fit simplification (+80pp — base model skips allFit() and upstream fixes, accepts iterative dropping), growth curve time slope (+60pp — validates advisor's "drop slope if variance ≈ 0" convention), convergence simplification with Bates et al. citation (+20pp), reviewer-requested cluster means (+20pp), CRSE vs. MLM cases (+20pp), and cluster RCT G*Power (+20pp). Ten evals show no gap — gaps appear when wrong practice is framed as established convention or backed by authority; the base model handles direct descriptions of wrong analyses correctly.

→ [multilevel-modeling/](multilevel-modeling/)

---

## multiverse-analysis

Perform multiverse / specification-curve analyses, not just describe them. The 7-step workflow: pin the estimand, elicit the decision grid, flag nonsensical cells, run every universe, describe the distribution, quantify which decisions drive variance, and do joint permutation inference.

**Why it matters:** The base model describes multiverse analysis well but treats it as a descriptive concept. The skill executes — using the bundled Python engine (`scripts/multiverse.py`, pandas/numpy/matplotlib only) or R's `multiverse`/`specr` packages — and enforces honest framing: a fragile finding is still a finding, a multiverse is not a tool for finding the "right" specification, and mixing DVs on different scales makes a specification curve meaningless.

**Gap:** +21.9pp — 32/32 with skill (100%) vs. 25/32 base (78.1%). Largest gains on scale-comparability warnings, binary DV constraint elicitation, and adversarial cherry-picking pushback.

→ [multiverse-analysis/](multiverse-analysis/)

---

## network-analysis

Apply practitioner-grade methodology to network analysis, social network analysis (SNA), and graph problems. Covers bipartite projection, community detection, peer effects, ERGMs, temporal networks, centrality, large-scale tools, and GNN link prediction.

**Why it matters:** The base model knows network methods but validates common plans without flagging structural artifacts. The most dangerous defaults: calling a bipartite→projection→Louvain pipeline "standard and defensible" without naming SDSM/FDSM backbone extraction; treating Q = 0.67 as a reliability certificate and proceeding to name communities without stability analysis; naming IV generically for peer effects without identifying the Bramoullé friends-of-friends instrument that actually solves the cross-sectional identification problem; and treating static betweenness as informative about communication dynamics in a temporally aggregated network.

**Gap:** +32.5pp on 8 trap-based evals (100% with skill, 67.5% without). Largest wins on bipartite projection (+60pp), community stability (+60pp), and temporal aggregation (+60pp).

→ [network-analysis/](network-analysis/)

---

## nilearn-fmri

Run reproducible fMRI analyses with [nilearn](https://nilearn.github.io). Covers four workflows: first- and second-level GLM, functional connectivity, MVPA decoding, and brain visualization/reporting.

**Why it matters:** The base model handles standard first-level GLM well, but fails silently on the next-level workflows. The most dangerous failures produce plausible-looking but wrong outputs — a `NiftiMapsMasker` on a label atlas runs without error and returns a `(150, 1)` timeseries instead of `(150, 6)`, a display threshold gets reported as FDR correction, `detrend=True` produces a tSNR map of all zeros. The skill routes to the correct masker class, statistical inference APIs, and the `standardize='zscore_sample'` deprecation fix.

**Gap:** +42pp overall; up to +64pp on connectivity masker selection and second-level GLM model class.

→ [nilearn-fmri/](nilearn-fmri/)

---

## preference-choice-modeling

Apply practitioner-grade methodology to MaxDiff and choice-based conjoint (CBC, ACBC, Menu-Based). Covers anchoring for absolute importance questions, sparse MaxDiff design, HB estimation, D-efficiency, alternative-specific design vs. prohibitions, cross-wave comparability, dual-response None, and sample size derivation from decision requirements rather than platform defaults.

**Why it matters:** The base model knows MaxDiff and CBC methods but validates common plan errors. It recommends prohibitions as "the standard approach" for unrealistic attribute combinations (alternative-specific design is better, with no D-efficiency cost and no confounding). It accepts z-score equating for cross-wave comparisons (anchored share-above-anchor is the only valid metric). It gives flat sample-size rules of thumb rather than deriving from required simulator precision on the smallest detectable share difference. The skill takes the opinionated practitioner position on all six documented traps.

**Gap:** +44.8pp — 29/29 with skill (100%) vs. 16/29 base (55.2%). Largest gains on prohibitions vs. alternative-specific design (+50pp), cross-wave comparability (+50pp), anchoring for absolute importance (+50pp), and subgroup sample size derivation (+50pp).

→ [preference-choice-modeling/](preference-choice-modeling/)

---

## psychometric-networks

Apply the network approach to psychological measurement — GGMs on questionnaire items and clinical symptoms using EBICglasso/bootnet/qgraph — with the field-specific conventions the base model underuses. An intersection skill: assumes psychometrics and network-analysis parent skills are loaded and adds only what is specific to these methods.

**Why it matters:** The base model gives solid general-purpose network and psychometrics answers but misses the field-specific layer: leading with `goldbricker` for node redundancy before estimation, applying CS-coefficient thresholds precisely (≥ 0.5 acceptable, ≥ 0.25 minimum, < 0.25 do not interpret), choosing Expected Influence over Strength for mixed-valence affect networks, naming Burger et al. (2023) as the authoritative reporting checklist, and framing causal limitations as a required element of any cross-sectional GGM write-up.

**Gap:** +15.4pp across 8 scenarios (100% with skill, 84.6% without). Largest gaps on node selection (+25pp), Expected Influence vs. Strength (+20pp), hairball diagnosis (+20pp), bootstrap CI vs. difference test (+20pp), and reporting standards (+20pp).

→ [psychometric-networks/](psychometric-networks/)

---

## psychometrics

Apply rigorous measurement theory to surveys, scales, questionnaires, and latent-variable models. Covers scale development, reliability (alpha vs. omega), factor analysis (EFA vs. PCA, rotation choice, factor retention), CFA/SEM, IRT, and measurement invariance.

**Why it matters:** The base model fails on every psychometric trap — validates PCA as a subscale-finder, opens "Yes, alpha = 0.73 is adequate," calls `ICC = 0.72` moderate-to-good for a state measure (inverted logic), and skips construct definition to jump straight into pilot testing. The skill holds the methodologically correct position on all eight traps, including positions that require overriding what reviewers or advisors asked for.

**Gap:** +97.5pp — the largest gap in this collection. The base model scores near zero on the trap-based eval suite.

→ [psychometrics/](psychometrics/)

---

## response-surface-analysis

Apply the Edwards & Parry (1993) / Humberg–Nestler–Back (2019) tradition of congruence RSA correctly — second-order polynomial regression, the C1–C4 conjunction checklist, a1–a5 surface parameters with bootstrap CIs, block-test gating, and the two documented fallacies (single-parameter and directionality). Explicitly scoped to *congruence modeling*, not design-of-experiments RSM.

**Why it matters:** The base model knows RSA vocabulary but validates plan errors without catching structural failures. It accepts a significant negative a4 as evidence of congruence (necessary but not sufficient — four conditions must hold simultaneously). It runs difference-score analyses without flagging the four untested constraints they impose. It interprets surfaces that failed their own block-test gate. It manufactures directional claims from symmetric surfaces (a3 ≈ 0, CI including 0) — the directionality fallacy. The skill holds the full checklist under pressure.

**Gap:** +31.8pp — 66/66 with skill (100%) vs. 45/66 base (68.2%). Largest gains on power planning simulation (+80pp), failed-gate refusal (+75pp), coefficient-fishing pushback (+60pp), and single-parameter fallacy (+50pp).

→ [response-surface-analysis/](response-surface-analysis/)

---

## robust-statistics

Reason about applied statistics the way an experienced methodologist does — starting from the estimand and what could go wrong for this specific goal, rather than running assumption tests and mapping them to a fixed procedure menu. Covers two-group comparisons, GLM selection, robust inference, missing data, and the inference fallacies that appear most often in practice.

**Why it matters:** The base model has strong statistical knowledge but defaults to assumption-policing ("Shapiro-Wilk rejected, so you can't use a t-test") and over-engineering. The skill corrects both: it rejects the difference-in-significance fallacy (separate p-values don't test whether effects differ), corrects "you must log-transform right-skewed data" as a universal rule, explains what Shapiro-Wilk actually tests vs. what inference requires, and stops when the simple method is adequate without appending alternatives that imply a problem that doesn't exist.

**Gap:** +38pp overall — 37/37 with skill (100%) vs. 23/37 base (62.2%). Largest gains on the subgroup comparison fallacy (+100pp), Lord's paradox/ANCOVA vs. change score (+80pp), and residual diagnostics (+40pp).

→ [robust-statistics/](robust-statistics/)

---

## sequence-analysis-hmm

Apply Hidden Markov Models and related sequence analysis techniques to problems with discrete latent structure. Covers three domains — bioinformatics (profile HMMs, HMMER, Pfam), time series (regime detection, anomaly detection, activity recognition), and NLP/speech (POS tagging, CRF comparison, ASR lineage) — plus the core algorithms (forward-backward, Viterbi, Baum-Welch) and the practical decisions that determine whether a model actually works.

**Why it matters:** The base model treats casual HMM questions as an invitation to enumerate subcomponents in bold bullets, produces single-restart fits (the most common source of bad HMM answers), and misses specific pitfalls like the geometric duration assumption by name. The skill enforces prose answers for conceptual questions, mandates multi-restart fitting with held-out validation, and redirects cleanly when a Kalman filter, CRF, or change-point method is the right tool instead.

**Gap:** +40pp on content evals (10/10 with skill vs. 6/10 base). Biggest wins on response formatting, code patterns, and pitfall diagnosis.

→ [sequence-analysis-hmm/](sequence-analysis-hmm/)

---

## signal-detection-theory

Apply Signal Detection Theory correctly to any two-class discrimination task — perception, recognition memory, eyewitness identification, medical diagnostics, LLM classifiers, vigilance. Separates sensitivity (d', d_a) from response bias (c, c_opt) and enforces the decomposition before any conclusion about "performance."

**Why it matters:** The base model knows SDT formulas but applies them without checking their assumptions and validates popular but flawed shorthand. It accepts the AUC→d' conversion without flagging the equal-variance assumption (recognition memory z-ROC slopes cluster at ≈ 0.8, not 1.0). It recommends gamma as a metacognition measure without routing to meta-d'. It reads the diagnosticity ratio (HR/FAR) as a sensitivity measure rather than a criterion-confounded ratio. It applies 2AFC d' to same-different tasks. The skill catches each of these before they become published findings.

**Gap:** +20.7pp — 58/58 with skill (100%) vs. 46/58 base (79.3%). Key differentiating evals: AUC→d' equal-variance trap (+67pp), same-different task structure (+67pp), rating-data z-ROC fitting (+67pp), metacognition routing to HMeta-d, and LLM classifier criterion vs. capability decomposition.

→ [signal-detection-theory/](signal-detection-theory/)

---

## survey-design

Design, review, and repair self-report surveys and questionnaires. Covers question wording, response format selection, scale construction, instrument assembly, response-bias mitigation, and the errors that originate at design time — before any data is collected.

**Why it matters:** The base model knows survey design facts but gives accommodating responses. When a user insists on a methodologically weak design, it validates the choices and provides formatting tips rather than explaining the data-quality cost. The skill gives the agent the conviction to explain the *specific* mechanism behind each design problem — the variance loss from a 2-point scale, the satisficing dynamic that causes "select all that apply" to undercount late items, the acquiescence inflation from agree/disagree batteries — and hold that position under pushback. It also enforces a clean boundary with psychometrics: questions about reliability coefficients, factor analysis, and IRT are handed off rather than improvised.

**Gap:** +48.6pp — 100% with skill vs. 51.4% base (35/35 assertions across 6 evals). Biggest gaps on the pushback eval (+83pp — base model validates user's bad choices; skill explains the data-quality cost and recommends the correct alternative) and the calibration eval (correctly avoids inventing flaws in a well-designed instrument).

→ [survey-design/](survey-design/)

---

## survival-analysis

Apply survival analysis (time-to-event modeling) correctly in R and Python. Covers the full workflow from Kaplan-Meier and log-rank through Cox PH, parametric AFT, Royston-Parmar splines, competing risks (cause-specific Cox and Fine-Gray), recurrent events (Andersen-Gill, PWP), frailty, multi-state models, interval censoring, and left truncation.

**Why it matters:** The base model validates common errors rather than catching them. It accepts immortal-time-biased covariate definitions, treats competing events as censoring and reports 1−KM as cumulative incidence, follows up a crossing-curve KM with a standard log-rank test and reports "no significant difference," and returns `coxph` output as a real HR when complete separation makes the partial likelihood diverge. The skill names these errors by name and provides the specific fix — time-varying covariate for immortal time bias, Aalen-Johansen CIF and Fine-Gray for competing risks, MaxCombo or FH(0,1) for non-PH alternatives, Firth-penalized Cox for separation.

**Gap:** +28pp — 29/29 with skill (100%) vs. 21/29 base (72%) on haiku, across 6 automated categories (method selection, pitfall detection, code correctness, communication, R/Python consistency, adversarial cases). Biggest gains on method selection (+80pp) and pitfall detection (+40pp).

→ [survival-analysis/](survival-analysis/)

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
