# TWFE with Staggered Rollout: Is Your +6% Estimate Reliable?

Your reviewer is correct, and yes, you should be worried — though not necessarily panicked. Let me walk through exactly what's happening, why it happens even when parallel trends holds, what your specific design's exposure looks like, and what you should do instead.

---

## 1. What rung of causation are you on, and why it matters here

Your question is firmly **Rung 2 (Intervention)**: you want to know what the customer success program *causes* to happen to renewal rates — P(renewal | do(program)) — not merely what's associated with renewal. Differences-in-differences is a design-based strategy specifically aimed at this rung. The problem is not that DiD is wrong for your question; it's that the standard TWFE implementation is defective in your specific design.

The DAG underlying your evaluation looks roughly like this:

```
RegionCharacteristics --> TreatmentTiming --> Treated --> RenewalRate
                     \___________________________________/^
                                                         |
                     TimePeriod ---> CommonTrend --------+
```

Region fixed effects absorb stable between-region differences. Time fixed effects absorb common trends. The assumption is that after those two adjustments, variation in `Treated` is as-good-as-random. Whether that's true is the parallel trends question. But even if it *is* true, TWFE does something else wrong with staggered rollout — and that's the mechanism your reviewer is flagging.

---

## 2. Why standard TWFE breaks under staggered rollout — even with valid parallel trends

This is one of the most important recent discoveries in applied econometrics (Callaway & Sant'Anna 2021; Goodman-Bacon 2021; de Chaisemartin & D'Haultfoeuille 2020). Here's the core intuition.

### What TWFE is actually computing under the hood

Standard TWFE with a single binary `treated` indicator uses every available 2×2 DiD comparison it can construct from your panel:

1. **Clean comparisons (good):** Early adopters (Q1 cohort) vs. not-yet-treated regions, in periods before the later cohorts receive treatment.
2. **Contaminated comparisons (the problem):** Already-treated early adopters (Q1 cohort) used as the *control group* when estimating the effect for later adopters (Q3 or Q4 cohorts).

That second type is the fundamental problem. TWFE implicitly treats previously-treated units as valid controls for units receiving treatment later. In the classical 2×2 DiD case — one treated group, one untreated group, one pre-period, one post-period — there are no previously-treated units to misuse, so this never arises. With staggered rollout, it's unavoidable.

### Why contaminated comparisons bias the estimate even under parallel trends

Parallel trends says: in the absence of treatment, all groups would have followed the same time trend. This assumption says nothing about *treatment effect homogeneity over time*.

If the customer success program's impact changes after regions have had it for a while — either growing (as customer success teams learn the system) or shrinking (as initial onboarding enthusiasm fades) — then the Q1 cohort's post-treatment trajectory is no longer a valid counterfactual for the Q3 cohort. The Q1 regions are already experiencing the program. When TWFE subtracts Q1-region trends to estimate Q3-region effects, it subtracts a *treated trajectory*, not a counterfactual untreated trajectory.

**The direction and magnitude of bias depend on how treatment effects evolve:**
- If early adopters' effects *grow over time* (learning curve in the program), TWFE will **underestimate** the true ATT for late adopters — it treats the rising early-adopter trajectory as a "control trend" and nets it out.
- If early adopters' effects *shrink over time* (honeymoon effect), TWFE will **overestimate** late-adopter effects — it interprets the declining early-adopter trajectory as if renewal rates are falling in the "control group," making the treated group look better by comparison.
- In extreme cases of treatment effect heterogeneity, TWFE can return a *negative* coefficient even when every cohort's true treatment effect is positive, because some implicit 2×2 DiD comparisons receive negative weight.

**Your +6% could be biased in either direction.** You cannot determine the direction or magnitude from the TWFE estimate alone.

---

## 3. The Goodman-Bacon decomposition: your specific exposure

Goodman-Bacon (2021) proves that the TWFE coefficient is a weighted average of all possible 2×2 DiD estimators. The weights are determined by group sizes and the variance in treatment timing — *not* by which comparisons are cleanest.

In your setting — 15 regions in Q1, 20 in Q3, 10 in Q4, and (based on your description) no never-treated group:

- You have **no never-treated group**, which eliminates the cleanest class of comparisons entirely.
- Every unit of identification comes from timing variation alone: not-yet-treated and already-treated regions serving as controls for each other.
- The Q1 cohort (15 regions, treated first, longest post-treatment window, largest pre-treatment variance relative to Q3 and Q4) will receive substantial weight as a *control group* for Q3 and Q4 estimates. Those comparisons are contaminated.
- With 18 months of panel data and Q1 treatment, the Q1 cohort accumulates 3–4 post-treatment quarters of data *before Q3 is treated* — that's a window where Q1 looks like a mature program and Q3 looks like untreated. After Q3 is treated, TWFE flips Q1 into the control role. This is exactly the structure that creates contamination.

The bias risk here is real and non-trivial. It is not a theoretical edge case — it is exactly the scenario that Goodman-Bacon's paper was designed to diagnose.

---

## 4. Clarify the estimand before choosing a method

Before picking an estimator, decide what you actually want to estimate. These are different quantities:

- **ATE (Average Treatment Effect):** What would the program do for a randomly selected region from the full population of regions, including types that haven't been given the program yet? This is what matters if you're deciding whether to expand to new regions.
- **ATT (Average Treatment Effect on the Treated):** Among the 45 regions that received the program, what did it do for *them*? This is what matters if you're evaluating whether the rollout was worth it.
- **Cohort-specific ATTs:** What did the program do for Q1 regions vs. Q3 regions vs. Q4 regions? These differ if region selection into early vs. late cohorts was non-random (which it almost certainly was — someone decided Q1 regions would get it first).

