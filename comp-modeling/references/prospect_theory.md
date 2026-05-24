# Prospect Theory and Risky Choice

Read this when the user is modeling decisions under risk — gambles, lotteries, mixed gain/loss prospects, loss aversion experiments, the standard risky-choice tasks (Holt-Laury, Sokol-Hessner gambles, multiple price lists), or comparing expected utility to prospect-theory accounts.

Canonical references: Kahneman & Tversky (1979, *Econometrica*) for original PT; Tversky & Kahneman (1992, *J. Risk Uncertain.*) for cumulative prospect theory; Wu & Gonzalez (1996), Gonzalez & Wu (1999) for parameter estimation methods; Sokol-Hessner et al. (2009) for the standard mixed-gambles loss aversion task.

## The three pieces of prospect theory

PT modifies expected utility on three fronts:

**1. Reference-dependent value function.** Outcomes are coded as gains or losses relative to a reference point (often the status quo). The value function is concave over gains, convex over losses, and steeper for losses than gains:

$$v(x) = \begin{cases} x^{\alpha} & x \geq 0 \\ -\lambda \cdot (-x)^{\beta} & x < 0 \end{cases}$$

- α ∈ (0, 1]: gain-side curvature (risk aversion over gains). Tversky-Kahneman estimate: 0.88.
- β ∈ (0, 1]: loss-side curvature. Often constrained α = β. Tversky-Kahneman estimate: 0.88.
- λ ≥ 0: loss aversion. Losses weighted λ times more than equivalent gains. Tversky-Kahneman estimate: 2.25.

Constraining α = β and using a single curvature parameter is very common and improves identifiability — use it unless the design specifically targets gain/loss asymmetric curvature.

**2. Probability weighting.** Subjective decision weights are a nonlinear function of objective probabilities — small probabilities overweighted, moderate-to-large probabilities underweighted. The Tversky-Kahneman (1992) one-parameter form:

$$w(p) = \frac{p^{\gamma}}{\left(p^{\gamma} + (1-p)^{\gamma}\right)^{1/\gamma}}$$

γ controls the inverse-S curvature. TK estimate ~0.61–0.69. Empirical estimates across the literature mostly land in 0.5–0.9. γ = 1 recovers linear weighting (expected utility).

The Prelec (1998) two-parameter form gives separate curvature and elevation control:

$$w(p) = \exp\left(-\delta \cdot (-\ln p)^{\gamma}\right)$$

Use Prelec when you specifically want to dissociate curvature (sensitivity to probability changes) from elevation (overall optimism/pessimism). Goldstein-Einhorn (1987) is another two-parameter weighting function with the same dissociation.

**3. Composition rule.** In *original* PT (1979), `V(prospect) = Σ w(pᵢ) v(xᵢ)` — each outcome's probability is weighted independently. This can violate stochastic dominance for some configurations. In *cumulative* PT (1992), weights are applied to cumulative probabilities (rank-dependent), which restores dominance. Use CPT for any prospect with >2 outcomes or for mixed gain/loss prospects; use OPT for two-outcome gambles where the simpler form suffices.

## Common tasks and the model you want

| Task | What it measures | Default model |
|------|-----------------|----------------|
| Mixed gambles (Sokol-Hessner) | λ, α (gain/loss symmetry assumed) | PT with α=β, no probability weighting (single p = 0.5) |
| Holt-Laury multiple price list | Risk aversion (CRRA or PT curvature) | Either EU with CRRA or PT-α |
| Gain-only gambles vs sure thing | α, γ | PT or CPT with probability weighting |
| Loss-only gambles vs sure loss | β, γ | Same |
| Mixed prospects with multiple outcomes | Full CPT | CPT (Tversky-Kahneman 1992) |
| Bechara IGT | Layered PT-like utility on top of RL update | PVL-delta or PVL-decay (see RL reference) |

For the Sokol-Hessner mixed-gambles task specifically, you get a clean λ estimate because the gambles are coin-flip 50-50 between a gain and a loss; probability weighting cancels out and you can fit α, λ alone. This is why it's the workhorse for measuring loss aversion.

## A reusable likelihood for the mixed-gambles task

For each trial, the subject faces a 50/50 gamble (gain G, loss L) vs a sure thing of 0. Choice = 1 if gamble accepted.

Subjective utility of the gamble:
$$U_{gamble} = 0.5 \cdot G^{\alpha} - 0.5 \cdot \lambda \cdot |L|^{\alpha}$$

Sure thing utility = 0. Softmax acceptance probability with sensitivity μ:
$$P(\text{accept}) = \frac{1}{1 + \exp(-\mu \cdot U_{gamble})}$$

```python
import numpy as np
from scipy.special import expit  # logistic sigmoid
from scipy.optimize import minimize

def pt_mixed_gambles_nll(params, gains, losses, accepted):
    """
    params: [alpha, lambda, mu]
    gains, losses: trial-level gain/loss magnitudes (losses positive in magnitude)
    accepted: int array 1=accepted gamble, 0=rejected
    """
    alpha, lam, mu = params
    U = 0.5 * gains**alpha - 0.5 * lam * losses**alpha
    p_accept = expit(mu * U)
    p_accept = np.clip(p_accept, 1e-9, 1 - 1e-9)  # numerical safety
    ll = accepted * np.log(p_accept) + (1 - accepted) * np.log(1 - p_accept)
    return -np.sum(ll)

res = minimize(pt_mixed_gambles_nll, x0=[0.9, 1.5, 0.5],
               args=(gains, losses, accepted),
               method='L-BFGS-B',
               bounds=[(0.05, 2.0), (0.1, 10), (1e-4, 10)])
```

