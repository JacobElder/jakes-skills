---
name: causal-inference
description: "Use for any question about causal reasoning, experimental validity, or whether a data analysis supports cause-and-effect conclusions. Always invoke when a user: asks if a result \"proves\" causation or whether a p-value, coefficient, or A/B test establishes a causal effect; questions whether controlling for a variable is the right move (confounders, mediators, bad controls); encounters a sign reversal or Simpson's paradox when splitting data; asks whether filtering or selecting a subgroup before analysis creates bias; questions a quasi-experiment (DiD/parallel trends, RDD threshold manipulation, IV exclusion restriction, SUTVA/network interference); asks which predictive model features to intervene on vs just predict with; asks about LATE vs ATE, complier effects, or rollout extrapolation from an opt-in experiment. Use it even when they don't say \"causal\" — if they're asking \"can I trust this estimate\" or \"what happens if we change X\", this skill applies."
---

# Causal Inference (Pearl's framework)

A skill for thinking clearly about cause and effect, drawn from Judea Pearl's *Book of Why* and the surrounding literature. Use it whenever a question is genuinely about cause and effect rather than prediction or association.

The single most useful move this skill makes is **redirecting questions from "what's correlated?" to "what would happen if we intervened?"** Most confusion in applied statistics comes from people asking causal questions but answering them with associational tools. Naming the rung is half the work.

## When to use this skill

Trigger when any of the following appear:

- "Does X cause Y?" / "What's driving Y?" / "Will doing X change Y?"
- Plans for an A/B test, RCT, or quasi-experiment
- Interpretation of a regression, correlation, or observational study
- Mentions of confounders, "controlling for", adjusting, covariates
- Paradoxical findings (a relationship reverses or vanishes when sliced differently)
- Selection effects, survivorship bias, "this only looks at people who…"
- Counterfactuals: "what would have happened if…", "but for…", attribution
- Predictive model being used to drive a decision (a covert causal question)

Don't trigger for pure prediction tasks where intervention isn't on the table. If prediction is being used to guide an action, that's a causal question in disguise.

## The Ladder of Causation

Three rungs, each requiring different tools:

| Rung | Activity | Question | Tools |
|------|----------|----------|-------|
| 1. Association | Seeing | "What if I see X?" | Correlation, regression, most ML |
| 2. Intervention | Doing | "What if I do X?" | RCTs, do-operator, back-door / front-door / IV |
| 3. Counterfactuals | Imagining | "What if I had done X?" | Structural causal models |

**Critical rule:** A higher rung cannot be answered with tools from a lower rung *without additional causal assumptions* — typically a DAG. No amount of rung-1 data alone, however large, answers a rung-2 question.

When a user asks a question, your first job is to name the rung. "Does this onboarding flow improve retention?" is rung 2. If the data is observational, flag the gap. Opt-in / self-selected experiments estimate the **ATT** (effect among those who chose in), not the **ATE** (effect if rolled out to everyone). When heterogeneous effects and self-selection are plausible, these differ substantially — and rollout decisions usually require the ATE.

## Two frameworks: DAGs and potential outcomes

There are two equivalent ways to express causal questions formally. **Pearl's DAG/do-calculus** framework (the focus of this skill) emphasizes the structure of relationships — drawing a diagram, finding paths, choosing adjustments. The **Neyman-Rubin potential outcomes** framework (dominant in econometrics, statistics, and A/B testing) emphasizes the missing-data view: each unit has a potential outcome under treatment Y(1) and under control Y(0), but we only observe one. The treatment effect is Y(1) − Y(0), and the fundamental problem of causal inference is that this difference is never observable for the same unit.

The two frameworks are mathematically equivalent for most purposes. DAGs are better for *thinking through* whether an effect is identifiable; potential outcomes are better for *defining the estimand* and reasoning about specific estimators. In practice, fluent practitioners use both — drawing a DAG to argue for identification, then writing the estimand in potential-outcomes notation (ATE, ATT, CATE) to be precise about what's being computed.

When discussing a problem, defaulting to DAG language is usually clearer for non-technical users. Switching to potential-outcomes language is appropriate when the user is already there (statisticians, econometricians, A/B testers) or when the question is specifically about heterogeneity or estimation.

## Causal diagrams (DAGs)

A DAG is the working object: nodes are variables, arrows are direct causal effects. The DAG encodes the assumptions; the data alone never can.

### The three junctions

Every path between two variables is built from three patterns:

- **Chain (mediator):** `A → B → C`. Information flows from A to C through B. Conditioning on B *blocks* the flow.
- **Fork (confounder):** `A ← B → C`. B is a common cause; A and C are spuriously correlated. Conditioning on B *removes* the spurious correlation — **good**.
- **Collider:** `A → B ← C`. B is a common effect. The path is *closed by default*. Conditioning on B *opens* it, creating spurious correlation — **bad**.

### The control rule

