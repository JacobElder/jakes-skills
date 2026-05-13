# TWFE with Staggered Rollout: Is Your +6% Estimate Reliable?

Your reviewer is absolutely right to flag this, and yes, you should be worried. This is one of the most important methodological developments in econometrics over the past several years, and it directly applies to your setup. Let me walk through what's going on and what you should do about it.

---

## The Short Answer

Standard two-way fixed-effects (TWFE) with staggered treatment timing is **not equivalent** to a simple difference-in-differences estimator, even when the parallel trends assumption holds perfectly. The TWFE coefficient is a weighted average of many different 2x2 DiD comparisons — and crucially, some of those weights can be **negative**. This means your +6% estimate could be biased in direction and magnitude, or even have the wrong sign, under treatment effect heterogeneity.

---

## Why TWFE Works Fine in the Simple Case

In the canonical DiD setup — two groups (treated and control), two time periods (before and after) — TWFE gives you exactly the average treatment effect on the treated (ATT). The "treatment" coefficient cleanly captures the within-group, within-time variation attributable to the intervention.

The problems emerge when you have **variation in treatment timing**.

---

## What TWFE Actually Does With Staggered Rollout

When treatment rolls out at different times across units, TWFE implicitly makes comparisons that are not just "treated vs. never-treated." It uses:

1. **Early-treated units as controls for late-treated units** — comparing your Q1-treated regions against your Q3 and Q4 regions *after Q3/Q4 has been treated*.
2. **Late-treated units as controls for early-treated units** — comparing your Q3/Q4 regions against Q1 regions in the pre-treatment periods for Q3/Q4.

The second type of comparison is the problematic one. Your Q1-treated regions are being used as a "clean comparison group" for Q3-treated regions — but they have already received treatment. You are effectively measuring the effect of *receiving treatment later vs. earlier*, not treatment vs. no treatment.

**The Goodman-Bacon (2021) decomposition** formalizes this. He shows that the TWFE estimator can be written as a weighted average of all possible 2x2 DiD comparisons, where the weights depend on:
- Group sizes
- Time spent in each treatment status
- Variance of the treatment indicator

Some of these weights are negative — specifically, comparisons that use already-treated units as the control group get negative weights when treatment effects are heterogeneous over time (i.e., treatment effects grow or evolve after adoption).

---

## Your Specific Setup

You have three treatment cohorts:
- **15 regions treated in Q1** (earliest adopters)
- **20 regions treated in Q3**
- **10 regions treated in Q4**

Assuming your study runs 18 months (roughly Q1 through Q6), the TWFE estimator will implicitly use comparisons like:

| Comparison | What it estimates |
|---|---|
| Q3 cohort vs. not-yet-treated pre-Q3 | Clean ATT for Q3 cohort |
| Q4 cohort vs. not-yet-treated pre-Q4 | Clean ATT for Q4 cohort |
| Q1 cohort vs. not-yet-treated pre-Q1 | Clean ATT for Q1 cohort |
| Q3 cohort vs. Q1 cohort (post-Q1, pre-Q3) | Pre-trend check for Q3; valid |
| Q4 cohort vs. Q1 cohort (post-Q1, pre-Q4) | Contaminated if Q1 effects evolve |
| Q4 cohort vs. Q3 cohort (post-Q3, pre-Q4) | Contaminated if Q3 effects evolve |

If your customer success program's effect on renewal rate is **dynamic** — meaning it takes several quarters to fully materialize, or the effect grows or decays over time — the "forbidden comparisons" using already-treated units as controls will contaminate your estimate.

**The +6% number could be**:
- Biased downward if treatment effects grow over time (early-treated regions look better and better, making them poor controls for later cohorts)
- Biased upward if there are diminishing returns
- Attenuated or amplified depending on the composition of the contaminated comparisons

With only 45 total regions and staggered cohorts of 15/20/10, the contaminated comparisons involving already-treated units as controls will carry non-trivial weight in your overall estimate.

---

## Is Parallel Trends Enough?

Your reviewer's framing is exactly right: **parallel trends is not sufficient** to save you here. Parallel trends rules out selection bias and ensures pre-treatment trends are comparable. But the negative-weights problem arises from **treatment effect heterogeneity across cohorts or over time**, not from violations of parallel trends.

Formally, TWFE recovers the true ATT if and only if treatment effects are **homogeneous** across:
- Cohorts (Q1, Q3, Q4 adopters all experience the same +X% effect)
- Time periods (the effect does not grow, decay, or change after adoption)

