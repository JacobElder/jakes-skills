# HMMs for Time Series and Finance

The application area where HMMs are most overhyped and most misused — but also where they can genuinely deliver value when applied carefully. This reference is about doing it carefully.

## When this is the relevant reference

- Regime detection ("the market is in a high-volatility state")
- Macroeconomic state-switching (Hamilton-style models)
- Activity recognition from sensor data (accelerometer → walking/sitting/running)
- Anomaly detection in system logs, traffic, or sensor streams
- Sleep stage classification from EEG
- Customer-journey segmentation
- Any case where the question is "the system was probably in mode X during this window"

## Honest warnings up front

State these directly when the user asks about price prediction:

1. **HMMs do not reliably predict stock prices.** Decades of literature have tried. The few claims of "predictive HMM trading systems" mostly don't survive out-of-sample testing or transaction costs. Manage expectations.

2. **What HMMs *can* do in finance**: identify regimes in *realized* volatility, correlation, or return distributions; flag regime changes ex-post or with short delay; segment historical data into similar-looking periods for further analysis; provide interpretable risk-management overlays. These are real uses. "Tell me tomorrow's return" is not.

3. **In-sample fit looks impressive; out-of-sample is much weaker.** Always evaluate on held-out periods. A 3-state HMM fit to S&P 500 returns 1990-2024 will produce a beautiful-looking decomposition; whether the regimes were detectable in real-time, with information available only up to that date, is a different question. Use filtering (forward only, no smoothing) for backtests, not smoothed γ_t.

4. **Beware look-ahead bias.** It's very easy to use future information when you don't mean to (e.g., fitting on the whole series, then "predicting" in-sample). For realistic evaluation: walk-forward fitting, where the model at time t was fit on data through t only.

## The canonical setup: Gaussian HMM on returns

A common setup:
- Observation: daily log returns of an asset/index.
- Emission: Gaussian per state (mean μ_i, variance σ_i²).
- States: 2 or 3 — typically "calm/bullish" (small positive mean, low vol), "normal," and "crisis/bear" (negative mean, high vol).

```python
from hmmlearn import hmm
import numpy as np

# returns: shape (T, 1), log returns
model = hmm.GaussianHMM(n_components=3, covariance_type="full",
                        n_iter=1000, tol=1e-4, random_state=42)
model.fit(returns)

# Inspect what the states represent
print("State means:", model.means_.flatten())
print("State variances:", np.diagonal(model.covars_, axis1=1, axis2=2).flatten())
print("Transition matrix:\n", model.transmat_)

# Expected duration in each state (geometric assumption):
# E[duration in state i] = 1 / (1 - A[i][i])
expected_durations = 1 / (1 - np.diag(model.transmat_))
print("Expected durations (days):", expected_durations)

# Posterior probabilities (smoothed, uses future data)
posteriors = model.predict_proba(returns)

# Filtered probabilities (online — only uses past data)
# hmmlearn doesn't expose this directly; compute via forward only:
log_alpha = model._compute_log_likelihood(returns)  # log b
# ... full filtering recipe below
```

A note on filtered vs smoothed: `predict_proba` returns γ_t which uses the entire sequence (uses future data). For realistic real-time use, you want filtered probabilities — forward pass only. hmmlearn's API forces a workaround; consider `dynamax` if you need filtering as a first-class operation.

## Hamilton's regime-switching model

James Hamilton's 1989 *Econometrica* paper is the foundational reference for regime-switching in macro/finance. The original model is a 2-state HMM where GDP growth has different means in expansion vs. recession. Modern extensions: state-dependent variances, multivariate observations, time-varying transition probabilities.

In Python: `hmmlearn` works fine for the basic version. For more complex regime-switching (e.g., Markov-switching VAR, time-varying transitions), `statsmodels.tsa.regime_switching.MarkovRegression` and `MarkovAutoregression` are the standard tools. They use MLE with numerical optimization rather than EM but the conceptual structure is identical.

```python
import statsmodels.api as sm

# 2-state Markov-switching mean and variance on returns
mod = sm.tsa.MarkovRegression(returns, k_regimes=2, switching_variance=True)
res = mod.fit()
print(res.summary())
# Smoothed probabilities of being in regime 0/1 at each t
res.smoothed_marginal_probabilities.plot()
```

## Anomaly detection via likelihood scoring

A genuinely useful application: train an HMM on "normal" sequences, then score new sequences. Low likelihood under the model = anomalous.

Workflow:
1. Collect sequences known to be normal (system logs from healthy operation, normal user sessions, etc.).
2. Fit an HMM (multiple restarts, choose K via held-out likelihood on normal data).
3. For new sequences, compute log P(X | model). 
4. Threshold by percentile of log-likelihood on a held-out normal set (e.g., flag sequences below the 1st percentile).

