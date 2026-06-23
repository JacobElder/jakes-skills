# Does Low Log-Loss Guarantee Calibration?

**Short answer: No.** Low log-loss on held-out data is a necessary but not sufficient condition for calibration. Your PM's request is reasonable — proper scoring rules do incentivize honest probabilities — but a single aggregate metric cannot tell you whether the model is locally calibrated, and that local structure is exactly what users will see when they read a confidence number.

---

## The identity that explains what log-loss actually measures

Log-loss (cross-entropy loss, NLL) and KL divergence are the same objective:

```
H(p̂, q) = H(p̂) + KL(p̂ ‖ q)
```

Minimizing log-loss over your model `q` with `p̂` = the empirical label distribution is equivalent to minimizing `KL(p̂ ‖ q)`, which is maximum likelihood. So good held-out log-loss means the *average* KL from the empirical distribution to your predicted distribution is small.

The word "average" is doing a lot of work there.

---

## Why low average log-loss does not guarantee calibration

A model can have low average log-loss while being miscalibrated in systematic ways. Here are the specific failure modes:

**1. High confidence on easy subgroups, low confidence on hard subgroups, averaging to a good number.**
If 90% of your test set is the dominant class and the model is overconfident on those while being incoherent on the minority class, the aggregate loss can look fine. Users of the product, however, will be shown wrong confidences on the hard cases — which are often exactly the cases they most need accurate probabilities for.

**2. Log-loss is sensitive to confident mistakes, but not to the shape of miscalibration.**
Log-loss penalizes overconfidence harshly (as `q → 0` on a positive example, the loss → ∞). This sensitivity is a *feature* for training and a *liability* for treating log-loss as a calibration certificate: the model learns to avoid catastrophic confident errors, but can still be systematically off in the 0.6–0.8 confidence band where the loss gradient is modest.

**3. Proper scoring rules incentivize honest reporting in expectation — over the training/test distribution.**
Log-loss is a **strictly proper scoring rule**, meaning the expected score is uniquely minimized by reporting the true conditional probabilities. But "incentivizes calibration" means the optimization pressure pushes toward calibration; it does not mean calibration is the result for every model class, every data regime, or every subpopulation.

---

## What proper scoring rule guarantees, precisely stated

A strictly proper scoring rule guarantees:

> Under the distribution from which the data are drawn, the **expected** loss is minimized if and only if the model reports the true probabilities.

This is an in-expectation, population-level statement. It does not say:
- The model *achieved* that minimum (finite data, model capacity, and training dynamics all affect this).
- The model is calibrated **in every confidence bin** or every subgroup.
- A model with lower log-loss than another is necessarily better-calibrated.

The Brier score (`Σ (q − y)²`) is another strictly proper scoring rule and decomposes explicitly into a **calibration term** and a **refinement (sharpness) term** (Murphy decomposition). But the same caveats apply: low Brier score tells you the model is jointly calibrated and sharp in aggregate, not that it is calibrated everywhere users will encounter it.

---

## How to actually check and fix calibration

**Check with a reliability diagram / ECE.**
Bin the model's predicted probabilities (e.g., ten bins from 0.0–0.1 up to 0.9–1.0). Within each bin, compute the fraction of true positives. A perfectly calibrated model falls on the diagonal. Expected Calibration Error (ECE) averages the absolute deviation, weighted by bin size. This is the right diagnostic — it shows *where* the miscalibration lives, not just whether it exists.

For a multiclass classifier, do this per-class (one-vs-rest reliability diagrams) and averaged; a model can be well-calibrated for the dominant class and badly calibrated for others.

**Fix with temperature scaling.**
Temperature scaling divides all logits by a single learned scalar `T > 0` before the softmax:

```
q_T(y | x) = softmax(z / T)
```

`T > 1` softens the distribution (reduces overconfidence); `T < 1` sharpens it. This is literally a one-parameter cross-entropy minimization on a held-out calibration set — it finds the `T` that best aligns predicted confidence with observed accuracy. It does not change the model's *decisions* (argmax is invariant to scaling), only the confidence values. It is cheap, interpretable, and works well in practice for neural classifiers.

More expressive options (isotonic regression, Platt scaling, histogram binning) exist if temperature scaling is insufficient, but they need a separate calibration split to avoid overfitting to the test set.

---

## What to tell your PM

The model's log-loss being low is a good sign — it means the model learned something real from the data and is not catastrophically wrong on average. But before exposing the raw softmax probabilities to users as "confidence," you need to:

1. **Plot reliability diagrams** on held-out data stratified by subgroup if subgroup performance matters. Look for systematic overconfidence (predicted probability > observed accuracy) or underconfidence.
2. **Compute ECE** as a single summary number. Acceptable values are domain-dependent, but ECE > 0.05 is typically meaningful miscalibration for user-facing probabilities.
3. **Apply temperature scaling** on a separate calibration split if you see miscalibration. This is a one-hour fix, not a model retrain.
4. **Recheck ECE and the reliability diagram** after scaling, and monitor it in production as the data distribution drifts.

The core principle to communicate to the PM: log-loss tells you your model's *average* predictive quality is good. Showing a user "78% confident" is a claim about a specific prediction, not the average. Those two things are only equivalent if the model is calibrated, which requires an explicit check.
