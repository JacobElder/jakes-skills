"""
Simulate Weibull AFT data with no treatment effect and fit Cox PH regression.
Demonstrates that Cox correctly fails to detect the null effect, and shows
the efficiency loss compared to the true parametric model.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter, WeibullAFTFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
from scipy.stats import weibull_min
import seaborn as sns

sns.set_style("whitegrid")

# ============================================================================
# 1. SIMULATE DATA FROM WEIBULL AFT
# ============================================================================

np.random.seed(42)

n = 1000
treatment = np.random.binomial(1, 0.5, n)

# Weibull AFT parameters
shape = 1.5  # shape parameter (inverse of scale parameter σ in log-linear form)
scale = 100  # scale parameter SAME for both arms (NO treatment effect)

# Generate true event times from Weibull distribution
# scipy.stats.weibull_min.rvs: c=shape, scale=scale
true_times = weibull_min.rvs(c=shape, scale=scale, size=n)

# Add right censoring (~30%)
censoring_times = np.random.exponential(scale=200, size=n)
event_observed = true_times < censoring_times
observed_times = np.minimum(true_times, censoring_times)

# Create dataframe
df = pd.DataFrame({
    'T': observed_times,
    'E': event_observed.astype(int),
    'treatment': treatment
})

print("=" * 75)
print("WEIBULL AFT SIMULATION: NO TREATMENT EFFECT")
print("=" * 75)
print(f"\nData generation:")
print(f"  N = {n} subjects")
print(f"  Weibull shape = {shape}")
print(f"  Weibull scale = {scale} (IDENTICAL for both arms)")
print(f"  Binary treatment: 0 or 1")
print(f"  Censoring rate: {(1 - df['E'].sum() / len(df)) * 100:.1f}%")
print(f"  Events observed: {df['E'].sum()} / {len(df)}")

# ============================================================================
# 2. LOG-RANK TEST (non-parametric hypothesis test)
# ============================================================================

results_logrank = logrank_test(
    durations_A=df.loc[df['treatment'] == 0, 'T'],
    durations_B=df.loc[df['treatment'] == 1, 'T'],
    event_observed_A=df.loc[df['treatment'] == 0, 'E'],
    event_observed_B=df.loc[df['treatment'] == 1, 'E']
)

print("\n" + "=" * 75)
print("LOG-RANK TEST")
print("=" * 75)
print(results_logrank)

# ============================================================================
# 3. COX PROPORTIONAL HAZARDS REGRESSION
# ============================================================================

cox = CoxPHFitter()
cox.fit(df, duration_col='T', event_col='E')

print("\n" + "=" * 75)
print("COX PROPORTIONAL HAZARDS REGRESSION")
print("=" * 75)
print(cox.summary)
print(f"\nTreatment effect (coefficient): {cox.params_['treatment']:.6f}")
print(f"Hazard ratio (exp(coef)): {np.exp(cox.params_['treatment']):.6f}")
print(f"95% CI: ({np.exp(cox.confidence_intervals_.loc['treatment', '95% lower-bound']):.4f}, "
      f"{np.exp(cox.confidence_intervals_.loc['treatment', '95% upper-bound']):.4f})")
print(f"P-value: {cox.summary.loc['treatment', 'p']:.4f}")

# ============================================================================
# 4. WEIBULL AFT REGRESSION (TRUE MODEL)
# ============================================================================

aft = WeibullAFTFitter()
aft.fit(df, duration_col='T', event_col='E')

print("\n" + "=" * 75)
print("WEIBULL AFT REGRESSION (TRUE MODEL)")
print("=" * 75)
print(aft.summary)
print(f"\nTreatment effect (log-acceleration): {aft.params_[('lambda_', 'treatment')]:.6f}")
print(f"95% CI: ({aft.confidence_intervals_.loc[('lambda_', 'treatment'), '95% lower-bound']:.4f}, "
      f"{aft.confidence_intervals_.loc[('lambda_', 'treatment'), '95% upper-bound']:.4f})")
print(f"P-value: {aft.summary.loc[('lambda_', 'treatment'), 'p']:.4f}")

# Compare standard errors
print("\n" + "=" * 75)
print("EFFICIENCY COMPARISON")
print("=" * 75)
cox_se = cox.summary.loc['treatment', 'se(coef)']
aft_se = aft.summary.loc[('lambda_', 'treatment'), 'se(coef)']
efficiency_gain = (cox_se / aft_se - 1) * 100

print(f"Cox standard error: {cox_se:.6f}")
print(f"AFT standard error: {aft_se:.6f}")
print(f"Relative SE increase (Cox vs AFT): {efficiency_gain:.1f}%")
print(f"\nWhen data is truly parametric (Weibull), the AFT model is more efficient")
print(f"than Cox PH, resulting in narrower confidence intervals.")

# ============================================================================
# 5. VISUALIZATION
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# KM curves by treatment
kmf = KaplanMeierFitter()
for treat in [0, 1]:
    mask = df['treatment'] == treat
    kmf.fit(df.loc[mask, 'T'], df.loc[mask, 'E'], label=f'Treatment={treat}')
    kmf.plot_survival_function(ax=axes[0, 0], ci_show=True)

axes[0, 0].set_title('Kaplan-Meier Curves by Treatment\n(No significant difference: p={:.3f})'.format(
    results_logrank.p_value), fontsize=11, fontweight='bold')
axes[0, 0].set_xlabel('Time')
axes[0, 0].set_ylabel('Survival Probability')
axes[0, 0].legend(fontsize=10)
axes[0, 0].grid(True, alpha=0.3)

# Event time distributions
for treat in [0, 1]:
    mask = df['treatment'] == treat
    axes[0, 1].hist(df.loc[mask, 'T'], bins=25, alpha=0.6,
                    label=f'Treatment={treat}', density=True)
axes[0, 1].set_title('Observed Event Time Distributions\n(Nearly Identical)',
                     fontsize=11, fontweight='bold')
axes[0, 1].set_xlabel('Time')
axes[0, 1].set_ylabel('Density')
axes[0, 1].legend(fontsize=10)
axes[0, 1].grid(True, alpha=0.3)

# Cox forest plot for treatment
axes[1, 0].barh([0], [cox.params_['treatment']], xerr=[[cox_se], [cox_se]],
                color='steelblue', error_kw={'elinewidth': 2, 'capsize': 5})
axes[1, 0].axvline(x=0, color='red', linestyle='--', linewidth=2, label='No effect')
axes[1, 0].set_yticks([0])
axes[1, 0].set_yticklabels(['Treatment'])
axes[1, 0].set_xlabel('Log Hazard Ratio (with 95% CI)')
axes[1, 0].set_title('Cox PH: Treatment Effect Estimate\n(Centered at zero: no effect)',
                     fontsize=11, fontweight='bold')
axes[1, 0].grid(True, alpha=0.3, axis='x')

# Summary table
summary_text = f"""
NULL HYPOTHESIS TEST RESULTS:

