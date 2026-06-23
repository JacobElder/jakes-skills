# Why Decision Trees Split on customer_id (and How to Fix It)

## What's happening

A decision tree algorithm selects splits by maximizing an impurity reduction criterion — typically information gain (based on entropy) or Gini impurity. A column like `customer_id` is a unique identifier: every row has a distinct value. When the tree evaluates that column, it sees a feature with as many distinct values as there are rows. Splitting on it produces one leaf per customer, each containing exactly one sample. A single-sample leaf is trivially pure — zero entropy, zero Gini impurity. The information gain from that split is therefore as large as it can possibly be, and the tree greedily selects it.

The tree is not broken or buggy. It is doing exactly what you asked: finding the split that maximally reduces impurity. The problem is that "information gain" as classically defined measures impurity reduction without any penalty for the number of children a split produces. A unique-ID column exploits this loophole perfectly.

## Why the split is useless despite being "optimal"

The whole point of a tree is to generalize — to describe patterns that will hold on unseen data. A split on `customer_id` memorizes the training set completely. On any new customer the model has never seen, the rule is undefined (the value falls outside every trained leaf). This is the textbook definition of overfitting: zero training error, zero generalization.

More precisely, information gain measures

```
IG(S, A) = H(S) - sum_v [ (|S_v| / |S|) * H(S_v) ]
```

where `H` is entropy and `v` ranges over the values of attribute `A`. When every value of `A` is unique, `|S_v| = 1` for all `v`, so `H(S_v) = 0` and `IG(S, A) = H(S)` — the maximum possible gain. The measure has no term that asks "how many distinct values does A take?" or "how well does this split generalize?"

## Five ways to prevent it

### 1. Drop identifier columns before training

This is the most reliable fix. Columns that are identifiers (`customer_id`, `user_id`, `order_id`, `email`, `SSN`) carry no causal or predictive signal; they are indexing artifacts. Remove them from the feature matrix entirely before fitting.

```python
# pandas
X = df.drop(columns=["customer_id", "order_id"])
```

This is almost always the right answer when the column is a true identifier.

### 2. Use Gain Ratio instead of raw Information Gain

Gain Ratio (the criterion used in C4.5 and C5.0) penalizes attributes that split into many branches by dividing information gain by the attribute's own entropy (called "split information"):

```
GainRatio(S, A) = IG(S, A) / SplitInfo(S, A)

SplitInfo(S, A) = -sum_v [ (|S_v| / |S|) * log2(|S_v| / |S|) ]
```

A unique-ID column has maximum `SplitInfo` (because every partition has size 1), so the ratio is driven toward zero. Columns with a small number of informative splits are preferred instead.

scikit-learn's `DecisionTreeClassifier` does not natively expose gain ratio, but switching to a C4.5-derived implementation (e.g., `chefboost`, or implementing the criterion manually) gives you this behavior.

### 3. Use Gini impurity with a cardinality cap

Gini impurity shares the same vulnerability to high-cardinality features as information gain, but you can combine it with hyperparameter constraints that indirectly protect against ID columns:

- `max_depth`: a shallow tree cannot exhaust a unique-ID split all the way down
- `min_samples_leaf`: requiring at least *k* samples per leaf prevents single-sample leaves; any split that would produce a leaf with fewer than `min_samples_leaf` samples is rejected, which blocks pure-by-uniqueness splits when *k* > 1

```python
from sklearn.tree import DecisionTreeClassifier

clf = DecisionTreeClassifier(
    min_samples_leaf=10,   # no leaf with fewer than 10 samples
    max_depth=5,
    random_state=42
)
```

These constraints do not remove the logical flaw; they suppress its worst manifestation.

### 4. Encode high-cardinality categoricals correctly (or drop them)

If the column is not a pure ID but has very high cardinality (e.g., zip codes, product SKUs), consider:

- **Frequency / target encoding**: replace the raw value with aggregate statistics (mean of target per category, frequency of that value in the training set). This collapses cardinality and retains signal.
- **Dropping**: if cardinality approaches n_samples, the column is effectively an ID and should be dropped.

### 5. Cross-validate to detect the symptom early

If you observe training accuracy near 100% and validation accuracy far lower, that is the diagnostic signature of this problem (and overfitting in general). A learning curve that shows near-zero training error but high validation error is a direct signal that an ID column or similar memorization artifact is leaking into the model.

## Summary

| Root cause | Fix |
|---|---|
| Information gain has no cardinality penalty | Switch to Gain Ratio (C4.5 criterion) |
| Column is a true row identifier | Drop it before fitting |
| High-cardinality categorical with some signal | Target-encode or frequency-encode |
| Want a quick guardrail without restructuring | Set `min_samples_leaf` ≥ 2–10 |

The cleanest solution is the first: if `customer_id` has no predictive meaning, remove it from the feature matrix. Any other approach is working around a data-cleaning error. Gain Ratio is the principled algorithmic fix if you have categorical features with legitimately varying cardinality and want the tree to handle them without manual filtering.
