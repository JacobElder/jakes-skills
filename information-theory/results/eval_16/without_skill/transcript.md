# Binning-Based MI Estimation for Continuous Variables

Yes, there are several problems with this approach worth understanding before you commit to it.

## The Core Issue: Binning Introduces Arbitrary Discretization Bias

When you bin two continuous variables and compute MI from the contingency table, you're estimating:

$$\hat{I}(X; Y) = \sum_{i,j} \hat{p}_{ij} \log \frac{\hat{p}_{ij}}{\hat{p}_i \hat{p}_j}$$

This estimate depends heavily on your binning choices in ways that are not transparent.

### Problem 1: Bin Count Is Arbitrary and Consequential

With 10 bins × 10 bins = 100 cells and 2000 points, you average 20 points per cell — that sounds reasonable, but it hides the problem. MI estimation from contingency tables has a positive bias even under independence, and the bias grows with the number of cells relative to sample size. The classic result (Miller 1955) gives the bias as approximately:

$$\text{Bias} \approx \frac{(r-1)(c-1)}{2N}$$

For a 10×10 table with N=2000, that's 81/4000 ≈ 0.02 nats — modest but nonzero. More importantly, the *variance* of your estimate is substantial, and changing from 10 to 8 or 12 bins can shift your point estimate by 10–20% without a principled reason to prefer one.

### Problem 2: Uniform Bins Distort Your Specific Data

Uniform-width bins are the default but are poorly suited to most real data. If latency is right-skewed (common), most of your 2000 points will cluster in a few low-latency bins while the high-latency bins are sparse. Sparse cells inflate variance and cause the plug-in estimator to underestimate MI (empty cells contribute nothing when they should contribute information). Uniform bins on satisfaction scores have the same problem if people cluster near the endpoints or middle.

### Problem 3: You Already Know the Relationship Is Monotone

If you already know the relationship is "clearly nonlinear monotone," MI is probably not the quantity you need. For a strictly monotone relationship, Spearman's ρ or Kendall's τ fully characterize the dependence — they capture any monotone association, not just linear. MI is most valuable when you suspect non-monotone structure (e.g., an inverted-U) or need an information-theoretic quantity specifically. If your goal is just to quantify "how strongly are these related," a rank correlation is more interpretable, assumption-free, and doesn't require any binning choice.

## Better Options If You Do Want MI

### Option A: KSG Estimator (Recommended)

The Kraskov-Stögbauer-Grassberger (KSG) estimator computes MI directly from the continuous data using k-nearest-neighbor distances. No binning required.

```python
from sklearn.feature_selection import mutual_info_regression
import numpy as np

# X: latency (n,1), y: satisfaction (n,)
mi = mutual_info_regression(X.reshape(-1, 1), y, n_neighbors=5, random_state=0)
```

Or with the `npeet` library for more control:
```python
from NPEET import entropy_estimators as ee
mi = ee.mi(latency.reshape(-1,1), satisfaction.reshape(-1,1), k=5)
```

With N=2000, KSG with k=5–10 neighbors is stable and well-validated. It handles nonlinear monotone relationships natively without any discretization.

### Option B: Equal-Frequency (Quantile) Bins

If you insist on the contingency table approach, use quantile-based bins rather than equal-width bins. This ensures roughly equal counts in each cell:

```python
import pandas as pd
from sklearn.metrics import mutual_info_score

lat_binned = pd.qcut(latency, q=10, labels=False, duplicates='drop')
sat_binned = pd.qcut(satisfaction, q=10, labels=False, duplicates='drop')
mi = mutual_info_score(lat_binned, sat_binned)
```

This eliminates the sparse-cell problem from skewed marginals. You should still apply a bias correction and report MI under several bin counts (8, 10, 12, 15) to verify your estimate is stable.

### Option C: Vary the Bin Count and Report Sensitivity

If you use binning, never report a single number. Compute MI for k ∈ {5, 8, 10, 12, 15, 20} bins and plot MI vs. k. A stable plateau indicates the estimate is robust. If MI increases monotonically with k, you have a bias problem from sparse cells.

## Summary Recommendation

For your situation — 2000 paired continuous observations, clearly monotone nonlinear relationship — the recommendation is:

1. **If you want a dependence measure**: Use Spearman's ρ. It's exact, distribution-free, captures any monotone association, and requires no tuning parameters.
2. **If you specifically need MI**: Use the KSG estimator via `sklearn.feature_selection.mutual_info_regression` or `npeet`. Do not bin.
3. **If you must use binning**: Use quantile bins, apply bias correction, and run sensitivity analysis across bin counts.

The 10-uniform-bin approach will give you *a* number, but there's no guarantee it's accurate, and you have no diagnostic to know whether it is.
