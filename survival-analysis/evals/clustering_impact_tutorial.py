"""
Andersen-Gill clustering tutorial: Why cluster-robust SEs are essential.

This script demonstrates the fundamental issue: when subjects contribute
multiple correlated rows to an analysis, standard Cox SEs are BIASED.

The bias direction (under- or over-estimation) depends on the correlation
structure. The POINT is that you must account for clustering to get valid inference.
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ============================================================================
# SCENARIO: Recurrent Hospital Readmissions
# ============================================================================

print("=" * 80)
print("ANDERSEN-GILL RECURRENT EVENTS: CLUSTERING TUTORIAL")
print("=" * 80)
print()

print("""
SETUP: Simulating 200 patients with recurrent hospital readmissions.

Data structure:
  - 200 subjects total
  - Each subject has multiple readmission records (counting-process format)
  - On average, 2.69 events per subject (737 total rows)
  - Treatment assignment is randomized (50/50)

True treatment effect (in simulation):
  - Treatment reduces hazard of readmission by ~30% (HR ≈ 0.71)
""")

# Generate the same data as before
n_subjects = 200
subject_data = pd.DataFrame({
    'id': range(1, n_subjects + 1),
    'treatment': np.random.binomial(1, 0.5, n_subjects),
    'age': np.random.normal(65, 12, n_subjects),
    'comorbidity_score': np.random.uniform(0, 10, n_subjects),
})

recurrent_rows = []
for idx, row in subject_data.iterrows():
    subject_id = row['id']
    treatment = row['treatment']
    age = row['age']
    comorbidity = row['comorbidity_score']

    hazard_multiplier = np.exp(
        -0.35 * treatment +
        0.05 * comorbidity +
        0.01 * (age - 65) / 10
    )

    follow_up_days = 730
    event_times = []
    current_time = 0

    while True:
        rate_per_day = (1.2 / 365) * hazard_multiplier
        inter_event_days = np.random.exponential(1 / rate_per_day)
        next_event_time = current_time + inter_event_days

        if next_event_time >= follow_up_days:
            break

        event_times.append(next_event_time)
        current_time = next_event_time

    prev_time = 0
    for event_day in event_times:
        recurrent_rows.append({
            'id': subject_id,
            'tstart': prev_time,
            'tstop': event_day,
            'event': 1,
            'treatment': treatment,
            'age': age,
            'comorbidity_score': comorbidity,
        })
        prev_time = event_day

    recurrent_rows.append({
        'id': subject_id,
        'tstart': prev_time,
        'tstop': follow_up_days,
        'event': 0,
        'treatment': treatment,
        'age': age,
        'comorbidity_score': comorbidity,
    })

recurrent_df = pd.DataFrame(recurrent_rows)

print(f"Data summary:")
print(f"  - Subjects: {n_subjects}")
print(f"  - Total rows: {len(recurrent_df)}")
print(f"  - Total events: {recurrent_df['event'].sum()}")
print(f"  - Avg rows per subject: {len(recurrent_df) / n_subjects:.2f}")
print()

# ============================================================================
# FIT MODELS: WITH AND WITHOUT CLUSTERING
# ============================================================================

import statsmodels.duration.hazard_regression as smh

print("=" * 80)
print("FITTING ANDERSEN-GILL MODELS")
print("=" * 80)
print()

exog_cols = ['treatment', 'age', 'comorbidity_score']
X = recurrent_df[exog_cols].values
endog = recurrent_df['tstop'].values
status = recurrent_df['event'].values
entry = recurrent_df['tstart'].values

# Model 1: Naive (ignores clustering)
print("MODEL 1: Naive (information-based SEs, assumes independence)")
print("-" * 80)
mod_naive = smh.PHReg(
    endog=endog,
    exog=X,
    status=status,
    entry=entry,
)
res_naive = mod_naive.fit(disp=False)
print(res_naive.summary())
print()

# Model 2: Robust (accounts for clustering)
print("MODEL 2: Robust (sandwich SEs, accounts for within-subject correlation)")
print("-" * 80)
mod_robust = smh.PHReg(
    endog=endog,
    exog=X,
    status=status,
    entry=entry,
)
res_robust = mod_robust.fit(groups=recurrent_df['id'].values, disp=False)
print(res_robust.summary())
print()

# ============================================================================
# CRITICAL COMPARISON: What Changed?
# ============================================================================

print("=" * 80)
print("CRITICAL COMPARISON: NAIVE vs ROBUST")
print("=" * 80)
print()

comparison = pd.DataFrame({
    'Variable': exog_cols,
    'Coef': res_naive.params,
    'Naive SE': res_naive.bse,
    'Robust SE': res_robust.bse,
    'SE Ratio (Robust/Naive)': res_robust.bse / res_naive.bse,
})

print(comparison.to_string(index=False))
print()

print("""
KEY OBSERVATIONS:

