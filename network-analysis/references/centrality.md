# Centrality

Centrality answers "who is important?" but importance is plural. This file is the menu of legitimate centrality measures, their assumptions, when each is appropriate, and the failure modes that produce wrong rankings.

## The fundamental classification (Borgatti 2005)

Borgatti's typology asks two questions about the implicit process the centrality measures:

1. **What flows on the network?** Discrete things (packages, parcels) or duplicated things (information, gossip, viruses)
2. **What paths does it use?** Geodesics (shortest), any path (random walks), or any trail (no repeat edges)

The centrality you should use is the one whose implicit flow matches the substantive process you care about. Asking "who is most influential in spreading rumors?" and then computing betweenness (which assumes flow over shortest paths) gives a wrong answer if rumors actually travel as random walks — PageRank or a random-walk betweenness would be correct.

| Centrality | Flow type | Path type | When to use |
|---|---|---|---|
| Degree | Anything | Direct only | Sheer activity; one-step influence |
| Closeness | Parcels | Geodesics | Speed of broadcast from this node |
| Betweenness | Parcels | Geodesics | Brokerage / control of flow |
| Eigenvector | Replication (gossip) | Walks | Status, prestige |
| Katz | Replication | Walks (with decay) | Eigenvector for non-strongly-connected graphs |
| PageRank | Random walker | Walks (with restart) | Steady-state importance |
| Bonacich β | Replication (signed) | Walks | Power in exchange networks (β can be negative) |
| Flow betweenness | Parcels | Max-flow | Brokerage with non-shortest options |
| Random-walk betweenness | Parcels | Random walks | Brokerage for stochastic flow |
| Percolation centrality | Damage | Geodesics | Vulnerability in infrastructure |

## Formal definitions

For a graph G = (V, E) with adjacency matrix A and n = |V|:

### Degree centrality

`C_D(i) = deg(i)`, normalized as `deg(i) / (n-1)` for a simple graph (this normalization assumes a complete graph denominator — be careful comparing across networks of different sizes; the "normalization" is comparison to the maximum possible, not to the actual maximum observed).

For directed graphs, distinguish **in-degree** (popularity, prestige) from **out-degree** (gregariousness, activity). For weighted graphs, the analog is **strength** = sum of incident edge weights.

### Closeness centrality

`C_C(i) = (n-1) / Σ_j d(i,j)` where d(i,j) is the geodesic distance.

**Critical failure**: if any j is unreachable from i, d(i,j) = ∞ and closeness is 0 or undefined. Workarounds:
- **Restrict to the largest connected component** (and report which component each node belongs to)
- **Harmonic centrality** (`C_H(i) = Σ_{j≠i} 1/d(i,j)`) handles infinity gracefully (1/∞ = 0). This is what most modern references recommend.

### Betweenness centrality

`C_B(i) = Σ_{s≠i≠t} σ_st(i) / σ_st`

where σ_st is the number of shortest paths from s to t and σ_st(i) is the number passing through i. Brandes (2001) gives an O(nm) algorithm for unweighted and O(nm + n² log n) for weighted graphs (still expensive for large networks).

For large networks, use **approximate betweenness** (Brandes & Pich 2007; Riondato & Kornaropoulos 2014) which samples source-target pairs and gives ε-additive approximation with high probability. NetworKit and graph-tool implement these.

**Edge betweenness** is the analogous measure on edges; it is the basis of the Girvan-Newman community detection algorithm.

### Eigenvector centrality

`x_i = (1/λ) Σ_j A_ij x_j`, i.e., x is the eigenvector corresponding to the leading eigenvalue λ of A.

By Perron-Frobenius, for a connected undirected graph the leading eigenvector exists and has all positive entries. On a directed graph with no strong components or on a graph with isolated components, eigenvector centrality **fails** — pages with no in-edges get score 0 and don't pass score to others (the "dangling node" problem).

### Katz centrality

`x = α A^T x + β · 1`, solvable as `x = β (I - α A^T)^(-1) 1`

