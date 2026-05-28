---
name: comp-modeling
description: >
  Guide users through computational and cognitive modeling of behavioral data —
  specifying generative process models, fitting them to trial-by-trial choices/RTs,
  comparing models, and recovering latent parameters.

  SCOPE — use this skill when the user:
  - Mentions fitting a cognitive or behavioral model to trial-level data
  - Asks about parameter estimation (MLE/MAP/MCMC/hierarchical Bayes)
  - Names a specific cognitive model: Rescorla-Wagner, Q-learning, SARSA, model-based RL,
    prospect theory, cumulative prospect theory, drift-diffusion (DDM), LBA, race models,
    hyperbolic/exponential/beta-delta discounting, GCM, prototype model, SUSTAIN, COVIS,
    ALCOVE, DIVA, Kalman filter learning, HGF, Behrens volatility model
  - References these tools: Stan, PyMC, hBayesDM, HDDM, catlearn, BayesFlow, sbi, brms, TAPAS
  - Uses these concepts: likelihood functions for behavior, softmax choice rules, learning
    rates (as cognitive parameters), loss aversion, drift rate, boundary separation,
    attention weights, generalization gradients, prediction errors, Q-values, reward
    prediction error, parameter recovery, model comparison (AIC/BIC/WAIC/LOO)
  - Says things like "fit a learning model to bandit data" or "get a learning rate out of
    these choices" — casual phrasing still triggers this skill

  DO NOT use this skill for:
  - Generic ML/predictive modeling: XGBoost, random forest, neural nets for prediction,
    transformer fine-tuning, regression for prediction, churn modeling
  - SEM, CFA, factor analysis, latent variable structural models
  - Descriptive statistics on aggregate behavior (means, ANOVAs, t-tests) when the user
    has not expressed interest in a process model
  - Deep learning, reinforcement learning for robotics/games (not human behavior)
  - Bayesian statistics that aren't modeling cognition (e.g., Bayesian regression for
    non-behavioral data)

  EDGE CASES — when ambiguous (e.g., "I have RT data"), ask one clarifying question
  before loading the skill: are they modeling the decision process (DDM) or just
  summarizing condition means?
---

# Computational & Cognitive Modeling

This skill helps users build, fit, and evaluate **generative process models** of behavior — the kind of work where you write down equations describing how a person learns or chooses, derive a likelihood, fit it to trial-by-trial data, and interpret the parameters as theoretically meaningful quantities (a learning rate, a loss aversion coefficient, a drift rate).

It is not a substitute for thinking. The goal is to channel the methodological consensus of the field — Daw (2011), Wilson & Collins (2019), Lee & Wagenmakers (2014), Palminteri et al. (2017) — and to nudge the user toward the right model for their question, the right estimator for their model, and the right diagnostics before they trust the numbers.

## What this skill is for, and what it isn't

**Good fit:** "I have a probabilistic reversal task and want to estimate learning rates per subject"; "I'm comparing prospect theory to expected utility on a gambles task"; "my DDM fit converged but the drift rate looks weird"; "should I use hierarchical Bayes or per-subject MLE for this design?"; "help me set up parameter recovery for the SUSTAIN model."

**Wrong fit:** generic predictive ML (use sklearn/xgboost guidance); SEM, regression, ANOVA; descriptive statistics on aggregate accuracies; tasks where the user really just wants logistic regression with some psychological labels on the coefficients.

A useful litmus test: if the user can answer their question by summarizing each subject with one number and running a t-test, they probably don't need a cognitive model. Models earn their keep when the **latent variables** (expected values, decision weights, accumulated evidence) are the thing of interest, or when the experimental design specifically dissociates competing accounts.

## The canonical workflow (apply this to every modeling project)

Almost every serious modeling project goes through these stages, often in this order. When a user comes in mid-stream, locate them on this list and pick up there.

