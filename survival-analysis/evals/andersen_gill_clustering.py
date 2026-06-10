"""
Andersen-Gill with recurrent events: demonstrating cluster_col impact on standard errors.

When subjects experience multiple events (recurrent events), observations are not
independent. Without clustering, standard errors are underestimated because the model
assumes independence. With cluster_col, robust sandwich estimators account for
within-subject correlation, producing larger (more accurate) standard errors.
"""

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
import matplotlib.pyplot as plt

np.random.seed(42)

# ============================================================================
# 1. GENERATE RECURRENT EVENT DATA
# ============================================================================

n_subjects = 200
max_events = 15  # Maximum number of events per subject
follow_up_time = 36  # months

data = []

for subject_id in range(1, n_subjects + 1):
    # Subject covariate (treatment: 0 or 1)
    treatment = np.random.binomial(1, 0.5)

    # Subject-level frailty term (unobserved heterogeneity)
    # Stronger frailty = stronger within-subject correlation
    frailty = np.random.exponential(2.0)  # Increased from 1.0

    # Number of events for this subject
    event_rate = 0.6 * np.exp(0.5 * treatment) * frailty  # Increased from 0.3
    n_events = np.random.poisson(event_rate * follow_up_time / 12)
    n_events = min(n_events, max_events)

    if n_events == 0:
        # No events: censored observation
        data.append({
            'subject_id': subject_id,
            'event_number': 1,
            'time_to_event': follow_up_time,
            'event': 0,
            'treatment': treatment,
            'start_time': 0
        })
    else:
        # Generate event times (non-homogeneous process)
        event_times = np.sort(np.random.uniform(0, follow_up_time, n_events))

        for event_num, event_time in enumerate(event_times, start=1):
            # Risk increases with treatment and subject frailty
            data.append({
                'subject_id': subject_id,
                'event_number': event_num,
                'time_to_event': event_time,
                'event': 1,
                'treatment': treatment,
                'start_time': 0 if event_num == 1 else event_times[event_num - 2]
            })

        # Add final censored row if last event before follow-up
        if event_times[-1] < follow_up_time:
            data.append({
                'subject_id': subject_id,
                'event_number': n_events + 1,
                'time_to_event': follow_up_time,
                'event': 0,
                'treatment': treatment,
                'start_time': event_times[-1]
            })

df = pd.DataFrame(data)
print("=" * 75)
print("RECURRENT EVENT DATA SUMMARY")
print("=" * 75)
print(f"Total subjects: {df['subject_id'].nunique()}")
print(f"Total observations (events + censoring): {len(df)}")
print(f"Total events: {df['event'].sum()}")
print(f"Mean events per subject: {df['event'].sum() / df['subject_id'].nunique():.2f}")
print(f"\nFirst 15 rows:")
print(df.head(15).to_string())

# ============================================================================
# 2. FIT ANDERSEN-GILL WITHOUT CLUSTERING
# ============================================================================

cph_no_cluster = CoxPHFitter()
cph_no_cluster.fit(
    df,
    duration_col='time_to_event',
    event_col='event',
    formula='treatment'
)

print("\n" + "=" * 75)
print("ANDERSEN-GILL WITHOUT CLUSTERING (cluster_col=None)")
print("=" * 75)
print(cph_no_cluster.summary[['coef', 'exp(coef)', 'se(coef)', 'coef lower 95%', 'coef upper 95%']])
print(f"\nStandard error for treatment: {cph_no_cluster.summary.loc['treatment', 'se(coef)']:.6f}")

# ============================================================================
# 3. FIT ANDERSEN-GILL WITH CLUSTERING
# ============================================================================

cph_with_cluster = CoxPHFitter()
cph_with_cluster.fit(
    df,
    duration_col='time_to_event',
    event_col='event',
    formula='treatment',
    cluster_col='subject_id'  # Account for within-subject correlation
)

print("\n" + "=" * 75)
print("ANDERSEN-GILL WITH CLUSTERING (cluster_col='subject_id')")
print("=" * 75)
print(cph_with_cluster.summary[['coef', 'exp(coef)', 'se(coef)', 'coef lower 95%', 'coef upper 95%']])
print(f"\nStandard error for treatment: {cph_with_cluster.summary.loc['treatment', 'se(coef)']:.6f}")

# ============================================================================
# 4. QUANTIFY THE DIFFERENCE
# ============================================================================

