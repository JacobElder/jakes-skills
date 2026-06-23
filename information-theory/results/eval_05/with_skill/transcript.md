# Why Your Huffman Coder Costs ~1 Bit/Symbol Even Though Entropy Is Low

## The short answer

Huffman is **optimal only among codes that assign an integer number of bits per codeword**. That integer constraint is the entire problem. At 95% skew, the entropy is roughly 0.29 bits/symbol, but Huffman must assign at least 1 bit to every codeword, so the dominant symbol still costs 1 bit — a 3× overhead. You are not doing anything wrong with the Huffman implementation itself; you have hit the fundamental ceiling of the per-symbol-integer-length restriction.

---

## The arithmetic in detail

For a binary-ish alphabet where one symbol `A` has probability `p = 0.95` and the rest share `q = 0.05`:

```
H(X) = −0.95 log₂(0.95) − 0.05 log₂(0.05)
     ≈ 0.0740 + 0.2161
     ≈ 0.286 bits/symbol
```

Huffman gives `A` a codeword of length **1** (the shortest possible integer). The expected codeword length is:

```
L_Huffman ≥ 1 · 0.95 + (longer codes) · 0.05 ≈ 1 bit/symbol
```

Compare to the entropy floor: 0.286 bits/symbol. The overhead is roughly **3.5×**. This is not a bug — it is the expected behavior of Huffman on a highly skewed source.

The source coding theorem guarantees:

```
H(X) ≤ L < H(X) + 1
```

The upper bound `H + 1` is nearly tight here because `H ≈ 0.29` leaves almost the full ±1 bit of slack on the high side. Huffman reaches that ceiling and cannot go below 1 bit/symbol no matter how you tune it.

---

## Why Huffman cannot escape this

The Kraft inequality requires that codeword lengths be positive integers. The minimum integer is 1. So the most frequent symbol will always receive a codeword of length ≥ 1. When one symbol dominates at 95%, that symbol drives nearly all the expected cost, and 1 bit is the floor.

**Huffman is "optimal" in the sense of minimizing expected length among all prefix codes with integer lengths.** But that optimality guarantee does not extend to "optimal among all lossless codes," and the gap is catastrophic when the entropy per symbol is a fraction of a bit.

---

## The fix: arithmetic coding (or ANS)

**Arithmetic coding** (and its modern variant, Asymmetric Numeral Systems / ANS) removes the per-symbol integer constraint by encoding the entire message as a single number in `[0,1)`. The compressed length approaches the source entropy:

```
L_arithmetic → H(X) bits/symbol  (within O(1) bits total, not per symbol)
```

For your stream at `H ≈ 0.286 bits/symbol`:

| Coder | Expected bits/symbol | Overhead |
|---|---|---|
| Huffman | ~1.0 | ~3.5× |
| Arithmetic / ANS | ~0.29 | ~1.01× |

That is a roughly 3.5× file size reduction just by switching the coding back-end. The probability model stays the same; only the way it is mapped to bits changes.

### How arithmetic coding works (the key idea)

At each symbol, arithmetic coding subdivides the current interval proportionally to the symbol probabilities. After `n` symbols, the interval has length approximately `∏ pᵢ`, and encoding the final interval requires approximately `−log₂(∏ pᵢ) = Σ −log₂ pᵢ` bits — which is exactly the cross-entropy of the sequence. No rounding to integers happens at the per-symbol level.

---

## Alternative: block Huffman (a partial fix)

If you want to keep Huffman for implementation simplicity, **block** your stream into groups of `k` symbols and build the Huffman code over the `|Σ|^k` joint symbols. The overhead amortizes:

```
L_block / k → H(X) as k → ∞
```

For `k = 8` on a binary alphabet dominated 95/5:

- The joint entropy of 8 symbols is `8 × 0.286 ≈ 2.29` bits.
- Huffman over 2^8 = 256 joint codewords can get within `H + 1/8` bits per original symbol.
- Expected cost per original symbol: `≈ 0.286 + 0.125 ≈ 0.41 bits/symbol` vs `~1.0 bit/symbol` for symbol-by-symbol Huffman.

This is much better, but it has exponential alphabet blowup (`|Σ|^k` codewords) and still has residual overhead. Arithmetic/ANS does the same thing without the blowup and without the residual.

---

## Practical recommendation

Use **arithmetic coding or rANS** (range ANS) as your entropy coder. Almost every modern compressor that operates on highly skewed distributions does this — LZMA, Zstandard, HEVC, AV1 all use ANS or arithmetic coding for their entropy stage. Huffman survives only in roughly-uniform contexts (e.g., DEFLATE's literal/length codes are reasonably flat after LZ77 back-reference removal, and the speed/simplicity tradeoff is acceptable there).

If you are in a constrained environment where arithmetic coding is unavailable, block Huffman with `k ≈ 8–16` will recover most of the gap.

---

## Summary

| Concept | What it means here |
|---|---|
| Entropy ≈ 0.286 bits/symbol | The true compressibility floor for your source |
| Huffman ≈ 1 bit/symbol | Expected — it cannot go below 1 bit/symbol regardless of skew |
| The gap (0.714 bits/symbol) | Entirely due to the per-symbol integer-length constraint, not a bug |
| Fix | Arithmetic coding or ANS — approaches entropy to within O(1) bits *total* |
| Partial fix | Block Huffman with block size `k`; overhead drops to `~1/k` bits/symbol |