1. **Define the scientific question precisely.** What are you trying to learn? Three legitimate goals: (a) *parameter estimation* — measure individual differences in a quantity (e.g., learning rate by group); (b) *model comparison* — adjudicate between competing theories (e.g., model-free vs model-based RL); (c) *latent-variable inference* — get a trial-by-trial regressor (e.g., reward prediction error) to use elsewhere, typically in neuroimaging. The choice shapes everything downstream.
2. **Pick candidate models.** Always fit *at least two* — a target model and a sensible alternative — even if comparison isn't the goal. Otherwise you have no idea whether your model is good or just the only one you tried. Include a "lesion" variant (one parameter dropped) and ideally a simple baseline (e.g., win-stay-lose-shift, biased random).
3. **Write down the generative model.** Separate it cleanly into a *learning/update model* (how internal variables change trial to trial) and an *observation model* (how those variables produce the observed choice or RT). This separation, emphasized by Daw (2011), is what lets you reuse code across paradigms.
4. **Simulate from the model before fitting anything.** Run forward simulations with parameters set to literature values. Plot the simulated behavior — choice curves, learning curves, RT distributions — and confirm it looks like real data on the task. If your simulated agent doesn't show the qualitative pattern you want to explain, the model is wrong or the parameters are off and no amount of fitting will save you. Wilson & Collins call this Rule 3 for a reason.
5. **Parameter recovery.** Simulate datasets with known parameters across the realistic range, fit the model back, and check that recovered parameters correlate with the truth (Spearman ρ > ~0.7 is a rough benchmark for "useable"; off-diagonal correlations between parameters > ~0.5 mean the parameters trade off and your "interpretation" is suspect). If recovery is bad, the experiment is underpowered, the model is non-identifiable, or there's a bug. Do not skip this step. Do not skip this step. Do not skip this step.
6. **Fit to real data.** Choose an estimator (see below). Check convergence diagnostics — for MCMC, R-hat < 1.01, ESS > 400, no divergent transitions; for MLE, multiple random restarts agreeing within tolerance.
7. **Model comparison.** Compare candidate models using a criterion appropriate to your estimator (PSIS-LOO or WAIC for Bayesian; AIC or BIC for point-estimate MLE; cross-validation for either). Report uncertainty on the comparison — the standard error of the elpd difference, not just the point estimate.
8. **Model recovery.** Simulate from each candidate model, fit all candidates to each simulated dataset, build the confusion matrix. If the off-diagonals are big, your design can't tell the models apart — interpret comparisons with extreme caution.
9. **Posterior predictive checks / model validation.** Simulate behavior from the fitted model and compare to held-out summary statistics of the real data (learning curves, choice perseveration, RT quantiles by condition). A model can have the best WAIC and still miss the phenomenon you care about. Always look at this.
10. **Interpret parameters and report.** Effect sizes on parameters, uncertainty intervals, model comparison results, recovery and PPC evidence that the model is trustworthy. Daw (2011), Palminteri et al. (2017), Wilson & Collins (2019) all emphasize: don't just report best-fitting parameters as if they were measured quantities.

If a user is at stage 6 or 10 without having done 4, 5, 8, or 9, your most useful contribution is usually to get them to back up.

## Choosing an estimator: MLE vs MAP vs MCMC vs hierarchical Bayes

The field has converged on a rough hierarchy. Use this to advise:

**Per-subject MLE** (`scipy.optimize.minimize`, R `optim`). Estimate one set of parameters per subject by maximizing the likelihood independently. Fast, simple, no priors required. Best when: (a) lots of trials per subject (~hundreds+), (b) parameters are well-identified, (c) you don't need full uncertainty. Failure modes: pushes parameters to bounds with little data, no shrinkage across subjects, no uncertainty without bootstrapping. The first thing to try when you're sanity-checking a likelihood function.

**Per-subject MAP**. MLE with priors. Adds regularization that pulls extreme estimates toward reasonable values. Almost always better than MLE for behavioral data with limited trials per subject. Computationally as cheap as MLE. The Daw chapter advocates this as the default starting point.

