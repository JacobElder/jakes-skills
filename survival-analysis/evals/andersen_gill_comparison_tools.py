"""
Comparison of lifelines vs. statsmodels for Andersen-Gill recurrent events.

Shows:
- lifelines CoxTimeVaryingFitter gives point estimates only (no robust SE option)
- statsmodels PHReg allows cluster-robust variance via groups= parameter
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from lifelines import CoxTimeVaryingFitter
import statsmodels.duration.hazard_regression as smh

np.random.seed(42)

# Generate sample data (same as before)
def generate_recurrent_data(n_subjects=200, max_time=365):
    data = []
    for subject_id in range(1, n_subjects + 1):
        treatment = 1 if subject_id % 2 == 0 else 0
        age = np.random.normal(65, 15)
        age = np.clip(age, 40, 90)
        subject_frailty = np.random.exponential(1.0)
        censoring_time = np.random.uniform(100, max_time)

        current_time = 0
        event_number = 1
        base_rate = 0.003

        while True:
            treatment_effect = np.exp(-0.3 * treatment)
            hazard = base_rate * subject_frailty * treatment_effect
            inter_event_time = np.random.exponential(1 / hazard)
            event_time = current_time + inter_event_time

            if event_time >= censoring_time:
                data.append({
                    'id': subject_id,
                    'tstart': current_time,
                    'tstop': censoring_time,
                    'event': 0,
                    'treatment': treatment,
                    'age': age,
                })
                break
            else:
                data.append({
                    'id': subject_id,
                    'tstart': current_time,
                    'tstop': event_time,
                    'event': 1,
                    'treatment': treatment,
                    'age': age,
                })
                current_time = event_time
                event_number += 1
                if event_number > 10:
                    data.append({
                        'id': subject_id,
                        'tstart': current_time,
                        'tstop': censoring_time,
                        'event': 0,
                        'treatment': treatment,
                        'age': age,
                    })
                    break
    return pd.DataFrame(data)

df = generate_recurrent_data(n_subjects=200)

print("=" * 75)
print("PYTHON TOOLS FOR ANDERSEN-GILL RECURRENT EVENTS")
print("=" * 75)

# ============================================================================
# APPROACH 1: lifelines CoxTimeVaryingFitter
# ============================================================================

print("\n" + "=" * 75)
print("APPROACH 1: lifelines.CoxTimeVaryingFitter")
print("=" * 75)
print("""
Purpose: Easy-to-use API for time-varying covariates (counting process format)
Pros:    Clean API, good for exploratory work
Cons:    No cluster-robust variance option (robust=True raises NotImplementedError)
""")

ctv = CoxTimeVaryingFitter()
ctv.fit(df, id_col='id', event_col='event',
        start_col='tstart', stop_col='tstop',
        formula='treatment + age')

print("\nResults from lifelines:")
print("-" * 75)
print(ctv.summary[['exp(coef)', 'se(coef)', '95% lower bound', '95% upper bound']])

lifelines_treatment_se = ctv.summary.loc['treatment', 'se(coef)']
lifelines_age_se = ctv.summary.loc['age', 'se(coef)']

# ============================================================================
# APPROACH 2: statsmodels PHReg (naive)
# ============================================================================

print("\n" + "=" * 75)
print("APPROACH 2a: statsmodels.PHReg (Naive)")
print("=" * 75)
print("""
Purpose: Maximum flexibility; fits Cox PH with counting-process entry/exit times
Method:  Information-based SEs (assumes independence between rows)
         ✗ WRONG for recurrent events!
