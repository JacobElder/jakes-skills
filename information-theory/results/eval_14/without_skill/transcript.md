# Is Your AUC 0.98 Real? A Framework for Diagnosing Suspicious Feature Gains

Your suspicion is well-placed. A jump to AUC 0.98 on a 30-day churn problem is almost never a genuine signal improvement — it is almost always a data artifact. Here is how to reason through it systematically.

---

## The Prior Should Make You Skeptical

Real-world churn prediction rarely exceeds AUC 0.85–0.90 on clean data, and typically lands in the 0.70–0.80 range when built carefully. A jump to 0.98 from a single engineered feature, accompanied by a spike in mutual information (MI), is a red flag, not a cause for celebration. The prior probability that this is legitimate is low. That prior should shift the burden of proof heavily onto the feature.

---

## The Most Likely Culprits

### 1. Target Leakage

This is the single most common cause of suspiciously high AUC and inflated MI. Target leakage occurs when the feature directly encodes information about the label, either because:

- The feature is computed from data that was only available *after* churn occurred (look-ahead bias)
- The feature aggregates or summarizes an event that *is* churn or is definitionally linked to it (e.g., a "cancellation request" flag, a "last login before cutoff" field, a "support ticket resolved post-cancellation" count)
- The feature was computed over a time window that bleeds past the prediction date into the outcome period

**How to check:** Trace the feature's construction end-to-end. For every data source it touches, ask: *Could this value change after the label is assigned?* Draw a timeline. The prediction date is T. Churn is observed over [T, T+30]. Every input to the feature must be computed from data observed strictly before T.

### 2. Train/Test Contamination

If the test set was used during feature engineering — even indirectly — the AUC does not reflect out-of-sample generalization.

- Was any normalization, scaling, or imputation fit on the full dataset before the split?
- Was the feature selected or tuned based on performance that included the test set?
- Is this a single fixed split, or was there a holdout that was "peeked at" iteratively?

**How to check:** Re-run the evaluation on a completely fresh holdout that was set aside before *any* feature engineering began. If you do not have one, set one aside now and evaluate cold.

### 3. Definition Mismatch Between Train and Serve

The feature may be computable in training (where you have full history) but would require future data at serve time. This produces a feature that looks predictive in retrospect but is useless or impossible in production.

**How to check:** Write out exactly how you would compute this feature in a live scoring pipeline the moment a user hits day T. If you would need data that does not yet exist, the feature has a lookahead problem.

### 4. Label Imbalance and MI Estimation Artifacts

Mutual information estimated from finite samples on imbalanced datasets can be inflated. If churn is rare (say 2–5%), MI estimators — especially histogram-based or k-NN-based estimators — can produce noisy, upward-biased estimates when one class has very few samples.

**How to check:**
- Report MI with confidence intervals or bootstrap standard errors, not a point estimate
- Compute MI separately within each class and check for anomalies
- Use a proper MI estimator designed for continuous features (e.g., MINE, k-NN estimators like sklearn's `mutual_info_classif` with appropriate neighbors)

### 5. The Feature Is a Near-Perfect Proxy for the Label

Even without strict leakage, a feature may be so causally close to churn that it is essentially the same variable. For example, "days since last login in the last 30 days" computed on the day the label window closes is nearly the same as the churn outcome.

**How to check:** Look at the feature distribution stratified by churn status. If the two distributions are nearly non-overlapping, ask whether the feature captures something genuinely antecedent to churn or is churn under a different name.

---

## A Systematic Diagnostic Checklist

Work through these in order:

**Step 1 — Temporal audit**
- Draw a timeline showing the prediction date (T), the feature computation window, and the churn observation window (T to T+30)
- Verify that every data source feeding the feature is finalized before T
- Check for any joins or aggregations that pull post-T data

**Step 2 — Cold holdout evaluation**
- Identify a time-based holdout (preferred) or a randomly held-out 20% that was untouched during feature engineering
- Re-compute the feature from scratch on this holdout using only data available before each observation's T
- Evaluate AUC on this cold holdout without any retraining

**Step 3 — Feature ablation**
- Train two models: one with the new feature, one without
- If the model *without* the feature already achieves 0.92+ AUC on the cold holdout, the feature is adding marginal legitimate value; if the model *without* the feature sits at 0.70 and the model *with* it jumps to 0.98, the feature is almost certainly leaking

**Step 4 — Production simulation**
- Simulate the exact scoring pipeline at serve time: at time T for a given user, what data is available?
- Compute the feature using only that data
- If the feature value changes when computed with only pre-T data vs. the training pipeline, you have confirmed leakage

**Step 5 — Calibration check**
- A model with AUC 0.98 should have very well-calibrated probabilities
- Plot a calibration curve (reliability diagram)
- A model benefiting from leakage often shows miscalibration: confident predictions that break down on fresh data

---

## How to Think About MI Specifically

MI measures the reduction in uncertainty about the label given the feature. If you are using a plugin (finite-sample) estimator:

- MI is upward-biased in small samples; the bias is proportional to the number of bins or effective degrees of freedom
- A feature with near-perfect leakage will show MI approaching H(Y) (the entropy of the label), which for a 5% churn rate is roughly 0.29 bits
- If your estimated MI is approaching or exceeding H(Y), that is a strong signal the feature is carrying label information directly

To sanity check: compute MI between the feature and the label on a *randomly shuffled* version of the label. It should drop to near zero. If it does not, your MI estimator has a bug or your sample is too small for reliable estimation.

---

## What to Tell Your Teammate

The right framing is not "this is wrong" but "this result is too good to trust before we rule out leakage." The cost of deploying a leaky model is real: the model will appear to work in backtest, fail in production, and the discrepancy will be hard to diagnose later. The team's credibility depends on catching this now.

Propose a concrete test: set aside a temporal holdout (e.g., the most recent 60 days of labeled data), re-engineer the feature cold on that holdout using only data available at each observation's prediction date, and re-evaluate. If AUC holds up, you have a genuine result. If it drops substantially, you have your answer.

---

## Summary

| Hypothesis | Key test |
|---|---|
| Target leakage | Temporal audit; re-compute feature with strictly pre-T data |
| Train/test contamination | Cold holdout, no test set peeking during feature engineering |
| Serve-time impossibility | Simulate live scoring pipeline |
| MI estimation artifact | Bootstrap CI on MI; shuffle-label null check |
| Near-proxy for label | Distribution overlap by churn class; ablation AUC |

Start with the temporal audit. In most cases, that is where the answer lives.
