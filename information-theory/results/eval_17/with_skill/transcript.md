# Transfer Entropy: What It Is, How It Differs, and What Will Fool You

You have two coupled time series and want to know the direction of influence. Transfer entropy is the right starting point — but it comes with a set of failure modes that are easy to miss if you only read the formula. Here is an exact account of what it is, how it differs from mutual information and Granger causality, and where things go wrong.

---

## 1. The core objects, precisely named

**Mutual information (MI)** is symmetric:

```
I(X; Y) = H(X) − H(X|Y) = H(Y) − H(Y|X)
```

It measures *how far X and Y are from independent* — the KL divergence from the joint to the product of marginals. It captures any statistical dependence, linear or not, but it has no direction and no temporal structure. If you ask "are these series coupled?" MI is appropriate. If you ask "which drives which?", MI is the wrong tool — it will give the same answer regardless of how you label the variables.

**Transfer entropy (TE)** adds temporal conditioning. Schreiber (2000) defined:

```
TE_{X→Y} = I( Y_{t+1} ; X_t^(l) | Y_t^(k) )
           = H( Y_{t+1} | Y_t^(k) ) − H( Y_{t+1} | Y_t^(k), X_t^(l) )
```

where `Y_t^(k)` is Y's own k-step history and `X_t^(l)` is X's l-step history. Read it as: *how much does X's past reduce uncertainty about Y's next step, beyond what Y's own past already tells us?*

The asymmetry is built in by construction. `TE_{X→Y} ≠ TE_{Y→X}`, and that asymmetry is the entire point. You should compute and report **both directions** every time.

---

## 2. How TE differs from mutual information

The difference is conditioning on the target's own history. Plain MI between `X_t` and `Y_{t+1}` captures *any* shared information, including the portion explainable by Y's own past dynamics alone. If both series are driven by a shared autocorrelated background, MI will be high even with zero cross-series coupling.

TE removes Y's self-prediction before asking what X adds. This is what makes it directed: a series that improves prediction of another beyond that other's own past is providing *new* predictive information, not merely correlating with it.

That said, TE is still a measure of **predictive information**, not causation in the interventional sense. It is not the same as asking "if I force X to a value, what happens to Y?" Keep this distinction clear in interpretation.

---

## 3. How TE differs from Granger causality

Granger causality asks whether X's past improves a *linear* model of Y's future beyond Y's own linear past. The standard test fits two VAR models and compares their residuals.

The relationship to TE is exact under Gaussian linear assumptions: for jointly Gaussian linear processes, Geweke's (1982) Granger statistic equals `2 · TE` (in nats). They are mathematically equivalent in that regime.

The practical implication: if your series are well-described by a linear VAR, Granger is simpler, better-understood, comes with standard test statistics and power calculations, and will give you the same directional conclusion as TE. Reach for TE specifically when:

- You suspect nonlinear coupling (e.g., threshold effects, multiplicative interactions, chaotic dynamics).
- You want a model-free characterization that does not assume linearity.

Do not sell TE as "model-free causality." It is directed *predictive* information, not interventional causality. It inherits every confound that Granger causality inherits.

---

## 4. The confounds TE inherits from Granger

**Hidden common driver.** If an unmeasured variable Z drives both X and Y, TE will show coupling in both directions even when there is no direct link between X and Y. This is exactly the Granger spurious-causality problem. The fix is **conditional TE**: `TE_{X→Y|Z} = I(Y_{t+1}; X_t^(l) | Y_t^(k), Z_t^(m))` — condition on Z's history to partial out the common driver. This requires measuring Z, which is not always possible.

**Instantaneous coupling.** If X and Y interact at the same time step (common in discretely sampled continuous processes), standard TE can be ambiguous about direction. Neither TE nor Granger handles this well without additional assumptions.

**Causal inference caution.** Predictive improvement is not intervention. High `TE_{X→Y}` means X's past helps forecast Y's future; it does not mean that forcing X to a value would change Y. If you want the latter, you need structural models or experiments.

---

## 5. Estimation: where most TE analyses go wrong

TE is harder to estimate than ordinary MI, and ordinary MI is already dangerous to estimate naively.

### The bias problem is worse here

Plug-in MI from a contingency table is biased **upward** by approximately `(K_X − 1)(K_Y − 1) / (2N)` nats. TE conditions on history, so the joint state space is `K^(k + l + 1)` cells — it grows exponentially with history length. With `k = 2, l = 2` and a 4-symbol alphabet you have `4^5 = 1024` possible states; you need far more than 1024 observations to populate them adequately. The plug-in bias is large, the cells are sparse, and the estimate becomes noise.

### The surrogate null is not optional

A positive TE estimate is not evidence of coupling. A TE above its surrogate null distribution is. The procedure:

1. Fix `Y` and destroy the temporal relationship from X by shifting or block-permuting X's values.
2. Recompute TE on the surrogate.
3. Repeat many times (200–999 is standard).
4. Your measured TE is only meaningful if it clearly exceeds the surrogate distribution.

The shuffle mean is your empirical bias floor. If your measured TE is indistinguishable from shuffled data, you have noise. The permutation null is implemented in `scripts/entropy_mi_estimators.py`.

### Choose history length k honestly

The target history length `k` is a model parameter, not a nuisance. Too short a `k` leaves predictable structure in the residual that the source X can "explain," inflating `TE_{X→Y}`. Set `k` based on Y's own autocorrelation structure or by AIC over univariate models of Y before adding any cross-series terms. Do not choose `k` by maximizing TE.

### Continuous data: use KSG, not bins

For continuous-valued series, binning TE inherits all the discretization sensitivity of binned MI, amplified by the extra conditioning dimensions. The Kraskov–Stögbauer–Grassberger (KSG) k-nearest-neighbor estimator is the appropriate default. The closed-form Gaussian case and a discrete TE with permutation null are both in `scripts/entropy_mi_estimators.py`; the Gaussian version cross-checks against a known linear VAR where directionality should be recoverable and the reverse direction should be near zero.

---

## 6. A summary of what to do

| Step | What to do |
|---|---|
| Name the object | TE is directed conditional MI, not causal. State this explicitly. |
| Choose k and l | From autocorrelation structure of each series; do not tune to maximize TE. |
| Estimate TE | Both directions: `TE_{X→Y}` and `TE_{Y→X}`. |
| Validate with surrogate null | Permute or shift X, recompute TE 200+ times, compare observed to null distribution. |
| Check for hidden drivers | If a plausible common cause Z exists, compute conditional TE given Z's history. |
| Bias-correct or bootstrap | Never report a raw point estimate without an uncertainty interval or comparison to null. |
| Continuous data | Use KSG estimator, not fixed bins. |
| Linear data | If the relationship is linear-Gaussian, Granger/VAR gives the same answer with better-understood sampling properties. |

---

## 7. The one-paragraph honest summary

Transfer entropy is mutual information with a temporal arrow nailed to it: it asks how much X's past reduces uncertainty about Y's next step beyond Y's own past. That conditioning is what makes it directional and is what MI lacks. For linear-Gaussian processes it reduces to Granger causality exactly, so reach for TE when linearity is genuinely in doubt. The hard part is estimation, not the formula: the joint state space grows exponentially with history length, plug-in estimates are biased upward exactly as ordinary MI is but worse, and a positive TE without a surrogate null comparison is evidence of nothing. The hidden-common-driver confound is inherited directly from Granger and is not solved by switching from VAR to TE. Get the surrogate null right, choose k from the target's own dynamics, and use KSG for continuous data.
