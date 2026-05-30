# Conjoint Analysis: Advanced Reference

Covers Choice-Based Conjoint (CBC), Adaptive CBC (ACBC), and Menu-Based Conjoint (MBC). Assumes familiarity with the basics; focus is on the decisions Qualtrics/Sawtooth defaults won't make for you.

Table of contents:
1. The choice model and what's being estimated
2. Design efficiency: D-efficiency, balance, overlap
3. Tasks, attributes, and levels — how many of each
4. Prohibitions: why they're costly and what to do instead
5. None alternatives: single None vs. dual-response None
6. ACBC: when it pays and when it doesn't
7. Menu-Based Conjoint
8. HB estimation for CBC
9. Market simulators — share of preference, first choice, RFC
10. Calibration to in-market shares
11. Common failure modes

---

## 1. The model

Standard CBC is multinomial logit (MNL):

```
P(alt j chosen) = exp(X_j β) / Σ_k exp(X_k β)
```

where `X_j` is the design vector for alternative j (effects-coded or dummy-coded attribute levels), and β are the part-worth utilities. Under HB, β varies by respondent: β_i ~ Normal(μ, Σ), with μ and Σ estimated from the data.

Importance scores are derived from the *range* of part-worths within an attribute, expressed as a percentage of the total range across all attributes. This is a derived quantity, not a directly estimated parameter, and it has the well-known property of being inflated for attributes with many levels (because more levels → more range, mechanically). When comparing importance across attributes with different level counts, this is a real distortion.

**Effects-coded vs. dummy-coded**: effects coding (sum-to-zero) is the standard for CBC because it gives interpretable part-worths around a zero mean per attribute. Dummy coding produces equivalent fit but harder-to-read coefficients. Most platforms output effects-coded by default — don't change unless you have a specific reason.

---

## 2. Design efficiency

**D-efficiency** = a measure of how informative the design is for parameter estimation, computed from the determinant of the information matrix. A perfectly balanced, orthogonal design has D-efficiency = 100%. Real designs are typically 90–98%; below 80% is a warning sign.

