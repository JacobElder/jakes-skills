# Response: Should "Manager Motivation Level" Be Controlled For?

## Short Answer

No — including manager motivation level measured 1 month post-training as a control variable is likely a **bad idea** from a causal inference standpoint. It introduces **mediator over-control bias** (also called post-treatment bias), which will bias your estimate of the training program's effect on performance.

---

## Why This Is Problematic

### The Variable Is Post-Treatment

Your treatment is the 3-day management training program. Manager motivation level is measured **1 month after the training ended** — meaning it is measured *after* the treatment has already occurred. This makes it a **post-treatment variable**.

The cardinal rule in causal inference is:

> **Never condition on a variable that was caused by the treatment.**

If the training program itself influenced manager motivation levels (which is highly plausible — training often boosts confidence, engagement, and drive), then motivation is not an independent background covariate. It is part of the **causal pathway** through which training affects performance.

### The Mediator Over-Control Problem

Structurally, this scenario likely looks like:

```
Training → Manager Motivation → Team Performance
    ↘_________________________________↗
              (Direct Effect)
```

Manager motivation is a **mediator**: a variable that sits on the causal path between the treatment and the outcome. When you control for a mediator, you block the very pathway you are trying to measure. You will:

1. **Underestimate the total effect** of the training — possibly severely, since motivation may be a primary mechanism.
2. **Introduce collider bias** if motivation also has other causes that relate to performance, creating spurious associations.
3. **Produce an uninterpretable estimate** — it will be neither the total effect nor a clean direct effect.

### Why "Strong Predictor" Doesn't Justify Controlling

It is tempting to include any variable that strongly predicts the outcome, because it reduces residual variance and can improve precision. This reasoning is valid for **pre-treatment covariates** (confounders measured before treatment assignment). But for post-treatment variables, predictive strength is irrelevant to whether inclusion is appropriate. A strong mediator is exactly the worst variable to control for if you want the total causal effect.

---

## What You Should Do Instead

### If You Want the Total Causal Effect of Training

Simply **do not include manager motivation** in the model. Estimate the reduced-form effect:

```
Team Performance ~ Training Program Assignment + Pre-Treatment Covariates
```

Pre-treatment covariates (measured *before* the training) are safe to include and can improve precision: baseline team performance, manager tenure, pre-training motivation scores, team size, industry, etc.

### If You Want to Understand the Mechanism

If your goal is to understand *how much* of the training effect flows through motivation versus other pathways, you need a **causal mediation analysis** — not simple covariate adjustment. This requires:

- A model for the mediator (motivation ~ treatment + pre-treatment covariates)
- A model for the outcome (performance ~ treatment + mediator + pre-treatment covariates)
- Careful handling of the no-unmeasured-mediator-confounders assumption

Tools: the `mediation` R package, `mediation` in Python (`statsmodels` has partial support), or manual implementation using the Baron-Kenny framework with the caveat that it assumes no interaction between treatment and mediator.

### If Motivation Was Measured Before Training

If manager motivation was measured **before** the training began, it is a pre-treatment covariate (a confounder if it affects both who gets trained and future performance), and controlling for it is appropriate and recommended.

---

## Summary Table

| Scenario | Action |
|---|---|
| Motivation measured before training | Include as confounder — reduces bias and variance |
| Motivation measured after training, goal is total effect | Do NOT include — causes mediator over-control bias |
| Motivation measured after training, goal is mechanism | Use formal causal mediation analysis |

---

## Bottom Line

The fact that manager motivation is a "strong predictor" of outcomes makes it more dangerous to over-control on, not less. Including a strong mediator as a covariate will absorb most of the treatment effect you are trying to estimate, leading you to dramatically understate the impact of the training program. Leave it out of the main model, and if you care about the mechanism, invest in a proper mediation analysis with appropriate sensitivity analyses.
