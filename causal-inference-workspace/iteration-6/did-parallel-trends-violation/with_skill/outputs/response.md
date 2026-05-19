# TWFE with Staggered Rollout: Is Your +6% Estimate Biased?

**Short answer:** Your reviewer is exactly right. TWFE with staggered treatment timing can produce biased estimates even when parallel trends holds perfectly for every cohort. You should be worried — and you should move to a modern staggered DiD estimator before reporting this result.

---

## 1. What Rung Are We On?

This is a **rung 2 (intervention)** question: "What is the causal effect of the customer success program on renewal rates?" You have a natural experiment — the program was rolled out in stages across regions — and you're asking whether that program causally improved renewal rates.

The question is correctly causal. The TWFE design is intended as a design-based identification strategy (DiD). The issue is that the *estimator* fails to correctly aggregate cohort-level causal effects in the staggered setting, even when the identification assumption holds.

---

## 2. The DAG (Briefly)

```
   Cohort (Q1/Q3/Q4)
      ↓
   Treatment timing ──→ Renewal rate
      ↑                    ↑
   Region FE          Time FE + trends
```

- Region fixed effects absorb time-invariant differences between regions (baseline renewal rates, size, market maturity).
- Time fixed effects absorb shared macro shocks that hit all regions equally in a given quarter.
- The "treated" dummy captures the post-program period within each region.

The parallel trends assumption here is: in the absence of the program, each region's renewal rate would have evolved identically to the overall time trend. With staggered rollout, this must hold separately for each adoption cohort (Q1, Q3, Q4 adopters).

This assumption is plausible on its face, and nothing in the description breaks it. But the *bias problem your reviewer is flagging is not a parallel-trends violation* — it's a problem with how TWFE aggregates information across cohorts when treatment timing differs.

---

## 3. The Core Problem: TWFE Uses Already-Treated Units as Controls

In a canonical 2x2 DiD (one treated group, one never-treated group, one pre and one post period), TWFE is unbiased and intuitive.

In a staggered rollout, TWFE implicitly constructs comparisons that go beyond "treated vs. never-treated." Specifically, it uses **already-treated regions as controls for later-treated regions**. This is the Callaway-Sant'Anna / Goodman-Bacon insight:

- When estimating the Q3 cohort's effect, TWFE partially compares Q3 adopters (post-treatment) against Q1 adopters (also post-treatment by Q3).
- The Q1 adopters' outcome in Q3 already reflects the program's effect on them.
- If the program's effect grew over time (or differed across cohorts), the Q1 adopters' outcome is a *contaminated* counterfactual for Q3 adopters.

The Goodman-Bacon decomposition shows that the TWFE coefficient is a **weighted average of all pairwise 2x2 DiD estimates** — including "forbidden comparisons" where a late-treated group is compared to an early-treated group using post-treatment periods for both. The weights can even be **negative** — meaning a cohort with a positive treatment effect can *subtract* from the TWFE estimate rather than add to it. In extreme cases the TWFE coefficient can have the wrong sign even if every cohort has a positive effect.

**In your setup:**
- 15 regions treated in Q1 (early cohort)
- 20 regions treated in Q3 (middle cohort)
- 10 regions treated in Q4 (late cohort)
- No never-treated control group is mentioned

The absence of a never-treated group is particularly important. With no clean control group, TWFE relies entirely on within-group timing variation and these contaminated cross-cohort comparisons. This is the highest-risk configuration for TWFE bias.

---

## 4. When Is the Bias Large?

The TWFE bias depends on two factors:

1. **Effect heterogeneity across cohorts.** If the program has exactly the same effect for Q1, Q3, and Q4 adopters, the bias is zero even with staggered timing — the forbidden comparisons cancel out. If the program is more effective when adopted early (perhaps early-adopter regions are more receptive, or the program improved over time), the bias is meaningful.

2. **Dynamic treatment effects.** If the effect grows over time within a cohort — renewal rates improve more in Q4 and Q5 after adoption than in Q1 and Q2 — then using early-treated regions as controls for later-treated regions contaminates the comparison, because the early-treated regions' outcomes are already elevated and still climbing.

Both of these are plausible in a customer success program context:
- Early-adopter regions may have been chosen for high receptivity (selection effect → cohort heterogeneity).
- Customer success programs often take time to fully deploy and train staff, so effects likely accumulate over quarters.

---

## 5. What to Do Instead

Modern estimators recover unbiased cohort-average treatment effects (CATTs) and then aggregate them properly. The recommended path:

### Step 1: Goodman-Bacon Decomposition
Run this first (available in Stata as `bacondecomp`, in R as `bacondecomp`). It decomposes your TWFE coefficient into all constituent 2x2 DiD comparisons and their weights. This tells you:
- How much of your +6% comes from clean comparisons (early cohort vs. late cohort, pre-treatment) vs. contaminated comparisons.
- Whether any weights are negative.
- How much the estimate would change if you excluded the problematic comparisons.

