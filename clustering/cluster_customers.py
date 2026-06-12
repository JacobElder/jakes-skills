import pandas as pd
import numpy as np
from kmodes.kprototypes import KPrototypes
from sklearn.preprocessing import StandardScaler

# ── sample data ─────────────────────────────────────────────────────────────
df = pd.DataFrame({
    "age":                [25, 34, 45, 23, 52, 31, 44, 29, 38, 60],
    "total_spend":        [120, 340, 890, 95, 1200, 210, 760, 180, 430, 1050],
    "subscription_tier":  ["low","medium","high","low","high","medium","high","low","medium","high"],
    "acquisition_channel":["organic","paid","referral","organic","paid","referral","paid","organic","referral","paid"],
})

# ── config ───────────────────────────────────────────────────────────────────
N_CLUSTERS = 3
NUMERIC_COLS = ["age", "total_spend"]
CAT_COLS    = ["subscription_tier", "acquisition_channel"]

# ── preprocessing ────────────────────────────────────────────────────────────
# Scale numerics so they don't dominate the distance calculation.
# KPrototypes still controls the numeric/categorical balance via `gamma`.
scaler = StandardScaler()
df_model = df.copy()
df_model[NUMERIC_COLS] = scaler.fit_transform(df[NUMERIC_COLS])

# KPrototypes needs a numpy array; categorical columns must be object dtype.
X = df_model.to_numpy()
cat_indices = [df_model.columns.get_loc(c) for c in CAT_COLS]

# ── fit ───────────────────────────────────────────────────────────────────────
kproto = KPrototypes(
    n_clusters=N_CLUSTERS,
    init="Cao",       # better than random for small datasets
    n_init=10,
    random_state=42,
    verbose=0,
)
labels = kproto.fit_predict(X, categorical=cat_indices)

# ── attach labels back to the original dataframe ─────────────────────────────
df["cluster"] = labels
print(df)
print("\nCluster counts:")
print(df["cluster"].value_counts().sort_index())
