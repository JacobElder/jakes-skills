"""
Simulate Weibull AFT model with no treatment effect and show Cox model doesn't detect it.
"""
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
import matplotlib.pyplot as plt

np.random.seed(42)

# ============================================================================
# PARAMETERS
# ============================================================================
n_subjects = 1000
weibull_shape = 1.5
weibull_scale = 1.0  # Same scale for BOTH arms (no treatment effect in AFT)
censoring_scale = 3.0  # Controls censoring rate

# ============================================================================
# SIMULATE DATA
# ============================================================================
treatment = np.repeat([0, 1], n_subjects // 2)

# Weibull AFT: same shape and scale in both arms means NO treatment effect
# T ~ Weibull(shape, scale)
T = np.random.weibull(weibull_shape, size=n_subjects) * weibull_scale

# Censoring times (independent)
C = np.random.exponential(scale=censoring_scale, size=n_subjects)

# Observed data
Y = np.minimum(T, C)
event = (T <= C).astype(int)

df = pd.DataFrame({
    'time': Y,
    'event': event,
    'treatment': treatment
})

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("="*70)
print("SIMULATED DATA SUMMARY (Weibull AFT, no treatment effect)")
print("="*70)
print(f"Total subjects: {len(df)}")
print(f"Events: {event.sum()} ({100*event.sum()/len(event):.1f}%)")
print(f"\nEvent rate by treatment group:")
event_summary = df.groupby('treatment')['event'].agg(['sum', 'count', 'mean'])
event_summary.columns = ['Events', 'N', 'Event_Rate']
print(event_summary)

print(f"\nMedian survival time by treatment group:")
print(df.groupby('treatment')['time'].agg(['count', 'median', 'mean', 'std']))

# ============================================================================
# FIT COX PROPORTIONAL HAZARDS MODEL
# ============================================================================
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event')

print("\n" + "="*70)
print("COX PROPORTIONAL HAZARDS MODEL RESULTS")
print("="*70)
print(cph.summary)

# Extract and report treatment effect
coef = cph.summary.loc['treatment', 'coef']
hr = np.exp(coef)
p_value = cph.summary.loc['treatment', 'p']
ci_lower = cph.summary.loc['treatment', 'exp(coef) lower 95%']
ci_upper = cph.summary.loc['treatment', 'exp(coef) upper 95%']

print(f"\n{'='*70}")
print("TREATMENT EFFECT INTERPRETATION")
print(f"{'='*70}")
print(f"Hazard Ratio (95% CI):     {hr:.4f} ({ci_lower:.4f} - {ci_upper:.4f})")
print(f"p-value:                   {p_value:.4f}")
print(f"Coefficient:               {coef:.4f}")

if p_value > 0.05:
    print(f"\n✓ RESULT: No significant treatment effect detected (p = {p_value:.4f} > 0.05)")
    print("  Expected outcome: the same scale in both arms means no true effect")
else:
    print(f"\n✗ UNEXPECTED: Significant effect detected (p = {p_value:.4f} < 0.05)")
    print("  Note: This could be due to random sampling variation (α = 5% test)")

# ============================================================================
# KAPLAN-MEIER CURVES
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

kmf = KaplanMeierFitter()

for treatment_val, label in [(0, 'Control'), (1, 'Treatment')]:
    mask = df['treatment'] == treatment_val
    kmf.fit(
        durations=df.loc[mask, 'time'],
        event_observed=df.loc[mask, 'event'],
        label=label
    )
    kmf.plot_survival_function(ax=ax, ci_show=True)

ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Survival Probability', fontsize=12)
ax.set_title('Kaplan-Meier Curves by Treatment\n(Weibull AFT with No Treatment Effect)', fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/Users/jacobelder/Documents/GitHub/jakes-skills/survival-analysis/evals/km_curves.png', dpi=150)
print(f"\n✓ Kaplan-Meier curves saved to km_curves.png")

# ============================================================================
# EXPLAIN THE MODEL
# ============================================================================
print(f"\n{'='*70}")
print("MODEL SETUP EXPLANATION")
print(f"{'='*70}")
print(f"""
This simulation demonstrates an important point about survival models:

1. DATA GENERATION (Weibull AFT):
   - True model: T ~ Weibull(shape={weibull_shape}, scale={weibull_scale})
   - Both treatment arms use SAME scale → NO true treatment effect
   - AFT model would find: β_treatment = 0

2. COX ANALYSIS:
   - We fit a Cox Proportional Hazards model (different model class)
   - Result: p-value = {p_value:.4f}

3. INTERPRETATION:
   - The Cox test does NOT detect a treatment effect
   - This is the correct result since we simulated data with no effect
   - The p-value of {p_value:.4f} indicates no significant difference
     between treatment arms

KEY INSIGHT:
The Weibull distribution (shape ≠ 1) violates the proportional hazards
assumption. However, when there IS NO TREATMENT EFFECT, the Cox model
correctly fails to detect one, regardless of the baseline hazard shape.
""")
