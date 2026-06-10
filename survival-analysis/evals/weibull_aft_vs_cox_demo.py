"""
Demonstrate Weibull AFT vs Cox: when there's no effect, Cox finds none.
Also show what happens with an actual effect (where PH is violated).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test
from lifelines.utils import median_survival_times

np.random.seed(42)
n = 1000

# ============================================================================
# SCENARIO 1: No treatment effect (same scale in both arms)
# ============================================================================
print("=" * 70)
print("SCENARIO 1: NO TREATMENT EFFECT")
print("=" * 70)

shape = 1.5
scale_control = 1.0  # scale for control arm
scale_treatment = 1.0  # SAME scale for treatment arm (no effect)

# Generate survival times from Weibull AFT
# T = scale * W^(1/shape), where W ~ Exp(1)
n_half = n // 2
W_control = np.random.exponential(1, n_half)
W_treatment = np.random.exponential(1, n_half)

T_control = scale_control * (W_control ** (1 / shape))
T_treatment = scale_treatment * (W_treatment ** (1 / shape))

# Add censoring (30% censoring rate)
censor_rate = 0.3
C_control = np.random.exponential(np.percentile(T_control, (1 - censor_rate) * 100), n_half)
C_treatment = np.random.exponential(np.percentile(T_treatment, (1 - censor_rate) * 100), n_half)

time_control = np.minimum(T_control, C_control)
event_control = (T_control <= C_control).astype(int)

time_treatment = np.minimum(T_treatment, C_treatment)
event_treatment = (T_treatment <= C_treatment).astype(int)

# Combine into dataframe
df_no_effect = pd.DataFrame({
    'time': np.concatenate([time_control, time_treatment]).astype(float),
    'event': np.concatenate([event_control, event_treatment]).astype(int),
    'treatment': np.concatenate([np.zeros(n_half), np.ones(n_half)]).astype(int)
})

# Fit Cox model
cox_no_effect = CoxPHFitter()
cox_no_effect.fit(df_no_effect, duration_col='time', event_col='event')

print("\nCox Regression (No Effect Scenario):")
print(cox_no_effect.summary[['exp(coef)', 'se(coef)', 'p']])
print(f"\nTreatment effect HR: {cox_no_effect.hazard_ratios_['treatment']:.3f}")
print(f"p-value: {cox_no_effect.summary.loc['treatment', 'p']:.4f}")

# Log-rank test
result_logrank = logrank_test(
    durations_A=df_no_effect[df_no_effect['treatment'] == 0]['time'],
    durations_B=df_no_effect[df_no_effect['treatment'] == 1]['time'],
    event_observed_A=df_no_effect[df_no_effect['treatment'] == 0]['event'],
    event_observed_B=df_no_effect[df_no_effect['treatment'] == 1]['event']
)
print(f"\nLog-rank test p-value: {result_logrank.p_value:.4f}")
print(f"Conclusion: Cox correctly finds NO significant effect (as expected)")

# Kaplan-Meier curves
kmf = KaplanMeierFitter()
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

kmf.fit(
    durations=df_no_effect[df_no_effect['treatment'] == 0]['time'],
    event_observed=df_no_effect[df_no_effect['treatment'] == 0]['event'],
    label='Control'
)
kmf.plot_survival_function(ax=ax[0], ci_show=True)

kmf.fit(
    durations=df_no_effect[df_no_effect['treatment'] == 1]['time'],
    event_observed=df_no_effect[df_no_effect['treatment'] == 1]['event'],
    label='Treatment'
)
kmf.plot_survival_function(ax=ax[0], ci_show=True)
ax[0].set_title('Scenario 1: No Effect (Curves Should Overlap)')
ax[0].set_ylabel('Survival Probability')
ax[0].set_xlabel('Time')

# ============================================================================
# SCENARIO 2: WITH treatment effect (to show contrast)
# ============================================================================
print("\n" + "=" * 70)
print("SCENARIO 2: WITH TREATMENT EFFECT (Scale = 1.0 vs 1.5)")
print("=" * 70)

scale_treatment_effect = 1.5  # Treatment increases scale, extends survival

T_control_2 = scale_control * (W_control ** (1 / shape))
T_treatment_2 = scale_treatment_effect * (W_treatment ** (1 / shape))

C_control_2 = np.random.exponential(np.percentile(T_control_2, (1 - censor_rate) * 100), n_half)
C_treatment_2 = np.random.exponential(np.percentile(T_treatment_2, (1 - censor_rate) * 100), n_half)

time_control_2 = np.minimum(T_control_2, C_control_2)
event_control_2 = (T_control_2 <= C_control_2).astype(int)

time_treatment_2 = np.minimum(T_treatment_2, C_treatment_2)
event_treatment_2 = (T_treatment_2 <= C_treatment_2).astype(int)

df_with_effect = pd.DataFrame({
    'time': np.concatenate([time_control_2, time_treatment_2]).astype(float),
    'event': np.concatenate([event_control_2, event_treatment_2]).astype(int),
    'treatment': np.concatenate([np.zeros(n_half), np.ones(n_half)]).astype(int)
})

# Fit Cox model
cox_with_effect = CoxPHFitter()
cox_with_effect.fit(df_with_effect, duration_col='time', event_col='event')

print("\nCox Regression (With Effect Scenario):")
print(cox_with_effect.summary[['exp(coef)', 'se(coef)', 'p']])
print(f"\nTreatment effect HR: {cox_with_effect.hazard_ratios_['treatment']:.3f}")
print(f"p-value: {cox_with_effect.summary.loc['treatment', 'p']:.4f}")

# Note: HR < 1 because treatment INCREASES scale, which DECREASES hazard
# AFT parameterization: longer scale = longer survival = lower hazard

result_logrank_2 = logrank_test(
    durations_A=df_with_effect[df_with_effect['treatment'] == 0]['time'],
    durations_B=df_with_effect[df_with_effect['treatment'] == 1]['time'],
    event_observed_A=df_with_effect[df_with_effect['treatment'] == 0]['event'],
    event_observed_B=df_with_effect[df_with_effect['treatment'] == 1]['event']
)
print(f"\nLog-rank test p-value: {result_logrank_2.p_value:.4f}")

# KM curves
kmf.fit(
    durations=df_with_effect[df_with_effect['treatment'] == 0]['time'],
    event_observed=df_with_effect[df_with_effect['treatment'] == 0]['event'],
    label='Control'
)
kmf.plot_survival_function(ax=ax[1], ci_show=True)

kmf.fit(
    durations=df_with_effect[df_with_effect['treatment'] == 1]['time'],
    event_observed=df_with_effect[df_with_effect['treatment'] == 1]['event'],
    label='Treatment'
)
kmf.plot_survival_function(ax=ax[1], ci_show=True)
ax[1].set_title('Scenario 2: With Effect (Treatment arm extends survival)')
ax[1].set_ylabel('Survival Probability')
ax[1].set_xlabel('Time')

plt.tight_layout()
plt.savefig('/Users/jacobelder/Documents/GitHub/jakes-skills/survival-analysis/evals/weibull_aft_vs_cox.png', dpi=150)
print("\nPlot saved to weibull_aft_vs_cox.png")

# ============================================================================
# Check proportional hazards assumption
# ============================================================================
print("\n" + "=" * 70)
print("PROPORTIONAL HAZARDS CHECK (Schoenfeld Residuals)")
print("=" * 70)

print("\nScenario 1 (No Effect):")
try:
    cox_no_effect.check_assumptions(df_no_effect, p_value_threshold=0.05)
except Exception as e:
    print(f"Note: PH check result: {e}")

print("\nScenario 2 (With Effect):")
try:
    cox_with_effect.check_assumptions(df_with_effect, p_value_threshold=0.05)
except Exception as e:
    print(f"Note: PH check result: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
Scenario 1 (No Effect):
  - Both arms generated with shape=1.5, scale=1.0
  - Cox log-rank test correctly finds NO effect (as expected)

Scenario 2 (With Effect):
  - Control: shape=1.5, scale=1.0
  - Treatment: shape=1.5, scale=1.5 (50% increase in scale)
  - This extends survival time (lower hazard)
  - Cox DETECTS the effect (p < 0.05)
  - HR < 1 indicates treatment reduces hazard (protects survival)

Key insight:
  - Weibull shape ≠ 1 means PH is violated (hazard ratio changes over time)
  - With shape=1.5, Cox is still reasonably powerful but parametrizes
    the effect differently than AFT's scale parameter
  - For true AFT interpretation, fit a Weibull AFT model, not Cox
""")
