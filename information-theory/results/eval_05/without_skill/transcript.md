# Why Your Huffman Coder Spends ~1 Bit/Symbol on a Skewed Source

## The Core Problem: Huffman Codes Are Symbol-by-Symbol

Huffman coding assigns one codeword per source symbol. The shortest possible codeword is 1 bit. When your dominant symbol has probability 0.95, its theoretical code length is:

```
-log2(0.95) ≈ 0.074 bits
```

But Huffman must assign it a codeword of at least 1 bit — it cannot represent fractional bits. So you're spending roughly 13× more bits than the entropy requires for that symbol. The total entropy of the source is around 0.286 bits/symbol (for a two-symbol source with p=0.95, p=0.05), but your coder burns ~1 bit/symbol because of this floor.

This is not a bug in your implementation. It is a fundamental limitation of symbol-by-symbol (memoryless, one-at-a-time) Huffman coding. The problem is the model, not the code.

---

## The Fix: Group Symbols Before Coding

The solution is to code blocks of N symbols together rather than one symbol at a time.

### Why Blocking Works

If you group N symbols into a single "super-symbol," the alphabet size grows to k^N (where k is the number of distinct source symbols), and you apply Huffman (or any prefix code) to that extended alphabet. The redundancy per symbol shrinks toward zero as N grows, because you can now assign shorter average codes to the common super-symbols and longer codes to the rare ones.

For a two-symbol source with p=0.95:

| Block size N | Entropy (bits/sym) | Huffman rate (bits/sym) | Redundancy |
|---|---|---|---|
| 1 | 0.286 | ~1.0 | ~0.714 |
| 4 | 0.286 | ~0.35 | ~0.064 |
| 8 | 0.286 | ~0.30 | ~0.014 |

The per-symbol redundancy of Huffman on a block code is bounded by 1/N bits/symbol, so increasing block size directly drives redundancy down.

**Trade-off:** The extended alphabet has k^N entries. For a binary source grouped in blocks of 8, that's 2^8 = 256 codewords — manageable. For a larger alphabet grouped in large blocks, the codebook can become impractically large.

---

## Better Alternative: Arithmetic Coding (or ANS)

Arithmetic coding (and its modern variant, Asymmetric Numeral Systems / ANS) sidesteps the 1-bit-per-symbol floor entirely. Instead of assigning codewords to individual symbols, these methods encode the entire sequence as a single number in the interval [0, 1), partitioned according to cumulative symbol probabilities.

**Arithmetic coding achieves a rate within 2 bits of the true entropy for the whole message** (not per symbol), and in practice operates very close to entropy regardless of how skewed the distribution is. For your 95/5 source, it will approach 0.286 bits/symbol automatically.

### Run-Length Encoding (RLE) as a Simpler Option

If your stream is literally one symbol nearly all the time with occasional rare symbols, RLE is worth considering:

- Encode runs of the common symbol as a count.
- Encode rare symbols literally.

The compressed representation is (count, rare_symbol) pairs. This is simple, fast, and highly effective when runs are long — which they will be when one symbol appears 95% of the time (expected run length ≈ 20 symbols before hitting a rare one).

---

## Summary

| Method | Achieves Near-Entropy? | Notes |
|---|---|---|
| Symbol-by-symbol Huffman | No | 1-bit floor kills you on skewed sources |
| Block Huffman (N symbols) | Approaches it | Redundancy ≤ 1/N; codebook grows as k^N |
| Arithmetic / ANS coding | Yes | Best general solution; negligible overhead |
| Run-length encoding | Yes (for this specific case) | Simple but fragile if distribution changes |

**Recommended fix:** Replace your Huffman coder with arithmetic coding or ANS. Both are well-supported in existing libraries (e.g., `range_coder` in Python, `rans` implementations in C). If you must keep Huffman, group symbols into blocks of 8–16 before coding. For this particular source structure (one very dominant symbol), RLE followed by Huffman on the rare events is also efficient and easy to implement.