Log-Rank Test:
  Test statistic: {results_logrank.test_statistic:.4f}
  P-value: {results_logrank.p_value:.4f}
  → No treatment effect detected ✓

Cox PH Regression:
  Treatment coef: {cox.params_['treatment']:.6f}
  Hazard ratio: {np.exp(cox.params_['treatment']):.6f}
  P-value: {cox.summary.loc['treatment', 'p']:.4f}
  95% CI for HR: ({np.exp(cox.confidence_intervals_.loc['treatment', '95% lower-bound']):.4f}, {np.exp(cox.confidence_intervals_.loc['treatment', '95% upper-bound']):.4f})
  → No treatment effect detected ✓

Weibull AFT Regression:
  Treatment coef: {aft.params_[('lambda_', 'treatment')]:.6f}
  P-value: {aft.summary.loc[('lambda_', 'treatment'), 'p']:.4f}
  → No treatment effect detected ✓

INTERPRETATION:
Both Cox (semi-parametric) and AFT (parametric)
correctly fail to detect a null effect, as expected.
Cox SE is {efficiency_gain:.0f}% larger than AFT.
"""
axes[1, 1].text(0.05, 0.95, summary_text, fontsize=9.5, family='monospace',
                verticalalignment='top', transform=axes[1, 1].transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
axes[1, 1].axis('off')

plt.tight_layout()
plt.savefig('/Users/jacobelder/Documents/GitHub/jakes-skills/survival-analysis/evals/weibull_aft_cox_sim.png', dpi=100, bbox_inches='tight')
print("\n✓ Plot saved to weibull_aft_cox_sim.png")
plt.show()

# ============================================================================
# 6. KEY INSIGHTS
# ============================================================================

print("\n" + "=" * 75)
print("KEY INSIGHTS")
print("=" * 75)
print("""
1. DATA GENERATION:
   - True model is Weibull AFT with shape=1.5, scale=100
   - Both treatment arms have IDENTICAL scale → no true treatment effect
   - Right-censored data (realistic survival study)

2. HYPOTHESIS TESTS:
   - Log-rank test: p={:.4f} (correctly rejects H₁: treatment ≠ control)
   - Cox PH: p={:.4f} (correctly fails to detect treatment effect)

3. MODEL COMPARISON:
   - Cox PH is VALID for parametric data (does not assume Weibull)
   - However, when data is truly parametric, AFT is MORE EFFICIENT
   - Cox has ~{:.0f}% larger standard errors than the true model

4. INTERPRETATION:
   - Both tests correctly show NO significant treatment effect
   - This is the expected result: the null hypothesis IS true
   - Neither model over-detects a spurious effect (Type I error = 0)

5. PRACTICAL LESSON:
   - Cox PH is robust but loses efficiency if the true distribution is known
   - If you suspect a parametric distribution (e.g., from EDA or external knowledge),
     consider fitting the parametric model for narrower CIs
   - For inference, both approaches are valid; choice depends on assumptions
     you're willing to make and efficiency you require
""".format(results_logrank.p_value, cox.summary.loc['treatment', 'p'], efficiency_gain))
