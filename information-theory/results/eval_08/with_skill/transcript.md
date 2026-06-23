# MI-Based Feature Selection for Churn: Solid Foundation, Three Real Gotchas

The approach is directionally right — MI is model-agnostic, catches nonlinear relationships that correlation misses, and is invariant to monotone rescaling of each feature. For a churn label those properties matter: features like "days since last login" or "billing amount" often have nonlinear thresholds, not linear slopes.

But there are three failure modes that routinely wreck MI-based feature ranking in practice, and at least two of them are almost certainly present in your setup.

---

## Gotcha 1: Your MI estimates are biased upward, and the bias is worst on the features most likely to overfit

Plug-in mutual information — computed from an empirical contingency table or histogram — is systematically biased:

```
E[Î_plugin] ≈ I_true + (K_X − 1)(K_Y − 1) / (2N)
```

The bias is **upward** (it invents spurious dependence), and it scales with the number of categories `K_X` and `K_Y`. High-cardinality features — customer IDs, fine-grained categorical codes, continuous features with many bins — get the largest inflation. This means naive MI ranking is biased toward exactly the features most prone to overfit downstream. The same mechanism is why decision-tree information gain over-selects many-valued splits; `gain ratio` corrections exist for precisely this reason.

**What to do:**

1. **Run a permutation null for every MI estimate.** Shuffle the churn label relative to each feature 200+ times, recompute MI each time, and compare your observed value to that shuffled distribution. The shuffle mean is your bias floor — a feature whose MI doesn't clearly exceed its shuffled null is noise, regardless of how large the raw number looks. This single habit prevents most false MI claims.

2. **For continuous features, use KSG (k-NN), not bins.** `sklearn.feature_selection.mutual_info_classif` already uses a KSG variant — if you're using that, you're in better shape than raw histogram MI. If you're binning, stop. Bin-count choices can flip the ranking, and the bias is severe in high dimensions.

3. **For discrete/categorical features, apply Miller–Madow correction** at minimum: `Ĥ_MM = Ĥ_plugin + (K̂ − 1) / (2N)` per entropy term. Correct the marginals *and* the joint — correcting only the marginals reintroduces bias.

The honest standard: report each MI as an estimate with a bootstrap interval and a permutation p-value, not a bare ranking number.

---

## Gotcha 2: High MI does not mean non-redundant — you're probably double-counting correlated features

Ranking 180 features by `I(X_j; churn)` and taking the top 25 selects for *relevance*, not for *unique information*. If your top 25 include "total charges this month," "average monthly charges," and "total charges lifetime," you may have selected three numbers that, conditioned on one another, carry very little additional information about churn.

Formally: the information in a set of features is *not* the sum of their individual MIs. Redundant features inflate the count without improving prediction.

```
I(X₁, X₂; Y) ≤ I(X₁; Y) + I(X₂; Y)
```

with equality only when X₁ and X₂ are conditionally independent given Y.

**The fix:** Replace marginal MI ranking with a criterion that accounts for redundancy:

- **mRMR (max Relevance − min Redundancy):** selects features that maximize `I(X_j; Y)` while minimizing mean pairwise MI with already-selected features. It's a greedy approximation but fast and well-validated.
- **JMI (Joint Mutual Information) or CMIM (Conditional MI Minimization):** score each candidate feature by `I(X_j; Y | already-selected set)`, adding the feature that contributes the most conditional information. More principled than mRMR but slightly heavier.

Plain top-k-by-MI is documented in the literature as a known failure mode for this reason. If your downstream model is regularized (e.g., L1 logistic regression, gradient boosting with feature subsampling), it partially handles redundancy on its own — but you've already thrown away 155 features before the model ever sees them.

---

## Gotcha 3: MI magnitude is not comparable across variable types without normalization

If your 180 features are a mix of continuous, low-cardinality discrete, and high-cardinality categorical, their raw MI values are not on the same scale. MI is bounded by `min(H(X), H(Y))` for discrete variables, but has no fixed upper bound for continuous ones (and is formally infinite for any deterministic invertible relationship). A continuous feature with high entropy can produce a large MI simply because of its marginal distribution, not because it's more informative about churn.

**What to do:** When comparing MI across variable types, use a normalized variant:

- `NMI = I(X; Y) / √(H(X) · H(Y))` — symmetric, bounded [0, 1] for discrete
- `I / min(H(X), H(Y))` — the fraction of X's entropy explained by Y
- The **information coefficient** `√(1 − exp(−2I))` — equals |ρ| for Gaussians, bounded [0, 1], and directly interpretable as an effect-size analog

Pick one normalization, apply it consistently, and report which one you used.

---

## What a hardened version of this approach looks like

```
1. Estimate MI correctly:
   - Continuous features: sklearn mutual_info_classif (KSG-based) or npeet
   - Discrete/mixed features: Miller-Madow corrected, or Ross/Gao mixed estimator
   
2. Run permutation null (200+ shuffles) for each feature:
   - Report observed MI, shuffle mean, p-value
   - Drop features not clearly above null

3. Normalize MI for cross-type comparison (NMI or information coefficient)

4. Select with redundancy penalty (mRMR or JMI greedy search),
   not pure marginal ranking

5. Report bootstrap CIs on the final MI estimates,
   not bare ranking values
```

---

## Bottom line

The approach is sound in intent — MI is the right tool, and filtering 180 → 25 before modeling is a sensible dimensionality step. But as implemented (raw marginal MI ranking), you're probably surfacing a mix of genuinely predictive features, estimation artifacts from high-cardinality features, and correlated clusters that look like independent signal. The permutation null (Gotcha 1) and redundancy criterion (Gotcha 2) are the two changes with the highest return. If you're already using `sklearn.mutual_info_classif`, you've handled the continuous-feature estimation problem; the redundancy issue is then the dominant remaining risk.
