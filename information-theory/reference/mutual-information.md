# Mutual Information

Contents: [Definition and identities](#definition-and-identities) · [Why MI beats correlation — and the footgun](#why-mi-beats-correlation-and-the-footgun) · [Data-processing inequality](#the-data-processing-inequality) · [Conditional and multivariate information](#conditional-and-multivariate-information) · [Feature selection](#mi-for-feature-selection) · [Estimation](#estimation-the-part-that-decides-whether-your-answer-is-real)

## Definition and identities

`I(X;Y) = D_KL( p(x,y) ‖ p(x)p(y) )` — the KL divergence from the joint to the product of
marginals, i.e. *how far X and Y are from independent*. Equivalent forms, all worth keeping:

```
I(X;Y) = H(X) − H(X|Y) = H(Y) − H(Y|X) = H(X) + H(Y) − H(X,Y)
```

Read as **the reduction in uncertainty about one variable from observing the other** — and
it's symmetric, `I(X;Y)=I(Y;X)`. Because it's a KL, `I ≥ 0`, with `=0` iff `X ⟂ Y`. Units
follow the log base (bits/nats).

Two facts that resolve most confusion:
- "Information gain" in decision trees **is** mutual information: the split's IG is
  `H(Y) − H(Y|split)`. So decision-tree questions are MI questions; the same estimation
  bias (below) is why information gain favors high-cardinality splits — pure overfitting
  dressed as signal, which is exactly what gain *ratio* and `−(K−1)/(2N)`-style corrections
  guard against.
- `I(X;X) = H(X)`: a variable's information about itself is its entropy.

## Why MI beats correlation — and the footgun

MI captures **any** statistical dependence, not just linear; `I=0` iff *fully independent*,
whereas Pearson `r=0` only rules out linear association. MI catches `Y=X²`, XOR, and
heteroscedastic coupling that `r` misses. It is also **invariant under invertible
transformations of each variable separately** — monotone rescaling of `X` or `Y` leaves
`I(X;Y)` unchanged. That invariance is MI's superpower for messy real features.

It is **also the footgun**:
- For **continuous** variables, a deterministic invertible relationship `Y=g(X)` has
  `I(X;Y) = ∞`. "High MI" does not mean "strong" on any bounded scale; raw MI is not
  comparable across variable pairs without normalization.
- MI has no fixed upper bound for continuous variables and is bounded by
  `min(H(X),H(Y))` for discrete ones — so a "big MI" can just mean "high-entropy variables."
  When you need a 0–1 effect size, use a **normalized** variant: e.g.
  `NMI = I / √(H(X)H(Y))` or `I / min(H(X),H(Y))`, or the information-coefficient
  `√(1 − e^{−2I})` (which equals `|ρ|` for Gaussians). Say which normalization and why.

## The data-processing inequality

If `X → Y → Z` is a Markov chain (`Z` depends on `X` only through `Y`), then
`I(X;Z) ≤ I(X;Y)`. **Post-processing cannot create information.** Practical consequences to
deploy:
- No deterministic feature transform, embedding, or model layer can increase the information
  about the target beyond what's in the input — it can only fail to destroy it. So "our
  fancy transform *added* signal about Y" is, taken literally, impossible; what it did was
  expose existing signal to a weak downstream model.
- It bounds achievable performance: `I(X;Y)` upper-bounds how well *any* method can predict
  `Y` from `X`. Use it to sanity-check "too good" results — if measured predictive
  information exceeds a careful `I(X;Y)` estimate, suspect leakage.

## Fano's inequality — turning information into an error bound

DPI tells you information can't be created; **Fano** tells you what a given amount of
information *costs you in achievable accuracy*. For predicting a discrete `Y` (with `K`
classes) from `X` through any estimator `Ŷ`, with error probability `Pₑ = P(Ŷ ≠ Y)`:

```
H(Y | X) ≤ H(Pₑ) + Pₑ · log₂(K − 1)
```

Read it as a floor on error: rearranging, **no classifier can drive `Pₑ` below the level
implied by the residual uncertainty `H(Y|X)`.** Two ways practitioners actually use it:
- **Feasibility check before modeling.** Estimate `H(Y|X) = H(Y) − I(X;Y)`; if it's large,
  Fano lower-bounds the best achievable error *for any model*. A target you can't hit is a
  data problem, not a modeling problem — stop tuning architectures and get better features.
- **Leakage/too-good detector (with DPI).** If a model's measured error is *below* the Fano
  floor implied by an honest `I(X;Y)` estimate, you have leakage or a broken eval, not a
  breakthrough. DPI caps the information; Fano converts that cap into the accuracy you should
  refuse to believe was beaten.

The weak (binary-ish) form `Pₑ ≥ (H(Y|X) − 1) / log₂(K)` is the quick napkin version. Both
need an `H(Y|X)` estimate, so the bias cautions in the estimation section apply — a biased-low
`H(Y|X)` gives an over-optimistic (too-loose) error floor.

## Conditional and multivariate information

- **Conditional MI** `I(X;Y|Z) = H(X|Z) − H(X|Y,Z)`: dependence between `X,Y` *after*
  accounting for `Z`. Central to causal-discovery conditional-independence tests.
- **Non-monotonicity trap:** conditioning can *raise or lower* MI. `I(X;Y|Z)` can exceed
  `I(X;Y)` (explaining-away / XOR: `X,Y` independent marginally but coupled given their
  parity `Z`). So you cannot infer marginal independence from conditional, or vice versa.
- **Interaction information** `I(X;Y;Z) = I(X;Y) − I(X;Y|Z)` **can be negative** — negative
  means synergy (the pair tells you more jointly than separately), positive means redundancy.
  Its sign-ambiguity is why the field moved to **Partial Information Decomposition (PID)**,
  which splits the information `(X,Y)` carry about a target into unique/redundant/synergistic
  parts. PID is genuinely useful but **not uniquely defined** — there are competing redundancy
  measures (Williams–Beer `I_min`, Bertschinger et al. `I_broja`, etc.); if a user invokes
  PID, name the measure and note the choice is contested rather than presenting one as canonical.
- **Total correlation** `TC(X₁..Xₙ) = Σ H(Xᵢ) − H(X₁..Xₙ)`: total multivariate redundancy;
  the objective minimized by independent-component / disentangling methods.

## Transfer entropy and directed information (coupling between time series)

Everything above is symmetric in time. When the data are **time series** and the question is
*directional* — does X's past help predict Y's future beyond Y's own past — the right object
is **transfer entropy** (Schreiber 2000), which is just a conditional MI with a temporal
structure:

```
TE_{X→Y} = I( Y_{t+1} ; X_t^{(l)} | Y_t^{(k)} )
         = H(Y_{t+1} | Y_t^{(k)}) − H(Y_{t+1} | Y_t^{(k)}, X_t^{(l)})
```

where `Y_t^{(k)}` is `Y`'s own `k`-step history. Use `scripts/entropy_mi_estimators.py`
(`transfer_entropy_discrete`, `gaussian_te`, and the permutation null). What to hold onto:

- **It is asymmetric by construction**: `TE_{X→Y} ≠ TE_{Y→X}`, and that asymmetry is the
  whole point — it's a directed measure, unlike MI. Report both directions.
- **It is the nonlinear generalization of Granger causality.** For jointly Gaussian, linear
  processes the two are *equivalent*: the Geweke Granger statistic equals `2·TE` (in nats).
  So if your relationships are linear-Gaussian, plain Granger/VAR is simpler and sufficient;
  reach for TE when you specifically need to capture **nonlinear** directed coupling. Don't
  sell TE as "model-free causality" — it's directed *predictive* information, and it inherits
  every confound of Granger causality (a hidden common driver `Z` produces spurious `TE`;
  condition on `Z` via the multivariate/conditional TE if you can measure it).
- **Estimation is the hard part, more so than ordinary MI.** TE conditions on history, so the
  state space is `K^(k+l+1)` cells — it undersamples *fast* as you add history length. The
  plug-in estimate is biased upward exactly like MI, and a **surrogate/permutation null is
  mandatory** (shift or block-permute the source to destroy directed timing while preserving
  marginals). A bare positive TE is not evidence of coupling; TE above its surrogate null is.
- **Choose `k` honestly.** Too short a target history `k` leaves predictable structure in the
  residual that the source can "explain," inflating `TE_{X→Y}`. Set `k` from the target's own
  autocorrelation/AIC before attributing predictability to the source.
- **Continuous signals:** use a KSG-style conditional-MI estimator (k-NN), not binning; binning
  TE inherits all the discretization fragility of binned MI, amplified by the extra dimensions.

## MI for feature selection

MI is a popular filter because it's model-agnostic and catches nonlinear relevance. Use it,
but with the standard cautions:
- **Relevance ≠ non-redundancy.** Ranking features by `I(Xⱼ;Y)` alone double-counts correlated
  features. The fix is criteria that subtract redundancy: **mRMR** (max relevance − mean
  pairwise MI), or conditional/joint MI criteria (JMI, CMIM) that score `I(Xⱼ;Y | already-
  selected)`. Plain top-`k`-by-MI is a known failure mode.
- **The estimate is biased upward** (next section), and the bias is *worse for high-cardinality
  / continuous features* — so naive MI ranking is biased toward exactly the features most
  prone to overfit. This is the same pathology as information-gain favoring many-valued splits.
  Correct the estimator or permutation-test each MI.
- **Discretization matters.** Binning continuous features changes the MI; results can flip
  with bin count. Prefer the KSG estimator over histogram MI for continuous features.

## Estimation — the part that decides whether your answer is real

Plug-in MI from a contingency table is biased **upward** by ≈ `(K_X−1)(K_Y−1)/(2N)` nats —
it reports spurious dependence, and reports the *most* spurious dependence exactly where you
have the fewest counts per cell. Two non-negotiables:
1. **Always test MI against a null.** Permute one variable many times, recompute MI, and
   compare your value to that shuffled distribution. The shuffle mean is your bias floor; a
   value not clearly above it is noise. (`scripts/entropy_mi_estimators.py` shows this.)
2. **For continuous data use KSG (k-NN), not bins.** The Kraskov–Stögbauer–Grassberger
   estimator (in the script, validated against the Gaussian closed form `I=−½ln(1−ρ²)`) is the
   field default; `sklearn.feature_selection.mutual_info_regression/classif` use a KSG variant.

See `reference/estimation.md` for the full estimator menu and when each is appropriate.
