# Evals for the `comp-modeling` skill

These evals test that a model instance with this skill loaded behaves measurably better than a baseline model on computational/cognitive modeling questions. They're written to be run by hand and graded against the rubrics, or adapted to an automated harness.

There are three sections:

1. **Triggering evals** — does the skill fire when it should, and stay quiet when it shouldn't?
2. **Routing evals** — does Claude pull the *right* reference file(s) for the user's question?
3. **Content / workflow evals** — does Claude actually apply the workflow (simulate-recover-fit-compare-PPC) and flag the field-specific pitfalls?

Each eval lists the prompt, what to grade on, what failure looks like, and what an ideal response should include. Pass/fail per eval; the overall score is the fraction passed.

---

## Section 1 — Triggering evals

The skill description should fire on these and *not* fire on the negative controls. Run the baseline model and the model-with-skill on each prompt; check whether the skill is loaded.

### T1 — Direct mention of standard model

**Prompt:** "I want to fit a Rescorla-Wagner model to my probabilistic reversal data — what's the best way to start?"

**Should:** Skill fires; reinforcement_learning.md and probably recovery.md get read.

**Fail mode:** Skill doesn't fire, or the model immediately writes a likelihood without pulling the reference.

### T2 — Casual phrasing, no model named

**Prompt:** "I've got bandit task data and want to get a learning rate out of it. Where do I start?"

**Should:** Skill fires (the description explicitly calls out this casual phrasing).

**Fail mode:** Claude treats this as a generic data-analysis question and doesn't pull the skill.

### T3 — Mentions Stan or hBayesDM by name

**Prompt:** "Help me debug my hBayesDM call — `ra_prospect` is throwing errors when I pass my data."

**Should:** Skill fires; prospect_theory.md and hierarchical_stan.md get read.

### T4 — DDM debugging language

**Prompt:** "My HDDM fit gave a drift rate of -0.05 for the hard condition and +0.02 for the easy one. The signs look right but the magnitudes feel small. Should I worry?"

**Should:** Skill fires; drift_diffusion.md gets read. Claude should engage with the actual numbers (drift in expected range or not, scaling considerations, etc.) rather than giving a generic answer.

### T5 — Comparison/criterion language

**Prompt:** "I have ΔWAIC = 8 in favor of my dual-α model over single-α. Is that reliable?"

**Should:** Skill fires; model_comparison.md gets read. Claude should ask for the SE of the difference, not just declare "yes/no."

### T6 — Negative control: predictive ML

**Prompt:** "I want to predict customer churn from behavioral logs using gradient boosting — what features should I engineer?"

**Should NOT:** Fire. This is generic ML, not cognitive modeling. The skill description excludes this.

**Fail mode:** Skill fires and the model gives a 12-step cognitive modeling lecture for an XGBoost problem.

### T7 — Negative control: descriptive stats

**Prompt:** "Compare mean accuracy between my two patient groups — what test should I use?"

**Should NOT:** Fire. This is a t-test/Mann-Whitney question, not a process model.

### T8 — Negative control: SEM

**Prompt:** "I'm running a CFA on my questionnaire data with three latent factors. How do I check fit?"

**Should NOT:** Fire. SEM / factor analysis is a different methodology family.

### T9 — Edge case: tempted-but-shouldn't

**Prompt:** "I have RT data from a Stroop task and want to compare conditions."

**Should:** Skill may fire if the user is going to model the RTs with a DDM; should NOT if they just want condition means. Claude should clarify before pulling the skill. Acceptable behavior: Claude asks whether the user wants a DDM-style decomposition or simple means/medians, and pulls the skill only if the former.

### T10 — Multi-model question

**Prompt:** "I want to compare Q-learning, model-based RL, and a hybrid, on my two-step task data. What's the right workflow?"

**Should:** Fire; pull reinforcement_learning.md, model_comparison.md, and recovery.md.

---

## Section 2 — Routing evals

Once triggered, does the model pull the *correct* reference files? These tests check that the file structure is being used.

### R1 — Pure RL question

**Prompt:** "Walk me through the math of the Rescorla-Wagner update rule."

**Expected refs:** reinforcement_learning.md only.

**Fail:** Pulls drift_diffusion.md, category_learning.md, or all references.

### R2 — Mixed-gambles task

**Prompt:** "How do I estimate loss aversion from Sokol-Hessner-style gambles?"

**Expected refs:** prospect_theory.md, probably hierarchical_stan.md if they're doing Bayesian.

### R3 — DDM RT distribution question

**Prompt:** "My DDM fit gives the correct mean RT but the slow-error pattern is wrong."

**Expected refs:** drift_diffusion.md.

**Quality check:** The model should specifically discuss inter-trial variability in drift (`sv`) as the most likely missing component.

### R4 — Category learning

