# Sample size for the onboarding-screen test

For a 2-percentage-point absolute lift on a 22% baseline (so 22% → 24%):

**~6,950 users per arm — about 13,900 total.**

From `power_analysis.py --solve n --type proportion --baseline 0.22 --mde 0.02`.

Assumptions: α = 0.05, two-sided; 80% power; the 2pp is treated as **absolute**
(if you actually meant a 2% *relative* lift — 22% → 22.44% — you'd need far more,
roughly 1.7M per arm, so worth confirming which you meant).

To turn that into a runtime, divide ~13,900 by your daily eligible users reaching
the onboarding screen (split across the two arms), and round up to whole weeks so
you cover the weekly cycle. Lock the sample size in advance and don't stop early
the first time it crosses significance.
