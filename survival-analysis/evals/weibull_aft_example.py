import pandas as pd
from lifelines import WeibullAFTFitter
from lifelines.datasets import load_rossi

# Load the Rossi dataset
rossi = load_rossi()

print("Dataset shape:", rossi.shape)
print("\nFirst few rows:")
print(rossi.head())

# Initialize and fit the Weibull AFT model
aft = WeibullAFTFitter()
aft.fit(rossi, duration_col='week', event_col='arrest')

# Print the summary
print("\n" + "="*70)
print("Weibull AFT Model Summary")
print("="*70)
print(aft.summary)

print("\n" + "="*70)
print("Predicted Median Survival Times for First 5 Rows")
print("="*70)

# Predict median survival time for the first 5 rows
median_predictions = aft.predict_median(rossi.iloc[:5])
print(median_predictions)

print("\n" + "="*70)
print("Comparison with Actual Data")
print("="*70)
comparison = pd.DataFrame({
    'predicted_median': median_predictions,
    'actual_week': rossi.iloc[:5]['week'].values,
    'arrest': rossi.iloc[:5]['arrest'].values
})
print(comparison)