The damping α must be less than 1/λ_max(A) for convergence. Katz fixes eigenvector's directional-graph problem by adding a base score β to everyone.

### PageRank

`x_i = (1-d)/n + d Σ_j A_ji x_j / k_j^out`

where d is the damping factor (typically 0.85) and k_j^out is j's out-degree (with a "teleport" handling for dangling nodes). PageRank is Katz with a probabilistic interpretation: it's the stationary distribution of a random walk that with probability d follows an edge and with probability 1-d teleports uniformly.

### Bonacich power centrality

`c(α, β) = α (I - β A)^(-1) A · 1`

For β > 0, this is Katz-like (well-connected neighbors help). For β < 0, **being connected to well-connected neighbors hurts you** — this is the centrality for **negative exchange networks** like bargaining: if your trading partners have many other options, you're in a weaker position. Use this whenever the substantive process is competitive/exchange-based, not informational.

|β| should be less than 1/λ_max(A). β = 0 reduces to degree.

### HITS (Hubs and Authorities, Kleinberg 1999)

For directed graphs (especially the web). Each node gets two scores:
- **Authority** = sum of hub scores of nodes pointing to it
- **Hub** = sum of authority scores of nodes it points to

`a = A^T h`, `h = A a` → a is leading eigenvector of A^T A, h of A A^T. Use when the graph has a clear bipartite-like structure of producers and pointers (web, citations, recommender systems).

## Group, bridge, and structural-hole centralities

### Group centrality (Everett & Borgatti 1999)

Centrality of a *set* of nodes, not extensible from individual scores. Group betweenness is the fraction of shortest paths passing through *any* member of the group; useful when asking "which 3 people should I monitor to maximize information capture?" This is generally NP-hard but greedy submodular optimization gives a (1-1/e) approximation.

### Burt's constraint and effective size (structural holes)

Burt (1992, 2004) — for studying brokerage and information advantage:

- **Effective size** = n_i − Σ redundancy(i,j) ≈ "non-redundant contacts"
- **Constraint** C_ij = (p_ij + Σ_q p_iq p_qj)² measures how much j constrains i; total constraint is Σ_j C_ij
- Low constraint = many structural holes = brokerage opportunity

NetworkX: `nx.structuralholes.constraint(G)`, `nx.structuralholes.effective_size(G)`. These are widely used in organizational network analysis (intra-firm advice networks) and have very different theoretical commitments than betweenness — Burt's argument is that brokerage advantage comes from *non-redundant* contacts, not from being on many paths.

### Bridge betweenness, k-bridge

A node is a **k-bridge** if its removal disconnects k component-pairs. Bridge measures complement standard centrality: a node with low betweenness can be a critical bridge.

## Temporal centrality

When edges have timestamps, classical centrality computed on the time-aggregated network is misleading because it ignores **time-respecting paths** (Holme & Saramäki 2012). For temporal data:

- **Temporal betweenness**: number of shortest *time-respecting paths* passing through i during a time window
- **Temporal closeness**: based on time-respecting reachability
- **Temporal degree / coreness**: aggregated over time windows; watch for window-size sensitivity

Libraries: `pathpy` (Scholtes), `teneto` (Thompson), `Raphtory`. Buß et al. (2020) give algorithms for temporal betweenness; distinguish *strict* (ascending times) from *non-strict* (non-descending) path definitions — they give different rankings.

## Centrality on bipartite networks

Special handling needed. Borgatti & Everett (1997) define normalized versions:
- **Bipartite degree** is the count of opposite-mode neighbors; for two-mode datasets, use the dual-projection or bipartite-specific functions in `networkx.algorithms.bipartite`.
- **Eigenvector centrality** on a bipartite graph: the leading eigenvalue's eigenvector has positive and negative entries alternating by mode (this is the singular vector). Use the SVD of the incidence matrix B; the leading left singular vector gives the "row centrality" and the right gives "column centrality". This is precisely correspondence analysis.
- **Betweenness** is computed normally but the values for nodes in different modes aren't directly comparable.

