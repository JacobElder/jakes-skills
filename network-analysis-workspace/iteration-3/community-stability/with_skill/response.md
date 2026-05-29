Before you name or describe these communities, there are several things that need to happen first — and a few flags to raise about Q = 0.67.

## Stop: your modularity score is not a reliability certificate

A modularity of 0.67 tells you that the partition has a high within-community edge fraction relative to a degree-preserving null. It does not tell you that the partition is stable, reproducible, or structurally real. These are different questions, and the literature is unambiguous on this point.

Specifically:

**The degeneracy problem (Good, De Montjoye & Clauset 2010).** The modularity landscape has exponentially many near-optimal partitions that are structurally very different from one another. A single Louvain run returns one of these almost arbitrarily. Re-running with a different random seed on the same graph will produce a different partition — potentially assigning major authors to different communities — while achieving nearly identical Q. High Q does not distinguish between "the one true partition" and one of thousands of near-equivalent alternatives.

**Louvain can produce internally disconnected communities.** The Traag, Waltman & van Eck (2019) paper that introduced Leiden documented that Louvain's local-move phase can disconnect communities, meaning what you call "Community 3" might not actually be a connected subgraph. Leiden was developed to fix this.

**Q = 0.67 has not been compared to a null.** Run the same Louvain procedure on 1,000 configuration-model randomizations of your network (preserving degree sequence). If the null gives Q ≈ 0.65 on average, your "great" Q is barely above chance. If it gives Q ≈ 0.30, you have something real. You cannot interpret the absolute value of Q without this comparison.

---

## What you need to do before naming communities

### Step 1: Run Louvain (or better, Leiden) many times

```python
import igraph as ig
import leidenalg
import numpy as np
from sklearn.metrics import adjusted_rand_score

g = ig.Graph.Read_Edgelist("coauthorship.edgelist")  # or your format

n_runs = 100
partitions = []
for seed in range(n_runs):
    part = leidenalg.find_partition(
        g, leidenalg.ModularityVertexPartition,
        seed=seed
    )
    partitions.append(part.membership)

# Pairwise ARI across all runs
ari_scores = []
for i in range(n_runs):
    for j in range(i+1, n_runs):
        ari_scores.append(adjusted_rand_score(partitions[i], partitions[j]))

print(f"Mean pairwise ARI: {np.mean(ari_scores):.3f}")
print(f"Std ARI: {np.std(ari_scores):.3f}")
```

**Interpreting the result:**
- Mean ARI > 0.90: the partition is highly stable; you can proceed to name communities with confidence.
- Mean ARI 0.70–0.90: moderate stability; note in your paper that you use the modal partition across runs.
- Mean ARI < 0.70: the partition is not stable. Do not name communities. Switch to a Stochastic Block Model (see below).

### Step 2: Compare Q to a configuration-model null

```python
import networkx as nx
import random

G = nx.read_edgelist("coauthorship.edgelist")
degree_seq = [d for _, d in G.degree()]

q_nulls = []
for _ in range(1000):
    G_null = nx.configuration_model(degree_seq, create_using=nx.Graph)
    G_null = nx.Graph(G_null)  # remove multi-edges
    G_null.remove_edges_from(nx.selfloop_edges(G_null))
    # run Louvain on G_null and record Q
    # (use python-louvain / community package)
    import community as community_louvain
    part_null = community_louvain.best_partition(G_null)
    q_nulls.append(community_louvain.modularity(part_null, G_null))

print(f"Observed Q: 0.67")
print(f"Null Q: {np.mean(q_nulls):.3f} ± {np.std(q_nulls):.3f}")
```

A z-score of (0.67 − null_mean) / null_std > 3 is a reasonable threshold to conclude the communities are not attributable to degree heterogeneity alone.

### Step 3 (strongly recommended): Cross-validate with Leiden and SBM

Run Leiden on the same network and compute ARI between Louvain and Leiden partitions. If they agree (ARI > 0.85), the community structure is robust to method choice. If they disagree substantially, you have method-dependent communities, not ground truth.

For a publication, consider also running a degree-corrected Stochastic Block Model (DC-SBM), which is generative, principled, and does not suffer from the degeneracy pathology:

```python
import graph_tool.all as gt

g = gt.load_graph("coauthorship.graphml")
state = gt.minimize_nested_blockmodel_dl(g)  # nested DC-SBM
for i, s in enumerate(state.levels):
    print(f"Level {i}: {s.get_nonempty_B()} blocks")
```

The nested SBM will also tell you if your 8 communities exist at a natural hierarchical level, or whether a 4-community or 16-community partition would be better supported by the data.

