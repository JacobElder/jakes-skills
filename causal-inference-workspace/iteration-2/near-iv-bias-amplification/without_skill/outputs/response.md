# Causal Inference: Controlling for Prior Performance in Mentorship-Promotion Analysis

## Short Answer

Your colleague's intuition is directionally correct — prior performance is a confounder and generally should be controlled for — but the situation is more nuanced and potentially dangerous than a simple "yes, control for it" answer. Because prior performance is so strongly correlated with mentorship receipt (r ≈ 0.85), controlling for it triggers a phenomenon called **bias amplification**, which can make your estimate of the mentorship effect *worse*, not better, under certain conditions.

---

## The Causal Structure

Let's name the variables:

- **P** = Prior performance
- **M** = Mentorship receipt (treatment)
- **Y** = Promotion (outcome)
- **U** = Unmeasured confounders (ambition, visibility, social capital, manager sponsorship, etc.)

The causal diagram you've described is:

```
P ──────────────────► Y
│                     ▲
│                     │
└──────► M ───────────┘
              ▲
              │
U ────────────┴──────► Y
```

Prior performance causes both mentorship receipt (the selection mechanism) and promotion directly. This is a classic **confounding** structure. The backdoor path from M to Y running through P is:

```
M ← P → Y
```

Controlling for P blocks this path, which is the goal. So far, your colleague is right.

---

## Why This Gets Complicated: Near-Instrument and Bias Amplification

Here's the critical issue. When the correlation between P and M is 0.85, P is functioning as a **near-instrument** for M — meaning it predicts treatment very strongly. This creates a specific bias amplification problem in the presence of unmeasured confounders U.

### The Bias Amplification Mechanism

Consider what happens when you condition on P in a regression of Y on M:

- You remove the variance in M that is explained by P. After conditioning on P, what remains of M is mostly **noise** — the idiosyncratic, unexplained variation in who got mentorship.
- If there is any unmeasured confounder U (e.g., social capital, manager favoritism, ambition) that predicts both M and Y, controlling for P can **amplify the bias** from U.

The formal result (Wooldridge 2009, Myers et al. 2011) shows that in a linear model:

**Bias after controlling for X ∝ (confounding from U) / (1 - R²_{X→T})**

When X is a near-instrument (R²_{X→T} → 1), the denominator approaches zero and bias is amplified. With your r = 0.85, R² ≈ 0.72 — large enough to produce meaningful amplification.

The intuition: Controlling for prior performance removes the "legitimate" variance in who got mentored — the part explained by performance. What remains is almost entirely driven by hidden factors U (ambition, visibility, sponsor relationships). Those hidden factors also drive promotions. You have conditioned away the clean variation and left only the contaminated variation.

---

## The Practical Risk in Your Setting

With r(P, M) = 0.85, roughly 72% of the variance in M is explained by P. After controlling for P, the effective comparison you're making is: among employees with similar prior performance, who got mentorship vs. who didn't? But the reason two equally high performers differed in mentorship receipt is almost certainly driven by unobservables — exactly the kinds of factors (visibility, political capital, sponsor advocacy) that also drive promotions.

This means:

1. **If P fully captures all confounding** — controlling for P gives an unbiased estimate. Good.
2. **If residual unobserved confounders exist** (almost certainly true in real organizations) — controlling for P amplifies their bias.

You are almost certainly in scenario 2.

---

## What You Should Do

### 1. Reconsider the identification strategy

With r(P, M) = 0.85, you have very limited exogenous variation in M conditional on P. This is a fundamental identification problem. Consider:

- **Regression discontinuity**: Is there a threshold in performance scores that determines mentorship eligibility? RD around that threshold gives clean identification.
- **Instrumental variables**: Is there a variable that affects mentorship assignment but has no direct effect on promotion? Examples: mentor availability constraints, randomized pilot programs, cohort-level capacity limits.
- **Difference-in-differences**: If mentorship programs were rolled out at different times across teams or divisions, variation in timing provides identification.

### 2. If you must use regression adjustment

- Include P but be explicit that you are relying on the **no unmeasured confounders conditional on P** assumption, and argue carefully why this is plausible.
- Conduct a **sensitivity analysis** (Rosenbaum bounds or E-values) to quantify how strong an unobserved confounder would need to be to explain away your estimated effect.
- The E-value framework (VanderWeele & Ding 2017) is particularly useful: it tells you the minimum association strength an unmeasured confounder would need to have with both treatment and outcome to fully explain your estimated effect.

### 3. Check for common support

Since treatment is highly predictable from P, propensity score analysis can reveal whether there are actually employees with similar propensity scores who both did and did not receive mentorship. With r = 0.85, common support may be very thin or nonexistent — nearly all high performers got mentorship; nearly no low performers did. If common support is thin, your causal estimate is only valid for a narrow slice of employees and relies heavily on model extrapolation.

---

## Summary

| Question | Answer |
|---|---|
| Is prior performance a confounder? | Yes — it causes both mentorship and promotion. |
| Should you control for it? | Generally yes, but with important caveats. |
| Is controlling for it sufficient? | Almost certainly not — unmeasured confounders likely remain. |
| Can controlling for it make things worse? | Yes — with r = 0.85, it is a near-instrument, and controlling for near-instruments amplifies bias from residual unmeasured confounding. |
| What is the best path forward? | Control for P plus other observed confounders; run sensitivity analyses; pursue quasi-experimental designs if feasible. |

**The core lesson:** Controlling for confounders is necessary but not sufficient, and controlling for near-instruments in the presence of unmeasured confounding is actively dangerous. A clean causal estimate here requires either a strong and well-defended assumption that P captures all confounding, or a design that creates genuine quasi-random variation in mentorship assignment.

---

## Key References

- Wooldridge, J.M. (2009). Should instrumental variables be used as matching variables? *Research in Economics*.
- Myers, J.A. et al. (2011). Effects of adjusting for instrumental variables on bias and precision of effect estimates. *American Journal of Epidemiology*, 174(11).
- VanderWeele, T.J. & Ding, P. (2017). Sensitivity analysis in observational research: Introducing the E-value. *Annals of Internal Medicine*, 167(4).
- Ding, P. & Miratrix, L.W. (2015). To adjust or not to adjust? Sensitivity analysis of M-bias and butterfly-bias. *Journal of Causal Inference*, 3(1).