## Centrality on weighted networks

Most centralities have weighted analogs but the weight semantics matter:

- **Weights as strength** (higher = stronger): for shortest-path measures (closeness, betweenness), invert (1/w) so high strength = short distance.
- **Weights as distance/cost** (higher = farther): use directly in shortest-path; for eigenvector-style, may need conversion.

**Always state explicitly** which interpretation you're using. A common error: applying Dijkstra to a network where weights are similarity scores gives the *least similar* path, not the most similar.

Opsahl, Agneessens, Skvoretz (2010) propose a tunable weighted centrality `C^wα = k^(1-α) · s^α` where k is degree and s is strength; α=0 recovers degree, α=1 recovers strength, α between trades them off. Useful when the substantive question doesn't dictate one over the other.

## Centralization (network-level)

Freeman's centralization measures *how unequally* centrality is distributed:

`C_X = Σ_i (C_X(v*) - C_X(i)) / max possible value`

where v* is the most central node and the max is taken over all graphs of size n. Interpretable as "how star-like is this network?" — 1 for a perfect star, 0 for a network where centrality is uniform.

This is what's reported in "the network is highly centralized" claims; without it, claims about centralization are vague.

## Sensitivity and robustness

Centrality is sensitive to:

- **Measurement error in edges**: Wang, Shi, McFarland, Leskovec (2012) and Borgatti, Carley, Krackhardt (2006) showed that even 10% edge perturbation can substantially reorder centrality rankings. Run a bootstrap (add/remove edges with probability ε, recompute centrality, measure rank correlation across replications).
- **Boundary specification**: an actor's centrality in a partial network is not their centrality in the full network. State the boundary.
- **Sampling**: in snowball samples, peripheral nodes are systematically underweighted; centrality of seed nodes is overestimated.

When reporting centrality, give the top-k list *with the bootstrap confidence interval on rank*, not just the ranking. "Node 17 is ranked between 2 and 5 across resamples" is honest; "node 17 is the second most central" is overclaim.

## Default choices for common substantive questions

| Substantive question | Default centrality | Why not the alternative |
|---|---|---|
| "Who influences opinions in this online community?" | PageRank (directed follower graph) | Eigenvector fails on dangling/new accounts |
| "Who would I remove to fragment a terror cell?" | Betweenness (or articulation point detection) | Degree finds visible leaders, not brokers |
| "Whose social standing is highest?" | Eigenvector / Bonacich β>0 | Degree counts low-status ties equally |
| "Who has the best negotiation position?" | Bonacich β<0 | Standard centralities all reward dense neighborhoods |
| "Whose departure would disrupt operations?" | Betweenness + Burt's constraint | Degree misses irreplaceable brokers |
| "Where should I place sensors to detect contagion?" | Acquaintance immunization (degree of friends) or random-walk centrality | Degree alone misses periphery exposure |
| "Who is best positioned to learn new things?" | Burt's effective size, low constraint | Betweenness measures control, not absorption |

## Canonical references

- Freeman, L. C. (1979). "Centrality in social networks: Conceptual clarification." *Social Networks* 1: 215–239.
- Bonacich, P. (1987). "Power and centrality: A family of measures." *American Journal of Sociology* 92(5): 1170–1182.
- Borgatti, S. P. (2005). "Centrality and network flow." *Social Networks* 27: 55–71.
- Brandes, U. (2001). "A faster algorithm for betweenness centrality." *Journal of Mathematical Sociology* 25: 163–177.
- Burt, R. S. (2004). "Structural holes and good ideas." *American Journal of Sociology* 110(2): 349–399.
- Newman, M. E. J. (2018). *Networks*. 2nd ed. Oxford. Ch. 7.
- Opsahl, T., Agneessens, F., & Skvoretz, J. (2010). "Node centrality in weighted networks." *Social Networks* 32: 245–251.
