# Multilayer and Multiplex Networks

When you have multiple relations among the same actors (advice + friendship + dislike), or the same nodes participating across multiple contexts (people across platforms), or interactions across multiple levels (people within teams within organizations), aggregating to a single graph throws away the structure that matters. Multilayer networks are the right formalism.

## Terminology (Kivelä et al. 2014 is the canonical taxonomy)

The literature is a mess of overlapping terms. Use these precisely:

- **Multilayer network**: the general framework. A set of layers, each with a node set and edges; plus inter-layer edges.
- **Multiplex network**: a special case where the same node set appears in every layer, and inter-layer edges only connect node-replicas to themselves (e.g., same person across "advice" and "friendship" layers).
- **Multi-relational network**: multiplex with categorical relation types
- **Interconnected network / Network of networks**: layers have disjoint node sets but are connected across layers (e.g., power grid + communication network)
- **Temporal network as multilayer**: each layer is a time snapshot, inter-layer edges connect a node to itself across consecutive layers
- **Multilevel network**: a system with both within-level ties (people-people, organization-organization) and between-level ties (people-organization, the affiliation relation). Distinguishes "level" semantically.

Kivelä et al. give a unified formalism using **adjacency tensors** of arbitrary rank.

## Representations

### Adjacency tensor (general multilayer)

For a multilayer network with N nodes and L layers, the adjacency tensor A has rank 4: A[i, j, α, β] = 1 if there's an edge from node i in layer α to node j in layer β.

In Python:
```python
import numpy as np
A = np.zeros((N, N, L, L))  # full multilayer
# A[i, j, alpha, alpha] = intra-layer edges in layer alpha
# A[i, i, alpha, beta] = inter-layer self-couplings (multiplex)
```

### Supra-adjacency matrix

Flatten the rank-4 tensor to a (NL × NL) matrix:
- Diagonal blocks (N × N each) = intra-layer adjacencies for each layer
- Off-diagonal blocks = inter-layer couplings

The supra-adjacency matrix is the adjacency matrix of the **supra-graph** (a single graph on NL "node-layer" pairs). All standard graph algorithms work on it. But: results need careful interpretation because "node 1 in layer 2" and "node 1 in layer 3" are different node-layers, not the same node.

```python
# multiplex with categorical coupling weight w
supra = np.zeros((N*L, N*L))
for alpha in range(L):
    supra[alpha*N:(alpha+1)*N, alpha*N:(alpha+1)*N] = A_layers[alpha]
for alpha in range(L):
    for beta in range(L):
        if alpha != beta:
            for i in range(N):
                supra[alpha*N + i, beta*N + i] = w  # self-coupling
```

The choice of inter-layer coupling weight w matters: too low → layers are effectively independent; too high → all of node i's appearances behave as a single super-node. Range over w and check sensitivity.

### Edge list with layer column

For practical analysis, a tidy edge list with columns (source, target, source_layer, target_layer, weight) is easier than the tensor. Libraries handle conversion.

## Why aggregation fails

The temptation is to aggregate all layers into a single weighted graph (sum edge weights, or take the max, or count layers). This is wrong in known ways:

- **Centrality changes qualitatively**, not just quantitatively. De Domenico et al. (2013, 2015) showed that a node can be highly central in the multiplex aggregate but irrelevant when each layer is considered properly, and vice versa.
- **Community structure is layer-specific**: nodes in the same community in one layer may be in different communities in another. Multilayer community detection (Mucha et al. 2010) reveals this.
- **Diffusion processes** have qualitatively different behavior on multiplex networks than on aggregated graphs: spread can be slower OR faster depending on layer coupling (Gomez et al. 2013).
- **Layer-specific roles are lost**: a person can be a hub in advice and a periphery in friendship; aggregating averages this away.

## Multilayer centrality

Several principled extensions of centrality to multilayer:

### Eigenvector / PageRank on the supra-adjacency matrix

Gives a centrality score per node-layer. Aggregate per-node by summing or taking max across layers. **Versatility** (De Domenico et al. 2015) is one principled aggregation: a node is versatile if it's central in many layers.

### Layer-by-layer ranking

Compute centrality independently per layer; report each. Useful when layers have substantively different meanings and you don't want to collapse them.

### Multiplex PageRank (Halu et al. 2013)

Modify PageRank so that the random walker can switch layers with some probability r. The aggregate score is the steady-state distribution. The parameter r interpolates between layer-independent and fully coupled.

### Tensor-based centralities

De Domenico, Solé-Ribalta, Omodei, Gómez & Arenas (2015) define multilayer eigenvector, HITS, and Katz on the rank-4 adjacency tensor directly, without flattening. The advantage: layer-specific weights can be incorporated as eigenvector components.

## Multilayer community detection

The dominant approach is **multilayer modularity** (Mucha, Richardson, Macon, Porter & Onnela 2010):

`Q = (1/2μ) Σ_{ijαβ} [(A_{ijα} − γ_α k_{iα}k_{jα}/2m_α) δ_{αβ} + δ_{ij} ω_{αβ}] δ(g_iα, g_jβ)`

