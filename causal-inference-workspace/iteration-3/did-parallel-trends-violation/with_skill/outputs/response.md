# No, the +8% DiD estimate is not trustworthy as stated.

The scenario describes a textbook parallel-trends violation, which is the load-bearing assumption of any DiD design. The +8% figure is likely a substantial overestimate of the true effect — and may be entirely an artifact of mean reversion, not evidence that the new pricing page did anything.

---

## Step 1: Name the rung

This is a **rung-2 question** — "what is the causal effect of the new pricing page on conversion?" The user wants to make a rollout decision, which requires knowing P(Y | do(new page)), not P(Y | new page). DiD is a design-based identification strategy for rung-2 questions, but only under its identifying assumption.

---

## Step 2: Sketch the DAG

```
  Market characteristics (U)
     /           \
  Treatment      Pre-treatment trend
  assignment  ->  Post-treatment outcome (Y)
     |
  New pricing page -> Y
```

The key structural fact: **treatment was not randomly assigned**. The 3 treatment markets were already growing 25% faster before rollout. This means there is a back-door path:

```
  New page <- [selection into treatment, correlated with pre-trend] -> Y
```

The "parallel trends" assumption required for DiD to close this back-door path is **directly contradicted by the data**.

---

## Step 3: The parallel trends violation — why it matters

DiD's causal identification rests on one assumption:

> In the absence of treatment, the treated and control groups would have followed the same trajectory.

The pre-period data show the opposite: the 3 treatment markets were growing 25% faster before the rollout. That is a documented, observable non-parallel trend.

The DiD estimator mechanically computes:

```
DiD = (Treatment_post - Treatment_pre) - (Control_post - Control_pre)
```

Now consider what actually happened: **after rollout, all 8 markets converged to similar growth rates**. The most likely explanation is that the DiD estimate is computed on conversion *levels*, not growth rates. If treatment markets were already at a higher conversion level due to their faster pre-period growth, the post-period level comparison still shows treatment markets above control markets — generating a positive DiD estimate. But this positive difference is at least partly (possibly entirely) a legacy of the pre-existing faster growth, not the pricing page.

---

## Step 4: What the convergence pattern tells us about the direction of bias

Two plausible scenarios:

**Scenario A — Mean reversion with positive level overhang.** Treatment markets had faster growth that was unsustainable. Post-treatment, they slow toward the market mean. Control markets, growing more slowly, look stable. DiD sees the treatment markets still ahead in level, and attributes that to the pricing page. The +8% is mostly or entirely mean reversion captured incorrectly.

**Scenario B — The new page genuinely boosted conversion, but in markets that were already ahead, suppressing further divergence.** In this case the true effect might exist but is confounded with selection — treatment markets may have been chosen because they were growing fast (e.g., less risky to pilot there), making it impossible to cleanly separate the page effect from pre-existing momentum.

Under both scenarios, the +8% is likely inflated. Under Scenario A, the true effect could be zero or even negative. Under Scenario B, the effect exists but is estimated on a non-representative set of markets (ATT, not ATE), biased upward by the pre-trend.

---

## Step 5: The most likely trap

**Parallel-trends violation as selection bias.** The 3 treatment markets were not chosen at random — they were selected, and their faster pre-period growth correlates with whatever made them "ready" for the new page. This correlation is a back-door path that DiD cannot close when trends are non-parallel.

The convergence pattern adds a second specific failure mode: **mean reversion masquerading as a treatment effect**. When units are selected into treatment partly because they have unusually high values on a trend variable, regression-to-the-mean will make them look like they "responded" to treatment even if treatment did nothing.

---

## Step 6: Alternative structural interpretations

| What the convergence reflects | Implication for the +8% |
|-------------------------------|--------------------------|
| Mean reversion of the faster-growing treatment markets | +8% is entirely spurious — the page did nothing |
| Treatment markets selected for high-growth and that growth faded | +8% is upward biased; page may have even hurt |
| New page caused convergence by boosting slower-growing markets more | +8% may understate the effect in some markets but the aggregate estimate is still confounded |
| External shock hit treatment markets while the page helped | Cannot separate the two; +8% is a net of opposing forces |

None of these alternatives requires unusual assumptions. All of them are consistent with the data pattern described.

---

## Step 7: What would actually identify the effect

**Before accepting the +8%:**

1. **Pre-trend test.** Plot the monthly conversion trajectory for treatment vs. control markets for the full year before rollout. If the gap was widening, shrinking, or non-parallel in any patterned way, DiD is not identified. The 25% faster growth rate already tells you this test would fail.

2. **Placebo tests.** Run the same DiD analysis using only pre-period data — pick a fake "treatment date" in the middle of the pre-period and check whether you find a spurious effect on the treatment markets. If yes, the design is picking up pre-existing differences.

3. **Event study / dynamic DiD.** Estimate the DiD coefficient for each period relative to the rollout date. You want to see flat pre-trend coefficients (near zero), then a jump at the rollout date. If coefficients are already non-zero in the pre-period and trending upward, parallel trends is violated.

**Better identification strategies for this setting:**

- **Synthetic control.** For each of the 3 treatment markets, construct a weighted combination of the 5 control markets that best matches the treatment market's specific pre-treatment trajectory. Use that synthetic market as the counterfactual. This is more honest than DiD precisely because it does not assume parallel trends — it explicitly matches pre-period trends before extrapolating. With only 5 control markets, precision will be limited, but it is the structurally correct tool.

- **DiD with market-specific linear time trends.** Extend the DiD specification to include a market-specific linear trend term. The effect is then identified from deviations from each market's own extrapolated trend, not from a shared-trend assumption. This is a stronger assumption than synthetic control but more tractable with limited data.

- **Interrupted time series (ITS).** For each treatment market, model the conversion trajectory over time and test whether there is a level shift or slope change at the rollout date, controlling for the pre-existing within-market trend. This is market-by-market and does not require a control group assumption.

- **Randomized expansion.** If you can still control which markets get the page next, randomize the remaining expansion. Compare newly randomized markets head-to-head. This generates clean identification going forward and avoids the current design's problems entirely.

---

## Step 8: Honest summary of what you can and cannot conclude

| Claim | Verdict |
|-------|---------|
| The new pricing page had some positive effect | Plausible but unestablished |
| The effect is specifically +8% | Almost certainly wrong; this number is contaminated by pre-trend differences and likely mean reversion |
| The estimate is reliable enough to use for a full rollout decision | No |
| The design was fundamentally flawed | Yes — parallel trends was violated before the analysis began |

---

## Recommendation

Do not use the +8% as a decision input for a full rollout. The pre-period trend difference is dispositive: DiD required parallel trends, the data show a 25% growth differential, and the post-period convergence is exactly the pattern expected from mean reversion regardless of any page effect.

The appropriate next step is either (a) re-run the analysis with synthetic control or a market-trend-adjusted DiD specification that explicitly models the pre-existing trend, or (b) run a randomized expansion to the remaining 5 markets and collect clean data. The current estimate's confidence interval should be treated as meaningless until the identification problem is addressed.

If the business needs a directional read right now: the fact that treatment markets did not diverge further from control markets after rollout — they converged — is actually mild evidence against a large positive effect. A pricing page that genuinely lifted conversion by +8% in markets already outperforming controls should have widened the gap, not closed it. That convergence is a warning sign, not a validation.
