# AIC vs. BIC Disagreement: Which to Report?

## The Short Answer

Report both, explain the disagreement, and make a principled argument for which one better fits your inferential goal. This is not a dodge — it is the correct answer, and it is what reviewers expect from a methodologically aware author.

## Why They Disagree

AIC and BIC penalize model complexity differently, and the disagreement you are seeing is a direct consequence of that difference — not a sign that something went wrong.

- **AIC** penalizes each additional parameter by 2. It targets *predictive accuracy*: among the models you fit, which one would predict new data from the same data-generating process most accurately?
- **BIC** penalizes each additional parameter by ln(N). Because ln(N) > 2 whenever N > 7, BIC always penalizes complexity more harshly than AIC. It targets *model identification*: which model is most likely to be the true generating model, under the assumption that the true model is in your candidate set?

When your sample is moderate to large, BIC's heavier penalty routinely selects sparser models than AIC. That is exactly what happened here. There is no mathematical contradiction; they are answering different questions.

## How to Decide Which One to Report

Ask yourself which inferential goal aligns with your research question.

**Favor AIC when:**
- Your goal is out-of-sample prediction or generalization.
- You do not believe the "true" model is in your candidate set (a realistic assumption in most social and behavioral science).
- Your theoretical motivation leads you to expect that the complex model captures real signal, and you want to avoid discarding it prematurely.
- Sample size is large relative to the number of parameters — in this regime AIC's optimism about complexity is less of a problem.

**Favor BIC when:**
- Your goal is to identify the correct model structure, not to maximize predictive accuracy.
- You have theoretical reasons to believe a parsimonious model is correct.
- Your sample size is small to moderate, where BIC's heavier penalty provides more reliable protection against overfitting.
- You are comparing models with a nested structure and have a hypothesis about which one is "true."

## What to Actually Write in the Paper

Do not report only one criterion and quietly ignore the other. That invites reviewer suspicion. Instead:

1. **Report both values** in a model comparison table — include AIC, BIC, and the number of parameters for every model you estimated.
2. **Acknowledge the disagreement explicitly** in one sentence: "AIC favored the larger model (ΔAIC = X relative to the 5-parameter model) while BIC favored the smaller model (ΔBIC = Y)."
3. **State which criterion you rely on for your primary inference and why**, grounded in your inferential goal. Example: "Because our goal is predictive generalization rather than model identification, and because we have no strong prior that the true model is contained in our candidate set, we follow AIC in retaining the larger model."
4. **Check whether the substantive conclusions change** across models. If the key coefficients are similar in both models, the disagreement matters less — say so. If they diverge meaningfully, that is a finding worth discussing.

## A Note on Magnitude

The absolute difference matters, not just the direction of the winner. A difference of 2 AIC units is conventional evidence of modest support; a difference of 10 is strong. If ΔAIC = 1.8 and ΔBIC = 3.1, neither criterion is delivering a strong verdict, and the honest conclusion is that the data do not sharply discriminate between the two models. In that case, reporting the simpler model with a note that the complex model performs comparably is often the most defensible position.

## Summary

| Criterion | Question it answers | Penalty per parameter | Tends to prefer |
|---|---|---|---|
| AIC | Which model predicts best? | 2 | Larger models |
| BIC | Which model is most likely true? | ln(N) | Smaller models |

The disagreement is expected and interpretable. Your job is to align your choice with your inferential goal, report both transparently, and tell the reader why you made the call you did.
