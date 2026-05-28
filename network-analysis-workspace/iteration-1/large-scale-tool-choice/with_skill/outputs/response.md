# Tool Choice for Large-Scale User-Item Recommendation Graph

## Short answer: No, NetworkX will not work at this scale.

Your graph has **5 million users + 2 million items = ~7 million nodes** and **800 million interactions (edges)**. NetworkX is pure Python with a dict-of-dict memory layout. At this scale it is not "slow" — it is the wrong tool entirely. Loading the edge list alone would exhaust most machines' RAM before a single algorithm runs, and betweenness centrality on the full graph would not terminate in any practical time.

Here is what you should use instead, task by task.

---

## Network classification first

Before picking tools, let's classify what you actually have:

- **Mode**: Two-mode / bipartite (users and items are different node types)
- **Directionality**: Likely directed (user → item interaction), possibly treatable as undirected for some analyses
- **Weight**: Almost certainly weighted (interaction counts, ratings, timestamps)
- **Scale**: Massive (>10⁶ nodes, nearly 10⁹ edges)

This bipartite structure matters critically for both tasks you named, and is addressed below.

---

## Betweenness Centrality at this scale

### The algorithm complexity problem

Exact betweenness centrality (Brandes algorithm) runs in **O(nm)** time for unweighted graphs — that is O(nodes × edges). For your graph: 7 × 10⁶ × 8 × 10⁸ ≈ 5.6 × 10¹⁵ operations. This is computationally infeasible regardless of tool.

**Exact betweenness on 800 million edges is not a tractable computation.**

### What to do instead

**Option 1 — Approximated betweenness (recommended for most use cases)**

Use a random-sample approximation (Brandes-Pich): sample k pivot nodes, run BFS/SSSP from each, and extrapolate. This gives a good approximation of the top-ranked nodes with far less computation.

- **NetworKit** has `nk.centrality.ApproxBetweenness` with controllable error bounds. It parallelizes across all cores and is the right tool here.
- **cuGraph** has `cugraph.betweenness_centrality(G, k=k)` with GPU acceleration — if you have an NVIDIA GPU, this is the fastest option by a large margin.

```python
import networkit as nk

# Load from edge list
reader = nk.graphio.EdgeListReader(' ', 0)
g = reader.read("interactions.edgelist")

# Approximated betweenness (epsilon=0.1 means ~10% relative error on top nodes)
ab = nk.centrality.ApproxBetweenness(g, epsilon=0.1, delta=0.1)
ab.run()
top_nodes = ab.ranking()[:100]
```

**Option 2 — Reconsider whether betweenness is the right metric**

For a recommendation graph, betweenness centrality answers "which node lies on the most shortest paths between other nodes." In a user-item bipartite graph, this has an ambiguous interpretation — it mixes paths that go user→item→user and item→user→item. Ask: what does "important" mean here?

- If you want items that bridge different user communities → betweenness on a one-mode item projection (see below)
- If you want influential users in terms of reach → **PageRank** or **degree** are far cheaper and often more informative for recommendation contexts
- If you want structural brokers between item categories → betweenness on the item-item co-interaction projection with backbone extraction

---

## Community Detection at this scale

### The bipartite problem

**This is the most important point**: you have a bipartite graph. Standard community detection algorithms (Louvain, Leiden, SBM) are designed for one-mode networks. Running them directly on a bipartite graph produces communities that mix user nodes and item nodes together, which is rarely meaningful for a recommendation system.

You have two principled options:

**Option A — Bipartite community detection directly**

Some algorithms handle bipartite structure natively. Bipartite SBM (Stochastic Block Model) via **graph-tool** can infer a joint partition of users and items simultaneously, respecting the bipartite structure. This is statistically principled and resists overfitting.

```python
import graph_tool.all as gt

g = gt.load_graph("interactions.graphml")  # or build from edge list
# Mark bipartite structure
g.vp["kind"] = g.new_vertex_property("int")  # 0=user, 1=item

state = gt.minimize_nested_blockmodel_dl(g, state_args={"deg_corr": True})
state.draw()
```

