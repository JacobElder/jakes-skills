# Network Analysis Skill

A skill that applies practitioner-grade methodology to network analysis, social network analysis (SNA), and graph problems. It gives the agent the conviction to raise the structural pitfalls that standard tools paper over — bipartite projection artifacts, modularity degeneracy, the homophily-contagion confound, temporal path validity, GNN leakage — and to give the opinionated, technically precise answer that a network scientist would give instead of validating whatever plan the user already has.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/network-analysis
```

Or manually:

```bash
cp -r jakes-skills/network-analysis ~/.claude/skills/network-analysis
```

Once installed, the skill applies automatically whenever you ask about networks, graphs, centrality, communities, diffusion, peer effects, ERGMs, temporal networks, GNNs, link prediction, or any system of nodes and edges — including informal descriptions like "I have data on who emails whom" or "I want to see how teams collaborate."

---

## Example use cases

### "I have co-authorship data — let me project and run Louvain"

> I have a person × project bipartite network (800 employees, 150 projects). My plan is to project to a person–person graph where edge weight = number of shared projects, then run Louvain community detection to find collaboration communities. Does that sound right?

Without the skill, the response calls the plan sound and suggests minor refinements:

> Your overall plan is sound and a common approach for this kind of problem. A few things worth knowing before you run it.
>
> Projecting a bipartite graph onto one mode (employees) and then running community detection is the standard workflow. The weight = number of shared projects is intuitive and easy to implement... raw co-participation counts have a known bias: prolific participants inflate edge weights. An employee on 50 projects will share edges with many people simply because of volume.
>
> Consider normalizing edge weights before running Louvain: Jaccard similarity — shared projects / union of projects... or Newman hyperbolic weighting...
>
> **Your plan is a standard, defensible approach.** The main refinement I would suggest: use `collaboration_weighted_projected_graph` (Newman hyperbolic weighting) instead of raw co-participation counts.

With the skill, the response flags the clique structure as a structural artifact before any analysis:

> On the right track conceptually, but there are two issues to fix before running Louvain — one that will meaningfully distort your results.
>
> **Issue 1: co-membership artifacts.** When you project a person × project bipartite graph, every person who shared a project gets connected to every other person in that project. If a large project had 40 employees, that single project creates a complete clique of 40 nodes — 40×39/2 = 780 edges. This is an artifact of co-membership, not evidence of a tight-knit collaboration group, and it will inflate clustering coefficients, inflate modularity scores, and bias community detection toward absorbing those large-project cliques.
>
> **The fix: backbone extraction with SDSM or FDSM.** The standard method for bipartite projections is the SDSM (Stochastic Degree Sequence Model) or the FDSM (Fixed Degree Sequence Model). These test each projected edge against a null model that preserves the bipartite degree sequence... retaining only edges that are statistically surprising given how many projects each person participates in.
>
> **Issue 2: edge weight ≠ relationship strength.** A shared count of 5 projects means something very different if one of those projects had 100 participants vs. 4 participants... raw weight suggests a stronger relationship, but the large-project contribution almost nothing in practice.
>
> **If you want a more principled approach**: since your data is bipartite, skip projection entirely and run a bipartite SBM directly on the person × project graph...

---

### "Louvain found 8 communities, Q = 0.67 — how do I report them?"

> I'm writing a paper on a co-authorship network (1,200 authors, 4,800 edges). I ran Louvain and got 8 communities with modularity Q = 0.67. That's a strong modularity score. How do I report the communities?

Without the skill, the response validates Q = 0.67 as strong and moves directly to reporting:

> Your setup — 1,200 authors, 4,800 edges, 8 communities, Q = 0.67 — is solid. A modularity of 0.67 is genuinely high (anything above 0.3 is conventionally considered meaningful; above 0.6 is strong). Here is how to report it rigorously.
>
> **Run the following before writing prose descriptions:** Size distribution. Internal density vs. external connectivity. Hub/core nodes...
>
> A community label like "Community 3 (n = 187, Q contribution = 0.11)" is necessary but not sufficient. Readers want to know what the cluster *means*. Here is the naming workflow: Step 1 — Extract the anchor authors...

With the skill, the response stops before naming anything:

> Before you name or describe these communities, there are several things that need to happen first — and a few flags to raise about Q = 0.67.
>
> **Stop: your modularity score is not a reliability certificate.**
>
> A modularity of 0.67 tells you that the partition has a high within-community edge fraction relative to a degree-preserving null. It does not tell you that the partition is stable, reproducible, or structurally real.
>
> **The degeneracy problem (Good, De Montjoye & Clauset 2010).** The modularity landscape has exponentially many near-optimal partitions that are structurally very different from one another. A single Louvain run returns one of these almost arbitrarily. Re-running with a different random seed on the same graph will produce a different partition — potentially assigning major authors to different communities — while achieving nearly identical Q. High Q does not distinguish between "the one true partition" and one of thousands of near-equivalent alternatives.
>
> **Q = 0.67 has not been compared to a null.** Run the same Louvain procedure on 1,000 configuration-model randomizations... If the null gives Q ≈ 0.65 on average, your "great" Q is barely above chance.
>
> **What you need to do before naming communities:** Run Louvain (or Leiden) 100+ times, compute pairwise ARI across runs. Mean ARI > 0.90: high stability, proceed. Mean ARI 0.70–0.90: moderate stability, use modal partition. Mean ARI < 0.70: **do not name communities** — switch to a Stochastic Block Model.

---

### "My regression shows peer influence on smoking"

> I ran a regression of students' smoking (binary) on the mean smoking of their nominated friends (proportion), controlling for gender, grade, and SES. My advisor says the coefficient of 0.43 (p < 0.001) shows peer influence. Does this approach work?

Without the skill, the response raises identification concerns but doesn't name the key cross-sectional fix:

> The coefficient of 0.43 on `mean_friends_smoking` means: for a one-unit increase in the proportion of close friends who smoke, a student's own smoking increases by 0.43 units... But this is an **association**, not a causal effect...
>
> **Reflection problem (Manski, 1993):** If you regress individual behavior on group mean behavior, and group membership is endogenous, the coefficient is not identified...
>
> **Consider stochastic actor-based models (SABMs).** The RSiena framework jointly models network evolution and behavior evolution over time... It requires panel data with at least two waves of both network and behavior measures.
>
> **Natural experiments or instrumental variables:** IV approaches require a valid instrument: something that affects who a student is friends with but does not independently affect their smoking behavior.

The response correctly flags Manski and Shalizi-Thomas but names IV only generically — never specifying the friends-of-friends instrument that Bramoullé et al. (2009) showed is identified from the network structure itself.

With the skill, the response names the cross-sectional identification strategy specifically:

> Your advisor's framing — "this shows peer influence" — is the most common misinterpretation in observational social network research...
>
> **The reflection problem (Manski 1993):** Your model is a linear-in-means model with a network-based peer measure. If peers influence you, then you also influence your peers, and everyone's smoking status is jointly determined...
>
> **Selection / homophily (Shalizi & Thomas 2011):** Shalizi and Thomas (2011) proved formally that in observational cross-sectional data, influence and homophily are generically confounded...
>
> **Option B: Use network structure as instruments (Bramoullé et al. 2009).** If you are stuck with cross-sectional data, there is still an identification strategy. Bramoullé, Djebbari & Fortin (2009) show that if your friendship network contains intransitive triads (student A nominates B, B nominates C, but A does not nominate C), then the smoking behavior of **friends-of-friends** provides a valid instrument for friends' smoking. The intuition: C's smoking affects A only through B, so if you instrument B's smoking with C's smoking and C's characteristics, you partial out the homophily confound...

---

## What the skill does

The base model knows network analysis methods. The skill gives the agent the *conviction to apply them correctly*. The skill's most important moves are:

- **Raise structural artifacts before running anything.** Bipartite projection inflates cliques. The disparity filter is wrong for bipartite projections — use SDSM or FDSM. The skill names the right tool instead of suggesting generic weight normalization.
- **Block conclusions until prerequisites are met.** Louvain communities cannot be named or interpreted until stability is established. SAOM requires longitudinal data with observable change between waves — not just "panel data."
- **Name the specific identification failure.** The linear-in-means peer effects regression hits the Manski reflection problem. Cross-sectional data cannot separate homophily from contagion (Shalizi & Thomas 2011). The Bramoullé friends-of-friends instrument is the cross-sectional fix — the skill names it instead of pointing generically to "IV approaches."
- **Distinguish degeneracy from stochasticity.** Louvain's multiple-run instability is not just random noise — it reflects the modularity landscape having exponentially many near-optimal partitions (Good et al. 2010). This is a different problem with a different fix (consensus partitioning, SBMs).
- **Enforce correct null models.** Q = 0.67 means nothing without comparison to a configuration-model null. ERGM estimates are meaningless without `mcmc.diagnostics()` and `gof()`. Temporal betweenness and static betweenness answer different questions — a node ranked first by static betweenness may rank near the bottom by temporal betweenness, not just at a different magnitude.

---

## Benchmark: skill vs. base model

Evaluated across 4 iterations using trap-based evals — prompts where the naive helpful answer validates a methodological error or omits a critical caveat. Each eval has 5 specific, objectively checkable assertions. Executor agents write responses without seeing the assertions; separate grader agents evaluate strictly against them.

### Iteration 4 — final results (8 scenarios)

```
with_skill:    100%  (40/40 assertions)
without_skill:  67.5%  (27/40 assertions)
delta:         +32.5pp
```

| Eval | With skill | Without skill | Delta |
|------|:---:|:---:|:---:|
| peer-effects | 100% | 60% | +40% |
| bipartite-projection-communities | 100% | 40% | +60% |
| ergm-degeneracy | 100% | 100% | +0% |
| centrality-process | 100% | 80% | +20% |
| temporal-aggregation | 100% | 40% | +60% |
| large-scale-tool-choice | 100% | 80% | +20% |
| community-stability | 100% | 40% | +60% |
| link-prediction-leakage | 100% | 100% | +0% |

The two non-discriminating evals (ergm-degeneracy, link-prediction-leakage) reflect topics where the base model already has robust coverage from the methods literature. They remain in the suite as regression guards.

### Where the base model fails most

| Scenario | What the trap is | With skill | Without skill |
|---|---|:---:|:---:|
| bipartite-projection-communities | Validates bipartite→project→Louvain without flagging clique inflation; never names SDSM/FDSM | 100% | 40% |
| community-stability | Calls Q = 0.67 "genuinely high" and moves to naming communities without establishing stability | 100% | 40% |
| temporal-aggregation | Suggests snapshot improvements but doesn't name time-respecting paths or specific temporal tools | 100% | 40% |
| peer-effects | Flags Manski/Shalizi-Thomas but points to generic IV rather than Bramoullé friends-of-friends specifically | 100% | 60% |
| centrality-process | Picks the wrong centrality for the substantive question; misses eigenvector failure on directed graphs | 100% | 80% |
| large-scale-tool-choice | Stays with NetworkX at 10M edges rather than switching to igraph/graph-tool/NetworKit | 100% | 80% |

### Iteration history

| Iteration | With skill | Without skill | Delta | Notes |
|---|:---:|:---:|:---:|---|
| 1 | 87.5% | 75.0% | +12.5pp | Baseline; simpler assertions |
| 2 | 100%* | 90%* | +10pp* | *Self-graded inflation; not comparable |
| 3 | 97.5% | 70.0% | +27.5pp | Separate executor/grader; harder assertions |
| 4 | **100%** | **67.5%** | **+32.5pp** | Fixed temporal rank-inversion gap |

---

## Eval suite

| # | Eval | Trap |
|---|------|------|
| 1 | `peer-effects` | Validates OLS peer-effects regression; misses Manski reflection and Shalizi-Thomas; names IV generically without Bramoullé |
| 2 | `bipartite-projection-communities` | Calls bipartite→projection→Louvain "standard and defensible"; suggests normalization instead of naming SDSM/FDSM backbone extraction |
| 3 | `ergm-degeneracy` | Uses `triangle` term in ERGM; proceeds without MCMC diagnostics |
| 4 | `centrality-process` | Applies eigenvector centrality to a directed weakly-connected graph; picks wrong centrality for the substantive question |
| 5 | `temporal-aggregation` | Aggregates 3 years of timestamped emails to a static graph; treats static betweenness as informative about communication dynamics |
| 6 | `large-scale-tool-choice` | Uses NetworkX on a 10M-edge graph; suggests algorithmic improvements without addressing library scalability |
| 7 | `community-stability` | Calls Q = 0.67 "strong community structure"; proceeds to name communities without stability analysis or null comparison |
| 8 | `link-prediction-leakage` | Random edge split for GNN link prediction leaks test edges through message passing; inflated AUROC from random negative sampling |

## Sources

The skill's positions are drawn from:

- **Wasserman, S. & Faust, K. (1994). *Social Network Analysis: Methods and Applications*.** Centrality, density, structural holes.
- **Newman, M. E. J. (2018). *Networks* (2nd ed.).** Community detection, modularity, null models, random graph theory.
- **Good, B. H., De Montjoye, Y.-A., & Clauset, A. (2010).** "Performance of modularity maximization in practical contexts." *Physical Review E* 81: 046106. — Modularity degeneracy; exponentially many near-optimal partitions.
- **Snijders, T. A. B. (2017).** "Stochastic actor-oriented models for network dynamics." *Annual Review of Statistics* 4: 343–363. — SAOM longitudinal requirements; co-evolution of network and behavior.
- **Shalizi, C. R. & Thomas, A. C. (2011).** "Homophily and contagion are generically confounded." *Sociological Methods & Research* 40: 211–239.
- **Manski, C. F. (1993).** "Identification of endogenous social effects: The reflection problem." *Review of Economic Studies* 60: 531–542.
- **Bramoullé, Y., Djebbari, H., & Fortin, B. (2009).** "Identification of peer effects through social networks." *Journal of Econometrics* 150: 41–55. — Friends-of-friends instruments.
- **Hunter, D. R., Handcock, M. S., Butts, C. T., Goodreau, S. M., & Morris, M. (2008).** "ergm: A package to fit, simulate and diagnose exponential-family models for networks." *Journal of Statistical Software* 24: 1–29.
- **Holme, P. & Saramäki, J. (2012).** "Temporal networks." *Physics Reports* 519: 97–125. — Time-respecting paths, temporal centrality, rank inversions.
- **Peixoto, T. P. (2014, 2017).** Stochastic block models, nested SBMs, graph-tool. — Principled community detection without resolution limits.
- **Hamilton, W. L. (2020). *Graph Representation Learning*.** GNNs, link prediction, message-passing leakage.
- **Ghasemian, A., Hosseinmardi, H., Galstyan, A., Airoldi, E. M., & Clauset, A. (2020).** "Stacking models for nearly optimal link prediction in complex networks." *PNAS* 117: 23393–23400. — GNNs vs. simple baselines under proper evaluation.
- **Traag, V. A., Waltman, L., & van Eck, N. J. (2019).** "From Louvain to Leiden: guaranteeing well-connected communities." *Scientific Reports* 9: 5234.