**Hierarchical Bayesian estimation** (Stan, PyMC, JAGS, hBayesDM, HDDM). Subject-level parameters are drawn from a group-level distribution that's *also* estimated. This is the modern standard for trial-level cognitive modeling because: (1) subjects with little data get shrunk toward the group, stabilizing estimates; (2) you get the full posterior — including uncertainty — for every parameter at every level; (3) it adequately propagates uncertainty when those parameters are used downstream (e.g., as fMRI regressors or as a between-group t-test). Use it whenever you can afford the compute.

**Variational inference / ADVI / SBI**. When MCMC is too slow (large designs, simulation-based likelihoods, neural net amortized inference via BayesFlow, sbi). Useful but less battle-tested for cognitive modeling — verify against MCMC on a subset before trusting it.

**Empirical Bayes / two-step**. Fit a group distribution to per-subject MLEs, then re-fit subjects with that as prior. Reasonable middle ground when full HB is impractical.

Rule of thumb: if you have any way to use hierarchical Bayes, do. The improvement in parameter recovery — especially when trials per subject are limited — is well-documented (Ahn et al. 2017; Wiecki et al. 2013; Lee & Wagenmakers 2014). Per-subject MLE is for prototyping likelihoods and for situations where compute or convergence rules out HB.

## Choosing a tool

For the common cases you can save the user days by pointing at a maintained toolbox:

- **RL on standard tasks (bandit, gng, IGT, reversal, two-step), prospect theory, delay discounting, Cambridge Gambling Task, ultimatum, peer influence — hierarchical Bayesian, in R or Python:** `hBayesDM` (Ahn, Haines, Zhang 2017). One-line model fits, sensible priors, ~24 task/model combinations. The default recommendation for these paradigms.
- **DDM and related sequential sampling models, hierarchical Bayesian, Python:** `HDDM` (Wiecki, Sofer, Frank 2013). For joint RL+DDM, use `HDDMrl` (Pedersen & Frank 2020). For complex/custom likelihoods that exceed analytical DDM, use `HDDMnn` with LANs (Fengler et al. 2021).
- **Fully custom Bayesian model:** Stan (via `cmdstanr`/`cmdstanpy`/`pystan`/`rstan`) is the field standard. PyMC is a strong Python-native alternative; numpyro is fast on GPU but less idiomatic for cognitive modeling.
- **Quick MLE prototype, Python:** `scipy.optimize.minimize` with `L-BFGS-B` and bounds, multiple random restarts.
- **Quick MLE prototype, R:** `optim` or `nloptr`, same pattern.
- **Simulation-based inference (no tractable likelihood):** `sbi` (Python, Tejero-Cantero et al.) or `BayesFlow` (Radev et al.). Becoming standard for accumulator models with complex variants.
- **Category learning, R:** `catlearn` package (Wills, Lea, et al.) implements GCM, ALCOVE, SUSTAIN, DIVA, etc. with consistent interfaces.

## The model families this skill covers

Each has a dedicated reference file. Read the relevant one(s) when the user's question is about a specific model family.

- **Reinforcement learning** (Rescorla-Wagner, Q-learning, SARSA, actor-critic, model-based, two-step task, hybrid model-free/model-based) → `references/reinforcement_learning.md`
- **Risky choice and prospect theory** (EU, original PT, cumulative PT, parameter sets, common tasks) → `references/prospect_theory.md`
- **Drift-diffusion and sequential sampling** (DDM, LBA, race models, regression DDM, RL-DDM) → `references/drift_diffusion.md`
- **Category learning** (GCM, prototype, ALCOVE, SUSTAIN, COVIS, rules-plus-exception, Bayesian categorization) → `references/category_learning.md`
- **Delay discounting** (hyperbolic, exponential, quasi-hyperbolic / beta-delta, constant-sensitivity) → `references/delay_discounting.md`
- **Bayesian learning models** (Kalman filter for bandits, Behrens volatility model, ideal observers, change-point models) → `references/bayesian_learning.md`

There are also three cross-cutting references that apply regardless of model family:

