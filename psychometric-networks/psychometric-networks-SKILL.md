---
name: psychometric-networks
description: Apply the network approach to psychological measurement — treating items/symptoms as nodes connected by partial-correlation edges rather than indicators of a latent variable. Use this skill whenever the user is estimating, interpreting, critiquing, or planning a "psychometric network", "symptom network", "network analysis of [questionnaire/symptoms/items]", a Gaussian Graphical Model (GGM) on psych data, an Ising network on binary items, or a temporal/contemporaneous network from ESM/EMA/daily-diary data. Trigger on mentions of qgraph, bootnet, EBICglasso, IsingFit, graphicalVAR, mgm, psychonetrics, EGAnet, expected influence, edge accuracy, centrality stability (CS-coefficient), the network theory of psychopathology, or the latent-vs-network debate. This skill is the intersection of psychometrics and network analysis and assumes the user already has the parent skills loaded — focus here on what's specific to running these methods on psychological items and on the field's published consensus and critiques.
---

# Psychometric networks

This skill covers the network approach to psychological measurement as developed primarily by the Amsterdam group (Denny Borsboom, Sacha Epskamp, Eiko Fried, Lourens Waldorp, Angélique Cramer) and collaborators (Donald Robinaugh, Payton Jones, Adela Isvoranu, Jonas Haslbeck, Laura Bringmann, Aidan Wright, and others). It is the *intersection* of psychometrics and network analysis: use the parent skills for general latent-variable modeling or general graph theory.

## What makes a network "psychometric"

A psychometric network is a model where:

1. **Nodes are psychological variables** — typically symptoms, items, behaviors, affects, or attitudes measured on the same set of persons.
2. **Edges are pairwise statistical associations conditional on every other node** — in the cross-sectional Gaussian case, partial correlations; in the binary case, Ising couplings; in time-series, lagged or contemporaneous partial regressions.
3. **The model is offered as a substantive alternative to the common-cause latent-variable model**, not just a visualization. Under the network theory of psychopathology (Borsboom, 2017, *World Psychiatry*), a "disorder" is the equilibrium behavior of a directly interacting symptom network, not the reflection of an underlying latent disease entity.

The third point is the conceptual move that distinguishes this field from (a) generic SEM/factor analysis applied to items and (b) generic network science applied to any data. Keep it in mind when interpreting results — almost every methodological choice here ties back to it.

## When the user wants you to estimate a network

Ask, or infer, what kind of data they have. The standard recipe branches on this:

| Data type | Model | R workhorse | Default in `bootnet` |
|---|---|---|---|
| Continuous / Likert (cross-sectional) | Gaussian Graphical Model (GGM) via graphical lasso + EBIC | `qgraph::EBICglasso`, `bootnet::estimateNetwork` | `default = "EBICglasso"` |
| Binary (cross-sectional) | Ising model | `IsingFit::IsingFit` | `default = "IsingFit"` |
| Mixed continuous/categorical | Mixed Graphical Model | `mgm::mgm` | `default = "mgm"` |
| Intensive longitudinal / ESM (n=1 or multilevel) | graphical VAR — temporal + contemporaneous networks | `graphicalVAR::graphicalVAR`, `mlVAR::mlVAR` | n/a |
| Latent network / hybrid SEM-network | Confirmatory psychometric network analysis | `psychonetrics` | n/a |
| Exploratory factor-like dimensionality | Exploratory Graph Analysis | `EGAnet::EGA` | n/a |

The single most common pipeline is GGM + EBICglasso, so default to that unless the data tells you otherwise. The canonical reference is **Epskamp, Borsboom & Fried (2018), "Estimating psychological networks and their accuracy: A tutorial paper" in *Behavior Research Methods*** — when the user asks "how do I do this", point them there first.

### Minimal GGM pipeline

```r
library(bootnet); library(qgraph)

net <- estimateNetwork(
  data,
  default   = "EBICglasso",
  corMethod = "cor_auto",   # auto-detects ordinal vars → polychoric
  tuning    = 0.5           # EBIC gamma; 0 = liberal, 1 = conservative
)
plot(net, layout = "spring", theme = "colorblind")
centralityPlot(net, include = c("Strength", "ExpectedInfluence"))
```

