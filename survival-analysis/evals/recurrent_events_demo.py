"""
Demonstrate Andersen-Gill with and without clustering for recurrent events.

When subjects experience multiple events (recurrent events), the observations
are not independent within each subject. Standard errors that ignore this
clustering are too narrow and lead to overstated significance.

The sandwich (robust) estimator with clustering accounts for this dependence.
"""

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# Parameters
n_subjects = 200
true_hazard_ratio = 1.5  # Covariate effect size

# Generate recurrent event data
def simulate_recurrent_events(n_subjects=200, true_hr=1.5):
    """
    Simulate recurrent event data using a two-stage process:
    1. Assign covariates and draw number of events per subject
    2. For each event, draw time using exponential with covariate-dependent rate
    """
    data = []
    subject_ids = []

    for subject_id in range(n_subjects):
        # Covariate: treatment group (0 or 1)
        treatment = np.random.binomial(1, 0.5)

        # Number of events for this subject (Poisson, conditional on treatment)
        # Treated subjects tend to have more events (higher recurrence rate)
        lambda_events = 3 + treatment * 1.5
        n_events = np.random.poisson(lambda_events)
        n_events = max(n_events, 1)  # At least 1 event per subject

        # Generate times for each event (gap times, exponential)
        # Hazard rate depends on treatment
        baseline_rate = 0.15
        rate = baseline_rate * (true_hr ** treatment)  # Proportional hazards

        # Draw gap times (time between events, or to first event)
        gap_times = np.random.exponential(1 / rate, size=n_events)

        # Convert gap times to cumulative time
        cumulative_times = np.cumsum(gap_times)

        # Add event indicator (all 1s since these are observed events)
        for event_num, event_time in enumerate(cumulative_times, 1):
            data.append({
                'subject_id': subject_id,
                'event_number': event_num,
                'time': event_time,
                'event': 1,  # All are events (observed recurrences)
                'treatment': treatment,
            })

    return pd.DataFrame(data)

# Generate data
df = simulate_recurrent_events(n_subjects=n_subjects, true_hr=true_hazard_ratio)

print("=" * 70)
print("RECURRENT EVENT DATA SUMMARY")
print("=" * 70)
print(f"Total subjects: {n_subjects}")
print(f"Total events: {len(df)}")
print(f"Mean events per subject: {len(df) / n_subjects:.2f}")
print(f"\nFirst 10 rows:")
print(df.head(10))
print(f"\nEvents by treatment group:")
print(df.groupby('treatment').agg({
    'subject_id': 'nunique',
    'event': 'sum'
}).rename(columns={
    'subject_id': 'n_subjects',
    'event': 'n_events'
}))

# Fit Andersen-Gill WITHOUT clustering
print("\n" + "=" * 70)
print("ANDERSEN-GILL: WITHOUT CLUSTERING (naive standard errors)")
print("=" * 70)

cph_naive = CoxPHFitter()
cph_naive.fit(df, duration_col='time', event_col='event', formula='treatment')

# Extract the result for treatment (note: CI is on log scale)
coef_naive = cph_naive.hazard_ratios_['treatment']
se_naive = cph_naive.standard_errors_['treatment']
ci_naive = cph_naive.confidence_intervals_
log_ci_lower_naive = ci_naive.iloc[0, 0]
log_ci_upper_naive = ci_naive.iloc[0, 1]
ci_lower_naive = np.exp(log_ci_lower_naive)
ci_upper_naive = np.exp(log_ci_upper_naive)
llr_test_naive = cph_naive.log_likelihood_ratio_test()
p_value_naive = llr_test_naive.p_value

print(f"\nHazard Ratio: {coef_naive:.4f}")
print(f"Standard Error: {se_naive:.6f}")
print(f"95% CI: [{ci_lower_naive:.4f}, {ci_upper_naive:.4f}]")
print(f"Log-rank test p-value: {p_value_naive:.6f}")

# Fit Andersen-Gill WITH clustering
print("\n" + "=" * 70)
print("ANDERSEN-GILL: WITH CLUSTERING (robust sandwich standard errors)")
print("=" * 70)

cph_clustered = CoxPHFitter()
cph_clustered.fit(
    df,
    duration_col='time',
    event_col='event',
    cluster_col='subject_id',  # Account for dependence within subjects
    formula='treatment'
)

coef_clustered = cph_clustered.hazard_ratios_['treatment']
se_clustered = cph_clustered.standard_errors_['treatment']
ci_clustered = cph_clustered.confidence_intervals_
log_ci_lower_clustered = ci_clustered.iloc[0, 0]
log_ci_upper_clustered = ci_clustered.iloc[0, 1]
ci_lower_clustered = np.exp(log_ci_lower_clustered)
ci_upper_clustered = np.exp(log_ci_upper_clustered)
llr_test_clustered = cph_clustered.log_likelihood_ratio_test()
p_value_clustered = llr_test_clustered.p_value

