# Power & Sample Size

The conceptual companion to `scripts/power_analysis.py`. Compute with the
script; reason with this.

## Table of contents
- The four interlocked quantities
- Choosing the MDE (the hard part)
- Where variance comes from, and reducing it
- Ratio metrics and the delta method
- Cluster designs and the design effect
- Multiple comparisons
- From N to runtime
- Underpowered is worse than it looks

## The four interlocked quantities

Power analysis is one equation relating four things; fix any three and the
fourth is determined:

- **Sample size (N)** — units per arm.
- **MDE (minimum detectable effect)** — smallest true effect you want a good
  chance of detecting.
- **Significance level (α)** — false-positive rate, the chance of declaring an
  effect when none exists. Usually 0.05.
- **Power (1 − β)** — true-positive rate, the chance of detecting an effect that
  is really there at the MDE. Usually 0.80; raise to 0.90+ when a miss is
  costly.

Outcome variance (or baseline rate for proportions) enters as a fifth input you
must supply from data. More variance → larger N for the same MDE.

The core intuition: required N scales roughly with **variance / MDE²**. Halving
the MDE quadruples the sample. This is why the MDE conversation dominates
feasibility.

## Choosing the MDE (the hard part)

The MDE is a decision, not a statistic. It is *not* "the effect I expect" and
*not* "the effect that would be significant" — it's **the smallest effect large
enough to change what you'd do.** Anchor it to consequences:

- What lift would justify the cost/risk of shipping? Power for that.
- If even a tiny effect would change the decision, you've signed up for a large
  study; confront that now, not after an underpowered null.
- Powering for an effect far larger than plausible guarantees a null you can't
  interpret ("no effect" vs. "underpowered" are indistinguishable).

When users hand you an MDE that's implausibly large, push back — it's the most
common way a test is doomed before launch.

## Where variance comes from, and reducing it

For a continuous metric, variance is the outcome's spread; for a proportion it's
p(1−p), maximized at p = 0.5. You can attack variance by design instead of
buying more units:

- **CUPED / covariate adjustment** — regress out a pre-period covariate
  correlated with the outcome; 30–50% variance reduction is common (see
  online-experiments.md). Equivalent to a large free increase in N.
- **Blocking / stratified randomization** — remove nuisance variance from a
  known strong predictor before it reaches the comparison.
- **Within-subject design** — removes between-unit variance entirely when the
  treatment allows it.
- **Winsorizing / capping** heavy-tailed metrics (revenue, time-on-site) so a
  few outliers don't dominate the variance.

Reducing variance is almost always cheaper than increasing N; reach for it first
when a study looks infeasible.

## Ratio metrics and the delta method

A surprising number of product metrics are **ratios where the denominator is
itself random and the analysis unit differs from the measurement unit**:
clicks-per-pageview, revenue-per-session, items-per-order — when randomization
is by *user* but the metric is computed over *sessions* or *pageviews*. You
cannot treat these as a simple mean or proportion: the standard error formula
assumes independent observations at the analysis unit, but a user contributes
many correlated sessions, so the naive variance is too small and the test
rejects far too often (inflated false positives).

The fix is the **delta method**: a ratio R = X̄/Ȳ has approximate variance

```
Var(R) ≈ (1/Ȳ²)·Var(X) + (X̄²/Ȳ⁴)·Var(Y) − 2(X̄/Ȳ³)·Cov(X, Y)
```

computed with X and Y aggregated *to the randomization unit* (per user), which
correctly accounts for the within-user correlation. Bootstrapping by resampling
users is an equivalent, assumption-light alternative. Plug the resulting
variance into the power calculation as the outcome variance — the bundled script
takes a variance/SD directly for the `mean` type, so compute the delta-method
variance first and pass it in, rather than letting the script assume a simple
mean. CUPED composes with this (apply it to the per-user ratio).

The practical tell that you're in this situation: the metric has a denominator
that varies across units, or you hear "per-session" / "per-visit" while
assignment is per-user. Flag it; it's one of the most common silent causes of
false positives in online experiments.

## Cluster designs and the design effect

When you randomize clusters (geos, stores) instead of individuals, outcomes
within a cluster are correlated (intracluster correlation, **ICC** or ρ). The
effective sample is smaller than the raw count by the **design effect**:

```
DEFF ≈ 1 + (m − 1)·ρ
```

where m is the average cluster size. Multiply your individually-randomized N by
DEFF to get the cluster-design N. Consequences: even a small ρ with large
clusters inflates N enormously, and **number of clusters drives power more than
units per cluster** — prefer many small clusters over few large ones. The script
takes ICC and cluster size and applies this for you.

## Multiple comparisons

Every extra metric, segment, variant, or interim look is another chance at a
false positive. k independent tests at α=0.05 give a family-wise error rate of
1 − 0.95^k (≈ 23% at k=5). Control it by pre-declaring one primary metric and
correcting the rest — Bonferroni (divide α by k; conservative), or
Benjamini-Hochberg (controls false discovery rate; better power with many
tests). The cleanest fix is fewer confirmatory comparisons, declared in advance.

## From N to runtime

Required N per arm is not the answer a practitioner needs — runtime is. Convert:

```
duration ≈ (N_per_arm × num_arms) / (eligible units per day × fraction in experiment × trigger rate)
```

Account for: ramp-up days at low exposure (don't count diluted traffic), the
triggered population (only units that hit the differing code path), weekly
seasonality (run in whole weeks so every day-of-week is represented equally),
and any minimum runtime needed to let novelty effects settle. If the duration
crosses a major seasonal boundary (holiday, back-to-school), either run long
enough to average over it or avoid straddling it.

## Underpowered is worse than it looks

An underpowered study doesn't just risk missing a real effect. Among the
significant results it *does* produce, effect sizes are systematically inflated
(the "winner's curse" / Type-M error) — you'll overstate the effect you
detected, and the sign can even be wrong (Type-S error) when power is very low.
So a noisy, underpowered "win" can be more misleading than a null. If the honest
required N is unreachable, say so and renegotiate the MDE, reduce variance, or
change the design — don't ship an underpowered test and read the tea leaves.