| Junction | Default | What conditioning does |
|----------|---------|----------------------|
| Chain | Open | Closes (blocks the effect) |
| Fork | Open (spurious) | Closes (removes confounding) |
| Collider | Closed | Opens (creates spurious correlation) |

**The instinct "control for everything you can measure" is wrong.** Controlling for a collider — or a descendant of one — actively creates bias where none existed.

## Identifying causal effects

Given a DAG and observational data, can you compute the causal effect P(Y | do(X))? Strategies in order of preference:

1. **Randomize.** If feasible, an RCT or A/B test makes adjustment unnecessary.
2. **Back-door adjustment.** Control for a set Z that blocks every path from X to Y starting with an arrow into X, without opening any colliders.
3. **Front-door adjustment.** When unobserved confounders block back-door but the effect runs through an observed mediator M. Before concluding "not identifiable," ask: is there an observed mediator between X and Y? If so, check all three conditions — but pay special attention to condition 1 (complete mediation): **there must be no direct X→Y path that bypasses M**. Ask explicitly: can X affect Y through *any* mechanism that doesn't go through M? A training program that directly boosts performance ratings by signaling effort (the halo of being seen attending training) would violate this, even if skills-applied is the main pathway. This condition is the one most often glossed over in front-door analyses.
4. **Instrumental variables.** Find a Z that affects X, has no direct effect on Y, and shares no confounder with Y. When evaluating an instrument, the exclusion restriction is the usual weak link. Key points that are easy to miss: (a) a violated exclusion restriction is a **bias** problem, not a power problem — more data does not fix it; (b) **the bias direction is unknown** — it depends on the sign and magnitude of the direct Z→Y effect, and the estimate can be wrong in sign, not just magnitude; (c) one practical falsification: check whether Z predicts Y in a sub-population where X cannot vary (e.g., does distance to gym predict health outcomes among people who will never join a gym regardless?). See `references/adjustment.md` for the full failure-mode analysis.
5. **Design-based.** Strategies that exploit how the data were generated:
   - **Regression discontinuity (RDD)** when a hard threshold determines treatment (eligibility cutoffs, age limits, vote shares).
   - **Differences-in-differences (DiD)** when treated and control groups are observed before and after treatment, and parallel trends are plausible.
   - **Synthetic control** when one unit was treated and many comparable untreated units exist (single-state policy, single-firm shock).
   - **Twin/adoption** for heritable-trait questions.
   - **Natural experiments** for as-if-random variation (lotteries, weather, border discontinuities).
6. **Not identifiable.** Some questions require an experiment or stronger assumptions. That's a legitimate conclusion.

See `references/adjustment.md` for the procedures, identifying assumptions, and failure modes of each.

## Choosing controls

Most applied causal questions reduce to: should I include variable Z in the regression? Two pieces of folklore are wrong:

- **"Control for any pre-treatment variable that predicts both treatment and outcome."** Wrong. Pre-treatment colliders and instruments both fit this description and *worsen* bias when controlled for.
- **"Never control for post-treatment variables."** Wrong. Some post-treatment variables are bias-neutral; some recover effects under sample-selection bias.

The right rule is structural. Z is a good control if it (1) blocks all non-causal paths from X to Y, (2) leaves causal paths intact, and (3) doesn't open new spurious paths. Whether a given Z does that depends on the DAG, not on temporal ordering.

### Per-variable classification

For each candidate control Z, classify its structural role and apply the verdict:

1. **Confounder (fork)?** → Control. Closes a spurious path.
2. **Mediator on the X → Y path, or descendant of one?** → Don't control if you want the total effect. Post-treatment variables are especially likely to be mediators — if a variable was measured *after* treatment assignment, ask whether treatment could have caused it before including it as a control.
3. **Collider, or descendant of one?** → Don't control. Conditioning opens a spurious path.
4. **Strong predictor of treatment, weak predictor of outcome (near-instrument)?** → Don't control as a regression covariate. With unobserved confounding present, conditioning amplifies bias rather than reducing it.
5. **Cause of Y only, unrelated to X?** → Neutral; helps precision.

Three structures worth recognizing on sight:

- **M-bias.** A pre-treatment variable that is a collider between two unobserved confounders affecting X and Y separately. Looks like a textbook confounder; controlling for it creates bias from nothing.
- **Bias amplification (near-IV).** A variable strongly predictive of treatment but weak on outcome. Conditioning concentrates the remaining variation in X onto the part correlated with unmeasured confounders, making bias worse.
- **Cancellation of offsetting biases.** Two confounders pushing bias in opposite directions can partially cancel in the unadjusted estimate. Adjusting for one removes the cancellation, unmasking the other — and the "corrected" estimate ends up further from the truth than the original.

For the full structural taxonomy and worked examples, see `references/controls.md`.

## Counterfactuals (rung 3)

Counterfactuals ask about specific cases under hypothetical alternatives, conditional on what actually happened — "would this patient have recovered without the drug?" Distinct from rung 2, which asks population-level questions about interventions.

