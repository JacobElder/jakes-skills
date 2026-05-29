# NetworkX for a 5M-user, 2M-item, 800M-interaction recommendation graph

Short answer: no, NetworkX will not work for this. The plan needs to change before you write a single line of analysis code. Here is the full picture.

---

## First: your graph is bipartite, and that changes everything

Before addressing the tool question, there is a structural issue that is more important: a user-item interaction graph is **bipartite**. Users and items are different node types. Edges only run between the two sets; there are no user-user or item-item edges.

This matters because the methods you named — betweenness centrality and community detection — behave very differently on a bipartite graph than on the unipartite graph these algorithms assume:

- **Betweenness centrality on a bipartite graph** will produce values that are dominated by nodes whose type appears less frequently (items, here, since there are 2M vs 5M users) and shortest paths that alternate between node types in a structurally constrained way. The resulting ranking mixes user centrality and item centrality in a single sorted list. That list is almost never what you want. The typical question in a recommendation system is "which items are structurally central across diverse user segments?" or "which users are bridges between otherwise disconnected interest clusters?" — and those are separate questions requiring separate computation on each node type.

- **Community detection on the raw bipartite graph** will return communities that contain both users and items. These mixed communities are usually uninterpretable. A "community" of 10,000 users and 3,000 items that all co-occur does not answer a useful business question. This is one of the most common errors in recommendation-system graph analysis: running standard community detection on the raw bipartite graph, then trying to interpret the output.

**What to do instead** depends on your substantive question:

1. **If you want user communities** (which users have similar taste?): project to the user-user one-mode graph (edge weight = number of co-interacted items), then apply backbone extraction (disparity filter) to retain only statistically significant edges, then run community detection. Without backbone extraction, the projection produces a dense graph where almost every user pair shares at least one item and all structure is noise.

2. **If you want item communities** (which items are consumed together?): project to the item-item one-mode graph and do the same.

3. **If you want bipartite community structure directly**: use a **bipartite Stochastic Block Model**. graph-tool's `minimize_blockmodel_dl` with `bipartite=True` finds principled community structure without requiring projection. This is the cleanest approach.

State explicitly to the person reading your analysis which of these questions you are answering, because the answer will differ depending on the choice.

---

## Why NetworkX will not work at this scale

Your graph is:
- 5M + 2M = **7 million nodes**
- **800 million edges**

NetworkX uses a Python dict-of-dict representation. Each edge is a Python object with all the overhead that entails. At 800M edges, NetworkX's memory footprint would be on the order of several hundred gigabytes and almost certainly exceed available RAM on any single machine. Even if it fit in memory, the algorithms are single-threaded pure Python. Betweenness centrality is O(VE) — or O(V + E) for unweighted with Brandes's algorithm — but on a graph of this size with a pure-Python implementation, a single full betweenness computation would take days to weeks. This is not a matter of patience or hardware tuning; it is the wrong tool category.

From `references/tools.md`: "Using NetworkX for a million-node graph and concluding 'this is too slow for our problem': it's not the problem, it's the tool. Switch."

At 800M edges, you are roughly two orders of magnitude past NetworkX's practical ceiling.

---

## What to use instead

### For centrality computation at this scale

**NetworKit** is the best starting point for your hardware budget. It is designed specifically for parallel centrality computation on graphs with billions of edges. The betweenness centrality implementation uses the **Brandes-Pich approximation** (randomized sampling of pivot nodes), which is essential — exact betweenness on a graph with 800M edges is not tractable on any single machine regardless of library. You will get approximate betweenness with controllable error bounds.

```python
import networkit as nk

# Load from edge list (most efficient format for this scale)
G = nk.graphio.EdgeListReader('\t', 0).read("interactions.tsv")

# Approximate betweenness — nSamples controls accuracy vs. speed tradeoff
btwn = nk.centrality.ApproxBetweenness(G, epsilon=0.1, delta=0.1)
btwn.run()
scores = btwn.scores()  # list indexed by node ID
```

The `epsilon` and `delta` parameters control the approximation guarantee: with `epsilon=0.1, delta=0.1`, the estimate is within 0.1 of the true normalized value with probability 0.9. Tighten both if you need higher precision; loosen if throughput matters more.

**cuGraph** (NVIDIA RAPIDS) is the other strong option if you have GPU hardware. On a modern A100, cuGraph betweenness on graphs of this size runs in minutes rather than hours. The API mirrors NetworkX closely:

