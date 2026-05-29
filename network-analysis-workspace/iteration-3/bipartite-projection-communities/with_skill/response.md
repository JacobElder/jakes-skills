# Response: Bipartite Projection + Community Detection for Employee Collaboration

Your plan is on the right track conceptually, but there are two issues to fix before running Louvain — one that will meaningfully distort your results, and one that affects the reliability of any result you get. Let me walk through both, then give you revised code.

---

## Issue 1: Projecting without backbone extraction inflates community structure

When you project a bipartite (person × project) network onto a person–person network, every pair of employees who shared a single project becomes connected, and employees who shared many projects get proportionally higher edge weights. The problem is that **large projects create cliques**. If 40 employees all worked on one big initiative, those 40 people get fully connected to each other with weight ≥ 1, even if the project was their only contact. This clique structure is an artifact of co-membership, not evidence of a tight-knit collaboration group. It will inflate clustering coefficients, inflate modularity scores, and bias community detection toward absorbing those large-project cliques as "communities."

The fix before running any community detection is **backbone extraction** — statistical filtering that retains only edges whose weight is more than you'd expect by chance given each person's overall project participation rate. The standard method for bipartite projections is the **SDSM (Stochastic Degree Sequence Model)** or the **FDSM (Fixed Degree Sequence Model)**. Both ask: "given that employee A participated in X projects and employee B participated in Y projects, how many shared projects would we expect by chance?" They then keep only edges where the observed co-membership is significantly higher than the null expectation.

For a network of your scale (800 nodes, ~150 events), the FDSM is feasible but slow; SDSM is faster and usually sufficient. The `backbone` Python package implements both cleanly.

```python
import networkx as nx
import numpy as np
from backbone import sdsm  # pip install backbone

# Build bipartite graph
B = nx.Graph()
# Add edges: (employee_id, project_id) pairs
# Mark node types
for emp in employees:
    B.add_node(emp, bipartite=0)
for proj in projects:
    B.add_node(proj, bipartite=1)
for emp, proj in edges:
    B.add_edge(emp, proj)

# Project to person-person (weighted)
from networkx.algorithms import bipartite
people = {n for n, d in B.nodes(data=True) if d["bipartite"] == 0}
W = bipartite.weighted_projected_graph(B, people)

print(f"Projected graph: n={W.number_of_nodes()}, m={W.number_of_edges()}, density={nx.density(W):.4f}")

# Extract backbone — keep edges significant at alpha=0.05
# sdsm() returns a pruned networkx graph
G_backbone = sdsm(W, alpha=0.05, missing="zero")
print(f"Backbone: n={G_backbone.number_of_nodes()}, m={G_backbone.number_of_edges()}, density={nx.density(G_backbone):.4f}")
```

Run community detection on `G_backbone`, not the full projection `W`.

---

## Issue 2: Louvain is unreliable — use Leiden, and run it many times

Louvain has two known problems you should know about:

**First**, it can produce internally disconnected "communities" — nodes can migrate out of a community during the local-move phase without the algorithm checking whether remaining nodes still form a connected subgroup. Leiden was developed specifically to fix this, and it guarantees connected communities. This matters practically: if you later want to say "this community of employees forms a coherent subteam," Louvain might give you a "community" that is actually two disjoint subgraphs.

**Second**, and more fundamentally, the modularity landscape is *degenerate*. There are exponentially many near-optimal partitions that are structurally very different from each other (Good, De Montjoye & Clauset 2010). A single Louvain or Leiden run returns essentially one arbitrary sample from this landscape. Running again with a different random seed gives a different partition, possibly with a different number of communities and different membership assignments, at nearly the same modularity score.

The correct workflow is:

1. Run Leiden 100+ times with different random seeds.
2. Compute pairwise ARI (Adjusted Rand Index) or NMI across runs to quantify stability.
3. Build a consensus partition from stable runs.
4. Only then interpret or name communities.