print(f"\nHazard Ratio: {coef_clustered:.4f}")
print(f"Standard Error: {se_clustered:.6f}")
print(f"95% CI: [{ci_lower_clustered:.4f}, {ci_upper_clustered:.4f}]")
print(f"Log-rank test p-value: {p_value_clustered:.6f}")

# Compare
print("\n" + "=" * 70)
print("COMPARISON: IMPACT OF CLUSTERING")
print("=" * 70)

se_ratio = se_clustered / se_naive
print(f"\nStandard Error Ratio (clustered / naive): {se_ratio:.3f}")
print(f"  → Clustered SE is {(se_ratio - 1) * 100:.1f}% LARGER")
print(f"\nCI Width Ratio (clustered / naive): {(ci_upper_clustered - ci_lower_clustered) / (ci_upper_naive - ci_lower_naive):.3f}")

print(f"\nNaive 95% CI width:     {ci_upper_naive - ci_lower_naive:.4f}")
print(f"Clustered 95% CI width: {ci_upper_clustered - ci_lower_clustered:.4f}")

print(f"\n→ Ignoring clustering gives FALSE CONFIDENCE (too-narrow CI)")
print(f"→ Clustered SE correctly accounts for within-subject dependence")

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Standard errors
methods = ['Naive\n(ignores clustering)', 'Robust\n(with clustering)']
ses = [se_naive, se_clustered]
colors = ['#d62728', '#2ca02c']

ax = axes[0]
bars = ax.bar(methods, ses, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
ax.set_ylabel('Standard Error', fontsize=11)
ax.set_title('Standard Error Comparison\n(lower is more confident, but naive is overconfident)',
             fontsize=11, fontweight='bold')
ax.set_ylim([0, max(ses) * 1.3])
for bar, se in zip(bars, ses):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{se:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Plot 2: Confidence intervals
ax = axes[1]
y_pos = [0, 1]
for i, (lower, upper, method, color) in enumerate([
    (ci_lower_naive, ci_upper_naive, 'Naive', colors[0]),
    (ci_lower_clustered, ci_upper_clustered, 'Robust', colors[1])
]):
    ax.plot([lower, upper], [i, i], 'o-', linewidth=2.5, markersize=8,
            color=color, label=method, alpha=0.8)
    ax.text(lower - 0.05, i, f'{lower:.3f}', ha='right', va='center', fontsize=9)
    ax.text(upper + 0.05, i, f'{upper:.3f}', ha='left', va='center', fontsize=9)

ax.axvline(true_hazard_ratio, color='gray', linestyle='--', linewidth=2,
           label=f'True HR = {true_hazard_ratio}', alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(['Naive', 'Robust'])
ax.set_xlabel('Hazard Ratio (log scale)', fontsize=11)
ax.set_title('95% Confidence Intervals\n(robust CI is wider because it''s correct)',
             fontsize=11, fontweight='bold')
ax.legend(loc='best', fontsize=9)
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/jacobelder/Documents/GitHub/jakes-skills/survival-analysis/evals/recurrent_events_comparison.png',
            dpi=150, bbox_inches='tight')
print("\n✓ Plot saved: recurrent_events_comparison.png")

# Statistical intuition
print("\n" + "=" * 70)
print("WHY THE STANDARD ERRORS DIFFER")
print("=" * 70)
print(f"""
In recurrent event data:
  • Subjects contribute multiple observations (events)
  • Events within the same subject are CORRELATED
  • Naive approach: treats all {len(df)} events as independent
  • Correct approach: clusters observations by subject (n={n_subjects})

Information content:
  • Effective sample size with clustering ≈ {n_subjects} (subjects)
  • Naive treats n as {len(df)} (events), which overstates information
  • Result: naive SE is {(1/se_ratio - 1) * 100:.1f}% too small

When to use clustering:
  ✓ Multiple events per subject (recurrent events)
  ✓ Multiple treatments per site (nested structure)
  ✓ Repeated measurements from same unit
  ✗ Should NOT use if data already structured as one row per subject
""")

# Show distribution of events per subject
print("\n" + "=" * 70)
print("DISTRIBUTION OF RECURRENCE ACROSS SUBJECTS")
print("=" * 70)
events_per_subject = df.groupby('subject_id').size()
print(f"Events per subject (summary):")
print(f"  Min: {events_per_subject.min()}")
print(f"  Median: {events_per_subject.median():.0f}")
print(f"  Max: {events_per_subject.max()}")
print(f"  Mean: {events_per_subject.mean():.2f}")

# Show that within-subject events are correlated
print(f"\nWith {events_per_subject.mean():.2f} events per subject on average,")
print(f"the naive SE ignores this {events_per_subject.mean():.2f}x correlation structure.")
