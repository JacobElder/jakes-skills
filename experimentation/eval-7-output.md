# Sizing the payment-step test from your history

Reading `checkout_history.csv` (63 days / 9 weeks):
- **Baseline conversion ≈ 4.2%** (12,201 conversions / 290,296 sessions).
- **Average traffic ≈ 4,600 sessions/day**, with a clear weekday/weekend swing
  (~5,200 weekday vs ~3,100 weekend), and weekends convert a touch higher.

**Target effect.** You want a 5% *relative* lift, i.e. 4.2% → ~4.41% (about
+0.21pp absolute). Small relative targets on a low base are expensive to detect.

**Sample size.** `power_analysis.py --solve n --type proportion --baseline 0.042
--mde 0.05 --relative` (α = 0.05 two-sided, 80% power) →

**~146,600 per arm, ~293,000 total.**

**Runtime.** At ~4,600 sessions/day split 50/50 across the two arms, you're
accumulating ~4,600 total/day toward that 293,000, so:

**≈ 64 days ≈ 9–10 weeks**, and you should round to whole weeks (10) so the
weekday/weekend cycle is balanced across arms.

**That's a long test — flag it before committing.** Ten weeks is a long time to
hold a payment-step change, and the steady traffic gives little slack. Levers,
roughly in order of payoff:
- **Variance reduction (CUPED).** Regress out each user's pre-period behavior;
  on a metric with decent pre/post correlation this commonly cuts variance
  30–50%, which can roughly halve the runtime for free. Biggest lever here.
- **Reconsider the MDE.** Is 5% relative really the smallest lift worth shipping
  for? If a 10% relative lift (→ 4.62%) is the real decision threshold, the test
  shrinks to a few weeks. Worth an explicit decision.
- **Whole-week runs** regardless, given the visible weekly seasonality — don't
  read a partial week.
- Confirm an SRM check and symmetric trigger logging before trusting results.

One caution: if "conversion" is computed per session but you randomize by user,
treat it as a ratio metric and compute the variance with the delta method (or a
user-level bootstrap) — the simple-proportion number above slightly understates
the needed sample otherwise.
