# Why Your Decision Tree Picks `customer_id` First — and How to Fix It

## The root cause: information gain is biased upward for high-cardinality features

Information gain in a decision tree is mutual information between the split feature and the target:

```
IG(feature) = H(Y) − H(Y | feature)
            = I(feature ; Y)
```

Plug-in mutual information — computed directly from empirical counts — is **biased upward** by approximately:

```
E[Î_plugin] ≈ I + (K_X − 1)(K_Y − 1) / (2N)
```

where `K_X` is the number of distinct values of the feature, `K_Y` is the number of target classes, and `N` is sample size.

`customer_id` has one distinct value per row, so `K_X ≈ N`. The bias term becomes `(N − 1)(K_Y − 1) / (2N) ≈ (K_Y − 1) / 2`, which is independent of actual signal and grows only with the number of target classes. For a binary target (`K_Y = 2`) this adds roughly 0.5 nats of spurious "information" to every unique-ID feature. For a ten-class target, it adds about 4.5 nats — regardless of whether the feature has any real predictive content. This is not a rounding error; it is a structural artifact that dominates the information gain score every time `K_X` is large relative to `N`.

The leaves coming out pure is the same phenomenon from a different angle: with one row per leaf, the conditional entropy `H(Y | feature)` is exactly zero by construction. A feature that assigns every observation its own bucket will *always* produce pure leaves and maximum information gain, even if its values were randomly generated.

## Why this is an estimation problem, not a signal problem

The split looks compelling — pure leaves, large IG — but every bit of that gain is an estimation artifact. If you generated a synthetic `random_id` column with `N` unique values drawn from a hash function, it would score identically to `customer_id`. The mutual information between a random unique identifier and any target is exactly zero in the population; the sample estimate reports something large and positive entirely because the plug-in estimator cannot distinguish "lots of signal" from "lots of categories, few counts per cell."

The rule of thumb: if `N / K` (average counts per cell in the contingency table) is not at least 10–30, the plug-in estimate is dominated by bias. For `customer_id`, `N / K ≈ 1`. You are as far into the undersampled regime as it is possible to be.

## Three fixes, in order of preference

### 1. Drop ID-like columns before fitting

The right intervention is upstream of the tree: remove `customer_id`, transaction IDs, row hashes, and any other column whose semantic role is "unique identifier." These carry zero population-level MI with any target by construction. No bias correction will help once you include them, because the estimator was never the problem — the feature was the problem. Encode the *relationships* that IDs index (customer history, aggregated behavior) as real features instead.

```python
# Drop before fitting
df_model = df.drop(columns=["customer_id", "transaction_id"])
```

### 2. Use gain ratio instead of information gain

C4.5 (and scikit-learn's `criterion="entropy"` does not implement this by default, but it can be replicated manually) normalizes information gain by the entropy of the split itself:

```
GainRatio(feature) = IG(feature) / H(feature)
```

A unique-ID column has `H(feature) ≈ log₂(N)` (maximum entropy — completely unpredictable), which is enormous. Dividing by that large denominator collapses the gain ratio of high-cardinality features to near zero, while leaving the ratio approximately unchanged for features with moderate cardinality. This is the classic fix and it works.

Note that gain ratio is not directly available as a scikit-learn option; you would need to implement it manually or use a library that exposes it. CART (which scikit-learn implements) uses Gini impurity or entropy but does not apply cardinality normalization, so this fix requires stepping outside the default API.

### 3. Apply the Miller–Madow correction and/or a permutation null

If you must compute information gain from counts (e.g., for a custom feature ranker), apply the Miller–Madow bias correction to each entropy term before taking differences:

```
Ĥ_MM = Ĥ_plugin + (K̂ − 1) / (2N)
```

Apply this correction to `H(Y)`, `H(feature)`, and `H(Y, feature)` consistently. Then compute `IG = Ĥ_MM(Y) + Ĥ_MM(feature) − Ĥ_MM(Y, feature)`.

More robustly: run a permutation null. Shuffle the target `Y` relative to the feature 200+ times, recompute IG each time, and compare your observed IG to the shuffled distribution. Any feature whose IG is not clearly above the shuffle mean (say, > 2σ above, or outside the 95th percentile of shuffled values) has no real signal. `customer_id` will sit squarely inside the null distribution once the shuffle destroys any real structure — which is the correct answer.

## Summary of the information-theoretic diagnosis

| What happened | Why |
|---|---|
| `customer_id` has enormous IG | Plug-in MI biased upward by `≈(K_X−1)(K_Y−1)/(2N)`; with `K_X = N`, the bias dominates completely |
| Leaves come out pure | One row per bucket → conditional entropy is 0 by construction, not by signal |
| Other real features rank lower | Their IG contains genuine signal but less bias; the bias on `customer_id` overwhelms them |

**The fix that actually solves the problem:** drop ID columns before training. Gain ratio is a good secondary defense for high-cardinality categoricals you want to keep (e.g., ZIP code, product SKU). The permutation null gives you a principled sanity check on any computed IG before you trust it.
