# Is Controlling for "Manager Motivation Level" a Good Idea?

## Short Answer

No — this is almost certainly a bad idea, and doing so would likely **bias your causal estimate** of the training program's effect on performance.

---

## The Core Problem: You're Controlling for a Mediator

"Manager motivation level," measured **one month after the training ended**, sits on the **causal pathway** between the training and the performance outcome. It is not a pre-treatment confounder — it is a **mediator** (or at minimum, a post-treatment variable influenced by the treatment).

Here's the causal structure you're likely dealing with:

```
Training Program --> Manager Motivation (1 mo. post) --> Team Performance (6 mo. post)
```

There may also be a direct path:

```
Training Program --> Team Performance (via other mechanisms)
```

When you **condition on a mediator**, you block the indirect pathway through which the treatment operates. This means you would be estimating only the **direct effect** of training on performance — not through motivation — while systematically discarding the effect that runs through motivation. That is almost certainly not the causal quantity you want.

---

## Why This Is Called "Overcontrol Bias"

Overcontrol bias occurs when a researcher controls for a variable that is causally downstream of the treatment. The result:

- **Coefficient on treatment is biased downward** (or toward zero), because you've absorbed some of the treatment's actual effect into the mediator.
- **Coefficient on the mediator may also be biased** (collider/mediator conditioning can open back-door paths you didn't intend to open).
- **You underestimate the total effect** of the training program.

This is a well-documented failure mode in applied causal inference and is sometimes called the "bad control" problem (Angrist & Pischke; Cinelli, Forney & Pearl).

---

## The Correct Framing

Ask yourself: **What is your research question?**

| Research Question | Correct Approach |
|---|---|
| What is the **total effect** of training on performance? | Do NOT control for motivation. Estimate the ITT (Intent-to-Treat) or ATE directly. |
| What is the **direct effect** of training, *not through motivation*? | Use mediation analysis (e.g., Baron-Kenny, structural equation modeling, or the potential outcomes mediation framework). This is a more complex estimand. |
| What is the **indirect effect** through motivation? | Use formal mediation analysis to decompose total → direct + indirect. |

If your goal is simply "did the training program improve performance?", you want the **total effect**, and you should not condition on motivation.

---

## What Motivation Level Might Actually Be

It's worth being precise about what post-treatment variables can be:

1. **Mediator**: Training causes motivation, motivation causes performance. (Most likely here.)
2. **Proxy for treatment compliance**: Motivation reflects how seriously managers engaged with the training, making it a post-treatment compliance indicator — also a bad control.
3. **Independent confounder**: Only if motivation level at 1 month post-training is **not influenced by the training at all** would it be safe to control for. This is implausible if the training is effective.

In nearly any realistic scenario for this study design, motivation is post-treatment and should not be in the regression as a covariate.

---

## What You Should Do Instead

1. **For total effect estimation**: Regress team performance on treatment assignment (trained vs. not trained), plus any **pre-treatment** covariates (e.g., baseline performance, manager tenure, team size). Do not include post-treatment variables.

2. **If you want to understand the role of motivation**: Conduct a formal mediation analysis. This requires additional assumptions (sequential ignorability) and a more careful identification strategy, but it lets you honestly decompose the effect.

3. **Pre-treatment motivation as a control**: If you have a measure of motivation **before** the training began, that would be a legitimate baseline covariate to include — it controls for pre-existing differences in motivation without blocking any causal pathway.

---

## Summary

Controlling for post-treatment variables that lie on the causal pathway between treatment and outcome is a classic and consequential methodological error. In your case:

- Manager motivation measured 1 month post-training is almost certainly **caused by the training**, making it a mediator.
- Including it as a control variable will **attenuate your treatment effect estimate** and produce a biased answer to your research question.
- The fix is straightforward: **remove it from the model**, or use mediation analysis if decomposing the pathway is the goal.

The fact that motivation is "a strong predictor of performance" makes it a tempting control — but causal direction, not predictive strength, determines whether a variable should be controlled for.
