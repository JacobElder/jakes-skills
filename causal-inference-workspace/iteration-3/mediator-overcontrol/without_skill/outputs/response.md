# Should You Control for Manager Motivation Level?

**Short answer: No — controlling for manager motivation level is likely a mistake and will bias your estimate of the training's effect.**

---

## The Core Problem: You're Controlling for a Mediator

Manager motivation level, measured 1 month after the training ended, is almost certainly a **mediator** — a variable that sits on the causal pathway *between* the treatment (training) and the outcome (performance). The causal chain likely looks something like this:

**Management Training → Manager Motivation ↑ → Team Performance ↑**

When you include a mediator as a control variable in a regression, you are blocking the very pathway through which your treatment works. This is called **overcontrol bias** (sometimes called "mediator bias" or "post-treatment bias"). The result is that your estimate of the training effect will be attenuated — you'll systematically underestimate how much the training actually improved performance, potentially to the point of finding no effect at all when there truly is one.

---

## Why "Strong Predictor" Doesn't Mean "Valid Control"

It's tempting to include strong predictors as controls because they reduce residual variance and can improve precision. That logic is sound for **pre-treatment confounders** (variables that affect both selection into training and performance outcomes, measured *before* training). But it breaks down entirely for **post-treatment variables**.

The criterion for a valid control variable is not just whether it predicts the outcome — it's whether it is:
1. Measured **before** treatment assignment (or at least causally prior to it), AND
2. Not itself affected by the treatment.

Manager motivation measured 1 month *after* training fails both conditions. The training almost certainly changed motivation levels — that's arguably the mechanism of action.

---

## What Could Go Wrong Concretely

Imagine the training works *entirely* through boosting motivation. If you control for motivation, your model asks: "Among managers with the same motivation level, did training affect performance?" The answer will be approximately zero — not because training doesn't work, but because you've conditioned away the effect. You've answered the wrong question.

Even if motivation is only a *partial* mediator, including it will still partially bias your estimate downward.

---

## What You Should Do Instead

**1. Treat motivation as a mediator, not a control.**
If you want to understand *how* training works (i.e., through what mechanisms), conduct a formal **mediation analysis** (e.g., Baron-Kenny steps, or preferably a causal mediation framework like the one proposed by Imai et al. 2010). This lets you decompose the total effect into direct and indirect (motivation-mediated) components without biasing your total effect estimate.

**2. For your primary estimate, omit post-treatment variables.**
Your main regression should include only pre-treatment covariates: baseline performance, manager tenure, team size, department, pre-training motivation (if available), etc.

**3. If you must include motivation, flag it clearly.**
If a reviewer or stakeholder insists, you can report a sensitivity analysis with motivation included, but clearly label it as a potentially biased estimate and explain the direction of expected bias (downward attenuation of the training effect).

---

## A Useful Heuristic

Before adding any variable to your model, ask: **"Could the treatment have changed this variable?"** If yes, it's a post-treatment variable, and including it risks bias. The timing tells you something important here — anything measured after the training began is a red flag.

---

## Summary

| Variable type | Include as control? |
|---|---|
| Pre-treatment confounder (e.g., baseline performance) | Yes |
| Pre-treatment motivation level | Yes |
| Post-treatment mediator (e.g., motivation 1 month after training) | No — biases effect estimate |

The fact that motivation is a strong predictor of performance actually makes this error more dangerous, not less. Including a powerful mediator as a control will more severely attenuate your estimate of the training effect than a weak mediator would.

Leave it out of your primary model, and consider a mediation analysis as a secondary analysis if understanding the mechanism is also a goal.
