# Entropy

Contents: [Discrete entropy](#discrete-entropy) · [Joint, conditional, chain rule](#joint-conditional-and-the-chain-rule) · [Differential entropy — the traps](#differential-entropy-the-traps) · [Maximum entropy](#maximum-entropy-and-why-it-gives-exponential-families) · [Generalized entropies](#generalized-entropies-renyi-tsallis) · [Common closed forms](#closed-forms-worth-memorizing)

## Discrete entropy

For a discrete distribution `p` over outcomes, `H(X) = −Σ pᵢ log pᵢ`. Base-2 log →
**bits**, natural log → **nats** (`1 nat = 1/ln2 ≈ 1.4427 bits`). Define `0 log 0 = 0`.

Interpretations that are actually useful when explaining:
- **Expected surprisal.** Surprisal of outcome `i` is `−log pᵢ`; entropy is its mean.
- **Optimal codelength.** The least achievable expected bits-per-symbol for lossless
  coding of i.i.d. draws (source coding theorem; `reference/coding.md`).
- **Log of the "effective number of outcomes."** `exp(H)` (in the matching base) is the
  *perplexity* — a flat distribution over `k` outcomes has `H = log k` and perplexity
  `k`. Quote perplexity when a stakeholder wants an interpretable "branching factor."

Bounds: `0 ≤ H(X) ≤ log K` for `K` outcomes; max at uniform, min (=0) at a point mass.

### The estimation caveat is not optional
When `p` is unknown and you have counts, the plug-in `Ĥ = −Σ p̂ᵢ log p̂ᵢ` is biased
**downward** by ≈ `(K−1)/(2N)` nats (Miller–Madow). With rare categories or `N` not far
above `K`, this bias is large and the naive number is simply wrong. Go to
`reference/estimation.md` before reporting a sample entropy.

## Joint, conditional, and the chain rule

- Joint: `H(X,Y) = −Σ p(x,y) log p(x,y)`.
- Conditional: `H(Y|X) = Σ p(x) H(Y|X=x) = H(X,Y) − H(X)`. Read as *remaining
  uncertainty in Y once X is known*.
- Chain rule: `H(X,Y) = H(X) + H(Y|X)`. Generalizes to `H(X₁..Xₙ) = Σ H(Xᵢ | X₁..Xᵢ₋₁)`.
- **Conditioning never increases entropy on average:** `H(Y|X) ≤ H(Y)`, with equality
  iff `X ⟂ Y`. The gap is exactly the mutual information `I(X;Y)` — this identity is the
  hinge between entropy and MI, so keep it in front of mind.

A frequent confusion to correct: `H(Y|X) ≤ H(Y)` holds **on average over X**. For a
*specific* value, `H(Y|X=x)` can exceed `H(Y)` — learning one particular thing can leave
you more uncertain. Don't let anyone "prove" independence from a single conditional.

## Entropy rate — entropy *per symbol* of a process

For a sequence (text, a sensor stream, a Markov chain) the quantity you actually want is the
**entropy rate**, the per-symbol uncertainty in the long run:

```
H(𝒳) = lim_{n→∞} H(X_n | X_1, …, X_{n−1})        (= lim (1/n) H(X_1..X_n) for a stationary process)
```

This is the formalism behind several things the rest of the skill uses loosely:
- **Bits per character / perplexity are entropy-rate estimates.** A language model's
  cross-entropy in bits/char estimates an *upper bound* on the text's entropy rate (upper,
  because the model's `q` ≠ true `p`); `perplexity = 2^(bits/char)`. "English is ~1 bit/char"
  (Shannon) is a claim about its entropy rate, not about the marginal letter distribution
  (which is ~4 bits/char). The gap is all the predictability in context.
- **i.i.d. is the special case.** If the symbols are independent, the entropy rate collapses to
  the marginal `H(X)`. Reporting marginal symbol entropy for a clearly dependent sequence
  (anything with autocorrelation) **overstates** its true per-symbol information — the
  conditional form is the honest one.
- **Markov chains have a closed form.** For a stationary first-order chain with stationary
  distribution `μ` and transition matrix `P`:
  `H(𝒳) = − Σᵢ μᵢ Σⱼ Pᵢⱼ log Pᵢⱼ = Σᵢ μᵢ H(row i)` — the stationary-weighted average of the
  per-state transition entropies. This is the right "how compressible is this stream" number,
  and it is generally **far below** the marginal entropy of the visited states.
- **Estimating it from data** is an undersampling problem in disguise: longer conditioning
  context = exponentially more histories = the bias issues of the estimation chapter. Block
  entropies `H(X_1..X_m)/m` converge to the rate from above as `m` grows, but each higher `m`
  needs far more data; don't push the block length past where your counts support it.

## Differential entropy — the traps

For a continuous density `f`, the differential entropy is `h(X) = −∫ f(x) log f(x) dx`.
It looks like the continuous analog of `H`. **It is not, and treating it as one is the
single most common continuous-information-theory mistake.** Three things break:

1. **It can be negative.** A `Uniform(0, ½)` has `h = log(½) = −1` bit. There is no "you
   can't have negative information" interpretation; `h` is not expected surprisal.
2. **It is not invariant under invertible reparameterization.** For `Y = g(X)` with `g`
   smooth invertible, `h(Y) = h(X) + E[log|g′(X)|]`. Change from meters to millimeters and
   the "entropy" changes by `log 1000`. So a differential-entropy *value* is meaningless
   without fixing the coordinate/units.
3. **It is the limit of discretized entropy minus a divergent term.** Quantize `X` to
   bins of width `Δ`: `H(X^Δ) ≈ h(X) − log Δ → ∞` as `Δ→0`. Continuous variables carry
   infinite Shannon information; `h` is what's left after subtracting the `−log Δ` infinity.

**What to use instead.** The quantities that *are* coordinate-free and well-behaved are
**relative entropy (KL)** and **mutual information** — both are differences of `−log f`
terms, so the Jacobian cancels. If a task is stated in terms of "entropy of a continuous
thing," the well-posed version is almost always a KL or an MI. Steer there.

(Differential entropy is still useful: it appears in the Gaussian channel, in maximum-
entropy derivations, and as a building block of MI. Just never compare two `h` values
computed on differently-scaled variables.)

## Maximum entropy and why it gives exponential families

The maximum-entropy principle (Jaynes): among all distributions consistent with stated
constraints, choose the one of **maximum entropy** — it commits to nothing beyond the
constraints. Under moment constraints `E[Tⱼ(X)] = μⱼ`, the MaxEnt solution is

```
p(x) ∝ exp( Σⱼ λⱼ Tⱼ(x) )
```

i.e. an **exponential family**, with the Lagrange multipliers `λⱼ` as the natural
parameters. This is why exponential families are everywhere and why MaxEnt is a unifying
lens, not a niche trick:

| Constraints on the support                  | MaxEnt distribution |
|----------------------------------------------|---------------------|
| support `[a,b]`, nothing else                | Uniform             |
| support `[0,∞)`, fixed mean                  | Exponential         |
| support `ℝ`, fixed mean and variance         | Gaussian            |
| support `{0,1,…}`, fixed mean                | Geometric           |
| support `ℝ`, fixed `E[X]`, `E[log X]` (x>0)  | Gamma               |

Use this when a user asks "what distribution should I assume?" — the honest answer is
"the MaxEnt one for the constraints you can actually defend," and the table tells you
which. The connection runs the other way too: fitting an exponential family by MLE is
moment-matching, which is minimizing KL to the empirical distribution (`reference/divergence.md`).

## Generalized entropies (Rényi, Tsallis)

Shannon entropy is the `α→1` case of a family. Reach for these only when the use case
calls for it; defaulting to them is usually overcomplication.

- **Rényi entropy** `H_α = (1/(1−α)) log Σ pᵢ^α`. Special cases: `α→1` Shannon; `α=0`
  log of support size (Hartley); `α=2` collision entropy `−log Σ pᵢ²`; `α→∞` min-entropy
  `−log max pᵢ`. **Min-entropy is the right one for security / guessing** (it bounds the
  best single guess); Shannon overstates the difficulty of guessing for skewed `p`.
- **Tsallis entropy** `S_q = (1/(q−1))(1 − Σ pᵢ^q)` — non-additive; appears in
  non-extensive statistical mechanics and some ecology. Rarely the right tool in
  ML/stats; flag if someone reaches for it without a specific reason.
- **Shannon diversity index** (ecology) is literally Shannon entropy of species
  proportions; **Simpson's index** is `1 − Σ pᵢ²` = collision-related. If a user is in an
  ecology/diversity framing, this skill applies — translate to entropy language and warn
  about the same small-sample bias (few individuals sampled ⇒ diversity underestimated).

## Closed forms worth memorizing

- **Binary entropy** `H_b(p) = −p log p − (1−p) log(1−p)`; max `1 bit` at `p=½`; symmetric;
  flat near the top (so estimating `p` near ½ barely changes `H`).
- **Uniform over K**: `H = log K`.
- **Univariate Gaussian** `N(μ,σ²)`: `h = ½ log(2πe σ²)` (nats). Depends only on `σ`.
- **Multivariate Gaussian** `N(μ,Σ)` in `d` dims: `h = ½ log((2πe)^d |Σ|)` (nats).
- These make good sanity checks and let you answer "entropy of a Gaussian" exactly —
  just remember (trap #2) the value is in the variable's own units.

## "Entropy" that is NOT Shannon entropy: regularity statistics for time series

A frequent collision. Someone says "entropy" and means **sample entropy (SampEn)**,
**approximate entropy (ApEn)**, **permutation entropy**, **multiscale entropy (MSE)**,
or **spectral entropy** — regularity/complexity measures for an *ordered* signal
(HRV, EEG, accelerometer, behavioral streams). These come from nonlinear-dynamics and
physiological-signal analysis (Pincus 1991; Richman & Moorman 2000; Bandt & Pompe 2002),
**a different lineage from Shannon (1948)**. Get the question right before you compute:

- **Shannon entropy** answers "how many bits does this *distribution* carry," is a
  function of probabilities, and is order-invariant (shuffle the data, same `H`).
- **Sample/approximate entropy** answer "how *predictable is the next value* given recent
  history," are functions of a trajectory, and are destroyed by shuffling. They are
  **not measured in bits of information** and must not be averaged with, or substituted
  for, Shannon quantities. Reaching for `np.log2` on a SampEn value is a category error.

Use `scripts/sample_entropy.py` (cross-validated against `antropy`) for these.

### Sample entropy (SampEn) — the default regularity measure
For embedding dimension `m` (default 2) and tolerance `r` (default `0.2·std`):
count template pairs that match within `r` (Chebyshev distance) at length `m` (call it
`B`) and at length `m+1` (`A`); then `SampEn = −ln(A/B)`. **Self-matches are excluded** —
that is the entire point of SampEn over ApEn. Low value ⇒ regular/self-similar; high ⇒
complex/irregular. Returns `+∞` when `A=0` (no longer-template matches): raise `r` or
lengthen the series rather than reporting infinity.

- **Parameter sensitivity is real.** `m`, `r`, and `N` all move the number. Report them.
  Never compare SampEn across studies that used different `(m, r, N)`. `r` is conventionally
  a fraction of the series SD, so **standardize or fix `r` deliberately** when comparing
  signals with different variance.
- **Length.** Short series (`N` a few hundred) give noisy, sometimes undefined SampEn.
  Richman & Moorman's whole motivation was reducing the short-series bias ApEn suffers.

### Approximate entropy (ApEn) — know it mainly to avoid it
`ApEn = φ(m) − φ(m+1)` where `φ` averages `ln(match-fraction)` **including self-matches**.
That self-count biases ApEn toward "more regular than reality," worse for short series and
small `r`, and makes it depend awkwardly on `N`. **Default to SampEn**; mention ApEn only
for backward compatibility with older clinical literature.

### Permutation entropy — a genuine Shannon entropy of *motifs*
Bandt–Pompe: take the ordinal pattern (the `argsort`) of each length-`order` window and
compute the **Shannon entropy of the motif-frequency distribution** (normalize by
`log₂(order!)` for a `[0,1]` scale). This one *is* a Shannon entropy — but of ordinal
patterns, so it captures temporal ordering a value-only entropy ignores. Cheap, robust to
monotone transforms, good first complexity screen. Tie-handling conventions differ across
implementations (matters only when the signal has exact repeats).

### Multiscale entropy (MSE) and spectral entropy — one-liners
- **MSE**: SampEn computed on coarse-grained versions of the signal at multiple time scales;
  the *curve* of SampEn vs scale is the object of interest (distinguishes white noise, which
  falls off, from `1/f`/complex signals, which stay high). Report the curve, not one number.
- **Spectral entropy**: Shannon entropy of the **normalized power spectral density** — a
  flat spectrum (white) is high-entropy, a peaky spectrum (a strong rhythm) is low. It is a
  Shannon entropy applied to spectral power, distinct from SampEn's template logic.

### Routing rule
If the user has a **distribution / counts / categorical or probability vector**, it is
Shannon territory (this file + `mutual-information.md`). If the user has a **time series and
asks about regularity, complexity, predictability, HRV/EEG**, it is the SampEn family
(`scripts/sample_entropy.py`). When unsure, ask which question they're asking — the word
"entropy" alone does not disambiguate, and answering in the wrong framework is the most
common failure here.
