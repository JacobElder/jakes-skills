NetworkX will not work at this scale. Here is a direct assessment of why, and what to use instead.

## Why NetworkX fails here

NetworkX is a pure-Python library that stores graphs as Python dicts of dicts. Every node and edge is a Python object. At your scale:

- **Memory**: A graph with 5M nodes and 800M edges in NetworkX consumes roughly 200–500 bytes per edge in object overhead alone. That is 160–400 GB of RAM just for the edge data, before you store any attributes. No commodity machine handles this.
- **Speed**: NetworkX betweenness centrality is O(VE) for unweighted graphs and O(VE + V² log V) for weighted. On a graph with 7M nodes and 800M edges, exact betweenness is not computable in any reasonable time — we are talking weeks to months on a single machine.
- **Single-threaded**: NetworkX does not parallelize across cores or distribute across machines. It cannot use GPUs.

**Bottom line**: NetworkX is appropriate for graphs with up to roughly 100K–500K edges, depending on your RAM and how long you are willing to wait. Your graph is 1,600x larger than that ceiling.

---

## What you should actually use

### For betweenness centrality

**Exact betweenness at this scale is almost certainly the wrong goal.** Even graph libraries that are orders of magnitude faster than NetworkX cannot compute exact betweenness on 800M edges in interactive time. Consider:

1. **Approximate betweenness with sampling** — Most frameworks (including NetworkX itself, ironically) support Brandes' algorithm with pivot sampling. You sample k source nodes instead of all V nodes. At k=1000, you get results within a few percent of exact with a fraction of the compute. This is the standard approach at scale.

2. **cuGraph (NVIDIA RAPIDS)** — GPU-accelerated graph analytics. Betweenness centrality with sampling runs on a single A100 in minutes on graphs of this size. Requires NVIDIA GPU with enough VRAM (an 80 GB A100 can handle ~500M edges in memory). API is intentionally close to NetworkX.

3. **GraphX (Apache Spark)** — Distributed, runs on a cluster. Slower than cuGraph for single-machine GPU workloads, but scales horizontally if you have a Spark cluster. Approximate betweenness is supported via Pregel.

4. **graph-tool** — C++ backend, multi-threaded, much faster than NetworkX for CPU-only work. Still single-machine, so 800M edges will push RAM limits, but it is a viable option if you have a machine with 512 GB+ RAM.

### For community detection

Community detection is more tractable at scale because the best algorithms (Louvain, Leiden) are near-linear in edges.

1. **igraph (Python binding)** — Louvain and Leiden are implemented in C. On a machine with enough RAM (you need roughly 20–40 bytes per edge for a CSR representation, so ~32 GB for 800M edges), igraph's Leiden implementation can process this in hours. This is the most practical option if you can fit the graph in RAM.

2. **cuGraph** — GPU-accelerated Louvain. On an A100, community detection on 800M edges runs in minutes. This is the best option if you have GPU access.

3. **PecanPy / node2vec + clustering** — If you want embedding-based communities, PecanPy computes node2vec embeddings efficiently on large graphs, and you cluster in embedding space.

4. **GraphX / Spark** — For distributed Louvain across a cluster, though the overhead of coordination makes it slower than cuGraph for single-node GPU work.

---

## Recommended stack by resource availability

| You have | Betweenness | Community detection |
|---|---|---|
| Single machine, no GPU, lots of RAM | graph-tool (approximate) | igraph (Leiden) |
| Single machine + NVIDIA GPU | cuGraph (approximate) | cuGraph (Louvain) |
| Cloud cluster (Spark) | GraphX (approximate) | GraphX (Louvain) |

---

## Practical migration note

If you are already writing NetworkX code, cuGraph is the easiest migration path — it has a `cugraph.betweenness_centrality()` and `cugraph.louvain()` that mirror NetworkX's API. You can often swap in cuGraph with minimal code changes.

For igraph, the API differs from NetworkX but is well-documented. Reading your edge list into igraph is straightforward with `igraph.Graph.TupleList()` or loading from a CSV.

---

## Summary

Do not use NetworkX. For your scale, the practical choices are cuGraph (if you have GPU access) or igraph + graph-tool (if you are CPU-only with a high-RAM machine). In either case, use approximate betweenness centrality with sampling — exact betweenness is not computationally feasible on a graph this large regardless of the library.
