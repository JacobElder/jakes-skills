# Data Decisions: Mode, Boundary, Sampling, Projections

The decisions made before any analytic method runs determine whether the analysis is interpretable. Most published-but-wrong network analyses make their key error here, in the unglamorous step of structuring the data. This file covers the decisions that matter and the methods that follow from each branch.

## Mode: one-mode, two-mode/bipartite, multimode

### One-mode (unipartite)

A single node type with ties among them: friendship, citation, co-authorship after projection. Standard SNA methods apply.

### Two-mode (bipartite, affiliation)

Two distinct node types with ties only between them: people-events, authors-papers, customers-products, words-documents. Represented by an N × M **incidence matrix** B.

**The bipartite trap**: most SNA tools assume one-mode. Common workaround is to **project** to one-mode (P = B B^T gives a people-people matrix where weights count shared events). This projection has known pathologies that almost all analyses ignore:

- **Each event/affiliation of size d creates d(d−1)/2 edges in the projection** — a clique. Two events with 100 attendees each create 9900 projected edges. A high-degree affiliation node dominates the projection.
- **Clustering coefficient is artificially inflated** by these induced cliques. Reporting "this network has high clustering" on a projection is meaningless without comparison to the bipartite null.
- **Community detection on projections** finds the affiliations as communities (which you already knew). Specialized bipartite community methods (next section) avoid this.
- **Centrality on projections** is distorted: nodes who attend large events have artificially high degree.

### The fix: backbone extraction

Before any analysis on a bipartite projection, extract a **statistically significant backbone** — the edges that are stronger than expected under a null model that preserves the bipartite structure.

**Methods (in order of strength for projections)**:

1. **Stochastic Degree Sequence Model (SDSM)** (Neal 2014): null preserves expected row and column sums. Each projection edge has its own p-value under the null; keep edges with p < α.
2. **Fixed Degree Sequence Model (FDSM)**: null preserves exact row and column sums. Stronger but slower; uses the fastball algorithm (Godard & Neal 2022) for sampling.
3. **Hypergeometric-based backbones**: tests edge weight against the hypergeometric distribution under random co-attendance.
4. **Disparity filter** (Serrano, Boguñá & Vespignani 2009): the "default" weighted-network backbone; works on the projection's edge weights but **does not use the bipartite structure**, so it misses information. SDSM/FDSM dominate disparity for bipartite projections.

R: `backbone` package (Neal). Python: similar functionality through `cdlib` or custom implementations.

```r
library(backbone)
P <- bipartite_to_unipartite(B)  # weighted projection
bb <- sdsm(P, alpha = 0.05, class = "igraph")  # backbone
# Now analyze bb, not P
```

**Always** report whether you backbone-extracted, the alpha level, and the fraction of edges retained. A backbone retaining 5% of edges has a fundamentally different topology than the original projection.

### Better than projection: analyze the bipartite network directly

- **Bipartite centrality**: `nx.algorithms.bipartite.centrality` has `degree_centrality`, `betweenness_centrality`, `closeness_centrality` properly normalized for bipartite
- **Bipartite community detection**: bipartite modularity (Barber 2007), bipartite SBM (graph-tool)
- **Bipartite ERGM**: ergm.bipartite in statnet
- **Latent Block Models (LBM)**: principled co-clustering; R `blockmodels`

If the substantive question concerns both types of nodes, do not project.

### Multimode / multilevel

More than two node types (people-organizations-events). Use multilevel ERGM (`MPNet`), multilevel SAOM, or treat as multilayer (see `references/multilayer.md`).

## Directionality

### Directed and reported directed

If your data records who-did-X-to-whom, it's directed: cite, follow, advise, email-to. Treat as directed.

### Undirected by construction

Co-authorship, co-attendance, friendship reported by both, simultaneous action: undirected.

### Apparent directionality without measurement

