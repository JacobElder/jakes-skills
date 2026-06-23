# Estimating Entropy, MI, and Divergence from Finite Samples

This is the file that earns the skill. The formulas are easy; **getting an honest number
out of finite data is not**, and the base model's default — plug in empirical frequencies —
is biased in a direction that systematically manufactures false conclusions. Read this
before quoting any entropy/MI/KL computed from data.

Contents: [The bias, precisely](#the-bias-precisely) · [Discrete entropy estimators](#discrete-entropy-estimators) · [Discrete MI / divergence](#discrete-mi-and-divergence) · [Continuous: k-NN (KSG)](#continuous-data-knn-ksg) · [Neural estimators](#neural-estimators-mine-infonce) · [Uncertainty](#always-attach-uncertainty) · [Decision guide](#decision-guide)

## The bias, precisely

Let `K` = number of categories, `N` = sample size, `Ĥ` = plug-in (MLE) entropy in nats.

```
E[Ĥ_plugin] ≈ H − (K − 1) / (2N)          → entropy biased DOWNWARD
E[Î_plugin] ≈ I + (K_X − 1)(K_Y − 1)/(2N) → MI biased UPWARD
```

Both biases scale with the number of categories and shrink only as `1/N`. The consequences
are not academic:
- **Undersampling fakes structure.** When `N` is not ≫ `K` (think: word distributions, joint
  tables of two categorical features, neural population states), plug-in MI can be almost
  entirely bias. Two independent variables will show "significant" MI.
- **It's worst where you're most tempted.** High-cardinality variables — IDs, fine-grained
  categories, many bins — have the largest `K`, so the largest bias. These are exactly the
  features naive MI ranking and decision-tree information gain over-select.
- **The variance is the *other* half.** Even bias-corrected estimators are noisy at small `N`;
  a point estimate without an interval is half an answer.

Rule of thumb: if `N / K` is not at least ~10–30 *per occupied cell*, you are in the
undersampled regime and must use a dedicated estimator (NSB/Chao–Shen/KSG), not a correction
to plug-in.

## Discrete entropy estimators

In rough order of "reach for it":

- **Miller–Madow** `Ĥ_MM = Ĥ_plugin + (K̂−1)/(2N)` (nats; `K̂` = # observed nonzero categories).
  The minimum acceptable default — it removes the leading bias term for free. Still
  underestimates when many categories are unobserved (it can't correct for cells you never saw).
- **NSB (Nemenman–Shafee–Bialek)** — Bayesian, mixture of Dirichlet priors chosen so the
  *implied prior over entropy* is nearly flat. The right tool in the **deeply undersampled**
  regime (`N ≲ K`), e.g. neural spike-train and language work. Use the `ndd` package. Gives a
  posterior, hence an interval for free.
- **Chao–Shen** — coverage-adjusted (Good–Turing) estimator that accounts for unseen species;
  strong when there's a long tail of rare categories. Common in ecology/diversity.
- **Grassberger** — another low-bias correction, popular in physics.
- **Bayesian / add-α (Dirichlet–multinomial)** — pseudocounts then plug in; simple and
  bounded, but the answer depends on `α`; report sensitivity. Fine for well-sampled data.

Don't hand-roll NSB or Chao–Shen; use `ndd`, `dit`, or domain packages. Do compute Miller–Madow
yourself (`scripts/entropy_mi_estimators.py`) — it's one line and you should never ship plug-in.

## Discrete MI and divergence

- Compute MI as `Ĥ(X)+Ĥ(Y)−Ĥ(X,Y)` **with each entropy bias-corrected**, or use a dedicated
  MI estimator. Correcting the marginals but not the joint reintroduces bias — correct all three.
- **Always run a permutation null** (shuffle `Y` relative to `X`, recompute MI ≥ 200×). Report
  the value, the shuffled mean (≈ the bias floor), and a p-value or the gap in σ units. A MI
  that isn't clearly above its shuffle distribution is not evidence of dependence, no matter how
  positive it is. This single habit prevents most false MI claims.
- For KL/cross-entropy between estimated discrete distributions, **smooth `q`** (add-α /
  Dirichlet) to avoid `log 0`; note the answer's sensitivity to the smoothing constant when
  categories are rare.

## Continuous data: k-NN (KSG)

Do **not** estimate continuous entropy/MI by histogramming — the answer depends on bin width
and the bias is severe in >1 dimension. Use **k-nearest-neighbor** estimators:
- **Kozachenko–Leonenko** for differential entropy.
- **KSG (Kraskov–Stögbauer–Grassberger)** for MI — the field standard, implemented and
  validated in `scripts/entropy_mi_estimators.py` against the bivariate-Gaussian closed form.
  `sklearn.feature_selection.mutual_info_*` use a KSG variant; `npeet` is a convenient package.

KSG practical notes:
- `k` (neighbors) trades bias vs variance: small `k` (≈3–5) lower bias/higher variance.
  Report sensitivity to `k`; if the estimate swings wildly with `k`, distrust it.
- It assumes a continuous density. **Ties / discreteness break it** — repeated values make
  k-NN distances zero and the estimate explodes. Add tiny jitter to genuinely continuous data
  with measurement ties; for truly mixed discrete–continuous variables use the **Ross (2014)**
  or Gao et al. mixed estimator instead of pretending it's continuous.
- It can return small **negative** values from noise — clamp at 0 and treat as "indistinguishable
  from independent," not as a real quantity.
- High dimension is hard (curse of dimensionality in the neighbor counts); KSG degrades as the
  joint dimension grows. Above a handful of dimensions, prefer a neural estimator and heavy skepticism.

## Neural estimators (MINE, InfoNCE)

For high-dimensional MI (representations, images), variational lower bounds estimated with a
neural net:
- **MINE** (Donsker–Varadhan bound) — high variance, biased gradients, can be unstable; treat
  its absolute values cautiously.
- **InfoNCE** (the contrastive bound behind CPC/SimCLR) — **lower-bounded by `log(batch size)`**.
  This is the crucial caveat: you literally cannot measure MI above `log K` with a `K`-sample
  contrastive estimate, so reported "MI" from InfoNCE is often just reporting the batch size.
  Use these to *optimize* representations, not to *report* an MI magnitude.
- General warning (McAllester–Stratos): any distribution-free high-confidence MI **lower bound**
  needs sample size exponential in the MI. Large MI cannot be certified from limited data.

## Always attach uncertainty

- **Bootstrap** the estimator (resample rows, recompute) for a CI — works for any estimator.
- **Permutation/shuffle** gives the null (bias floor) for MI/divergence specifically.
- For NSB and Bayesian estimators, the posterior gives the interval directly.
- Present entropy/MI as *estimate ± interval, with the null*, the way you'd never report a
  regression coefficient without a standard error. A bare number invites overinterpretation.

## Decision guide

| Situation                                                | Estimator                                  |
|----------------------------------------------------------|--------------------------------------------|
| Discrete, well-sampled (`N ≫ K`)                          | Miller–Madow (+ bootstrap CI)              |
| Discrete, undersampled (`N ≲ K`, long tail)               | NSB, or Chao–Shen for diversity/ecology    |
| Discrete MI, any sample size                              | bias-corrected H's **+ permutation null**  |
| Continuous, low-dim                                       | KSG (k≈3–7), report k-sensitivity          |
| Mixed discrete/continuous                                 | Ross/Gao mixed estimator (not raw KSG)     |
| High-dim representations (optimize, don't report)         | InfoNCE/MINE, with the `log K` caveat      |
| Any reported figure                                       | + bootstrap interval; never a bare number  |
