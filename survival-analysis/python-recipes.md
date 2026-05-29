# Python recipes for survival analysis

A consolidated reference for Python. For deep coverage, see method-specific files. This is the "what package, what class, what argument" lookup. Note: several specialized methods are R-only or much better-supported in R; those gaps are flagged in the relevant places.

## Package landscape

| Package | What it's for | Notes |
|---|---|---|
| **lifelines** | KM/NA/AJ fitters, Cox, parametric (Weibull, log-normal, etc.), time-varying Cox | Cleanest API, great for getting started. |
| **scikit-survival** (`sksurv`) | scikit-learn-compatible Cox, RSF, GB survival, kernel SVM | The right choice for ML pipelines. |
| **pycox** | DeepSurv, DeepHit, PCHazard (neural network survival) | Requires PyTorch. |
| **statsmodels** | Basic KM, Cox, log-rank | Limited; prefer lifelines unless you need stats-style API. |
| **scikit-learn** | Cross-validation, pipelines, hyperparameter search | Used in conjunction with sksurv. |

For these things, **use R instead**:
- Royston-Parmar flexible parametric splines
- Fine-Gray subdistribution model (no clean Python implementation)
- Gray's test for competing risks
- Multi-state regression (`mstate`)
- Joint frailty models (`frailtypack`)
- Semi-parametric interval-censored regression
- MaxCombo for non-PH

If you need these in a Python project, the practical option is `rpy2` to call R, or do that piece in R and serialize results.

## Data setup

```python
import pandas as pd
import numpy as np

# Standard: one row per subject with 'time' and 'event' columns
# event = 1 if event observed, 0 if censored
df = pd.DataFrame({...})

# sksurv expects a structured array
from sksurv.util import Surv
y = Surv.from_dataframe(event='event', time='time', data=df)
# or
y = Surv.from_arrays(event=df['event'].astype(bool), time=df['time'])

# Time-varying covariates / counting process: one row per (id, interval)
# Columns: id, start, stop, event, plus covariates
```

## Kaplan-Meier and Nelson-Aalen

```python
from lifelines import KaplanMeierFitter, NelsonAalenFitter
from lifelines.plotting import add_at_risk_counts
import matplotlib.pyplot as plt

kmf = KaplanMeierFitter()
kmf.fit(df['time'], event_observed=df['event'], label='All')
kmf.survival_function_
kmf.confidence_interval_survival_function_
kmf.median_survival_time_           # inf if not reached
kmf.survival_function_at_times([180, 365])

# By group with at-risk table
fig, ax = plt.subplots(figsize=(9, 6))
kmfs = []
for grp, sub in df.groupby('group'):
    k = KaplanMeierFitter().fit(sub['time'], sub['event'], label=str(grp))
    k.plot_survival_function(ax=ax)
    kmfs.append(k)
add_at_risk_counts(*kmfs, ax=ax)

# Nelson-Aalen for cumulative hazard
naf = NelsonAalenFitter()
naf.fit(df['time'], event_observed=df['event'])
naf.cumulative_hazard_
naf.plot_cumulative_hazard()
```

## Group comparisons

```python
from lifelines.statistics import logrank_test, multivariate_logrank_test

# Two-group log-rank
r = logrank_test(df_a['time'], df_b['time'],
                 event_observed_A=df_a['event'], event_observed_B=df_b['event'])
print(r.p_value, r.test_statistic)

# Multi-group log-rank
r = multivariate_logrank_test(df['time'], df['group'], df['event'])

# Weighted log-rank (Gehan, Tarone-Ware, Peto, Fleming-Harrington)
r = logrank_test(df_a['time'], df_b['time'],
                 event_observed_A=df_a['event'], event_observed_B=df_b['event'],
                 weightings='fleming-harrington', p=0, q=1)
# weightings options: 'wilcoxon' (Gehan), 'tarone-ware', 'peto', 'fleming-harrington'

# RMST (lifelines basic; for proper CI on difference, prefer R's survRM2 via rpy2)
from lifelines.utils import restricted_mean_survival_time
kmf = KaplanMeierFitter().fit(df['time'], df['event'])
rmst = restricted_mean_survival_time(kmf, t=365)
```

