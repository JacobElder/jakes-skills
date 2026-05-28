---
name: network-analysis
description: Apply rigorous network analysis (also called graph analysis, social network analysis, SNA, or network science) to relational data. Use this skill whenever the user mentions networks, graphs, nodes/edges, ties/relations, communities, centrality, influence, contagion/diffusion, homophily, blockmodels, ERGMs, SAOM/RSiena, stochastic block models, network motifs, multilayer/multiplex/temporal networks, graph embeddings, GNNs, link prediction, or asks "who is most influential/central", "what are the communities/clusters/cliques", "how does X spread", "are people similar because they're connected or connected because they're similar", or wants to model an organizational chart, citation network, social media graph, brain connectome, supply chain, knowledge graph, or any system of nodes and edges. Also use when the user has edge lists, adjacency matrices, .gml/.graphml/.pajek/.net/.edgelist files, or asks about NetworkX, igraph, graph-tool, statnet, ergm, sna, or RSiena. Even when the user just describes a relational system informally ("I have data on who emails whom", "I want to see how teams collaborate"), this skill applies — don't wait for them to say the word "network".
---

# Network Analysis

This skill encodes practitioner-grade methodology for analyzing networks — the kind of decisions that distinguish defensible analysis from confidently wrong analysis. Network methods have an unusually high ratio of pitfalls to principles: the same dataset analyzed with default settings in different tools can produce contradictory conclusions about who is influential, how many communities exist, or whether peers influence each other. This skill is built around those decision points.

## The first question: what kind of network do you have?

Before any analysis, classify the network along these axes — they determine which methods are legal and which are nonsense. A method that's appropriate for one type and applied to another is the most common source of bad network analysis. Ask the user (or examine the data) for each:

