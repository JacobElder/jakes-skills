# AIC vs BIC Disagreement: Which Do You Report?

The short answer: **report both, explain why they disagree, and pick the one whose
target matches your scientific question.** The framing "which do I report" is itself
the category error — the disagreement is not a problem to resolve by picking a winner,
it is *information*.

---

## Why they disagree is not mysterious

AIC and BIC are not two estimates of the same thing. They estimate different quantities
and are each correct for their own target.

| | AIC | BIC |
|---|---|---|
| What it estimates | Out-of-sample predictive deviance (expected KL from truth to model) | Log marginal likelihood (approximated via Laplace) |
| Optimal property | **Efficient** — selects the best-predicting model | **Consistent** — selects the true model (if it's in your set) |
| Assumes a "true model" exists in the candidate set? | No | Yes |
| Penalty | `2k` | `k · ln N` |
| Asymptotic behavior | May keep a slightly over-complex model if it predicts better | Converges to the true model under its assumption |

BIC's penalty is `k · ln N`. For `N > 7`, that is always larger than AIC's `2k`, so
BIC is systematically harder on complexity. The gap between the two criteria grows with
`N`. When they disagree, as they do here, it means: **the richer model predicts better,
but the simpler model is more defensible as a structural description of the data-generating
process.** That is a substantive, reportable fact.

---

## The question you need to answer first

**What is the scientific goal?**

**If the goal is prediction** — you want the model that minimizes out-of-sample error on new
observations from the same process — then AIC (or better, AICc if `N/k` is anywhere near
40 or below; AICc = AIC + `2k(k+1)/(N−k−1)`) is the right target. AIC is asymptotically
equivalent to leave-one-out cross-validation, so it directly addresses the question "which
model generalizes better?" The 9-parameter model won on this criterion. That's your answer
for a prediction-oriented paper.

**If the goal is identifying which variables are real / recovering a parsimonious structural
model** — you believe a "true" sparse model exists and you want to find it — then BIC is
the right target. BIC's consistency guarantee says that, *given the true model is among your
candidates*, it will select it as `N → ∞`. The 5-parameter model won on this criterion.
That's your answer for a structure-oriented paper. But you must own the assumption you're
buying: the true model is in your candidate set. That is rarely guaranteed.

**Do not pick whichever one agrees with your prior.** That's not model selection, it's
confirmation.

---

## What to actually do

### 1. Run AICc, not just AIC

Before finalizing anything, check whether `N/k` is small. With `k = 9` parameters, if
`N < 360` you should be using AICc rather than AIC. AICc applies a finite-sample correction
that can shift the outcome. If you've been running bare AIC, recompute with AICc.

### 2. Report a table, not a winner

Show the full model comparison:

| Model | params | log L | AIC | ΔAIC | w_AIC | BIC | ΔBIC |
|---|---|---|---|---|---|---|---|
| Small (5 param) | 5 | … | … | … | … | … | 0 |
| Large (9 param) | 9 | … | … | 0 | 1.0 | … | … |

Akaike weights `w_i ∝ exp(−½ΔAIC_i)` quantify relative predictive support as probabilities
summing to 1. For BIC, `ΔBIC` of 2–6 is positive evidence for the simpler model, 6–10 is
strong, >10 is very strong (Kass–Raftery). Your reviewer needs to see the magnitude, not
just the direction.

### 3. State which question you're answering

In the paper, write something like:

> "AIC favored the 9-parameter model (ΔAIC = X.X relative to the 5-parameter model,
> Akaike weight = 0.9X), indicating better out-of-sample predictive accuracy. BIC favored
> the 5-parameter model (ΔBIC = X.X), which under the assumption that the true data-generating
> model is among the candidates corresponds to [strong/very strong] evidence for the more
> parsimonious structure. Because our primary goal is [prediction / structural identification],
> we report [AIC / BIC] as the primary criterion; both criteria are reported in full in Table X."

This is not hedging. It is the correct statistical statement.

### 4. If prediction is the actual goal, go to CV

AIC is a cheap analytic approximation to LOO. If you have the data and the compute, run
actual LOO-CV (or PSIS-LOO for Bayesian models). It will tell you whether the 4-parameter
advantage from the richer model is real or just noise in the AIC approximation. When AIC
and held-out CV agree, you have a firm answer. When they disagree, trust CV.

---

## The one thing not to do

**Do not average AIC and BIC**, use some weighted combination, or report "AIC/BIC both
considered" without saying what you concluded. That conveys no information. The criteria
are not measuring the same thing and the numbers are not on a commensurable scale.

---

## Summary

Your AIC–BIC split is telling you something real: **the 9-parameter model predicts better,
but the 5-parameter model is the more structurally defensible one given a true-model
assumption.** Report both in a table. State which criterion is primary and why. If
prediction is the goal, lean on AIC/AICc (or run CV). If parsimony / structure identification
is the goal, lean on BIC and own the assumption it requires. The disagreement belongs in
the paper, not in the trash.
