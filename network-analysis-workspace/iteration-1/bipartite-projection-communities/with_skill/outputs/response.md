# Response: Bipartite Projection + Louvain Community Detection

## Short answer

Your general direction is reasonable, but the plan as stated has two significant problems that will meaningfully distort your results. Before you run your existing NetworkX code, you need to address both. Here is what to fix and why.

---

## Problem 1: Projecting without backbone extraction

When you project your bipartite (person × project) network onto a person-person graph, every project of size *d* creates a complete clique of *d(d-1)/2* edges in the projection. A project with 20 employees contributes 190 edges; a project with 50 employees contributes 1,225 edges. With ~150 projects at a realistic size distribution across 800 employees, this means:

- **Clustering is artificially inflated** — the projection is structurally dominated by induced cliques, not genuine repeated collaboration
- **Edge weights (shared-project counts) are not a meaningful measure of relationship strength** without controlling for project size and each employee's overall project load. Someone who joins every large project will be connected to hundreds of colleagues with high weights, simply because those projects are large, not because of any special collaboration.
- **Community detection on the raw projection tends to recover the project affiliations as communities** — which you already know, since that's your input data.

**The fix: backbone extraction before community detection.**

For a bipartite projection, the appropriate null model must respect the bipartite structure. The two best options are:

- **Stochastic Degree Sequence Model (SDSM)** (Neal 2014): tests each projection edge against a null that preserves expected row and column sums of the incidence matrix. Gives a p-value per edge; keep edges with *p* < 0.05 (or your chosen α). This is the recommended default.
- **Fixed Degree Sequence Model (FDSM)**: same idea but preserves *exact* row/column sums (stronger null, slower computation).

Do **not** use the disparity filter here — it works on the projection's edge weights but ignores the bipartite structure, so it misses the information that drives the correct null.

In R, the `backbone` package (Neal 2022) handles this directly:

```r
library(backbone)
bb <- sdsm(B, alpha = 0.05, class = "igraph")  # B is your incidence matrix
# Now run community detection on bb, not the raw projection
```

For Python, there is no single canonical equivalent, but you can implement SDSM from the analytical approximation in Neal (2014), or use `cdlib` for related backbone methods.

After extraction, **report how many edges were retained** (e.g., "the backbone retains 8% of projected edges at α = 0.05"). A backbone retaining 5% vs. 50% of edges represents fundamentally different network topologies and this number belongs in any report of results.

**Alternative: skip the projection entirely.** If the goal is to find communities of employees who collaborate, you can run bipartite community detection directly on the person × project network. Options:
- **Bipartite SBM** in graph-tool: `gt.minimize_nested_blockmodel_dl(g, state_args=dict(pclabel=g.vp.kind))` — principled, learns the number of communities, handles hierarchy
- **Bipartite modularity** (Barber 2007): available in `cdlib`

This avoids the projection pathologies entirely and is the cleaner methodological choice.

---

## Problem 2: Louvain has known reliability problems — use Leiden instead

Assuming you do project and backbone-extract, Louvain is not the best choice for the final community detection step:

1. **Louvain can produce internally disconnected communities.** Its local-move + aggregation procedure can move nodes out of a community without checking whether the remaining nodes are still connected. This is a documented structural flaw (Traag, Waltman & van Eck 2019).

2. **A single Louvain run is unreliable.** Modularity's optimization landscape has exponentially many near-optimal partitions that are structurally very different from each other. One run returns one near-arbitrary sample from this landscape. Running again with a different seed can give a very different partition.

3. **The resolution limit.** Modularity cannot detect communities smaller than √(2m) edges, where *m* is the number of edges. After backbone extraction your edge count will be much smaller, so this may not bite you, but it is worth knowing.

**Use Leiden instead of Louvain.** Leiden guarantees internally connected communities and finds better local maxima via a refinement step. It is a strict improvement. In Python:

```python
import leidenalg
import igraph as ig

# Convert your backbone NetworkX graph to igraph
G_ig = ig.Graph.from_networkx(G_backbone)

# Run Leiden many times, assess stability
partitions = []
for seed in range(100):
    part = leidenalg.find_partition(
        G_ig,
        leidenalg.ModularityVertexPartition,
        seed=seed
    )
    partitions.append(part.membership)

# Compare stability across runs
from sklearn.metrics import adjusted_rand_score
aris = [adjusted_rand_score(partitions[0], partitions[i]) for i in range(1, 100)]
print(f"Mean ARI across 100 runs: {np.mean(aris):.3f}")
```

