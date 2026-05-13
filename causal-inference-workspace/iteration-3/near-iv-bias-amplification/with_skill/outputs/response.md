# Causal Analysis: Executive Mentorship and Promotion Rates

## The Question

Should you control for prior performance when estimating the causal effect of executive mentorship on promotion rates, given that mentorship is almost exclusively given to high performers (r ≈ 0.85 between prior performance and mentorship receipt)?

The short answer: **controlling for prior performance is the right instinct structurally, but the near-perfect correlation between prior performance and mentorship creates a separate, serious problem that your colleague's advice does not address — and that problem can make your estimate worse, not better.**

---

## Step 1: Name the Rung

This is a **Rung 2 (Intervention) question**: "What would happen to promotion rates if we intervened on mentorship receipt?" You want to know P(Promotion | do(Mentorship = 1)) − P(Promotion | do(Mentorship = 0)).

The data is observational — mentorship was not randomly assigned. That gap between rung-2 question and rung-1 data is exactly where the difficulty lives.

---

## Step 2: Sketch the DAG

The core structure described in the problem:

```
Prior Performance (P)
     ↙              ↘
Mentorship (M)  →  Promotion (Y)
```

Prior performance is a **classic fork (confounder)**: it causes both mentorship assignment and promotion outcomes directly. The back-door path is:

```
M ← P → Y
```

This spurious path inflates the observed correlation between mentorship and promotions — high performers get mentorship *and* get promoted, regardless of what mentorship does.

Your colleague is correct that P is a confounder and that you need to close this back-door path. **In the abstract, controlling for prior performance is the right structural move.**

---

## Step 3: The Near-Instrument Problem

Here is where the advice breaks down in practice.

The correlation between prior performance and mentorship is 0.85. That means prior performance is an extremely strong predictor of treatment (mentorship). This is the defining feature of a **near-instrument** — a variable that is heavily predictive of treatment but has a weaker direct relationship to the outcome independent of the treatment path.

The bias amplification structure is:

```
Prior Performance (P) → Mentorship (M) → Promotion (Y)
                                ↑
                                U (unobserved confounder)
                                ↓
                              Promotion (Y)
```

What is U? Think about variables that predict who gets mentored — beyond prior performance — and also predict promotions. Plausible candidates: visibility to senior leadership, social capital and network, likability or cultural fit, volunteering for high-profile projects, having a sponsor who advocates informally. These are likely imperfectly captured by any single "prior performance" measure.

**Conditioning on prior performance removes prior performance's contribution to variation in mentorship.** The residual variation in mentorship — the part that remains after controlling for prior performance — is now disproportionately driven by U, those unmeasured confounders. They become *stronger* confounders in the adjusted regression than they were in the unadjusted one.

This is bias amplification. The mechanism from the controls taxonomy:

> Conditioning on Z removes Z's contribution to X's variation. The remaining variation in X is now disproportionately driven by U, the unmeasured confounder. U becomes a stronger confounder than it was unconditionally.

The more extreme the correlation between the near-instrument and treatment, the worse the amplification. At r = 0.85, you are conditioning out the dominant source of variation in mentorship assignment. What is left is almost entirely noise plus unmeasured factors — and those unmeasured factors are exactly the ones you have not controlled for.

**Practical consequence:** The adjusted estimate can be *further* from the true causal effect than the unadjusted estimate, even though controlling for prior performance is structurally the correct intent.

---

## Step 4: Classify Prior Performance by Structural Role

Applying the per-variable classification:

| Role | Verdict |
|------|---------|
| Confounder (fork: P → M and P → Y)? | Yes — **should control** |
| Mediator on M → Y path? | No — prior performance predates mentorship |
| Collider? | No |
| Strong predictor of treatment, weaker on outcome — near-instrument? | **Yes, r = 0.85** — controlling amplifies bias from U |

Prior performance is simultaneously a genuine confounder *and* a near-instrument. The two properties create a genuine tension. The correct-sounding advice ("control for the confounder") ignores that the near-instrument property makes conditioning hazardous when unmeasured confounding is likely.

---

