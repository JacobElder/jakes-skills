# Adjustment strategies

Once a question is identified as causal (rung 2 or 3) and a DAG is sketched, the next question is whether the effect is *identifiable* from observed data — and if so, how to compute it. The strategies below are listed in roughly preferred order; pick the first one the DAG allows.

## 1. Randomization

The reference standard. Random assignment makes the treatment independent of all other variables by construction — no back-door paths exist. The simple difference in means is an unbiased estimate of the average treatment effect.

When feasible (A/B tests, lab experiments, RCTs), this is the answer. When not feasible, the strategies below recover causal effects from observational data under specific assumptions.

## 2. Back-door adjustment

The most common and most general adjustment.

**Procedure:** find a set Z that satisfies the **back-door criterion**:

1. Z blocks every path between X and Y that has an arrow pointing *into* X.
2. Z contains no descendants of X.

Then `P(Y | do(X)) = Σ_Z P(Y | X, Z) P(Z)` — the conditional outcome distribution averaged over Z.

In practice: include Z as covariates in a regression of Y on X. The coefficient on X estimates the causal effect.

**Example.** Estimating the effect of education (X) on income (Y) when family background (Z) affects both:

```
   Z (family background)
   ↙ ↘
   X → Y
```

Back-door path: X ← Z → Y. Conditioning on Z blocks it. Z is a valid adjustment set.

**Failure modes:**
- Missing a confounder. Z is incomplete; the back-door isn't fully closed.
- Including a collider in Z. Conditioning opens a path that wasn't open.
- Including a mediator in Z. Blocks part of the causal effect you're trying to estimate.

## 3. Front-door adjustment

When unobserved confounders make back-door adjustment impossible, but the entire effect of X on Y runs through an observed mediator M.

**Front-door criterion (all three must hold):**
1. **Complete mediation:** M blocks *all* directed paths from X to Y — there is no direct X→Y path that bypasses M. This is easy to miss. Ask: could X affect Y through *any* mechanism that doesn't go through M? If training directly boosts performance ratings (e.g., being visibly seen attending training creates a halo effect, independent of skills actually applied), that direct path exists and the front-door formula is biased — even if M (skills applied) mediates the main effect. Check this assumption explicitly; it's the most commonly overlooked front-door condition.
2. **No unblocked back-door from X to M:** The unobserved confounder U must not directly cause M independent of X. If ambition causes employees to apply skills on the job *regardless* of whether they attended training, U→M is open and condition 2 fails.
3. **All back-door paths from M to Y are blocked by X:** The path M←X←U→Y can be blocked by conditioning on X, so this typically holds when condition 2 holds.

**Pearl's smoking-tar-cancer example:**

```
   U (genes, unobserved)
   ↙   ↘
   X → M → Y
   smoking → tar → cancer
```

The effect of smoking on cancer can't be back-door-adjusted because the genetic confounder U is unobserved. But if tar deposition fully mediates the smoking→cancer effect, and there's no back-door from tar to cancer, the effect is identified through M.

Two-step computation:
1. P(M | do(X)) — identifiable because the smoking→tar relationship has no unblocked back-doors.
2. P(Y | do(M)) — identifiable because conditioning on X blocks the back-door from M to Y.