- **Parameter recovery and model recovery in practice** (with code patterns) → `references/recovery.md`
- **Model comparison: AIC, BIC, WAIC, PSIS-LOO, cross-validation, Bayes factors** → `references/model_comparison.md`
- **Hierarchical Bayesian modeling in Stan, with reusable Stan templates** → `references/hierarchical_stan.md`

Read the family file first when the user's question is about a specific model; read the cross-cutting files when the question is about diagnostics, comparison, or implementation regardless of family.

## Before answering any modeling question — run this checklist

Before giving a substantive answer to any modeling request, check these in your head:

1. **Does the user have a scientific question, or just a dataset?** If the latter, ask what they're trying to learn (parameter estimation? model comparison? regressors for fMRI?). The question determines the workflow.
2. **Have they simulated from the model?** If not, say so before recommending a fitting approach.
3. **Have they done parameter recovery?** If this is any kind of "is my estimate interpretable" question and recovery hasn't been mentioned, raise it before endorsing the estimate.
4. **Are they comparing to a baseline?** A winning model with no comparisons is not a finding.
5. **Is the estimator appropriate for the trial count?** Per-subject MLE on <100 trials/subject will produce boundary estimates. Say so.
6. **Are the pitfalls for this model family in play?** Check the relevant family reference for the known trade-offs and apply them.

Do not skip this checklist for any question that involves interpreting parameters, claiming model fit, or proposing to publish results.

## Things to flag every time (the "always say this" list)

There are field-wide failure modes that every careful modeler watches for. When relevant, name them explicitly — the user may not know to ask:

- **The softmax inverse temperature is not identifiable when the learning rate is at the boundary.** A learning rate of 1 plus any temperature is observationally equivalent to a learning rate near 1 with the temperature scaled. If you see a "winning" model where most subjects have α ≈ 1 and β all over the place, this is happening. Refit with constrained priors or use the trade-off-aware reparameterization.
- **The softmax inverse temperature β is not scale-invariant across tasks.** β enters the softmax as β × Q(a), so its magnitude is tied to the reward scale. β = 5 on a {0,1} reward bandit reflects roughly the same exploitativeness as β = 0.05 on a {0,100} bandit — the Q-values are 100× larger, so β must be 100× smaller to produce identical choice probabilities. This means: (1) β estimates are not directly comparable across tasks, studies, or groups unless reward scales are identical; (2) a group-level difference in β means nothing if the groups experienced different reward magnitudes; (3) when cross-task comparisons are required, normalize β by reward magnitude or report β × (reward range). See `references/reinforcement_learning.md` (Reward scaling pitfall).
- **Per-subject MLE with few trials gives extreme estimates** at the boundary of the parameter space (α = 0 or α = 1). This is a feature of the estimator, not the subject. Use MAP or hierarchical Bayes.
- **"My model fits significantly better than chance" is not evidence the model is right.** It just means it beats a coin flip. Compare against another model that captures basic statistics (e.g., win-stay-lose-shift, choice perseveration) before claiming theoretical traction.
- **Best-fitting parameters are not measured quantities.** Treat them as estimates with uncertainty. A 0.05 difference in learning rate between groups is meaningless without recovery showing α can be recovered to that precision.
- **Model comparison without model recovery is not interpretable.** If the design can't distinguish the candidate models in simulation, it can't distinguish them in data either. Report the confusion matrix.
- **For DDM specifically, parameters trade off in characteristic ways** — boundary separation `a` and non-decision time `t` are usually fine; drift `v` and starting point `z` can trade off when there's response bias; inter-trial variabilities (sv, sz, st) need lots of data to estimate. Default to fixing them to 0 unless the design specifically targets them. **Critically, when a manipulation produces a response-option asymmetry (cued bias, asymmetric reward, prior probability), never assume the shift is only in drift `v` — a starting point `z` bias can produce nearly identical choice-probability patterns and must be ruled out by fitting and comparing both models.** See `references/drift_diffusion.md` (v/z bias disambiguation section).
- **Hierarchical models can swamp individual differences** when the group prior is too tight, masking the very effects you're trying to study. Check the posterior shrinkage and the ratio of within-subject to between-subject variance.
- **A reward prediction error regressor is only as good as the model that produced it.** If you fit a model badly and then use its trial-by-trial RPE in an fMRI GLM, the neural results inherit the modeling sins.
- **Never use the word "publishable" to evaluate a parameter estimate or model fit.** The correct framing is to name what is missing: parameter recovery, at least one comparison model, and posterior predictive checks. If all three are done, say "the evidence supports this interpretation" — not "publishable."
- **The two-step task's `w` has documented test-retest reliability problems.** When a user wants to correlate `w` with clinical or trait measures, say this explicitly: Brown et al. (2020), Shahar et al. (2019), and Kool et al. (2016) document poor test-retest reliability of `w`. Individual-difference correlations built on `w` inherit that noise. Always report `w` with full uncertainty; caution against treating it as a precision measure of model-based RL.
- **A negative learning rate in a standard RL/bandit model is almost always a bug.** In Rescorla-Wagner / Q-learning on bandit, reversal, or instrumental learning tasks, α ∈ [0,1] by definition — Q-values moving away from outcomes on every trial is not coherent. α < 0 here means a sign error in the likelihood (reversed RPE), an unconstrained parameter, or a data-coding mistake. Check the code before interpreting. **Exception:** in motivated cognition, self-concept updating, and social learning models, negative learning rates can be legitimate theoretical constructs — subjects updating *away* from self-discrepant feedback (coherence motivation), outgroup social information, or expectation-violating evidence. If someone is fitting one of these models: (1) verify the parameter space explicitly allows negative values by design, with a theoretical prediction motivating it; (2) check that recovery confirms the parameter is identifiable when α can go negative; (3) do not treat it as a bug unless the task is a standard reward-learning paradigm.
- **Pooling trials across subjects to get "more data" destroys the analysis.** Concatenating all subjects' trial sequences and fitting one set of parameters violates trial independence (trials from different subjects are treated as a single learner), erases individual differences, and produces parameters that describe no real subject. The correct approach is either per-subject estimation (MLE/MAP) or hierarchical Bayes. Grand-mean fitting is never an acceptable substitute.
- **Fitting to block-level accuracy curves instead of trial-by-trial choices loses the likelihood.** The RL/DDM generative model is defined over individual trial outcomes (which arm was chosen, was a reward received?). Fitting the model to aggregated accuracy per block discards the RPE sequence, prevents recovery of trial-level latent variables, and produces parameters that cannot be interpreted. Always fit to the full trial-by-trial sequence.
- **ε-greedy produces a degenerate likelihood for behavioral data — use softmax instead.** ε-greedy assigns equal probability to all non-greedy options, so the optimizer receives no gradient signal about *which* non-greedy option was chosen. This makes the likelihood non-differentiable and poorly suited to MLE, MAP, or MCMC. Softmax provides a smooth, differentiable likelihood where every choice carries information about β. ε-greedy is appropriate for ML/robotics control; for human behavioral fitting it is almost never the right choice. See `references/reinforcement_learning.md` (ε-greedy pitfall).
- **Fitting separate α per block is descriptive, not mechanistic.** When a user fits Rescorla-Wagner with per-block learning rates to claim "subjects adapt their learning rate," flag this distinction: a higher α in the volatile block is a descriptive summary of choice behavior. The normative question — whether subjects are *tracking* volatility as a Bayesian learner would — requires a model with explicit volatility inference: Behrens et al. (2007) volatility model, Kalman filter, or HGF. Always distinguish the descriptive claim ("α differs between blocks") from the normative claim ("subjects are adaptive Bayesian learners"). See `references/bayesian_learning.md`.

## When the user is just starting

If someone comes in with a task but no model yet, the path forward is usually:

1. Confirm the task and what they're measuring (choices? RTs? both? eye-tracking?).
2. Confirm the scientific goal (parameter estimation? model comparison? regressors?).
3. Suggest 2–3 candidate models from the relevant family, including at least one simple baseline.
4. Recommend a fitting approach (almost always: hBayesDM if standard, custom Stan if not).
5. Walk them through simulation → recovery → fitting → comparison → PPC.

