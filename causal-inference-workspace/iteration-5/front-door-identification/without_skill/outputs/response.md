# Does Unmeasured Ambition Make the Training–Performance Effect Unidentifiable?

**Short answer: No. The effect is still identifiable. The variable you described — "skills applied on the job" — gives you exactly what you need to apply the front-door criterion, one of the most powerful identification strategies in causal inference.**

---

## Restating Your Causal Structure

Before diving into the solution, let me make your causal structure precise, because the structure is everything in identification analysis.

You have described the following variables:

- **Training (T):** Whether an employee received technical skills training. This is your treatment.
- **Performance Rating (Y):** The outcome you want to understand causally.
- **Ambition (U):** An unmeasured common cause. Ambitious employees are more likely to be selected into or seek out training, and ambitious employees also independently earn higher performance ratings through effort and initiative — regardless of any specific training content.
- **Skills Applied on the Job (M):** A measured variable that captures whether the training content actually showed up in the employee's daily work behavior.

The causal graph implied by your description looks like this:

```
        U (Ambition — unmeasured)
       / \
      v   v
      T   Y
      |   ^
      v   |
      M ---
```

More precisely, the arrows are:
- U → T  (ambition drives selection into training)
- U → Y  (ambition independently raises performance)
- T → M  (receiving training causes skill application on the job)
- M → Y  (applying skills causes better performance ratings)

There is a backdoor path from T to Y: **T ← U → Y**. Because U is unmeasured, you cannot block this path by conditioning on U. A naive regression of Y on T would capture both the causal effect of training and the spurious association due to ambitious employees self-selecting into training — and these two quantities are tangled together in the observed data.

This is a genuine confounding problem. But it is not a fatal one.

---

## The Front-Door Criterion

Judea Pearl introduced the **front-door criterion** precisely for situations like yours: an unmeasured confounder between treatment and outcome, but a measured mediator on the causal pathway between them. The criterion specifies conditions under which the causal effect of T on Y is fully identifiable from observational data, even when you cannot measure U.

The name comes from the causal graph structure: instead of identifying the effect by "going through the back door" (conditioning on confounders), you identify it by going "through the front door" — through a mediating variable that lies on the causal path forward from treatment to outcome.

### The Three Conditions

For the front-door criterion to apply, your mediator M must satisfy three conditions simultaneously:

---

**Condition 1: M intercepts all causal paths from T to Y.**

Every causal path from Training to Performance Rating must pass through Skills Applied. There must be no direct effect of training on performance that bypasses M — no path T → Y that doesn't go through M.

In your setting, this means training can only improve performance *because* it causes employees to apply new skills on the job. If training also improved performance through some other channel — for example, completing the training sends a signal to managers that the employee is high-potential, and managers reward that signal in performance ratings regardless of whether skills are actually applied — that would constitute a direct T → Y path that violates this condition.

This is often the most demanding condition to defend in organizational contexts. Think carefully about whether:
- Managers know who attended training and raise their ratings for attendees as a form of acknowledgment
- Training completion affects organizational visibility or social capital in ways independent of behavioral change
- Employees receive a credential from training that affects their ratings independently of skill use

---

**Condition 2: There are no unblocked backdoor paths from T to M.**

The path from Training to Skills Applied must be unconfounded — that is, there is no unmeasured common cause of T and M other than what flows through T itself.

In your structure, U (ambition) affects T, but U does not have a direct arrow into M. Ambition might make someone seek out training, but it doesn't cause them to apply training-derived skills on the job through some pathway that bypasses the training itself. An employee cannot apply skills from a training program they haven't attended. This condition is typically easy to defend in this kind of setting.

The assumption would be violated if, say, ambitious employees also independently develop the same skills through self-study or mentoring — so that M is elevated both by formal training (T → M) and by an independent ambition-driven route (U → M directly). If that were true, there would be an unmeasured common cause of T and M (namely U), which would open a backdoor from T to M that you couldn't close.

---

**Condition 3: All backdoor paths from M to Y are blocked by conditioning on T.**

There must be no open path from Skills Applied to Performance Rating that goes "backwards" and isn't closed when you condition on Training.

In your graph, the only potential backdoor path from M to Y runs through U: M ← T ← U → Y. But this path passes through T. Once you condition on T — that is, once you compare employees who received the same training exposure — the path M ← T ← U → Y is blocked at T. The variation in M within a fixed level of T can no longer be explained by U flowing through T, because T is held constant. So conditioning on T suffices to close the only back-door from M to Y.

---

All three conditions hold in your described scenario. The front-door criterion applies. The causal effect of training on performance is identifiable.

---

## The Front-Door Adjustment Formula

When the front-door criterion holds, the causal effect of T on Y is given by:

$$P(Y = y \mid do(T = t)) = \sum_{m} P(M = m \mid T = t) \cdot \sum_{t'} P(Y = y \mid M = m, T = t') \cdot P(T = t')$$

This formula expresses the interventional distribution — what would happen if you *forced* training to take value t — entirely in terms of observational conditional probabilities that you can estimate from your data.

Let me walk through what each piece is doing.

### Step 1: Estimate how Training affects Skill Application

Compute P(M | T): the conditional distribution of skill application given training status.

Because Condition 2 holds — there is no backdoor from T to M — this observational conditional probability *equals* the causal effect of T on M. No adjustment is needed. You just look at how skill application differs between trained and untrained employees.

### Step 2: Estimate how Skill Application affects Performance, conditioning on Training

Compute P(Y | M, T): the conditional distribution of performance given both skill application and training status.

Because Condition 3 holds — conditioning on T blocks the only backdoor from M to Y — this observational conditional probability, *after conditioning on T*, gives you the causal effect of M on Y. You compare performance outcomes across different levels of skill application, within groups defined by training status.

### Step 3: Average the M → Y effect over the distribution of Training

The quantity Σ_{t'} P(Y | M = m, T = t') P(T = t') marginalizes out the training-status conditioning. This constructs a training-adjusted estimate of the effect of M on Y that isn't specific to any particular training level.

### Step 4: Compose

Weighting the result of Step 3 by P(M = m | T = t) and summing over M gives you the total causal effect of setting T = t on Y — the effect of training on performance, purged of all confounding by unmeasured ambition.

---

## The Intuition Behind the Math

You might wonder: why does this work? What's the logical move that lets unmeasured U stop mattering?

The answer is a two-step argument:

**Step 1 — The T → M link is clean.** The path from training to skill application is causally direct and unconfounded. Even though ambitious people are more likely to receive training (U → T), once they're in the training group and you're asking how much skill application it produces, ambition doesn't have a separate lane into M. So the T → M relationship, as you observe it, reflects the causal mechanism, not selection.

**Step 2 — Within training groups, the M → Y link is clean.** Once you hold training status fixed, the variation in M across employees within that training group is no longer explained by U-driven selection. If you're looking only at trained employees, the ones who apply skills more vs. less aren't more vs. less ambitious in some way that's channeled through training — because training is already fixed. The U → T → M backdoor is blocked. So M → Y, conditional on T, is causally interpretable.

Combining these two clean relationships — training reliably changes skill application, and within-training-group variation in skill application reliably changes performance — gives you the causal effect of training on performance, without ever needing to observe ambition.

---

## Assumptions to Scrutinize

### The Exclusion Restriction (Condition 1) is the hard one

Training must affect performance *only through* skill application. In most organizational contexts, this is the assumption most likely to be contested. Managers often know who attended training programs. Attending training may improve social standing, signal motivation, or result in formal certification — all of which could translate to better performance ratings independently of behavioral change on the job.

If you believe there is a meaningful direct T → Y effect that bypasses M, the front-door criterion fails, and you would need to either:
- Argue the direct effect is negligible and bound the resulting bias
- Find a way to block or measure the direct pathway
- Fall back to partial identification, which gives you intervals rather than point estimates

### The No U → M Assumption (Condition 2)

You need to be confident that ambitious employees are not developing and applying the same skills through routes other than the formal training program. If "skills applied on the job" can be elevated by high ambition independently of training — because ambitious employees pick up skills from books, peers, or experience — then U has a direct arrow into M and Condition 2 fails.

### Measurement of M

"Skills applied on the job" must be measured with enough validity to serve as the causal mediator. If this is a self-report that's influenced by how positively an employee feels about their training experience (rather than an objective behavioral measure), measurement error could introduce bias. Consider whether the measure could be systematically higher or lower for certain types of employees in ways correlated with U.

---

## Practical Estimation

For a continuous or binary outcome with a binary treatment and a continuous or binary mediator, the most common practical approaches are:

**Product-of-coefficients (linear setting):**
1. Regress M on T. Call the coefficient β₁.
2. Regress Y on M and T. Call the coefficient on M β₂.
3. The front-door total effect estimate is β₁ × β₂.

This is algebraically equivalent to the front-door formula under linearity. Note that this is different from standard mediation analysis: you are not decomposing a total effect into direct and indirect components — you are *identifying the total effect itself* via the mediator, because the total effect is otherwise unidentifiable given the unmeasured confounder.

**Nonparametric estimation:**
For more complex relationships, you can implement the front-door formula nonparametrically using kernel regression or flexible machine learning models for each conditional probability. Libraries like `causalml` or `econml` in Python support mediation-based identification that can accommodate this structure.

**Standard errors:**
Because your final estimate is a composition of two estimated quantities, standard errors from either stage alone will understate uncertainty. Use the delta method, the bootstrap, or a joint estimating equation approach that propagates uncertainty from both stages.

---

## What This Strategy Cannot Identify

Be clear about the boundaries of what the front-door criterion gives you:

- It identifies the **total causal effect** of T on Y flowing through M. If there is a direct T → Y effect, the front-door formula does not identify it separately — and if you assume no direct effect but there is one, your estimate will be biased.
- It does not give you the **direct effect of T on Y** (if any exists) or the **indirect effect through M** in the mediation-analysis sense.
- It relies on **correct causal graph specification**. If you've omitted an arrow, misspecified a direction, or missed a common cause, identification fails.
- It does not handle **weak instruments** gracefully. If training has little effect on skill application (T → M is weak or noisy), the front-door estimate becomes imprecise even if it's theoretically unbiased.

---

## Summary

Your situation is not hopeless — far from it. The structure you've described is one of the canonical examples where the front-door criterion applies, and you happen to have measured the key variable that makes it work.

The unmeasured confounder (ambition) would derail a naive regression of performance on training. But it does not make the causal effect unidentifiable. "Skills applied on the job" sits on the causal path from training to performance, is not directly caused by ambition (except through training), and its relationship to performance can be deconfounded by conditioning on training status. These are exactly the conditions the front-door criterion requires.

**The path forward:**
1. Verify the exclusion restriction: are you confident training affects performance *only* through skill application?
2. Verify that ambition does not cause skill application through a channel that bypasses training.
3. Apply the front-door adjustment formula — in the linear case, a product-of-coefficients from two regressions.
4. Use bootstrapped standard errors to correctly capture uncertainty across both stages.

If you can defend the assumptions, the front-door criterion gives you a causally valid estimate of the effect of technical skills training on performance ratings, identified entirely from observational data, without ever measuring employee ambition.