A common mistake: data show "A reports being friends with B but B doesn't report A" and analysts treat this as directed friendship. Often this reflects measurement asymmetry (only some respondents were surveyed; or B forgot to list A), not asymmetric friendship. **Decide between**:
- Treat as directed (interpret as "claims to be friends with")
- Symmetrize as union (i↔j if either reports it) — more inclusive, conservative for some questions
- Symmetrize as intersection (i↔j only if both report) — more strict; what Wasserman & Faust suggest as "confirmed friendship"

State which choice you made and why.

### Directional analyses require directional algorithms

- Eigenvector centrality fails on directed networks without strong components → use Katz or PageRank
- Modularity for directed networks has several variants (Leicht-Newman, Arenas et al.) — they're not equivalent
- Community algorithms designed for undirected graphs (most modularity-based) ignore direction unless you use a directed variant
- Reciprocity is meaningful only for directed networks (`nx.reciprocity`)

## Weights

### What does the weight mean?

This determines what analyses are appropriate:

| Weight semantic | Examples | Appropriate methods |
|---|---|---|
| Frequency / count | Number of emails | Standard weighted SNA |
| Intensity / strength | Reported closeness | Standard weighted SNA |
| Distance / cost | Travel time, dissimilarity | Shortest paths use weights directly |
| Similarity | Correlation, cosine | INVERT to use as distance (1−sim, 1/sim, or -log) |
| Capacity | Bandwidth | Max-flow methods, not shortest path |
| Probability | Tie probability | Aggregate as expected count or model directly |

**A common error**: using cosine similarity as edge weight in a shortest-path computation gives "the path of least similarity", which is nonsense if the goal is "the most similar route".

### Backbone extraction for unipartite weighted networks

**Disparity filter** (Serrano, Boguñá & Vespignani 2009) is the standard:

For each node i and each edge (i,j), the null hypothesis is that i's strength s_i is uniformly distributed among its k_i edges. The disparity filter tests whether edge weight w_ij/s_i is significantly larger than expected. P-value:

`p_ij = (1 − w_ij/s_i)^(k_i − 1)`

Keep edges with p < α from either endpoint's perspective. Implementation: `backbone::disparity` in R, easy to roll in Python.

Other backbone methods for unipartite weighted: Pólya urn filter (Marcaccioli & Livan 2019), GloSS, LANS, noise-corrected (Coscia & Neffke 2017). Each has different null assumptions; the comparative study by Yassin et al. (2024) found disparity is a strong default for general structure but other filters preserve different features.

## Sampling: what data do you have, really?

The biggest determinant of what you can claim is what you actually observed.

### Complete network

A defined boundary (e.g., "all employees of company X as of date Y") and all ties within that boundary are observed. Most ERGM theory assumes this.

### Egocentric sample

Each respondent reports their own local network: their alters and possibly alter-alter ties. The "name generator" methodology (Burt 1984; McCallister & Fischer 1978):

1. Generate egos by sampling (often random sample of a population)
2. For each ego, generate up to k alters via a name-generator question
3. Optionally, ask about alter attributes and alter-alter ties

Egocentric data **cannot** answer questions about global structure (modularity, components, true degree distribution). It **can** answer questions about local structure (ego network composition, density, constraint).

ERGMs for egocentric data exist (Krivitsky & Morris 2017, `ergm.ego` package): they fit population-level ERGMs to local samples by assuming a known ego-sampling design.

### Snowball sample

Start with a seed set; each respondent names alters; alters are recruited as new respondents in subsequent waves. Network grows by recruitment chains.

**Snowball samples are biased in known ways**:
- **Over-samples high-degree nodes** (more likely to be named by someone)
- **Visibility bias** (more visible / connected respondents are recruited first)
- **Cluster-bound** (chains stay within communities; isolated regions of the network are never reached)

Conclusions about degree distribution, density, centrality are systematically wrong on snowball samples without correction.

### Respondent-Driven Sampling (RDS) (Heckathorn 1997)

Snowball with a payment structure and weighting: each respondent is paid for recruiting (typically 3) others and for participating. Weighting by personal network size (asked in survey) compensates for the degree-bias of snowball.

