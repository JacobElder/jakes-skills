# Psychometric Networks Skill

A skill for the network approach to psychological measurement — treating questionnaire items and clinical symptoms as nodes in a Gaussian Graphical Model rather than indicators of a latent variable. It gives the agent the conviction to apply field-specific conventions that the base model underuses: the `bootnet` accuracy-and-stability workflow, CS-coefficient thresholds, the goldbricker redundancy check, the Bringmann critique of betweenness and closeness, the Robinaugh Expected Influence fix for mixed-valence affect networks, and the Burger et al. (2023) reporting standards. This is an **intersection skill** — it assumes the user's general psychometrics and network-analysis parent skills are loaded and focuses only on what is specific to running these methods on psychological items.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/psychometric-networks
```

Or manually:

```bash
cp -r jakes-skills/psychometric-networks ~/.claude/skills/psychometric-networks
```

Once installed, the skill applies automatically when the user mentions GGMs on items or symptoms, EBICglasso, bootnet, qgraph, IsingFit, graphicalVAR, mlVAR, mgm, psychonetrics, EGAnet, CS-coefficients, expected influence, edge accuracy, the network theory of psychopathology, or the latent-vs-network debate.

---

## Example use cases

### "My 15-node depression network has 91 edges — it's a hairball"

> I ran EBICglasso on my 15-node depression item network (N=210) using bootnet with default settings and got 91 edges out of a possible 105. Almost everything connects to everything — it's a hairball. Is this typical? What's going wrong and how do I make the network interpretable?

Without the skill, the response lists several diagnostic possibilities but never leads with gamma as the primary lever or names goldbricker for node redundancy:

> 91/105 edges is a red flag — EBICglasso is *supposed* to produce sparse networks. Something is pushing regularization toward near-zero, and there are several likely culprits.
>
> **1. Strong common factor structure (most likely root cause).** Depression scales are explicitly designed to be highly intercorrelated... even *after* partialling out neighbors, substantial residual associations survive regularization. GLASSO can't zero them out because they're genuinely non-zero partial correlations under a strong-factor structure.
>
> **2. γ tuning parameter too low.** The EBIC hyperparameter γ controls the complexity penalty. The bootnet default is `tuning = 0.5`, but if you're using `gamma = 0`... you get much denser networks. Check what you actually ran.
>
> **3. Pearson correlations on ordinal data.** If your depression items are Likert-scale... and you used Pearson correlations, the input matrix is misspecified. Polychoric correlations are the correct input for ordinal items.
>
> **Fix 1: Use `cor_auto` for polychoric correlations... Fix 2: Increase γ... Fix 3: Switch to TMFG...**

With the skill, the response leads with node redundancy, names the right tool immediately, then correctly explains gamma as the primary sparsity lever:

> 91 out of 105 edges (87% density) is pathologically dense — and it's a clear signal that something upstream is wrong before you even get to interpretation. Three culprits, roughly in order of suspicion:
>
> **Culprit 1: Node redundancy (check this first).** Depression scales are the canonical case. Items like "sad mood," "depressed affect," and "feels empty" have nearly identical conditioning sets — every other item predicts them equally well — so they produce near-identical columns in the partial-correlation matrix. This creates a cluster of very strong edges that then propagates spurious density throughout the graph.
>
> Run `goldbricker` before anything else:
> ```r
> library(networktools)
> gb <- goldbricker(data, threshold = 0.25, corMethod = "cor_auto")
> print(gb)
> ```
> `goldbricker` flags pairs whose partial-correlation profiles are so similar that they likely represent redundant nodes. Any pair flagged at `threshold = 0.25` should be either dropped or combined into a composite before re-estimation.
>
> **Culprit 2: Gamma is too liberal — increase it.** The EBIC tuning parameter `gamma` controls how aggressively the model penalizes edge inclusion. The default of `0.5` is fine for many settings but can be too liberal for highly correlated item sets... `gamma = 0.5` is the field default per Epskamp & Fried (2018), but for very correlated item sets values of 0.75–1.0 are defensible and commonly used.
>
> **Culprit 3: The conceptual problem.** If your 15 items are all from a single depression scale designed to measure one construct... the GGM is being asked: *"What are the pairwise conditional associations among items that all reflect the same underlying thing?"* The answer will always be "almost everything connects to everything."
>
> Don't tune `gamma` upward until you get a "nice-looking" sparse graph and then report the result as if it were a default analysis. If you increase gamma, justify the choice and report edge counts under both gamma = 0.5 and gamma = 1.0 as a sensitivity check.

---

### "A reviewer asked me to follow reporting standards for my GGM"

> I've finished a GGM network analysis of anxiety symptoms (N=340, 12 nodes, EBICglasso with gamma=0.5 and polychoric correlations). A previous reviewer criticized my write-up for not following current reporting standards. What should my methods and results sections include?

Without the skill, the response gives a solid general checklist but never names the authoritative reporting standards paper, and omits the cross-sectional/causal limitation as a required element:

> Great question — and a timely one, since reviewer expectations for network papers have crystallized substantially around a handful of landmark methodological papers. Here's what current standards call for.
>
> **Methods:** Node selection rationale; correlation type (polychoric); EBICglasso, γ = 0.5; layout algorithm for reproducibility; which centrality indices you will report.
>
> **Stability analyses ← most commonly missing.** Current standards (Epskamp et al., 2018) require: bootstrapped edge accuracy CIs, edge weight difference tests, CS-coefficients per centrality index.
>
> **Results:** Network visualization with edges colored positive/negative; full edge weight matrix; centrality results flagging which indices have CS ≥ 0.25; stability results with CS-coefficient per index and bootstrap CI plot.

With the skill, the response opens by naming Burger et al. (2023), frames causal limitations as a required element alongside the technical checklist, and flags the goldbricker check as something reviewers now expect:

> Good timing to get this right — the field has converged on a reasonably explicit checklist since **Burger et al. (2023), "Reporting standards for psychological network analyses in cross-sectional data," *Psychological Methods*.**
>
> **Methods — network estimation subsection:** (1) Estimator, package, and version; (2) `cor_auto` with explanation that items with ≤7 unique integers get polychoric correlations via `lavaan`; (3) tuning parameter γ = 0.5 with citation to Epskamp & Fried (2018); (4) node selection rationale — *the single most underreported element in early network papers*. Also note whether you checked for node redundancy (`networktools::goldbricker()`); with 12 anxiety items there's a real risk that near-synonymous items produce spuriously strong edges.
>
> **Methods — stability subsection** (the section most commonly flagged by reviewers):
>
> | Check | Method | What to report |
> |---|---|---|
> | Edge-weight accuracy | Non-parametric bootstrap, 1,000 iterations | Bootstrapped 95% CIs; note distinguishable edges via difference test |
> | Centrality stability | Case-dropping bootstrap, 1,000 iterations | **CS-coefficient for each centrality index reported** |
> | Difference tests | Bootstrapped edge and centrality difference tests | Which pairs are statistically distinguishable |
>
> If any CS-coefficient < 0.25, you **cannot interpret that centrality index** — it needs to be dropped from the results, not just flagged.
>
> **Explicit cross-sectional limitations statement.** This is not optional. A GGM on cross-sectional data cannot establish causal direction among symptoms, cannot establish that one node activates another, and cannot support intervention targets. State this in your Discussion. Reviewers at *Psychological Medicine*, *JAMA Psychiatry*, and methodology-aware outlets will look for it.

---

### "I'm interpreting centrality but my bootstrapped CIs overlap"

> My centrality plot shows node A has Strength = 0.42 (bootstrapped 95% CI: [0.18, 0.61]) and node B has Strength = 0.39 (CI: [0.17, 0.58]). My co-author says the heavily overlapping CIs mean A and B aren't significantly different in centrality and I shouldn't say either is 'more central'. Is that right?

Without the skill, the response correctly identifies the overlap fallacy but doesn't name the bootstrapped difference test or state the practical norm:

> Your co-author is applying a common shortcut that is actually incorrect. Overlapping confidence intervals do NOT mean two values are not significantly different...
>
> The width of the confidence interval for the *difference* between two estimates is generally narrower than what you'd infer by looking at whether the individual intervals overlap. Visual overlap is neither necessary nor sufficient for statistical non-significance...
>
> Run a formal test if you need to make a specific claim about ordering. In network analysis, this means running a bootstrapped difference test using `bootnet`.

With the skill, the response makes the same correction but adds the critical practical note — that non-distinguishability is the norm, not an anomaly:

> Your co-author's reasoning is wrong, but the practical conclusion may still be right — for a different reason.
>
> **The logic error:** overlapping bootstrapped CIs do not imply the difference is non-significant. The CI for the *difference* between two estimates is narrower than what visual inspection of individual intervals would suggest. Non-overlap is sufficient for significance but not necessary. The correct test is the bootstrapped difference test from `bootnet`.
>
> **The practical reality:** in most psychometric networks, few pairs of centrality values are statistically distinguishable from one another. Running the difference test typically reveals that you cannot claim any specific ordering among nodes with confidence. This is the norm — not a problem with your network or your sample. It means centrality *ordering* across nodes is more interpretable as a whole than any specific pairwise claim.
>
> What this means for your write-up: run the difference test, report whether A and B are distinguishable, and if they are not, describe centrality in relative/ordinal terms without singling out specific nodes. "Restlessness had the highest Strength, though the difference from the next-ranked node was not statistically significant" is defensible; "restlessness is the most central node" without the difference test is not.

---

## What the skill does

The base model knows the psychometric network literature. The skill gives the agent the *specific field conventions* to apply them correctly. The key moves:

- **Lead with node redundancy before estimation.** The `goldbricker` check (`networktools::goldbricker()`) is the first thing to run before EBICglasso, not an afterthought. Dense hairball networks are usually a node-redundancy or gamma problem, in that order. The skill enforces this diagnostic hierarchy.
- **Apply the CS-coefficient thresholds precisely.** CS ≥ 0.5 acceptable, ≥ 0.25 minimum to interpret, < 0.25 do not interpret. These are field conventions most base-model responses soften or omit.
- **Distinguish Expected Influence from Strength.** For mixed-valence affect networks, Strength (sum of absolute weights) masks sign and misranks nodes that have both large positive and large negative edges. Expected Influence (Robinaugh et al., 2016) is the correct default. The skill enforces this choice contextually rather than always recommending one over the other.
- **Name Burger et al. (2023) for reporting.** The authoritative reporting checklist for cross-sectional GGMs. The base model gives solid generic checklists; the skill names the paper and frames causal limitations as a required, not optional, element.
- **Gate the Bringmann critique.** Betweenness and closeness are inappropriate for dense weighted partial-correlation graphs (Bringmann et al., 2019) — but this caveat belongs only in psychometric contexts, not as a response to generic graph-theory questions. The skill applies the critique where relevant and stays neutral where it isn't.
- **State the difference-test norm.** Few centrality pairs are typically statistically distinguishable in published psychometric networks. This is the expected outcome, not a methodological failure, and users should frame their results accordingly.

---

## Benchmark: skill vs. base model

Evaluated across 3 iterations. Evals are conversational prompts graded by an LLM judge against specific, objective expectations. Executor and grader are separate calls to eliminate self-grading inflation.

### Iteration 3 — final results (8 scenarios, 39 total expectations)

```
with_skill:    97.4%  (38/39 expectations)
without_skill: 84.6%  (33/39 expectations)
delta:         +12.8pp
```

| Eval | With skill | Without skill | Delta |
|------|:---:|:---:|:---:|
| ggm-estimation-likert | 100% | 83% | +17pp |
| expected-influence-vs-strength | 100% | 80% | +20pp |
| bootstrap-ci-vs-difference-test | 100% | 80% | +20pp |
| hairball-gamma-tuning | 80% | 80% | +0pp |
| stability-interpretation | 100% | 100% | +0pp |
| node-selection-question | 100% | 75% | +25pp |
| negative-trigger-generic-network | 100% | 100% | +0pp |
| reporting-standards-checklist | 100% | 80% | +20pp |

The three non-discriminating evals (hairball-gamma-tuning iter-3, stability-interpretation, negative-trigger) reflect either base-model coverage that already matches the skill or single-run variance. They remain as regression guards.

### Where the base model fails most

| Scenario | What the gap is | With skill | Without skill |
|---|---|:---:|:---:|
| node-selection-question | Misses node redundancy as a concrete concern; never names `goldbricker` | 100% | 75% |
| ggm-estimation-likert | Misses the Epskamp, Borsboom & Fried (2018) tutorial reference | 100% | 83% |
| expected-influence-vs-strength | Names EI as the right index but doesn't make the unipolar-equivalence distinction | 100% | 80% |
| bootstrap-ci-vs-difference-test | Corrects the CI fallacy but doesn't state that non-distinguishability is the norm | 100% | 80% |
| reporting-standards-checklist | Gives a solid checklist but omits cross-sectional/causal limitations as required | 100% | 80% |

### Iteration history

| Iteration | With skill | Without skill | Delta | Notes |
|---|:---:|:---:|:---:|---|
| 1 | 92.3% | 89.7% | +2.6pp | Baseline; 5 of 8 evals non-discriminating |
| 2 | 97.4% | 87.2% | +10.3pp | 4 evals redesigned; goldbricker + betweenness gate added to skill |
| 3 | **97.4%** | **84.6%** | **+12.8pp** | Difference-test norm sentence added; eval 3 gap closed |

The jump from iteration 1 to iteration 2 reflects both skill improvements (two targeted additions) and eval redesign (replacing four non-discriminating evals with harder probes). The iteration 2→3 gain reflects the single sentence added about the difference-test norm closing the bootstrap-CI eval.

---

## Eval suite

| # | Eval | What it tests |
|---|------|--------------|
| 1 | `ggm-estimation-likert` | Full GGM pipeline on Likert data: EBICglasso, cor_auto, gamma, bootnet, canonical citation |
| 2 | `expected-influence-vs-strength` | Choosing Expected Influence over Strength for mixed-valence affect networks |
| 3 | `bootstrap-ci-vs-difference-test` | Overlapping CIs ≠ non-significant difference; name the bootstrapped difference test; state the norm |
| 4 | `hairball-gamma-tuning` | Dense hairball network: gamma as primary lever, cor_auto fix, node redundancy |
| 5 | `stability-interpretation` | Applying CS-coefficient thresholds (0.25/0.50) to specific reported values |
| 6 | `node-selection-question` | Node selection as theoretical choice; goldbricker for redundancy; Fried's work |
| 7 | `negative-trigger-generic-network` | Betweenness question with no psychometric context: answer generically, don't over-trigger |
| 8 | `reporting-standards-checklist` | Burger et al. (2023) checklist: estimation details, bootstrapped CIs, CS-coefficients, causal limitations |

---

## Sources

- **Epskamp, S., Borsboom, D. & Fried, E. I. (2018).** "Estimating psychological networks and their accuracy: A tutorial paper." *Behavior Research Methods* 50: 195–212. — The primary tutorial; bootstrapped accuracy and stability workflow.
- **Burger, J., et al. (2023).** "Reporting standards for psychological network analyses in cross-sectional data." *Psychological Methods*. — The authoritative reporting checklist.
- **Borsboom, D. (2017).** "A network theory of mental disorders." *World Psychiatry* 16: 5–13. — The theoretical manifesto for the network approach to psychopathology.
- **Robinaugh, D. J., Millner, A. J. & McNally, R. J. (2016).** "Identifying highly influential nodes in the complicated grief network." *Journal of Abnormal Psychology* 125: 747–757. — Introduction of Expected Influence centrality.
- **Bringmann, L. F., et al. (2019).** "What do centrality measures measure in psychological networks?" *Journal of Abnormal Psychology* 128: 892–903. — Why betweenness and closeness are inappropriate for dense weighted partial-correlation graphs.
- **Fried, E. I., Epskamp, S., Nesse, R. M., Tuerlinckx, F. & Borsboom, D. (2016).** "What are 'good' depression symptoms? Comparing the centrality of DSM and non-DSM symptoms of depression in a network analysis." *Journal of Affective Disorders* 189: 314–320. — Node selection shapes network structure.
- **Fried, E. I. (2017).** "The 52 symptoms of major depression: Lack of content overlap among seven common depression scales." *Journal of Affective Disorders* 208: 191–197. — Node heterogeneity in depression measurement.
- **Isvoranu, A. M., Epskamp, S., Waldorp, L. J. & Borsboom, D. (Eds.) (2022).** *Network Psychometrics with R: A Guide for Behavioral and Social Scientists.* Routledge. — Current textbook.
- **Constantin, M. A., Schuurman, N. K. & Vermunt, J. (2022).** "A general Monte Carlo method for sample size analysis in the context of network models." *Psychological Methods.* — Power analysis via simulation for network studies.
- **Forbes, M. K., Wright, A. G. C., Markon, K. E. & Krueger, R. F. (2017).** "Evidence that psychopathology symptom networks have limited replicability." *Journal of Abnormal Psychology* 126: 969–988. — Replication critique of cross-sectional networks.
- **Marsman, M., et al. (2018).** "An introduction to network psychometrics: Relating Ising network models to item response theory models." *Multivariate Behavioral Research* 53: 15–35. — Statistical equivalence between Ising models and latent-variable IRT models.