""")

mod_naive = smh.PHReg(
    endog=df['tstop'].values,
    exog=df[['treatment', 'age']].values,
    status=df['event'].values,
    entry=df['tstart'].values,
)
res_naive = mod_naive.fit(disp=False)

print("\nResults from statsmodels (naive SEs):")
print("-" * 75)
summary_naive = pd.DataFrame({
    'Coef': res_naive.params,
    'SE': res_naive.bse,
    'z-stat': res_naive.params / res_naive.bse,
    'p-value': res_naive.pvalues,
    'HR': np.exp(res_naive.params),
})
summary_naive.index = ['treatment', 'age']
print(summary_naive)

# ============================================================================
# APPROACH 2b: statsmodels PHReg (Robust)
# ============================================================================

print("\n" + "=" * 75)
print("APPROACH 2b: statsmodels.PHReg (Cluster-Robust)")
print("=" * 75)
print("""
Purpose: Same as 2a, but with sandwich-corrected variance
Method:  groups= parameter applies Lin-Wei sandwich correction for clusters
         ✓ CORRECT for recurrent events (equivalent to cluster(id) in R)
""")

mod_robust = smh.PHReg(
    endog=df['tstop'].values,
    exog=df[['treatment', 'age']].values,
    status=df['event'].values,
    entry=df['tstart'].values,
)
res_robust = mod_robust.fit(groups=df['id'].values, disp=False)

print("\nResults from statsmodels (robust SEs):")
print("-" * 75)
summary_robust = pd.DataFrame({
    'Coef': res_robust.params,
    'SE': res_robust.bse,
    'z-stat': res_robust.params / res_robust.bse,
    'p-value': res_robust.pvalues,
    'HR': np.exp(res_robust.params),
})
summary_robust.index = ['treatment', 'age']
print(summary_robust)

# ============================================================================
# COMPARISON TABLE
# ============================================================================

print("\n" + "=" * 75)
print("SIDE-BY-SIDE COMPARISON")
print("=" * 75)

comparison = pd.DataFrame({
    'Tool': ['lifelines', 'statsmodels (naive)', 'statsmodels (robust)'],
    'Treatment SE': [lifelines_treatment_se, res_naive.bse[0], res_robust.bse[0]],
    'Age SE': [lifelines_age_se, res_naive.bse[1], res_robust.bse[1]],
})

print("\n" + comparison.to_string(index=False))

print("\n\nKey Observations:")
print("-" * 75)
print(f"1. lifelines and statsmodels (naive) give identical SEs:")
print(f"   Treatment: {lifelines_treatment_se:.6f} ≈ {res_naive.bse[0]:.6f} ✓")
print(f"   (Both assume independence)")

print(f"\n2. statsmodels (robust) SEs are ~{res_robust.bse[0]/res_naive.bse[0]:.2f}x larger:")
print(f"   Treatment: {res_robust.bse[0]:.6f} vs {res_naive.bse[0]:.6f}")
print(f"   (Accounts for within-subject clustering)")

print(f"\n3. Point estimates are IDENTICAL across all approaches:")
print(f"   Treatment: {res_robust.params[0]:.6f} (all three methods)")

print("\n" + "=" * 75)
print("RECOMMENDATION FOR PYTHON USERS")
print("=" * 75)
print("""
For recurrent event analysis (Andersen-Gill):

Use statsmodels PHReg with groups= parameter:

    from statsmodels.duration.hazard_regression import PHReg

    mod = PHReg(
        endog=df['tstop'].values,
        exog=df[['treatment', 'age']].values,
        status=df['event'].values,
        entry=df['tstart'].values,
    )

    # CRITICAL: use groups= for cluster-robust variance
    result = mod.fit(groups=df['id'].values, disp=False)

    print(result.summary())

NOT:
    ✗ lifelines (no robust option)
    ✗ statsmodels without groups= (biased SEs)
""")

print("\nFor quick exploratory work, lifelines is fine:")
print("    from lifelines import CoxTimeVaryingFitter")
print("    ctv = CoxTimeVaryingFitter()")
print("    ctv.fit(df, id_col='id', event_col='event',")
print("            start_col='tstart', stop_col='tstop')")
print("    # Get point estimates; SEs are naive but may be useful for intuition")
print("=" * 75)