Both of these are strong assumptions that you should test empirically, not take on faith.

---

## Concrete Illustration

Imagine the truth is:
- Cohort Q1 effect: +10% (largest because these were the most prepared regions)
- Cohort Q3 effect: +5%
- Cohort Q4 effect: +3%

The true size-weighted ATT is approximately: (15 x 10 + 20 x 5 + 10 x 3) / 45 = (150 + 100 + 30) / 45 = **+6.2%**

TWFE might accidentally report close to the right number here. But now imagine:
- Cohort Q1 effect: +2% (small because these regions had structural barriers)
- Cohort Q3 effect: +7%
- Cohort Q4 effect: +12%

The true ATT is approximately (15 x 2 + 20 x 7 + 10 x 12) / 45 = **+6.4%**

But if TWFE uses Q1 (already treated, with a growing effect) as a control for Q3 and Q4, it detects the *difference* between Q3/Q4's outcomes and Q1's already-rising outcomes — potentially underestimating the true effects for later cohorts. TWFE could plausibly report +6% in both scenarios, but the underlying reality and the policy implications are completely different.

---

## What the Reviewer Is Specifically Right About

The reviewer's statement is precisely the formal result established in:

- **Goodman-Bacon (2021)**: Decomposed TWFE into a weighted sum of 2x2 DiDs, showing negative weights arise when treatment effects are heterogeneous across cohorts or over time.
- **Callaway & Sant'Anna (2021)**: Proposed a cohort-specific ATT estimator that avoids forbidden comparisons entirely.
- **Sun & Abraham (2021)**: Proposed an interaction-weighted estimator that corrects for heterogeneous treatment effect bias.
- **de Chaisemartin & D'Haultfoeuille (2020)**: Characterized the conditions under which TWFE is consistent and proposed a robust first-difference alternative.

The key insight across all of these: the parallel trends assumption is about potential outcomes — what would have happened absent treatment. TWFE's bias is not about that assumption being wrong. It is about TWFE making additional implicit assumptions (homogeneous effects, no dynamics) that are entirely separate from parallel trends, and that you did not sign up for when you wrote down your regression equation.

---

## Diagnosing the Problem in Your Data

Before choosing a remedy, run these diagnostics:

### 1. Goodman-Bacon Decomposition

The `bacondecomp` package in Stata or R will decompose your TWFE estimate into its constituent 2x2 comparisons and show you:
- Which comparisons have negative weights
- What fraction of your estimate comes from "forbidden" comparisons (later-treated vs. earlier-treated)
- Whether the individual 2x2 estimates are qualitatively consistent with each other

If the sub-estimates are all around +6% with positive weights, TWFE is probably fine in practice. If there is wild heterogeneity or negative weights dominate, you have a serious problem.

### 2. Event Study Plots by Cohort

Rather than a single post-treatment indicator, estimate cohort-specific event studies: for each cohort, plot average outcomes from several periods before treatment through several periods after. This lets you:
- Visually verify parallel trends pre-treatment (flat pre-trends by cohort)
- Assess whether treatment effects are growing, stable, or decaying over time
- Identify heterogeneity across cohorts

### 3. Check for Early-Adopter Selection

In your setting, the Q1 regions were presumably chosen or assigned first. Were they higher-performing to begin with? Faster-growing? More engaged? If so, you may have both a TWFE mechanics problem and a selection problem layered on top of it.

---

## The Fix: Modern Staggered DiD Estimators

You should replace TWFE with one of the following robust estimators. They all share the same core logic: estimate cohort-specific treatment effects using only clean (not-yet-treated or never-treated) controls, then aggregate transparently.

### Option 1: Callaway & Sant'Anna (2021) — Recommended for Your Case

This estimator computes ATT(g, t) — the average treatment effect for cohort g (defined by when they were first treated) at time period t. You can then aggregate these into:
- An overall ATT
- A cohort-weighted ATT
- An event-time ATT (effect at k periods post-treatment)

**Why it is well-suited for your situation**: With 45 total regions and three cohorts, you have enough observations per cohort to estimate meaningful cohort-specific effects. The `did` package in R or `csdid` in Stata implements this. The estimator is well-documented, and the output is easy to interpret for stakeholders.

### Option 2: Sun & Abraham (2021)

This is implemented as a modified OLS regression with cohort-by-event-time interactions. It is compatible with standard regression software and produces clean interaction-weighted estimates that average only over valid comparisons. The `sunab` command in Stata or the `fixest` package in R implements this efficiently.

