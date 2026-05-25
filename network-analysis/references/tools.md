# Tools and Libraries

This file is the field guide to network analysis software. Choosing the right tool for the network size and task is a productivity multiplier; running NetworkX on a million-node graph is not "slow Python" — it's a wrong-tool choice that will take days to terminate.

## Python

### NetworkX

The default for prototyping and learning. Pure Python; readable; well-tested.

- **Strengths**: huge API, easy installation, integrates with everything, excellent documentation
- **Weaknesses**: slow for >50k nodes; memory-hungry; no parallelism
- **Use when**: graph is small-to-medium, you're prototyping, you need a specific algorithm that other libraries don't have, you want maximum reproducibility

```python
import networkx as nx
G = nx.karate_club_graph()
nx.pagerank(G), nx.betweenness_centrality(G), nx.diameter(G)
```

### python-igraph

C-backed library with Python bindings. Same API as igraph in R.

- **Strengths**: 10–100× faster than NetworkX for most algorithms; consistent across languages
- **Weaknesses**: less Pythonic API than NetworkX (uses integer vertex IDs by default; named vertices via `g.vs["name"]`); fewer recent algorithms
- **Use when**: graphs in the 10k–1M range; you need speed; you want consistency with R workflows

```python
import igraph as ig
g = ig.Graph.Erdos_Renyi(n=10000, p=0.001)
g.pagerank()
g.community_leiden(objective_function="modularity")  # Leiden!
```

### graph-tool

C++ template library with Python bindings; the choice for large graphs and advanced statistical models.

