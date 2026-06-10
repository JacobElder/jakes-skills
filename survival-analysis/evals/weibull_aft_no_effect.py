"""
Simulate 1000 subjects from Weibull AFT model with shape=1.5 and no treatment effect.
Show that Cox proportional hazards test does not detect a (non-existent) treatment effect.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from lifelines import CoxPHFitter, WeibullAFTFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test

np.random.seed(42)

# ============================================================================
# 1. Simulate Weibull AFT data with NO treatment effect
# ============================================================================

n_subjects = 1000
shape = 1.5  # Weibull shape parameter

# Binary treatment: 0 or 1 (50/50 split)
treatment = np.random.binomial(n=1, p=0.5, size=n_subjects)

# Scale parameter: SAME for both arms (no treatment effect)
scale = 2.0  # Both treatment and control have scale=2

# Generate event times from Weibull distribution
# Weibull survival: S(t) = exp(-(t/scale)^shape)
# To sample: T = scale * (-log(U))^(1/shape) where U ~ Uniform(0,1)
U = np.random.uniform(0, 1, n_subjects)
event_times = scale * np.power(-np.log(U), 1/shape)

# Add administrative censoring at tau=3 (roughly 20-30% censoring)
tau = 3.0
observed_times = np.minimum(event_times, tau)
event_indicator = (event_times <= tau).astype(int)

# Create DataFrame
df = pd.DataFrame({
    'time': observed_times,
    'event': event_indicator,
    'treatment': treatment
})

print("=" * 70)
print("WEIBULL AFT SIMULATION: NO TREATMENT EFFECT")
print("=" * 70)
print(f"Sample size: {n_subjects}")
print(f"Shape parameter: {shape}")
print(f"Scale parameter: {scale} (same for both arms)")
print(f"Censoring time: {tau}")
print(f"Event rate: {df['event'].mean():.1%}")
print(f"Treatment split: {(df['treatment']==0).sum()} control, {(df['treatment']==1).sum()} treated")
print()

# ============================================================================
# 2. Fit Cox PH model
# ============================================================================

cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event')

print("RESULTS: Cox Proportional Hazards Model")
print("-" * 70)
print(cph.summary)
print()

# Extract p-value for treatment effect
treatment_pval = cph.summary.loc['treatment', 'p']
treatment_hr = np.exp(cph.summary.loc['treatment', 'coef'])

print(f"Treatment coefficient: {cph.summary.loc['treatment', 'coef']:.4f}")
print(f"Hazard Ratio (HR): {treatment_hr:.4f}")
print(f"95% CI: [{np.exp(cph.summary.loc['treatment', 'coef lower 95%']):.4f}, "
      f"{np.exp(cph.summary.loc['treatment', 'coef upper 95%']):.4f}]")
print(f"p-value: {treatment_pval:.4f}")
print()

if treatment_pval > 0.05:
    print("✓ CORRECT: Cox test does NOT detect a treatment effect (p > 0.05)")
    print("  This is the expected result since treatment has no effect.")
else:
    print("✗ WARNING: Cox test detects a treatment effect (p < 0.05)")
    print("  This is a Type I error (false positive).")
print()

# ============================================================================
# 2b. Check Proportional Hazards Assumption
# ============================================================================

print("Proportional Hazards Assumption Check (Schoenfeld Residuals)")
print("-" * 70)
cph.check_assumptions(df, p_value_threshold=0.05, show_plots=False)
print()

# ============================================================================
# 2c. Fit Weibull AFT model (the true data-generating model)
# ============================================================================

print("RESULTS: Weibull AFT Model (True Underlying Model)")
print("-" * 70)

aft = WeibullAFTFitter()
aft.fit(df, duration_col='time', event_col='event')
print(aft.summary)
print()

aft_pval = aft.summary.loc[('lambda_', 'treatment'), 'p']
aft_coef = aft.summary.loc[('lambda_', 'treatment'), 'coef']
aft_exp_coef = aft.summary.loc[('lambda_', 'treatment'), 'exp(coef)']

print(f"Weibull AFT Treatment coefficient: {aft_coef:.4f}")
print(f"Weibull AFT Treatment exp(coef): {aft_exp_coef:.4f}")
print(f"Weibull AFT p-value: {aft_pval:.4f}")
print(f"True shape: {shape}, True scale: {scale}")
print()

if aft_pval > 0.05:
    print("✓ CORRECT: Weibull AFT also fails to detect effect (as expected)")
else:
    print("✗ Warning: Weibull AFT detects effect (unusual, likely sampling variability)")
print()

# ============================================================================
# 3. Kaplan-Meier curves by treatment
# ============================================================================

kmf = KaplanMeierFitter()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Plot KM by treatment arm
for treatment_arm in [0, 1]:
    mask = df['treatment'] == treatment_arm
    label = f"Control (n={mask.sum()})" if treatment_arm == 0 else f"Treated (n={mask.sum()})"
    kmf.fit(
        durations=df.loc[mask, 'time'],
        event_observed=df.loc[mask, 'event'],
        label=label
    )
    kmf.plot_survival_function(ax=axes[0])

axes[0].set_xlabel('Time')
axes[0].set_ylabel('Survival Probability')
axes[0].set_title('Kaplan-Meier Curves: Control vs Treated\n(No Treatment Effect)')
axes[0].grid(True, alpha=0.3)

# Log-rank test
mask_ctrl = df['treatment'] == 0
mask_trt = df['treatment'] == 1

results = logrank_test(
    durations_A=df.loc[mask_ctrl, 'time'],
    durations_B=df.loc[mask_trt, 'time'],
    event_observed_A=df.loc[mask_ctrl, 'event'],
    event_observed_B=df.loc[mask_trt, 'event']
)

print(f"Log-rank test p-value: {results.p_value:.4f}")
print()

# Plot cumulative hazard
kmf_ctrl = KaplanMeierFitter()
kmf_ctrl.fit(
    durations=df.loc[mask_ctrl, 'time'],
    event_observed=df.loc[mask_ctrl, 'event'],
    label='Control'
)

kmf_trt = KaplanMeierFitter()
kmf_trt.fit(
    durations=df.loc[mask_trt, 'time'],
    event_observed=df.loc[mask_trt, 'event'],
    label='Treated'
)

kmf_ctrl.plot_cumulative_density(ax=axes[1])
kmf_trt.plot_cumulative_density(ax=axes[1])

axes[1].set_xlabel('Time')
axes[1].set_ylabel('Cumulative Event Probability')
axes[1].set_title('Cumulative Event Curves\n(No Treatment Effect)')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('weibull_aft_no_effect.png', dpi=150, bbox_inches='tight')
print("Plot saved: weibull_aft_no_effect.png")

# ============================================================================
# 4. Summary table
# ============================================================================

print("\nSUMMARY TABLE: Event counts by arm")
print("-" * 70)
summary = df.groupby('treatment').agg({
    'time': ['count', 'mean', 'min', 'max'],
    'event': ['sum', 'mean']
}).round(3)

summary.index = ['Control (0)', 'Treated (1)']
print(summary)
print()

print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print("With no true treatment effect (same scale in both arms),")
print("the Cox test correctly fails to reject the null hypothesis.")
print(f"Cox p-value: {treatment_pval:.4f} {'> 0.05 ✓' if treatment_pval > 0.05 else '< 0.05 ✗'}")
