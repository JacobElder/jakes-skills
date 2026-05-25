# Parameter Recovery and Model Recovery

Read this whenever the user is fitting a model and hasn't yet shown they can recover the parameters of that model from simulated data. This applies regardless of model family — it's the single most-skipped diagnostic in computational modeling and the source of an embarrassing fraction of irreproducible findings.

Canonical references: Wilson & Collins (2019) eLife — the modern textbook treatment; Heathcote, Brown & Wagenmakers (2015); Palminteri, Wyart & Koechlin (2017); Daw (2011).

## Why this matters

A parameter you can't recover from simulated data is a parameter you can't measure from real data. Period. If you simulate behavior using α = 0.3 and your fitting procedure returns α = 0.7, no amount of theory can save you — the design or the model is failing to identify what you think it's identifying.

This is independent of statistical significance, model comparison, or how well the model fits. You can have a model with the best WAIC in the comparison and a beautifully tight posterior on a parameter that bears no relation to the underlying truth. The literature is full of these.

## Parameter recovery: the procedure

The core loop:

1. Choose a realistic range for each parameter (informed by prior estimates from the literature, not the full prior range).
2. Sample N parameter sets covering the range. Use a grid for low-dimensional models, latin hypercube or random uniform for higher-dim.
3. For each parameter set: simulate a full dataset of behavior using the same trial structure as your real experiment.
4. Fit the model to each simulated dataset using your actual fitting pipeline.
5. Compare the recovered parameters to the generating parameters.

### What to look at

**Correlation between true and recovered (Spearman ρ).** Per-parameter, across simulated subjects. Rules of thumb:
- ρ > 0.9: excellent
- 0.7 < ρ < 0.9: usable for individual-difference work
- 0.4 < ρ < 0.7: usable for group-level inferences only
- ρ < 0.4: not usable; rethink design or model

**Bias.** Is the recovered estimate systematically off the true value (e.g., always shrunk toward the prior mean, always biased toward the boundary)? Plot recovered vs true and look for slope ≠ 1 or intercept ≠ 0.

**Cross-parameter correlations.** Compute the correlation of recovered parameters across simulations. If `α` and `β` are correlated > 0.5 in recovery, they trade off; your "interpretation" of one without controlling for the other is suspect.

**Recovery as a function of trial count.** Re-run the analysis at the trial counts of your real experiment (and at 0.5×, 2× of that). This tells you whether your study is adequately powered for the parameter estimates.

**Recovery as a function of true parameter value.** Some models recover well in the middle of the parameter range but poorly near boundaries. Look at recovery error as a function of true value.

## Minimal Python skeleton for parameter recovery

```python
import numpy as np
from scipy.optimize import minimize
from scipy.stats import spearmanr

def simulate_rl(alpha, beta, n_trials, reward_probs):
    """Simulate one subject's data."""
    Q = np.zeros(2)
    choices, rewards = [], []
    for t in range(n_trials):
        p = np.exp(beta * Q) / np.sum(np.exp(beta * Q))
        c = np.random.choice(2, p=p)
        r = float(np.random.random() < reward_probs[c])
        Q[c] = Q[c] + alpha * (r - Q[c])
        choices.append(c)
        rewards.append(r)
    return np.array(choices), np.array(rewards)

def fit_rl(choices, rewards, n_restarts=10):
    """MLE fit with random restarts."""
    def nll(params):
        alpha, beta = params
        Q = np.zeros(2)
        ll = 0
        for c, r in zip(choices, rewards):
            log_p = beta * Q[c] - np.logaddexp(beta * Q[0], beta * Q[1])
            ll += log_p
            Q[c] += alpha * (r - Q[c])
        return -ll
    
    best = None
    for _ in range(n_restarts):
        x0 = [np.random.uniform(0.05, 0.95), np.random.uniform(0.5, 10)]
        res = minimize(nll, x0, method='L-BFGS-B',
                       bounds=[(1e-4, 1 - 1e-4), (1e-4, 30)])
        if best is None or res.fun < best.fun:
            best = res
    return best.x

# Recovery study
n_sim = 100
n_trials = 200
true_alphas = np.random.uniform(0.05, 0.95, n_sim)
true_betas  = np.random.uniform(1, 8, n_sim)
recovered = np.zeros((n_sim, 2))
for i in range(n_sim):
    ch, rw = simulate_rl(true_alphas[i], true_betas[i], n_trials, [0.7, 0.3])
    recovered[i] = fit_rl(ch, rw)

# Report recovery
rho_alpha, _ = spearmanr(true_alphas, recovered[:, 0])
rho_beta, _  = spearmanr(true_betas,  recovered[:, 1])
print(f"α recovery ρ = {rho_alpha:.2f}")
print(f"β recovery ρ = {rho_beta:.2f}")
print(f"cross-parameter ρ (recovered α vs β) = "
      f"{spearmanr(recovered[:, 0], recovered[:, 1])[0]:.2f}")
```

For hierarchical Bayesian fits, the same loop applies but you simulate multi-subject datasets and fit them with the full hierarchical model. Recovery is typically *better* than MLE because of shrinkage and uncertainty propagation.

## Model recovery: the procedure

Same logic, but for the question "can my experiment distinguish my candidate models?" Even if each model recovers its own parameters fine, the design might not let you tell which model produced the data.