Per-position version: compute γ_t and flag positions where no state explains the observation well, or where the posterior is uniformly low across states.

This is the standard "one-class" anomaly detection setup adapted to sequences. Works well when "normal" is structured enough to be modeled compactly; fails when normal is too heterogeneous or when anomalies happen to mimic legitimate rare states.

## Activity recognition

Triaxial accelerometer at the wrist or hip. Observations are short feature windows (mean, variance, FFT coefficients over 1-second windows). States are activities (sitting, walking, running, climbing stairs). With labeled training data, fit a supervised HMM (just count transitions and fit emission models per state); without labels, fit unsupervised and interpret.

The "Plotnik" or "TIHM" approach: hierarchical HMMs where the top level transitions slowly between activity contexts (working / exercising / sleeping) and the bottom level models within-context behavior. Standard `hmmlearn` does flat HMMs; for hierarchical use `pomegranate` or build the architecture as a flat HMM with structured transition matrix.

## Specific time-series pitfalls

1. **Non-stationarity.** A 3-state model fit to 1990-2024 financial data is fitting an average over very different periods (2008 crisis, COVID, etc.). The "normal" state from 1995 is not the "normal" state from 2024. Either model this explicitly (more states, time-varying transitions) or accept that the model is a coarse summary.

2. **The geometric duration trap.** Standard HMMs assume the duration in a state is geometrically distributed: most "regimes" are 1 timestep long, with an exponential tail. Real economic regimes don't behave that way (recessions cluster, last months to years). Symptoms: fitted models that constantly flip between states. Two fixes: (a) use an HSMM with explicit duration distributions; (b) use coarser time aggregation (weekly/monthly returns instead of daily) so the geometric assumption is less violated.

3. **Choosing K with financial data.** Held-out likelihood often keeps going up with K because more states means more flexibility to capture fat tails and skewness. Information criteria (BIC) over-penalize. Best practice: pick K based on domain interpretability ("I can describe 3 regimes meaningfully; I cannot describe 7") rather than chasing the best likelihood.

4. **Conditioning on volatility.** If you fit a Gaussian HMM to returns, the model usually discovers volatility regimes (not return regimes), because variance differences across regimes dominate the likelihood. If you actually want return regimes, work with risk-adjusted or standardized returns; or use a t-distribution emission to absorb the volatility differences.

5. **Multivariate observations.** Multiple correlated time series (e.g., several asset returns) → use full or diagonal covariance Gaussian emissions. Full covariance grows as K*D²; for D > 5 or so you'll overfit without lots of data. Consider factor models inside each state or a sparser parameterization.

6. **Filtering vs. smoothing for real-time use.** Reiterating: `predict_proba` uses the whole sequence. For real-time signals, you need filtered (forward-only) probabilities. The lag between an actual regime change and the model detecting it is typically days to weeks; report this honestly when delivering a real-time regime classifier.

7. **Look-ahead in walk-forward.** When backtesting a trading system that uses HMM signals, the HMM should be re-fit on data through time t only at each point — not fit once on the full sample and then "applied" to the past. The full-sample fit incorporates information from the future. This single mistake explains a lot of "great backtest, terrible live performance."

## Comparison with alternatives for time-series

| Method | When better than HMM |
|---|---|
| Bayesian change-point detection (e.g., `bayesloop`, `ruptures`) | When you have a small number of distinct regime changes, not recurring states |
| Kalman filter / linear-Gaussian state space | When the latent state is continuous (price level, smoothed trend), not discrete modes |
| GARCH and family | For pure volatility modeling without explicit regimes |
| Particle filter | When emissions are nonlinear or non-Gaussian and you need full posterior |
| RNN / LSTM / Transformer | When you have lots of data, only care about prediction, and don't need interpretability |
| Plain rolling statistics | When you don't really need a model — sometimes a 20-day rolling vol is the right tool |

The general rule: HMMs win when interpretability and a small, discrete state space matter, and when data is moderate (not huge). Neural sequence models win when data is huge and only prediction matters.

## Recommended reading

- Hamilton (1989), "A new approach to the economic analysis of nonstationary time series and the business cycle," *Econometrica* 57(2). Foundation paper for regime-switching in econ.
- Hamilton (1994), *Time Series Analysis*, Chapter 22. Textbook treatment of regime-switching.
- Kim & Nelson (1999), *State-Space Models with Regime Switching*. The book for advanced regime-switching econometrics.
- Rabiner (1989), still useful — the algorithms are domain-independent.