For hierarchical Bayesian estimation, `hBayesDM::ra_prospect` implements exactly this with sensible priors on α, λ, ρ (the inverse-temperature equivalent). It's a one-line call and is the right default.

## Cumulative prospect theory likelihood for multi-outcome prospects

For a prospect with outcomes `x₁ < x₂ < ... < xₙ` and probabilities `p₁, ..., pₙ`, separate gains and losses around the reference, then apply rank-dependent cumulative weighting separately to each side. The decision weight for outcome `xᵢ` on the gain side is:

$$\pi_i^+ = w^+(p_i + p_{i+1} + \cdots + p_n) - w^+(p_{i+1} + \cdots + p_n)$$

and analogously on the loss side using `w⁻`. The prospect value:

$$V = \sum_{i: x_i \geq 0} \pi_i^+ \cdot v(x_i) + \sum_{i: x_i < 0} \pi_i^- \cdot v(x_i)$$

When fitting choices between two prospects, take `V_A - V_B` and pass it through a softmax/logit choice rule. Implementing this carefully is finicky — `JanaJarecki/cognitivemodels` (R) has a clean implementation; or write it yourself with the equations above.

## Parameter ranges to expect

From TK92 and replications (Camerer & Ho 1994; Wu & Gonzalez 1996; Gonzalez & Wu 1999; Booij et al. 2010; many more):

- **α (gain curvature)**: 0.6–1.0, modal ~0.85–0.9
- **β (loss curvature)**: 0.6–1.0, often constrained to equal α
- **λ (loss aversion)**: median ~1.5–2.5; substantial individual variation; some subjects show λ < 1 ("loss-seeking"); λ > 4 should make you suspicious of the fit
- **γ (probability weighting curvature)**: 0.5–0.9
- **δ (probability weighting elevation, Prelec)**: 0.6–1.2

If your estimates are far outside these ranges, check: (1) your reward scaling — λ depends on whether you parameterized losses as positive magnitudes or as signed values; (2) your data quality — a subject who accepts/rejects almost everything won't yield identifiable λ; (3) your priors if HB.

## Common pitfalls in PT fitting

- **λ and the choice sensitivity (μ/ρ) trade off heavily.** A subject who always rejects gambles can be modeled as high λ + low μ or moderate λ + high μ. Recovery is poor unless the design includes a wide range of gain/loss ratios. Sokol-Hessner et al. designed their task specifically to constrain this — use those gambles or a similar grid.
- **Reference point assumptions matter.** PT assumes outcomes are coded relative to *something*. In most lab tasks the reference is 0 (the status quo before the trial), but in tasks with expectations (e.g., after a prior gain) the assumed reference can be wrong and bias λ.
- **Gain-only or loss-only tasks can't estimate λ.** Loss aversion is the *ratio* of slopes around the reference; if all outcomes are on one side, λ is unidentified. Mix gains and losses or fix λ to a literature value.
- **CPT vs OPT diverge mostly for >2 outcomes with mixed signs.** For two-outcome gambles in the same domain, they're essentially equivalent. Use OPT for simplicity unless you have the structure that distinguishes them.
- **Subjects who never accept (or always accept) yield degenerate likelihoods.** Filter or flag these; one common cutoff: at least 25% of each response on a balanced design.
- **The probability-weighting function `w(p)` becomes flat near p = 0.5.** Tasks that only use p = 0.5 gambles can't estimate γ — the data just don't constrain it. Either fix γ to 1 (no weighting) or include a range of probabilities.
- **Tversky-Kahneman's median estimates (α=0.88, λ=2.25, γ=0.61) are population medians from one experiment.** They're useful prior centers but should not be cited as universal constants.

## A note on the elicitation method

Two main methods to estimate PT parameters:

1. **Certainty equivalents.** Subject states or chooses what sure amount equals a given gamble. You estimate parameters by matching `v(CE) = w(p) v(x)`. Clean math but requires many trials and is sensitive to anchoring/random response.
2. **Choice tasks.** Subject chooses between prospects, you fit the parameters that maximize choice likelihood. Robust and scales to lots of subjects. This is the default for behavioral/clinical work.

If the user is starting fresh, choice tasks are easier to deploy and analyze. Use CE-based estimation only if the design demands precise per-subject estimates with few subjects.

## Connections to other models

- **Prospect Valence Learning (PVL)** models for the Iowa Gambling Task (Ahn et al. 2008; 2011; 2014) plug a PT-like utility (`u(x) = x^α` for gains, `-λ(-x)^α` for losses) into a delta-rule learner. See `reinforcement_learning.md`.
- **Risk-sensitive reinforcement learning** (Niv et al. 2012) uses asymmetric learning rates to produce PT-like value functions endogenously.
- **Anticipated utility / regret theory** are alternatives to PT; usually only worth fitting if the design specifically targets counterfactual feedback.

## Things to always do when reporting a PT fit

- Show the fitted value function and weighting function shapes for the group, not just numerical parameter estimates.
- Report individual-subject fits with uncertainty intervals, especially for λ.
- Compare against expected utility (set γ = 1, α = β = 1, λ = 1, freely fit choice sensitivity) as a baseline. If PT doesn't beat EU on LOO/WAIC, you've found nothing.
- Compare against a "linear utility with loss aversion" model (α = β = 1, λ free) to see whether nonlinear curvature is doing real work.
- Run parameter recovery — λ recovery in particular depends critically on the gamble grid.
