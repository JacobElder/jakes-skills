# Binned MI on Continuous Variables: What Can Go Wrong

Yes, there are real problems with the approach. The plan will give you a number, but without the fixes below that number is probably inflated, and its magnitude will depend substantially on arbitrary choices you made when you set up the bins.

## Problem 1: Plug-in MI from a contingency table is biased upward

The plug-in estimator of MI from a joint frequency table has a known positive bias:

```
E[Î_plugin] ≈ I + (K_X − 1)(K_Y − 1) / (2N)
```

With 10 bins on each variable, `K_X = K_Y = 10`, so the bias is:

```
(10 − 1)(10 − 1) / (2 × 2000) = 81 / 4000 ≈ 0.020 nats
```

That is a fixed additive floor on top of your true MI — present whether or not there is any real dependence. At N=2000 this is modest but not negligible, and it will loom large if your true MI is small.

The sharper concern is that a permutation null can manufacture even larger apparent MI from the random assignment of points to bins alone, especially near bin boundaries. The bias formula above is only the leading term; finite-sample variance on top of it adds more noise.

**Fix:** Never report a raw plug-in MI. Always compare it to a permutation null: shuffle Y relative to X 500+ times, recompute the same binned MI each time, and report your observed value, the null mean (which approximates the bias floor), and how many sigma above the null you sit. If your value isn't clearly above the null distribution, you do not have a real result.

## Problem 2: Fixed equal-width bins are not the right choice for a nonlinear monotone relationship

Equal-width bins produce cells with very unequal counts when the marginal distributions are skewed or heavy-tailed — which is common for latency measurements. Sparse cells are particularly dangerous because:

- The bias term above is an average; the actual inflation is driven by cells with low expected counts. Cells that are mostly empty but occasionally occupied introduce high-variance, high-bias contributions to the joint entropy.
- The rule of thumb for adequate sampling is N ≫ K_total occupied cells. With a 10×10 table you have up to 100 cells and 2000 points, giving ~20 points per cell *in expectation*. Uneven distributions will leave some cells with 5 or fewer points, pushing you into the undersampled regime for those cells.

**Better option:** Equal-quantile (equal-frequency) bins instead of equal-width. Force each marginal bin to contain the same number of points. This concentrates your samples more evenly across the joint table and reduces the number of near-empty cells.

## Problem 3: The result depends on bin count in a way you cannot calibrate from the data

If you run 8 bins vs. 10 vs. 12, you will get different MI values, and there is no principled way to argue one is correct. The relationship between bin count and MI estimate is non-monotone and problem-specific. Any MI number you report from a fixed binning is not a reproducible quantity — it is "MI under this binning choice."

For a nonlinear monotone relationship this is especially painful, because a coarse binning will miss within-bin structure and a fine binning will run into undersampling. There is no obviously right resolution from inside the binning framework.

## The right approach: KSG (k-NN) estimator

For continuous bivariate data the standard estimator is **KSG (Kraskov–Stögbauer–Grassberger)**, a k-nearest-neighbor method:

- It does **not** bin; it uses local neighbor distances in the joint and marginal spaces.
- It has substantially less bias than histogramming for continuous data.
- It is invariant to monotone transformations of each variable separately — exactly the property you want here given the nonlinear monotone relationship.
- At N=2000 with low dimension, it performs well.

Available implementations:
- `sklearn.feature_selection.mutual_info_regression` — uses a KSG variant; easy entry point.
- `npeet` package — the original Kraskov estimator, more configurable.
- The `scripts/entropy_mi_estimators.py` script in this skill validates KSG against the Gaussian closed form `I = −½ ln(1−ρ²)`.

Practical notes:
- KSG has one hyperparameter `k` (number of neighbors). Try `k = 3, 5, 7` and verify the estimate is stable. If it swings wildly with `k`, report the range, not a single value.
- KSG can return small negative values due to numerical noise; clamp those to zero and treat as "indistinguishable from independent."
- Add a tiny jitter (say, 1e-10 × std) if your data has measurement ties (repeated identical latency values are common). Exact ties cause zero k-NN distances and break the estimator.

## What to report

Whatever estimator you use, a bare MI number is half an answer. Report:

1. The point estimate (with units: bits if log₂, nats if ln).
2. A bootstrap 95% CI (resample rows with replacement, recompute 500–1000 times).
3. The permutation null: mean and distribution of MI under shuffle, so the reader can see how far above chance your estimate sits.
4. Optionally a normalized variant if you want a 0–1 effect size: `NMI = I / √(H(X)H(Y))` or the information coefficient `√(1 − e^{−2I})`, which equals `|ρ|` for Gaussians and gives an interpretable magnitude.

## Summary

| Issue | Consequence | Fix |
|---|---|---|
| Plug-in MI biased up by ~0.02 nats | Overstates dependence | Permutation null; bias-correct (Miller–Madow at minimum) |
| Equal-width bins with heavy-tailed latency | Sparse cells, high-variance estimate | Equal-quantile bins, or drop binning entirely |
| Bin count is arbitrary | Result not reproducible across `K` choices | Use KSG k-NN instead of fixed binning |
| Point estimate only | Invites overinterpretation | Bootstrap CI + permutation null |

The approach will not give you a wrong *sign* — the relationship is clearly there with 2000 points and a strong monotone signal. The problems are that the magnitude will be inflated, depends on the binning you chose, and cannot be compared to a MI reported by someone using a different bin count. KSG plus a permutation null is the standard fix and is not much harder to run than constructing a contingency table.
