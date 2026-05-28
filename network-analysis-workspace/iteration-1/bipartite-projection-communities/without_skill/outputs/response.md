# Response: Bipartite Projection + Louvain Community Detection

## Short answer

Your plan is reasonable and will work, but there are a few pitfalls worth knowing about before you run it.

---

## What your plan gets right

**Bipartite projection to a person-person network** is a standard, well-understood approach for this problem. Weighting edges by the number of shared projects is a sensible choice — it captures collaboration intensity, not just binary co-participation. NetworkX has `bipartite.weighted_projected_graph()` built in for exactly this.

**Louvain on the projected graph** is also a solid default. Louvain is fast even at 800-node scale, and the weighted version will respect your shared-project counts as edge weights, which is what you want.

---

## Pitfalls to watch for

### 1. The hub-and-spoke inflation problem

If a few large projects (say, a 200-person all-hands project) are in your dataset, projection will create a dense clique of 200 employees all connected to each other with weight ≥ 1. This makes a large, bureaucratic project look like a strong community signal, when really it's just "everyone was on the all-hands."

**What to do:**
- Check your project size distribution first. If you have heavy-tailed project sizes, consider filtering out very large projects before projecting, or down-weighting edges from large projects.
- A common fix is to use **hyperbolic weighting**: instead of raw shared-project count, weight each co-participation on project *k* by `1 / (size_k - 1)`. This way, co-appearing on a 5-person project counts far more than co-appearing on a 100-person project. NetworkX doesn't do this automatically, but it's easy to implement.

### 2. Resolution limit in Louvain

Louvain has a known resolution limit — it tends to merge small but real communities into larger ones when the graph is dense. With 800 nodes and potentially many edges (if most people share at least one project), this can matter.

**What to do:**
- Tune the `resolution` parameter in `community.louvain_communities(G, resolution=r)` (default is 1.0). Higher values favor smaller communities; lower values favor fewer, larger ones.
- Run Louvain multiple times (it's stochastic) and check stability across runs. If community assignments are wildly inconsistent, you may have a resolution or density issue.

### 3. Edge weight thresholding

After projection, you'll likely have many weak edges (pairs of employees who coincidentally shared one large project). These weak edges add noise for Louvain.

**What to do:**
- Consider removing edges below a minimum weight threshold (e.g., keep only pairs with ≥ 2 shared projects, or use the hyperbolic weight and set a floor).
- Check the edge weight distribution before deciding.

### 4. Isolated nodes

Employees who only participated in one project, and no one else on that project is in the dataset (or all co-members were on other projects too), may end up as isolates in the projected graph. Louvain will assign each isolate its own singleton community. Decide in advance whether to include or exclude them.

---

## Recommended workflow

```python
import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms import community

# 1. Build bipartite graph
B = nx.Graph()
# Add employee nodes
B.add_nodes_from(employees, bipartite=0)
# Add project nodes
B.add_nodes_from(projects, bipartite=1)
# Add edges
B.add_edges_from(employee_project_pairs)

# 2. Check project size distribution before projecting
project_sizes = {p: B.degree(p) for p in projects}
# inspect: sorted(project_sizes.values(), reverse=True)[:20]

# 3. (Optional) Filter large projects
MAX_PROJECT_SIZE = 50  # tune based on your data
filtered_projects = {p for p, s in project_sizes.items() if s <= MAX_PROJECT_SIZE}
B_filtered = B.subgraph(employees | filtered_projects)

# 4. Project onto employees, weighted by shared projects
G = bipartite.weighted_projected_graph(B_filtered, employees)

# 5. (Optional) Apply hyperbolic weighting manually for more nuance
# For each edge, down-weight contributions from large projects

# 6. (Optional) Threshold weak edges
MIN_WEIGHT = 2
G_thresh = nx.Graph(
    (u, v, d) for u, v, d in G.edges(data=True) if d["weight"] >= MIN_WEIGHT
)

# 7. Run Louvain (multiple times for stability check)
communities = community.louvain_communities(G_thresh, weight="weight", seed=42)

# 8. Inspect
print(f"Found {len(communities)} communities")
sizes = sorted([len(c) for c in communities], reverse=True)
print("Community sizes:", sizes)
```

---

## Summary

| Your plan | Verdict |
|---|---|
| Project bipartite → person-person, weight = shared projects | Good default |
| Run Louvain on the projected graph | Good, but tune `resolution` |
| Use weighted edges | Correct — don't ignore weights |
| **Missing: check project size distribution** | Do this first |
| **Missing: consider hyperbolic weighting** | Worth it if project sizes vary widely |
| **Missing: threshold weak edges** | Helps Louvain find cleaner communities |

Your plan is on the right track. The main thing to add before hitting run is a quick inspection of project sizes — that distribution will tell you whether you need the hyperbolic weighting or large-project filtering step, and will save you from getting communities that just reflect "everyone was on the big project."