- **Strengths**: fastest of the three (often 10× igraph); best Stochastic Block Model implementation in any language (Peixoto, the author); great drawing
- **Weaknesses**: hard install (heavy C++ template compilation; consider conda's `gt` channel or Docker); steeper API
- **Use when**: graphs >1M nodes; you need SBMs (especially nested / hierarchical); you need publication-quality visualization

```python
import graph_tool.all as gt
g = gt.collection.data["football"]
state = gt.minimize_nested_blockmodel_dl(g)  # hierarchical SBM
state.draw()
```

### NetworKit

C++/Python library focused on **parallel** algorithms.

- **Strengths**: multicore by default; centralities and community detection at billion-edge scale
- **Weaknesses**: smaller API than NetworkX; less common in tutorials
- **Use when**: very large graphs (10M+ edges) on multicore hardware

### cuGraph (RAPIDS)

NVIDIA's GPU-accelerated graph library.

- **Strengths**: 100–1000× speedup on GPU for centrality, PageRank, community detection
- **Weaknesses**: requires NVIDIA GPU; algorithms not as complete as CPU libraries
- **Use when**: you have a GPU and you're running standard algorithms (PageRank, Louvain, BFS) on huge graphs

### Specialized libraries

| Library | Purpose |
|---|---|
| `pyG` (torch_geometric) | Graph neural networks (PyTorch) |
| `DGL` (Deep Graph Library) | GNNs, alternative to PyG |
| `node2vec`, `gensim` | Random-walk embeddings |
| `pathpy` (Scholtes) | Higher-order temporal networks, time-respecting paths |
| `teneto` (Thompson) | Temporal network metrics |
| `Raphtory` | Streaming/large-scale temporal |
| `infomap` | Infomap community detection (best implementation) |
| `leidenalg` | Leiden algorithm (Traag, the author) |
| `cdlib` | Community detection algorithm collection |
| `EoN` (Miller) | Epidemics on networks (SIR, SIS, SEIR, custom) |
| `ndlib` | General dynamics simulation |
| `backbone` (R, has Py port) | Backbone extraction (disparity, SDSM, FDSM) |
| `pymnet` (Kivelä) | Multilayer networks |
| `Snap.py` | Stanford library; large-scale; less actively maintained |
| `python-louvain` | Louvain (deprecated in favor of leidenalg) |
| `karateclub` | Embedding methods, community detection |

## R

### igraph (R version)

Same C library, R bindings. Sturdy default.

```r
library(igraph)
g <- erdos.renyi.game(n=1000, p=0.01)
pr <- page_rank(g)$vector
cl <- cluster_leiden(g, resolution_parameter=1.0)
```

### statnet ecosystem

The standard for inferential SNA in R.

- **`network`**: data structure
- **`sna`**: classical SNA functions (centralities, blockmodeling)
- **`ergm`**: exponential random graph models — the canonical implementation
- **`ergm.count`**: ERGMs for valued (count-weighted) networks
- **`ergm.ego`**: ERGMs from egocentric samples
- **`tergm`**: temporal/separable ERGMs (STERGM)
- **`Bergm`**: Bayesian ERGM with different MCMC strategies
- **`latentnet`**: latent space models for ties

### RSiena

The canonical SAOM implementation. Stand-alone or via R package `RSiena`. Documentation is comprehensive at https://www.stats.ox.ac.uk/~snijders/siena/.

### Other R packages

| Package | Purpose |
|---|---|
| `intergraph` | Convert between `network`, `igraph`, `tidygraph` objects |
| `tidygraph`, `ggraph` | Tidy/ggplot workflow for graphs |
| `qgraph` | Psychometric networks, correlation networks |
| `bootnet` | Bootstrap for psychological network estimation |
| `backbone` (Neal) | Backbone extraction; best in any language |
| `MPNet` (cross-platform GUI) | Multilevel ERGMs |
| `goldfish` (Stadtfeld) | DyNAM models for event-based dynamics |
| `relevent` (Butts) | Relational event models |
| `igraphdata` | Standard datasets |

## Other languages / platforms

### Standalone tools

- **Gephi**: GUI-based, interactive exploration; excellent for visualization and quick metrics; weak for inferential models
- **Pajek**: classic SNA software (Batagelj & Mrvar); pre-dates open-source era; still used in some communities
- **Cytoscape**: biology-focused, large plugin ecosystem
- **VOSviewer**: bibliometrics-focused
- **UCINET**: commercial SNA toolkit; long history in management/sociology
- **NodeXL**: Excel-based, accessible for non-programmers

### Database / streaming

- **Neo4j** (Cypher query language): graph database; good for transactional / OLTP graph workloads; supports GDS (Graph Data Science) library with PageRank, Louvain, etc.
- **TigerGraph**: similar
- **JanusGraph, ArangoDB**: alternatives
- **Apache Flink Gelly, Spark GraphX/GraphFrames**: distributed graph processing

For network *analysis* (as opposed to *storage and query*), the Python/R libraries are typically faster and more flexible than database-native processing — unless your graph genuinely doesn't fit in memory.

## Decision matrix

| Network size | Best Python | Best R | Notes |
|---|---|---|---|
| < 1k nodes | NetworkX | igraph | Pick whichever you know |
| 1k–50k nodes | python-igraph or NetworkX | igraph | NetworkX OK if you're patient |
| 50k–500k | python-igraph | igraph | NetworkX too slow |
| 500k–10M | graph-tool, NetworKit | igraph (if it fits) | Watch memory; sparse representation matters |
| > 10M nodes | graph-tool, NetworKit, cuGraph | distributed required | Consider Spark GraphFrames if it doesn't fit in memory |

| Task | Best tool |
|---|---|
| Centralities, components, paths | igraph (any language) |
| Community: Leiden | `leidenalg` (Py), `igraph::cluster_leiden` (R) |
| Community: Infomap | `infomap` Python package |
| Community: SBM, nested SBM | graph-tool |
| ERGM | R `ergm` |
| SAOM / RSiena | R `RSiena` |
| STERGM | R `tergm` |
| ALAAM | R `RSiena` or MPNet |
| Multilevel ERGM | MPNet |
| Multilayer general | `pymnet` (Py), `multinet` (R) |
| GNNs | PyTorch Geometric |
| Embeddings | `node2vec` (Py), `karateclub` (Py) |
| Temporal / time-respecting | `pathpy` (Py), `teneto` (Py) |
| Relational events | R `goldfish` or `relevent` |
| Backbone extraction | R `backbone` |
| Bipartite analysis | `igraph::bipartite_*` (R), `nx.bipartite` (Py) |
| Spreading simulation | `EoN`, `ndlib` (Py) |
| Visualization, large | Gephi, graph-tool |
| Visualization, programmatic | `ggraph` (R), `graph-tool` (Py) |
| Network database | Neo4j, TigerGraph |

## File formats

| Format | Tools | Notes |
|---|---|---|
| **edgelist** (`.edges`, `.csv`) | All | Simplest; just (source, target [, weight]); ad-hoc but universal |
| **GraphML** (`.graphml`) | igraph, NetworkX, graph-tool, Gephi | XML; supports node/edge attributes; portable |
| **GEXF** (`.gexf`) | Gephi, NetworkX, igraph | Gephi-native; supports dynamics |
| **Pajek** (`.net`, `.paj`) | Pajek, NetworkX, igraph | Classic SNA; widely supported |
| **GML** (`.gml`) | igraph, NetworkX | Older but supported |
| **DOT** (`.dot`, `.gv`) | Graphviz | For visualization-focused workflows |
| **DGS** | DGS for dynamic graphs | Less common |
| **JSON** | Custom / D3.js | For web viz |

For interchange across tools, **GraphML** is the safest format: XML, supports attributes (typed), widely implemented, no parser-specific quirks.

## Performance tips

- **Use sparse representations**: NetworkX uses dict-of-dict (memory-heavy); igraph uses CSR (sparse); graph-tool uses optimized vectors. For large graphs, the difference matters.
- **Avoid copying graphs unnecessarily**: `G.subgraph(...)` in NetworkX creates a view by default; `.copy()` materializes
- **Profile before optimizing**: many bottlenecks are in I/O or data preparation, not in the graph algorithm
- **For centralities on large graphs, use approximations**: Brandes-Pich for betweenness; eigenvalue approximations for eigenvector
- **Parallelize**: NetworKit and cuGraph use parallelism; with NetworkX, use `joblib` or `dask` for embarrassingly parallel tasks (per-component, per-window)

## Common tool mistakes

- **Using NetworkX for a million-node graph and concluding "this is too slow for our problem"**: it's not the problem, it's the tool. Switch.
- **Installing graph-tool from PyPI**: it's compiled, won't work; use conda's `gt` channel.
- **Conflating Louvain and Leiden**: `python-louvain` is the *old* Louvain implementation; for Leiden, use `leidenalg`.
- **Using `networkx.algorithms.community.modularity_max.greedy_modularity_communities` and assuming it's Louvain**: it's a different algorithm (Clauset-Newman-Moore).
- **Mixing igraph indices with NetworkX node labels** when converting between libraries: indices change; use `intergraph` (R) or careful conversion (Py).
- **Reading edge lists with header rows treated as data**: silently produces a node called "source" and one called "target".

## Canonical citations for tools (cite these in any paper that uses them)

- Hagberg, A., Schult, D., & Swart, P. (2008). "Exploring network structure, dynamics, and function using NetworkX." *Proceedings of SciPy 2008*: 11–15.
- Csardi, G. & Nepusz, T. (2006). "The igraph software package for complex network research." *InterJournal Complex Systems* 1695.
- Peixoto, T. P. (2014). "The graph-tool python library." `figshare`.
- Staudt, C. L., Sazonovs, A., & Meyerhenke, H. (2016). "NetworKit: A tool suite for large-scale complex network analysis." *Network Science* 4: 508–530.
- Handcock, M. S., Hunter, D. R., Butts, C. T., Goodreau, S. M., & Morris, M. (2008). "statnet: Software tools for the representation, visualization, analysis and simulation of network data." *Journal of Statistical Software* 24(1).
- Ripley, R. M., Snijders, T. A. B., Boda, Z., Vörös, A., & Preciado, P. (2024). "Manual for RSiena." University of Oxford.
- Fey, M. & Lenssen, J. E. (2019). "Fast graph representation learning with PyTorch Geometric." *ICLR Workshop on Representation Learning on Graphs and Manifolds*.
