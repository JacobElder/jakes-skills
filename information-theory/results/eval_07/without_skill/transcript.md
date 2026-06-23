# Is 15% Compression Achievable from 1.2 Bits per Character?

## Short Answer

No, the claim is wrong. A model reporting 1.2 bits per character implies a theoretical compression ratio of roughly **15% of the original size only if raw ASCII text uses 8 bits per character**. Under that assumption the math works out: 1.2 / 8 = 0.15, which is 15%. But that baseline is misleading. Raw English text encoded in UTF-8 or ASCII does use 8 bits per character, so the arithmetic is technically correct — but the conclusion conflates the theoretical entropy limit with achievable compression, and it also depends on what "raw size" means. Let me unpack both issues carefully.

---

## The Shannon Entropy Connection

A language model assigns a probability distribution over the next character given all prior context. If the model is well-calibrated, its per-character cross-entropy on held-out text estimates the true entropy rate of the source:

$$H \approx \frac{1}{N} \sum_{i=1}^{N} -\log_2 p(c_i \mid c_1, \ldots, c_{i-1})$$

When your model reports **1.2 bits per character**, it means the average surprise under the model is 1.2 bits per character. Shannon's source coding theorem tells us that the minimum average code length per symbol, using an optimal code matched to those probabilities, approaches the entropy from above. So **1.2 bits per character is the theoretical lower bound on lossless compression** achievable by an arithmetic coder or range coder that uses exactly this model's probability estimates.

---

## Where the 15% Figure Comes From

Plain ASCII text stores each character in **8 bits** (1 byte). If you could compress perfectly to 1.2 bits per character, the compressed file would occupy:

$$\text{compression ratio} = \frac{1.2 \text{ bits/char}}{8 \text{ bits/char}} = 0.15 = 15\%$$

So the arithmetic is straightforward, and the 15% figure is the right theoretical compression ratio relative to an 8-bit-per-character baseline.

---

## Why the Claim Is Misleading (or Only Conditionally Right)

### 1. Theoretical limit vs. practical compression

The 1.2 bits/character is the **entropy estimate under this model**, not the entropy of the actual source. The true entropy of written English is estimated to be around 1.0–1.3 bits per character (Shannon's original experiments suggested roughly 1.0–1.3 bpc for English), so 1.2 is plausible but is still the model's cross-entropy, not necessarily the true source entropy. There will be a small gap between what the model achieves and the true theoretical minimum.

More practically, to actually achieve compression at 1.2 bits/character you need an **arithmetic coder** (or asymmetric numeral systems encoder) driven by the model's probability outputs at every character position. Standard compression tools (gzip, bzip2, LZ77) do not use neural language model predictions and will not approach this limit. The 15% figure is achievable in principle only if you build a compressor that uses the model as its probability estimator.

### 2. The baseline matters

The 15% figure assumes **8 bits per character** as the baseline. This is appropriate for ASCII text. But:

- If your "raw text" is already stored in a more compact encoding (e.g., some files pack characters differently), the baseline changes.
- If you compare against another general-purpose compressor rather than raw ASCII, the gain looks smaller. For example, gzip might already compress English text to roughly 30–40% of its raw size (around 2.5–3.2 bits/character). Against a gzip baseline, 1.2 bits/character represents a factor of roughly 2–2.5× additional compression, not 6.7×.

### 3. Cross-entropy is an upper bound on the achievable compression rate

Because cross-entropy $H(p_\text{true} \| p_\text{model}) \geq H(p_\text{true})$, the model's reported bits per character is always **at least as large as the true entropy**. A perfect model would achieve the true entropy; an imperfect model wastes bits by misassigning probability. So 1.2 bpc is an upper bound on the compression limit, not the exact limit. You cannot do better than the true entropy; you can do exactly as well as 1.2 bpc if you use this model perfectly as a coder.

---

## Putting It Together

| Quantity | Value |
|---|---|
| Model cross-entropy | 1.2 bits/char |
| Raw ASCII baseline | 8 bits/char |
| Theoretical compression ratio (vs. raw ASCII) | 1.2 / 8 = **15%** |
| True English entropy (estimated) | ~1.0–1.3 bits/char |
| Achievable in practice? | Only with arithmetic coding driven by the model |

---

## Verdict

Your colleague's claim is **arithmetically correct but requires important qualifications**:

1. The 15% figure is a theoretical lower bound on file size, achievable only with an optimal arithmetic coder that uses your model's probability outputs directly.
2. It assumes 8-bit-per-character raw storage as the baseline.
3. It conflates the model's cross-entropy (which bounds achievable compression from above) with the true source entropy (the absolute minimum).
4. In practice, building such a compressor is feasible — arithmetic coding with a neural LM as the probability model is exactly how neural text compression systems like NNCP or "compress with a language model" work — but standard file compressors will not get you there automatically.

So: yes, with the right compressor, you could in principle compress to roughly 15% of raw ASCII size. But calling it a guaranteed property of the model report alone, without the necessary arithmetic coding infrastructure, overstates what the number alone implies.