## Step 5: The Structural Verdict

Controlling for prior performance is the right move **if and only if** prior performance fully captures all the confounding. If it does — if there are no remaining unmeasured U variables after conditioning — then adjusting for P closes the back-door and your estimate is valid.

But at r = 0.85, you face a near-total selection problem. The residual variation in mentorship after conditioning on prior performance is tiny, and the employees who received mentorship despite lower prior performance, or who didn't receive it despite high prior performance, are almost certainly a non-representative group selected on exactly the unmeasured factors you cannot control. The "clean variation" you are trying to use to identify the mentorship effect is contaminated.

---

## Step 6: What to Do Instead

### Option A: Instrument for mentorship

Find a variable Z that:
1. Predicts mentorship receipt (relevance)
2. Has no direct effect on promotion independent of mentorship (exclusion)
3. Is exogenous — shares no confounders with promotion (exogeneity)

Candidates: whether a senior executive had an open mentorship slot due to factors unrelated to performance (e.g., organizational restructuring, an executive's workload changes, random assignment of mentees in a formal program, mentor availability), or whether an employee was geographically co-located with a senior executive at a time unrelated to their performance.

If a portion of mentorship assignments were made through any mechanism that didn't prioritize prior performance (program lotteries, geographic proximity, time-of-hire cohort effects), that variation can serve as an instrument. Use it.

### Option B: Exploit a formal mentorship program with structured assignment

If your organization has any period or cohort where mentorship was assigned through a more structured or systematic process (rotation, cohort programs, lottery-based slots), treat that as a near-natural experiment. Compare outcomes within that cohort rather than in the general population where selection is almost entirely on prior performance.

### Option C: Differences-in-differences around program initiation

If a formal mentorship program was introduced at a specific time, you can compare pre/post promotion trajectories for eligible employees vs. ineligible employees, under the parallel trends assumption. This handles time-invariant confounders (including stable "prior performance" levels) by design.

### Option D: Sensitivity analysis

If you proceed with back-door adjustment despite the concerns above, run a sensitivity analysis to quantify how strong an unmeasured confounder U would need to be to explain away your estimate. Given the near-instrument properties of prior performance, a plausible U with moderate correlation with both mentorship and promotion is enough to fully overturn the result. Report that explicitly. If the estimate is only defensible under assumptions of near-zero residual confounding, say so.

### Option E: Bound the effect

With the current data structure, you may not be able to point-identify the causal effect. Compute sharp bounds on the causal effect given plausible assumptions about U's strength. A credible range is more useful than a single precise-but-wrong number.

---

## The Core Diagnostic

Before accepting your colleague's advice, ask this question: **after conditioning on prior performance, what drives the remaining variation in mentorship receipt?**

If the answer is "essentially random noise and unmeasured factors like informal sponsorship, visibility, and social capital" — which is highly plausible at r = 0.85 — then you have conditioned away the part of mentorship variation that is relatively clean and left the part that is maximally contaminated. The adjusted regression's identification now rests entirely on those residual, unmeasured factors being uncorrelated with promotion, which is probably false.

Your colleague's structural intuition (prior performance is a confounder, control for it) is correct. The operational advice (just put it in the regression) fails because it ignores bias amplification under near-perfect selection on observables.

---

## Summary

| Question | Answer |
|----------|--------|
| Is prior performance a confounder? | Yes — it causes both mentorship and promotion |
| Should you control for it in principle? | Yes, if all confounding runs through it |
| Is the near-instrument property a problem? | Yes — r = 0.85 triggers bias amplification when residual unmeasured confounders exist |
| Will controlling for prior performance fix the problem? | Only if prior performance is a perfect or near-perfect proxy for *all* confounders, which is unlikely |
| What should you do? | Seek an instrument, exploit a formal program's structured assignment, use DiD, or at minimum report sensitivity analysis |

The right causal question here is: among employees with identical measured prior performance, does mentorship still raise promotion rates? At r = 0.85, that comparison involves so few such employees — and they are so unusual — that regression adjustment cannot reliably answer it. You need a cleaner source of variation in mentorship receipt.
