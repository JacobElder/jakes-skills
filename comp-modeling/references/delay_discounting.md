# Delay Discounting Models

Read this when the user is fitting intertemporal choice data — choices between sooner-smaller and later-larger rewards, monetary discounting (MCQ, Kirby titrator, adjusting-amount, adjusting-delay procedures), discounting of consumable goods, or any context where the question is "how much does this person devalue future rewards."

Canonical references: Mazur (1987) for hyperbolic; Samuelson (1937) for exponential; Laibson (1997) for quasi-hyperbolic (β-δ); Ebert & Prelec (2007) for constant-sensitivity; Kirby & Maraković (1996) for the standard 27-item MCQ; Vincent (2016) for Bayesian hierarchical delay discounting; Wileyto et al. (2004) for logistic regression approach.

## The standard task

Subject chooses between a sooner-smaller (SS) reward at delay `d_s` (often 0, i.e., immediate) and a later-larger (LL) reward at delay `d_l`. From these choices we estimate a discount function `D(d)` that captures how present-value falls with delay.

Subjective value of reward `A` at delay `d`: `V = A · D(d)`.

Choice probability under softmax:

$$P(\text{LL}) = \frac{1}{1 + \exp\left[-\beta \cdot (V_{LL} - V_{SS})\right]}$$

`β` is a choice-sensitivity / inverse-temperature parameter. Higher β = more deterministic, value-driven choices; lower β = noisier.

## The four standard discount functions

**1. Exponential (Samuelson 1937):** `D(d) = exp(-k · d)`. The normative model from economics; constant rate of discounting per unit time. Time-consistent — no preference reversals.

