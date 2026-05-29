# Identifying Influential People in Your Advice Network

## Step 0: Classify the network before touching any numbers

Before computing a single metric, I need to pin down what kind of network you have — because the type determines which methods are legal and which produce misleading results.

Based on your description:

| Axis | Your network |
|---|---|
| Mode | One-mode (employees → employees) |
| Directionality | **Directed** — "who do you go to for advice" is inherently asymmetric. Person A seeking advice from Person B does not mean B seeks advice from A. |
| Weight | Likely binary (each respondent either named someone or didn't), but check whether you recorded nomination frequency |
| Time | Cross-sectional snapshot (one survey wave) |
| Boundary | Complete network (you surveyed the full population of 200 employees) |
| Scale | Small (200 nodes) — NetworkX handles this without issue |

The directed aspect is the most consequential choice. A directed advice network distinguishes **who is sought out** (high in-degree = being named as an advisor) from **who seeks many people** (high out-degree = active advice-seeker). These answer different questions. Do not treat this as undirected.

---

## Step 1: Inspect before computing

Run this before any centrality calculation:

```python
import networkx as nx
import numpy as np
import pandas as pd

# Load your edge list (source = advice-seeker, target = advice-giver)
G = nx.read_edgelist("advice_network.csv", delimiter=",",
                     create_using=nx.DiGraph(),
                     nodetype=str)

print(f"n = {G.number_of_nodes()}")
print(f"m = {G.number_of_edges()}")
print(f"directed: {G.is_directed()}")
print(f"density: {nx.density(G):.4f}")
print(f"weakly connected components: {nx.number_weakly_connected_components(G)}")
print(f"strongly connected components: {nx.number_strongly_connected_components(G)}")
print(f"reciprocity: {nx.reciprocity(G):.3f}")
print(f"transitivity: {nx.transitivity(G):.3f}")

# Degree distribution
in_deg = dict(G.in_degree())
out_deg = dict(G.out_degree())
print(f"\nIn-degree  — mean: {np.mean(list(in_deg.values())):.2f}, "
      f"max: {max(in_deg.values())}, median: {np.median(list(in_deg.values())):.1f}")
print(f"Out-degree — mean: {np.mean(list(out_deg.values())):.2f}, "
      f"max: {max(out_deg.values())}, median: {np.median(list(out_deg.values())):.1f}")

# Isolates
isolates = list(nx.isolates(G))
print(f"Isolates: {len(isolates)}")
```

Things to check from this output before proceeding:

- **Multiple weakly connected components**: if the graph has isolated subgraphs (e.g. a remote team that only advises each other), closeness centrality must be handled with harmonic centrality, not standard closeness.
- **Low reciprocity** (e.g., < 0.2): confirms the directed asymmetry is real and meaningful — do not collapse to undirected.
- **Extreme in-degree max**: if one node has in-degree 80 out of 200, they are a clear hub; the distribution shape will tell you whether this is a star-like network or flatter.

---

## Step 2: Which centralities answer your specific questions

You have two substantive goals, and they map to different centrality measures:

### Goal A: "Who are the knowledge champions?" (go-to experts, most sought-after advisors)

This is fundamentally a **prestige/status** question. Who is sought out by many people, especially by people who are themselves sought out?

**Primary measure: In-degree**

Raw in-degree counts how many people named this person as an advice source. In a 200-person complete network, this is your most transparent and defensible first cut. High in-degree = many people trust this person's advice enough to name them unprompted.

```python
in_degree_centrality = dict(G.in_degree())
top_k_indegree = sorted(in_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 by in-degree (most sought-after advisors):")
for node, score in top_k_indegree:
    print(f"  {node}: named by {score} colleagues")
```

**Secondary measure: PageRank**

PageRank extends in-degree by asking: not just how many people name you, but how important are those people? Being named by 5 highly sought-out advisors is worth more than being named by 5 people nobody else consults. PageRank handles the directed structure correctly and avoids the "dangling node" problem that breaks plain eigenvector centrality on directed graphs.

```python
pr = nx.pagerank(G, alpha=0.85)
top_k_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 by PageRank (high-quality advice reputation):")
for node, score in top_k_pr:
    print(f"  {node}: {score:.4f}")
```

**Do not use plain eigenvector centrality on this directed graph.** Eigenvector centrality fails on directed networks without strong components — nodes with no in-edges receive score 0 and pass nothing upstream, breaking the computation. PageRank is the correct directed analog.

---

### Goal B: "Who should we loop in early for initiative rollout?" (change ambassadors, cross-departmental connectors)

This is a **brokerage / information flow** question. You want people who sit between groups — who, if they carry your message, would reach parts of the organization that wouldn't otherwise hear it. These are not always the same as the most-named advisors.

**Primary measure: Betweenness centrality**

Betweenness counts the fraction of all shortest paths between pairs of employees that pass through a given node. High betweenness = this person is a bridge between subgroups, a broker. Their removal (or non-participation) would fragment information flow.

```python
# Use the largest weakly connected component for betweenness
lwcc = max(nx.weakly_connected_components(G), key=len)
G_lwcc = G.subgraph(lwcc).copy()

btw = nx.betweenness_centrality(G_lwcc, normalized=True)
top_k_btw = sorted(btw.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 by betweenness (cross-group brokers):")
for node, score in top_k_btw:
    print(f"  {node}: {score:.4f}")
```

**Secondary measure: Burt's constraint (structural holes)**

Burt's constraint measures how redundant a person's advice contacts are. Low constraint = the person connects to people who don't otherwise connect to each other (structural holes). This is a more refined brokerage measure than betweenness — it specifically captures whether someone bridges genuinely separate clusters.

```python
constraint = nx.constraint(G)
# Low constraint = more structural holes = better broker
top_brokers = sorted(constraint.items(), key=lambda x: x[1])[:10]
print("\nTop 10 lowest constraint (best structural-hole brokers):")
for node, score in top_brokers:
    print(f"  {node}: constraint = {score:.4f}")
```

The theory: people with low constraint are exposed to diverse, non-overlapping information streams and are well-positioned to synthesize and transmit across silos. Burt (2004) shows these are also the people most likely to generate novel ideas in organizational networks.

---

## Step 3: Combine the measures into a decision matrix

For each employee, compute all four scores and put them in a table. The substantive interpretation maps directly to your use cases:

```python
# Build a summary DataFrame
nodes = list(G.nodes())
df = pd.DataFrame({
    "employee": nodes,
    "in_degree": [G.in_degree(n) for n in nodes],
    "pagerank": [pr[n] for n in nodes],
    "betweenness": [btw.get(n, 0) for n in nodes],
    "constraint": [constraint.get(n, np.nan) for n in nodes],
})

# Rank each column (lower constraint rank = better broker)
df["rank_indegree"] = df["in_degree"].rank(ascending=False)
df["rank_pagerank"] = df["pagerank"].rank(ascending=False)
df["rank_betweenness"] = df["betweenness"].rank(ascending=False)
df["rank_constraint"] = df["constraint"].rank(ascending=True)  # lower is better

df_sorted = df.sort_values("rank_pagerank")
print(df_sorted.head(20).to_string(index=False))
```

**Reading the table:**

| Profile | What it means | Action |
|---|---|---|
| High in-degree + high PageRank, low betweenness | Expert within a cluster — well-known in their subgroup | Knowledge champion within their department |
| High betweenness + low constraint, moderate in-degree | Cross-group broker — spans organizational silos | Loop in early for rollout; they will carry the message across teams |
| High on all four | Rare "hub-broker" — influential and well-connected across groups | Highest-priority early stakeholder; also a single point of failure |
| Low in-degree + low betweenness | Peripheral node | May not need prioritizing, but check if they're an isolate in a specific subgroup |

---

## Step 4: Closeness centrality — handle the directed graph carefully

Closeness measures how quickly a person can reach everyone else (broadcast speed). It is useful if you want to identify people who could spread a message most rapidly.

**Critical note**: standard closeness centrality breaks on disconnected graphs (and on directed graphs, nodes in different weakly connected components are mutually unreachable). Use harmonic centrality instead — it handles this gracefully by summing 1/distance terms (1/∞ = 0).

```python
# Harmonic centrality handles disconnected graphs correctly
harmonic = nx.harmonic_centrality(G)
top_k_harmonic = sorted(harmonic.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 by harmonic centrality (fastest broadcasters):")
for node, score in top_k_harmonic:
    print(f"  {node}: {score:.2f}")
```

---

## Step 5: Sensitivity check your top-list

Centrality rankings in survey-based networks are sensitive to measurement error — if a respondent forgot to name one advisor, or misremembered a name, your rankings can shift. Before making personnel decisions on this data, run a bootstrap:

```python
import random

def bootstrap_centrality(G, measure_fn, n_boot=500, p_remove=0.05, seed=42):
    """Remove each edge with probability p_remove, recompute centrality, return rank stability."""
    rng = random.Random(seed)
    rankings = []
    edges = list(G.edges())
    for _ in range(n_boot):
        edges_to_keep = [e for e in edges if rng.random() > p_remove]
        G_boot = nx.DiGraph()
        G_boot.add_nodes_from(G.nodes())
        G_boot.add_edges_from(edges_to_keep)
        scores = measure_fn(G_boot)
        ranked = sorted(scores, key=scores.get, reverse=True)
        rankings.append(ranked)
    return rankings

# Example for PageRank
boot_rankings = bootstrap_centrality(G, nx.pagerank)

# Compute how often each node appears in the top 10 across bootstrap replicates
from collections import Counter
top10_counts = Counter()
for ranking in boot_rankings:
    for node in ranking[:10]:
        top10_counts[node] += 1

print("\nBootstrap stability — fraction of resamples in top 10:")
for node, count in top10_counts.most_common(15):
    print(f"  {node}: {count/500:.2%}")
```

Report nodes as confident top-list members only if they appear in the top 10 across >80% of bootstrap replicates. Nodes that fluctuate in and out are statistically fragile — they deserve a softer claim.

---

## Step 6: State assumptions explicitly when reporting results

When you present results to stakeholders, be explicit about the assumptions embedded in each metric:

- **"Person X has the highest PageRank"** → "Person X is the most sought-out advisor, weighted by the status of those who seek them out. This assumes the advice network is an accurate reflection of actual advice-seeking behavior."
- **"Person Y has high betweenness"** → "Person Y sits on the most paths between departments. Removing them from early rollout communication would likely fragment how the initiative diffuses across organizational silos. This assumes information travels along efficient (shortest) paths, which is a reasonable approximation for explicit referral networks."
- **"Person Z has low constraint"** → "Person Z bridges genuinely separate groups — their contacts don't otherwise talk to each other. They have access to diverse perspectives and can carry ideas across structural holes."

Do not say "Person X is most influential" without qualifying which dimension of influence and under what model of how advice spreads.

---

## Summary: who to target

For **knowledge champions** (internal experts to elevate and recognize):
- Rank by in-degree first; use PageRank to break ties and catch cases where someone is named specifically by other well-connected advisors
- These are your visible expertise anchors — they already have earned trust within the network

For **early-rollout stakeholders** (people to brief first to seed broad adoption):
- Rank by betweenness and low constraint
- These are your organizational bridges — they span teams and will carry information into corners that hub-experts won't reach on their own

The highest-value targets for any initiative rollout are people who score well on **both** dimensions — high PageRank and high betweenness — because they are both trusted and well-positioned to diffuse. There are usually only 3–5 such people in a 200-person network.

---

## Reference

- Freeman, L. C. (1979). Centrality in social networks: Conceptual clarification. *Social Networks* 1: 215–239.
- Borgatti, S. P. (2005). Centrality and network flow. *Social Networks* 27: 55–71.
- Burt, R. S. (2004). Structural holes and good ideas. *American Journal of Sociology* 110(2): 349–399.
- Bonacich, P. (1987). Power and centrality: A family of measures. *American Journal of Sociology* 92(5): 1170–1182.
