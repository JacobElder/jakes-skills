# Response: Reporting Louvain Communities in a Co-authorship Network

## Before naming communities: address serious methodological concerns

Your setup — 1,200 authors, 4,800 edges, Louvain, Q = 0.67, 8 communities — has real problems that need to be resolved *before* you write up community descriptions in a paper. Reporting them as-is would invite a sharp reviewer comment. Here is what needs to happen first.

---

## Issue 1: A single Louvain run is not "the" partition

This is the most important thing to fix. The modularity landscape has exponentially many near-optimal solutions that are structurally very different from each other (Good, De Montjoye & Clauset 2010). A single Louvain run returns one of these almost arbitrarily. Running again with a different random seed will return a different partition, possibly quite different.

**What to do:** Run Louvain 100+ times (or switch to Leiden, which finds better local maxima and guarantees connected communities — more on that below). Then report partition stability.

```python
import igraph as ig
from igraph import Graph
import numpy as np

# Load your graph
g = Graph.Read_Edgelist("coauthorship.edgelist")
g.to_undirected()

# Run Leiden 100 times (preferred over Louvain)
from leidenalg import find_partition, ModularityVertexPartition
import leidenalg

partitions = []
for seed in range(100):
    part = leidenalg.find_partition(g, leidenalg.ModularityVertexPartition,
                                    seed=seed)
    partitions.append(part.membership)

# Compare all pairs with ARI
from sklearn.metrics import adjusted_rand_score
aris = []
for i in range(len(partitions)):
    for j in range(i+1, len(partitions)):
        aris.append(adjusted_rand_score(partitions[i], partitions[j]))

print(f"Mean ARI across runs: {np.mean(aris):.3f} (SD={np.std(aris):.3f})")
print(f"Min ARI: {np.min(aris):.3f}")
```

Interpret results:
- Mean ARI > 0.90: the partition is quite stable; you can report the dominant partition with confidence
- Mean ARI 0.70–0.90: report stability explicitly; name only communities that appear in >80% of runs
- Mean ARI < 0.70: the partition is not stable; do not name individual communities; consider SBM instead

**Report in your paper:** "We ran Leiden (or Louvain) 100 times with different random seeds. The mean adjusted Rand index across run pairs was [X] (SD = [Y]), indicating [high/moderate] partition stability. We report the partition with the highest modularity score as the representative partition."

---

## Issue 2: Use Leiden, not Louvain

Louvain has a known bug: it can produce internally *disconnected* communities (Traag, Waltman & van Eck 2019). This is not a minor edge case — it happens because nodes can move out of a community without checking whether the remaining nodes still form one connected component. Leiden was developed specifically to fix this and guarantees connected communities.

If your results are going into a peer-reviewed paper, switch to Leiden now. The `leidenalg` Python package and `igraph::cluster_leiden` in R implement it. The modularity value will be similar or better.

---

## Issue 3: Validate Q = 0.67 against a null model

A modularity of 0.67 looks high, but modularity finds "communities" even in Erdős–Rényi random graphs where no community structure exists (Lancichinetti & Fortunato 2009). You must compare your Q against a configuration-model null that preserves the degree sequence.

```python
import networkx as nx
import numpy as np

# Assuming G is your NetworkX graph
real_Q = 0.67  # your reported value

# Generate 1000 configuration-model nulls
null_Qs = []
for _ in range(1000):
    G_null = nx.configuration_model(list(dict(G.degree()).values()))
    G_null = nx.Graph(G_null)  # remove multi-edges/self-loops
    G_null.remove_edges_from(nx.selfloop_edges(G_null))
    # Run Louvain/Leiden on null
    part = nx.algorithms.community.louvain_communities(G_null, seed=42)
    Q_null = nx.algorithms.community.modularity(G_null, part)
    null_Qs.append(Q_null)

print(f"Real Q: {real_Q:.3f}")
print(f"Null Q: mean={np.mean(null_Qs):.3f}, SD={np.std(null_Qs):.3f}")
print(f"Z-score: {(real_Q - np.mean(null_Qs)) / np.std(null_Qs):.1f}")
```

