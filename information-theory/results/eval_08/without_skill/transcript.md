# Mutual Information for Churn Feature Selection: Solid Approach, But Know the Gotchas

Scoring 180 features by mutual information (MI) with the churn label and keeping the top 25 is a reasonable starting point. MI is non-parametric and can detect nonlinear relationships that correlation-based filters miss. But there are several failure modes worth knowing before you ship this.

---

## What MI does well

- **Catches nonlinear associations.** A feature with a U-shaped relationship to churn will score near zero on a Pearson correlation but meaningfully on MI. This is the primary reason to prefer MI over correlation for feature selection.
- **Works on mixed feature types.** With the right estimator (e.g., `sklearn`'s `mutual_info_classif`), it handles both continuous and categorical features in the same pass.
- **Model-agnostic.** It makes no assumptions about your downstream learner.

---

## The real gotchas

### 1. MI is univariate — it ignores redundancy

The biggest problem with filter-based MI selection is that it scores each feature independently. If you have five highly correlated tenure-related features (account age, days since last login, contract length, months at current plan, time since last upgrade), all five may score high on MI individually. You keep several of them, and they contribute almost no additional information beyond the first one.

The fix is a method like **mRMR (minimum Redundancy Maximum Relevance)** or **CMIM**, which explicitly penalize features that are redundant with already-selected features. Alternatively, run a post-filter step: after selecting top-25 by MI, check pairwise correlations among the selected set and drop near-duplicates.

### 2. High cardinality categoricals are systematically overscored

MI estimated from data increases with the number of unique values in a feature, independent of true signal. A customer ID or a raw timestamp will score high simply because it has many distinct values—it effectively memorizes the training labels. This is a well-known bias in MI estimation from finite samples.

Before running MI selection, audit your feature list:
- Drop or encode high-cardinality categoricals properly.
- Apply shrinkage or discretization before estimating MI for continuous features.
- `sklearn`'s `mutual_info_classif` uses a k-nearest-neighbor estimator for continuous features that is somewhat resistant to this, but high-cardinality discrete features still inflate scores.

### 3. Class imbalance distorts MI estimates

Churn datasets are typically 2–10% churn. MI estimated on an imbalanced label distribution can be unreliable, particularly for features that are weakly predictive of the minority class. A feature that perfectly separates the 5% churners but is noise for the 95% non-churners may score lower than a feature with a modest effect across the majority class.

If your churn rate is low, consider whether your MI estimates are stable. Bootstrapping MI scores across subsamples is a quick sanity check—if ranks shift substantially across subsamples, your top-25 list is fragile.

### 4. MI scores don't tell you about interaction effects

A feature that has near-zero marginal MI with churn can still be critical as an interaction partner. For example, "number of support tickets" may look uninformative marginally, but among customers on a specific contract type, it might be the strongest predictor. Pure marginal MI selection will miss this.

This is not a reason to abandon MI selection, but it is a reason to treat your top-25 list as a starting point rather than a definitive answer. After fitting your model, check whether permutation importance or SHAP values diverge substantially from your MI ranking—if they do, there are interaction-driven features worth recovering.

### 5. MI threshold is arbitrary

Keeping exactly the top 25 is a convenient round number, not a principled cutoff. Two better approaches:

- **Elbow in the MI score curve.** Plot MI scores in rank order. If there is a clear drop-off, cut there. If the curve is smooth and gradual, a hard cutoff at 25 is as good as any.
- **Cross-validated model performance.** Fit your model at top-10, top-15, top-20, top-25, top-30, top-40, and compare AUC/precision-recall on a held-out set. If performance plateaus before 25, you're adding noise.

### 6. MI selection is done pre-split vs. post-split

If you computed MI on your full dataset (including test), you have a mild form of data leakage. The feature selection step should be fit only on the training fold and applied to the test fold. In practice this rarely changes results dramatically, but it inflates optimism in your validation metrics and is methodologically incorrect.

---

## Summary

| Concern | Severity | Fix |
|---|---|---|
| Redundancy among selected features | High | mRMR, or post-filter pairwise correlation check |
| High-cardinality feature bias | High | Audit before scoring; encode properly |
| Class imbalance | Medium | Bootstrap MI estimates; check stability |
| Missed interaction-driven features | Medium | Compare to post-model SHAP rankings |
| Arbitrary cutoff at 25 | Low | Elbow plot or CV model performance sweep |
| Data leakage if scored on full dataset | Low–Medium | Score only on training fold |

The approach is not wrong, but it is best understood as a first-pass filter, not a final answer. The redundancy problem is the one most likely to hurt you in practice—five correlated tenure features in the top 25 crowd out genuinely independent predictors. Running mRMR or a post-hoc redundancy check on your selected set is worth the 30 minutes it takes.