**2. Hyperbolic (Mazur 1987):** `D(d) = 1 / (1 + k · d)`. The empirically dominant model in behavioral data. Predicts preference reversals (you'd take $100 today over $110 tomorrow, but $110 in 31 days over $100 in 30 days). `k` is the only parameter (besides choice sensitivity).

**3. Quasi-hyperbolic / β-δ (Laibson 1997):** `D(d) = β · δ^d` for `d > 0`, `D(0) = 1`. Discrete drop from immediate to delayed (the "present bias" β), then exponential discounting at rate δ. Two parameters. Popular in behavioral economics because it cleanly separates "present bias" from baseline discounting.

**4. Constant-sensitivity (Ebert & Prelec 2007):** `D(d) = exp(-(k · d)^s)`. Generalization that allows the curvature of discounting to be sensitive (s > 1) or insensitive (s < 1) to delay length. Three parameters when you include choice sensitivity. `hBayesDM::dd_cs` implements this.

There are other variants (Green-Myerson hyperboloid; Loewenstein-Prelec; Killeen's additive utility) but these four cover ~95% of applications.

## Which model to use

For most behavioral applications, hyperbolic is the default starting point — it fits better than exponential almost universally in human data. Then:

- **If the question is about present bias specifically** (e.g., self-control, addiction studies): use β-δ. The `β` parameter is the construct of interest.
- **If the question requires comparison to economic theory:** include exponential as a baseline so you can show hyperbolic beats it.
- **If you want flexibility in the curvature:** use constant-sensitivity (Ebert-Prelec).
- **If you have neural data or want a model-based regressor:** hyperbolic; trial-wise subjective values are easily computed from the fitted `k`.

Always fit and compare at least two. Don't just report a hyperbolic `k` without showing it outperforms exponential.

## A reusable likelihood (Python)

For hyperbolic + softmax, given trial-level data with `delay_ss`, `amount_ss`, `delay_ll`, `amount_ll`, and `choice` (1 = chose LL):

```python
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize

def dd_hyperbolic_nll(params, delay_ss, amount_ss, delay_ll, amount_ll, choice):
    """
    params: [log_k, beta]
        log_k = log discount rate (fitted on log scale because k spans orders of magnitude)
        beta = choice sensitivity
    """
    log_k, beta = params
    k = np.exp(log_k)
    
    V_ss = amount_ss / (1 + k * delay_ss)
    V_ll = amount_ll / (1 + k * delay_ll)
    
    p_ll = expit(beta * (V_ll - V_ss))
    p_ll = np.clip(p_ll, 1e-9, 1 - 1e-9)
    
    ll = choice * np.log(p_ll) + (1 - choice) * np.log(1 - p_ll)
    return -np.sum(ll)

# Fit
res = minimize(dd_hyperbolic_nll, x0=[np.log(0.01), 0.01],
               args=(delay_ss, amount_ss, delay_ll, amount_ll, choice),
               method='L-BFGS-B',
               bounds=[(np.log(1e-6), np.log(10)), (1e-5, 5.0)])
log_k_hat, beta_hat = res.x
k_hat = np.exp(log_k_hat)
```

**Critical implementation note:** `k` spans many orders of magnitude across subjects (typically 10⁻⁴ to 10⁻¹) and should be fit on the log scale. Linear-scale fitting will give terrible results. All hierarchical implementations (hBayesDM, Vincent's bayesianMatchingPennies framework) do this.

## Hierarchical Bayesian fitting

Use `hBayesDM` for standard delay discounting tasks. It implements:
- `dd_exp` — exponential
- `dd_hyperbolic` — hyperbolic (the most common choice)
- `dd_cs` — constant sensitivity

```r
library(hBayesDM)
fit <- dd_hyperbolic(data = your_data, niter = 4000, nwarmup = 1000, 
                     nchain = 4, ncore = 4)
plot(fit)
printFit(fit, ic = "looic")
```

Required data columns: `subjID`, `delay_later`, `amount_later`, `delay_sooner`, `amount_sooner`, `choice` (0 = sooner, 1 = later).

For β-δ or other models not in hBayesDM, write Stan code. Vincent (2016) provides templates.

## The MCQ shortcut (Kirby titrator)

Kirby & Maraković's 27-item Monetary Choice Questionnaire is a fixed set of choices specifically designed so that the pattern of choices maps onto a few candidate `k` values. The traditional scoring assigns each subject a discrete `k` based on which value best explains their pattern — no fitting required.

The MCQ approach is fast and reliable for screening, but it gives a coarse `k` estimate and assumes a discrete distribution. For finer estimates, fit hyperbolic to the MCQ choices using the regular likelihood — it works fine and gives you continuous `k` plus uncertainty.

Gray, Amlung, Acker, Sweet & MacKillop (2016) "Item-by-Item Analysis" extends the MCQ scoring; Kaplan et al. (2016) propose 5- and 21-item versions if you need a shorter assessment.

## Parameter ranges to expect

From large normative samples:

- **Hyperbolic `k`:** ~10⁻⁴ to ~10⁻¹ per day; healthy young adults median ~0.01 (i.e., a $100 reward in 100 days is worth ~$50 now); clinical addiction populations often 10–100× higher.
- **β-δ:** `β` typically 0.6–0.9 (present bias), `δ` typically 0.99–0.9999 per day (very mild long-run discounting).
- **Choice sensitivity** depends on reward scale — for typical $10–$100 tasks, β around 0.005–0.1.

`k` values outside this range — especially `k > 1` or `k < 10⁻⁵` — usually indicate a subject who responded almost-always-one-way or a bug in the units (days vs years).

## Common pitfalls in delay discounting fitting

- **Fitting `k` on the linear scale.** Don't. Always fit `log(k)` and exponentiate. Otherwise you get terrible likelihood surfaces.
- **Units of delay matter.** A subject's `k` per-day is 365× their `k` per-year. Document and standardize.
- **Subjects who always choose LL (or always SS) give degenerate `k` estimates** (k → 0 or k → ∞). Either flag/exclude them or use hierarchical Bayes with informative priors to handle them gracefully.
- **`k` and `β` (choice sensitivity) trade off** when subjects are noisy. A subject who's 60% LL across the board can be fit as low-k + low-β or moderate-k + low-β. Hierarchical priors help; reporting joint posteriors helps more.
- **Magnitude effects.** Discounting rates are not constant across reward sizes — typically `k` is lower for larger rewards (the magnitude effect). If your task uses a fixed magnitude, fine; if it varies, model the magnitude dependence (Vincent 2016 has variants).
- **Domain effects.** Discounting for money differs from discounting for primary rewards (food, drugs). Don't generalize across domains.
- **Hyperbolic vs exponential identification depends on delay range.** If all your delays are short or all are long, the two models predict very similar choices and your comparison won't separate them. Vary delays across at least one order of magnitude.
- **MCQ vs. fitted estimates.** MCQ `k` and fitted `k` correlate well but aren't identical. Don't compare them across studies as if they were the same metric.
- **Indifference points and AUC.** Some studies report indifference points (the SS amount equivalent to a fixed LL amount at each delay) and area-under-the-curve metrics. These are model-free; you can supplement model-based estimates with them as robustness checks.

## When delay discounting connects to other models

- **Choice variability ↔ DDM.** Several papers fit DDM to intertemporal choice (Rodriguez, Turner & McClure 2015; Amasino et al. 2019). The drift rate is `β · (V_LL − V_SS)`. This gives RT-based information about the choice process on top of the value-based information.
- **Discounting as RL.** In tasks where subjects learn about delayed rewards through experience, you might use a γ-discounted RL framework instead. The two parameterizations are related but address different paradigms.
- **Discounting as risk.** Some accounts argue delay discounting reflects implicit uncertainty (Sozou 1998); models of risk and time discounting share structure. Useful when the task has both delay and probability dimensions.

## What to report

- Discount function chosen and rationale.
- Per-subject `k` (on log scale or with log-transformed summary stats).
- Comparison to at least one alternative discount function (LOO or WAIC).
- Choice consistency / sensitivity parameter.
- Whether estimates were derived from MCQ scoring or from full likelihood fitting.
- For β-δ specifically, both `β` and `δ` with uncertainty; interpret in terms of present bias vs long-run discounting.