Combined: P(Y | do(X)) = Σ_M P(M | X) Σ_X' P(Y | M, X') P(X').

The conditions are restrictive in practice — most observational settings have at least one unblocked back-door from M to Y. When the front-door applies, it's powerful; when it doesn't, look elsewhere.

## 4. Instrumental variables

Find a Z that:
1. Affects X (relevance).
2. Has no direct effect on Y (exclusion restriction).
3. Shares no confounder with Y (exogeneity).

```
   Z → X → Y
       ↑
       U (confounder, possibly unobserved)
       ↓
       Y
```

Z's effect on Y operates entirely through X, so Z's variation provides clean variation in X. The IV estimator recovers the local average treatment effect for the subpopulation whose X is affected by Z.

**Examples:**
- John Snow used water-company assignment as an instrument for water cleanliness in establishing cholera transmission.
- Lottery-based admissions instrument for the effect of attending a particular school.
- Distance to college instrument for years of schooling.

**Failure modes:**
- Weak instrument: Z affects X only slightly. Estimates become unstable and biased toward OLS.
- Exclusion violation: Z has a direct path to Y. The estimate conflates Z's direct effect with the X-mediated effect. **The bias direction is unknown** — it depends on the sign and magnitude of the direct Z→Y effect relative to the Z→X→Y effect. The estimate may be wrong in sign, not merely inflated in magnitude. This is a bias problem, not a power problem; more data does not fix it.
- Hidden confounding of Z and Y: Z isn't truly exogenous.

The exclusion restriction is not directly testable, but one useful falsification: **check whether Z predicts Y in a sub-population where X cannot vary.** For example, does distance to gym predict health outcomes among people who are physically unable to use a gym (severe mobility limitations, elderly in care facilities)? If yes, there is a direct path from the instrument to the outcome that bypasses gym membership — the exclusion restriction fails. This approach identifies sub-populations where the treatment effect is (near) zero, so any remaining Z→Y correlation must be a direct effect. When a clean never-taker population exists in the data, this is often the sharpest single diagnostic available.

## 5. Design-based identification

A class of strategies that handle confounding through how the data were collected, not through post-hoc adjustment.

### Natural experiments

Real-world situations producing as-if-random variation in X — lotteries, weather shocks, border discontinuities. Avoids the assumption that all confounders are measured. The key step is arguing that the variation is genuinely as-if-random for the units affected.

### Regression discontinuity (RDD)

When treatment is assigned by a hard cutoff in a continuous "running variable" — test scores, age thresholds, eligibility income, vote shares, hospital admission scores — units just above and just below the cutoff are nearly identical except for treatment. Comparing their outcomes recovers the local average treatment effect at the threshold.

```
   X (running) → D (treatment) → Y
   D = 1 if X ≥ c, else 0
```

**Conditions:** the cutoff must be exogenous (units can't precisely manipulate which side they fall on), and the relationship between X and Y must be smooth in the absence of treatment (so that any jump at the cutoff is attributable to D).

**Examples:** Angrist & Lavy used Israeli class-size rules (a new class opens when enrollment crosses 40) to estimate the effect of class size on achievement. Card studied Medicare's effect on health outcomes by comparing people just under and just over age 65.

**Variants:** *sharp* RDD when the cutoff deterministically assigns treatment; *fuzzy* RDD when it only changes the probability of treatment (and the cutoff serves as an instrument for actual treatment).

**Failure modes:** manipulation of the running variable around the cutoff (people gaming the threshold), other things changing discontinuously at the same cutoff, the local effect not generalizing beyond the threshold.

### Differences-in-differences (DiD)

Compares the *change* in outcomes between a treated group and a control group, before and after treatment. The control group's pre-post change estimates what the treated group's change would have been without treatment.

```
   ATE = (Y_treated_post − Y_treated_pre) − (Y_control_post − Y_control_pre)
```

The key assumption is **parallel trends**: in the absence of treatment, the treated and control groups would have followed the same trajectory. DiD doesn't require that the two groups have the same level — only the same trend. Time-invariant differences between groups (and time effects shared by both groups) cancel out in the double difference.

**Examples:** Card & Krueger used DiD to study minimum wage effects, comparing fast-food employment in New Jersey (treated) vs. Pennsylvania (control) before and after a NJ wage increase. Standard for evaluating policy changes, product launches in some markets but not others, A/B test rollouts staggered across time.

**Failure modes:** parallel-trends violation (the groups were already diverging before treatment), anticipation effects (treated units changing behavior before nominal treatment), composition changes within groups, differential shocks hitting only one group during the post period.

A pre-period plot of both groups' trajectories is the standard diagnostic — if pre-trends are clearly non-parallel, DiD's main assumption is suspect.

### Synthetic control

A generalization of DiD for the case where there's only *one* treated unit (a single state, country, or company) and many potential controls. Constructs a weighted combination of untreated units that closely tracks the treated unit's pre-treatment trajectory, then uses that "synthetic" unit as the counterfactual for the post-treatment period.

**Examples:** Abadie & Gardeazabal estimated the economic cost of Basque terrorism using a synthetic Basque region built from other Spanish regions. Card studied the Mariel boatlift's wage effects on Miami using a synthetic Miami. Common in policy evaluation where the unit of interest is large (a state, country, or industry) and few comparable units exist.

**Failure modes:** no untreated units that resemble the treated one; pre-treatment fit doesn't generalize to the post period; treatment effect contaminated by other shocks specific to the treated unit.

### Twin and adoption designs

Within-pair comparisons of monozygotic twins handle genetic and shared-family confounding by construction. If a relationship between X and Y survives within twin pairs, it can't be explained by genetic or shared-environment confounding. Especially valuable when the question involves heritable traits or family transmission.

### Surrogate interventions

Randomize a lab proxy for a real-world cause that can't be ethically or practically manipulated (e.g., manipulating perceived social class instead of actual social class). Internal validity high; the gap from proxy to real-world claim is a separate argument.

When a strong design is available, it leans less on assumptions about which confounders are measured. The cost is usually narrower scope: the design works because it's specific.

## 6. Not identifiable

Some questions can't be answered from observational data even with the right adjustment, because the DAG forbids it. Three productive responses:

- **Sensitivity analysis.** Quantify how strong an unmeasured confounder would need to be to overturn the conclusion. If "very strong," the conclusion is robust.
- **Bounds.** Compute the range of values the causal effect could plausibly take given the structural constraints.
- **Honest acknowledgment.** Report the limitation. Don't run a regression and pretend.

Pretending an unidentifiable question is identifiable is the most common analytic error in applied causal work. The DAG-first workflow is largely a discipline against this.

## Choosing among strategies

| Available? | Use |
|------------|-----|
| Randomization | RCT / A/B test |
| All confounders observable | Back-door |
| Mediator with no back-door from M to Y | Front-door |
| Instrument satisfying relevance + exclusion + exogeneity | IV |
| Hard threshold/cutoff in a continuous running variable | RDD |
| Treated and control groups, before/after observations | DiD |
| One treated unit, many comparable control units | Synthetic control |
| Within-family heritable trait question | Twin / adoption design |
| Real-world as-if-random variation (lottery, threshold) | Natural experiment |
| None of the above | Sensitivity analysis, bounds, or honest reporting |

The order isn't absolute — a strong natural experiment beats a weak back-door adjustment. The discipline is matching the strategy to what the DAG actually supports.

## A note on estimation methods

The strategies above are about *identification* — whether a causal effect can be recovered in principle from the data. *Estimation* is a separate question: given that an effect is identified, what method computes it?

For most cases, ordinary regression (with appropriate covariates and standard errors) suffices. A few estimation approaches worth knowing about:

- **Matching and propensity-score methods.** Alternatives to regression for back-door adjustment. They face the same identification challenges as regression — they fail if a key confounder is omitted, succeed if all are included and measured well. They're alternative implementations, not alternative identification strategies.
- **Doubly robust methods.** Estimators (like AIPW, DR-Learner) that combine an outcome model and a propensity score model and remain consistent if *either* is correctly specified. Useful when you're uncertain about model specification.
- **Double machine learning (DML) and causal forests.** ML-flavored methods for estimating average and heterogeneous treatment effects with high-dimensional covariates while preserving valid inference. Useful when there are many confounders and the parametric model risks misspecification.
- **Meta-learners (S-, T-, X-learners).** Methods for estimating *heterogeneous* treatment effects (CATE — how the effect varies across the population). When the question is "for whom does this work?" rather than "does it work on average?", these are the relevant tools.

The Python ecosystem (DoWhy, EconML, CausalML) and R ecosystem (grf, dowhy.r) implement these. They're estimation tools — they don't change the identification strategy. The DAG still decides whether a causal effect is identifiable; estimators just decide how to compute it once it is.