- **Mode**: one-mode (single node type, e.g. people→people), two-mode/bipartite (e.g. people→events, authors→papers), or multilevel/multimode
- **Directionality**: directed (asymmetric, e.g. who follows whom, advice-seeking) or undirected (symmetric, e.g. coauthorship)
- **Weight**: binary (tie/no tie), weighted (frequency, intensity, distance, similarity), or signed (positive/negative)
- **Multiplicity**: single-relation or multi-relation (friendship + advice + dislike); if multi-relation, possibly multiplex/multilayer
- **Time**: cross-sectional snapshot, panel/longitudinal (waves), or continuous-time event sequence (temporal network)
- **Boundary**: complete network (all nodes in a defined population observed), egocentric (each respondent's local neighborhood), or sampled
- **Scale**: small (<500), medium (500–10⁴), large (10⁴–10⁶), or massive (>10⁶). Scale changes which library is viable (NetworkX → igraph → graph-tool → NetworKit/cuGraph) and which algorithms are tractable.

These choices propagate. For example: a bipartite network projected to one mode produces a weighted network whose edge weights are *not* a measure of relationship strength in the usual sense — they're induced co-membership counts, and they need backbone extraction before community detection or centrality can be interpreted. A "directed" friendship network where reciprocity wasn't measured is really undirected with measurement error. See `references/data_decisions.md` for the full decision tree and the common mistakes each branch enables.

## When the user asks a question, identify the underlying task

Network questions usually map to one of these archetypes. Each has a default method *and* a list of decisions to surface to the user — they often don't know the choice matters:

| User's question (paraphrased) | Task | Where to start |
|---|---|---|
| "Who is the most important/influential/central?" | Node-level structural position | `references/centrality.md` |
| "What are the groups/clusters/communities/cliques?" | Mesoscale partition | `references/communities.md` |
| "How does X spread / who would I target?" | Diffusion / influence maximization | `references/dynamics.md` |
| "What kinds of ties form / why is this network shaped this way?" | Generative statistical model | `references/ergm_saom.md` |
| "Are similar people connected, or do connections make people similar?" | Selection vs. influence (homophily vs. contagion) | `references/peer_effects.md` |
| "How did the network change over time?" | Longitudinal / temporal analysis | `references/temporal.md` |
| "Predict missing/future links" | Link prediction | `references/prediction.md` |
| "Find vector representations of nodes" | Embeddings / GNNs | `references/embeddings.md` |
| "How do multiple networks interact?" | Multilayer / multiplex | `references/multilayer.md` |
| "Visualize this network" | Layout & graphical encoding | `references/visualization.md` |

Do not read every reference file; read the ones relevant to the user's task. Each reference is a self-contained 200–500 line deep dive with formulas, library calls, and pitfalls.

## Core principles that apply across all tasks

### 1. Centrality is plural; pick the right one

There is no "the" most central node. The seven centralities listed in most textbooks (degree, closeness, betweenness, eigenvector, Katz, PageRank, Bonacich's β) answer different questions and can rank nodes in directly opposing orders.

- **Degree** = local activity/volume
- **Closeness** = ability to reach others quickly (broken on disconnected graphs)
- **Betweenness** = control over information flow / brokerage
- **Eigenvector** = connected to other well-connected nodes (undefined sign on bipartite, fails on directed networks without strong components — use Katz or PageRank instead)
- **Katz** = eigenvector with a decay parameter (works on directed acyclic graphs where eigenvector fails)
- **PageRank** = Katz with random restarts (handles dangling nodes)
- **Bonacich's β** = eigenvector generalization where β > 0 means well-connected neighbors *help* (status), β < 0 means they *hurt* (bargaining power in negative-exchange networks)

Before computing any centrality, ask: what does "important" mean for the user's substantive question? Influence over fast-spreading information argues for betweenness or PageRank; bargaining power in negotiations may argue for negative-β Bonacich; vulnerability of infrastructure argues for percolation centrality. See `references/centrality.md` for the full menu plus temporal/group/bridge variants.

### 2. Community detection has no ground truth

Modularity-maximizing methods (Louvain, Leiden) are not "discovering" communities — they're optimizing an objective function with known pathologies:

- **Resolution limit**: modularity cannot detect communities smaller than √(2m), where m is edge count. In a network of 100,000 edges, communities under ~450 nodes are invisible to plain modularity.
- **Louvain produces disconnected communities** in some cases (this is why Leiden was invented — it guarantees connectedness).
- **Modularity is degenerate**: many very different partitions can have near-maximal modularity, so a single Louvain run is unreliable. Run many times, or use ensemble methods.
- **Modularity overfits random graphs**: it will find "communities" in Erdős–Rényi networks where none exist.

When the user wants robust community structure, prefer **Stochastic Block Models** (especially the nested/hierarchical SBM in graph-tool), which are generative, principled, and resist overfitting by minimizing description length. Use Leiden with the Constant Potts Model (CPM) when you want tunable resolution and don't need a generative model. Use Infomap when the dynamics on the network (random-walk flow) is what matters, e.g., information cascades. See `references/communities.md`.

### 3. Statistical network models require care: ERGM degeneracy is real

ERGMs (Exponential Random Graph Models) are the workhorse for "why does this network look the way it does?" but the naive specification with `triangle` and `kstar(2)` terms is *almost always degenerate* — the MCMC will collapse to the empty graph or the complete graph, and the estimates are meaningless. The fix, from Snijders, Pattison, Robins, and Handcock (2006) and Hunter (2007), is to use **geometrically weighted statistics**: `gwesp` (geometrically weighted edgewise shared partners) instead of `triangle`, `gwdegree` instead of `kstar`, `gwdsp` (geometrically weighted dyadwise shared partners). These give curved exponential family models that estimate cleanly. Always run `mcmc.diagnostics()` and `gof()` after fitting. See `references/ergm_saom.md`.

For longitudinal data, **SAOM (Stochastic Actor-Oriented Models, RSiena)** and **TERGM/STERGM** answer different questions: SAOM models tie *changes* as continuous-time decisions by actors and is ideal for friendship dynamics where actors have agency; STERGM separately models tie formation and dissolution in discrete time and is better when "actors" don't choose (e.g., citation networks). The Block et al. (2018) comparison is the standard reference.

### 4. Homophily and contagion are confounded

This is Shalizi and Thomas (2011)'s central result: in observational data, you generally *cannot* separate "I do X because my friends do" (influence/contagion) from "I'm friends with these people because we both do X" (selection/homophily) without strong assumptions or design intervention. When the user wants to claim peer effects, this confound must be raised. SAOM with co-evolution of network and behavior is one of the few principled tools; randomized peer assignment, instrumental variables, and Egami-style double negative controls are others. The default of "I'll regress my outcome on the mean of my friends' outcome" hits Manski's **reflection problem** (perfect collinearity) and is *not* identified.

### 5. Visualization is analysis, not decoration

For networks of more than a few hundred nodes, default force-directed layouts (Fruchterman-Reingold, Kamada-Kawai) produce uninformative "hairballs". Solutions: (a) extract a backbone first (disparity filter for unipartite weighted, SDSM/FDSM for bipartite projections), (b) cluster first and lay out by community (use graph-tool's `draw_hierarchy` for nested SBM), (c) use a layout that respects community structure (ForceAtlas2 with LinLog mode, or Yifan Hu), (d) consider not visualizing the whole network — show a matrix view, a community-summary "metagraph", or small-multiples per subgroup. The "show me the network" instinct is often wrong; show what answers the question.

## Workflow

For any non-trivial network task, follow this loop. It catches the errors that downstream tools quietly absorb.

1. **Inspect before computing.** Print: n nodes, n edges, density, n connected components (and size of largest), is_directed, is_weighted, presence of self-loops, presence of isolates, degree distribution summary (mean, median, max, skewness). A surprising number of network errors come from misreading the data — e.g. an edge list with three columns where you assumed two and the "weight" you computed was actually a timestamp.

2. **State assumptions explicitly to the user.** "I'm treating this as undirected because you didn't specify direction" or "I'm dropping the 23 isolated nodes for the closeness calculation, since closeness is undefined for them." Make the choices visible.

3. **Pick the smallest sufficient tool.** NetworkX is the right default for graphs under ~10,000 nodes — most users have it installed, the API is readable, and the algorithms are well-tested. For larger graphs or when speed matters, switch to igraph (C backend, also available in R/Python). For very large graphs (millions of edges) or for advanced statistical models (nested SBMs, latent space), graph-tool is best (heavily templated C++, harder install). For massive graphs, NetworKit (parallel) or cuGraph (GPU). For temporal/dynamic analysis specifically, consider pathpy or teneto. See `references/tools.md`.

4. **Compute baseline structure first, then go to the user's question.** Density, degree distribution (plot on log-log if scale is non-trivial), reciprocity (if directed), transitivity / global clustering coefficient, assortativity (degree assortativity and any attribute assortativity), connected components. These are quick and they often reframe the question.

5. **Always compare to a null model.** A clustering coefficient of 0.3 means nothing until you compare to a configuration-model null with the same degree sequence. A modularity of 0.45 means nothing if a random graph would give 0.4. Use the configuration model (`networkx.configuration_model`, `igraph.Graph.Degree_Sequence`) or the appropriate ERGM null. For weighted networks, use the disparity filter's α to baseline edge significance.

6. **Sensitivity-check the headline result.** Centrality rankings should be checked under edge-weight perturbation; community partitions under different random seeds / different algorithms (Louvain vs. Leiden vs. SBM); model coefficients under term variation.

## Common mistakes to watch for and call out

These are errors Claude (and most analysts) make if not on guard. If the user's plan contains one of these, raise it before proceeding:

- **Projecting a bipartite network and then running standard SNA on the projection without backbone extraction.** The projection inherits a huge clique structure from each event/group node and inflates clustering, modularity, and centrality measures.
- **Computing eigenvector centrality on a directed network with weak components.** Use Katz or PageRank.
- **Computing closeness on a disconnected graph without explicit handling.** Either restrict to the largest component (and say so) or use harmonic centrality.
- **Using normalized degree across networks of different sizes** without realizing normalization assumes a complete graph denominator.
- **Treating Louvain's single output as "the" communities.** The modularity landscape is degenerate: many qualitatively different partitions have near-identical modularity (Good et al. 2010). This is not just stochasticity — re-running Louvain with the same seed on the same graph finds different optima. The correct workflow is: run 100+ times, compute pairwise ARI/NMI across runs to quantify stability, build a consensus partition if needed, *then* interpret. **Do not name or describe communities until stability is established.** High modularity (e.g., Q = 0.67) is not evidence of stable structure — compare Q to a configuration-model null.
- **Using `triangle` in an ERGM.** Almost always degenerate. Use `gwesp` (geometrically weighted edgewise shared partners) instead. The reason `gwesp` works where `triangle` fails: each additional shared partner contributes *geometrically less* than the last (controlled by the decay parameter α ≈ 0.25–0.75), breaking the explosive positive-feedback loop. Also use `gwdsp` (geometrically weighted dyadwise shared partners) for path-2 closure, and `gwdegree` in place of any `kstar` terms. After refitting, `mcmc.diagnostics()` and `gof()` are non-negotiable — a model with "significant" coefficients but degenerate MCMC is uninterpretable. The reported p-values from a degenerate model are artifacts, not evidence.
- **Snowball-sampled data analyzed as if it were a complete network.** Degree distributions, centralities, and densities are all biased; use RDS-aware estimators or restrict claims to local structure.
- **"Peer effects" from cross-sectional data with friendship.** Manski reflection + Shalizi-Thomas confound. SAOM, randomized experiments, or negative-control methods are needed. SAOM specifically requires *longitudinal panel data* — at minimum 2 waves, ideally 3+, with observable network change *and* behavior change between waves. Cross-sectional data cannot identify influence even with SAOM; the right cross-sectional fix is Bramoullé et al. GMM/IV using network structure (friends-of-friends as instruments).
- **Comparing temporal-network metrics computed on aggregated snapshots to ones computed on time-respecting paths.** They measure different things; the difference is the whole point of temporal network analysis.
- **Reporting a single number for a "scale-free" exponent.** Use Clauset-Shalizi-Newman MLE + bootstrap goodness-of-fit; many networks called scale-free aren't.
- **User-item interaction graphs (recommendation systems, purchases, content views) are bipartite — users and items are different node types.** Running standard community detection on the raw graph mixes user and item nodes into the same communities, which is usually meaningless. Either project to one mode (with backbone extraction), use bipartite SBM, or use bipartite-aware algorithms. This is the single most common error in recommendation-system graph analysis.
- **GNN link prediction with a random edge split leaks structure through message passing.** When test edges are present in the training graph's adjacency matrix during node encoding, the GNN learns representations that encode test-edge information. The fix is to mask all test and validation edges from message passing (PyG's `RandomLinkSplit` with `is_undirected=True` does this correctly). Also: random negative sampling inflates AUROC 10–20pp; use distance-2 hard negatives. Always compare to Adamic-Adar/resource-allocation baselines — GNNs under proper evaluation often match these simple heuristics on standard benchmarks (Ghasemian et al. 2020 PNAS).

## Communicating results

Network results are easy to misread. When reporting, do these things:

- **Always state the network's basic dimensions** (n, m, directed/undirected, weighted, density, components) before any derived metric.
- **Interpret centrality in the substantive language of the question**, not the metric. "Alice has the highest betweenness" → "Alice is the person whose removal would most disrupt information flow between subgroups."
- **For community partitions, report stability** (e.g. NMI across runs), not just the partition.
- **For ERGM/SAOM, report convergence diagnostics and goodness-of-fit**, not just coefficient tables. A model with significant coefficients but bad GoF tells you nothing.
- **When recommending action** (who to target, which tie to monitor), explain the assumption that links the metric to the action: "betweenness assumes information travels along shortest paths, which is approximately true for explicit referrals but not for diffuse communication."
- **Distinguish description from inference.** "This network has high modularity" is description. "These communities reflect real social groups" is inference and needs justification.

## Code patterns

For reproducibility, prefer this skeleton in Python:

```python
import networkx as nx  # or igraph as ig
import numpy as np
import pandas as pd

# 1. Load and inspect
G = nx.read_edgelist("...", create_using=nx.DiGraph, data=[("weight", float)])
print(f"n={G.number_of_nodes()}, m={G.number_of_edges()}, "
      f"directed={G.is_directed()}, density={nx.density(G):.4f}")
print(f"components: {nx.number_weakly_connected_components(G)}")
# largest weakly connected component
G_lwcc = G.subgraph(max(nx.weakly_connected_components(G), key=len)).copy()

# 2. Baseline structure
print(f"reciprocity: {nx.reciprocity(G):.3f}")
print(f"transitivity: {nx.transitivity(G):.3f}")
print(f"degree assortativity: {nx.degree_assortativity_coefficient(G):.3f}")

# 3. Centralities (on appropriate subgraph, with explicit handling)
deg = dict(G.degree())
btw = nx.betweenness_centrality(G_lwcc, normalized=True)  # restrict to LWCC
pr  = nx.pagerank(G, alpha=0.85)  # works on full G
```

Set a random seed before any stochastic algorithm (Louvain, SBM inference, ERGM MCMC, sampling). State the seed in output.

## When in doubt

If the user's request is ambiguous, ask *one* clarifying question — usually it's "what is the substantive question this network should answer?" Network analysis methods are interpretable only relative to a substantive question. Five different reasonable questions about the same network demand five different methods.

For deep dives on any specific area, read the corresponding reference file. The reference files contain formulas, library calls (Python and R), citations to canonical literature (Wasserman & Faust 1994; Snijders 2017; Newman 2018; Hunter et al. 2008; Holme & Saramäki 2012; Peixoto 2014/2017; Hamilton 2020), and worked examples. They are not light reading — they're designed to make Claude make decisions a domain expert would make. Read the relevant ones in full before recommending a method.