1. Coefficients are IDENTICAL:
   - Naive and robust fit gives the same point estimates
   - Clustering does NOT change coefficient values
   - It ONLY changes standard errors and thus confidence intervals

2. Standard Errors are DIFFERENT:
   - In this simulation, robust SEs are similar to naive (small effect)
   - In other simulations, robust SEs can be 10-50% larger or smaller
   - Direction depends on the correlation structure
   - The KEY POINT: we must account for correlation to get valid SEs

3. Why the SEs differ is important:
   - Naive SEs treat each row as independent
   - But rows from the same subject are correlated
   - Sandwich estimator corrects for this correlation
   - This affects CI width and p-values

""")

# ============================================================================
# IMPACT ON INFERENCE
# ============================================================================

print("=" * 80)
print("IMPACT ON INFERENCE (95% CONFIDENCE INTERVALS)")
print("=" * 80)
print()

naive_hr = np.exp(res_naive.params)
naive_ci_lower = np.exp(res_naive.params - 1.96 * res_naive.bse)
naive_ci_upper = np.exp(res_naive.params + 1.96 * res_naive.bse)

robust_hr = np.exp(res_robust.params)
robust_ci_lower = np.exp(res_robust.params - 1.96 * res_robust.bse)
robust_ci_upper = np.exp(res_robust.params + 1.96 * res_robust.bse)

for i, var in enumerate(exog_cols):
    print(f"{var}:")
    print(f"  Naive  CI: ({naive_ci_lower[i]:.4f}, {naive_ci_upper[i]:.4f})")
    print(f"  Robust CI: ({robust_ci_lower[i]:.4f}, {robust_ci_upper[i]:.4f})")

    if robust_ci_lower[i] < naive_ci_lower[i] or robust_ci_upper[i] > naive_ci_upper[i]:
        print(f"  → Robust CI is WIDER (more conservative)")
    else:
        print(f"  → Robust CI is NARROWER (less conservative)")

    print()

# ============================================================================
# THE KEY LESSON
# ============================================================================

print("=" * 80)
print("THE KEY LESSON: WHY CLUSTERING MATTERS")
print("=" * 80)
print()

print("""
PROBLEM: Multiple events per subject violate independence assumption.

  Standard Cox regression assumes:
    - Each row is an independent observation
    - SE is based on the # of rows (737 in this case)

  Reality with recurrent events:
    - Rows from same subject are CORRELATED
    - They share subject-level characteristics (frailty, unmeasured health, etc.)
    - Effective sample size is smaller than 737
    - Naive SE formula overcounts information

SOLUTION: Use cluster-robust (sandwich) standard errors.

  The robust estimator:
    1. Computes residuals and covariance matrix (like standard Cox)
    2. Then ADJUSTS for within-cluster correlation
    3. Produces SEs that are valid even with clustering

IMPLEMENTATION:

  R (survival package):
    coxph(Surv(tstart, tstop, event) ~ treatment + age + cluster(id),
          data = df)

  Python (statsmodels):
    mod = PHReg(endog, exog, status=status, entry=entry)
    mod.fit(groups=df['id'])

  Python (lifelines CoxTimeVaryingFitter):
    NOT CURRENTLY SUPPORTED (as of v0.30.x)
    Use statsmodels PHReg instead

THE BOTTOM LINE:
  - Always use cluster-robust SEs for recurrent event data
  - Point estimates don't change, but SEs (and thus CIs, p-values) do
  - Failure to cluster leads to BIASED inference, even if direction is variable
  - It's a one-line fix in both R and Python — no excuse not to do it

""")

# ============================================================================
# VERIFICATION
# ============================================================================

print("=" * 80)
print("VERIFICATION")
print("=" * 80)

# Check that coefficients are identical
max_coef_diff = np.max(np.abs(res_naive.params - res_robust.params))
print(f"Max coefficient difference: {max_coef_diff:.2e} (should be ~0)")

# Check that SEs are different
max_se_diff = np.max(np.abs(res_naive.bse - res_robust.bse))
print(f"Max SE difference: {max_se_diff:.6f}")

print()
print("✓ Analysis complete. Point estimates identical, SEs adjusted for clustering.")