`cor_auto` matters: items with ≤7 unique integer values are treated as ordinal and entered as polychoric correlations via `lavaan`. Forgetting this and feeding Pearson correlations on Likert data is one of the most common errors — Pearson correlations on ordinal data are inflated relative to their polychoric equivalents, which makes it harder for the graphical lasso to shrink edges to zero and can directly cause an artificially dense or "hairball" network. When a user reports unexpectedly high edge density, check whether polychoric correlations were used before investigating other causes. `tuning = 0.5` (gamma) is the field default per Epskamp & Fried (2018); lower gives a denser, more exploratory graph, higher gives a sparser, more conservative one.

### Intensive longitudinal data

For ESM/EMA data, the field standard is the **graphical VAR**, which produces two networks per person (or two group-level networks):

- a **temporal** network of lag-1 directed edges (predicts symptom at *t* from symptoms at *t-1*, controlling for all others), and
- a **contemporaneous** network of partial correlations among residuals (within-occasion associations after the temporal structure is removed).

Use `graphicalVAR` for single-subject (idiographic) designs and `mlVAR` for multilevel data where you also want a between-subjects network. Detrending and stationarity assumptions matter a lot here — flag them when reviewing analyses.

## Accuracy and stability — the non-negotiable second step

A psychometric network without accuracy and stability checks is incomplete and, in 2018+ standards, not publishable in the methodology-aware journals. The `bootnet` package exists primarily to make these routine. Always recommend three checks, all from Epskamp, Borsboom & Fried (2018):

1. **Bootstrapped edge-weight CIs** (`bootnet(net, nBoots = 1000, type = "nonparametric")`) — *non-overlapping CIs do not equal a significant difference*; use the bootstrapped difference test instead. Edge ordering is generally more trustworthy than absolute edge values.
2. **Centrality stability** via case-dropping subset bootstrap (`bootnet(..., type = "case")`) summarized by the **CS-coefficient**: the largest proportion of cases that can be dropped while keeping centrality order correlated ≥0.7 with the original (with 95% probability). **Rule of thumb: CS ≥ 0.5 is acceptable, ≥ 0.25 is the minimum to interpret centrality at all, < 0.25 means do not interpret.**
3. **Bootstrapped difference tests** for edges and centrality indices — these tell you which pairwise comparisons are actually distinguishable.