**Relative D-efficiency** (Sawtooth's default report) compares your design to a theoretical optimum given your constraints. This is more interpretable than raw D-efficiency, especially when prohibitions or alternative-specific constraints are in play.

**Balance**: each level of each attribute should appear roughly equally often across the design. Imbalance reduces precision on the under-represented levels.

**Overlap**: how often the same level repeats across alternatives within a task. Sawtooth's default is "balanced overlap" — moderate overlap that improves the precision of interactions and non-linear price effects. Zero-overlap (older default) is more efficient for main effects but worse for everything else.

**When to override defaults:**
- Pure main-effects model, no interactions, no non-linear price → minimal overlap is fine
- Want to estimate any interaction → balanced or higher overlap
- Want to estimate non-linear price (piecewise) → higher overlap on price

**Random vs. optimized designs**: a randomized design with reasonable constraints achieves ~95% relative D-efficiency at modest sample sizes. The marginal gain from optimization (Federov, modified Federov, etc.) is real but small for typical studies (1–3% efficiency). It matters more for small samples (<200) or complex designs with prohibitions.

---

## 3. How many tasks, attributes, and levels

**Tasks per respondent (t):**
- Standard range: 8–15. Below 8 = under-collecting; above 15 = fatigue.
- For HB stability, total observations per respondent matters: t × (alternatives - 1) should be ≥ 30 for solid individual-level estimation. With 3 alternatives and a None, that's t ≥ 10.
- More tasks help individual-level precision more than population-level. If you only need aggregate logit, t = 8 is fine; for HB-driven simulators, push for t = 12+.

**Alternatives per task (a):**
- Typical: 3–4 alternatives plus a None.
- 2 alternatives: lower per-task information but lower cognitive load. Useful for vulnerable or low-literacy populations.
- 5+ alternatives: respondents start ignoring alternatives ("non-attendance to alternatives"). Diminishing returns above 4.

**Attributes (k):**
- 4–6 attributes: comfortable, no special handling needed
- 7–8 attributes: starting to see non-attendance (respondents ignoring 1–2 attributes per task). HB picks this up as a low part-worth range for the ignored attribute, but it's not really "low importance" — it's that they didn't look at it.
- 9+ attributes: use partial-profile CBC (each task shows only a subset of attributes per alternative) or ACBC
- Detect non-attendance: in HB, look at the variance of within-respondent part-worth ranges across attributes. A respondent with near-zero range on one attribute is likely ignoring it.

**Levels per attribute:**
- 2–5 levels: easy
- 6–7 levels: workable but watch sample size; need more observations to estimate all part-worths
- 8+ levels: consider treating the attribute as continuous (with linear or piecewise-linear coding) rather than categorical. Especially for price.

**Linear vs. categorical price**: linear price (one coefficient) is more efficient but assumes constant marginal disutility, which is rarely true. Piecewise-linear (one coefficient per segment) or fully categorical is better. Default to categorical for ≤5 price levels and piecewise-linear for more.

---

## 4. Prohibitions

A prohibition is a constraint that certain attribute-level combinations cannot appear together (e.g., "premium brand cannot have lowest price"). They're seductive — they make the design look more realistic — but they're statistically expensive.

**Why prohibitions hurt:**
- They reduce design efficiency. A few prohibitions cost 1–3% D-efficiency; many can drop you below 80%.
- They make some main effects partially confounded with the prohibition pattern. Strong prohibitions can fully confound them.
- They invalidate the simulator outside the prohibited regions — but stakeholders often want to simulate exactly there ("what if Brand A *did* sell at the low price?").

**Default policy: use the minimum number of prohibitions necessary to keep the design face-valid.** "Premium brand + lowest price" probably needs to be prohibited; "mid brand + mid-low price" probably doesn't.

**Alternatives to prohibitions:**

1. **Alternative-specific designs**: rather than prohibiting brand-price combinations, structure the design so each brand has its own price range. This is the standard for product categories where the price range genuinely differs by brand. Sawtooth supports this directly.

2. **Conditional pricing**: price levels defined relative to each brand's base price (e.g., -10%, base, +10%, +20%). The actual prices shown vary by brand. Statistically equivalent to alternative-specific in many cases, simpler to design.

3. **Reframe**: sometimes the "prohibition" reflects a true constraint that should be modeled differently (e.g., "feature X requires plan Y" is a hierarchical product structure that needs MBC, not CBC).

**When prohibitions are unavoidable**: explicitly check the design's relative D-efficiency. If it drops below 85%, you're paying real cost. Consider larger sample size to compensate.

---

## 5. None alternatives

**Single None**: "I would not choose any of these." Standard option. Provides an outside-good utility that anchors the model and enables realistic share simulations.

**Dual-response None** (recommended default for most studies): respondent first picks their preferred alternative from the shown set, then answers a separate question — "Would you actually buy/use this?" — yes/no.

Pros of dual-response:
- Distinguishes "I'd pick A over B and C" from "I'd actually use A." Lots of respondents would rather pick A in a forced choice but wouldn't buy any of the three.
- Doubles the response per task without doubling cognitive load.
- Yields more realistic share-of-purchase simulations.

Cons:
- Slightly more complex estimation (two MNL terms).
- The "would you buy" question wording matters — be specific about the action.

**When to use single None instead**:
- The decision is forced-choice in reality (e.g., insurance plan selection — you have to pick something)
- The product category has near-100% adoption (rarely)
- Survey length is a hard constraint

**No-None design**: every task forces a choice. Useful only when you genuinely know everyone in the population buys one of the alternatives — uncommon.

---

## 6. ACBC (Adaptive CBC)

ACBC has three stages:

1. **BYO (Build Your Own)**: respondent selects their preferred level on each attribute. Acts as a prior on individual-level part-worths.
2. **Screener**: shown a series of alternatives near their BYO, marks each as "a possibility" or "won't consider." Identifies must-haves and unacceptables.
3. **Choice Tournament**: pairwise (or triple) choices among the "possibility" set. Provides the main choice data.

**When ACBC pays:**
- Many attributes (≥8) — the BYO and Screener stages dramatically reduce the design space before the Tournament, so respondents don't waste effort on alternatives they'd never consider.
- Strong must-have / unacceptable patterns in the population — ACBC identifies these per respondent; CBC bakes them into part-worth ranges with no nuance.
- Complex pricing (summed price across optional components) — ACBC's summed pricing engine handles this natively.

**When ACBC hurts:**
- Few attributes (≤5) — the BYO stage just adds survey length without proportional gain.
- Categorical attributes with no natural "preferred level" — BYO is awkward when respondent's true preference depends on context.
- Trying to simulate products far from any respondent's "consideration set." ACBC concentrates information near the consideration set, so simulator estimates degrade for alternatives outside it.

**ACBC failure modes:**
- **BYO seeding bias**: respondents anchor on their BYO and over-state attribute importance because they explicitly constructed their ideal. Importance scores from ACBC tend to be more spread than CBC equivalents.
- **Unacceptable inflation**: some respondents mark too many levels unacceptable, leaving the Tournament with very few alternatives. Watch the average size of each respondent's "possibility set" — if it's <8, the Tournament is under-powered.

**Default**: use ACBC for ≥8 attributes or complex pricing structures. Use CBC otherwise. The complexity is real and the gain is conditional.

---

## 7. Menu-Based Conjoint

MBC models situations where respondents assemble a bundle — pick a base product plus optional add-ons. The standard estimation is independent logits per element (base, add-on 1, add-on 2, ...), with cross-effects modeled where bundle interactions matter.

**When to use MBC:**
- Subscription tiers with add-ons (storage, support, premium features)
- Configurable products (cars with options, software with modules)
- Bundle pricing studies where the question is "what combination do they choose"

**Design considerations:**
- Show the full menu, with prices, and let the respondent pick any combination including "nothing"
- 8–12 menu choice tasks per respondent
- Estimate is on each element's selection probability conditional on the menu offered

**Common failure mode**: ignoring the correlation between add-on selections. Respondents who add storage are also more likely to add support; standard independent-logit MBC misses this. Solution: include cross-effects for plausibly correlated add-ons.

---

## 8. HB estimation for CBC

**Priors:**
- Mean prior: zero, on effects-coded part-worths. Don't change.
- Covariance prior degrees of freedom: default is k + 5 (where k is number of estimated parameters). Lower df = weaker prior, more between-respondent variation. For studies with many parameters and modest n, the default is often too informative — try df = k + 2 to k + 3.
- Prior variance: usually 1 or 2 on effects-coded part-worths. Higher = weaker shrinkage. Default is fine for most cases.

**Iterations:**
- Burn-in: 20,000 (some platforms default to 10,000 — too few for complex designs).
- Used draws: 20,000+, with thinning so the final saved set is 1,000–2,000 draws.
- Convergence check: trace plots of mean part-worths and the covariance matrix should stabilize. Run multiple chains from different starting points if the platform allows.

**Per-respondent draws**: keep 100–1,000 draws per respondent for the simulator. Single-point (posterior mean) estimates lose information about respondent-level uncertainty, which matters for share-of-preference simulations that integrate over respondents.

**Convergence pathologies:**
- One attribute's part-worth bouncing wildly → likely an identifiability issue, often from prohibitions
- The covariance matrix is near-singular → too many parameters for the sample size; consider constraining or dropping an attribute
- Log-likelihood keeps drifting → not converged; run more iterations

**Reversals**: at the individual level, HB will sometimes produce non-monotonic part-worths on monotonic attributes (e.g., higher price preferred to lower for some respondents). For aggregate readouts, the rate of reversals is usually small. For individual-level simulators, consider monotonicity constraints — but only if you're confident the attribute *is* monotonic for the population (price typically yes; brand no).

---

## 9. Market simulators

Three main simulation rules:

**First Choice**: each respondent's predicted choice is whichever simulated product has highest utility for them. Aggregate share = % of respondents who pick each product. Highly sensitive to small utility differences (a 0.01 utility gap flips the choice). Tends to over-state share of dominant products.

**Share of Preference**: each respondent's share for each product is `exp(U_j) / Σ exp(U_k)`. Aggregate share = average across respondents. Less sensitive to small utility differences, more realistic distribution.

**Randomized First Choice (RFC)**: First Choice with stochastic error added to utilities. Combines First Choice's discreteness with Share of Preference's stability. Often the practical default.

**Which to use:**
- Default to **Share of Preference** for stable readouts and when there are many alternatives.
- Use **RFC** when stakeholders need a "% who choose X" framing that's interpretable as a count.
- Use **First Choice** only when you have strong evidence respondents are highly deterministic in the actual market (rare).

**Tuning the simulator**: most platforms have an "exponent" parameter (a.k.a. scale or Gumbel scale). Higher exponent → choices become more deterministic, closer to First Choice. Lower → flatter, closer to uniform. Calibrate by checking that simulated shares of a known product line match market shares (see calibration below).

---

## 10. Calibration to in-market shares

Raw simulator shares are **relative**, not absolute. Reasons they don't match in-market:
- Distribution, awareness, salesforce, brand effects not in the experiment
- Respondent sample isn't a market sample
- Stated preference ≠ revealed preference
- Survey environment removes search costs and inertia

**Calibration approaches:**

1. **External effects (a.k.a. brand adjustment)**: add a brand-specific constant to each brand's utility, fit so simulated shares match known in-market shares for the existing product line. Then use the calibrated model to predict shares for new products.

2. **Tuning the exponent**: adjust scale until top-line shares match. Cheaper than external effects but only fixes the *concentration* of shares, not their *ordering*.

3. **Calibration to claimed purchase intent**: have respondents rate their likelihood to buy each simulated product on a scale; use that to scale simulator output. Industry-standard but introduces its own bias.

**The honest framing**: calibrate when you need absolute volume predictions; otherwise report shares of preference as *relative* and don't pretend they're market shares.

---

## 11. Common failure modes

**Non-attendance to attributes**: respondents ignoring one or more attributes. Detect via HB individual part-worth ranges. Fix by: shorter attribute lists, partial-profile CBC, or ACBC.

**Non-attendance to alternatives**: respondents only looking at the leftmost (or first) alternative. Detect by checking if the leftmost is chosen disproportionately. Fix by randomizing alternative position.

**Reference-price effects**: respondents anchor on the first task's prices. Subsequent tasks' price utilities are biased relative to that anchor. Hard to fully fix; reduce by varying price across tasks and using piecewise-linear price.

**Screening on price**: some respondents will refuse to consider the highest price regardless of features (or the lowest price as "too good to be true"). Looks like extreme price part-worths. Use ACBC's Screener stage or explicitly model with HB constraints.

**Attribute-level imbalance**: rare levels are estimated with high SE. Make sure each level has at least 200–300 observations across the study (which usually falls out naturally with balanced designs at adequate n).

**Linear price assumption fails**: piecewise or categorical price almost always fits better. Check by adding non-linear price terms; if part-worths aren't monotonic on price (within reason), don't force linearity.

**Simulator overconfidence**: stakeholders treat simulator output as point predictions. Always show simulator output with CIs computed from posterior draws. A 30% share with [22%, 38%] CI tells a very different story than 30% alone.

**The "more attributes is more realistic" fallacy**: adding attributes does not improve the simulator unless those attributes drive choice. It does add cognitive load and reduce precision per attribute. Default to fewer attributes, modeled well.
