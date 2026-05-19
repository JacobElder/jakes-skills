# TWFE with Staggered Rollout: Is Your +6% Estimate Reliable?

## Short Answer

Your reviewer is correct. TWFE regression with staggered treatment timing can produce biased and potentially misleading estimates **even when the parallel trends assumption holds perfectly**. The +6% estimate warrants scrutiny before you act on it.

---

## What's Actually Happening: The Contaminated Comparison Problem

Standard two-way fixed effects with a single "treated" dummy implicitly constructs a weighted average of many pairwise 2x2 DiD comparisons. In a staggered rollout, this includes comparisons that are conceptually valid and comparisons that are not.

Specifically, the TWFE estimator uses:

1. **Clean comparisons** — treated regions vs. never-treated regions (in your case, the 10 regions treated in Q4 serve as partial controls for Q1/Q3, and never-treated regions if any exist)
2. **Forbidden comparisons** — early-treated regions (Q1 cohort) used as the *control group* for later-treated regions (Q3 or Q4 cohorts)

The second category is the problem. Once a unit is already treated, using it as a control for units that are about to be treated implicitly assumes the treatment effect is constant over time and across cohorts. If treatment effects grow over time (which is plausible — customer success programs often ramp up) or vary across the Q1, Q3, and Q4 cohorts, the "treated" control units carry a contaminated counterfactual. This can introduce negative weights on certain cohort-period comparisons.

**The critical insight from Callaway & Sant'Anna (2021), Sun & Abraham (2021), and Goodman-Bacon (2021):** The TWFE coefficient is a weighted average of cohort-specific ATTs, but the weights can be *negative* for some cohorts. This means the aggregate estimate can be an economically meaningless number — or worse, point in the wrong direction — even when no assumption has been violated.

---

## Diagnosing the Severity in Your Setting

Your design has three features that determine how worried you should be:

### 1. Cohort Composition
- **Q1 cohort**: 15 regions — the largest group, treated earliest, so they accumulate the most post-treatment periods
- **Q3 cohort**: 20 regions — treated mid-study
- **Q4 cohort**: 10 regions — treated late, so they contribute little post-treatment data and may serve as controls for Q1/Q3

The Q1 cohort (15 regions) will disproportionately act as "contaminated controls" for the Q3 and Q4 cohorts in the TWFE machinery.

### 2. Heterogeneous Treatment Effect Timing (Effect Dynamics)
Ask: does the program's impact on renewal rates likely build over time? If yes — e.g., customer success reps need ramp time, relationship-building is slow — then the Q1 cohort's treatment effect has had 2-3 additional quarters to mature compared to the Q3 cohort. TWFE will treat this variation as noise or, worse, subtract it from the estimate.

### 3. No Never-Treated Group
If all 45 regions eventually received treatment (15+20+10=45), you have **no pure never-treated control group**. Every comparison is across cohorts. This maximizes the contamination potential and is the most concerning aspect of your design.

---

## What the Bias Looks Like Mechanically

Goodman-Bacon (2021) showed that the TWFE estimator can be decomposed as:

```
β_TWFE = Σ_{k,l} w_{kl} * δ_{kl}
```

Where `k` and `l` are cohort pairs and the weights `w_{kl}` are determined by group sizes and timing — not by causal logic. If early-treated cohorts have large, growing treatment effects, and they're being used as controls for late-treated cohorts, those comparisons contribute *negatively weighted* terms to the aggregate β.

**Concrete example from your setting:**
- Q1 cohort by Q3 gets, say, a +10% lift (effect has had time to compound)
- When TWFE compares Q3 cohort (just treated) vs. Q1 cohort (already treated), the Q1 cohort looks "better" than a clean untreated control would
- This makes the Q3 cohort's treatment look *smaller* than it truly is
- The aggregate +6% could be masking a +9% true effect — or the composition could flip in other scenarios

---

## What You Should Do

### Step 1: Run the Goodman-Bacon Decomposition
This diagnostic decomposes your TWFE estimate into its constituent 2x2 comparisons and shows you what fraction of the weight comes from "forbidden" (already-treated vs. soon-to-be-treated) comparisons. If forbidden comparisons drive a large share of the weight, the +6% is unreliable.