**Report in your paper:** "The observed modularity (Q = 0.67) substantially exceeded the mean modularity of 1,000 configuration-model null graphs with identical degree sequences (Q_null = [mean] ± [SD]; z = [Z]), confirming that the detected community structure is non-trivial."

For a 1,200-node coauthorship network, a random graph of this density will typically yield Q_null in the range 0.05–0.15, so Q = 0.67 will almost certainly survive this check. But you still have to run it and report it.

---

## Issue 4: Check the resolution limit

With 4,800 edges, Louvain/Leiden cannot detect communities with fewer than √(2 × 4,800) ≈ 98 internal edges. If any of your 8 communities has fewer than ~98 edges, they may be real communities that modularity is artificially merging with neighbors. Check:

```python
# After running partition
for i, community in enumerate(communities):
    subgraph = G.subgraph(community)
    internal_edges = subgraph.number_of_edges()
    print(f"Community {i+1}: {len(community)} nodes, {internal_edges} internal edges")
```

If small communities fall below the √(2m) threshold, consider running Leiden with the Constant Potts Model (CPM) at multiple resolution values (γ = 0.01 to 0.5) and scanning for stable community counts.

---

## How to name and describe communities (once the above checks pass)

Once you have a stable, validated partition, here is how to characterize and name each community for a paper.

### Step 1: Compute structural descriptors for each community

For each of the 8 communities, compute:

| Descriptor | What it tells you | Code |
|---|---|---|
| Size (nodes, edges) | Scale of the group | `len(community)`, `G.subgraph(community).number_of_edges()` |
| Internal density | How tightly connected | `nx.density(G.subgraph(community))` |
| Internal/external edge ratio | How well-separated | internal edges / (internal + boundary edges) |
| Mean internal degree | Activity level | mean degree within subgraph |
| Top-degree nodes | Who anchors the community | sorted by degree within subgraph |

```python
import networkx as nx

for i, comm in enumerate(communities):
    sg = G.subgraph(comm)
    # Boundary edges (edges from this community to others)
    boundary = [(u, v) for u, v in G.edges()
                if (u in comm) != (v in comm)]
    internal_edges = sg.number_of_edges()
    ratio = internal_edges / (internal_edges + len(boundary) + 1e-9)
    top_nodes = sorted(sg.degree(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"\nCommunity {i+1}: n={len(comm)}, edges={internal_edges}")
    print(f"  Density: {nx.density(sg):.4f}")
    print(f"  Int/total edge ratio: {ratio:.3f}")
    print(f"  Top 5 nodes by degree: {top_nodes}")
```

### Step 2: Use node metadata to name communities

Community names must come from your metadata, not from the structural position of nodes. For a coauthorship network, you likely have access to:

- **Institutional affiliations**: if community members cluster by institution, call it "MIT cluster" or "European consortium"
- **Research subfield / keyword**: pull the most frequent MeSH terms, journal names, or keyword co-occurrences from the papers authored by members
- **Career stage / role**: if you have faculty vs. postdoc metadata
- **Temporal activity**: if some communities are dominated by authors active in different periods

**Name construction rule:** A community name should reflect what makes this group coherent, not a structural label ("Community 1"). Examples:
- "Computational neuroimaging cluster" — if members co-publish primarily in NeuroImage, OHBM
- "Clinical trials consortium" — if dominated by trial PIs from multiple hospitals
- "Methods developers" — if members share methods-focused publication records

**What not to do:** Do not call them "Core group," "Peripheral cluster," or "High-density community" — these are structural descriptions, not substantive ones, and reviewers will ask "what does this actually represent?"

### Step 3: Check communities for interpretive coherence

For each community, the check is: **can I write one sentence explaining why these authors form a group?** If you cannot, the community may be an artifact (especially if it is small and near the resolution limit) or may represent a structurally real but substantively incoherent cluster (authors who co-authored for convenience, not shared research program). It is legitimate to note this in your paper.

