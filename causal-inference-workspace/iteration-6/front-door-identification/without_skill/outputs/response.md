# Front-Door Identification: Does Unmeasured Confounding Make the Effect Unidentifiable?

## Short Answer

No, the effect is not necessarily unidentifiable. Your setup describes exactly the conditions under which the **Front-Door Criterion** (Pearl, 1995) applies. If three structural conditions hold, you can non-parametrically identify the causal effect of training on performance ratings even though employee ambition is unmeasured and uncontrolled.

---

## The Causal Structure You Are Describing

Let the variables be:

- **T** = Technical skills training (the treatment; 1 = received, 0 = did not)
- **M** = Skills applied on the job (the mediator)
- **Y** = Performance rating (the outcome)
- **U** = Employee ambition (unmeasured confounder)

The causal graph (DAG) is:

```
U
├──→ T
└──→ Y

T ──→ M ──→ Y
```

More explicitly:
- U → T (ambitious employees are more likely to be selected for or seek out training)
- U → Y (ambitious employees earn higher performance ratings independently)
- T → M (training causes the employee to apply new skills on the job)
- M → Y (applying skills on the job causes higher performance ratings)
- There is NO direct arrow from U to M
- There is NO direct arrow from T to Y except through M (this is discussed further below)

---

## The Front-Door Criterion

Pearl's front-door criterion states that the causal effect of T on Y is identified if there exists a set of mediating variables M such that:

1. **M blocks all directed paths from T to Y.** Every path from T to Y passes through M. In your case, the only path from training to performance goes through "skills applied on the job."

2. **There are no unblocked backdoor paths from T to M.** The backdoor paths into T run through U, but U has no direct arrow to M, so no unblocked backdoor path from T to M exists.

3. **All backdoor paths from M to Y are blocked by T.** The confounder U affects Y, and U also affects T, meaning U creates a backdoor path from M to Y that runs M ← T ← U → Y. This path is blocked when we condition on T (the treatment). Since T is observed, we can condition on it.

When these three conditions hold, the causal effect of T on Y is identified by the **front-door formula**:

```
P(Y = y | do(T = t)) = Σ_m P(M = m | T = t) Σ_t' P(Y = y | T = t', M = m) P(T = t')
```

In plain language, you:
1. Estimate the effect of training on skills application (T → M), which is unconfounded because U does not affect M.
2. Estimate the effect of skills application on performance, controlling for training (M → Y | T), which blocks the backdoor through U.
3. Average (marginalize) the controlled M → Y estimate over the observed distribution of T.

---

## Why Each Condition Is Defensible in Your Setting

**Condition 1 (M intercepts all T → Y paths):** This is the substantive assumption you must defend. It requires that training has no direct effect on performance ratings other than through the employee actually applying the skills. This is plausible if managers rate performance based on demonstrated behaviors (what employees actually do) rather than on whether an employee attended training as a credential. If managers do give a ratings bump simply for training participation independent of observable behavior change, Condition 1 fails. You should assess this carefully.

**Condition 2 (No unblocked backdoor into T → M):** Ambition drives training attendance and drives performance, but there is no strong reason to think ambition directly causes employees to *apply skills they have not yet learned*. The content of training is only available to those who attend; M is downstream of T in a way that U cannot shortcut. This makes Condition 2 defensible.

**Condition 3 (Backdoor from M to Y blocked by conditioning on T):** Within each level of T (trained vs. untrained), variation in M is driven by something other than U (since U only enters through T). Conditioning on T holds constant the ambition-driven component of who selected into training, breaking the spurious M ← T ← U → Y path.

---

## What the Unmeasured Confounder Does and Does Not Undermine

It **does** undermine:
- A naive regression of Y on T (OLS with no controls will be biased upward because ambitious employees both attend training and get higher ratings)
- A simple mediation analysis (Baron-Kenny style) of T → M → Y without accounting for the T ← U → Y backdoor

It **does not** undermine the front-door estimator, because:
- The T → M arm is identified (U does not confound this path)
- The M → Y arm, once we condition on T, is also identified (conditioning on T d-separates the M ← T ← U → Y spurious path)
- The two identified arms can be combined via the front-door formula to recover the total causal effect of T on Y

---

## A Practical Worked Example (Binary Variables)

Suppose T, M, Y are all binary. The front-door estimator becomes:

```
P(Y=1 | do(T=1)) - P(Y=1 | do(T=0))
= [Σ_m P(M=m|T=1) Σ_t P(Y=1|M=m,T=t)P(T=t)]
- [Σ_m P(M=m|T=0) Σ_t P(Y=1|M=m,T=t)P(T=t)]
```

Every quantity in this expression is estimable from observed data: P(M|T), P(Y|M,T), and P(T) are all identified from your dataset without any assumption about U.

---

## Caveats and Threats to Validity

1. **Exclusion restriction (Condition 1) may be violated.** If managers know who attended training and reward attendance independent of behavioral change, training has a direct effect on ratings not mediated by M. This would break identification. You can make this more plausible by using manager-blind rating systems or by checking whether ratings change even for trained employees who show no skills application (M=0).

2. **M must be measured without error.** Measurement error in the mediator attenuates the estimated T → M and M → Y associations and can introduce bias. If "skills applied on the job" is a noisy self-report or a coarse behavioral checklist, you should account for measurement error.

3. **No interference (SUTVA).** The standard causal inference assumption that one employee's training does not affect another employee's performance rating is required. In team settings where cross-training and knowledge spillovers occur, this may be violated.

4. **Positivity.** The formula requires that P(T=t) > 0 for both values of t and that P(M=m|T=t) > 0 wherever needed. If certain combinations of T and M are structural zeros (e.g., untrained employees never apply training content), division by zero is an issue. In practice, check support overlap.

5. **The confounder structure must be correctly specified.** The front-door argument assumes U affects T and Y but not M. If ambition also directly affects how much effort employees put into applying skills (independent of whether they received training), U → M exists and Condition 2 fails. Whether this is realistic depends on context.

---

## Conclusion

The unmeasured confounder (ambition) makes naive estimation of the training-to-performance effect invalid, but it does **not** make the causal effect unidentifiable. Your variable "skills applied on the job" acts as a front-door mediator. Provided the three front-door conditions hold — especially the exclusion restriction that training only affects ratings through behavioral application — the front-door formula recovers the population average causal effect of training on performance ratings using only observed data. The key assumptions to scrutinize are (1) that training has no direct, behavior-independent effect on ratings, and (2) that ambition does not independently drive skills application outside of training participation.
