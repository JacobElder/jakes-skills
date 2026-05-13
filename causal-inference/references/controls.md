# Controls: a structural taxonomy

The question "should I control for Z?" has no answer without a DAG. The same observed correlation pattern (Z correlates with X and Y) is produced by *every* structural relationship below — confounder, mediator, collider, proxy. The DAG decides which one Z actually is, and therefore whether controlling helps or hurts.

This is the canonical lookup table. It draws on Cinelli, Forney, and Pearl's "Crash Course in Good and Bad Controls" (2022), Wysocki, Lawson, and Rhemtulla (2022) on confound-blockers, and Steiner and Kim (2016) on bias amplification.

## Good controls (block back-door paths without opening new ones)

### Classic confounder

```
   Z (observed)
  ↙ ↘
  X → Y
```

Z is a common cause of X and Y. Controlling for Z closes the back-door path X ← Z → Y, removing spurious correlation. **Control.**

### Confound-blocker

A variable that isn't itself a confounder but lies *on* a confounding path between an unobserved confounder and X or Y. Conditioning on it blocks the back-door even though the true confounder is unmeasured.

```
   U (unobserved)
   ↓
   Z
   ↓
   X → Y    with U → Y also
```

Controlling for Z blocks the back-door from X through U to Y. The textbook confounder doesn't have to be measured directly — any variable on the path will do. **Control.**

### Cause of Y only, unrelated to X

```
   Z → Y
   X → Y
```

Z affects Y but not X. Doesn't help with bias (there's no confounding to remove) but reduces residual variance in Y. **Control if precision matters; otherwise neutral.**

## Bad controls (induce or amplify bias)

### Mediator (overcontrol bias)

```
   X → Z → Y
```

Z is on the causal path from X to Y. Controlling for Z blocks the very effect you're trying to estimate, giving the *direct* effect rather than the *total* effect. **Don't control for Z** unless the direct effect is specifically what you want.

The same applies to descendants of mediators. Anything downstream of a mediator partially blocks the mediated path when conditioned on.

### Collider

```
   X → Z ← Y    or    X → Z ← U → Y
```