Two distinct concepts:
- **Necessary causation (PN):** Was X needed for Y to occur? (Legal but-for standard.)
- **Sufficient causation (PS):** Would X alone produce Y? (Policy-relevant.)

Different numbers, different applications. See `references/counterfactuals.md`.

## Common traps

- **Confounding ignored.** Two variables move together; a lurking common cause is the real driver.
- **Collider conditioning.** Controlling for a common effect creates correlations from nothing. Sample selection on a downstream variable is a form of conditioning.
- **Simpson's paradox.** A trend reverses when you slice the data differently. The DAG decides: confounder → disaggregate; mediator → aggregate. The critical diagnostic before concluding "segment is a confounder" is: *could the treatment itself have caused users to change segments?* A feature that redirects users to a mobile app could cause web users to become app users; "platform" would then be a mediator on the treatment path, and the aggregate result is the correct one. Ask explicitly: (1) was segment membership fixed before treatment exposure, or could treatment change it? (2) is there a mechanism by which the feature causes users to shift from one segment to another? If yes to (2), the segment is likely a mediator — do not disaggregate, because you would be conditioning on a mediator and blocking the very effect you're trying to measure.
- **Predictive accuracy ≠ causal validity.** A model that predicts well can give wildly wrong answers about what to do. ZIP code may predict default, but lending policy based on it doesn't intervene on the cause. **Downstream indicator trap:** many high-importance features are consequences of the outcome state, not causes. Days since last login predicts churn because disengaged customers stop logging in *before* they cancel — the disengagement causes both the infrequent logins and the eventual churn. Re-engagement campaigns that increase login frequency without addressing the underlying disengagement will not reduce churn; they treat the symptom, not the cause. The do-operator makes this precise: P(churn | last_login_days = 30) is the churn rate among users who *happen* to have 30-day login gaps; P(churn | do(last_login_days = 30)) — forcing someone to log in every 30 days — is a much smaller and different quantity. For every high-importance predictive feature, ask: does this variable move *because* the outcome state is already changing, or does it move *before* and *cause* that state? Downstream indicators are valid targeting signals (who to act on) but not valid intervention targets (what to change).
- **Mistaking RCT for the only path.** Back-door, front-door, IV, and natural experiments can identify causal effects from observational data when the DAG cooperates.
- **Forgetting the DAG is an assumption.** Every conclusion is conditional on the DAG being right. Articulate alternatives and check whether the conclusion is robust.
- **Table 2 Fallacy.** Interpreting every coefficient in a multiple regression as a causal effect. Only the focal coefficient is identified; control coefficients describe model fit, not causal effects of those variables — even when those controls are valid for the focal effect.
- **Statistical-only justification.** "Z correlates with X and Y, so I controlled for it." The same correlation pattern is produced by *every* DAG type — confounder, mediator, collider, proxy. Choosing whether to control requires causal reasoning.

## End-to-end response workflow

When a user brings a causal question, the per-question approach (distinct from the per-variable classification under "Choosing controls" above):

1. **Name the rung.** Often the user is on the wrong rung for what they actually want to know.
2. **Sketch the DAG.** Even in prose: "let's say W → X → Y with U → X and U → Y as a confounder." Make assumptions visible.
3. **Identify the structure.** Where are the chains, forks, colliders? Which paths are back-door paths? For each candidate control, apply the per-variable classification above.
4. **Pick a strategy.** RCT if feasible; otherwise back-door → front-door → IV → "not identifiable, here's what you'd need."
5. **Flag the most likely trap.** Usually: unmeasured confounder, a collider being controlled for, or sample selection.
6. **Enumerate alternative structural roles.** For the key variables in dispute, explicitly state: what if this variable is a confounder vs. a mediator vs. a collider? What does the answer become under each alternative? This is what separates a causal diagnostic from a statistical description — and it's often the most useful thing to say. If one plausible DAG flips the recommendation, say so explicitly and give the user a concrete diagnostic to discriminate between the alternatives. For any variable framed as a potential intervention target: ask whether it is *upstream* (a cause of the outcome — a valid lever) or *downstream* (a consequence of the outcome state — a symptom). Downstream variables cannot be valid intervention targets; they should be used as targeting signals at most.

A good causal-inference response is a diagnostic, not a lecture.

## What this skill is *not* for

- Pure forecasting / prediction with no decision attached.
- Pure model-specification questions once identification is settled.
- Philosophical debates about whether causation "really exists" — Pearl's framework is operational.

## References

- `controls.md` — Structural taxonomy of controls (confounder, mediator, collider, proxy) with verdicts and the named traps (M-bias, bias amplification, Table 2 Fallacy) in one place.
- `adjustment.md` — Back-door, front-door, and instrumental-variable adjustment with brief worked examples; design-based alternatives.
- `counterfactuals.md` — Three-step counterfactual procedure, necessary vs. sufficient causation.
