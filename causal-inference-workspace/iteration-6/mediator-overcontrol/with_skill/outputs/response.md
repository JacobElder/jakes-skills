# Should You Control for "Manager Motivation Level" Measured 1 Month Post-Training?

**Short answer: No. Controlling for it is almost certainly a mistake — and the mistake has a name: overcontrol bias (mediator conditioning).**

---

## 1. Name the Rung

This is a **Rung 2 (intervention)** question. You want to know what happens *if* a manager attends the 3-day training — P(performance | do(training)). The data here is observational (or quasi-experimental at best), and you're asking whether to add a covariate. That's a structural question, not a statistical one.

---

## 2. Sketch the DAG

The relevant causal structure looks like this:

```
Training (X) ──────────────────────────────────────► Performance (Y)
     │                                                      ▲
     │                                                      │
     └──────► Motivation Level @ +1 month (M) ─────────────┘
```

With potential confounders:

```
U (e.g., pre-existing manager quality, organizational support)
↙                                                          ↘
Training (X) ──► Motivation Level (M) ──► Performance (Y)
                                                     ▲
U ───────────────────────────────────────────────────┘
```

**The critical temporal fact:** Motivation level is measured *one month after the training ended* — it is a post-treatment variable. The training program plausibly *causes* motivation level (managers who complete a development program may feel more motivated, more confident, more supported). That makes motivation a likely **mediator** on the Training → Performance path.

---

## 3. Classify the Structural Role of "Motivation Level"

Applying the per-variable classification from the skill:

> "Mediator on the X → Y path, or descendant of one? → Don't control if you want the total effect."

The classification here is almost certainly **mediator**. Motivation level at +1 month is a plausible mechanism through which training produces better performance outcomes at +6 months. The causal chain is:

**Training → (Managers feel more motivated) → (They lead their teams more effectively) → Better team performance**

If you control for motivation level, you are blocking this pathway. Your regression will be estimating something like: "The effect of training on performance *holding motivation constant*" — which is not the total causal effect of training. You would be asking: among managers who ended up with the *same* motivation level, did training help? That partially strips out the very mechanism you presumably care about.

**This is the textbook mediator overcontrol bias.**

```
X → M → Y

Controlling on M: blocks the X → M → Y path
Result: your estimate of X → Y is biased downward (toward zero)
        because you've absorbed part of the effect into the M coefficient
```

---

## 4. What Does It Mean for Your Estimate?

If you include motivation as a control, your coefficient on "training" will estimate the **direct effect** of training on performance — the portion of the effect that does *not* operate through motivation changes. This will typically be smaller than the **total effect** (which includes the motivation-mediated pathway).

In some cases, if motivation is the *primary* mechanism, the direct effect could be near zero or even negative, leading you to conclude training "doesn't work" when in fact it works precisely *by* raising motivation.

This is not a precision problem. It is a bias problem — the estimate answers a different causal question than the one you asked.

---

## 5. The Reason It's Tempting — and Why the Instinct Fails

The intuition driving the decision to include motivation is:

> "Motivation is a strong predictor of performance. I should control for it to get a cleaner estimate."

This is the **"control for everything that predicts the outcome"** folk rule — and it is wrong in exactly this type of situation. The skill is explicit about this:

> "Control for any pre-treatment variable that predicts both treatment and outcome." Wrong. Post-treatment variables are especially likely to be mediators — if a variable was measured *after* treatment assignment, ask whether treatment could have caused it before including it as a control.

Statistical predictive power is not a criterion for control. Structural role is. Here:
- Motivation is post-treatment ✓ (flagging signal)
- Training plausibly causes motivation ✓ (it's a mediator)
- Motivation causes performance ✓ (it's on a causal path)

All three together confirm: **mediator, don't control.**

---

## 6. When Would Controlling for Motivation Be Correct?

There is one legitimate scenario: if you specifically want to know whether training has any **direct** effect on performance *beyond* its effect on motivation. For example:

- Does training improve team performance through mechanisms other than manager motivation? (Better tools? Changed team structures? Improved manager communication style operating independently of self-reported motivation?)
- This "direct effect" question requires controlling for the mediator.

But this is a **different estimand** — the controlled direct effect (CDE) rather than the total effect — and it requires explicitly acknowledging you are decomposing the effect, not adjusting for confounding.

If your goal is to evaluate the training program as a whole — to answer "should we keep running this?" — you want the total effect. Don't control.

---

## 7. What Should You Do Instead?

**To estimate the total effect of training on performance:**

1. Do not include motivation level as a control.
2. Focus on variables that are:
   - Measured *before* training began, and
   - Common causes of both training participation and performance outcomes (classic confounders — e.g., manager seniority, team size, prior performance scores, organization type).

**If you want to understand the mechanism** (how much of the effect runs through motivation vs. other paths), conduct a formal **mediation analysis** — but do it explicitly as a mediation analysis with the appropriate estimand (natural direct effect, natural indirect effect), not by naively including motivation as a regression covariate.

**If motivation measured at +1 month is intended to capture pre-existing motivation** (you believe it's a stable trait), you face an identification problem: you can't cleanly separate "pre-existing motivation" from "training-induced motivation change" using a post-treatment measurement. The solution is to measure motivation *before* training begins, not after. A pre-treatment motivation measure would be a legitimate confounder to control for.

---

## 8. Summary Verdict

| Question | Answer |
|---|---|
| What is motivation level's structural role? | Mediator (post-treatment, caused by training, causes performance) |
| Should you control for it to estimate total training effect? | No — this is overcontrol bias |
| What happens if you control for it? | You estimate the direct effect, not the total effect; likely biases toward zero |
| Is it a confounder? | Only if you can argue training did *not* cause motivation — unlikely given timing |
| What should you control for instead? | Pre-treatment confounders: prior performance, manager tenure, baseline team characteristics |
| What if you want the mediated vs. direct decomposition? | Run a formal mediation analysis; don't add it as a covariate in the main regression |

**The bottom line:** Controlling for a variable because it's "a strong predictor of performance" is not causal reasoning — it's pattern matching. The DAG shows motivation is on the causal pathway from training to performance. Blocking that path in your regression doesn't make your estimate cleaner; it makes it answer a different question.