Z is a common effect. By default the path is closed (information doesn't flow through a collider). **Conditioning on Z opens the path**, creating spurious correlation between X and Y where none existed. Same applies to descendants of colliders.

This is the canonical structural mistake. Conditioning on a downstream variable — by including it in a regression, by selecting the sample on it, by stratifying — can produce strong "effects" that are entirely artifacts.

### M-bias (the pre-treatment trap)

```
   U1 → Z ← U2
   ↓        ↓
   X        Y
```

Z is pre-treatment, correlated with both X and Y, looks like a textbook confounder. It's a *collider* between two unobserved confounders that affect X and Y separately. Controlling for Z opens a spurious path U1 ← Z → U2 connecting X to Y, creating bias from nothing.

The lesson: pre-treatment status is not a license to control. The DAG is.

### Bias amplification (near-instrument trap)

```
   Z → X → Y
       ↑
       U (unobserved)
       ↓
       Y
```

Z is a strong predictor of treatment but weak (or zero) on outcome — an instrument or near-instrument. With unobserved confounding present, controlling for Z **strictly increases bias** from the unmeasured confounder.

Mechanism: conditioning on Z removes Z's contribution to X's variation. The remaining variation in X is now disproportionately driven by U, the unmeasured confounder. U becomes a *stronger* confounder than it was unconditionally. The "great covariate" intuition (it correlates with treatment, so controlling must help) is exactly backwards.

If you have an instrument-like Z and unmeasured confounding, use Z as an actual instrument. Don't put it in the regression.

### Cancellation of offsetting biases

When two confounders X and U push bias in opposite directions in the unadjusted estimate, they partially cancel — the naive correlation can be relatively close to the true effect. Adjusting for X removes its contribution and *unmasks* U's bias, leaving an estimate further from the truth than the unadjusted one.

The unsettling implication: a confounded estimate may sometimes be closer to the truth than a partially-adjusted one. Without knowledge of the full confounding structure, you can't tell which is which. This is why sensitivity analysis matters when full identification isn't possible.

### Selection bias / collider stratification

```
   X → S ← Y
```

S is a sample-selection indicator (whether someone is in the dataset). If selection depends on both X and Y, the sample itself is a conditioned-on collider. Hospitalized patients, surveyed users, employed workers, app users — all are selected populations. Effects estimated within them can be artifacts of the selection.

### Proxy under measurement error

```
   X → Z
   X → Y
```

Z is downstream of X with no path to Y — pure proxy. If X is measured cleanly, Z is bias-neutral. But if X is measured *with error* (X_measured is a noisy version of the true X), then Z and X_measured are both imperfect indicators of the same underlying construct. Controlling for Z partials out shared variance with X_measured that includes real signal — *attenuating* the estimate.

Practical rule: don't control for a downstream proxy of a noisily-measured predictor. You'll bleed away the very effect you're trying to estimate.

## What about post-treatment variables more generally?

The folk rule "never condition on post-treatment variables" is wrong. Post-treatment variables that are neither mediators nor descendants of the outcome are bias-neutral. In some selection-bias structures, conditioning on a post-treatment variable is the *only* way to recover the effect.

The rule is the same as for pre-treatment variables: classify by structural role, not by temporal position.

## What kills naive practice

Four pieces of dominant folklore that the structural framework refutes:

- **"Control for all pre-treatment variables that predict treatment."** False. M-bias colliders and near-IVs both fit this description.
- **"Never control for post-treatment variables."** False. Some post-treatment variables are neutral; some are necessary.
- **"More controls is safer."** False. Adding the wrong control can move an unbiased estimate to a biased one.
- **"If Z correlates with both X and Y, control for Z."** False. The same correlation pattern fits *every* DAG type — confounder, mediator, collider, proxy. Statistical association isn't sufficient.

## The Table 2 Fallacy

When you fit `Y ~ X + Z1 + Z2 + ...` to estimate the effect of X, the coefficient on X is (under the right adjustment) interpretable as a causal effect — but the coefficients on Z1, Z2 etc. are *not* generally interpretable the same way. Even when Z is a *valid* control (correctly closes the back-door for X→Y), its own coefficient is typically biased for its own effect on Y.

Why: identifying X→Y requires blocking back-doors from X to Y. Identifying each Z→Y would require an "all-causes regression" — every direct cause of Y in the model. That much stronger condition almost never holds. So the focal effect can be cleanly identified while every other coefficient in the same regression is biased.

Westreich and Greenland (2013) named this the **Table 2 Fallacy** — interpreting every coefficient in the standard "Table 2" of a regression paper as a causal effect. Hünermund and Louw (2024) extended it: a control's coefficient can vary wildly across different valid adjustment sets even though the focal coefficient is stable.

Practical implication: when reporting a causal estimate, only the targeted coefficient deserves a causal interpretation. The rest describe model fit.

## A workflow for choosing controls

1. **Identify the focal effect.** Which X → Y? What estimand (total / direct effect)?
2. **Draw the DAG** with X, Y, candidate controls, and any plausible unmeasured confounders (use U).
3. **Classify each candidate control** by structural role using the taxonomy above.
4. **Identify alternative plausible DAGs.** The same variable is often *plausibly* a confounder *or* a mediator. Be explicit about which.
5. **Choose an adjustment strategy.** Single DAG with valid adjustment → adjust. Multiple DAGs with the same valid set → adjust and report robustness. Multiple DAGs with different sets → run multiple analyses and present the range. No valid adjustment → consider IV, front-door, sensitivity analysis, or honestly report the limitation.

## Tools

For non-trivial DAGs, **dagitty** (https://www.dagitty.net) lets you draw the graph and ask it for valid adjustment sets directly. Removes the human-error step from manual structural reasoning.

## References

Cinelli, C., Forney, A., & Pearl, J. (2022). *A Crash Course in Good and Bad Controls.* Sociological Methods & Research.

Wysocki, A. C., Lawson, K. M., & Rhemtulla, M. (2022). *Statistical Control Requires Causal Justification.* Advances in Methods and Practices in Psychological Science 5(2).

Steiner, P. M., & Kim, Y. (2016). *The Mechanics of Omitted Variable Bias.* Journal of Causal Inference 4(2).

Westreich, D., & Greenland, S. (2013). *The Table 2 Fallacy.* American Journal of Epidemiology 177(4).

Hünermund, P., & Louw, B. (2024). *On the Nuisance of Control Variables in Causal Regression Analysis.* Organizational Research Methods 28(1).
