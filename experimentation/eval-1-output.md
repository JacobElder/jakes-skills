# Experiment Design: Does the new checkout flow lift purchase completion?

**Causal question.** Among sessions that reach the cart, does the new checkout
flow (vs. the current flow) change the purchase-completion rate over a 2–3 week
window?

**Decision & ethics.** Ship the new flow if it lifts completion enough to
justify the eng/maintenance cost. This is a low-stakes UI change — no consent or
ethics-review concerns beyond normal product practice.

## Design
- **Type:** Between-subjects, parallel 50/50.
- **Unit of randomization:** the **user** (not the session), so a returning
  shopper always sees the same flow — switching flows mid-funnel would both
  confuse users and contaminate the comparison. Hash the user ID into a stable
  bucket.
- **Population/trigger:** only users who reach the cart (the point where the two
  flows diverge). Log the trigger symmetrically so control "would-have-triggered"
  users are comparable.
- No marketplace/social interference here, so individual randomization is valid.

## Metrics
- **Primary (one):** purchase-completion rate among triggered sessions.
- **Guardrails (must not regress):** revenue per session, checkout latency,
  payment-error rate, refund/chargeback rate. A completion lift that tanks
  revenue-per-session (e.g. by nudging cheaper carts) or adds latency is not a
  ship.
- **Secondary (watch, don't decide on):** completion is a near-term proxy;
  keep an eye on downstream returns/refunds as a value check.

## Sample size & duration
The MDE is your call, not a statistical default — what's the smallest lift that
would actually change the decision to ship? At a 3% baseline:

| Decision-relevant lift | Treatment rate | N per arm | ~Traffic at 40k/wk |
|---|---|---|---|
| +0.3pp (≈ +10% rel) | 3.3% | ~53,200 | ~2.7 weeks |
| +0.5pp (≈ +17% rel) | 3.5% | ~19,700 | ~1 week |
| +0.75pp (≈ +25% rel) | 3.75% | ~9,100 | ~0.5 week |

(α = 0.05 two-sided, 80% power; from `power_analysis.py`.)

**Recommendation:** a +10% relative lift is a defensible "worth shipping"
threshold for checkout, so plan for ~53,000/arm. Even though traffic would
supply that in under three weeks, **run at least two full weeks** regardless, to
cover the weekly cycle and let any novelty effect settle — and run in whole-week
multiples so every day-of-week is represented equally.

## Analysis plan
- Two-proportion test on the triggered population, analyzed by assignment (ITT).
- **Fixed duration set in advance — no peeking.** Do not stop the moment it
  crosses p < 0.05; daily checking against a fixed test can push the real
  false-positive rate well above 30%. If you need interim looks, switch to a
  sequential method (group-sequential or always-valid p-values) rather than
  eyeballing the fixed test.
- Frequentist, report the effect with a 95% CI; guardrails as one-sided checks.
- Run an SRM check (observed vs. 50/50) before reading any result.

## Threats & mitigations
- **Novelty effect** — early bump from "new," not steady state → ≥2 weeks, watch
  the daily curve flatten.
- **Weekly seasonality** — whole-week runs only; don't straddle a holiday.
- **SRM / instrumentation** — a broken split or asymmetric trigger logging
  poisons everything → verify allocation and symmetric triggering first.

## Open decisions
1. The MDE — confirm the smallest lift worth shipping for.
2. Whether revenue-per-session is a guardrail or co-primary (it changes the call
   if completion and revenue move in opposite directions).
