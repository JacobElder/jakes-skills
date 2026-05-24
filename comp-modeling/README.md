# comp-modeling — a Claude skill for computational and cognitive modeling

A skill for fitting **generative process models** of behavior — RL, prospect theory, DDM, category learning, delay discounting, Bayesian learning — to trial-by-trial choice and RT data. Built around the methodological consensus of Daw (2011), Wilson & Collins (2019), Palminteri et al. (2017), and Lee & Wagenmakers (2014).

## Structure

```
comp-modeling/
├── SKILL.md                          ← top-level skill, always loaded; cross-cutting workflow + estimator/tool choices
├── references/                       ← progressively-disclosed model-family detail
│   ├── reinforcement_learning.md     ← RW, Q-learning, dual-α, two-step, PVL, hybrid MF/MB
│   ├── prospect_theory.md            ← OPT, CPT, weighting functions, Sokol-Hessner gambles
│   ├── drift_diffusion.md            ← DDM, LBA, race models, RL-DDM, HDDM patterns
│   ├── category_learning.md          ← GCM, ALCOVE, SUSTAIN, COVIS, RULEX, Bayesian categorization
│   ├── delay_discounting.md          ← exponential, hyperbolic, β-δ, constant-sensitivity, MCQ
│   ├── bayesian_learning.md          ← Kalman bandits, Behrens volatility, HGF, change-point
│   ├── recovery.md                   ← parameter recovery and model recovery, code patterns
│   ├── model_comparison.md           ← AIC/BIC/WAIC/PSIS-LOO/Bayes factors, when to use which
│   └── hierarchical_stan.md          ← Stan templates, non-centered parameterization, debugging
├── scripts/                          ← reusable Python utilities (smoke-tested)
│   ├── parameter_recovery.py         ← generic recovery loop with Spearman ρ, bias, RMSE, cross-param corr
│   ├── model_recovery.py             ← confusion + inversion matrices from candidate model set
│   └── posterior_predictive.py       ← PPC runner with pre-built bandit and DDM summary statistics
└── evals/                            ← evaluation suite for the skill itself
    ├── README.md
    ├── triggering.json               ← does the skill activate when it should
    ├── routing.json                  ← does the skill pull the right reference file
    ├── workflow.json                 ← does the skill produce the right workflow + flag pitfalls
    └── golden_responses.md           ← hand-crafted ideal answers as scoring anchors
```

## Design choices

**Progressive disclosure.** The top-level `SKILL.md` is the cross-cutting workflow that applies to every modeling project — research goal, simulate-before-fit, recovery, fit, model comparison, model recovery, PPC. Family-specific math, code, and pitfalls live in `references/` and get pulled in when the relevant model family is in play. This keeps the always-loaded surface manageable.

**Both Python and R.** Code patterns use Python with `scipy.optimize`, `cmdstanpy`, and PyMC where appropriate. R templates use `cmdstanr`, `loo`, `hBayesDM`, and `catlearn`. Stan code is the same regardless of caller language.

**Hierarchical Bayes by default for production work; per-subject MLE for prototyping.** The skill explicitly recommends `hBayesDM` for standard tasks and Stan with non-centered parameterization for custom models, and flags when per-subject MLE will give boundary estimates that mislead.

**The recovery insistence.** The skill is opinionated that parameter recovery and model recovery are non-negotiable, not optional polish. Almost every reference file links back to `recovery.md` and the cross-cutting workflow names recovery as step 5.

## Running the scripts

The Python utilities in `scripts/` are runnable directly and include self-tests at the bottom:

```bash
python scripts/parameter_recovery.py   # recovers RW α, β on a 200-trial 70/30 bandit
python scripts/model_recovery.py       # builds RW-vs-dual-α confusion matrix
```

The self-test in `model_recovery.py` is intentionally underpowered (200 trials, 70/30 reward probabilities — exactly the conditions where AIC penalty wins over the more complex model regardless of generator). This accidentally demonstrates a key teaching point: model comparison without adequate trials produces uninterpretable confusion matrices, just as the recovery reference warns.

## How to test the skill

Run the evals in `evals/`. Each JSON file lists prompts with `must_include` and `must_not_include` criteria; pass each prompt to Claude with the skill loaded and score the response. `golden_responses.md` anchors what excellent answers look like for three high-stakes prompts.

## Selected references the skill is built on

- Daw, N. D. (2011). Trial-by-trial data analysis using computational models.
- Wilson, R. C., & Collins, A. G. E. (2019). Ten simple rules for the computational modeling of behavioral data. *eLife*.
- Palminteri, S., Wyart, V., & Koechlin, E. (2017). The importance of falsification in computational cognitive modeling. *TiCS*.
- Lee, M. D., & Wagenmakers, E.-J. (2014). *Bayesian Cognitive Modeling: A Practical Course.*
- Ahn, W.-Y., Haines, N., & Zhang, L. (2017). hBayesDM. *Computational Psychiatry*.
- Wiecki, T. V., Sofer, I., & Frank, M. J. (2013). HDDM. *Frontiers in Neuroinformatics*.
- Vehtari, A., Gelman, A., & Gabry, J. (2017). PSIS-LOO and WAIC. *Statistics and Computing*.
