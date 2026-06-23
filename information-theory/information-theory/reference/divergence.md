# KL Divergence, Cross-Entropy, and the Divergence Family

Contents: [KL divergence](#kl-divergence-relative-entropy) · [Direction is a modeling choice](#direction-is-a-modeling-choice-the-most-important-section) · [Cross-entropy and the one-fact identity](#cross-entropy-and-the-one-fact-identity) · [Proper scoring & calibration](#proper-scoring-rules-and-calibration) · [f-divergences](#f-divergences-the-general-family) · [Closed forms](#closed-forms) · [Estimating divergences](#estimating-divergences-from-samples)

## KL divergence (relative entropy)

`D_KL(p ‖ q) = Σ p(x) log[ p(x) / q(x) ] = E_p[ log p − log q ]` (continuous: integral).

Read it as: **the expected extra bits you pay to encode draws from `p` using a code
optimized for `q`** — the penalty for believing `q` when the truth is `p`. Equivalently,
the average log-likelihood ratio favoring the true model; this is why it governs how fast
you can tell two distributions apart (Stein's lemma, Chernoff information).

Properties — and the ones people get wrong:
- `D_KL ≥ 0`, with equality iff `p = q` a.e. (Gibbs' inequality).
- **It is not a metric.** Not symmetric, no triangle inequality. Calling it "KL distance"
  invites exactly the symmetric-reasoning errors below. Say "divergence."
- **It is reparameterization-invariant** (unlike differential entropy): the `log p − log q`
  difference cancels any Jacobian. This is why KL, not entropy, is the right primitive for
  continuous variables.
- `D_KL(p‖q) = ∞` whenever `q(x)=0` but `p(x)>0`. The asymmetry is built into the support.

## Direction is a modeling choice (the most important section)

`D_KL(p‖q)` and `D_KL(q‖p)` are different numbers with different behavior. When `q` is an
approximating family being fit to a target `p`, the direction you minimize determines the
*failure mode you accept*. This is a real decision in variational inference, EP, distillation,
and RL, and it is routinely glossed.

**Forward KL, `D_KL(p ‖ q)` — "M-projection," mass-covering, zero-avoiding.**
The expectation is under `p`, so wherever `p` has mass, `q` is penalized hard for being
near zero (`log p/q → ∞`). The optimum *covers* all of `p`'s support; if `q` is too simple
to fit a multimodal `p`, it spreads out and puts mass *between* modes. Minimizing forward KL
with `p` = data is **maximum likelihood / moment matching**. Used by EP and by training a
model on samples.

**Reverse KL, `D_KL(q ‖ p)` — "I-projection," mode-seeking, zero-forcing.**
The expectation is under `q`, so `q` is free to ignore regions where it places no mass; it
is penalized for putting mass where `p` is low. The optimum *locks onto one mode* and is
**too narrow** — it **underestimates variance/uncertainty**. This is what standard
variational inference (the ELBO) minimizes, which is exactly why mean-field VI gives
overconfident posteriors. Flag this whenever someone treats a VI posterior's width as real.

Practical rule: if the cost of *missing* a real possibility is high, you want forward
(mass-covering). If the cost of *hallucinating* mass where there is none is high, you want
reverse (mode-seeking). State the choice; never write "minimize the KL" unqualified.

## Cross-entropy and the one-fact identity

Cross-entropy: `H(p, q) = −Σ p(x) log q(x) = E_p[−log q]`. The decomposition

```
H(p, q) = H(p) + D_KL(p ‖ q)
```

is the hinge for an entire cluster of ML concepts. Because `H(p)` doesn't depend on `q`,
**minimizing cross-entropy over `q` = minimizing `D_KL(p‖q)`**. And when `p` is the empirical
distribution of the data, that minimization **is maximum likelihood**:

```
argmin_q H(p̂, q)  =  argmin_q D_KL(p̂ ‖ q)  =  argmax_q Σᵢ log q(xᵢ)  =  MLE
```

So **"cross-entropy loss," "negative log-likelihood," "log loss," and "minimizing KL to the
data" are the same objective.** Per-sample, cross-entropy loss `= −log q(true class)`.
The only differences across the names are (a) log base — bits vs nats merely rescale by
`ln2` — and (b) whether you average (loss) or sum (log-likelihood). When a user is confused
about how these relate, give them this identity rather than four separate explanations.

- **Perplexity** `= exp(cross-entropy)` in the matching base; a language model's
  per-token perplexity is `exp` of its average NLL. "2.3 bits/char" and "perplexity 4.9"
  are the same statement.
- **Label smoothing** replaces the one-hot target `p` with `(1−ε)·one-hot + ε·uniform`;
  the added term is a `KL(uniform‖q)` pull, i.e. a regularizer toward uncertainty.
- **Knowledge distillation** trains the student's `q` against the teacher's soft `p` via
  cross-entropy — again this same identity, now with a non-degenerate `p`.

**Disambiguation:** the *cross-entropy method* (CEM) is an unrelated stochastic-optimization
/ rare-event algorithm that happens to minimize a KL at each step. If a user says "cross-
entropy method" in an optimization/RL-planning context, they mean CEM, not the loss.

## Proper scoring rules and calibration

Log loss is a **strictly proper scoring rule**: the expected score is uniquely optimized by
reporting the true probabilities, so it *incentivizes honest, calibrated probabilities*.
But low cross-entropy does **not** guarantee calibration on its own — a model can achieve
good average log loss while being miscalibrated in regions. Two correctives to mention:
- **Brier score** (`Σ (q − y)²`) is another proper scoring rule, bounded and quadratic;
  decomposes into calibration + refinement (Murphy). Less sensitive to confident mistakes
  than log loss, which blows up as `q→0` on a positive — that sensitivity is a feature for
  flagging overconfidence and a liability with label noise.
- To actually *check* calibration use reliability diagrams / ECE; to *fix* it use temperature
  scaling (a single scalar dividing the logits — a one-parameter cross-entropy minimization).

## f-divergences (the general family)

KL is one member of the **f-divergence** family `D_f(p‖q) = Σ q(x) f(p(x)/q(x))` for convex
`f` with `f(1)=0`. Useful when KL's infinities or asymmetry are a problem:
- `f(t)=t log t` → KL; `f(t)=−log t` → reverse KL.
- **Jensen–Shannon** `JS(p,q) = ½KL(p‖m) + ½KL(q‖m)`, `m=(p+q)/2`: symmetric, bounded by
  `log 2`, finite even on disjoint support, and `√JS` is a metric. Good default when you
  need a symmetric "distance between distributions." (The original GAN objective is a JS
  surrogate; its vanishing-gradient problem on disjoint supports is *why* Wasserstein GANs
  exist — and Wasserstein is an optimal-transport distance, **not** an f-divergence, so it
  stays finite and informative when supports don't overlap.)
- **Total variation** `½Σ|p−q|`: the `f(t)=½|t−1|` member; the tightest "probability of
  distinguishing in one sample" interpretation. Pinsker's inequality bounds it by KL:
  `TV ≤ √(KL/2)`.
- **χ²-divergence** `Σ (p−q)²/q`: upper-bounds KL; shows up in importance-sampling variance.

Pick by the property you need (symmetry, boundedness, behavior on disjoint support), not by
habit. If someone needs a distance and reaches for raw KL, JS or Wasserstein is usually the
better-posed object.

## Fisher information: KL up close, and the geometry under everything

Zoom in on KL between two members of the same parametric family at nearby parameters `θ` and
`θ+dθ`. The first-order term vanishes (KL is minimized at `dθ=0`), and the **second-order term
is the Fisher information**:

```
KL( p_θ ‖ p_{θ+dθ} ) ≈ ½ dθᵀ I(θ) dθ ,     I(θ) = E[ (∇_θ log p_θ)(∇_θ log p_θ)ᵀ ]
```

So KL is *locally* a squared distance whose metric is the Fisher information matrix — this is
the entry point to **information geometry** (the space of distributions as a Riemannian manifold
with `I(θ)` as its metric). Why this matters in practice, not just in theory:

- **It explains reparameterization behavior.** KL is invariant to how you coordinatize the
  distribution, and `I(θ)` transforms as a metric tensor — together they're why KL-based
  quantities don't depend on arbitrary parameter scaling the way Euclidean parameter distance
  does. (This is the same invariance that makes the **Jeffreys prior** `∝ √det I(θ)`
  parameterization-invariant.)
- **It's the bridge to estimation theory.** `I(θ)` is the curvature of the log-likelihood;
  the **Cramér–Rao bound** says any unbiased estimator has covariance `⪰ I(θ)⁻¹`. High Fisher
  information = sharply identified parameter = distributions that are *easy to tell apart*,
  which is exactly the "distinguishability volume" interpretation.
- **It closes the loop with model selection and MDL.** The `log ∫ √det I(θ) dθ` complexity term
  in NML/MDL (`coding.md`) and the Laplace approximation behind BIC (`model-selection.md`) are
  both Fisher-geometry volumes — model complexity is *how much distinguishable distribution* a
  model can reach, not how many parameters it has. When two models with equal parameter counts
  have different effective complexity, this is why.
- **Natural gradient** preconditions by `I(θ)⁻¹`, following the steepest-descent direction in
  KL geometry rather than parameter-coordinate geometry; it's the principled version of "the
  loss landscape's units are wrong," and the reason whitening/natural-gradient methods help.

You rarely compute `I(θ)` by hand for applied work, but knowing KL ≈ ½ Fisher locally is what
makes "KL is the natural loss/metric for distributions" precise rather than a slogan.

## Closed forms

- **KL between Gaussians** (1-D), `p=N(μ₁,σ₁²)`, `q=N(μ₂,σ₂²)`:
  `KL(p‖q) = log(σ₂/σ₁) + (σ₁² + (μ₁−μ₂)²)/(2σ₂²) − ½` (nats). Note the asymmetry directly:
  swapping the roles of σ₁,σ₂ changes the value.
- **KL between multivariate Gaussians**:
  `KL = ½[ tr(Σ₂⁻¹Σ₁) + (μ₂−μ₁)ᵀΣ₂⁻¹(μ₂−μ₁) − d + log(|Σ₂|/|Σ₁|) ]`.
- **KL between categoricals** `Σ pᵢ log(pᵢ/qᵢ)` — and remember it's `+∞` if any `qᵢ=0`
  where `pᵢ>0`, which is why you smooth `q` in practice.

## Estimating divergences from samples

KL/cross-entropy estimates inherit the entropy estimation problems (`reference/estimation.md`).
For **discrete** data, smooth `q` (add-`α` / Dirichlet) so you don't hit `log 0`; the choice
of smoothing materially moves the number when categories are rare. For **continuous** data,
don't bin — use **k-NN density-ratio estimators** (Wang–Kulkarni–Verdú) or train a classifier
and use the density-ratio trick (a calibrated classifier's logit estimates `log p/q`). Always
sanity-check that the estimate is `≥ 0` up to noise; large negative estimates mean the
estimator broke (usually disjoint-support / extrapolation).
