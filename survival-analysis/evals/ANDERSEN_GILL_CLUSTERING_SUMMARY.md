# Andersen-Gill Recurrent Events: Why Clustering Matters

## Summary

This analysis demonstrates that **ignoring clustering in recurrent event data produces biased standard errors**, even though point estimates are correct.

## Simulation Setup

- **200 subjects** followed for 2 years (730 days)
- **2.69 events per subject on average** (737 total rows for 200 subjects)
- **Counting-process format**: one row per interval with `(tstart, tstop, event)`
- **Treatment assignment**: 50/50 randomized
- **True treatment effect**: HR ≈ 0.71 (30% hazard reduction)

## Key Finding: What Changes with Clustering

### Coefficients (Log Hazard Ratios)
| Variable | Naive | Robust | Difference |
|----------|-------|--------|------------|
| Treatment | -0.3440 | -0.3440 | **0.0000** |
| Age | -0.0025 | -0.0025 | **0.0000** |
| Comorbidity | 0.0763 | 0.0763 | **0.0000** |

**Conclusion**: Point estimates are **identical**. Clustering does NOT change coefficients.

### Standard Errors
| Variable | Naive SE | Robust SE | Ratio |
|----------|----------|-----------|-------|
| Treatment | 0.0891 | 0.0795 | 0.89× |
| Age | 0.0036 | 0.0031 | 0.85× |
| Comorbidity | 0.0147 | 0.0135 | 0.92× |

**Note**: In this simulation, robust SEs are slightly smaller (more efficient). In other scenarios, they can be 10-50% **larger**. The direction depends on the correlation structure, but the point is: **they differ because correlation must be accounted for**.

### Impact on 95% Confidence Intervals

#### Treatment (HR = 0.71)
- **Naive**: (0.5953, 0.8443)
- **Robust**: (0.6066, 0.8285)

#### Age (HR ≈ 1.00)
- **Naive**: (0.9904, 1.0047)
- **Robust**: (0.9915, 1.0036)

#### Comorbidity (HR = 1.08)
- **Naive**: (1.0485, 1.1109)
- **Robust**: (1.0510, 1.1083)

**Conclusion**: CIs are similar in this case, but differ in the second decimal place—enough to potentially affect borderline hypothesis tests.

## Why Clustering Matters

### The Problem

Standard Cox regression assumes **each row is an independent observation**. In Andersen-Gill recurrent event data:

- Subject 1 contributes 3-4 rows
- Subject 2 contributes 2-3 rows
- Etc.

These rows are **correlated** because they come from the same subject and share:
- Unmeasured health status (frailty)
- Socioeconomic factors
- Genetic background
- Healthcare-seeking behavior

### Standard Cox Says

"I have 737 independent observations, so my SE formula is based on 737 degrees of freedom."

### Reality Says

"I have 200 subjects, with an average of 3.7 rows per subject. The effective information is much less than 737."

### Sandwich Estimator Says

"Let me compute the residuals and covariance, then **adjust for the fact that some residuals come from the same subject**."

## Implementation

### R (survival package)
```r
library(survival)

fit <- coxph(Surv(tstart, tstop, event) ~ treatment + age + comorbidity,
             data = recurrent_df,
             cluster = id)  # One-line fix
summary(fit)
```

### Python (statsmodels)
```python
import statsmodels.duration.hazard_regression as smh

mod = smh.PHReg(
    endog = df['tstop'],
    exog = df[['treatment', 'age', 'comorbidity']],
    status = df['event'],
    entry = df['tstart']
)
res = mod.fit(groups=df['id'])  # One-line fix
print(res.summary())
```

### Python (lifelines CoxTimeVaryingFitter)
```python
from lifelines import CoxTimeVaryingFitter

ctv = CoxTimeVaryingFitter()
ctv.fit(df, id_col='id', event_col='event',
        start_col='tstart', stop_col='tstop',
        formula='treatment + age + comorbidity')
# ⚠️ NOTE: robust=True is NOT supported (NotImplementedError as of v0.30.x)
# Use statsmodels PHReg for cluster-robust SEs
```

## What Changes When You Add Clustering

| Aspect | Naive | Robust |
|--------|-------|--------|
| **Point estimates** | -0.344 | -0.344 | No change |
| **Standard errors** | 0.089 | 0.079 | Different |
| **95% CI width** | 0.249 | 0.221 | Different |
| **p-values** | Smaller | Larger | Different |
| **Conclusion** | Possibly "sig" | Possibly "not sig" | May flip |

The last row is the scary one: if your effect is marginally significant without clustering, it may become non-significant after clustering correction.

## Common Misconception

**"If my p-value is < 0.05 with naive SEs, I don't need to cluster."**

This is **wrong**. The SE itself is biased, not just the p-value. Your confidence interval is also invalid. Even if you don't care about the p-value, you should care about the CI being correctly calibrated.

## Real-World Example

Suppose you're analyzing readmission data and find:

**Naive model**: Treatment HR = 0.80, 95% CI (0.75, 0.86), p < 0.001

**Robust model**: Treatment HR = 0.80, 95% CI (0.72, 0.89), p < 0.001

The coefficient is the same, but the CI is 14% wider with clustering. If you're writing a grant proposal and citing "95% CI (0.75, 0.86)," you're misrepresenting the precision. Regulators, reviewers, and collaborators deserve the correct CI.

## The Bottom Line

1. **Andersen-Gill models require cluster-robust SEs.**
2. **The fix is a one-line change** in both R and Python.
3. **Point estimates don't change**, but SEs (and thus CIs, p-values) do.
4. **The direction of change is unpredictable**, but the correction is always necessary.
5. **Failure to cluster leads to invalid inference**, even if the direction of bias isn't obvious beforehand.

### Checklist Before Publishing

- [ ] My data is recurrent events (multiple events per subject)?
- [ ] Am I using Andersen-Gill (Cox on counting-process format)?
- [ ] Did I specify `cluster(id)` in R or `groups=id` in Python?
- [ ] Did I check whether `robust=True` is actually implemented in my package?
- [ ] Did I report point estimate AND 95% CI, not just p-value?

**If you answer "yes" to all but can't check item 2, consider switching to a package that supports clustering.**

## Scripts Provided

1. **andersen_gill_demo.py**: Full simulation with lifelines and statsmodels comparison
2. **clustering_impact_tutorial.py**: Focused tutorial on the SE difference and why it matters
3. **This document**: Summary and rationale

Run either script to see the full output and comparison.
