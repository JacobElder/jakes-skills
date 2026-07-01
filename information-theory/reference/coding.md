# Coding and Compression

Contents: [Source coding theorem](#source-coding-theorem-the-floor-is-entropy) · [Kraft and prefix codes](#kraft-inequality-and-prefix-codes) · [Huffman vs arithmetic](#huffman-vs-arithmetic-coding) · [Compression = prediction](#compression-is-prediction-the-key-bridge) · [Channel coding](#channel-coding-in-one-paragraph) · [MDL bridge](#the-mdl-bridge-to-model-selection)

## Source coding theorem: the floor is entropy

For an i.i.d. source `X ~ p`, any uniquely-decodable lossless code has expected length per
symbol `L ≥ H(X)` (bits, with base-2 logs), and codes exist achieving `H(X) ≤ L < H(X)+1`.
Block the source into chunks of `n` and the overhead amortizes: `L_n/n → H(X)`. **Entropy is
not a metaphor for compressibility — it is the exact achievable limit.** This is the concrete
meaning behind "entropy = information content": it's the bit count you can't get below.

A direct consequence worth stating to users: the bits a good model assigns to data
(`−log₂ q(data)`) *is* a compressed file length. "How many bits does this cost" and "how well
does my model predict this" are the same question (see below).

## Kraft inequality and prefix codes

A **prefix (instantaneous) code** is one where no codeword is a prefix of another — decodable
without lookahead. Codeword lengths `{ℓᵢ}` are realizable by a prefix code **iff** they satisfy
the **Kraft inequality** `Σ 2^(−ℓᵢ) ≤ 1`. The same inequality holds for all uniquely-decodable
codes (McMillan), so prefix codes lose nothing — there's never a reason to use a non-prefix
uniquely-decodable code.

This is the bridge between codes and distributions: lengths `ℓᵢ = −log₂ qᵢ` satisfy Kraft with
equality, so **every distribution `q` defines a code** (lengths `−log₂ qᵢ`) and every code
defines an implied distribution. Expected length under the true `p` using `q`'s code is exactly
the **cross-entropy** `H(p,q) = H(p) + KL(p‖q)`: the `KL` term is the bits you waste by coding
for the wrong distribution. Optimal coding = knowing the true `p`; this is the same identity as
in `reference/divergence.md`, now wearing a coding hat.

## Huffman vs arithmetic coding

- **Huffman** builds an optimal *symbol* code by a greedy merge of the two least-probable
  symbols. It is optimal *among codes that assign an integer number of bits per symbol*. That
  integer constraint costs up to ~1 bit/symbol of overhead — catastrophic for skewed
  distributions where the entropy is a fraction of a bit (e.g. a symbol with `p=0.9` "deserves"
  0.15 bits but Huffman must spend ≥1).
- **Arithmetic coding** (and modern **ANS**) removes the integer constraint by encoding the whole
  message as one number in `[0,1)`; it approaches the entropy bound to within `O(1)` bits *total*,
  not per symbol. This is why real compressors (and all model-based compression) use arithmetic/
  ANS, not Huffman, whenever symbol probabilities are skewed or adaptive.
- **When Huffman is still fine:** roughly-uniform alphabets, or where decode simplicity/speed
  matters more than the last few percent (it's used as a back-end stage in DEFLATE/JPEG).

Correct the common conflation: Huffman is "optimal" only under the per-symbol-integer-length
restriction. It is *not* the best possible lossless coder; arithmetic coding beats it whenever
the entropy isn't close to an integer number of bits per symbol.

## Compression is prediction (the key bridge)

A probabilistic model and a lossless compressor are the same object: feed the model's
sequential predictions `q(xₜ | x_{<t})` into an arithmetic coder and the compressed length is
`Σ −log₂ q(xₜ|x_{<t})` bits — the model's **cumulative cross-entropy / NLL**. Therefore:
- **Better prediction ⇔ better compression**, exactly. A language model's "bits per character"
  is both its loss and the size of the file it could compress text to. (This is why compression
  benchmarks like enwik8/the Hutter Prize are treated as language-modeling benchmarks.)
- **Bits-back / minimum description length** make this rigorous for models with parameters:
  the cost of the data is "bits to describe the model" + "bits to describe the data given the
  model," which is precisely the MDL two-part code below.

Use this bridge to demystify cross-entropy for users: it's not an arbitrary loss, it's the
length of the message your model would send.

## Channel coding (in one paragraph)

The other half of Shannon's theory: a noisy channel has a **capacity** `C = max_{p(x)} I(X;Y)`
(the input distribution that maximizes mutual information through the channel), and reliable
communication is possible at any rate below `C` and impossible above it (noisy-channel coding
theorem). Source coding squeezes out redundancy; channel coding adds *structured* redundancy
back to survive noise. Most data-science work lives in source coding / prediction, so keep
channel capacity in view mainly for the identity `C = max I(X;Y)` and the Gaussian-channel
result `C = ½ log₂(1 + SNR)` bits/use, which underlies rate–distortion and the "information
bottleneck."

## Lossy compression: rate–distortion and the information bottleneck

Everything above is *lossless* (`H ≤ L < H+1`). When you're allowed to throw information away —
which is what every representation, embedding, quantization, and summary does — the governing
theory is **rate–distortion**. For a source `X`, a reproduction `X̂`, and a distortion measure
`d(x, x̂)`, the minimum bits per symbol needed to stay within average distortion `D` is

```
R(D) = min_{ p(x̂|x) : E[d] ≤ D }  I(X ; X̂)
```

The object being minimized is **mutual information** — rate-distortion is the dual of channel
capacity (capacity maximizes `I` subject to a power constraint; R(D) minimizes `I` subject to a
distortion constraint). `R(D)` is non-increasing and convex; `R(0)` recovers the lossless rate.
Worth memorizing: the **Gaussian source** `N(0, σ²)` under squared-error distortion has
`R(D) = ½ log₂(σ²/D)` for `0 ≤ D ≤ σ²` and `0` beyond — i.e., every halving of allowed MSE
costs exactly **½ bit per sample**. That closed form is the right back-of-envelope for "how many
bits to store this signal at this fidelity."

The **information bottleneck** (Tishby–Pereira–Bialek) is rate-distortion with the distortion
measure *replaced by relevance*: compress `X` into `T` while preserving information about a
target `Y`, trading the two off with `β`:

```
min_{ p(t|x) }   I(X ; T) − β · I(T ; Y)
```

`I(X;T)` is the rate (how much you compressed), `I(T;Y)` is the relevance (how much of what
matters you kept). This is a clean way to *frame* representation learning — a "good"
representation is a minimal sufficient statistic for `Y` — and it's the honest definition of
"compression that keeps the useful part." Two cautions to deploy:
- **It's a framing/objective, not a turnkey method.** The exact IB solution requires knowing
  `p(x, y)`; the "deep IB" / variational-IB estimators optimize *bounds* on these MI terms and
  inherit all the MI-estimation fragility in `estimation.md` (and the InfoNCE/MINE bound issues).
  Treat reported `I(X;T)`/`I(T;Y)` as bounds, not measurements.
- **The "IB explains deep learning" claims are contested.** The original compression-phase
  story is sensitive to the MI estimator and the nonlinearity used and does not reproduce
  cleanly in general; cite IB as a useful objective, not as a settled account of why networks
  generalize.

## The MDL bridge to model selection

**Minimum Description Length**: the best model is the one that most compresses the data,
counting the model's own description. The **two-part code** length is

```
L(model) + L(data | model)
```

`L(data|model)` is the cross-entropy/NLL (the prediction cost); `L(model)` is the cost of
encoding the parameters — and *quantizing parameters more finely costs more bits but lowers the
data cost*, so MDL trades fit against complexity automatically. Refined MDL replaces the crude
two-part code with the **Normalized Maximum Likelihood (NML)** / stochastic complexity, whose
complexity term is `log ∫ √|I(θ)| dθ` — a **volume in Fisher-information geometry**, not a count
of parameters. The payoff: MDL complexity depends on how *distinguishable* a model's
distributions are, so two models with the same parameter count can have different complexities.

This is the coding-theoretic sibling of the information criteria in
`reference/model-selection.md`: BIC is an approximation to `−log` marginal likelihood, which is
itself an approximation to NML/MDL stochastic complexity. They are not competing philosophies so
much as different resolutions of the same "bits to describe the data" idea.
