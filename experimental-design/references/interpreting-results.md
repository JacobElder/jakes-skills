# Interpreting Results

Design discipline doesn't stop when the data arrives — the same principles
govern what a result is allowed to mean. This file is for the after-the-fact
questions: "is this real?", "it's significant, do we ship?", "the test was flat,
does that mean no effect?"

## Table of contents
- Intervals over verdicts
- Statistical vs. practical significance
- What a null result does and doesn't license
- Inflated effects in small studies (Type M / Type S)
- Sanity checks before you trust a headline number
- Bayesian vs. frequentist: how each frames the decision

## Intervals over verdicts

A p-value answers one narrow question: how surprising is this data if the true
effect were zero? It does not tell you how big the effect is or how precisely you
measured it. The confidence interval does — report it. "+2.1% (95% CI: +0.3% to
+3.9%)" is informative; "p = 0.03" alone hides whether the plausible effect runs
from trivial to enormous. A wide interval that happens to exclude zero is a weak
result dressed as a win.

Interpretation caveat: a 95% confidence interval does not mean "95% probability
the true effect is in here" — that's the Bayesian credible interval's claim. The
frequentist CI means the procedure captures the truth 95% of the time across
hypothetical repetitions. The distinction rarely changes the decision, but don't
state the Bayesian interpretation of a frequentist interval.

## Statistical vs. practical significance

With large samples, effects far too small to matter clear p < 0.05 routinely.
The right comparison is not the estimate vs. zero but the estimate vs. the
**MDE that justified the test** — the smallest effect that would change the
decision. If a significant result sits below that threshold, the honest read is
"real but not worth acting on." Conversely, a non-significant estimate larger
than the MDE means the test was underpowered, not that the effect is absent.

## What a null result does and doesn't license

"Not statistically significant" almost never means "no effect." It means the
data didn't rule out zero — which is also true when the study was underpowered,
when variance was higher than planned, or when attrition ate the sample. Before
calling something a null:
- Check the achieved power / the width of the CI. A CI from −5% to +6% is
  uninformative, not evidence of no effect.
- If you genuinely need to demonstrate *equivalence* (that the effect is
  negligibly small), use an equivalence/non-inferiority test against a margin —
  a plain two-sided test can never confirm the null.

## Inflated effects in small studies (Type M / Type S)

When power is low, the significant results that survive are a biased sample:
only the larger sample-effects cross the threshold, so observed effects
overstate the truth (Type M, magnitude error), and at very low power the sign
can even be wrong (Type S). A surprisingly large effect from a small or short
study should be *discounted*, not celebrated, and ideally replicated at adequate
power before you act on the magnitude.

## Sanity checks before you trust a headline number

- **Sample ratio mismatch (SRM)** — re-confirm the allocation is what you
  assigned; a broken split poisons every downstream number.
- **Guardrails** — a primary-metric win that quietly regressed latency, revenue,
  or retention is usually not shippable.
- **Segment fishing** — "it worked for new users on Android in Brazil" found
  after the fact is a multiple-comparisons artifact until pre-registered and
  replicated.
- **Novelty** — an early effect on a short test may be reaction to change, not
  the steady state.

## Bayesian vs. frequentist: how each frames the decision

The two frameworks answer different questions, and conflating their vocabularies
is a common error. Pick one in the analysis plan (see SKILL.md step 6).

**Frequentist.** Fixes the design, controls long-run error rates (α, power), and
reports a p-value and confidence interval against a null hypothesis. Strengths:
well-understood error guarantees, no prior to argue about, the lingua franca of
most scientific reporting. Costs: the peeking penalty is real (validity depends
on the fixed stopping rule), and p-values are routinely misinterpreted as the
probability the hypothesis is true.

**Bayesian.** Combines a prior with the data into a posterior distribution over
the effect, and reports directly decision-relevant quantities: the probability
treatment beats control, a credible interval ("95% probability the effect is in
here," the interpretation people *want*), or the expected loss from shipping.
Strengths: the posterior is valid to read at any time (continuous monitoring
without a peeking correction), and the output maps cleanly onto a ship decision
via an explicit rule. Costs: results depend on the prior (which must be chosen
and defended), and the decision threshold must be set in advance — otherwise the
flexibility just relocates the garden of forking paths. Many modern
experimentation platforms (and most "always-on" experiment dashboards) are
Bayesian under the hood.

Neither is inherently more rigorous. Frequentist suits confirmatory, fixed-N
tests with a need for accepted error guarantees; Bayesian suits continuous
monitoring and decisions framed as "ship if probably better by enough." What's
not acceptable is mixing them after the fact — running a frequentist fixed-N
plan, peeking daily, and then reaching for a Bayesian justification when the
p-value cooperates.