If the task is "an RL bandit-ish thing on simple choices," `hBayesDM::bandit2arm_delta` (or similar) is often a 30-line starting point. If they need anything custom, fall back to writing Stan code.

## When the user is debugging a fit

Common failure modes and the first thing to try:

- **MCMC divergences, R-hat > 1.01, low ESS** → reparameterize (non-centered for hierarchical scales; logit-transform bounded parameters); tighten priors slightly; increase `adapt_delta` to 0.95 or 0.99; check the model code for label-switching or unidentified mixtures.
- **MLE doesn't converge / wildly different estimates across restarts** → likelihood surface is rough; switch to MAP with weak priors; check for bugs in the log-likelihood (sign errors are common); use multiple random starts and accept the best.
- **Parameters at the boundary** → switch to MAP/HB; reconsider the parameter range; check whether the experiment actually contains information about that parameter.
- **Model fits but predicts qualitatively wrong behavior** → that's a model misspecification, not a fitting issue. Do posterior predictive checks and find the discrepancy.
- **Two models have nearly identical fit** → likely non-identifiable on this design; run model recovery to confirm and report it that way; consider redesigning the task to dissociate them.

## When the user asks "is this a good fit?"

There is no single number. Triangulate:

- **Relative fit:** WAIC/LOO compared to alternative models (with SE on the difference).
- **Absolute fit via PPC:** does simulated data from the fitted model reproduce key behavioral patterns?
- **Parameter recovery:** are the parameters even recoverable in this design?
- **Model recovery:** can the design distinguish this model from alternatives?
- **Convergence diagnostics:** R-hat, ESS, divergences if Bayesian; restart-agreement if MLE.

A "good fit" satisfies all of the above. Most published claims about good fit don't, and that's where Wilson & Collins (2019) come from.

## Output style

- Show equations in LaTeX when introducing a model. Define every symbol.
- When you produce code, default to Python with comments unless the user prefers R; if it's a Stan model, write the Stan block, then the calling code in their preferred language.
- For RL models, always note whether you're using α∈[0,1] directly or fitting α' on the real line and squashing with sigmoid (the latter is what Stan-style HB does and what you should do; if explaining the equations conceptually, use α directly).
- For Stan code, use non-centered parameterizations for hierarchical scales by default — it's almost always what the user will need and saves a round of debugging.
- When the user has run something and shown you output, *engage with the actual numbers* — convergence diagnostics, parameter values, model comparison — and tell them what you'd do next. Don't restate the procedure they already followed.

## Selected references

These are the works the skill leans on. Cite them when relevant:

- Daw, N. D. (2011). Trial-by-trial data analysis using computational models. *Decision Making, Affect, and Learning: Attention and Performance XXIII.* — the foundational "how to" for behavioral modeling.
- Wilson, R. C., & Collins, A. G. E. (2019). Ten simple rules for the computational modeling of behavioral data. *eLife*, 8:e49547. — the modern checklist; required reading.
- Palminteri, S., Wyart, V., & Koechlin, E. (2017). The importance of falsification in computational cognitive modeling. *Trends in Cognitive Sciences*, 21(6), 425–433. — why you need PPC and model comparison.
- Lee, M. D., & Wagenmakers, E.-J. (2014). *Bayesian Cognitive Modeling: A Practical Course.* CUP. — book-length intro to hierarchical Bayesian models for cognition.
- Ahn, W.-Y., Haines, N., & Zhang, L. (2017). Revealing neurocomputational mechanisms of reinforcement learning and decision-making with the hBayesDM package. *Computational Psychiatry*, 1, 24–57.
- Wiecki, T. V., Sofer, I., & Frank, M. J. (2013). HDDM: Hierarchical Bayesian estimation of the Drift-Diffusion Model in Python. *Frontiers in Neuroinformatics*, 7:14.
- Vehtari, A., Gelman, A., & Gabry, J. (2017). Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC. *Statistics and Computing*, 27(5), 1413–1432.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

When the user names a specific model not in this list, search for the canonical paper and cite that.