```python
import cudf
import cugraph

edges = cudf.read_csv("interactions.tsv", sep="\t", header=None, names=["src", "dst"])
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="src", destination="dst")

btwn_df = cugraph.betweenness_centrality(G, k=100)  # k = number of pivot samples
```

If no GPU is available, use NetworKit. If GPU is available, cuGraph will be faster.

### For community detection at this scale

After projecting and extracting a backbone (if going the one-mode route), or on the raw bipartite graph (if using SBM):

- **graph-tool** with `minimize_blockmodel_dl(bipartite=True)` for bipartite SBM — principled, generative, no resolution limit, no Louvain degeneracy. This is the highest-quality method. Harder to install (use conda's `gt` channel, not PyPI), but worth it for production analysis.

- **NetworKit + leidenalg** for a faster but less principled approach: NetworKit for the heavy graph operations, then `leidenalg` with the Constant Potts Model (CPM) for community detection after reducing graph size. Leiden guarantees connected communities (Louvain does not) and CPM avoids the resolution limit.

- **cuGraph** has a Louvain implementation that runs fast at scale, but Louvain has known issues: it can produce disconnected communities, and a single run is unreliable (the modularity landscape is degenerate — many different partitions have nearly identical modularity). If you use it, run many times and measure partition stability with NMI or ARI across runs before interpreting any community.

### Memory and I/O considerations

At 800M edges, the first bottleneck you will hit is data loading. Recommendations:

- Store interactions as a **compressed edge list** (`.tsv.gz` or Parquet). Do not load the full interaction table into a pandas DataFrame before building the graph — build the graph directly from the edge iterator.
- For NetworKit, use `nk.graphio.EdgeListReader` which streams rather than materializing.
- For graph-tool, use `gt.load_graph_from_csv`.
- Use integer node IDs, not string user/item identifiers, in the graph representation. Map string IDs to integers once in preprocessing and store the mapping separately. This alone can cut memory by 30–50%.

---

## Recommended sequence

1. **Clarify the substantive question.** What does "betweenness centrality" tell you in your system? If you want to find "bridge" users who connect otherwise disconnected taste communities, betweenness is reasonable (on the user-mode projection or on user nodes in a bipartite SBM partition). If you want to rank items by influence over information flow, item betweenness on the item projection is the right target. If neither of these is the question, a different centrality measure may serve better — PageRank over the bipartite graph (treating it as directed from user to item) gives item popularity weighted by user diversity, which is often more useful in recommendation contexts.

2. **Inspect before computing.** Even before any centrality or community work, compute: number of nodes per type, number of edges, density, degree distribution for each node type (expect heavy-tailed; plot on log-log scale), number of connected components, and the size of the largest connected component. At this scale you will likely find a giant component containing nearly all nodes and a long tail of isolates or small components; confirm this before running any global algorithm.

3. **Decide: projection + backbone, or bipartite-native methods.** This is the key methodological fork. Bipartite SBM (graph-tool) is cleaner but harder to deploy. Projection + backbone + Leiden is more familiar but introduces the projection step's assumptions. Neither is wrong; be explicit about the choice and its implications.

4. **Match the tool to the scale.** For this graph:
   - Use **NetworKit** (CPU multicore) or **cuGraph** (GPU) for centrality
   - Use **graph-tool** for SBM community detection
   - Use **leidenalg** for Leiden if you go the projection route
   - Do not use NetworkX for anything beyond prototype exploration on a sample

5. **Approximate betweenness, do not compute exact.** Exact betweenness on 7M nodes and 800M edges is not a tractable single-machine computation. The Brandes-Pich approximation with a few hundred pivot samples gives reliable rankings for top-k nodes, which is what you actually need.

---

## Summary

| Concern | Assessment |
|---|---|
| NetworkX at this scale | Not viable — memory and compute both prohibitive |
| Bipartite structure | Must be addressed before any standard algorithm is applied |
| Community detection on raw graph | Will produce uninterpretable mixed user-item communities |
| Betweenness (exact) | Not tractable at 7M nodes / 800M edges; use approximation |
| Recommended tool: centrality | NetworKit (CPU) or cuGraph (GPU) |
| Recommended tool: community | graph-tool (bipartite SBM) or leidenalg (post-projection) |
| Recommended tool: backbone | R `backbone` package (disparity filter) or Python port |
