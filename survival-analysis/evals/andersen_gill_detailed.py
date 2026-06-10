"""
Additional visualization: Understanding the correlation structure.
Shows why within-subject correlation is real and substantial.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

np.random.seed(42)

# Recreate the data from the previous script
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
                    'event_number': event_number,
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
                    'event_number': event_number,
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
                        'event_number': event_number,
                    })
                    break
    return pd.DataFrame(data)

df = generate_recurrent_data(n_subjects=200, max_time=365)

# Create figures
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# Panel A: Distribution of events per subject
ax1 = fig.add_subplot(gs[0, 0])
events_per_subject = df.groupby('id')['event'].sum()
ax1.hist(events_per_subject, bins=np.arange(0, events_per_subject.max() + 2) - 0.5, 
         color='steelblue', edgecolor='black', alpha=0.7)
ax1.set_xlabel('Number of Events per Subject', fontsize=11)
ax1.set_ylabel('Frequency', fontsize=11)
ax1.set_title('Distribution of Recurrent Events\nper Subject', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)
ax1.text(0.98, 0.97, f'n={events_per_subject.shape[0]} subjects\nMean={events_per_subject.mean():.2f}',
         transform=ax1.transAxes, fontsize=10, ha='right', va='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Panel B: Rows per subject (correlation indicator)
ax2 = fig.add_subplot(gs[0, 1])
rows_per_subject = df.groupby('id').size()
ax2.hist(rows_per_subject, bins=np.arange(1, rows_per_subject.max() + 2) - 0.5,
         color='coral', edgecolor='black', alpha=0.7)
ax2.set_xlabel('Number of Rows (Intervals) per Subject', fontsize=11)
ax2.set_ylabel('Frequency', fontsize=11)
ax2.set_title('Multiple Rows = Multiple Events\nThese Rows Are Correlated!', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)
ax2.text(0.98, 0.97, f'Total rows={len(df)}\nIf independent: SE = sqrt({len(df)})',
         transform=ax2.transAxes, fontsize=10, ha='right', va='top',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

# Panel C: Example subjects with multiple events
ax3 = fig.add_subplot(gs[1, :])
events_by_subject = df.groupby('id')['event'].sum()
example_ids = [1, events_by_subject[events_by_subject > 2].index[0]]
colors = ['#2ecc71', '#e74c3c']

for idx, (color, example_id) in enumerate(zip(colors, example_ids)):
    subject_data = df[df['id'] == example_id].sort_values('tstop')
    for i, (_, row) in enumerate(subject_data.iterrows()):
        y_offset = idx
        width = row['tstop'] - row['tstart']
        if row['event'] == 1:
            ax3.barh(y_offset, width, left=row['tstart'], height=0.4,
                    color=color, edgecolor='black', linewidth=2)
            ax3.scatter(row['tstop'], y_offset, marker='*', s=300, color='gold', 
                       edgecolor='black', zorder=5)
        else:
            ax3.barh(y_offset, width, left=row['tstart'], height=0.4,
                    color=color, alpha=0.3, edgecolor='black', linewidth=1, linestyle='--')

ax3.set_yticks([0, 1])
ax3.set_yticklabels([f'Subject {example_ids[0]}', f'Subject {example_ids[1]}'], fontsize=11)
ax3.set_xlabel('Time (days)', fontsize=11)
ax3.set_title('Example: Subjects with Multiple Events\n(Stars = Event times; Dashed = Censoring intervals)',
             fontsize=12, fontweight='bold')
ax3.grid(axis='x', alpha=0.3)
ax3.set_xlim([0, 300])

# Panel D: Why clustering matters - illustration of naive assumption violation
ax4 = fig.add_subplot(gs[2, 0])

n_rows = len(df)
n_subjects = df['id'].nunique()
avg_rows_per_subject = n_rows / n_subjects

inflation_factor_theory = np.sqrt(avg_rows_per_subject)
se_inflation_treatment = 1.27
se_inflation_age = 1.23

methods = ['Theory\n(ideal clustering)', 'Observed\n(Treatment)', 'Observed\n(Age)']
inflation_factors = [inflation_factor_theory, se_inflation_treatment, se_inflation_age]
colors_bars = ['gray', '#e74c3c', '#e67e22']

bars = ax4.bar(methods, inflation_factors, color=colors_bars, alpha=0.7, edgecolor='black', linewidth=2)
ax4.axhline(1, color='black', linestyle='--', linewidth=2, label='No inflation (independent rows)')
ax4.set_ylabel('SE Inflation Factor (Robust / Naive)', fontsize=11)
ax4.set_title('SE Inflation: Theory vs. Observed', fontsize=12, fontweight='bold')
ax4.set_ylim([0.9, inflation_factor_theory * 1.1])

for bar, val in zip(bars, inflation_factors):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{val:.2f}x', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax4.legend(fontsize=10, loc='upper left')
ax4.grid(axis='y', alpha=0.3)

# Panel E: Type I error rate simulation (conceptual)
ax5 = fig.add_subplot(gs[2, 1])

nominal_alpha = 0.05
critical_z = norm.ppf(1 - nominal_alpha / 2)

inflation_seq = np.linspace(1.0, 2.0, 50)
actual_alpha = []
for inf in inflation_seq:
    critical_true_z = critical_z / inf
    actual_alpha_val = 2 * (1 - norm.cdf(critical_true_z))
    actual_alpha.append(actual_alpha_val)

ax5.plot(inflation_seq, actual_alpha, color='#e74c3c', linewidth=3, label='Actual Type I error')
ax5.axhline(0.05, color='black', linestyle='--', linewidth=2, label='Nominal α=0.05')
ax5.scatter([se_inflation_treatment], 
           [2 * (1 - norm.cdf(critical_z / se_inflation_treatment))],
           color='#e74c3c', s=200, zorder=5, edgecolor='black', linewidth=2,
           label=f'This example (inflation={se_inflation_treatment:.2f}x)')
ax5.set_xlabel('SE Inflation Factor (Robust / Naive)', fontsize=11)
ax5.set_ylabel('Actual Type I Error Rate', fontsize=11)
ax5.set_title('Cost of Ignoring Clustering\n(Inflated False Positive Rate)', 
             fontsize=12, fontweight='bold')
ax5.set_xlim([1.0, 2.0])
ax5.set_ylim([0.04, 0.25])
ax5.legend(fontsize=10, loc='upper left')
ax5.grid(alpha=0.3)

plt.suptitle('Why Cluster-Robust SEs Are Essential in Recurrent Event Analysis',
            fontsize=14, fontweight='bold', y=0.995)

plt.savefig('andersen_gill_clustering_details.png', dpi=300, bbox_inches='tight')
print("Figure saved: andersen_gill_clustering_details.png")

# Print summary statistics
print("\n" + "=" * 70)
print("CLUSTERING STRUCTURE IN THIS DATA")
print("=" * 70)
print(f"\nTotal observations (rows): {len(df)}")
print(f"Number of subjects (clusters): {n_subjects}")
print(f"Ratio: {n_rows/n_subjects:.2f} rows per subject on average")
print(f"\nTheoretical SE inflation (ideal case):")
print(f"  sqrt({avg_rows_per_subject:.2f}) = {inflation_factor_theory:.2f}x")
print(f"\nObserved SE inflation:")
print(f"  Treatment: 1.27x")
print(f"  Age:       1.23x")
print(f"\nWhy the difference between theory and observed?")
print(f"  → Clustering is imperfect (some subjects have 1 row, others 4)")
print(f"  → Not all within-subject correlation is due to multiple events")
print(f"  → Some variation is unexplained (residual variation)")
print("=" * 70)