TWFE collapses all of these into a single weighted average with poorly understood weights. The modern estimators let you define the estimand first, then estimate it. For most program evaluation questions, the ATT is the right starting point.

---

## 5. What to do instead

### Step 1 — Run the Goodman-Bacon decomposition (diagnostic, not a fix)

Before anything else, decompose your TWFE estimate into its constituent 2×2 comparisons and their weights:

- **In Stata:** `bacondecomp renewal_rate treated, ddetail`
- **In R:** the `bacondecomp` package

This tells you: (a) what share of your estimate comes from "already-treated as control" comparisons, and (b) how heterogeneous the 2×2 estimates are across comparison types. If the contaminated comparisons have large weights and their estimates diverge substantially from the clean comparisons, your +6% is unreliable.

### Step 2 — Use a heterogeneity-robust estimator

Several estimators have been developed to handle staggered rollout correctly. The common thread: they only use clean comparisons (not-yet-treated or never-treated as controls) and then aggregate cohort-specific effects using a pre-specified, transparent weighting scheme.

**Callaway & Sant'Anna (2021) — recommended for your case**

Estimates the ATT for each cohort-by-period cell: "what is the average effect on Q1-cohort regions, 1 quarter after treatment?", "2 quarters after?", etc. You then aggregate into:
- An overall ATT (weighted average across cohort-time cells)
- A dynamic event-study plot (treatment effect by quarters-since-treatment)
- Cohort-specific ATTs (is Q1 different from Q3? Q4?)

Since you have no never-treated group, the "not-yet-treated" control option is the right choice — Q3 and Q4 regions serve as controls for Q1 before they're treated, and Q4 serves as control for Q3 before Q4 is treated. This is legitimate under parallel trends, but you're entirely dependent on timing variation for identification — state that limitation explicitly.

Available in R (`did` package, `att_gt()` function) and Stata (`csdid`).

**Sun & Abraham (2021)**

An interaction-weighted (IW) estimator that integrates into a standard regression framework and is easier to explain to stakeholders. Mechanically, replace the single `treated` indicator with interactions between cohort-membership indicators and event-time indicators, then aggregate using cohort shares. Available in R (`sunab()` inside the `fixest` package) and Stata (`eventstudyinteract`).

**de Chaisemartin & D'Haultfoeuille (2020)**

The `did_multiplegt` estimator. More conservative (uses first-difference comparisons by default), but robust to arbitrary treatment effect heterogeneity. Good as a robustness check against Callaway-Sant'Anna.

### Step 3 — Plot the event study (essential, not optional)

Regardless of estimator, produce an event-study plot: treatment effect by quarters-relative-to-treatment, for pre-treatment and post-treatment periods separately.

1. **Pre-trend test:** Pre-treatment period coefficients should be statistically indistinguishable from zero if parallel trends holds. Flat pre-trends are evidence (not proof) of a valid design. Sloping pre-trends are a warning sign that regions were already on divergent trajectories before treatment — that would undermine identification entirely, separately from the staggered-rollout bias discussed here.
2. **Dynamic effect pattern:** Post-treatment coefficients show whether effects grow, shrink, or plateau over time since treatment. This is substantively important (does the program get better as teams embed it, or is it one-time onboarding?) and directly tells you whether TWFE's homogeneity assumption was being violated.

Note: with TWFE, even the event-study version (replacing `treated` with lead/lag indicators) is contaminated by staggered adoption — the Sun-Abraham or Callaway-Sant'Anna event studies are the clean versions.

---

## 6. Interpreting your +6% in context

The +6% TWFE estimate is not meaningless — it's telling you *something* is happening. But without the diagnostics above, you cannot know whether it:

- Is approximately right (treatment effect heterogeneity across cohorts is small)
- Is an underestimate (early-adopter effects grew over time, TWFE netted out the growth as a "trend")
- Is an overestimate (early-adopter effects decayed, contaminating late-adopter estimates upward)
- Is masking large positive effects in some cohorts and near-zero in others

The most operationally valuable reframe: run Callaway-Sant'Anna, get cohort-specific ATTs, and look at whether the 18-month-in regions (Q1 cohort) have substantially different effects than the 6-month-in regions (Q4 cohort). That directly answers whether the program's value compounds over time or decays — which is strategically important for your rollout decision *regardless* of the TWFE debate.

---

## 7. One additional trap to check: selection into rollout cohorts

Who decided which 15 regions got the program in Q1? If Q1 regions were selected because they were highest-potential, already-performing better, or had better-resourced customer success infrastructure, then the cohort-specific ATTs from Callaway-Sant'Anna are cohort ATTs — the effect *for those types of regions*. Extrapolating to all regions requires assuming that the treatment effect is similar for regions that came later, which is a substantive assumption worth examining. The parallel trends assumption, even if valid, does not protect you from this type of external-validity limitation.

---

## 8. Summary verdict

| Question | Answer |
|---|---|
| Is the reviewer right that TWFE can be biased even under parallel trends? | Yes, definitively. This is an established result. |
| Should you be worried? | Yes. No never-treated group + three cohorts + 18-month window = real exposure. |
| Is the +6% certainly wrong? | Not necessarily, but you cannot know without decomposing it. |
| What is the source of potential bias? | TWFE uses already-treated units as controls for later cohorts; this biases estimates when treatment effects vary over time. |
| Is there a better approach? | Yes. Callaway-Sant'Anna or Sun-Abraham, plus an event-study plot. |
| What's the single most important first step? | Goodman-Bacon decomposition — quantify how much weight falls on contaminated comparisons before drawing conclusions. |

The good news: your design (multiple cohorts, clear timing, panel data, known treatment dates) is exactly where modern staggered-DiD estimators perform well. The question of how much the program helps is answerable — the standard TWFE just isn't the right tool to answer it cleanly here.
