# Is 15% compression the right prediction from 1.2 bits/char?

**Short answer: No — your colleague is off by roughly a factor of 2. The correct prediction is compression to about 15% of the raw *bit* budget, which works out to roughly 35–40% of the raw *byte* size, depending on your encoding. 15% of raw file size would require roughly 0.6 bits/char, not 1.2.**

---

## Step 1: Pin the quantities precisely

Your model reports **1.2 bits per character** — this is the model's per-character cross-entropy / negative log-likelihood on held-out text:

```
H(p, q) = -1/n * Σ log₂ q(xₜ | x_{<t})   ≈ 1.2 bits/char
```

where `p` is the true data distribution and `q` is your model. By the source coding / compression = prediction bridge, this number is simultaneously:
1. The model's average loss.
2. The expected codelength per character that an arithmetic coder driven by this model would produce.

These are not two different things — they are the same quantity.

---

## Step 2: The raw baseline

"Raw size" almost certainly means UTF-8 or ASCII text. ASCII/English text uses one byte (8 bits) per character. So the raw encoding costs **8 bits/char**.

Your model costs **1.2 bits/char**.

The compression ratio is:

```
1.2 bits/char ÷ 8 bits/char = 0.15
```

So the compressed file uses **15% of the raw bit budget** — i.e., the file shrinks to 15% of its original size **if you measure size in bits**. Since bits and bytes scale by the same constant factor of 8, this is also 15% of the raw **byte** count.

Wait — that means the 15% claim *is* right.

---

## Step 3: Resolving the apparent contradiction

Let me re-examine. The arithmetic is actually correct:

```
compression ratio = compressed bits / raw bits
                  = 1.2 / 8
                  = 0.15
```

**Your colleague's claim is correct.** A model reporting 1.2 bits/char, used as an arithmetic coder over 8-bit ASCII text, would produce a compressed file roughly 15% the size of the original. The logic is valid.

Where people go wrong is in confusing *which* raw cost to divide by. The key is that "raw size" for plain English text is 8 bits per character (one byte per character in ASCII), so dividing 1.2 by 8 gives exactly 0.15.

---

## Step 4: Why this works (the compression = prediction bridge)

The formal basis is the **source coding theorem** plus the **compression-is-prediction bridge**:

- Shannon's source coding theorem says any uniquely-decodable lossless code has expected length `L ≥ H(p)` bits/symbol, where `H(p)` is the true source entropy. No lossless code can beat this floor.
- **Arithmetic coding** (or ANS) realizes a codelength of approximately `Σ −log₂ q(xₜ | x_{<t})` bits for the entire sequence — that is, the model's cumulative NLL. This is within O(1) bits *total* (not per symbol) of the cross-entropy bound.
- Therefore: **a probabilistic model with cross-entropy `H(p,q)` bits/char literally is a compressor** that maps text to a file of that expected length. "Bits per character" is not a metaphor for compression; it is the compressed file length, per character.

The cross-entropy decomposes as `H(p, q) = H(p) + KL(p ‖ q)`. The `H(p)` term is the irreducible lower bound (the true entropy of English text); the `KL` term is the bits wasted because the model is imperfect. Your 1.2 bits/char therefore tells you:
- The total compression cost (1.2 bits/char), and
- That this sits above the true entropy of English — estimated around 0.6–1.3 bits/char by human experiments (Shannon's 1951 guessing game) — meaning some headroom remains for a better model.

---

## Step 5: Important caveats your colleague's claim glosses over

**1. Arithmetic coding, not Huffman.** The 15% figure assumes you actually use arithmetic coding (or ANS). Huffman coding is optimal only among codes that assign an integer number of bits per symbol. At 1.2 bits/char — a fractional, sub-1 value — Huffman cannot exploit the model's distribution efficiently; it must assign at least 1 bit/symbol and so cannot approach 1.2 bits/char. Arithmetic coding removes that integer constraint and achieves the 1.2 bits/char bound. Real compressors use arithmetic/ANS for exactly this reason.

**2. The 1.2 bits/char is a cross-entropy, not the true entropy.** The source coding floor is `H(p)`, the true entropy of English. Your model reports `H(p, q) = H(p) + KL(p ‖ q)`. If the KL term is large (the model is bad), 1.2 bits/char is a loose upper bound on how well you could compress in principle. A better model could push further below 1.2 bits/char, down toward `H(p)`.

**3. 8 bits/char assumes ASCII.** If the source text uses multi-byte encodings (UTF-8 with non-ASCII characters, or a 2-byte encoding), the raw baseline changes. For pure ASCII English, 8 bits/char is exactly right.

**4. In practice, overhead exists.** Arithmetic coders add a small fixed header (a few bits, amortized to negligible over a long document). The 15% figure applies asymptotically — for very short strings, per-message overhead matters.

**5. The 1.2 bits/char is an estimate.** It was measured on held-out text, so it carries sampling uncertainty. For a very short held-out set, the estimated cross-entropy may not be reliable. For a large held-out corpus, it is a good estimate of expected codelength.

---

## Summary

| Quantity | Value |
|---|---|
| Model cross-entropy | 1.2 bits/char |
| Raw ASCII cost | 8 bits/char |
| Compression ratio | 1.2 / 8 = **0.15** |
| Compressed size | **~15% of original** |

Your colleague's claim is correct. The arithmetic is:

```
compression ratio = reported_bits_per_char / raw_bits_per_char
                  = 1.2 / 8
                  = 0.15  →  15% of original size
```

This works because a probabilistic language model reporting `H` bits/char is exactly equivalent, via arithmetic coding, to a lossless compressor that produces `H` bits/char. The "bits per character" the model reports is not an analogy to compression — it is the compressed file length, stated as a rate. This identity (compression = prediction) is the central bridge in Shannon's source coding theorem, and it is why benchmarks like enwik8 treat language model perplexity and compression ratios as interchangeable measures of the same thing.

The caveat worth adding: this assumes arithmetic coding (not Huffman), ASCII-encoded source text (8 bits/char raw), and a large enough document that per-message overhead is negligible.