### Option 3: de Chaisemartin & D'Haultfoeuille (2020)

The `did_multiplegt` command in Stata estimates a "first difference" DiD that is robust to heterogeneous effects and requires minimal functional form assumptions. Good as a robustness check alongside the others.

### Which Control Group to Use

In your setup, you have no "never-treated" control group — all 45 regions eventually receive the program. This is common. Your options:

1. **Not-yet-treated as controls**: Use regions that have not received treatment yet as controls for regions that have. This is the default in most staggered estimators. Valid if there are no anticipation effects (regions don't start changing behavior before the program officially launches).
2. **Last-treated cohort as pseudo-control**: Your Q4 cohort (treated late in the study) can serve as a near-clean control for Q1 during the middle of the study period, if their pre-treatment period is long enough to establish parallel trends.

---

## Practical Recommendations

Given your setup, here is what I would do:

1. **Run the Goodman-Bacon decomposition first.** This is fast and gives immediate diagnostic insight. If the 2x2 sub-estimates are tightly clustered around +6% with all-positive weights, your TWFE estimate is likely credible and the reviewer's concern is moot in practice — even if technically valid in general.

2. **Estimate cohort-specific event studies.** You have 15, 20, and 10 regions per cohort — enough to run separate pre/post regressions with not-yet-treated controls. Plot these. Do pre-trends look flat? Do post-treatment effects look similar across cohorts?

3. **Re-estimate using Callaway & Sant'Anna or Sun & Abraham.** Report these as your primary estimates. If they yield approximately +6% as well, you have strong evidence your TWFE estimate was not badly biased in this particular case. If they diverge substantially, the robust estimates should be preferred.

4. **Report heterogeneity.** Even if the overall ATT is similar, the cohort-specific estimates are substantively interesting: did the program work better in regions that received it earlier? Does the effect grow over time? These are actionable findings for any future rollout decisions.

5. **Address the selection concern explicitly.** If Q1 regions were chosen because they were highest-priority or most ready, compare their pre-treatment trends and baseline renewal rates to Q3 and Q4 regions. If they were already on a better trajectory, parallel trends may be violated for some comparisons, which is a separate and more fundamental problem than the TWFE mechanics issue.

---

## Summary Assessment of Your Situation

| Concern | Severity | Action Required |
|---|---|---|
| TWFE mechanics bias from staggered rollout | Moderate — possible but unknown | Run Goodman-Bacon decomposition; re-estimate with robust DiD |
| Heterogeneous treatment effects across cohorts | Likely — early vs. late adopters plausibly differ | Estimate and report cohort-specific effects |
| No never-treated control group | Present — use not-yet-treated as controls | Handled by modern estimators; verify no anticipation effects |
| Selection into early adoption | Unknown — depends on how cohorts were assigned | Document assignment mechanism; compare pre-treatment trends by cohort |
| Dynamic treatment effects (effect grows or decays over time) | Plausible — customer success programs often have a ramp-up period | Event study plots by cohort |

**Bottom line**: The reviewer is correct, and the concern is practically relevant in your setting. You have staggered rollout, likely heterogeneous treatment effects, and no never-treated control. These are exactly the conditions that motivate the recent staggered DiD literature. The +6% TWFE estimate is not necessarily wrong, but you cannot currently vouch for it. Running the Goodman-Bacon decomposition and Callaway & Sant'Anna estimator will take a few hours and will tell you whether your estimate is robust or needs revision. Given that a program rollout decision hangs on this number, the additional analysis is worth doing.

---

## Key References

- Goodman-Bacon, A. (2021). "Difference-in-differences with variation in treatment timing." *Journal of Econometrics*, 225(2), 254-277.
- Callaway, B., & Sant'Anna, P. H. C. (2021). "Difference-in-differences with multiple time periods." *Journal of Econometrics*, 225(2), 200-230.
- Sun, L., & Abraham, S. (2021). "Estimating dynamic treatment effects in event studies with heterogeneous treatment effects." *Journal of Econometrics*, 225(2), 175-199.
- de Chaisemartin, C., & D'Haultfoeuille, X. (2020). "Two-way fixed effects estimators with heterogeneous treatment effects." *American Economic Review*, 110(9), 2964-2996.
- Roth, J., Sant'Anna, P., Bilinski, A., & Poe, J. (2023). "What's trending in difference-in-differences? A synthesis of the recent econometrics literature." *Journal of Econometrics*, 235(2), 2218-2244.