**Report the stability, not just the partition.** "Mean ARI across 100 runs = 0.82" is a defensible result. "Here are the communities" from a single Louvain run is not.

For even stronger guarantees, consider the **Constant Potts Model (CPM)** resolution in Leiden (`leidenalg.CPMVertexPartition`), which does not have the resolution limit. You tune the resolution parameter γ and can scan across values to see which community structure is stable across a range.

---

## The principled alternative: Stochastic Block Model

If you want the most defensible result, the nested SBM in graph-tool (Peixoto 2014, 2017) is the gold standard:

- **Learns the number of communities** from the data (no need to choose K or γ)
- **Generalizes:** finds assortative communities, core-periphery, or disassortative structure — whatever the data support, not just "dense groups"
- **Resists overfitting** via minimum description length (MDL) inference — won't find "communities" in a random graph
- **Hierarchical** by default — discovers nested structure automatically

```python
import graph_tool.all as gt
state = gt.minimize_nested_blockmodel_dl(g)
for i, s in enumerate(state.levels):
    print(f"level {i}: {s.get_nonempty_B()} blocks")
```

graph-tool has a harder install than NetworkX/igraph, but for an 800-node network it is tractable.

---

## Recommended workflow, concretely

Given your setup (800 employees, ~150 projects, NetworkX code ready):

1. **Inspect the bipartite network first.** Check: distribution of project sizes, distribution of employee project counts, overall density. A project with 200 of 800 attendees dominates the projection; you need to know if you have any.

2. **Project with backbone extraction (SDSM at α = 0.05).** If you must stay in Python and don't want to port to R, implement the SDSM p-value analytically (see Neal 2014 Eq. 3–4) or use FDSM via bootstrap sampling. Report the fraction of edges retained.

3. **Run Leiden on the backbone** (not Louvain), with 50–100 seeds. Report the mean ARI across runs as a stability measure alongside the best partition.

4. **Compare to a null.** Shuffle the backbone (configuration model, preserving degrees), rerun Leiden. If your actual modularity or community structure score is not substantially better than on shuffled graphs, the "communities" are not real.

5. **Validate against available metadata.** Do the detected communities correspond to department, team, seniority level, or office location? Correlation between network communities and organizational metadata is evidence of construct validity (but note: metadata and communities are answering different questions — Peel, Larremore & Clauset 2017).

---

## Summary of changes to make

| Issue | Current plan | Fix |
|---|---|---|
| Bipartite projection | Raw weighted projection (shared-project count) | SDSM backbone extraction before any analysis |
| Community algorithm | Louvain, single run | Leiden, 50–100 seeds; report stability (ARI) |
| Null comparison | Not mentioned | Rerun on configuration-model null; compare modularity |
| Alternative (if possible) | Project first | Bipartite SBM or bipartite modularity directly on the two-mode network |

Your NetworkX code for the projection step is a fine starting point, but the analysis it feeds into needs these two fixes to be defensible. The backbone extraction in particular is not optional — projecting without it and running community detection is one of the most common and most documented errors in applied social network analysis.

---

## Key references

- Neal, Z. P. (2014). "A sign of the times? Weak and strong polarization in the U.S. Congress, 1973–2016." *Social Networks* — introduces SDSM
- Neal, Z. P. (2022). "backbone: An R package to extract network backbones." *PLOS ONE* 17: e0269137
- Traag, V. A., Waltman, L., & van Eck, N. J. (2019). "From Louvain to Leiden." *Scientific Reports* 9: 5233
- Barber, M. J. (2007). "Modularity and community detection in bipartite networks." *Physical Review E* 76: 066102
- Peixoto, T. P. (2019). "Bayesian stochastic blockmodeling." In *Advances in Network Clustering and Blockmodeling*. Wiley
- Good, B. H., De Montjoye, Y.-A., & Clauset, A. (2010). "Performance of modularity maximization in practical contexts." *Physical Review E* 81: 046106