se_no_cluster = cph_no_cluster.summary.loc['treatment', 'se(coef)']
se_with_cluster = cph_with_cluster.summary.loc['treatment', 'se(coef)']
se_ratio = se_with_cluster / se_no_cluster

print("\n" + "=" * 75)
print("STANDARD ERROR COMPARISON")
print("=" * 75)
print(f"SE (no clustering):     {se_no_cluster:.6f}")
print(f"SE (with clustering):   {se_with_cluster:.6f}")
print(f"Ratio (with/without):   {se_ratio:.4f}")
print(f"Relative increase:      {(se_ratio - 1) * 100:.2f}%")

# ============================================================================
# 5. IMPACT ON INFERENCE
# ============================================================================

coef = cph_no_cluster.summary.loc['treatment', 'coef']

z_no_cluster = coef / se_no_cluster
z_with_cluster = coef / se_with_cluster

from scipy.stats import norm
p_no_cluster = 2 * (1 - norm.cdf(np.abs(z_no_cluster)))
p_with_cluster = 2 * (1 - norm.cdf(np.abs(z_with_cluster)))

print("\n" + "=" * 75)
print("IMPACT ON HYPOTHESIS TESTS")
print("=" * 75)
print(f"Treatment coefficient: {coef:.6f}")
print(f"\nWithout clustering:")
print(f"  Z-statistic: {z_no_cluster:.4f}")
print(f"  p-value:     {p_no_cluster:.6f}")
print(f"\nWith clustering:")
print(f"  Z-statistic: {z_with_cluster:.4f}")
print(f"  p-value:     {p_with_cluster:.6f}")

# ============================================================================
# 6. VISUALIZE THE DIFFERENCE
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Confidence intervals comparison
ax = axes[0]
ci_no_cluster = cph_no_cluster.summary.loc['treatment', ['coef lower 95%', 'coef upper 95%']]
ci_with_cluster = cph_with_cluster.summary.loc['treatment', ['coef lower 95%', 'coef upper 95%']]

y_pos = [1, 2]
ax.errorbar(
    [coef, coef], y_pos,
    xerr=[[coef - ci_no_cluster[0], coef - ci_with_cluster[0]],
          [ci_no_cluster[1] - coef, ci_with_cluster[1] - coef]],
    fmt='o', markersize=8, capsize=5, capthick=2, linewidth=2
)
ax.axvline(0, color='red', linestyle='--', alpha=0.5, label='Null (coef=0)')
ax.set_yticks(y_pos)
ax.set_yticklabels(['No clustering', 'With clustering'])
ax.set_xlabel('Treatment coefficient (95% CI)')
ax.set_title('Confidence Interval Width Comparison')
ax.grid(True, alpha=0.3)
ax.legend()

# Plot 2: Standard error comparison
ax = axes[1]
models = ['No clustering', 'With clustering']
ses = [se_no_cluster, se_with_cluster]
colors = ['#1f77b4', '#ff7f0e']
bars = ax.bar(models, ses, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
ax.set_ylabel('Standard Error')
ax.set_title('Standard Error of Treatment Coefficient')
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, se in zip(bars, ses):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{se:.4f}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('/Users/jacobelder/Documents/GitHub/jakes-skills/survival-analysis/evals/results/andersen_gill_clustering.png', dpi=300, bbox_inches='tight')
print("\n" + "=" * 75)
print("Plot saved to: andersen_gill_clustering.png")
print("=" * 75)

# ============================================================================
# 7. EXPLANATION
# ============================================================================

print("\n" + "=" * 75)
print("WHY DO STANDARD ERRORS DIFFER?")
print("=" * 75)
print("""
Without cluster_col:
  - Treats each row (event) as an independent observation
  - Ignores that multiple events from the same subject are correlated
  - Underestimates true standard errors (too optimistic inference)
  - Assumes no unobserved subject-level heterogeneity

With cluster_col='subject_id':
  - Uses robust sandwich estimator (Huber-White-Rogers variance)
  - Accounts for within-subject correlation in event times
  - Produces larger, more accurate standard errors
  - Recognizes that subjects vary in their underlying risk (frailty)

In this simulation:
  - {n:.0f} subjects with {events:.0f} total events
  - SE increased by {pct:.1f}% when clustering is accounted for
  - Wider confidence intervals reflect genuine uncertainty

Impact: Without clustering, you might claim significance you don't actually have.
Recurrent event data almost always needs cluster_col for valid inference.
""".format(n=n_subjects, events=df['event'].sum(), pct=(se_ratio - 1) * 100))

plt.show()