**No native MaxCombo in Python.** Either pre-specify a single FH weighting, run multiple FH tests with manual combination, or call R.

## Aalen-Johansen (competing risks CIFs)

```python
from lifelines import AalenJohansenFitter

# CIF for cause 1
ajf = AalenJohansenFitter(calculate_variance=True)
ajf.fit(df['time'], event_observed=df['status'], event_of_interest=1)
ajf.cumulative_density_
ajf.plot()

# Plot all causes
fig, ax = plt.subplots()
for cause in [1, 2]:
    AalenJohansenFitter().fit(df['time'], df['status'],
                               event_of_interest=cause).plot(ax=ax, label=f'cause {cause}')
```

## Cox proportional hazards

```python
from lifelines import CoxPHFitter

cph = CoxPHFitter(penalizer=0.0, l1_ratio=0.0)
cph.fit(df, duration_col='time', event_col='event',
        formula='age + sex + ph_ecog + C(treatment)',
        robust=False)
cph.print_summary()

# Access pieces
cph.params_              # log HRs
cph.hazard_ratios_       # exp(params_)
cph.confidence_intervals_
cph.concordance_index_
cph.AIC_partial_

# Predictions
cph.predict_partial_hazard(df.iloc[:5])             # exp(x'beta)
cph.predict_survival_function(df.iloc[:5])          # full S(t)
cph.predict_survival_function(df.iloc[:5], times=[180, 365, 730])
cph.predict_median(df.iloc[:5])
cph.predict_cumulative_hazard(df.iloc[:5])

# Stratified Cox
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event',
        strata=['institution'], formula='age + sex')

# Cluster-robust SEs (without explicit frailty)
cph.fit(df, duration_col='time', event_col='event',
        formula='age + sex', cluster_col='hospital_id', robust=True)

# Diagnostics
cph.check_assumptions(df, p_value_threshold=0.05, show_plots=True)
cph.plot()                                          # forest plot of HRs
cph.plot_partial_effects_on_outcome('age', values=[40, 60, 80])

# Schoenfeld residuals manually
sch_res = cph.compute_residuals(df, kind='schoenfeld')

# scikit-survival version
from sksurv.linear_model import CoxPHSurvivalAnalysis
est = CoxPHSurvivalAnalysis(alpha=1e-4)  # tiny ridge for stability
est.fit(X, y)
est.score(X, y)             # concordance index
risk = est.predict(X)        # linear predictor
sf_fns = est.predict_survival_function(X)
ch_fns = est.predict_cumulative_hazard_function(X)
```

## Time-varying covariates

```python
from lifelines import CoxTimeVaryingFitter

# df_long: id, start, stop, event, covariates (covariates constant within interval)
ctv = CoxTimeVaryingFitter()
ctv.fit(df_long, id_col='id', event_col='event',
        start_col='start', stop_col='stop',
        formula='treatment + age + ph_ecog',
        robust=True)
ctv.print_summary()
```

Same fitter handles left-truncated data (entry/exit form) and is the basis for Andersen-Gill recurrent-event models in Python.

## Parametric / AFT

```python
from lifelines import (WeibullFitter, WeibullAFTFitter,
                       LogNormalFitter, LogNormalAFTFitter,
                       LogLogisticFitter, LogLogisticAFTFitter,
                       ExponentialFitter, GeneralizedGammaFitter,
                       GeneralizedGammaRegressionFitter)

# Univariate (no covariates)
wf = WeibullFitter().fit(df['time'], df['event'])
wf.print_summary()
wf.median_survival_time_
wf.survival_function_at_times([180, 365])

# AFT regression
waft = WeibullAFTFitter()
waft.fit(df, duration_col='time', event_col='event',
         formula='age + sex + ph_ecog',
         ancillary='age')        # let scale parameter also depend on age
waft.print_summary()
waft.predict_survival_function(df.iloc[:5])
waft.predict_median(df.iloc[:5])

# Generalized gamma (most flexible parametric in Python)
ggreg = GeneralizedGammaRegressionFitter()
ggreg.fit(df, duration_col='time', event_col='event', formula='age + sex')
```