```python
import leidenalg as la
import igraph as ig
from sklearn.metrics import adjusted_rand_score
import numpy as np

# Convert backbone to igraph
edges = [(u, v, d["weight"]) for u, v, d in G_backbone.edges(data=True)]
node_list = list(G_backbone.nodes())
node_index = {n: i for i, n in enumerate(node_list)}
g = ig.Graph()
g.add_vertices(len(node_list))
g.add_edges([(node_index[u], node_index[v]) for u, v, _ in edges])
g.es["weight"] = [w for _, _, w in edges]

# Run Leiden 100 times
partitions = []
np.random.seed(0)
for seed in range(100):
    part = la.find_partition(
        g,
        la.ModularityVertexPartition,
        weights="weight",
        seed=seed
    )
    partitions.append(part.membership)

# Compute pairwise ARI
aris = []
for i in range(len(partitions)):
    for j in range(i + 1, len(partitions)):
        aris.append(adjusted_rand_score(partitions[i], partitions[j]))

print(f"Mean pairwise ARI across 100 runs: {np.mean(aris):.3f} ± {np.std(aris):.3f}")
print(f"Number of communities per run: {[len(set(p)) for p in partitions[:10]]}")
```

Interpret the mean ARI:
- ARI > 0.9: the partition is highly stable — the community structure is robust
- ARI 0.7–0.9: moderate stability — report the consensus but note variability
- ARI < 0.7: the partition is unreliable — do not name communities; consider SBM instead

**Also compare to a null model.** A modularity score of 0.4 means nothing if a shuffled version of the same graph also achieves 0.35. Run the same algorithm on a degree-preserving shuffle:

```python
# Configuration-model null comparison
Q_nulls = []
for _ in range(20):
    g_null = ig.Graph.Degree_Sequence(g.degree(), method="vl")
    part_null = la.find_partition(g_null, la.ModularityVertexPartition, seed=0)
    Q_nulls.append(part_null.modularity)

part_real = la.find_partition(g, la.ModularityVertexPartition, weights="weight", seed=0)
print(f"Real graph Q: {part_real.modularity:.3f}")
print(f"Null graph Q: {np.mean(Q_nulls):.3f} ± {np.std(Q_nulls):.3f}")
```

If the real Q is not substantially above the null Q, you don't have meaningful community structure to report.

---

## If you want a more principled approach

For your use case — finding defensible, interpretable employee collaboration groups — a **Stochastic Block Model (SBM)** via `graph-tool` is worth considering. Advantages over modularity:

- The number of communities is inferred from the data, not chosen
- It resists overfitting (a random graph correctly returns one block)
- It finds both assortative and disassortative structure
- Hierarchical variants reveal nested community structure (e.g., teams within departments)

Alternatively, since your data is bipartite, you can skip projection entirely and run a **bipartite SBM** directly on the person × project graph:

```python
import graph_tool.all as gt

g = gt.load_graph("your_bipartite.graphml")
# Mark node kinds (0 = person, 1 = project)
kind = g.new_vp("int")
for v in g.vertices():
    kind[v] = 0 if v in person_set else 1
g.vp["kind"] = kind

state = gt.minimize_nested_blockmodel_dl(
    g,
    state_args=dict(deg_corr=True, pclabel=g.vp.kind)
)
state.draw()
```

This avoids projection artifacts entirely and gives you a generative model you can interpret.

---

## Summary of recommended changes

| Your plan | Issue | Fix |
|---|---|---|
| Project bipartite → person-person | Large-project cliques inflate community structure | Apply SDSM/FDSM backbone extraction before community detection |
| Run Louvain on projection | Can produce disconnected communities; single run is unreliable | Use Leiden; run 100+ times; report mean ARI before interpreting |
| Interpret results directly | No null comparison | Compare modularity to configuration-model null |

Your NetworkX code is fine for building the projection. The main surgery is: (1) add backbone extraction after the projection, (2) switch to `leidenalg` + `igraph` for community detection, and (3) add the stability loop before reading anything into the partition.