Sample size requirements are not trivial. For a 20-node GGM, several hundred cases are typically needed for stable centrality; for denser true networks and more nodes, more. There is no single magic number — the field has converged on running power analysis via Monte Carlo simulation (`bootnet`'s simulation functions; Constantin, Schuurman & Vermunt, 2022) and reporting CS-coefficients rather than citing a rule of thumb. Isvoranu & Epskamp (2023, "Which estimation method to choose") is the modern reference for estimator selection across data conditions. In practice, the bootstrapped difference test typically shows that few pairs of centrality values are statistically distinguishable from one another; this is the norm in most published psychometric networks, not a methodological failure — it means centrality ordering is more interpretable than absolute values or pairwise rankings.

## Centrality — be conservative and skeptical

This is where psychometric networks diverge sharply from social-network conventions. The field has converged on three rules:

1. **Strength** (sum of absolute edge weights) is the centrality index most defensible to report. It corresponds directly to the model's parameters.
2. **Expected Influence** (Robinaugh, Millner & McNally, 2016, *J Abnormal Psychol*) is preferred over Strength when edges can be negative, because Strength sums absolute values and so misses the sign. For mood/affect networks with mixed-valence edges, default to Expected Influence.
3. **Closeness and Betweenness should generally not be reported** for psychometric networks (Bringmann et al., 2019, *J Abnormal Psychol*, "What do centrality measures measure in psychological networks?"). They were designed for flow/distance interpretations on sparse unweighted graphs that don't transfer to dense weighted partial-correlation graphs of psych items, and they are typically unstable. If the user has them in a draft, suggest dropping them. **Context gate**: apply this caveat only when the user is clearly working on psychological item or symptom data. For a general graph-theory question about what betweenness or closeness measures, answer it as a network-science question without volunteering this critique — a brief mention that the interpretation differs in dense weighted settings is fine, but the Bringmann critique should not be the centerpiece of a generic answer.

Centrality is not causal importance. A high-strength node is not necessarily a good intervention target — that requires a causal model the cross-sectional GGM does not supply. Treat centrality as a descriptive summary of the estimated graph, nothing more.

## The latent-vs-network debate — what's actually settled

A user reading the popular network-analysis literature can come away with the impression that networks have superseded latent-variable models. They have not. Be calibrated:

- **Mathematically**, the Ising model and a unidimensional latent-variable model with appropriate item parameters can be statistically equivalent (Marsman et al., 2018; van der Maas et al., 2006). A GGM and a factor model are not generally equivalent but can fit the same data well. You usually cannot distinguish them from cross-sectional data alone.
- **The network claim is therefore more philosophical/causal than statistical**: it says the *generative story* is direct interactions, not a common cause. Whether this is true is an empirical question requiring intervention, temporal data, or theory — not something you read off a `qgraph` plot.
- **Replicability of cross-sectional networks** has been weaker than early enthusiasm suggested. Forbes, Wright, Markon & Krueger (2017, *J Abnormal Psychol*) and subsequent exchanges with Borsboom, Fried, Epskamp et al. are the touchstone. Modern guidance is to use larger samples, report stability metrics, and treat exploratory network structure as hypothesis-generating.
- **Symptoms are not natural kinds.** Fried (2017, "The 52 symptoms of major depression: Consequences for the network approach") and Fried & Nesse (2015, "Depression is not a consistent syndrome") emphasize that the nodes themselves — DSM symptom items — are theoretically loaded choices, not neutral observables. Fried, Epskamp, Nesse, Tuerlinckx & Borsboom (2016) "What are 'good' depression symptoms?" specifically examines how node selection changes network structure. Node selection matters as much as estimation. Beyond theoretical justification, **node redundancy** is a concrete practical risk: near-duplicate items (e.g., "sad mood" and "depressed affect") have nearly identical conditioning sets, producing spuriously strong edges that inflate those nodes' centrality. Run `networktools::goldbricker(data)` before estimation to flag item pairs whose partial-correlation profiles are nearly identical; consider pruning or combining items flagged as redundant. The `networktools` package also provides `bridge()` for bridge centrality in communities.

When a user presents network results, the right reviewer questions are usually about (a) what nodes were chosen and why, (b) what the sample size buys them in stability, and (c) whether they're making causal claims their design supports — not about the estimation algorithm.

## Reporting checklist

When helping a user write up a psychometric network analysis, the modern minimum is:

- Data type, node selection rationale, and sample size.
- Estimator and tuning parameter (e.g., "EBICglasso, gamma = 0.5, polychoric correlations via cor_auto").
- The plotted network with layout specified (typically the Fruchterman-Reingold spring layout, `layout = "spring"` in qgraph).
- Edge-weight matrix or supplementary table.
- Bootstrapped edge-weight CIs and the bootstrapped difference test for the edges/nodes the authors interpret.
- Centrality plot (Strength and/or Expected Influence only by default) with CS-coefficients reported.
- Explicit acknowledgment of cross-sectional/causal limitations.

If any of these are missing in a draft you're reviewing, flag them. The published reporting standards reference is **Burger et al. (2023), "Reporting standards for psychological network analyses in cross-sectional data"** in *Psychological Methods* — point users there if they want the authoritative checklist.

## Pointers for further depth

The field moves quickly and consolidates in a few canonical sources. Send the user to these rather than reasoning from first principles when they need depth:

- **Isvoranu, Epskamp, Waldorp & Borsboom (Eds.) (2022), *Network Psychometrics with R: A Guide for Behavioral and Social Scientists*.** Routledge. The current textbook.
- **Epskamp, Borsboom & Fried (2018)** in *Behavior Research Methods* — the tutorial paper, freely available; the practical reference.
- **Borsboom (2017)** in *World Psychiatry* — the theoretical manifesto for the network theory of psychopathology.
- **Robinaugh, Hoekstra, Toner & Borsboom (2020)** in *Psychological Medicine* — a decade-in review of where the field has and hasn't delivered.
- **`psych-networks.com`** — the field's blog, run by Fried, has running commentary on debates and new methods.

## Boundary with causal inference methods

Psychometric networks, causal discovery algorithms, and structural equation models all use graph structures and sometimes causal language. They are fundamentally different tools with different inferential goals. Get this boundary right when the user conflates them.

### GGM vs. causal discovery (PC, FCI, LiNGAM, GES)

A **Gaussian Graphical Model** estimates the partial correlation graph by regularizing the precision matrix. Its edges are undirected and represent conditional dependence — two nodes connected in a GGM share variance after conditioning on all other nodes. That is a statistical regularization claim, not a causal claim. Edge absence under EBICglasso is a regularization artifact, not evidence of causal independence: the lasso can zero out a true partial correlation if the sample is small or the tuning parameter is conservative.

**Causal discovery algorithms** (PC, FCI, LiNGAM, GES, GFCI, etc.) explicitly attempt to identify causal structure from observational data using conditional independence tests and orientation rules (Meek rules, FCI rules, LiNGAM's ICA-based approach). They output a DAG or CPDAG with causal semantics under strong assumptions: the Markov condition, the faithfulness assumption, acyclicity (for DAG methods), and — for PC — no hidden common causes. When these assumptions hold, the orientation of edges carries causal meaning. When they don't (and hidden confounders are common in psychology), the orientation is unreliable.

Key traps to prevent:
- **Interpreting GGM edge weights as causal effects.** They are partial correlations, not causal effect estimates. A weight of 0.3 between depression and fatigue does not mean "depression increases fatigue by 0.3 units if you intervene on depression."
- **Concluding that a "hub" node causes other symptoms.** Centrality in a GGM reflects statistical connectivity (how much a node's value co-varies with its neighbors, net of the rest), not causal influence. A node can be highly central purely because it shares measurement variance with many neighbors.
- **Treating GGM communities as causal modules.** Walktrap or Louvain communities from a GGM reflect statistical clustering, not causally coherent subsystems.
- **Claiming PC/GGM equivalence because both produce graphs.** The inferential goals are opposite: GGM estimates the precision matrix with regularization; PC tests conditional independence iteratively and orients edges using orientation rules. A GGM edge is symmetric (A–B). A PC edge carries a direction (A→B) with causal meaning under stated assumptions. They are not interchangeable.

If the user wants to explore conditional dependence patterns, bridge structure, or community detection without causal commitment, GGM is appropriate. If the user wants to infer causal structure and is willing to accept the strong assumptions (faithfulness, no hidden confounders, acyclicity), causal discovery algorithms are appropriate — but the assumptions must be stated explicitly and the output is a skeleton of candidate causal structures, not confirmed causal relationships.

### GGM vs. structural equation modeling / path analysis

**SEM and path analysis** are researcher-specified causal models. The researcher draws arrows based on theory; those arrows encode directional causal hypotheses (A→B means the researcher claims A causes B). Fit indices (CFI, RMSEA, SRMR) assess whether the specified causal structure is consistent with the data. Path coefficients are interpreted as causal effect estimates under the model. This is a *test of a pre-specified causal story*, not discovery.

A GGM is an *undirected* model. It can identify that self-esteem and depression are conditionally dependent after controlling for all other measured variables, but it cannot tell you whether self-esteem causes depression or vice versa (or both), because edges have no direction. It cannot test mediation. It cannot test a causal pathway from X through M to Y, because "through" implies direction.

When a user asks whether to use a GGM or SEM:
- **Test a directed causal hypothesis (mediation, moderation, path model)?** → SEM. The directed arrows encode the hypothesis; the fit test evaluates it.
- **Explore conditional dependence structure, bridge nodes between symptom clusters, or identify community structure without imposing direction?** → GGM.
- **Both?** → `psychonetrics` supports confirmatory GGMs that can be compared via SEM-style fit indices, allowing the user to test network structures rather than just estimate them.

The Borsboom & Cramer (2013, *Psychological Review*) paper frames symptom networks causally — symptoms cause each other — but that theoretical claim is not the same as the GGM encoding causal direction. The GGM is consistent with the causal interpretation but does not establish it.

## Granger causality: predictive, not interventional

Temporal networks built with `graphicalVAR` or `mlVAR` produce **directed** edges representing lagged predictions. These are commonly described as "Granger-causal" — a term that is widely misread as implying interventional causality. It does not.

**What Granger causality actually means:** X Granger-causes Y if past values of X improve prediction of Y beyond Y's own past (Granger, 1969, *Econometrica*). It is a statement about incremental predictive validity in time series, not about what would happen if you intervened on X. The name is historical and misleading — Granger himself acknowledged the limitation. Two variables can exhibit Granger causality purely because they are both caused by a common third variable C with a lagged effect (C→X and C→Y, offset by one lag): the model will show X→Y even though X does not cause Y.

**What Granger causality cannot handle:**
- Hidden common causes (latent variables driving multiple observed symptoms)
- Instantaneous effects (within-occasion, same-lag associations — handled separately by the contemporaneous network in graphicalVAR, but still not identifiably causal)
- Non-linear dynamics
- Short time series with feedback loops (Runge et al., 2019, *Science Advances*, "Detecting and quantifying causal associations in large nonlinear time series datasets")

**The right language:** When describing `graphicalVAR` temporal edges, use "Granger-predicts" rather than "causes":
- Correct: "Anxiety Granger-predicts depression" or "past anxiety is predictive of future depression beyond depression's autocorrelation"
- Incorrect: "Anxiety causally predicts depression" or "anxiety drives depression over time"

**Contrast with interventional causality.** Pearl's do-calculus (Pearl, 2009, *Causality*) defines causality in terms of interventions: X causes Y if setting X=x (via external intervention) changes the distribution of Y. This requires a causal graph with no hidden confounders (or explicit accounting for them). Granger causality does not satisfy the do-calculus definition. The potential outcomes framework (Rubin) similarly requires intervention or assignment to treatment — temporal prediction does not suffice.

**In psychometric networks specifically:** `graphicalVAR` temporal edges are frequently interpreted as "X activates Y over time" or "X is a causal precursor of Y." These are stronger claims than the data support. The correct claim is that knowing a person's level of X at time *t* helps predict their level of Y at time *t+1*, beyond knowing their own prior level of Y. That is meaningful and worth reporting, but it is a predictive temporal association, not an interventional causal claim. Always flag this distinction when reviewing graphicalVAR output.

When a user reports a temporal network finding, prompt them to:
1. Replace "X causes Y" with "X Granger-predicts Y" or "past X predicts future Y"
2. Acknowledge that the Granger temporal edge is consistent with, but does not establish, X as a causal driver of Y
3. Note the common-cause alternative: both X and Y may be driven by an unmeasured variable
4. Distinguish temporal network edges (Granger/lagged) from contemporaneous network edges (within-occasion partial correlations, also not interventionally causal)

## Python and other ecosystems

R remains dominant; the canonical packages (`qgraph`, `bootnet`, `IsingFit`, `mgm`, `graphicalVAR`, `mlVAR`, `psychonetrics`, `EGAnet`) have no full Python equivalent. If the user wants Python, options are: `scikit-learn`'s `GraphicalLasso`/`GraphicalLassoCV` for the GGM estimation step, `networkx` for centrality on the resulting adjacency, and `statsmodels` for VAR; but you lose `bootnet`'s accuracy/stability machinery and the polychoric handling, and you'll need to roll those yourself. For most users, the right answer is to do the network estimation in R via `reticulate` or a saved-output handoff and bring results back to Python for downstream work.
