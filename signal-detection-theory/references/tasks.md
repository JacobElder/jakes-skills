# Discrimination Task Taxonomy — choosing the right d' model

"SDT" is not one task. The relationship between observed performance and d' depends on the **task structure** and, for some tasks, on the **decision rule** the observer uses. Getting this wrong means your d' is on the wrong scale. This file is the routing layer: identify the task, then use the right conversion (and, in practice, the right `sensR` method rather than a hand-derived formula).

## The two questions that fix the model

1. **How many stimuli per trial, and what's the response?** (one stimulus + yes/no vs. several stimuli + pick-one vs. judge-relation)
2. **For relational tasks, what decision rule?** (independent-observation vs. differencing — they give *different* d' from the same proportion correct)

## The task families

### Single-interval / yes-no
One stimulus, "signal present?" → d', c. **Bias is live.** This is the default `formulas.md` case. The decision variable is compared to a single criterion.

### m-Alternative Forced Choice (mAFC)
Signal and m−1 noise alternatives presented together; pick the one that seems to be the signal. **Bias is largely neutralized** (no criterion to set).
- **2AFC:** `d' = √2 · z(Pc)` (decision variable is the difference of two draws, variance 2).
- **mAFC (m > 2):** Pc relates to d' through an integral over the maximum of m−1 noise draws vs. one signal draw — there is **no closed form**. Use tables (Hacker & Ratcliff 1979; Elliott) or `sensR`/`psyphy`. Do not reuse the 2AFC √2 formula for m > 2.

### Same-different
Two stimuli per trial; judge "same" or "different." **The decision rule matters and changes the d'↔Pc mapping:**
- **Independent-observation rule:** the observer forms two separate observations and a decision based on their joint position. More efficient.
- **Differencing rule:** the observer computes |obs₁ − obs₂| and compares it to a criterion. Less efficient; common when stimuli aren't labeled by interval.
Same-different is **much less efficient** than 2AFC — you need a substantially larger d' to reach the same proportion correct. Report which rule you assume; don't quote a same-different d' as if it were a 2AFC d'.

### ABX (matching-to-sample)
Present A, then B, then X; X equals A or B — say which. d' depends on the decision rule (typically a differencing-type rule). Intermediate efficiency.

### Oddity / triangle / tetrad (sensory science)
Several stimuli, all-but-one identical; pick the odd one (triangle = 3 stimuli with 2 alike; tetrad = 4). Ubiquitous in food/consumer science. **Highly inefficient** — chance is 1/3 for the triangle, and a given d' yields low Pc. Each protocol has its own psychometric function (Thurstonian model).

### Rating / confidence
Yes-no plus a confidence scale → a full ROC. Fit the z-ROC (unequal variance). See `formulas.md` §4 and `estimation.md`. Strongly preferred whenever you can collect confidence, because it *tests* rather than *assumes* equal variance.

## Practical rule: don't hand-derive non-2AFC conversions — use sensR

For everything beyond yes-no and 2AFC, the protocol-specific Pc↔d' conversions are fiddly and easy to get wrong. R's **`sensR`** package implements them directly via a Thurstonian model:

```r
library(sensR)
# one entry point, choose the protocol with `method`
discrim(correct = 35, total = 50, method = "triangle")   # triangle test
discrim(40, 50, method = "twoAFC")                        # 2AFC
discrim(38, 50, method = "threeAFC")                      # 3AFC
discrim(33, 50, method = "duotrio")                       # duo-trio
discrim(42, 60, method = "tetrad")                        # tetrad
samediff(nsamesame = 25, ndiffsame = 8,                   # same-different
         nsamediff = 10, ndiffdiff = 22)
# convert / test d' across protocols:
psyfun(d.prime = 1.5, method = "triangle")  # protocol Pc for a given d'
dprime_test(...); dprime_compare(...)        # inference on d'
```
`discrim()` returns d' on a common scale **with a standard error and CI**, so cross-protocol comparison is valid (a triangle d' and a 2AFC d' become comparable once both are Thurstonian d'). In Python there is no equivalent full package; for non-2AFC protocols, call out to `sensR` or implement the specific psychometric function from Macmillan & Creelman ch. 9 with care.

## The one-line decision guide
- yes/no → d', c (sdt.py / sdt.R)
- 2AFC → `√2·z(Pc)`
- mAFC, same-different, ABX, triangle/tetrad/duo-trio → **`sensR::discrim(..., method=...)`**; never the 2AFC formula
- have confidence ratings → fit the z-ROC (rating model), report d_a / A_z