**No Royston-Parmar in Python.** For flexible parametric with spline-based baseline hazard, use R.

## Interval and left censoring

```python
from lifelines import WeibullFitter, WeibullAFTFitter, KaplanMeierFitter

# Univariate
kmf = KaplanMeierFitter()
kmf.fit_left_censoring(df['time'], event_observed=df['event'])

wf = WeibullFitter()
wf.fit_interval_censoring(lower_bound=df['L'], upper_bound=df['R'])

# Regression
waft = WeibullAFTFitter()
waft.fit_interval_censoring(df, lower_bound_col='L', upper_bound_col='R',
                            formula='age + sex')
```

For non-parametric or semi-parametric interval-censored regression, use R (`icenReg`).

## Competing risks

```python
# CIF (Aalen-Johansen): see above

# Cause-specific Cox: fit separately per cause
from lifelines import CoxPHFitter

df['cause1_event'] = (df['status'] == 1).astype(int)
cph1 = CoxPHFitter().fit(df, duration_col='time', event_col='cause1_event',
                         formula='age + sex + treatment')

df['cause2_event'] = (df['status'] == 2).astype(int)
cph2 = CoxPHFitter().fit(df, duration_col='time', event_col='cause2_event',
                         formula='age + sex + treatment')
```

**No native Fine-Gray in Python.** Options:
1. Call R's `cmprsk::crr` via rpy2.
2. Fit only cause-specific models and clearly label them as such.
3. For prediction, use predicted CIFs from `AalenJohansenFitter` or from a multi-state model.

## Recurrent events

Andersen-Gill via `CoxTimeVaryingFitter` with counting-process data:

```python
from lifelines import CoxTimeVaryingFitter

ctv = CoxTimeVaryingFitter()
ctv.fit(recurrent_df, id_col='id', event_col='event',
        start_col='tstart', stop_col='tstop',
        formula='treatment + age')
ctv.print_summary()
```

**Note**: `CoxTimeVaryingFitter` does not yet implement `robust=True` in lifelines (raises `NotImplementedError` as of 0.30.x). Cluster-robust standard errors for Andersen-Gill are not available in lifelines; use R's `coxph(..., cluster(id))` for that feature.

PWP-TT / PWP-GT / WLW: not natively supported. Restructure data and use stratification via interaction terms, or fit per-event-number models with manual robust SE adjustment. R is much cleaner for this.

## Machine learning

### Random Survival Forest (sksurv)

```python
from sksurv.ensemble import RandomSurvivalForest

rsf = RandomSurvivalForest(n_estimators=500, min_samples_split=10,
                            min_samples_leaf=15, n_jobs=-1, random_state=0)
rsf.fit(X_train, y_train)
rsf.score(X_test, y_test)                         # concordance
surv_fns = rsf.predict_survival_function(X_test)
chf_fns  = rsf.predict_cumulative_hazard_function(X_test)
```

### Gradient Boosting Survival (sksurv)

```python
from sksurv.ensemble import GradientBoostingSurvivalAnalysis, ComponentwiseGradientBoostingSurvivalAnalysis

gbs = GradientBoostingSurvivalAnalysis(n_estimators=300, max_depth=3, learning_rate=0.1,
                                        random_state=0)
gbs.fit(X_train, y_train)
gbs.score(X_test, y_test)
```

### Penalized Cox (sksurv)

