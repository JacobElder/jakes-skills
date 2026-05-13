# Causal Inference Response: Unmeasured Confounding and Identifiability

## The Short Answer

No, the unmeasured confounder does not necessarily make the effect unidentifiable. Your setup — where you have a mediator ("skills applied on the job") that sits between training and performance — is precisely the structure that enables identification through the **front-door criterion**, even in the presence of an unmeasured confounder like ambition.

---

## Understanding the Problem Structure

Let's map out the causal structure you've described:

- **T**: Technical skills training (treatment)
- **M**: Skills applied on the job (mediator)
- **Y**: Performance ratings (outcome)
- **U**: Employee ambition (unmeasured confounder)

The causal graph looks like this:

```
U ---------> T
|            |
|            v
|            M
|            |
|            v
+---------> Y
```

- U → T (ambition drives who gets selected for training)
- U → Y (ambition independently drives better performance ratings)
- T → M (training causes the employee to apply new skills)
- M → Y (applying new skills causes better performance)

This is the classic setup for applying the **front-door criterion**.

---

## The Front-Door Criterion

The front-door criterion, introduced by Judea Pearl, allows identification of a causal effect even when the treatment and outcome share an unmeasured common cause, provided:

1. **M blocks all directed paths from T to Y** — meaning all causal influence of training on performance runs through skills applied (no direct path T → Y bypassing M).
2. **There are no backdoor paths from T to M** — meaning U does not confound the T → M relationship. Since U affects T and Y, but not M directly, this holds here.
3. **All backdoor paths from M to Y are blocked by T** — meaning we can control for T when estimating the M → Y effect.

Your scenario satisfies all three conditions:
- Training only affects performance through whether skills get applied.
- Ambition drives who gets trained, but does not independently determine whether skills get applied on the job (that's determined by the training itself).
- Ambition affects Y, but when we condition on T (training status), we block U's ability to confound the M → Y path through T.

---

## The Front-Door Estimator

The causal effect of T on Y is identified by:

$$P(Y | do(T)) = \sum_m P(M=m | T) \sum_{t'} P(Y | T=t', M=m) P(T=t')$$

In plain English:

1. **Step 1**: Estimate the effect of training on skills applied. Since there's no confounding on the T → M path (U doesn't independently cause M), this is just the observed association: P(M | T).

2. **Step 2**: Estimate the effect of skills applied on performance, adjusting for training status. Conditioning on T blocks the U → T → ... → Y backdoor paths when estimating M → Y. So we compute E[Y | T, M] and average over the distribution of T.

3. **Step 3**: Combine via the law of total probability, averaging the M → Y effect over the observed distribution of M given T.

This gives you the identifiable causal effect of training on performance ratings, despite never observing ambition.

---

## Key Assumptions to Scrutinize

The front-door identification strategy depends on assumptions that are not automatically guaranteed. You should think carefully about:

**1. No direct effect of training on performance that bypasses skills applied**
If training affects performance ratings through channels other than skills application — for example, if managers rate trained employees more favorably simply because they know they attended training — then T has a direct path to Y, and the front-door criterion fails. This "certification effect" or "halo effect" would violate the exclusion restriction.

**2. Ambition does not directly cause skills applied on the job**
If more ambitious employees also apply skills on the job regardless of training (because ambitious people are self-learners), then U → M exists, and there's unmeasured confounding on the M → Y path that cannot be blocked by conditioning on T. This would break the second condition.

**3. Skills applied is measured reliably and is not a collider**
If "skills applied" is measured with error, or if conditioning on it opens any collider paths, your estimates will be biased. You should also verify that M is not affected by other unmeasured variables that also affect Y.

**4. Positivity**
All levels of training and skills applied must occur with positive probability across the population. If some employees always apply skills regardless of training, or if some subgroups never apply skills even after training, the estimator can become undefined or unstable.

---

## Practical Implications

Given that your design holds:

- You can estimate the **total causal effect** of training on performance ratings from observational data.
- You do not need to instrument for training or run an experiment.
- The estimate will be valid even though you cannot observe or measure ambition.
- The decomposition into T → M and M → Y also gives you mechanistic insight: you can see how much of the training effect operates through skill application, which is useful for program evaluation.

If you want to be rigorous, you should:
- Conduct a sensitivity analysis for the assumption that ambition does not cause skill application.
- Test for direct effects of training on performance that bypass skill application (e.g., through manager awareness of who received training).
- Use a doubly robust or semiparametric estimator of the front-door functional to improve finite-sample efficiency.

---

## Summary

The unmeasured confounder (ambition) does not make this effect unidentifiable. Your "skills applied on the job" variable, precisely because it is a mediator that sits between training and performance and is itself unconfounded, enables identification through the front-door criterion. The key is that the bias from ambition cancels out across the two-step estimation procedure. You should, however, carefully audit whether the exclusion and no-direct-confounding assumptions hold in your specific organizational context before trusting the estimates.
