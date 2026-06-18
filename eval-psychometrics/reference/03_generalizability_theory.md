# 03 — Generalizability Theory for Evals

G-theory is the **primary reliability tool for the small-N iteration regime** and the right way
to answer the two questions that actually block decisions: *how much of my score movement is real
vs. measurement noise?* and *how many cases / seeds / judges do I need to reliably tell version A
from version B?* It works at small N because it estimates variance components, and it reports its
own uncertainty honestly. Script: `scripts/gtheory_eval.py`.

## The core idea (vs. CTT)

CTT lumps all error into one term: `X = T + E`. G-theory **decomposes** error by source. In an
eval suite the observed score for a (version, case, judge, seed) cell varies because of:

- the **version** (the object of measurement — this is the variance you *want*),
- the **case** (some cases are just harder),
- the **judge/grader** (some graders are stricter),
- the **seed/run** (run-to-run stochasticity),
- and their **interactions** (a version that's strong on routing cases but weak on edge cases is
  a version×case interaction).

The variance you want is `σ²(version)`. Everything else is error. G-theory tells you the size of
each piece, so you learn *where your noise lives* — and noise has different fixes depending on
source (add cases vs. fix the judge vs. add seeds).

## Setup: object of measurement and facets

- **Object of measurement:** usually the **skill version** (you want to dependably rank versions).
  If instead you're auditing the *instrument*, make the **case** the object and versions a facet.
- **Facets:** case, judge, seed, prompt-variant — whatever you crossed or nested.
- **Crossed vs. nested:** if every version is run on every case, version×case is *crossed*. If
  each case is scored by its own judge, judge is *nested* within case. The script asks you to
  declare the design; it changes which variance components exist.
- **Random vs. fixed facets:** a facet is **random** if its levels are a sample from a universe
  you want to generalize to (e.g., your 15 cases stand in for "the kind of cases users will hit")
  and **fixed** if you only care about exactly these levels (e.g., these three specific judges and
  no others). Random facets contribute to error; fixing a facet removes its main effect from the
  error term (and shrinks Δ error). Default to **random** for cases and seeds — you do want to
  generalize beyond the specific ones you sampled.

## Two coefficients — use the right one

- **Generalizability coefficient Eρ²** (relative decisions): proportion of variance due to the
  object, using only *relative* error δ (interactions with the object). Use when you care about
  **ranking** versions against each other ("is B better than A?"). Analogue of reliability /
  Cronbach's α (a single-facet G-study reduces to α).
- **Dependability coefficient Φ** (absolute decisions): uses *absolute* error Δ, which also
  includes main effects of facets. Use when the score has a **standalone threshold** ("did the
  version clear 80%?"). Φ ≤ Eρ² always, because Δ ≥ δ.

Pick based on the decision. Promoting the better of two versions → Eρ². Shipping iff ≥ a bar → Φ.
Rule of thumb: Eρ²/Φ ≥ 0.8 is "dependable enough to decide on"; below ~0.5 your eval can't
reliably support the decision you're asking it to.

## The D-study — how to size the suite (the actionable part)

The G-study gives you variance components from your *current* design. A **D-study** uses those
components to project Eρ²/Φ under *hypothetical* designs: more cases, more seeds, more judges.
Because facet error variance enters the coefficient divided by the number of levels, the D-study
answers "what's the cheapest way to hit Eρ² = 0.8?"

The classic and recurring finding — which holds for evals — is that **adding cases (items) buys
far more reliability than adding judges/raters.** If version×case interaction dominates your
error, doubling cases helps a lot and adding a second judge barely moves the needle. If
seed/run variance dominates, add seeds. **The D-study tells you which lever to pull instead of
guessing.** Typical output:

```
Current design (15 cases × 1 judge × 3 seeds):  Eρ² = 0.62   <- can't reliably rank versions
Project: 30 cases × 1 judge × 3 seeds:          Eρ² = 0.78
Project: 30 cases × 1 judge × 5 seeds:          Eρ² = 0.81   <- cheapest path over 0.80
Project: 15 cases × 2 judges × 3 seeds:         Eρ² = 0.64   <- second judge barely helps
```

That table is the deliverable. It converts "my eval feels noisy" into "run 30 cases × 5 seeds and
the second judge isn't worth it."

## How it's estimated (small-N friendly)

For balanced crossed designs the variance components come from **expected mean squares (EMS)** —
closed-form from an ANOVA decomposition, no iterative fitting, no large-N requirement. The script
uses this for balanced designs. For unbalanced/nested designs, fit a **linear mixed model** with
random effects for each facet (hand off to the multilevel-modeling skill; `lme4`/`statsmodels`
random-effects variances are the components). Negative variance estimates can occur at small N —
the script floors them at 0 and warns, which is the standard practical fix.

Caveat to state honestly: at small N the variance components themselves have wide confidence
intervals. The script bootstraps them. Treat the D-study as a planning guide with uncertainty, not
a precise oracle — but it is still far better than sizing your suite by feel.

## When to reach for IRT instead

G-theory treats items as exchangeable and gives you *suite-level* reliability and sizing. If you
need *per-item* difficulty/discrimination on a latent scale, or item *selection*, that's IRT
(`04_irt_for_evals.md`) — but only in the model-bank regime. In small-N iteration, G-theory for
reliability + CTT for per-item trimming is the right pairing; IRT adds little you can trust.