```python
from sksurv.linear_model import CoxnetSurvivalAnalysis

est = CoxnetSurvivalAnalysis(l1_ratio=0.9, n_alphas=100, alpha_min_ratio=0.01)
est.fit(X, y)
# CV via sklearn
from sklearn.model_selection import GridSearchCV
gs = GridSearchCV(est, {'alphas': [[a] for a in est.alphas_]}, cv=5)
gs.fit(X, y)
```

### Survival Support Vector Machines

```python
from sksurv.svm import FastSurvivalSVM, FastKernelSurvivalSVM

ssvm = FastSurvivalSVM(alpha=1.0, random_state=0)
ssvm.fit(X_train, y_train)
ssvm.score(X_test, y_test)
```

### Neural network survival (pycox)

```python
import torch
from pycox.models import CoxPH, DeepHitSingle, PCHazard
from pycox.evaluation import EvalSurv

# DeepSurv-style (PH-style with neural network)
# Define a torch.nn.Module net
net = torch.nn.Sequential(
    torch.nn.Linear(input_dim, 64), torch.nn.ReLU(), torch.nn.Dropout(0.1),
    torch.nn.Linear(64, 32), torch.nn.ReLU(), torch.nn.Dropout(0.1),
    torch.nn.Linear(32, 1)
)
model = CoxPH(net, torch.optim.Adam)
log = model.fit(X_train, (durations_train, events_train),
                batch_size=256, epochs=100,
                val_data=(X_val, (durations_val, events_val)))
model.compute_baseline_hazards()
surv = model.predict_surv_df(X_test)

# Evaluation
ev = EvalSurv(surv, durations_test, events_test, censor_surv='km')
ev.concordance_td()
ev.integrated_brier_score(np.linspace(durations_test.min(), durations_test.max(), 100))
```

## Evaluation metrics

```python
# Concordance from a fitted model
cph.concordance_index_                     # lifelines
rsf.score(X_test, y_test)                  # sksurv

# Time-dependent concordance (Antolini)
from sksurv.metrics import concordance_index_ipcw, integrated_brier_score, cumulative_dynamic_auc

# IPCW-weighted concordance
cindex_ipcw = concordance_index_ipcw(y_train, y_test, risk_scores, tau=365)

# Integrated Brier Score
times = np.linspace(30, 365, 50)
ibs = integrated_brier_score(y_train, y_test, surv_probs_at_times, times)
# surv_probs_at_times: (n_test, len(times)) matrix of S(t|x_test)

# Time-dependent AUC
auc, mean_auc = cumulative_dynamic_auc(y_train, y_test, risk_scores, times)

# Lifelines: brier scores
from lifelines.utils import median_survival_times
# For Brier score with proper IPCW, sksurv is cleaner.
```

## Cross-validation pipeline

```python
from sksurv.ensemble import RandomSurvivalForest
from sklearn.model_selection import KFold
import numpy as np

kf = KFold(n_splits=5, shuffle=True, random_state=0)
scores = []
for train_idx, test_idx in kf.split(X):
    X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
    y_tr, y_te = y[train_idx], y[test_idx]
    rsf = RandomSurvivalForest(n_estimators=300, random_state=0).fit(X_tr, y_tr)
    scores.append(rsf.score(X_te, y_te))
print(f"C-index: {np.mean(scores):.3f} ± {np.std(scores):.3f}")

# lifelines built-in
from lifelines.utils import k_fold_cross_validation
scores = k_fold_cross_validation(CoxPHFitter(), df, duration_col='time',
                                  event_col='event', k=5, scoring_method='concordance_index')
```

## scikit-survival pipelines

Because sksurv follows the sklearn API, you can use Pipeline, GridSearchCV, etc.:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sksurv.linear_model import CoxPHSurvivalAnalysis

pipe = Pipeline([
    ('scale', StandardScaler()),
    ('cox',   CoxPHSurvivalAnalysis()),
])
param_grid = {'cox__alpha': [0.001, 0.01, 0.1, 1.0]}
gs = GridSearchCV(pipe, param_grid, cv=5)
gs.fit(X, y)
print(gs.best_params_, gs.best_score_)
```