Graph-tool is the only major Python library with a well-implemented bipartite SBM. Installation is via conda: `conda install -c conda-forge graph-tool`.

**Option B — Project to one mode, then detect communities (with backbone extraction)**

Project the bipartite graph to a user-user or item-item graph (connecting users who interacted with the same items, or items shared by the same users), then run community detection on the projection.

**Critical warning**: naive bipartite projection produces dense cliques (every user who bought the same popular item is fully connected). This inflates clustering coefficients, modularity scores, and centrality — the projection is meaningless without backbone extraction.

Backbone extraction filters to statistically significant edges:
- Use the **disparity filter** (Serrano et al. 2009) via the `backbone` R package or its Python port
- Or use **SDSM/FDSM** (Neal 2022), which conditions specifically on bipartite structure and is more appropriate here

After backbone extraction, run **Leiden with CPM** (Constant Potts Model) using `leidenalg`:

```python
import igraph as ig
import leidenalg

# Load the backbone-filtered projection
g_proj = ig.Graph.Read_Edgelist("item_projection_backbone.edges")

# Leiden with CPM (tunable resolution; avoids resolution limit)
partition = leidenalg.find_partition(
    g_proj,
    leidenalg.CPMVertexPartition,
    resolution_parameter=0.01,
    n_iterations=10,
    seed=42
)
print(f"Found {len(partition)} communities")
```

**Why Leiden and not Louvain**: Louvain can produce disconnected communities. Leiden (Traag, Waltman & van Eck 2019) guarantees connectivity and is strictly superior.

**Why CPM and not modularity**: modularity has a resolution limit — communities smaller than √(2m) edges are invisible. With 800 million interactions in the projected graph, this could hide all but the largest communities.

---

## Tool recommendations by task

| Task | Tool | Why |
|---|---|---|
| Approximate betweenness | **NetworKit** `ApproxBetweenness` | Parallel, scales to billions of edges, controllable error |
| Betweenness with GPU | **cuGraph** | 100–1000× faster if NVIDIA GPU available |
| Bipartite community detection | **graph-tool** nested SBM | Principled, bipartite-aware, best SBM implementation |
| Projected community detection | **leidenalg** + **igraph** | Fast Leiden on one-mode projection |
| Backbone extraction (projection) | **backbone** (R) or Python port | Required before any projection-based analysis |
| Loading/manipulating the graph | **igraph** (Python) | C backend, sparse representation, handles millions of nodes |

**Do not use NetworkX for any of these tasks at your scale.** The tools.md decision matrix is clear: for 500k–10M nodes, use graph-tool or NetworKit; for >10M, those plus cuGraph or distributed options.

---

## Memory and infrastructure considerations

800 million edges at ~16 bytes per edge (two 4-byte node IDs + 8-byte weight) = ~12.8 GB just for the edge data. You need a machine with at least **32 GB RAM** (64+ recommended) and a sparse-representation library (igraph, graph-tool, NetworKit — not NetworkX).

If the graph does not fit in memory at all, consider:
- **Apache Spark GraphFrames** for distributed processing
- **Neo4j with GDS** (Graph Data Science) plugin — handles PageRank and Louvain natively in a graph database

---

## Summary of what to actually do

1. **Do not use NetworkX.** Use igraph or NetworKit for loading and basic operations.
2. **Clarify whether you need exact or approximate betweenness.** Exact is infeasible; approximated (NetworKit or cuGraph) is tractable.
3. **Decide how to handle bipartite structure for community detection.** Bipartite SBM in graph-tool (principled) or backbone-extracted projection + Leiden (more scalable, less principled).
4. **Extract a backbone before projecting.** If you project users→users or items→items and then run community detection without backbone extraction, the results will be artifacts of the projection's clique structure, not real communities.
5. **Re-examine whether betweenness is the right centrality for your question.** For recommendation systems, PageRank on the projected graph or item co-occurrence degree often answers the "which items/users are important" question more directly and runs in a fraction of the time.