**Prompt:** "I'm comparing GCM and prototype models on a family resemblance task. What stimuli should I use?"

**Expected refs:** category_learning.md.

**Quality check:** The model should specifically reference Medin-Schaffer / 5/4 task and mention that arbitrary stimuli won't dissociate the models.

### R5 — Delay discounting MCQ

**Prompt:** "I have Kirby MCQ data. Should I use the traditional k-scoring or fit the hyperbolic model?"

**Expected refs:** delay_discounting.md.

### R6 — Volatility task

**Prompt:** "Subjects show faster learning in the volatile block than the stable block. What model captures this?"

**Expected refs:** bayesian_learning.md, possibly reinforcement_learning.md for comparison.

**Quality check:** The model should mention that fixed-α RW *cannot* capture this by design and point to Behrens/HGF/Kalman as the appropriate model class.

### R7 — Cross-cutting: parameter recovery

**Prompt:** "How do I know if my parameter estimates are trustworthy?"

**Expected refs:** recovery.md primarily.

### R8 — Cross-cutting: WAIC vs LOO

**Prompt:** "When should I use WAIC vs PSIS-LOO?"

**Expected refs:** model_comparison.md.

### R9 — Cross-cutting: Stan reparameterization

**Prompt:** "My hierarchical RL Stan model is divergent."

**Expected refs:** hierarchical_stan.md.

**Quality check:** The model should immediately suggest non-centered parameterization before anything else.

### R10 — Multi-family question

**Prompt:** "I want to fit an RL-DDM to my instrumental learning data with RTs."

**Expected refs:** reinforcement_learning.md AND drift_diffusion.md.

---

## Section 3 — Content / workflow evals

These check that the model actually *applies* the methodology, not just pulls the reference.

### C1 — The "fit and report" trap

**Prompt:** "I fit a 3-parameter RL model to 60 subjects and the group-mean learning rate is 0.34 (SE 0.04). Is that publishable?"

**Pass criteria:**
- The model does NOT just say "looks fine."
- The model asks about (or proactively addresses): parameter recovery on simulated data, model comparison vs simpler/competing models, posterior predictive checks, and recovery confusion with other parameters.
- Specifically mentions that "a number with an SE" is not the same as a measured quantity.

**Fail:** Claude provides feedback as if learning rate is a measured value and ignores the methodological gaps.

### C2 — The α/β trade-off

**Prompt:** "I have a bunch of subjects whose fitted learning rate is essentially 1.0 (at the upper bound), and inverse temperature β is all over the place. The model fit is okay on LOO."

**Pass criteria:**
- Claude recognizes this is the classic α ≈ 1 with unidentified β case.
- Claude doesn't accept the fit as-is; suggests reparameterization, switch to MAP or HB with informative priors, or that α at the boundary means the model isn't doing real work for these subjects.

### C3 — Loss aversion from gain-only gambles

**Prompt:** "I want to estimate loss aversion (λ) from a gain-only task with gambles like $10 vs sure $5."

**Pass criteria:**
- Claude immediately flags that λ is *not identifiable* from gain-only gambles by construction.
- Claude proposes either using a mixed-gambles task or fixing λ.
- Does NOT just hand the user some Stan code and let them run it.

### C4 — DDM units bug

**Prompt:** "I'm using HDDM but my fitted boundary `a` is 1200 and `t` is 350. What's wrong?"

**Pass criteria:**
- Claude immediately identifies this as RT-in-ms-vs-seconds. HDDM expects seconds; the user has fed it ms.
- Suggests dividing RTs by 1000 and refitting.

**Fail:** Generic "convergence issues" answer.

### C5 — The "two-step `w` is reliable" trap

**Prompt:** "I want to use the model-based weight `w` from the two-step task as a between-subjects individual difference measure correlating with my clinical scores."

**Pass criteria:**
- Claude flags that test-retest reliability of `w` is mediocre (Brown et al. 2020; Shahar et al. 2019).
- Suggests checking the reliability in the user's own dataset before correlating with clinical scores.
- Mentions reporting parameter recovery and uncertainty intervals.

### C6 — Hierarchical model is over-shrinking

**Prompt:** "My hierarchical Bayesian RL fit shows everyone's α basically equal to the group mean. I expected more individual variation."

**Pass criteria:**
- Claude considers whether `sigma` (the group SD on α) is being shrunk toward zero by the prior.
- Suggests inspecting the posterior on `sigma`, considering a wider hyperprior, or checking whether the data simply don't support individual-level identification at this trial count.

### C7 — Just fit it for me

**Prompt:** "Here's my CSV of bandit data. Please write Stan code and fit it for me."

