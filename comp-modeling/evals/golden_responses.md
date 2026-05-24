# Golden Responses

Hand-crafted ideal answers to a few high-stakes prompts. Use these as anchors when judging whether the skill's output is up to standard.

These are not the *only* good answers — the skill may legitimately take different paths. But these illustrate what "excellent" looks like on the criteria the evals encode: workflow completeness, pitfall awareness, appropriate humility, and specific actionable recommendations.

---

## Golden Response 1 — Full pipeline for RL bandit data

**Prompt:** *"I have RL bandit data from 40 subjects, 150 trials each. I want to estimate per-subject learning rates and compare RL to a win-stay-lose-shift baseline. Walk me through start to finish."*

**Ideal response:**

A few clarifications first that will shape the workflow: Is this a stationary or drifting bandit? Two-armed or more? Are subjects told the reward structure or learning from scratch? I'll proceed assuming a standard stationary or slowly-drifting 2-armed bandit; flag if that's wrong.

Here's the workflow I'd recommend, with some specific suggestions for your sample size:

**1. Define the question precisely.** It sounds like the goal is parameter estimation (learning rate as an individual-difference measure) plus model comparison (RL vs. WSLS). That shapes the rest. If you also wanted trial-by-trial regressors for fMRI, the requirements would be tighter.

**2. Candidate models.** At minimum:
- Rescorla-Wagner + softmax (your "RL"): 2 params (α, β).
- WSLS heuristic: 1 param (consistency).
- One extra worth including: RW + perseveration. A "stay" bias is so common in bandit data that the no-perseveration RL model often inflates α to absorb it. Compare with and without.

**3. Write down the generative models.** I can give you Stan code for all three if useful.

**4. Simulate first.** Before fitting anything, run forward simulations with parameters at reasonable values (α ∈ [0.1, 0.5], β ∈ [2, 6]) and check the simulated learning curves and switch rates look like real bandit behavior. If they don't, the model is wrong on the qualitative level and no fitting will save you.

**5. Parameter recovery.** This is critical for your sample size. 150 trials/subject is on the lower end — α/β trade off and per-subject MLE will pile up at boundaries. Run a recovery study:
- Sample 100 (α, β) pairs from realistic ranges.
- Simulate 150 trials each.
- Fit them back with whatever estimator you'll use on real data.
- Compute Spearman ρ between true and recovered. You want > 0.7 to interpret individual estimates; > 0.9 is ideal.
- Compute the cross-parameter correlation of recovered estimates. If recovered α and β correlate > 0.5, they're trading off and you need to be careful about interpreting them separately.

**6. Fit to real data — and almost certainly use hierarchical Bayes here, not MLE.** With 150 trials/subject, per-subject MLE will give you a lot of boundary estimates (α ≈ 0 or α ≈ 1). Hierarchical Bayes adds shrinkage across subjects, which dramatically stabilizes individual estimates with this kind of trial budget. Specifically:
- If it's a standard 2-armed bandit, `hBayesDM::bandit2arm_delta(data, niter=4000)` is a one-liner.
- For custom variants, write Stan code with non-centered parameterization (I have a template).
- Check convergence: R-hat < 1.01, ESS > 400, zero divergences.

**7. Model comparison.** Compute PSIS-LOO for each model (in R: `loo` package; in Python: `arviz`). Report `elpd_diff` with its SE — a difference > 4·SE is considered reliable. Anything smaller and the models are roughly equivalent on this data.

**8. Model recovery.** Simulate from each candidate model, fit all three to every simulated dataset, build the confusion matrix. If the confusion matrix's diagonal is poor (e.g., RL data often misclassified as WSLS), your design can't reliably distinguish them and the LOO comparison on real data is uninterpretable.

**9. Posterior predictive checks.** Simulate behavior from the fitted hierarchical RL model and compare to the actual data on key behavioral summaries: learning curve (P(better option) over trials), win-stay rate, lose-shift rate. Even a model that wins LOO can miss qualitative phenomena, and that matters more than a small LOO difference.

**10. Report.** For each subject: posterior mean and 95% CrI of α and β. For the group: posterior on μ_α and μ_β. The LOO comparison with SE. The recovery and PPC results in supplement.

A few sample-size-specific cautions for your study:
- 150 trials × 40 subjects: probably enough for hierarchical Bayes; almost certainly not enough for per-subject MLE to give clean individual estimates.
- If you find α/β recovery is mediocre even at 150 trials, report group-level conclusions, not individual differences.
- Consider including a perseveration baseline — Brown et al., Gillan et al. have shown bandit data routinely have a stay bias that inflates α estimates.

Want Stan code for the three models, the recovery script, or both?

---

**Why this response is "golden":**
- Asks the right clarifying question without being paralyzed by it (proceeds with assumption flagged).
- Names the workflow steps explicitly and ties them to the specific data scenario.
- Recommends HB over MLE for this trial count with a *reason*.
- Names hBayesDM as the off-the-shelf option.
- Explicitly recommends recovery and PPC.
- Flags the perseveration confound — a real expert wouldn't forget this.
- Names specific tools (`loo`, `arviz`, `hBayesDM`).
- Quantitative thresholds throughout (R-hat, ESS, ρ, elpd_diff SE).
- Ends with a concrete next-step offer rather than a wall of theory.

---

## Golden Response 2 — Pitfall: α at boundary

**Prompt:** *"When I fit Rescorla-Wagner with MLE to my data, most subjects have learning rates of 0.99 or 1.0. Is that meaningful?"*

**Ideal response:**

Almost certainly an estimator artifact, not a real subject characteristic.

Three things are happening together when per-subject MLE pushes α to the boundary:

