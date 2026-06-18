# 07 — Small-Sample Playbook

**Read this whenever you have a handful of versions and a few dozen cases — the default
skill-iteration regime.** It explains why the textbook psychometric machinery breaks here and
gives an ordered menu of remedies. The headline: in this regime, *reframe the problem* (G-theory
and CTT, with fixed-item IRT if you need a latent scale) rather than forcing a free IRT fit.

## Why the standard machinery breaks

In eval analysis your response matrix is `takers × items`. The "items" are eval cases (you
usually have plenty). The **"takers" are whatever varies across columns** — skill versions,
prompt variants, model tiers, ablations, seeds. In the iteration loop you typically have
**4–8 takers**. That is the binding constraint, because item parameters are estimated *across
takers*.

Established sample-size needs for stable item parameters:

- **Rasch / 1PL** (difficulty only, discrimination fixed at 1): ~100–200 takers per item is the
  textbook comfort zone; simpler estimators can do "reasonable" at ~100. A crude floor for a
  single item's difficulty to be within ~1 logit is roughly **8 passes and 8 fails** on that item.
- **2PL** (difficulty + free discrimination): commonly cited **~500** takers, with 1000 for
  comfort.
- **3PL** (adds guessing): **~1000+**.

With 6 takers you are 1–2 orders of magnitude short for a *free* 2PL. The model will still
return numbers — that is the danger. Discrimination estimates in particular will be wild, and
the per-version ability estimates will have intervals so wide they can't separate your versions.
**A confident IRT table at N=6 is the tell that something has gone wrong, not that it worked.**

CTT statistics (difficulty, item–rest correlation) don't *break* at small N, but they get noisy:
an item–rest correlation computed across 6 takers has a huge standard error. So small N hurts
everywhere; the question is which tool degrades most gracefully and how to buy back power.

## The menu (apply in roughly this order)

### 1. Expand the taker dimension — the cheapest, highest-leverage fix
Most "I only have 6 takers" situations are self-imposed. Add columns:

- **Run across model tiers.** Haiku / Sonnet / Opus (+ a couple of non-Anthropic models if you
  have them) each become a taker. This is the single best move: it both inflates N *and* spreads
  takers across a real ability range, which is exactly what makes item difficulty and
  discrimination estimable (an item only discriminates if takers differ in ability).
- **Add a no-skill baseline and partial-skill ablations.** Skill-off, SKILL.md-only (no
  references), references-but-no-scripts, etc. These are cheap and informative takers.
- **Add seeds.** Re-run each (version × case) at temperature. Each (version, seed) is an extra
  column. Seeds are *not* independent abilities — they share a version — so treat them as a
  nested facet (see G-theory) rather than pretending they're 30 independent takers, but they
  still buy power for difficulty estimates and are essential for measuring run-to-run noise.
- **Include prior versions.** Every checkpoint you've already run is a free taker. Keep a
  cumulative response matrix across the whole iteration history.

Going from 6 to ~30 takers (3 tiers × 2 ablations × a few seeds, plus history) moves you from
"nothing is estimable" to "Rasch and shrinkage-regularized 2PL are reasonable."

### 2. Make G-theory your primary tool, not IRT
G-theory is variance-components based, so it's estimable at small N (with wide CIs, which it
reports honestly) and it answers the questions you actually have in iteration:
*how much of my score movement is real vs. noise, and how many cases/seeds/judges do I need to
tell version A from version B?* See `03_generalizability_theory.md`. In this regime, prefer a
dependability coefficient + D-study over any IRT ability table.

### 3. Drop to Rasch (1PL) before reaching for 2PL
If you need a latent scale, fix discrimination to 1 and estimate difficulty only. You give up
the discrimination parameter (get it from CTT item–rest correlation instead, which is what you'd
trust at this N anyway) and gain stability. Rasch person/version estimates are still noisy at
N≈30 but the difficulty ordering is usable, and the model is identified.

### 4. Fixed-item (anchor) calibration — turn an impossible fit into an easy one
This is the most important structural move and it's underused. **Calibrate item parameters once,
on a large taker bank, then freeze them.** Sources for the bank:

- A public leaderboard's response matrix on shared items (dozens–hundreds of models).
- A one-time sweep where you run *many* models on your suite (even cheap/old ones — they widen
  the ability range).