1. For each candidate model M, simulate datasets with sensible parameters.
2. Fit *every* candidate model to *every* simulated dataset.
3. For each simulation, record which model "won" by your chosen criterion (LOO, WAIC, AIC/BIC).
4. Build a confusion matrix: rows = generating model, columns = best-fit model. Cells = proportion of simulations from row's model best fit by column's model.
5. The diagonal is the model-recovery rate. The identity matrix is the goal.

### What to look at

**Diagonal entries.** If `P(M_recovered = M_x | M_generating = M_x)` is low (e.g., < 0.7), your design can't reliably identify model M_x.

**Asymmetric confusion.** If model A is often misclassified as B but B is rarely misclassified as A, then evidence for A is suspect, but evidence for B can be trusted. This is the *inversion matrix* perspective Wilson & Collins emphasize.

**What's confusable with what.** Often a richer model is identified easily but a simpler one gets "absorbed" into it. The pattern of confusion tells you which theoretical contrasts your design supports.

## Combining parameter and model recovery

The full diagnostic story has four pieces:

1. **Parameter recovery for the focal model** — can we trust the parameters of the model we like?
2. **Model recovery across all candidates** — can we tell our preferred model apart from competitors?
3. **Confusion matrix interpretation** — which model comparisons can our design support?
4. **Inversion matrix** — given a winning model, how confident can we be that it generated the data?

Report all four (at least the diagonals and a brief note on off-diagonals) in any modeling paper. Without them, claims about parameters or model wins are house-of-cards.

## Things that improve recovery

- **More trials per subject.** Linear in information; recovery generally scales roughly as √N.
- **More informative trial structure.** A bandit with very asymmetric reward probabilities (e.g., 90/10) discriminates models better than 60/40. A DDM with high accuracy across difficulty levels constrains drift better.
- **Hierarchical priors.** Shrinkage stabilizes individual estimates, often dramatically. Wiecki et al. (2013) Fig 6 shows this clearly for DDM.
- **Reparameterization.** Fitting α on the logit scale and β on the log scale often helps; non-centered parameterization for hierarchical scales is almost always better.
- **Removing unidentified parameters.** If a parameter has a flat likelihood, fitting it just adds noise. Lesion-test by fixing it to a literature value and see if other parameters' recovery improves.
- **Adding a "boring" parameter that absorbs nuisance variance.** Wilson & Collins's Box 6 example: adding a perseveration term to RL improves recovery of α and β even though perseveration itself isn't the focus. This is counterintuitive but real.

## Things that hurt recovery

- **Too few trials.** The single biggest factor.
- **Too narrow a range of conditions.** If you only have one difficulty level, DDM can't separate drift and boundary.
- **Parameter trade-offs not addressed.** α/β in RL, `a`/`t` in DDM, `c`/`w` in GCM, `k`/`β` in delay discounting — these are well-known. Design experiments that break the symmetry.
- **Subjects who don't show the relevant behavior.** A subject with no learning has no information about α. A subject who always rejects has no information about λ.
- **Likelihood bugs.** A surprisingly common cause of "poor recovery" is a bug in the negative log-likelihood. If recovery is mysteriously bad, simulate-and-fit a single subject with known parameters and step through to verify the fitting machinery.

## Reporting parameter and model recovery

The minimum to include in the methods/supplement:

- Range of generating parameters and trial structure used.
- Recovery correlations per parameter, by trial count if relevant.
- Confusion matrix for model recovery across all candidate models.
- A statement of which contrasts the design supports and which it doesn't.

Wilson & Collins (2019) Box 4, Box 5, Box 6 are the templates worth emulating.

## When recovery is bad — the decision tree

1. **Is the issue a parameter trade-off?** Check cross-parameter correlations. If two parameters correlate > 0.5 in recovery, they're trading off. Fix one to a literature value, drop one, or redesign the task to dissociate them.
2. **Is the issue insufficient trials?** Re-run recovery at 2× and 4× trial counts. If it improves substantially, you need a longer study.
3. **Is the issue a likelihood/code bug?** Simulate one subject with known parameters, fit just that subject, step through the fitting code. Verify that simulated and fitted choice probabilities match.
4. **Is the issue boundary parameters?** If recovered values pile up at the boundary, switch to MAP with weakly informative priors or use HB with a regularizing group prior.
5. **Is the issue model misspecification?** Models that don't include perseveration, decay, or other nuisance processes often have inflated parameter estimates. Add the nuisance parameter and see if recovery improves.
6. **Is the issue fundamentally non-identifiable?** Some parameters simply can't be recovered from some task structures (e.g., loss aversion from gain-only gambles). No amount of fitting fixes this. Either change the task or fix the parameter.

If you've gone through this list and recovery is still bad, the paper-writing implication is: report the parameter at the *group level only*, or don't report it as an individual-difference measure. The data don't support the claim.

---

**See also:**
- `references/model_comparison.md` — model recovery and parameter recovery together constitute the diagnostic story; always run both before reporting.
- `references/reinforcement_learning.md` — α/β trade-off details and perseveration confound.
- `references/category_learning.md` — c/w trade-off in GCM; strategy heterogeneity.
- `references/hierarchical_stan.md` — hierarchical Bayesian fitting often improves recovery substantially vs per-subject MLE.