In Stata: `bacondecomp renewal_rate treated, ddetail`
In R: `bacon()` from the `bacondecomp` package

### Step 2: Estimate Cohort-Specific ATTs Using a Robust Estimator

Replace the single TWFE with one of these heterogeneity-robust DiD estimators:

**Callaway & Sant'Anna (2021)** — estimates group-time average treatment effects ATT(g,t) for each cohort g at each time t, then aggregates. Handles staggered adoption, variable treatment timing, and no never-treated group (using "not-yet-treated" as controls).

**Sun & Abraham (2021)** — interacts cohort dummies with event-time dummies, which is equivalent to estimating clean cohort-specific effects. Implementable in standard regression software.

**Stacked DiD** — creates a separate "clean" dataset for each treatment cohort (using only not-yet-treated units as controls) and stacks them, then runs regression on the stack.

In R: `did` package (Callaway & Sant'Anna), `fixest` with `sunab()` (Sun & Abraham)
In Stata: `csdid`, `eventstudyinteract`

### Step 3: Inspect Event Study Plots by Cohort

Plot renewal rates for each cohort (Q1, Q3, Q4) relative to their treatment date, not a common calendar date. Look for:
- Pre-treatment parallel trends (slopes should be similar to controls before treatment)
- Post-treatment divergence (the treatment effect emerging after rollout)
- Whether effects look similar or different across cohorts

If the Q1 cohort shows a much steeper post-treatment trajectory than Q3, you have effect heterogeneity that TWFE is mishandling.

### Step 4: Check for Anticipation

Did regions know in advance when they'd receive the program? Customer success teams might change behavior before official rollout if they were told "you're getting this in Q3." Anticipation effects can also bias TWFE (and most estimators), and they can appear as pre-treatment violations in event study plots.

---

## What to Report

Rather than a single aggregate +6%, report:

| Cohort | ATT Estimate | 95% CI | N Regions | Quarters Post-Treatment |
|--------|-------------|--------|-----------|------------------------|
| Q1     | XX%         | [X,X]  | 15        | ~4-6                   |
| Q3     | XX%         | [X,X]  | 20        | ~2-4                   |
| Q4     | XX%         | [X,X]  | 10        | ~1-2                   |
| Aggregate (CS) | XX% | [X,X] | 45      | —                      |

This is more informative for decision-making anyway — you'll learn whether the program works better in some regions, and whether effects compound over time (which predicts what Q3/Q4 regions can expect as they mature).

---

## Bottom Line

Your reviewer is raising a well-documented methodological concern. The +6% TWFE estimate:

- **May be biased** due to forbidden comparisons between cohorts at different treatment stages
- **May have incorrect sign** in extreme cases (though this requires substantial heterogeneity)
- **Is almost certainly a distorted average** that blends cohort-specific effects with arbitrary implicit weights

The fix is not heroic — it's running Callaway & Sant'Anna or Sun & Abraham, which are now standard in applied work. The good news: if the true effects are positive and roughly similar across cohorts, the robust estimator will still show a positive effect, and you'll have much stronger justification for the +6% (or whatever it turns out to be). If the cohort-specific estimates diverge substantially from +6%, you'll have learned something important about program heterogeneity that's actionable for rollout strategy.

**Recommendation: Do not finalize the evaluation report using the TWFE estimate alone. Run the robust estimators and the Goodman-Bacon decomposition, report cohort-specific ATTs, and note the TWFE result as a comparison point.**

---

## Key References

- Goodman-Bacon, A. (2021). "Difference-in-differences with variation in treatment timing." *Journal of Econometrics*, 225(2), 254-277.
- Callaway, B., & Sant'Anna, P. H. (2021). "Difference-in-differences with multiple time periods." *Journal of Econometrics*, 225(2), 200-230.
- Sun, L., & Abraham, S. (2021). "Estimating dynamic treatment effects in event studies with heterogeneous treatment effects." *Journal of Econometrics*, 225(2), 175-199.
- Roth, J., Sant'Anna, P. H., Bilinski, A., & Poe, J. (2023). "What's trending in difference-in-differences? A synthesis of the recent econometrics literature." *Journal of Econometrics*, 235(2), 2218-2244.