RDS gives **statistically defensible population estimates** under conditions: (1) the network is connected, (2) recruitment is random within an individual's network, (3) personal network size is reported accurately. **Salganik & Heckathorn (2004)** and later refinements (Volz & Heckathorn 2008; Gile 2011) developed RDS estimators.

Even with RDS, **structure-level inferences (community structure, centrality) remain biased**. RDS is good for prevalence estimation, not for structural analysis. Rohe (2017) showed there's a critical threshold above which design effects become severe.

### Crawled / observational

API scrapes, log data. Often partial in unknown ways: rate limits, sampled streams (Twitter 1% sample), missing edges due to privacy / deletion. **Document what you have and what's missing.**

### Population size estimation from samples

If you want to estimate the size of a hidden population (sex workers, homeless, opioid users) from a network sample: Frank-Snijders (1994) for snowball; Crawford, Wu & Heimer (2018) for RDS-based network estimators.

## Boundary specification (Laumann, Marsden & Prensky 1989)

Who is "in" the network is a substantive decision, not a technical one. Three classic approaches:

- **Realist**: include nodes the actors themselves consider members
- **Nominalist**: include nodes defined by an external criterion (employees of firm X)
- **Reputational**: include nodes named by expert informants

The boundary choice changes centrality (a node may be central in the included subgraph but peripheral in the full system), community structure (boundaries may cut natural communities), and density (smaller boundaries give higher density automatically).

**Almost all "complete network" analyses are actually bounded subgraph analyses.** Be explicit about the boundary and how it might affect conclusions.

## Missing data

Network data are almost always missing in non-trivial ways: non-responding actors, item non-response on specific ties, censoring. Default treatment (listwise deletion) is often wrong: removing a non-responding actor also removes all observed ties to that actor.

**Imputation for networks** is an active area (Krause, Huisman, Steglich & Snijders 2020 survey). Some options:

- **MICE-style multiple imputation** treating ties as variables
- **Latent space imputation** (fit a latent space model, impute from it)
- **SBM-based imputation** (fit SBM, impute from block probabilities)
- **For ERGM**: Bayesian data augmentation handling missing dyads

For SAOM, RSiena handles missing data natively by treating missing as a separate state. For ERGMs, the `ergm` package has options for handling missing dyads.

## Common data-decision mistakes

- Projecting a bipartite network and computing standard SNA on the projection without backbone extraction
- Treating asymmetric reporting as actual directionality
- Reporting centralities computed on snowball samples as if from a complete network
- Inverting similarity weights inconsistently across analyses
- Reporting "the network has [X] property" when X is sensitive to the chosen boundary
- Listwise deletion of non-responding actors in survey-based networks
- Using a single name-generator and assuming it captures all relevant relations (different generators elicit different networks; Bailey & Marsden 1999)

## Canonical references

- Wasserman, S. & Faust, K. (1994). *Social Network Analysis: Methods and Applications*. Cambridge. (Chapters 2, 3 on data collection and boundary)
- Laumann, E. O., Marsden, P. V., & Prensky, D. (1989). "The boundary specification problem in network analysis." In *Research Methods in Social Network Analysis*.
- Marsden, P. V. (1990). "Network data and measurement." *Annual Review of Sociology* 16: 435–463.
- Heckathorn, D. D. (1997). "Respondent-driven sampling: A new approach to the study of hidden populations." *Social Problems* 44: 174–199.
- Kolaczyk, E. D. (2009). *Statistical Analysis of Network Data*. Springer. (Chapter 5 on sampling)
- Neal, Z. P. (2022). "backbone: An R package to extract network backbones." *PLOS ONE* 17: e0269137.
- Serrano, M. Á., Boguñá, M., & Vespignani, A. (2009). "Extracting the multiscale backbone of complex weighted networks." *PNAS* 106: 6483–6488.
- Krause, R. W., Huisman, M., Steglich, C., & Snijders, T. (2020). "Missing data in cross-sectional networks – An extensive comparison of missing data treatment methods." *Social Networks* 62: 99–112.