### Step 2: Adopt a Robust Staggered DiD Estimator
Several estimators are designed specifically for staggered rollout. The most practical choices:

| Estimator | Best for | Implementation |
|-----------|----------|---------------|
| Callaway & Sant'Anna (2021) | No never-treated group; nonparametric | R: `did` package |
| Sun & Abraham (2021) | Interaction-weighted, parametric regression | R/Stata: `eventstudyinteract` |
| de Chaisemartin & D'Haultfoeuille (2020) | Very general; allows effect dynamics | R/Stata: `did_multiplegt` |
| Borusyak, Jaravel & Spiess (2024) | Imputation-based; efficient | R: `didimputation` |

All of these compute cohort-by-period average treatment effects (ATT(g,t) in Callaway-Sant'Anna notation) and then aggregate them into an overall average effect. They avoid the forbidden comparisons that contaminate TWFE.

### Step 3: Event Study Plots
Plot the treatment effect for each cohort in the periods before and after adoption. The pre-adoption periods are falsification tests — if treatment effects appear before the program launched in a given cohort's regions, parallel trends is violated for that cohort. Flat pre-trends are not proof of validity but they are a necessary condition.

---

## 6. No Never-Treated Group: The Additional Complication

Your design has no control group that never received the program. This matters because:

- Every comparison must come from timing variation alone.
- Callaway-Sant'Anna requires choosing a "clean comparison group" — either never-treated units or not-yet-treated units. With no never-treated units, you're using not-yet-treated as the control, which is valid but requires that later cohorts' outcomes in early periods accurately represent what early cohorts would have done without treatment.
- This is a stronger assumption than having never-treated controls.

If you have any regions that received the program very late (e.g., not until Q6 or later), they can serve as the effective control group in the early periods. If all 45 regions were treated by Q4 of an 18-month window, the identifiable window is narrow.

**Consider:** Is there any possibility of expanding the analysis to regions that didn't receive the program yet? Even a small holdout group substantially strengthens the identification.

---

## 7. What the +6% Estimate Actually Means

Under staggered TWFE, the +6% is a particular weighted average — but the weights may not reflect a quantity you care about. Specifically:

- It is **not** the ATT (average treatment effect on the treated regions) unless effects are homogeneous across cohorts.
- It may **overstate** the effect if early adopters (who get more weight in the TWFE because they have longer post-treatment windows) had larger effects.
- It may **understate** — or even reverse-sign — the effect if cohort effects are heterogeneous and negative weights dominate.

The Callaway-Sant'Anna approach would give you:
- **ATT(g=Q1, t=quarter):** the effect on the 15 Q1-adopter regions, separately by quarter.
- **ATT(g=Q3, t=quarter):** the effect on the 20 Q3-adopter regions, separately by quarter.
- **ATT(g=Q4, t=quarter):** the effect on the 10 Q4-adopter regions, separately by quarter.
- An aggregate **ATT** that weights these proportionally to cohort size — which is what a business decision-maker actually wants.

---

## 8. Summary Diagnosis

| Question | Answer |
|----------|--------|
| Is the reviewer right that TWFE can bias estimates even when parallel trends holds? | Yes — this is a well-established result (Callaway & Sant'Anna 2021, Goodman-Bacon 2021, Sun & Abraham 2021). |
| Should you be worried about your specific setup? | Yes. Staggered timing across 3 cohorts, no never-treated group, and a program where dynamic effects are likely — this is a high-risk configuration. |
| Does this mean the true effect is not +6%? | Not necessarily — but you can't know without running the robust estimator. The +6% may be an over- or underestimate. |
| Can you still use your region and time fixed effects? | Yes — the modern estimators still use region and time fixed effects. The change is in how the cohort-level comparisons are aggregated, not in whether you control for region and time. |
| Is this a parallel trends violation? | No. This bias arises **even when parallel trends holds for every cohort**. The two problems are distinct. Your reviewer may be conflating them, but they're correct that TWFE is unreliable here. |

---

## 9. Recommended Action

1. **Immediately:** Run the Goodman-Bacon decomposition on your existing TWFE to see how much of the estimate comes from contaminated comparisons.
2. **Primary analysis:** Rerun using Callaway & Sant'Anna (or Sun & Abraham) with not-yet-treated as the control group.
3. **Robustness:** Plot event-study estimates for each cohort to check pre-trends and characterize dynamics.
4. **Report:** Report the cohort-level ATTs alongside the aggregate ATT. If they're all positive and similar in magnitude, the +6% is likely directionally correct. If they're heterogeneous, that heterogeneity is itself a finding worth reporting.

The infrastructure cost here is low — this is a one-day analysis in R or Stata with existing packages. The credibility payoff is high: a result that survives the known failure mode of staggered TWFE is substantially more defensible to a sophisticated audience than the raw TWFE estimate.