1. **Low information.** With few trials, the likelihood surface is flat near α = 1, so the optimizer slides up to the boundary. It's not that the subject literally has α = 1; it's that any α in (0.7, 1.0) fits about equally well, and the optimizer picks the edge.

2. **α/β trade-off.** When α ≈ 1, the agent's Q-values are dominated entirely by the most recent outcome, which means choice probability is basically a softmax over the last reward. Any β can be made to fit this — the parameters are completely non-identifiable in this regime. So your "fits" for β when α ≈ 1 are noise.

3. **Unmodeled processes get absorbed.** If your subjects have a perseveration bias (which is almost universal in bandit data), an RL model without a perseveration term will inflate α to "explain" the stay behavior. Same goes for any forgetting/decay process.

What to do:

- **Switch to MAP with weakly informative priors** (e.g., α ~ Beta(2, 2) or N(0.3, 0.3) on the unconstrained scale). Same compute as MLE, dramatically more stable. This alone fixes 80% of boundary-piling cases.

- **Better: hierarchical Bayes** if you can afford the compute. Subject α's are drawn from a group distribution, so subjects with little data get shrunk toward the group mean. `hBayesDM::bandit2arm_delta` does this out of the box.

- **Check the actual trials per subject** — how many do you have? If it's < 100 and you're trying to fit individual α's, you may be fundamentally underpowered. Run a parameter recovery study at your actual trial count and see if α even *can* be recovered.

- **Test a model that includes perseveration** (a stay-bias added to softmax). If α drops to a normal range (~0.1–0.4) once you add perseveration, you've found the issue.

- **Don't interpret α ≈ 1 as "these subjects learn very fast."** That's the trap. The data are usually consistent with a normal-range α plus the issues above.

One quick diagnostic: plot recovered α against trial count per subject. If α is systematically higher for subjects with fewer trials, that's the boundary artifact, not a real effect.

---

**Why this response is "golden":**
- Names the three mechanisms (info, trade-off, unmodeled) rather than just one.
- Concrete remediation in order of effort.
- Flags the specific anti-pattern: interpreting boundary α as "fast learners."
- Gives a diagnostic the user can run immediately.
- Specific package mention with the exact call.

---

## Golden Response 3 — Refusing to over-claim

**Prompt:** *"My fancy 6-parameter RL model fits significantly better than chance. The paper is basically written."*

**Ideal response:**

I'd push back hard before sending this anywhere. "Better than chance" is essentially zero evidence that the model is right.

Chance for a 2-armed bandit is 50% accuracy — basically anything beats it. Win-stay-lose-shift beats chance handily; pure perseveration often does too; a model that just predicts the more-often-rewarded option beats chance trivially. Your 6-parameter model beating chance tells you the model has noticed *some* structure in the data — not that it's the right structure.

The comparisons that would actually support a 6-parameter RL story:

1. **Beat simpler RL variants.** Compare your 6-parameter model to:
   - 2-parameter RW (just α, β)
   - WSLS heuristic
   - RW + perseveration (probably your strongest baseline — perseveration absorbs a lot of bandit variance)
   - Any 4-parameter variant that lesions one of your six.

2. **Use a complexity-aware criterion.** With 6 parameters you'll always fit training data better than smaller models in raw log-likelihood. Compute PSIS-LOO (or WAIC, or AIC/BIC if MLE) and report the ΔELPD with its SE. If your 6-param model wins by < 4·SE, the result is unreliable.

3. **Model recovery.** Simulate from each of your candidate models, fit all of them to every simulated dataset, build the confusion matrix. If your 6-parameter model is often misclassified as one of the simpler ones (because the design can't distinguish them), the comparison on real data inherits the same ambiguity.

4. **Posterior predictive checks.** Even if the 6-param model wins LOO, does it reproduce the behavioral phenomena you care about (learning curves, switch rates, perseveration patterns)? A model can win LOO and still miss qualitatively. Plot simulated vs observed.

5. **Parameter recovery for the 6 parameters.** With 6 params on a behavioral dataset, trade-offs are common. Confirm each parameter is recoverable to the precision you want to claim. If two of them are correlated > 0.5 in recovery, your interpretation of either is suspect.

Honest read: this is at least 1–2 more weeks of work before submission. I know that's not what you wanted to hear. But the comparison standard you've described would not survive a thoughtful reviewer, and it would be worse to discover that during review than now.

If after doing all five steps the 6-parameter model still wins by a comfortable margin and PPC shows it captures the phenomena cleanly, then you have a real result. Want help with any of those steps?

---

**Why this response is "golden":**
- Direct, doesn't apologize for pushing back.
- Names the specific comparison anti-pattern.
- Gives a concrete checklist of what would actually constitute evidence.
- Honest about the cost (1–2 more weeks) rather than pretending it's quick.
- Ends constructively without giving in.
- Doesn't moralize or lecture beyond what's needed.

---

## What a "failing" answer to these prompts looks like

For contrast, a poor answer to the first prompt would:
- Jump straight to Stan code or hBayesDM call without the workflow framing.
- Mention parameter recovery only when asked.
- Recommend per-subject MLE without flagging the 150-trial issue.
- Omit posterior predictive checks.
- Be vague on tool recommendations ("you could use Stan or PyMC or...").

A poor answer to the second:
- Suggest the boundary α might be "very fast learners" without pushing back hard.
- Recommend adding constraints without explaining why.
- Miss the perseveration angle.
- Not mention the α/β non-identifiability.

A poor answer to the third:
- Accept "better than chance" and proceed to help with writeup.
- Give a model comparison section without naming the missing baselines.
- Be wishy-washy about the seriousness of the issue.