### Step 4: Standard reporting template

Here is a reporting template that covers what methods-oriented reviewers will expect:

---

*Example methods section (adapt to your network):*

> We detected community structure using the Leiden algorithm (Traag, Waltman & van Eck, 2019), which improves on Louvain by guaranteeing internally connected communities. We ran the algorithm 100 times with different random seeds (leidenalg v0.10.2, Python 3.11). The mean adjusted Rand index across run pairs was 0.XX (SD = 0.0Y), indicating high partition stability. We report the partition with the highest modularity score. The observed modularity (Q = 0.XX) substantially exceeded the mean modularity of 1,000 configuration-model null graphs with the same degree sequence (Q_null = 0.XX ± 0.0X, z = XX, p < 0.001), confirming that the detected community structure is non-trivial. The co-authorship network comprised 1,200 authors (nodes) and 4,800 edges (co-authored papers as weighted ties). Community detection yielded 8 communities ranging in size from XX to XX authors (Table 1). We characterized each community by its most frequent institutional affiliations and publication venues among member authors, yielding the descriptive labels in Table 1.

---

*Example results table:*

| Community | Label | N authors | N edges | Density | Top institution | Top journal |
|---|---|---|---|---|---|---|
| 1 | [Substantive name] | XX | XX | 0.XXX | [Institution] | [Journal] |
| 2 | [Substantive name] | XX | XX | 0.XXX | [Institution] | [Journal] |
| ... | | | | | | |

---

### Step 5: Consider supplementary SBM validation

If reviewers push back on the modularity-based partition (common in methods-aware venues), run a degree-corrected Stochastic Block Model with graph-tool and show that the SBM's inferred block structure is consistent with the Leiden partition. This is the gold standard because SBMs are generative, resist overfitting via MDL, and the number of blocks is learned rather than tuned.

```python
import graph_tool.all as gt
g = gt.load_graph("coauthorship.graphml")
state = gt.minimize_blockmodel_dl(g, state_args=dict(deg_corr=True))
print(f"SBM infers {state.get_nonempty_B()} blocks")
# Compare to your 8 Leiden communities with ARI
```

If the SBM recovers a similar number of blocks (e.g., 6–10) and the ARI between the two partitions is > 0.7, you have strong convergent evidence for your 8-community solution.

---

## Summary of what to do before submitting

1. Switch from Louvain to Leiden (guarantees connected communities)
2. Run 100 times; compute and report mean ARI across runs
3. Run configuration-model null comparison; report z-score for Q
4. Check all 8 communities for resolution-limit violations (< √(2m) ≈ 98 internal edges)
5. For each community, compute size, density, internal/external edge ratio, and top nodes
6. Use author metadata (institution, journal, subfield) to assign substantive names
7. Optionally: validate with a degree-corrected SBM

Without steps 1–4, you cannot reliably claim that these 8 communities are real, stable structures — a single Louvain run with Q = 0.67 is a starting point, not a finding.

---

## Canonical references

- Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. *Scientific Reports*, 9, 5233.
- Good, B. H., De Montjoye, Y.-A., & Clauset, A. (2010). Performance of modularity maximization in practical contexts. *Physical Review E*, 81, 046106.
- Fortunato, S. & Barthélemy, M. (2007). Resolution limit in community detection. *PNAS*, 104(1), 36–41.
- Lancichinetti, A. & Fortunato, S. (2009). Community detection algorithms: a comparative analysis. *Physical Review E*, 80, 056117.
- Karrer, B. & Newman, M. E. J. (2011). Stochastic blockmodels and community structure in networks. *Physical Review E*, 83, 016107.
- Peixoto, T. P. (2019). Bayesian stochastic blockmodeling. In *Advances in Network Clustering and Blockmodeling*. Wiley.
- Peel, L., Larremore, D. B., & Clauset, A. (2017). The ground truth about metadata and community detection in networks. *Science Advances*, 3, e1602548.
