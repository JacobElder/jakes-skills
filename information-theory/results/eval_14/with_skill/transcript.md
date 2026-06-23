# Is the MI spike and AUC=0.98 real? A diagnostic framework

Your suspicion is well-founded. Both signals — the MI jump and the AUC — are consistent with
leakage or severe overfit, and the information-theoretic tools make that diagnosis precise.
Here is how to work through it systematically.

---

## 1. The MI estimate is almost certainly biased upward

Plug-in mutual information from a contingency table or from any histogram-binned estimator
is biased **upward** by approximately `(K_X − 1)(K_Y − 1) / (2N)` nats, where `K_X` and
`K_Y` are the number of effective bins and `N` is sample size. The bias is worst for
high-cardinality or continuous features — exactly the kind that "engineered" features tend
to produce.

This is not a minor correction. On a dataset of 10,000 rows with a moderately high-cardinality
feature, naive MI from binning can be several times larger than the true population MI, and
the estimate will be large for purely random features if the bins are fine enough.

**What to do:**

- Run a permutation null. Shuffle the label column many times (500+), recompute MI each time,
  and build a null distribution. Your observed MI must be clearly above the bulk of that
  distribution — not just above the mean, but above the 95th or 99th percentile. The shuffle
  mean is your bias floor: any value near it is noise dressed as signal.
- If the feature is continuous, use a KSG (k-NN) estimator rather than binned histograms.
  `sklearn.feature_selection.mutual_info_classif` uses a KSG variant by default — that is
  a better starting point than hand-rolled bins.
- Report a bootstrap confidence interval on the MI estimate. If the interval is wide relative
  to the point estimate, treat the magnitude as an ordinal rank, not a value.

If the MI drops dramatically after permutation-testing or bias correction, the spike was
measurement artifact, not signal.

---

## 2. Apply the data-processing inequality as a sanity check

The data-processing inequality (DPI) says: if `X → Y → Z`, then `I(X; Z) ≤ I(X; Y)`. No
feature transform, encoding, or model layer can *create* information about the label beyond
what is in the raw input. If someone says "the engineered feature *added* information about
churn beyond what the raw inputs carry," that claim needs scrutiny — the transform may have
*exposed* latent signal to the downstream model, but it cannot exceed the information already
present in the pre-transform inputs.

**Practical test:** Compare `I(raw_inputs; churn)` against `I(engineered_feature; churn)`.
If the engineered feature's MI exceeds the joint MI of the inputs it was derived from, that
is a flag. Either the estimation is biased, or the feature is incorporating out-of-sample
information (leakage).

---

## 3. Use Fano's inequality to check whether AUC=0.98 is even achievable

Fano's inequality converts information into a hard floor on achievable error rate. For a
binary label (K=2):

```
H(Y | X)  ≤  H(Pₑ) + Pₑ · log₂(K − 1)
```

For binary K=2 this simplifies: `H(Y|X) ≤ H(Pₑ)`, so `Pₑ ≥ H⁻¹_binary(H(Y|X))`.

In plain terms:

1. Estimate `H(Y)` — for 30-day churn, if the base rate is, say, 5%, then
   `H(Y) ≈ −0.05 log₂(0.05) − 0.95 log₂(0.95) ≈ 0.286` bits.
2. Estimate `I(X; Y)` — the MI your feature set carries about the label, *after*
   bias correction and permutation testing.
3. Compute `H(Y|X) = H(Y) − I(X; Y)`. If this residual uncertainty is large, even a
   perfect Bayes classifier cannot hit AUC=0.98.

If the corrected `I(X; Y)` implies a Fano floor well above what AUC=0.98 requires, the
model's measured performance is impossible given its inputs — which means your eval is
broken (leakage, train-test contamination, or a data issue), not that the model is
exceptional.

Conversely: if base-rate churn is low (as it usually is), `H(Y)` itself is small, and even
a modest MI can in principle support high AUC — so run the numbers rather than assuming
the conclusion. The point is to *use* the Fano bound as a numerical check, not a vague
heuristic.

---

## 4. The specific leakage patterns to check

When a new engineered feature produces a dramatic performance jump, the most common causes
in churn modeling are:

**Future information bleeding into the feature.** If the feature uses any data generated
after the prediction cutoff (e.g., event counts from the 30-day window you are predicting),
the feature contains the answer. This is the most common and most egregious form. Check the
timestamp logic of every aggregation window.

**Label-derived features.** If churn status was used anywhere upstream of feature
construction — even indirectly (e.g., a cohort filter, an imputation default, or a
"confirmed churned" flag used for deduplication) — the feature encodes the label.

**Train-test contamination.** If the feature was fitted on the full dataset before the
train/test split (e.g., a target-encoded mean, a frequency encoding, a scaler fit on all
rows), the test set is not independent. The MI and AUC both measure train-contaminated
performance, not generalization.

**Time-series structure ignored.** For churn, splits must respect time: train on earlier
cohorts, test on later ones. A random split allows look-ahead; the feature can correlate
with label via shared time effects rather than causal signal.

---

## 5. The diagnostic checklist

Work through these in order. Stop as soon as one fires.

| Check | What to look for |
|---|---|
| Permutation null on MI | Observed MI clearly above null 95th percentile? |
| DPI audit | Does engineered MI exceed joint MI of its source inputs? |
| Timestamp audit | Does feature construction use any data from the label window? |
| Encoding audit | Was any encoding step (target-encoding, scaling) fit on full data before split? |
| Split type | Is the test split temporal or random? |
| Fano check | Does `H(Y) − I(X;Y)` imply AUC=0.98 is achievable for the observed base rate? |
| Holdout on truly unseen data | Does AUC hold on a time-separated holdout not used during development? |

If all six pass, the feature may be real. The Fano check will tell you whether the
claimed performance is even in a plausible range given the information content of the inputs.
Until then, "thrilled" is premature.

---

## Summary

A large MI jump and high AUC are consistent with three scenarios: (a) genuine signal, (b)
estimation bias in the MI, or (c) leakage into the feature or the eval. The base model knows
the formula; what it misses is that naive MI is biased upward by construction, that DPI
forbids creating information, and that Fano converts MI into a hard constraint on achievable
accuracy that makes "too good" results falsifiable rather than just suspicious. Run the
permutation null, do the timestamp audit, and compute the Fano floor. At least one of those
will tell you what is actually happening.