With items frozen, scoring your 6 versions reduces to estimating **6 ability values against
fixed item parameters** — a well-posed problem at any N, because you're no longer trying to learn
items from 6 takers. This is exactly how tinyBenchmarks deploys: fit IRT on a model bank, then
estimate any new model's ability from its responses to the pre-calibrated anchor items. Practical
rule: *never estimate item parameters and version abilities simultaneously from a tiny taker
set — separate the two phases in time.*

### 5. Hierarchical adaptive shrinkage — regularization that relaxes as N grows
This is the principled version of "regularize the discrimination parameter and loosen it as
sample size increases." Instead of a fixed penalty, put the item discriminations under a common
prior and let the data set the prior's width:

```
log(a_i) ~ Normal(mu_a, sigma_a)      # items' discriminations share a population
sigma_a  ~ HalfCauchy(0, 0.5)          # hyperprior; data decides how much they vary
b_i      ~ Normal(mu_b, sigma_b)
theta_v  ~ Normal(0, 1)                # version abilities
```

The mechanism is **partial pooling**: when data are sparse/uninformative, `sigma_a` is estimated
small, so every `a_i` is pulled toward the common mean `mu_a` (heavy shrinkage → behaves like
Rasch, stable). As you add takers and the data genuinely distinguish discriminations, `sigma_a`
grows and the estimates are allowed to spread out (shrinkage relaxes → recovers 2PL). The amount
of regularization is **learned, not hand-tuned**, and it adapts automatically with N — which is
the property you want. In simulations this kind of hierarchical 2PL (half-Cauchy or exponential
hyperprior on the scale) gives unbiased, lower-RMSE discrimination estimates down to N≈50,
beating both marginal-MLE 2PL and a non-hierarchical Bayesian 2PL.

Implementation notes:
- Build it in PyMC or brms (hand off to the multilevel-modeling skill for the estimation
  machinery). The half-Cauchy/half-Student-t on the scale parameter is the Gelman-standard weakly
  informative choice; it allows values near 0 (full pooling) with heavy tails (room to spread).
- Don't shrink the version abilities toward each other if your whole goal is to *separate*
  versions — keep `theta_v` on a fixed N(0,1) scale and only pool the *item* parameters.
- If you want a frequentist analogue, a ridge/Firth-type penalty on log-discrimination gives
  similar stabilization but you have to schedule the penalty by N yourself; the hierarchical
  Bayes version does that scheduling for you, which is why it's preferred.

**This is implemented.** `scripts/irt_latent.py --backend mcmc` fits exactly this hierarchical 2PL
(half-Cauchy hyperprior on σ_a, abilities un-pooled) and reports σ_a as the shrinkage state. Note
the lesson baked into that script: do *not* try to get σ_a from a joint MAP/EM optimizer — the
variance component collapses to 0 (or the discriminations run away to perfect-separation infinity).
The adaptive-shrinkage 2PL needs full Bayes; the scipy fallback therefore fixes discrimination
(Rasch) rather than faking a 2PL. See `08_latent_estimation.md`.

### 6. Always carry uncertainty; pre-commit thresholds
At small N the point estimate is the least interesting number. Required habits:

- **Bootstrap** item statistics over takers (and over cases) to get intervals; report the
  interval, not just the value. A point-biserial of 0.4 with a 95% CI of [−0.1, 0.8] is "unknown,"
  not "discriminating."
- **Bayesian intervals** fall out of the hierarchical model for free — use them.
- **Pre-register the decision rule** before looking: e.g., "promote version B only if its
  dependability-adjusted advantage excludes 0 at the suite level." This stops you from reading a
  2-point pass-rate bump (well inside seed-to-seed noise) as progress.

### 7. Binarize carefully if you have partial-credit scores
Graded/rubric scores can feed CTT and G-theory directly (they handle continuous outcomes). For
IRT you'll typically binarize; use a single, pre-declared scenario-level threshold (tinyBenchmarks'
approach) rather than per-item thresholds, so difficulty stays comparable across items.

## What to actually do at N=6 (the TL;DR)

1. Inflate takers to ~30 with model tiers + ablations + seeds + history (menu item 1).
2. Lead with **G-theory**: report a dependability coefficient and a D-study saying how many
   cases/seeds you need (menu item 2).
3. Run **CTT item stats with bootstrap CIs** to flag trim/fix candidates (menu item 6 +
   `02_ctt_item_analysis.md`).
4. Only if you need a latent ability scale: use **fixed-item anchoring** (item 4) or a
   **hierarchical adaptive-shrinkage Rasch/2PL** (items 3 + 5). Never a free 2PL on the raw 6.
5. Attach intervals to everything and decide against a pre-committed threshold (item 6).