**Pass criteria:**
- Claude provides the Stan code (using the template from hierarchical_stan.md) and a fit-calling script.
- But ALSO insists on (or builds in) simulation-based parameter recovery before treating the fit as valid.
- Mentions the canonical pitfalls (α/β trade-off, perseveration as nuisance, model comparison vs baselines).
- Doesn't just deliver code and call it done.

### C8 — Best WAIC isn't best model

**Prompt:** "Model A has the best WAIC by a wide margin (ΔWAIC = 50 vs B). I'm going with A."

**Pass criteria:**
- Claude asks about (or proactively raises): the SE of the difference; PPC for model A; model recovery confusion matrix to check whether A and B are even distinguishable; whether model A's parameters are recoverable.
- A bare "great, ship it" is a fail.

### C9 — Category learning recovery question

**Prompt:** "I'm fitting GCM to my categorization data — c = 2.3, w = (0.7, 0.3). Reasonable?"

**Pass criteria:**
- Claude notes that c/w trade off in GCM (high c + low w peakedness ≈ low c + high w peakedness).
- Asks about parameter recovery on simulated data with this stimulus structure.
- Mentions that the answer depends heavily on the dimension scaling (was MDS used? was it just raw pixels?).

### C10 — Volatile-block learning rate

**Prompt:** "I want to show subjects' learning rates are higher in the volatile block than the stable block, so I'm fitting RW with separate α per block."

**Pass criteria:**
- Claude points out that fitting separate α per block is a *descriptive* approach that may work fine, but a *normative* approach would use a Bayesian/Behrens-style model that derives the block effect from a single set of parameters.
- Notes that the two approaches answer different questions.

### C11 — MLE on a few trials

**Prompt:** "I have 30 trials per subject and want per-subject MLE estimates of α and β."

**Pass criteria:**
- Claude warns that MLE on 30 trials will give extreme/boundary estimates for many subjects.
- Strongly recommends MAP or hierarchical Bayes.
- Doesn't just provide an MLE script without the warning.

### C12 — Prospect theory baseline missing

**Prompt:** "I fit cumulative prospect theory to my gambles data and the parameters look great."

**Pass criteria:**
- Claude asks whether they fit expected utility as a baseline.
- Notes that PT-vs-EU is the comparison that earns the right to publish a PT story.
- Asks about PPC.

### C13 — Drift rate by condition

**Prompt:** "I have a perceptual decision task with 3 difficulty levels. Should I fit one drift rate or three?"

**Pass criteria:**
- Claude says: three (one per condition), and explains why a single drift averaged across conditions will mis-fit the RT distribution.
- May propose the HDDM regression interface.

### C14 — Asks before answering when ambiguous

**Prompt:** "What's the best learning model for my data?"

**Pass criteria:**
- Claude asks what the task is, what the scientific goal is (parameter estimation, model comparison, fMRI regressors), and what they've already tried.
- Does NOT recommend a specific model without this context.

### C15 — Engages with actual output

**Prompt:** Paste this Stan output:
```
       mean   se_mean    sd   2.5%   25%   50%   75%  97.5%  n_eff  Rhat
alpha  0.34   0.01    0.08   0.18  0.28  0.34  0.40  0.51    156   1.04
beta   3.21   0.05    0.41   2.44  2.93  3.20  3.49  4.03    220   1.03
```

**Pass criteria:**
- Claude notes that Rhat = 1.04 and 1.03 are above 1.01 — concerning, not catastrophic, but worth addressing.
- Notes ESS = 156 is on the low side for alpha; suggests more iterations or thinning.
- Engages with the actual values (alpha looks reasonable; beta looks reasonable for typical reward scaling).
- Does not say "looks great" without addressing the diagnostics.

---

## Grading

For each eval: pass = met all "Pass criteria" / fired correctly / pulled correct refs. Fail otherwise. Partial credit (e.g., 0.5) acceptable for routing evals that pulled the right primary reference but missed a secondary one.

**Overall scoring (rough targets):**
- Triggering (T1–T10): expect ≥ 9/10 to pass.
- Routing (R1–R10): expect ≥ 8/10.
- Content (C1–C15): expect ≥ 12/15. The content evals are the hardest and where the skill earns its keep.

If the skill scores < 80% overall, debug:
- Triggering misses → description not specific enough.
- Routing misses → reference filenames or top-level routing in SKILL.md unclear.
- Content misses → workflow or pitfalls not surfaced clearly enough in the relevant reference.

## Notes for the eval-runner

- Run each eval in an isolated conversation; don't let prior context contaminate.
- For content evals, the *first* response is what's graded. Followups are useful as additional signal but the skill should fire its workflow on turn 1.
- For triggering evals, instrument whether the skill files actually get read (e.g., check that the relevant `view` calls happen on SKILL.md and the appropriate reference).
- Negative-control evals (T6–T8) are as important as positive ones — a skill that fires on every question is as bad as one that never fires.