---

## How to report communities in your paper (conditional on passing the above)

Assuming stability is established, here is what defensible reporting looks like:

### Structural description (required)

For each community, report:
- Size (number of authors)
- Internal edge density
- Identifying structural role: is it tightly knit (high clustering), or does it contain hubs?

You can compute per-community density:

```python
import networkx as nx

G = nx.read_edgelist("coauthorship.edgelist")
# membership is a dict {node: community_id}
for comm_id in set(membership.values()):
    nodes = [n for n, c in membership.items() if c == comm_id]
    subg = G.subgraph(nodes)
    density = nx.density(subg)
    print(f"Community {comm_id}: n={len(nodes)}, density={density:.3f}")
```

### Substantive naming (requires domain knowledge, not network structure)

Network community detection does not produce names. The partition tells you which authors cluster together structurally; your domain knowledge tells you what that means. The correct approach:

1. Identify the top 5–10 authors by degree (or betweenness) within each community. These are the anchors.
2. Look at their publication venues, keywords, institutional affiliations, or subfield identifiers.
3. Name the community after the substantive theme that best captures the majority of its members.
4. Acknowledge the simplification: real communities overlap; forcing a hard partition means some authors will be in a community that doesn't fully capture their work.

An example of defensible naming in a methods section:
> "Community 4 (n = 187 authors) contained the highest-degree authors publishing in computational social science and complex systems venues (Nature Human Behaviour, JASSS, PNAS social science section). We label this community 'Computational Social Science.' Eight authors in this community also had strong ties to Community 2 (Network Neuroscience); we note them as cross-community bridges."

This is defensible. What is not defensible:
> "Louvain found 8 natural communities. We named them based on their members."

That sentence implies Louvain discovered something natural, when it optimized an objective function with known degeneracy.

### Required elements in the paper

1. **Network dimensions**: n = 1200 authors, m = 4800 edges, undirected, density = 4800 / (1200 × 1199 / 2) ≈ 0.0067. State whether you are using the giant component only.

2. **Algorithm and implementation**: "We used Leiden community detection (Traag, Waltman & van Eck 2019) implemented in `leidenalg` v0.9.x with the ModularityVertexPartition objective." (If you used Louvain: note it and explain why you didn't use Leiden.)

3. **Stability**: "We ran the algorithm 100 times with different random seeds. The mean pairwise ARI across runs was 0.XX (SD = 0.XX), indicating [high/moderate/low] stability. Communities reported here reflect the modal partition across 100 runs." If ARI < 0.80, this sentence is load-bearing — reviewers will ask.

4. **Null comparison**: "The observed modularity (Q = 0.67) substantially exceeded the mean modularity of 1,000 configuration-model null networks with the same degree sequence (Q_null = M ± SD), indicating that the partition is unlikely to result from degree heterogeneity alone."

5. **Resolution limit check**: With m = 4800 edges, the resolution limit is √(2 × 4800) ≈ 98 edges. Any community with fewer than ~98 internal edges is below the resolution limit and may have been merged with a neighbor or artificially split. Report community sizes and internal edge counts; note any communities that fall near this threshold.

6. **Community profiles**: A table with community ID, size (n), internal edge density, top 3–5 member authors (or institutions), and the label you assign.

---

## A note on co-authorship networks specifically

Co-authorship networks are one-mode projections of a bipartite author-paper network. If you constructed this network by projecting directly from the bipartite structure (authors × papers), you should verify that you applied backbone extraction (e.g., the disparity filter) before community detection. Raw projections inflate clustering and can produce spurious communities driven by large multi-author papers — a single 50-author paper creates a 50-node clique in the projection, which will dominate any modularity-based partition.

If you projected without backbone extraction, the communities may reflect paper-size heterogeneity rather than intellectual communities. This is worth checking and worth a sentence in your methods section regardless.

---

## Summary of required steps before naming

| Step | What to do | Why |
|---|---|---|
| Stability analysis | Run 100+ times, report mean ARI | Single Louvain run is arbitrary sample |
| Null comparison | Compare Q to configuration-model null | High Q alone doesn't establish real structure |
| Method robustness | Cross-validate with Leiden | Communities should survive method change |
| Resolution limit | Check community sizes vs. √(2m) ≈ 98 | Small communities may be artifacts |
| Bipartite origin | Verify backbone extraction was applied | Raw projection inflates structure |

Only after steps 1 and 2 produce acceptable results should you proceed to naming communities. If stability is low (mean ARI < 0.70), switch to a Stochastic Block Model before reporting.