where γ_α is the resolution per layer and ω_{αβ} is the inter-layer coupling. The partition g assigns each node-layer pair to a community.

- **GenLouvain** (MATLAB) and `pymnet` (Python) and `MultilayerGM` implement this
- Tuning γ scans resolution within layers; tuning ω scans coupling between layers
- Multilayer SBM extensions (Peixoto 2015) provide the principled alternative

The output is a partition of node-layers, not nodes. A node can belong to different communities in different layers — this is informative, not noise.

## Multilevel ERGM

Wang, Robins, Pattison & Lazega (2013) defined ERGMs for multilevel networks: simultaneously model person-person, organization-organization, and person-organization ties. New statistics capture cross-level configurations like "person ties cluster within organizations" or "well-connected organizations have well-connected people".

R package: `MPNet` (PNet's multilevel cousin). Substantial estimation cost; subsample if large.

## Multiplex SAOM (RSiena)

Snijders, Lomi & Torló (2013) extended SAOM to **multiplex** networks: jointly model the dynamics of friendship, advice, dislike. Each layer has its own rate function and objective function; cross-layer effects (e.g., "advice ties follow friendship ties") are explicit parameters.

Multilevel SAOM (Koskinen & Snijders 2022): hierarchical SAOM across multiple comparable multiplex networks (e.g., advice + friendship in many classrooms).

## Practical workflow

1. **Decide the formalism**: multiplex (same nodes, different relations), interconnected (different nodes, coupling), multilevel (semantic levels), temporal (layers = time). The wrong formalism gives meaningless results.
2. **Specify inter-layer coupling**: weights, conditional independence assumptions, ranges to scan
3. **Inspect per layer**: density, degree distribution, components within each layer
4. **Compute aggregate baselines and per-layer baselines**: report both
5. **Choose multilayer methods explicitly**: multilayer modularity for communities, supra-PageRank or versatility for centrality, multiplex ERGM/SAOM for inference
6. **Visualize layers separately or with layer-aware layouts** (3D stacked layouts; multilayer-aware ForceAtlas)

## Libraries

| Library | Language | Strengths |
|---|---|---|
| `pymnet` (Kivelä) | Python | Full multilayer toolkit; matches the Kivelä taxonomy |
| `multinet` | R/Python | General multilayer (built on `manet`) |
| `muxViz` | R/Web | Visualization-first multilayer |
| `MultilayerGM` | Python | Stochastic block models for multilayer |
| `GenLouvain` | MATLAB | The original multilayer modularity reference impl. |
| `RSiena` | R | Multiplex SAOM |
| `MPNet` | Standalone | Multilevel ERGMs |
| `graph-tool` | Python | Multilayer SBMs via labeled blocks |

## Common multilayer mistakes

- **Treating multiplex as multi-relational without modeling**: if you have advice + friendship, "average" or "any" gives loss of information; model each layer explicitly.
- **Choosing inter-layer coupling weight arbitrarily**: scan a range; report sensitivity.
- **Reporting centrality / community on the aggregate without explanation**: tell the reader why you chose to aggregate, and what's lost.
- **Confusing **layer** with **time** in the multilayer formalism**: temporal networks fit multilayer formally but the inter-layer coupling has a specific interpretation (causal/temporal succession).
- **Using algorithms designed for single-layer on the supra-adjacency matrix without re-interpretation**: a high-centrality node-layer is not the same as a high-centrality node.
- **Multilevel ≠ multiplex**: people-orgs has a clear semantic distinction (people are at one level, orgs at another); friendship-advice doesn't have a level distinction. Use the right framework.

## Canonical references

- Kivelä, M., Arenas, A., Barthelemy, M., Gleeson, J. P., Moreno, Y., & Porter, M. A. (2014). "Multilayer networks." *Journal of Complex Networks* 2: 203–271.
- Boccaletti, S. et al. (2014). "The structure and dynamics of multilayer networks." *Physics Reports* 544: 1–122.
- De Domenico, M., Solé-Ribalta, A., Cozzo, E., Kivelä, M., Moreno, Y., Porter, M. A., Gómez, S., & Arenas, A. (2013). "Mathematical formulation of multilayer networks." *Physical Review X* 3: 041022.
- Mucha, P. J., Richardson, T., Macon, K., Porter, M. A., & Onnela, J.-P. (2010). "Community structure in time-dependent, multiscale, and multiplex networks." *Science* 328: 876–878.
- Wang, P., Robins, G., Pattison, P., & Lazega, E. (2013). "Exponential random graph models for multilevel networks." *Social Networks* 35: 96–115.
- Snijders, T. A. B., Lomi, A., & Torló, V. J. (2013). "A model for the multiplex dynamics of two-mode and one-mode networks." *Social Networks* 35: 265–276.
- Peixoto, T. P. (2015). "Inferring the mesoscale structure of layered, edge-valued, and time-varying networks." *Physical Review E* 92: 042807.
